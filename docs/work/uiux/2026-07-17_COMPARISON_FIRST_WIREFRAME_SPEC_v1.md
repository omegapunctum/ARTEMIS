# ARTEMIS — Comparison-first Responsive Wireframe Spec v1

## Статус

- Тип: active implementation wireframe contract.
- Дата: 2026-07-17.
- Product direction: Architecture Atlas vertical MVP.
- UX decision owner: `2026-07-17_UX_CONCEPT_CORRECTION_v1.md`.
- Runtime status: Batch C1 merged; Batch C2 implemented in a separate PR candidate; D/E/F remain pending.
- Reference viewports: desktop `1440×900`, tablet `1024×768`, mobile `390×844`.

Этот документ фиксирует структуру, состояния и responsive behavior. Он не является high-fidelity visual mockup и не вводит новый feature scope.

## 1. Цель

Сделать путь `найти → открыть sourced detail → выбрать 2–3 объекта → сравнить → сохранить исследование` видимым без предварительного знания термина Research Slice.

Wireframe должен одновременно защищать:

- map primacy;
- evidence visibility;
- relation/similarity separation;
- public capability truth;
- compact time control;
- staged mobile interaction;
- полный keyboard/focus path.

## 2. Обязательные состояния

| ID | Состояние | Обязательный результат |
|---|---|---|
| `S0` | loading | Каркас стабилен, карта и данные не выглядят пустым успешным состоянием |
| `S1` | ready / no selection | Карта первична; видимы search, period и map tools; Slice UI не доминирует |
| `S2` | object selected | Открыт sourced detail; доступно `Добавить к сравнению` |
| `S3` | comparison collecting | Tray показывает `1 из 3`; compare CTA ещё не primary-ready |
| `S4` | comparison ready | Выбрано 2–3 Features; доступно `Сравнить` |
| `S5` | compare active | Видно сопоставление fields, sources, Relations и Similarity |
| `S6` | filters / no results | Причина пустого результата понятна; доступен reset без потери приложения |
| `S7` | detail/compare partial data | Missing source/media/relation обозначены честно, layout не ломается |
| `S8` | backend capability unavailable | Backend-dependent navigation/actions скрыты или явно недоступны до входа в flow |

Additional regression states: map load error, offline cached data, search open, filters open, timeline expanded, mobile sheet expanded, keyboard focus and reduced motion.

## 3. Interaction invariants

1. Map click selects Feature and opens preview/detail; он не добавляет объект в comparison автоматически.
2. `Добавить к сравнению` является явным действием внутри sourced detail.
3. Comparison tray отсутствует до первого выбранного Feature.
4. При одном Feature tray показывает collecting state `1 из 3`; primary compare доступен с двух Features.
5. Третий Feature разрешён; четвёртый требует replace/remove, а не молчаливого вытеснения.
6. Закрытие compare surface сохраняет selection до явного `Очистить`.
7. Research Slice сохраняет текущие selection, viewport, period, layers/filters и notes после получения полезного контекста.
8. `Сравнить` для Features и secondary `Сопоставить исследования` не используют одинаковый label.
9. Reviewed Relation и computed Similarity никогда не объединяются в один безымянный related block.
10. Любое geometry-changing открытие/закрытие панели вызывает map resize после transition.

## 4. Desktop wireframe — 1440×900

### 4.1 Geometry contract

- top shell: `60 px`, допустимый диапазон `56–64 px`;
- compact timeline: `80 px`, допустимый диапазон `72–88 px`;
- map/workspace: всё пространство между shell и timeline;
- outer application gutter: `0`;
- structural left rail: `0`;
- map tool offset: `16 px` от functional edge;
- object detail inspector: `380–420 px`;
- compare surface: `640–760 px`, но map сохраняет минимум `480 px`;
- comparison tray: contextual overlay над timeline, без reserved row.

### 4.2 S1 — ready / no selection

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ ARTEMIS  [Найти здание, стиль, город или период…]  Исследование  Истории  ◉ │ 60
├──────────────────────────────────────────────────────────────────────────────┤
│ [＋]                                                                         │
│ [−]   [Слои]                                                                │
│ [⌖]   [Фильтры]                  MAP + MAPPED DATA                           │
│       [Тема]                                                                │
│                                                                              │
│                  first-run hint: «Выберите объект на карте                   │
│                  или найдите его через поиск»                                │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ Период  ─────────────●════════════●────────────  1200–1450  [Развернуть]    │ 80
└──────────────────────────────────────────────────────────────────────────────┘
```

Правила:

- header не содержит отдельную строку состояния Slice;
- `Сохранённые исследования` и `Истории` показываются только при public capability;
- first-run hint является лёгким contextual overlay, не modal blocker;
- controls MapLibre и ARTEMIS составляют одну левую вертикальную систему с визуальным разделением provider/native actions;
- theme action уходит в secondary controls/overflow, если группа не помещается.

### 4.3 S2/S3 — selected object and collecting comparison

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ ARTEMIS  [Поиск…]                                  Исследование  Истории  ◉ │
├───────────────────────────────────────────────────────┬──────────────────────┤
│ [map tools]                                           │ OBJECT DETAIL        │
│                                                       │ image / title        │
│                       MAP                             │ date · place · style │
│                                                       │ sourced summary      │
│                selected marker + halo                 │ [Добавить к сравнению]│
│                                                       │ Source / attribution │
│                                                       │ Relations            │
│                                                       │ Similarity           │
│                         [Объект A] [＋]  1 из 3        │                      │
├───────────────────────────────────────────────────────┴──────────────────────┤
│ Период  ─────────────●════════════●────────────  1200–1450                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

Правила:

- detail открывается справа и только тогда уменьшает map width;
- selected marker получает halo и остаётся видимым при открытом detail;
- tray располагается над timeline, центрируется в доступной map area и не перекрывает attribution;
- при `1 из 3` tray предлагает продолжить выбор; disabled compare не выглядит primary CTA;
- detail source расположен рядом с factual summary, а не только в конце панели.

### 4.4 S4/S5 — comparison ready and active

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ ARTEMIS  [Поиск…]                            Сравнение: 3 объекта  [Закрыть] │
├───────────────────────────────┬──────────────────────────────────────────────┤
│                               │ COMPARE                                      │
│            MAP                │ A             B             C                │
│   A ●──── reviewed ────● B    │ title         title         title            │
│     ╲ ··· similarity ··· ● C  │ time/place    time/place    time/place       │
│                               │ style         style         style            │
│                               │ sources       sources       sources          │
│                               │ ─ Reviewed Relations ─                       │
│                               │ - - Computed Similarity + criteria - -       │
├───────────────────────────────┴──────────────────────────────────────────────┤
│ Период  ─────────────●════════════●────────────  [Сохранить исследование]   │
└──────────────────────────────────────────────────────────────────────────────┘
```

Правила:

- compare является contextual analytical mode, не новой глобальной route;
- сравнение до трёх объектов использует выровненные rows, а не три независимые длинные карточки;
- missing value занимает место в row и маркируется `Нет данных`, чтобы колонки не смещались;
- source links доступны в каждой колонке;
- reviewed relation использует solid line/label; similarity — dashed line/label и критерии;
- `Сохранить исследование` появляется только при доступном public Slice backend; иначе action отсутствует и capability status доступен в system info.

## 5. Tablet wireframe — 1024×768

### 5.1 Geometry contract

- top shell: `56 px`;
- compact timeline: `76–80 px`;
- persistent structural rail: отсутствует;
- search: `minmax(280 px, 1fr)`;
- primary navigation: current mode + overflow;
- detail: right overlay `min(420 px, 52vw)`;
- compare: staged workspace overlay на всю content width;
- map tools: overlay `12 px` от edge.

### 5.2 Ready and selected

```text
┌──────────────────────────────────────────────────────────────┐
│ ARTEMIS  [Поиск…]                          Исследование  ⋯  ◉│ 56
├──────────────────────────────────────────────────────────────┤
│ [tools]                                  ┌───────────────────┐│
│                                          │ OBJECT DETAIL     ││
│                 MAP                      │ sourced preview   ││
│                                          │ add to compare    ││
│                                          │ evidence          ││
│             [A] [＋] 1 из 3              └───────────────────┘│
├──────────────────────────────────────────────────────────────┤
│ Период  ───────●════════●──────  1200–1450                  │ 80
└──────────────────────────────────────────────────────────────┘
```

Tablet detail overlays map; он не создаёт узкую остаточную map-column. Compare открывается как staged full content surface с явным `Назад к карте`, сохраняя selection и viewport state.

## 6. Mobile wireframe — 390×844

### 6.1 Geometry contract

- top shell: `52 px + safe-top`;
- default map fills remaining viewport above timeline;
- compact timeline: `72–76 px + safe-bottom`;
- toolbar: horizontal overlay, controls `44×44 px`;
- detail preview sheet: `40–48dvh`;
- expanded detail: до `calc(100dvh - safe-top - 52px)`;
- comparison tray: bottom action bar above timeline или внутри active sheet action zone;
- compare: full-screen stacked analytical view; map временно не виден, но state сохраняется.

### 6.2 S1 — mobile ready

```text
┌──────────────────────────────┐
│ ARTEMIS   [Поиск]        ⋯  │ 52
├──────────────────────────────┤
│ [Слои][Фильтры][⌖]           │
│                              │
│             MAP              │
│                              │
│  «Выберите объект или        │
│   задайте период»            │
│                              │
├──────────────────────────────┤
│ 1200–1450  ─●══════●─   ⌃   │ 72–76
└──────────────────────────────┘
```

### 6.3 S2/S3 — mobile detail and collecting

```text
┌──────────────────────────────┐
│ ARTEMIS                ×     │
├──────────────────────────────┤
│            MAP               │
│          selected ●          │
│                              │
├──────── detail sheet ────────┤
│ ── drag handle ──            │
│ Title · date · place         │
│ sourced summary              │
│ [Добавить к сравнению]       │
│ [A] [＋] 1 из 3              │
└──────────────────────────────┘
```

При открытом sheet timeline не остаётся интерактивным под ним. Collapsed sheet может сосуществовать с timeline только при отсутствии overlap; expanded sheet переводит timeline в interaction-locked state.

### 6.4 S5 — mobile compare

```text
┌──────────────────────────────┐
│ ← Сравнение        2 объекта │
├──────────────────────────────┤
│ [A] [B]                      │
│                              │
│ Время                        │
│ A: …              B: …       │
│ Место                        │
│ A: …              B: …       │
│ Источники                    │
│ A: ссылка         B: ссылка  │
│                              │
│ Reviewed Relations           │
│ Computed Similarity          │
├──────────────────────────────┤
│ [Сохранить исследование]*    │
└──────────────────────────────┘
```

Mobile compare использует rows/sections, а не горизонтальный overflow таблицы. `*` Save показывается только при доступной public capability.

## 7. Search, filters and no-results contract

### Search

- desktop/tablet: inline field с max useful width;
- mobile: icon/compact field открывает full-width search overlay;
- placeholder: `Найти здание, стиль, город или период…`;
- suggestions группируются по объектам, стилям/слоям, городам и периодам только при наличии соответствующих данных;
- keyboard: Arrow keys перемещают active option, Enter выбирает, Escape закрывает и возвращает focus.

### Filters

- active filter count видим в trigger;
- current constraints отображаются removable chips только при наличии активного ограничения;
- reset не сбрасывает comparison selection без отдельного подтверждённого действия;
- `S6` показывает число активных ограничений и action `Сбросить фильтры`, а не пустую карту без объяснения.

## 8. Timeline contract

- default state содержит range/point control, выбранный период и expand action;
- hardcoded historical event labels отсутствуют;
- optional context строится из реальных Feature dates: rug/histogram/density marks;
- tick density адаптируется к ширине и выбранному диапазону;
- point/range mode не дублирует выбранный период несколькими равнозначными labels;
- keyboard step и coarse step определены отдельно;
- expanded timeline является contextual surface, а не постоянной второй рабочей областью.

## 9. Detail and epistemic hierarchy

Порядок detail:

1. title, date, place/style;
2. media с attribution или честный placeholder;
3. primary action `Добавить к сравнению` / `Убрать из сравнения`;
4. sourced factual summary;
5. provenance/source links;
6. reviewed Relations;
7. computed Similarity с критериями;
8. interpretation/hypothesis только при наличии и с отдельной маркировкой.

Visual semantics не полагается только на цвет:

| Knowledge type | Label | Structural treatment |
|---|---|---|
| Fact | `Факт` при неоднозначном контексте | neutral surface |
| Reviewed Relation | `Документированная связь` | solid line/border |
| Computed Similarity | `Похожий объект` | dashed line/border + criteria |
| Interpretation | `Интерпретация` | archival accent + label |
| Hypothesis | `Гипотеза` | secondary accent + dashed boundary |
| Unavailable | `Нет данных` | muted explicit placeholder |

## 10. Capability-aware behavior

До рендера navigation/actions runtime формирует capability set.

| Capability | Public available | Public unavailable |
|---|---|---|
| Explore | show | blocking global error только при data failure |
| Object compare | show | скрывать только при критическом data-contract failure |
| Slice save/list/share | show navigation/action | не показывать primary navigation/action |
| Stories | show при curated corpus | не показывать пустую library как завершённый раздел |
| Courses/AI/UGC | frozen | отсутствуют в primary public navigation |

Capability state не выводится из наличия DOM-кнопки; он должен опираться на runtime configuration/health contract в отдельном implementation batch.

## 11. Accessibility and focus

- touch/click target: target `44×44 px`, absolute minimum `40×40 px` для плотного desktop control;
- icon-only control имеет accessible name и tooltip/title;
- focus order следует: shell → map tools/map → contextual tray → detail/compare → timeline;
- открытие detail переводит focus только при keyboard-triggered action; pointer selection не вызывает неожиданный scroll;
- staged tablet/mobile compare удерживает focus внутри surface и возвращает его в исходный trigger;
- escape закрывает только верхний active layer;
- selected/related/similar states различимы без цвета;
- `prefers-reduced-motion` отключает geometry animation без потери state feedback;
- live regions не объявляют каждое движение range handle, только committed value.

## 12. Layering and collision rules

Порядок снизу вверх:

1. map canvas and markers;
2. MapLibre controls and ARTEMIS map tools;
3. comparison tray / compact contextual overlays;
4. detail inspector or staged panel;
5. search/filter popover;
6. system status/toast;
7. modal/full-screen mobile compare.

Ни один overlay не перекрывает MapLibre attribution. На mobile одновременно открыта только одна primary staged surface: detail, filters, search или compare.

## 13. Implementation batches

### Batch C1 — shell geometry

- [x] capability-aware navigation shell;
- [x] remove decorative outer gutter/frame;
- [x] remove structural rail;
- [x] overlay tool placement;
- [x] one compact top shell;
- [x] map resize synchronization after inspector geometry changes.

### Batch C2 — timeline

- [x] compact `84 px` desktop/tablet and `80 px` mobile default;
- [x] remove hardcoded anchors and obsolete tests/constants;
- [x] omit temporal marks because the current feed exposes no evidence-backed mark contract;
- [x] preserve point/range, native range-input keyboard behavior and pointer drag.

### Batch D — object comparison

- Feature selection state independent from Slice comparison state;
- add/remove/replace/clear actions;
- comparison tray;
- 2–3 column/row compare surface;
- selected/relation/similarity map states.

### Batch E — sourced detail

- content hierarchy and add-to-compare action;
- provenance adjacency;
- Relation/Similarity visual grammar;
- partial/missing-data states.

### Batch F — responsive/accessibility polish

- SVG icons and actual font-loading decision;
- 44 px targets;
- tablet overlays and mobile sheets;
- focus, reduced motion, collision and visual regression pass.

Каждый batch получает отдельный PR и не смешивается с framework rewrite.

## 14. Acceptance matrix

| State | 1440×900 | 1024×768 | 390×844 |
|---|---:|---:|---:|
| S0 loading | required | required | required |
| S1 ready | required | required | required |
| S2 selected detail | required | required | required |
| S3 compare collecting | required | required | required |
| S4 compare ready | required | required | required |
| S5 compare active | required | required | required |
| S6 no results | required | required | required |
| S7 partial data | required | required | required |
| S8 backend unavailable | required | required | required |

For every cell verify: no horizontal overflow, map/control collision, clipped primary CTA, hidden attribution, unreachable focus target or false public capability promise.

## 15. Implementation gate

Runtime work может начаться, когда:

- этот wireframe contract принят;
- Batch C1/C2/D/E/F boundaries сохранены в issue/PR plan;
- tests, защищающие hardcoded timeline anchors и obsolete navigation, помечены на корректировку в соответствующем batch;
- implementation не требует изменения canonical data/API contracts;
- before-screenshots зафиксированы для трёх reference viewports и обязательных states, доступных в текущем runtime.
