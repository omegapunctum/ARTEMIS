# ARTEMIS — Globe Runtime Spike Engine Decision v1

## Status

- Type: working R&D decision record.
- Date: 2026-08-08.
- Issue: #343.
- Dependencies: #340 / #341 / #342 completed.
- Selected engine for the first bounded spike: **MapLibre GL JS 5.24.0**.
- Selection scope: #343 only. This is not a permanent product-engine decision and does not upgrade the current public runtime.

## 1. Decision question

Which browser engine gives ARTEMIS the smallest credible 3D Earth experiment that can consume the merged renderer-neutral contracts without creating a second semantic model?

The engine must be judged as rendering infrastructure, not as a source of historical meaning.

## 2. Current ARTEMIS baseline

The current public frontend loads MapLibre GL JS `4.7.1` directly from unpkg in `index.html` and uses vanilla JavaScript. `js/map.js` is Point-only compatibility code over `data/features.geojson`.

The public runtime must remain untouched by #343.

Therefore the spike uses its own generated static artifact and pins its own engine version. No `index.html`, `js/map.js`, public `data/*`, service-worker or production dependency is changed by the spike.

## 3. Candidates

### A. MapLibre GL JS 5.24.0 — selected for first spike

Current official documentation demonstrates:

- globe projection;
- terrain / raster DEM rendering;
- GeoJSON/vector layers;
- feature queries/picking;
- custom 3D layers, including globe examples and Three.js integration;
- browser/static usage without a required ARTEMIS backend.

Official references checked 2026-08-08:

- https://maplibre.org/maplibre-gl-js/docs
- https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/
- https://maplibre.org/maplibre-gl-js/docs/examples/create-a-heatmap-layer-on-a-globe-with-terrain-elevation/
- https://maplibre.org/maplibre-gl-js/docs/examples/add-a-3d-model-to-globe-using-threejs/
- https://maplibre.org/maplibre-gl-js/docs/API/type-aliases/QueryRenderedFeaturesOptions/
- https://github.com/maplibre/maplibre-gl-js/blob/main/LICENSE.txt

Strengths for #343:

- lowest conceptual integration cost with current ARTEMIS frontend;
- natural consumption of projected cartographic Point/LineString/Polygon/MultiPolygon;
- enough globe + terrain capability to validate the architecture before adding another engine;
- straightforward static prototype;
- BSD-3-Clause engine license.

Risks:

- current public ARTEMIS is still on MapLibre 4.7.1, so the spike must not silently become an upgrade PR;
- MapLibre is still primarily map/style/tiles oriented rather than a dedicated geospatial scene engine;
- deep 3D Tiles / volumetric / planetary-scene requirements may later justify another renderer;
- custom globe layers require careful projection/subdivision handling.

Decision: **use for #343, isolated from public runtime**.

### B. CesiumJS — retained alternative

Current official documentation demonstrates:

- a native ellipsoidal 3D globe;
- terrain-provider abstraction, including ellipsoid and streamed terrain paths;
- GeoJSON loading;
- scene picking;
- first-class geospatial 3D / 3D Tiles ecosystem.

Official references checked 2026-08-08:

- https://cesium.com/learn/cesiumjs-learn/cesiumjs-terrain/
- https://cesium.com/learn/cesiumjs/ref-doc/TerrainProvider.html
- https://cesium.com/learn/cesiumjs/ref-doc/CesiumTerrainProvider.html
- https://cesium.com/learn/cesiumjs/ref-doc/GeoJsonDataSource.html
- https://cesium.com/learn/cesiumjs/ref-doc/Scene.html
- https://github.com/CesiumGS/cesium/blob/main/LICENSE.md

Strengths:

- strongest dedicated 3D geospatial/globe model of the evaluated candidates;
- mature terrain and 3D Tiles path;
- explicit scene picking and globe primitives;
- Apache-2.0 engine license.

Why not first:

- introduces a second rendering stack immediately before ARTEMIS has proven that it needs one;
- higher integration and future dual-renderer maintenance cost;
- some high-quality hosted terrain/imagery workflows involve separate provider/account/token decisions that #342 intentionally keeps outside the engine decision;
- #343 is a minimum architecture proof, not yet a final planetary-renderer selection.

Decision: **reserve as escalation candidate** if MapLibre spike cannot satisfy semantic parity, terrain/3D extensibility or performance needs.

### C. Three.js — rejected as primary geospatial engine for #343

Official WebGLRenderer documentation confirms a general-purpose WebGL scene renderer, not an ARTEMIS-ready globe/terrain/geospatial data model.

Official reference checked 2026-08-08:

- https://threejs.org/docs/pages/WebGLRenderer.html

Three.js remains useful *inside* a geospatial engine/custom layer for bespoke 3D content, but choosing it as the primary #343 engine would force ARTEMIS to own globe projection, terrain tiling, geospatial precision, picking conventions and provider integration too early.

Decision: **not primary for #343**.

## 4. Selection criteria

The executable comparison fixture scores only #343 requirements:

1. interactive globe/ellipsoid;
2. terrain/elevation-capable path;
3. Point/Line/Polygon rendering;
4. canonical picking/selection plumbing;
5. attribution/provider integration;
6. static/browser deployment without required ARTEMIS backend;
7. compatibility with current renderer-neutral projection;
8. isolation from domain semantics;
9. integration risk for the current vanilla-JS repository;
10. future 3D extensibility.

A candidate with a required `fail` cannot be selected.

## 5. Spike isolation

The runtime will not be committed as another root/public HTML entrypoint.

Repository source lives under `scripts/globe_spike/` and `fixtures/globe_runtime/`. A build script generates a self-contained static spike into an output directory. CI can upload that generated directory as an artifact.

This keeps GitHub Pages / current `index.html` unchanged until #345 decides the permanent repository/deployment boundary.

## 6. Data flow

The spike must consume:

```text
reviewed World Model fixture
        +
merged Explorer State
        ↓
merged Render Projection builder
        ↓
neutral projection + Globe adapter payload
        ↓
MapLibre Globe 5.24.0 experimental runtime
```

It must not read `data/features.geojson` as its historical source.

## 7. Trajectory rule

The reviewed fixture deliberately marks Mara Vale's route gap as unknown and prohibits invented route geometry.

Therefore:

- the semantic Trajectory/gap is shown as unresolved/uncertain and is **not** connected by a line;
- a separate `renderer_capability_path` fixture verifies polyline rendering only;
- the capability path has no World Model `object_ref`, cannot be picked as historical knowledge and is visually labelled non-semantic.

This is stricter than drawing a plausible line and is required by the existing uncertainty contract.

## 8. Terrain rule

#343 proves an elevation-capable adapter path without selecting a production terrain provider.

The generated runtime reads the #342 geospatial manifest. The default synthetic terrain asset does not contain real terrain bytes, so the runtime uses a globe surface and reports the terrain provider as synthetic/unavailable rather than inventing elevation.

A real network terrain provider can be evaluated later only through a manifest that passes #342 provider, vertical-reference, provenance, license, cache and secret rules.

## 9. Exit / escalation

Keep MapLibre after #343 only if the spike demonstrates:

- deterministic globe rendering from the shared projection;
- canonical picking;
- explicit uncertainty handling;
- acceptable startup/render behavior;
- credible terrain/provider adapter path;
- no semantic fork.

Escalate to a CesiumJS comparison spike if any of these materially fail, especially deep terrain/3D Tiles/scene extensibility or geospatial precision requirements.

The final repository/deployment decision remains #345.