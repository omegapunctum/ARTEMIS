# ARTEMIS — UX Concept Correction v1

## Статус

- Тип: active product/UX decision record.
- Дата: 2026-07-17.
- Область: Architecture Atlas vertical MVP, public workspace и следующий UI refinement cycle.
- Решение: comparison-first discovery, Research Slice as saved output.
- Implementation status: documentation contract only; runtime не изменён этим документом.
- Responsive wireframe owner: `2026-07-17_COMPARISON_FIRST_WIREFRAME_SPEC_v1.md`.

Этот документ устраняет расхождение между product thesis, component map и текущим runtime. Он не меняет Option A и не открывает новый feature scope.

## 1. Причина коррекции

Текущий интерфейс ставит Research Slice в начало пути пользователя: onboarding предлагает начать со среза, context strip постоянно показывает его состояние, а compare action привязан к выбору сохранённых срезов. При этом canonical product thesis определяет первый момент ценности иначе — пользователь должен найти и доказательно сравнить архитектурные объекты.

Дополнительные расхождения:

- public navigation показывает Stories, Courses и Saved как равноправные возможности, хотя GitHub Pages не предоставляет backend-dependent flows end-to-end;
- «Рабочая область» и «Исследования» визуально конкурируют за один и тот же workspace;
- пользовательский термин «срез» предъявляется до того, как пользователь понимает сохраняемый результат;
- desktop chrome резервирует постоянные зоны, не усиливающие поиск, выбор и сравнение объектов;
- timeline использует hardcoded historical anchors вместо контекста из реальных данных.

## 2. Принятое UX-решение

### 2.1 Первый момент ценности

Первый момент ценности ARTEMIS — **доказательное сравнение двух или трёх архитектурных объектов** по времени, месту, направлению, источникам и статусу связей.

Отдельный объект остаётся входом в исследование. Сравнение создаёт понимание. Research Slice сохраняет полученный контекст.

### 2.2 Роль Research Slice

Research Slice не является обязательным первым действием и не должен доминировать над пустым workspace.

Он является:

- сохраняемым результатом исследования;
- единицей возврата и восстановления контекста;
- read-only share unit;
- контейнером выбранных объектов, viewport, периода, слоёв, фильтров, comparison state и заметок.

Внутреннее canonical name остаётся `Research Slice`. В пользовательском copy до проверки терминологии допускается формула **«Сохранённое исследование»**, а короткое «Срез» используется как вторичная или экспертная подпись.

### 2.3 Primary loop

1. Выбрать период, направление или регион либо найти объект через search.
2. Открыть sourced preview/detail.
3. Добавить объект в comparison selection.
4. Сопоставить 2–3 объекта.
5. Проверить provenance, reviewed Relations и отдельно labelled Similarity.
6. Сохранить результат как Research Slice.
7. Вернуться к нему или поделиться read-only представлением.

Stories могут быть curated entry point в этот loop. Courses, AI и open UGC остаются frozen.

## 3. Public information architecture

### 3.1 Navigation target

Целевая IA продукта:

1. **Исследование** — default map-time workspace.
2. **Сравнение** — contextual mode, доступный после выбора первого объекта; не отдельный пустой route.
3. **Сохранённые исследования** — public entry только при работающем Slice backend.
4. **Истории** — public entry только при наличии curated public Stories.

`Рабочая область` не дублирует `Исследование`. `Courses`, AI, UGC и moderation не входят в primary public navigation текущего цикла.

### 3.2 Capability truth rule

- `PUBLIC NOW` capability может находиться в primary navigation.
- `BACKEND-AVAILABLE` capability не показывается как обычная public action без configured backend.
- `PILOT` capability получает явную маркировку и не выглядит завершённой библиотекой.
- `FUTURE` capability скрывается из primary workflow.

Недоступная функция не маскируется под активную кнопку с ошибкой после клика.

### 3.3 Search language

Search placeholder и suggestions описывают только текущий corpus. Для Architecture Atlas baseline:

> Найти здание, стиль, город или период…

Люди, события и общие historical entities не обещаются до их появления в canonical data model и public corpus.

## 4. Target interaction model

### 4.1 Selection and comparison

- У sourced detail есть явное действие `Добавить к сравнению`.
- Comparison selection содержит от двух до трёх Features.
- После первого выбора появляется compact tray со счётчиком `1 из 3`.
- Tray позволяет открыть сравнение, заменить или удалить объект и очистить selection.
- Primary compare surface сопоставляет объекты, а не сохранённые срезы.
- Сравнение срезов может существовать позже как secondary analytical action и не использует тот же primary label.

### 4.2 Detail hierarchy

Detail раскрывается по уровням:

1. title, date, place/style, image и add-to-compare;
2. sourced factual summary;
3. provenance и media attribution рядом с соответствующим содержанием;
4. reviewed Relations;
5. отдельно labelled computed Similarity;
6. extended interpretation только по запросу.

Relation и Similarity не используют одинаковый visual treatment. Reviewed relation получает solid treatment; computed similarity — dashed/secondary treatment с видимыми критериями.

### 4.3 First-run experience

Onboarding не требует понимания термина Research Slice. Первый prompt предлагает найти объект или выбрать период. Следующая contextual подсказка появляется после открытия detail и объясняет comparison selection. Save предлагается после появления полезного контекста.

## 5. Target workspace geometry

### Desktop

- один compact top shell высотой 56–64 px;
- map занимает всю доступную основную сцену без structural left rail и decorative outer frame;
- search имеет полезную ограниченную ширину и corpus-accurate copy;
- map tools размещаются единым overlay control group;
- detail inspector занимает правую ширину только в открытом состоянии;
- comparison tray является contextual overlay и не резервирует пустую полосу;
- compact timeline занимает 72–88 px и может иметь expanded state;
- temporal context формируется из dataset distribution, выбранного периода или явного запроса, а не hardcoded anchors.

### Tablet and mobile

- toolbar остаётся overlay;
- detail становится staged overlay/bottom sheet;
- comparison tray адаптируется в bottom action bar;
- timeline остаётся доступным при закрытом sheet и получает coordination/interaction lock при открытом expanded sheet;
- touch hit area target — 44×44 px.

## 6. Visual direction

Working direction остаётся **Cartographic Research Editorial**:

- карта и данные визуально первичны;
- surfaces используются только для функциональной иерархии;
- primary blue обозначает action/selection;
- archival accent используется для provenance/editorial context;
- fact, reviewed relation, computed similarity, interpretation и uncertainty различаются не только цветом, но также label, line/border style и wording;
- Unicode/emoji primary icons заменяются единым SVG set;
- заявленные UI/editorial fonts должны реально загружаться либо быть заменены честным system-font baseline.

Новый visual theme сам по себе не считается решением UX-проблемы.

## 7. Scope boundaries

В scope следующего UX cycle:

- capability-aware navigation;
- terminology and onboarding correction;
- map-first shell geometry;
- compact data-aware timeline;
- object comparison selection and tray;
- sourced detail hierarchy;
- SVG icons, typography runtime и accessibility sizing;
- desktop/tablet/mobile regression coverage.

Не в scope:

- framework rewrite;
- Courses, AI или open UGC expansion;
- новые entity domains;
- изменение canonical identity/source/relation contracts;
- декоративный multi-theme project;
- сравнение сохранённых срезов как замена object comparison.

## 8. Delivery order

1. Синхронизировать canonical product/UX owner documents с этим решением.
2. Зафиксировать capability-aware navigation и user-facing glossary.
3. Выполнить wireframe contract `2026-07-17_COMPARISON_FIRST_WIREFRAME_SPEC_v1.md` для desktop 1440×900, tablet 1024×768 и mobile 390×844.
4. Выполнить shell/map/timeline geometry batch.
5. Реализовать object comparison selection и tray отдельным batch.
6. Выполнить sourced detail/epistemic presentation batch.
7. Завершить icon, typography, accessibility и responsive hardening.
8. Провести Round 0 truth check и пользовательскую validation по `PRODUCT_VALIDATION_PLAN.md`.

## 9. Acceptance criteria документационного этапа

- product thesis, scope, MVP boundary, UX system, component map и refinement spec не называют Slice первым обязательным действием;
- object comparison и slice comparison не смешиваются;
- public navigation следует capability truth rule;
- user-facing terminology отделена от internal canonical naming;
- следующий implementation batch не требует изменения data/API contracts;
- visual refinement не начинается до согласования wireframe states.
