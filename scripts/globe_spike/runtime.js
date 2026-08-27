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
    acceptanceEvidence: null,
    visualReadiness: {
      ready: false,
      contextSourceFeatureCount: 0,
      contextRenderedFeatureCount: 0
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

  function cloneJson(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function viewKey(temporalPresetId, layerRefs) {
    return `${temporalPresetId}|${[...(layerRefs || [])].sort().join(',')}`;
  }

  function geometrySignature(globe) {
    return JSON.stringify((globe?.primitives || []).map((primitive) => [
      primitive.primitive_id,
      primitive.primitive_kind,
      primitive.coordinates
    ]));
  }

  function alternativeGeometryCount(globe) {
    return (globe?.primitives || []).filter((primitive) => (
      primitive.render_role === 'region_geometry'
      && primitive.geometry_is_primary === false
    )).length;
  }

  function syncUrlState() {
    if (!runtime.activeTemporalPresetId) return;
    const url = new URL(window.location.href);
    url.searchParams.set('time', runtime.activeTemporalPresetId);
    url.searchParams.set('layers', [...runtime.activeLayerRefs].sort().join(','));
    if (runtime.selectedItemId) url.searchParams.set('item', runtime.selectedItemId);
    else url.searchParams.delete('item');
    window.history.replaceState({ artemisExplorerState: true }, '', url);
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
    const interactive = [...document.querySelectorAll('button, input, a[href], summary')]
      .filter((node) => !node.hidden && node.getClientRects().length > 0);
    const unnamed = interactive.filter((node) => !accessibleName(node));
    const measuredTargets = [...document.querySelectorAll('button, input[type="range"], summary')]
      .filter((node) => !node.hidden && node.getClientRects().length > 0);
    const minTarget = Number(thresholds.min_interactive_target_css_px || 24);
    const undersized = measuredTargets.filter((node) => {
      const rect = node.getBoundingClientRect();
      return rect.width < minTarget || rect.height < minTarget;
    });
    const globeRect = byId('globe-shell')?.getBoundingClientRect();
    const overlayRects = ['globe-controls', 'temporal-map-status', 'terrain-status', 'attribution-status']
      .map((id) => byId(id)?.getBoundingClientRect())
      .filter((rect) => rect && rect.width > 0 && rect.height > 0);
    let overlayCollisions = 0;
    for (let left = 0; left < overlayRects.length; left += 1) {
      for (let right = left + 1; right < overlayRects.length; right += 1) {
        const a = overlayRects[left];
        const b = overlayRects[right];
        const overlapWidth = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const overlapHeight = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (overlapWidth > 1 && overlapHeight > 1) overlayCollisions += 1;
      }
    }
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
      overlay_collision_count: overlayCollisions,
      globe_css_px: {
        width: Math.round(globeRect?.width || 0),
        height: Math.round(globeRect?.height || 0)
      },
      startup_to_idle_ms: runtime.performance.startupToIdleMs,
      average_frame_ms: runtime.performance.averageFrameMs,
      visual_render_ready: runtime.visualReadiness.ready,
      context_source_feature_count: runtime.visualReadiness.contextSourceFeatureCount,
      context_rendered_feature_count: runtime.visualReadiness.contextRenderedFeatureCount,
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
    root.dataset.artemisOverlayCollisionCount = String(overlayCollisions);
    root.dataset.artemisGlobeWidth = String(runtime.acceptanceEvidence.globe_css_px.width);
    root.dataset.artemisGlobeHeight = String(runtime.acceptanceEvidence.globe_css_px.height);
    root.dataset.artemisStartupRecorded = String(runtime.performance.startupToIdleMs !== null);
    root.dataset.artemisStartupToIdleMs = runtime.performance.startupToIdleMs === null
      ? 'diagnostic-only-pending'
      : runtime.performance.startupToIdleMs.toFixed(1);
    root.dataset.artemisAverageFrameMs = runtime.performance.averageFrameMs === null
      ? 'diagnostic-only-pending'
      : runtime.performance.averageFrameMs.toFixed(1);
    root.dataset.artemisVisualReady = String(runtime.visualReadiness.ready);
    root.dataset.artemisContextSourceFeatureCount = String(runtime.visualReadiness.contextSourceFeatureCount);
    root.dataset.artemisContextRenderedFeatureCount = String(runtime.visualReadiness.contextRenderedFeatureCount);
  }

  function verifyEarthContextRender(map, contract) {
    const root = document.documentElement;
    let renderProbePending = false;

    const probe = () => {
      if (runtime.visualReadiness.ready || renderProbePending) return;
      if (!map.getSource('artemis-earth-context') || !map.isSourceLoaded('artemis-earth-context')) return;

      const sourceFeatures = map.querySourceFeatures('artemis-earth-context');
      runtime.visualReadiness.contextSourceFeatureCount = sourceFeatures.length;
      if (!sourceFeatures.length) {
        collectAcceptanceEvidence(contract);
        return;
      }

      renderProbePending = true;
      map.once('render', () => {
        renderProbePending = false;
        const renderedFeatures = map.queryRenderedFeatures({
          layers: ['artemis-present-day-land', 'artemis-present-day-coastline']
        });
        runtime.visualReadiness.contextRenderedFeatureCount = renderedFeatures.length;
        runtime.visualReadiness.ready = renderedFeatures.length > 0;
        collectAcceptanceEvidence(contract);
        if (!runtime.visualReadiness.ready) {
          map.triggerRepaint();
          window.requestAnimationFrame(probe);
        }
      });
      map.triggerRepaint();
    };

    root.dataset.artemisVisualReady = 'false';
    map.on('sourcedata', (event) => {
      if (event.sourceId === 'artemis-earth-context') probe();
    });
    window.requestAnimationFrame(probe);
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

  function renderTemporalStatus(view) {
    const preset = (runtime.viewIndex?.temporal_presets || []).find(
      (candidate) => candidate.preset_id === view.temporal_preset_id
    );
    const comparableViews = (runtime.viewIndex?.views || []).filter(
      (candidate) => viewKey('', candidate.active_layer_refs) === viewKey('', view.active_layer_refs)
    );
    const signatures = new Set(comparableViews.map((candidate) => geometrySignature(candidate.globe)));
    const geometryIsTimeInvariant = comparableViews.length > 1 && signatures.size === 1;
    const recordCount = (view.projection.items || []).length;
    const primitiveCount = (view.globe.primitives || []).length;
    const base = `${preset?.label || view.temporal_preset_id}. ${recordCount} records in the semantic projection.`;
    const explanation = geometryIsTimeInvariant
      ? ' The globe geometry is unchanged across these source-bound dates: only present-day named-settlement reference points are authorized; exact historical positions, routes and Region boundaries remain unknown.'
      : ` ${primitiveCount} authorized spatial primitives are visible for this time/layer view.`;
    setText('temporal-map-status', `${base}${explanation}`);
    document.documentElement.dataset.artemisTemporalGeometryChanged = String(!geometryIsTimeInvariant);
  }

  function updateAlternativeGeometryControl(globe) {
    const control = byId('toggle-alternatives');
    if (!control) return;
    const count = alternativeGeometryCount(globe);
    control.hidden = count === 0;
    control.disabled = count === 0;
    control.setAttribute('aria-pressed', String(runtime.alternativesVisible));
    control.textContent = `Map display: alternative geometry ${runtime.alternativesVisible ? 'shown' : 'hidden'} (${count})`;
    document.documentElement.dataset.artemisAlternativeGeometryCount = String(count);
  }

  function applyAlternativeLayerVisibility(map) {
    if (!map) return;
    for (const layerId of ALTERNATIVE_LAYER_IDS) {
      if (map.getLayer(layerId)) {
        map.setLayoutProperty(
          layerId,
          'visibility',
          runtime.alternativesVisible ? 'visible' : 'none'
        );
      }
    }
  }

  function renderUnresolved(projection) {
    const host = byId('unresolved-list');
    if (!host) return;
    host.innerHTML = '';

    const lossByItem = new Map((projection.losses || []).map((loss) => [loss.item_id, loss]));
    const unresolved = (projection.items || []).filter((item) => item.spatial_status === 'unresolved');
    setText('unresolved-count', unresolved.length);

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
    const geometry = (record.geometries || [])[0] || null;
    const rows = [
      ['object_ref', record.object_ref],
      ['subobject_ref', record.subobject_ref || '—'],
      ['type', record.object_type],
      ['role', record.render_role],
      ['temporal', record.temporal_membership],
      ['spatial', record.spatial_status],
      ['geometry role', geometry?.origin_kind || '—'],
      ['spatial precision', geometry?.spatial_precision || '—']
    ];
    if (record.semantic_flags?.reconstruction_mode) {
      rows.push(['reconstruction', record.semantic_flags.reconstruction_mode]);
      rows.push(['primary geometry', String(record.semantic_flags.is_primary === true)]);
    }
    const dl = document.createElement('dl');
    dl.className = 'identity-list';
    for (const [key, value] of rows) {
      appendText(dl, 'dt', key);
      appendText(dl, 'dd', value);
    }
    host.append(dl);
  }

  function knowledgeDisclosure(host, label, count) {
    const section = document.createElement('details');
    section.className = 'knowledge-section knowledge-disclosure';
    const summary = document.createElement('summary');
    summary.textContent = `${label} · ${count}`;
    section.append(summary);
    host.append(section);
    return section;
  }

  function addEvidence(host, record) {
    const section = knowledgeDisclosure(host, 'Claims & evidence', (record.claims || []).length);
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
  }

  function addUncertainties(host, record) {
    const section = knowledgeDisclosure(host, 'Material uncertainty', (record.uncertainties || []).length);
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
  }

  function addReconstructionAlternatives(host, record) {
    if (record.object_type !== 'Region') return;
    const alternatives = (runtime.data?.projection?.items || []).filter((item) => (
      item.object_type === 'Region'
      && item.object_ref === record.object_ref
      && item.semantic_flags?.reconstruction_mode
    ));
    if (!alternatives.length) return;

    const section = knowledgeDisclosure(host, 'Reconstruction alternatives', alternatives.length);
    const allGeometryWithheld = alternatives.every((alternative) => (
      !(alternative.geometry_refs || []).length || alternative.spatial_status === 'unresolved'
    ));
    appendText(
      section,
      'p',
      allGeometryWithheld
        ? 'These are separate source-bound interpretations. No variant has authorized geometry, so none is drawn as a Region boundary.'
        : 'These are separate source-bound interpretations. Geometry availability is reported per variant; the map control appears when toggleable alternative geometry is present.',
      'empty-note'
    );
    for (const alternative of alternatives) {
      const geometryAvailable = (alternative.geometry_refs || []).length > 0
        && alternative.spatial_status !== 'unresolved';
      const card = document.createElement('article');
      card.className = 'alternative-card';
      appendText(
        card,
        'strong',
        `${alternative.subobject_ref}${alternative.item_id === record.item_id ? ' · selected' : ''}`
      );
      appendText(
        card,
        'p',
        `${alternative.semantic_flags.reconstruction_mode} · primary=${alternative.semantic_flags.is_primary === true} · spatial=${alternative.spatial_status}`,
        'record-meta'
      );
      appendText(
        card,
        'p',
        geometryAvailable
          ? `Geometry available (${alternative.geometry_refs.length} reference${alternative.geometry_refs.length === 1 ? '' : 's'}); rendered by its semantic layer.`
          : 'Geometry withheld; not rendered.',
        geometryAvailable ? 'record-meta' : 'warning'
      );
      section.append(card);
    }
  }

  function addCoverage(host) {
    const coverage = runtime.data?.projection?.coverage || {};
    const policy = coverage.coverage_policy || {};
    const exclusions = policy.known_exclusion_ids || [];
    const section = knowledgeDisclosure(host, 'Coverage / corpus limits', exclusions.length);
    appendText(
      section,
      'p',
      'The corpus is explicitly incomplete. Missing records or geometry must not be interpreted as historical absence.',
      'warning'
    );
    const dl = document.createElement('dl');
    dl.className = 'identity-list';
    for (const [key, value] of [
      ['corpus completeness', policy.corpus_completeness || 'unavailable'],
      ['absence semantics', policy.absence_semantics || 'unavailable'],
      ['source scope', policy.source_scope || 'unavailable'],
      ['coverage manifest', coverage.coverage_manifest_ref || 'unavailable']
    ]) {
      appendText(dl, 'dt', key);
      appendText(dl, 'dd', value);
    }
    section.append(dl);
    if (exclusions.length) {
      const list = document.createElement('ul');
      list.className = 'coverage-list';
      for (const exclusion of exclusions) appendText(list, 'li', exclusion);
      section.append(list);
    }
  }

  function addProjectionLosses(host, record) {
    const section = knowledgeDisclosure(host, 'Projection loss', (record.projection_losses || []).length);
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
    addReconstructionAlternatives(card, record);
    addCoverage(card);
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

  function clearCanonicalSelection(message = 'No semantic object selected.', options = {}) {
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
    for (const row of document.querySelectorAll('.unresolved-item[aria-pressed="true"]')) {
      row.setAttribute('aria-pressed', 'false');
    }
    if (options.syncUrl !== false) syncUrlState();
  }

  function selectKnowledgeItem(itemId, options = {}) {
    const record = runtime.knowledgeByItem.get(itemId);
    const projectionItem = currentProjectionItem(itemId);
    if (!record || !projectionItem) {
      clearCanonicalSelection(`No active projection record exists for ${itemId}.`, options);
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
    if (options.syncUrl !== false) syncUrlState();
  }

  function renderSelection(properties) {
    const itemId = properties.item_id;
    if (itemId) {
      selectKnowledgeItem(itemId, { focus: true });
      return;
    }
    clearCanonicalSelection('Rendered feature has no semantic item_id and cannot be resolved.');
  }

  function renderCapabilitySelection() {
    clearCanonicalSelection(
      'Renderer capability path selected. This geometry has no World Model object_ref and cannot be resolved as historical knowledge.'
    );
  }

  function syncExplorerControls() {
    const presets = runtime.viewIndex?.temporal_presets || [];
    const presetIndex = Math.max(0, presets.findIndex(
      (preset) => preset.preset_id === runtime.activeTemporalPresetId
    ));
    const range = byId('temporal-preset');
    const presetLabel = presets[presetIndex]?.label || runtime.activeTemporalPresetId;
    if (range) {
      range.value = String(presetIndex);
      range.setAttribute('aria-valuetext', presetLabel);
    }
    setText('temporal-preset-value', presetLabel);
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
    renderTemporalStatus(next);
    renderUnresolved(next.projection);
    syncExplorerControls();
    updateAlternativeGeometryControl(next.globe);
    applyAlternativeLayerVisibility(runtime.map);

    const itemIds = new Set((next.projection.items || []).map((item) => item.item_id));
    if (priorSelection && itemIds.has(priorSelection)) {
      selectKnowledgeItem(priorSelection, { syncUrl: false });
    } else if (options.initial) {
      const primaryObjectRef = next.state.selection?.primary_object_ref;
      const primaryItem = (next.projection.items || []).find(
        (item) => item.object_ref === primaryObjectRef
      );
      if (primaryItem) selectKnowledgeItem(primaryItem.item_id, { syncUrl: false });
      else clearCanonicalSelection('No semantic object selected.', { syncUrl: false });
    } else if (priorSelection) {
      clearCanonicalSelection(
        'Selection cleared: the object is outside the active time/layer projection.',
        { syncUrl: false }
      );
    } else {
      clearCanonicalSelection('No semantic object selected.', { syncUrl: false });
    }

    const status = byId('interaction-status');
    if (status) {
      status.textContent = `${next.projection.items.length} projected records · ${runtime.activeLayerRefs.length} active layers · selection and picking synchronized.`;
    }
    document.documentElement.dataset.artemisTemporalPreset = temporalPresetId;
    document.documentElement.dataset.artemisLayerCount = String(runtime.activeLayerRefs.length);
    if (options.syncUrl !== false) syncUrlState();
    return next;
  }

  function restoreExplorerStateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const defaultView = (runtime.viewIndex?.views || []).find(
      (view) => view.view_id === runtime.viewIndex.default_view_id
    );
    if (!defaultView) return;
    const requestedPreset = params.get('time') || defaultView.temporal_preset_id;
    const requestedLayers = params.has('layers')
      ? params.get('layers').split(',').filter(Boolean)
      : defaultView.active_layer_refs;
    const view = runtime.viewByKey.get(viewKey(requestedPreset, requestedLayers)) || defaultView;
    applySemanticView(view.temporal_preset_id, view.active_layer_refs, { syncUrl: false });
    const requestedItem = params.get('item');
    if (requestedItem) selectKnowledgeItem(requestedItem, { syncUrl: false });
    else clearCanonicalSelection('No semantic object selected.', { syncUrl: false });
    syncUrlState();
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
      applyAlternativeLayerVisibility(map);
      event.currentTarget.setAttribute('aria-pressed', String(runtime.alternativesVisible));
      updateAlternativeGeometryControl(runtime.data?.globe);
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
    applySemanticView(initialView.temporal_preset_id, initialView.active_layer_refs, { initial: true, syncUrl: false });
    const requestedItem = params.get('item');
    if (requestedItem) selectKnowledgeItem(requestedItem, { syncUrl: false });
    syncUrlState();
    window.addEventListener('popstate', restoreExplorerStateFromUrl);
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

    map.on('error', (event) => {
      console.warn('[ARTEMIS:globe-spike] MapLibre runtime warning', event?.error || event);
    });

    map.on('load', () => {
      if (typeof map.setProjection === 'function') map.setProjection({ type: 'globe' });
      verifyEarthContextRender(map, acceptanceProfiles);
      addContextLayers(map, context);
      addSemanticLayers(map, runtime.data.globe);
      applyAlternativeLayerVisibility(map);
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
