#!/usr/bin/env node
// Native browser proof for the one-document shared layer workspace.
import { spawn, execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { delay, waitForDevToolsPort, waitForPageEndpoint, connectCdp, evaluate } from './capture_globe_browser_evidence.mjs';

const sha256 = value => createHash('sha256').update(typeof value === 'string' || Buffer.isBuffer(value) ? value : JSON.stringify(value)).digest('hex');
const check = (ok, message) => {if (!ok) throw new Error('Unified browser proof: '+message);};
const contextReplaced = error => /Inspected target navigated or closed|Execution context was destroyed|Cannot find (?:default execution context|context with specified id)/.test(String(error));

function argumentsFor(argv) {
  const values = {};
  for (let i=2;i<argv.length;i+=2) {
    check(argv[i]?.startsWith('--') && argv[i+1]!==undefined,'expected --name value arguments');
    values[argv[i].slice(2)] = argv[i+1];
  }
  check(values.browser && values.output,'--browser and --output are required');
  check(Boolean(values.artifact)!==Boolean(values.url),'provide either --artifact or --url');
  if (values.url) check(values['expected-artifact'],'live proof requires --expected-artifact');
  values.width=Number(values.width || 1440);values.height=Number(values.height || 900);
  values.timeoutMs=Number(values['timeout-ms'] || 270000);
  check([values.width,values.height,values.timeoutMs].every(v=>Number.isFinite(v)&&v>0),'invalid dimensions or timeout');
  values.expectedArtifact=resolve(values.artifact || values['expected-artifact']);
  values.output=resolve(values.output);
  return values;
}

// The shared URL preserves exact native renderer numbers and semantic fields.
const sameState=(left,right)=>JSON.stringify(left)===JSON.stringify(right);

async function localServer(directory) {
  const server=spawn('python',['-u','-m','http.server','0','--bind','127.0.0.1','--directory',directory],{stdio:['ignore','pipe','pipe']});
  let log='';server.stderr.on('data',chunk=>{log+=chunk;});
  const port=await new Promise((resolvePort,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Local artifact server did not start')),5000);
    server.once('exit',code=>{clearTimeout(timer);reject(new Error('Local artifact server exited '+code));});
    server.stdout.on('data',chunk=>{log+=chunk;const match=String(chunk).match(/port (\d+)/);if(match){clearTimeout(timer);resolvePort(Number(match[1]));}});
  });
  return {process:server,url:`http://127.0.0.1:${port}/globe/`,log:()=>log};
}

async function verifyBytes(options, base, deadline) {
  const results=[];
  for(const entry of ['globe','region']) {
    const directory=join(options.expectedArtifact,entry),files=['build-meta.json','unified-bundle.json'];
    // Both browser entries are bound to checked metadata and the common bundle.
    // Pages separately verifies every published file before this native proof.
    // Remote content cannot select paths or provide the expected digest.
    for(let offset=0;offset<files.length;offset+=6) {
      const group=await Promise.all(files.slice(offset,offset+6).map(async relative=>{
        const expected=await readFile(join(directory,relative));
        const url=new URL(entry+'/'+relative,base);url.searchParams.set('artemis_browser_check',process.env.GITHUB_SHA || 'local');
        const timeout=Math.min(15000,deadline-Date.now());check(timeout>0,'artifact verification exhausted deadline');
        const response=await fetch(url,{cache:'no-store',signal:AbortSignal.timeout(timeout)});
        check(response.ok,'artifact fetch failed '+entry+'/'+relative+' HTTP '+response.status);
        const actual=Buffer.from(await response.arrayBuffer());
        check(sha256(actual)===sha256(expected),'published bytes differ '+entry+'/'+relative);
        return {entry,path:relative,bytes:actual.length,sha256:sha256(actual)};
      }));results.push(...group);
    }
  }
  check(sha256(await readFile(join(options.expectedArtifact,'globe/unified-bundle.json')))===sha256(await readFile(join(options.expectedArtifact,'region/unified-bundle.json'))),'entry bundles differ');
  return results;
}

async function runScenario(cdp,options,url,deadline,expectedBundle) {
  const base=new URL('../',url),captures=[],actions=[],checks=[],renderSettlements=[];
  let documentOrigin=null,mapObjectId=null,immutableHash=null;
  const bundleHash=sha256(expectedBundle);
  async function settle() {await evaluate(cdp,'new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))',true);}
  async function key(key,code,virtualKey,modifiers=0,navigates=false) {
    await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',key,code,windowsVirtualKeyCode:virtualKey,modifiers,
      ...(key==='Enter'?{text:'\r',unmodifiedText:'\r'}:{})});
    await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',key,code,windowsVirtualKeyCode:virtualKey,modifiers});
    if(!navigates)await settle();
  }
  async function ready() {
    let last=null;
    while(Date.now()<deadline) {
      last=await evaluate(cdp,`(() => {const r=window.__ARTEMIS_EXPLORER,f=document.getElementById('fatal-error');return {ready:r?.ready===true,visual:document.documentElement.dataset.artemisVisualReady==='true',fatal:f&&!f.hidden?f.textContent:null};})()`);
      if(last.fatal)throw new Error(last.fatal);
      if(last.ready&&last.visual)return last;await delay(100);
    }
    throw new Error('Unified runtime readiness timed out: '+JSON.stringify(last));
  }
  async function idle(reason) {
    const remaining=Math.min(20000,deadline-Date.now());check(remaining>0,'native render deadline exhausted');
    const result=await evaluate(cdp,`(async()=>{
      const m=window.__ARTEMIS_EXPLORER.map;
      await new Promise((resolve,reject)=>{const t=setTimeout(()=>{m.off('idle',done);reject(new Error('Native map idle timed out'));},${remaining});function done(){clearTimeout(t);requestAnimationFrame(()=>requestAnimationFrame(resolve));}m.once('idle',done);m.triggerRepaint();});
      if(!m.loaded()||m.isMoving())throw new Error('Native idle did not complete rendering');
      return {loaded:m.loaded(),moving:m.isMoving(),projection:m.getProjection().type};
    })()`,true);
    renderSettlements.push({reason,...result});
  }
  async function navigate(destination) {
    const prior=await evaluate(cdp,'performance.timeOrigin');
    await cdp.send('Page.navigate',{url:String(destination)});let arrived=false;
    while(Date.now()<deadline) {
      try{arrived=await evaluate(cdp,`performance.timeOrigin!==${prior}&&location.pathname===${JSON.stringify(new URL(destination).pathname)}`);}catch(error){if(!contextReplaced(error))throw error;}
      if(arrived)break;await delay(100);
    }
    check(arrived,'explicit entry did not create destination document');await ready();await idle('explicit entry navigation');
    await cdp.send('Emulation.setFocusEmulationEnabled',{enabled:true});
    documentOrigin=await evaluate(cdp,'performance.timeOrigin');
    const reference=await cdp.send('Runtime.evaluate',{expression:'window.__ARTEMIS_EXPLORER.map',returnByValue:false});
    mapObjectId=reference.result?.objectId;check(mapObjectId,'could not retain native map object reference');
    immutableHash=sha256(await evaluate(cdp,'window.__ARTEMIS_EXPLORER.bundle'));
    check(immutableHash===bundleHash,'runtime bundle differs from checked artifact');
  }
  async function snapshot() {
    return evaluate(cdp,`(() => {const r=window.__ARTEMIS_EXPLORER;return {state:r.state,visible:r.visibleItems.map(i=>({itemId:i.item_id,layer:i.layer_id,kind:i.kind,interval:i.interval||null})),origin:performance.timeOrigin,inspectorHidden:document.getElementById('inspector').hidden,disclosures:[...document.querySelectorAll('#inspector details')].map(d=>({id:d.id,open:d.open})),card:document.getElementById('inspector').textContent,camera:{center:r.map.getCenter().toArray(),zoom:r.map.getZoom(),pitch:r.map.getPitch(),bearing:r.map.getBearing()},url:location.href};})()`);
  }
  async function stable(reason) {
    const origin=await evaluate(cdp,'performance.timeOrigin');check(origin===documentOrigin,reason+' reloaded/navigated the document');
    const same=await cdp.send('Runtime.callFunctionOn',{objectId:mapObjectId,functionDeclaration:'function(){return this===window.__ARTEMIS_EXPLORER.map;}',returnByValue:true});
    check(same.result?.value===true,reason+' replaced the native map instance');
    const current=sha256(await evaluate(cdp,'window.__ARTEMIS_EXPLORER.bundle'));check(current===immutableHash,reason+' mutated source bundle');
    actions.push({action:reason,documentTimeOrigin:origin,sameMap:true,bundleSha256:current});
  }
  async function click(selector,keyboard=false) {
    const point=await evaluate(cdp,`(() => {const n=document.querySelector(${JSON.stringify(selector)});if(!n)throw new Error('Missing control '+${JSON.stringify(selector)});n.scrollIntoView({block:'nearest'});n.focus({preventScroll:true});const b=n.getBoundingClientRect(),x=b.x+b.width/2,y=b.y+b.height/2;if(n.disabled||!b.width||!b.height||!n.contains(document.elementFromPoint(x,y)))throw new Error('Obstructed control '+${JSON.stringify(selector)});if(document.activeElement!==n)throw new Error('Control focus failed');return {x,y};})()`);
    if(keyboard)await key(' ','Space',32);
    else{await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...point});await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...point});await settle();}
    await stable(selector);return point;
  }
  async function number(id,value) {
    await evaluate(cdp,`(() => {const n=document.getElementById(${JSON.stringify(id)});if(!n||n.hidden||n.disabled)throw new Error('Unavailable native year input');n.focus();if(document.activeElement!==n)throw new Error('Year input focus failed');})()`);
    await key('a','KeyA',65,2);await cdp.send('Input.insertText',{text:String(value)});await key('Tab','Tab',9);
    await stable(id+'='+value);
  }
  async function layer(id,enabled) {if(await evaluate(cdp,`document.getElementById('layer-'+${JSON.stringify(id)}).checked`)!==enabled)await click('#layer-'+id,true);}
  async function select(itemId) {
    const indices=await evaluate(cdp,`(() => {const n=document.getElementById('record-select');n.focus();const target=[...n.options].findIndex(o=>o.value===${JSON.stringify(itemId)});if(target<0)throw new Error('Item not available in native selection');return {target,current:n.selectedIndex};})()`);
    let current=indices.current;if(current<0){await key('Home','Home',36);current=0;}
    const delta=indices.target-current;for(let step=0;step<Math.abs(delta);step++)await key(delta>0?'ArrowDown':'ArrowUp',delta>0?'ArrowDown':'ArrowUp',delta>0?40:38);
    const state=await snapshot();check(state.state.selectedItemId===itemId&&!state.inspectorHidden,'native record selector lost identity');await stable('select '+itemId);
  }
  async function disclose(id) {
    if(!await evaluate(cdp,`document.getElementById(${JSON.stringify(id)}).open`))await click('#'+id+' > summary',true);
    check(await evaluate(cdp,`document.getElementById(${JSON.stringify(id)}).open`),'native disclosure failed '+id);
  }
  async function close() {if(!await evaluate(cdp,"document.getElementById('inspector').hidden"))await click('#close-details');}
  async function membership(expected,reason) {
    await idle(reason);const current=await snapshot();
    const actual=Object.fromEntries(['leonardo','roman','architecture'].map(layer=>[layer,current.visible.filter(i=>i.layer===layer).length]));
    check(JSON.stringify(actual)===JSON.stringify(expected),reason+' membership mismatch '+JSON.stringify(actual));
    checks.push({case:reason,state:current.state,counts:actual,itemIds:current.visible.map(i=>i.itemId),documentTimeOrigin:current.origin});return current;
  }
  async function capture(suffix) {
    await idle('capture '+suffix);
    const layout=await evaluate(cdp,`(() => {
      const visible=n=>{if(!n?.checkVisibility({checkVisibilityCSS:true}))return false;const b=n.getBoundingClientRect();return b.width>0&&b.height>0&&b.left>=0&&b.top>=0&&b.right<=innerWidth+1&&b.bottom<=innerHeight+1;};
      for(const id of ['workspace-header','layer-controls','view-globe','view-map','language-en','language-ru','time-dock'])if(!visible(document.getElementById(id)))throw new Error('Control outside viewport '+id);
      if(document.documentElement.scrollWidth>innerWidth+1)throw new Error('Horizontal overflow');
      const h=document.getElementById('workspace-header').getBoundingClientRect(),t=document.getElementById('time-dock').getBoundingClientRect();if(h.bottom>t.top)throw new Error('Header overlaps shared time controls');
      const r=window.__ARTEMIS_EXPLORER,s=r.state;
      if(document.getElementById('view-'+s.presentationView).getAttribute('aria-pressed')!=='true'||document.getElementById('language-'+s.language).getAttribute('aria-pressed')!=='true')throw new Error('Projection/language aria state differs');
      if(r.map.getProjection().type!==(s.presentationView==='map'?'mercator':'globe'))throw new Error('Native projection mismatch');
      return {width:innerWidth,height:innerHeight,headerBottom:h.bottom,timeTop:t.top,language:s.language,view:s.presentationView};
    })()`);
    const screenshot=join(options.output,suffix+'.png'),dom=join(options.output,suffix+'.html');
    const png=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});await writeFile(screenshot,Buffer.from(png.data,'base64'));await writeFile(dom,await evaluate(cdp,'document.documentElement.outerHTML'));
    captures.push({case:suffix,...layout,screenshot,dom,screenshotSha256:sha256(await readFile(screenshot)),domSha256:sha256(await readFile(dom))});
  }
  async function view(mode) {
    const before=await snapshot();await click('#view-'+mode,true);await idle('projection '+mode);const after=await snapshot();
    const previous={...before.state},next={...after.state};delete previous.presentationView;delete next.presentationView;
    check(sameState(previous,next),'projection changed shared semantic/camera state');
    check(before.card===after.card&&JSON.stringify(before.disclosures)===JSON.stringify(after.disclosures),'projection changed selected source disclosures');
  }
  async function history(direction,expected) {
    const history=await cdp.send('Page.getNavigationHistory'),entry=history.entries[history.currentIndex+direction];check(entry,'missing shared history entry');
    await cdp.send('Page.navigateToHistoryEntry',{entryId:entry.id});
    let restored=false;
    while(Date.now()<deadline){const current=await evaluate(cdp,'window.__ARTEMIS_EXPLORER.state');restored=sameState(current,expected);if(restored)break;await delay(100);}
    check(restored,'shared Back/Forward state restoration failed');await idle('history');await stable(direction<0?'Back':'Forward');
  }

  await navigate(url);await membership({leonardo:11,roman:0,architecture:0},'default Leonardo entry');
  await click('#mode-scrub');await number('cursor-year',100);
  const early=await membership({leonardo:0,roman:1,architecture:0},'Scrub100 Roman only');
  check(early.state.cursorYear===100,'global cursor clamped to Leonardo origin');
  const roman100=early.visible.find(i=>i.layer==='roman');await select(roman100.itemId);await disclose('sources-disclosure');await disclose('evidence-disclosure');
  const romanDetails=await snapshot();
  check(romanDetails.card.includes('Cliopatria')&&romanDetails.card.includes('CC-BY-4.0'),'Roman source/license missing');
  check(romanDetails.card.includes('91')&&romanDetails.card.includes('105'),'Roman native interval missing');
  const cameraBefore=romanDetails.camera;
  await layer('architecture',true);const unrelated=await snapshot();
  check(unrelated.state.selectedItemId===roman100.itemId&&JSON.stringify(unrelated.disclosures)===JSON.stringify(romanDetails.disclosures)&&unrelated.card===romanDetails.card,'unrelated architecture layer changed Roman source selection');
  check(JSON.stringify(unrelated.camera)===JSON.stringify(cameraBefore)&&unrelated.state.cursorYear===100,'enabling reference layer changed camera/time');
  await membership({leonardo:0,roman:1,architecture:31},'atemporal references at100');await capture('roman100-en-globe');
  await number('cursor-year',1502);const later=await membership({leonardo:7,roman:0,architecture:31},'Scrub1502 Leonardo trace');
  check(later.state.selectedItemId===null,'own time visibility did not clear Roman selection');
  await click('#mode-range');await number('time-start',1502);await number('time-end',1502);
  const range=await membership({leonardo:4,roman:0,architecture:31},'Range1502 Leonardo only');
  const cesena=expectedBundle.leonardo.lifePath.presences.find(p=>p.presence_id==='presence-cesena-1502-08-10');
  check(cesena,'expected existing Cesena identity missing');await select(cesena.presence_item_id);await disclose('sources-disclosure');await disclose('evidence-disclosure');
  const leo=await snapshot();await layer('roman',false);const preserved=await snapshot();
  check(preserved.state.selectedItemId===cesena.presence_item_id&&preserved.card===leo.card&&JSON.stringify(preserved.disclosures)===JSON.stringify(leo.disclosures),'unrelated Roman layer changed Leonardo source disclosure');
  await layer('roman',true);
  for(const lang of ['en','ru']){await click('#language-'+lang);for(const mode of ['globe','map']){await view(mode);await capture('selected-leonardo-'+lang+'-'+mode);}}
  await close();await click('#language-en');
  const referenceChecks=[];
  for(const reference of expectedBundle.architecture.references) {
    await select(reference.item_id);await disclose('sources-disclosure');await disclose('input-disclosure');
    const details=await evaluate(cdp,`(() => {const r=window.__ARTEMIS_EXPLORER;return {selected:r.state.selectedItemId,scope:document.getElementById('selection-scope').textContent,input:document.getElementById('selection-input').textContent,sources:document.getElementById('selection-sources').textContent};})()`);
    check(/atemporal|historical applicability unknown/i.test(details.scope),'reference lacked atemporal/unknown applicability warning');
    for(const source of reference.sources){check(details.sources.includes(source.id)&&details.sources.includes(source.title),'existing reference source identity/title not disclosed');}
    const properties=reference.raw_feature.properties;
    const rawDates=Object.fromEntries(Object.entries(properties).filter(([name,value])=>/date|year|construction/.test(name)&&value!==null&&typeof value!=='object'));
    for(const value of Object.values(rawDates))check(details.input.includes(String(value)),'raw reference date lost '+reference.original_id+' '+value);
    referenceChecks.push({item:reference.item_id,originalId:reference.original_id,geometrySha256:sha256(reference.raw_feature.geometry),rawDates,sourceIds:reference.source_ids,historicalApplicability:'unknown'});
  }
  check(referenceChecks.length===31,'not all imported references inspected');
  const bce=referenceChecks.filter(r=>Object.values(r.rawDates).some(v=>/^-\d|BCE/.test(String(v))));check(bce.length>0,'raw BCE references not exercised');
  const bceExample=bce[0];await select(bceExample.item);await disclose('sources-disclosure');await disclose('input-disclosure');await disclose('evidence-disclosure');await capture('atemporal-raw-negative-dates-en-map');await click('#language-ru');await capture('atemporal-raw-negative-dates-ru-map');await click('#language-en');
  const selectedReference=(await snapshot()).state.selectedItemId;await layer('architecture',false);check((await snapshot()).state.selectedItemId===null,'hiding selected reference layer did not clear selection');await layer('architecture',true);await close();
  await click('#period-all');const wide=await membership({leonardo:11,roman:3,architecture:31},'wide Range interval collection');
  const nativeRoman=await evaluate(cdp,`(async()=>{const r=window.__ARTEMIS_EXPLORER,features=(await r.map.getSource('workspace-features').getData()).features;return features.filter(f=>f.properties.layer_id==='roman').map(f=>({item:f.properties.item_id,geometry:f.geometry}));})()`,true);
  check(nativeRoman.length===3&&new Set(nativeRoman.map(r=>r.item)).size===3,'eligible Roman versions were merged/dropped');
  const nativeGeometries=nativeRoman.map(r=>({item:r.item,geometrySha256:sha256(r.geometry)}));
  for(const record of nativeRoman){const version=expectedBundle.roman.versions.find(v=>v.item_id===record.item);check(version,'Roman version identity changed');const geometry=version.geometry_version.spatial_extent.geometry;check(record.geometry.type===geometry.type&&JSON.stringify(record.geometry.coordinates)===JSON.stringify(geometry.coordinates),'Roman native geometry changed/unioned');}
  check(/collection|коллекц/i.test(await evaluate(cdp,"document.getElementById('time-status').textContent")),'wide Range not labelled interval collection');
  for(const lang of ['en','ru']){await click('#language-'+lang);for(const mode of ['globe','map']){await view(mode);await capture('wide-range-'+lang+'-'+mode);}}
  await click('#language-en');await view('map');await close();
  const point=await evaluate(cdp,`(() => {const r=window.__ARTEMIS_EXPLORER,b=r.map.getCanvas().getBoundingClientRect();for(let y=b.top+8;y<b.bottom-8;y+=10)for(let x=b.left+8;x<b.right-8;x+=10){if(document.elementFromPoint(x,y)!==r.map.getCanvas())continue;const hit=r.map.queryRenderedFeatures([x-b.left,y-b.top],{layers:['workspace-points','workspace-regions']}).find(f=>f.properties.item_id);if(hit)return {x,y,item:hit.properties.item_id};}throw new Error('No unobstructed native workspace feature pixel');})()`);
  await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,x:point.x,y:point.y});await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:point.x,y:point.y});await settle();
  check((await snapshot()).state.selectedItemId===point.item,'native unified map picking failed');await stable('native canvas picking');await close();
  // Native drag is renderer-local camera input, independently of semantic time.
  const drag=await evaluate(cdp,`(() => {const c=window.__ARTEMIS_EXPLORER.map.getCanvas(),b=c.getBoundingClientRect();for(let y=b.top+40;y<b.bottom-40;y+=20)for(let x=b.left+60;x<b.right-60;x+=20)if(document.elementFromPoint(x,y)===c&&document.elementFromPoint(x+40,y)===c)return {x,y};throw new Error('No unobstructed map drag area');})()`);
  const beforeDrag=await snapshot();await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...drag});await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',button:'left',buttons:1,x:drag.x+40,y:drag.y});await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:drag.x+40,y:drag.y});await idle('native camera drag');await stable('native camera drag');
  const cameraState=await snapshot();check(JSON.stringify(cameraState.camera)!==JSON.stringify(beforeDrag.camera),'native camera drag did not move camera');
  const semanticBefore={...beforeDrag.state},semanticAfter={...cameraState.state};delete semanticBefore.camera;delete semanticAfter.camera;check(JSON.stringify(semanticBefore)===JSON.stringify(semanticAfter),'camera input changed semantic state');
  await click('#language-ru');const historyBefore=(await snapshot()).state;await layer('architecture',false);const historyMiddle=(await snapshot()).state;await view('globe');const historyAfter=(await snapshot()).state;
  await history(-1,historyMiddle);await history(-1,historyBefore);await history(1,historyMiddle);await history(1,historyAfter);await capture('shared-history-restored-ru-globe');
  const saved=(await snapshot()).url,savedState=(await snapshot()).state;
  // Explicit compatibility entry navigation is outside the persistent-document
  // assertions; all ordinary interactions above retained the actual map handle.
  await navigate(new URL('region/',base));await membership({leonardo:0,roman:1,architecture:0},'Region compatible entry own native default');await capture('region-entry-en-globe');
  await navigate(saved);check(sameState((await snapshot()).state,savedState),'shared saved URL lost workspace/camera state');await stable('shared saved state reopened');
  const legacy=[];
  const leoLegacy=new URL('globe/?mode=scrub&from=1452&at=1502&presence=presence-cesena-1502-08-10&lang=ru&view=map',base);await navigate(leoLegacy);
  const translatedLeo=await snapshot();check(translatedLeo.state.cursorYear===1502&&translatedLeo.state.mode==='scrub'&&translatedLeo.state.selectedItemId===cesena.presence_item_id&&translatedLeo.state.language==='ru'&&translatedLeo.state.presentationView==='map','legacy Leonardo saved state translation failed');legacy.push({entry:'leonardo',url:leoLegacy.href,state:translatedLeo.state});
  const version=expectedBundle.roman.versions[1];const romanLegacy=new URL('region/',base);romanLegacy.searchParams.set('time',version.preset_id);romanLegacy.searchParams.set('layers','layer-political-territory');romanLegacy.searchParams.set('item',version.item_id);romanLegacy.searchParams.set('lang','en');romanLegacy.searchParams.set('view','map');await navigate(romanLegacy);
  const translatedRoman=await snapshot();check(translatedRoman.state.selectedItemId===version.item_id&&translatedRoman.state.startYear===106&&translatedRoman.state.endYear===113,'legacy Roman saved state translation failed');legacy.push({entry:'roman',url:romanLegacy.href,state:translatedRoman.state});
  await disclose('sources-disclosure');await capture('legacy-roman-source-en-map');
  return {outcome:'TECHNICAL_UNIFIED_WORKSPACE_PASS',actions,checks,referenceChecks,rawNegativeDateReferenceCount:bce.length,rawDatePolicy:'Literal imported strings including negative BCE-style values; no calendar/lifetime normalization',nativeRomanGeometries:nativeGeometries,nativePicking:point,camera:{before:beforeDrag.camera,after:cameraState.camera},history:{back:true,forward:true,savedUrlRestored:true,state:savedState},legacy,captures,renderSettlements,
    valueValidation:'not_assessed',limitations:['Automated native interaction evidence does not establish user comprehension or user value.','Architecture references retain imported metadata; no historical applicability or source acceptance is inferred.','Shared URL restoration compares exact workspace fields and native renderer camera numbers.','Same engine and cartographic projection comparison, not independent renderer-adapter proof.','Named controls and native input only; not a complete assistive technology audit.']};
}

async function main() {
  const options=argumentsFor(process.argv);await mkdir(options.output,{recursive:true});
  const deadline=Date.now()+options.timeoutMs;
  let server=null,browser=null,cdp=null,browserLog='';
  const profile=await mkdtemp(join(tmpdir(),'artemis-unified-chrome-'));
  try {
    if(options.artifact)server=await localServer(options.expectedArtifact);
    const url=options.url || server.url,base=new URL('../',url);
    const byteVerification=await verifyBytes(options,base,deadline);
    const expectedBundle=JSON.parse(await readFile(join(options.expectedArtifact,'globe/unified-bundle.json'),'utf8'));
    browser=spawn(options.browser,['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--force-prefers-reduced-motion=reduce','--remote-debugging-port=0',`--user-data-dir=${profile}`,`--window-size=${options.width},${options.height}`,'about:blank'],{stdio:['ignore','ignore','pipe']});
    browser.stderr.on('data',chunk=>{browserLog=(browserLog+chunk).slice(-20000);});
    const port=await waitForDevToolsPort(profile,browser,deadline),endpoint=await waitForPageEndpoint(port,deadline);cdp=await connectCdp(endpoint,deadline);await cdp.send('Page.enable');await cdp.send('Runtime.enable');
    const scenario=await runScenario(cdp,options,url,deadline,expectedBundle);
    const report={...scenario,artifactVerification:{scope:'checked metadata and common input bundle at both registered entries; full release files separately checked by verify_public_artifact.py',files:byteVerification},provenance:{evidenceKind:'automated_native_browser_check',checkoutCommit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),recordedAtUtc:new Date().toISOString(),browser:await cdp.send('Browser.getVersion'),requestedWindow:{width:options.width,height:options.height},runnerSha256:sha256(await readFile(fileURLToPath(import.meta.url))),sharedTransportSha256:sha256(await readFile(new URL('./capture_globe_browser_evidence.mjs',import.meta.url))),bundleSha256:sha256(await readFile(join(options.expectedArtifact,'globe/unified-bundle.json'))),workflowRunUrl:process.env.GITHUB_RUN_ID?`https://github.com/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}`:null,workflowRunAttempt:process.env.GITHUB_RUN_ATTEMPT || null,live:!!options.url}};
    await writeFile(join(options.output,'report.json'),JSON.stringify(report,null,2)+'\n');process.stdout.write(JSON.stringify(report)+'\n');
  } catch(error) {
    if(cdp)await Promise.race([Promise.allSettled([evaluate(cdp,'document.documentElement.outerHTML').then(dom=>writeFile(join(options.output,'failure.html'),dom)),cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false}).then(image=>writeFile(join(options.output,'failure.png'),Buffer.from(image.data,'base64')))]),delay(3000)]);
    if(browserLog)await writeFile(join(options.output,'browser.log'),browserLog);throw error;
  } finally {
    cdp?.close();if(browser&&browser.exitCode===null){const exited=new Promise(resolve=>browser.once('exit',resolve));browser.kill('SIGTERM');await Promise.race([exited,delay(2000)]);}
    if(server){server.process.kill('SIGTERM');await writeFile(join(options.output,'server.log'),server.log());}
    await rm(profile,{recursive:true,force:true,maxRetries:5,retryDelay:100});
  }
}

export { argumentsFor, verifyBytes, contextReplaced, sameState };
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))main().catch(error=>{process.stderr.write((error?.stack || error)+'\n');process.exitCode=1;});
