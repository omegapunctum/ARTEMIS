// The actual runner's byte binding and entry validation stay fatal; importing its
// shared CDP helpers must not launch the legacy browser CLI.
const assert=require('node:assert/strict');
const {mkdtemp,mkdir,writeFile,rm}=require('node:fs/promises');
const {tmpdir}=require('node:os');
const {join}=require('node:path');
const http=require('node:http');
(async()=>{
  const {argumentsFor,verifyBytes,sameState,contextReplaced}=await import('../scripts/capture_unified_explorer_browser_evidence.mjs');
  assert.throws(()=>argumentsFor(['node','runner','--browser','chrome','--output','proof','--url','https://example.test/globe/']),/expected-artifact/);
  assert.throws(()=>argumentsFor(['node','runner','--browser','chrome','--output','proof','--url','https://example.test/globe/','--artifact','local']),/either/);
  assert.equal(contextReplaced(new Error('Inspected target navigated or closed')),true);
  assert.equal(contextReplaced(new Error('WebSocket closed')),false);
  const state={mode:'range',startYear:91,endYear:1519,cursorYear:100,layers:['leonardo','roman'],camera:{center:[10.00000001,15],zoom:.800000001,pitch:0,bearing:0}};
  assert.equal(sameState(state,JSON.parse(JSON.stringify(state))),true);
  assert.equal(sameState(state,{...state,camera:{center:[10,15],zoom:.8,pitch:0,bearing:0}}),false,'exact native camera must not be silently rounded');
  assert.equal(sameState(state,{...state,cursorYear:101}),false,'state comparison must not hide a different calendar');
  assert.equal(sameState(state,{...state,layers:['roman']}),false,'state comparison must not hide layer loss');
  const directory=await mkdtemp(join(tmpdir(),'artemis-unified-byte-test-')),remote=new Map(),requests=[];
  const server=http.createServer((request,response)=>{const path=new URL(request.url,'http://test').pathname;requests.push(path);const value=remote.get(path);response.writeHead(value===undefined?404:200);response.end(value || 'missing');});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const base=new URL(`http://127.0.0.1:${server.address().port}/`),options={expectedArtifact:directory};
  try{
    for(const entry of ['globe','region']){
      await mkdir(join(directory,entry));
      for(const [path,value] of [['build-meta.json',JSON.stringify({entry})],['unified-bundle.json','{"bundle_id":"immutable"}\n']]){
        await writeFile(join(directory,entry,path),value);remote.set('/'+entry+'/'+path,value);
      }
    }
    const result=await verifyBytes(options,base,Date.now()+5000);assert.equal(result.length,4);
    const checked=remote.get('/globe/unified-bundle.json');remote.set('/globe/unified-bundle.json','{"bundle_id":"unreviewed"}');
    await assert.rejects(verifyBytes(options,base,Date.now()+5000),/published bytes differ globe\/unified-bundle/);
    remote.set('/globe/unified-bundle.json',checked);remote.set('/region/build-meta.json','{"entry":"wrong-release"}');
    await assert.rejects(verifyBytes(options,base,Date.now()+5000),/published bytes differ region\/build-meta/);
    remote.set('/region/build-meta.json',JSON.stringify({entry:'region'}));
    const different='{"bundle_id":"competing-registry"}\n';await writeFile(join(directory,'region','unified-bundle.json'),different);remote.set('/region/unified-bundle.json',different);
    await assert.rejects(verifyBytes(options,base,Date.now()+5000),/entry bundles differ/);
    assert.ok(requests.every(path=>['/globe/build-meta.json','/globe/unified-bundle.json','/region/build-meta.json','/region/unified-bundle.json'].includes(path)),'remote content selected an unreviewed path');
    console.log('Unified artifact binding, entry validation, exact camera state and fatal mismatch checks PASS');
  }finally{await new Promise(resolve=>server.close(resolve));await rm(directory,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
