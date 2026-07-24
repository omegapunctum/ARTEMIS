# ARTEMIS — PRODUCT SCOPE v1.2

## Статус

- Тип: canonical product scope document.
- Статус: active.
- Дата решения: 2026-07-24.
- Активный delivery focus: Architecture Atlas vertical MVP.
- North Star определяется `ARTEMIS_CONCEPT.md`.
- Фактическая доступность определяется `PROJECT_TRUTH.md`.

Этот документ защищает текущий цикл от product drift. Он не отменяет долгосрочную explainable spatial-temporal architecture, но запрещает выдавать её за scope ближайшего продукта.

## 1. Формула текущего продукта

ARTEMIS Architecture Atlas — **инструмент доказательного сравнения архитектурных объектов в пространстве и времени**.

Его задача:

- показать архитектурные объекты в пространстве и времени;
- дать содержательное сравнение;
- показать документированные relations и отдельно вычисляемую similarity;
- сделать provenance видимым;
- сохранить вопрос, evidence, заметку/вывод и восстановимый контекст как Research Slice.

Stories могут использоваться как curated вход в основной цикл, но не являются самостоятельным обязательным продуктовым слоем MVP.

## 2. Primary user

Первичный пользователь:

- продвинутый студент истории архитектуры/искусства, готовящий сравнительное эссе, семинар или исследовательское задание.

Primary job:

> Сопоставить 2–3 архитектурных объекта, понять основания сходства и различий, проверить источники и сохранить доказательное сравнение для дальнейшей работы.

Формулировка «любой интеллектуальный пользователь» недостаточна для приоритизации и не используется как primary persona текущего цикла.

Преподаватели и кураторы являются вторичной exploratory-аудиторией. Профессиональные исследователи не считаются beachhead-аудиторией до расширения корпуса и provenance depth.

## 3. Главная ценность

Главный момент ценности — доказательное сравнение объектов. Главная сохраняемая единица — Research Slice.

Следствие для UX: object comparison является primary analytical action, а Research Slice — результатом, который сохраняет уже собранный контекст. Сравнение сохранённых срезов не заменяет сравнение 2–3 Features и не использует тот же primary action без явного уточнения.

Research Slice включает:

- research question;
- выбранные Features;
- rationale выбора;
- отобранные evidence/source-aware references;
- user notes, findings и uncertainty;
- conclusion;
- Saved View: spatial focus/viewport, time state, active filters/layers и comparison state;
- title, metadata и version.

`Saved View` — компонент Research Slice, а не его синоним. Сохранённый viewport без вопроса, evidence и человеческого вывода не считается продуктово завершённым Research Slice.

Обязательные Slice actions для MVP:

- create;
- save;
- list;
- reopen/restore;
- update/rename;
- delete;
- share as read-only state.

## 4. Core product loop

1. Сформулировать или выбрать исследовательский вопрос.
2. Найти 2–3 объекта через map/time/filter.
3. Сравнить sourced detail, properties и relations.
4. Проверить reviewed evidence и отдельно labelled similarity.
5. Зафиксировать заметку, вывод и неопределённость.
6. Сохранить Research Slice.
7. Вернуться к Slice или поделиться им.

Stories допускаются только как curated вход в этот цикл. Courses и AI не входят в active MVP loop.

User-facing terminology: до отдельной validation термин `Research Slice` отображается как «Сохранённое исследование» с возможной вторичной подписью «срез». Onboarding не требует знания внутреннего термина до получения первой ценности.

## 5. Обязательный scope

### 5.1 Curated architecture data

- Architecture Features с canonical UUID;
- reviewed Layers;
- Sources с ролью evidence;
- Media с direct asset URL, license и attribution;
- reviewed Relations;
- semantic validation gate;
- controlled publish flow.

Контент производится сравнительными когортами, а не отдельными несвязанными объектами. Для каждой когорты фиксируются research question, 3–5 Features, evidence-backed Relations, Sources, rights-clean Media и reference Slice. Измеряются preparation time, review time и reuse.

Семантика полей определяется `DATA_DICTIONARY.md`, export mechanics — `DATA_CONTRACT.md`.

### 5.2 Map-time workspace

- map;
- compact timeline;
- search;
- filters по периоду, направлению и региону;
- selected state;
- sourced detail panel;
- desktop/tablet/mobile adaptation.

Temporal claim boundary:

- MVP является time-indexed исследованием объектов, а не полной моделью их изменения;
- даты/периоды и timeline не доказывают поддержку reconstruction, destruction, function change или evolving geometry;
- будущая модель `Entity → Event → Time interval → State change → Evidence` открывается только после validation decision и начинается с одного архитектурного сценария.

### 5.3 Compare

- выбор 2–3 объектов;
- сравнение temporal/spatial/style/source properties;
- отдельное отображение Relations и Similarity;
- отсутствие неподтверждённых causal claims.

### 5.4 Research Slices

- полный public end-to-end loop;
- backend persistence;
- research question, evidence selection, notes/findings, conclusion и uncertainty;
- Saved View как восстановимый UI-компонент;
- восстановление контекста;
- shareable read-only state.

### 5.5 Optional curated entry

- один или несколько curated entry points допустимы для onboarding;
- каждый вход должен вести в основной Compare–Evidence–Save loop;
- отсутствие Stories не блокирует MVP validation и exit.

### 5.6 Provenance and epistemic clarity

Внутренняя epistemic model остаётся детальной. Primary UI группирует статусы в четыре понятных класса:

- подтверждено источником;
- редакционная интерпретация;
- гипотеза или неопределённость;
- вычисленное сходство.

Подробный canonical status доступен по запросу и не теряется при упрощённом представлении.

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

Перед comparison-first Round 0:

- 30–40 Features;
- 6–8 comparison cohorts минимум по 3 Features;
- 12–20 reviewed Relations;
- source coverage 100%;
- primary Media coverage не ниже 90%;
- relation evidence coverage 100%.

Порог является утверждённым узким pilot envelope из `docs/work/2026-07-21_VALIDATION_CORPUS_PILOT_v1.md`. Более широкий ориентир 100–150 Features / 50+ Relations / reference Slices остаётся maturity reference после decision gate. Stories оцениваются отдельно как onboarding-механизм. Полная граница MVP определяется `MVP_ARCHITECTURE_ATLAS.md`.

До expansion необходимо зафиксировать стоимость подготовки и проверки одной comparison cohort. Рост числа Features без этого показателя не доказывает масштабируемую content model.

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

Проверка разделяется на три независимых gate:

- usability — пользователь завершает сценарий;
- cognitive value — сравнение создаёт новое или уточнённое понимание, связанное с evidence;
- behavioral value — пользователь самостоятельно возвращается, изменяет или передаёт сохранённое исследование.

Map + time должны сравниваться с catalogue/list baseline. Прохождение usability без cognitive и behavioral evidence не открывает expansion.

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
