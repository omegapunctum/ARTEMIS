# ARTEMIS — DATA DICTIONARY

## Статус

- Тип: canonical semantic data dictionary.
- Версия: 2.0.
- Дата: 2026-07-26.
- Область: Architecture Atlas MVP.
- `DATA_CONTRACT.md` остаётся владельцем export/public artifact mechanics; этот документ владеет business semantics.

## 1. Identity decision

### Canonical public ID

- Формат: UUID v4.
- Поле: `id`.
- Создаётся один раз и не изменяется.
- Используется в GeoJSON, URLs, Investigations/revisions, Relations и compatibility Research Slices.

### Source record ID

- Поле: `source_record_id`.
- Для Airtable содержит record ID вида `rec...`.
- Является техническим provenance identifier, но не public canonical ID.

### Migration alias

- Поле: `properties.legacy_ids` в public GeoJSON.
- Артефакт: `data/id_aliases.json`, schema version `1`.
- Используется только для перехода старых `rec...` ссылок.
- Карта также сохраняет 11 исторических псевдо-UUID, заменённых в migration v1.
- Каждый alias обязан указывать на существующий опубликованный UUID v4; alias не может быть canonical ID.
- Не создаёт второй canonical identity.

Record с отсутствующим или невалидным canonical `id` не публикуется. Migration window закрыт: compatibility поддерживается только чтением aliases, но не публикацией legacy ID.

## 2. Feature

Обязательные поля MVP:

| Поле | Семантика |
|---|---|
| `id` | UUID v4 canonical ID |
| `source_record_id` | технический ID source system |
| `name_ru`, `name_en` | display names |
| `feature_type` | `architecture_object` в vertical MVP |
| `layer_id` | reviewed непустой Layer |
| `date_start`, `date_end` | temporal extent с documented convention |
| `latitude`, `longitude` | point coordinate baseline |
| `coordinates_source` | источник координат |
| `coordinates_confidence` | `exact`, `approximate`, `derived`, `unknown` |
| `description` | sourced factual summary либо явно marked interpretation |
| `source_ids` | ссылки на canonical Sources |
| `media_ids` | ссылки на Media |
| `review_status` | `draft`, `reviewed`, `rejected` |
| `is_active` | publish eligibility после review |
| `updated_at` | timestamp последнего semantic update |

`validated=true` без пройденного semantic gate не считается достаточным publish evidence.

## 3. Layer

Layer описывает предметную классификацию или curated grouping.

Обязательные поля:

- `layer_id` — стабильный semantic ID;
- `name_ru`, `name_en`;
- `layer_kind` — style, period, region или curated theme;
- `enabled`;
- display color/icon, если они используются UI.

Enabled Layer без опубликованных Features запрещён в public filter set.

## 4. Source

Source — provenance/bibliographic unit. Source сам по себе не подтверждает Feature или Relation «в целом»; он связан с конкретным Claim через EvidenceLink.

Source не является изображением и не наследует лицензию Media. Его `id` — стабильная уникальная строка, которая не меняется при исправлении title или locator. Существующие `src_*` IDs сохраняются, если они уникальны; новые IDs создаются один раз в том же namespace.

Обязательные поля:

- `id`;
- `url` или библиографический locator;
- `title`;
- `author_or_organization`;
- `source_type`;
- `accessed_at`, где применимо;
- `review_status`.

`source_type` MVP allowlist:

- `primary`;
- `official`;
- `academic`;
- `institutional`;
- `reference`;
- `other`.

`review_status` allowlist для Source и Media: `draft`, `reviewed`, `rejected`.

Legacy `Sources.license` не является media license и не участвует в publish eligibility. Если необходимо хранить лицензию или terms самой публикации, это отдельное optional поле `content_license`; оно не переносится в Media автоматически.

Current compatibility link roles:

- `general_reference`;
- `date_evidence`;
- `coordinate_evidence`;
- `description_evidence`;
- `relation_evidence`.

Роль принадлежит связи Source с Feature/Relation, а не самой Source. В current Airtable Feature evidence хранится в `FeatureSources`, relation evidence — в `RelationSources`.

Эти association tables являются compatibility baseline. `claim_note` не заменяет first-class Claim, а link role не доказывает, что Source поддерживает каждое поле Feature/Relation.

### 4.1 Claim target

Claim — атомарное утверждение.

Target fields:

- `id`;
- `statement`;
- subject/context refs;
- `claim_kind`;
- `origin`;
- `review_state`;
- `confidence`;
- `evidence_state`;
- uncertainty records;
- created/updated metadata.

Target model определяется `EPISTEMIC_CONTRACT.md`. First-class Claim schema ещё не реализована в checked-in artifacts.

### 4.2 EvidenceLink target

EvidenceLink связывает ровно один Claim с ровно одним Source.

Target fields:

- `claim_id`;
- `source_id`;
- `locator`;
- `relation_to_claim`: `supports`, `challenges`, `contextualizes`;
- `evidence_strength`: `direct`, `indirect`, `background`;
- `review_state`;
- reviewer/timestamps.

Миграция из current `FeatureSources`/`RelationSources` не может выдумывать Claim, locator или relation-to-claim. Неполные legacy links должны оставаться явно неполными.

## 5. Media

Media — отображаемый ресурс и его rights/attribution record. Media не считается factual Source только потому, что изображает объект.

Обязательные поля:

- `id`;
- `asset_url` — прямой URL пригодного для отображения ресурса;
- `source_page_url`;
- `creator`;
- `license`;
- `license_url`, если лицензия требует ссылку;
- `attribution_text`;
- `media_type`;
- `review_status`.

HTML page URL, например Commons `wiki/File:...`, не считается `asset_url`.

`media_type` MVP allowlist: `image`, `map`, `drawing`, `diagram`, `document`.

Связь Media с Feature хранится в association table `FeatureMedia` с полями `feature`, `media`, `display_role`, `sort_order`, `caption`, `review_status`. `display_role` MVP allowlist: `primary`, `gallery`, `context`, `detail`.

Public Feature содержит `source_ids`, `media_ids`, а также link metadata `source_refs` и `media_refs`. Legacy `source_url` и `image_url` допускаются только как временные compatibility projections из primary reviewed Source/Media; `source_license` deprecated и не может использоваться как Media license.

## 6. Relation

Relation — structured Claim между двумя Entities/Features. Current public v1 relation artifact является compatibility representation без first-class Claim/EvidenceLink axes.

В v1 публичный predicate всегда читается буквально как:

`source_feature_id relation_type target_feature_id`.

Направление нельзя выводить из порядка записей Airtable или положения объекта в UI. Для симметричных типов endpoints сохраняются в лексикографическом порядке UUID, чтобы одна связь не могла существовать в двух направлениях.

Обязательные поля:

| Поле | Семантика |
|---|---|
| `id` | UUID v4 relation ID |
| `source_feature_id` | canonical Feature ID |
| `target_feature_id` | canonical Feature ID |
| `relation_type` | тип связи из allowlist |
| `description` | краткое sourced explanation |
| `epistemic_status` | compatibility projection: `fact`, `interpretation`, `hypothesis` |
| `confidence` | `high`, `medium`, `low` |
| `source_ids` | reviewed evidence Sources, derived from `RelationSources` |
| `valid_from`, `valid_to` | optional temporal applicability |
| `review_status` | обязательный editorial status |

Executable current Feature↔Feature allowlist:

- `influenced`;
- `inspired_by`;
- `same_movement`;
- `reconstructed_from`;
- `part_of`.

Directionality:

| `relation_type` | Чтение | Directionality |
|---|---|---|
| `influenced` | source Feature повлиял на target Feature | directed |
| `inspired_by` | source Feature был вдохновлён target Feature | directed |
| `same_movement` | оба Feature относятся к одному документированному движению | symmetric; UUIDs sorted |
| `reconstructed_from` | source Feature реконструирован на основании target Feature | directed |
| `part_of` | source Feature является частью target Feature | directed |

Concept Lock v2 boundary:

- `same_movement` is legacy documented shared-classification projection;
- it does not count as substantive historical Relation or relation-value evidence;
- new shared-classification content should be modelled as two ClassificationAssertions to a Movement/Layer;
- current records remain readable until explicit data migration;
- they must not be auto-converted to `influenced`, `derived_from` or another predicate.

Target substantive Feature↔Feature families include:

- `influenced`;
- `inspired_by`;
- `modelled_on`;
- `derived_from`;
- `adapted_from`;
- `reconstructed_from`;
- `part_of`.

New executable types require schema/ETL/UI migration before use.

`designed_by` и `located_in` требуют Person/Place targets и не входят в Feature↔Feature MVP. Они могут быть добавлены только вместе с canonical entity identity, а не как строки или фиктивные Features.

Current evidence хранится в `RelationSources`: `id`, `relation`, `source`, `roles`, `claim_note`, `review_status`. Каждая строка обязана ссылаться ровно на одну Relation и один Source. Reviewed current Relation обязана иметь минимум одну reviewed связь с reviewed Source и ролью `relation_evidence`.

Для validation-ready target этого недостаточно: RelationClaim требует locator, `supports/challenges/contextualizes`, evidence strength и independent epistemic dimensions.

Public `relations.json` содержит только reviewed Relations с валидными canonical Feature UUIDs и reviewed evidence. Каждый `source_refs` элемент включает canonical `source_id`, `roles`, `claim_note` и денормализованные `title`/`url` для отображения evidence без второго runtime-запроса. Feature projections могут содержать только `relation_ids`; полный description/status/evidence contract принадлежит `relations.json`.

## 7. Similarity

Similarity — вычисляемая близость по слою, времени, географии или признакам. Она не является Claim, evidence или Relation и не получает canonical Relation ID.

UI обязан маркировать Similarity как «Похожие объекты» и показывать критерии (`same_layer`, `date_overlap`, `date_distance`, а позже — `geographic_distance` or feature similarity). Similarity может стать только candidate RelationClaim после явной формулировки predicate, review and EvidenceLinks; сам score не является evidence.

## 8. Semantic validation gate

Implementation status 2026-07-21: executable ETL/release contract merged in #302 (`d4e8b53`). Canonical enforcement owners are `scripts/semantic_data_gate.py`, `scripts/export_airtable.py`, `scripts/release_check.py` and `data/validation_report.json` schema version 2.

### Content profile

`data/content_profile.json` schema version 1 is derived technical release evidence for the legacy comparison-corpus envelope. It records current Feature/cohort/Relation counts and Source/Media/link coverage against 30–40 / 6–8 / 12–20.

Its `comparison_ready` status:

- means the executable legacy envelope is internally complete;
- does not mean three deep research modules are ready;
- does not exclude `same_movement` from its historical Relation count;
- does not authorize external product validation.

Missing or stale profile still blocks release. Product-validation readiness belongs to `PRODUCT_VALIDATION_PLAN.md`.

Публикация блокируется при:

- invalid/missing canonical ID;
- missing required source;
- invalid coordinate range;
- unknown controlled vocabulary value;
- relation без evidence source;
- Media без direct asset URL, license или attribution;
- enabled empty Layer;
- inconsistent dates;
- unreviewed active Feature/Relation;
- duplicate canonical ID.

Техническая реализация также блокирует drift между public artifacts: отсутствующий Source/Media/Relation target, несовпадающие Feature projections, legacy HTML image URL без reviewed Media, непустой `rejected.json`, скрытый blocking error в validation report или неизвестный warning reason.

Enabled empty Layers не входят в public `layers.json`; каждый исключённый Layer остаётся отдельным warning, а количество сверяется с `export_meta.layers_total_source`, `layers_published` и `enabled_empty_layers_excluded`.

Warnings должны появляться при:

- всех координатах одного confidence level;
- отсутствии tags/classification depth;
- слабом или единственном general-purpose source;
- large temporal range без пояснения;
- missing media у ключевого Feature.

Warnings не превращаются в молчаливое разрешение: каждый reason имеет временный pilot ceiling. Превышение ceiling или новый reason блокирует release до исправления данных либо явного governance decision. `ready_with_warnings` означает publish-safe pilot, но не production-grade corpus.

## 9. ETL write-back truth

Поле не должно описываться как автоматически заполняемое ETL, если pipeline фактически не выполняет write-back.

Допустимы два режима:

1. ETL действительно записывает `etl_status`, errors, version и timestamps обратно в source system.
2. Эти значения существуют только в export artifacts, а source schema/documentation прямо это указывает.

Смешанный или неявный режим запрещён.
