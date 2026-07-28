# ARTEMIS — ENTITY MODEL

## Статус документа

- Тип: canonical foundation entity model.
- Версия: 3.0.
- Дата: 2026-07-28.
- Статус: proposed by Foundation v3.
- Роль: фиксирует типы knowledge, research, runtime и context entities.
- Пространственно-временная семантика: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`.
- Эпистемическая семантика: `EPISTEMIC_CONTRACT.md`.

## 1. Главный принцип

ARTEMIS моделирует мир через сущности, события, состояния и процессы, расположенные в пространстве и времени.

`Entity` отвечает на вопрос «кто или что». `Event`, `State`, `Process`, `Trajectory` и `Region` отвечают, как мир существует и меняется.

Claim/EvidenceLink обеспечивают проверяемость этой модели.

## 2. Уровни модели

### Knowledge

- `Entity`;
- `Place`;
- `Person`;
- `Object`;
- `Institution`;
- `Organism`;
- `Event`;
- `State`;
- `Process`;
- `Trajectory`;
- `Region`;
- `Layer`;
- `Relation`;
- `ClassificationAssertion`;
- `Claim`;
- `Source`;
- `EvidenceLink`;
- `Uncertainty`;
- `Media`.

### Research/product

- `WorldSlice`;
- `Investigation`;
- `SliceRevision`;
- `ResearchBrief`;
- `Collection`;
- future `GuidedExploration`;
- future `Story/Course`;
- future `AIInsight`.

### Runtime

- `User`;
- `Session`;
- `ResearchSlice` compatibility envelope;
- `Draft`;
- `ModerationItem`;
- `Upload`;
- `PublishBatch`;
- `ExportArtifact`.

### Context

- `SynchronizedView`;
- `SavedView`;
- `TimeState`;
- `CameraState`;
- `LayerState`;
- `SelectionState`;
- `ReconstructionMode`;
- `ExplainabilityContext`.

## 3. Base Entity

`Entity` — устойчивая идентифицируемая knowledge unit.

Минимальные свойства:

- stable ARTEMIS id;
- type;
- label/name;
- optional description;
- temporal and spatial compatibility;
- Claim references;
- uncertainty;
- external/source identities;
- relation capacity.

Entity может не иметь собственной geometry, если она адресуется через Place/Event/State и причина видима.

Entity card не является самостоятельной продуктовой миссией.

## 4. Entity subtypes

### Place

Идентифицируемое место. Геометрия и границы могут меняться и храниться через Region/State.

### Person

Человек, связанный с Places, Events, Institutions, Works, Relations и Trajectory.

Standalone biography без пространственно-временного контекста не реализует core ARTEMIS.

### Object

Материальный или культурный объект: building, artifact, infrastructure, work.

Object может иметь creation/use/destruction/reconstruction Events и изменяющиеся States.

### Institution

Организация, двор, школа, религиозный институт, государственная структура или другая коллективная entity.

### Organism

Таксон, population или individual living entity в зависимости от domain contract.

Ареал хранится как Region/State/Process, а не как статическое свойство вида.

## 5. Change objects

### Event

Ограниченное событие с temporal extent, spatial context и participants.

Event не обязан быть одной точкой; distributed event использует несколько extents/subevents.

### State

Состояние subject/Region в интервале и scope.

State используется для:

- political control;
- cultural/religious prevalence;
- object function;
- institutional status;
- ecological presence;
- terrain/coastline reconstruction.

### Process

Длительное изменение, объединяющее Events/States.

Process определяет scope, stages/indicators, uncertainty и competing interpretations.

### Trajectory

Упорядоченный путь Entity через presence/movement/inferred-gap segments.

Соединение известных точек прямой линией не доказывает маршрут.

### Region

Пространственная область с identity, temporal validity и geometry precision.

Примеры: political territory, cultural area, religion distribution, habitat, coastline, analytical region.

### Layer

Тематическая группировка для query/display.

Layer не является evidence или epistemic status.

## 6. Knowledge assertions

### Claim

Атомарное утверждение, которое можно проверить, поддержать, оспорить или оставить unresolved.

Claims применяются к identity, time, geometry, state, process, trajectory, classification и relation.

### Source

Bibliographic/provenance unit. Source не подтверждает Entity целиком.

### EvidenceLink

Связывает Claim и Source через locator, relation to claim, strength and review.

### Uncertainty

Самостоятельная структурированная запись о неизвестности, диапазоне, alternatives или corpus limitation.

### ClassificationAssertion

Claim-like assertion `Entity classified_as Category`.

Общая classification двух Entities не создаёт substantive Relation.

### Relation

Structured Claim:

`subject → predicate → object`.

Relation включает direction, temporal/spatial scope, qualifiers, epistemic dimensions and EvidenceLinks.

### Media

Image/map/model/document/asset с provenance and rights.

Media может быть evidence только через соответствующий Source/EvidenceLink/Claim context.

## 7. Relation ladder

Отдельные значения:

- computed `co_present`;
- inferred `possible_encounter`;
- `documented_encounter`;
- `interaction`;
- `influence`;
- separately governed `causal`.

Rules:

- proximity and overlap do not create Relation automatically;
- each stronger predicate requires its own Claim basis;
- `associated_with` does not substitute for unknown predicate;
- `same_movement` remains derived shared classification;
- Similarity remains computed output;
- AI-suggested Relation remains marked hypothesis pending review.

## 8. WorldSlice

`WorldSlice` — ограниченный source-aware фрагмент модели мира.

Он определяет:

- spatial/temporal bounds;
- included layers and object types;
- selection rationale;
- coverage limitations;
- source/review criteria;
- dataset/schema identity;
- version.

WorldSlice не утверждает полноту мира за своими границами.

## 9. Research entities

### Investigation

Развивающаяся работа с устойчивой identity.

### SliceRevision

Неизменяемая версия Investigation с question, selected world context, Claims, EvidenceLinks, conclusion/unresolved, uncertainty and SavedView.

### ResearchBrief

Детерминированная читаемая проекция SliceRevision.

### Collection / GuidedExploration

Организационные/учебные consumers world-model objects. Они не создают отдельную ontology.

Investigation/Brief полезны для глубокого исследования, но не являются обязательным первым outcome каждого просмотра ARTEMIS.

## 10. Runtime compatibility

Current:

- GeoJSON `Feature` is point-oriented public representation;
- `ResearchSlice v2` is mutable compatibility envelope;
- Stories/Courses are frozen runtime code;
- existing Relation/Source artifacts implement only part of target semantics.

Правила:

- compatibility object does not redefine conceptual model;
- `content_version` is not immutable historical revision;
- legacy schema migration cannot invent time, geometry, Claim or evidence;
- adapters must expose loss/unknowns.

## 11. Identity

Каждая canonical unit имеет stable ARTEMIS identity.

External/source ids remain separately traceable. Uncertain duplicates are not silently merged.

Identity revision does not erase historical versions or source identity.

## 12. Lifecycle

Knowledge candidate:

`candidate → technically_validated → reviewed/contested/rejected → published → revised/superseded → archived`

Technical validity не равна epistemic trust.

User/private research content не становится canonical knowledge автоматически.

## 13. Composition

Базовая цепочка world model:

`Entity + Event + State + Process + Trajectory + Region`

Trust chain:

`Claim → EvidenceLink → Source → Uncertainty`

Research chain:

`WorldSlice/View → Investigation? → SliceRevision? → ResearchBrief?`

Future AI/Story/Course/VR consume explicit world-model context; они не определяют его.

## 14. Failure modes

Модель нарушена, если:

- всё сводится к статическим object cards;
- Event/State/Process кодируются одной датой;
- современная geometry используется для всех эпох без маркировки;
- Region отображается точнее evidence;
- line between trajectory points выдается за documented route;
- co-presence превращается в encounter/influence;
- Source прикреплён как blanket proof;
- AI output становится Source;
- counterfactual меняет historical state;
- absence in dataset интерпретируется как historical absence;
- runtime compatibility object объявляется canonical target.

## 15. Change control

Новый entity/change type обязан определить:

- layer and identity;
- temporal and spatial semantics;
- Claim/Evidence requirements;
- uncertainty;
- relation behavior;
- WorldSlice coverage;
- public/private lifecycle;
- compatibility projection;
- fixtures and validation.

## 16. Итог

ARTEMIS растёт через совместимую модель мира, а не через накопление локальных таблиц и экранов.
