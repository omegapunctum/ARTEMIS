# ARTEMIS — PROJECT PHASES v7.9

## Status

- Type: canonical operational phases document.
- Date: 2026-09-05.
- Current phase: **5.1 — M5 bounded UX correction in progress in PR #411; full acceptance and publication pending**.
- Active issue: **#355**.
- Gate C: **completed / FREEZE**.
- Gate D: **OPEN / IN PROGRESS**.
- Public surfaces: Core landing at `/`, Leonardo Globe at `/globe/`, frozen Architecture Atlas compatibility surface at `/atlas/`.

## Phase 0 — Preserved history

The following work remains traceable but is not the active roadmap:

- Architecture Atlas product and data pipeline;
- FastAPI/auth/UGC/moderation/research compatibility platform;
- Gate A/B recovery packages and repository-governance evidence;
- Airtable World Model shadow schema and row plan;
- accepted Progressive Refinement v1 review envelope.

No historical artifact is deleted or reinterpreted by Core Reset.

## Phase 1 — ARTEMIS Core foundation [completed]

Preserved:

- source-aware spatial-temporal World Model;
- Claim → EvidenceLink → Source/locator;
- explicit uncertainty and coverage;
- Event, State, Process, Trajectory and temporal Region;
- Explorer State and Render Projection;
- frozen Leonardo-in-Romagna 1502 boundary;
- renderer parity and bounded MapLibre Globe runtime.

Passing these contracts proves representability and technical integrity, not product value.

## Phase 2 — Core Reset [completed]

Completed by PR `#393`.

The resulting boundary is:

- the root is a small ARTEMIS Core landing;
- Leonardo Globe at `/globe/` is the primary product-development/research surface;
- Architecture Atlas is isolated at `/atlas/` as compatibility-only;
- the required Core path does not depend on backend, Redis, moderation, Airtable or mutable review-routing documents;
- #392 does not block the read-only MVP critical path;
- frozen Gate C evidence and no-invented-geometry rules remain intact;
- ARTEMIS Core Check is the required product signal.

Core Reset was a narrowing inside #355. It did not reopen Gate C, promote historical Claims or complete Gate D.

## Phase 3 — Leonardo Temporal Map loop, iteration 1 [completed]

PR `#395` established the calendar-based life-path loop. The published manual check produced an explicit **`ITERATE`** result because:

- Range and Scrub looked too similar;
- the timeline did not read as the primary instrument;
- place selection exposed too much persistent text;
- single-click camera movement was too aggressive.

PR `#396` completed the bounded correction:

- the full-width bottom timeline is the primary time instrument;
- `Range` is a two-handle calendar interval and shows documented Presences overlapping the interval;
- `Scrub` keeps a chosen build origin plus one current-time cursor and progressively accumulates the path;
- map, timeline, selection and URL share one state;
- first click opens a compact popup without moving the camera;
- optional further action opens the right detail drawer;
- double-click may focus/zoom the selected place;
- earlier dashed connectors were chronology-only presentation and never historical route geometry; current M5 uses no spatial connector between unsupported Presence coordinates;
- no new Leonardo data, route geometry, historical coordinates or promoted Claims were introduced.

The current bounded corpus remains the four source-bound 1502 Romagna Presences. It is an interaction scaffold, not Leonardo's complete biography.

## Phase 4 — Fresh user check of the published loop [completed]

The fresh check of the published #396 interface reported that the interaction is now good enough to continue and that remaining visual problems are not the next priority.

Check whether a user can:

1. understand the difference between `Range` and `Scrub`;
2. use the bottom timeline as the primary time control;
3. understand how the visible path changes as time changes;
4. select a Presence without unwanted camera movement;
5. read concise place/date/activity information and reach source/uncertainty details when needed;
6. understand chronological sequence/period cues while exact historical routes remain unknown and unsupported Presence coordinates remain unconnected.

The allowed product result vocabulary was:

- `ITERATE` — improve the same product loop;
- `NARROW` — reduce content or interaction scope;
- `STOP/RETHINK` — stop this Globe/Temporal Map approach and revisit the product hypothesis.

The recorded result is **`ITERATE`**. The evidence and its limitations are preserved in `docs/work/2026-08-29_GATE_D_POST_396_USER_CHECK_v1.md`.

This check does not declare Gate D complete or claim validated historical/product capability.

## Phase 5A — Leonardo Major-Life Presence Scope v1 [completed]

The post-#396 `ITERATE` opened one source-aware candidate package of seven major-life Presences across 1452–1519. PR #400 completed independent review and froze the non-public candidate package without runtime authorization.

Completed evidence:

- source discovery and candidate selection;
- explicit inclusion/exclusion and whole-life coverage rationale;
- Claim/EvidenceLink/Source/locator and uncertainty mapping;
- cost and review design;
- no runtime promotion before a package freeze/review decision.

The package remains non-public and is not evidence of a live external-source adapter.

## Phase 5B — M2 One-source proof [completed]

M2 asks one bounded architecture/product question: can one real structured external fact pass through ARTEMIS into the existing Globe while preserving source identity, rights, temporal/spatial precision and uncertainty?

PR #401 merged the selected Wikidata birth Presence proof with green Core, Geospatial and Globe Boundary checks. The recorded result is `PROCEED_TO_M3`; this does not publish the proof or authorize M4.

## Phase 5C — M3 Multi-source proof [completed]

M3 asks whether one independent second provider can corroborate, refine or conflict with the existing Leonardo birth Presence while preserving both source identities and visible uncertainty.

PR #403 completed the exact two-provider/one-Presence proof. Wikidata and Museo Leonardiano remain distinct publisher identities; their birth dates agree exactly, while the spatial statements are preserved as a granularity refinement rather than collapsed into a stronger claim. The recorded result is `PROCEED_TO_M4`.

The proof does not establish upstream-independent corroboration, a hard-conflict case, production ingestion/storage or public user value.

## Phase 5D — M4 Architecture decision [completed]

M4 asks whether the completed M2/M3 evidence warrants `ADOPT`, `NARROW` or `REJECT` for the source-federated architecture direction.

The recorded result is `ADOPT`: source-specific reviewed intake may normalize into the canonical Claim/EvidenceLink/Source/Uncertainty path without becoming a second ontology. This is a semantic direction, not authorization for live federation, automatic reconciliation, generic ingestion/storage, public runtime promotion or new data.

PR #405 did not open a post-M4 implementation phase. The later M5 start occurred through explicit owner instruction, without an intervening repository decision record; that deviation is preserved rather than retroactively rewritten.

Context/layers, curation storage, persistence/sharing, renderer/provider work, generative AI, causal/counterfactual runtime, universal corpus and VR/AR remain unopened/gated.

## Phase 5E — M5 Whole-Life Runtime Proof [completed]

PR #406 merged and published the reviewed PR #400 major-life package in the existing Temporal Map as one bounded product proof:

- 11 Presence anchors: seven major-life plus four Romagna;
- six coarse life periods across 1452–1519;
- existing Range/Scrub, popup/drawer and shared URL-state behavior;
- no invented historical route geometry or new infrastructure.

The direct owner check recorded exactly `ITERATE`. The whole-life scale remains viable, while seven product findings require a separately scoped UX correction. The result does not open that implementation branch automatically.

## Phase 5F — M5 Bounded UX Correction v1 [in progress / PR #411]

The 2026-09-05 scope decision merged in PR #409 and opened one implementation branch, PR #411, for the seven observed M5 findings. The correction must make chronological order legible through non-route sequence/period/timeline semantics, clean popup/drawer state, reduce visual density and timeline height, remove responsive collisions, add current-M5 `EN / RU`, and preserve attribution visibility. Full acceptance checks, merge and publication remain pending.

It cannot draw unknown routes, add historical content, change Range/Scrub semantics, introduce a second state model or mix Export Airtable maintenance into the product diff. Publication requires automated Core/semantic checks and deterministic responsive evidence; a fresh manual product result follows publication.

## Rule

One active product vertical and at most one active milestone. M4 remains complete with `ADOPT`; M5 remains complete with `ITERATE`. The merged bounded UX decision opened exactly one correction branch, PR #411, and no other product branch.
