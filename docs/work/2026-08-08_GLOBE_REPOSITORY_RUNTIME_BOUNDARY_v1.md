# ARTEMIS — Globe Repository / Runtime / CI Boundary v1

## Status

- Type: working architecture decision.
- Date: 2026-08-08.
- Issue: #345.
- Parent R&D track: #339.
- Dependencies: #340–#344 completed.
- Decision status: R&D boundary only; no public Globe promotion.

## 1. Decision

ARTEMIS will **not** perform a repository-wide `apps/*` / packages / framework migration merely because the bounded 3D Globe spike now exists.

For the current evidence level, the accepted repository boundary is:

```text
current public runtime
├── index.html
├── js/
├── css/
└── data/

renderer-neutral executable contracts
├── fixtures/world_model/
├── fixtures/explorer_state/
├── fixtures/render_projection/
├── fixtures/render_parity/
└── scripts/validate_* / build_render_projection_*

bounded Globe R&D source
├── scripts/globe_spike/
├── scripts/build_globe_spike.py
└── fixtures/globe_runtime/

geospatial infrastructure contract
├── fixtures/geospatial_assets/
└── scripts/validate_geospatial_assets.py

generated / disposable runtime
└── build/globe-spike/ or CI artifact only
```

`index.html` remains the only public frontend entrypoint.

The Globe spike remains a **generated experimental artifact**, not a second checked-in public application.

## 2. Why no `apps/*` migration yet

A split such as:

```text
apps/explorer-2d
apps/globe
packages/world-model
packages/explorer-state
packages/render-projection
```

may become correct later, but doing it now would create migration cost before ARTEMIS has evidence that:

- the 3D renderer should be a product surface rather than R&D;
- two long-lived frontend applications are actually required;
- the repository needs a JavaScript package/build system;
- the current vanilla-JS public shell should be migrated;
- a final Globe engine/provider/deployment model is chosen;
- a real World Slice and user-value validation justify maintaining both runtimes.

The current contract/build boundaries already prevent semantic duplication. A packaging migration would therefore be structural churn rather than risk reduction.

## 3. Current ownership

### Public runtime

Owner:

- root `index.html` + current `js/` + current `css/` + checked-in `data/*`.

Rules:

- remains current public Pages runtime;
- remains MapLibre GL JS 4.7.1 until a separate upgrade decision;
- does not import or link the Globe spike;
- service worker / PWA manifest do not pre-cache or advertise the Globe spike;
- `data/features.geojson` remains the current public 2D compatibility projection, not the Foundation v3 World Model.

### Globe R&D source

Owner:

- `scripts/globe_spike/` for static runtime templates/source used by the builder;
- `scripts/build_globe_spike.py` for deterministic artifact construction;
- `fixtures/globe_runtime/v1/` for R&D-only engine/capability evidence.

Rules:

- source under `scripts/globe_spike/` is **not** a public entrypoint;
- it may not own World Model or Explorer State semantics;
- it may not read `data/features.geojson` as historical truth;
- it may not depend on ARTEMIS backend APIs for the #343 baseline;
- it may pin an experimental engine version independently from the public runtime;
- generated output is disposable and excluded from source-of-truth semantics.

The `scripts/globe_spike/` location is accepted specifically because the current runtime is template material consumed only by a deterministic R&D builder. If it becomes a maintained application, this location becomes invalid and promotion must move it to an explicit application boundary.

## 4. Generated artifact boundary

The builder output may exist only as:

- local `build/globe-spike/` (or an explicitly supplied temporary output directory);
- GitHub Actions artifact;
- another disposable review artifact explicitly approved by #345 successor governance.

Generated output must not be committed as canonical content or copied into root Pages artifacts by the R&D workflow.

Required metadata:

- `public_pages_entrypoint=false`;
- `backend_required=false` for the current spike;
- World Slice / Explorer State / projection IDs;
- engine identity;
- semantic primitive/unresolved counts;
- terrain/provider status;
- deterministic input/projection hashes.

## 5. GitHub Pages boundary

Until an explicit promotion decision:

- root `index.html` is the only Pages app entrypoint;
- Globe R&D workflows must not call `actions/deploy-pages`, `actions/upload-pages-artifact`, `peaceiris/actions-gh-pages` or equivalent publishing actions;
- Globe artifact upload uses generic `actions/upload-artifact` for review only;
- root `manifest.json` must not advertise the Globe runtime;
- root `sw.js` must not cache Globe spike files;
- public navigation must not link to the generated spike;
- private provider credentials must never be exposed to Pages.

This is a hard boundary, not a naming convention.

## 6. CI topology

The accepted Globe R&D CI chain is additive and bounded:

1. Explorer State validation;
2. Render Projection contract gate;
3. Geospatial Assets contract gate;
4. Cross-Renderer Semantic Parity gate;
5. Globe Runtime Spike gate;
6. Repository Boundary gate;
7. existing repository release/ETL/security regression workflows.

No Globe workflow replaces the canonical Release Discipline Gate.

Each specialized gate owns one architectural risk:

- State: renderer-independent interaction state;
- Projection: deterministic model→renderer semantics;
- Assets: terrain/imagery/provider boundary;
- Parity: semantic equivalence between renderers;
- Runtime spike: real browser/WebGL execution;
- Repository boundary: prevent accidental public promotion or second semantic/runtime core.

## 7. Dependency policy

### MapLibre 5.24.0

Allowed only in the generated #343 Globe artifact / R&D templates.

It does not authorize:

- upgrading public MapLibre 4.7.1;
- using Globe 5.x APIs in the public runtime;
- adding MapLibre 5.x files to the service worker cache;
- declaring MapLibre the final ARTEMIS 3D engine.

### CesiumJS

Remains an evidence-backed escalation candidate.

A Cesium comparison is justified only if future work exposes a concrete gap in MapLibre for terrain, 3D Tiles, precision, scene complexity or performance. It must consume the same Explorer State / Render Projection contracts.

### New framework/build system

React/Vue/Angular/TypeScript/npm workspace/bundler migration is not implied by Globe R&D.

A future build-system decision must solve a demonstrated project-wide problem, not merely make the experimental renderer look more conventional.

## 8. Semantic ownership invariant

No repository layout may create:

```text
2D historical model
3D historical model
```

The only accepted relationship is:

```text
World Model / World Slice
        +
Explorer State
        ↓
Render Projection
        ↓
2D adapter | Globe adapter | future adapter
```

Renderer source owns presentation and engine integration only.

## 9. Promotion gate: R&D → maintained experimental app

Moving Globe source out of `scripts/globe_spike/` into an application boundary such as `apps/globe/` requires all of:

1. #340–#344 remain green;
2. a real curated World Slice beyond synthetic fixtures is available;
3. Globe provides a user-value capability that cannot be tested adequately as a generated artifact;
4. engine choice is re-evaluated with real data/performance evidence;
5. provider/terrain licensing and attribution path are production-usable;
6. deployment/security model is explicit;
7. ownership and maintenance cost of two frontends is accepted;
8. shared package/build-system need is demonstrated rather than assumed.

This step may create an `apps/*` structure, but only through a separate architecture decision.

## 10. Promotion gate: experimental app → public product surface

Public promotion requires additional evidence:

- real World Slice/product validation, not synthetic fixtures alone;
- semantic parity on the promoted corpus;
- real-device browser/performance evidence;
- accessibility and UX review;
- provider availability/cost/license/attribution review;
- offline/cache/PWA decision;
- security review for any runtime configuration;
- rollback plan;
- explicit update to `PROJECT_TRUTH`, `DATA_CONTRACT`, `PROJECT_STRUCTURE`, public docs and release checks;
- no false implication that modern terrain/imagery is historical reconstruction.

#343 visual success by itself is insufficient.

## 11. Future target structure (conditional, not current)

If both renderers become maintained product applications, a plausible future target is:

```text
apps/
├── explorer-2d/
└── globe/

packages/
├── explorer-state/
├── render-projection/
└── shared-ui-or-runtime-contracts/
```

This is **not** current repository structure and must not be created incrementally/ad hoc before promotion.

World Model truth may remain outside JavaScript packages; packaging must not redefine ontology ownership.

## 12. Cleanup / lifecycle rule

The R&D Globe source may remain in `main` after #345 as executable architecture evidence, provided:

- dedicated CI stays green;
- it remains non-public;
- dependencies are pinned/reviewable;
- generated artifacts remain disposable;
- it does not become an unmaintained shadow product.

If it stops being exercised, it must be explicitly archived/removed rather than silently rotting beside the public runtime.

## 13. #339–#345 R&D conclusion

The bounded renderer R&D track has established:

- one semantic core;
- renderer-neutral state;
- deterministic render projection;
- explicit geospatial provider/terrain boundary;
- real 3D Globe execution;
- machine-checkable 2D/3D semantic parity;
- a repository/deployment boundary that prevents accidental promotion.

After #345 acceptance, #339–#345 should be treated as **completed architecture/R&D evidence**, not an active parallel product-development branch.

Production-scale 3D/dynamic Earth remains gated until product/data evidence opens a new execution cycle.