# ARTEMIS — PRIORITIES v4.2

## Статус

- Тип: canonical active priorities document.
- Дата: 2026-07-16.
- Активный цикл: Architecture Atlas Product/Data Validation.

Приоритет получает только работа, которая подтверждает продуктовую ценность, исправляет semantic data truth, делает core loop публично доступным или предотвращает критическую деградацию.

## P0 — обязательные блокеры

### P0.1 Strategy and documentation truth

- зафиксировать Option A во всём canonical set;
- различать public/backend/pilot/future capabilities;
- обновить issues, противоречащие active scope;
- не расширять implementation до завершения documentation reset.

Owner docs:

- `PROJECT_TRUTH.md`;
- `PRODUCT_THESIS.md`;
- `ARTEMIS_PRODUCT_SCOPE.md`;
- `MVP_ARCHITECTURE_ATLAS.md`.

### P0.2 Canonical identity

- canonical public UUID;
- Airtable record ID только как `source_record_id`;
- migration aliases;
- invalid ID блокирует публикацию;
- Research Slice/Relation references используют canonical ID.

### P0.3 Sources, Media and Relations

- Source URL/role/review semantics;
- direct Media assets, license и attribution;
- canonical reviewed Relations table;
- Relation не выводится из same-layer/time heuristic;
- Similarity получает отдельную маркировку.

### P0.4 Semantic data gate

- проверка identity/source/media/relation/review semantics;
- пустые enabled Layers не публикуются;
- validation report отражает semantic warnings;
- source schema не обещает ETL write-back, если write-back отсутствует.

### P0.5 Public capability alignment

- выбрать public backend deployment contour;
- настроить API base;
- реализовать public Slice save/open/share E2E;
- скрыть или label Stories/Courses/auth surfaces, если backend недоступен;
- public UI не обещает internal-only capability.

## P1 — product proof

### P1.1 Architecture content pilot

- 100–150 Features;
- 15–20 populated Layers/styles/periods;
- 50+ reviewed Relations;
- source/media coverage;
- 3 Stories и reference Slices.

### P1.2 Compare and sourced detail

- compare 2–3 objects;
- provenance рядом с factual claims;
- relation/similarity separation;
- coordinate confidence отдельно от knowledge type.

### P1.3 Workspace refinement

- map without reserved empty rail;
- compact top dock и timeline;
- detail only when active;
- real-data temporal context вместо hardcoded anchors;
- consistent SVG icons;
- responsive staged behavior.

### P1.4 Research Slice loop

- create/save/list/open/update/delete;
- restore complete context;
- read-only share;
- public E2E and error states.

### P1.5 Product validation

- Round 0 truth check;
- Round 1 with 5–8 users;
- corrective pass;
- Round 2;
- explicit decision gate.

## P2 — maintainability in service of MVP

### P2.1 CSS ownership

- remove `css/main-screen.css` as competing override;
- separate tokens/base/layout/features;
- keep critical selector under one owner;
- preserve visual regression evidence.

### P2.2 JavaScript ownership

Extract from `js/ui.js` in controlled steps:

- timeline;
- detail;
- comparison;
- navigation;
- viewport/layout;
- research toolbar.

Framework rewrite is not a priority.

### P2.3 Browser regression coverage

- desktop 1440×900;
- tablet 1024×768;
- mobile 390×844;
- explore/compare/detail/slice/share states;
- tests synchronized with active UI spec.

## Maintenance guardrails

Разрешены независимо от phase:

- critical security fixes;
- data-loss fixes;
- broken deployment/release restoration;
- migration integrity fixes;
- dependency vulnerabilities;
- factual correction/removal.

Они не используются для скрытого расширения scope.

## Frozen backlog

Не является active priority:

- Courses depth/progression;
- AI generation;
- UGC/social expansion;
- general-domain entities;
- causal/counterfactual/predictive systems;
- gamification;
- native apps;
- enterprise/platform integrations;
- heavy multi-node scaling без evidence;
- marketing campaigns до validation.

## Порядок исполнения

1. P0.1 documentation truth.
2. P0.2–P0.4 data foundation.
3. P1.1 content pilot.
4. P0.5 public capability.
5. P1.2–P1.4 product loop and UX.
6. P2 maintainability required by the changed product surface.
7. P1.5 validation and decision.

## Правило завершения

Задача снимается с приоритета только при наличии:

- implemented artifact;
- relevant automated/manual evidence;
- synchronized owner docs;
- no known contradictory public claim;
- recorded follow-up or explicit no-follow-up decision.
