# ARTEMIS — World Model → Render Projection Contract v1

## Status

- Type: working executable contract proposal.
- Date: 2026-08-08.
- Parent issue: #341.
- Architecture: #339 / PR #346 (merged).
- Explorer State: #340 / PR #347 (merged).
- Semantic dependencies: Foundation v3 World Model, reviewed #329 fixtures, reviewed #330 uncertainty semantics.
- Relation boundary: Relation rendering is not part of projection v1; #331 remains authoritative for relation predicates and evidence requirements.
- Capability status: R&D projection contract only; no 3D Globe or new public data source is introduced.

## 1. Purpose

Render Projection is the explicit boundary between ARTEMIS knowledge/query state and a presentation renderer.

It answers:

> Given one pinned World Slice and one valid Explorer State, which spatial-temporal objects are active or possibly active, which geometry is actually supported, what uncertainty/evidence must travel with it, and what may a renderer draw without inventing meaning?

Target flow:

```text
World Model / World Slice
        +
Renderer-neutral Explorer State
        ↓
Temporal + spatial resolution
        ↓
Render Projection Package
        ↓
2D GeoJSON adapter | Globe cartographic adapter | future adapter
```

The projection package is derived and reproducible. It is not a new source of historical truth.

## 2. Why an intermediate projection package is required

Directly giving a renderer the World Model creates several failure modes:

- MapLibre and a Globe engine may implement different time filtering;
- an engine may connect two documented trajectory endpoints with a visually plausible but unsupported line;
- a disputed Region may be reduced to one silent winner;
- a `named_place` without resolved geometry may acquire guessed coordinates;
- renderer-specific primitive IDs may replace canonical object identity;
- source/evidence/uncertainty metadata may disappear between model and picking/detail UI.

The intermediate package makes these decisions deterministic and testable before any engine draws pixels.

## 3. Projection v1 scope

Projection v1 supports spatial projection for:

- `Event`;
- `State`;
- `Process` stages;
- `Trajectory` segments;
- `Region` geometry versions;
- selected/context `Entity` records as semantic items, including explicitly unresolved spatial items.

Projection v1 deliberately excludes:

- `Relation` rendering/promotion semantics;
- volume/voxel/mesh historical geometry;
- elevation/vertical datum semantics;
- terrain/imagery provider semantics;
- causal/counterfactual branches;
- renderer styling/color/animation rules.

Those exclusions are visible. They must not be silently approximated.

## 4. Inputs

A projection build requires exactly:

1. versioned World Model / World Slice package;
2. valid Explorer State;
3. projection schema/version;
4. adapter capability profile when materializing a renderer payload.

The Explorer State `world_slice_ref` and `dataset_identity` must exactly match the source package.

## 5. Neutral Render Projection Package

Conceptual shape:

```text
RenderProjectionPackage
├── schema_version
├── projection_id
├── source
│   ├── world_slice_ref
│   ├── dataset_identity
│   └── explorer_state_ref
├── temporal_selection
├── coordinate_reference: EPSG:4326
├── vertical_semantics: not_modeled
├── included_object_types[]
├── deferred_object_types[]
├── active_object_refs[]
├── possible_active_object_refs[]
├── geometries[]
│   ├── geometry_ref
│   ├── geometry
│   ├── owner_ref
│   ├── owner_subobject_ref?
│   ├── origin_kind
│   ├── spatial_precision
│   ├── claim_refs[]
│   └── uncertainty_refs[]
├── items[]
│   ├── item_id
│   ├── object_ref
│   ├── object_type
│   ├── subobject_ref?
│   ├── render_role
│   ├── temporal_membership
│   ├── spatial_status
│   ├── geometry_refs[]
│   ├── place_ref?
│   ├── layer_refs[]
│   ├── claim_refs[]
│   ├── uncertainty_refs[]
│   ├── evidence_link_refs[]
│   ├── source_refs[]
│   └── semantic_flags
├── losses[]
└── coverage
```

### 5.1 Identity

`object_ref` and `subobject_ref` always use World Model identities.

`item_id` is a projection-local deterministic ID, but picking/detail resolution must return `object_ref` + optional `subobject_ref`.

Renderer primitive IDs may equal `item_id`; they may never replace `object_ref` in semantic state.

### 5.2 Geometry registry

Geometry is deduplicated into `geometries[]`.

An item references one or more `geometry_refs`. This allows a Region geometry version to be reused by:

- the Region item itself;
- a State whose spatial extent is `region_ref`;
- an active Process stage whose spatial extent is that Region.

Geometry reuse is derived projection reuse, not a claim that State/Process/Region are the same knowledge object.

### 5.3 Temporal membership

Projection v1 distinguishes:

- `active` — canonical interval/instant semantics include the selected time;
- `possible_active` — an approximate/alternative temporal reconstruction can include the selected time but the projection must not present it as exact;
- `atemporal_context` — a selected/context Entity has no first-class temporal extent and is carried for identity/detail purposes;
- inactive objects are omitted from the active projection package.

Projection must not create its own historical date interpretation beyond the accepted temporal/uncertainty semantics.

### 5.4 Spatial status

Each projected item is:

- `resolved` — supported geometry exists;
- `unresolved` — semantically relevant, but no supported geometry is available;
- `not_spatial` — object is carried for identity/context without a spatial assertion.

`unresolved` is a valid projection result. It is preferable to invented geometry.

## 6. Spatial resolution rules

### 6.1 Explicit geometry

If `spatial_extent.geometry` is present and allowed, projection may create a geometry record directly.

Supported v1 geometry kinds:

- Point;
- LineString;
- Polygon;
- MultiPolygon.

### 6.2 Named place

If an extent contains only `place_ref` and the referenced Place has no independently resolved canonical geometry, projection records:

```text
spatial_status = unresolved
loss_kind = geometry_unresolved
reason = named_place_without_resolved_geometry
```

Forbidden:

- deriving coordinates from a nearby event;
- choosing a centroid from an unrelated Region;
- geocoding a label during projection;
- copying coordinates from a modern service without provenance.

A later place-geometry contract may resolve the reference explicitly.

### 6.3 Region reference

`region_ref` resolves only to Region geometry versions temporally valid for the Explorer State.

When alternatives are requested/required:

- primary and alternative current geometries may coexist;
- `reconstruction_mode`, `is_primary` and uncertainty refs remain visible;
- no silent winner is chosen.

### 6.4 Trajectory

A Trajectory is projected segment by segment.

- explicit path geometry may produce a LineString;
- presence at a resolved point/place may produce a point-like item;
- `inferred_gap` with unknown spatial extent produces **no connecting line**;
- two endpoint observations never authorize interpolation;
- segment kind and uncertainty refs survive into every adapter.

### 6.5 Process

A Process is projected through active/possibly-active stages when stages exist.

The adapter may visualize current stage geometry, but cannot transform an analytical grouping into a directional diffusion arrow unless the World Model explicitly supports such geometry/meaning.

## 7. Epistemic preservation

For every item, projection carries:

- `claim_refs`;
- `uncertainty_refs`;
- `evidence_link_refs` derived from its claims;
- `source_refs` derived from those EvidenceLinks.

Geometry records preserve their own basis claim/uncertainty refs where applicable.

A renderer may hide detailed citation UI behind interaction, but the payload cannot discard the references needed to open it.

## 8. Loss model

Every material projection loss is explicit:

```text
loss_id
item_id
loss_kind
cause
severity
reason
place_ref?
```

Causes:

- `source_model_gap` — input semantics exist but supported geometry is missing;
- `renderer_capability` — neutral projection has supported semantics the adapter cannot represent.

Rules:

- `source_model_gap` may produce an unresolved item while preserving semantic/epistemic metadata;
- material `renderer_capability` loss is fail-closed for that adapter;
- cosmetic differences are not semantic losses;
- a loss record cannot be used as permission to invent a substitute.

## 9. 2D MapLibre adapter shape

Projection v1 defines a **future adapter shape**, not a replacement for current public `data/features.geojson`.

Output:

```text
FeatureCollection
└── Feature[]
    ├── id = item_id
    ├── geometry = resolved projection geometry
    └── properties
        ├── object_ref
        ├── object_type
        ├── subobject_ref?
        ├── render_role
        ├── temporal_membership
        ├── layer_refs
        ├── claim_refs
        ├── uncertainty_refs
        ├── evidence_link_refs
        ├── source_refs
        └── semantic_flags
```

Unresolved items are emitted separately in adapter metadata and are not converted into fake GeoJSON points.

Supported adapter geometries: Point, LineString, Polygon, MultiPolygon.

## 10. 3D Globe adapter shape

Because #343 has not selected an engine and #342 owns terrain/elevation policy, Globe v1 remains engine-neutral.

Output:

```text
GlobeProjection
├── coordinate_reference: EPSG:4326
├── vertical_semantics: not_modeled
├── primitives[]
│   ├── primitive_id = item_id
│   ├── object_ref
│   ├── subobject_ref?
│   ├── primitive_kind
│   │   ├── cartographic_point
│   │   ├── cartographic_polyline
│   │   ├── cartographic_polygon
│   │   └── cartographic_multipolygon
│   ├── coordinates
│   └── same semantic/epistemic refs
└── unresolved_items[]
```

Coordinates contain longitude/latitude only in v1.

The adapter does **not** add elevation, terrain clamping semantics or WGS84 ellipsoid height as historical data. #342 must define those policies before a production Globe adapter can depend on them.

## 11. Capability failure

Each adapter declares supported neutral geometry/semantic capabilities.

If a neutral package contains a material supported geometry that the adapter cannot represent, the adapter must fail with an explicit capability error.

Examples:

- future `volume` geometry presented to v1 adapter → fail;
- disputed alternative geometry where adapter can only accept one reconstruction → fail rather than silently choose;
- unresolved named place → preserve unresolved metadata, because the problem is a source-model gap rather than adapter capability.

## 12. Deterministic fixture target

The executable #341 fixture uses:

- reviewed `fixtures/world_model/v1/package.json`;
- merged `fixtures/explorer_state/v1/state-1504-local-global.json`.

At `1504-03-01`, the fixture intentionally exercises:

- explicit point geometry (`event-far-observation`);
- active Region v2 + disputed alternative geometry;
- active State/Process geometry resolved through Region references;
- named-place objects without independent geometry;
- active Trajectory presence and inferred-gap semantics without invented route lines;
- selected/local/global context identity;
- evidence/source/uncertainty propagation.

This is synthetic contract evidence only.

## 13. Adapter parity required by #341

For one neutral package, 2D and Globe outputs must preserve the same set of **rendered item IDs** and the same semantic identity/epistemic fields for those items.

This is a narrow adapter-preservation assertion.

Full cross-renderer semantic parity, UI state reciprocity and promotion gates remain owned by #344.

## 14. Non-goals

- replacing current public `features.geojson`;
- rewriting `js/map.js`;
- choosing Cesium/MapLibre Globe/Three.js or another engine;
- terrain/elevation provider policy (#342);
- implementing product 3D runtime (#343);
- relation visualization before #331 semantics are accepted;
- visual styling, clustering, label placement or LOD;
- historical route interpolation.

## 15. Exit criteria

The executable portion of #341 is ready when:

- neutral projection schema exists;
- deterministic builder produces neutral, 2D and Globe fixtures from the same World Slice + Explorer State;
- named-place and unknown-route gaps remain explicit and geometry-free;
- current/alternative Region geometry remains distinguishable;
- evidence/source/uncertainty refs survive projection;
- both adapters preserve canonical object/subobject IDs;
- unsupported material capabilities fail explicitly;
- checked-in fixtures are drift-checked in CI;
- no public/runtime capability or data-source claim changes.