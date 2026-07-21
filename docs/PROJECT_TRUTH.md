# ARTEMIS — PROJECT TRUTH

## Статус

- Тип: canonical current-state document.
- Дата фиксации: 2026-07-16.
- Владелец смысла: фактическая доступность продукта и граница между public, backend и future scope.
- Обновляется только при изменении фактической доступности runtime, данных или пользовательского сценария.

Этот документ отвечает на вопрос «что ARTEMIS действительно умеет сейчас». Он не заменяет продуктовую стратегию, data contract или release policy.

## 1. Принятое продуктовое направление

Активный delivery focus ARTEMIS — **доказательный пространственно-временной атлас истории архитектуры**.

Долгосрочная архитектура explainable spatial-temporal research workspace сохраняется, но не является обещанием текущего публичного продукта. Расширение на другие предметные области допускается только после проверки архитектурного vertical MVP.

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
- Research Slices CRUD;
- Stories CRUD как thin orchestration над slices;
- Courses CRUD как thin orchestration над stories;
- Explain Context Contract без генеративного AI-ответа;
- Redis-backed session paths и SQLite baseline persistence.

Наличие backend-кода не означает, что функция доступна на публичном GitHub Pages URL.

## 4. Текущее состояние данных

На дату фиксации Airtable/public export содержит:

- 19 Features;
- 26 source Layers / 19 enabled populated public Layers;
- 20 Sources (`19 reviewed / 1 draft`);
- 16 reviewed Media records linked as primary to 16 pilot Features;
- 2 reviewed canonical Relation records, each with one reviewed evidence link;
- только архитектурные объекты.

Известные ограничения:

- canonical identity migration v1 завершена в PR `#290`: ETL и public artifacts используют `Features.id` UUID v4, а Airtable record ID отделён как `source_record_id`;
- source migration выполнена: контрольное чтение Airtable подтверждает `19/19 id_status=ok`; точная таблица, execution evidence и recovery-план зафиксированы в `docs/work/2026-07-16_CANONICAL_IDENTITY_MIGRATION_v1.md`;
- Source batch #283 выполнен: для `19/19` Features существует ровно один reviewed primary Source; Airtable содержит `20 Sources / 19 reviewed / 1 unverifiable legacy candidate in draft` и `20 FeatureSources / 19 reviewed / 1 draft`;
- пять Media batch #283 содержат 16 reviewed direct assets и 16 reviewed primary FeatureMedia links; для трёх rights-blocked объектов public `image_url=null`, поэтому legacy Commons HTML pages не публикуются как изображения (Бурдж-Халифа, Вилла Савой и Центр Помпиду); полный перечень, evidence и migration plan находятся в `docs/work/2026-07-16_SOURCES_MEDIA_MIGRATION_v1.md`;
- 7 enabled empty source Layers исключены из public `layers.json` и сохранены как actionable semantic warnings; public Layer set содержит только 19 populated Layers;
- Media semantics реализованы в ETL, но reviewed-миграция охватывает 16 из 19 пилотных Features; для трёх современных зданий требуется отдельный источник изображения с достаточными правами;
- Relations/Similarity pilot реализован: detail panel показывает reviewed evidence-backed записи из `data/relations.json` в блоке «Документированные связи», а эвристику одинакового слоя/периода — отдельно как «Похожие объекты» с явными критериями;
- 2 reviewed Relations достаточны для проверки контракта, но ещё не образуют полноценный исследовательский relation graph;
- semantic ETL/release gate проверяет blocking errors отдельно от budgeted warnings, cross-artifact evidence/review semantics, enabled populated Layers и отсутствие unreviewed legacy image URLs;
- текущий checked-in report имеет статус `ready_with_warnings`: 14 warnings (7 empty-Layer exclusions, 3 missing primary Media и 4 corpus-quality signals), 0 blocking errors.
- comparison-pilot profile имеет статус `building`: 19/30 минимальных Features, 0/6 comparison cohorts, 2/12 Relations и 84.21%/90% primary Media; Source и Relation evidence coverage уже 100%.

До исправления этих ограничений dataset считается pilot, а не исследовательским корпусом production-уровня.

## 5. Что не считается реализованным продуктом

- универсальная историческая knowledge platform;
- production-hardened multi-node backend;
- публично доступный end-to-end Research Slice workflow;
- полноценные guided Stories и Courses;
- AI explanation, comparison или hypothesis generation;
- полноценная доказательная relation graph за пределами 2-record pilot;
- causal, predictive или counterfactual engine.

## 6. Главные риски текущего состояния

1. Интерфейс обещает больше, чем доступно в public runtime.
2. Документация и backend breadth создают впечатление зрелости, не подтверждённое содержанием.
3. Identity/source/media contracts допускают формально успешный, но семантически слабый export.
4. Малый объём Relations может создать впечатление более полной графовой модели, чем фактически существует.
5. Scaling до доказательства product loop увеличивает стоимость неподтверждённой архитектуры.

## 7. Текущий operational verdict

ARTEMIS находится в состоянии **controlled engineering prototype / product-data validation**.

Следующая активная фаза — не scaling и не feature expansion, а:

1. синхронизация продукта и документации;
2. исправление data foundation;
3. сбор утверждённого comparison-first content pilot 30–40 / 6–8 cohorts / 12–20 Relations;
4. подключение публичного backend для Slice loop;
5. UX refinement;
6. пользовательская проверка.

## 8. Правило честного описания

README, UI, issues, release notes и публичные материалы обязаны различать:

- `PUBLIC NOW` — работает на опубликованном URL;
- `BACKEND-AVAILABLE` — реализовано, но требует отдельного runtime/configuration;
- `PILOT` — существует, но недостаточно подтверждено данными или пользователями;
- `FUTURE` — концепция или запланированный слой.

Формулировка более высокого уровня зрелости запрещена без исполнимого evidence.
