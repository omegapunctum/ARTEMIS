# ARTEMIS — Cross-Renderer Semantic Parity Contract v1

## Status

- Type: working executable contract.
- Date: 2026-08-08.
- Issue: #344.
- Dependencies: #340 Explorer State, #341 Render Projection, #343 executable Globe spike — completed.
- Scope: semantic equivalence between 2D MapLibre/GeoJSON and 3D Globe adapters for the same World Slice + Explorer State.
- Visual status: screenshots and visual regression are explicitly **not** semantic parity evidence.

## 1. Purpose

ARTEMIS may have multiple renderers, but it must have one meaning.

The parity contract answers:

> If two renderers consume the same versioned World Slice and Explorer State, do they expose the same knowledge identity, temporal membership, spatial reconstruction choice, uncertainty and evidence — even when their pixels, camera, projection and rendering primitives differ?

The contract treats renderer divergence in semantic fields as a release-blocking failure.

## 2. Renderer input envelope

Parity is checked over the complete renderer input envelope:

```text
World Model / World Slice
        +
Explorer State
        ↓
Neutral Render Projection
        +
renderer adapter payload
        ↓
2D renderer | 3D renderer
```

This is important for unresolved/non-spatial objects. They may not have a drawable geometry, but their meaning remains in the neutral projection and must be recoverable consistently by both renderers.

## 3. Semantic fingerprint

For every projection item, parity uses a renderer-neutral fingerprint containing:

- `item_id`;
- `object_ref`;
- `object_type`;
- optional `subobject_ref`;
- `render_role`;
- `temporal_membership`;
- `spatial_status`;
- `geometry_refs`;
- `place_ref`;
- `layer_refs`;
- `claim_refs`;
- `uncertainty_refs`;
- `evidence_link_refs`;
- `source_refs`;
- `semantic_flags`.

For each rendered geometry instance the fingerprint additionally contains:

- adapter instance ID;
- `geometry_ref`;
- normalized geometry type (`Point | LineString | Polygon | MultiPolygon`);
- geometry Claim/Uncertainty refs;
- reconstruction mode;
- `is_primary`.

A renderer may rename its technical primitive (`Feature`, `cartographic_polygon`, etc.), but after normalization the semantic fingerprint must be identical.

## 4. World-state parity

For one pinned input, both renderer envelopes must expose the same:

- World Slice ID;
- dataset identity;
- Explorer State ID;
- projection ID;
- selected primary object ID;
- selected object IDs;
- active object IDs;
- possible-active object IDs;
- atemporal/context object IDs;
- deferred object types;
- active trajectory/segment focus;
- active Region/geometry focus.

A renderer cannot silently omit an active object merely because it lacks drawable geometry.

## 5. Temporal parity

Time filtering belongs to the shared projection, not to renderer engines.

Parity tests include explicit boundary cases around the 1503 → 1504 transition in the synthetic World Model:

- 1503-12-31 must use `region-geometry-v1` and `process-stage-north`;
- 1504-01-01 must use `region-geometry-v2` / its alternative and `process-stage-south`;
- `trajectory-segment-gap` remains active across the boundary according to the reviewed fixture;
- inactive geometry/stages from the other side of the boundary must be absent.

Both adapters are generated from each boundary state and compared independently.

## 6. Region reconstruction parity

For `region-fixture-basin` at the baseline selected time:

- primary `region-geometry-v2` must be present;
- alternative `region-geometry-v2-alternative` must be present when `show_alternatives=true`;
- primary/alternative identity must not be swapped;
- reconstruction mode must survive;
- `uncertainty-region-alternative` must survive;
- Claim/Evidence/Source refs must survive.

A visually identical polygon with the wrong reconstruction identity is a semantic failure.

## 7. Trajectory parity

For `trajectory-mara-vale`:

- `trajectory-segment-gap` remains `segment_kind=inferred_gap`;
- its spatial status remains `unresolved`;
- it has no geometry refs;
- `uncertainty-trajectory-route` survives;
- it cannot become a LineString through renderer interpolation.

The accepted baseline Explorer State focuses `trajectory-segment-workshop`. The
unresolved gap remains part of the complete semantic envelope and is tested as an
independent uncertainty anchor; focus is not rewritten merely to make the gap
drawable or selected.

The separate #343 capability path is outside World Model parity because it has no canonical object identity.

## 8. Selected-object parity

The baseline Explorer State selects `event-documented-workshop-meeting` as primary
and keeps `entity-mara-vale` in the full selected-object set.

That event has a named-place reference without canonical geometry in the reviewed fixture. Therefore the correct renderer behavior is not to invent a point: both renderer envelopes must resolve the selected object as the same `unresolved` semantic item.

Primary selection, the complete selected-object set and active focus are semantic;
camera centering, highlight color and popup layout are visual.

## 9. Epistemic parity

The following are parity-critical:

- Claim refs;
- Uncertainty refs;
- EvidenceLink refs;
- Source refs;
- Region reconstruction metadata;
- projection losses/reasons where relevant.

Dropping one of these in a renderer-specific path is a blocking failure even if the map still looks plausible.

## 10. Derived observation vs Relation

The World Model fixture contains:

- `observation-mara-traveler-co-presence` — a DerivedObservation with `relation_created=false`;
- documented Relations such as `relation-mara-ren-encounter` and `relation-ren-influences-council-protocol`.

Parity must preserve the distinction:

- derived co-presence cannot be promoted to a documented Relation;
- documented Relation objects remain Relation objects;
- Render Projection v1 continues to declare `Relation` deferred until #331 semantics are accepted;
- no renderer may infer a Relation because two objects share time/space.

## 11. Renderer-only differences

The expected fixture explicitly allows these to differ without failing semantic parity:

- 2D feature vs 3D primitive technical type;
- camera center/zoom/pitch/bearing/orientation;
- screen coordinates and pixel size;
- paint/style/color/opacity;
- clustering and LOD;
- label placement;
- terrain draping/clamping presentation when it does not assert historical altitude;
- animation/interpolation used only as presentation;
- GPU/tile/cache/picking-buffer implementation;
- screenshot pixels.

No semantic field may be added to this allow-list merely to silence a failing parity test.

## 12. Expected-state fixture

`fixtures/render_parity/v1/expected.json` is not historical truth. It is executable regression evidence over the reviewed synthetic fixture.

It pins:

- source identities;
- selected and active state;
- semantic anchors;
- Region alternatives;
- uncertainty/evidence expectations;
- temporal boundary cases;
- Relation/DerivedObservation distinction;
- allowed renderer-only differences.

Changing it requires explaining which accepted upstream contract changed and why.

## 13. Negative fixtures

`negative_cases.json` describes controlled semantic corruptions. The parity harness must reject at least:

- canonical object-ID drift;
- dropped uncertainty;
- wrong temporal membership;
- dropped alternative Region reconstruction;
- dropped Source/Evidence refs;
- trajectory segment-kind corruption;
- invented geometry for an unresolved trajectory gap.

The negative cases mutate derived test payloads only; they never modify reviewed World Model fixtures.

## 14. Parity harness

`scripts/validate_renderer_parity.py`:

1. validates the expected fixture;
2. builds neutral projection + both adapters from the reviewed baseline;
3. normalizes 2D and Globe adapter instances;
4. combines each adapter with the shared neutral semantic items for unresolved/non-spatial cases;
5. compares complete semantic envelopes;
6. validates expected anchors;
7. validates selected-object resolution;
8. runs boundary states through both adapters;
9. validates DerivedObservation vs Relation semantics;
10. exposes mutation helpers used by negative tests.

## 15. CI

`Cross-Renderer Semantic Parity Gate` is independent of screenshot/visual CI.

A renderer cannot be promoted if parity fails, even when:

- its own build succeeds;
- screenshots look correct;
- the other renderer still works.

Visual regression and renderer performance remain separate concerns.

## 16. Acceptance

#344 is complete when:

- baseline 2D/Globe semantic envelopes match;
- expected fixture passes;
- boundary cases pass;
- selected unresolved object identity is preserved;
- Region alternative and trajectory uncertainty semantics pass;
- Claim/Evidence/Source refs pass;
- DerivedObservation/Relation distinction passes;
- all negative corruption cases are rejected;
- dedicated parity CI and normal repository gates are green.

## 17. Non-goals

This contract does not:

- require visual pixel equality;
- make the Globe public;
- choose final 2D/3D repository layout (#345);
- define Relation predicates (#331);
- define historical terrain/altitude;
- require every renderer to support the same visual effects.

It requires only that different renderers do not change what ARTEMIS knows.
