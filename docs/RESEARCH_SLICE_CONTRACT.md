# ARTEMIS — RESEARCH SLICE CONTRACT

## Статус документа

- Тип: foundation product/data/UI/AI contract document
- Статус: active, pending canonical registration in `PROJECT_STRUCTURE.md` and `DOCUMENTATION_SYSTEM.md`
- Роль: фиксирует Research Slice как главную единицу ценности ARTEMIS v1.0
- Назначение: определить смысл, состав, границы, lifecycle и downstream-роль research slice для map workspace, stories, courses и AI assistance
- Scope: product semantics, data semantics, UI semantics, AI-context semantics, lifecycle, v1.0 baseline, out-of-scope boundaries

---

## 1. Главная формула

Research Slice — это не просто сохранённый вид карты.

Research Slice — это **минимальная сохраняемая единица исследовательского контекста ARTEMIS**.

Он фиксирует, что пользователь исследовал:

- где;
- когда;
- какие слои были активны;
- какие сущности были выбраны;
- какие фильтры и состояния карты формировали контекст;
- какие заметки, интерпретации или гипотезы были добавлены;
- какой объяснимый контекст может быть передан stories, courses и AI.

---

## 2. Почему Research Slice является главной единицей ценности

ARTEMIS не должен строиться вокруг отдельного объекта.

Одиночный объект:
- полезен как точка входа;
- важен для карты и detail panel;
- но слишком мал, чтобы быть устойчивой продуктовой единицей.

ARTEMIS не должен строиться вокруг story как первичной единицы.

Story:
- важна как narrative layer;
- но строится поверх уже выбранных исследовательских состояний;
- не должна заменять базовый research workflow.

ARTEMIS не должен строиться вокруг course как первичной единицы.

Course:
- важен как guided learning layer;
- но должен использовать slices и stories;
- не должен превращать ARTEMIS в обычную LMS.

Следовательно:

> Object opens research. Slice preserves research. Story sequences research. Course teaches through research. AI explains research context.

---

## 3. Product meaning

Research Slice нужен, чтобы пользователь мог:

1. собрать исследовательское состояние;
2. сохранить его;
3. вернуться к нему;
4. сравнить его с другим состоянием;
5. развить его в story, collection или course;
6. получить AI-assisted explanation без потери контекста.

Без Research Slice ARTEMIS остаётся:
- картой с фильтрами;
- каталогом объектов;
- набором карточек;
- или narrative-first продуктом без исследовательского ядра.

С Research Slice ARTEMIS становится:
- средой накопления исследовательской работы;
- системой возвращаемых контекстов;
- основой для stories/courses;
- базой для explainable AI assistance.

---

## 4. Что входит в Research Slice

Research Slice состоит из нескольких обязательных смысловых блоков.

### 4.1 Spatial context

Фиксирует:
- viewport;
- центр карты;
- zoom;
- возможную область интереса;
- выбранные пространственные сущности.

Цель:
- восстановить исследовательское положение пользователя в пространстве.

### 4.2 Temporal context

Фиксирует:
- выбранный год или диапазон дат;
- режим timeline;
- временной фильтр;
- temporal state, влияющий на отображение объектов.

Цель:
- восстановить исследовательское положение пользователя во времени.

### 4.3 Layer context

Фиксирует:
- активные слои;
- отключённые слои;
- быстрые фильтры;
- category/layer state.

Цель:
- сохранить не всю базу, а конкретную конфигурацию видимости.

### 4.4 Entity context

Фиксирует:
- выбранные объекты/features;
- selected feature;
- связанные сущности, если они поддерживаются текущим runtime;
- порядок или фокус исследования.

Цель:
- определить, какие entities входят в исследовательскую конфигурацию.

### 4.5 Filter context

Фиксирует:
- search/filter state;
- confidence filters;
- category filters;
- other workspace constraints.

Цель:
- восстановить не только карту, но и логику отбора.

### 4.6 Human context

Фиксирует:
- title;
- description;
- note;
- annotation;
- curator/user explanation;
- explicit hypothesis or interpretation, if present.

Цель:
- сохранить человеческий смысл среза, а не только машинное состояние UI.

### 4.7 AI context

Фиксирует или предоставляет:
- explainability context;
- selected entities;
- temporal/spatial/layer constraints;
- user notes;
- allowed epistemic status for AI output.

Цель:
- дать AI не произвольный prompt, а ограниченный исследовательский контекст.

---

## 5. Minimal v1.0 baseline

Минимальный Research Slice v1.0 должен включать:

- unique id;
- owner/user id;
- title;
- optional description;
- feature refs;
- time range;
- view state;
- selected feature id if present;
- enabled layer ids;
- optional annotations;
- visibility state;
- created/updated timestamps.

Runtime/API baseline для JSON model и endpoints определён в:

- `docs/RESEARCH_SLICE_SPEC.md`

Этот contract определяет смысл и границы slice. `RESEARCH_SLICE_SPEC.md` определяет текущую runtime/API форму.

Если contract и spec расходятся:
- текущий runtime проверяется по `RESEARCH_SLICE_SPEC.md` и tests;
- продуктовый смысл проверяется по этому contract;
- расхождение должно быть устранено через отдельный docs/code sync cycle.

---

## 6. Lifecycle

### 6.1 Create

Пользователь формирует slice из текущего map-time workspace.

Create должен сохранять:
- selected entities;
- current time state;
- current view state;
- active layers;
- relevant filters;
- minimal metadata.

### 6.2 Save

Slice сохраняется как owner-only resource.

Для baseline v1.0:
- slice private by default;
- canonical public dataset не меняется;
- slice не публикует UGC в public knowledge base.

### 6.3 Reopen

Пользователь может восстановить slice.

Reopen должен возвращать:
- карту;
- timeline;
- layers;
- selected entities;
- detail context if available.

### 6.4 Update

Пользователь может изменить slice.

Update допустим для:
- title;
- description;
- selected entities;
- time range;
- view state;
- annotations.

### 6.5 Delete

Пользователь может удалить private slice.

Delete не должен:
- удалять public data;
- менять canonical dataset;
- удалять source entities.

### 6.6 Share

Share является planned product layer, если он ещё не реализован полноценно.

Share не должен нарушать:
- owner/privacy model;
- source/provenance discipline;
- distinction between private research state and public canonical knowledge.

### 6.7 Compare

Compare является важным planned product behavior.

Compare должен сопоставлять:
- time ranges;
- selected entities;
- layers;
- spatial focus;
- annotations;
- AI summaries if present.

Compare не должен автоматически превращать correlation into causation.

### 6.8 Evolve into Story / Course

Slice может стать строительным блоком:
- story step;
- course module;
- guided learning state;
- collection item.

Story/course должны ссылаться на slice или slice-like state, а не дублировать его логику.

---

## 7. Relationship to other product entities

### 7.1 Object / Feature

Object or Feature:
- is an entry point;
- provides factual/detail context;
- may be selected into a slice.

It is not the primary value unit.

### 7.2 Research Slice

Research Slice:
- is the primary value unit;
- preserves research context;
- enables return, compare, share and explanation.

### 7.3 Collection

Collection:
- groups slices, entities or scenarios;
- is an organizational layer;
- must not replace slice semantics.

### 7.4 Story

Story:
- sequences slices or slice-like states;
- adds narrative/analytical progression;
- should not become a standalone article detached from map-time context.

### 7.5 Course

Course:
- uses stories/slices for guided learning;
- adds educational progression;
- must not turn ARTEMIS into a generic LMS detached from spatial-temporal research.

### 7.6 AI Insight

AI Insight:
- may explain a slice;
- may compare slices;
- may suggest hypotheses;
- must be marked as AI output;
- must not become canonical fact without review.

---

## 8. Epistemic requirements

Research Slice may contain different epistemic layers:

- fact;
- relation;
- interpretation;
- hypothesis;
- AI-generated summary;
- AI-generated comparison;
- uncertainty notes.

Rules:

1. Fact must not be mixed with interpretation.
2. Hypothesis must be explicitly marked.
3. AI output must be explicitly marked.
4. User annotation must be distinguishable from source-backed data.
5. Counterfactual or speculative content must not be shown as historical reality.
6. Strong claims based on slice context must expose their basis.

Current annotation baseline in `RESEARCH_SLICE_SPEC.md` supports:
- `fact`;
- `interpretation`;
- `hypothesis`.

Future epistemic expansion must align with `EPISTEMIC_CONTRACT.md` after that document is created.

---

## 9. AI requirements

AI must work from slice context, not from detached conversation alone.

Allowed AI behaviors:

- explain selected slice;
- summarize selected entities;
- compare two slices;
- identify visible patterns;
- suggest hypotheses;
- point out missing or weak data;
- help transform slice into story/course draft.

Forbidden AI behaviors:

- present AI output as source-backed fact;
- create canonical public content without review;
- infer causality without explicit epistemic marking;
- hide uncertainty;
- ignore source/provenance constraints;
- generate counterfactual scenarios as if they were history.

AI outputs related to slice must include or be able to expose:

- input slice id/context;
- entities considered;
- time/spatial/layer constraints;
- epistemic status;
- confidence/uncertainty note where relevant;
- source/provenance basis where available.

---

## 10. Data and runtime boundaries

Research Slice is not the canonical public data source.

Rules:

- `data/features.geojson` remains the canonical public map dataset.
- Research Slice references public features/entities but does not redefine them.
- Slice may store private user context.
- Slice may store annotations, but annotations do not become public facts automatically.
- Slice deletion must not affect source features.
- Slice sharing must not alter public dataset.
- Slice API must enforce owner-only access unless a separate sharing contract is introduced.

Runtime/API details remain in:

- `docs/RESEARCH_SLICE_SPEC.md`

Public data/export details remain in:

- `docs/DATA_CONTRACT.md`

---

## 11. Visibility and ownership

Baseline v1.0:

- slice is private by default;
- owner-only access is required;
- cross-user access is not baseline unless explicitly introduced;
- public sharing requires a separate sharing contract;
- collaborative editing is out of baseline scope.

Visibility states may evolve later, but must be explicit:

- private;
- unlisted/share-link;
- public curated;
- collaborative.

Only `private` is baseline unless implemented and documented otherwise.

---

## 12. Out of scope for current baseline

The following are not part of the current baseline unless separately implemented and documented:

- fully public slice publishing;
- collaborative slice editing;
- social feed of slices;
- automatic canonical publishing from slice annotations;
- AI-generated public knowledge without moderation;
- causal engine over slices;
- counterfactual simulation layer;
- unrestricted import/export of arbitrary user datasets;
- standalone AI conversations detached from slice context as core product value.

---

## 13. Acceptance criteria

Research Slice is correctly implemented conceptually if:

1. It restores a meaningful map-time research state.
2. It contains selected entities or equivalent research focus.
3. It preserves enough context for later return.
4. It is distinct from object, story and course.
5. It can serve as basis for story/course/AI explanation.
6. It does not alter canonical public data by itself.
7. It preserves epistemic separation of facts, interpretations, hypotheses and AI output.
8. It is owner-controlled unless a separate sharing model is explicitly defined.

---

## 14. Failure modes

The slice model is considered degraded if:

- slice becomes just a bookmark;
- slice becomes just a saved viewport;
- slice duplicates story logic;
- slice stores unmarked AI output as fact;
- slice changes public data without governance;
- slice sharing bypasses ownership/privacy rules;
- slice cannot be used by stories/courses/AI as context;
- object card becomes the main value unit instead of slice.

---

## 15. Change-control rule

Any change to Research Slice semantics must check impact on:

- `docs/ARTEMIS_PRODUCT_SCOPE.md`;
- `docs/RESEARCH_SLICE_SPEC.md`;
- `docs/DATA_CONTRACT.md`;
- `docs/EPISTEMIC_CONTRACT.md` after creation;
- stories runtime;
- courses runtime;
- AI/ECC layer;
- frontend map-time workspace;
- auth/ownership model;
- tests and release checks if executable behavior changes.

A slice-related change is incomplete if product semantics, runtime/API shape and downstream story/course/AI assumptions are not synchronized.

---

## 16. Итог

Research Slice is the core unit that prevents ARTEMIS from collapsing into separate modules.

It connects:

- map;
- time;
- entities;
- filters;
- layers;
- human notes;
- stories;
- courses;
- AI assistance.

The correct development direction is:

1. stabilize slice as research context;
2. build stories from slices;
3. build courses from stories/slices;
4. let AI explain and compare slice contexts;
5. avoid turning ARTEMIS into generic map, LMS, social platform or AI chat.
