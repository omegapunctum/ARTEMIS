# ARTEMIS — Gate D Browser Evidence v1

## Status

- Type: Gate D working evidence contract.
- Date: 2026-08-14.
- Owner issue: #355.
- Runtime: isolated generated Globe artifact only.
- Public capability: no.
- Gate E: closed until explicit `ADVANCE_TO_GATE_E`.

## 1. Decision supported

This evidence closes the reproducibility gap in the existing `Globe Runtime Spike Gate`: the same generated MapLibre artifact is now exercised at deterministic desktop, tablet and mobile viewport profiles. It does not create a second browser test system and does not promote the Globe runtime.

The acceptance contract is versioned at `fixtures/globe_runtime/v1/gate_d_acceptance_profiles.json`. CI publishes one machine-readable `artemis-globe-browser-evidence.json` plus DOM snapshots and screenshots for all profiles.

## 2. Automated evidence

| Profile | Viewport | Expected layout | Reduced motion | Evidence |
|---|---:|---|---|---|
| desktop | 1440 × 900 CSS px | two-column desktop | default | DOM + screenshot |
| tablet | 1024 × 768 CSS px | compact two-column tablet | default | DOM + screenshot |
| mobile | 390 × 844 CSS px | stacked mobile | forced `reduce` | DOM + screenshot |

Each profile must reach the MapLibre `load` path and prove:

1. the requested viewport and expected layout mode match;
2. the globe remains at least 320 × 320 CSS px;
3. document-level horizontal overflow is at most 1 CSS px;
4. interactive buttons, inputs and links have a programmatically discoverable name;
5. measured buttons and range input are at least 24 × 24 CSS px;
6. the mobile profile observes `prefers-reduced-motion: reduce`;
7. the frozen Leonardo World Slice, source-aware inspector, uncertainty boundary and MapLibre canvas remain present;
8. URL-pinned time, layer and selection state remains restorable.

Startup-to-idle and animation-frame values are retained in the evidence artifact as diagnostics only. They are never pass/fail thresholds under hosted headless virtual-time scheduling.

## 3. What this does not prove

The automated evidence is not:

- a complete WCAG conformance audit;
- screen-reader or other assistive-technology certification;
- a real iOS, Android, tablet or desktop-device run;
- a cross-engine Firefox/Safari result;
- a production performance SLO or capacity baseline;
- authorization to add historical geometry, a live terrain provider, backend services or a public Globe route;
- a Gate D exit decision or permission to open Gate E.

## 4. Remaining Gate D review

Before an explicit Gate D exit decision, the owner must review the uploaded profile screenshots/DOM/evidence and record:

1. at least one real desktop and one real mobile interaction pass, including keyboard navigation and visual legibility;
2. representative browser/OS versions and any WebGL warnings;
3. startup/interaction observations as evidence, without converting hosted headless timing into an SLO;
4. whether the MapLibre path exposes a measured blocker that justifies a bounded CesiumJS comparison;
5. the explicit promote/hold decision, rollback boundary and canonical truth synchronization.

Absent a measured blocker, MapLibre remains the selected Gate D candidate. The current public runtime remains the root 2D MapLibre application.

## 5. Semantic and data boundaries

All profile runs consume the single approved semantic path:

`World Model → Explorer State → Render Projection → renderer`

The evidence preserves the frozen Gate C boundary: Leonardo in Romagna, 8 August–31 December 1502; non-public; Claims draft/rejected; zero historical render primitives; unresolved geometry remains unresolved. Natural Earth land is bundled real present-day context only, and terrain remains synthetic/non-live.

No Airtable historical import is authorized. Airtable remains a curation surface, while GitHub remains canonical truth.
