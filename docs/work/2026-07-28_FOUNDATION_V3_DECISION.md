# ARTEMIS — FOUNDATION v3 DECISION

## Статус

- Тип: foundation decision record.
- Дата решения: 2026-07-28.
- Статус: `PROPOSED / PENDING MERGE`.
- Parent: GitHub issue `#327`.
- Supersedes: `2026-07-26_CONCEPT_LOCK_V2.md`.
- Scope: mission, product identity, world model, role of evidence, role of map/time, first validation vertical and backlog boundary.
- Не является runtime/API/schema implementation specification.

После merge normative meaning принадлежит canonical owner documents. Этот record сохраняет rationale и migration boundary.

## 1. Причина решения

Concept Lock v2 исправил важные epistemic проблемы:

- отделил Claim от Source;
- отделил Relation от classification/Similarity;
- сохранил uncertainty;
- запретил AI быть Source;
- ввёл честное различие между current runtime и target.

Но одновременно он изменил идентичность ARTEMIS:

- evidence-first research workflow стал миссией;
- Research Brief стал главным outcome;
- Architecture Atlas стал определять единственного primary user;
- map/time были понижены до факультативных линз;
- исходная задача совместного наблюдения мира в пространстве и времени стала optional branch.

Это было не только сужение MVP. Product-validation scenario был ошибочно превращён в North Star.

## 2. Восстановленное ядро

ARTEMIS определяется как source-aware spatial-temporal world model.

Mission:

> помогать человеку понимать мир как взаимосвязанную систему сущностей, событий, состояний и процессов, наблюдаемую в пространстве и времени.

Evidence:

> обязательный trust layer, но не замена миссии.

## 3. Утверждаемые решения

### D1. Space/time are core

Пространство и время являются обязательными координатами knowledge and interaction model.

Неудача конкретного map UI ведёт к пересмотру UI/vertical/corpus, а не к превращению ARTEMIS в другой продукт.

### D2. Change objects are first-class

Core model включает:

- Entity;
- Event;
- State;
- Process;
- Trajectory;
- Region;
- Layer.

Static object + date не является достаточной моделью мира.

### D3. Evidence is a trust layer

Claim/EvidenceLink/Source/locator/uncertainty сохраняются как foundation.

Evidence chain нужна, чтобы пользователь мог доверять model assertions и различать evidence, inference and hypothesis.

### D4. Relation ladder is explicit

Различаются:

- co-presence;
- possible encounter;
- documented encounter;
- interaction;
- influence;
- causality.

Пространственно-временная близость не повышается до Relation автоматически.

### D5. Epistemic separation is retained and expanded

Отдельно представлены:

- factual assertion;
- observation/computed signal;
- interpretation;
- inference;
- hypothesis;
- counterfactual.

Origin, review, confidence, evidence state and uncertainty остаются независимыми.

### D6. Architecture Atlas becomes a thematic layer

Выполненная работа сохраняется. Architecture Atlas остаётся current public/technical baseline и потенциальным компонентом World Slices.

Он больше не определяет миссию всего ARTEMIS.

### D7. Research artifacts become supporting outcomes

Investigation, immutable Slice Revision, Saved View and Research Brief остаются допустимыми и полезными.

Они не являются обязательным первым moment of value и не задают всю ontology.

### D8. AI remains future and source-bound

Долгосрочно AI может анализировать world model, показывать inference trace и предлагать hypotheses/counterfactuals.

AI generation остаётся замороженной. AI не становится Source и не публикует canonical knowledge автоматически.

### D9. 3D/VR/dynamic Earth remain North Star surfaces

Они закрепляются как допустимые долгосрочные формы взаимодействия, но не current promises.

### D10. First validation vertical is Life in Context

Первый slice прослеживает жизнь исторической личности вместе с local/global context.

Initial candidate: Leonardo da Vinci, 1452–1519.

## 4. Что сохраняется из Concept v2

- human judgment;
- Claim/EvidenceLink and locator;
- independent epistemic dimensions;
- Relation as structured Claim;
- classification and Similarity separation;
- uncertainty as a legitimate result;
- public truth before promise;
- current runtime vs target distinction;
- immutable revisions/Brief as optional research model;
- independent gates for risky expansion.

## 5. Что superseded

- human research workflow as the only mission;
- evidence chain as the sole core value;
- map/time as removable validated lenses;
- Architecture Atlas comparison as project identity;
- Research Brief as primary reusable outcome for all ARTEMIS;
- `Question → Claims → Evidence → Conclusion` as the only valid core loop;
- branch model in which spatial-temporal depth is optional future expansion;
- Gate B–E migration order based on that identity.

## 6. Immediate implementation boundary

Until this decision is merged:

- #323–#325 remain held;
- #286–#289 and #308–#313 are not executed as active v3 work;
- PR #314 remains unmerged;
- no schema/runtime migration is performed;
- security/compatibility maintenance remains allowed;
- completed Gate A data is preserved.

After merge:

- old Concept v2 implementation issues may be closed `not planned` with links to #327;
- clean v3 child issues are created;
- PR #314 is closed without merge unless a later v3 decision explicitly reuses it;
- contracts and fixtures precede code.

## 7. First vertical boundary

Included:

- one Person trajectory;
- selected local Events and regional States;
- selected contemporaries and documented Relations;
- explicit co-presence;
- selected global simultaneous Events;
- at least one Process and changing Region;
- Claims/EvidenceLinks/locators/uncertainty;
- synchronized 2D map/timeline/layers;
- same-content controlled baseline.

Excluded:

- comprehensive history;
- generative AI;
- causal engine;
- counterfactual simulation;
- 3D/VR;
- universal domain expansion;
- public backend dependency unless proven necessary.

## 8. Alternatives rejected

### Keep Concept v2 as North Star and add spatial branch

Rejected: makes the original ARTEMIS identity contingent on validation of a secondary evidence-first product.

### Revert all Concept v2 work

Rejected: Claim/Evidence discipline, uncertainty, governance and Architecture Atlas fixtures remain valuable.

### Begin universal schema implementation immediately

Rejected: would make an irreversible ontology decision before contract fixtures and first World Slice expose real requirements.

### Start with 3D/VR or AI

Rejected: increases technical and epistemic risk before the core synchronized 2D value is demonstrated.

## 9. Acceptance

The decision is ready to merge only if:

- canonical owner docs agree;
- current capabilities remain honestly described;
- v2 history is preserved and marked superseded;
- world-model contract has test fixtures and uncertainty semantics;
- first vertical has measurable hypotheses;
- operational priorities/phases no longer authorize v2 migrations;
- no runtime/data capability is implied by docs.

## 10. Change control

Changing any D1–D10 requires a new foundation decision.
