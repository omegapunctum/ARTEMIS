# ARTEMIS — Gate D Browser Evidence v1

## Current applicability — 2026-09-15

Sections 1–5 below preserve the original August evidence/review context, including historical runtime and gate statements. They are not current project-state claims. Current lifecycle/public surfaces are owned by `docs/PROJECT_TRUTH.md`, `docs/project_state.json` and `docs/work/README.md`. The additive coverage audit in section 6 describes the current runner.

## Historical status

- Type: Gate D working evidence contract.
- Date: 2026-08-14.
- Owner issue: #355.
- Runtime: isolated generated Globe artifact only.
- Public capability: deterministic R&D preview reachability is separately authorized; this evidence still proves no product readiness.
- Gate E: closed until explicit `ADVANCE_TO_GATE_E`.

## 1. Decision supported

This evidence closes the reproducibility gap in the existing `Globe Runtime Spike Gate`: the same generated MapLibre artifact is now exercised at deterministic desktop, tablet and mobile browser-window profiles. It does not create a second browser test system and does not promote the Globe runtime.

The acceptance contract is versioned at `fixtures/globe_runtime/v1/gate_d_acceptance_profiles.json`. CI publishes one machine-readable `artemis-globe-browser-evidence.json` plus DOM snapshots and screenshots for all profiles.

## 2. Automated evidence

| Profile | Requested browser window | Expected layout | Reduced motion | Evidence |
|---|---:|---|---|---|
| desktop | 1440 × 900 CSS px | two-column desktop | default | DOM + screenshot |
| tablet | 1024 × 768 CSS px | compact two-column tablet | default | DOM + screenshot |
| mobile | 500 × 844 CSS px | stacked mobile | forced `reduce` | DOM + screenshot |

Each profile uses one browser process and a dependency-free Chrome DevTools Protocol capture driver for both DOM and screenshot capture. The driver waits on wall-clock MapLibre visual readiness, so the DOM assertions and pixels describe the same runtime. It must reach the MapLibre `load` path and prove:

1. the requested browser-window width and expected layout mode match; the actual CSS viewport is recorded because headless Chrome may reserve browser chrome from the requested outer height;
2. the globe remains at least 320 × 320 CSS px;
3. document-level horizontal overflow is at most 1 CSS px;
4. interactive buttons, inputs and links have a programmatically discoverable name;
5. measured buttons and range input are at least 24 × 24 CSS px;
6. globe controls, terrain status and attribution overlays do not collide;
7. the mobile profile observes `prefers-reduced-motion: reduce`;
8. the frozen Leonardo World Slice, source-aware inspector, uncertainty boundary and MapLibre canvas remain present;
9. URL-pinned time, layer and selection state remains restorable.
10. the bundled Earth-context source has loaded and at least one Natural Earth land/coastline feature is queryable in the rendered viewport before the screenshot is accepted.

Startup-to-idle and animation-frame values are retained in the evidence artifact as diagnostics only. They are never pass/fail thresholds under hosted-runner wall-clock scheduling.

Chrome 150 clamps the hosted headless browser-window width to 500 CSS px. This still exercises the actual mobile breakpoint and stacked layout, but it does not substitute for the required 390 CSS px real-device review.

## 3. What this does not prove

The automated evidence is not:

- a complete WCAG conformance audit;
- screen-reader or other assistive-technology certification;
- a real iOS, Android, tablet or desktop-device run;
- a cross-engine Firefox/Safari result;
- a production performance SLO or capacity baseline;
- authorization to add historical geometry, a live terrain provider, backend services or any public Globe route beyond the bounded `/globe/` R&D preview;
- a Gate D exit decision or permission to open Gate E.

## 4. Remaining Gate D review

Before an explicit Gate D exit decision, the owner must review the uploaded profile screenshots/DOM/evidence and record:

1. at least one real desktop and one 390 CSS px real mobile interaction pass, including keyboard navigation and visual legibility;
2. representative browser/OS versions and any WebGL warnings;
3. startup/interaction observations as evidence, without converting hosted headless timing into an SLO;
4. whether the MapLibre path exposes a measured blocker that justifies a bounded CesiumJS comparison;
5. the explicit promote/hold decision, rollback boundary and canonical truth synchronization.

Absent a measured blocker, MapLibre remains the selected Gate D candidate. The root 2D MapLibre application remains the default public runtime and rollback path; `/globe/` is a separate review preview.

## 5. Semantic and data boundaries

All profile runs consume the single approved semantic path:

`World Model → Explorer State → Render Projection → renderer`

The evidence preserves the frozen Gate C boundary: Leonardo in Romagna, 8 August–31 December 1502; non-public; Claims draft/rejected; zero historical render primitives; unresolved geometry remains unresolved. Natural Earth land is bundled real present-day context only, and terrain remains synthetic/non-live.

No Airtable historical import is authorized. Airtable remains a curation surface, while GitHub remains canonical truth.

## 6. Native UI Quality coverage audit — 2026-09-15

### Authority and method

Scope: the owner's Engineering request to compare these files against four accepted UI Quality principles, preserving domain assertions and adding only objectively missing native checks. The four labels were recovered from the prior accepted discussion (2026-09-14); this is an implementation mapping, not a new canonical UI rule source. No external skills repository was imported or used as authority.

Inspected baseline: ARTEMIS main `c85414d80785ac36ffae0d8f4406e8faf1dfbf9d`. Files: this document, `fixtures/globe_runtime/v1/gate_d_acceptance_profiles.json`, `scripts/capture_globe_browser_evidence.mjs`, runtime `collectAcceptanceEvidence`, `tests/test_globe_runtime_spike.py`, `tests/test_temporal_region_proof.py`, and owned Globe/Pages workflows.

| Accepted invariant | Existing coverage | Exact gap and bounded addition |
|---|---|---|
| Real rendered UI correctness | Wall-clock MapLibre readiness; rendered Natural Earth feature query; same-session DOM/screenshot; viewport/layout/overflow/target/name/overlay assertions; Place label collisions and Region visible disclosure/hit test | Existing coverage is retained. No new aesthetic metric is justified. Evidence limitation: card text read inside a hidden inspector proves content closure, not visibility; Region's separate visible link/click test covers its declared provenance access. |
| Declared interaction truth | Leonardo Presence/Place identity, Range/Scrub, two-stage popup/details, no single-click camera move, unknown-route boundary, URL restore; three distinct Region geometries/native intervals and visible provenance link click | Many checks call runtime methods or dispatch synthetic DOM events. Add real CDP Tab/Shift-Tab plus native Enter/Space activation for Range/Scrub on all owned profiles, asserting state and aria-pressed; add Home/ArrowDown for the Region select, asserting focused selection and canonical preset. Explicit initial focus is disclosed. Existing detailed semantic checks are unchanged. |
| Objective verification is not visual acceptance | Profile limitations already exclude full WCAG, real-device/cross-engine certification, performance SLO and value validation | Emit explicit `evidenceKind=automated_browser_check` and `visualAcceptance=not_assessed`; clarify the contract. Do not convert screenshot creation or green CI into human visual approval. |
| UI evidence/critique provenance | Workflow artifacts and logs exist, but individual capture JSON lacks revision/browser/file bindings | Add checkout commit, run URL/attempt, UTC recording time, actual browser version, captured URL, requested window/reduced-motion mode, and runner/DOM/screenshot SHA-256. Owned workflow verifies hashes and checkout identity before including provenance in aggregate evidence. |

### Preserved boundaries and limitations

- No changes to historical data, coordinates, temporal model, source package, geometry, Leonardo runtime behavior, or Region publication.
- Existing domain-specific assertions remain: 11 Presences / 9 Places, repeated Place identity, chronology-is-not-route, source/uncertainty closure, URL restoration, three native Region intervals and distinct geometries.
- Existing metrics are bounded approximations: DOM naming is not the browser accessibility tree; measured target selectors are buttons/range/select/summary, not every possible interactive element; overlay tests and text assertions do not establish universal occlusion/legibility.
- The keyboard scenarios cover the named controls, not every link, popup, focus trap or device. Initial programmatic focus is not evidence of reaching the control from page entry.
- Native 500 px headless mobile remains different from real 390 px mobile. Safari/Firefox, real touch, visual hierarchy, typography, contrast judgement and aesthetic consistency are not newly gated.
- Capture DOM/pixels precede the separate URL-restoration and keyboard-interaction scenarios. Their recorded URL identifies that capture state; later interaction results must not be described as the captured pixels.
- Checkout identity identifies test code, not the deployment commit at a public URL. Live Pages evidence is a separate artifact/run. No deployed revision is inferred solely from checkout or passing checks.
- A human critique must identify inspected URL/artifact, relevant state/viewport, review provenance and observations separately; no human review or participant result is synthesized here.
- No second framework, design tokens, Figma parity, heuristic taste checks or new capability/value claim. E1/E2 and formal value state are unchanged.

### Verification provenance

Implementation evidence is the PR's exact-head owned CI, per-profile capture JSON and aggregate `artemis-globe-browser-evidence.json`; each capture binds its DOM/screenshot hashes and test checkout. Pages retains the separate `region-live-failed-task-retest` artifact. Run links and final results are recorded in the implementation PR after checks complete. This document records coverage, not a retroactive PASS for historical captures.
