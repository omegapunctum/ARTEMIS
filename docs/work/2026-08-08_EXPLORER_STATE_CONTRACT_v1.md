# ARTEMIS — Renderer-neutral Explorer State Contract v1

## Status

- Type: working executable contract proposal.
- Date: 2026-08-08.
- Parent issue: #340.
- Architecture dependency: #339 / PR #346.
- Semantic dependencies: Foundation v3 World Model, reviewed #329 fixtures, reviewed #330 uncertainty semantics.
- Relation dependency: no predicate semantics are redefined here; #331 remains authoritative for relation meaning.
- Capability status: R&D contract only; this document does not implement or publish a 3D Globe.

## 1. Purpose

Explorer State is the smallest serializable state that answers:

> Given one versioned World Slice, what spatial-temporal configuration is the user currently examining, independent of whether it is rendered by MapLibre, a 3D Earth engine or another future renderer?

It exists to prevent renderer engines from becoming owners of ARTEMIS meaning.

The state determines **what the user is examining**. A renderer determines **how that state is drawn**.

## 2. Boundary

Explorer State owns:

- selected time instant/interval;
- active thematic layers;
- selected canonical knowledge-object IDs;
- local/global contextual focus;
- active trajectory segment and Region geometry/reconstruction where explicitly selected;
- comparison scope;
- mandatory epistemic-display intent;
- renderer-neutral spatial view intent;
- World Slice and dataset identity required for deterministic restore.

Explorer State does not own:

- MapLibre map instances;
- Cesium/other globe viewer instances;
- WebGL/GPU resources;
- tile caches;
- DOM elements;
- hover/picking buffers;
- pixel coordinates;
- engine-specific `zoom`, `pitch`, `bearing`, camera matrices or scene objects;
- derived visible-object lists that can be recomputed from World Slice + state;
- historical facts, geometry or uncertainty themselves.

## 3. Contract shape

```text
ExplorerState
├── schema_version
├── state_id
├── world_slice_ref
├── dataset_identity
├── temporal_selection
│   ├── mode: instant | interval
│   ├── start
│   ├── end
│   ├── precision
│   └── calendar
├── active_layer_refs[]
├── selection
│   ├── primary_object_ref?
│   ├── selected_object_refs[]
│   └── comparison_object_refs[]
├── context
│   ├── local_context_refs[]
│   ├── global_context_refs[]
│   └── derived_observation_refs[]
├── active_focus
│   ├── trajectory_ref?
│   ├── trajectory_segment_ref?
│   ├── region_ref?
│   ├── region_geometry_ref?
│   └── reconstruction_ref?
├── comparison_scope
│   ├── mode
│   └── reference_refs[]
├── epistemic_display
│   ├── show_material_uncertainty
│   ├── show_alternatives
│   └── show_corpus_limits
└── view_intent
    ├── kind: bounds | focus_object | global
    ├── bbox?              # WGS84 geographic bounds
    ├── target_ref?
    └── coordinate_reference
```

## 4. Core invariants

### 4.1 Dataset-pinned restore

`world_slice_ref` and `dataset_identity` are required.

A saved state cannot silently restore against a different World Slice/dataset version. Compatibility migration must be explicit.

### 4.2 Canonical references only

Every object reference resolves into the pinned World Slice package or its registered derived-observation set.

Renderer primitive IDs are forbidden as semantic references.

### 4.3 Time is user/query state, not evidence

`temporal_selection` expresses the time the user asks ARTEMIS to evaluate. It does not assert that an event occurred exactly at that time.

Historical temporal precision/uncertainty remains on World Model objects and is evaluated by the temporal semantics contract.

For `mode=instant`, `start == end` is required.

### 4.4 Visibility is derived

The state does not persist `visible_object_ids` as truth.

Active objects are recomputed deterministically from:

```text
WorldSlice + temporal_selection + active_layer_refs + model semantics
```

Persisting a stale visibility list would let renderers disagree after data/model changes.

### 4.5 Selection is not relation

Selecting two people, events or regions creates no Relation. `comparison_object_refs` are comparison state only.

### 4.6 Active trajectory/region detail is explicit

When a user drills into a specific trajectory segment or Region reconstruction, the chosen IDs are stored explicitly.

A renderer may not replace an `inferred_gap` with generated path geometry or silently replace one disputed Region geometry with another.

### 4.7 Material uncertainty cannot be disabled

`epistemic_display.show_material_uncertainty` and `show_corpus_limits` must remain `true` in v1.

A renderer may choose visual treatment but cannot restore a state that suppresses material uncertainty or turns corpus absence into historical absence.

### 4.8 View intent is not engine camera state

The shared contract stores geographic intent:

- `global` — Earth/world overview;
- `bounds` — fit a WGS84 geographic bounding box;
- `focus_object` — focus the canonical object identified by `target_ref`.

Exact MapLibre zoom, globe altitude, pitch, bearing, camera matrix and animation progress remain renderer-local.

This intentionally sacrifices pixel-identical restore in exchange for semantic portability.

## 5. Mapping from existing ARTEMIS runtime

Current `js/ui.js` state mixes semantic, UI and cache state. The target mapping is:

| Current field / behavior | Explorer State v1 | Disposition |
|---|---|---|
| `timelineMode` + `currentStartYear/currentEndYear` | `temporal_selection` | shared semantic/query state |
| `enabledLayerIds` | `active_layer_refs` | shared |
| `selectedFeatureId` | `selection.primary_object_ref` / `selected_object_refs` | migrate from Feature IDs to canonical World Model refs as v3 runtime arrives |
| `sliceCompareSelectionIds` | `selection.comparison_object_refs` | shared comparison state |
| local/global Life in Context selection | `context.*_context_refs` | shared |
| active trajectory segment | `active_focus.trajectory_*` | new first-class shared state |
| active Region reconstruction | `active_focus.region_*` | new first-class shared state |
| `search`, overlay/modal, detail-sheet, hover | none | UI-local |
| `filteredFeatures`, `filteredFeatureIds`, cache keys | none | derived/cache-local |
| `displayMode`, map theme | none in v1 | presentation preference, not semantic state |
| MapLibre object / event handlers | none | renderer-local |

## 6. Mapping from ResearchSlice v2 Saved View

Current mutable Saved View stores:

- `time_range`;
- `enabled_layer_ids`;
- `selected_feature_id`;
- `comparison_feature_ids`;
- MapLibre-like `center` + `zoom`;
- current filter state.

Compatibility plan:

1. time range → `temporal_selection`;
2. enabled layers → `active_layer_refs`;
3. selected/comparison Feature IDs → canonical object refs through compatibility identity mapping where non-inventive;
4. center/zoom are **not copied into canonical Explorer State**;
5. a 2D compatibility adapter may derive a WGS84 `bounds` view intent from an actual runtime viewport when saving;
6. if only center/zoom exists and no deterministic viewport bounds can be reconstructed, retain it in the mutable Slice compatibility envelope rather than pretending it is renderer-neutral state;
7. arbitrary current `filter_state` remains compatibility/UI state until each filter has explicit cross-domain semantics.

This avoids turning the current MapLibre Saved View into the permanent multi-renderer contract.

## 7. Mapping from Foundation v1 SynchronizedView fixture

The reviewed `SynchronizedView` fixture already provides most semantic ingredients:

- `time_state` → `temporal_selection`;
- `active_layer_refs` → same;
- `selected_object_refs` → `selection.selected_object_refs`;
- `local_context_refs` / `global_context_refs` → same;
- `derived_observation_refs` → same;
- `comparison_scope` → same;
- `uncertainty_display` → `epistemic_display`;
- `dataset_identity` → same;
- `camera_state.kind=bounds` → `view_intent.kind=bounds`.

Explorer State v1 additionally makes active trajectory/Region reconstruction focus explicit and removes the misleading generic name `camera_state` from shared semantics.

## 8. Deterministic restore algorithm

A consumer restores state in this order:

1. validate `schema_version`;
2. resolve exact `world_slice_ref` and `dataset_identity`;
3. validate every layer/object/context/focus reference;
4. validate temporal selection shape and interval ordering;
5. evaluate active World Model objects using canonical temporal/spatial semantics;
6. apply canonical selection/context/focus;
7. expose mandatory uncertainty/coverage semantics;
8. hand the resolved semantic state to a renderer projection adapter;
9. renderer converts `view_intent` into its own camera state.

A renderer must not reorder steps 5–8 by filtering independently from the model.

## 9. Invalid examples

Invalid Explorer State includes:

- `zoom`, `pitch`, `bearing`, camera matrix or engine viewer objects in shared state;
- a dataset identity different from the pinned World Slice;
- unknown layer/object references;
- trajectory segment that does not belong to the named trajectory;
- Region geometry that does not belong to the named Region;
- `mode=instant` with different `start/end`;
- `start > end`;
- material uncertainty or corpus limits disabled;
- persisted visible-object list presented as authoritative;
- renderer-specific historical IDs.

## 10. Executable package

Proposed fixture contour:

```text
fixtures/explorer_state/v1/
├── schema.json
├── state-1504-local-global.json
└── README.md

scripts/validate_explorer_state_fixtures.py
tests/test_explorer_state_fixtures.py
```

The positive fixture is derived from the reviewed #329 synthetic World Slice rather than from historical content.

The validator must check JSON Schema plus cross-reference and semantic constraints against `fixtures/world_model/v1/package.json`.

## 11. Non-goals

- runtime refactor of `js/ui.js` in this issue;
- migration of ResearchSlice v2 persistence;
- selecting a Globe engine;
- defining #341 renderer projection payloads;
- relation predicate semantics from #331;
- screen layout, CSS or visual design;
- exact pixel/camera restore across renderer engines.

## 12. Exit criteria

#340 is ready to close only when:

- the versioned schema and fixture exist;
- validator rejects renderer-owned state and broken references;
- deterministic restore semantics are documented;
- current UI/Saved View compatibility losses are explicit;
- two renderer adapters can later consume the state without extending its semantic core;
- repository checks execute the fixture tests;
- no public/runtime capability overclaim is introduced.