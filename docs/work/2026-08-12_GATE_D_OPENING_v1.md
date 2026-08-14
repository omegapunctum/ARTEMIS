# ARTEMIS — Gate D Opening v1

## Status

- Type: active product lifecycle decision.
- Date: 2026-08-12.
- Active vertical: `Life in Context / source-aware Globe MVP`.
- Owner issue: `#355`.
- Gate: `D / in_progress`.
- Public capability change: amended 2026-08-14 for a labelled `/globe/` R&D review preview only; no product or historical-content promotion.

`2026-08-14_GLOBE_PUBLIC_REVIEW_PREVIEW_DECISION_v1.md` is the later explicit deployment decision. It changes review reachability without reopening Gate C or closing Gate D.

## 1. Decision

Open Gate D as the single active product gate.

Gate D builds one bounded source-aware Globe experience from the already frozen Leonardo-in-Romagna 1502 World Slice. It does not reopen Gate C, promote the historical Claims or create a second data model. The generated experience may now be viewed through the labelled public R&D preview.

The only permitted semantic path is:

`frozen Gate C World Slice → Explorer State → Render Projection → 2D + Globe adapters`

## 2. Frozen input

Gate D consumes the repository package under:

`fixtures/world_slices/leonardo_romagna_1502/v1/`

The completed Gate C identity remains machine-pinned in `docs/project_state.json`:

- frozen commit: `bd2e103cdeec615cb19f0a4293c708fe37a4ae52`;
- frozen tree: `757fc3d0701e825e865ceeec401d233484f066b7`;
- reviewed content digest: `1323ca8f0e85e0d1287cdf8d78db8fcfd907551d7a7dbb37646725cbba72ddca`;
- decision: `FREEZE`;
- two independent Gate C reviews: `READY`, zero unresolved critical/material findings.

The package remains non-public and epistemically unchanged: Claims remain draft, three route gaps remain `unknown_route`, Region geometry remains withheld and documented Relation predicates remain prohibited.

## 3. Progressive fidelity decision

Gate D uses the minimum sufficient fidelity needed to validate the synchronized experience.

The merged Airtable pre-write contour #371 / PR #372 established a lossless empty schema, deterministic 154-row plan and fail-closed write boundary. It is not required to render Gate D because the authoritative frozen repository package is already a sufficient input.

Therefore:

- the 154 historical rows are not imported before Gate D by default;
- #371 and its independent review #373 are deferred outside the active critical path;
- all nine Airtable shadow tables remain non-authoritative and empty;
- `historical_rows_authorized=false` remains binding;
- future Airtable import requires a separately reopened data-governance decision, exact-digest independent review, controlled write, readback and normalized round-trip parity.

This deferral removes duplicate work without discarding the schema/mapping evidence.

## 4. Required Gate D experience

The bounded experience must provide:

1. one shared selected instant or interval for every projection;
2. synchronized layer visibility and temporal change;
3. canonical selection/picking by World Model identity;
4. Event, State, Process, Trajectory and temporal Region projection;
5. explicit display of unresolved routes and geometry-withheld Regions without invented geometry;
6. source, locator, evidence state and material uncertainty in the inspector;
7. visible coverage/known gaps and reconstruction/projection-loss semantics;
8. local context plus selected global simultaneity without implying interaction;
9. Earth context with explicit provider, attribution, temporal role, licensing and secret/cache policy;
10. executable 2D/Globe semantic parity;
11. representative desktop/mobile, keyboard, focus, reduced-motion, accessibility and performance evidence;
12. a reproducible generated review artifact, optionally served through the authorized `/globe/` R&D preview.

## 5. Implementation boundary

- Start from the generated MapLibre Globe artifact and accepted renderer-neutral contracts.
- Keep root `index.html` and the current 2D Architecture Atlas as the public baseline and rollback path.
- Keep Globe work isolated and generated; public exposure is limited to the explicit `/globe/` R&D review decision.
- Do not move to `apps/globe/` unless evidence supports a maintained experimental application.
- Do not switch to Cesium without a measured MapLibre blocker.
- Do not create a new backend, framework or historical dataset merely for interface convenience.

## 6. Relation and epistemic boundary

Issue #331 is deferred, not implemented. Before its contract is separately accepted:

- derived proximity/co-presence may be displayed as a computed observation;
- possible encounter may appear only as explicit inference with assumptions;
- documented encounter, interaction, influence and causal predicates are prohibited;
- no visual interpolation may strengthen time, route, boundary or relation claims;
- the rejected Cesena `ff. 9r–10r` Claim remains rejected.

## 7. Out of scope

- product-ready/default Globe deployment or promotion of draft candidate content as accepted historical truth;
- historical Airtable import and round-trip execution;
- documented Relation predicates;
- exact route or Region geometry reconstruction;
- broader Leonardo/world corpus;
- AI generation or AI view control;
- VR/AR;
- universal or photorealistic historical Earth;
- causal/counterfactual runtime;
- unrelated backend/framework/repository rewrite.

## 8. Exit contract

Gate D may record exactly one decision:

- `ADVANCE_TO_GATE_E` — the bounded experience is ready for task-based evidence collection;
- `NARROW` — reduce experience/content/technical scope and continue Gate D;
- `REJECT` — stop the current Gate D approach and record why.

Only `ADVANCE_TO_GATE_E` may open Gate E. Gate D completion does not itself publish the Globe.

Required exit evidence:

- the bounded experience exists and is reproducible;
- relevant release, repository-boundary, geospatial and parity checks pass on exact head;
- no critical semantic loss or invented precision remains;
- known UX/accessibility/performance gaps and implementation cost are recorded;
- current capability wording remains explicitly R&D/candidate-state and truthful;
- #355 and `docs/project_state.json` record the same decision.
