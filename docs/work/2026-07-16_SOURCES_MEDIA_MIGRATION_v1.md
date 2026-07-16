# ARTEMIS — SOURCES / MEDIA MIGRATION v1

## Статус

- Issue: `#283`.
- Статус: contract and audit complete; Airtable/code migration not started.
- Snapshot date: 2026-07-16.
- Scope: normalize factual Sources, display Media, per-link evidence/presentation semantics and compatibility projections for the 19-Feature Architecture Atlas pilot.

Этот документ фиксирует план до любых schema/data writes. Он не утверждает, что target fields или artifacts уже существуют.

## 1. Verified current state

Read-only audit of Airtable base `Artemis_Base` and checked-in `data/features.geojson` found:

| Check | Result |
|---|---:|
| Active/validated Features | 19 |
| Features with `source_url` | 19 |
| Sources records | 10 |
| Sources with `url` | 0 |
| Sources linked to Features | 0 |
| Media records | 0 |
| Features with `image_url` | 19 |
| Direct displayable Feature image URLs | 0 |
| Wikimedia Commons HTML file pages used as `image_url` | 19 |

All ten Sources contain an ID, title and legacy `license=CC BY-SA`, but no URL. This license value is not trustworthy as Media rights metadata and MUST NOT be copied automatically. Current `Features.source_license` is likewise conflated and cannot prove either factual-source terms or image rights.

The current exporter reads only `Features` and `Layers`; it does not fetch, validate or publish `Sources` or `Media`.

## 2. Contract decisions

1. Source supports a factual claim; Media describes a displayable asset and its rights.
2. Existing stable `src_*` Source IDs are preserved. Nine missing pilot Sources receive deterministic `src_*` IDs listed below.
3. Source roles belong to the Feature↔Source association, not to Source globally.
4. Media display role and ordering belong to the Feature↔Media association.
5. Only `reviewed` records and links can enter public artifacts.
6. Commons `wiki/File:*` URLs are stored as `source_page_url`, never as `asset_url`.
7. Creator, exact license/version and attribution are verified from the media source page; they are never inferred from `Features.source_license`.
8. Legacy `source_url` and `image_url` remain temporary derived projections for old UI consumers. `source_license` is deprecated and is not a Media license.
9. #283 prepares Sources for Relation evidence. Physical Relation↔Source links are added with the Relations table in #282.

## 3. Target Airtable schema

### Sources

Required fields: `id`, `url` or `bibliographic_locator`, `title`, `author_or_organization`, `source_type`, `review_status`. Optional: `accessed_at`, `content_license`, `notes`.

### Media

Required fields: `id`, `asset_url`, `source_page_url`, `creator`, `license`, `license_url` where applicable, `attribution_text`, `media_type`, `review_status`.

### FeatureSources

Required fields: `feature`, `source`, `roles`, `is_primary`, `review_status`. Optional: `claim_note`.

Exactly one reviewed primary Source is required per published Feature. Multiple roles are allowed on one link.

### FeatureMedia

Required fields: `feature`, `media`, `display_role`, `sort_order`, `review_status`. Optional: `caption`.

At most one reviewed `primary` Media link is allowed per Feature.

## 4. Deterministic Source migration matrix

Each Feature receives one initial `general_reference` link. Additional roles require editorial verification and are not inferred from current labels.

| Feature | Source ID | Action | Source locator |
|---|---|---|---|
| Бурдж-Халифа | `src_burj_khalifa_official` | reuse + complete | `https://www.burjkhalifa.ae/en/` |
| Вилла Савой | `src_villa_savoye_wikipedia` | reuse + complete | `https://en.wikipedia.org/wiki/Villa_Savoye` |
| Собор Святого Петра | `src_st_peters_basilica_wikipedia` | reuse + complete | `https://en.wikipedia.org/wiki/St._Peter%27s_Basilica` |
| Шартрский собор | `src_chartres_unesco` | reuse + complete | `https://whc.unesco.org/en/list/81/` |
| Центр Жоржа Помпиду | `src_centre_pompidou_wikipedia` | reuse + complete | `https://en.wikipedia.org/wiki/Centre_Pompidou` |
| Пантеон (Париж) | `src_pantheon_paris_wikipedia` | reuse + complete | `https://en.wikipedia.org/wiki/Panth%C3%A9on` |
| Пантеон (Рим) | `src_pantheon_rome_wikipedia` | reuse + complete | `https://en.wikipedia.org/wiki/Pantheon,_Rome` |
| Собор в Сантьяго-де-Компостела | `src_santiago_cathedral_official` | reuse + complete | `https://catedraldesantiago.es/en/cathedral/` |
| Крайслер-билдинг | `src_chrysler_building_wikipedia` | reuse + complete | `https://en.wikipedia.org/wiki/Chrysler_Building` |
| Версальский дворец | `src_versailles_wikipedia` | reuse + complete | `https://en.wikipedia.org/wiki/Palace_of_Versailles` |
| Альгамбра | `src_alhambra_wikipedia` | create | `https://en.wikipedia.org/wiki/Alhambra` |
| Еврейский музей в Берлине | `src_jewish_museum_berlin_official` | create | `https://www.jmberlin.de/en/libeskind-building` |
| Парфенон | `src_parthenon_wikipedia` | create | `https://en.wikipedia.org/wiki/Parthenon` |
| Стоунхендж | `src_stonehenge_unesco` | create | `https://whc.unesco.org/en/list/373/` |
| Великая пирамида Гизы | `src_great_pyramid_wikipedia` | create | `https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza` |
| Каса-Батльо | `src_casa_batllo_official` | create | `https://www.casabatllo.es/en/` |
| Королевский национальный театр | `src_royal_national_theatre_wikipedia` | create | `https://en.wikipedia.org/wiki/Royal_National_Theatre` |
| Великий зиккурат в Уре | `src_ziggurat_ur_britannica` | create | `https://www.britannica.com/topic/ziggurat-at-Ur` |
| Собор Святой Софии | `src_hagia_sophia_wikipedia` | create | `https://en.wikipedia.org/wiki/Hagia_Sophia` |

No Source is marked `reviewed` until title, organization/type and locator support have been checked.

## 5. Media migration rule

For each of the 19 current Commons file-page URLs:

1. keep the existing URL as `Media.source_page_url` candidate;
2. open the page and verify that the referenced file exists;
3. resolve a direct HTTPS asset URL suitable for browser display;
4. record creator exactly as credited by the source page;
5. record exact license/version and canonical license URL;
6. write a complete attribution string;
7. create a Media record with `review_status=draft`;
8. create the FeatureMedia link;
9. mark both Media and link `reviewed` only after a direct-load and metadata check;
10. derive legacy `image_url` from reviewed primary Media.

A missing, deleted, non-displayable or ambiguously licensed file is not migrated. The Feature keeps no primary Media until a replacement is reviewed.

## 6. Execution order and recovery

### Batch A — schema

Add target fields and association tables without deleting or renaming legacy fields. Record all created table/field IDs in the execution evidence section.

### Batch B — Sources

Complete the ten existing records, create nine missing records, then create 19 FeatureSources links as `draft`. Verify uniqueness and locator coverage before changing review status.

### Batch C — Media

Research and create Media/FeatureMedia records in small reviewed batches. Do not bulk-copy current license values.

### Batch D — ETL and artifacts

Fetch all normalized tables, validate cross-references and publish `sources.json`, `media.json`, `source_refs` and `media_refs`. Keep compatibility projections until frontend consumers migrate.

### Recovery

- Schema additions are additive and leave current export behavior intact.
- Before any record update, save a record-ID/old-values snapshot in this document or a checked-in machine-readable migration artifact.
- If a batch fails validation, leave its new records/links as `draft`; the current public export remains unchanged.
- Legacy fields are removed only in a later cleanup after normalized artifacts and frontend tests are green.

## 7. Documentation-phase acceptance

- [x] current Airtable and checked-in artifact counts verified;
- [x] Source/Media semantic ownership separated;
- [x] per-link role model defined;
- [x] 19-Feature Source migration matrix defined;
- [x] Media verification procedure defined;
- [x] compatibility and recovery rules defined;
- [ ] Airtable schema created;
- [ ] Source/Media data migrated and reviewed;
- [ ] ETL/public artifacts implemented;
- [ ] semantic validation and frontend contract tests green.

## 8. Execution evidence

Not started. This section is populated only by applied Airtable and code migrations.
