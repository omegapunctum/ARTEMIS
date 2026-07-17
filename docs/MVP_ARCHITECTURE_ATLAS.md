# ARTEMIS — ARCHITECTURE ATLAS MVP

## Статус

- Тип: canonical MVP boundary document.
- Версия: 1.0.
- Дата: 2026-07-16.
- Зависит от: `PRODUCT_THESIS.md`, `PROJECT_TRUTH.md`, `DATA_DICTIONARY.md`.

## 1. Цель MVP

Доказать, что ARTEMIS помогает исследовать историю архитектуры через пространственно-временное сравнение и прозрачные источники, а Research Slice создаёт возвращаемый результат работы.

MVP не обязан доказать универсальную платформу, Courses, UGC или AI generation.

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

- создать и назвать срез;
- сохранить выбранные объекты, время, слои, viewport и notes;
- повторно открыть;
- получить shareable read-only URL.

### Curated Story

- минимум три редакционных маршрута;
- каждый шаг связывает текст, карту, timeline, объекты и источники;
- Story строится поверх проверенных объектов и relations.

## 3. Минимальный content envelope

Перед product validation corpus должен содержать:

- 100–150 active Features;
- 15–20 непустых Layers/periods/styles;
- 50+ reviewed Relations;
- минимум один valid Source для каждого Feature;
- минимум одно корректно атрибутированное Media для большей части ключевых Features;
- 3 curated Stories;
- 5–10 reference Research Slices для smoke и демонстрации.

Числа являются validation threshold, а не обещанием окончательного масштаба.

## 4. Public runtime boundary

На публичном URL должны работать end-to-end:

- explore;
- compare;
- auth, если он нужен для save;
- save/list/open/delete Slice;
- shareable read-only Slice;
- curated Stories.

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
4. Истории — только при наличии curated public Stories.

Courses, AI, UGC и moderation не входят в primary public navigation. Недоступная `BACKEND-AVAILABLE` или `FUTURE` capability скрывается, а не выглядит обычным рабочим разделом.

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
- desktop/tablet/mobile primary flows не имеют blocking defects;
- 5–8 целевых пользователей прошли validation;
- не менее 80% завершили основной сценарий;
- unresolved epistemic mislabeling отсутствует;
- принято отдельное решение: iterate, expand или stop.
