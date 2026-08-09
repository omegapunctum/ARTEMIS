# ARTEMIS — Globe Runtime Spike Runbook v1

## Status

- Type: working R&D runbook.
- Updated: 2026-08-09.
- Issues: #343 engine spike; #358 source-aware Globe MVP inspector.
- Runtime: generated static artifact only.
- Public capability: no.

## 1. Purpose

This runbook reproduces and manually verifies the bounded #343 3D Earth prototype and its #358 source-aware inspector without changing the current ARTEMIS public runtime.

The spike consumes merged World Model / Explorer State / Render Projection / Geospatial Asset contracts and generates a separate static directory.

## 2. Build

From the repository root:

```bash
python scripts/build_globe_spike.py --output /tmp/artemis-globe-spike
```

Expected result:

```text
[PASS] Globe runtime spike build: ...
```

The output directory must contain:

- `index.html`;
- `runtime.js`;
- `style.css`;
- `projection.json`;
- `globe-projection.json`;
- `explorer-state.json`;
- `geospatial-assets.json`;
- `synthetic-earth-context.geojson`;
- `capability-path.geojson`;
- `engine-evaluation.json`;
- `knowledge-index.json`;
- `sources/` with checksum-verified local source artifacts referenced by the World Model package;
- `build-meta.json`;
- `README.txt`.

The build is disposable and must not be copied into root public Pages artifacts as part of #343.

## 3. Serve locally

```bash
python -m http.server 8080 --directory /tmp/artemis-globe-spike
```

Open:

```text
http://127.0.0.1:8080/
```

Default spike behavior requires network access only for the pinned MapLibre GL JS 5.24.0 engine files from unpkg. Historical/semantic fixture data and synthetic Earth context are local generated files.

No ARTEMIS backend is required.

## 4. Expected visual/runtime state

On successful load:

- the canvas is an interactive globe, not a flat public compatibility map;
- the banner says `ARTEMIS · Source-aware 3D Globe MVP` and explicitly says the renderer is experimental/non-public;
- the inspector displays the World Slice, Explorer State, selected time, Render Projection ID and honest corpus status;
- semantic points/Regions come from `globe-projection.json` generated from the merged Render Projection contract;
- primary and alternative `region-fixture-basin` reconstructions are visibly distinguishable;
- the `Alternatives` control can hide/show the alternative Region without changing World Model state;
- the unresolved list contains keyboard-operable semantic records, including the Mara Vale trajectory gap with `uncertainty-trajectory-route` and no geometry;
- the dashed capability path is visibly labelled as renderer capability only and is not historical knowledge;
- terrain status states that the default terrain fixture is synthetic/no live DEM;
- attribution shows the synthetic fixture attribution required by the #342 manifest.

## 5. Picking acceptance

Click a semantic point or Region.

The inspector must resolve the selected projection item through `knowledge-index.json` and display canonical:

- `object_ref`;
- optional `subobject_ref`;
- object type;
- render role;
- temporal membership;
- spatial/projection status;
- Claim ID, statement, review/confidence/evidence state;
- EvidenceLink relation/strength/review state and repeatable locator;
- Source title, copied artifact URI and review state;
- material Uncertainty description/effect/alternatives;
- projection loss, when present.

Choose an unresolved record with keyboard or pointer input.

Expected result:

- the same inspector opens without inventing geometry;
- its Claim/Evidence/Source/Uncertainty closure is identical to the neutral projection refs;
- a local source link resolves to the checksum-verified copied artifact.

Click the dashed capability path.

Expected result:

- the inspector explicitly says this is renderer capability geometry;
- no World Model object ID is returned;
- it cannot be interpreted as the Mara Vale route.

## 6. Uncertainty acceptance

The spike passes only if all are true:

1. `trajectory-mara-vale / trajectory-segment-gap` remains unresolved;
2. no line connects its documented endpoints as historical movement;
3. primary and alternative Region reconstructions both remain available;
4. alternative reconstruction styling is distinguishable;
5. `event-workshop-arrival` remains `possible_active` rather than exact `active` where represented in projection state;
6. corpus/geometry absence is not presented as historical absence.

## 7. Terrain acceptance

The default spike does **not** prove real-world terrain data quality.

It proves:

- the runtime has an explicit `raster-dem` / `setTerrain` adapter path;
- terrain configuration is read through the merged geospatial asset boundary;
- a synthetic/non-live terrain manifest does not silently fabricate elevation;
- a future live terrain asset must pass #342 vertical datum, provenance, licensing, cache and secret rules.

A real DEM provider is outside #343 default acceptance.

## 8. Performance baseline

The inspector records:

- startup → first MapLibre idle time;
- a short browser animation-frame sample in milliseconds/frame;
- approximate FPS;
- semantic primitive count.

These values are diagnostic R&D evidence only. They are not a production performance SLO.

When manually evaluating the spike, record at minimum:

- browser/version;
- device/OS;
- startup → idle value;
- frame sample;
- whether globe rotate/zoom/pitch feels responsive;
- any WebGL/MapLibre warnings.

Hosted headless Chrome is used for runtime acceptance but its virtual-time scheduling is **not** treated as a performance baseline. `idle`/rAF values may remain `pending` there even after the MapLibre globe has loaded successfully.

## 9. Failure states

The spike must fail visibly when:

- MapLibre 5.24.0 cannot load;
- generated JSON cannot load;
- projection contracts fail during build;
- a projected Claim, EvidenceLink, Source or Uncertainty ref cannot be resolved;
- an EvidenceLink escapes the projected Claim/Source closure or lacks a locator;
- a copied local source checksum differs from its reviewed package checksum;
- a required point/Region fixture disappears;
- the reviewed trajectory gap acquires geometry;
- provider/terrain manifest becomes invalid.

It must not silently fall back to `data/features.geojson`, `/api/*`, or the current public 2D runtime.

## 10. CI

`Globe Runtime Spike Gate` performs:

1. Explorer State validation;
2. Render Projection build validation;
3. Geospatial Asset validation;
4. static Globe artifact build;
5. runtime contract tests;
6. static HTTP serving smoke test;
7. **headless Chrome execution of the generated artifact** with SwiftShader/WebGL;
8. assertions that the browser DOM contains the canonical World Slice/Explorer State, source title + repeatable locator, honest fixture status, unresolved trajectory uncertainty, synthetic terrain status, MapLibre 5.24 engine status and a real `maplibregl-canvas` created by the runtime;
9. upload of the generated artifact `artemis-globe-runtime-spike` for inspection.

The headless gate proves that the pinned MapLibre engine executes in a browser and reaches its map `load` path with the generated semantic data. It does not replace human visual/interaction review, and it intentionally does not fail on hosted-runner `idle`/rAF timing because those values are not a production SLO.

Manual browser inspection remains useful for interaction feel, visual legibility and real-device performance evidence.

## 11. Exit decision

After review:

- keep MapLibre as the leading candidate only if the spike proves sufficient globe interaction, semantic picking, uncertainty handling and a credible terrain/provider path;
- escalate to a CesiumJS comparison spike if deep terrain, 3D Tiles, geospatial scene precision or extensibility is materially inadequate;
- keep the generated runtime non-public under the completed #345 boundary until #355 records a separate promotion decision and rollback plan.
