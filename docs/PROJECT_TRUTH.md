# ARTEMIS — PROJECT TRUTH

## Статус

- Тип: canonical current-state document.
- Дата фиксации: 2026-08-10.
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
- The artifact is **R&D EVIDENCE, NOT PUBLIC CAPABILITY**: there is no public ARTEMIS Globe product surface, no Gate C historical World Slice integrated into that runtime and no production terrain/provider decision.
- Issue #344 / PR #351 semantic parity is merged executable evidence; issue #355 remains the active product-facing MVP contour.
- Gate C is completed/FREEZE in #332/#360 / PR #362 for the non-public Leonardo-in-Romagna boundary, 8 August–31 December 1502.
- The Gate C package has two independent READY reviews and measured curation/review cost, but `historical_objects_ready=false`, `promotion_allowed=false`, Claims remain draft and unsupported route/Region geometry remains withheld.
- Foundation v3.1 / #363 / PR #364 is completed; Gate D is still only the next product gate and has not been opened by the Foundation decision or by Airtable data-governance work.
- An empty, non-authoritative Airtable World Model **shadow curation schema** exists under #368 as pre-Gate-D data-governance evidence. It is not read by the public exporter, contains no Gate C historical records and does not change product capability.

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

После #366 / PR #367 существующие восемь Airtable tables явно зафиксированы как Architecture Atlas compatibility/public-projection curation, а не как Foundation v3 semantic owner. Canonical current export остаётся:

`legacy Airtable tables → scripts/export_airtable.py → semantic data gate → checked-in public data/*`.

Под #368 создан отдельный **empty/non-authoritative shadow schema** из шести таблиц:

- `WorldSlices`;
- `KnowledgeObjects`;
- `ObjectParts`;
- `Claims`;
- `EvidenceLinks`;
- `Uncertainties`.

Фактическая граница этого shadow contour:

- все шесть таблиц проверены с `0` records после создания;
- `Sources` переиспользуется только как стабильный provenance registry;
- `Layers` переиспользуется только как display/query grouping;
- `Media` остаётся presentation/rights subsystem;
- новый Relation table не создавался, пока #331 paused;
- shadow tables не читаются текущим `export_airtable.py` и не являются source of truth для public `data/*`;
- live schema snapshot и executable contract находятся в `fixtures/airtable_curation/v1/`;
- `scripts/validate_airtable_curation_schema.py --require-empty` fail-closed проверяет schema/lifecycle boundary;
- Airtable автоматически создаёт inverse-link fields; они являются storage implementation detail, а не новыми семантическими Relations;
- Airtable UI сам по себе не гарантирует Claim/Evidence/Uncertainty cardinalities, поэтому реальные записи нельзя импортировать до отдельного row-level validator/import contract;
- record-time `dateTime` fields в shadow schema используют Airtable display timezone `Europe/London`; это не историческое valid time и не меняет temporal semantics World Model.

Наличие этой schema означает только, что ARTEMIS теперь имеет проверяемую editorial storage shape для будущей curation. Оно **не** означает наличие World Model corpus в Airtable, readiness historical data, Gate D start или public capability.

Gate C historical curation package остаётся отдельным от public Airtable export и от пустого shadow schema:

- #332/#360 / PR #362 froze Leonardo-in-Romagna 1502 as a non-public World Slice boundary;
- 17 candidate objects, 10 Sources, 22 atomic Claims, 38 EvidenceLinks and 11 provenance-bearing Uncertainties are bound to the frozen reviewed revision;
- no documented Relations are stored while #331 remains paused;
- three inter-place routes remain unknown with no invented geometry;
- Duchy of Romagna Region states remain geometry-withheld where evidence/rights do not support a boundary;
- this package is reviewed as a **Gate C boundary**, not promoted to public/READY historical product data;
- none of these Gate C historical records has been imported into the Airtable shadow schema at the #368 schema stage.

До отдельной promotion/runtime decision public dataset остаётся Architecture Atlas pilot, Gate C package — non-public frozen input, а Airtable World Model tables — empty shadow curation infrastructure.

## 5. Что не считается реализованным продуктом

- universal spatial-temporal knowledge-model runtime;
- public/product-ready Life in Context World Slice and synchronized explorer;
- Airtable World Model shadow schema as a historical corpus, canonical storage authority or product capability;
- Gate C package integrated into Airtable as a validated shadow copy;
- Gate C package integrated into the Globe runtime as a complete Gate D experience;
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
11. Empty Airtable World Model schema может стать competing semantic/storage authority, если реальные данные начнут вноситься вручную до deterministic import/export + row-level validation + round-trip parity against the frozen repository package.

## 7. Текущий operational verdict

ARTEMIS находится в состоянии **controlled engineering prototype / Gate C frozen / Foundation v3.1 accepted / Gate D not opened**.

Current public runtime and public data remain the Architecture Atlas baseline. Foundation contracts are substantially ahead of public implementation. Airtable now additionally contains an empty non-authoritative World Model curation shadow schema, but this is data-governance infrastructure, not a new product/runtime capability.

Reviewed/accepted foundation evidence includes:

- #329 / PR #336 world-model fixtures — READY;
- #330 / PR #337 uncertainty semantics — READY;
- #339–#345 / PRs #346–#352 renderer-neutral Globe foundations — accepted;
- #332/#360 / PR #362 Gate C World Slice boundary — FREEZE with two independent READY reviews;
- #363 / PR #364 Foundation v3.1 Attractor refinement — accepted with all required repository workflows green on its merge candidate.

Pre-Gate-D data-governance evidence now includes:

- #366 / PR #367 — legacy Airtable boundary/schema truth and canonical audit path aligned;
- #368 — empty, executable, non-authoritative Airtable World Model shadow schema; no Gate C historical import and no public export authority.

There is currently no active foundation-maintenance issue. #368 is data-governance maintenance and is not a second product vertical. The next **product** transition remains Gate D, but it must be opened explicitly under #355; neither Airtable schema creation nor any future shadow-import parity work may open it by implication.

До explicit Gate D допустимы только bounded maintenance/evidence шаги, которые не меняют product capability. Для Airtable следующий потенциальный шаг после acceptance #368 — отдельный non-authoritative Gate C shadow-import + round-trip parity contour с row-level validation. Он также не является Gate D.

Когда product execution возобновится через явный Gate D transition, primary order остаётся:

1. explicitly open Gate D under #355 with a bounded source-aware Globe experience contract;
2. build the synchronized Globe/timeline/layers experience from the frozen Gate C boundary through shared contracts;
3. preserve the current 2D renderer as public baseline, parity target and rollback path;
4. collect semantic, UX, accessibility and representative performance evidence;
5. record one promotion/iterate/narrow/stop decision before public deployment.

Issue #331 is paused outside this critical path. Until it is accepted, the real slice/runtime may expose only derived proximity/co-presence and must not publish documented encounter, interaction, influence or causal predicates.

The superseded #323–#325 path and PR #314 remain closed. Passing fixtures, storage schemas or Foundation documents prove neither public capability nor user value.

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
