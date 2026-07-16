# ARTEMIS — DATA DICTIONARY

## Статус

- Тип: canonical semantic data dictionary.
- Версия: 1.0.
- Дата: 2026-07-16.
- Область: Architecture Atlas MVP.
- `DATA_CONTRACT.md` остаётся владельцем export/public artifact mechanics; этот документ владеет business semantics.

## 1. Identity decision

### Canonical public ID

- Формат: UUID v4.
- Поле: `id`.
- Создаётся один раз и не изменяется.
- Используется в GeoJSON, URLs, Research Slices, Relations и Stories.

### Source record ID

- Поле: `source_record_id`.
- Для Airtable содержит record ID вида `rec...`.
- Является техническим provenance identifier, но не public canonical ID.

### Migration alias

- Поле/артефакт: `legacy_ids` или versioned alias map.
- Используется только для перехода старых `rec...` ссылок.
- Не создаёт второй canonical identity.

Record с отсутствующим или невалидным canonical `id` не публикуется после завершения migration window.

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

Source подтверждает факт, датировку, координату или relation.

Обязательные поля:

- `id`;
- `url` или библиографический locator;
- `title`;
- `author_or_organization`;
- `source_type`;
- `accessed_at`, где применимо;
- `review_status`.

`license` у Source не заменяет media license. Лицензия страницы также не должна автоматически приписываться фактам.

Рекомендуемые роли link:

- `general_reference`;
- `date_evidence`;
- `coordinate_evidence`;
- `description_evidence`;
- `relation_evidence`.

## 5. Media

Обязательные поля:

- `id`;
- `asset_url` — прямой URL пригодного для отображения ресурса;
- `source_page_url`;
- `creator`;
- `license`;
- `attribution_text`;
- `media_type`;
- `review_status`.

HTML page URL, например Commons `wiki/File:...`, не считается `asset_url`.

## 6. Relation

Relation — доказательное утверждение между двумя Features.

Обязательные поля:

| Поле | Семантика |
|---|---|
| `id` | UUID v4 relation ID |
| `source_feature_id` | canonical Feature ID |
| `target_feature_id` | canonical Feature ID |
| `relation_type` | тип связи из allowlist |
| `description` | краткое sourced explanation |
| `epistemic_status` | `fact`, `interpretation`, `hypothesis` |
| `confidence` | controlled confidence label |
| `source_ids` | evidence Sources |
| `valid_from`, `valid_to` | optional temporal applicability |
| `review_status` | обязательный editorial status |

Начальный relation type allowlist:

- `influenced`;
- `inspired_by`;
- `same_movement`;
- `designed_by`;
- `reconstructed_from`;
- `located_in`;
- `part_of`.

Новый тип добавляется только после semantic review.

## 7. Similarity

Similarity — вычисляемая близость по слою, времени, географии или признакам. Она не является Relation.

UI обязан маркировать similarity как «Похожие объекты» и при необходимости объяснять критерий. Similarity не сохраняется в canonical Relation table без редакционного review и sources.

## 8. Semantic validation gate

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

Warnings должны появляться при:

- всех координатах одного confidence level;
- отсутствии tags/classification depth;
- слабом или единственном general-purpose source;
- large temporal range без пояснения;
- missing media у ключевого Feature.

## 9. ETL write-back truth

Поле не должно описываться как автоматически заполняемое ETL, если pipeline фактически не выполняет write-back.

Допустимы два режима:

1. ETL действительно записывает `etl_status`, errors, version и timestamps обратно в source system.
2. Эти значения существуют только в export artifacts, а source schema/documentation прямо это указывает.

Смешанный или неявный режим запрещён.
