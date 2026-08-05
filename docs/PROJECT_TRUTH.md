# ARTEMIS — PROJECT TRUTH

## Статус

- Тип: canonical current-state document.
- Дата фиксации: 2026-07-28.
- Владелец смысла: фактическая доступность продукта и граница между public, backend и future scope.
- Обновляется только при изменении фактической доступности runtime, данных или пользовательского сценария.

Этот документ отвечает на вопрос «что ARTEMIS действительно умеет сейчас». Он не заменяет продуктовую стратегию, data contract или release policy.

## 1. Принятое продуктовое направление

Foundation v3, accepted in PR `#328`, fixes the long-term direction of ARTEMIS: **source-aware spatial-temporal world model**, in which a person explores Entities, Events, States, Processes, Trajectories and Regions as synchronized layers of space and time.

Первый proposed validation vertical — `Life in Context` на ограниченном Leonardo World Slice. Architecture Atlas сохраняется как thematic layer и current public/technical baseline.

Важно:

- Foundation v3 documentation не реализует world model;
- текущий public runtime остаётся статическим Architecture Atlas;
- Life in Context, temporal Regions, full Trajectories and synchronized multi-layer change ещё не доступны;
- Claim/Evidence discipline сохраняется как trust layer;
- Research Brief/revisions остаются optional future research capabilities, а не current public core;
- generative AI, causal/counterfactual runtime, 3D/VR and universal corpus остаются frozen/future.

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

До исправления этих ограничений dataset считается pilot, а не исследовательским корпусом production-уровня.

## 5. Что не считается реализованным продуктом

- universal spatial-temporal world model runtime;
- Life in Context World Slice and synchronized explorer;
- first-class State, Process, Trajectory and temporal Region schemas;
- dynamic terrain/3D/VR experience;
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

## 7. Текущий operational verdict

ARTEMIS находится в состоянии **controlled engineering prototype / World Model Contract**.

Current runtime and data remain the Architecture Atlas baseline. Foundation v3 is accepted, but its world-model objects are not implemented in the public runtime or database/API.

Следующий допустимый порядок:

1. preserve completed #329 / PR #336 world-model fixtures as reviewed contract evidence;
2. preserve completed #330 / PR #337 uncertainty semantics;
3. complete #331 relation semantics against the reviewed uncertainty contract;
4. prepare one limited source-aware Leonardo World Slice under #332;
5. implement synchronized 2D map/timeline/layers under #333 on the static-first contour;
6. run #334 contextual-learning validation;
7. open at most one evidence-backed branch.

The superseded #323–#325 path and PR #314 are closed. Passing fixtures proves contract representability only; it does not change `PUBLIC NOW`, `BACKEND-AVAILABLE` or user-value status.

## 8. Правило честного описания

README, UI, issues, release notes и публичные материалы обязаны различать:

- `PUBLIC NOW` — работает на опубликованном URL;
- `BACKEND-AVAILABLE` — реализовано, но требует отдельного runtime/configuration;
- `PILOT` — существует, но недостаточно подтверждено данными или пользователями;
- `CONCEPT TARGET` — утверждено концептуально, но не реализовано;
- `FUTURE` — концепция или запланированный слой.

Формулировка более высокого уровня зрелости запрещена без исполнимого evidence.
