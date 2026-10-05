'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('scripts/globe_spike/runtime.js', 'utf8');
const helpers = 'function presentationViewFromUrl' + source.split('function presentationViewFromUrl')[1].split('function bindOverlayLayout')[0];

function setup(url) {
  const listeners = {}, history = [], calls = [];
  const button = () => ({ attrs: {}, disabled: true, events: {}, setAttribute(k, v) { this.attrs[k] = v; }, addEventListener(k, fn) { this.events[k] = fn; } });
  const link = button(); link.dataset = { exampleRoute: '../region/' };
  const status = { hidden: true, textContent: '' };
  const elements = { 'view-globe': button(), 'view-map': button(), 'language-en': button(), 'language-ru': button(), 'projection-status': status, 'research-examples': { querySelectorAll() { return [link]; } } };
  const map = {
    type: 'globe',
    setProjection({ type }) { calls.push(type); this.type = type; },
    getProjection() { return { type: this.type }; },
    once(event, fn) { assert.equal(event, 'idle'); fn(); }
  };
  const runtime = { map, projectionReady: false, presentationView: 'globe',
    data: { state: { temporal_selection: 'nondefault', selection: { item: 'selected' } }, projection: { geometries: ['shared'], losses: ['unknown'] }, knowledge: { sources: ['retained'], evidence: ['draft'], uncertainty: ['unknown'] }, lifePath: { route_policy: { geometry: null } } },
    selectedItemId: 'selected', selectedPresenceId: 'presence', activeLayerRefs: ['region'], activeTemporalPresetId: 'period-114-116', lifePathMode: 'scrub', lifePathStartIndex: 4, lifePathEndIndex: 7 };
  const document = { documentElement: { dataset: {} } };
  const window = { location: { href: url }, ARTEMIS_I18N: { language: 'en', setLanguage(value) { this.language = value; }, refresh() {} },
    history: { state: { preserved: true }, pushState(state, _, value) { history.push({ kind: 'push', url: String(value), state }); window.location.href = String(value); }, replaceState(state, _, value) { history.push({ kind: 'replace', url: String(value), state }); window.location.href = String(value); } },
    addEventListener(event, fn) { (listeners[event] ||= []).push(fn); } };
  const context = vm.createContext({ URL, window, document, runtime, byId: id => elements[id], requestAnimationFrame: fn => fn(), syncOverlayLayout() {}, layoutPlaceLabels() {}, positionChronologyCues() {} });
  vm.runInContext(helpers, context);
  const semantics = () => JSON.stringify(Object.fromEntries(Object.entries(runtime).filter(([key]) => !['map', 'projectionReady', 'presentationView'].includes(key))));
  return { context, runtime, map, elements, status, link, window, listeners, history, calls, semantics };
}

const initial = 'https://example.test/ARTEMIS/globe/?mode=scrub&from=1499&at=1502&presence=presence&item=selected&lang=ru&unknown=keep#saved';
const t = setup(initial);
t.context.bindLanguageControls(true);
t.context.bindPresentationControls();
assert.equal(t.context.applyPresentationView('map', 'push'), false);
assert.deepEqual(t.calls, []);
assert.deepEqual(t.history, []);
t.runtime.projectionReady = true;
t.context.restorePresentationViewFromUrl();
assert.equal(t.elements['view-globe'].disabled, false);
const before = t.semantics();
t.elements['view-map'].events.click();
assert.equal(t.map.type, 'mercator');
assert.equal(t.runtime.presentationView, 'map');
assert.equal(t.elements['view-map'].attrs['aria-pressed'], 'true');
assert.equal(t.elements['view-globe'].attrs['aria-pressed'], 'false');
assert.equal(t.semantics(), before);
const expected = new URL(initial); expected.searchParams.set('view', 'map');
assert.equal(t.window.location.href, expected.href);
assert.equal(t.history.length, 1);
assert.equal(t.history[0].kind, 'push');
assert.equal(t.history[0].state.preserved, true);
assert.equal(t.link.attrs.href, '../region/?lang=ru&view=map');
t.elements['view-map'].events.click();
assert.equal(t.history.length, 1); // Selecting the already active native mode creates no entry.
t.elements['language-en'].events.click();
assert.equal(t.link.attrs.href, '../region/?lang=en&view=map');
assert.equal(new URL(t.window.location.href).searchParams.get('at'), '1502');
t.elements['view-globe'].events.click();
assert.equal(t.history.at(-1).kind, 'push');
assert.equal(t.map.type, 'globe');
assert.equal(t.semantics(), before);

// Popstate gets its projection from the restored URL, retaining that entry's language.
t.window.location.href = expected.href;
for (const fn of t.listeners.popstate) fn();
assert.equal(t.runtime.presentationView, 'map');
assert.equal(t.map.type, 'mercator');
assert.equal(t.link.attrs.href, '../region/?lang=ru&view=map');

// Saved URLs, invalid native mode and missing mode are each tested independently.
for (const [value, actual] of [['map', 'mercator'], ['globe', 'globe'], ['MAP', 'globe'], ['bad<script>', 'globe'], ['', 'globe'], [null, 'globe']]) {
  const url = new URL(initial);
  if (value !== null) url.searchParams.set('view', value);
  const test = setup(url.href);
  test.runtime.projectionReady = true;
  test.context.restorePresentationViewFromUrl();
  assert.equal(test.map.type, actual);
  assert.equal(new URL(test.window.location.href).hash, '#saved');
  assert.equal(new URL(test.window.location.href).searchParams.get('at'), '1502');
}

// Synchronous rejection retains Globe; failure after mutation is rolled back.
for (const mutate of [false, true]) {
  const test = setup(initial);
  test.runtime.projectionReady = true;
  test.map.setProjection = ({ type }) => { if (type === 'mercator') { if (mutate) test.map.type = type; throw Error('native failure'); } test.map.type = type; };
  const snapshot = test.semantics();
  assert.equal(test.context.applyPresentationView('map', 'push'), false);
  assert.equal(test.map.type, 'globe');
  assert.equal(test.runtime.presentationView, 'globe');
  assert.equal(test.status.hidden, false);
  assert.match(test.status.textContent, /Could not complete/);
  assert.equal(test.history.at(-1).kind, 'replace');
  assert.equal(new URL(test.window.location.href).searchParams.get('view'), 'globe');
  assert.equal(test.semantics(), snapshot);
}

// If rollback itself fails, UI and URL describe the projection actually retained.
const ignored = setup(initial); ignored.runtime.projectionReady = true;
ignored.map.setProjection = () => {};
assert.equal(ignored.context.applyPresentationView('map', 'push'), false);
assert.equal(ignored.runtime.presentationView, 'globe');
assert.equal(ignored.status.hidden, false);
assert.equal(ignored.history.at(-1).kind, 'replace');

const rollback = setup(initial); rollback.runtime.projectionReady = true;
rollback.map.setProjection = ({ type }) => { if (type === 'mercator') rollback.map.type = type; throw Error('failure'); };
assert.equal(rollback.context.applyPresentationView('map', 'push'), false);
assert.equal(rollback.map.type, 'mercator');
assert.equal(rollback.runtime.presentationView, 'map');
assert.equal(rollback.elements['view-map'].attrs['aria-pressed'], 'true');
assert.equal(new URL(rollback.window.location.href).searchParams.get('view'), 'map');
rollback.map.setProjection = ({ type }) => { rollback.map.type = type; };
assert.equal(rollback.context.applyPresentationView('globe', 'push'), true);
assert.equal(rollback.status.hidden, true);
console.log('Explorer presentation behavior PASS');
