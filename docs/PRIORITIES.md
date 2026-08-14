# ARTEMIS — PRIORITIES v6.8

## Статус

- Тип: canonical active priorities.
- Дата: 2026-08-14.
- Active cycle: Globe MVP.
- Active primary issue: GitHub issue `#355`.
- Completed recovery foundation: issue `#344` / PR `#351`.
- Current public baseline: root 2D MapLibre runtime; no public Globe promotion is implied.

The active product decision is recorded in `docs/work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md`.

## P0 — Restore repository truth and parity — COMPLETED

### P0.1 Lifecycle recovery

- keep PR #338 closed as superseded and issue #331 explicitly `DEFERRED`;
- preserve #331 as the required gate before documented Relation predicates enter a real World Slice/runtime;
- correct the incomplete governance merge from PR #354;
- make canonical owners, agent routing and executable lifecycle guards agree on #355;
- restore a green Release Discipline Gate.

### P0.2 Cross-renderer semantic parity — COMPLETED / #344 / PR #351

- PR #351 was synchronized with current `main`;
- selected-object / active-focus fixture drift was repaired against the accepted Explorer State;
- object identity, time-boundary membership, uncertainty, alternatives, evidence and projection-loss semantics are executable;
- screenshot/visual regression remains separate from semantic parity;
- the recovered parity and repository gates passed before merge.

Exit achieved: `main` is green, #344 is closed by the merged parity implementation, and governance describes the evidence actually present.

## P1 — First real Globe World Slice

Freeze one deliberately small, source-aware corpus boundary under #355.

Required content:

- at least one Event, State, Process, Trajectory and temporally changing Region;
- Claims, EvidenceLinks, locators, uncertainty and alternative reconstructions;
- explicit coverage, inclusion/exclusion rules and known gaps;
- geometry provenance and licensing;
- measured curation/review cost.

The initial candidate is the bounded Leonardo / Life in Context slice delivered through #332, while #355 owns the active cross-cutting vertical.

The former marker `Active Gate C delivery: #332/#360` is superseded. Gate C is completed by a `FREEZE` decision for #332/#360. The non-public Leonardo-in-Romagna boundary covers 8 August–31 December 1502 with institutional source candidates, pinned university-press locators, explicit unknown-route segments, temporal geometry-withheld Region states, known gaps and measured preparation/review cost. Two independent reviews on one Git-bound revision are `READY` with zero unresolved critical/material findings. The Claims and EvidenceLinks remain draft rather than READY historical data; the separate Cesena wall-survey folio Claim remains rejected from the supported set. Gate D is now in progress under #355 and consumes this frozen package without upgrading its historical readiness.

Until #331 is accepted, the slice may expose derived proximity/co-presence only. It must not publish documented encounter, interaction, influence or causal predicates.

## P2 — Source-aware Globe MVP

The Globe is the primary interface-development surface for this cycle.

Completed #377 / PR #378 owns the accepted append-only refinement contract. Gate D may continue to
read and render the frozen Gate C package, but write/edit/refinement behavior still requires a
separate implementation authorization. Contract acceptance did not reopen Gate C or change
`project_state` capability.

Required interaction:

- one shared time/interval state;
- synchronized layers and visible temporal change;
- canonical selection/picking;
- Event, State, Process, Trajectory and Region rendering;
- explicit unresolved routes and alternative reconstructions;
- source, locator, uncertainty, coverage and projection-loss access;
- modern terrain/imagery shown as attributed context, not timeless historical truth;
- desktop/mobile/accessibility and representative performance checks.

Completed Gate D increments:

- PR #379 consumes the frozen Leonardo package directly through World Model → Explorer State → Render Projection and keeps all historical geometry withheld;
- PR #380 provides 96 deterministic Explorer views from six source-native temporal presets × 16 semantic-layer combinations, with synchronized timeline, layers, selection/picking, inspector, URL restoration, keyboard operation and reduced-motion behavior;
- PR #382 provides pinned bundled Natural Earth 1:110m Land `present_day_context` plus provenance, attribution, temporal-role, licensing, cache and secret policy while terrain remains synthetic/non-live;
- PR #383 provides desktop/tablet/hosted-mobile Chromium evidence, accessible-name/target-size/overflow/overlay checks and responsive overlay fixes; all six triggered workflows passed;
- PR #385 replaces premature virtual-time screenshots with same-page wall-clock CDP capture, requires non-zero loaded/rendered Natural Earth features and restores legible hosted desktop/tablet/mobile Earth context; all six triggered workflows passed;
- the generated artifact remains non-public and Gate D remains open.

Remaining Gate D work:

- normal-browser real desktop and 390 CSS px mobile interaction/visual evidence; hosted 500 px evidence remains non-equivalent to a real-device pass;
- assistive-technology review and representative non-virtual performance observations; hosted wall-clock metrics remain diagnostic only;
- one explicit Gate D exit decision.

The current 2D renderer remains:

- the public compatibility baseline;
- a same-content comparison renderer;
- a semantic parity target;
- a rollback path.

MapLibre GL JS remains the leading MVP engine. CesiumJS comparison requires a measured blocker in terrain, 3D Tiles, precision, scene complexity or performance.

## P3 — Gate D closeout evidence and one decision

Before Gate D exit:

- preserve the reproducible non-public generated review artifact from PRs #379–#385;
- verify semantic parity on the bounded frozen corpus;
- collect real-device/browser, accessibility and performance evidence;
- preserve the completed #382 provider availability/licensing/attribution/cache/security boundary and evaluate any future live provider separately;
- define rollback and current-truth/release implications;
- prepare the Gate E task protocol, but do not run participant validation before `ADVANCE_TO_GATE_E`.

Record exactly one result:

- `ADVANCE_TO_GATE_E`;
- `NARROW`;
- `REJECT`.

Only `ADVANCE_TO_GATE_E` opens #334 participant evidence work. Public promotion remains a separate later decision.

## Accepted renderer foundations

Preserved executable architecture evidence:

- #339 / PR #346 — renderer-neutral architecture;
- #340 / PR #347 — Explorer State;
- #341 / PR #348 — Render Projection;
- #342 / PR #349 — geospatial asset/provider boundary;
- #343 / PR #350 — browser-executed MapLibre Globe spike;
- #344 / PR #351 — cross-renderer semantic parity.
- #345 / PR #352 — repository/runtime/CI boundary.

PR #354 attempted to close the lifecycle but merged only a workflow change and a failing guard, without the declared canonical owner updates. Its intended evidence claim is therefore superseded by the recovery decision above.

## Preserved technical foundations

- public MapLibre/GeoJSON baseline;
- reviewed #329 World Model and #330 uncertainty fixtures;
- one World Model → Explorer State → Render Projection path;
- UUID/source identity split;
- Source/Media export and semantic ETL/release gate;
- Architecture Atlas corpus and Gate A fixtures;
- mutable ResearchSlice v2 backend compatibility;
- fail-closed Pages API configuration.

These assets do not prove a public Globe, historical terrain coverage, a real Foundation v3 corpus or user value.

## Deferred and frozen work

Deferred:

- #331 relation predicates, reactivated before documented Relations enter the real slice/runtime;
- #334 validation work until Gate E; #333 is superseded by the #355 Gate D contour;
- #371/#373 Airtable historical import and independent mapping review; the merged preflight remains fail-closed with empty tables and `historical_rows_authorized=false`.

Frozen:

- generative AI;
- automatic causal/counterfactual engine;
- public production Globe before promotion evidence;
- universal or photorealistic historical terrain reconstruction;
- VR/AR;
- universal corpus;
- framework/backend/repository rewrite without a measured blocker;
- product/platform expansion unrelated to #355.

Security, compatibility and critical reliability maintenance remain allowed.

## Execution order

1. Preserve the completed governance, Release Discipline and #344 parity foundations.
2. Freeze and curate the first real bounded World Slice through #332 within #355 — completed/FREEZE.
3. Preserve the completed #379/#380 frozen-package and synchronized-interaction increments.
4. Complete Earth-context policy plus desktop/mobile, accessibility and representative performance evidence.
5. Record exactly one Gate D decision: `ADVANCE_TO_GATE_E`, `NARROW` or `REJECT`.

## Completion rule

A priority closes only with:

- an artifact;
- relevant test/review evidence;
- synchronized owner docs and issue lifecycle;
- honest public/current capability wording;
- no semantic fork or invented precision;
- an explicit next dependency or stop decision.
