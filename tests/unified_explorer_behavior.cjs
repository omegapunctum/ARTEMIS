'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const h = require('../scripts/unified_explorer/runtime.js');
if (!process.argv[2]) throw Error('Pass the actual composed source bundle as a fixture');
const bundle = h.freeze(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
const digest = () => crypto.createHash('sha256').update(JSON.stringify(bundle)).digest('hex');
const before = digest();
const ids = result => result.map(item => item.item_id);
const base = h.defaults('globe');
assert.equal(bundle.registry.length,45);
assert.equal(h.query(bundle,base).length,11);
assert.equal(h.query(bundle,h.defaults('region')).length,1);
const preLeonardo = h.normalizeState(bundle,{...base,mode:'scrub',cursorYear:100});
assert.equal(preLeonardo.cursorYear,100);
assert.equal(preLeonardo.traceOriginYear,1452);
assert.equal(h.query(bundle,preLeonardo).filter(item => item.layer_id === 'leonardo').length,0);
assert.deepEqual(h.query(bundle,preLeonardo).filter(item => item.layer_id === 'roman').map(item => item.interval),[{start:91,end:105}]);
for (const cursorYear of [105,106,113,114,116,117,1451,1452,1502,1519]) {
  const state = h.normalizeState(bundle,{...base,mode:'scrub',cursorYear});
  const result = h.query(bundle,state);
  assert.equal(state.cursorYear,cursorYear);
  assert(result.filter(item => item.layer_id === 'roman').every(item => item.interval.start <= cursorYear && item.interval.end >= cursorYear));
  assert(result.filter(item => item.layer_id === 'leonardo').every(item => cursorYear >= state.traceOriginYear && item.interval.start <= cursorYear && item.interval.end >= state.traceOriginYear));
}
const wide = h.normalizeState(bundle,{...base,startYear:91,endYear:1519,layers:['leonardo','roman','architecture']});
assert.equal(h.query(bundle,wide).length,45);
const features = h.featuresFor(bundle,h.query(bundle,wide));
const groups = h.placeGroups(bundle,h.query(bundle,wide));
assert.equal(groups.length,9);
assert.equal(groups.reduce((count,group) => count+group.presences.length,0),11);
assert.equal(groups.find(group => group.place_ref === 'place-florence').presences.length,2);
assert.equal(groups.find(group => group.place_ref === 'place-milan').presences.length,2);
const placeAnchors = features.features.filter(feature => feature.properties.kind === 'presence');
assert.equal(placeAnchors.length,9);
for (const group of groups) {
  const anchor = placeAnchors.find(feature => feature.properties.place_ref === group.place_ref);
  assert.deepEqual(anchor.geometry.coordinates,group.presences[0].coordinates);
  assert(group.presences.every(presence => JSON.stringify(presence.coordinates) === JSON.stringify(anchor.geometry.coordinates)));
  assert.equal(anchor.properties.episode_count,group.presences.length);
  assert.deepEqual(JSON.parse(anchor.properties.presence_item_ids),group.presences.map(presence => presence.presence_item_id));
  assert.equal(h.placeChoice(group,wide).presence_item_id,group.presences[0].presence_item_id);
  assert.equal(h.placeChoice(group,{...wide,mode:'scrub'}).presence_item_id,group.presences.at(-1).presence_item_id);
  for (const presence of group.presences) assert.equal(h.placeChoice(group,{...wide,selectedItemId:presence.presence_item_id}).presence_item_id,presence.presence_item_id);
}
const leo1502 = h.normalizeState(bundle,{...base,startYear:1502,endYear:1502});
assert.equal(h.placeGroups(bundle,h.query(bundle,leo1502)).length,4);
const cesena = bundle.leonardo.lifePath.presences.find(presence => presence.place_ref === 'place-cesena');
const emphasisState = h.normalizeState(bundle,{...base,mode:'scrub',cursorYear:1502,selectedItemId:cesena.presence_item_id});
const emphasis = h.presentationEmphasis(bundle,h.query(bundle,emphasisState),emphasisState);
assert.equal(emphasis.selectedPlace,'place-cesena');
assert.equal(emphasis.currentPlace,'place-imola');
assert.equal(emphasis.selectedPresence,cesena.presence_id);
assert(emphasis.transitions.some(transition => transition.emphasis === 2));
assert.equal(emphasis.transitions.filter(transition => transition.emphasis > 0).length,1);
const currentEmphasisState = {...emphasisState,selectedItemId:null};
assert(h.presentationEmphasis(bundle,h.query(bundle,currentEmphasisState),currentEmphasisState).transitions.some(transition => transition.emphasis === 1));
for (const cue of h.chronologyCues(bundle,h.query(bundle,wide),wide)) {
  assert.equal(cue.renderer_only,true); assert.equal(cue.route_geometry,null);
  assert.deepEqual(cue.midpoint,[(cue.coordinates[0][0]+cue.coordinates[1][0])/2,(cue.coordinates[0][1]+cue.coordinates[1][1])/2]);
}
assert.equal(h.presentationEmphasis(bundle,h.query(bundle,preLeonardo),preLeonardo).currentPlace,null);
const regions = features.features.filter(feature => feature.properties.kind === 'region');
assert.equal(regions.length,3);
assert.deepEqual(regions.map(feature => [feature.properties.native_start,feature.properties.native_end]),[[91,105],[106,113],[114,116]]);
for (let i=0;i<3;i++) assert.deepEqual(regions[i].geometry.coordinates,bundle.roman.versions[i].globe.primitives[0].coordinates);
assert.equal(features.features.filter(feature => feature.properties.kind === 'reference').length,31);
for (const reference of bundle.architecture.references) {
  assert.equal(reference.temporal_extent,null);
  assert.equal(reference.historical_applicability,'unknown');
  assert.deepEqual(features.features.find(feature => feature.id === reference.item_id).geometry,reference.raw_feature.geometry);
  assert.deepEqual(reference.claim_refs,[]);
  assert.deepEqual(reference.evidence_link_refs,[]);
}
assert(features.features.filter(feature => feature.properties.kind === 'chronology').every(feature => feature.properties.route_geometry === null));
assert.equal(bundle.leonardo.lifePath.route_policy.geometry,null);
const architecture100 = h.query(bundle,h.normalizeState(bundle,{...preLeonardo,layers:['architecture']}));
const architecture1502 = h.query(bundle,h.normalizeState(bundle,{...base,mode:'scrub',cursorYear:1502,layers:['architecture']}));
assert.deepEqual(ids(architecture100),ids(architecture1502));
assert.equal(architecture100.length,31);
assert(bundle.architecture.references.some(reference => String(reference.raw_feature.properties.date_start).startsWith('-')));

const presence = bundle.registry.find(item => item.layer_id === 'leonardo' && item.interval.start <= 1502 && item.interval.end >= 1502);
assert(presence);
const selected = h.normalizeState(bundle,{...base,mode:'scrub',cursorYear:1502,selectedItemId:presence.presence_id});
assert.equal(selected.selectedItemId,presence.item_id);
assert.equal(h.normalizeState(bundle,{...selected,layers:['leonardo','architecture']},selected).selectedItemId,presence.item_id);
assert.equal(h.normalizeState(bundle,{...selected,layers:['roman']},selected).selectedItemId,null);
assert.equal(h.normalizeState(bundle,{...selected,cursorYear:100},selected).selectedItemId,null);
assert.equal(h.resolveSelection(bundle,presence.event_item_id),presence.item_id);
assert.equal(h.resolveSelection(bundle,'invented-item'),null);
const reference = bundle.architecture.references[0];
assert.equal(h.resolveSelection(bundle,reference.original_id),reference.item_id);
for (const alias of reference.aliases) assert.equal(h.resolveSelection(bundle,alias),reference.item_id);

const origin = 'https://example.test/ARTEMIS/globe/?unknown=keep#saved';
const saved = {...selected,language:'ru',presentationView:'map',layers:['leonardo','roman','architecture'],camera:{center:[12.123456789123,43.234567891234],zoom:4.123456789,pitch:12.5123456789,bearing:-45.234567891}};
const savedUrl = h.stateUrl(origin,saved,bundle);
assert.equal(savedUrl.hash,'#saved');
assert.equal(savedUrl.searchParams.get('unknown'),'keep');
assert.deepEqual(h.parseUrl(bundle,savedUrl.href),saved);
// Each recorded workspace URL retains the inactive Scrub cursor during Range.
const rangeAfterScrub = {...saved,mode:'range',startYear:91,endYear:1519};
const nextUrl = h.stateUrl(savedUrl.href,rangeAfterScrub,bundle);
assert.deepEqual(h.parseUrl(bundle,nextUrl.href),rangeAfterScrub);
assert.deepEqual(h.parseUrl(bundle,savedUrl.href),saved); // Back
assert.deepEqual(h.parseUrl(bundle,nextUrl.href),rangeAfterScrub); // Forward
const legacyPresence = h.parseUrl(bundle,`https://example.test/globe/?mode=scrub&from=1452&at=1502&presence=${encodeURIComponent(presence.presence_id)}&lang=ru&view=map`);
assert.equal(legacyPresence.selectedItemId,presence.item_id);
const version = bundle.roman.versions[1];
const legacyRoman = h.parseUrl(bundle,`https://example.test/region/?time=${version.preset_id}&item=${encodeURIComponent(version.item_id)}&layers=layer-political-territory`,'region');
assert.equal(legacyRoman.selectedItemId,version.item_id);
assert.equal(legacyRoman.startYear,106); assert.equal(legacyRoman.endYear,113);
for (const malformed of ['mode=wrong&start=NaN&end=-3000&at=2000&from=-9&layers=unknown&item=fake&lang=RU&view=MAP','center=,&zoom=Infinity&pitch=-1&bearing=900']) {
  const state = h.parseUrl(bundle,`https://example.test/globe/?${malformed}`);
  assert.equal(state.mode,'range'); assert.equal(state.startYear,1452); assert.equal(state.endYear,1519); assert.equal(state.cursorYear,1519); assert.equal(state.traceOriginYear,1452);
  assert.equal(state.selectedItemId,null); assert.equal(state.language,'en'); assert.equal(state.presentationView,'globe'); assert.deepEqual(state.camera,base.camera);
}
assert.deepEqual(h.query(bundle,h.normalizeState(bundle,{...wide,layers:[]})),[]);
const reversed = h.normalizeState(bundle,{...base,startYear:1519,endYear:100});
assert.equal(reversed.startYear,100); assert.equal(reversed.endYear,1519);
assert.equal(digest(),before); // Query, URL, selection and renderer construction never mutate input.
assert(Object.isFrozen(bundle.architecture.references[0].raw_feature));
console.log('Unified Explorer actual-bundle query, geometry, selection, URL/history and negative cases PASS');
