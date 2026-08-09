# ARTEMIS — PROJECT TRUTH

## Статус

- Тип: canonical current-state document.
- Дата фиксации: 2026-08-08.
- Владелец смысла: фактическая доступность продукта и граница между public, backend, R&D и future scope.
- Обновляется только при изменении фактической доступности runtime, данных, пользовательского сценария или когда active R&D status иначе создаёт прямое противоречие с capability wording.

Этот документ отвечает на вопрос «что ARTEMIS действительно умеет сейчас». Он не заменяет продуктовую стратегию, data contract или release policy.

## 1. Принятое продуктовое направление

Foundation v3, accepted in PR `#328`, fixes the long-term direction of ARTEMIS: **source-aware spatial-temporal world model**, in which a person explores Entities, Events, States, Processes, Trajectories and Regions as synchronized layers of space and time.

Первый active validation vertical — `Life in Context` на ограниченном Leonardo World Slice; issue #355 делает 3D Globe основной interface-development surface этого цикла. Architecture Atlas и root 2D MapLibre сохраняются как thematic/public technical baseline and rollback path.

Важно:

- Foundation v3 documentation не реализует world model;
- текущий public runtime остаётся статическим Architecture Atlas;
- real Life in Context corpus, temporal Regions, full Trajectories and synchronized multi-layer change ещё не доступны публично;
- Claim/Evidence discipline сохраняется как trust layer;
- Research Brief/revisions остаются optional future research capabilities, а не current public core;
- generative AI, causal/counterfactual runtime, VR/AR and universal corpus remain frozen/future;
- **A real executable 3D Globe R&D artifact now exists** and uses MapLibre GL JS `5.24.0` in isolation; the current public runtime remains MapLibre GL JS `4.7.1`.
- The artifact is **R&D EVIDENCE, NOT PUBLIC CAPABILITY**: there is no public ARTEMIS Globe product surface, no real historical World Slice in that runtime and no production terrain/provider decision.
- Issue #344 / PR #351 semantic parity remains an open recovery gate; issue #355 is the active product-facing MVP contour after that recovery.

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

На дату фиксации Airtable/public export содержит:

- 31 Features;
- 6 comparison cohorts минимум по 3 Features;
- 35 reviewed Sources;
- 28 reviewed Media records linked as primary к 28 Features (`90.32%`);
- 12 reviewed current Relation records и 21 reviewed legacy relation-source links;
- только архитектурные объекты.

Известные ограничения:

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
- текущий checked-in report имеет статус `ready_with_warnings`: 14 warnings (7 empty-Layer exclusions, 3 missing primary Media и 4 corpus-quality signals), 0 blocking errors.
- comparison-pilot profile имеет технический статус `comparison_ready`: 31 Feature, 6 cohorts, 12 legacy-counted Relations, 100% current link coverage и 90.32% primary Media;
- Architecture Gate A package завершён со статусом `3/3 READY` и двумя independent review processes; он сохраняется как reviewed fixture/evidence package, но не является Foundation v3 user-value validation.
- executable world-model fixtures #329 / PR #336 and uncertainty semantics #330 / PR #337 are reviewed READY contract evidence; they are fixtures/contracts, not public World Model data or a public Globe runtime.

До исправления этих ограничений dataset считается pilot, а не исследовательским корпусом production-уровня.

## 5. Что не считается реализованным продуктом

- universal spatial-temporal world model runtime;
- Life in Context World Slice and synchronized explorer;
- first-class State, Process, Trajectory and temporal Region schemas in current public runtime;
- public/product 3D Globe, production dynamic terrain or VR experience; #355 changes active development scope, not current public capability;
- production-hardened multi-node backend;
- публично развернутый end-to-end Research Slice workflow: share-контракт реализован в коде, но отдельный API runtime и `ARTEMIS_API_BASE` ещё не опубликованы;
- полноценные guided Stories и Courses;
- AI explanation, comparison или hypothesis generation;
- зрелый relation graph за пределами 12-record validation pilot;
- first-class Claim/EvidenceLink corpus;
- Foundation v3 Leonardo World Slice and same-content baseline;
- immutable Investigation/revision model and Research Brief export;
- causal, predictive или counterfactual engine.

## 6. Главные риски текущего состояния

1. Интерфейс обещает больше, чем доступно в public runtime.
2. Документация и backend breadth создают впечатление зрелости, не подтверждённое содержанием.
3. Identity/source/media contracts допускают формально успешный, но семантически слабый export.
4. Legacy `same_movement` count может создать впечатление relation graph, хотя 10/12 записей являются shared classification.
5. Scaling до доказательства product loop увеличивает стоимость неподтверждённой архитектуры.
6. Backend-complete mutable Slice v2 может быть ошибочно принят за target immutable research model.
7. Usability test без cognitive и behavioral evidence может создать ложное впечатление подтверждённой продуктовой ценности.
8. Globe MVP может стать shadow product, если он обойдёт shared World Model / Explorer State / Render Projection или преждевременно войдёт в public Pages.
9. PR #354 was merged with an incomplete governance diff and a failing lifecycle guard; repository lifecycle evidence must be verified from the actual diff and CI, not the PR narrative.

## 7. Текущий operational verdict

ARTEMIS находится в состоянии **controlled engineering prototype / Globe MVP recovery**.

Current runtime and data remain the Architecture Atlas baseline. Foundation v3 is accepted, but its world-model objects are not implemented in the public runtime or database/API.

Reviewed contract foundation now includes:

- #329 / PR #336 world-model fixtures — READY;
- #330 / PR #337 uncertainty semantics — READY.

Следующий допустимый primary order:

1. restore canonical governance and a green Release Discipline Gate after PR #354;
2. complete reopened #344 / PR #351 cross-renderer semantic parity;
3. freeze one small real source-aware World Slice inside #355;
4. implement the synchronized Globe/timeline/layers experience through shared contracts;
5. preserve the current 2D renderer as public baseline, parity target and rollback path;
6. collect semantic, UX, accessibility and representative performance evidence;
7. record one promotion/iterate/narrow/stop decision before public deployment.

Issue #331 is paused outside this critical path. Until it is accepted, the real slice/runtime may expose only derived proximity/co-presence and must not publish documented encounter, interaction, influence or causal predicates.

Accepted renderer foundations are #339–#343 and #345 / PRs #346–#350 and #352. #344 / PR #351 is not accepted until its red parity workflow is repaired and the implementation is merged.

The superseded #323–#325 path and PR #314 are closed. Passing fixtures proves contract representability only; it does not change `PUBLIC NOW`, `BACKEND-AVAILABLE` or user-value status.

## 8. Правило честного описания

README, UI, issues, release notes и публичные материалы обязаны различать:

- `PUBLIC NOW` — работает на опубликованном URL;
- `BACKEND-AVAILABLE` — реализовано, но требует отдельного runtime/configuration;
- `PILOT` — существует, но недостаточно подтверждено данными или пользователями;
- `R&D` — bounded experimental architecture/runtime work that is not a public capability promise;
- `CONCEPT TARGET` — утверждено концептуально, но не реализовано;
- `FUTURE` — концепция или запланированный слой.

Формулировка более высокого уровня зрелости запрещена без исполнимого evidence.
