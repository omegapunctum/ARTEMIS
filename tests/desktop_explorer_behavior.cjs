// Execute the shipped presentation adapter; native layout evidence is separate.
const assert = require('node:assert/strict');
class Element {
  constructor(id) {this.id=id;this.children=[];this.dataset={};this.attrs={};this.events={};}
  detach(){if(this.parent){this.parent.children.splice(this.parent.children.indexOf(this),1);}}
  append(e){e.detach();e.parent=this;this.children.push(e);}
  before(e){e.detach();e.parent=this.parent;this.parent.children.splice(this.parent.children.indexOf(this),0,e);}
  after(e){e.detach();e.parent=this.parent;this.parent.children.splice(this.parent.children.indexOf(this)+1,0,e);}
  getAttribute(k){return this.attrs[k]??null;} setAttribute(k,v){this.attrs[k]=v;} removeAttribute(k){delete this.attrs[k];}
  addEventListener(k,f){this.events[k]=f;} focus(){this.focused=true;document.activeElement=this;}
  contains(e){return this===e||this.children.some(c=>c.contains(e));}
  checkVisibility(){return this.visible!==false;}
}
const els=new Map(), el=id=>{if(!els.has(id))els.set(id,new Element(id));return els.get(id);};
const original=['presentation-controls','layer-controls','layer-status','search-hint','search-status','record-picker','workspace-error','record-search'];
for(const id of original)el('original').append(el(id));
let listener;const media={matches:false,addEventListener:(_,f)=>listener=f};
global.document={getElementById:el,querySelector:s=>el(s.slice(1)),createComment:()=>new Element('anchor')};
global.window={matchMedia:()=>media};
const {mount,MOBILE_QUERY}=require('../scripts/unified_explorer/desktop.js');
assert.equal(MOBILE_QUERY,require('../scripts/unified_explorer/mobile.js').MOBILE_QUERY);
const runtime={state:{language:'en',selectedItemId:'cesena',camera:{center:[12,44]},startYear:1452,endYear:1519}};
runtime.registry=new Map([['cesena',{label:'Cesena',interval:{start:1502,end:1502}}]]);
const option=new Element('option'); option.value='cesena'; option.textContent='Leonardo · Cesena · 1502–1502'; el('record-select').options=[option];
const initial=JSON.stringify(runtime.state);const adapter=mount({runtime,layout(){}});
assert.equal(option.textContent,'Cesena · 1502');
assert.equal(el('record-search').parent,el('desktop-search'));
assert.equal(el('record-select').getAttribute('size'),'7');
el('records-toggle').events.click();assert.equal(el('desktop-records-body').hidden,true);assert.equal(el('records-toggle').focused,true);
adapter.selectionChanged('cesena');el('inspector-toggle').events.click();assert.equal(el('inspector').dataset.desktopCollapsed,'true');
adapter.selectionChanged('cesena');assert.equal(el('inspector').dataset.desktopCollapsed,'true');
assert.equal(JSON.stringify(runtime.state),initial);
media.matches=true;listener();assert.equal(option.textContent,'Leonardo · Cesena · 1502–1502');assert.deepEqual(el('original').children.filter(e=>e.id!=='anchor').map(e=>e.id),original);
assert.equal(el('record-select').getAttribute('size'),null);assert.equal(el('inspector').dataset.desktopCollapsed,'false');
media.matches=false;listener();assert.equal(el('inspector').dataset.desktopCollapsed,'true');
adapter.selectionChanged('rimini');assert.equal(el('inspector').dataset.desktopCollapsed,'false');
runtime.state.language='ru';adapter.render();assert.equal(el('records-toggle').textContent,'Развернуть записи');
el('records-toggle').events.click();assert.equal(el('desktop-records-body').hidden,false);
// Explicitly model native blur during reparenting and hidden breakpoint owners.
el('record-search').focus();
el('record-search').visible=false;
media.matches=true;listener();assert.equal(document.activeElement,el('mobile-records'));
el('mobile-records').visible=false;
media.matches=false;listener();assert.equal(document.activeElement,el('records-toggle'));
el('inspector').append(el('inspector-toggle'));
el('inspector-toggle').focus();el('inspector-toggle').visible=false;
media.matches=true;listener();assert.equal(document.activeElement,el('close-details'));
el('inspector').append(el('selection-facts'));
el('selection-facts').focus();el('selection-facts').visible=false;
el('inspector-toggle').visible=true;
media.matches=false;listener();assert.equal(document.activeElement,el('inspector-toggle'));
assert.equal(JSON.stringify({...runtime.state,language:'en'}),initial);
el('desktop-layers').append(el('layers-summary'));
el('layers-summary').focus();el('layers-summary').visible=false;
media.matches=true;listener();assert.equal(document.activeElement,el('mobile-layers'));
console.log('DESKTOP_EXPLORER_BEHAVIOR_PASS');
