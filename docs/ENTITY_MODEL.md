# ARTEMIS — ENTITY MODEL

## Статус документа

- Тип: foundation entity model document
- Статус: active, canonical registration confirmed in `PROJECT_STRUCTURE.md` and `DOCUMENTATION_SYSTEM.md`
- Роль: фиксирует базовую модель сущностей ARTEMIS и связи между ними
- Назначение: предотвратить хаотичное добавление новых типов данных, runtime-моделей и продуктовых сущностей без единого conceptual/data/product контракта
- Scope: knowledge entities, Claim/Evidence model, product research entities, runtime entities, context entities and Relation model

---

## 1. Главный принцип

ARTEMIS работает не с разрозненными карточками, а с сущностями, атомарными Claims, evidence chains и версионированными результатами исследования. Пространство и время являются привилегированными линзами этой модели.

Любая новая сущность должна отвечать минимум на вопросы:

1. Что это такое?
2. Где она существует: knowledge layer, product layer, runtime layer или AI/context layer?
3. Имеет ли она Claim, пространство, время, Source или связь с другими сущностями?
4. Может ли она входить в Investigation/Slice Revision?
5. Может ли она становиться частью Story или Course?
6. Какие независимые epistemic dimensions к ней применимы?
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
- `Claim`
- `ClassificationAssertion`
- `Relation`
- `Source`
- `EvidenceLink`
- `Media`

### 2.2 Product entities

Сущности, через которые пользователь работает с исследованием:

- `Investigation`
- `SliceRevision`
- `ResearchBrief`
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
- `ResearchSlice` (current runtime compatibility envelope)

### 2.4 Context entities

Сущности, которые не являются самостоятельным знанием, но задают контекст:

- `ViewState`
- `SavedView`
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
- claim/evidence context where relevant;
- relation capacity.

Правила:

- Entity не обязана всегда иметь точные координаты, но должна быть совместима с spatial-temporal model.
- Entity не должна смешивать factual fields и interpretation fields без маркировки.
- Entity может быть частью Investigation/Slice Revision.
- Claims about Entity могут быть связаны с Source через EvidenceLink.
- Entity может быть связана с Media и RelationClaim.

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
- Object не должен становиться главной продуктовой единицей вместо evidence-aware comparison and Investigation;
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
- Layer is not an epistemic dimension;
- Layer must not hide uncertainty or source status;
- Layer can be used in SavedView/classification context.

### 4.7 Claim

`Claim` — атомарное утверждение об Entity, Relation, classification или исследовательском выводе.

Rules:
- Claim has stable id within its owning layer;
- claim kind, origin, review state, confidence, evidence state and uncertainty are independent;
- Claim must be narrow enough for a reviewer to determine whether EvidenceLink supports it;
- user/AI Claim does not become canonical public knowledge without governance.

Primary contract:
- `docs/EPISTEMIC_CONTRACT.md`.

### 4.8 ClassificationAssertion

`ClassificationAssertion` links one Entity to one Movement, Layer, typology or other classification.

Rules:
- classification has its own Claim/Evidence semantics;
- two entities in one classification do not create a substantive pairwise Relation;
- `same_movement` is a derived compatibility projection from two ClassificationAssertions.

### 4.9 Relation

`Relation` is a structured Claim:

`subject → predicate → object`.

Relation examples in the current target:
- part-of;
- influenced-by;
- modelled-on;
- derived-from;
- adapted-from;
- reconstructed-from.

Rules:
- Relation must have a precise predicate and direction where meaningful;
- Relation inherits Claim/Evidence requirements;
- `associated-with` must not replace an unknown predicate;
- spatial/temporal proximity and shared classification are not substantive Relations by themselves;
- Relation does not imply causality unless a separately approved predicate and evidence policy allow it;
- AI-suggested Relation remains a draft hypothesis until review.

### 4.10 Source

`Source` — provenance unit for claims, fields or entities.

Source may contain evidence relevant to many Claims.

Rules:
- AI is not a source;
- Source quality must be representable;
- Source may conflict with another source;
- Source is not attached as blanket proof of an Entity;
- relevance to a Claim is expressed through EvidenceLink.

### 4.11 EvidenceLink

`EvidenceLink` connects one Claim to one Source with:

- locator;
- relation `supports/challenges/contextualizes`;
- direct/indirect/background strength;
- review state.

EvidenceLink is not a Relation between historical Entities. It belongs to provenance/evidence semantics.

### 4.12 Media

`Media` — image, map, drawing, diagram, document or other asset connected to entities/sources.

Rules:
- Media must have origin/provenance where possible;
- Media license/source should be known before public display;
- Media does not prove a claim by itself without interpretation/source context;
- user upload is runtime media until reviewed/promoted.

---

## 5. Product entity types

### 5.1 Investigation

`Investigation` — evolving owner-scoped research work with stable identity and ordered revisions.

Rules:
- Investigation may change;
- it references a latest SliceRevision;
- it is private by default;
- it is not canonical public knowledge.

### 5.2 SliceRevision

`SliceRevision` — immutable version of Investigation.

It preserves:
- question and scope;
- compared entities;
- Claims/findings;
- EvidenceLinks;
- conclusion or unresolved;
- uncertainty;
- dataset/schema identity;
- nested SavedView.

Rules:
- update creates a new revision;
- previous revision is not overwritten;
- share pins revision unless explicitly marked live;
- revision may be consumed by future Story/Course/AI, but those layers do not define it.

Primary document:
- `docs/RESEARCH_SLICE_CONTRACT.md`.

### 5.3 ResearchBrief

`ResearchBrief` — deterministic readable/exportable projection of one SliceRevision.

Rules:
- Brief does not own independent epistemic truth;
- it identifies revision and dataset context;
- it preserves citations/locators and material uncertainty;
- stale Brief must be regenerated from revision.

### 5.4 Story

`Story` — future sequence of revisions or revision-like states with narrative/analytical progression.

Rules:
- Story should be grounded in spatial-temporal context;
- Story should not become a detached article;
- Story may include interpretations, but must preserve epistemic distinctions;
- Story may be curated, private or owner-scoped depending on runtime contract.

### 5.5 Course

`Course` — future guided educational structure built from stories, revisions and explanations.

Rules:
- Course must remain connected to spatial-temporal research context;
- Course should not become generic LMS content detached from ARTEMIS core;
- Course explanations must preserve epistemic honesty;
- Course may use progress tracking, but progress tracking is not the core product value.

### 5.6 Collection

`Collection` — grouped set of entities, Investigations/revisions, stories or courses.

Rules:
- Collection organizes research objects;
- Collection does not replace Investigation/SliceRevision;
- Collection may be private, curated or shared depending on future contract;
- Collection must not imply epistemic validation by grouping alone.

### 5.7 Annotation

`Annotation` — human or AI-assisted note attached to Entity, Investigation/revision, Story step or Course context.

Rules:
- Annotation must have author/source context;
- Annotation must have epistemic type where relevant;
- Annotation is not canonical fact by default;
- AI annotation must be visibly marked.

### 5.8 AIInsight

`AIInsight` — AI-assisted summary, explanation, comparison, pattern or hypothesis.

Rules:
- AIInsight is AI output, not source;
- AIInsight must expose input context;
- AIInsight must expose claim kind, origin, review and evidence state where relevant;
- AIInsight may support user thinking but not directly publish canonical content.

---

## 6. Runtime entity types

### 6.1 User

`User` — authenticated actor using ARTEMIS.

May own:
- drafts;
- Investigations/current research slices;
- stories;
- courses;
- uploads;
- private annotations.

Rules:
- user-owned runtime data is not automatically public canonical knowledge;
- ownership and visibility must be explicit.

### 6.2 ResearchSlice

`ResearchSlice` is the current mutable runtime envelope defined by `RESEARCH_SLICE_SPEC.md`.

Rules:
- it is not the final product ontology;
- it may serve as latest working state during migration;
- `content_version` is not immutable revision identity;
- public descriptions must not claim absent Investigation/revision/Brief capabilities.

### 6.3 Draft

`Draft` — user-submitted candidate content before moderation/publish.

Rules:
- Draft is not canonical content;
- Draft may contain useful data, weak data or invalid data;
- Draft must pass moderation/governance before promotion;
- Draft lifecycle is separate from Investigation/research-work lifecycle.

### 6.4 ModerationItem

`ModerationItem` — unit of review for draft/content governance.

Rules:
- moderation evaluates both technical validity and epistemic/content validity;
- approval path must not bypass governance;
- rejection reason should be preserved where relevant.

### 6.5 Upload

`Upload` — runtime file/media item submitted by user.

Rules:
- Upload is runtime asset, not trusted media by default;
- accepted upload does not equal curated media;
- public display must respect validation, serving policy and provenance/licensing rules.

### 6.6 ExportArtifact

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
- ViewState alone is not SliceRevision;
- ViewState becomes meaningful when combined with entities, time, filters and context.

### 7.2 SavedView

`SavedView` composes ViewState, TimeRange, FilterState, LayerState and SelectionState.

Rules:
- SavedView is nested context, not knowledge;
- it may be absent or minimal if irrelevant to a question;
- it does not contain Claims, EvidenceLinks or conclusion;
- it must not be called a complete research result.

### 7.3 TimeRange

`TimeRange` stores temporal filter/state.

Rules:
- TimeRange may be point-like or range-like;
- BCE/negative years must be supported where relevant;
- TimeRange does not prove historical duration by itself.

### 7.4 FilterState

`FilterState` stores user selection constraints.

Rules:
- FilterState affects display/research context;
- FilterState must be restorable if included in SavedView.

### 7.5 LayerState

`LayerState` stores active/disabled layer visibility.

Rules:
- LayerState is UI/product context;
- LayerState must not be confused with data validity.

### 7.6 SelectionState

`SelectionState` stores selected entities/features.

Rules:
- selected entity must refer to known entity/feature id;
- selection is user context, not epistemic validation.

### 7.7 ExplainabilityContext

`ExplainabilityContext` is structured input for AI/explanation behavior.

May include:
- investigation/revision id;
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

A RelationClaim must define:

- Claim id and statement;
- subject Entity;
- object Entity;
- precise predicate;
- directionality;
- qualifiers and temporal scope where relevant;
- claim kind and origin;
- review state, confidence and uncertainty;
- EvidenceLinks with locators.

Current Architecture Atlas target categories:

| Category | Examples |
|---|---|
| structural | part-of, contains |
| reception/derivation | influenced-by, modelled-on, derived-from, adapted-from, inspired-by |
| reconstruction | reconstructed-from |

Separate models:

- `classified_as` belongs to ClassificationAssertion;
- `source supports claim` belongs to EvidenceLink;
- computed before/after, proximity and feature similarity belong to comparison output;
- causal Relation is outside current approved scope.

Rules:
- `associated-with` must not substitute for a missing predicate;
- `same_movement` must not count as substantive Relation;
- Relation may be factual, interpretive or hypothetical;
- influence/derivation requires reviewed claim-level evidence;
- AI-suggested Relation remains draft hypothesis until review.

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

ARTEMIS product layers compose in this order:

1. Entity/Feature provides research subject.
2. Claim states something specific.
3. EvidenceLink connects Claim to Source.
4. Comparison produces human findings.
5. Investigation organizes evolving work.
6. SliceRevision freezes one result and SavedView.
7. ResearchBrief transfers the revision.
8. Future Story/Course/AI may consume explicit revision context after independent gates.

Forbidden inversion:
- Course must not define core data model.
- Story must not replace Investigation/revision model.
- AI must not create canonical entities without governance.
- Object card browsing must not replace evidence-aware comparison.
- SavedView must not be presented as product-complete SliceRevision.
- ResearchBrief must not become a stale independent source of truth.

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

### 12.3 Entity vs Claim

Entity is a research subject.

Claim is an assertion about Entity/context.

Source supports/challenges/contextualizes Claim through EvidenceLink.

### 12.4 Entity vs Investigation/Revision

Entity is researched.

Investigation organizes work; SliceRevision freezes one version of Claims, Evidence and context.

### 12.5 Revision vs Brief

SliceRevision is source of truth for saved research state.

ResearchBrief is its readable projection.

### 12.6 Entity vs AIInsight

Entity is knowledge object.

AIInsight is model output about context/entities.

AIInsight does not become Entity or Source by default.

---

## 13. Failure modes

The entity model is broken if:

- object, Story, Course, Investigation, revision and Brief duplicate each other's core data structures;
- AI output becomes source;
- user draft becomes public entity without governance;
- relation implies causality without evidence;
- feature id, source id and canonical id are mixed without traceability;
- courses become generic lessons detached from spatial-temporal entities;
- Stories become articles detached from revision evidence context;
- ResearchSlice becomes only a viewport bookmark;
- mutable ResearchSlice is described as immutable revision history;
- Source is attached as blanket proof without Claim/EvidenceLink;
- shared classification or Similarity counts as substantive Relation;
- ResearchBrief diverges from its revision;
- Layer is used to hide or collapse epistemic dimensions;
- Media is treated as proof without provenance.

---

## 14. Relationship to other foundation docs

- `ARTEMIS_CONCEPT.md` defines why ARTEMIS needs evidence-first human research with privileged spatial-temporal lenses.
- `ARTEMIS_PRODUCT_SCOPE.md` defines current product boundaries.
- `RESEARCH_SLICE_CONTRACT.md` defines Investigation/SliceRevision/SavedView/ResearchBrief semantics.
- `EPISTEMIC_CONTRACT.md` defines Claim/EvidenceLink and independent epistemic dimensions.
- `DATA_CONTRACT.md` defines current public data artifact shape.
- `CONTENT_GOVERNANCE.md` will define how candidates become trusted content.
- `AI_POLICY.md` will define AI behavior boundaries.

---

## 15. Change-control rule

Any new Entity, Claim form or Relation predicate must define:

- layer: knowledge/product/runtime/context;
- identity model;
- source/provenance requirements;
- epistemic-dimension requirements;
- relation to Investigation/SliceRevision;
- relation to Story/Course/AI if any;
- public/private visibility;
- impact on `DATA_CONTRACT.md` if public data changes;
- impact on `RESEARCH_SLICE_CONTRACT.md` if research-work context changes;
- impact on `CONTENT_GOVERNANCE.md` after creation if moderation/content trust changes;
- tests or release checks if executable behavior changes.

New types must not be added only because one feature needs a local shape. If the type has product or knowledge meaning, it must be added to this model first.

---

## 16. Итоговое правило

ARTEMIS should grow by extending a coherent entity model, not by accumulating unrelated objects, tables and UI states.

The stable conceptual chain is:

`Entity → Claim → EvidenceLink → Investigation → SliceRevision → ResearchBrief`

Future Story, Course and AI are optional consumers after independent evidence gates. This chain protects ARTEMIS from becoming a generic map, generic LMS, social feed, wiki or AI chat.
