# ARTEMIS — PRIORITIES v6.1

## Статус

- Тип: canonical active priorities.
- Дата: 2026-08-08.
- Active cycle: World Model Contract.
- Active primary issue: GitHub issue `#331`.
- Accepted foundation: PR `#328` / issue `#327`.
- Parallel non-blocking R&D: 3D Globe / renderer architecture, parent issue `#339`.

Работа получает приоритет, если она восстанавливает coherent spatial-temporal foundation, делает first World Slice проверяемым, предотвращает необратимую реализацию superseded Concept v2 или создаёт обратимо проверяемую renderer infrastructure без изменения product-validation order.

## P0 — Foundation decision

### P0.1 Canonical alignment — COMPLETED

- Concept v3;
- product thesis/scope/truth;
- spatial-temporal world-model contract;
- entity and epistemic contracts;
- Foundation decision and migration matrix;
- operational docs/lifecycle registry;
- no runtime capability overclaim.

Exit: Foundation v3 PR reviewed and merged.

### P0.2 Hold superseded execution — COMPLETED

- no #323–#325 migration;
- no #286–#289 / #308–#313 execution as active path;
- PR #314 unmerged;
- security/compatibility fixes only where necessary;
- preserve completed Architecture Atlas assets.

### P0.3 World-model contract and fixtures — ACTIVE / #331

Completed foundations:

- #329 / PR #336 — executable world-model fixtures v1;
- #330 / PR #337 — executable uncertainty semantics v1.

Active dependency:

- #331 — relation ladder: coexistence, possible encounter, documented encounter, interaction, influence and causality.

Required semantic surface remains:

- Entity/Event/State/Process/Trajectory/Region/Layer semantics;
- temporal/spatial precision;
- uncertainty and alternative reconstructions;
- relation ladder;
- corpus coverage;
- deterministic fixtures.

Exit: relation semantics close the remaining P0 ambiguity before the first historical World Slice is frozen.

## P1 — First World Slice

### P1.1 Life in Context content

- Leonardo trajectory segments;
- selected local Events and regional States;
- at least one Process and changing Region;
- selected contemporaries;
- co-presence separate from documented Relations;
- selected synchronous global Events;
- sources, locators, uncertainty and coverage;
- preparation/review cost.

### P1.2 Synchronized explorer

- one shared map/time/layer state;
- trajectory, Events, Regions/States and details;
- local/global context;
- source/uncertainty access;
- honest static Pages-first contour;
- responsive/accessibility baseline.

The first controlled implementation under #333 remains a 2D MapLibre/static-first validation contour. It is not replaced by the parallel Globe R&D track.

### P1.3 Contextual-learning validation

- same-content baseline;
- frozen task/timebox/rubric;
- context reconstruction;
- simultaneity discovery;
- change/trajectory comprehension;
- relation overclaim errors;
- source/uncertainty comprehension;
- explicit decision.

## P2 — Maintainability required by P0/P1

- compatibility adapters without invented semantics;
- release/docs drift checks;
- browser regression for affected flows;
- source/media rights;
- security/reliability/dependency fixes;
- migration design only after contract approval;
- no framework rewrite.

## R&D-G — Parallel 3D Globe / renderer architecture

Status: **ACTIVE PARALLEL R&D / NON-BLOCKING**.

Parent: #339.

Purpose: allow ARTEMIS to develop a Google-Earth-class spatial presentation direction without turning the current Point-only MapLibre compatibility contract into the permanent domain model and without delaying the controlled Foundation v3 validation path.

Required rule:

**one spatial-temporal world model → one renderer-neutral Explorer State → explicit render projections → multiple presentation renderers.**

Child work:

- #340 — renderer-neutral Explorer State;
- #341 — World Model → Render Projection contract;
- #342 — geospatial assets / terrain / imagery contract;
- #343 — minimal 3D Earth runtime spike;
- #344 — cross-renderer semantic parity tests;
- #345 — repository/runtime boundary and Globe CI contour.

R&D-G guardrails:

- does not block #331 → #332 → #333 → #334;
- does not make 3D `PUBLIC NOW` or product-validated;
- does not replace #333 with a 3D implementation;
- does not create a second historical/data source of truth;
- does not force a frontend framework or repository rewrite;
- terrain/imagery are rendering assets, not historical truth by default;
- World Model, uncertainty, evidence and relation semantics remain renderer-independent;
- any promotion into active product scope requires executable evidence and explicit owner-doc updates.

Architecture working record: `docs/work/2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md`.

## Preserved technical foundations

- public MapLibre/GeoJSON baseline;
- UUID/source identity split;
- Source/Media export;
- semantic ETL/release gate;
- Architecture Atlas corpus and Gate A fixtures;
- executable world-model and uncertainty fixtures;
- mutable ResearchSlice v2 backend capability;
- fail-closed Pages API configuration;
- Concept v2 epistemic discipline retained where compatible.

These are assets, not evidence that Foundation v3 or the 3D Globe runtime is implemented publicly.

## Frozen backlog

- generative AI;
- causal/counterfactual engine;
- high-fidelity / production 3D dynamic terrain beyond the bounded R&D-G spike;
- VR/AR;
- Stories/Courses expansion;
- open UGC;
- institutional workflow;
- universal corpus;
- native apps;
- enterprise integrations;
- heavy scaling;
- immutable revision migration unless later required.

Note: bounded renderer/globe R&D under #339–#345 is explicitly removed from the old blanket freeze on all 3D work. Product-scale dynamic Earth remains gated.

## Execution order

Primary validation path:

1. Preserve #329 / PR #336 world-model fixtures and #330 / PR #337 uncertainty semantics as reviewed READY foundations.
2. Resolve #331 relation-ladder semantics.
3. Freeze the #332 Leonardo World Slice.
4. Implement the #333 synchronized 2D explorer.
5. Run #334 controlled validation.
6. Record one decision and open at most one evidence-backed product branch.

Parallel Globe R&D path:

1. #340 renderer-neutral state and #341 render-projection contract.
2. #342 geospatial asset/terrain/imagery contract.
3. #343 bounded 3D Earth runtime spike.
4. #344 semantic parity gate.
5. #345 repository/runtime and CI integration decision.
6. Decide whether to stop, continue as R&D, or propose promotion. Promotion is not automatic.

## Completion rule

A priority closes only with:

- artifact;
- relevant review/test evidence;
- synchronized owner docs;
- honest current capability statement;
- no semantic contradiction;
- explicit next dependency or stop decision.