# ARTEMIS — SEMANTIC DATA GATE v1

## Статус

- Issue: `#284`.
- Статус: implementation candidate; pending PR review and merge.
- Snapshot: 2026-07-21, current pilot export at 19 Features.
- Scope: Airtable export diagnostics, checked-in cross-artifact validation, warning budgets and CI/release enforcement.

## 1. Verified pre-implementation gap

До этого change set ETL проверял отдельные records, но successful checked-in release не доказывал semantic publish readiness:

- `release_check.py` проверял identity/count/JSON structure, но не Source/Media/Relation cross-references;
- `validation_report.json.errors` не был обязательным input release gate;
- `rejected.json` мог быть непустым при structural PASS;
- все 26 Layers публиковались, включая 7 enabled empty Layers;
- 3 Features без reviewed Media сохраняли Commons HTML page в compatibility `image_url`;
- all-exact coordinate confidence, пустые tags, one-source depth и broad dates не становились release-quality warnings;
- warning ceiling был агрегированным и не различал известный pilot debt от нового drift.

## 2. Gate architecture

### ETL owner

`scripts/export_airtable.py`:

- продолжает валидировать source records;
- трактует unreviewed active Feature как blocking error;
- очищает public `image_url`, если нет reviewed primary Media;
- исключает disabled и enabled-empty Layers из public `layers.json`;
- создаёт semantic quality warnings;
- пишет `validation_report.json` schema version 2 и `export_meta.semantic_gate`.

### Shared semantic owner

`scripts/semantic_data_gate.py`:

- владеет warning reasons/budgets;
- выбирает publishable Layers;
- выводит corpus-quality warnings;
- повторно проверяет checked-in Features, Layers, Sources, Media and Relations как одну связанную release graph;
- не доверяет одному только ETL status или `validated=true`.

### Release owner

`scripts/release_check.py`:

- сохраняет structural checks;
- запускает semantic gate до backend/frontend/PWA checks;
- блокирует release при blocking errors, rejected records, invalid rights/evidence/review semantics, projection drift, invalid dates/geometry or warning-budget drift.

## 3. Blocking contract

Release блокируется при любом из условий:

- missing/non-v4/duplicate canonical Feature or Relation ID;
- unreviewed active or rejected Feature;
- Feature without reviewed primary Source;
- missing/invalid Source reference or Source controlled vocabulary;
- Media page URL used as `asset_url`;
- Media without creator, allowed license, source page or attribution;
- Feature `image_url` not derived from reviewed primary Media;
- published disabled or empty Layer;
- invalid coordinate range or inconsistent date order;
- Relation without valid endpoints, evidence Source, role or claim note;
- Relation/Feature projection mismatch;
- validation report contains a blocking error;
- new/unbudgeted warning reason or warning count above its ceiling.

## 4. Warning contract

Warnings are actionable pilot debt, not blocking errors while inside the approved ceiling.

| Reason | Current | Ceiling | Meaning |
|---|---:|---:|---|
| `enabled_empty_layer_excluded` | 7 | 7 | Source Layer enabled but excluded because it has no published Feature |
| `missing_primary_media` | 3 | 3 | Feature is publishable without an image; `image_url=null` |
| `uniform_coordinates_confidence` | 1 dataset warning | 1 | All 19 Features use `exact` confidence |
| `missing_classification_depth` | 1 dataset warning | 1 | Pilot Features have no tags/classification depth |
| `weak_source_depth` | 1 dataset warning | 1 | Pilot Features have only one reviewed Source each |
| `broad_temporal_range` | 1 | 1 | Stonehenge range exceeds 500 years |

Current total: `14 warnings / 0 blocking errors`.

The ceilings are regression limits, not targets. Cleanup reduces them; adding a new warning requires an explicit contract change rather than silent acceptance.

## 5. Artifact contract

### `data/validation_report.json`

- `schema_version=2`;
- `status=ready|ready_with_warnings|blocked`;
- `blocking_errors_count` and `blocking_errors`;
- `warnings_count` and `warnings`;
- compatibility aliases `errors_count` and `errors`, equal to blocking-error fields.

### `data/export_meta.json`

- `layers_total_source`;
- `layers_published`;
- `enabled_empty_layers_excluded`;
- exact `warning_stats` and `warning_categories`;
- `semantic_gate.status`, `.blocking_errors`, `.warnings`.

### Public artifacts

- `layers.json` contains 19 enabled populated Layers, not all 26 Airtable Layers;
- `features.geojson` keeps all 19 valid Features;
- Burj Khalifa, Villa Savoye and Centre Pompidou have `image_url=null` until reviewed Media rights exist;
- `sources.json`, `media.json`, `relations.json` remain reviewed-only canonical projections.

## 6. CI and export behavior

- release workflow runs structural + semantic checks on every push/PR;
- ETL dry-run validates schema version 2 and zero blocking errors;
- scheduled Airtable export runs the release gate before export and again on newly exported artifacts;
- a post-export semantic failure prevents the data commit/push;
- full regression remains separate from release-gate semantics.

## 7. Acceptance mapping

- [x] validation report separates blocking errors from warnings;
- [x] CI/export workflow fails on blocking semantic errors;
- [x] invalid UUID and HTML-image fixtures are covered by tests;
- [x] enabled empty Layers are excluded and diagnosed;
- [x] current Airtable defects produce truthful diagnostics before cleanup;
- [x] release documentation describes semantic gate and warning budgets.

## 8. Recovery and future cleanup

- remove a warning budget only after the corresponding data cleanup is exported and checked in;
- never raise a ceiling merely to make CI green without a governance decision;
- if the semantic module cannot read or reconcile artifacts, release fails closed;
- source Airtable records remain unchanged by this implementation batch;
- future corpus expansion must keep warnings bounded by reason, not hide them in an aggregate count;
- `ready_with_warnings` must not be described as full corpus maturity or production readiness.
