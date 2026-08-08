# ARTEMIS — Globe / Renderer Architecture v1

## Status

- Type: working architecture decision record.
- Date: 2026-08-08.
- Parent issue: #339.
- Scope: parallel 3D Globe R&D architecture.
- Foundation: `ARTEMIS_CONCEPT.md`, `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`, `UNCERTAINTY_SEMANTICS_CONTRACT.md`.
- Capability status: architecture/R&D only; this document does not make 3D `PUBLIC NOW`.

## 1. Decision

ARTEMIS will support multiple presentation renderers over one spatial-temporal world model.

The current 2D MapLibre runtime and the experimental 3D Earth runtime must not evolve into separate products, separate historical schemas or separate sources of truth.

Target flow:

```text
Curated Sources / Data
        ↓
Spatial-Temporal World Model
Entity · Event · State · Process · Trajectory · Region
Claim · EvidenceLink · Uncertainty · Layer
        ↓
Versioned World Slice / Query Result
        ↓
Renderer-neutral Explorer State
        ↓
Render Projection Layer
        ↓
┌──────────────────┬──────────────────┬──────────────────┐
│ 2D Map renderer  │ 3D Globe renderer│ future renderer  │
│ current MapLibre │ experimental      │ VR/AR/etc.       │
└──────────────────┴──────────────────┴──────────────────┘
```

The renderer changes how the model is projected and viewed. It does not own what the model means.

## 2. Why this is required

Foundation v3 makes space and time mandatory coordinates, but explicitly allows different visualizations: 2D map, 3D globe, local scene, timeline, animation and future VR/AR.

The current public implementation predates that target architecture:

- `data/features.geojson` is a Point-only public map artifact;
- `js/map.js` filters the current payload to Point geometry;
- MapLibre-specific state and rendering behavior are tightly coupled;
- current public data contracts are optimized for Architecture Atlas rather than the full World Model.

Building a globe directly on top of that Point-only contract would make the current compatibility projection the de facto domain model. That would block Trajectory, temporal Region, Process and later 3D/vertical semantics.

## 3. Invariants

### 3.1 One semantic core

`Entity`, `Event`, `State`, `Process`, `Trajectory`, `Region`, `Relation`, `Claim`, `EvidenceLink`, `Uncertainty`, `Layer` and coverage semantics belong to the World Model contracts.

A renderer may not redefine them.

### 3.2 One object identity

The same knowledge object keeps the same canonical identity in 2D and 3D projections.

Picking a visual primitive returns the World Model object identity, not a renderer-owned historical ID.

### 3.3 Renderer payloads are projections

Renderer-ready GeoJSON, primitives, meshes, tiles or engine-specific objects are derived projections.

They are not canonical historical truth and must be reproducible from a versioned source package or World Slice.

### 3.4 Time is resolved before rendering

The shared selected instant/interval and temporal inclusion rules determine the active knowledge state before renderer-specific styling.

A renderer cannot use an independent time filter that changes model meaning.

### 3.5 Uncertainty survives projection

Approximate time, inferred routes, disputed boundaries, alternative reconstructions and unknown gaps must remain distinguishable after projection.

A renderer that cannot represent a required uncertainty state must fail explicitly or use a documented fallback; it may not silently render false precision.

### 3.6 Derived proximity is not historical relation

2D and 3D renderers may compute or display spatial proximity, overlap and co-presence, but must preserve the relation ladder and cannot promote those signals into documented encounter/influence/causality.

### 3.7 Geospatial assets are infrastructure

Terrain, elevation, basemap imagery, raster/vector tiles and 3D tiles are rendering/geospatial assets.

They require provenance, licensing, coverage, resolution and coordinate metadata, but they do not become historical knowledge objects merely because they are shown on the globe.

Historical/reconstructed coastline, terrain or boundaries are different: when they make historical claims they must use World Model temporal validity, provenance and uncertainty semantics.

## 4. Current compatibility boundary

The current runtime remains valid and supported:

```text
Airtable → ETL → data/features.geojson → MapLibre 2D
```

For current Architecture Atlas publication, `data/features.geojson` remains the canonical public map source.

This status is intentionally narrower than the North Star model. It must not be generalized into the statement that Point-only GeoJSON is the canonical representation of all ARTEMIS knowledge.

## 5. Target projection boundary

A render projection consumes:

```text
WorldSlice
+ ExplorerState
+ renderer capability profile
```

and produces renderer-ready data while preserving references back to:

- canonical object ID;
- object type;
- temporal extent/version;
- active/inactive state;
- geometry or place provenance;
- uncertainty references;
- Claim/Evidence/Source references where material;
- layer references;
- alternative reconstruction identity;
- coverage/known-gap context where relevant.

Projection may be lossy only when the loss is declared and semantically safe.

## 6. Shared Explorer State

Renderer-neutral state should own at minimum:

- selected instant or interval;
- active layers;
- selected knowledge object;
- selected local/global context;
- active trajectory segment where applicable;
- active Region version/reconstruction where applicable;
- source/uncertainty/coverage focus;
- view intent sufficient for restore/share without serializing engine instances.

Renderer-local state may own:

- hover primitive;
- frame/render caches;
- GPU resources;
- engine camera object;
- tile cache;
- temporary picking buffers;
- visual-only transitions.

## 7. Geometry and Earth coordinates

World Model spatial semantics remain richer than the current public Point contract and include point, path, polygon/multipolygon, named place, alternative geometry and temporal Region validity.

The Globe track must explicitly define:

- horizontal coordinate reference assumptions;
- conversion boundary to Earth-fixed/globe engine coordinates;
- altitude/height semantics when introduced;
- vertical datum policy when height materially affects a claim;
- surface-clamped vs absolute-height geometry;
- LOD/generalization that does not alter historical meaning.

Height must not be added to canonical data merely because a renderer supports it.

## 8. Terrain and imagery policy

A geospatial asset manifest should eventually identify:

- asset/provider ID;
- asset kind;
- coverage bounds;
- horizontal CRS;
- vertical datum/height model if applicable;
- resolution / LOD information;
- source/provenance;
- license and attribution;
- retrieval/deployment configuration;
- temporal applicability;
- whether it is modern context, analytical surface or historical reconstruction.

A modern terrain surface can provide present-day physical context. It must not imply that the same terrain/coastline is historically valid for all selected dates.

## 9. Repository/runtime boundary

During R&D:

- current `index.html` + `js/map.js` remain the public 2D baseline;
- Globe code must live behind an explicit experimental boundary and must not enter the Pages artifact accidentally;
- shared contracts can be introduced incrementally without moving the whole repository to a new framework/layout;
- an `apps/` + shared-package structure is allowed later only when the second runtime proves enough value to justify migration.

The long-term rule is **one domain core, multiple registered presentation runtimes**, not one frontend entrypoint at any cost.

## 10. CI and semantic parity

A second renderer requires three distinct classes of checks:

1. **World Model checks** — validity of domain/epistemic semantics.
2. **Projection/parity checks** — same World Slice + Explorer State resolves to the same active object identities and uncertainty/evidence semantics across renderers.
3. **Renderer checks** — build, browser, visual and performance checks specific to MapLibre or Globe runtime.

Semantic parity is not screenshot parity.

For the same state, 2D and 3D must agree on at least:

- active objects;
- selected object;
- temporal boundary inclusion;
- active Region geometry version;
- trajectory segment kind;
- uncertainty/alternative reconstruction references;
- documented Relation vs derived co-presence distinction.

## 11. Execution tracks

The existing product-validation path remains:

```text
#331 → #332 → #333 → #334
```

The parallel Globe R&D path is:

```text
#339
├── #340 renderer-neutral Explorer State
├── #341 World Model → Render Projection contract
├── #342 terrain/imagery/geospatial asset contract
├── #343 minimal 3D Earth runtime spike
├── #344 cross-renderer semantic parity tests
└── #345 repository/runtime + CI boundary
```

Neither path should silently redefine the other.

## 12. Promotion gate

The Globe track may move from experimental R&D toward product scope only when there is executable evidence that it adds value or is required by the ARTEMIS interaction model.

Before promotion:

- no `PUBLIC NOW` claim;
- no replacement of #333 with 3D;
- no mandatory backend solely for Globe;
- no universal terrain/imagery promise;
- no large repository/framework migration.

Promotion requires an explicit decision plus synchronized updates to `PROJECT_TRUTH`, product scope, priorities, project structure and release/deployment documentation.

## 13. Immediate next step

Execute #340 and #341 first, while #343 may run a tightly bounded engine/runtime spike using provisional adapters. The prototype must converge on the reviewed state/projection contracts before it can be considered architecture evidence.