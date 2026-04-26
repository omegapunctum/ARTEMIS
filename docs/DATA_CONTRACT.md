# ARTEMIS Data Contract

## Статус документа

- Тип: canonical data contract document
- Статус: active
- Роль: source of truth для ETL/data/public map contract, release artifact semantics и runtime data boundaries
- Scope: Airtable curated source → ETL/export → checked-in `data/*` → public map runtime

---

## 1. Contract ownership

ARTEMIS data contract is owned by the checked-in ETL/export pipeline and canonical documentation layer.

Owner chain:
1. Airtable is the curated editorial source.
2. `scripts/export_airtable.py` validates and exports curated source records.
3. `data/*` stores checked-in release artifacts.
4. `data/features.geojson` is the only canonical public map dataset.
5. frontend public map bootstrap reads `data/features.geojson` by default.
6. runtime API routes must not replace the published public dataset.

Rule:
- any change to source fields, validation semantics, release artifact structure, or public map payload must update this document and the relevant ETL/check code in the same change cycle.

---

## 2. Canonical public map source

Canonical public map dataset:
- `data/features.geojson`

Supporting release artifacts:
- `data/features.json`
- `data/export_meta.json`
- `data/rejected.json`

Diagnostic artifacts:
- `data/validation_report.json`
- `data/export_errors.log`

Rules:
- `data/features.geojson` is the production-default public source for map rendering.
- `data/features.json` is a supporting/raw validated artifact, not the public source of truth.
- `export_meta.json` and `rejected.json` are release-quality and diagnostic artifacts.
- diagnostic artifacts do not become competing source-of-truth layers unless release gate explicitly depends on them.

---

## 3. Release artifact contract

Required release artifacts:
- `data/features.geojson`
- `data/features.json`
- `data/export_meta.json`
- `data/rejected.json`

Release gate rules:
- required artifacts must exist;
- `data/features.geojson` must be valid JSON;
- `data/features.geojson.type` must be `FeatureCollection`;
- `data/features.geojson.features` must be a non-empty array;
- `data/features.json` must be an array;
- `records_exported` in `data/export_meta.json` must match:
  - number of records in `data/features.json`;
  - number of features in `data/features.geojson.features`;
- `data/rejected.json` must be an array;
- if `records_rejected` exists in `export_meta.json`, it must match `len(data/rejected.json)`;
- if `records_total_source` exists in `export_meta.json`, it must equal exported plus rejected records;
- release gate blocks on missing artifacts, mismatched record counts, invalid warning categories, warning threshold violations, or invalid public GeoJSON payload.

Current warning policy:
- `warning_categories.expected_fallback` must be an integer and must not exceed the release-check threshold;
- `warning_categories.data_quality` must be an integer and must not exceed the release-check threshold;
- raw source diagnostic metadata alone is not release-gating unless ETL converts it into release warnings or rejections.

---

## 4. Public GeoJSON schema

`data/features.geojson` must follow this baseline shape:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "string",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {}
    }
  ]
}
```

Geometry rules:
- only `Point` geometry is accepted in the current public map baseline;
- coordinates order is `[longitude, latitude]`;
- longitude and latitude must be numeric;
- longitude must be within `[-180, 180]`;
- latitude must be within `[-90, 90]`;
- features without valid geometry must not enter `data/features.geojson` as public map features.

Feature identity rules:
- `Feature.id` must be stable for the exported record;
- `properties.id` must match the exported feature identity;
- `properties.canonical_publish_id` is the canonical publish identity when present;
- `properties.airtable_record_id` tracks Airtable origin when present;
- `properties.origin_key` is the source-origin key used to preserve traceability.

---

## 5. Public feature properties schema

Current baseline properties observed in the public artifact:

| Field | Type | Required | Role |
|---|---:|---:|---|
| `id` | string | yes | public feature/source identity |
| `normalized_id` | string/null | no | normalized stable id if available |
| `canonical_publish_id` | string/null | yes | canonical publish identity |
| `airtable_record_id` | string/null | no | Airtable record traceability |
| `external_id` | string/null | no | external/source-system id |
| `source_draft_id` | string/null | no | draft-origin traceability for moderated records |
| `origin_key` | string/null | yes | source-origin key |
| `layer_id` | string | yes | layer/category id used by UI filters/layers |
| `layer_type` | string/null | no | semantic layer type, e.g. architecture |
| `name_ru` | string | yes | Russian display name |
| `name_en` | string/null | no | English display name |
| `date_start` | string/number | yes | start year/date value for timeline filtering |
| `date_construction_end` | string/number/null | no | optional construction end date |
| `date_end` | string/number/null | no | end year/date value |
| `longitude` | number | yes | duplicated longitude for property-level consumers |
| `latitude` | number | yes | duplicated latitude for property-level consumers |
| `influence_radius_km` | number/null | no | map/context radius |
| `title_short` | string/null | no | compact title/subtitle |
| `description` | string/null | no | public description |
| `image_url` | string/null | no | public image/source URL |
| `source_url` | string/null | no | public source/provenance URL |
| `source_license` | string/null | no | source/media license label |
| `coordinates_confidence` | string/null | no | confidence class for coordinates |
| `coordinates_source` | string | yes | source label from controlled allowlist |
| `sequence_order` | number/null | no | optional sequence ordering |
| `tags` | array | no | tag list |
| `validated` | boolean | yes | ETL validation status for exported record |
| `date_valid` | boolean | yes | date validation status |
| `has_geometry` | boolean | yes | geometry validation status |

Required-for-public baseline:
- identity: `id`, `canonical_publish_id`, `origin_key`;
- display: `name_ru`;
- map: `longitude`, `latitude`, valid Point geometry;
- filtering: `layer_id`, `date_start`;
- provenance/quality: `coordinates_source`, `validated`, `date_valid`, `has_geometry`.

Optional fields may be `null` or absent only if frontend/runtime consumers handle that absence explicitly.

---

## 6. Date contract

Current baseline accepts signed or zero-padded year-like values as strings or numeric values after ETL normalization.

Rules:
- BCE dates may be represented as negative year values, e.g. `-2589`;
- year strings may be zero-padded in source/export, e.g. `0532`;
- `date_start` is required for public timeline participation;
- `date_end` may be null only when the record represents a point-like date or the end date is unknown;
- `date_valid=true` means the ETL accepted the date payload for public export.

Frontend must not assume all dates are modern positive years.

---

## 7. coordinates_source allowlist

Allowed values (curated Airtable enum + ETL allowlist):

- UNESCO
- Britannica
- Official Site
- Vatican
- Pompidou Site
- Wikipedia
- Pleiades
- GBIF
- IUCN
- expert estimate
- PBS
- Dezeen
- Saylor

Synchronization rule:
- Airtable enum MUST be synchronized with the ETL allowlist.
- Adding a new `coordinates_source` value in Airtable requires updating ETL allowlist/normalization first.
- Otherwise records with the new value are rejected as `invalid_coordinates_source`.

---

## 8. Validation and rejection semantics

A source record may be exported only if it satisfies the current ETL validation contract.

Exported public records must satisfy:
- valid identity;
- valid `layer_id`;
- valid coordinates;
- valid geometry;
- valid or accepted date payload;
- accepted `coordinates_source`;
- required display fields for public UI;
- no release-blocking data-quality warnings.

Rejected records:
- must be written to `data/rejected.json`;
- must include enough diagnostic information to identify the failed source record and reason;
- must be counted by `records_rejected` when that field exists in `export_meta.json`.

Release-quality warnings:
- must be aggregated in `export_meta.json.warning_categories` when they affect release policy;
- must not be inferred directly from raw Airtable-only fields unless ETL converts them into release warnings.

---

## 9. Raw/source diagnostics vs release-quality signals

Clarification:
- `data/features.json` is a raw/supporting source artifact and may include source-side diagnostic metadata from Airtable.
- raw diagnostic metadata, including `fields.id_status` when present, is not release-gating by itself.
- release warnings/rejections are derived from ETL validation/export pipeline signals, especially `export_meta.json` and `rejected.json`.
- documentation, release gate, and audits must not treat raw source metadata as final release truth unless the ETL pipeline has promoted it into release-quality signals.

---

## 10. Runtime map feed boundary

Boundary rules:
- canonical public map dataset remains `data/features.geojson`;
- `GET /api/map/feed` is an auxiliary, non-canonical runtime support/read-model endpoint for authenticated UI/runtime scenarios;
- current baseline implementation of `/api/map/feed` must be treated as a temporary MVP adapter, not as a production-grade public read model over the published dataset;
- `/api/map/feed` currently serves internal runtime feed semantics without transitional/mock-backed place payloads; any future entity expansion must remain internal/non-canonical and be introduced explicitly;
- frontend main map bootstrap path must keep `data/features.geojson` as default source;
- `/api/map/feed` may be used only as an explicit internal runtime toggle/path;
- runtime consumers must not treat `/api/map/feed` as a replacement for published `/data/*` artifacts or as a stable public export contract.

---

## 11. Upload runtime / file-serving boundary

Boundary rules:
- upload API surface is runtime-only and consists of `POST /api/uploads` and `POST /api/uploads/image`;
- public serving of uploaded files is static via `/uploads/*` mount;
- `/uploads/*` serving for user-uploaded files includes explicit baseline response-header policy at runtime;
- baseline serving-policy headers for `/uploads/*` are `X-Content-Type-Options: nosniff`, `Content-Disposition: inline`, and `Cache-Control: no-store`;
- upload acceptance validates declared upload metadata (`content_type`) and applies server-side magic-bytes signature checks for supported image types (`PNG`, `JPEG/JPG`, `WEBP`);
- when declared type is allowlisted but the detected file signature does not match that declared type, the upload is rejected;
- upload acceptance (runtime API) and uploaded-file delivery (static path) are separate contract surfaces and must not be conflated;
- there is no contract route `GET /api/uploads/{filename}` in the current baseline;
- frontend must treat backend-returned `url` from upload responses as source of truth for file access paths.

---

## 12. Change-control rule

Any change to this contract must define:
- affected source fields;
- affected ETL code;
- affected checked-in `data/*` artifact shape;
- affected frontend/runtime consumers;
- release-check impact;
- migration or compatibility behavior for existing records;
- required documentation sync.

A data-contract change is not complete until:
- ETL/export behavior is updated;
- release checks are updated if needed;
- checked-in data artifacts match the new contract;
- this document is updated;
- relevant tests pass.
