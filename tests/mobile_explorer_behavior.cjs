// Behavioral checks execute the shipped adapter. Layout and native gestures
// require the separate browser loop; this DOM adapter claims neither.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const helpers = require('../scripts/unified_explorer/mobile.js');
const initial = {mode:'range',startYear:1452,endYear:1519,cursorYear:1519};
assert.deepEqual(helpers.stepDraft(initial,'startYear',999),{...initial,startYear:1519});
assert.deepEqual(helpers.stepDraft(initial,'endYear',-999),{...initial,endYear:1452});
assert.equal(helpers.stepDraft(initial,'cursorYear',-9999).cursorYear,91);
assert.equal(helpers.stepDraft(initial,'cursorYear',9999).cursorYear,1519);
assert.deepEqual(initial,{mode:'range',startYear:1452,endYear:1519,cursorYear:1519});
assert.deepEqual(helpers.commitDraft(initial),{startYear:1452,endYear:1519});
assert.deepEqual(helpers.commitDraft({...initial,mode:'scrub'}),{cursorYear:1519});
assert.deepEqual(helpers.stepDraft(initial,'traceOriginYear',10),initial);
assert.equal(helpers.MOBILE_QUERY,'(max-width:640px), (max-width:960px) and (max-height:500px)');

class Element {
  constructor() { this.dataset = {}; this.attrs = {}; this.events = {}; this.children = {}; this.disabled = false; this.textContent = ''; this.focused = false; this.capture = null; }
  setAttribute(key,value) { this.attrs[key] = value; }
  querySelector(selector) { return this.children[selector] ||= new Element(); }
  addEventListener(key,fn) { (this.events[key] ||= []).push(fn); }
  focus() { this.focused = true; }
  closest() { return null; }
  setPointerCapture(value) { this.capture = value; }
  hasPointerCapture(value) { return this.capture === value; }
  releasePointerCapture() { this.capture = null; }
  emit(key,values = {}) { const event = {key:null,detail:1,target:this,button:0,pointerId:1,preventDefault(){this.prevented=true;},stopPropagation(){this.stopped=true;},stopImmediatePropagation(){this.immediate=true;},...values}; for (const fn of this.events[key] || []) fn(event); return event; }
}
const elements = new Map(), el = id => { if (!elements.has(id)) elements.set(id,new Element()); return elements.get(id); };
const document = new Element(); document.getElementById = el;
let narrow = true, commits = [], layouts = 0;
const mediaListeners = [];
const media = {get matches(){return narrow;},addEventListener:(_,fn) => mediaListeners.push(fn)};
const runtime = {state:{...initial,language:'ru',traceOriginYear:1452,layers:['catalog'],camera:{center:[10,15]}},ready:true};
const context = vm.createContext({document,window:{matchMedia:query => { assert.equal(query,helpers.MOBILE_QUERY); return media; }},module:{exports:{}},setTimeout});
vm.runInContext(fs.readFileSync('scripts/unified_explorer/mobile.js','utf8'),context);
let adapter;
adapter = context.window.ARTEMIS_MOBILE.mount({runtime,layout:() => layouts++,applyState:patch => { commits.push({...patch}); runtime.state = {...runtime.state,...patch}; adapter.render(); }});
adapter.render();
assert.equal(el('time-dock').dataset.expanded,'false');
assert.equal(el('mobile-range-start').attrs['aria-valuenow'],'1452');
assert.equal(el('mobile-range-start').attrs['aria-label'],'Начальный год интервала, н. э.');
assert.equal(el('mobile-apply').disabled,true);
assert.equal(el('header-close').textContent,'Закрыть панель');

// Wheel edits cannot mutate canonical years, camera, layers or URL adapter.
const canonical = JSON.stringify(runtime.state);
el('mobile-range-start').emit('keydown',{key:'ArrowUp'});
assert.equal(JSON.stringify(runtime.state),canonical); assert.equal(commits.length,0);
assert.equal(el('mobile-range-start').attrs['aria-valuenow'],'1453');
assert.equal(el('range-start-handle').value,1453);
assert.equal(el('range-end-handle').value,1519);
assert.equal(el('mobile-apply').disabled,false);
el('mobile-apply').emit('click');
assert.deepEqual(commits,[{startYear:1453,endYear:1519}]);
assert.equal(runtime.state.traceOriginYear,1452);
assert.deepEqual(runtime.state.layers,['catalog']);
assert.equal(el('mobile-apply').disabled,true);

el('mobile-range-end').emit('keydown',{key:'Home'});
assert.equal(el('mobile-range-end').attrs['aria-valuenow'],'1453');
el('mobile-cancel').emit('click');
assert.equal(el('mobile-range-end').attrs['aria-valuenow'],'1519');
assert.equal(el('range-end-handle').value,1519);
el('mobile-range-start').emit('keydown',{key:'PageUp'});
runtime.state = {...runtime.state,language:'en'}; adapter.render();
assert.equal(el('mobile-range-start').attrs['aria-valuenow'],'1463');
assert.equal(el('mobile-range-start').attrs['aria-label'],'Interval start year CE');
assert.equal(el('header-close').textContent,'Close panel');
document.emit('keydown',{key:'Escape'});
assert.equal(el('mobile-range-start').attrs['aria-valuenow'],'1453');
assert.equal(el('mobile-apply').disabled,true);

// Incumbent temporal commits/history/presets take precedence over staged edits.
el('mobile-range-start').emit('keydown',{key:'ArrowUp'});
runtime.state = {...runtime.state,startYear:91,endYear:116}; adapter.render();
assert.equal(el('mobile-range-start').attrs['aria-valuenow'],'91');
assert.equal(el('mobile-apply').disabled,true);
el('mobile-range-start').emit('keydown',{key:'End'});
assert.equal(el('mobile-range-start').attrs['aria-valuenow'],'116');
el('mobile-range-start').emit('keydown',{key:'ArrowUp'});
assert.equal(el('mobile-range-start').attrs['aria-valuenow'],'116');
el('mobile-cancel').emit('click');

// Header exclusivity, selection close, Escape focus return, map untouched.
const beforePanels = JSON.stringify(runtime.state);
el('mobile-layers').emit('click'); assert.equal(el('workspace-header').dataset.headerPanel,'layers');
el('mobile-records').emit('click'); assert.equal(el('workspace-header').dataset.headerPanel,'records');
assert.equal(el('mobile-layers').attrs['aria-expanded'],'false');
document.emit('keydown',{key:'Escape'});
assert.equal(el('workspace-header').dataset.headerPanel,''); assert.equal(el('mobile-records').focused,true);
el('mobile-records').emit('click'); adapter.selectionChanged('catalog:wikidata:Q83125');
assert.equal(el('workspace-header').dataset.headerPanel,'');
assert.equal(JSON.stringify(runtime.state),beforePanels);

// Cancelled touch gestures restore staged values; never commit implicitly.
const spinner = el('mobile-range-start');
spinner.emit('pointerdown',{clientY:100}); spinner.emit('pointermove',{clientY:64});
assert.equal(spinner.attrs['aria-valuenow'],'93');
spinner.emit('pointercancel'); assert.equal(spinner.attrs['aria-valuenow'],'91');
assert.equal(commits.length,1);
spinner.emit('wheel',{deltaY:20}); assert.equal(spinner.attrs['aria-valuenow'],'92');
el('mobile-cancel').emit('click');
el('dock-toggle').emit('pointerdown',{clientY:100}); el('dock-toggle').emit('pointerup',{clientY:140});
assert.equal(el('time-dock').dataset.expanded,'false');
assert.equal(commits.length,1);

// Scrub commits only cursor, retaining trace origin and remembered range.
runtime.state = {...runtime.state,mode:'scrub',cursorYear:1519}; adapter.render();
el('mobile-cursor-year').emit('keydown',{key:'PageDown'});
assert.equal(runtime.state.cursorYear,1519); assert.equal(el('time-cursor').value,1509);
el('mobile-cursor-year').emit('keydown',{key:'Enter'});
assert.deepEqual(commits[1],{cursorYear:1509});
assert.equal(runtime.state.startYear,91); assert.equal(runtime.state.endYear,116); assert.equal(runtime.state.traceOriginYear,1452);
el('mobile-cursor-year').emit('keydown',{key:'ArrowDown'});
el('mobile-settings').emit('click'); el('attribution-toggle').emit('click');
assert.equal(el('app').dataset.attributionOpen,'true');
narrow = false; for (const fn of mediaListeners) fn({matches:false});
assert.equal(el('mobile-cursor-year').attrs['aria-valuenow'],'1509');
assert.equal(el('mobile-apply').disabled,true);
assert.equal(el('workspace-header').dataset.headerPanel,'');
assert.equal(el('time-dock').dataset.expanded,'false');
assert.equal(el('app').dataset.attributionOpen,'false');
assert.equal(commits.length,2);
assert.equal(el('time-cursor').value,1509);
el('mobile-cursor-year').emit('keydown',{key:'ArrowDown'});
assert.equal(el('mobile-cursor-year').attrs['aria-valuenow'],'1509');
runtime.ready = false; adapter.render();
el('mobile-cursor-year').emit('keydown',{key:'ArrowDown'});
assert.equal(el('mobile-cursor-year').attrs['aria-valuenow'],'1509');
assert.equal(el('mobile-cursor-year').attrs['aria-disabled'],'true');
assert.ok(layouts > 0);
console.log('MOBILE_EXPLORER_BEHAVIOR_PASS');
