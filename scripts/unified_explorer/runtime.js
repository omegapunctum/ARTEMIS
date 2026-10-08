(() => {
  'use strict';
  const LAYERS = ['leonardo', 'roman', 'architecture', 'catalog'];
  const MIN = 91, MAX = 1519;
  const words = {
    en: {preview:'Public research prototype · user value unvalidated',globe:'Globe',map:'2D map',layers:'Layers',leonardo:'Leonardo',roman:'Roman Empire',architecture:'Architecture references',eleven:'11 selected presences',three:'3 reconstructions',atemporal:'Atemporal · historical applicability unknown',visible:'Visible records',choose:'Choose a record',focus:'Focus map on this record',evidence:'Claims, evidence and uncertainty',raw:'Source-native input and provenance',range:'Range',scrub:'Scrub',from:'From',to:'To',cursor:'Current year CE',routes:'Leonardo chronology is not a travel route; exact routes and historical positions remain unknown.',sources:'Sources',none:'outside dated coverage / no matching record',off:'off',unknown:'Unknown',interval:'Interval collection; records may come from different eras, not simultaneous context.',trace:'Leonardo accumulates from',reference:'Atemporal imported reference. Historical applicability, lifetime and historical position are unknown.',reconstruction:'Approximate scholarly reconstruction; not exact historical borders.',presence:'Source-bounded documented presence; exact historical position and routes unknown.',sourceScope:'Source links do not mean historical claims have been verified. Other historical sources may exist; no reliability score is assigned.',legacy:'Raw export flags are metadata, not historical acceptance or geometry precision.',context:'Present-day reference context; not historical terrain.',error:'Could not complete the view change. The controls show the current view; try again.'},
    ru: {preview:'Публичный исследовательский прототип · пользовательская ценность не подтверждена',globe:'Глобус',map:'Карта 2D',layers:'Слои',leonardo:'Леонардо',roman:'Римская империя',architecture:'Архитектурные объекты',eleven:'11 выбранных присутствий',three:'3 реконструкции',atemporal:'Вне времени · историческая применимость неизвестна',visible:'Видимые записи',choose:'Выберите запись',focus:'Фокусировать карту на записи',evidence:'Утверждения, доказательства и неопределённость',raw:'Исходные данные и происхождение',range:'Интервал',scrub:'Курсор',from:'От',to:'До',cursor:'Текущий год н. э.',routes:'Хронология Леонардо не является маршрутом; точные маршруты и исторические положения неизвестны.',sources:'Источники',none:'вне временного покрытия / нет подходящих записей',off:'выключен',unknown:'Неизвестно',interval:'Коллекция интервала: записи могут относиться к разным эпохам, а не одновременному контексту.',trace:'След Леонардо накапливается с',reference:'Импортированная опорная запись вне времени. Историческая применимость, время существования и историческое положение неизвестны.',reconstruction:'Приблизительная научная реконструкция; не точные исторические границы.',presence:'Документированное присутствие в пределах источников; точное историческое положение и маршруты неизвестны.',sourceScope:'Связь с источником не означает проверенность исторических утверждений. Могут существовать другие источники; рейтинг достоверности не назначается.',legacy:'Флаги исходного экспорта — метаданные, а не историческое принятие или точность геометрии.',error:'Не удалось завершить смену вида. Кнопки показывают текущий вид; попробуйте снова.'}
  };
  Object.assign(words.en,{catalog:'London architecture catalog',catalogPilot:'Selected pilot · 10 objects · London',catalogReference:'Modern reference point. Historical position and lifetime are unknown.',catalogUnverified:'Imported from Wikidata; independent verification has not been performed.',search:'Search names or QID',clearSearch:'Clear search',searchEmpty:'No matching visible records. Clear search or enable another layer.',searchCount:'Matching visible records',coordinate:'Reported longitude / latitude',precision:'Source numeric precision (degrees)',precisionLimit:'Numeric precision is not measurement accuracy. Site extent and historical applicability are unknown.',revision:'Wikidata source revision',wikipedia:'Wikipedia context',searchHint:'Search filters this chooser only; the map and open record remain unchanged.'});
  Object.assign(words.ru,{catalog:'Каталог архитектуры Лондона',catalogPilot:'Пилотный каталог · 10 объектов · Лондон',catalogReference:'Современная опорная точка. Историческое положение и период существования не установлены.',catalogUnverified:'Импортировано из Wikidata; независимая проверка не выполнена.',search:'Поиск по названию или QID',clearSearch:'Очистить поиск',searchEmpty:'Нет подходящих видимых записей. Очистите поиск или включите другой слой.',searchCount:'Найдено видимых записей',coordinate:'Указанные долгота / широта',precision:'Численная точность в источнике (градусы)',precisionLimit:'Численная точность не означает точность измерения. Размер объекта и историческая применимость неизвестны.',revision:'Версия источника Wikidata',wikipedia:'Контекст в Wikipedia',searchHint:'Поиск фильтрует только список; карта и открытая запись остаются прежними.'});
  const year = (value, fallback) => /^\d{1,4}$/.test(String(value ?? '')) && Number(value) >= MIN && Number(value) <= MAX ? Number(value) : fallback;
  const clone = value => JSON.parse(JSON.stringify(value));
  function freeze(value) { if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.freeze(value); for (const item of Object.values(value)) freeze(item); } return value; }
  // Process the latest event once per frame; events arriving inside a callback
  // still schedule the next frame rather than being lost.
  function frameThrottle(callback, requestFrame = requestAnimationFrame) {
    let pending = false, latest;
    return (...args) => { latest = args; if (pending) return; pending = true; requestFrame(() => { pending = false; callback(...latest); }); };
  }
  function defaults(profile = 'globe') { return {mode:'range',startYear:profile === 'region' ? 91 : 1452,endYear:profile === 'region' ? 105 : 1519,cursorYear:profile === 'region' ? 100 : 1519,traceOriginYear:1452,layers:['leonardo','roman','catalog'],selectedItemId:null,language:'en',presentationView:'globe',camera:{center:[10,15],zoom:.8,pitch:0,bearing:0}}; }
  function query(bundle, state) {
    const overlap = (interval, start, end) => interval && interval.start <= end && interval.end >= start;
    return Object.freeze(bundle.registry.filter(item => {
      if (!state.layers.includes(item.layer_id)) return false;
      if (item.layer_id === 'architecture' || item.layer_id === 'catalog') return true;
      if (state.mode === 'range') return overlap(item.interval, state.startYear, state.endYear);
      if (item.layer_id === 'roman') return overlap(item.interval, state.cursorYear, state.cursorYear);
      return state.cursorYear >= state.traceOriginYear && overlap(item.interval, state.traceOriginYear, state.cursorYear);
    }));
  }
  function resolveSelection(bundle, value) {
    return bundle.registry.find(item => item.item_id === value || item.presence_id === value || item.event_item_id === value || item.original_id === value || (Array.isArray(item.aliases) && item.aliases.includes(value)))?.item_id || null;
  }
  function normalizeState(bundle, input, fallback = defaults()) {
    const state = {...clone(fallback),...clone(input)};
    state.mode = state.mode === 'scrub' ? 'scrub' : 'range';
    state.startYear = year(state.startYear, fallback.startYear); state.endYear = year(state.endYear, fallback.endYear);
    if (state.startYear > state.endYear) [state.startYear,state.endYear] = [state.endYear,state.startYear];
    state.cursorYear = year(state.cursorYear, fallback.cursorYear);
    state.traceOriginYear = year(state.traceOriginYear,1452); if (state.traceOriginYear < 1452) state.traceOriginYear = 1452;
    state.layers = Array.isArray(state.layers) ? LAYERS.filter(layer => state.layers.includes(layer)) : [...fallback.layers];
    state.language = state.language === 'ru' ? 'ru' : 'en'; state.presentationView = state.presentationView === 'map' ? 'map' : 'globe';
    const camera = state.camera || {}, finite = (value,min,max,other) => typeof value === 'number' && Number.isFinite(value) && value >= min && value <= max ? value : other;
    state.camera = {center:[finite(camera.center?.[0],-180,180,fallback.camera.center[0]),finite(camera.center?.[1],-90,90,fallback.camera.center[1])],zoom:finite(camera.zoom,0,20,fallback.camera.zoom),pitch:finite(camera.pitch,0,85,fallback.camera.pitch),bearing:finite(camera.bearing,-180,180,fallback.camera.bearing)};
    state.selectedItemId = resolveSelection(bundle,state.selectedItemId);
    if (!query(bundle,state).some(item => item.item_id === state.selectedItemId)) state.selectedItemId = null;
    return state;
  }
  function parseUrl(bundle, href, profile = 'globe') {
    const params = new URL(href).searchParams, base = defaults(profile), requested = {};
    requested.mode = params.get('mode') || 'range';
    requested.startYear = year(params.get('start'),base.startYear); requested.endYear = year(params.get('end'),base.endYear);
    requested.cursorYear = year(params.get('at'),base.cursorYear); requested.traceOriginYear = year(params.get('from'),1452);
    if (params.has('layers')) {
      const layers = params.get('layers').split(',');
      // Existing isolated semantic layer IDs are translated by their entry profile.
      requested.layers = layers.every(value => LAYERS.includes(value)) || !params.get('layers') ? layers : base.layers;
    }
    const preset = bundle.roman.versions.find(version => version.preset_id === params.get('time'));
    if (preset) { requested.mode = 'range'; requested.startYear = preset.interval.start; requested.endYear = preset.interval.end; }
    requested.selectedItemId = params.get('presence') || params.get('item');
    requested.language = params.get('lang'); requested.presentationView = params.get('view');
    const centerParts = params.get('center')?.split(','), center = centerParts?.map(Number);
    if (center?.length === 2 && center.every(Number.isFinite) && centerParts.every(part => part.trim() !== '')) requested.camera = {...base.camera,center};
    for (const key of ['zoom','pitch','bearing']) if (params.has(key) && params.get(key).trim() !== '') { requested.camera ||= clone(base.camera); requested.camera[key] = Number(params.get(key)); }
    return normalizeState(bundle,requested,base);
  }
  function stateUrl(href, state, bundle) {
    const url = new URL(href), params = url.searchParams;
    for (const key of ['time','stop','presence','item','mode','start','end','from','at','layers','lang','view','center','zoom','pitch','bearing']) params.delete(key);
    params.set('mode',state.mode); params.set('start',state.startYear); params.set('end',state.endYear);
    params.set('from',state.traceOriginYear); params.set('at',state.cursorYear);
    params.set('layers',state.layers.join(',')); params.set('lang',state.language); params.set('view',state.presentationView);
    if (state.selectedItemId) { params.set('item',state.selectedItemId); const selected = bundle.registry.find(item => item.item_id === state.selectedItemId); if (selected?.presence_id) params.set('presence',selected.presence_id); }
    // Renderer-local camera values round-trip exactly; these are not historical coordinates.
    params.set('center',state.camera.center.join(','));
    for (const key of ['zoom','pitch','bearing']) params.set(key,state.camera[key]);
    return url;
  }
  // Application WorkspaceState coordinates native inputs. It is not a migrated
  // canonical ExplorerState v1 and does not rewrite the retained input states.
  function placeGroups(bundle, items) {
    const visible = new Set(items.filter(item => item.kind === 'presence').map(item => item.item_id)), groups = new Map();
    for (const presence of bundle.leonardo.lifePath.presences) {
      if (!visible.has(presence.presence_item_id)) continue;
      if (!groups.has(presence.place_ref)) groups.set(presence.place_ref,{place_ref:presence.place_ref,label:presence.place_label,coordinates:presence.coordinates,presences:[]});
      groups.get(presence.place_ref).presences.push(presence);
    }
    return freeze([...groups.values()].map(group => ({...group,presences:group.presences.sort((a,b) => a.index-b.index)})));
  }
  function placeChoice(group, state) {
    return group.presences.find(item => item.presence_item_id === state.selectedItemId)
      || (state.mode === 'scrub' ? group.presences.at(-1) : group.presences[0]);
  }
  function presentationEmphasis(bundle, items, state) {
    const visible = new Set(items.map(item => item.item_id));
    const presences = bundle.leonardo.lifePath.presences.filter(item => visible.has(item.presence_item_id)).sort((a,b) => a.index-b.index);
    const selected = presences.find(item => item.presence_item_id === state.selectedItemId), current = state.mode === 'scrub' ? presences.at(-1) : null;
    const episode = selected || current;
    const incoming = episode && bundle.leonardo.lifePath.transitions.find(transition => transition.to_presence_ref === episode.presence_id && presences.some(presence => presence.presence_id === transition.from_presence_ref));
    return freeze({selectedPresence:selected?.presence_id || null,currentPresence:current?.presence_id || null,selectedPlace:selected?.place_ref || null,currentPlace:current?.place_ref || null,transitions:bundle.leonardo.lifePath.transitions.map(transition => ({id:transition.transition_id,emphasis:episode && (incoming ? transition === incoming : transition.from_presence_ref === episode.presence_id) ? selected ? 2 : 1 : 0}))});
  }
  function featuresFor(bundle, items) {
    const features = [], visible = new Set(items.map(item => item.item_id));
    for (const group of placeGroups(bundle,items)) if (group.coordinates) features.push({type:'Feature',id:`place-anchor:${group.place_ref}`,geometry:{type:'Point',coordinates:group.coordinates},properties:{item_id:group.presences[0].presence_item_id,place_ref:group.place_ref,layer_id:'leonardo',kind:'presence',episode_count:group.presences.length,presence_item_ids:JSON.stringify(group.presences.map(item => item.presence_item_id))}});
    for (const item of items) {
      if (item.kind === 'presence') {
        continue; // One fixed Place anchor; all Presence identities remain selectable.
      } else if (item.kind === 'reference' || item.kind === 'catalog_reference') {
        const reference = (item.kind === 'reference' ? bundle.architecture : bundle.catalog).references.find(value => value.item_id === item.item_id);
        features.push({type:'Feature',id:item.item_id,geometry:reference.geometry,properties:{item_id:item.item_id,layer_id:item.layer_id,kind:item.kind}});
      } else {
        const version = bundle.roman.versions.find(value => value.item_id === item.item_id);
        for (const primitive of version.globe.primitives) {
          if (primitive.item_id !== item.item_id) continue;
          const type = {cartographic_polygon:'Polygon',cartographic_multipolygon:'MultiPolygon',point_anchor:'Point',cartographic_line:'LineString'}[primitive.primitive_kind];
          if (!type) throw Error(`Unsupported native primitive: ${primitive.primitive_kind}`);
          features.push({type:'Feature',id:primitive.primitive_id,geometry:{type,coordinates:primitive.coordinates},properties:{item_id:item.item_id,layer_id:item.layer_id,kind:item.kind,geometry_ref:primitive.geometry_ref || item.geometry_version_ref,native_start:item.interval.start,native_end:item.interval.end}});
        }
      }
    }
    if (bundle.leonardo.lifePath.route_policy?.chronological_connector_permitted === true) {
      const presences = new Map(bundle.leonardo.lifePath.presences.map(item => [item.presence_id,item]));
      for (const transition of bundle.leonardo.lifePath.transitions) {
        const from = presences.get(transition.from_presence_ref), to = presences.get(transition.to_presence_ref);
        if (from && to && visible.has(from.presence_item_id) && visible.has(to.presence_item_id) && from.coordinates && to.coordinates) features.push({type:'Feature',id:transition.transition_id,geometry:{type:'LineString',coordinates:[from.coordinates,to.coordinates]},properties:{kind:'chronology',layer_id:'leonardo',route_geometry:null}});
      }
    }
    // Technical renderer key binds native tile IDs to presentation feature state.
    // Native input/item IDs and geometry are retained; source objects are not mutated.
    return {type:'FeatureCollection',features:features.map(feature => ({...feature,properties:{...feature.properties,render_key:feature.id}}))};
  }
  function chronologyCues(bundle,items,state) {
    const emphasis = presentationEmphasis(bundle,items,state);
    return freeze(featuresFor(bundle,items).features.filter(feature => feature.properties.kind === 'chronology').filter(feature => JSON.stringify(feature.geometry.coordinates[0]) !== JSON.stringify(feature.geometry.coordinates[1])).map(feature => ({id:feature.id,coordinates:feature.geometry.coordinates,midpoint:[(feature.geometry.coordinates[0][0]+feature.geometry.coordinates[1][0])/2,(feature.geometry.coordinates[0][1]+feature.geometry.coordinates[1][1])/2],emphasis:emphasis.transitions.find(transition => transition.id === feature.id)?.emphasis || 0,renderer_only:true,route_geometry:null})));
  }
  function recordLabel(item, language) {
    if (item.kind !== 'catalog_reference') return item.label;
    const labels = item.labels || {}, preferred = labels[language];
    if (preferred) return preferred;
    const fallback = labels.en ? 'en' : Object.keys(labels).sort()[0];
    return fallback ? `${labels[fallback]} (${fallback})` : item.label;
  }
  function searchKey(value) { return String(value ?? '').normalize('NFKC').toLocaleLowerCase('und'); }
  function chooserItems(bundle, items, search) {
    const needle = searchKey(search).trim(); if (!needle) return items;
    return items.filter(item => {
      const original = item.kind === 'reference' ? bundle.architecture.references.find(value => value.item_id === item.item_id)?.raw_feature.properties : null;
      const aliases = Array.isArray(item.aliases) ? item.aliases : Object.values(item.aliases || {}).flat();
      return [item.label,item.qid,...Object.values(item.labels || {}),...aliases,original?.name_en,original?.name_ru].some(value => searchKey(value).includes(needle));
    });
  }
  const helpers = Object.freeze({recordLabel,searchKey,chooserItems,defaults,query,resolveSelection,normalizeState,parseUrl,stateUrl,featuresFor,placeGroups,placeChoice,presentationEmphasis,chronologyCues,freeze,frameThrottle});
  if (typeof module !== 'undefined' && module.exports) module.exports = helpers;
  if (typeof document === 'undefined') return;
  const runtime = {bundle:null,state:null,registry:null,visibleItems:[],map:null,ready:false,meta:null,placeMarkers:new Map(),chronologyMarkers:new Map(),search:''};
  window.__ARTEMIS_EXPLORER = Object.freeze({get bundle(){return runtime.bundle;},get state(){return runtime.state;},get registry(){return runtime.bundle?.registry;},get visibleItems(){return runtime.visibleItems;},get placeGroups(){return runtime.bundle ? placeGroups(runtime.bundle,runtime.visibleItems) : [];},get map(){return runtime.map;},get ready(){return runtime.ready;},get meta(){return runtime.meta;},query:state => query(runtime.bundle,state || runtime.state)});
  const byId = id => document.getElementById(id), text = (id,value) => { byId(id).textContent = value; }, t = key => words[runtime.state?.language || 'en'][key] || key;
  let renderedSelection = null, restoringCamera = false, recordSignature = '';
  function node(tag, value, className = '') { const element = document.createElement(tag); element.textContent = value ?? ''; if (className) element.className = className; return element; }
  const pendingJson = new WeakMap(), boundDisclosures = new WeakSet();
  function inputJson(host,value) {
    const pre = node('pre',''), disclosure = host.closest('details'); host.append(pre);
    if (!disclosure || disclosure.open) { pre.textContent = JSON.stringify(value,null,2); return; }
    // Keep the source value intact; formatting a large native Region input is
    // needed only when the user opens this disclosure.
    pre.dataset.jsonPending = 'true'; pendingJson.set(pre,value);
    if (!boundDisclosures.has(disclosure)) {
      boundDisclosures.add(disclosure);
      disclosure.addEventListener('toggle',() => { if (!disclosure.open) return; for (const target of disclosure.querySelectorAll('pre[data-json-pending]')) { target.textContent = JSON.stringify(pendingJson.get(target),null,2); pendingJson.delete(target); delete target.dataset.jsonPending; } });
    }
  }
  function safeLink(value) { try { const url = new URL(value,location.href); return ['https:','http:'].includes(url.protocol) ? url.href : null; } catch (_) { return null; } }
  function layout() { const style = document.documentElement.style; style.setProperty('--header-bottom',`${Math.ceil(byId('workspace-header').getBoundingClientRect().bottom)}px`); style.setProperty('--dock-height',`${Math.ceil(byId('time-dock').getBoundingClientRect().height)}px`); style.setProperty('--attribution-height',`${Math.ceil(byId('attribution').getBoundingClientRect().height)}px`); }
  function history(mode = 'push') { window.history[mode === 'replace' ? 'replaceState' : 'pushState']({artemisExplorer:true},'',stateUrl(location.href,runtime.state,runtime.bundle)); }
  function sourceRecord(item) {
    const bundle = runtime.bundle;
    if (item.kind === 'reference') return bundle.architecture.references.find(value => value.item_id === item.item_id);
    if (item.kind === 'catalog_reference') return bundle.catalog.references.find(value => value.item_id === item.item_id);
    if (item.kind === 'region') return {version:bundle.roman.versions.find(value => value.item_id === item.item_id),record:bundle.roman.knowledge.records.find(value => value.item_id === item.item_id)};
    const presence = bundle.leonardo.lifePath.presences.find(value => value.presence_item_id === item.item_id);
    const record = bundle.leonardo.knowledge.records.find(value => value.item_id === presence.event_item_id) || presence;
    return {presence,record};
  }
  function sourcesFor(input) { return input.sources || input.record?.sources || input.presence?.sources || []; }
  function renderEpisodeChoices(selected) {
    const host = byId('place-episodes'), group = selected?.kind === 'presence' ? placeGroups(runtime.bundle,runtime.visibleItems).find(value => value.presences.some(presence => presence.presence_item_id === selected.item_id)) : null;
    host.hidden = !group || group.presences.length < 2;
    if (host.hidden) { host.replaceChildren(); return; }
    const signature = `${runtime.state.language}|${selected.item_id}|${group.presences.map(item => item.presence_item_id).join('|')}`;
    if (host.dataset.signature === signature) return;
    host.dataset.signature = signature; host.replaceChildren(node('span',runtime.state.language === 'ru' ? 'Видимые присутствия в этом месте' : 'Visible presences at this place'));
    for (const presence of group.presences) {
      const button = node('button',presence.temporal.source_native?.length < 25 ? presence.temporal.source_native : `${presence.temporal.start} — ${presence.temporal.end}`);
      button.type = 'button'; button.dataset.presenceItemId = presence.presence_item_id; button.setAttribute('aria-pressed',String(presence.presence_item_id === selected.item_id));
      button.addEventListener('click',() => selectItem(presence.presence_item_id)); host.append(button);
    }
  }
  function renderInspector() {
    const selected = runtime.registry.get(runtime.state.selectedItemId), inspector = byId('inspector');
    if (!selected) { inspector.hidden = true; renderedSelection = null; renderEpisodeChoices(null); return; }
    inspector.hidden = false;
    // Layer/time/projection changes that retain this item preserve native disclosures.
    if (renderedSelection === selected.item_id) { renderInspectorLanguage(selected); renderEpisodeChoices(selected); return; }
    renderedSelection = selected.item_id; inspector.scrollTop = 0;
    inspector.dataset.itemId = selected.item_id;
    for (const id of ['selection-facts','selection-sources','selection-evidence','selection-input']) byId(id).replaceChildren();
    for (const id of ['sources-disclosure','evidence-disclosure','input-disclosure']) byId(id).open = false;
    const input = sourceRecord(selected), facts = byId('selection-facts');
    if (selected.kind === 'catalog_reference') {
      renderCatalogFacts(input);
      inputJson(byId('selection-evidence'),{claims:input.claims,evidence_links:input.evidence_links,uncertainties:input.uncertainties,historical_position:input.historical_position,historical_applicability:input.historical_applicability});
    } else if (selected.kind === 'reference') {
      const raw = input.raw_feature.properties;
      const list = node('dl','');
      for (const [key,value] of [['date_start',raw.date_start],['date_construction_end',raw.date_construction_end],['date_end',raw.date_end],['original_id',input.original_id],['historical_applicability','unknown'],['historical_position','unknown'],['historical_precision','unknown']]) { list.append(node('dt',key),node('dd',value == null ? 'null / unknown' : String(value))); }
      const legacy = node('p',t('legacy')); legacy.dataset.i18n = 'legacy'; facts.append(list,legacy);
      inputJson(byId('selection-evidence'),{claim_refs:input.claim_refs,evidence_link_refs:input.evidence_link_refs,historical_applicability:input.historical_applicability,legacy_export_flags:{validated:raw.validated,date_valid:raw.date_valid,coordinates_confidence:raw.coordinates_confidence,coordinates_source:raw.coordinates_source}});
    } else if (selected.kind === 'presence') {
      facts.append(node('p',input.presence.temporal.source_native || `${input.presence.temporal.start} — ${input.presence.temporal.end}`),node('p',input.presence.short_description || ''),node('p',input.presence.duration_status));
      inputJson(byId('selection-evidence'),{claims:input.record.claims || [],evidence_links:input.record.evidence_links || [],uncertainties:input.record.uncertainties || [],route_geometry:null,spatial_precision:input.presence.spatial_precision});
    } else {
      facts.append(node('p',`${selected.interval.start}–${selected.interval.end} CE`),node('p',selected.geometry_version_ref));
      inputJson(byId('selection-evidence'),{claims:input.record?.claims || [],evidence_links:input.record?.evidence_links || [],uncertainties:input.record?.uncertainties || [],native_temporal_extent:input.version.geometry_version.temporal_extent});
    }
    const sourceHost = byId('selection-sources'), sourceScope = node('p',t('sourceScope')); sourceScope.dataset.i18n = 'sourceScope'; sourceHost.append(sourceScope);
    for (const source of sourcesFor(input)) {
      const entry = node('article','', 'source-entry'); entry.append(node('strong',source.title || source.source_id || source.id));
      const locator = source.url || source.source_url || source.uri || source.artifact_uri, href = safeLink(locator);
      if (href) { const link = node('a',locator); link.href = href; link.target = '_blank'; link.rel = 'noopener noreferrer'; const paragraph = node('p',''); paragraph.append(link); entry.append(paragraph); }
      inputJson(entry,source); sourceHost.append(entry);
    }
    if (selected.kind === 'region') { sourceHost.append(node('p','Cliopatria · CC-BY-4.0')); const link = node('a','Source manifest · provenance & license'); link.href = './source_manifest.json'; sourceHost.append(link); inputJson(sourceHost,runtime.bundle.roman.sourceManifest); }
    inputJson(byId('selection-input'),{registry:selected,source_native_input:input,input_ledger:runtime.bundle.input_ledger});
    renderInspectorLanguage(selected); renderEpisodeChoices(selected); layout();
  }
  function renderCatalogFacts(input) {
    const facts = byId('selection-facts'); facts.replaceChildren(node('p',t('catalogUnverified')));
    const coordinateValue = input.coordinate_statement?.mainsnak?.datavalue?.value || {}, list = node('dl','');
    for (const [key,displayValue] of [[t('coordinate'),`${input.geometry.coordinates[0]} / ${input.geometry.coordinates[1]}`],[t('precision'),coordinateValue.precision ?? t('unknown')],['Wikidata',input.qid]]) list.append(node('dt',key),node('dd',String(displayValue)));
    facts.append(list,node('p',t('precisionLimit')));
    const source = input.sources[0], link = node('a',`${t('revision')} · ${source.revision}`); link.id = 'catalog-revision-link'; link.href = safeLink(source.url); link.target = '_blank'; link.rel = 'noopener noreferrer';
    const paragraph = node('p',''); paragraph.append(link); facts.append(paragraph,node('p',source.license));
    const urls = input.wikipedia_urls || {}, language = urls[runtime.state.language] ? runtime.state.language : urls.en ? 'en' : Object.keys(urls).sort()[0];
    if (language && safeLink(urls[language])) { const context = node('a',`${t('wikipedia')} (${language})`); context.id = 'catalog-context-link'; context.href = safeLink(urls[language]); context.target = '_blank'; context.rel = 'noopener noreferrer'; const p = node('p',''); p.append(context); facts.append(p); }
  }
  function renderInspectorLanguage(selected) {
    const input = sourceRecord(selected); text('selection-title',selected.kind === 'reference' ? input.raw_feature.properties[`name_${runtime.state.language}`] || selected.label : recordLabel(selected,runtime.state.language));
    text('selection-scope',t(selected.kind === 'catalog_reference' ? 'catalogReference' : selected.kind === 'reference' ? 'reference' : selected.kind === 'region' ? 'reconstruction' : 'presence'));
    text('sources-summary',`${t('sources')} · ${sourcesFor(input).length}`);
    if (selected.kind === 'catalog_reference') renderCatalogFacts(input);
  }
  function renderControls() {
    const state = runtime.state; document.documentElement.lang = state.language;
    for (const element of document.querySelectorAll('[data-i18n]')) element.textContent = t(element.dataset.i18n);
    for (const value of ['globe','map']) { byId(`view-${value}`).disabled = !runtime.ready; byId(`view-${value}`).setAttribute('aria-pressed',String(state.presentationView === value)); }
    for (const value of ['en','ru']) byId(`language-${value}`).setAttribute('aria-pressed',String(state.language === value));
    for (const layer of LAYERS) { byId(`layer-${layer}`).checked = state.layers.includes(layer); byId(`layer-${layer}`).disabled = !runtime.ready; }
    for (const value of ['range','scrub']) byId(`mode-${value}`).setAttribute('aria-pressed',String(state.mode === value));
    byId('range-controls').hidden = state.mode !== 'range'; byId('scrub-controls').hidden = state.mode !== 'scrub';
    byId('time-start').value = state.startYear; byId('time-end').value = state.endYear; byId('cursor-year').value = state.cursorYear; byId('time-cursor').value = state.cursorYear;
    byId('range-start-handle').value = state.startYear; byId('range-end-handle').value = state.endYear;
    for (const id of ['time-start','time-end','range-start-handle','range-end-handle','cursor-year','time-cursor','mode-range','mode-scrub','period-roman','period-leonardo','period-all']) byId(id).disabled = !runtime.ready;
    text('time-status',state.mode === 'range' ? `${state.startYear}–${state.endYear} CE · ${t('interval')}` : `${state.cursorYear} CE · ${t('trace')} ${state.traceOriginYear}; ${state.cursorYear < state.traceOriginYear ? t('none') : `${state.traceOriginYear}–${state.cursorYear}`}`);
    text('layer-status',LAYERS.map(layer => `${t(layer)}: ${!state.layers.includes(layer) ? t('off') : runtime.visibleItems.filter(item => item.layer_id === layer).length || t('none')}`).join(' · '));
    const results = chooserItems(runtime.bundle,runtime.visibleItems,runtime.search);
    const select = byId('record-select'), nextSignature = `${state.language}|${runtime.search}|${results.map(item => item.item_id).join('|')}`;
    if (recordSignature !== nextSignature) {
      recordSignature = nextSignature; select.replaceChildren(node('option',t('choose'))); select.firstChild.value = '';
      for (const item of results) { const option = node('option',`${t(item.layer_id)} · ${recordLabel(item,state.language)}${item.interval ? ` · ${item.interval.start}–${item.interval.end}` : ` · ${t('atemporal')}`}`); option.value = item.item_id; select.append(option); }
    }
    select.value = results.some(item => item.item_id === state.selectedItemId) ? state.selectedItemId : ''; select.disabled = !runtime.ready || !results.length;
    byId('record-search').disabled = !runtime.ready; byId('clear-search').disabled = !runtime.ready || !runtime.search;
    text('search-status',results.length ? `${t('searchCount')}: ${results.length}` : t('searchEmpty'));
    byId('record-search').placeholder = t('search');
    document.documentElement.dataset.artemisLanguage = state.language; document.documentElement.dataset.artemisPresentationView = state.presentationView;
    document.documentElement.dataset.artemisSelectedItem = state.selectedItemId || ''; document.documentElement.dataset.artemisTimeCursor = String(state.cursorYear);
    const attributionContext = byId('attribution-context'); if (attributionContext) attributionContext.textContent = state.language === 'ru' ? 'Современный опорный контекст; не историческая поверхность.' : words.en.context;
    layout();
  }
  function applyState(input, options = {}) {
    const previous = runtime.state, next = normalizeState(runtime.bundle,{...previous,...input},previous);
    if (runtime.ready && next.presentationView !== previous.presentationView) {
      const actual = () => runtime.map.getProjection().type === 'mercator' ? 'map' : 'globe';
      try { runtime.map.setProjection({type:next.presentationView === 'map' ? 'mercator' : 'globe'}); if (actual() !== next.presentationView) throw Error('Projection not applied'); byId('workspace-error').hidden = true; }
      catch (_) { try { runtime.map.setProjection({type:previous.presentationView === 'map' ? 'mercator' : 'globe'}); } catch (_) {} next.presentationView = actual(); text('workspace-error',words[next.language].error); byId('workspace-error').hidden = false; options.history = 'replace'; }
    }
    const visibleItems = query(runtime.bundle,next), membershipChanged = runtime.visibleItems.map(item => item.item_id).join('|') !== visibleItems.map(item => item.item_id).join('|');
    runtime.state = freeze(next); runtime.visibleItems = visibleItems;
    if (runtime.ready) {
      if (membershipChanged) runtime.map.getSource('workspace-features').setData(featuresFor(runtime.bundle,runtime.visibleItems));
      if (JSON.stringify(previous.camera) !== JSON.stringify(next.camera)) { restoringCamera = true; try { runtime.map.jumpTo(next.camera); } finally { restoringCamera = false; } }
      updatePlacePresentation();
    }
    renderControls(); renderInspector(); if (options.history !== false) history(options.history || 'push');
    return runtime.state;
  }
  function selectItem(itemId) { return applyState({selectedItemId:itemId}); }
  function layoutPlaceLabels() {
    if (!runtime.ready) return;
    const canvas = runtime.map.getCanvas(), occupied = [];
    const emphasis = presentationEmphasis(runtime.bundle,runtime.visibleItems,runtime.state), groups = placeGroups(runtime.bundle,runtime.visibleItems), ends = new Set([groups[0]?.place_ref,groups.at(-1)?.place_ref]);
    const priority = place => place === emphasis.selectedPlace ? 0 : place === emphasis.currentPlace ? 1 : ends.has(place) ? 2 : (groups.find(group => group.place_ref === place)?.presences.length || 0) > 1 ? 3 : 4;
    const markers = [...runtime.placeMarkers].sort((a,b) => priority(a[0])-priority(b[0]));
    // Read every label before writing any position. Interleaved reads/writes
    // could repeatedly invalidate browser style/layout state.
    const measurements = markers.map(([place,marker]) => { const label = marker.getElement().querySelector('.place-label'); return {place,label,point:runtime.map.project(marker.getLngLat()),width:label.offsetWidth,height:label.offsetHeight}; });
    const points = measurements.map(({place,point}) => ({place,...point})), placements = [];
    for (const {place,label,point,width,height} of measurements) {
      const candidates = [[9,-10],[-width-9,-10],[9,-height-12],[-width-9,12],[9,12],[-width/2,-height-20],[-width/2,20]];
      const fits = ([dx,dy]) => { const rect = {left:point.x+dx,right:point.x+dx+width,top:point.y+dy,bottom:point.y+dy+height}; return rect.left >= 0 && rect.right <= canvas.clientWidth && rect.top >= 0 && rect.bottom <= canvas.clientHeight && !points.some(other => other.place !== place && rect.left < other.x+8 && rect.right > other.x-8 && rect.top < other.y+8 && rect.bottom > other.y-8) && !occupied.some(other => rect.left < other.right+3 && rect.right > other.left-3 && rect.top < other.bottom+3 && rect.bottom > other.top-3); };
      const placement = candidates.find(fits), [dx,dy] = placement || candidates[0];
      placements.push({label,suppressed:!placement,left:`${16+dx}px`,top:`${16+dy}px`});
      if (placement) occupied.push({left:point.x+dx,right:point.x+dx+width,top:point.y+dy,bottom:point.y+dy+height});
    }
    for (const {label,suppressed,left,top} of placements) { if (label.classList.contains('is-suppressed') !== suppressed) label.classList.toggle('is-suppressed',suppressed); if (label.style.left !== left) label.style.left = left; if (label.style.top !== top) label.style.top = top; }
    for (const {marker,coordinates} of runtime.chronologyMarkers.values()) { const from = runtime.map.project(coordinates[0]), to = runtime.map.project(coordinates[1]); marker.getElement().firstChild.style.transform = `rotate(${Math.atan2(to.y-from.y,to.x-from.x)}rad)`; }
  }
  function updatePlacePresentation() {
    const groups = placeGroups(runtime.bundle,runtime.visibleItems), emphasis = presentationEmphasis(runtime.bundle,runtime.visibleItems,runtime.state), visiblePlaces = new Set(groups.map(group => group.place_ref));
    for (const [place,marker] of runtime.placeMarkers) if (!visiblePlaces.has(place)) { marker.remove(); runtime.placeMarkers.delete(place); }
    for (const group of groups) {
      let marker = runtime.placeMarkers.get(group.place_ref);
      if (!marker) {
        const button = node('button','', 'workspace-place-marker'); button.type = 'button'; button.dataset.placeRef = group.place_ref;
        const dot = node('span','', 'place-dot'); dot.setAttribute('aria-hidden','true'); button.append(dot);
        const label = node('span','', 'place-label'); label.append(node('span','', 'place-name'),node('span','', 'place-count')); button.append(label);
        button.addEventListener('click',() => { const active = placeGroups(runtime.bundle,runtime.visibleItems).find(value => value.place_ref === group.place_ref); if (active) selectItem(placeChoice(active,runtime.state).presence_item_id); });
        button.addEventListener('dblclick',event => { event.preventDefault(); event.stopPropagation(); const active = placeGroups(runtime.bundle,runtime.visibleItems).find(value => value.place_ref === group.place_ref); if (active) { selectItem(placeChoice(active,runtime.state).presence_item_id); focusSelection(); } });
        marker = new maplibregl.Marker({element:button,anchor:'center'}).setLngLat(group.coordinates).addTo(runtime.map); runtime.placeMarkers.set(group.place_ref,marker);
      }
      const button = marker.getElement(); button.querySelector('.place-name').textContent = group.label; button.querySelector('.place-count').textContent = group.presences.length > 1 ? ` ×${group.presences.length}` : '';
      button.setAttribute('aria-label',runtime.state.language === 'ru' ? `${group.label} · видимых присутствий: ${group.presences.length}; двойной щелчок — фокус карты` : `${group.label} · ${group.presences.length} visible presences; double-click to focus map`);
      button.setAttribute('aria-pressed',String(group.place_ref === emphasis.selectedPlace)); button.classList.toggle('is-selected',group.place_ref === emphasis.selectedPlace); button.classList.toggle('is-current',group.place_ref === emphasis.currentPlace);
      runtime.map.setFeatureState({source:'workspace-features',id:`place-anchor:${group.place_ref}`},{selected:group.place_ref === emphasis.selectedPlace,current:group.place_ref === emphasis.currentPlace});
    }
    for (const transition of emphasis.transitions) runtime.map.setFeatureState({source:'workspace-features',id:transition.id},{emphasis:transition.emphasis});
    const cues = chronologyCues(runtime.bundle,runtime.visibleItems,runtime.state), cueIds = new Set(cues.map(cue => cue.id));
    for (const [id,cue] of runtime.chronologyMarkers) if (!cueIds.has(id)) { cue.marker.remove(); runtime.chronologyMarkers.delete(id); }
    for (const cue of cues) {
      let rendered = runtime.chronologyMarkers.get(cue.id);
      if (!rendered) { const glyph = node('span','', 'workspace-chronology-cue'); glyph.dataset.transitionId = cue.id; glyph.setAttribute('aria-hidden','true'); glyph.append(node('span','▸')); rendered = {coordinates:cue.coordinates,marker:new maplibregl.Marker({element:glyph,anchor:'center'}).setLngLat(cue.midpoint).addTo(runtime.map)}; runtime.chronologyMarkers.set(cue.id,rendered); }
      rendered.marker.getElement().dataset.emphasis = String(cue.emphasis); rendered.marker.getElement().firstChild.style.opacity = cue.emphasis ? '.95' : '.12';
    }
    for (const item of runtime.visibleItems.filter(item => item.kind !== 'presence')) {
      if (item.kind === 'reference' || item.kind === 'catalog_reference') runtime.map.setFeatureState({source:'workspace-features',id:item.item_id},{selected:item.item_id === runtime.state.selectedItemId});
      else for (const primitive of runtime.bundle.roman.versions.find(version => version.item_id === item.item_id).globe.primitives) runtime.map.setFeatureState({source:'workspace-features',id:primitive.primitive_id},{selected:item.item_id === runtime.state.selectedItemId});
    }
    layoutPlaceLabels();
  }
  function focusSelection() {
    const selected = runtime.registry.get(runtime.state.selectedItemId); if (!selected || !runtime.ready) return;
    const feature = featuresFor(runtime.bundle,[selected]).features.find(item => item.properties.item_id === selected.item_id); if (!feature) return;
    if (feature.geometry.type === 'Point') runtime.map.flyTo({center:feature.geometry.coordinates,zoom:Math.max(runtime.map.getZoom(),['reference','catalog_reference'].includes(selected.kind) ? 10 : 5),duration:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 800});
    else { const positions = []; const collect = value => { if (typeof value[0] === 'number') positions.push(value); else value.forEach(collect); }; collect(feature.geometry.coordinates); const bounds = positions.reduce((box,p) => box.extend(p),new maplibregl.LngLatBounds()); runtime.map.fitBounds(bounds,{padding:60,duration:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 800}); }
  }
  function bindControls() {
    for (const layer of LAYERS) byId(`layer-${layer}`).addEventListener('change',() => applyState({layers:LAYERS.filter(value => byId(`layer-${value}`).checked)}));
    for (const language of ['en','ru']) byId(`language-${language}`).addEventListener('click',() => applyState({language}));
    for (const presentationView of ['globe','map']) byId(`view-${presentationView}`).addEventListener('click',() => { if (presentationView !== runtime.state.presentationView) applyState({presentationView}); });
    for (const mode of ['range','scrub']) byId(`mode-${mode}`).addEventListener('click',() => applyState({mode}));
    byId('time-start').addEventListener('change',event => applyState({startYear:year(event.target.value,runtime.state.startYear)}));
    byId('time-end').addEventListener('change',event => applyState({endYear:year(event.target.value,runtime.state.endYear)}));
    byId('range-start-handle').addEventListener('change',event => applyState({startYear:year(event.target.value,runtime.state.startYear)}));
    byId('range-end-handle').addEventListener('change',event => applyState({endYear:year(event.target.value,runtime.state.endYear)}));
    for (const id of ['time-cursor','cursor-year']) byId(id).addEventListener('change',event => applyState({cursorYear:year(event.target.value,runtime.state.cursorYear)}));
    for (const [id,startYear,endYear] of [['period-roman',91,116],['period-leonardo',1452,1519],['period-all',91,1519]]) byId(id).addEventListener('click',() => applyState({mode:'range',startYear,endYear}));
    byId('record-search').addEventListener('input',event => { runtime.search = event.target.value; renderControls(); });
    byId('clear-search').addEventListener('click',() => { runtime.search = ''; byId('record-search').value = ''; renderControls(); byId('record-search').focus(); });
    byId('record-select').addEventListener('change',event => selectItem(event.target.value));
    byId('close-details').addEventListener('click',() => selectItem(null)); byId('focus-selection').addEventListener('click',focusSelection);
    document.addEventListener('keydown',event => { if (event.key === 'Escape' && runtime.state.selectedItemId) { selectItem(null); byId('record-select').focus(); } });
    window.addEventListener('popstate',() => applyState(parseUrl(runtime.bundle,location.href,document.documentElement.dataset.entryProfile),{history:false}));
    const observer = new ResizeObserver(layout); for (const id of ['workspace-header','time-dock','attribution']) observer.observe(byId(id));
    window.addEventListener('resize',layout);
  }
  async function load(path) {
    const version = document.documentElement.dataset[path.includes('unified-bundle') ? 'bundleVersion' : 'contextVersion'];
    const reusable = path.includes('unified-bundle') || path.includes('earth-context');
    const url = reusable && version ? `${path}?v=${version}` : path;
    const response = await fetch(url,{cache:reusable ? 'default' : 'no-cache'});
    if (!response.ok) throw Error(`${path}: HTTP ${response.status}`); return response.json();
  }
  async function main() {
    const [bundle,context,assets,meta] = await Promise.all(['./unified-bundle.json','./earth-context.geojson','./geospatial-assets.json','./build-meta.json'].map(load));
    runtime.bundle = freeze(bundle); runtime.registry = new Map(bundle.registry.map(item => [item.item_id,item])); runtime.meta = freeze(meta);
    runtime.state = freeze(parseUrl(bundle,location.href,document.documentElement.dataset.entryProfile)); runtime.visibleItems = query(bundle,runtime.state);
    runtime.query = state => query(runtime.bundle,state || runtime.state);
    bindControls(); renderControls(); renderInspector();
    if (!window.maplibregl) throw Error('Pinned MapLibre engine could not be loaded.');
    const map = new maplibregl.Map({container:'map',style:{version:8,projection:{type:runtime.state.presentationView === 'map' ? 'mercator' : 'globe'},sources:{},layers:[{id:'space',type:'background',paint:{'background-color':'#02050b'}}],sky:{'atmosphere-blend':['interpolate',['linear'],['zoom'],0,1,4,.8,7,0]}},...runtime.state.camera,attributionControl:false,pixelRatio:Math.min(window.devicePixelRatio || 1,2),canvasContextAttributes:{antialias:true}});
    runtime.map = map; map.addControl(new maplibregl.NavigationControl({visualizePitch:true}),'top-left');
    map.on('error',event => { console.error('ARTEMIS map error',event.error || event); const host = byId('fatal-error'); host.hidden = false; host.textContent = `ARTEMIS map rendering failed: ${event.error?.message || String(event.error || event)}`; });
    map.on('load',() => {
      map.addSource('earth-context',{type:'geojson',data:context});
      map.addLayer({id:'earth-land',type:'fill',source:'earth-context',filter:['==',['get','semantic_role'],'present_day_context'],paint:{'fill-color':'#17334a','fill-outline-color':'#68a8c4'}});
      map.addSource('workspace-features',{type:'geojson',promoteId:'render_key',data:featuresFor(bundle,runtime.visibleItems)});
      map.addLayer({id:'workspace-regions',type:'fill',source:'workspace-features',filter:['==',['get','kind'],'region'],paint:{'fill-color':['match',['get','native_start'],91,'#36ccb9',106,'#73d0ec','#b6a3f1'],'fill-opacity':['case',['boolean',['feature-state','selected'],false],.4,.24]}});
      map.addLayer({id:'workspace-region-outlines',type:'line',source:'workspace-features',filter:['==',['get','kind'],'region'],paint:{'line-color':'#74d8cf','line-width':['case',['boolean',['feature-state','selected'],false],2.2,1.4]}});
      map.addLayer({id:'workspace-chronology',type:'line',source:'workspace-features',filter:['==',['get','kind'],'chronology'],paint:{'line-color':'#a8bed0','line-width':['case',['>', ['coalesce',['feature-state','emphasis'],0],0],2.2,1.4],'line-dasharray':[1.5,2.2],'line-opacity':['match',['coalesce',['feature-state','emphasis'],0],2,.95,1,.8,.35]}});
      map.addLayer({id:'workspace-points',type:'circle',source:'workspace-features',filter:['==',['geometry-type'],'Point'],paint:{'circle-radius':['case',['boolean',['feature-state','selected'],false],8,['boolean',['feature-state','current'],false],7,['match',['get','kind'],'reference',5,'catalog_reference',5,6]],'circle-color':['case',['boolean',['feature-state','selected'],false],'#ffd590',['boolean',['feature-state','current'],false],'#79cfff',['match',['get','kind'],'reference','#f0b55a','catalog_reference','#c6d697','#268dad']],'circle-stroke-color':'#c6edff','circle-stroke-width':1.5}});
      runtime.ready = true;
      const scheduleLabels = frameThrottle(layoutPlaceLabels);
      updatePlacePresentation(); map.on('move',scheduleLabels); map.on('resize',scheduleLabels); map.on('idle',scheduleLabels);
      const attribution = (assets.assets || []).filter(asset => asset.attribution).map(asset => asset.attribution).join(' · ');
      byId('attribution').replaceChildren(node('span',`${attribution || 'Natural Earth · public domain'} · Cliopatria CC-BY-4.0 · Wikidata CC0-1.0 · `)); const explanation = node('span',words.en.context); explanation.id = 'attribution-context'; byId('attribution').append(explanation);
      renderControls(); history('replace');
      map.on('click',event => { const hits = map.queryRenderedFeatures(event.point,{layers:['workspace-points','workspace-regions']}); if (hits.length) { const hit = hits[0], group = hit.properties.place_ref ? placeGroups(runtime.bundle,runtime.visibleItems).find(value => value.place_ref === hit.properties.place_ref) : null; selectItem(group ? placeChoice(group,runtime.state).presence_item_id : hit.properties.item_id); } });
      map.on('mousemove',frameThrottle(event => { const cursor = map.queryRenderedFeatures(event.point,{layers:['workspace-points','workspace-regions']}).length ? 'pointer' : ''; if (map.getCanvas().style.cursor !== cursor) map.getCanvas().style.cursor = cursor; }));
      map.on('moveend',() => {
        if (restoringCamera) return;
        const center = map.getCenter(), camera = {center:[center.lng,center.lat],zoom:map.getZoom(),pitch:map.getPitch(),bearing:map.getBearing()};
        if (JSON.stringify(camera) !== JSON.stringify(runtime.state.camera)) { runtime.state = freeze(normalizeState(bundle,{...runtime.state,camera},runtime.state)); history('push'); }
      });
      map.once('idle',() => { document.documentElement.dataset.artemisRuntimeReady = 'true'; document.documentElement.dataset.artemisVisualReady = String(map.queryRenderedFeatures({layers:['earth-land']}).length > 0); layout(); });
    });
  }
  main().catch(error => { const host = byId('fatal-error'); host.hidden = false; host.textContent = `ARTEMIS Explorer could not start: ${error.message}`; console.error(error); });
})();
