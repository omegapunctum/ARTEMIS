# 2026-07-16_UIUX_MAIN_SCREEN_REFINEMENT_SPEC_ACTIVE_v1_0

## Статус документа

- Статус: **ACTIVE / IMPLEMENTATION-READY WORKING SPEC**.
- Область: главный экран / Workspace Core.
- Дата фиксации: 2026-07-16.
- Роль: track-specific target layer для компактного map-first refinement.
- Rollout owner: `docs/work/ARTEMIS_UI_UX_IMPLEMENTATION_PLAN_v1_0.md`.
- UX owner: `docs/work/uiux/ARTEMIS_UI_UX_SYSTEM.md`.
- Component owner: `docs/work/uiux/ARTEMIS_UI_UX_COMPONENT_MAP.md`.
- Visual owner: `docs/work/uiux/ARTEMIS_UI_UX_VISUAL_SYSTEM.md`.

Этот документ не создаёт новую продуктовую архитектуру и не заменяет owner-docs. Он фиксирует согласованный target для следующего UI patch cycle.

## 1. Причина refinement

Текущий desktop runtime сохраняет функциональный Workspace Core, но визуально расходует слишком много пространства на chrome:

- отдельный зарезервированный rail слева уменьшает map canvas и создаёт пустую вертикальную полосу;
- nested frame + top-dock borders создают лишнее декоративное обрамление;
- header и отдельная context strip занимают много высоты и оставляют растянутую пустую середину;
- timeline постоянно резервирует большую нижнюю область;
- semantic timeline anchors заданы вручную и визуально перегружают основной range-control;
- Unicode/emoji icons не образуют единую визуальную систему;
- `css/style.css` и поздний override `css/main-screen.css` имеют конкурирующих владельцев critical layout selectors.

Refinement должен устранить эти причины, не меняя data/API contracts и не ослабляя map/time/detail core.

## 2. Target layout contract

### 2.1 App shell

- Workspace занимает доступный viewport без декоративного внешнего gutter.
- У главной сцены нет nested rounded frame.
- Граница допускается только как функциональный divider между смысловыми зонами.
- Map canvas остаётся главным визуальным объектом.

### 2.2 Top shell and slice context

- Desktop target: один компактный top dock.
- Целевая высота primary header: 56–64 px.
- Отдельная постоянно видимая 48 px context strip не является обязательной.
- Slice title/status, period/layers/objects metadata и actions собираются в compact contextual group без растянутой пустой центральной колонки.
- Search получает ограниченную полезную ширину; его размер не должен искусственно создавать симметричные пустоты.
- Secondary actions раскрываются через progressive disclosure.

### 2.3 Map tools

- Desktop map workspace использует одну основную grid-column.
- Отдельный `--map-rail-width` не резервирует ширину рядом с картой.
- Research tools размещаются как compact overlay поверх карты.
- Custom tools и MapLibre navigation controls не перекрываются и визуально читаются как одна control system.
- Overlay не блокирует spatial reading и не создаёт пустой structural column.

### 2.4 Detail panel

- Desktop detail остаётся right-side dock/inspector только при открытом объекте.
- Закрытый detail не резервирует ширину.
- На tablet detail может быть overlay; на mobile — bottom sheet.
- Открытие/закрытие detail не должно ломать timeline и map resize.

### 2.5 Timeline

- Timeline остаётся load-bearing time control, но становится компактнее.
- Целевая desktop высота dock: 72–88 px в обычном состоянии.
- Постоянные вручную заданные semantic anchors и их подписи удаляются из основного runtime UI.
- Range track, handles, point/range mode и active period остаются.
- Дополнительный temporal context допускается только из реальных данных или по явному запросу пользователя.
- Timeline может получить expanded state позже, но compact state является default.

### 2.6 Icons

- Unicode glyphs и emoji в primary controls заменяются согласованным SVG icon set.
- Базовый размер: 18–20 px; hit area не менее 40×40 px, целевой минимум 44×44 px для touch.
- Icon-only actions сохраняют accessible name, tooltip/title и видимый focus state.

## 3. Visual hierarchy

1. Map and mapped data.
2. Selected object/detail.
3. Active time range and slice context.
4. Navigation and utility controls.

Правила:

- не добавлять панели только для заполнения свободного места;
- не использовать рамку как основной способ отделить каждый блок;
- уменьшить количество одновременно видимых surface levels;
- action accent использовать только для active/selected/primary states;
- muted controls не должны конкурировать с map markers и selected state.

## 4. CSS architecture contract

Текущий размер CSS сам по себе не является дефектом. Дефектом является отсутствие одного владельца для layout rules.

Следующий implementation cycle должен:

- прекратить использование `css/main-screen.css` как patch-layer поверх `css/style.css`;
- перенести принятые правила к владельцам компонентов;
- не оставлять один critical selector в нескольких feature files без явной cascade policy;
- сохранить design tokens отдельно от layout и feature rules;
- удалить obsolete/legacy rules только после проверки runtime usage;
- держать responsive rules рядом с component owner либо в явно определённом responsive layer.

Рекомендуемое разбиение:

- `css/tokens.css`
- `css/base.css`
- `css/components.css`
- `css/layout/shell.css`
- `css/features/map.css`
- `css/features/timeline.css`
- `css/features/detail.css`
- `css/features/research.css`
- `css/features/auth.css`
- `css/features/ugc.css`
- `css/features/moderation.css`

Точное число файлов может быть скорректировано при implementation audit. Запрещено дробление без удаления competing overrides.

## 5. JavaScript ownership

Layout refinement не должен продолжать рост `js/ui.js` как единственного UI owner.

Минимальные extraction candidates:

- timeline rendering and interaction;
- viewport/layout synchronization;
- top navigation and overflow;
- research toolbar/panels;
- detail panel docking.

Удаление semantic timeline anchors должно включать cleanup констант и render-path, а не только `display: none`.

## 6. Scope boundaries

В scope:

- shell geometry;
- map tools placement;
- compact timeline;
- icon consistency;
- CSS owner cleanup;
- responsive preservation;
- visual regression/smoke coverage.

Не в scope:

- изменение canonical map source;
- API/data-contract changes;
- новый Story/Course/AI UX;
- redesign detail content semantics;
- новые product routes;
- изменение slice persistence contract.

## 7. Implementation order

1. Зафиксировать documentation contract.
2. Удалить structural desktop rail и перенести tools в overlay.
3. Упростить outer frame и top dock.
4. Сжать timeline и удалить semantic anchors.
5. Унифицировать icons.
6. Разнести CSS по владельцам и удалить late override layer.
7. Проверить desktop/tablet/mobile layout and interactions.
8. Выполнить visual regression review и runtime smoke.

## 8. Acceptance criteria

### Desktop

- Map начинается у левой границы workspace без пустого зарезервированного rail.
- Нет nested outer frame вокруг всей map-first сцены.
- Top controls не создают большую пустую центральную полосу.
- Timeline default height находится в target 72–88 px.
- На timeline нет вручную заданных исторических подписей.
- MapLibre controls, custom tools и overlays не перекрываются.
- Detail при закрытии не резервирует место.

### Tablet and mobile

- При ширине до 1080 px tools остаются overlay и не создают отдельную колонку.
- При ширине до 720 px detail работает как bottom sheet.
- Timeline остаётся доступным и не перекрывается sheet без interaction lock.
- Navigation collapses without horizontal overflow.
- Safe-area insets сохраняются.

### Engineering

- Нет изменений data/API behavior.
- Нет console errors в primary flow.
- Map вызывает resize после geometry-changing transitions.
- Keyboard focus order остаётся предсказуемым.
- Critical layout selectors имеют одного явного owner.
- `css/main-screen.css` удалён либо перестаёт быть competing override layer.

## 9. Validation baseline

- Manual: load → search → set time point/range → open research tools → select object → open/close detail.
- Viewports: 2048×1152, 1440×900, 1024×768, 390×844.
- States: ready, filtered, no results, detail open, panel open, mobile sheet.
- Compare before/after screenshots for map area, top dock, tool placement and timeline height.
