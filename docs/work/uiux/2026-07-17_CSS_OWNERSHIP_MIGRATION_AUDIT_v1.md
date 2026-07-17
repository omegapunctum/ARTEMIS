# ARTEMIS — CSS OWNERSHIP MIGRATION AUDIT v1

## Статус

- Issue: `#288`.
- Статус: **AUDIT COMPLETE / BATCH C2 COMPACT TIMELINE IMPLEMENTED IN PR CANDIDATE**.
- Snapshot: 2026-07-17, `main` at `7971b7d`.
- Scope: CSS ownership, main Workspace geometry, responsive contract and migration safety.
- Runtime changes: Batch B foundation and Batch C1 shell geometry merged; Batch C2 compact timeline implemented in the current PR candidate.

Этот audit переводит согласованный map-first target в исполнимый CSS migration contract. Он не вводит новый visual direction и не заменяет `2026-07-16_UIUX_MAIN_SCREEN_REFINEMENT_SPEC_ACTIVE_v1_0.md`.

## 1. Verdict

`css/style.css` содержит 2793 строки. Это много для одного owner-файла, но само число строк не является главным дефектом. Фактическая проблема состоит из четырёх частей:

1. один файл одновременно владеет tokens, reset, primitives, shell, map, timeline, detail, product surfaces, auth, UGC, moderation, responsive и motion;
2. `css/main-screen.css` загружается позже и повторно определяет critical layout selectors;
3. текущие structural tests защищают часть superseded geometry;
4. JavaScript динамически записывает layout variables, поэтому CSS нельзя механически разрезать без согласованной ownership boundary.

Проекту нужен owner-scoped migration, а не косметическое сокращение строк и не массовое переименование классов.

## 2. Измеренный baseline

| Проверка | Результат |
|---|---:|
| `css/style.css` | 2793 строки / 56 529 bytes |
| `css/main-screen.css` | 183 строки / 4 152 bytes |
| CSS total | 2976 строк / 60 681 bytes |
| Семантические секции в `style.css` | 16 |
| Responsive breakpoints в `style.css` | 1080, 720, 420 px |
| Responsive breakpoints в `main-screen.css` | 1080, 720 px |
| `!important` в `style.css` | 15 |
| Stylesheet order | `style.css`, затем `main-screen.css` |

Текущие секции `style.css`:

| Секция | Текущие строки | Target owner |
|---|---:|---|
| Design tokens | 1–98 | `tokens.css` |
| Reset/global baseline | 99–260 | `base.css` |
| Form/control primitives | 261–459 | `components/controls.css` |
| Shared surfaces | 460–551 | `components/surfaces.css` |
| Application shell/workspace | 552–879 | `layout/shell.css` + `features/map.css` |
| Exploration rail/panels | 880–1166 | `features/map.css` + `features/research.css` |
| Timeline | 1167–1393 | `features/timeline.css` |
| Detail/epistemic content | 1394–1694 | `features/detail.css` |
| Slice/compare/story/course/live | 1695–1819 | `features/product-modes.css` |
| Status/offline/system feedback | 1820–2029 | `components/feedback.css` |
| Modal/authentication | 2030–2077 | `features/auth.css` |
| UGC editor | 2078–2215 | `features/ugc.css` |
| Moderation workspace | 2216–2333 | `features/moderation.css` |
| Legacy compatibility | 2334–2372 | temporary `compat.css` |
| Global responsive block | 2373–2734 | move beside each owner |
| Motion | 2735–2793 | `base.css` / owner-local motion |

Line ranges are audit evidence, not copy/paste instructions. Responsive and state rules move with the component they modify.

## 3. Competing ownership

`main-screen.css` claims to be limited to dock/grid ownership, but it overrides the same geometry already declared in `style.css` for these selector families:

- `#workspace-top-dock`;
- `#top-header`;
- `#research-context-bar`;
- `#workspace-main` and `#app-shell.has-right-detail #workspace-main`;
- `#explore-toolbar-shell`;
- `.map-tools-shell` and `.top-actions-cluster`;
- `#map-container`;
- `#detail-panel` and its open-shell variant;
- `#workspace-bottom-dock`;
- `#bottom-panel`.

The second stylesheet changes grid columns, positioning, borders, surfaces and responsive behavior. The resulting runtime therefore depends on load order rather than a single declared owner.

## 4. Target/runtime gaps verified

### 4.1 Structural rail remains active

Desktop `#workspace-main` still uses:

`grid-template-columns: var(--map-rail-width) minmax(0, 1fr)`.

`--map-rail-width` is 58 px on desktop and 52 px on tablet. This directly explains the empty left structural zone visible in the supplied screenshot and contradicts the full-width map target.

### 4.2 Outer frame remains decorative

`#workspace-frame` still owns border, radius and shadow around the complete workspace. `#workspace-top-dock` adds another bordered rounded surface. The screenshot therefore shows nested framing and more surface levels than the target hierarchy allows.

### 4.3 Top shell remains two persistent rows

The shell reserves `--top-header-height: 58px` plus `--workspace-strip-height: 48px`. Search is placed in a three-column header with a `42vw` middle column. This produces the large low-information top region called out in the visual review.

### 4.4 Timeline remains oversized and hardcoded

- desktop `--bottom-panel-height` is 152 px;
- `.timeline-track-wrap` is 78 px high;
- `TIMELINE_SEMANTIC_ANCHORS` is hardcoded in `js/ui.js`;
- CSS renders `.timeline-anchor-label` on desktop;
- a current test explicitly requires those labels and the 152 px dock.

The target requires a 72–88 px default dock and no hardcoded historical labels.

### 4.5 Responsive ownership is split

The same 1080/720 modes are implemented in both stylesheets. JavaScript independently selects `desktop/tablet/mobile` and writes measured values into:

- `--top-header-height`;
- `--workspace-strip-height`;
- `--bottom-panel-height`.

The migration must treat CSS breakpoints, JS viewport mode and measured variables as one contract.

## 5. Test drift

Current tests are useful safety nets but include superseded assertions:

- `tests/test_style_contract.py` requires `--map-rail-width`;
- it requires both `style.css` and `main-screen.css` in the service-worker precache;
- `tests/test_main_workspace_ux_contract.py` requires desktop semantic anchor labels;
- release-check fixtures assume both stylesheet links.

These assertions must be replaced in the same implementation batch that changes the contract. Removing tests before the runtime change is forbidden.

Target assertions:

- no `--map-rail-width` in active layout ownership;
- no `main-screen.css` reference in `index.html` or `sw.js` after retirement;
- no `TIMELINE_SEMANTIC_ANCHORS` render path;
- one owner for every critical selector family;
- 1080/720 CSS modes remain aligned with JavaScript;
- compact timeline height contract is enforced;
- checked stylesheets are substantive, balanced and present in the PWA cache.

## 6. Target CSS ownership

The final structure should stay small enough to understand and large enough to express ownership:

```text
css/
├── tokens.css
├── base.css
├── components/
│   ├── controls.css
│   ├── surfaces.css
│   └── feedback.css
├── layout/
│   └── shell.css
└── features/
    ├── map.css
    ├── timeline.css
    ├── detail.css
    ├── research.css
    ├── product-modes.css
    ├── auth.css
    ├── ugc.css
    └── moderation.css
```

This is a target ownership map, not a requirement to create every file in one commit. A file above roughly 700 lines requires an ownership review, but line count is a review signal rather than a hard quality metric.

### Ownership rules

1. A critical selector family has one file owner.
2. Responsive rules live beside the selector owner.
3. Feature files may consume tokens but may not redefine global tokens.
4. State modifiers remain with their base component.
5. `compat.css`, if temporarily required, contains only documented legacy aliases and is removed at the end of migration.
6. Load order is explicit in `index.html`; accidental late overrides are forbidden.
7. No new `!important` may be added to solve ownership conflicts.

### Critical selector owner matrix

| Selector family | Owner |
|---|---|
| `:root`, design tokens | `tokens.css` |
| `html`, `body`, reset, accessibility baseline, reduced motion | `base.css` |
| shared buttons/fields | `components/controls.css` |
| panels/cards/badges | `components/surfaces.css` |
| loading/error/offline/toasts | `components/feedback.css` |
| `#app-shell`, `#workspace-frame`, top/main/bottom dock geometry | `layout/shell.css` |
| header/nav/search/context geometry | `layout/shell.css` |
| `#map-container`, `#map`, MapLibre controls, map tool overlay | `features/map.css` |
| timeline dock internals and modes | `features/timeline.css` |
| detail inspector/sheet and epistemic blocks | `features/detail.css` |
| research panels/layers/filters | `features/research.css` |
| Slice/Compare/Story/Course/Live | `features/product-modes.css` |
| auth/modal | `features/auth.css` |
| UGC | `features/ugc.css` |
| moderation | `features/moderation.css` |

## 7. Migration batches

### Batch A — contract and executable guardrails

- merge this audit;
- update tests to express target ownership only when corresponding runtime changes are included;
- add a selector-ownership contract that fails when a critical family appears in multiple owner files.

### Batch B — no-visual-change extraction

- extract tokens, base and shared components;
- preserve computed style and stylesheet order;
- update `index.html`, `sw.js`, release fixtures and style tests atomically;
- keep current feature geometry unchanged.

### Batch C — map-first shell geometry

- remove the desktop structural rail and `--map-rail-width`;
- move research controls to a compact map overlay;
- remove decorative outer-frame treatment;
- collapse top shell/context into the agreed compact hierarchy;
- preserve on-demand right inspector and mobile bottom sheet;
- call map resize after geometry-changing transitions.

### Batch D — compact time system

- remove `TIMELINE_SEMANTIC_ANCHORS` and its renderer;
- remove anchor DOM/CSS/test ownership;
- reduce default desktop timeline dock to 72–88 px;
- keep range/point modes, handles, keyboard use and selected period.

### Batch E — feature extraction and override retirement

- move detail/research/product/auth/UGC/moderation rules to owners;
- absorb accepted rules from `main-screen.css` into owners;
- remove `main-screen.css` from runtime, PWA cache and tests;
- retire the monolithic `style.css` after no active selectors remain.

### Batch F — visual and interaction validation

- compare screenshots at 2048×1152, 1440×900, 1024×768 and 390×844;
- run load → search → time → research tools → object → detail open/close;
- verify map/control overlap, safe areas, focus order and no horizontal overflow;
- record residual visual issues separately; do not reopen ownership by late override.

## 8. Recovery

- each batch is independently reviewable and may be reverted without reverting data work;
- no batch mixes CSS migration with Airtable/API changes;
- old files are deleted only after their selectors have an owner and runtime tests pass;
- a failed visual batch reverts its owner files and matching tests together;
- `main-screen.css` is never retained as an emergency catch-all after final retirement.

## 9. Documentation-gate acceptance

- [x] current file sizes and section boundaries measured;
- [x] competing critical selectors identified;
- [x] screenshot symptoms mapped to runtime rules;
- [x] CSS/JS/test coupling identified;
- [x] target owner matrix defined;
- [x] migration batches and recovery defined;
- [x] owner-scoped runtime foundation modules created;
- [x] map-first shell geometry implemented;
- [x] compact timeline implemented;
- [ ] `main-screen.css` retired;
- [ ] desktop/tablet/mobile visual regression accepted.

## 10. Batch B execution evidence

Foundation extraction выполнен без изменения cascade или geometry:

| Owner file | Lines after extraction |
|---|---:|
| `css/tokens.css` | 98 |
| `css/base.css` | 162 |
| `css/components/controls.css` | 199 |
| `css/components/surfaces.css` | 92 |
| transitional `css/style.css` | 2248 |
| transitional `css/main-screen.css` | 183, unchanged |

Runtime load order закреплён в `index.html`: tokens → base → controls → surfaces → transitional feature/layout rules → transitional main-screen override. Все шесть файлов включены в GitHub Pages artifact и service-worker precache.

До изменения заголовочного комментария конкатенация четырёх owner-файлов и оставшейся части `style.css` побайтно совпала с pre-extraction `style.css`: SHA-256 `511c2608c24f041f4af9a02406f82a4ab8d8303502d519ad44a5caa16041cfd2`.

Batch B намеренно не меняет structural rail, timeline height, semantic anchors или `main-screen.css`. Эти изменения принадлежат следующим independently reviewable batches.

## 11. Batch C1 execution evidence

Map-first shell реализован отдельным runtime patch без изменения timeline semantics, object comparison или canonical data/API contracts:

- public navigation сокращена до `Исследование`, capability-gated `Истории` и `Сохранённые исследования`;
- decorative outer gutter/frame удалены;
- structural desktop rail и `--map-rail-width` удалены, инструменты перенесены в map overlay;
- отдельная context strip встроена в единый компактный top shell;
- карта занимает всю доступную ширину при закрытом inspector;
- при смене dock-геометрии inspector карта получает отложенный `resize()` после layout transition;
- onboarding начинает путь с объекта на карте, а недоступные backend capabilities не обещаются в public shell.

Проверки PR candidate:

- focused UI/style/service-worker contracts: `15 passed`;
- полный test suite: `275 passed, 3 skipped, 10 subtests passed`;
- `node --check js/ui.js` и `node --check js/map.js`;
- HTML parser smoke и `git diff --check`.

Batch C1 merged in PR `#299`. Остаются отдельными batches: D object comparison, E sourced detail и F responsive/accessibility visual acceptance.

## 12. Batch C2 execution evidence

Compact timeline реализован отдельным runtime patch без изменения map shell, object comparison или data/API contracts:

- desktop/tablet dock contract установлен на `84 px`, mobile — на `80 px`;
- track сокращён с `78 px` до `24 px`, сохраняя два handles и hit areas range inputs;
- `TIMELINE_SEMANTIC_ANCHORS`, `renderTimelineAxis`, axis DOM и весь anchor CSS удалены;
- point/range modes, keyboard-capable native range inputs, pointer drag, selected-period capsule и filter commit сохранены;
- initial HTML state синхронизирован с runtime default `range`, чтобы исключить ложный point flash;
- service-worker cache и structural contracts обновлены атомарно.

Visual screenshot acceptance остаётся в Batch F: cloud browser не открывает локальный runtime, а C2 не создаёт внешний preview environment.

Проверки PR candidate:

- focused UI/style/service-worker contracts: `15 passed`;
- полный test suite: `275 passed, 3 skipped, 10 subtests passed`;
- release check: все обязательные sections `PASS`;
- `node --check js/ui.js`, `node --check js/map.js`, HTML parser smoke и `git diff --check`.
