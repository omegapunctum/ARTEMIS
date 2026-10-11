#!/usr/bin/env node
// Bounded diagnostic: native wheel input, software GPU, no device-FPS claim.
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir,mkdtemp,rm} from 'node:fs/promises';
import {resolve,join,extname} from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {delay,waitForDevToolsPort,waitForPageEndpoint,connectCdp,evaluate} from './capture_globe_browser_evidence.mjs';
const args={};for(let i=2;i<process.argv.length;i+=2)args[process.argv[i].replace(/^--/,'')]=process.argv[i+1];
for(const key of ['browser','artifact','output'])if(!args[key])throw Error(`Missing --${key}`);
const repetitions=Number(args.repetitions||3),view=args.view||'globe';
if(!Number.isInteger(repetitions)||repetitions<1||repetitions>5||!['map','globe'].includes(view))throw Error('Invalid repetition/view');
const root=resolve(args.artifact),output=resolve(args.output),temp=await mkdtemp(join(tmpdir(),'artemis-zoom-'));
await mkdir(output,{recursive:true});
const sha=b=>createHash('sha256').update(b).digest('hex');
const report={kind:'native_wheel_zoom_diagnostic',schemaVersion:2,view,repetitions,selectionMode:args.selected==='true'?'native-picked compact card':'no selection',intervention:args['hide-context']==='true'?'earth-land visibility:none':'none',limitations:['Headless SwiftShader software GPU; results are not owner-device FPS','Frame intervals include rendering, CPU and diagnostic overhead; causal attribution requires paired controls','Profiler is optional and adds overhead when enabled','Whole-interaction frame intervals include wheel pacing and settle waits; moving zoom-band samples classify each interval by its end-frame state and zoom, not exact time spent within that band','Optional --screenshots true adds capture pauses to the measured interval; disabled by default'],runs:[],errors:[]};
let server,browser,cdp,observer,log='',activeRun=null;
const deadline=Date.now()+Math.min(600000,repetitions*120000+60000);
const persist=()=>writeFile(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
const checkTime=()=>{if(Date.now()>deadline)throw Error('Global diagnostic deadline exceeded');};
async function waitFor(expression,label,timeout=20000){const end=Math.min(deadline,Date.now()+timeout);let last;while(Date.now()<end){try{last=await evaluate(cdp,expression);if(last)return last;}catch{}await delay(100);}throw Error(`${label} timeout; last=${JSON.stringify(last)}`);}
try{
  report.bundleSha256=sha(await readFile(join(root,'globe/unified-bundle.json')));
  report.runtimeSha256=sha(await readFile(join(root,'globe/runtime.js')));
  report.contextSha256=sha(await readFile(join(root,'globe/earth-context.geojson')));
  report.engineSha256=sha(await readFile(join(root,'globe/engine/maplibre-gl.js')));
  server=createServer(async(req,res)=>{try{const p=new URL(req.url,'http://local').pathname;const path=resolve(root,'.'+decodeURIComponent(p)+(p.endsWith('/')?'index.html':''));if(!path.startsWith(root+'/'))throw Error('Path outside artifact');const data=await readFile(path);res.writeHead(200,{'Content-Type':({'.html':'text/html','.js':'text/javascript','.json':'application/json','.geojson':'application/json','.css':'text/css'})[extname(path)]||'application/octet-stream'});res.end(data);}catch{res.writeHead(404);res.end();}});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const profile=join(temp,'profile');browser=spawn(args.browser,['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--remote-debugging-port=0',`--user-data-dir=${profile}`,'--window-size=1440,900','about:blank'],{stdio:['ignore','ignore','pipe']});browser.stderr.on('data',b=>log=(log+b).slice(-20000));
  const endpoint=await waitForPageEndpoint(await waitForDevToolsPort(profile,browser,deadline),deadline);cdp=await connectCdp(endpoint,deadline);
  observer=new WebSocket(endpoint);await new Promise((ok,fail)=>{const t=setTimeout(()=>fail(Error('Observer timeout')),5000);observer.addEventListener('open',()=>{clearTimeout(t);ok();},{once:true});observer.addEventListener('error',()=>{clearTimeout(t);fail(Error('Observer error'));},{once:true});});
  observer.addEventListener('message',event=>{try{const m=JSON.parse(String(event.data));if(m.method==='Runtime.exceptionThrown'||m.method==='Network.loadingFailed'||m.method==='Log.entryAdded'){report.errors.push(m);if(report.errors.length>30)report.errors.shift();}}catch{}});
  ['Runtime.enable','Network.enable','Log.enable'].forEach((method,i)=>observer.send(JSON.stringify({id:i+1,method})));
  for(const domain of ['Page','Runtime','Performance'])await cdp.send(domain+'.enable');
  await cdp.send('Emulation.setFocusEmulationEnabled',{enabled:true});report.browser=await cdp.send('Browser.getVersion');
  report.viewport=await evaluate(cdp,'({width:innerWidth,height:innerHeight,dpr:devicePixelRatio,screenWidth:screen.width,screenHeight:screen.height})');
  const screenshot=async(name)=>{const bytes=Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false})).data,'base64');await writeFile(join(output,name),bytes);return {name,sha256:sha(bytes)};};
  const metrics=async()=>Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(m=>[m.name,m.value]));
  const settle=()=>waitFor('window.__ARTEMIS_EXPLORER?.map?.loaded() && !window.__ARTEMIS_EXPLORER.map.isMoving()','map settle',30000);
  for(let rep=0;rep<repetitions;rep++){
    checkTime();const previousOrigin=await evaluate(cdp,'performance.timeOrigin');await cdp.send('Page.navigate',{url:`http://127.0.0.1:${server.address().port}/globe/`});
    await waitFor(`performance.timeOrigin !== ${previousOrigin} && document.documentElement.dataset.artemisRuntimeReady === "true"`,'startup',45000);
    await evaluate(cdp,`document.getElementById('view-${view}').click();void 0`);await settle();
    const initial=await evaluate(cdp,`(()=>{const r=window.__ARTEMIS_EXPLORER,m=r.map;const row=r.bundle.catalog.references[0];if(!row)throw Error('London catalog absent');window.__zoomMap=m;window.__zoomOrigin=performance.timeOrigin;window.__zoomTarget=row.geometry.coordinates;m.jumpTo({center:row.geometry.coordinates,zoom:3,pitch:0,bearing:0});${args['hide-context']==='true'?"m.setLayoutProperty('earth-land','visibility','none');":''}return {target:row.item_id,coordinates:row.geometry.coordinates,registry:r.registry.map(row=>row.item_id)};})()`);await settle();
    if(args.selected==='true'){
      await evaluate(cdp,'window.__zoomMap.jumpTo({center:window.__zoomTarget,zoom:14,pitch:0,bearing:0});void 0');await settle();
      const point=await evaluate(cdp,`(()=>{const m=window.__zoomMap,c=m.getCanvas(),b=c.getBoundingClientRect(),p=m.project(window.__zoomTarget),x=b.left+p.x,y=b.top+p.y;if(document.elementFromPoint(x,y)!==c)throw Error('Native selection target obscured');return {x,y}})()`);
      await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',buttons:1,clickCount:1,...point});
      await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',buttons:0,clickCount:1,...point});
      await waitFor(`window.__ARTEMIS_EXPLORER.state.selectedItemId===${JSON.stringify(initial.target)} && document.getElementById('summary-title')?.checkVisibility({checkVisibilityCSS:true}) && document.getElementById('open-details')?.checkVisibility({checkVisibilityCSS:true})`,'native compact selection');
      await evaluate(cdp,'window.__zoomMap.jumpTo({center:window.__zoomTarget,zoom:3,pitch:0,bearing:0});void 0');await settle();
      await waitFor(`window.__ARTEMIS_EXPLORER.state.selectedItemId===${JSON.stringify(initial.target)} && document.getElementById('summary-title')?.checkVisibility({checkVisibilityCSS:true})`,'compact card retained at starting camera');
    }
    const stateExpression=`(()=>{const r=window.__ARTEMIS_EXPLORER,s={...r.state};delete s.camera;const u=new URL(location.href);for(const k of ['camera','center','lat','lon','lng','zoom','bearing','pitch'])u.searchParams.delete(k);return {state:s,registry:r.registry.map(row=>row.item_id),visible:r.visibleItems.map(x=>x.item_id),urlNonCamera:u.search};})()`;
    const before=await evaluate(cdp,stateExpression);
    await evaluate(cdp,`(()=>{const m=window.__zoomMap,d=window.__zoomDiagnostic={frames:[],frameSamples:[],longTasks:[],counts:{},sources:{},active:true,leg:null};let last=performance.now();function tick(t){if(!d.active)return;d.frames.push(t-last);d.frameSamples.push({intervalMs:t-last,zoom:m.getZoom(),moving:m.isMoving(),leg:d.leg});last=t;requestAnimationFrame(tick)}requestAnimationFrame(tick);d.handlers={};for(const name of ['render','move','zoom','moveend','zoomend','sourcedata']){const f=e=>{d.counts[name]=(d.counts[name]||0)+1;if(name==='sourcedata'){const key=(e.sourceId||'?')+':'+(e.sourceDataType||'?')+':'+Boolean(e.isSourceLoaded);d.sources[key]=(d.sources[key]||0)+1;}};d.handlers[name]=f;m.on(name,f)}try{d.observer=new PerformanceObserver(list=>{for(const e of list.getEntries())d.longTasks.push({start:e.startTime,duration:e.duration})});d.observer.observe({type:'longtask',buffered:false})}catch{}return true})()`);
    const firstMetrics=await metrics();const started=Date.now();
    if(args.profile==='true'){await cdp.send('Profiler.enable');await cdp.send('Profiler.start');}
    const legs=[];activeRun={repetition:rep,initial,before,legs,firstMetrics,started,screenshots:[]};await persist();
    for(const direction of ['in','out']){
      await evaluate(cdp,`window.__zoomDiagnostic.leg=${JSON.stringify(direction)};void 0`);
      const target=direction==='in'?14:3,leg={direction,target,wheels:0,startZoom:await evaluate(cdp,'window.__zoomMap.getZoom()')};
      legs.push(leg);leg.trajectory=[];await persist();
      const legDeadline=Math.min(deadline,Date.now()+45000);
      while(Date.now()<legDeadline&&leg.wheels<80){
        const z=await evaluate(cdp,'window.__zoomMap.getZoom()');leg.trajectory.push({elapsedMs:Date.now()-started,zoom:z,wheels:leg.wheels});if(direction==='in'?z>=13.8:z<=3.2)break;
        const p=await evaluate(cdp,`(()=>{const c=window.__zoomMap.getCanvas(),b=c.getBoundingClientRect(),x=b.left+b.width/2,y=b.top+b.height/2;if(document.elementFromPoint(x,y)!==c)throw Error('Canvas center is obstructed');return {x,y}})()`);
        await cdp.send('Input.dispatchMouseEvent',{type:'mouseWheel',x:p.x,y:p.y,deltaX:0,deltaY:direction==='in'?-400:400});leg.wheels++;await delay(180);
      }
      await settle();leg.endZoom=await evaluate(cdp,'window.__zoomMap.getZoom()');leg.passed=direction==='in'?leg.endZoom>=13.8:leg.endZoom<=3.2;if(args.screenshots==='true')activeRun.screenshots.push(await screenshot(`run-${rep}-${direction==='in'?'high-zoom':'end'}.png`));if(!leg.passed)throw Error('Native wheel endpoint not reached '+JSON.stringify(leg));
    }
    if(args.profile==='true'){const profileResult=await cdp.send('Profiler.stop');await writeFile(join(output,`profile-${rep}.cpuprofile`),JSON.stringify(profileResult.profile));}
    const lastMetrics=await metrics();
    const observed=await evaluate(cdp,`(()=>{const d=window.__zoomDiagnostic,m=window.__zoomMap;d.active=false;d.observer?.disconnect();for(const [name,f]of Object.entries(d.handlers))m.off(name,f);return {frames:d.frames,frameSamples:d.frameSamples,longTasks:d.longTasks,counts:d.counts,sources:d.sources,mapPreserved:m===window.__ARTEMIS_EXPLORER.map,documentPreserved:window.__zoomOrigin===performance.timeOrigin,zoom:m.getZoom(),center:m.getCenter().toArray(),pixelRatio:m.getPixelRatio(),contextVisibility:m.getLayoutProperty('earth-land','visibility')||'visible'}})()`);
    const after=await evaluate(cdp,stateExpression),sorted=[...observed.frames].sort((a,b)=>a-b);
    const bandsFor=direction=>[[3,6],[6,10],[10,15]].map(([min,max])=>{const values=observed.frameSamples.filter(x=>x.moving&&(!direction||x.leg===direction)&&x.zoom>=min&&(max===15?x.zoom<=max:x.zoom<max)).map(x=>x.intervalMs).sort((a,b)=>a-b);return {minZoom:min,maxZoom:max,maxInclusive:max===15,count:values.length,p50Ms:values.length?values[Math.floor(values.length*.5)]:null,p95Ms:values.length?values[Math.floor(values.length*.95)]:null};});
    const movingZoomBands=bandsFor(null),movingZoomBandsByDirection={in:bandsFor('in'),out:bandsFor('out')};
    const run={movingZoomBands,movingZoomBandsByDirection,repetition:rep,initial,legs,screenshots:activeRun.screenshots,elapsedMs:Date.now()-started,before,after,...observed,frameSummary:{count:sorted.length,medianMs:sorted[Math.floor(sorted.length*.5)],p95Ms:sorted[Math.floor(sorted.length*.95)],maxMs:sorted.at(-1)},metricDelta:Object.fromEntries(['ScriptDuration','TaskDuration','LayoutDuration','RecalcStyleDuration','LayoutCount','RecalcStyleCount'].map(k=>[k,lastMetrics[k]-firstMetrics[k]])),nonCameraStatePreserved:JSON.stringify(before)===JSON.stringify(after)};
    report.runs.push(run);activeRun=null;await persist();if(!run.mapPreserved||!run.documentPreserved||!run.nonCameraStatePreserved)throw Error('Map/document/non-camera invariant failed');
  }
  report.success=true;
}catch(error){report.failure=String(error.stack||error);process.exitCode=1;if(activeRun){report.partialRun={...activeRun,elapsedMs:Date.now()-activeRun.started};try{report.partialRun.observed=await evaluate(cdp,`(()=>{const d=window.__zoomDiagnostic;return {frames:d?.frames,frameSamples:d?.frameSamples,longTasks:d?.longTasks,counts:d?.counts,sources:d?.sources,zoom:window.__zoomMap?.getZoom(),mapPreserved:window.__zoomMap===window.__ARTEMIS_EXPLORER?.map}})()`);}catch(e){report.partialRun.observationError=String(e)}}try{report.failureState=await evaluate(cdp,'({url:location.href,ready:document.documentElement.dataset.artemisRuntimeReady,fatal:document.getElementById("fatal-error")?.textContent,zoom:window.__ARTEMIS_EXPLORER?.map?.getZoom()})');}catch{}}
finally{await persist();await writeFile(join(output,'browser.log'),log);observer?.close();cdp?.close();if(browser&&browser.exitCode===null)browser.kill('SIGTERM');server?.close();await delay(300);await rm(temp,{recursive:true,force:true,maxRetries:5,retryDelay:100});}
console.log(JSON.stringify({success:report.success||false,report:join(output,'report.json'),runs:report.runs.map(r=>({repetition:r.repetition,frameSummary:r.frameSummary,legs:r.legs,counts:r.counts,metricDelta:r.metricDelta})),failure:report.failure}));
