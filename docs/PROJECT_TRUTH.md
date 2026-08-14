# ARTEMIS — PROJECT TRUTH

## Статус

- Тип: canonical current-state document.
- Дата фиксации: 2026-08-14.
- Владелец смысла: фактическая доступность продукта и граница между public, backend, R&D и future scope.
- Обновляется только при изменении фактической доступности runtime, данных, пользовательского сценария или когда active R&D/data-governance status иначе создаёт прямое противоречие с capability wording.

Этот документ отвечает на вопрос «что ARTEMIS действительно умеет сейчас». Он не заменяет продуктовую стратегию, data contract или release policy.

## 1. Принятое продуктовое направление

Foundation v3 / PR `#328` restored ARTEMIS as a source-aware spatial-temporal World Model. Foundation v3.1 / issue `#363` / PR `#364` clarifies that `World Model` is a source-aware **knowledge representation about the world**, not an objective digital twin or a claim of completeness. This accepted clarification changes North Star wording, not current capability.

Первый active validation vertical — `Life in Context`; issue #355 делает 3D Globe основной interface-development surface этого цикла. Architecture Atlas и root 2D MapLibre сохраняются как thematic/public technical baseline and rollback path.

Важно:

- Foundation documentation не реализует world model runtime;
- текущий public runtime остаётся статическим Architecture Atlas;
- real Life in Context synchronized multi-layer experience ещё не доступен публично;
- Claim/Evidence discipline сохраняется как trust layer;
- Research Brief/revisions остаются optional future research capabilities, а не current public core;
- generative AI, causal/counterfactual runtime, personal knowledge model, VR/AR and universal corpus remain frozen/future;
- **A real executable 3D Globe R&D artifact exists** and uses MapLibre GL JS `5.24.0` in isolation; the current public runtime remains MapLibre GL JS `4.7.1`.
- The artifact is **R&D EVIDENCE, NOT PUBLIC CAPABILITY**: there is no public ARTEMIS Globe product surface and no production Earth-context/provider decision.
- PR `#379` integrates the frozen Gate C package into the generated non-public Globe artifact through the shared World Model → Explorer State → Render Projection path. It preserves `0` authorized historical geometries/primitives, all withheld Region alternatives and all unknown-route gaps.
- PR `#380` adds 96 deterministic Explorer views from six source-native temporal presets and all 16 combinations of four semantic layers, plus synchronized timeline/layers, canonical selection/picking, inspector, URL restoration, keyboard operation and reduced-motion behavior. This is a completed Gate D interaction increment, not a completed Gate D experience or public promotion.
- Issue #344 / PR #351 semantic parity is merged executable evidence; issue #355 remains the active product-facing MVP contour.
- Gate C is completed/FREEZE in #332/#360 / PR #362 for the non-public Leonardo-in-Romagna boundary, 8 August–31 December 1502.
- The Gate C package has two independent READY reviews and measured curation/review cost, but `historical_objects_ready=false`, `promotion_allowed=false`, Claims remain draft and unsupported route/Region geometry remains withheld.
- Foundation v3.1 / #363 / PR #364 is completed. Gate D is now separately opened and in progress under #355; that lifecycle transition does not change public capability or historical readiness.
- #368 established the original six-table empty/non-authoritative Airtable World Model shadow schema. Merged PR #372 extends that preflight surface with three additional empty shadow-only tables plus parity fields, but **no Gate C historical row has been written**. Issues #371/#373 are deferred outside the Gate D critical path.

## 2. Что доступно публично

GitHub Pages публикует статический runtime:

- карту MapLibre;
- checked-in `data/*`;
- фильтры, поиск, выбор периода и карточку объекта;
- PWA/static behavior в границах текущего service worker;
- интерфейсные entry points, не требующие backend API.

GitHub Pages не исполняет FastAPI. Без отдельно настроенного `ARTEMIS_API_BASE` публичный сайт не предоставляет рабочие auth, Research Slices, Stories, Courses, uploads и moderation API.

## 3. Что реализовано в репозитории, но требует backend runtime

- auth и refresh-session flow;
- drafts и uploads;
- moderation lifecycle;
- Research Slice v2 owner create/edit/reopen/delete, explicit question/rationale/evidence/findings/conclusion/uncertainty, nested Saved View и unlisted read-only share/rotate/revoke;
- Stories CRUD как thin orchestration над slices;
- Courses CRUD как thin orchestration над stories;
- Explain Context Contract без генеративного AI-ответа;
- Redis-backed session paths и SQLite baseline persistence.

Наличие backend-кода не означает, что функция доступна на публичном GitHub Pages URL.

Research Slice schema/code sync выполнен как v2: migration 203, API, client и tests используют explicit question/rationale, fail-closed evidence state и Source/Relation refs, typed findings, conclusion/unresolved, uncertainty, schema/content version и вложенный Saved View.

После Concept Lock v2 current model честно классифицируется как mutable compatibility envelope. Она не реализует:

- first-class Investigation;
- immutable Slice Revisions;
- Claim/EvidenceLinks with locators and evidence relation/strength;
- pinned dataset identity;
- revision-pinned share;
- deterministic citation-ready Research Brief.

Migration preflight и release gate подтверждают current backend capability, но не target research model, public availability or product value.

## 4. Текущее состояние данных

Текущий Architecture Atlas Airtable/public export содержит:

- 31 Features;
- 6 comparison cohorts минимум по 3 Features;
- 35 reviewed Sources;
- 28 reviewed Media records linked as primary к 28 Features (`90.32%`);
- 12 reviewed current Relation records и 21 reviewed legacy relation-source links;
- только архитектурные объекты.

Известные ограничения public/Architecture Atlas corpus:

- canonical identity migration v1 завершена в PR `#290`: ETL и public artifacts используют `Features.id` UUID v4, а Airtable record ID отделён как `source_record_id`;
- source migration выполнена: контрольное чтение Airtable подтверждает `19/19 id_status=ok`; точная таблица, execution evidence и recovery-план зафиксированы в `docs/work/2026-07-16_CANONICAL_IDENTITY_MIGRATION_v1.md`;
- initial Source batch #283 закрыл `19/19` исходных Features; V2/V3 довели текущий corpus до 35 reviewed Sources и `31/31` Feature Source coverage;
- initial Media batch #283 содержал 16 reviewed direct assets; V2 довёл текущий корпус до `28/31` primary Media, а для трёх rights-blocked объектов public `image_url=null` (Бурдж-Халифа, Вилла Савой и Центр Помпиду); полный перечень исходной миграции и blockers находится в `docs/work/2026-07-16_SOURCES_MEDIA_MIGRATION_v1.md`;
- 7 enabled empty source Layers исключены из public `layers.json` и сохранены как actionable semantic warnings;
- Media semantics реализованы в ETL; текущая reviewed coverage составляет `28/31`, а для трёх rights-blocked объектов public `image_url=null`;
- Relations/Similarity pilot реализован технически: detail panel показывает 12 reviewed records, а computed Similarity — отдельно;
- 10 из 12 current Relation records имеют тип `same_movement`; Concept Lock v2 классифицирует их как documented shared-classification compatibility records, а не substantive historical Relations;
- только два current records (`influenced`, `inspired_by`) являются кандидатами на substantive Relation value, но ещё не имеют target claim-level locator/evidence semantics;
- semantic ETL/release gate проверяет blocking errors отдельно от budgeted warnings, cross-artifact evidence/review semantics, enabled populated Layers и отсутствие unreviewed legacy image URLs;
- текущий checked-in report имеет статус `ready_with_warnings`: 14 warnings (7 empty-Layer exclusions, 3 missing primary Media и 4 corpus-quality signals), 0 blocking errors;
- comparison-pilot profile имеет технический статус `comparison_ready`: 31 Feature, 6 cohorts, 12 legacy-counted Relations, 100% current link coverage и 90.32% primary Media;
- Architecture Gate A package завершён со статусом `3/3 READY` и двумя independent review processes; он сохраняется как reviewed fixture/evidence package, но не является Foundation v3 user-value validation;
- executable world-model fixtures #329 / PR #336 and uncertainty semantics #330 / PR #337 are reviewed READY contract evidence; they are fixtures/contracts, not public World Model data or a public Globe runtime.

### Airtable World Model shadow curation schema

После #366 / PR #367 существующие восемь legacy Airtable tables явно зафиксированы как Architecture Atlas compatibility/public-projection curation, а не как Foundation v3 semantic owner. Canonical current export остаётся:

`legacy Airtable tables → scripts/export_airtable.py → semantic data gate → checked-in public data/*`.

#368 / PR #369 создал исходный **empty/non-authoritative shadow schema** из шести таблиц:

- `WorldSlices`;
- `KnowledgeObjects`;
- `ObjectParts`;
- `Claims`;
- `EvidenceLinks`;
- `Uncertainties`.

Merged PR #372 завершил отдельный **schema/mapping preflight** для frozen Leonardo Gate C package. В live Airtable дополнительно существуют три shadow-only таблицы, также проверенные с `0` records:

- `SliceLayers` — exact per-WorldSlice layer identity/role без записи Gate C слоёв в legacy public-source `Layers`;
- `WorldSources` — lossless World Model source/rights registry без записи Leonardo Sources в legacy public `Sources`;
- `UncertaintyTargets` — storage junction для many-target `Uncertainty.target_refs[]` без клонирования 11 исходных Uncertainty identities.

Дополнительные parity/provenance fields в `KnowledgeObjects`, `ObjectParts`, `Claims`, `EvidenceLinks` и `Uncertainties` сохраняют source temporal tokens, source/reconstruction metadata, Claim confidence basis, Uncertainty basis и WorldSource refs. Эти поля являются storage representation, а не новой semantic ontology.

Фактическая граница shadow contour на 2026-08-12:

- все шесть исходных #368 tables по-прежнему проходят `--require-empty` с `0` historical records;
- все три #371 extension tables проверены с `0` records;
- legacy `KnowledgeObjects.layers` должен оставаться пустым для Gate C shadow import; World Model layer roles идут через `SliceLayers`;
- legacy `EvidenceLinks.source` должен оставаться пустым для Gate C shadow import; Claim-specific evidence идёт через `EvidenceLinks.world_source → WorldSources`;
- legacy Architecture Atlas `Layers`, `Sources`, `Media`, exporter и checked-in public `data/*` не изменены этим contour;
- новый Relation table не создавался; #331 deferred;
- live schema evidence v1 остаётся в `fixtures/airtable_curation/v1/`; #371 extensions/mapping/row-plan evidence находятся в `fixtures/airtable_curation/v2/`;
- `scripts/validate_airtable_leonardo_shadow_preflight.py` fail-closed проверяет frozen package, schema extensions, ref closure, unknown-route/geometry-withheld semantics и Gate C/Gate D boundary;
- deterministic semantic-ID row-plan builder воспроизводит ровно **154 candidate rows**: 1 WorldSlice, 4 SliceLayers, 10 WorldSources, 17 KnowledgeObjects, 11 ObjectParts, 22 Claims, 38 EvidenceLinks, 11 Uncertainties и 40 UncertaintyTargets;
- этот row plan frozen отдельным lock с SHA-256 `ff63b8ed036ec79ac73e11c2eb4d3cad22b69b0e5a361c23cef767c5c5ac83f1` и проверяется Release Discipline;
- **row-plan lock не является разрешением на historical write**: `historical_rows_authorized=false`, independent mapping review остаётся обязательным до первой записи;
- Airtable автоматически создаёт inverse-link fields; они являются storage implementation detail, а не новыми семантическими Relations;
- record-time `dateTime` fields используют Airtable display timezone `Europe/London`; это не historical valid time и не меняет temporal semantics World Model.

Наличие девяти empty shadow tables, deterministic mapping и frozen row plan означает только, что ARTEMIS имеет проверяемую editorial storage/preflight форму для возможного будущего controlled import. Оно **не** означает наличие World Model corpus в Airtable, historical readiness, round-trip parity, Gate D evidence или public capability.

Gate C historical curation package остаётся отдельным от public Airtable export и от пустого shadow storage:

- #332/#360 / PR #362 froze Leonardo-in-Romagna 1502 as a non-public World Slice boundary;
- 17 candidate objects, 10 Sources, 22 atomic Claims, 38 EvidenceLinks and 11 provenance-bearing Uncertainties are bound to the frozen reviewed revision;
- no documented Relations are stored while #331 remains deferred;
- three inter-place routes remain unknown with no invented geometry;
- Duchy of Romagna Region states remain geometry-withheld where evidence/rights do not support a boundary;
- this package is reviewed as a **Gate C boundary**, not promoted to public/READY historical product data;
- none of the 154 planned shadow rows has been written at the #371 row-plan-lock stage.

Public dataset остаётся Architecture Atlas pilot, Gate C package — non-public frozen authority, а Airtable World Model tables — empty non-authoritative shadow infrastructure. #371/#373 import/review work is deferred; Gate D consumes the repository package directly.

## 5. Что не считается реализованным продуктом

- universal spatial-temporal knowledge-model runtime;
- public/product-ready Life in Context World Slice and synchronized explorer;
- Airtable World Model shadow schema as a historical corpus, canonical storage authority or product capability;
- frozen 154-row Airtable plan as imported data, round-trip parity evidence or historical readiness;
- Gate C package integrated into Airtable as a validated shadow copy;
- a complete Gate D experience with production Earth context, representative desktop/mobile/accessibility/performance evidence and an explicit Gate D exit decision;
- first-class State, Process, Trajectory and temporal Region schemas in current public runtime;
- public/product 3D Globe, production dynamic terrain or VR experience; #355 changes active development scope, not current public capability;
- production-hardened multi-node backend;
- публично развернутый end-to-end Research Slice workflow: share-контракт реализован в коде, но отдельный API runtime и `ARTEMIS_API_BASE` ещё не опубликованы;
- полноценные guided Stories и Courses;
- AI explanation/comparison/hypothesis generation runtime;
- AI Knowledge Exploration Interface or executable AI view-action contract;
- personal knowledge model;
- зрелый relation graph за пределами 12-record validation pilot;
- first-class public Claim/EvidenceLink corpus;
- immutable Investigation/revision model and Research Brief export;
- causal, predictive или counterfactual engine;
- universal corpus or objective digital twin of the world.

## 6. Главные риски текущего состояния

1. Интерфейс обещает больше, чем доступно в public runtime.
2. Документация и backend breadth создают впечатление зрелости, не подтверждённое содержанием.
3. Identity/source/media contracts допускают формально успешный, но семантически слабый export.
4. Legacy `same_movement` count может создать впечатление relation graph, хотя 10/12 записей являются shared classification.
5. Scaling до доказательства product loop увеличивает стоимость неподтверждённой архитектуры.
6. Backend-complete mutable Slice v2 может быть ошибочно принят за target immutable research model.
7. Usability test без cognitive и behavioral evidence может создать ложное впечатление подтверждённой продуктовой ценности.
8. Globe MVP может стать shadow product, если он обойдёт shared World Model / Explorer State / Render Projection или преждевременно войдёт в public Pages.
9. Long-term attractor может быть ошибочно воспринят как permission to implement AI/VR/universal corpus before gates; Foundation v3.1 explicitly forbids this.
10. `World Model` wording can drift back toward objective-digital-twin claims unless the knowledge-vs-world boundary remains explicit.
11. Airtable World Model schema может стать competing semantic/storage authority, если данные начнут вноситься вручную в обход deterministic import/export + row-level validation + round-trip parity against the frozen repository package.
12. Frozen 154-row plan может быть ошибочно принят за completed import evidence; поэтому live historical write остаётся fail-closed до отдельного independent mapping review и последующего readback/parity proof.
13. Accepted #377 / PR #378 refinement semantics can be mistaken for runtime/storage capability. No mutable precision/history behavior is authorized until a separate implementation decision preserves append-only lineage, valid-time/record-time separation, alternatives and evidence history.

## 7. Текущий operational verdict

ARTEMIS находится в состоянии **controlled engineering prototype / Gate C frozen / Foundation v3.1 accepted / Gate D in progress and non-public**.

Current public runtime and public data remain the Architecture Atlas baseline. Foundation contracts are substantially ahead of public implementation. Airtable additionally contains nine empty non-authoritative World Model shadow tables plus a deterministic/frozen Leonardo row plan, but this is data-governance infrastructure and preflight evidence, not a new product/runtime or historical-corpus capability.

Reviewed/accepted foundation evidence includes:

- #329 / PR #336 world-model fixtures — READY;
- #330 / PR #337 uncertainty semantics — READY;
- #339–#345 / PRs #346–#352 renderer-neutral Globe foundations — accepted;
- #332/#360 / PR #362 Gate C World Slice boundary — FREEZE with two independent READY reviews;
- #363 / PR #364 Foundation v3.1 Attractor refinement — accepted with all required repository workflows green on its merge candidate;
- #377 / PR #378 Progressive Refinement Contract v1 — accepted foundation evidence without runtime/storage capability change;
- PR #379 — frozen Gate C package consumed by the generated non-public Globe artifact through the shared semantic path;
- PR #380 — synchronized time/layers/selection/inspector interaction increment with 96 deterministic Explorer views and all six PR workflows green.

Completed/deferred Airtable data-governance evidence now includes:

- #366 / PR #367 — legacy Airtable boundary/schema truth and canonical audit path aligned;
- #368 / PR #369 — original six-table empty executable non-authoritative Airtable World Model shadow schema;
- #371 / merged PR #372 — completed lossless schema/mapping preflight with three additional empty shadow tables and a 154-row frozen semantic-ID plan; #371/#373 are deferred and historical writes remain unauthorized.

Issue #377 is foundation maintenance whose exact lifecycle is owned by
`PROGRESSIVE_REFINEMENT_CONTRACT.md` and its review registry. It is completed through PR #378, but
does not enter the product issue lifecycle sets, consume the product-gate WIP slot or change current
capability. Gate D remains explicitly open under #355 as the sole active product gate. The runtime
may read/render the frozen Gate C package, but contract acceptance does not authorize
runtime/storage mutation, Airtable writes or public capability. There is no active Airtable import
issue.

#371/#373 могут возобновиться только отдельным lifecycle decision. Если #371 будет reopened, следующий разрешённый шаг — independent review frozen row plan; только после успешного review можно отдельно разрешить controlled live import, обязательный readback/row-level validation и normalized round-trip parity against the frozen Gate C package.

Для активного Gate D primary order:

1. preserve the explicit Gate D opening contract under #355;
2. preserve the accepted #377 contract and require a separate implementation authorization before editable precision/history behavior;
3. preserve the merged #379/#380 frozen-package adapter and synchronized time/layers/selection/inspector increments;
4. complete the Earth-context provider, attribution, temporal-role, licensing, cache and secret policy without presenting modern context as historical truth;
5. preserve the current 2D renderer as public baseline, parity target and rollback path while collecting desktop/mobile, accessibility and representative performance evidence;
6. record exactly one Gate D decision — `ADVANCE_TO_GATE_E`, `NARROW` or `REJECT` — before any Gate E work or public deployment.

Issue #331 is deferred outside this critical path. Until it is explicitly reopened and accepted, the real slice/runtime may expose only derived proximity/co-presence and must not publish documented encounter, interaction, influence or causal predicates.

The superseded #323–#325 path and PR #314 remain closed. Passing fixtures, storage schemas, row plans or Foundation documents prove neither public capability nor user value.

## 8. Правило честного описания

README, UI, issues, release notes и публичные материалы обязаны различать:

- `PUBLIC NOW` — работает на опубликованном URL;
- `BACKEND-AVAILABLE` — реализовано, но требует отдельного runtime/configuration;
- `PILOT` — существует, но недостаточно подтверждено данными или пользователями;
- `R&D` — bounded experimental architecture/runtime work that is not a public capability promise;
- `SHADOW` — non-authoritative storage/curation/evidence contour, not public capability and not canonical historical corpus;
- `CONCEPT TARGET` — утверждено концептуально, но не реализовано;
- `FUTURE` — концепция или запланированный слой.

Long-term attractor, AI view-control semantics, personal knowledge, universal corpus and VR/AR remain `FUTURE` until separately implemented and validated.

Формулировка более высокого уровня зрелости запрещена без исполнимого evidence.
