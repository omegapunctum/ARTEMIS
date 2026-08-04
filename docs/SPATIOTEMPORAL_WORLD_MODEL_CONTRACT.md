# ARTEMIS — SPATIAL-TEMPORAL WORLD MODEL CONTRACT

## Статус

- Тип: canonical foundation model contract.
- Версия: 1.0.
- Дата: 2026-07-28.
- Статус: active; accepted in PR `#328`.
- Владеет: пространственно-временной семантикой knowledge model.
- Не владеет: текущими JSON/API schemas; их определяют runtime/data contracts.

## 1. Назначение

Этот контракт определяет минимальную семантику, необходимую для того, чтобы разные тематические слои ARTEMIS составляли одну модель мира, а не набор несвязанных datasets.

Он отвечает на вопросы:

- что существовало;
- где и когда;
- в каком состоянии;
- как изменялось или перемещалось;
- какие отношения утверждаются;
- на каком основании;
- что неизвестно;
- какой corpus вообще представлен.

## 2. Главные инварианты

1. Пространство и время моделируются совместно.
2. Static entity не заменяет Event/State/Process.
3. Геометрия имеет temporal validity.
4. Время может быть точным, интервальным, приблизительным, открытым или спорным.
5. Co-presence вычисляется из модели и не создаёт Relation автоматически.
6. Любая содержательная Relation является Claim.
7. Source/EvidenceLink относятся к конкретным Claims.
8. Неопределённость не прячется в свободном тексте.
9. Corpus coverage отделяется от historical absence.
10. Current reconstruction, alternative reconstruction и counterfactual branch не смешиваются.

## 3. Общий envelope

Каждый knowledge object должен иметь:

```text
id
type
label
temporal_extent?
spatial_extent?
claim_refs[]
uncertainty_refs[]
source/provenance refs where applicable
layer_refs[]
version/projection metadata
```

Отсутствие `spatial_extent` допустимо, если объект имеет relation к пространственно адресуемому контексту и причина отсутствия видима.

Отсутствие `temporal_extent` допустимо только для atemporal classification/concept objects или явно неизвестного времени.

## 4. Temporal model

### 4.1 Temporal extent

Поддерживаются:

- instant;
- closed interval;
- open-start interval;
- open-end interval;
- approximate instant/interval;
- disputed alternatives;
- recurring/periodic pattern, если предметная область требует.

Минимальная conceptual shape:

```text
TemporalExtent
├── start?
├── end?
├── precision
├── calendar
├── certainty
├── alternatives[]?
└── basis_claim_refs[]
```

### 4.2 Precision

Precision хранится отдельно от значения:

- exact instant;
- day;
- month;
- year;
- decade;
- century;
- range;
- unknown.

UI не должен отображать `1452` как точный день или плавно интерполировать событие внутри года без основания.

### 4.3 Valid time and record time

Различаются:

- `valid_time` — когда утверждаемое состояние существовало в мире;
- `record_time` — когда запись была создана, пересмотрена или опубликована.

Версия данных не является историческим временем.

## 5. Spatial model

### 5.1 Spatial extent

Поддерживаются:

- point;
- path/line;
- polygon/multipolygon;
- volume/3D extent в будущих schemas;
- fuzzy/uncertain area;
- named Place without resolved geometry;
- alternative geometries.

Минимальная conceptual shape:

```text
SpatialExtent
├── geometry_or_place_ref
├── coordinate_reference
├── precision
├── validity_interval?
├── alternatives[]?
└── basis_claim_refs[]
```

### 5.2 Temporal geometry

Region, route, coastline, habitat, political boundary или built object могут менять геометрию во времени.

Запрещено:

- прикреплять одну современную геометрию ко всем периодам без маркировки;
- отображать спорную границу как точную;
- интерполировать изменение границы как исторический факт без модели/evidence.

## 6. Core knowledge objects

### 6.1 Entity

Устойчивая идентифицируемая единица: Person, Place, Object, Institution, Organism, Concept/Tradition и другие подтипы.

Entity отвечает на `кто/что`, но не заменяет изменение.

### 6.2 Event

Ограниченное событие с temporal extent, участниками и spatial context.

Event может быть:

- point-like;
- distributed across several places;
- uncertain/disputed;
- composed of subevents.

### 6.3 State

Утверждение о состоянии subject или Region в интервале:

`subject has state/value during temporal extent and spatial scope`.

Примеры:

- политический контроль региона;
- культурный/религиозный контекст;
- функция здания;
- habitat presence;
- статус института;
- состояние рельефа или береговой линии.

State не равен classification без temporal validity.

### 6.4 Process

Длительное изменение, которое связывает Events/States и может иметь неодинаковую интенсивность в пространстве и времени.

Примеры:

- migration;
- diffusion;
- urbanization;
- religious spread;
- ecological range shift;
- erosion/uplift;
- institutional change.

Process может иметь stages, indicators and competing interpretations. Он не сводится к одной стрелке на карте.

### 6.5 Trajectory

Упорядоченная во времени последовательность presence/transition segments одной Entity.

```text
Trajectory
├── subject_ref
├── segments[]
│   ├── temporal_extent
│   ├── spatial_extent/place_ref
│   ├── segment_kind: presence | movement | inferred_gap
│   ├── basis_claim_refs[]
│   └── uncertainty_refs[]
└── coverage
```

Линия между двумя документированными точками не становится подтверждённым маршрутом автоматически.

### 6.6 Region

Пространственная область с identity and temporal geometry.

Region может представлять:

- political territory;
- cultural/religious distribution;
- ecological range;
- language area;
- terrain/coastline reconstruction;
- analytical area.

Region должен различать:

- observed/documented boundary;
- estimated boundary;
- analytical aggregation;
- alternative reconstruction.

### 6.7 Layer

Тематическая перспектива и display/query grouping.

Layer:

- не является evidence;
- не определяет истинность;
- может иметь собственные coverage and uncertainty rules;
- не должна скрывать cross-layer Relations.

## 7. Relations and proximity semantics

### 7.1 Derived proximity

Система может вычислить:

- temporal overlap;
- spatial overlap/proximity;
- co-presence;
- before/after;
- route intersection;
- similarity.

Эти outputs являются observations/computed signals, а не историческими Relations.

### 7.2 Relation ladder

| Level | Meaning | Minimum basis |
|---|---|---|
| `co_present` | пересечение пространственно-временных extents | model computation + extent uncertainty |
| `possible_encounter` | встреча была возможна | explicit inference and assumptions |
| `documented_encounter` | встреча документирована | supporting EvidenceLink + locator |
| `interaction` | документирован обмен/действие | specific RelationClaim + evidence |
| `influence` | утверждается воздействие на решение/процесс | mechanism/scope + evidence |
| `causal` | утверждается причинная зависимость | separately approved causal policy |

Система не повышает уровень автоматически.

### 7.3 Direction and scope

Relation определяет:

- subject;
- predicate;
- object;
- directionality;
- temporal validity;
- spatial scope where relevant;
- qualifiers/mechanism;
- Claim epistemics;
- EvidenceLinks.

## 8. Claim binding

Claims требуются для material assertions, включая:

- identity;
- date/time;
- location/geometry;
- participation;
- state value;
- process interpretation;
- trajectory segment;
- Region boundary;
- relation;
- causal or counterfactual statement.

Одно поле может быть projection нескольких Claims. Runtime schema может денормализовать, но не должна терять возможность восстановить provenance/uncertainty.

## 9. Uncertainty model

Uncertainty имеет:

```text
id
subject_or_claim_ref
dimension
description
effect
range_or_alternatives?
basis
review_state
```

Dimensions:

- temporal value/precision;
- spatial value/precision;
- identity;
- attribution;
- geometry/reconstruction;
- state;
- process;
- trajectory gap;
- relation;
- translation/terminology;
- source conflict;
- corpus coverage;
- inference/model assumption.

UI обязана показывать uncertainty рядом с затронутым элементом, а не только в глобальной сноске.

## 10. Corpus coverage

Каждый World Slice декларирует:

- spatial bounds;
- temporal bounds;
- included layers;
- selection rationale;
- known exclusions;
- density/coverage limitations;
- source and review criteria;
- last reviewed version.

Отсутствие события или сущности в slice не означает, что их не существовало.

## 11. Reconstruction modes

Поддерживаются отдельные modes:

- `historical_assertion`;
- `scholarly_reconstruction`;
- `alternative_reconstruction`;
- `analytical_model`;
- `hypothesis`;
- `counterfactual`.

Mode должен быть видим. Counterfactual branch не изменяет canonical historical state.

## 12. View and query state

Synchronized view содержит:

- map/camera extent;
- time or time range;
- active layers;
- selected objects;
- comparison/reference scope;
- reconstruction mode;
- uncertainty display settings;
- dataset/slice identity.

Изменение time state обновляет все temporal objects через один shared state.

## 13. Compatibility with current runtime

Current GeoJSON point features and `year` fields — compatibility projection, не target model.

До schema decision разрешены adapters, если:

- target distinctions существуют в fixtures;
- no evidence or precision is invented;
- legacy limitations are visible;
- adapter does not become a second canonical ontology.

Compatibility projection must preserve missing target semantics as missing. It must not invent Claims, EvidenceLinks, locators, temporal precision, spatial precision or geometry merely because a legacy field exists.

An executable contract fixture may be explicitly synthetic when its purpose is to test semantics rather than curate history. A synthetic fixture must be visibly marked, source-bound to immutable fixture documents, excluded from historical capability claims and kept separate from the real World Slice corpus.

## 14. Validation fixtures

Минимальный contract test set:

1. exact Event at one Place;
2. approximate Event with alternative date;
3. changing political/cultural Region;
4. Person trajectory with documented and inferred-gap segments;
5. long Process spanning several Regions;
6. co-presence without Relation;
7. documented encounter;
8. influence Claim with challenge;
9. disputed geometry/reconstruction;
10. explicit corpus exclusion.

Fixture validation must include negative cases for semantic collapse, orphan references, unsupported precision, derived proximity stored as Relation, invented compatibility evidence and corpus absence represented as historical absence.

Passing fixtures proves contract representability only. It does not prove database/API/runtime implementation, historical corpus readiness or user value.

## 15. Change control

Изменение core object, temporal/spatial precision, relation ladder, uncertainty or reconstruction mode требует:

- update этого контракта;
- update `ENTITY_MODEL.md` / `EPISTEMIC_CONTRACT.md`;
- migration compatibility statement;
- fixtures;
- UI/query impact;
- current-truth statement;
- executable validation before capability claim.

## 16. Итог

ARTEMIS world model считается корректным только если пользователь может отличить:

- что утверждается;
- где и когда это относится к миру;
- как оно меняется;
- из чего это известно;
- что вычислено системой;
- что выведено или предположено;
- что остаётся неизвестным;
- какой части мира вообще касается dataset.
