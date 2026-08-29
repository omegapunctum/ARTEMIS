# ARTEMIS — PRIORITIES v7.1

## Status

- Type: canonical active priorities.
- Date: 2026-08-29.
- Active cycle: Leonardo Temporal Map fresh user check after the first `ITERATE`.
- Active primary issue: GitHub issue `#355`.
- Gate C: completed / `FREEZE`.
- Gate D: `OPEN / IN PROGRESS`.
- Public entrypoint: ARTEMIS Core landing; Leonardo Globe is primary at `/globe/`, Architecture Atlas is compatibility-only at `/atlas/`.

## P0 — Validate the current Leonardo Temporal Map loop

The only active product question is whether the **current published #396 interaction** makes the spatial-temporal life-path model understandable enough to justify another iteration or a single next branch.

The load-bearing path remains:

`Leonardo sources/manifests → World Model → Explorer State → Render Projection → Globe + timeline + concise details`

Current required behavior:

- the full-width bottom timeline is the primary time instrument;
- `Range` is a two-handle calendar interval and shows documented Presences overlapping that interval;
- `Scrub` keeps a chosen build origin and one current-time cursor, progressively revealing the accumulated path;
- visible Presence selection is shared by timeline, map and URL;
- one click opens a compact popup without moving the camera;
- optional further action opens the right detail drawer;
- double-click may focus the selected place;
- source, locator, uncertainty, coverage and projection-loss details remain available through progressive disclosure;
- explicit unknown routes and geometry-withheld alternatives remain honest;
- dashed connectors mean chronology only and never historical route geometry;
- present-day context remains clearly separated from historical assertions;
- exploration remains URL-restorable and backend-independent.

The current bounded package remains honest:

- Gate C `FREEZE` evidence for #332/#360 is preserved byte-for-byte;
- historical Claims remain draft/rejected;
- no route or Region geometry is invented;
- `historical_corpus_ready=false` and `promotion_allowed=false`;
- four settlement coordinates are present-day source-bound reference anchors only;
- the four Romagna Presences are an interaction scaffold, not Leonardo's complete biography.

## P1 — Preserve the completed Core Reset boundary

Core Reset was completed by PR `#393`; it is no longer an active implementation task.

Preserve:

1. Leonardo Globe as the primary product-development/research surface.
2. Architecture Atlas at `/atlas/` as a compatibility baseline, not a second active product.
3. FastAPI, auth, Redis, drafts, moderation, Research Slices, Stories, Courses and uploads as frozen compatibility code outside the Core critical path.
4. Airtable legacy export and the nine empty World Model shadow tables outside the Core critical path.
5. Progressive Refinement v1 as accepted historical foundation evidence; editable refinement remains deferred.
6. ARTEMIS Core Check as the required product signal. Legacy checks run only for their owned compatibility paths or by manual dispatch.

Security fixes and preservation of accepted evidence remain allowed. New backend, storage, Airtable, UGC or platform capability requires evidence that the static read-only loop is insufficient.

## P2 — Fresh user check before more data or infrastructure

PR `#395` established the calendar life-path interaction. Its first published manual check produced `ITERATE` because Range/Scrub looked too similar, the timeline lacked primary visual weight, place selection was too persistent, and single-click camera movement was too aggressive.

PR `#396` implemented the bounded correction and is published. The next action is therefore **not** another infrastructure gate and **not** a broader Leonardo dataset.

Run a fresh user check of the current interface and observe whether the user can:

1. distinguish `Range` from `Scrub` and explain why visible Presences change;
2. use the timeline naturally as the primary time control;
3. understand the progressively accumulated path in Scrub;
4. select a Presence without unwanted camera motion;
5. retrieve concise place/date/activity meaning and reach source/uncertainty details when needed;
6. avoid interpreting dashed chronology as a known historical route.

Record exactly one next result:

- `ITERATE`;
- `NARROW`;
- `STOP/RETHINK`.

The fresh check does not by itself close Gate D or prove validated product value.

## P3 — Open at most one evidence-backed next branch

Only after the post-#396 decision may one next branch be opened. Candidate branches may include:

- one bounded source-aware data increment, such as roughly 6–10 major life Presences across 1452–1519;
- one measured local/global context or layer increment;
- curation/editorial storage;
- persistence/sharing;
- a measured renderer/provider improvement.

Do not open multiple branches from one `ITERATE` result.

## Preserved foundations

- #329 / PR #336 — reviewed World Model fixtures;
- #330 / PR #337 — uncertainty semantics;
- #339 / PR #346 — renderer-neutral architecture;
- #340 / PR #347 — Explorer State;
- #341 / PR #348 — Render Projection;
- #342 / PR #349 — geospatial asset boundary;
- #343 / PR #350 — MapLibre Globe spike;
- #344 / PR #351 — cross-renderer semantic parity;
- #345 / PR #352 — repository/runtime boundary;
- #332/#360 / PR #362 — frozen Leonardo-in-Romagna source boundary;
- #393 — Core Reset boundary;
- #395 — calendar-based Leonardo life-path interaction;
- #396 — first feedback-driven Temporal Map UX correction.

These are technical/product-development foundations, not final user-value evidence.

## Deferred

- #331 documented Relation predicates;
- #334 formal participant protocol as previously sequenced;
- #371/#373 Airtable historical import/review;
- editable Progressive Refinement runtime;
- broader Leonardo corpus before the current loop is rechecked;
- generative AI, causal/counterfactual runtime, universal corpus, VR/AR;
- production backend and dynamic Earth infrastructure.

## Execution order

1. Freshly check the published #396 Leonardo Temporal Map loop with a user.
2. Record exactly one `ITERATE`, `NARROW` or `STOP/RETHINK` result.
3. If justified, open at most one evidence-backed next branch.

## Completion rule

A change is complete when the core artifact works, source/uncertainty semantics are preserved, the relevant Core checks pass and the next user-facing question is explicit. Implementation success, public deployment and visual polish do not by themselves equal product validation.