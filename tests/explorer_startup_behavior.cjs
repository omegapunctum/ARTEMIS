// Execute all shipped application scripts from their entry points against a
// minimal DOM port built from the actual template. This is not a browser/WebGL
// or CSS-layout acceptance test: the Map constructor and viewport are stubbed.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const fixture = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
class Element {
  constructor(tag, attrs = {}) {
    this.tagName = tag.toUpperCase(); this.attrs = {...attrs}; this.children = [];
    this.dataset = {}; this.events = {}; this.hidden = 'hidden' in attrs; this.disabled = 'disabled' in attrs;
    this.id = attrs.id; this.className = attrs.class || ''; this.value = attrs.value || ''; this.textContent = '';
    this.properties = {}; this.style = {setProperty:(k,v)=>this.properties[k]=v,getPropertyValue:k=>this.properties[k] || ''};
    for (const [k,v] of Object.entries(attrs)) if (k.startsWith('data-')) this.dataset[k.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=v;
  }
  get parentElement(){return this.parent;}
  get firstChild(){return this.children[0];}
  get options(){return this.children;}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this);this.parent=null;}
  append(...nodes){for(const n of nodes){n.remove();n.parent=this;this.children.push(n);}}
  replaceChildren(...nodes){for(const n of [...this.children])n.remove();this.append(...nodes);}
  before(n){n.remove();n.parent=this.parent;this.parent.children.splice(this.parent.children.indexOf(this),0,n);}
  after(n){n.remove();n.parent=this.parent;this.parent.children.splice(this.parent.children.indexOf(this)+1,0,n);}
  getAttribute(k){return this.attrs[k] ?? null;} setAttribute(k,v){this.attrs[k]=v;} removeAttribute(k){delete this.attrs[k];}
  addEventListener(k,f){(this.events[k] ||= []).push(f);}
  contains(n){return this===n || this.children.some(c=>c.contains(n));}
  focus(){} checkVisibility(){return !this.hidden && (!this.parent || this.parent.checkVisibility());}
  getBoundingClientRect(){return {bottom:52,height:80,top:0,left:0,right:1440};}
  matches(s){return s[0]==='#'?this.id===s.slice(1):s[0]==='.'?this.className.split(' ').includes(s.slice(1)):s==='[data-i18n]'?'data-i18n' in this.attrs:this.tagName===s.toUpperCase();}
  querySelectorAll(s){return this.children.flatMap(c=>[...(c.matches(s)?[c]:[]),...c.querySelectorAll(s)]);}
  querySelector(s){return this.querySelectorAll(s)[0] || null;}
}
function tree(raw){const e=new Element(raw.tag,raw.attrs);e.append(...raw.children.map(tree));return e;}
async function scenario(kind) {
  const document=tree(fixture.tree);
  document.documentElement=document.querySelector('html'); document.documentElement.dataset.entryProfile='globe';
  document.body=document.querySelector('body'); document.activeElement=document.body;
  document.getElementById=id=>document.querySelector('#'+id); document.createElement=tag=>new Element(tag); document.createComment=()=>new Element('comment');
  if(kind==='embedded') for(const name of ['unified-bundle.json','earth-context.geojson','geospatial-assets.json','build-meta.json']) {
    const script=new Element('script',{id:'embedded-'+name});
    script.textContent=Buffer.from(JSON.stringify(name==='unified-bundle.json'?fixture.bundle:{}),'utf8').toString('base64');
    document.body.append(script);
  }
  const timers=new Map();let sequence=0, constructed=0;
  const window={events:{},addEventListener(k,f){(this.events[k] ||= []).push(f);},matchMedia:()=>({matches:false,addEventListener(){}}),history:{replaceState(){},pushState(){}}};
  class MapPort {constructor(){constructed++;if(kind==='webgl')throw Error('WebGL unavailable');}addControl(){}on(){} }
  if(kind!=='engine')window.maplibregl={Map:MapPort,NavigationControl:class{}};
  const context=vm.createContext({window,document,console:{error(){}},URL,Map,WeakMap,WeakSet,Set,AbortController,
    location:{href:kind==='embedded'?'file:///ARTEMIS.html':'http://127.0.0.1:4175/'},ResizeObserver:class{observe(){}},
    atob:encoded=>Buffer.from(encoded,'base64').toString('binary'),TextDecoder,Uint8Array,
    maplibregl:window.maplibregl,requestAnimationFrame:fn=>fn(),
    setTimeout:(fn,ms)=>{const id=++sequence;timers.set(id,{fn,ms});return id;},clearTimeout:id=>timers.delete(id),
    fetch:async (url,opts)=>{
      if(kind==='embedded')throw Error('Unexpected network request in standalone startup');
      if(kind==='fetch')throw Error('Server connection lost');
      if(kind==='timeout')return new Promise((_,reject)=>opts.signal.addEventListener('abort',()=>reject(Error('Aborted'))));
      return {ok:kind!=='http',status:404,json:async()=>url.includes('unified-bundle')?fixture.bundle:{}};
    }});
  for(const script of ['startup.js','mobile.js','desktop.js','runtime.js']) {
    if(kind===script) {
      const target=new Element('script',{src:'./'+script}); for(const handler of window.events.error)handler({target});
    } else vm.runInContext(fs.readFileSync('scripts/unified_explorer/'+script,'utf8'),context,{filename:script});
  }
  if(kind==='timeout') for(const {fn,ms} of [...timers.values()])if(ms===15000)fn();
  for(let i=0;i<30;i++)await Promise.resolve();
  const byId=id=>document.getElementById(id), state=window.__ARTEMIS_EXPLORER?.state;
  if(kind==='ok'||kind==='embedded') {
    assert.equal(constructed,1); assert(state); assert.equal(byId('record-search').parentElement.parentElement.id,'desktop-search');
    assert.equal(byId('layer-controls').parentElement.id,'desktop-layer-body'); assert.equal(byId('record-select').getAttribute('size'),'7');
    const track=byId('range-start-handle').parentElement;
    assert.equal(track.dataset.rangeReady,'true'); assert(Number.parseFloat(track.properties['--range-start'])>95);
    assert.equal(track.properties['--range-end'],'100%'); assert.equal(track.dataset.overlap,'false');
    byId('range-start-handle').value='1519';byId('range-start-handle').events.input[0]();
    assert.equal(track.dataset.overlap,'true'); assert.equal(track.properties['--range-start'],'100%');
    assert.equal(document.documentElement.dataset.artemisBoot,'loading');
    timers.get([...timers.keys()][0]).fn(); assert.match(byId('startup-status').textContent,/Starting the globe/);
    window.ARTEMIS_STARTUP.ready(); assert.equal(byId('startup-status').hidden,true); assert.equal(timers.size,0);
  } else {
    assert.equal(document.documentElement.dataset.artemisBoot,'failed');assert.equal(timers.size,0);
    const diagnostic=kind.endsWith('.js')?byId('startup-status'):byId('fatal-error');
    assert.equal(diagnostic.hidden,false);
    assert.match(diagnostic.textContent,kind==='webgl'?/WebGL unavailable/:kind==='engine'?/Pinned MapLibre/:kind==='timeout'?/timed out/:kind==='http'?/HTTP 404/:kind.endsWith('.js')?/local script unavailable/:/Server connection lost/);
    const failure=byId('startup-status').textContent;
    window.ARTEMIS_STARTUP.phase('map');window.ARTEMIS_STARTUP.ready();
    assert.equal(document.documentElement.dataset.artemisBoot,'failed');assert.equal(byId('startup-status').textContent,failure);
  }
}
(async()=>{for(const kind of ['ok','embedded','engine','webgl','fetch','timeout','http','mobile.js','desktop.js','runtime.js'])await scenario(kind);console.log('EXPLORER_STARTUP_BEHAVIOR_PASS');})().catch(e=>{console.error(e);process.exitCode=1;});
