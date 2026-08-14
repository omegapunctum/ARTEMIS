# ARTEMIS — Globe Public Review Preview Decision v1

## Status

- Type: active Gate D deployment decision under issue `#355`.
- Date: 2026-08-14.
- Decision: publish the generated Globe at the existing GitHub Pages site as a clearly labelled R&D review preview.
- Route: `./globe/` from the root 2D application.
- Product promotion: no.
- Gate D exit: no; D1/M1/A1/P1 evidence and one exit decision remain required.

## Decision

The project owner explicitly requires the Globe to be reviewable on the existing ARTEMIS site. GitHub Pages therefore builds the deterministic Gate D artifact during deployment and publishes it under `/globe/`. The root 2D Architecture Atlas remains the default and rollback entrypoint.

Public reachability changes; semantic maturity does not. The preview must continue to state that:

- it is experimental R&D, not a product-ready capability;
- the Leonardo Gate C package remains frozen candidate material with draft/rejected Claims;
- `promotion_allowed=false` is preserved;
- historical routes and Region geometry remain withheld where unsupported;
- Natural Earth is generalized present-day context, not 1502 geography;
- terrain remains synthetic/non-live;
- no backend, credential, provider token or Airtable historical write is required.

## Deployment boundary

The Pages workflow may run:

```text
python scripts/build_globe_spike.py --public-preview --output pages_artifact/globe
```

The generated directory remains untracked and disposable. The dedicated Globe R&D workflow remains review-only and must not deploy Pages. Source remains under `scripts/globe_spike/`; this decision does not create `apps/globe/`, a second semantic core, a framework migration or a second backend.

The root PWA manifest and service worker do not pre-cache or advertise the Globe as an offline app. The preview requires network access for the pinned MapLibre 5.24.0 CDN assets.

## Navigation and labeling

- root desktop and compact navigation link to `./globe/` as `3D Globe · R&D`;
- the preview links back to the 2D map;
- the preview banner states `Публичный R&D-preview — экспериментальная поверхность, не готовый продукт`;
- the existing source, uncertainty, coverage and projection-loss disclosures remain visible.

## Public-data boundary

The preview serializes the already reviewed frozen Gate C package for inspection. This is public review exposure, not publication as accepted historical truth. No local source files are copied for the Leonardo package; the registry contains external public URLs and repeatable locators. Draft/rejected state and zero authorized historical primitives remain machine-readable and visible.

## Verification

- default local build remains `public_pages_entrypoint=false`;
- Pages build uses `public_pages_entrypoint=true` and `deployment_mode=public_r_and_d_preview`;
- root 2D runtime remains MapLibre 4.7.1;
- Globe preview remains isolated on MapLibre 5.24.0;
- boundary, runtime, project-state and Pages workflow tests pass;
- the deployed `/globe/` route reaches visual-ready state before the change is handed off.

## Rollback

Remove the two root navigation links and the `Build public Globe R&D preview` Pages step. The root 2D artifact, data export and rollback path remain unchanged.

## Non-goals

- Gate D completion or automatic `ADVANCE_TO_GATE_E`;
- product-ready/public historical content claims;
- default replacement of the 2D map;
- PWA/offline Globe support;
- live terrain or imagery providers;
- historical geometry invention;
- Airtable import, backend deployment, AI, Cesium or framework migration.
