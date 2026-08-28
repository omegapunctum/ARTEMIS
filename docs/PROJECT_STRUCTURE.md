# ARTEMIS — СТРУКТУРА ПРОЕКТА v4.4

Статус: updated canonical project structure document.
Назначение документа: фиксировать canonical структуру репозитория, архитектурные boundaries, documentation system и место концептуального основания проекта в doc-system.
Дата обновления: 2026-08-28.

---

## 1. ПРИНЦИП СТРУКТУРЫ

Структура проекта должна отвечать на три вопроса:
1. Где находится production/runtime код и какие presentation runtimes зарегистрированы явно.
2. Где находятся canonical публичные данные и где заканчивается текущая render projection.
3. Где находится документация и какой у неё статус.

К технической структуре добавляется жёсткая документационная иерархия:
- canonical source-of-truth layer;
- working layer (`docs/work/*`);
- audit layer (`docs/audits/*`);
- historical reference layer (`docs/archive/*`, `docs/reference/*`).

Это обязательная часть структуры проекта, а не вспомогательная заметка.

Архитектурный инвариант для renderer expansion:

- canonical domain/world-model semantics имеют одного владельца и не дублируются по renderer-веткам;
- несколько явно зарегистрированных presentation runtimes допустимы, если они используют общий World Model / Explorer State / projection boundary;
- новый renderer не может создавать скрытый backend, отдельную historical truth или competing data core;
- experimental runtime может попасть в production artifact только через отдельно зарегистрированный, явно маркированный public R&D preview; случайная публикация запрещена.

---

## 2. КОРЕНЬ ПРОЕКТА

```text
/
├── .github/
├── app/
├── css/
├── data/
├── docs/
├── fixtures/
├── icons/
├── js/
├── scripts/
├── tests/
├── AGENTS.md
├── index.html
├── manifest.json
├── pytest.ini
├── README.md
├── requirements.txt
├── sw.js
└── ...
```

### Назначение верхнего уровня

| Путь | Назначение | Статус |
|---|---|---|
| `.github/` | workflows, CI/CD, release/publish automation | системный |
| `app/` | frozen backend compatibility runtime | compatibility |
| `css/` | Architecture Atlas compatibility styles | compatibility |
| `data/` | Architecture Atlas compatibility data + export diagnostics | compatibility |
| `docs/` | canonical / working / audits / archive / reference documentation system | основной |
| `fixtures/` | versioned executable contract fixtures; not public/runtime data | validation |
| `icons/` | PWA assets | основной |
| `js/` | Architecture Atlas compatibility frontend modules | compatibility |
| `scripts/` | ETL, import/export, audit, release and contract checks | основной |
| `tests/` | automated checks | основной |
| `AGENTS.md` | единый repository entrypoint для агентов; маршрутизирует к canonical owners | operational |
| `README.md` | корневой entrypoint документации | canonical |
| `sw.js` | service worker | основной |
| `manifest.json` | PWA manifest | основной |

Source root retains the Architecture Atlas compatibility implementation. The Pages artifact maps it to `/atlas/`; public `/` is generated from `scripts/globe_spike/root-index.html`, and `/globe/` is generated from the shared semantic path.

Дополнение по release/workflow layer:
- structural and semantic release discipline закреплён исполнимыми checks в workflow-слое (`.github/workflows/*`), `scripts/release_check.py` и `scripts/semantic_data_gate.py`;
- renderer-neutral Explorer State contract under #340 has its own executable validator/test contour and remains validation/R&D evidence rather than public runtime data;
- `scripts/release_check.py` остаётся canonical executable release/readiness entrypoint;
- точные enforcement points должны определяться по текущим workflow files, а не по упрощённой формулировке в одном summary-документе;
- workflow-слой не заменяет полный regression suite и не должен описываться как его эквивалент.

---

## 3. CANONICAL ENTRYPOINTS

| Слой | Entry point |
|---|---|
| Public ARTEMIS Core landing | generated `/` from `scripts/globe_spike/root-index.html` |
| Primary Leonardo Globe research prototype | generated `/globe/` via `.github/workflows/pages.yml` and `scripts/build_globe_spike.py --public-preview` |
| Architecture Atlas compatibility frontend | source `index.html`, deployed at `/atlas/` |
| Backend | `app/main.py` |
| ETL | `scripts/export_airtable.py` |
| Release check | `scripts/release_check.py` |
| World-model fixture validation | `scripts/validate_world_model_fixtures.py` |
| Uncertainty-semantics validation | `scripts/validate_uncertainty_fixtures.py` |
| Explorer-state fixture validation | `scripts/validate_explorer_state_fixtures.py` |
| Uncertainty-semantics owner | `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md` |
| Current public 2D map projection | `data/features.geojson` |
| Agent instructions | `AGENTS.md` |
| Root documentation entry | `README.md` |

Правило:
- canonical semantic/domain owner для одной ответственности должен быть один;
- backend, ETL, release-check и documentation registries не получают competing entrypoints;
- presentation runtimes являются отдельным классом: несколько renderer entrypoints допустимы только после явной регистрации и при общей domain/state/projection семантике;
- наличие второго renderer не разрешает второй World Model, второй historical source of truth или второй backend;
- generated Core landing is the default public entrypoint;
- generated `/globe/` is primary but remains explicitly non-product-validated;
- source `index.html` is deployed under `/atlas/` as compatibility-only;
- Explorer State validator is a validation entrypoint, not a frontend/backend runtime entrypoint;
- working Explorer State ownership remains in `docs/work/README.md`; it is not promoted into the canonical owner registry by this structure document;
- legacy-слои не могут становиться скрытым альтернативным runtime.

---

## 4. FRONTEND СЛОЙ

Compatibility Architecture Atlas source tree (published under `/atlas/`):

```text
index.html
css/
├── tokens.css
├── base.css
├── components/
│   ├── controls.css
│   └── surfaces.css
├── style.css
└── main-screen.css

js/
├── auth.js
├── courses_runtime.js
├── data.js
├── explain_context.js
├── map.js
├── pwa.js
├── research_slices.js
├── safe-dom.js
├── state.js
├── stories.js
├── ugc.js
├── ui.js
├── ui.moderation.js
├── ui.ugc.js
├── uploads.js
└── ux.js
```

Правила текущего public contour:
- frontend остаётся vanilla JS без нового framework layer;
- current 2D карта читает canonical public data только из `data/*`;
- `/api/map/feed` не становится альтернативным public data source;
- безопасный DOM-rendering обязателен для пользовательского контента;
- PWA и UX-hardenings не должны подменять архитектурные boundaries;
- `css/tokens.css`, `css/base.css` и `css/components/*` являются первой owner-scoped foundation extraction без изменения visual contract;
- `css/style.css` временно владеет оставшимися layout/feature/legacy rules до следующих migration batches;
- `css/main-screen.css` является текущим transitional override layer, а не целевой архитектурой;
- в Architecture Atlas UX cycle актуальные правила должны быть перенесены к owner-scoped modules, после чего competing override удаляется;
- owner-scoped split должен разделять tokens/base/layout/features и не создавать параллельные visual systems;
- measured baseline, selector-owner matrix, staged target tree and recovery rules зафиксированы в `docs/work/uiux/2026-07-17_CSS_OWNERSHIP_MIGRATION_AUDIT_v1.md`.

Renderer expansion rule:
- Globe/future renderer code должен находиться за explicit experimental/runtime boundary; Pages получает только deterministic generated preview;
- renderer-neutral selected time/layers/object state не должен принадлежать MapLibre или Globe engine objects;
- render adapters получают World Model / World Slice data через явную projection boundary;
- engine-specific camera, GPU resources, tile caches, hover/picking buffers и visual transitions остаются renderer-local;
- нельзя переписывать current frontend framework/layout только ради появления второго renderer без отдельного evidence-backed architecture decision;
- target repository split (`apps/*`, shared packages или другой layout) определяется #345, а не предполагается этим документом заранее.

Working renderer architecture record: `docs/work/2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md`.
Working Explorer State contract: `docs/work/2026-08-08_EXPLORER_STATE_CONTRACT_v1.md`.

---

## 5. BACKEND СЛОЙ

```text
app/
├── main.py
├── routes/
├── auth/
├── courses/
├── drafts/
├── explain_context/
├── moderation/
├── research_slices/
├── security/
├── stories/
├── uploads/
├── observability.py
├── map_feed_schemas.py
└── url_validation.py
```

Правила:
- `app/` — единственный backend runtime;
- legacy root package `api/` удалён; новый competing backend package запрещён;
- 3D Globe/renderer expansion само по себе не является основанием для второго backend runtime;
- env/runtime configuration закрепляется только за `app.main:app`;
- session backend deployment policy: memory-backed refresh sessions допустимы только для development/testing/local baseline (включая short aliases `dev`/`test`); non-development/testing/local deployments обязаны использовать Redis-backed session store (`AUTH_SESSION_BACKEND=redis` + `REDIS_URL`) с fail-fast на misconfiguration;
- Redis-backed refresh-session consume в текущем baseline трактуется как atomic one-time operation (`GETDEL` или atomic fallback path), а legacy non-atomic `get+delete` не должен считаться допустимым baseline-поведением;
- rate limiting в текущем baseline остаётся process-local/in-memory; `X-Forwarded-For` для извлечения client IP в rate-limit key trusted только от configured trusted proxy peers (`ARTEMIS_TRUSTED_PROXIES` / `TRUSTED_PROXY_IPS`, exact IP + CIDR), иначе используется peer IP (`request.client.host`);
- текущий persistence baseline использует shared SQLAlchemy scope: `app.auth.service` задаёт общий `engine`/`Base`, который переиспользуется в `drafts` / `research_slices` / `stories` / `courses`;
- current mutable ResearchSlice sharing хранит только SHA-256 capability token в `research_slices.share_token_hash`; raw token существует только in owner response and URL fragment, public response является read-only/no-store и не раскрывает owner identity; share reads the mutable row and is not revision-pinned;
- migration/bootstrap path текущего baseline выполняется при runtime startup через `init_db()` вызовы в `app.main.py`, а не через отдельный внешний migration orchestrator;
- versioned migrations в backend опираются на общую `schema_version` discipline как baseline-механизм и не должны трактоваться как fully hardened production migration platform;
- общая `schema_version` таблица рассматривается как shared baseline coordination mechanism для всех runtime-доменов, а не как изолированный per-service журнал;
- migration version ids в общей `schema_version` модели должны оставаться глобально уникальными и domain-coordinated между `auth` / `drafts` / `research_slices` / `stories` / `courses`;
- новые migration steps нельзя добавлять произвольно: перед добавлением версии обязателен локальный check текущего version space в общей `schema_version` discipline, чтобы избежать ручного drift/коллизий;
- startup owner gate текущего baseline: migration apply path выполняется только при `MIGRATION_STARTUP_ROLE=owner`; `MIGRATION_STARTUP_ROLE=non-owner` выполняет обычный runtime boot без apply;
- вне development/testing/local aliases `MIGRATION_STARTUP_ROLE` должен быть явно задан (`owner`/`non-owner`), иначе startup трактуется как fail-fast config error;
- execution policy текущего baseline: migration/apply path выполняется в controlled single-writer режиме (явный owner запуска), а не как некоординированный конкурентный first-boot apply из нескольких инстансов одновременно;
- рекомендуемый baseline порядок выполнения: preflight-only discipline check → migration/apply path (`init_db()` startup sequence) → обычный runtime boot;
- concurrent first-boot apply считается нарушением baseline guardrail и не должен нормализоваться как допустимая operational практика;
- ошибка preflight трактуется как stop-before-apply event; ошибка startup apply трактуется как fail-fast operational event, а не как silent retry semantics внутри текущего baseline;
- moderation path не является direct publish path для public dataset;
- текущий upload surface должен описываться как runtime split: API-приём файлов идёт через `/api/uploads` и `/api/uploads/image`, а публичная выдача загруженных файлов идёт через статический `/uploads/*` mount;
- документация не должна описывать несуществующий отдельный runtime route `GET /api/uploads/{filename}`, если фактическая раздача файлов закреплена за static mount.

---

## 6. DATA LAYER

```text
data/
├── content_profile.json
├── courses.json
├── export_errors.log
├── export_meta.json
├── features.geojson
├── features.json
├── id_aliases.json
├── layers.json
├── media.json
├── relations.json
├── rejected.json
├── sources.json
└── validation_report.json
```

Правила:
- `data/features.geojson` — canonical current public 2D map projection/source;
- Point-only limitations of `data/features.geojson` do not define the Foundation v3 World Model spatial ontology;
- `features.json` не является public source of truth;
- `data/id_aliases.json` — versioned compatibility map from legacy/source IDs to canonical UUID v4;
- raw / validated / rejected слои не смешиваются;
- checked-in data artifacts должны использовать тот же contract, что и release gate;
- renderer-specific payloads for future 2D/3D runtimes are derived projections and cannot become independent historical truth without an explicit contract change;
- terrain/elevation/imagery/tile assets belong to a separate geospatial asset boundary and do not silently enter historical World Model semantics;
- `content_profile.json` schema version 1 — детерминированный snapshot comparison-pilot readiness; генерируется из public artifacts и проверяется на drift;
- `validation_report.json` schema version 2 — обязательное release evidence с разделёнными blocking errors и budgeted warnings; это не content source-of-truth, но semantic release gate опирается на него напрямую;
- `export_errors.log` остаётся человекочитаемой JSONL-проекцией тех же diagnostics и не создаёт отдельную validation truth.

Canonical details remain in `docs/DATA_CONTRACT.md`.

---

## 7. SCRIPTS / ETL / CHECKS

```text
scripts/
├── audit_airtable.py
├── export_airtable.py
├── import_features.py
├── release_check.py
├── semantic_data_gate.py
├── validate_world_model_fixtures.py
├── validate_uncertainty_fixtures.py
└── validate_explorer_state_fixtures.py
```

```text
tests/
├── test_explorer_state_fixtures.py
└── ...
```

```text
fixtures/
├── explorer_state/
│   └── v1/
│       ├── README.md
│       ├── schema.json
│       └── state-1504-local-global.json
└── world_model/
    ├── v1/
    │   ├── compatibility/
    │   ├── sources/
    │   ├── README.md
    │   ├── coverage_manifest.json
    │   ├── package.json
    │   ├── review_registry.json
    │   └── schema.json
    └── uncertainty/
        └── v1/
            ├── compatibility/
            ├── README.md
            ├── package.json
            ├── review_registry.json
            └── schema.json
```

Правила:
- `fixtures/` хранит versioned executable contract evidence, не public `data/*` и не runtime schema;
- `fixtures/explorer_state/v1` pins a renderer-neutral query/selection state to the reviewed synthetic World Model package and does not duplicate World Model facts;
- synthetic fixtures must be visibly marked and cannot support historical capability claims;
- compatibility projections expose losses and never invent missing evidence/precision;
- additive contract extensions reference the reviewed base and do not rewrite a READY package;
- `scripts/validate_explorer_state_fixtures.py` owns structural + cross-reference checks for #340 and must reject renderer-owned state such as engine zoom/pitch/camera objects;
- `scripts/` отвечают за ETL, import/export, checks, preparation;
- `tests/` отвечают за автоматическую проверку контрактов и регрессий;
- cross-renderer semantic parity, when a second renderer exists, belongs to executable tests and must be independent from screenshot/visual regression;
- release discipline не должна жить только в Markdown без исполнимой проверки.

---

## 8. НОВАЯ СИСТЕМА ДОКУМЕНТАЦИИ

Цель:
Перевести документацию ARTEMIS из разросшегося набора файлов в управляемую систему.

### 8.1 Root-level canonical document

```text
README.md
```

Назначение:
- главный вход в проект;
- краткое описание продукта, стека, запуска и ссылок на canonical docs;
- не заменяет архитектурные и release-документы, но направляет к ним.

### 8.2 Canonical docs

Полный canonical set и назначение каждого owner document зарегистрированы только в `FOUNDATION_INDEX.md`.

Правило:
- `FOUNDATION_INDEX.md` является единственным canonical registry;
- foundation-layer (`FOUNDATION_INDEX.md`, `ARTEMIS_CONCEPT.md`, `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `RESEARCH_SLICE_CONTRACT.md`, `EPISTEMIC_CONTRACT.md`, `ENTITY_MODEL.md`, `CONTENT_GOVERNANCE.md`, `AI_POLICY.md`) является обязательным контуром для product/data/UI/AI решений;
- conceptual foundation не может существовать только как внешний черновик;
- упоминание старого canonical-набора (`ARCHITECTURE.md`, `RELEASE_SYSTEM.md`, `ROADMAP.md`) считается documentation drift, если эти файлы не являются реальными действующими canonical entrypoints.

### 8.3 Working docs

Текущий lifecycle registry: `docs/work/README.md`.

Назначение:
- рабочие документы текущего цикла;
- допускают быстрые изменения;
- не считаются canonical по умолчанию;
- active renderer architecture/Explorer State records must be registered here and cannot override canonical model/data/truth owners;
- UI/UX working specs физически размещаются в `docs/work/uiux/`, а не в canonical root `docs/`; `ARTEMIS_UI_UX_SYSTEM.md` владеет общей UX-моделью, `ARTEMIS_UI_UX_COMPONENT_MAP.md` — картой компонентов и состояний, `ARTEMIS_UI_UX_VISUAL_SYSTEM.md` — visual design layer;
- historical AI/Courses/expansion plans live in `docs/archive/` and cannot open scope.

### 8.4 Audits

Текущий слой:

```text
docs/audits/
└── *.md
```

Назначение:
- фиксируют результаты проверок;
- не определяют архитектуру или roadmap;
- всегда проверяют canonical docs, а не заменяют их.

### 8.5 Archive / Reference

Текущий слой:

```text
docs/archive/
└── ...

docs/reference/
└── ...
```

Назначение:
- старые snapshot-документы и reference-материалы;
- historical context;
- reference only.

Правило:
- archive/reference слой нельзя использовать как текущий source of truth.

---

## 9. ЧТО СЧИТАЕТСЯ НАРУШЕНИЕМ СТРУКТУРЫ

Технические нарушения:
- competing backend package рядом с canonical `app/`;
- прямой доступ frontend к Airtable;
- implicit fallback public map на runtime API;
- смешивание draft/runtime/public data contracts;
- competing backend entrypoints;
- второй renderer, который владеет собственной historical/domain semantics вместо shared model/projection boundary;
- renderer-specific historical data forks (`*_2d`, `*_3d` or equivalent) that can drift semantically;
- renderer-owned `zoom/pitch/bearing/camera/viewer/scene` state promoted into the semantic Explorer State contract;
- authoritative persisted `visible_object_ids` instead of deterministic derivation from World Slice + Explorer State;
- experimental Globe assets/dependencies entering the public Pages artifact outside the explicit `--public-preview` build and `/globe/` route;
- использование terrain/imagery provider metadata как substitute for historical provenance.

Документационные нарушения:
- несколько равноправных source-of-truth документов по одной теме;
- хранение активного roadmap в archive/reference-слое;
- несинхрон canonical docs и checked-in release/data behavior;
- использование audit-файла вместо обновления canonical doc;
- обновление кода без обязательного docs sync для архитектурных, data и release изменений;
- сохранение в canonical docs старых имён документов или старых API summary после смены фактической структуры проекта;
- добавление product/data/UI/AI решений без проверки against foundation-layer;
- развитие Stories/Courses/AI вне independent branch decision;
- описание current mutable ResearchSlice as immutable revision;
- использование classification/Similarity as substantive Relation;
- использование AI output как source-backed/canonical knowledge без governance;
- описание experimental 3D Globe R&D как current public/product capability.

---

## 10. ПРАВИЛО DOCS SYNC

Любое изменение в следующих областях обязано сопровождаться обновлением canonical docs:
- architecture boundaries;
- registered frontend/presentation runtime boundaries;
- renderer-neutral state or render-projection contracts;
- data contract;
- release gate / workflow / readiness semantics;
- canonical current public map source;
- geospatial asset/terrain/imagery semantics when they affect runtime or historical interpretation;
- auth/runtime deployment constraints;
- mission, product scope, research-work semantics, Claim/Evidence model, entity model, content governance and AI policy;
- documentation governance и правила размещения документов.

Без этого change считается незавершённым.
