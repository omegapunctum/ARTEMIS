// Run shipped summary/inspector functions against a minimal DOM and Popup port.
// This proves presentation transitions, not native layout or WebGL performance.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const h = require('../scripts/unified_explorer/runtime.js');
const bundle = h.freeze(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
const source = fs.readFileSync('scripts/unified_explorer/runtime.js','utf8');
class Element {
  constructor(tag='div',text='',className='') {this.tag=tag;this.textContent=text;this.className=className;this.children=[];this.style={};this.dataset={};this.events={};this.hidden=false;this.attrs={};}
  append(...nodes){for(const n of nodes){n.remove();n.parent=this;this.children.push(n);}}
  remove(){if(this.parent){this.parent.children=this.parent.children.filter(n=>n!==this);this.parent=null;}}
  replaceChildren(...nodes){for(const n of [...this.children])n.remove();this.append(...nodes);}
  setAttribute(k,v){this.attrs[k]=v;}
  addEventListener(k,f){this.events[k]=f;}
  contains(n){return this===n||this.children.some(c=>c.contains(n));}
  closest(s){if(s==='.'+this.className||s===this.tag)return this;return this.parent?.closest(s)||null;}
  focus(){document.activeElement=this;}
  checkVisibility(){return !this.hidden&&(!this.parent||this.parent.checkVisibility());}
  getBoundingClientRect(){return this.id==='workspace-header'?{bottom:52}:this.id==='time-dock'?{top:820}:{top:200,bottom:400,left:400,right:700};}
}
const root=new Element(), staticIds=['map','workspace-header','time-dock','selection-summary','inspector','record-select','records-toggle','mobile-records'];
const node=(tag,text='',cls='')=>new Element(tag,text,cls);
const add=(parent,id,tag='div')=>{const e=node(tag);e.id=id;parent.append(e);return e;};
for(const id of staticIds)add(root,id);
const find=(n,id)=>n.id===id?n:n.children.map(c=>find(c,id)).find(Boolean);
const byId=id=>find(root,id);
for(const id of ['selection-title','selection-scope','selection-facts','selection-details','selection-sources','selection-evidence','selection-input','place-episodes'])add(byId('inspector'),id);
for(const id of ['record-disclosure','sources-disclosure','evidence-disclosure','input-disclosure'])add(byId('inspector'),id,'details');
const document={activeElement:null,getElementById:byId};
let projected={x:500,y:400}, occluded=false, popupCount=0;
class Popup {
  constructor(options){this.options=options;this.element=node('div');this.element.style.opacity=occluded?'0':'1';popupCount++;}
  setLngLat(point){this.point=point;return this;}
  setDOMContent(card){this.element.append(card);return this;}
  addTo(){byId('map').append(this.element);return this;}
  getElement(){return this.element;}
  remove(){this.element.remove();}
}
const runtime={bundle,registry:new Map(bundle.registry.map(i=>[i.item_id,i])),visibleItems:bundle.registry,state:{language:'en',presentationView:'map',selectedItemId:null},ready:true,map:{project:()=>projected,getCanvas:()=>({clientWidth:1440,clientHeight:900}),getCenter:()=>({lng:12,lat:44}),isMoving:()=>false}};
const frames=[];
const context=vm.createContext({document,runtime,node,byId,t:key=>key,recordLabel:h.recordLabel,summaryAnchor:h.summaryAnchor,placeGroups:h.placeGroups,
  selectionUI:h.selectionPresentation(),selectionPopup:null,summarySignature:'',clickAnchor:null,renderedSelection:null,mobile:null,desktop:null,
  maplibregl:{Popup},requestAnimationFrame:fn=>frames.push(fn),getComputedStyle:e=>e.style,
  renderCatalogFacts(){},renderCatalogContext(){},renderInspectorLanguage(){},renderSourceRights(){},technicalJson(){},safeLink:()=>null,inputJson(host,value){host.value=value;},layout(){}});
const functions=source.slice(source.indexOf('  function sourceRecord('),source.indexOf('  function renderCatalogFacts('));
vm.runInContext(functions,context);
context.selectItem=id=>{runtime.state={...runtime.state,selectedItemId:id};context.selectionUI.summary();context.renderInspector();};
const drain=()=>{while(frames.length)frames.shift()();};
const text=n=>[n.textContent,...n.children.map(text)].join(' ');
const first=bundle.registry.find(i=>i.kind==='catalog_reference');
context.selectItem(first.item_id);drain();
assert.equal(byId('inspector').hidden,true);assert(byId('open-details'));assert.equal(popupCount,1);
assert(text(byId('selection-card')).includes('catalogUnverified'));
const state=JSON.stringify(runtime.state);
byId('open-details').events.click();
assert.equal(byId('inspector').hidden,false);assert.equal(byId('selection-card'),undefined);
assert.equal(JSON.stringify(runtime.state),state);assert.equal(document.activeElement,byId('selection-title'));
byId('sources-disclosure').open=true;
runtime.state={...runtime.state,language:'ru'};context.renderInspector();
assert.equal(byId('inspector').hidden,false);assert.equal(byId('sources-disclosure').open,true);
context.selectionUI.summary();context.renderInspector();drain();
assert.equal(byId('inspector').hidden,true);assert.equal(byId('open-details').textContent,'Подробнее');
byId('open-details').events.click();assert.equal(byId('sources-disclosure').open,true);
const reference=bundle.registry.find(i=>i.kind==='reference' && bundle.architecture.references.find(r=>r.item_id===i.item_id).raw_feature.properties.name_ru);
context.selectItem(reference.item_id);drain();
assert.equal(byId('inspector').hidden,true);
assert.equal(byId('summary-title').textContent,bundle.architecture.references.find(r=>r.item_id===reference.item_id).raw_feature.properties.name_ru);
const cesena=bundle.leonardo.lifePath.presences.find(p=>p.event_ref==='event-leonardo-cesena-survey');
context.selectItem(cesena.presence_item_id);drain();
assert(text(byId('selection-card')).includes(cesena.temporal.start));
assert(text(byId('selection-card')).includes(cesena.short_description));
assert(text(byId('selection-card')).includes('cesenaCandidateContext'));
projected={x:-100,y:400};context.selectItem(first.item_id);drain();assert.equal(byId('selection-summary').hidden,false);
projected={x:500,y:400};occluded=true;context.selectItem(reference.item_id);drain();
assert.equal(byId('selection-summary').hidden,false);assert(byId('open-details'));
byId('close-summary').events.click();assert.equal(runtime.state.selectedItemId,null);assert.equal(byId('selection-card'),undefined);
assert.equal(document.activeElement,byId('record-select'));
const region=bundle.registry.find(i=>i.kind==='region');context.selectItem(region.item_id);drain();
assert.equal(byId('selection-summary').hidden,false);assert(text(byId('selection-card')).includes('reconstruction'));
console.log('COMPACT_SELECTION_DOM_BEHAVIOR_PASS');
