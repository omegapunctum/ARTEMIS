# ARTEMIS — Globe Runtime Spike Runbook v1

## Status

- Type: working R&D runbook.
- Updated: 2026-08-28.
- Issues: #343 engine spike; #358 source-aware inspector; #355 Gate D real-slice vertical.
- Runtime: generated static artifact only.
- Public capability: labelled generated `/globe/` R&D review preview; no product readiness.

## 1. Purpose

This runbook reproduces and manually verifies the bounded #343 3D Earth prototype and the revised calendar-based `Leonardo Life Path` interaction scaffold over the frozen Leonardo Gate C package for #355.

The default build adapts the frozen, non-public `fixtures/world_slices/leonardo_romagna_1502/v1/` package into a read-only World Model-compatible view, then consumes the shared Explorer State / Render Projection / Geospatial Asset contracts. It preserves draft/rejected Claim states, withheld geometry, unresolved routes, `promotion_allowed=false`, and the accepted #377 read-only runtime boundary.

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
- `explorer-views.json` (precomputed time/layer Explorer State + projection packages);
- `life-path.json` (four source-bound presences, calendar axis, canonical segment bindings, null route gaps and presentation-only chronology policy);
- `geospatial-assets.json`;
- `earth-context.geojson` (bundled Natural Earth 1:110m Land v4.0.0 present-day context);
- `capability-path.geojson`;
- `engine-evaluation.json`;
- `acceptance-profiles.json` (pinned desktop/tablet/mobile hosted-browser contract);
- `knowledge-index.json`;
- optional `sources/` only when a selected package contains checksum-pinned local source artifacts;
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

Default spike behavior requires network access for the pinned MapLibre GL JS 5.24.0 engine files from unpkg. Frozen semantic records and the pinned Natural Earth context are generated/copied locally; Earth context needs no runtime network or secret. Source links remain the exact external registry URLs and are not treated as archived evidence.

No ARTEMIS backend is required.

### Public review route

The canonical Pages workflow builds the same deterministic artifact with:

```bash
python scripts/build_globe_spike.py --public-preview --output pages_artifact/globe
```

It is reachable from the existing site at `./globe/` and linked as `3D Globe · R&D`. The public build changes labeling, navigation and `build-meta.json` deployment metadata only; World Model, Explorer State, Render Projection, sources, uncertainty and geometry-withheld semantics remain identical to the default local build.

## 4. Expected visual/runtime state

On successful load:

- the canvas is an interactive globe, not a flat public compatibility map;
- the header says `ARTEMIS · Leonardo Life Path`; a local build is labelled as a generated review artifact, while `--public-preview` is explicitly labelled as a public experimental R&D surface;
- four numbered markers represent Rimini, Cesena, Cesenatico and Imola using present-day named-settlement reference coordinates;
- `Range` shows every documented presence whose temporal extent overlaps the selected calendar interval;
- `Range` is a two-handle interval on the full-width bottom timeline;
- `Scrub` has one primary current-time cursor plus a secondary `Build from` value and progressively reveals accumulated presences;
- changing either control selects the matching precomputed Explorer State / Render Projection closure while the browser preserves the exact calendar selection;
- selecting a marker once opens a compact map popup without changing the camera; selecting it again or choosing `Open details` opens the right drawer; double-click alone focuses the map;
- dashed links connect currently visible consecutive presences as presentation-only chronology; all three historical routes remain unknown with null geometry;
- layer combinations, Region alternatives and renderer diagnostics remain available in generated evidence but are not default user controls;
- real generalized Natural Earth land is visible only as `present_day_context`, carries no World Model identity and is not presented as valid 1502 coastline geometry;
- terrain status states that the default terrain fixture is synthetic/no live DEM;
- attribution shows both voluntary Natural Earth attribution and the synthetic terrain warning required by the #342 manifest.

## 5. Interaction and picking acceptance

In `Range`, move the start and end controls. Then switch to `Scrub`, choose a calendar start and move current time.

Expected result:

- `Range` displays exactly the presences overlapping the calendar interval;
- `Scrub` displays exactly the accumulated presences from start through current time;
- the globe markers update with the active temporal view;
- the Explorer State, projection and URL update with calendar values and the visible presence set;
- selecting an out-of-range marker is prevented;
- reduced-motion preference removes scripted camera animation.

Select Cesena or Cesenatico from its marker. The first click must open the compact popup without moving the camera; use `Open details` or select the same marker again to open the right drawer.

The card must show:

- place name and source-native date/range;
- the concise activity label bound to the existing Event;
- duration unavailable;
- exact historical position unknown;
- route from the previous stop unknown, where applicable;
- a collapsed `Sources and uncertainty` section.

Open that section. It must resolve the selected Event and presence item through
`knowledge-index.json` and preserve their Claim/Evidence/Source/Uncertainty closure, repeatable
locators and exact external registry URIs. The runtime must not return a capability-only path or
claim that the marker is Leonardo's exact historical coordinate.

## 6. Uncertainty acceptance

The spike passes only if all are true:

1. all three `trajectory-leonardo-romagna-1502` inferred gaps remain unresolved;
2. every dashed connector is explicitly presentation-only chronology and is never exposed as historical movement;
3. both Region reconstruction alternatives remain separately inspectable with null geometry and no silent winner;
4. all 22 Claims retain their exact `draft` or `rejected` Gate C review state;
5. the frozen package boundary remains 8 August–31 December 1502, while life-path presences preserve only their source-native day/month precision without invented intermediate dates;
6. corpus/geometry absence is not presented as historical absence.

## 7. Terrain acceptance

The default spike does **not** prove real-world terrain data quality.

It does include a real, pinned Natural Earth physical-land context layer under the separate provider policy in `2026-08-14_GATE_D_EARTH_CONTEXT_PROVIDER_POLICY_v1.md`. That layer proves globe-scale Earth orientation only, not elevation, local coastline accuracy or historical validity.

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
- a selected package's copied local source checksum differs from its reviewed package checksum;
- a frozen Leonardo canonical object, Region alternative, Claim/Evidence/Source/Uncertainty ref disappears;
- any Leonardo trajectory gap or Region alternative acquires geometry;
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
7. **headless Chrome execution of the generated artifact** with SwiftShader/WebGL at pinned desktop (`1440×900`), tablet (`1024×768`) and hosted-mobile (`500×844`, Chrome headless minimum) browser-window profiles, while recording each actual CSS viewport;
8. layout-mode, horizontal-overflow, globe-size, overlay-collision, interactive-control accessible-name, 24 CSS px target-size and mobile reduced-motion assertions defined by `acceptance-profiles.json`;
9. assertions that the browser DOM contains Leonardo Life Path/Explorer State, four source-bound presences, a selected concise activity, source/uncertainty access, honest frozen-candidate status, synthetic terrain status, MapLibre 5.24 engine status and a real `maplibregl-canvas` created by the runtime;
10. URL-restorable Range/Scrub calendar state, visible-presence count and canonical presence selection checks;
11. upload of the generated runtime, three screenshots, DOM snapshots and `artemis-globe-browser-evidence.json` for inspection.

The headless gate proves that the pinned MapLibre engine executes in a browser and reaches its map `load` path with the generated semantic data across the three deterministic viewport profiles. It does not replace human visual/interaction review or a complete WCAG audit, and it intentionally does not fail on hosted-runner `idle`/rAF timing because those values are not a production SLO.

Manual browser inspection remains required for interaction feel, visual legibility, assistive-technology review and real-device performance evidence. See `2026-08-14_GATE_D_BROWSER_EVIDENCE_v1.md` for the evidence boundary and remaining Gate D decision work.

The synthetic contract fixture remains available only as a renderer regression input. In this mode
the life-path presentation is unavailable and the legacy renderer controls/capability geometry may
be used for technical regression checks:

```bash
python scripts/build_globe_spike.py --dataset contract_fixture --output /tmp/artemis-globe-contract-fixture
```

That mode may render the fictional explicit point and Region polygons. It is not the default Gate D content path.

## 11. Exit decision

After review:

- keep MapLibre as the leading candidate only if the spike proves sufficient globe interaction, semantic picking, uncertainty handling and a credible terrain/provider path;
- escalate to a CesiumJS comparison spike if deep terrain, 3D Tiles, geospatial scene precision or extensibility is materially inadequate;
- keep the generated runtime non-public under the completed #345 boundary until #355 records a separate promotion decision and rollback plan.
