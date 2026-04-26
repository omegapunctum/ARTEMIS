# ARTEMIS — ENTITY MODEL

## Статус документа

- Тип: foundation entity model document
- Статус: active, pending canonical registration in `PROJECT_STRUCTURE.md` and `DOCUMENTATION_SYSTEM.md`
- Роль: фиксирует базовую модель сущностей ARTEMIS и связи между ними
- Назначение: предотвратить хаотичное добавление новых типов данных, runtime-моделей и продуктовых сущностей без единого conceptual/data/product контракта
- Scope: knowledge entities, product entities, runtime entities, source/provenance entities, AI-context entities, relation model

---

## 1. Главный принцип

ARTEMIS работает не с разрозненными карточками, а с пространственно-временными сущностями, связями и исследовательскими состояниями.

Любая новая сущность должна отвечать минимум на вопросы:

1. Что это такое?
2. Где она существует: knowledge layer, product layer, runtime layer или AI/context layer?
3. Имеет ли она пространство, время, источник или связь с другими сущностями?
4. Может ли она входить в Research Slice?
5. Может ли она становиться частью Story или Course?
6. Какой у неё epistemic status?
7. Может ли она быть canonical public content или только private/runtime state?

---

## 2. Слои сущностей

В ARTEMIS различаются четыре уровня сущностей.

### 2.1 Knowledge entities

Сущности, описывающие внешний мир и историко-пространственные данные:

- `Entity`
- `Place`
- `Object`
- `Event`
- `Process`
- `Person`
- `Layer`
- `Relation`
- `Source`
- `Media`

### 2.2 Product entities

Сущности, через которые пользователь работает с исследованием:

- `ResearchSlice`
- `Story`
- `Course`
- `Collection`
- `Annotation`
- `AIInsight`

### 2.3 Runtime entities

Сущности backend/frontend исполнения:

- `User`
- `Session`
- `Draft`
- `ModerationItem`
- `Upload`
- `PublishBatch`
- `ExportArtifact`

### 2.4 Context entities

Сущности, которые не являются самостоятельным знанием, но задают контекст:

- `ViewState`
- `TimeRange`
- `FilterState`
- `LayerState`
- `SelectionState`
- `ExplainabilityContext`

---

## 3. Base entity

`Entity` — базовая knowledge-сущность ARTEMIS.

Entity может представлять:
- место;
- объект;
- событие;
- процесс;
- персону;
- маршрут;
- институцию;
- слой;
- другой spatial-temporal knowledge item.

Минимальные свойства Entity:

- stable id;
- type;
- name/title;
- optional description;
- temporal attribution where relevant;
- spatial attribution where relevant;
- source/provenance where available;
- epistemic status;
- relation capacity.

Правила:

- Entity не обязана всегда иметь точные координаты, но должна быть совместима с spatial-temporal model.
- Entity не должна смешивать factual fields и interpretation fields без маркировки.
- Entity может быть частью Research Slice.
- Entity может быть связана с Source, Media и Relation.

---

## 4. Knowledge entity types

### 4.1 Place

`Place` — пространственная сущность.

Примеры:
- город;
- регион;
- археологическая зона;
- архитектурный ансамбль;
- географическая область.

Правила:
- Place должен иметь spatial reference;
- confidence coordinates must be explicit if location is approximate;
- Place может содержать вложенные entities or be part of larger Place.

### 4.2 Object

`Object` — конкретный объект, который может быть отображён или исследован.

Примеры:
- здание;
- памятник;
- артефакт;
- инфраструктурный объект;
- культурный объект.

Правила:
- Object может иметь точку, область или approximate location;
- Object не должен становиться главной продуктовой единицей вместо Research Slice;
- Object является entry point для исследования.

### 4.3 Event

`Event` — событие, локализованное во времени и, при возможности, в пространстве.

Примеры:
- битва;
- основание города;
- строительство;
- политическое событие;
- открытие маршрута.

Правила:
- Event должен иметь temporal attribution;
- spatial attribution может быть точным, approximate или disputed;
- Event может быть связан с Place, Person, Object, Process.

### 4.4 Process

`Process` — длительное изменение или историческая динамика.

Примеры:
- урбанизация;
- миграция;
- распространение стиля;
- экономическая трансформация;
- культурное влияние.

Правила:
- Process часто имеет time range rather than point date;
- Process may involve multiple Places, Events and Entities;
- Process should not be reduced to one map marker unless explicitly simplified.

### 4.5 Person

`Person` — историческая или современная персона, если она связана с spatial-temporal knowledge context.

Правила:
- Person must be connected to events, places, works, institutions or processes;
- standalone biography without spatial-temporal role is not core ARTEMIS content;
- Person may be included in relations and stories/courses.

### 4.6 Layer

`Layer` — тематический или категориальный слой отображения и анализа.

Примеры:
- architecture;
- events;
- routes;
- natural systems;
- political structures;
- cultural heritage.

Правила:
- Layer groups entities by analytical/display purpose;
- Layer is not the same as epistemic status;
- Layer must not hide uncertainty or source status;
- Layer can be used in Research Slice context.

### 4.7 Relation

`Relation` — связь между entities.

Relation examples:
- located-in;
- part-of;
- near;
- before/after;
- influenced-by;
- associated-with;
- authored-by;
- caused-by candidate;
- source-supports;
- depicts.

Rules:
- Relation must have type;
- Relation should have direction if meaningful;
- Relation must have epistemic status;
- Relation does not imply causality unless explicitly typed and supported;
- AI-suggested relation is hypothesis until reviewed.

### 4.8 Source

`Source` — provenance unit for claims, fields or entities.

Source may support:
- entity existence;
- date;
- coordinates;
- relation;
- interpretation;
- media rights;
- confidence decision.

Rules:
- AI is not a source;
- Source quality must be representable;
- Source may conflict with another source;
- Source can support different claims with different confidence.

### 4.9 Media

`Media` — image, map, drawing, diagram, document or other asset connected to entities/sources.

Rules:
- Media must have origin/provenance where possible;
- Media license/source should be known before public display;
- Media does not prove a claim by itself without interpretation/source context;
- user upload is runtime media until reviewed/promoted.

---

## 5. Product entity types

### 5.1 ResearchSlice

`ResearchSlice` — главная единица ценности ARTEMIS v1.0.

It preserves:
- spatial context;
- temporal context;
- layer/filter state;
- selected entities;
- human annotations;
- AI/explainability context.

Rules:
- ResearchSlice references entities but does not redefine them;
- ResearchSlice is private by default;
- ResearchSlice may become building block for Story/Course;
- ResearchSlice is not canonical public data source.

Primary document:
- `docs/RESEARCH_SLICE_CONTRACT.md`

Runtime/API document:
- `docs/RESEARCH_SLICE_SPEC.md`

### 5.2 Story

`Story` — последовательность slices or slice-like states with narrative/analytical progression.

Rules:
- Story should be grounded in spatial-temporal context;
- Story should not become a detached article;
- Story may include interpretations, but must preserve epistemic distinctions;
- Story may be curated, private or owner-scoped depending on runtime contract.

### 5.3 Course

`Course` — guided educational structure built from stories, slices and explanations.

Rules:
- Course must remain connected to spatial-temporal research context;
- Course should not become generic LMS content detached from ARTEMIS core;
- Course explanations must preserve epistemic honesty;
- Course may use progress tracking, but progress tracking is not the core product value.

### 5.4 Collection

`Collection` — grouped set of entities, slices, stories or courses.

Rules:
- Collection organizes research objects;
- Collection does not replace ResearchSlice;
- Collection may be private, curated or shared depending on future contract;
- Collection must not imply epistemic validation by grouping alone.

### 5.5 Annotation

`Annotation` — human or AI-assisted note attached to entity, slice, story step or course context.

Rules:
- Annotation must have author/source context;
- Annotation must have epistemic type where relevant;
- Annotation is not canonical fact by default;
- AI annotation must be visibly marked.

### 5.6 AIInsight

`AIInsight` — AI-assisted summary, explanation, comparison, pattern or hypothesis.

Rules:
- AIInsight is AI output, not source;
- AIInsight must expose input context;
- AIInsight must have epistemic status;
- AIInsight may support user thinking but not directly publish canonical content.

---

## 6. Runtime entity types

### 6.1 User

`User` — authenticated actor using ARTEMIS.

May own:
- drafts;
- research slices;
- stories;
- courses;
- uploads;
- private annotations.

Rules:
- user-owned runtime data is not automatically public canonical knowledge;
- ownership and visibility must be explicit.

### 6.2 Draft

`Draft` — user-submitted candidate content before moderation/publish.

Rules:
- Draft is not canonical content;
- Draft may contain useful data, weak data or invalid data;
- Draft must pass moderation/governance before promotion;
- Draft lifecycle is separate from ResearchSlice lifecycle.

### 6.3 ModerationItem

`ModerationItem` — unit of review for draft/content governance.

Rules:
- moderation evaluates both technical validity and epistemic/content validity;
- approval path must not bypass governance;
- rejection reason should be preserved where relevant.

### 6.4 Upload

`Upload` — runtime file/media item submitted by user.

Rules:
- Upload is runtime asset, not trusted media by default;
- accepted upload does not equal curated media;
- public display must respect validation, serving policy and provenance/licensing rules.

### 6.5 ExportArtifact

`ExportArtifact` — checked-in output of ETL/export pipeline.

Examples:
- `data/features.geojson`;
- `data/features.json`;
- `data/export_meta.json`;
- `data/rejected.json`.

Rules:
- `data/features.geojson` is canonical public map source;
- diagnostic artifacts are not separate source-of-truth unless release gate defines them as such.

---

## 7. Context entity types

### 7.1 ViewState

`ViewState` stores map viewport and selected display state.

Rules:
- ViewState alone is not ResearchSlice;
- ViewState becomes meaningful when combined with entities, time, filters and context.

### 7.2 TimeRange

`TimeRange` stores temporal filter/state.

Rules:
- TimeRange may be point-like or range-like;
- BCE/negative years must be supported where relevant;
- TimeRange does not prove historical duration by itself.

### 7.3 FilterState

`FilterState` stores user selection constraints.

Rules:
- FilterState affects display/research context;
- FilterState must be restorable if included in slice.

### 7.4 LayerState

`LayerState` stores active/disabled layer visibility.

Rules:
- LayerState is UI/product context;
- LayerState must not be confused with data validity.

### 7.5 SelectionState

`SelectionState` stores selected entities/features.

Rules:
- selected entity must refer to known entity/feature id;
- selection is user context, not epistemic validation.

### 7.6 ExplainabilityContext

`ExplainabilityContext` is structured input for AI/explanation behavior.

May include:
- slice id;
- selected entities;
- layer/time/view context;
- source/provenance summaries;
- annotations;
- allowed epistemic output types.

Rules:
- AI must use context without treating it as source beyond its provenance;
- ExplainabilityContext is not canonical knowledge by itself.

---

## 8. Relation model

A relation must define:

- source entity;
- target entity;
- relation type;
- directionality where relevant;
- temporal validity where relevant;
- spatial validity where relevant;
- source/provenance where available;
- epistemic status;
- confidence where relevant.

Minimum relation categories:

| Category | Meaning |
|---|---|
| spatial | located-in, near, part-of-place |
| temporal | before, after, during, contemporary-with |
| structural | part-of, contains, belongs-to |
| authorship | created-by, attributed-to |
| participation | participated-in, involved-in |
| influence | influenced-by, derived-from |
| association | associated-with, related-to |
| provenance | source-supports, source-claims |
| hypothesis | may-relate-to, possible-influence |

Rules:
- `associated-with` must not be used as a lazy substitute for precise relation type if better type exists;
- `influenced-by` must not be used as causal proof unless source/interpretation supports it;
- hypothesis relation must be visually and epistemically marked;
- AI-suggested relation remains hypothesis until reviewed.

---

## 9. Entity identity rules

Entities must have stable identity.

Rules:
- public features require stable ids;
- runtime private entities require owner-scoped ids;
- external/source ids must be traceable separately from ARTEMIS ids;
- normalized/canonical ids must not erase source identity;
- duplicate entities should be resolved through governance, not silently merged if uncertain.

Identity fields may include:
- internal id;
- canonical publish id;
- source id;
- Airtable record id;
- external id;
- origin key;
- normalized id.

`DATA_CONTRACT.md` owns current checked-in field semantics for public artifacts.

---

## 10. Entity lifecycle

### 10.1 Candidate

Entity candidate may originate from:
- curated source;
- Airtable row;
- user draft;
- import script;
- manual editorial work;
- AI-suggested candidate pending review.

### 10.2 Validated

Validated entity has passed technical validation.

Technical validation does not equal final epistemic trust.

### 10.3 Curated

Curated entity has been accepted by editorial/content governance.

### 10.4 Published

Published entity appears in public canonical data artifact.

For current map baseline:
- published public map entity appears through `data/features.geojson`.

### 10.5 Revised

Entity may be corrected or updated as sources improve.

### 10.6 Rejected

Rejected entity must remain traceable if it entered validation/moderation pipeline.

### 10.7 Archived

Archived entity/content is historical or deprecated and not active canonical content.

---

## 11. Product-layer composition

ARTEMIS product layers must compose entities in this order:

1. Entity/Feature provides factual entry point.
2. ResearchSlice combines entities with spatial, temporal, layer and human context.
3. Story sequences slices or slice-like states.
4. Course structures stories/slices into guided learning.
5. AI explains, compares or hypothesizes over explicitly provided context.

Forbidden inversion:
- Course must not define core data model.
- Story must not replace slice model.
- AI must not create canonical entities without governance.
- Object card must not become the primary value unit.

---

## 12. Boundaries

### 12.1 Entity vs Feature

`Feature` is the GeoJSON/public-map representation of an entity-like record.

`Entity` is the conceptual/knowledge unit.

Not every future Entity must be rendered as one GeoJSON Point Feature, but current public map baseline is point-feature oriented.

### 12.2 Entity vs Draft

Draft is candidate/runtime submission.

Entity is accepted or candidate knowledge unit depending on lifecycle.

Draft does not become Entity in public canonical sense until governance/publish flow accepts it.

### 12.3 Entity vs Slice

Entity is researched.

Slice is the saved research context around selected entities and states.

### 12.4 Entity vs AIInsight

Entity is knowledge object.

AIInsight is model output about context/entities.

AIInsight does not become Entity or Source by default.

---

## 13. Failure modes

The entity model is broken if:

- object, story, course and slice duplicate each other's core data structures;
- AI output becomes source;
- user draft becomes public entity without governance;
- relation implies causality without evidence;
- feature id, source id and canonical id are mixed without traceability;
- courses become generic lessons detached from spatial-temporal entities;
- stories become articles detached from slices;
- ResearchSlice becomes only a viewport bookmark;
- Layer is used to hide epistemic status;
- Media is treated as proof without provenance.

---

## 14. Relationship to other foundation docs

- `ARTEMIS_CONCEPT.md` defines why ARTEMIS needs structured spatial-temporal knowledge.
- `ARTEMIS_PRODUCT_SCOPE.md` defines v1.0 product boundaries and Research Slice centrality.
- `RESEARCH_SLICE_CONTRACT.md` defines slice semantics.
- `EPISTEMIC_CONTRACT.md` defines epistemic status and knowledge-type separation.
- `DATA_CONTRACT.md` defines current public data artifact shape.
- `CONTENT_GOVERNANCE.md` will define how candidates become trusted content.
- `AI_POLICY.md` will define AI behavior boundaries.

---

## 15. Change-control rule

Any new entity type or relation type must define:

- layer: knowledge/product/runtime/context;
- identity model;
- source/provenance requirements;
- epistemic status requirements;
- relation to ResearchSlice;
- relation to Story/Course/AI if any;
- public/private visibility;
- impact on `DATA_CONTRACT.md` if public data changes;
- impact on `RESEARCH_SLICE_CONTRACT.md` if slice context changes;
- impact on `CONTENT_GOVERNANCE.md` after creation if moderation/content trust changes;
- tests or release checks if executable behavior changes.

New types must not be added only because one feature needs a local shape. If the type has product or knowledge meaning, it must be added to this model first.

---

## 16. Итоговое правило

ARTEMIS should grow by extending a coherent entity model, not by accumulating unrelated objects, tables and UI states.

The stable conceptual chain is:

`Entity → Relation → ResearchSlice → Story → Course → AIInsight`

This chain protects ARTEMIS from becoming a generic map, generic LMS, social feed, wiki or AI chat.
