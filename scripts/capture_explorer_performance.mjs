#!/usr/bin/env node
// Controlled local diagnostic; timings are not a production/device SLA.
import {spawn,execFileSync} from 'node:child_process';
import {createServer} from 'node:http';
import {readFile,mkdir,mkdtemp,rm,writeFile,cp} from 'node:fs/promises';
import {join,resolve,extname} from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {delay,waitForDevToolsPort,waitForPageEndpoint,connectCdp,evaluate} from './capture_globe_browser_evidence.mjs';
const args=Object.fromEntries(process.argv.slice(2).reduce((a,v,i,all)=>i%2?a:[...a,[v.replace(/^--/,''),all[i+1]]],[]));
for(const name of ['browser','artifact','output','baseline-ref'])if(!args[name])throw Error('Missing --'+name);
const output=resolve(args.output), temp=await mkdtemp(join(tmpdir(),'artemis-perf-'));
await mkdir(output,{recursive:true});
const hash=x=>createHash('sha256').update(x).digest('hex');
const report={kind:'controlled_local_browser_diagnostic',baselineRef:args['baseline-ref'],checkout:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),limitations:['Software WebGL on CI; not user-device FPS','Local max-age=3600 server; not actual Pages caching','Programmatic camera movement measures renderer work, not native gesture usability'],runs:[]};
let server,browser,cdp,diagnosticSocket,log='';
const diagnosticEvents=[],requestUrls=new Map();
report.diagnostics={events:diagnosticEvents,eventLimit:40,readinessFailure:null};
const boundedText=value=>String(value??'').slice(0,1000);
function observeDiagnosticEvent(message) {
  const params=message.params||{};
  if(message.method==='Network.requestWillBeSent') {requestUrls.set(params.requestId,boundedText(params.request?.url));if(requestUrls.size>100)requestUrls.delete(requestUrls.keys().next().value);return;}
  let event=null;
  if(message.method==='Runtime.exceptionThrown')event={kind:'runtime_exception',text:boundedText(params.exceptionDetails?.exception?.description||params.exceptionDetails?.text),url:boundedText(params.exceptionDetails?.url)};
  else if(message.method==='Runtime.consoleAPICalled'&&['error','warning'].includes(params.type))event={kind:'console_'+params.type,text:boundedText((params.args||[]).map(arg=>arg.value??arg.description??arg.type).join(' '))};
  else if(message.method==='Network.loadingFailed')event={kind:'network_loading_failed',url:requestUrls.get(params.requestId)||null,error:boundedText(params.errorText),blockedReason:params.blockedReason||null,type:params.type||null};
  if(event){if(diagnosticEvents.length>=40)diagnosticEvents.shift();diagnosticEvents.push(event);}
}

try {
  for(const variant of ['baseline','current'])await cp(resolve(args.artifact),join(temp,variant),{recursive:true});
  for(const file of ['runtime.js','style.css'])await writeFile(join(temp,'baseline/globe',file),execFileSync('git',['show',`${args['baseline-ref']}:scripts/unified_explorer/${file}`]));
  const template=execFileSync('git',['show',`${args['baseline-ref']}:scripts/unified_explorer/index.html.template`],{encoding:'utf8'});
  await writeFile(join(temp,'baseline/globe/index.html'),template.replace('{{ENTRY_PROFILE}}','globe'));
  report.bundleSha256=hash(await readFile(join(temp,'current/globe/unified-bundle.json')));
  report.expectedRegistryCount=JSON.parse(await readFile(join(temp,'current/globe/unified-bundle.json'),'utf8')).registry.length;
  if(report.bundleSha256!==hash(await readFile(join(temp,'baseline/globe/unified-bundle.json'))))throw Error('Paired bundle differs');
  server=createServer(async(req,res)=>{try{const pathname=decodeURIComponent(new URL(req.url,'http://local').pathname);const path=resolve(temp,'.'+pathname+(pathname.endsWith('/')?'index.html':''));if(!path.startsWith(temp+'/'))throw Error('path');const bytes=await readFile(path);res.writeHead(200,{'Cache-Control':'public,max-age=3600','Content-Type':({'.js':'text/javascript','.json':'application/json','.geojson':'application/json','.css':'text/css','.html':'text/html'})[extname(path)]||'application/octet-stream'});res.end(bytes);}catch{res.writeHead(404);res.end();}});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}`;
  const profile=join(temp,'profile'),deadline=Date.now()+(args.phase==='high-dpi'?300000:480000);
  browser=spawn(args.browser,['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--remote-debugging-port=0',`--user-data-dir=${profile}`,'--window-size=1440,900','about:blank'],{stdio:['ignore','ignore','pipe']});browser.stderr.on('data',x=>{log=(log+x).slice(-20000)});
  const endpoint=await waitForPageEndpoint(await waitForDevToolsPort(profile,browser,deadline),deadline);
  cdp=await connectCdp(endpoint,deadline);
  // A separate observational CDP connection preserves bounded error events without
  // replacing application code, bypassing readiness, or changing measured inputs.
  diagnosticSocket=new WebSocket(endpoint);
  await new Promise((resolveOpen,reject)=>{const timer=setTimeout(()=>reject(Error('Diagnostic CDP connection timeout')),5000);diagnosticSocket.addEventListener('open',()=>{clearTimeout(timer);resolveOpen();},{once:true});diagnosticSocket.addEventListener('error',()=>{clearTimeout(timer);reject(Error('Diagnostic CDP connection failed'));},{once:true});});
  diagnosticSocket.addEventListener('message',event=>{try{observeDiagnosticEvent(JSON.parse(String(event.data)));}catch{}});
  for(const [index,method] of ['Runtime.enable','Network.enable'].entries())diagnosticSocket.send(JSON.stringify({id:index+1,method}));
  for(const domain of ['Page','Runtime','Network','Performance'])await cdp.send(domain+'.enable');
  report.browser=await cdp.send('Browser.getVersion');
  await cdp.send('Emulation.setFocusEmulationEnabled',{enabled:true});
  const metrics=async()=>Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(x=>[x.name,x.value]));
  const diff=(a,b)=>Object.fromEntries(['LayoutCount','RecalcStyleCount','LayoutDuration','RecalcStyleDuration','ScriptDuration','TaskDuration'].map(k=>[k,b[k]-a[k]]));
  async function ready(prior){
    const until=Date.now()+45000;let last=null;
    while(Date.now()<until){
      try{last=await evaluate(cdp,`(()=>{const fatal=document.getElementById('fatal-error');return {url:location.href,timeOrigin:performance.timeOrigin,runtimeReady:document.documentElement.dataset.artemisRuntimeReady||null,visualReady:document.documentElement.dataset.artemisVisualReady||null,fatal:fatal&&!fatal.hidden?fatal.textContent.slice(0,1000):null};})()`);}
      catch(error){last={evaluationError:boundedText(error)};}
      if(last.timeOrigin!==prior&&last.runtimeReady==='true')return;
      await delay(50);
    }
    report.diagnostics.readinessFailure=last;
    throw Error('Map readiness timeout');
  }
  async function navigate(url){const prior=await evaluate(cdp,'performance.timeOrigin');await cdp.send('Page.navigate',{url});await ready(prior);return evaluate(cdp,"({readyObservedMs:performance.now(),resources:performance.getEntriesByType('resource').map(x=>({name:x.name,duration:x.duration,transferSize:x.transferSize,encodedBodySize:x.encodedBodySize,decodedBodySize:x.decodedBodySize}))})");}
  async function openCompactDetails() {
    if(await evaluate(cdp,"!!document.getElementById('open-details')")) {
      const before=await evaluate(cdp,"JSON.stringify({state:window.__ARTEMIS_EXPLORER.state,url:location.href})");
      await evaluate(cdp,"(()=>{const n=document.getElementById('open-details');if(!n.checkVisibility({checkVisibilityCSS:true}))throw Error('Compact details trigger hidden');n.focus();if(document.activeElement!==n)throw Error('Compact details focus failed');})()");
      await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,text:'\r',unmodifiedText:'\r'});
      await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
      if(!await evaluate(cdp,"!document.getElementById('inspector').hidden && document.getElementById('selection-title').checkVisibility({checkVisibilityCSS:true})"))throw Error('Native Enter did not open compact Details');
      if(before!==await evaluate(cdp,"JSON.stringify({state:window.__ARTEMIS_EXPLORER.state,url:location.href})"))throw Error('Details transition changed canonical state');
    }
  }
  for(let repetition=0;repetition<(args.phase==='high-dpi'?0:3);repetition++)for(const variant of repetition%2?['current','baseline']:['baseline','current']){
    await cdp.send('Network.clearBrowserCache');
    const url=`${base}/${variant}/globe/`,cold=await navigate(url),warm=await navigate(url);
    await evaluate(cdp,'window.__perfMap=window.__ARTEMIS_EXPLORER.map;window.__perfOrigin=performance.timeOrigin');
    const before=await metrics();
    const movement=await evaluate(cdp,`(async()=>{const map=window.__perfMap, samples=[];for(let i=0;i<160;i++){const t=performance.now();map.jumpTo({center:[10+Math.sin(i/20)*25,15],bearing:i/2});await new Promise(requestAnimationFrame);samples.push(performance.now()-t);}return {samples,mapPreserved:map===window.__ARTEMIS_EXPLORER.map,documentPreserved:window.__perfOrigin===performance.timeOrigin}})()`,true);
    const movementMetrics=diff(before,await metrics());
    if(!movement.mapPreserved||!movement.documentPreserved)throw Error('Map/document replaced');
    await evaluate(cdp,"document.getElementById('period-roman').click()");await delay(100);
    const selectionBefore=await metrics();
    const selection=await evaluate(cdp,`(()=>{const s=document.getElementById('record-select'),r=window.__ARTEMIS_EXPLORER.visibleItems.find(x=>x.kind==='region');if(!r)throw Error('Region missing');const t=performance.now();s.value=r.item_id;s.dispatchEvent(new Event('change',{bubbles:true}));return {handlerMs:performance.now()-t,rawTextChars:document.getElementById('selection-input').textContent.length,collapsed:!document.getElementById('input-disclosure').open}})()`);
    const selectionMetrics=diff(selectionBefore,await metrics());
    await openCompactDetails();
    await evaluate(cdp,"(()=>{const n=document.querySelector('#input-disclosure summary');n.scrollIntoView({block:'center'});n.focus();if(document.activeElement!==n||!n.checkVisibility({checkVisibilityCSS:true}))throw Error('Native input summary is not focused/visible');})()");
    await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});
    await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});
    // Lazy JSON is populated by the asynchronous native toggle event. Wait for
    // its observable completion, without opening the disclosure programmatically.
    let disclosure;
    const disclosureDeadline=Date.now()+5000;
    do {
      disclosure=await evaluate(cdp,"({open:document.getElementById('input-disclosure').open,rawTextChars:document.getElementById('selection-input').textContent.length,pending:document.querySelectorAll('#selection-input pre[data-json-pending]').length,item:window.__ARTEMIS_EXPLORER.state.selectedItemId,inspectorHidden:document.getElementById('inspector').hidden,focused:document.activeElement?.outerHTML?.slice(0,300)})");
      if(disclosure.open&&!disclosure.pending&&disclosure.rawTextChars>=1000)break;
      await delay(50);
    } while(Date.now()<disclosureDeadline);
    report.pendingDisclosure={variant,repetition,...disclosure};
    if(!disclosure.open||disclosure.pending||disclosure.rawTextChars<1000)throw Error('Native disclosure did not expose raw input '+JSON.stringify(disclosure));
    disclosure.rawSha256=hash(await evaluate(cdp,"document.getElementById('selection-input').textContent"));
    if(report.runs.length && disclosure.rawSha256!==report.runs[0].disclosure.rawSha256)throw Error('Disclosed native input differs '+JSON.stringify(disclosure));
    delete report.pendingDisclosure;
    const sorted=[...movement.samples].sort((a,b)=>a-b);movement.summary={medianMs:sorted[80],p95Ms:sorted[152],maxMs:sorted[159]};
    report.runs.push({variant,repetition,cold,warm,movement,movementMetrics,selection,selectionMetrics,disclosure});
    await writeFile(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
  }
  if(args.phase==='high-dpi') {
    report.limitations.push('DPR3 emulation is not evidence from a physical phone; CSS500x900, desktop input, software WebGL');
    report.highDpi=[];
    await cdp.send('Emulation.setDeviceMetricsOverride',{width:500,height:900,deviceScaleFactor:3,mobile:false});
    const settle=()=>evaluate(cdp,`new Promise((resolve,reject)=>{const m=window.__ARTEMIS_EXPLORER.map;if(m.loaded()&&!m.isMoving())return requestAnimationFrame(()=>requestAnimationFrame(resolve));const t=setTimeout(()=>reject(Error('Map settle timeout')),15000);m.once('idle',()=>{clearTimeout(t);requestAnimationFrame(resolve)});})`,true);
    const key=async()=>{await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});await delay(100);};
    const click=async p=>{await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,x:p.x,y:p.y});await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,x:p.x,y:p.y});};
    for(const variant of ['baseline','current']) {
      await navigate(`${base}/${variant}/globe/`);await evaluate(cdp,'window.__perfMap=window.__ARTEMIS_EXPLORER.map;window.__perfOrigin=performance.timeOrigin');
      for(const view of ['globe','map']) {
        await evaluate(cdp,`document.getElementById('view-${view}').click();document.getElementById('period-leonardo').click();window.__perfMap.jumpTo({center:[12,44],zoom:3,bearing:0,pitch:0});void 0`);await settle();
        const movement=await evaluate(cdp,`(async()=>{const samples=[];for(let i=0;i<40;i++){const t=performance.now();window.__perfMap.jumpTo({center:[12+Math.sin(i/10)*2,44]});await new Promise(requestAnimationFrame);samples.push(performance.now()-t)}return samples})()`,true);
        await settle();
        const place=await evaluate(cdp,`(()=>{const r=window.__ARTEMIS_EXPLORER,n=[...document.querySelectorAll('.workspace-place-marker')].find(n=>n.querySelector('.place-name')?.textContent==='Florence')||document.querySelector('.workspace-place-marker');n.focus();return {place:n.dataset.placeRef}})()`);await key();await settle();
        const geometry=await evaluate(cdp,`(async()=>{const r=window.__ARTEMIS_EXPLORER,m=r.map,c=m.getCanvas(),b=c.getBoundingClientRect(),n=document.querySelector('.workspace-place-marker[aria-pressed="true"]');if(!n)throw Error('No selected Place');const f=(await m.getSource('workspace-features').getData()).features.find(f=>f.properties.place_ref===n.dataset.placeRef),p=m.project(f.geometry.coordinates),nb=n.getBoundingClientRect(),hits=m.queryRenderedFeatures(p,{layers:['workspace-points']});return {dpr:devicePixelRatio,pixelRatio:m.getPixelRatio(),width:c.width,height:c.height,cssWidth:b.width,cssHeight:b.height,registry:r.registry.length,selected:r.state.selectedItemId,alignment:Math.hypot(nb.left+nb.width/2-b.left-p.x,nb.top+nb.height/2-b.top-p.y),nativeSelected:hits.some(h=>h.properties.place_ref===n.dataset.placeRef&&h.state.selected),preserved:m===window.__perfMap&&performance.timeOrigin===window.__perfOrigin}})()`,true);
        if(geometry.pixelRatio!==(variant==='baseline'?3:1.5)||geometry.registry!==report.expectedRegistryCount||Math.abs(geometry.width-geometry.cssWidth*geometry.pixelRatio)>1||Math.abs(geometry.height-geometry.cssHeight*geometry.pixelRatio)>1||!geometry.preserved||geometry.alignment>2||!geometry.nativeSelected)throw Error('High-DPI pixel ratio/Place/identity invariant failed '+JSON.stringify(geometry));
        const png=Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false})).data,'base64'),name=`${variant}-${view}-dpr3.png`;await writeFile(join(output,name),png);
        await evaluate(cdp,"document.getElementById('close-details').click();document.getElementById('period-roman').click();window.__perfMap.jumpTo({center:[12,40],zoom:2,bearing:0,pitch:0});void 0");await settle();
        const pick=await evaluate(cdp,`(()=>{const r=window.__ARTEMIS_EXPLORER,c=r.map.getCanvas(),b=c.getBoundingClientRect();for(let y=b.top+10;y<b.bottom-10;y+=10)for(let x=b.left+10;x<b.right-10;x+=10){if(document.elementFromPoint(x,y)!==c)continue;const h=r.map.queryRenderedFeatures([x-b.left,y-b.top],{layers:['workspace-regions']})[0];if(h)return {x,y,item:h.properties.item_id}}throw Error('No unobstructed Region pixel')})()`);await click(pick);await settle();
        if(!await evaluate(cdp,`window.__ARTEMIS_EXPLORER.state.selectedItemId===${JSON.stringify(pick.item)}`))throw Error('High-DPI native Region pick failed');
    await openCompactDetails();
        await evaluate(cdp,"document.querySelector('#sources-disclosure summary').focus()");await key();
        const sources=await evaluate(cdp,"({open:document.getElementById('sources-disclosure').open,text:document.getElementById('selection-sources').textContent})");if(!sources.open||!sources.text.length)throw Error('High-DPI keyboard sources failed');
        // Readable labels may change; the actually disclosed native records must not.
        // The baseline has inline JSON; current technical records require native disclosure.
        const sourceDetails=await evaluate(cdp,"[...document.querySelectorAll('#selection-sources details')].map(n=>n.id)");
        for(const id of sourceDetails) {
          await evaluate(cdp,`(()=>{const n=document.getElementById(${JSON.stringify(id)}),s=n?.querySelector('summary');if(!s?.checkVisibility({checkVisibilityCSS:true}))throw Error('High-DPI technical source summary hidden');s.focus();if(document.activeElement!==s)throw Error('High-DPI technical source focus failed');})()`);await key();
          if(!await evaluate(cdp,`document.getElementById(${JSON.stringify(id)}).open`))throw Error('High-DPI keyboard technical source failed');
        }
        const sourceProof=await evaluate(cdp,`(()=>{const r=window.__ARTEMIS_EXPLORER,record=r.bundle.roman.knowledge.records.find(n=>n.item_id===r.state.selectedItemId),expected=[...(record?.sources||[]),r.bundle.roman.sourceManifest],actual=[...document.querySelectorAll('#selection-sources pre')].map(n=>JSON.parse(n.textContent));if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('High-DPI disclosed source records differ from native input');return {records:actual,text:document.getElementById('selection-sources').textContent};})()`);
        await evaluate(cdp,"document.getElementById('close-details').click()");
        const drag=await evaluate(cdp,`(()=>{const c=window.__perfMap.getCanvas(),b=c.getBoundingClientRect();for(let y=b.top+20;y<b.bottom-20;y+=20)for(let x=b.left+20;x<b.right-70;x+=20)if(document.elementFromPoint(x,y)===c&&document.elementFromPoint(x+50,y)===c)return {x,y,center:window.__perfMap.getCenter().toArray()};throw Error('No drag area')})()`);
        await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',x:drag.x,y:drag.y});await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',buttons:1,clickCount:1,x:drag.x,y:drag.y});for(let i=1;i<=5;i++)await cdp.send('Input.dispatchMouseEvent',{type:'mouseMoved',button:'left',buttons:1,x:drag.x+i*10,y:drag.y});await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',buttons:0,clickCount:1,x:drag.x+50,y:drag.y});await settle();
        if(!await evaluate(cdp,`JSON.stringify(window.__perfMap.getCenter().toArray())!==${JSON.stringify(JSON.stringify(drag.center))}&&window.__perfMap===window.__ARTEMIS_EXPLORER.map&&performance.timeOrigin===window.__perfOrigin`))throw Error('High-DPI native drag/identity failed');
        const sourceSha256=hash(JSON.stringify(sourceProof.records)),sourceTextSha256=hash(sourceProof.text),prior=report.highDpi.find(x=>x.view===view);
        if(prior&&prior.sourceSha256!==sourceSha256)throw Error('High-DPI disclosed source identity changed');
        if(prior&&prior.pick.item!==pick.item)throw Error('High-DPI native Region identity changed');
        const ordered=[...movement].sort((a,b)=>a-b),movementSummary={medianMs:ordered[20],p95Ms:ordered[38],maxMs:ordered[39]};
        report.highDpi.push({variant,view,geometry,movement,movementSummary,pick,sourceSha256,sourceTextSha256,sourceRecordCount:sourceProof.records.length,screenshot:{name,sha256:hash(png)},nativeDrag:true,keyboardSources:true});await writeFile(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
      }
    }
  }
} catch(error){report.error=String(error.stack||error);throw error;} finally {
  await writeFile(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(output,'browser.log'),log);
  diagnosticSocket?.close();cdp?.close();if(browser&&browser.exitCode===null)browser.kill('SIGTERM');server?.close();await delay(300);await rm(temp,{recursive:true,force:true,maxRetries:5,retryDelay:100});
}
