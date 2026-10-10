'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const h = require('../scripts/unified_explorer/runtime.js');
if (!process.argv[2]) throw Error('Pass the actual composed source bundle as a fixture');
const bundle = h.freeze(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
const digest = () => crypto.createHash('sha256').update(JSON.stringify(bundle)).digest('hex');
const before = digest();
// A burst uses the newest event once; an event from inside the callback is
// retained for the next frame instead of being dropped.
const frames = [], events = [];
const throttled = h.frameThrottle(value => { events.push(value); if (value === 3) throttled(4); },callback => frames.push(callback));
throttled(1); throttled(2); throttled(3);
assert.equal(frames.length,1); frames.shift()();
assert.deepEqual(events,[3]); assert.equal(frames.length,1); frames.shift()();
assert.deepEqual(events,[3,4]); assert.equal(frames.length,0);
const ids = result => result.map(item => item.item_id);
const base = h.defaults('globe');
assert.equal(bundle.registry.length,55);
assert.equal(h.query(bundle,base).length,21);
assert.equal(h.query(bundle,h.defaults('region')).length,11);
// Catalog extends the same frozen registry; its point is source-relative and
// explicitly atemporal, never an assertion of historical existence.
assert.deepEqual(base.layers,['leonardo','roman','catalog']);
const catalog = bundle.catalog.references;
assert.equal(catalog.length,10);
const catalogEarly = h.query(bundle,h.normalizeState(bundle,{...base,mode:'scrub',cursorYear:100,layers:['catalog']}));
const catalogLate = h.query(bundle,h.normalizeState(bundle,{...base,mode:'scrub',cursorYear:1519,layers:['catalog']}));
assert.deepEqual(ids(catalogEarly),ids(catalogLate));
assert.equal(catalogEarly.length,10);
for (const reference of catalog) {
  assert.equal(reference.temporal_extent,null);
  assert.equal(reference.historical_position,null);
  assert.equal(reference.historical_applicability,'unknown');
  const item = bundle.registry.find(item => item.item_id === reference.item_id);
  assert.equal(item.interval,null);
  const feature = h.featuresFor(bundle,[item]).features[0];
  assert.deepEqual(feature.geometry,reference.geometry);
  assert.equal(feature.properties.kind,'catalog_reference');
  assert.equal(feature.id,`catalog:wikidata:${reference.qid}`);
  const selectedCatalog = h.normalizeState(bundle,{...base,selectedItemId:item.item_id});
  assert.equal(selectedCatalog.selectedItemId,item.item_id);
  assert.equal(h.normalizeState(bundle,{...selectedCatalog,layers:['leonardo','roman']},selectedCatalog).selectedItemId,null);
  assert.equal(h.parseUrl(bundle,h.stateUrl('https://example.test/globe/',selectedCatalog,bundle)).selectedItemId,item.item_id);
  assert(h.chooserItems(bundle,catalogEarly,reference.qid.toLowerCase()).some(result => result.item_id === item.item_id));
  for (const label of Object.values(reference.labels)) assert(h.chooserItems(bundle,catalogEarly,label.normalize('NFD')).some(result => result.item_id === item.item_id));
  for (const alias of Object.values(reference.aliases).flat()) assert(h.chooserItems(bundle,catalogEarly,alias).some(result => result.item_id === item.item_id));
}
assert.deepEqual(h.parseUrl(bundle,'https://example.test/globe/?layers=leonardo,roman').layers,['leonardo','roman']);
assert.deepEqual(h.parseUrl(bundle,'https://example.test/region/?layers=catalog','region').layers,['catalog']);
assert.deepEqual(h.chooserItems(bundle,catalogEarly,'   '),catalogEarly);
assert.deepEqual(h.chooserItems(bundle,catalogEarly,'no-such-record-xyz'),[]);
const beforeSearchState = {...base,selectedItemId:catalog[0].item_id};
h.chooserItems(bundle,h.query(bundle,beforeSearchState),'no-such-record-xyz');
assert.equal(beforeSearchState.selectedItemId,catalog[0].item_id);
assert.deepEqual(beforeSearchState.camera,base.camera);
assert.equal(h.recordLabel({kind:'catalog_reference',labels:{en:'Native English'},label:'Native English'},'ru'),'Native English (en)');
assert.equal(h.recordLabel({kind:'catalog_reference',labels:{ru:'Исходное название',en:'Name'},label:'Name'},'ru'),'Исходное название');
assert.equal(h.searchKey('ＡＢＣ'),h.searchKey('abc'));
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
const renderKeys = features.features.map(feature => feature.properties.render_key);
assert.equal(new Set(renderKeys).size,features.features.length);
assert(features.features.every(feature => typeof feature.id === 'string' && feature.properties.render_key === feature.id));
assert.deepEqual([...new Set(features.features.map(feature => feature.properties.kind))].sort(),['chronology','presence','reference','region']);
for (const reference of bundle.architecture.references) {
  const feature = features.features.find(item => item.id === reference.item_id);
  assert.equal(feature.properties.item_id,reference.item_id);
  assert.equal(feature.properties.render_key,reference.item_id);
  assert.deepEqual(feature.geometry,reference.raw_feature.geometry);
}
for (const version of bundle.roman.versions) for (const primitive of version.globe.primitives.filter(item => item.item_id === version.item_id)) {
  const feature = features.features.find(item => item.id === primitive.primitive_id);
  assert.equal(feature.properties.item_id,version.item_id);
  assert.equal(feature.properties.geometry_ref,primitive.geometry_ref || version.geometry_version.id);
  assert.deepEqual(feature.geometry.coordinates,primitive.coordinates);
}
for (const transition of bundle.leonardo.lifePath.transitions) {
  const feature = features.features.find(item => item.id === transition.transition_id);
  if (feature) assert.equal(feature.properties.route_geometry,null);
}
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

// Summary/details visibility is local and preserves canonical identity, URL and data.
const presentation = h.selectionPresentation();
const chosen = bundle.registry.find(row => row.kind === 'catalog_reference');
assert.deepEqual(presentation.sync(chosen.item_id),{itemId:chosen.item_id,details:false});
presentation.open(); assert.equal(presentation.sync(chosen.item_id).details,true);
presentation.summary(); assert.equal(presentation.sync(chosen.item_id).details,false);
presentation.open(); assert.equal(presentation.sync('another-item').details,false);
assert.deepEqual(presentation.sync(null),{itemId:null,details:false});
presentation.open(); assert.equal(presentation.sync(null).details,false);
for (const item of bundle.registry) {
  const anchor = h.summaryAnchor(bundle,item);
  if (item.kind === 'region') assert.equal(anchor,null);
  else {
    const point = h.featuresFor(bundle,[item]).features.find(row => row.geometry.type === 'Point');
    assert.deepEqual(anchor,point.geometry.coordinates);
  }
}
assert.equal(digest(),before);
