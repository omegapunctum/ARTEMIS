// Run the actual projection runner's input/navigation helpers against a peer
// that unloads the source page on native link activation. No Chromium required.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const source = fs.readFileSync('scripts/capture_globe_browser_evidence.mjs', 'utf8');
const projection = source.slice(source.indexOf('async function verifyProjectionSwitch('), source.indexOf('async function main('));
const inputSource = projection.slice(projection.indexOf('  async function key('), projection.indexOf('  async function waitDocumentNavigation('));
const inputFactory = new Function('cdp', 'evaluate', 'settle', `${inputSource}; return {click,key};`);
const navigationSource = projection.slice(projection.indexOf('  async function waitDocumentNavigation('), projection.indexOf('  async function navigate('));
const navigationFactory = new Function('cdp', 'evaluate', 'deadline', 'check', 'delay', 'waitForVisualReadiness', 'mapIdle', `${navigationSource}; return waitDocumentNavigation;`);
const check = (condition, message) => {if (!condition) throw new Error(message);};
const unloaded = new Error('{"code":-32000,"message":"Inspected target navigated or closed"}');

async function inputCase({keyboard, navigation}) {
  let detached = false, settled = 0, readCount = 0;
  const commands = [];
  const cdp = {async send(method, params) {
    commands.push({method,...params});
    if (navigation && (params.type === 'mouseReleased' || params.type === 'keyUp')) detached = true;
  }};
  const evaluate = async (_cdp, expression) => {
    assert.match(expression, /document\.querySelector/);
    assert.equal(detached,false,'runner tried reading the unloaded source document');
    readCount++;
    return {x:10,y:20,href:navigation?'https://example.test/region/':null};
  };
  const settle = async () => {if (detached) throw unloaded; settled++;};
  const {click} = inputFactory(cdp,evaluate,settle);
  const result = await click(navigation?'#example-region':'#view-map',keyboard,navigation);
  assert.equal(readCount,1);
  assert.equal(settled,navigation?0:1,'only non-navigation controls settle the current document');
  assert.equal(commands.length,2);
  if (keyboard) {
    assert.deepEqual(commands.map(c=>c.type),['keyDown','keyUp']);
    assert.ok(commands.every(c=>c.key===(navigation?'Enter':' ')));
  } else assert.deepEqual(commands.map(c=>c.type),['mousePressed','mouseReleased']);
  assert.equal(result.href,navigation?'https://example.test/region/':null);
}

async function navigationCase() {
  // Old ready document, replacing execution context, old-origin wrong document,
  // then a destination document. Readiness must never be tested prematurely.
  const replies = [false,unloaded,false,true,true];
  const stages = [];
  let reads = 0;
  const evaluate = async (_cdp, expression) => {
    assert.match(expression,/location\.pathname/);
    if (reads<4) assert.match(expression,/performance\.timeOrigin!==100/);
    const response=replies[reads++];
    if(response instanceof Error)throw response;
    return response;
  };
  const cdp = {async send(method) {stages.push(method);}};
  const waitReady = async () => {assert.equal(reads,4);stages.push('destination visual readiness');};
  const idle = async () => {assert.equal(reads,5);stages.push('native map idle');};
  const wait = navigationFactory(cdp,evaluate,Date.now()+1000,check,async()=>{},waitReady,idle);
  await wait(100,'/region/');
  assert.equal(reads,5);
  assert.deepEqual(stages,['destination visual readiness','Emulation.setFocusEmulationEnabled','native map idle']);

  let fatalReads=0;
  const fatal = navigationFactory(cdp,async()=>{fatalReads++;throw new Error('WebSocket closed');},Date.now()+1000,check,async()=>{},waitReady,idle);
  await assert.rejects(fatal(100,'/region/'),/WebSocket closed/);
  assert.equal(fatalReads,1,'a non-navigation transport failure must not be retried');
  const expired = navigationFactory(cdp,async()=>{throw new Error('expired navigation must not read');},Date.now()-1,check,async()=>{},waitReady,idle);
  await assert.rejects(expired(100,'/region/'),/new destination document did not load/);

  const badMap = navigationFactory(cdp,async()=>true,Date.now()+1000,check,async()=>{},async()=>{throw new Error('actual fatal map failure');},idle);
  await assert.rejects(badMap(100,'/region/'),/actual fatal map failure/);
}

(async()=>{
  for(const keyboard of [false,true])for(const navigation of [false,true])await inputCase({keyboard,navigation});
  await navigationCase();
  assert.match(projection,/click\('#example-'\+target,false,true\)/);
  assert.match(projection,/waitDocumentNavigation\(priorOrigin,routes\[target\]\.pathname\)/);
  console.log('Native navigation unload, destination readiness, button settling and fatal failure checks PASS');
})().catch(error=>{console.error(error);process.exitCode=1;});
