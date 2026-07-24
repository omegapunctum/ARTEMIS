# ARTEMIS — ARCHITECTURE ATLAS MVP

## Статус

- Тип: canonical MVP boundary document.
- Версия: 1.1.
- Дата: 2026-07-24.
- Зависит от: `PRODUCT_THESIS.md`, `PROJECT_TRUTH.md`, `DATA_DICTIONARY.md`.

## 1. Цель MVP

Доказать, что ARTEMIS помогает продвинутому студенту получить более качественное или более быстрое доказательное сравнение 2–3 архитектурных объектов, чем обычный каталог/список, а Research Slice сохраняет вопрос, evidence и вывод как возвращаемый результат работы.

MVP не обязан доказать универсальную платформу, Stories как отдельный продуктовый слой, Courses, UGC или AI generation.

## 2. Обязательные пользовательские возможности

### Explore

- фильтрация по периоду, направлению и региону;
- map + compact timeline;
- поиск объекта;
- карточка с датой, местом, направлением, описанием, источниками и media attribution.

### Compare

- выбор 2–3 объектов;
- сопоставление периода, региона, направления, признаков, sources и relations;
- явное разделение documented relation и computed similarity.

### Research Slice

- сформулировать вопрос и назвать исследование;
- сохранить выбранные объекты, evidence, заметку/вывод и uncertainty;
- сохранить Saved View: время, слои, фильтры, comparison state и viewport;
- повторно открыть;
- получить shareable read-only URL.

### Optional curated entry

- может помочь пользователю начать основной сценарий;
- должен вести в Compare → Evidence → Save;
- не является MVP exit requirement.
## 3. Content envelope

Для comparison-first Round 0 утверждён сокращённый pilot threshold:

- 30–40 active reviewed Features;
- 6–8 comparison cohorts минимум по 3 Features;
- 12–20 reviewed evidence-backed Relations;
- valid reviewed Source для каждого Feature;
- reviewed primary Media минимум для 90% Features;
- 0 пустых опубликованных Layers.

Исполнимый профиль и текущие gaps находятся в `data/content_profile.json`; решение и batching — в `docs/work/2026-07-21_VALIDATION_CORPUS_PILOT_v1.md`.

Ориентир зрелого корпуса остаётся прежним: 100–150 Features, 15–20 наполненных Layers/periods/styles, 50+ Relations и 5–10 reference Research Slices. Curated Stories оцениваются отдельно как onboarding-механизм. Этот ориентир не является входным барьером Round 0 и пересматривается после пользовательского decision gate.

## 4. Public runtime boundary

На публичном URL должны работать end-to-end:

- explore;
- compare;
- auth, если он нужен для save;
- save/list/open/delete Slice;
- shareable read-only Slice;
- фиксация вопроса, evidence, заметки/вывода и uncertainty в Slice.

Пункт навигации запрещено показывать как primary action, если соответствующий public flow не работает.

## 5. Frozen scope

До завершения validation замораживаются:

- Courses product depth;
- AI generation;
- open UGC expansion;
- gamification;
- multi-domain entity expansion;
- enterprise API;
- predictive/counterfactual layers;
- non-critical multi-node scaling.

Заморозка не требует удаления существующего backend-кода. Замороженные поверхности должны быть скрыты или явно помечены internal/future.

## 6. UX target

Основная навигация MVP:

1. Исследование.
2. Сравнение — contextual mode после выбора Features, а не пустой top-level route.
3. Сохранённые исследования — только при работающем public Slice backend.

Stories, Courses, AI, UGC и moderation не входят в primary public navigation. Curated entry может быть вторичным onboarding-маршрутом. Недоступная `BACKEND-AVAILABLE` или `FUTURE` capability скрывается, а не выглядит обычным рабочим разделом.

Главная иерархия:

1. mapped data;
2. selected object/detail;
3. active time and comparison context;
4. navigation and utilities.

Первый UX-момент ценности — sourced object comparison. Research Slice сохраняет результат и не является обязательным первым действием.

UI refinement выполняется по `docs/work/uiux/2026-07-16_UIUX_MAIN_SCREEN_REFINEMENT_SPEC_ACTIVE_v1_0.md`, но semantic product behavior определяется этим документом.

## 7. Engineering boundary

Допускается:

- owner-scoped CSS split;
- постепенное извлечение модулей из `js/ui.js`;
- browser regression tests;
- production backend configuration;
- semantic ETL checks.

Не допускается:

- одновременный framework rewrite;
- изменение canonical source без migration plan;
- UI-only simulation backend features;
- маркировка heuristic similarity как factual relation;
- scaling work без подтверждённой MVP dependency.

## 8. MVP exit criteria

- semantic data gate проходит;
- identity/source/media/relation contracts соблюдаются;
- public save/restore/share flow проходит E2E;
- сохранённое исследование содержит вопрос, evidence и пользовательский вывод, а не только UI state;
- desktop/tablet/mobile primary flows не имеют blocking defects;
- primary cohort из 5–8 целевых пользователей прошёл usability и cognitive validation;
- не менее 80% завершили основной сценарий;
- не менее 70% формулируют новое/уточнённое понимание и показывают supporting evidence;
- полевой follow-up подтверждает самостоятельный возврат, изменение или передачу Slice;
- map + time + compare протестированы против catalogue/list baseline;
- unresolved epistemic mislabeling отсутствует;
- принято отдельное решение: `ITERATE`, `EXPAND`, `NARROW` или `STOP/RETHINK`.
