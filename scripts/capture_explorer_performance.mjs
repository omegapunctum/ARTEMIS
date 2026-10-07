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
let server,browser,cdp,log='';
try {
  for(const variant of ['baseline','current'])await cp(resolve(args.artifact),join(temp,variant),{recursive:true});
  for(const file of ['runtime.js','style.css'])await writeFile(join(temp,'baseline/globe',file),execFileSync('git',['show',`${args['baseline-ref']}:scripts/unified_explorer/${file}`]));
  const template=execFileSync('git',['show',`${args['baseline-ref']}:scripts/unified_explorer/index.html.template`],{encoding:'utf8'});
  await writeFile(join(temp,'baseline/globe/index.html'),template.replace('{{ENTRY_PROFILE}}','globe'));
  report.bundleSha256=hash(await readFile(join(temp,'current/globe/unified-bundle.json')));
  if(report.bundleSha256!==hash(await readFile(join(temp,'baseline/globe/unified-bundle.json'))))throw Error('Paired bundle differs');
  server=createServer(async(req,res)=>{try{const pathname=decodeURIComponent(new URL(req.url,'http://local').pathname);const path=resolve(temp,'.'+pathname+(pathname.endsWith('/')?'index.html':''));if(!path.startsWith(temp+'/'))throw Error('path');const bytes=await readFile(path);res.writeHead(200,{'Cache-Control':'public,max-age=3600','Content-Type':({'.js':'text/javascript','.json':'application/json','.geojson':'application/json','.css':'text/css','.html':'text/html'})[extname(path)]||'application/octet-stream'});res.end(bytes);}catch{res.writeHead(404);res.end();}});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}`;
  const profile=join(temp,'profile'),deadline=Date.now()+240000;
  browser=spawn(args.browser,['--headless=new','--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--remote-debugging-port=0',`--user-data-dir=${profile}`,'--window-size=1440,900','about:blank'],{stdio:['ignore','ignore','pipe']});browser.stderr.on('data',x=>{log=(log+x).slice(-20000)});
  cdp=await connectCdp(await waitForPageEndpoint(await waitForDevToolsPort(profile,browser,deadline),deadline),deadline);
  for(const domain of ['Page','Runtime','Network','Performance'])await cdp.send(domain+'.enable');
  report.browser=await cdp.send('Browser.getVersion');
  await cdp.send('Emulation.setFocusEmulationEnabled',{enabled:true});
  const metrics=async()=>Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(x=>[x.name,x.value]));
  const diff=(a,b)=>Object.fromEntries(['LayoutCount','RecalcStyleCount','LayoutDuration','RecalcStyleDuration','ScriptDuration','TaskDuration'].map(k=>[k,b[k]-a[k]]));
  async function ready(prior){const until=Date.now()+45000;while(Date.now()<until){if(await evaluate(cdp,`performance.timeOrigin!==${prior} && document.documentElement.dataset.artemisRuntimeReady==='true'`).catch(()=>false))return;await delay(50);}throw Error('Map readiness timeout');}
  async function navigate(url){const prior=await evaluate(cdp,'performance.timeOrigin');await cdp.send('Page.navigate',{url});await ready(prior);return evaluate(cdp,"({readyObservedMs:performance.now(),resources:performance.getEntriesByType('resource').map(x=>({name:x.name,duration:x.duration,transferSize:x.transferSize,encodedBodySize:x.encodedBodySize,decodedBodySize:x.decodedBodySize}))})");}
  for(let repetition=0;repetition<3;repetition++)for(const variant of repetition%2?['current','baseline']:['baseline','current']){
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
    await evaluate(cdp,"document.querySelector('#input-disclosure summary').focus()");
    await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});
    await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});
    await delay(100);
    const disclosure=await evaluate(cdp,"({open:document.getElementById('input-disclosure').open,rawTextChars:document.getElementById('selection-input').textContent.length})");
    disclosure.rawSha256=hash(await evaluate(cdp,"document.getElementById('selection-input').textContent"));
    if(report.runs.length && disclosure.rawSha256!==report.runs[0].disclosure.rawSha256)throw Error('Disclosed native input differs');
    if(!disclosure.open||disclosure.rawTextChars<1000)throw Error('Native disclosure did not expose raw input');
    const sorted=[...movement.samples].sort((a,b)=>a-b);movement.summary={medianMs:sorted[80],p95Ms:sorted[152],maxMs:sorted[159]};
    report.runs.push({variant,repetition,cold,warm,movement,movementMetrics,selection,selectionMetrics,disclosure});
    await writeFile(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');
  }
} catch(error){report.error=String(error.stack||error);throw error;} finally {
  await writeFile(join(output,'report.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(output,'browser.log'),log);
  cdp?.close();if(browser&&browser.exitCode===null)browser.kill('SIGTERM');server?.close();await delay(300);await rm(temp,{recursive:true,force:true,maxRetries:5,retryDelay:100});
}
