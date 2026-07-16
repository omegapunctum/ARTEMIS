# ARTEMIS — SOURCES / MEDIA MIGRATION v1

## Статус

- Issue: `#283`.
- Статус: Airtable schema, reviewed Source batch and ETL implementation complete; Media migration in reviewed batches (`3/19`).
- Snapshot date: 2026-07-16.
- Scope: normalize factual Sources, display Media, per-link evidence/presentation semantics and compatibility projections for the 19-Feature Architecture Atlas pilot.

Документ был создан как pre-write plan и теперь также содержит execution evidence для выполненных schema/data/code batches.

## 1. Verified pre-write baseline

Read-only audit of Airtable base `Artemis_Base` and checked-in `data/features.geojson` before migration found:

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

At the pre-write baseline, the exporter read only `Features` and `Layers`; the implementation evidence below records the normalized exporter added during this migration.

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
- [x] Airtable schema created;
- [x] Source data migrated and reviewed for all 19 pilot Features;
- [ ] Media data migrated and reviewed;
- [x] ETL/public artifacts implemented;
- [x] semantic ETL validation and contract tests green.

## 8. Execution evidence

### Schema batch — 2026-07-16

Additive schema changes were applied without deleting or renaming legacy fields.

- Sources added fields: `bibliographic_locator` (`fldF9ZoG5wqZBhIVC`), `author_or_organization` (`fldGcNldPj3OqarMB`), `source_type` (`fldNYY2VhgSPwgAE5`), `accessed_at` (`fldQWMsgX1uRsh3IU`), `review_status` (`fldO7aJ5wbGOwXNqY`), `content_license` (`fldjfofmSBs05N6Is`), `notes` (`fldpkCTzDWyA5rEBE`).
- Media added fields: `asset_url` (`fldIMbUlIhZfyfFi3`), `source_page_url` (`fldtfoTmUMHUBqkTt`), `creator` (`fldulEr7xy0SN40t5`), `license_url` (`fld6Huddl5Owtgwo8`), `attribution_text` (`fldN9B9jzuoq2BM8N`), `media_type` (`fldYcdNhetS7aj56l`), `review_status` (`fldfKz5wOi58FfIBU`), `notes` (`fldfl9QK2O1ghjxZ9`).
- Created `FeatureSources` (`tblxTjN3tcCo5nxBV`) with Feature link `fldvnWawcWLIDmQ1n` and Source link `fldHu6kWqe0NUjOZD`.
- Created `FeatureMedia` (`tblEqczlCmiIRGGo2`) with Feature link `fldx0fj5FHIQJRFvI` and Media link `fldYXdgPiXx4eR797`.
- Airtable exposed all four relationship fields as `multipleRecordLinks`; ETL must enforce exactly one linked record on each side of an association row.
- Post-write schema read confirmed six tables and reciprocal link fields on Features, Sources and Media.

### Pre-write Sources snapshot

All ten pre-existing Sources had `url=null`, no Media links and legacy `license=CC BY-SA` before the data batch.

| Airtable record ID | Source ID | Existing title |
|---|---|---|
| `recI0DEi5kV2CiEr4` | `src_burj_khalifa_official` | Burj Khalifa — Official Site |
| `recN3jrFPLXO2RDVu` | `src_chartres_unesco` | Chartres Cathedral — UNESCO World Heritage Centre |
| `recUWXGH1KVdDU6oj` | `src_chrysler_building_wikipedia` | Chrysler Building — Wikipedia |
| `recdFbUmncwt9Rih0` | `src_st_peters_basilica_wikipedia` | St. Peter's Basilica — Wikipedia |
| `recdXf8lu5F7qkYqZ` | `src_villa_savoye_wikipedia` | Villa Savoye — Wikipedia |
| `receZjrpka5zGZQn9` | `src_pantheon_paris_wikipedia` | Panthéon — Wikipedia |
| `recf7GLYZro9PxkVH` | `src_versailles_wikipedia` | Palace of Versailles — Wikipedia |
| `rechvy4Rzxfrslujt` | `src_santiago_cathedral_official` | Santiago de Compostela Cathedral — Official Site |
| `recsWHqg2b9gALhS4` | `src_centre_pompidou_wikipedia` | Centre Pompidou — Wikipedia |
| `recstir8wePZAKVIJ` | `src_pantheon_rome_wikipedia` | Pantheon, Rome — Wikipedia |

### Source data batch — 2026-07-16

- Completed the ten existing Sources and created the nine missing records from the deterministic matrix as `draft`.
- Created 19 deterministic FeatureSources rows as `general_reference`, initially `draft`.
- Verified 17 locators by opening the source page directly; the Burj Khalifa official locator was corroborated through the indexed building record and official website reference.
- The legacy Britannica locator for Ziggurat at Ur could not be verified by direct open or search and remains `draft`, non-primary.
- Added reviewed fallback `src_ziggurat_ur_wikipedia` (`recUxWZovAKEt4Dzq`) and reviewed primary link `reckBGcyknAxVlXBI`; no unverifiable claim was promoted.
- Final control read: `20 Sources / 19 reviewed / 1 draft`, `20 FeatureSources / 19 reviewed / 1 draft`.
- Every one of the 19 Features has exactly one reviewed primary Source; missing and duplicate-primary sets are empty.
- No legacy image/license value was promoted automatically into normalized Media.

### ETL and CI batch — 2026-07-16

- Export now reads `Sources`, `Media`, `FeatureSources` and `FeatureMedia` alongside Features/Layers.
- Only reviewed, valid Source/Media records and reviewed association rows enter public artifacts.
- Feature validation blocks missing reviewed Sources, ambiguous primary Sources, duplicate refs and association rows with invalid cardinality.
- `data/sources.json`, `data/media.json`, `source_refs`, `media_refs` and legacy primary projections are generated by the ETL.
- Dry-run completed with `1 Feature / 1 Source / 1 Media / 0 errors`; normalized output assertions were added to CI.
- Focused evidence tests: `31 passed, 10 subtests passed`.
- Repository test suite: `259 passed, 10 subtests passed`; release check passed all gates with the known single-node memory-session warning.

### Media pilot batch 1 — 2026-07-16

- Created 3 reviewed Media records and 3 reviewed primary FeatureMedia links for Stonehenge, Parthenon and Great Pyramid of Giza.
- Every `asset_url` is a direct `upload.wikimedia.org` image, while `source_page_url` preserves the corresponding Commons File page.
- Creator, exact license family/version, license URL and display attribution were verified on each source page.
- IDs: `media_stonehenge_wiscombe_2007`, `media_parthenon_swayne_1978`, `media_great_pyramid_vanderzee_2023`.
- Control read: `3 Media / 3 reviewed`, `3 FeatureMedia / 3 reviewed`; each association has exactly one Feature, one Media and one `primary` role.
- A Burj Khalifa candidate was rejected from this batch because its Commons page carries a UAE freedom-of-panorama warning; this confirms the migration does not treat a photo license alone as sufficient rights evidence.
- Remaining Media scope: 16 Features require separate source and rights review before the migration checklist can be closed.
