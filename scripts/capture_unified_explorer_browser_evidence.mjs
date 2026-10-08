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
// Ownership routing describes visible mobile UI only; helpers still dispatch
// native input and never make hidden controls visible or mutate canonical state.
const mobileControlOwner = selector => /^#(?:view-|language-)/.test(selector) ? 'settings' : /^#layer-/.test(selector) ? 'layers' : /^#(?:record-|clear-search|search-)/.test(selector) ? 'records' : /^#(?:mode-|period-)/.test(selector) ? 'calendar' : null;
const mobileYearControl = id => ({'time-start':'mobile-range-start','time-end':'mobile-range-end','cursor-year':'mobile-cursor-year'})[id] || null;
function wheelKeys(value,min,max) {
  check(Number.isInteger(value)&&Number.isInteger(min)&&Number.isInteger(max)&&value>=min&&value<=max,'native wheel target outside exposed bounds');
  const lower=value-min<=max-value,delta=lower?value-min:max-value;
  return [lower?'Home':'End',...Array(Math.floor(delta/10)).fill(lower?'PageUp':'PageDown'),...Array(delta%10).fill(lower?'ArrowUp':'ArrowDown')];
}
// Deliberately unavailable Wikimedia endpoints make this an offline visitor proof.
const WIKIMEDIA_BLOCKED_URLS=['*://*.wikidata.org/*','*://wikidata.org/*','*://*.wikipedia.org/*','*://wikipedia.org/*','*://*.wikimedia.org/*'];
const isWikimediaRequest=url=>{try{return /(^|\.)(wikidata|wikipedia|wikimedia)\.org$/.test(new URL(url).hostname);}catch{return false;}};


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
  const base=new URL('../',url),captures=[],actions=[],checks=[],renderSettlements=[],placeAnchorChecks=[],catalogChecks=[],mobileChecks=[],networkDocuments=[];
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
  async function networkSnapshot() {
    const current=await evaluate(cdp,`({url:location.href,attempts:window.__ARTEMIS_BROWSER_REQUESTS||[],resources:performance.getEntriesByType('resource').map(entry=>entry.name)})`);
    check(!current.attempts.some(isWikimediaRequest)&&!current.resources.some(isWikimediaRequest),'visitor attempted live Wikimedia request');
    networkDocuments.push(current);
  }
  async function navigate(destination) {
    await networkSnapshot();
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
  async function mobile() {return evaluate(cdp,"matchMedia('(max-width:640px), (max-width:960px) and (max-height:500px)').matches");}
  async function expose(selector) {
    if(!await mobile())return;
    const owner=mobileControlOwner(selector);
    if(owner==='calendar') {if(!await evaluate(cdp,"document.getElementById('time-dock').dataset.expanded==='true'"))await click('#dock-toggle');}
    else if(owner&&await evaluate(cdp,'document.getElementById(\"workspace-header\").dataset.headerPanel')!==owner)await click('#mobile-'+owner);
  }
  async function collapseMobile() {
    if(!await mobile())return;
    if(await evaluate(cdp,"Boolean(document.getElementById('workspace-header').dataset.headerPanel)"))await click('#header-close');
    if(await evaluate(cdp,"document.getElementById('time-dock').dataset.expanded==='true'"))await click('#dock-toggle');
  }
  async function click(selector,keyboard=false) {
    await expose(selector);
    const point=await evaluate(cdp,`(() => {const n=document.querySelector(${JSON.stringify(selector)});if(!n)throw new Error('Missing control '+${JSON.stringify(selector)});n.scrollIntoView({block:'nearest'});n.focus({preventScroll:true});const b=n.getBoundingClientRect(),x=b.x+b.width/2,y=b.y+b.height/2;if(n.disabled||!b.width||!b.height||!n.contains(document.elementFromPoint(x,y)))throw new Error('Obstructed control '+${JSON.stringify(selector)});if(document.activeElement!==n)throw new Error('Control focus failed');return {x,y};})()`);
    if(keyboard)await key(' ','Space',32);
    else{await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...point});await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...point});await settle();}
    await stable(selector);return point;
  }
  async function number(id,value) {
    const wheel=mobileYearControl(id);
    if(await mobile()&&wheel) {
      const bounds=await evaluate(cdp,`(() => {const n=document.getElementById(${JSON.stringify(wheel)});if(!n?.checkVisibility({checkVisibilityCSS:true})||n.getAttribute('aria-disabled')==='true')throw new Error('Unavailable visible mobile year wheel');n.focus({preventScroll:true});return {min:Number(n.getAttribute('aria-valuemin')),max:Number(n.getAttribute('aria-valuemax'))};})()`);
      const codes={Home:36,End:35,PageUp:33,PageDown:34,ArrowUp:38,ArrowDown:40};
      for(const name of wheelKeys(value,bounds.min,bounds.max))await key(name,name,codes[name],0,true);
      await settle();
      check(await evaluate(cdp,`Number(document.getElementById(${JSON.stringify(wheel)}).getAttribute('aria-valuenow'))`)===value,'mobile native wheel did not reach requested year');
      if(!await evaluate(cdp,"document.getElementById('mobile-apply').disabled"))await click('#mobile-apply');
    } else {
      await evaluate(cdp,`(() => {const n=document.getElementById(${JSON.stringify(id)});if(!n?.checkVisibility({checkVisibilityCSS:true})||n.disabled)throw new Error('Unavailable native year input');n.focus();if(document.activeElement!==n)throw new Error('Year input focus failed');})()`);
      await key('a','KeyA',65,2);await cdp.send('Input.insertText',{text:String(value)});await key('Tab','Tab',9);
    }
    await stable(id+'='+value);
  }
  async function layer(id,enabled) {if(await evaluate(cdp,`document.getElementById('layer-'+${JSON.stringify(id)}).checked`)!==enabled)await click('#layer-'+id,true);}
  async function select(itemId) {
    async function available() {
      await expose('#record-select');
      return evaluate(cdp,`(() => {const n=document.getElementById('record-select');if(!n.checkVisibility({checkVisibilityCSS:true}))throw new Error('Native record selector is hidden');n.scrollIntoView({block:'nearest'});n.focus({preventScroll:true});if(document.activeElement!==n)throw new Error('Native record selector cannot receive focus');const target=[...n.options].findIndex(o=>o.value===${JSON.stringify(itemId)});if(target<0)throw new Error('Item not available in native selection');return {target,current:n.selectedIndex,count:n.options.length};})()`);
    }
    let indices=await available(),steps=0;
    // Closed native selects commit each Arrow. The responsive UI closes the
    // owning panel on a completed selection. Reopen it through its real button
    // before EVERY subsequent key instead of dispatching into a hidden select.
    while(indices.current!==indices.target) {
      check(steps++<indices.count+1,'native record selection exhausted bounded steps');
      const before=indices.current;
      if(before<0)await key('Home','Home',36);
      else {const down=indices.target>before;await key(down?'ArrowDown':'ArrowUp',down?'ArrowDown':'ArrowUp',down?40:38);}
      const next=await evaluate(cdp,`(() => {const n=document.getElementById('record-select');return {target:[...n.options].findIndex(o=>o.value===${JSON.stringify(itemId)}),current:n.selectedIndex,count:n.options.length,value:n.value,selected:window.__ARTEMIS_EXPLORER.state.selectedItemId,panel:document.getElementById('workspace-header').dataset.headerPanel,active:document.activeElement?.id,url:location.href};})()`);
      check(next.target>=0&&Math.abs(next.target-next.current)<Math.abs(indices.target-before),'native record selector made no progress '+JSON.stringify({expected:itemId,before,...next}));
      indices=next;if(indices.current!==indices.target)indices=await available();
    }
    const state=await snapshot();check(state.state.selectedItemId===itemId&&!state.inspectorHidden,'native record selector lost identity '+JSON.stringify({expected:itemId,actual:state.state.selectedItemId,inspectorHidden:state.inspectorHidden,indices,url:state.url}));await stable('select '+itemId);
  }
  async function search(value) {
    await expose('#record-search');
    await evaluate(cdp,`(() => {const input=document.getElementById('record-search');input.focus({preventScroll:true});if(document.activeElement!==input)throw new Error('Search input cannot receive focus');})()`);
    await key('a','KeyA',65,2);await key('Backspace','Backspace',8);
    if(value)await cdp.send('Input.insertText',{text:value});await settle();await stable('search '+value);
    return evaluate(cdp,`({values:[...document.getElementById('record-select').options].map(option=>option.value).filter(Boolean),status:document.getElementById('search-status').textContent,query:document.getElementById('record-search').value})`);
  }
  async function clearSearch() {
    const visible=await evaluate(cdp,"document.getElementById('clear-search').checkVisibility({checkVisibilityCSS:true})");
    if(visible)await click('#clear-search',true);
    else {check(await mobile(),'desktop clear search control hidden');await search('');}
  }
  async function disclose(id) {
    if(!await evaluate(cdp,`document.getElementById(${JSON.stringify(id)}).open`))await click('#'+id+' > summary',true);
    check(await evaluate(cdp,`document.getElementById(${JSON.stringify(id)}).open`),'native disclosure failed '+id);
  }
  async function close() {if(!await evaluate(cdp,"document.getElementById('inspector').hidden"))await click('#close-details');}
  async function membership(expected,reason) {
    await idle(reason);const current=await snapshot();
    const actual=Object.fromEntries(['leonardo','roman','architecture',...(Object.hasOwn(expected,'catalog')?['catalog']:[])].map(layer=>[layer,current.visible.filter(i=>i.layer===layer).length]));
    check(JSON.stringify(actual)===JSON.stringify(expected),reason+' membership mismatch '+JSON.stringify(actual));
    checks.push({case:reason,state:current.state,counts:actual,itemIds:current.visible.map(i=>i.itemId),documentTimeOrigin:current.origin});return current;
  }
  async function placeAnchors(reason) {
    await idle('Place anchors '+reason);
    const actual=await evaluate(cdp,`(async()=>{
      const r=window.__ARTEMIS_EXPLORER,source=await r.map.getSource('workspace-features').getData(),mapBounds=r.map.getContainer().getBoundingClientRect();
      const nativePoint=f=>({id:f.id,renderKey:f.properties.render_key,place:f.properties.place_ref,state:{selected:f.state?.selected,current:f.state?.current}});
      return {visible:r.visibleItems.filter(i=>i.layer_id==='leonardo').map(i=>i.item_id),state:r.state,
        sourceRenderKeys:source.features.map(f=>({id:f.id,renderKey:f.properties.render_key,kind:f.properties.kind})),
        nativeChronology:r.map.getProjection().type==='mercator'?r.map.queryRenderedFeatures({layers:['workspace-chronology']}).map(f=>({id:f.id,renderKey:f.properties.render_key,emphasis:f.state?.emphasis})):[],
        anchors:[...document.querySelectorAll('.workspace-place-marker')].map(n=>{
          const feature=source.features.find(f=>f.id==='place-anchor:'+n.dataset.placeRef),bounds=n.getBoundingClientRect(),style=getComputedStyle(n),pixel=feature&&r.map.project(feature.geometry.coordinates);
          return {place:n.dataset.placeRef,name:n.querySelector('.place-name')?.textContent,count:n.querySelector('.place-count')?.textContent,aria:n.getAttribute('aria-label'),pressed:n.getAttribute('aria-pressed'),selected:n.classList.contains('is-selected'),current:n.classList.contains('is-current'),labelVisible:getComputedStyle(n.querySelector('.place-label')).visibility!=='hidden',
            positionEligible:Boolean(feature&&pixel&&Number.isFinite(pixel.x)&&Number.isFinite(pixel.y)&&pixel.x>=0&&pixel.y>=0&&pixel.x<=mapBounds.width&&pixel.y<=mapBounds.height&&bounds.width>0&&bounds.height>0&&style.visibility!=='hidden'&&style.display!=='none'&&Number(style.opacity)>0),
            nativePoints:pixel?r.map.queryRenderedFeatures(pixel,{layers:['workspace-points']}).filter(f=>f.properties.place_ref===n.dataset.placeRef).map(nativePoint):[],
            center:{x:bounds.left+bounds.width/2,y:bounds.top+bounds.height/2},projected:pixel?{x:mapBounds.left+pixel.x,y:mapBounds.top+pixel.y}:null};
        }),
        points:source.features.filter(f=>f.properties.layer_id==='leonardo'&&f.geometry.type==='Point').map(f=>({id:f.id,properties:f.properties,coordinates:f.geometry.coordinates,state:r.map.getFeatureState({source:'workspace-features',id:f.id})})),
        chronology:source.features.filter(f=>f.properties.kind==='chronology').map(f=>({id:f.id,properties:f.properties,coordinates:f.geometry.coordinates,state:r.map.getFeatureState({source:'workspace-features',id:f.id})})),
        chronologyCues:[...document.querySelectorAll('.workspace-chronology-cue')].map(n=>({id:n.dataset.transitionId,emphasis:Number(n.dataset.emphasis),opacity:Number(getComputedStyle(n.firstChild).opacity)})),
        markerPaint:r.map.getPaintProperty('workspace-points','circle-radius'),chronologyPaint:r.map.getPaintProperty('workspace-chronology','line-opacity')};
    })()`,true);
    check(actual.sourceRenderKeys.every(feature=>typeof feature.id==='string'&&feature.renderKey===feature.id)&&new Set(actual.sourceRenderKeys.map(feature=>feature.renderKey)).size===actual.sourceRenderKeys.length,reason+' renderer feature keys are missing, duplicated or disconnected from existing source IDs');
    const groups=new Map();
    for(const presence of expectedBundle.leonardo.lifePath.presences.filter(p=>actual.visible.includes(p.presence_item_id))){if(!groups.has(presence.place_ref))groups.set(presence.place_ref,[]);groups.get(presence.place_ref).push(presence);}
    check(actual.anchors.length===groups.size&&actual.points.length===groups.size,reason+' duplicated/omitted a Place anchor');
    check(new Set(actual.anchors.map(a=>a.place)).size===groups.size,reason+' duplicated Place IDs');
    for(const [place,episodes] of groups){
      const anchor=actual.anchors.find(a=>a.place===place),point=actual.points.find(p=>p.properties.place_ref===place);
      check(anchor&&point,reason+' missing existing Place '+place);
      if(anchor.positionEligible){
        check(anchor.projected&&Number.isFinite(anchor.projected.x)&&Number.isFinite(anchor.projected.y)&&Math.hypot(anchor.center.x-anchor.projected.x,anchor.center.y-anchor.projected.y)<=2,reason+' DOM Place anchor displaced from native map coordinate '+place+' '+JSON.stringify({center:anchor.center,projected:anchor.projected}));
        check(anchor.nativePoints.length>0,reason+' native point query omitted a visible Place '+place);
        for(const rendered of anchor.nativePoints){check(rendered.id===point.id&&rendered.renderKey===point.id,reason+' rendered Place ID disconnected from source feature '+place+' '+JSON.stringify({sourceId:point.id,renderedId:rendered.id}));check(typeof rendered.state.selected==='boolean'&&typeof rendered.state.current==='boolean'&&rendered.state.selected===point.state.selected&&rendered.state.current===point.state.current,reason+' rendered selected/current state disconnected from source feature '+place);}
      }
      check(anchor.name===episodes[0].place_label&&anchor.aria?.includes(episodes[0].place_label),reason+' lost Place name/accessibility');
      check(point.id==='place-anchor:'+place&&JSON.stringify(point.coordinates)===JSON.stringify(episodes[0].coordinates),reason+' moved a fixed Place reference');
      check(point.properties.episode_count===episodes.length,reason+' episode count does not match visible Presences');
      const itemIds=typeof point.properties.presence_item_ids==='string'?JSON.parse(point.properties.presence_item_ids):point.properties.presence_item_ids;check(JSON.stringify([...itemIds].sort())===JSON.stringify(episodes.map(p=>p.presence_item_id).sort()),reason+' Place anchor collapsed/substituted Presence IDs');
      if(episodes.length>1)check(anchor.count?.includes(String(episodes.length)),reason+' repeated Place count hidden from label');
      if(episodes.some(p=>p.presence_item_id===actual.state.selectedItemId)){check(anchor.selected&&anchor.pressed==='true'&&anchor.labelVisible&&point.state.selected===true,reason+' selected Place emphasis missing');}
    }
    check(!groups.size||actual.anchors.some(anchor=>anchor.positionEligible),reason+' no visible projected DOM Place anchor was checked');
    const policy=expectedBundle.leonardo.lifePath.route_policy;
    check(policy.historical_route_geometry_permitted===false&&policy.chronological_connector_is_route===false,'chronology policy promoted a route');
    check(actual.chronology.every(line=>line.properties.route_geometry===null),'chronology introduced historical route geometry');
    const selectedEpisode=expectedBundle.leonardo.lifePath.presences.find(p=>p.presence_item_id===actual.state.selectedItemId);
    const visibleEpisodes=expectedBundle.leonardo.lifePath.presences.filter(p=>actual.visible.includes(p.presence_item_id)).sort((a,b)=>a.index-b.index);
    const currentEpisode=actual.state.mode==='scrub'?visibleEpisodes.at(-1):null,emphasizedEpisode=selectedEpisode||currentEpisode;
    const incoming=emphasizedEpisode&&expectedBundle.leonardo.lifePath.transitions.find(t=>t.to_presence_ref===emphasizedEpisode.presence_id&&visibleEpisodes.some(p=>p.presence_id===t.from_presence_ref));
    for(const line of actual.chronology){
      const transition=expectedBundle.leonardo.lifePath.transitions.find(t=>t.transition_id===line.id);
      const expected=emphasizedEpisode&&(incoming?transition===incoming:transition.from_presence_ref===emphasizedEpisode.presence_id)?selectedEpisode?2:1:0;
      check(line.state.emphasis===expected,reason+' selected/current chronology policy changed for '+line.id);
    }
    for(const rendered of actual.nativeChronology){
      const line=actual.chronology.find(line=>line.id===rendered.id);
      check(line&&rendered.renderKey===line.id,reason+' rendered chronology ID disconnected from source feature '+JSON.stringify(rendered));
      check(typeof rendered.emphasis==='number'&&rendered.emphasis===line.state.emphasis,reason+' rendered chronology emphasis disconnected from source state '+rendered.id);
    }
    check(actual.chronologyCues.length===actual.chronology.filter(line=>JSON.stringify(line.coordinates[0])!==JSON.stringify(line.coordinates[1])).length,reason+' non-route chronology cues missing');
    for(const cue of actual.chronologyCues){const line=actual.chronology.find(line=>line.id===cue.id);check(line&&cue.emphasis===line.state.emphasis&&cue.opacity===(cue.emphasis ? .95 : .12),reason+' chronology cue presentation does not match native emphasis');}
    for(const point of actual.points){const anchor=actual.anchors.find(a=>a.place===point.properties.place_ref),selected=point.properties.place_ref===selectedEpisode?.place_ref,current=point.properties.place_ref===currentEpisode?.place_ref;check(point.state.selected===selected&&point.state.current===current&&anchor.selected===selected&&anchor.current===current,reason+' stale Place selected/current emphasis');}
    check(JSON.stringify(actual.markerPaint).includes('feature-state')&&JSON.stringify(actual.chronologyPaint).includes('feature-state'),reason+' native styles ignore selected/current presentation state');
    if(actual.state.mode==='scrub'&&actual.visible.length){
      const latest=currentEpisode,anchor=actual.anchors.find(a=>a.place===latest.place_ref),point=actual.points.find(p=>p.properties.place_ref===latest.place_ref);
      check(anchor?.current&&point?.state.current===true,reason+' current accumulated Place emphasis missing');
      if(!selectedEpisode&&actual.chronology.length)check(actual.chronology.some(line=>line.state.emphasis===1),reason+' current chronology emphasis missing');
    }
    placeAnchorChecks.push({case:reason,presenceCount:actual.visible.length,placeCount:groups.size,anchors:actual.anchors,pointStates:actual.points.map(p=>({place:p.properties.place_ref,state:p.state})),pointCoordinatesSha256:sha256(actual.points.map(p=>({place:p.properties.place_ref,coordinates:p.coordinates}))),sourceRenderKeys:actual.sourceRenderKeys,chronology:actual.chronology,nativeChronology:actual.nativeChronology,chronologyCues:actual.chronologyCues,paint:{markers:actual.markerPaint,chronology:actual.chronologyPaint}});
  }
  async function capture(suffix,{keepMobileOpen=false}={}) {
    if(!keepMobileOpen)await collapseMobile();
    await idle('capture '+suffix);
    const layout=await evaluate(cdp,`(() => {
      const visible=n=>{if(!n?.checkVisibility({checkVisibilityCSS:true}))return false;const b=n.getBoundingClientRect();return b.width>0&&b.height>0&&b.left>=0&&b.top>=0&&b.right<=innerWidth+1&&b.bottom<=innerHeight+1;};
      const mobile=matchMedia('(max-width:640px), (max-width:960px) and (max-height:500px)').matches;
      const ids=mobile?['workspace-header','record-search','mobile-layers','mobile-records','mobile-settings','time-dock','dock-toggle',...(window.__ARTEMIS_EXPLORER.state.mode==='scrub'?['mobile-cursor-year','time-cursor']:['mobile-range-start','mobile-range-end','range-start-handle','range-end-handle'])]:['workspace-header','layer-controls','view-globe','view-map','language-en','language-ru','record-search','clear-search','record-select','time-dock'];
      for(const id of ids)if(!visible(document.getElementById(id)))throw new Error('Control outside viewport '+id);
      if(mobile&&!${keepMobileOpen})for(const id of ['layer-controls','view-globe','view-map','language-en','language-ru','record-select','time-start','time-end','cursor-year'])if(visible(document.getElementById(id)))throw new Error('Collapsed mobile surface exposed desktop control '+id);
      if(document.documentElement.scrollWidth>innerWidth+1)throw new Error('Horizontal overflow');
      const h=document.getElementById('workspace-header').getBoundingClientRect(),t=document.getElementById('time-dock').getBoundingClientRect();if(h.bottom>t.top)throw new Error('Header overlaps shared time controls');
      const r=window.__ARTEMIS_EXPLORER,s=r.state;
      if(document.getElementById('view-'+s.presentationView).getAttribute('aria-pressed')!=='true'||document.getElementById('language-'+s.language).getAttribute('aria-pressed')!=='true')throw new Error('Projection/language aria state differs');
      if(r.map.getProjection().type!==(s.presentationView==='map'?'mercator':'globe'))throw new Error('Native projection mismatch');
      return {width:innerWidth,height:innerHeight,headerBottom:h.bottom,timeTop:t.top,mapGap:t.top-h.bottom,mobile,headerPanel:document.getElementById('workspace-header').dataset.headerPanel||null,dockExpanded:document.getElementById('time-dock').dataset.expanded==='true',language:s.language,view:s.presentationView};
    })()`);
    const screenshot=join(options.output,suffix+'.png'),dom=join(options.output,suffix+'.html');
    const png=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});await writeFile(screenshot,Buffer.from(png.data,'base64'));await writeFile(dom,await evaluate(cdp,'document.documentElement.outerHTML'));
    captures.push({case:suffix,...layout,screenshot,dom,screenshotSha256:sha256(await readFile(screenshot)),domSha256:sha256(await readFile(dom))});
  }
  async function mobileSourceScrollClearance() {
    if(!await mobile())return;
    await collapseMobile();const before=await snapshot();
    const point=await evaluate(cdp,`(() => {const n=document.getElementById('inspector'),b=n.getBoundingClientRect(),x=b.x+b.width/2,y=b.y+Math.min(b.height/2,120),hit=document.elementFromPoint(x,y);if(n.hidden||!n.contains(hit))throw new Error('Native source inspector scroll surface obstructed');return {x,y};})()`);
    async function scrollToEdge(delta,bottom) {
      await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',...point});await settle();
      await cdp.send('Input.dispatchMouseEvent',{type:'mouseWheel',...point,deltaY:delta,deltaX:0});
      const scrollDeadline=Math.min(deadline,Date.now()+2000);let metrics=null;
      do {metrics=await evaluate(cdp,`(() => {const n=document.getElementById('inspector'),last=document.getElementById('selection-input').lastElementChild,t=document.getElementById('mobile-tools').getBoundingClientRect();return {top:n.scrollTop,maximum:n.scrollHeight-n.clientHeight,lastBottom:last?.getBoundingClientRect().bottom,toolsTop:t.top,toolsBottom:t.bottom};})()`);if(bottom?metrics.top>=metrics.maximum-1:metrics.top<=1)break;await delay(25);}while(Date.now()<scrollDeadline);
      check(bottom?metrics.top>=metrics.maximum-1:metrics.top<=1,'native inspector wheel did not reach scroll edge '+JSON.stringify({bottom,point,metrics}));return metrics;
    }
    const end=await scrollToEdge(100000,true);
    check(Number.isFinite(end.lastBottom)&&end.lastBottom<=end.toolsTop-4,'mobile tools obscure final source-native text '+JSON.stringify(end));
    await capture('mobile-source-card-scroll-end',{keepMobileOpen:true});
    await scrollToEdge(-100000,false);const after=await snapshot();
    check(sameState(before.state,after.state)&&sameState(before.camera,after.camera)&&before.card===after.card,'native inspector scrolling changed canonical card or camera');await stable('mobile source card scroll clearance');
    mobileChecks.push({case:'source-native card scroll-end clearance',nativePointerWheel:true,lastContentBottom:end.lastBottom,toolsTop:end.toolsTop,maximum:end.maximum,scrollEnd:end.top,lastTextUnobstructed:true,canonicalStateUnchanged:true});
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

  async function mobileRegression() {
    if(!await mobile())return;
    await collapseMobile();const initial=await snapshot();
    const layout=await evaluate(cdp,`(() => {const h=document.getElementById('workspace-header').getBoundingClientRect(),t=document.getElementById('time-dock').getBoundingClientRect();return {width:innerWidth,height:innerHeight,header:h.height,dock:t.height,mapGap:t.top-h.bottom,overflow:document.documentElement.scrollWidth>innerWidth+1};})()`);
    check(!layout.overflow&&layout.mapGap>=layout.height*.4,'collapsed mobile UI did not leave usable map clearance');
    for(const panel of ['layers','records','settings']) {
      await click('#mobile-'+panel);if(panel==='layers')await capture('mobile-layers-panel',{keepMobileOpen:true});check(await evaluate(cdp,"document.getElementById('workspace-header').dataset.headerPanel")===panel,'mobile panel did not open '+panel);
      await click('#header-close');const after=await snapshot();check(sameState(initial.state,after.state)&&sameState(initial.camera,after.camera),'mobile panel toggle changed canonical state or camera');
    }
    const wheel='mobile-range-start';
    async function focusWheel(id=wheel) {await evaluate(cdp,`(() => {const n=document.getElementById(${JSON.stringify(id)});if(!n.checkVisibility({checkVisibilityCSS:true})||n.getAttribute('role')!=='spinbutton'||n.tagName==='INPUT'||n.isContentEditable)throw new Error('Mobile year editor opens a text input');n.focus({preventScroll:true});if(document.activeElement!==n)throw new Error('Mobile wheel focus failed');})()`);}
    async function draftUncommitted(reason) {const after=await snapshot();check(after.url===initial.url&&sameState(initial.state,after.state)&&sameState(initial.camera,after.camera)&&sameState(initial.visible,after.visible),reason+' changed canonical state before Apply');}
    await focusWheel();await key('End','End',35);await key('ArrowUp','ArrowUp',38);
    check(await evaluate(cdp,`document.getElementById('${wheel}').getAttribute('aria-valuenow')===document.getElementById('${wheel}').getAttribute('aria-valuemax')`),'mobile upper boundary escaped');
    await key('Home','Home',36);await key('ArrowDown','ArrowDown',40);
    check(await evaluate(cdp,`document.getElementById('${wheel}').getAttribute('aria-valuenow')===document.getElementById('${wheel}').getAttribute('aria-valuemin')`),'mobile lower boundary escaped');
    await draftUncommitted('bounded wheel draft');await capture('mobile-expanded-staged-boundary',{keepMobileOpen:true});await click('#mobile-cancel');
    check(await evaluate(cdp,`Number(document.getElementById('${wheel}').getAttribute('aria-valuenow'))`)===initial.state.startYear,'Cancel retained a staged year');
    await focusWheel();const point=await evaluate(cdp,`(() => {const n=document.getElementById('${wheel}');n.scrollIntoView({block:'nearest'});const b=n.querySelector('.wheel-value').getBoundingClientRect(),x=b.x+b.width/2,y=b.y+b.height/2,hit=document.elementFromPoint(x,y);if(!n.contains(hit))throw new Error('Native wheel center obstructed '+JSON.stringify({x,y,hit:hit?.id||hit?.className}));return {x,y};})()`);
    await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',...point});await settle();
    await cdp.send('Input.dispatchMouseEvent',{type:'mouseWheel',...point,deltaY:60,deltaX:0});
    // Wheel input travels through the compositor; two animation frames alone
    // need not mean that the single native event has reached its DOM handler.
    const wheelDeadline=Math.min(deadline,Date.now()+2000);let staged=null;
    do {staged=await evaluate(cdp,`Number(document.getElementById('${wheel}').getAttribute('aria-valuenow'))`);if(staged===initial.state.startYear+1)break;await delay(25);}while(Date.now()<wheelDeadline);
    await settle();
    const observedWheelEvents=await evaluate(cdp,'window.__ARTEMIS_BROWSER_WHEEL_EVENTS||[]');
    check(staged===initial.state.startYear+1,'native wheel scroll did not stage one year '+JSON.stringify({point,expected:initial.state.startYear+1,actual:staged,observedWheelEvents}));
    check(observedWheelEvents.some(event=>event.trusted&&event.wheel===wheel&&event.deltaY===60),'native wheel proof lacks a trusted event delivered to the visible spinbutton');
    check(await evaluate(cdp,`Number(document.getElementById('range-start-handle').value)`)===initial.state.startYear+1,'staged mobile wheel did not preview timeline handle');await draftUncommitted('native wheel scroll');await capture('mobile-expanded-staged-year',{keepMobileOpen:true});await click('#mobile-apply');
    check((await snapshot()).state.startYear===initial.state.startYear+1,'Apply did not commit selected year');await number('time-start',initial.state.startYear);
    // Native pointer movement inside the year wheel is separate from dock drag.
    await focusWheel();const yearPoint=await evaluate(cdp,`(() => {const b=document.querySelector('#${wheel} .wheel-value').getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2};})()`);
    await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...yearPoint});
    await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',button:'left',buttons:1,x:yearPoint.x,y:yearPoint.y-36});
    await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:yearPoint.x,y:yearPoint.y-36});await settle();
    check(await evaluate(cdp,`Number(document.getElementById('${wheel}').getAttribute('aria-valuenow'))`)===initial.state.startYear+2,'native vertical wheel drag did not stage two years');await click('#mobile-cancel');
    const handle=await evaluate(cdp,`(() => {const b=document.getElementById('dock-toggle').getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2};})()`);
    await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...handle});
    await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',button:'left',buttons:1,x:handle.x,y:handle.y+40});
    await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:handle.x,y:handle.y+40});await settle();
    check(await evaluate(cdp,"document.getElementById('time-dock').dataset.expanded==='false'"),'native downward handle drag did not collapse calendar');await stable('mobile wheel and dock native gestures');
    await click('#mode-scrub');await evaluate(cdp,"document.getElementById('time-cursor').focus({preventScroll:true})");await key('ArrowLeft','ArrowLeft',37);
    check((await snapshot()).state.cursorYear===initial.state.cursorYear-1,'native mobile scrub slider did not commit one year');await number('cursor-year',initial.state.cursorYear);await click('#mode-range');
    await evaluate(cdp,"document.getElementById('range-start-handle').focus({preventScroll:true})");await key('ArrowRight','ArrowRight',39);
    check((await snapshot()).state.startYear===initial.state.startYear+1,'native mobile interval slider did not commit one year');await number('time-start',initial.state.startYear);await collapseMobile();
    const after=await snapshot();check(sameState(initial.state,after.state)&&sameState(initial.camera,after.camera),'mobile regression did not restore initial semantic and camera state');
    mobileChecks.push({case:'compact calendar native interaction',layout,panels:['layers','records','settings'],draftChangesCanonicalState:false,draftChangesUrl:false,keyboardInputRequired:false,nativeWheelScroll:true,observedWheelEvents,nativeWheelDrag:true,yearBoundaries:true,cancel:true,apply:true,nativeDockDragCollapse:true,nativeScrub:true,nativeRange:true,sameMap:true});
  }

  await navigate(url);
  await mobileRegression();
  const readyCatalog=await membership({leonardo:11,roman:0,architecture:0,catalog:10},'fresh ready London catalog');
  check(readyCatalog.state.layers.includes('catalog'),'fresh entry did not enable catalog');
  const pilotLabel=await evaluate(cdp,"document.getElementById('layer-catalog').parentElement.textContent");
  check(/10/.test(pilotLabel)&&/London/.test(pilotLabel),'catalog did not disclose bounded pilot count and coverage');
  await capture('ready-catalog-default-en-globe');
  const catalog=expectedBundle.catalog.references;
  check(catalog.length===10&&new Set(catalog.map(row=>row.item_id)).size===10,'catalog cohort missing/duplicated');
  const first=catalog.find(reference=>reference.labels?.en&&reference.labels?.ru&&Object.values(reference.aliases||{}).flat().length);
  check(first,'cohort has no source-native RU/EN/alias record for native search proof');
  const firstRegistry=expectedBundle.registry.find(row=>row.item_id===first.item_id);
  check(firstRegistry?.kind==='catalog_reference'&&firstRegistry.interval===null,'catalog entered historical intervals');
  const nativeCatalog=await evaluate(cdp,`(async()=>{const source=await window.__ARTEMIS_EXPLORER.map.getSource('workspace-features').getData();return source.features.filter(feature=>feature.properties.layer_id==='catalog').map(feature=>({item:feature.properties.item_id,geometry:feature.geometry}));})()`,true);
  check(nativeCatalog.length===10,'native shared map source omitted catalog points');
  for(const feature of nativeCatalog){const reference=catalog.find(row=>row.item_id===feature.item);check(reference&&sameState(feature.geometry,reference.geometry),'catalog native geometry differs from preserved source point');}
  await select(first.item_id);
  const initialCard=await evaluate(cdp,`({title:document.getElementById('selection-title').textContent,facts:document.getElementById('selection-facts').textContent,revision:document.getElementById('catalog-revision-link')?.href,evidencePresent:Boolean(document.querySelector('#selection-evidence pre'))})`);
  check(initialCard.title===first.labels.en&&initialCard.revision===first.sources[0].url&&initialCard.evidencePresent,'catalog inspector failed to render its native title/source/evidence');
  for(const value of [...first.geometry.coordinates,first.coordinate_statement.mainsnak.datavalue.value.precision])check(initialCard.facts.includes(String(value)),'catalog primary facts lost literal coordinate/precision');
  await disclose('sources-disclosure');await disclose('evidence-disclosure');await disclose('input-disclosure');
  await mobileSourceScrollClearance();
  const catalogSelected=await snapshot(),beforeSearch=catalogSelected;
  const searchCases=[];
  const qid=first.item_id.split(':').at(-1);
  const labels=first.labels||firstRegistry.labels||{},aliases=first.aliases||firstRegistry.aliases||{};
  const textValue=value=>typeof value==='string'?value:value?.value;
  const en=textValue(labels.en)||firstRegistry.label,ru=textValue(labels.ru);
  const originalAliases=Object.values(aliases).flat().map(textValue).filter(value=>typeof value==='string'&&value);
  const alias=originalAliases.find(value=>value.normalize('NFD')!==value)||originalAliases[0];
  for(const [kind,query] of [['QID',qid],['English',en],...(ru?[['Russian',ru]]:[]),...(alias?[['alias',alias]]:[])]) {
    const results=await search(query.toUpperCase().normalize('NFD')),after=await snapshot();
    check(results.values.includes(first.item_id),'Unicode '+kind+' search lost catalog identity');
    check(sameState(beforeSearch.state,after.state)&&sameState(beforeSearch.camera,after.camera)&&sameState(beforeSearch.visible,after.visible)&&beforeSearch.card===after.card,'search changed canonical selection/time/camera/map records');
    searchCases.push({kind,query:query.toUpperCase().normalize('NFD'),matches:results.values});
  }
  check(searchCases.some(row=>row.kind==='Russian')&&searchCases.some(row=>row.kind==='alias'),'source-native RU and alias search were not exercised');
  const empty=await search('ARTEMIS-no-match-\u2603-zzzz'),emptyState=await snapshot();
  check(empty.values.length===0&&empty.status.trim().length>0&&!emptyState.inspectorHidden&&emptyState.state.selectedItemId===first.item_id,'empty search hid selection or lacked explicit status');
  await capture('catalog-empty-search-selection-retained-en-globe');
  await clearSearch();const cleared=await snapshot();
  check(await evaluate(cdp,"document.getElementById('record-search').value===''"),'clear action did not clear search');
  check(cleared.state.selectedItemId===first.item_id&&sameState(cleared.visible,beforeSearch.visible)&&cleared.card===beforeSearch.card,'clear action changed map or source selection');
  const allChooser=await evaluate(cdp,"[...document.getElementById('record-select').options].map(option=>option.value).filter(Boolean)");
  check(allChooser.length===21,'clear did not restore all visible chooser records');
  const sourceDetails=[];
  for(const reference of catalog) {
    await select(reference.item_id);await disclose('sources-disclosure');await disclose('input-disclosure');await disclose('evidence-disclosure');
    const details=await evaluate(cdp,`({title:document.getElementById('selection-title').textContent,scope:document.getElementById('selection-scope').textContent,revision:document.getElementById('catalog-revision-link')?.href,context:document.getElementById('catalog-context-link')?.href,input:document.getElementById('selection-input').textContent,evidence:JSON.parse(document.querySelector('#selection-evidence pre').textContent),card:document.getElementById('inspector').textContent})`);
    check(details.revision&&/^https:\/\/www\.wikidata\.org\//.test(details.revision)&&/oldid=\d+|revision\/\d+/.test(details.revision),'catalog primary revision link is not pinned');
    check(details.revision===reference.sources[0].url,'catalog revision link differs from pinned source revision');
    check(details.context===reference.wikipedia_urls.en,'catalog context link differs from literal source sitelink');
    check(details.context&&/^https:\/\/[a-z-]+\.wikipedia\.org\/wiki\//.test(details.context),'catalog primary Wikipedia context link missing');
    check(/modern|present-day/i.test(details.scope)&&/historical/i.test(details.scope),'catalog point meaning/unknown applicability absent');
    check(details.card.includes('CC0')&&details.input.includes('P625'),'catalog native coordinate/provenance not disclosed');
    const claims=details.evidence.claims;
    check(sameState(claims,reference.claims)&&sameState(details.evidence.evidence_links,reference.evidence_links),'catalog source-relative Claim/EvidenceLink changed in native disclosure');
    check(claims.length>0&&claims.every(claim=>claim.review_state==='draft'&&claim.confidence==='unknown'&&claim.evidence_state==='missing'),'catalog technical import promoted epistemic acceptance');
    const keyboardLinks=await evaluate(cdp,`['catalog-revision-link','catalog-context-link'].map(id=>{const link=document.getElementById(id);link.focus({preventScroll:true});if(document.activeElement!==link||link.tabIndex<0)throw new Error('Source link cannot receive keyboard focus');return {id,href:link.href};})`);
    sourceDetails.push({item:reference.item_id,title:details.title,revision:details.revision,context:details.context,claimIds:claims.map(claim=>claim.id),keyboardLinks});
  }
  await select(first.item_id);await disclose('sources-disclosure');await disclose('evidence-disclosure');await disclose('input-disclosure');
  const unfocused=await snapshot();await click('#focus-selection',true);await idle('explicit catalog focus');const focused=await snapshot();
  check(!sameState(unfocused.camera,focused.camera),'explicit catalog focus did not move camera');
  const previous={...unfocused.state},next={...focused.state};delete previous.camera;delete next.camera;
  check(sameState(previous,next),'catalog focus changed historical semantics');
  const coordinates=first.geometry.coordinates;
  check(Math.hypot(focused.camera.center[0]-coordinates[0],focused.camera.center[1]-coordinates[1])<1e-7,'catalog focus uses another coordinate');
  for(const lang of ['en','ru']) {await click('#language-'+lang);
    const translatedFacts=await evaluate(cdp,`({title:document.getElementById('selection-title').textContent,facts:document.getElementById('selection-facts').textContent,revision:document.getElementById('catalog-revision-link')?.href})`);
    check(translatedFacts.title===first.labels[lang]&&translatedFacts.revision===first.sources[0].url&&translatedFacts.facts.includes(String(first.geometry.coordinates[0])),'catalog language change lost native primary facts');
    for(const mode of ['globe','map']) {await view(mode);await capture('catalog-selected-source-'+lang+'-'+mode);}}

  const fallback=catalog.find(reference=>!(reference.labels||{}).ru);
  if(fallback) {await select(fallback.item_id);check(/\(en\)/.test((await snapshot()).card),'missing RU label did not disclose English fallback');await capture('catalog-language-fallback-ru-map');}
  await click('#language-en');await select(first.item_id);
  const catalogHistoryBefore=(await snapshot()).state;await layer('architecture',true);const catalogHistoryMiddle=(await snapshot()).state;
  await view('globe');const catalogHistoryAfter=(await snapshot()).state;
  await history(-1,catalogHistoryMiddle);await history(-1,catalogHistoryBefore);await history(1,catalogHistoryMiddle);await history(1,catalogHistoryAfter);
  await click('#period-all');const allLayers=await membership({leonardo:11,roman:3,architecture:31,catalog:10},'all four layers55records');
  check(allLayers.visible.length===55,'four layers did not preserve exact legacy45pluscatalog10');
  await number('time-start',91);await number('time-end',91);check((await snapshot()).visible.filter(row=>row.layer==='catalog').length===10,'catalog excluded by historical time');
  await layer('catalog',false);check((await snapshot()).state.selectedItemId===null,'hiding selected catalog layer retained selection');await layer('catalog',true);
  catalogChecks.push({case:'ready catalog search source focus and shared history',cohort:catalog.map(row=>row.item_id),nativeCatalogGeometrySha256:sha256(nativeCatalog),searchCases,emptySearch:{query:empty.query,status:empty.status,selectionRetained:true},clearedChooserCount:allChooser.length,sourceDetails,focus:{before:unfocused.camera,after:focused.camera},fallbackItem:fallback?.item_id||null,fallbackEvidence:fallback?'native source fallback checked':'not applicable: all ten source records contain RU and EN labels; fallback mechanism covered in owned behavior tests',allLayersCount:allLayers.visible.length,catalogParticipatesInHistoricalFilter:false,sameMap:true,blockedExternalApis:true});
  // Existing saved layers remain authoritative and retain the old 45-record proof.
  const incumbent=new URL('globe/?layers=leonardo,roman',base);await navigate(incumbent);
  check(!(await snapshot()).state.layers.includes('catalog'),'explicit legacy layers silently added catalog');
  await membership({leonardo:11,roman:0,architecture:0,catalog:0},'explicit legacy layers entry');await placeAnchors('default11Presences9Places');
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
  await number('cursor-year',1502);const later=await membership({leonardo:7,roman:0,architecture:31},'Scrub1502 Leonardo trace');await placeAnchors('Scrub1502 current');await capture('scrub1502-current-en-globe');
  check(later.state.selectedItemId===null,'own time visibility did not clear Roman selection');
  await click('#mode-range');await number('time-start',1502);await number('time-end',1502);
  const range=await membership({leonardo:4,roman:0,architecture:31},'Range1502 Leonardo only');
  const cesena=expectedBundle.leonardo.lifePath.presences.find(p=>p.presence_id==='presence-cesena-1502-08-10');
  check(cesena,'expected existing Cesena identity missing');await select(cesena.presence_item_id);await disclose('sources-disclosure');await disclose('evidence-disclosure');
  const cesenaEvidence=await evaluate(cdp,"JSON.parse(document.querySelector('#selection-evidence pre').textContent)");
  const narrowedClaim=cesenaEvidence.claims.find(claim=>claim.id==='claim-cesena-presence-1502-08-10');
  check(narrowedClaim?.statement==='Leonardo was present in Cesena by 10 August 1502.','Cesena disclosure did not expose the authorized statement narrowing');
  check(narrowedClaim.review_state==='draft'&&narrowedClaim.confidence==='unknown'&&narrowedClaim.evidence_state==='missing','Cesena correction promoted historical status');
  const rejectedSurvey=cesenaEvidence.claims.find(claim=>claim.id==='claim-cesena-survey-folios-9r-10r');
  check(rejectedSurvey?.review_state==='rejected'&&rejectedSurvey.confidence==='low'&&rejectedSurvey.evidence_state==='missing','Separate rejected survey Claim changed');
  const locator=cesenaEvidence.evidence_links.find(link=>link.id==='evidence-cesena-uniurb-f46v');
  check(locator?.review_state==='draft'&&locator.reviewer===null,'Cesena EvidenceLink status changed');
  checks.push({case:'Cesena bounded statement amendment',claim:narrowedClaim.id,statement:narrowedClaim.statement,status:narrowedClaim.review_state,confidence:narrowedClaim.confidence,evidence:narrowedClaim.evidence_state,rejectedSurveyPreserved:true,evidenceLink:locator.id,locator:locator.locator});
  await placeAnchors('Range1502 selectedCesena');const leo=await snapshot();await layer('roman',false);const preserved=await snapshot();
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
  await click('#period-all');const wide=await membership({leonardo:11,roman:3,architecture:31},'wide Range interval collection');await placeAnchors('wide11Presences9Places');
  const repeated=expectedBundle.leonardo.lifePath.presences.filter(p=>p.place_ref==='place-florence');check(repeated.length===2,'accepted repeated Florence episodes missing');
  await evaluate(cdp,`(() => {const n=document.querySelector('.workspace-place-marker[data-place-ref="place-florence"]');if(!n?.checkVisibility({checkVisibilityCSS:true}))throw new Error('Florence Place anchor hidden');n.focus({preventScroll:true});if(document.activeElement!==n)throw new Error('Florence anchor cannot receive focus');})()`);
  await key(' ','Space',32);await stable('native Florence anchor keyboard selection');await placeAnchors('native Florence grouped anchor');
  for(const episode of repeated){await click('#place-episodes button[data-presence-item-id="'+episode.presence_item_id+'"]',true);check((await snapshot()).state.selectedItemId===episode.presence_item_id,'repeated Place episode selection collapsed');check(await evaluate(cdp,`document.querySelector('#place-episodes button[data-presence-item-id=\\\"'+${JSON.stringify(episode.presence_item_id)}+'\\\"]').getAttribute('aria-pressed')==='true'`),'repeated Place episode active state missing');await placeAnchors('Florence '+episode.presence_id);}
  await disclose('sources-disclosure');await capture('repeated-florence-source-en-map');await close();
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
  await navigate(new URL('region/',base));await membership({leonardo:0,roman:1,architecture:0,catalog:10},'Region compatible entry ready catalog default');await capture('region-entry-en-globe');
  await navigate(saved);check(sameState((await snapshot()).state,savedState),'shared saved URL lost workspace/camera state');await stable('shared saved state reopened');
  const legacy=[];
  const leoLegacy=new URL('globe/?mode=scrub&from=1452&at=1502&presence=presence-cesena-1502-08-10&lang=ru&view=map',base);await navigate(leoLegacy);
  const translatedLeo=await snapshot();check(translatedLeo.state.cursorYear===1502&&translatedLeo.state.mode==='scrub'&&translatedLeo.state.selectedItemId===cesena.presence_item_id&&translatedLeo.state.language==='ru'&&translatedLeo.state.presentationView==='map','legacy Leonardo saved state translation failed');legacy.push({entry:'leonardo',url:leoLegacy.href,state:translatedLeo.state});
  const version=expectedBundle.roman.versions[1];const romanLegacy=new URL('region/',base);romanLegacy.searchParams.set('time',version.preset_id);romanLegacy.searchParams.set('layers','layer-political-territory');romanLegacy.searchParams.set('item',version.item_id);romanLegacy.searchParams.set('lang','en');romanLegacy.searchParams.set('view','map');await navigate(romanLegacy);
  const translatedRoman=await snapshot();check(translatedRoman.state.selectedItemId===version.item_id&&translatedRoman.state.startYear===106&&translatedRoman.state.endYear===113,'legacy Roman saved state translation failed');legacy.push({entry:'roman',url:romanLegacy.href,state:translatedRoman.state});
  await disclose('sources-disclosure');await capture('legacy-roman-source-en-map');
  await networkSnapshot();
  return {outcome:'TECHNICAL_UNIFIED_WORKSPACE_PASS',actions,checks,placeAnchorChecks,catalogChecks,mobileChecks,network:{blockedUrls:WIKIMEDIA_BLOCKED_URLS,documents:networkDocuments,liveWikimediaRequests:0},referenceChecks,rawNegativeDateReferenceCount:bce.length,rawDatePolicy:'Literal imported strings including negative BCE-style values; no calendar/lifetime normalization',nativeRomanGeometries:nativeGeometries,nativePicking:point,camera:{before:beforeDrag.camera,after:cameraState.camera},history:{back:true,forward:true,savedUrlRestored:true,state:savedState},legacy,captures,renderSettlements,
    valueValidation:'not_assessed',limitations:['Automated native interaction evidence does not establish user comprehension or user value.','Architecture references retain imported metadata; no historical applicability or source acceptance is inferred.','Shared URL restoration compares exact workspace fields and native renderer camera numbers.','Same engine and cartographic projection comparison, not independent renderer-adapter proof.','Named controls and native input only; not a complete assistive technology audit.']};
}

async function main() {
  const options=argumentsFor(process.argv);await mkdir(options.output,{recursive:true});
  const deadline=Date.now()+options.timeoutMs;
  let server=null,browser=null,cdp=null,browserLog='';
  const profile=await mkdtemp(join(tmpdir(),'artemis-unified-chrome-'));
  const hostWindow={width:Math.max(options.width,960),height:Math.max(options.height+256,1100)};
  let hostViewport=null;
  try {
    if(options.artifact)server=await localServer(options.expectedArtifact);
    const url=options.url || server.url,base=new URL('../',url);
    const byteVerification=await verifyBytes(options,base,deadline);
    const expectedBundle=JSON.parse(await readFile(join(options.expectedArtifact,'globe/unified-bundle.json'),'utf8'));
    browser=spawn(options.browser,['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--force-prefers-reduced-motion=reduce','--remote-debugging-port=0',`--user-data-dir=${profile}`,`--window-size=${hostWindow.width},${hostWindow.height}`,'about:blank'],{stdio:['ignore','ignore','pipe']});
    browser.stderr.on('data',chunk=>{browserLog=(browserLog+chunk).slice(-20000);});
    const port=await waitForDevToolsPort(profile,browser,deadline),endpoint=await waitForPageEndpoint(port,deadline);cdp=await connectCdp(endpoint,deadline);await cdp.send('Page.enable');await cdp.send('Runtime.enable');
    // Chromium compositor wheel hit testing also depends on its host widget.
    // Keep that widget larger than the intended responsive CSS viewport.
    hostViewport=await evaluate(cdp,'({width:innerWidth,height:innerHeight,devicePixelRatio})');
    check(hostViewport.width>=options.width&&hostViewport.height>=options.height,'native host widget is smaller than requested CSS viewport '+JSON.stringify({hostWindow,hostViewport,requestedCss:{width:options.width,height:options.height}}));
    // --window-size includes headless window chrome; bind the actual CSS viewport.
    await cdp.send('Emulation.setDeviceMetricsOverride',{width:options.width,height:options.height,deviceScaleFactor:1,mobile:false});
    check(await evaluate(cdp,`innerWidth===${options.width}&&innerHeight===${options.height}`),'native CSS viewport differs from requested dimensions');
    await cdp.send('Network.enable');await cdp.send('Network.setBlockedURLs',{urls:WIKIMEDIA_BLOCKED_URLS});
    await cdp.send('Page.addScriptToEvaluateOnNewDocument',{source:`(()=>{const requests=[];Object.defineProperty(window,'__ARTEMIS_BROWSER_REQUESTS',{value:requests});const wheelEvents=[];Object.defineProperty(window,'__ARTEMIS_BROWSER_WHEEL_EVENTS',{value:wheelEvents});document.addEventListener('wheel',event=>wheelEvents.push({trusted:event.isTrusted,target:event.target?.id||event.target?.className||event.target?.tagName,wheel:event.target?.closest?.('[role=spinbutton]')?.id||null,x:event.clientX,y:event.clientY,deltaX:event.deltaX,deltaY:event.deltaY,timeStamp:event.timeStamp}),{capture:true,passive:true});const nativeFetch=window.fetch;window.fetch=function(input,...args){requests.push(typeof input==='string'?new URL(input,location.href).href:input?.url||String(input));return nativeFetch.call(this,input,...args);};const nativeOpen=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(method,url,...args){requests.push(new URL(url,location.href).href);return nativeOpen.call(this,method,url,...args);};})()`});
    const scenario=await runScenario(cdp,options,url,deadline,expectedBundle);
    const report={...scenario,artifactVerification:{scope:'checked metadata and common input bundle at both registered entries; full release files separately checked by verify_public_artifact.py',files:byteVerification},provenance:{evidenceKind:'automated_native_browser_check',checkoutCommit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),recordedAtUtc:new Date().toISOString(),browser:await cdp.send('Browser.getVersion'),launchWindow:hostWindow,hostViewportBeforeOverride:hostViewport,requestedCssViewport:{width:options.width,height:options.height},cssViewport:await evaluate(cdp,'({width:innerWidth,height:innerHeight,devicePixelRatio})'),viewportEmulation:'CSS dimensions fixed through CDP; DPR1, desktop input, not physical iPhone/touch/safe-area verification',runnerSha256:sha256(await readFile(fileURLToPath(import.meta.url))),sharedTransportSha256:sha256(await readFile(new URL('./capture_globe_browser_evidence.mjs',import.meta.url))),bundleSha256:sha256(await readFile(join(options.expectedArtifact,'globe/unified-bundle.json'))),workflowRunUrl:process.env.GITHUB_RUN_ID?`https://github.com/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}`:null,workflowRunAttempt:process.env.GITHUB_RUN_ATTEMPT || null,live:!!options.url}};
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

export { argumentsFor, verifyBytes, contextReplaced, sameState, mobileControlOwner, mobileYearControl, wheelKeys, isWikimediaRequest, WIKIMEDIA_BLOCKED_URLS };
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))main().catch(error=>{process.stderr.write((error?.stack || error)+'\n');process.exitCode=1;});
