# ARTEMIS — Airtable Shadow Curation Schema v1

Status: **COMPLETED PRE-GATE-D EVIDENCE / SHADOW ONLY**  
Date: 2026-08-10  
Issue: #368  
Implementation: PR #369 / merge `db273a525f0f5906c2d9681b561ee17d17d63d60`  
Predecessor: #366 / PR #367  
Parent product contour: #355

## 1. Outcome

An empty Foundation v3 Airtable curation surface now exists alongside the current Architecture Atlas compatibility tables.

This is a **shadow schema**, not a historical corpus and not a new semantic owner.

It does not:

- open Gate D;
- change `docs/project_state.json`;
- import the frozen Leonardo Gate C package;
- make any Gate C Claim reviewed historical truth;
- change public `data/*`;
- change the current Airtable → Architecture Atlas export authority;
- resume #331 Relation semantics;
- make Globe public.

The semantic owner remains `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` and related reviewed repository contracts.

## 2. Live tables

Created in `Artemis_Base` (`appHmf8ubeUF9nfkO`) in dependency order:

| Table | Airtable ID | Records after creation | Role |
|---|---|---:|---|
| `WorldSlices` | `tblBug0vkNAI8DO1R` | 0 | corpus/review boundary |
| `KnowledgeObjects` | `tblffBsDcOZ0HOLfw` | 0 | common Entity/Event/State/Process/Trajectory/Region envelope |
| `ObjectParts` | `tblBH9L9ZcYe8MU6Z` | 0 | trajectory segments, process stages, Region states and reconstruction alternatives |
| `Claims` | `tblOeuGE19Vbg3XLh` | 0 | atomic material assertions |
| `EvidenceLinks` | `tblGqSgg3PBndArk5` | 0 | Claim → Source evidence with locator and explicit relation/strength |
| `Uncertainties` | `tbl370NEfV6TtYiM2` | 0 | first-class material uncertainty |

Existing tables reused narrowly:

- `Sources` / `tblfLhLLhppIywhYM` — stable provenance identity; evidence remains Claim-specific;
- `Layers` / `tblVKoF68mrZ8BM8B` — display/query grouping only;
- `Media` / `tblXWjucWBSa9Go5a` — presentation/rights subsystem only.

No legacy table record value was changed while creating the shadow schema.

## 3. Executable evidence

Repository evidence:

- `fixtures/airtable_curation/v1/schema_contract.json` — executable expected schema;
- `fixtures/airtable_curation/v1/live_schema_snapshot.json` — captured live table/forward-field IDs and verified zero record counts;
- `scripts/validate_airtable_curation_schema.py` — deterministic offline contract/snapshot/lifecycle validator;
- `tests/test_airtable_curation_schema.py` — regression guard;
- Release Discipline Gate executes the validator with `--require-empty`.

The earlier #366 proposal remains in the working layer at:

`docs/work/airtable/2026-08-10_AIRTABLE_CURATION_SCHEMA_PLAN_v1.json`.

The executable contract validates itself against that accepted plan so implementation cannot silently diverge from the decision that authorized it.

PR #369 passed all standard repository workflows on its final head, including Release Discipline, ETL Check, Globe Repository Boundary, Geospatial Assets, Moderation and Auth Redis integration.

## 4. Airtable implementation details

### 4.1 Inverse linked-record fields

Airtable automatically creates inverse linked-record fields when a `multipleRecordLinks` field is created.

Those inverse fields are implementation-generated convenience fields. They do not add new semantic relationships and are not part of the declared forward-field contract.

The contract therefore validates declared forward fields and link targets while allowing Airtable-generated inverse fields.

### 4.2 Cardinality

Airtable linked-record fields can hold multiple records and do not enforce all Foundation cardinalities structurally.

Therefore rules such as:

- `EvidenceLinks.claim` = exactly one;
- `EvidenceLinks.source` = exactly one;
- `Claims.knowledge_object` = exactly one;
- `Claims.object_part` = zero or one;
- `Uncertainties` target = exactly one of KnowledgeObject / ObjectPart / Claim;

belong to the executable curation validator/export layer, not to Airtable UI assumptions.

No real import may begin until those row-level validators exist.

### 4.3 Record time versus historical time

Historical/valid time remains explicit signed-year/date text plus separate precision/certainty semantics.

`Claims.created_at`, `Claims.updated_at` and `EvidenceLinks.reviewed_at` are curation **record-time** fields only.

Airtable rejected `UTC` as a `dateTime` display timezone in the current API configuration, so these record-time fields use `Europe/London`. This is a display/storage implementation detail and cannot be interpreted as historical valid-time semantics.

### 4.4 Gate C layer mapping remains deliberately unresolved

The frozen Gate C selection manifest uses four layer IDs:

- `layer-leonardo-trajectory`;
- `layer-local-context`;
- `layer-engineering-work`;
- `layer-global-simultaneity`.

Those IDs do **not** currently exist in the legacy Architecture Atlas `Layers` table.

#368 therefore created only the `KnowledgeObjects.layers` schema link and did **not** add any new Layer records. Silently inserting the Gate C layers into the legacy public-source table would couple shadow curation to the current Architecture Atlas exporter before an explicit mapping decision.

Before any Gate C shadow import, the mapping contract must choose and validate one clean representation, for example:

- prove that shadow-only Layer records can coexist in the existing `Layers` table without entering or perturbing the public export; or
- introduce a separate versioned World Model layer/slice-layer representation if contextual layer roles cannot be preserved by the legacy table.

The choice must preserve the Gate C `layer_id` values and per-slice roles (`primary_trajectory`, `local_context`, `change_context`, `global_context`) without inventing or dropping semantics. No legacy Layer record should be created merely to make an import pass.

## 5. Fail-closed semantic rules

The new tables preserve the accepted boundaries:

- `Feature` is not used as a universal World Model object;
- `KnowledgeObjects.object_type` is limited to the accepted core envelope for this curation schema;
- `ObjectParts.spatial_status=unknown_route` and `segment_kind=unknown_route` exist explicitly so route geometry need not be fabricated;
- `EvidenceLinks` requires explicit `locator`, `supports | challenges | contextualizes`, and `direct | indirect | background` semantics in the contract;
- `Sources` are reused rather than duplicated, but a Source does not support a Claim without an EvidenceLink;
- `Layers` remain grouping, never evidence; Gate C layer-record mapping is unresolved rather than silently written into the legacy public-source table;
- `Media` remains presentation/rights, never evidence by default;
- no Relation table is added to the shadow World Model while #331 remains paused;
- no compatibility `same_movement` record is promoted into a substantive Relation;
- absence from `WorldSlices` never means historical absence.

## 6. Current authority boundary

Current public data path remains:

`legacy Airtable Architecture Atlas tables → export_airtable.py → semantic_data_gate → public data/*`.

The six new shadow tables are not read by the public exporter.

Future target path remains:

`World Model curation → validated/versioned canonical package → Explorer State → Render Projection → renderers`.

A later storage system may replace Airtable without changing this semantic architecture.

## 7. Gate C boundary

The frozen repository package:

`fixtures/world_slices/leonardo_romagna_1502/v1/`

remains the authority for the reviewed Gate C boundary.

There are **zero Leonardo/Gate C records** in the six shadow tables at #368 completion.

A later import issue must treat Airtable records as a non-authoritative shadow copy until a deterministic round-trip comparison proves semantic equivalence against the frozen package.

## 8. Next allowed step

The next optional data-governance step is a separate **Gate C shadow import + round-trip parity** issue. It is intentionally **not opened** by #368 completion.

That future issue must, before writing real records:

1. implement row-level validators for cardinality and cross-reference closure;
2. define deterministic import/export mapping from the frozen Gate C package;
3. resolve Gate C Layer IDs and per-slice roles without silently polluting the legacy public-source `Layers` table;
4. prohibit invention of missing locator/evidence/geometry/relation semantics;
5. preserve unknown-route and geometry-withheld states;
6. compare IDs, object counts, Claims, EvidenceLinks, Sources, Uncertainties, layer roles and reconstruction semantics back to the frozen repository package;
7. keep Airtable non-authoritative until parity passes;
8. leave Gate D unopened unless #355 separately performs its explicit lifecycle transition.

## 9. Lifecycle closure

#366 completed in PR #367: legacy Airtable ownership/schema truth, canonical audit routing and the proposal-only schema decision were aligned.

#368 completed in PR #369: six empty shadow tables, executable contract/snapshot validation and Release Discipline integration were accepted with all standard workflows green.

There is no active Airtable data-governance execution after this lifecycle close. The next data step requires a new explicit issue; Gate D remains unopened.
