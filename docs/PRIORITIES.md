# ARTEMIS — PRIORITIES v7.5

## Status

- Type: canonical active priorities.
- Date: 2026-09-01.
- Active cycle: `M4 — Architecture decision` after PR #403 completed M3 with `PROCEED_TO_M4`.
- Active primary issue: GitHub issue `#355`.
- Gate C: completed / `FREEZE`.
- Gate D: `OPEN / IN PROGRESS`.
- Public entrypoint: ARTEMIS Core landing; Leonardo Globe is primary at `/globe/`, Architecture Atlas is compatibility-only at `/atlas/`.

## P0 — Decide the architecture direction; do not build it

M1 is complete with `ITERATE`. PR #400 completed the independently reviewed major-life candidate package without runtime authorization. PR #401 completed M2 with one pinned Wikidata birth Presence. PR #403 completed M3 with Wikidata and Museo Leonardiano preserved as separate publisher identities for the same Presence, exact date agreement and an explicit spatial-granularity refinement. The recorded M3 result is `PROCEED_TO_M4`. The only active question is whether that bounded evidence supports `ADOPT`, `NARROW` or `REJECT` for the source-federated architecture direction.

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

The M3 proof remains limited to the existing Leonardo birth Presence, Wikidata and Museo Leonardiano. It demonstrates a viable source-aware comparison path, but it does not prove upstream-independent historical corroboration, a hard-conflict case, broad operational value, production ingestion/storage or public user value. M4 must decide from this evidence without adding implementation.

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

## P3 — Keep M4 decision-only

The single opened branch is one architecture decision over the completed M2/M3 evidence.

- preserve both completed proofs and their source/uncertainty boundaries unchanged;
- compare demonstrated value with the recorded evidence limitations;
- distinguish incremental source-aware semantics from a premature generic federation platform;
- record exactly one exit decision: `ADOPT`, `NARROW` or `REJECT`;
- state the implementation consequences of the selected outcome without implementing them in the decision PR.

Do not open context/layers, curation storage, persistence/sharing, renderer/provider work or another branch from the same `ITERATE` result.

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
- public integration of the PR #400 candidate package;
- a third provider or second Presence before the M4 decision;
- generic provider, federation, reconciliation, ingestion or storage infrastructure;
- generative AI, causal/counterfactual runtime, universal corpus, VR/AR;
- production backend and dynamic Earth infrastructure.

## Execution order

1. Compare the M2 one-source and M3 two-source evidence against the long-term architecture direction.
2. Weigh the demonstrated semantic/projection fit against unknown upstream dependence, missing conflict evidence and unmeasured operational cost.
3. Select exactly one M4 outcome: `ADOPT`, `NARROW` or `REJECT`.
4. Record the selected scope and consequences before any new source, data, runtime or infrastructure work.

## Completion rule

A change is complete when the core artifact works, source/uncertainty semantics are preserved, the relevant Core checks pass and the next user-facing question is explicit. Implementation success, public deployment and visual polish do not by themselves equal product validation.
