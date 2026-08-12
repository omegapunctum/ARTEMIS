# ARTEMIS — PROJECT PHASES v6.5

## Статус

- Тип: canonical operational phases document.
- Дата: 2026-08-12.
- Активная фаза: **4.8 Globe MVP vertical / real World Slice**.
- Active primary issue: **#355**.
- Completed Gate C delivery: **#332/#360 / Leonardo-in-Romagna World Slice 1502**.
- Completed recovery foundation: **#344 / PR #351**.
- Public runtime: unchanged 2D MapLibre baseline.

Фазы определяют порядок исполнения. North Star принадлежит `ARTEMIS_CONCEPT.md`; активное решение принадлежит `docs/work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md`.

## Принцип перехода

Фаза закрывается только по exit evidence. Документ, schema, synthetic fixture или визуально работающий Globe сами по себе не подтверждают historical content quality, semantic parity, public capability or user value.

## Фазы 0–4 — Technical baseline [закрыты с ограничениями]

Сохранены:

- MapLibre/GeoJSON public map;
- Airtable → ETL → `data/*`;
- FastAPI backend baseline;
- auth/UGC/moderation/research compatibility code;
- release/workflow/documentation discipline;
- PWA/UX baseline.

Ограничения принадлежат `PROJECT_TRUTH.md`.

## Фаза 4.5 — Concept v2 Architecture Atlas validation [остановлена]

Статус: **SUPERSEDED BEFORE GATES B–E**.

Завершённые Architecture Atlas artifacts сохраняются, но старый #323–#325 execution path не возобновляется.

## Фаза 4.6 — Foundation v3 [завершена]

Foundation v3 / PR #328 закрепила spatial-temporal world model, evidence, uncertainty, change objects and Life in Context as the first candidate vertical.

## Фаза 4.7 — World Model foundations [частично завершена]

Completed:

- #329 / PR #336 — reviewed World Model fixtures;
- #330 / PR #337 — reviewed uncertainty semantics.

Active foundation maintenance:

- #377 — progressive refinement/source-native fidelity contract; exact lifecycle is owned by its
  contract/registry, and runtime/storage still requires separate authorization for mutable knowledge refinement.

Deferred:

- #331 — documented Relation predicate semantics; reopen before such predicates enter the corpus/runtime.

#331 no longer blocks Globe infrastructure, time/layer synchronization or a real slice without documented Relations. It becomes blocking before documented encounter, interaction, influence or causal predicates enter the corpus/runtime. Derived proximity/co-presence remains separate meanwhile.

## Фаза 4.8 — Globe MVP vertical

Статус: **ACTIVE / ISSUE #355**.

### Gate A — Repository recovery

- completed in PRs #356–#357;
- canonical owners agree on #355;
- PR #338 remains closed and #331 deferred;
- Release Discipline Gate is green.

### Gate B — Cross-renderer parity

- completed in #344 / PR #351;
- selected-object / active-focus fixture drift is repaired;
- time-boundary, identity, uncertainty, alternative reconstruction, evidence and projection-loss semantics are executable;
- parity and required repository workflows passed before merge.

### Gate C — Real World Slice

- completed with `FREEZE` through #332/#360 and `docs/work/2026-08-09_LEONARDO_WORLD_SLICE_SCOPE_v1.md`;
- the analytical 8 August–31 December 1502 Romagna selection boundary is frozen without claiming historical content readiness;
- one bounded source-aware slice is frozen as a non-public capability boundary;
- include Event, State, Process, Trajectory and temporally changing Region;
- bind Claims/EvidenceLinks/locators/uncertainty;
- declare coverage, known gaps, geometry provenance, licensing and cost;
- omit documented Relation predicates until #331 is accepted.

### Gate D — Source-aware Globe experience

- **ACTIVE / IN PROGRESS** under #355; opened separately after the Gate C freeze;
- consume the frozen repository package directly; #371/#373 Airtable import/review are deferred and no historical write is authorized;
- read/render work may proceed over the frozen package, but editable precision/history behavior
  requires the recorded #377 decision plus separate implementation authorization; #377 does not change Gate D lifecycle state;
- consume World Model → Explorer State → Render Projection;
- synchronize time, layers and selection;
- expose sources, uncertainty, alternatives, coverage and projection losses;
- preserve unresolved trajectories without invented lines;
- treat modern terrain/imagery as contextual geospatial assets;
- verify desktop/mobile/accessibility and representative performance.

### Gate E — Evidence and decision

- deferred until Gate D exit evidence exists; issue #334 is not active during Gate D;
- provide a reproducible non-public preview/review artifact;
- compare against the current 2D same-content baseline where useful;
- test contextual understanding and semantic literacy rather than visual novelty alone;
- record one result: continue generated R&D, promote to maintained experimental app, narrow/rework, or stop/rethink.

Public promotion is a separate decision after provider/licensing/security/rollback/current-truth evidence.

## Completed renderer foundations

Accepted executable foundations:

- #339 / PR #346 — renderer-neutral architecture;
- #340 / PR #347 — shared Explorer State;
- #341 / PR #348 — deterministic Render Projection;
- #342 / PR #349 — geospatial asset/provider boundary;
- #343 / PR #350 — MapLibre Globe runtime spike;
- #344 / PR #351 — cross-renderer semantic parity;
- #345 / PR #352 — repository/runtime/CI boundary.

The generated Globe spike remains R&D evidence. It is the implementation seed for #355, not a public product surface.

## Current repository/runtime boundary

Until Gate E explicitly promotes the Globe:

- root `index.html` remains the only public Pages app;
- generated Globe artifacts stay non-public and disposable;
- public MapLibre 4.7.1 remains unchanged;
- the Globe spike may pin MapLibre 5.24.0 in isolation;
- an `apps/globe/` move requires a separate maintained-application decision;
- no renderer may own a separate historical model.

## Independent future branches

Still gated:

- source-bound generative AI;
- automatic causal/counterfactual engine;
- universal or production-scale historical terrain;
- broader World Slices beyond one evidence-backed decision;
- institutional workflows;
- VR/AR;
- unrelated platform/framework scaling.

## Rule

Update this document whenever the active phase, exit gate, dependency order, public capability or Globe promotion boundary changes.
