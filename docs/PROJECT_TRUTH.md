# ARTEMIS — PROJECT TRUTH

## Статус

- Тип: canonical current-state document.
- Дата фиксации: 2026-07-24.
- Владелец смысла: фактическая доступность продукта и граница между public, backend и future scope.
- Обновляется только при изменении фактической доступности runtime, данных или пользовательского сценария.

Этот документ отвечает на вопрос «что ARTEMIS действительно умеет сейчас». Он не заменяет продуктовую стратегию, data contract или release policy.

## 1. Принятое продуктовое направление

Активный delivery focus ARTEMIS — **инструмент доказательного сравнения 2–3 архитектурных объектов для продвинутого студента истории архитектуры**.

`ARTEMIS_CONCEPT.md` определяет North Star, а не текущую версию продукта. Долгосрочная explainable spatial-temporal research workspace сохраняется, но не является обещанием текущего публичного продукта. Расширение на другие предметные области допускается только после решения `EXPAND` в `VALIDATION_DECISION.md`.

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
- Research Slices owner CRUD и unlisted read-only share/revoke contract для текущего persistence envelope;
- Stories CRUD как thin orchestration над slices;
- Courses CRUD как thin orchestration над stories;
- Explain Context Contract без генеративного AI-ответа;
- Redis-backed session paths и SQLite baseline persistence.

Наличие backend-кода не означает, что функция доступна на публичном GitHub Pages URL.

Текущий Slice schema сохраняет Features, time/view state и annotations, но не имеет отдельных first-class полей для research question, evidence refs, conclusion, uncertainty и content version. Поэтому кодовый Slice baseline не считается product-complete Research Slice до schema/code sync и public validation.

## 4. Текущее состояние данных

На дату фиксации Airtable/public export содержит:

- 31 Features;
- 6 comparison cohorts минимум по 3 Features;
- 35 reviewed Sources;
- 28 reviewed Media records linked as primary к 28 Features (`90.32%`);
- 12 reviewed canonical Relations и 21 reviewed evidence links (`100%` evidence coverage);
- только архитектурные объекты.

Известные ограничения:

- canonical identity migration v1 завершена в PR `#290`: ETL и public artifacts используют `Features.id` UUID v4, а Airtable record ID отделён как `source_record_id`;
- source migration выполнена: контрольное чтение Airtable подтверждает `19/19 id_status=ok`; точная таблица, execution evidence и recovery-план зафиксированы в `docs/work/2026-07-16_CANONICAL_IDENTITY_MIGRATION_v1.md`;
- initial Source batch #283 закрыл `19/19` исходных Features; V2/V3 довели текущий corpus до 35 reviewed Sources и `31/31` Feature Source coverage;
- initial Media batch #283 содержал 16 reviewed direct assets; V2 довёл текущий корпус до `28/31` primary Media, а для трёх rights-blocked объектов public `image_url=null` (Бурдж-Халифа, Вилла Савой и Центр Помпиду); полный перечень исходной миграции и blockers находится в `docs/work/2026-07-16_SOURCES_MEDIA_MIGRATION_v1.md`;
- 7 enabled empty source Layers исключены из public `layers.json` и сохранены как actionable semantic warnings;
- Media semantics реализованы в ETL; текущая reviewed coverage составляет `28/31`, а для трёх rights-blocked объектов public `image_url=null`;
- Relations/Similarity pilot реализован: detail panel показывает 12 reviewed evidence-backed записей из `data/relations.json` в блоке «Документированные связи», а эвристику одинакового слоя/периода — отдельно как «Похожие объекты» с явными критериями;
- semantic ETL/release gate проверяет blocking errors отдельно от budgeted warnings, cross-artifact evidence/review semantics, enabled populated Layers и отсутствие unreviewed legacy image URLs;
- текущий checked-in report имеет статус `ready_with_warnings`: 14 warnings (7 empty-Layer exclusions, 3 missing primary Media и 4 corpus-quality signals), 0 blocking errors.
- comparison-pilot profile имеет статус `comparison_ready`: 31 Feature, 6 cohorts, 12 Relations, 100% Source/Relation evidence coverage и 90.32% primary Media.

До исправления этих ограничений dataset считается pilot, а не исследовательским корпусом production-уровня.

## 5. Что не считается реализованным продуктом

- универсальная историческая knowledge platform;
- production-hardened multi-node backend;
- публично развернутый end-to-end Research Slice workflow: share-контракт реализован в коде, но отдельный API runtime и `ARTEMIS_API_BASE` ещё не опубликованы;
- product-complete Research Slice с отдельными question/evidence/conclusion/uncertainty/version semantics;
- полноценные guided Stories и Courses;
- AI explanation, comparison или hypothesis generation;
- зрелый relation graph за пределами 12-record validation pilot;
- causal, predictive или counterfactual engine.

## 6. Главные риски текущего состояния

1. Интерфейс обещает больше, чем доступно в public runtime.
2. Документация и backend breadth создают впечатление зрелости, не подтверждённое содержанием.
3. Identity/source/media contracts допускают формально успешный, но семантически слабый export.
4. Малый объём Relations может создать впечатление более полной графовой модели, чем фактически существует.
5. Scaling до доказательства product loop увеличивает стоимость неподтверждённой архитектуры.
6. Текущий Slice persistence envelope может быть ошибочно принят за завершённый исследовательский артефакт.
7. Usability test без cognitive и behavioral evidence может создать ложное впечатление подтверждённой продуктовой ценности.

## 7. Текущий operational verdict

ARTEMIS находится в состоянии **controlled engineering prototype / product-data validation**.

Следующая активная фаза — не scaling и не feature expansion, а:

1. синхронизация продукта и документации;
2. исправление data foundation;
3. завершение product-complete Slice schema/code sync;
4. подключение публичного backend для Slice loop;
5. UX refinement вокруг Question → Compare → Evidence → Conclusion → Save;
6. validation против catalogue/list baseline;
7. usability, cognitive и behavioral evidence;
8. отдельное решение в `VALIDATION_DECISION.md`.

## 8. Правило честного описания

README, UI, issues, release notes и публичные материалы обязаны различать:

- `PUBLIC NOW` — работает на опубликованном URL;
- `BACKEND-AVAILABLE` — реализовано, но требует отдельного runtime/configuration;
- `PILOT` — существует, но недостаточно подтверждено данными или пользователями;
- `FUTURE` — концепция или запланированный слой.

Формулировка более высокого уровня зрелости запрещена без исполнимого evidence.
