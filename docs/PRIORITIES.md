# ARTEMIS — PRIORITIES v7.9

## Status

- Type: canonical active priorities.
- Date: 2026-09-06.
- Active cycle: `Gate D closeout/review`; M5 bounded UX correction completed with `PROCEED_TO_GATE_D_REVIEW`; #409/#411/#412 are completed evidence.
- Active primary issue: GitHub issue `#355`.
- Gate C: completed / `FREEZE`.
- Gate D: `OPEN / IN PROGRESS`.
- Public entrypoint: ARTEMIS Core landing; Leonardo Globe is primary at `/globe/`, Architecture Atlas is compatibility-only at `/atlas/`.

## P0 — Accept M5 closeout and record the Gate D exit

M1 is complete with `ITERATE`. PR #400 completed the independently reviewed major-life candidate package. PR #401 completed M2, PR #403 completed M3, and PR #405 recorded M4 as `ADOPT`. The owner then directly instructed M5 without an intervening repository decision record. PR #406 merged and published the bounded whole-life proof. That sequence is a recorded governance deviation, not retroactive authorization invented for M4.

The direct owner check of the published 1452–1519 loop recorded exactly `ITERATE`. It found seven issues: missing relational legibility, stale popup after opening details, oversized elements, excessive timeline height, header/map-control collision, missing current-M5 `EN / RU` switching and drawer/attribution overlap.

PR #409 scoped the correction; PRs #411 and #412 implemented and published it. The owner accepted #412 on 2026-09-06 with `PROCEED_TO_GATE_D_REVIEW`. [work/2026-09-06_M5_UX_CLOSEOUT_AND_GATE_D_REVIEW_v1.md](work/2026-09-06_M5_UX_CLOSEOUT_AND_GATE_D_REVIEW_v1.md) closes this execution cycle and records one bounded review. Its recommendation is `ADVANCE_TO_GATE_E`; Gate D itself remains open until an explicit synchronized exit. M4 `ADOPT` is completed architecture evidence, not the Gate D decision.

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
- dashed connectors express chronology only and never historical route geometry; the published #412 legend preserves that distinction;
- present-day context remains clearly separated from historical assertions;
- exploration remains URL-restorable and backend-independent.

The current bounded package remains honest:

- Gate C `FREEZE` evidence for #332/#360 is preserved byte-for-byte;
- historical Claims remain draft/rejected;
- no route or Region geometry is invented;
- `historical_corpus_ready=false` and `promotion_allowed=false`;
- four settlement coordinates are present-day source-bound reference anchors only;
- the runtime contains 11 reviewed coarse Presence anchors — seven major-life anchors plus the four Romagna Presences — and six periods across 1452–1519;
- the result remains a bounded R&D proof, not Leonardo's complete biography.

The M3 proof remains limited to the existing Leonardo birth Presence, Wikidata and Museo Leonardiano. It demonstrates a viable source-aware comparison path, but it does not prove upstream-independent historical corroboration, a hard-conflict case, broad operational value, production ingestion/storage or public user value. M4 adopts the direction without converting these missing proofs into implementation authorization.

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

## P2 — Preserve the post-#396 decision boundary

PR `#395` established the calendar life-path interaction. Its first published manual check produced `ITERATE` because Range/Scrub looked too similar, the timeline lacked primary visual weight, place selection was too persistent, and single-click camera movement was too aggressive.

PR `#396` implemented the bounded correction and is published. The fresh check recorded `ITERATE`: preserve the current interaction, treat remaining visual issues as non-priority and continue through one bounded data branch.

This result does not close Gate D, prove formal user value or authorize another UI iteration. Preserve the exact decision record in `docs/work/2026-08-29_GATE_D_POST_396_USER_CHECK_v1.md`.

The recorded post-#396 vocabulary was `ITERATE`, `NARROW` or `STOP/RETHINK`; the selected result was `ITERATE`.

## P3 — Keep completed correction evidence closed

The earlier merged decision opened exactly one UX implementation branch, followed by the owner-directed #412 correction. Both are completed evidence; the correction outcome is `PROCEED_TO_GATE_D_REVIEW`. Historical M5 `ITERATE` remains preserved. No implementation branch is currently opened.

- preserve both completed proofs and their source/uncertainty boundaries unchanged;
- preserve `ADOPT` as one semantic path, not a live-federation capability;
- preserve PR #406 without widening its data, interaction or infrastructure scope;
- do not infer any second successor branch from publication, CI success or the M5 result.

Do not open context/layers, curation storage, persistence/sharing, renderer/provider work or another feature branch from the M5 result. Export Airtable CI repair #410 is completed and confirmed by scheduled successes, latest run 34005145312.

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
- a third provider or second Presence before a separate bounded branch decision;
- generic provider, federation, reconciliation, ingestion or storage infrastructure;
- generative AI, causal/counterfactual runtime, universal corpus, VR/AR;
- production backend and dynamic Earth infrastructure.

## Execution order

1. Review/merge the single decision-only M5 closeout and Gate D review PR.
2. Use its completed evidence matrix; record one Gate D exit: `ADVANCE_TO_GATE_E / NARROW / REJECT`. Recommendation: `ADVANCE_TO_GATE_E`; no concrete material implementation gap identified.
3. Keep M4 `ADOPT`, M5 original `ITERATE` and correction `PROCEED_TO_GATE_D_REVIEW` separate.
4. Preserve confirmed scheduled CI repair #410. Open no new implementation unless a concrete material gap is identified.

## Completion rule

A change is complete when the core artifact works, source/uncertainty semantics are preserved, the relevant Core checks pass and the next user-facing question is explicit. Implementation success, public deployment and visual polish do not by themselves equal product validation.
