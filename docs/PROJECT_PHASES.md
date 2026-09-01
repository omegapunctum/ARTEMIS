# ARTEMIS — PROJECT PHASES v7.4

## Status

- Type: canonical operational phases document.
- Date: 2026-09-01.
- Active phase: **5.0 — M3 multi-source proof**.
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
- dashed connectors remain chronology-only presentation and never historical route geometry;
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
6. understand that dashed connectors are chronology only and that exact historical routes remain unknown.

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

## Phase 5C — M3 Multi-source proof [active]

M3 asks whether one independent second provider can corroborate, refine or conflict with the existing Leonardo birth Presence while preserving both source identities and visible uncertainty.

The active scope is exactly two providers and one Presence. A third provider, another Presence, a generic federation framework, public runtime promotion and M4 remain closed.

Context/layers, curation storage, persistence/sharing, renderer/provider work, generative AI, causal/counterfactual runtime, universal corpus and VR/AR remain unopened/gated.

## Rule

One active product loop and one active milestone. The next decision is `PROCEED_TO_M4`, `NARROW_M3` or `STOP_M3`; a green implementation does not decide M4 or authorize public data expansion.
