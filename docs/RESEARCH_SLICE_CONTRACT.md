# ARTEMIS — RESEARCH SLICE CONTRACT

## Статус документа

- Тип: foundation product/data/UI/AI contract document
- Статус: active, canonical registration confirmed in `PROJECT_STRUCTURE.md` and `DOCUMENTATION_SYSTEM.md`
- Роль: фиксирует Research Slice как воспроизводимый результат исследовательской работы; доказательное сравнение создаёт первую ценность, Slice сохраняет и передаёт её
- Назначение: определить отличие Research Slice от Saved View, обязательный смысловой состав, lifecycle и границы интеграции
- Scope: product semantics, data semantics, UI semantics, lifecycle, MVP baseline, out-of-scope boundaries

---

## 1. Главная формула

Research Slice — это не просто сохранённый вид карты.

Research Slice — это **минимальная сохраняемая единица исследовательского контекста ARTEMIS**.

Он фиксирует, что пользователь исследовал:

- какой вопрос был поставлен;
- какие сущности были выбраны;
- почему они были выбраны;
- какие sources/relations использованы как evidence;
- какие заметки, интерпретации, выводы и uncertainty были зафиксированы;
- какой Saved View позволяет восстановить пространственно-временной UI-контекст.

`Saved View` фиксирует viewport, time state, layers, filters и selection. Он является компонентом Research Slice, но не исследовательским результатом сам по себе.

Минимальный смысл Research Slice должен отвечать на четыре вопроса:

1. Что исследовалось?
2. Почему выбраны эти объекты?
3. Какие доказательства использованы?
4. К какому выводу пришёл пользователь и что осталось неопределённым?

---

## 2. Почему Research Slice является главным повторно используемым артефактом

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

> Object opens research. Comparison creates understanding. Slice preserves and communicates the result.

Story, Course и AI могут использовать Slice позднее, но не определяют его MVP-семантику.

---

## 3. Product meaning

Research Slice нужен, чтобы пользователь мог:

1. собрать исследовательское состояние;
2. связать вопрос и вывод с evidence;
3. сохранить его;
4. вернуться к нему;
5. передать read-only результат другому человеку;
6. позднее использовать как source-bound context для downstream layers.

Без Research Slice ARTEMIS остаётся:
- картой с фильтрами;
- каталогом объектов;
- набором карточек;
- или narrative-first продуктом без исследовательского ядра.

С Research Slice ARTEMIS становится:
- средой накопления исследовательской работы;
- системой возвращаемых контекстов;
- системой воспроизводимых evidence-aware сравнений;
- потенциальной основой для будущих stories/courses/AI assistance.

---

## 4. Что входит в Research Slice

Research Slice состоит из обязательного исследовательского содержания и вложенного Saved View.

### 4.1 Research question

Фиксирует:
- вопрос или проверяемую тему;
- краткую цель сравнения.

Цель:
- объяснить, что именно пользователь пытался понять.

### 4.2 Selection rationale

Фиксирует:
- выбранные Features/entities;
- причину выбора;
- порядок или фокус сравнения.

Цель:
- сделать выбор объектов воспроизводимым, а не случайным.

### 4.3 Evidence context

Фиксирует:
- source references;
- reviewed Relations;
- явно обозначенную computed similarity;
- связь evidence с заметкой или выводом.

Цель:
- показать основание исследования и не смешать evidence с inference.

### 4.4 Human findings

Фиксирует:
- notes;
- interpretation;
- hypothesis;
- conclusion;
- uncertainty или unresolved questions.

Цель:
- сохранить человеческий смысл и результат, а не только машинное состояние UI.

### 4.5 Saved View: spatial context

Фиксирует:
- viewport;
- центр карты;
- zoom;
- возможную область интереса;
- выбранные пространственные сущности.

Цель:
- восстановить исследовательское положение пользователя в пространстве.

### 4.6 Saved View: temporal context

Фиксирует:
- выбранный год или диапазон дат;
- режим timeline;
- временной фильтр;
- temporal state, влияющий на отображение объектов.

Цель:
- восстановить исследовательское положение пользователя во времени.

### 4.7 Saved View: layer context

Фиксирует:
- активные слои;
- отключённые слои;
- быстрые фильтры;
- category/layer state.

Цель:
- сохранить не всю базу, а конкретную конфигурацию видимости.

### 4.8 Saved View: entity context

Фиксирует:
- выбранные объекты/features;
- selected feature;
- связанные сущности, если они поддерживаются текущим runtime;
- порядок или фокус исследования.

Цель:
- определить, какие entities входят в исследовательскую конфигурацию.

### 4.9 Saved View: filter context

Фиксирует:
- search/filter state;
- confidence filters;
- category filters;
- other workspace constraints.

Цель:
- восстановить не только карту, но и логику отбора.

### 4.10 Metadata and version

Фиксирует:
- title;
- description;
- owner;
- created/updated timestamps;
- schema/content version;
- visibility/share state.

Цель:
- обеспечить traceability, update и воспроизводимость.

### 4.11 Future AI context

Может позднее предоставлять:
- explainability context;
- selected entities;
- temporal/spatial/layer constraints;
- user notes;
- allowed epistemic status for AI output.

Цель:
- дать AI не произвольный prompt, а ограниченный исследовательский контекст.

---

## 5. Minimal MVP baseline

Минимальный product-complete Research Slice MVP должен включать:

- unique id;
- owner/user id;
- title;
- research question;
- optional description/selection rationale;
- feature refs;
- evidence refs или явно зафиксированное отсутствие evidence;
- минимум одну user note/finding;
- conclusion либо explicit unresolved state;
- uncertainty notes where relevant;
- time range;
- view state;
- selected feature id if present;
- enabled layer ids;
- visibility state;
- schema/content version;
- created/updated timestamps.

Runtime/API baseline для JSON model и endpoints определён в:

- `docs/RESEARCH_SLICE_SPEC.md`

Этот contract определяет смысл и границы slice. `RESEARCH_SLICE_SPEC.md` определяет текущую runtime/API форму.

Если contract и spec расходятся:
- текущий runtime проверяется по `RESEARCH_SLICE_SPEC.md` и tests;
- продуктовый смысл проверяется по этому contract;
- capability нельзя объявлять validation-ready;
- расхождение должно быть устранено через отдельный docs/code sync cycle.

Текущий runtime baseline ещё не имеет отдельных first-class полей для question, evidence refs, conclusion и content version. До schema/code sync он является persistence envelope для Slice, но не доказательством product-complete Research Slice.

---

## 6. Lifecycle

### 6.1 Create

Пользователь формирует slice из текущего map-time workspace.

Create должен сохранять:
- research question;
- selected entities;
- evidence context;
- notes/findings;
- conclusion или unresolved state;
- current time state;
- current view state;
- active layers;
- relevant filters;
- minimal metadata.

### 6.2 Save

Slice сохраняется как owner-only resource.

Для MVP baseline:
- slice private by default;
- canonical public dataset не меняется;
- slice не публикует UGC в public knowledge base.

### 6.3 Reopen

Пользователь может восстановить slice.

Reopen должен возвращать:
- research question и findings;
- evidence refs;
- карту;
- timeline;
- layers;
- selected entities;
- detail context if available.

### 6.4 Update

Пользователь может изменить slice.

Update допустим для:
- title;
- research question;
- description;
- evidence refs;
- conclusion/uncertainty;
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

Share реализуется как явная unlisted read-only capability-ссылка поверх private-by-default Slice.

Share не должен нарушать:
- owner/privacy model;
- source/provenance discipline;
- distinction between private research state and public canonical knowledge.

Текущий baseline:
- raw capability token передаётся владельцу только при создании/rotation;
- backend хранит только hash token;
- повторный share инвалидирует предыдущую ссылку;
- revoke и delete немедленно закрывают публичное чтение;
- shared response не раскрывает owner identity и не допускает mutation;
- sharing не создаёт searchable/public-curated запись.

### 6.7 Object comparison

Сравнение 2–3 Features является обязательным upstream behavior, которое создаёт содержание Slice.

Compare должен сопоставлять:
- temporal/spatial/style/source properties;
- reviewed Relations;
- clearly labelled Similarity;
- provenance.

Compare не должен автоматически превращать correlation into causation.

Slice-to-Slice compare является future behavior и не заменяет object comparison в MVP.

### 6.8 Future downstream use

Slice может стать строительным блоком:
- story step;
- course module;
- guided learning state;
- collection item.

Downstream layer должен ссылаться на slice или slice-like state, а не дублировать его логику. Этот пункт не открывает Stories/Courses/AI в active MVP.

---

## 7. Relationship to other product entities

### 7.1 Object / Feature

Object or Feature:
- is an entry point;
- provides factual/detail context;
- may be selected into a slice.

Object comparison creates the first user value.

### 7.2 Research Slice

Research Slice:
- is the primary reusable research artifact;
- preserves question, evidence, findings and Saved View;
- enables return, update and read-only share.

### 7.3–7.6 Future downstream entities

Collection, Story, Course и AI Insight могут использовать Slice после соответствующего validation/scope decision. Они не входят в обязательный MVP loop и не должны определять текущий Slice schema.

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

Future epistemic expansion must align with the active `EPISTEMIC_CONTRACT.md`.

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
- Slice API enforces owner-only CRUD; отдельный share-контракт разрешает только unlisted read-only capability access.

Runtime/API details remain in:

- `docs/RESEARCH_SLICE_SPEC.md`

Public data/export details remain in:

- `docs/DATA_CONTRACT.md`

---

## 11. Visibility and ownership

MVP baseline:

- slice is private by default;
- owner-only access is required;
- unlisted read-only access разрешён только по явно созданному capability token;
- share capability не даёт owner/update/delete permissions;
- collaborative editing is out of baseline scope.

Visibility states may evolve later, but must be explicit:

- private;
- unlisted/share-link;
- public curated;
- collaborative.

Текущий реализованный baseline: `private` owner resource + `unlisted/share-link` read-only capability. `public curated` и `collaborative` не реализованы.

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

1. It records a research question or explicit topic.
2. It contains selected entities and selection rationale.
3. It exposes source/relation evidence or explicitly records that evidence is missing.
4. It preserves at least one human note/finding and a conclusion or unresolved state.
5. It restores a meaningful Saved View without being reduced to that view.
6. It preserves enough versioned context for later return.
7. It is distinct from object, Story and Course.
8. It does not alter canonical public data by itself.
9. It preserves epistemic separation of facts, interpretations, hypotheses and AI output.
10. It is owner-controlled unless a separate sharing model is explicitly defined.

---

## 14. Failure modes

The slice model is considered degraded if:

- slice becomes just a bookmark;
- slice becomes just a saved viewport;
- question, evidence and conclusion cannot be recovered;
- a conclusion cannot be traced to supporting evidence;
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
- `docs/EPISTEMIC_CONTRACT.md`;
- stories runtime;
- courses runtime;
- AI/ECC layer;
- frontend map-time workspace;
- auth/ownership model;
- tests and release checks if executable behavior changes.

A slice-related change is incomplete if product semantics, runtime/API shape and downstream story/course/AI assumptions are not synchronized.

---

## 16. Итог

Research Slice is the reusable research artifact that prevents ARTEMIS from collapsing into a map with bookmarks.

It connects:

- research question;
- selected entities;
- evidence;
- human notes;
- conclusion and uncertainty;
- Saved View: map, time, filters and layers.

The correct development direction is:

1. separate Saved View from product-complete Research Slice;
2. make question, evidence, finding and conclusion explicit;
3. prove public save/reopen/share on a real research task;
4. validate cognitive and behavioral reuse;
5. consider Stories, Courses or AI only after an explicit scope decision.
