(() => {
  'use strict';

  const FILES = {
    projection: './projection.json',
    globe: './globe-projection.json',
    state: './explorer-state.json',
    assets: './geospatial-assets.json',
    context: './synthetic-earth-context.geojson',
    capabilityPath: './capability-path.geojson',
    engineEvaluation: './engine-evaluation.json',
    knowledge: './knowledge-index.json',
    meta: './build-meta.json'
  };

  const SEMANTIC_LAYER_IDS = [
    'artemis-points',
    'artemis-semantic-lines',
    'artemis-region-primary-fill',
    'artemis-region-alt-fill'
  ];
  const ALTERNATIVE_LAYER_IDS = [
    'artemis-region-alt-fill',
    'artemis-region-alt-outline'
  ];

  const startedAt = performance.now();
  const runtime = {
    map: null,
    data: null,
    knowledgeByItem: new Map(),
    alternativesVisible: true,
    performance: {
      startupToIdleMs: null,
      averageFrameMs: null,
      estimatedFps: null
    }
  };
  window.__ARTEMIS_GLOBE_SPIKE = runtime;

  function byId(id) {
    return document.getElementById(id);
  }

  function setText(id, value) {
    const node = byId(id);
    if (node) node.textContent = String(value ?? '—');
  }

  function appendText(host, tagName, text, className = '') {
    const node = document.createElement(tagName);
    if (className) node.className = className;
    node.textContent = String(text ?? '—');
    host.append(node);
    return node;
  }

  function fatal(error) {
    const node = byId('fatal-error');
    if (node) {
      node.hidden = false;
      node.textContent = `ARTEMIS Globe spike failed:\n${String(error?.stack || error?.message || error)}`;
    }
    console.error('[ARTEMIS:globe-spike]', error);
  }

  async function loadJson(url) {
    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Failed to load ${url}: HTTP ${response.status}`);
    return response.json();
  }

  function parseList(value) {
    if (Array.isArray(value)) return value;
    if (typeof value !== 'string' || !value) return [];
    try {
      const parsed = JSON.parse(value);
      return Array.isArray(parsed) ? parsed : [value];
    } catch (_error) {
      return [value];
    }
  }

  function semanticProperties(primitive) {
    return {
      item_id: primitive.item_id,
      object_ref: primitive.object_ref,
      object_type: primitive.object_type,
      subobject_ref: primitive.subobject_ref,
      render_role: primitive.render_role,
      temporal_membership: primitive.temporal_membership,
      geometry_ref: primitive.geometry_ref,
      geometry_reconstruction_mode: primitive.geometry_reconstruction_mode,
      geometry_is_primary: primitive.geometry_is_primary,
      layer_refs: JSON.stringify(primitive.layer_refs || []),
      claim_refs: JSON.stringify(primitive.claim_refs || []),
      uncertainty_refs: JSON.stringify(primitive.uncertainty_refs || []),
      evidence_link_refs: JSON.stringify(primitive.evidence_link_refs || []),
      source_refs: JSON.stringify(primitive.source_refs || []),
      semantic_flags: JSON.stringify(primitive.semantic_flags || {})
    };
  }

  function globePrimitivesToGeoJson(globe) {
    const typeMap = {
      cartographic_point: 'Point',
      cartographic_polyline: 'LineString',
      cartographic_polygon: 'Polygon',
      cartographic_multipolygon: 'MultiPolygon'
    };
    return {
      type: 'FeatureCollection',
      features: (globe.primitives || []).map((primitive) => {
        const geometryType = typeMap[primitive.primitive_kind];
        if (!geometryType) throw new Error(`Unsupported Globe primitive: ${primitive.primitive_kind}`);
        return {
          type: 'Feature',
          id: primitive.primitive_id,
          properties: semanticProperties(primitive),
          geometry: {
            type: geometryType,
            coordinates: primitive.coordinates
          }
        };
      })
    };
  }

  function createStyle() {
    return {
      version: 8,
      projection: { type: 'globe' },
      sources: {},
      layers: [
        {
          id: 'space-background',
          type: 'background',
          paint: { 'background-color': '#02050b' }
        }
      ],
      sky: {
        'atmosphere-blend': [
          'interpolate', ['linear'], ['zoom'],
          0, 1,
          4, 0.8,
          7, 0
        ]
      }
    };
  }

  function addContextLayers(map, context) {
    map.addSource('artemis-synthetic-earth', { type: 'geojson', data: context });
    map.addLayer({
      id: 'artemis-synthetic-surface',
      type: 'fill',
      source: 'artemis-synthetic-earth',
      filter: ['==', ['get', 'semantic_role'], 'present_day_context'],
      paint: {
        'fill-color': '#10243c',
        'fill-opacity': 0.88
      }
    });
    map.addLayer({
      id: 'artemis-graticule',
      type: 'line',
      source: 'artemis-synthetic-earth',
      filter: ['==', ['get', 'kind'], 'graticule'],
      paint: {
        'line-color': '#31577c',
        'line-width': 0.8,
        'line-opacity': 0.6
      }
    });
  }

  function addSemanticLayers(map, globe) {
    const data = globePrimitivesToGeoJson(globe);
    map.addSource('artemis-semantic', { type: 'geojson', data });

    map.addLayer({
      id: 'artemis-region-primary-fill',
      type: 'fill',
      source: 'artemis-semantic',
      filter: [
        'all',
        ['==', ['geometry-type'], 'Polygon'],
        ['==', ['get', 'render_role'], 'region_geometry'],
        ['==', ['get', 'geometry_is_primary'], true]
      ],
      paint: {
        'fill-color': '#3a8d8b',
        'fill-opacity': 0.32
      }
    });
    map.addLayer({
      id: 'artemis-region-primary-outline',
      type: 'line',
      source: 'artemis-semantic',
      filter: [
        'all',
        ['==', ['geometry-type'], 'Polygon'],
        ['==', ['get', 'render_role'], 'region_geometry'],
        ['==', ['get', 'geometry_is_primary'], true]
      ],
      paint: {
        'line-color': '#82d8d3',
        'line-width': 2.2,
        'line-opacity': 0.95
      }
    });

    map.addLayer({
      id: 'artemis-region-alt-fill',
      type: 'fill',
      source: 'artemis-semantic',
      filter: [
        'all',
        ['==', ['geometry-type'], 'Polygon'],
        ['==', ['get', 'render_role'], 'region_geometry'],
        ['==', ['get', 'geometry_is_primary'], false]
      ],
      paint: {
        'fill-color': '#c79a58',
        'fill-opacity': 0.2
      }
    });
    map.addLayer({
      id: 'artemis-region-alt-outline',
      type: 'line',
      source: 'artemis-semantic',
      filter: [
        'all',
        ['==', ['geometry-type'], 'Polygon'],
        ['==', ['get', 'render_role'], 'region_geometry'],
        ['==', ['get', 'geometry_is_primary'], false]
      ],
      paint: {
        'line-color': '#f0c47a',
        'line-width': 2,
        'line-dasharray': [2, 2],
        'line-opacity': 0.95
      }
    });

    map.addLayer({
      id: 'artemis-semantic-lines',
      type: 'line',
      source: 'artemis-semantic',
      filter: ['==', ['geometry-type'], 'LineString'],
      paint: {
        'line-color': '#8bc3ff',
        'line-width': 3,
        'line-opacity': 0.9
      }
    });

    map.addLayer({
      id: 'artemis-points',
      type: 'circle',
      source: 'artemis-semantic',
      filter: ['==', ['geometry-type'], 'Point'],
      paint: {
        'circle-radius': 6,
        'circle-color': '#72c7ff',
        'circle-stroke-color': '#e4f5ff',
        'circle-stroke-width': 1.5,
        'circle-opacity': 0.95
      }
    });
  }

  function addCapabilityPath(map, capabilityPath) {
    map.addSource('renderer-capability-path', { type: 'geojson', data: capabilityPath });
    map.addLayer({
      id: 'renderer-capability-path-line',
      type: 'line',
      source: 'renderer-capability-path',
      paint: {
        'line-color': '#d79ae8',
        'line-width': 2.5,
        'line-dasharray': [1.5, 1.5],
        'line-opacity': 0.9
      }
    });
  }

  function configureTerrainPath(map, manifest) {
    const terrain = (manifest.assets || []).find((asset) => asset.asset_kind === 'terrain_elevation');
    const node = byId('terrain-status');
    if (!terrain) {
      if (node) node.textContent = 'Terrain: no terrain asset in manifest';
      return;
    }

    const provider = terrain.provider || {};
    const endpoint = provider.endpoint_template || '';
    const liveRasterDem = provider.adapter_kind === 'raster_url_template'
      && /^https?:\/\//i.test(endpoint);

    if (!liveRasterDem) {
      if (node) {
        node.textContent = `Terrain: capability path ready · ${terrain.asset_id} is synthetic/no live DEM`;
      }
      return;
    }

    map.addSource('artemis-terrain', {
      type: 'raster-dem',
      tiles: [endpoint],
      tileSize: 256
    });
    map.setTerrain({ source: 'artemis-terrain', exaggeration: 1 });
    if (node) node.textContent = `Terrain: enabled from manifest asset ${terrain.asset_id}`;
  }

  function renderAttribution(manifest) {
    const rows = (manifest.assets || []).map((asset) => asset.licensing?.attribution_text).filter(Boolean);
    setText('attribution-status', rows.join(' · '));
  }

  function renderSharedState(data) {
    const temporal = data.state.temporal_selection || {};
    setText('world-slice', data.state.world_slice_ref);
    setText('explorer-state', data.state.state_id);
    setText('selected-time', temporal.start === temporal.end ? temporal.start : `${temporal.start} → ${temporal.end}`);
    setText('projection-id', data.projection.projection_id);
    setText('primitive-count', (data.globe.primitives || []).length);
    setText(
      'corpus-status',
      data.knowledge.historical_corpus_ready
        ? 'reviewed historical corpus'
        : 'synthetic contract fixture · not historical evidence'
    );
    setText('deferred-types', (data.knowledge.deferred_object_types || []).join(', ') || 'none');

    const cards = [
      ['active', (data.projection.active_object_refs || []).length],
      ['possible', (data.projection.possible_active_object_refs || []).length],
      ['context', (data.projection.context_object_refs || []).length],
      ['losses', (data.projection.losses || []).length]
    ];
    const summary = byId('semantic-summary');
    if (summary) {
      summary.innerHTML = '';
      for (const [label, value] of cards) {
        const card = document.createElement('div');
        card.className = 'summary-card';
        const strong = document.createElement('strong');
        strong.textContent = String(value);
        const span = document.createElement('span');
        span.textContent = label;
        card.append(strong, span);
        summary.append(card);
      }
    }
  }

  function renderUnresolved(projection) {
    const host = byId('unresolved-list');
    if (!host) return;
    host.innerHTML = '';

    const lossByItem = new Map((projection.losses || []).map((loss) => [loss.item_id, loss]));
    const unresolved = (projection.items || []).filter((item) => item.spatial_status === 'unresolved');

    for (const item of unresolved) {
      const loss = lossByItem.get(item.item_id);
      const segmentKind = item.semantic_flags?.segment_kind || null;
      const row = document.createElement('button');
      row.type = 'button';
      row.className = 'unresolved-item';
      if (segmentKind === 'inferred_gap') row.dataset.kind = 'trajectory-gap';
      row.dataset.itemId = item.item_id;
      row.setAttribute('aria-label', `Inspect unresolved ${item.object_type} ${item.object_ref}`);

      appendText(row, 'strong', `${item.object_type} · ${item.object_ref}`);

      const uncertainty = (item.uncertainty_refs || []).join(', ') || 'none';
      appendText(
        row,
        'span',
        `subobject=${item.subobject_ref || '—'} · reason=${loss?.reason || 'unresolved'} · uncertainty=${uncertainty}`
      );
      row.addEventListener('click', () => selectKnowledgeItem(item.item_id, { focus: true }));
      host.append(row);
    }

    if (!unresolved.length) {
      host.textContent = 'No unresolved semantic items in this projection.';
    }
  }

  function addIdentityRows(host, record) {
    const rows = [
      ['object_ref', record.object_ref],
      ['subobject_ref', record.subobject_ref || '—'],
      ['type', record.object_type],
      ['role', record.render_role],
      ['temporal', record.temporal_membership],
      ['spatial', record.spatial_status]
    ];
    const dl = document.createElement('dl');
    dl.className = 'identity-list';
    for (const [key, value] of rows) {
      appendText(dl, 'dt', key);
      appendText(dl, 'dd', value);
    }
    host.append(dl);
  }

  function addEvidence(host, record) {
    const section = document.createElement('section');
    section.className = 'knowledge-section';
    appendText(section, 'h3', 'Claims & evidence');
    const evidenceByClaim = new Map();
    for (const evidence of record.evidence_links || []) {
      const rows = evidenceByClaim.get(evidence.claim_id) || [];
      rows.push(evidence);
      evidenceByClaim.set(evidence.claim_id, rows);
    }
    const sourceById = new Map((record.sources || []).map((source) => [source.id, source]));

    if (!(record.claims || []).length) {
      appendText(section, 'p', 'No projected claims for this semantic item.', 'empty-note');
    }
    for (const claim of record.claims || []) {
      const group = document.createElement('article');
      group.className = 'evidence-group';
      appendText(group, 'div', claim.id, 'record-id');
      appendText(group, 'p', claim.statement, 'claim-statement');
      appendText(
        group,
        'div',
        `${claim.review_state} · confidence ${claim.confidence} · evidence ${claim.evidence_state}`,
        'record-meta'
      );

      for (const evidence of evidenceByClaim.get(claim.id) || []) {
        const source = sourceById.get(evidence.source_id);
        const row = document.createElement('div');
        row.className = 'evidence-row';
        if (source) {
          const link = document.createElement('a');
          link.href = source.artifact_uri || source.uri;
          link.target = '_blank';
          link.rel = 'noopener';
          link.textContent = source.title || source.id;
          row.append(link);
        } else {
          appendText(row, 'span', evidence.source_id);
        }
        if (source) {
          appendText(
            row,
            'span',
            `${source.source_type} · ${source.review_state} · ${source.uri}`,
            'record-meta'
          );
        }
        appendText(row, 'code', evidence.locator, 'evidence-locator');
        appendText(
          row,
          'span',
          `${evidence.relation_to_claim} · ${evidence.evidence_strength} · ${evidence.review_state}`,
          'record-meta'
        );
        group.append(row);
      }
      section.append(group);
    }
    host.append(section);
  }

  function addUncertainties(host, record) {
    const section = document.createElement('section');
    section.className = 'knowledge-section';
    appendText(section, 'h3', 'Material uncertainty');
    if (!(record.uncertainties || []).length) {
      appendText(section, 'p', 'No material uncertainty is referenced by this projection item.', 'empty-note');
    }
    for (const uncertainty of record.uncertainties || []) {
      const card = document.createElement('article');
      card.className = 'uncertainty-card';
      appendText(card, 'div', uncertainty.id, 'record-id');
      appendText(card, 'strong', uncertainty.dimension);
      appendText(card, 'p', uncertainty.description);
      appendText(card, 'p', `Effect: ${uncertainty.effect}`, 'uncertainty-effect');
      if ((uncertainty.alternatives || []).length) {
        appendText(card, 'p', `Alternatives: ${uncertainty.alternatives.join(' · ')}`, 'record-meta');
      }
      section.append(card);
    }
    host.append(section);
  }

  function addProjectionLosses(host, record) {
    const section = document.createElement('section');
    section.className = 'knowledge-section';
    appendText(section, 'h3', 'Projection loss');
    if (!(record.projection_losses || []).length) {
      appendText(section, 'p', 'No projection loss is recorded for this item.', 'empty-note');
    }
    for (const loss of record.projection_losses || []) {
      appendText(
        section,
        'p',
        `${loss.loss_kind} · ${loss.reason} · ${loss.severity}`,
        'loss-card'
      );
    }
    host.append(section);
  }

  function renderKnowledgeRecord(record) {
    const card = byId('selection-card');
    if (!card) return;
    card.classList.remove('empty');
    card.innerHTML = '';
    card.dataset.itemId = record.item_id;
    appendText(card, 'div', record.label, 'selection-title');
    appendText(card, 'div', record.item_id, 'record-id');
    addIdentityRows(card, record);
    addEvidence(card, record);
    addUncertainties(card, record);
    addProjectionLosses(card, record);
  }

  function selectKnowledgeItem(itemId, options = {}) {
    const record = runtime.knowledgeByItem.get(itemId);
    if (!record) {
      const card = byId('selection-card');
      if (card) {
        card.classList.remove('empty');
        card.textContent = `No knowledge-index record exists for ${itemId}.`;
      }
      return;
    }
    renderKnowledgeRecord(record);
    if (options.focus) byId('selection-card')?.focus({ preventScroll: false });
  }

  function renderSelection(properties) {
    const itemId = properties.item_id;
    if (itemId) {
      selectKnowledgeItem(itemId, { focus: true });
      return;
    }
    const card = byId('selection-card');
    if (card) {
      card.classList.remove('empty');
      card.textContent = 'Rendered feature has no semantic item_id and cannot be resolved.';
    }
  }

  function renderCapabilitySelection() {
    const card = byId('selection-card');
    if (!card) return;
    card.classList.remove('empty');
    card.textContent = 'Renderer capability path selected. This geometry has no World Model object_ref and cannot be resolved as historical knowledge.';
  }

  function bindPicking(map) {
    map.on('click', (event) => {
      const semantic = map.queryRenderedFeatures(event.point, { layers: SEMANTIC_LAYER_IDS });
      if (semantic.length) {
        renderSelection(semantic[0].properties || {});
        return;
      }
      const capability = map.queryRenderedFeatures(event.point, { layers: ['renderer-capability-path-line'] });
      if (capability.length) renderCapabilitySelection();
    });

    map.on('mousemove', (event) => {
      const hits = map.queryRenderedFeatures(event.point, {
        layers: [...SEMANTIC_LAYER_IDS, 'renderer-capability-path-line']
      });
      map.getCanvas().style.cursor = hits.length ? 'pointer' : '';
    });
  }

  function bindControls(map) {
    byId('view-global')?.addEventListener('click', () => {
      map.flyTo({ center: [10, 15], zoom: 0.8, pitch: 0, bearing: 0, duration: 900 });
    });
    byId('view-basin')?.addEventListener('click', () => {
      map.flyTo({ center: [10.6, 50.0], zoom: 4.2, pitch: 38, bearing: -12, duration: 900 });
    });
    byId('toggle-alternatives')?.addEventListener('click', (event) => {
      runtime.alternativesVisible = !runtime.alternativesVisible;
      for (const layerId of ALTERNATIVE_LAYER_IDS) {
        if (map.getLayer(layerId)) {
          map.setLayoutProperty(layerId, 'visibility', runtime.alternativesVisible ? 'visible' : 'none');
        }
      }
      event.currentTarget.setAttribute('aria-pressed', String(runtime.alternativesVisible));
      event.currentTarget.textContent = `Alternatives: ${runtime.alternativesVisible ? 'on' : 'off'}`;
    });
  }

  function sampleFrames(frameCount = 60) {
    const samples = [];
    let previous = performance.now();
    function tick(now) {
      samples.push(now - previous);
      previous = now;
      if (samples.length < frameCount) {
        requestAnimationFrame(tick);
        return;
      }
      const stable = samples.slice(5);
      const average = stable.reduce((sum, value) => sum + value, 0) / Math.max(1, stable.length);
      runtime.performance.averageFrameMs = average;
      runtime.performance.estimatedFps = average > 0 ? 1000 / average : null;
      setText('frame-sample', `${average.toFixed(1)} ms/frame · ~${runtime.performance.estimatedFps.toFixed(0)} FPS`);
    }
    requestAnimationFrame(tick);
  }

  async function main() {
    if (!window.maplibregl) throw new Error('MapLibre GL JS 5.24.0 failed to load. Network access to the pinned engine CDN is required for this R&D artifact.');

    const [projection, globe, state, assets, context, capabilityPath, engineEvaluation, knowledge, meta] = await Promise.all([
      loadJson(FILES.projection),
      loadJson(FILES.globe),
      loadJson(FILES.state),
      loadJson(FILES.assets),
      loadJson(FILES.context),
      loadJson(FILES.capabilityPath),
      loadJson(FILES.engineEvaluation),
      loadJson(FILES.knowledge),
      loadJson(FILES.meta)
    ]);

    runtime.data = { projection, globe, state, assets, context, capabilityPath, engineEvaluation, knowledge, meta };
    runtime.knowledgeByItem = new Map((knowledge.records || []).map((record) => [record.item_id, record]));
    runtime.selectItem = (itemId) => selectKnowledgeItem(itemId, { focus: true });
    renderSharedState(runtime.data);
    renderUnresolved(projection);
    renderAttribution(assets);
    const primaryObjectRef = state.selection?.primary_object_ref;
    const primaryRecord = (knowledge.records || []).find((record) => record.object_ref === primaryObjectRef);
    if (primaryRecord) renderKnowledgeRecord(primaryRecord);
    setText('engine-status', `engine: MapLibre GL JS ${window.maplibregl.version || '5.24.0'} · R&D`);

    const map = new maplibregl.Map({
      container: 'globe',
      style: createStyle(),
      center: [10, 15],
      zoom: 0.8,
      pitch: 0,
      bearing: 0,
      attributionControl: false,
      canvasContextAttributes: { antialias: true }
    });
    runtime.map = map;
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-left');
    if (maplibregl.GlobeControl) map.addControl(new maplibregl.GlobeControl(), 'top-left');

    map.on('error', (event) => {
      console.warn('[ARTEMIS:globe-spike] MapLibre runtime warning', event?.error || event);
    });

    map.on('load', () => {
      if (typeof map.setProjection === 'function') map.setProjection({ type: 'globe' });
      addContextLayers(map, context);
      addSemanticLayers(map, globe);
      addCapabilityPath(map, capabilityPath);
      configureTerrainPath(map, assets);
      bindPicking(map);
      bindControls(map);

      map.once('idle', () => {
        runtime.performance.startupToIdleMs = performance.now() - startedAt;
        setText('startup-ms', `${runtime.performance.startupToIdleMs.toFixed(0)} ms`);
        sampleFrames();
      });
    });
  }

  main().catch(fatal);
})();
