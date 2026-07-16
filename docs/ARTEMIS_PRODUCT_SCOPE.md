# ARTEMIS — PRODUCT SCOPE v1.1

## Статус

- Тип: canonical product scope document.
- Статус: active.
- Дата решения: 2026-07-16.
- Активный delivery focus: Architecture Atlas vertical MVP.
- Долгосрочная миссия определяется `ARTEMIS_CONCEPT.md`.
- Фактическая доступность определяется `PROJECT_TRUTH.md`.

Этот документ защищает текущий цикл от product drift. Он не отменяет долгосрочную explainable spatial-temporal architecture, но запрещает выдавать её за scope ближайшего продукта.

## 1. Формула текущего продукта

ARTEMIS v1.1 — **доказательный пространственно-временной атлас истории архитектуры**.

Его задача:

- показать архитектурные объекты в пространстве и времени;
- дать содержательное сравнение;
- показать документированные relations и отдельно вычисляемую similarity;
- сделать provenance видимым;
- сохранить исследовательский контекст как Research Slice;
- предложить ограниченные curated Stories.

## 2. Primary user

Первичный пользователь:

- продвинутый студент истории архитектуры/искусства;
- преподаватель;
- исследователь, автор или куратор.

Primary job:

> Найти, сопоставить и сохранить архитектурные объекты в пространстве и времени, понимая источники и статус показанных связей.

Формулировка «любой интеллектуальный пользователь» недостаточна для приоритизации и не используется как primary persona текущего цикла.

## 3. Главная ценность

Главный момент ценности — доказательное сравнение объектов. Главная сохраняемая единица — Research Slice.

Research Slice включает:

- spatial focus/viewport;
- time state;
- выбранные Features;
- active filters/layers;
- comparison state;
- user notes;
- title и metadata;
- source-aware references.

Обязательные Slice actions для MVP:

- create;
- save;
- list;
- reopen/restore;
- update/rename;
- delete;
- share as read-only state.

## 4. Core product loop

1. Выбрать эпоху, направление или регион.
2. Найти объекты через map/time/filter.
3. Открыть sourced detail.
4. Сравнить 2–3 объекта.
5. Изучить reviewed relations либо clearly labelled similarity.
6. Сохранить Research Slice.
7. Вернуться к Slice или поделиться им.

Stories являются curated входом и downstream-слоем. Courses и AI не входят в active MVP loop.

## 5. Обязательный scope

### 5.1 Curated architecture data

- Architecture Features с canonical UUID;
- reviewed Layers;
- Sources с ролью evidence;
- Media с direct asset URL, license и attribution;
- reviewed Relations;
- semantic validation gate;
- controlled publish flow.

Семантика полей определяется `DATA_DICTIONARY.md`, export mechanics — `DATA_CONTRACT.md`.

### 5.2 Map-time workspace

- map;
- compact timeline;
- search;
- filters по периоду, направлению и региону;
- selected state;
- sourced detail panel;
- desktop/tablet/mobile adaptation.

### 5.3 Compare

- выбор 2–3 объектов;
- сравнение temporal/spatial/style/source properties;
- отдельное отображение Relations и Similarity;
- отсутствие неподтверждённых causal claims.

### 5.4 Research Slices

- полный public end-to-end loop;
- backend persistence;
- восстановление контекста;
- shareable read-only state.

### 5.5 Curated Stories

- минимум три редакционных маршрута;
- шаги на основе sourced Features/Relations;
- синхронизация с map/time/detail.

### 5.6 Provenance and epistemic clarity

UI различает:

- fact;
- source;
- reviewed relation;
- computed similarity;
- interpretation;
- hypothesis;
- unavailable/future AI.

## 6. Public capability rule

Функция входит в пользовательскую primary navigation только если она работает на public deployment end-to-end.

Backend-код без public API deployment обозначается `BACKEND-AVAILABLE`, а не «доступно пользователю».

Thin CRUD не считается полноценной Stories/Courses product depth.

## 7. Frozen scope до validation gate

- Courses expansion;
- AI generation/explanation;
- open-ended UGC;
- new domain/entity expansion;
- causal engine;
- counterfactual simulation;
- predictive layers;
- gamification;
- native apps;
- enterprise API/integrations;
- non-critical scaling и framework rewrite.

Существующий код замороженных слоёв может сохраняться, тестироваться и получать security fixes, но не задаёт product roadmap.

## 8. Content threshold

Перед первой внешней validation:

- 100–150 Features;
- 15–20 непустых Layers/periods/styles;
- 50+ reviewed Relations;
- source coverage для всех Features;
- media attribution для ключевых Features;
- 3 curated Stories;
- 5–10 reference Slices.

Полная граница MVP определяется `MVP_ARCHITECTURE_ATLAS.md`.

## 9. AI boundary

Explain Context Contract может существовать как backend contract, но AI generation не считается реализованной product feature.

Будущий AI обязан:

- опираться на selected sourced context;
- отделять fact от interpretation/hypothesis;
- показывать provenance;
- не создавать canonical Relations;
- не скрывать uncertainty.

## 10. Validation gate

Product expansion запрещён до выполнения `PRODUCT_VALIDATION_PLAN.md`.

Минимальное решение после validation:

- `ITERATE`;
- `EXPAND`;
- `NARROW`;
- `STOP/RETHINK`.

Только явно зафиксированное решение может изменить этот scope.

## 11. Связанные owner documents

- `PRODUCT_THESIS.md` — аудитория, проблема, hypotheses и value proposition;
- `PROJECT_TRUTH.md` — фактическое текущее состояние;
- `MVP_ARCHITECTURE_ATLAS.md` — MVP boundary и exit criteria;
- `DATA_DICTIONARY.md` — semantic data model;
- `PRODUCT_VALIDATION_PLAN.md` — evidence gate;
- `RESEARCH_SLICE_CONTRACT.md` — Slice semantics;
- `EPISTEMIC_CONTRACT.md` — knowledge-type rules;
- `CONTENT_GOVERNANCE.md` — trusted content governance;
- `PROJECT_PHASES.md` и `PRIORITIES.md` — operational order.
