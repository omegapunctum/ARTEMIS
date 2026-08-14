(() => {
  'use strict';

  const FILES = {
    projection: './projection.json',
    globe: './globe-projection.json',
    state: './explorer-state.json',
    views: './explorer-views.json',
    assets: './geospatial-assets.json',
    context: './earth-context.geojson',
    capabilityPath: './capability-path.geojson',
    engineEvaluation: './engine-evaluation.json',
    acceptanceProfiles: './acceptance-profiles.json',
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
    viewIndex: null,
    viewByKey: new Map(),
    knowledgeByItem: new Map(),
    selectedItemId: null,
    activeTemporalPresetId: null,
    activeLayerRefs: [],
    alternativesVisible: true,
    performance: {
      startupToIdleMs: null,
      averageFrameMs: null,
      estimatedFps: null
    },
    acceptanceEvidence: null
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

  function cloneJson(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function viewKey(temporalPresetId, layerRefs) {
    return `${temporalPresetId}|${[...(layerRefs || [])].sort().join(',')}`;
  }

  function currentProjectionItem(itemId) {
    return (runtime.data?.projection?.items || []).find((item) => item.item_id === itemId) || null;
  }

  function cameraDuration() {
    return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 0 : 900;
  }

  function accessibleName(node) {
    const ariaLabel = node.getAttribute('aria-label')?.trim();
    if (ariaLabel) return ariaLabel;
    const labelledBy = node.getAttribute('aria-labelledby');
    if (labelledBy) {
      const value = labelledBy
        .split(/\s+/)
        .map((id) => byId(id)?.textContent?.trim() || '')
        .filter(Boolean)
        .join(' ');
      if (value) return value;
    }
    const labelText = [...(node.labels || [])]
      .map((label) => label.textContent?.trim() || '')
      .filter(Boolean)
      .join(' ');
    return labelText || node.textContent?.trim() || node.getAttribute('title')?.trim() || '';
  }

  function layoutMode(contract) {
    const breakpoints = contract.layout_breakpoints_css_px || {};
    if (window.innerWidth <= breakpoints.mobile_max_width) return 'mobile';
    if (window.innerWidth <= breakpoints.tablet_max_width) return 'tablet';
    return 'desktop';
  }

  function collectAcceptanceEvidence(contract) {
    const root = document.documentElement;
    const thresholds = contract.thresholds || {};
    const mode = layoutMode(contract);
    const requestedProfileId = new URLSearchParams(window.location.search).get('profile');
    const profile = (contract.profiles || []).find((candidate) => (
      candidate.profile_id === requestedProfileId
    )) || (contract.profiles || []).find((candidate) => (
      candidate.browser_window_css_px?.width === window.innerWidth
      && candidate.expected_layout_mode === mode
    ));
    const interactive = [...document.querySelectorAll('button, input, a[href]')];
    const unnamed = interactive.filter((node) => !accessibleName(node));
    const measuredTargets = [...document.querySelectorAll('button, input[type="range"]')];
    const minTarget = Number(thresholds.min_interactive_target_css_px || 24);
    const undersized = measuredTargets.filter((node) => {
      const rect = node.getBoundingClientRect();
      return rect.width < minTarget || rect.height < minTarget;
    });
    const globeRect = byId('globe-shell')?.getBoundingClientRect();
    const horizontalOverflow = Math.max(0, root.scrollWidth - root.clientWidth);
    const reducedMotion = Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);

    runtime.acceptanceEvidence = {
      evidence_scope: contract.evidence_scope,
      profile_id: profile?.profile_id || 'unmatched',
      layout_mode: mode,
      expected_layout_mode: profile?.expected_layout_mode || null,
      viewport_css_px: { width: window.innerWidth, height: window.innerHeight },
      reduced_motion: reducedMotion,
      horizontal_overflow_css_px: horizontalOverflow,
      unnamed_interactive_control_count: unnamed.length,
      undersized_target_count: undersized.length,
      globe_css_px: {
        width: Math.round(globeRect?.width || 0),
        height: Math.round(globeRect?.height || 0)
      },
      startup_to_idle_ms: runtime.performance.startupToIdleMs,
      average_frame_ms: runtime.performance.averageFrameMs,
      limitations: contract.limitations || []
    };

    root.dataset.artemisRuntimeReady = 'true';
    root.dataset.artemisViewportProfile = runtime.acceptanceEvidence.profile_id;
    root.dataset.artemisLayoutMode = mode;
    root.dataset.artemisViewportWidth = String(window.innerWidth);
    root.dataset.artemisViewportHeight = String(window.innerHeight);
    root.dataset.artemisReducedMotion = String(reducedMotion);
    root.dataset.artemisHorizontalOverflow = String(horizontalOverflow);
    root.dataset.artemisUnnamedControlCount = String(unnamed.length);
    root.dataset.artemisUndersizedTargetCount = String(undersized.length);
    root.dataset.artemisGlobeWidth = String(runtime.acceptanceEvidence.globe_css_px.width);
    root.dataset.artemisGlobeHeight = String(runtime.acceptanceEvidence.globe_css_px.height);
    root.dataset.artemisStartupRecorded = String(runtime.performance.startupToIdleMs !== null);
    root.dataset.artemisStartupToIdleMs = runtime.performance.startupToIdleMs === null
      ? 'diagnostic-only-pending'
      : runtime.performance.startupToIdleMs.toFixed(1);
    root.dataset.artemisAverageFrameMs = runtime.performance.averageFrameMs === null
      ? 'diagnostic-only-pending'
      : runtime.performance.averageFrameMs.toFixed(1);
  }

  function safeSourceHref(value) {
    try {
      const url = new URL(String(value || ''), window.location.href);
      return ['http:', 'https:'].includes(url.protocol) ? url.href : null;
    } catch (_error) {
      return null;
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
    map.addSource('artemis-earth-context', { type: 'geojson', data: context });
    map.addLayer({
      id: 'artemis-present-day-land',
      type: 'fill',
      source: 'artemis-earth-context',
      filter: ['==', ['get', 'semantic_role'], 'present_day_context'],
      paint: {
        'fill-color': '#17334a',
        'fill-opacity': 0.92
      }
    });
    map.addLayer({
      id: 'artemis-present-day-coastline',
      type: 'line',
      source: 'artemis-earth-context',
      filter: ['==', ['get', 'semantic_role'], 'present_day_context'],
      paint: {
        'line-color': '#4f7591',
        'line-width': 0.7,
        'line-opacity': 0.8
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
    const contextAsset = (data.assets.assets || []).find((asset) => asset.asset_kind === 'vector_basemap');
    setText('world-slice', data.state.world_slice_ref);
    setText('explorer-state', data.state.state_id);
    setText('selected-time', temporal.start === temporal.end ? temporal.start : `${temporal.start} → ${temporal.end}`);
    setText('projection-id', data.projection.projection_id);
    setText('primitive-count', (data.globe.primitives || []).length);
    setText(
      'corpus-status',
      data.knowledge.corpus_status_label
        || (data.knowledge.historical_corpus_ready
          ? 'reviewed historical corpus'
          : 'candidate package · historical readiness not established')
    );
    setText(
      'boundary-status',
      `Earth context: ${contextAsset?.label || 'bundled reference layer'} · real generalized physical geography · present_day_context only. Semantic input: ${data.knowledge.corpus_status_label || 'status unavailable'}. No historical coastline validity, historical geometry, real terrain, satellite imagery, provider token, or public promotion is implied.`
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
      row.setAttribute('aria-pressed', String(item.item_id === runtime.selectedItemId));
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
        const sourceHref = source ? safeSourceHref(source.artifact_uri || source.uri) : null;
        if (source && sourceHref) {
          const link = document.createElement('a');
          link.href = sourceHref;
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

  function updateCanonicalSelection(item) {
    const state = runtime.data?.state;
    if (!state || !item) return;
    state.selection.primary_object_ref = item.object_ref;
    state.selection.selected_object_refs = [item.object_ref];
    if (item.object_type === 'Trajectory') {
      state.active_focus.trajectory_ref = item.object_ref;
      state.active_focus.trajectory_segment_ref = item.subobject_ref;
    }
    if (item.object_type === 'Region') {
      state.active_focus.region_ref = item.object_ref;
      state.active_focus.region_geometry_ref = item.subobject_ref;
    }
  }

  function clearCanonicalSelection(message = 'No semantic object selected.') {
    runtime.selectedItemId = null;
    if (runtime.data?.state?.selection) {
      runtime.data.state.selection.primary_object_ref = null;
      runtime.data.state.selection.selected_object_refs = [];
    }
    const card = byId('selection-card');
    if (card) {
      card.classList.add('empty');
      card.removeAttribute('data-item-id');
      card.textContent = message;
    }
  }

  function selectKnowledgeItem(itemId, options = {}) {
    const record = runtime.knowledgeByItem.get(itemId);
    const projectionItem = currentProjectionItem(itemId);
    if (!record || !projectionItem) {
      const card = byId('selection-card');
      if (card) {
        card.classList.remove('empty');
        card.textContent = `No active projection record exists for ${itemId}.`;
      }
      return;
    }
    const losses = (runtime.data.projection.losses || []).filter((loss) => loss.item_id === itemId);
    runtime.selectedItemId = itemId;
    updateCanonicalSelection(projectionItem);
    renderKnowledgeRecord({
      ...record,
      temporal_membership: projectionItem.temporal_membership,
      spatial_status: projectionItem.spatial_status,
      semantic_flags: projectionItem.semantic_flags,
      projection_losses: losses
    });
    renderUnresolved(runtime.data.projection);
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

  function syncExplorerControls() {
    const presets = runtime.viewIndex?.temporal_presets || [];
    const presetIndex = Math.max(0, presets.findIndex(
      (preset) => preset.preset_id === runtime.activeTemporalPresetId
    ));
    const range = byId('temporal-preset');
    if (range) range.value = String(presetIndex);
    setText('temporal-preset-value', presets[presetIndex]?.label || runtime.activeTemporalPresetId);
    for (const input of document.querySelectorAll('#layer-controls input[type="checkbox"]')) {
      input.checked = runtime.activeLayerRefs.includes(input.value);
    }
  }

  function applySemanticView(temporalPresetId, layerRefs, options = {}) {
    const next = runtime.viewByKey.get(viewKey(temporalPresetId, layerRefs));
    if (!next) throw new Error(`No deterministic Explorer view for ${temporalPresetId}`);

    const priorSelection = runtime.selectedItemId;
    runtime.activeTemporalPresetId = next.temporal_preset_id;
    runtime.activeLayerRefs = [...next.active_layer_refs];
    runtime.data.state = cloneJson(next.state);
    runtime.data.projection = next.projection;
    runtime.data.globe = next.globe;

    const semanticSource = runtime.map?.getSource?.('artemis-semantic');
    if (semanticSource?.setData) semanticSource.setData(globePrimitivesToGeoJson(next.globe));

    renderSharedState(runtime.data);
    renderUnresolved(next.projection);
    syncExplorerControls();

    const itemIds = new Set((next.projection.items || []).map((item) => item.item_id));
    if (priorSelection && itemIds.has(priorSelection)) {
      selectKnowledgeItem(priorSelection);
    } else if (options.initial) {
      const primaryObjectRef = next.state.selection?.primary_object_ref;
      const primaryItem = (next.projection.items || []).find(
        (item) => item.object_ref === primaryObjectRef
      );
      if (primaryItem) selectKnowledgeItem(primaryItem.item_id);
      else clearCanonicalSelection();
    } else if (priorSelection) {
      clearCanonicalSelection('Selection cleared: the object is outside the active time/layer projection.');
    } else {
      clearCanonicalSelection();
    }

    const status = byId('interaction-status');
    if (status) {
      status.textContent = `${next.projection.items.length} projected records · ${runtime.activeLayerRefs.length} active layers · selection and picking synchronized.`;
    }
    document.documentElement.dataset.artemisTemporalPreset = temporalPresetId;
    document.documentElement.dataset.artemisLayerCount = String(runtime.activeLayerRefs.length);
    return next;
  }

  function renderExplorerControls() {
    const presets = runtime.viewIndex?.temporal_presets || [];
    const range = byId('temporal-preset');
    if (range) {
      range.max = String(Math.max(0, presets.length - 1));
      range.disabled = presets.length < 2;
      range.addEventListener('input', (event) => {
        const preset = presets[Number(event.currentTarget.value)];
        if (preset) applySemanticView(preset.preset_id, runtime.activeLayerRefs);
      });
    }

    const layers = byId('layer-controls');
    if (layers) {
      for (const option of runtime.viewIndex.layer_options || []) {
        const label = document.createElement('label');
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.value = option.layer_ref;
        input.addEventListener('change', () => {
          const active = [...layers.querySelectorAll('input:checked')].map((node) => node.value);
          applySemanticView(runtime.activeTemporalPresetId, active);
        });
        const span = document.createElement('span');
        span.textContent = option.label;
        label.append(input, span);
        layers.append(label);
      }
    }
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
      map.flyTo({ center: [10, 15], zoom: 0.8, pitch: 0, bearing: 0, duration: cameraDuration() });
    });
    const focusSlice = () => {
      const intent = runtime.data?.state?.view_intent || {};
      if (intent.kind === 'bounds' && Array.isArray(intent.bbox) && intent.bbox.length === 4) {
        map.fitBounds(
          [[intent.bbox[0], intent.bbox[1]], [intent.bbox[2], intent.bbox[3]]],
          { padding: 40, duration: cameraDuration() }
        );
        return;
      }
      map.flyTo({ center: [10, 15], zoom: 0.8, pitch: 0, bearing: 0, duration: cameraDuration() });
    };
    runtime.focusSlice = focusSlice;
    byId('view-slice')?.addEventListener('click', focusSlice);
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
      collectAcceptanceEvidence(runtime.data.acceptanceProfiles);
    }
    requestAnimationFrame(tick);
  }

  async function main() {
    if (!window.maplibregl) throw new Error('MapLibre GL JS 5.24.0 failed to load. Network access to the pinned engine CDN is required for this R&D artifact.');

    const [projection, globe, state, views, assets, context, capabilityPath, engineEvaluation, acceptanceProfiles, knowledge, meta] = await Promise.all([
      loadJson(FILES.projection),
      loadJson(FILES.globe),
      loadJson(FILES.state),
      loadJson(FILES.views),
      loadJson(FILES.assets),
      loadJson(FILES.context),
      loadJson(FILES.capabilityPath),
      loadJson(FILES.engineEvaluation),
      loadJson(FILES.acceptanceProfiles),
      loadJson(FILES.knowledge),
      loadJson(FILES.meta)
    ]);

    runtime.data = { projection, globe, state, assets, context, capabilityPath, engineEvaluation, acceptanceProfiles, knowledge, meta };
    runtime.viewIndex = views;
    runtime.viewByKey = new Map((views.views || []).map((view) => [
      viewKey(view.temporal_preset_id, view.active_layer_refs),
      view
    ]));
    runtime.knowledgeByItem = new Map((knowledge.records || []).map((record) => [record.item_id, record]));
    runtime.selectItem = (itemId) => selectKnowledgeItem(itemId, { focus: true });
    runtime.selectView = (presetId, layerRefs) => applySemanticView(presetId, layerRefs || runtime.activeLayerRefs);
    renderExplorerControls();
    renderAttribution(assets);

    const params = new URLSearchParams(window.location.search);
    const defaultView = (views.views || []).find((view) => view.view_id === views.default_view_id);
    if (!defaultView) throw new Error(`Default Explorer view does not resolve: ${views.default_view_id}`);
    const requestedPreset = params.get('time') || defaultView.temporal_preset_id;
    const requestedLayers = params.has('layers')
      ? params.get('layers').split(',').filter(Boolean)
      : defaultView.active_layer_refs;
    const initialView = runtime.viewByKey.get(viewKey(requestedPreset, requestedLayers)) || defaultView;
    applySemanticView(initialView.temporal_preset_id, initialView.active_layer_refs, { initial: true });
    const requestedItem = params.get('item');
    if (requestedItem) selectKnowledgeItem(requestedItem);
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
      addSemanticLayers(map, runtime.data.globe);
      addCapabilityPath(map, capabilityPath);
      configureTerrainPath(map, assets);
      bindPicking(map);
      bindControls(map);
      collectAcceptanceEvidence(acceptanceProfiles);
      window.addEventListener('resize', () => collectAcceptanceEvidence(acceptanceProfiles));

      map.once('idle', () => {
        runtime.performance.startupToIdleMs = performance.now() - startedAt;
        setText('startup-ms', `${runtime.performance.startupToIdleMs.toFixed(0)} ms`);
        collectAcceptanceEvidence(acceptanceProfiles);
        sampleFrames();
      });
    });
  }

  main().catch(fatal);
})();
