# ARTEMIS — PROJECT PHASES v6.0

## Статус

- Тип: canonical operational phases document.
- Дата: 2026-07-28.
- Активная фаза: **4.7 World Model Contract**.

Фазы определяют порядок исполнения. North Star принадлежит `ARTEMIS_CONCEPT.md`.

## Принцип перехода

Фаза закрывается только по exit evidence. Документ или schema сами по себе не подтверждают value, content quality или public capability.

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

Завершено и сохранено:

- Concept v2 decision/history;
- Claim/Evidence and Relation discipline;
- Gate A architecture validation modules;
- audits and migration planning.

Не выполняются:

- Claim/Evidence schema migration under #323;
- Investigation/revision/Brief migration under #324;
- public target E2E under #325;
- прежний UI/backend critical path.

Причина: architecture comparison vertical был ошибочно превращён в идентичность всего проекта.

## Фаза 4.6 — Foundation v3 [завершена]

### Цель

Вернуть spatial-temporal world model в ядро ARTEMIS до irreversible implementation.

### Track A — Foundation decision

- Concept v3;
- world-model contract;
- product thesis/scope/truth;
- entity/epistemic alignment;
- migration matrix;
- operational docs;
- old decision marked superseded.

### Track B — Backlog correction

- hold old issues until Foundation merge;
- close superseded v2 implementation issues afterward;
- preserve completed assets/history;
- create clean v3 child issues.

### Exit

- Foundation PR merged;
- current truth unchanged except direction/status;
- no contradictory active owner docs;
- world-model fixtures are defined;
- next work is contract/corpus, not schema migration.

## Фаза 4.7 — World Model Contract

Статус: **ACTIVE / ISSUE #330**.

Scope:

- temporal/spatial extent and precision;
- Entity/Event/State/Process/Trajectory/Region/Layer;
- uncertainty and alternative reconstruction;
- relation ladder;
- corpus coverage;
- compatibility fixtures.

Exit:

- versioned fixtures represent every required object kind;
- deterministic validator and negative semantic tests pass;
- two independent reviews find no unresolved critical contradiction;
- non-inventive legacy mapping is explicit;
- current truth continues to deny runtime implementation;
- uncertainty/relation follow-ups are explicitly routed before implementation.

Progress:

- #329 fixture package completed and merged in PR #336;
- #330 uncertainty semantics are active;
- #331 relation-ladder semantics remain gated on #330.

## Фаза 4.8 — Life in Context Dataset

Статус: **GATED**.

Scope:

- one frozen Leonardo World Slice;
- source/locator/uncertainty review;
- coverage statement;
- curation cost;
- no claim of comprehensive history.

Exit:

- content ready;
- no invented trajectory/geometry;
- relation ladder fixtures valid;
- same-content baseline can be built.

## Фаза 4.9 — Spatial-Temporal Explorer

Статус: **GATED**.

Scope:

- synchronized 2D map/timeline/layers;
- trajectory;
- Events/Regions/States/Processes;
- local/global context;
- evidence and uncertainty;
- responsive/accessibility/browser acceptance.

Exit:

- deterministic shared state;
- public/static pilot contour;
- capability truth updated only after deploy evidence.

## Фаза 5 — Contextual Learning Pilot

Статус: **GATED**.

Scope:

- same-content controlled baseline;
- 6–8 users;
- context/simultaneity/change measures;
- relation overclaim errors;
- source/uncertainty comprehension;
- cost;
- explicit decision.

Possible outcomes:

- `ITERATE`;
- `EXPAND ONE BRANCH`;
- `NARROW VERTICAL`;
- `STOP/RETHINK`.

## Independent future branches

Blocked until pilot decision:

- richer temporal Regions/States;
- 3D globe/dynamic Earth;
- guided learning;
- source-bound AI;
- broader World Slices;
- institutional work;
- VR/AR.

One decision opens one branch.

## Scaling/Business

Security/reliability maintenance remains allowed. Scaling, platform distribution and monetization require separate evidence and operational reasons.

## Rule

Update this document whenever active phase, exit gate or dependency order changes.
