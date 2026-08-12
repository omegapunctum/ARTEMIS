# ARTEMIS — Leonardo Gate C Airtable Shadow Import v1

Status: **PREFLIGHT COMPLETE / IMPORT DEFERRED / LIVE HISTORICAL WRITE BLOCKED**
Date: 2026-08-12
Issue: #371
Implementation: merged PR #372
Parent product contour: #355
Predecessor: #368 / PR #369
Product gate: Gate C remains `completed/FREEZE`; Gate D is separately in progress under #355.

## 1. Goal

Prove a deterministic and fail-closed mapping from the frozen, authoritative repository package:

`fixtures/world_slices/leonardo_romagna_1502/v1/`

into a non-authoritative Airtable shadow representation, then prove round-trip semantic parity before Airtable can be used as a practical editorial surface for this World Slice.

This work is data-governance maintenance outside the one-product-gate WIP slot. It did not start Gate D, change the public runtime, promote historical Claims or resume #331 Relation semantics.

The mapping preflight was merged fail-closed. Progressive fidelity now lets Gate D consume the frozen repository package directly, so #371/#373 and all historical Airtable writes are deferred. The nine shadow tables remain empty and `historical_rows_authorized=false` remains authoritative.

## 2. Starting boundary

#368 / PR #369 created six empty shadow tables:

- `WorldSlices`;
- `KnowledgeObjects`;
- `ObjectParts`;
- `Claims`;
- `EvidenceLinks`;
- `Uncertainties`.

The frozen Gate C package contains:

- 17 KnowledgeObject candidates;
- 10 Sources;
- 22 atomic Claims;
- 38 EvidenceLinks;
- 11 Uncertainty identities;
- four exact World Model layer IDs/roles;
- one Trajectory with four presence anchors and three unknown-route gaps;
- one temporal Region with two source-bound states and two reconstruction alternatives.

At #371 start all six original shadow tables contained 0 historical records.

## 3. Preflight findings and decisions

### 3.1 Legacy `Layers` cannot represent the Gate C layer boundary safely

The frozen package uses:

- `layer-leonardo-trajectory` / `primary_trajectory`;
- `layer-local-context` / `local_context`;
- `layer-engineering-work` / `change_context`;
- `layer-global-simultaneity` / `global_context`.

Those IDs do not exist in the legacy Architecture Atlas `Layers` table. Adding them there merely to satisfy a shadow import would couple World Model curation to the current public exporter.

Decision: create shadow-only `SliceLayers` and add `KnowledgeObjects.slice_layers`. For the Gate C import, legacy `KnowledgeObjects.layers` must remain empty.

### 3.2 Frozen Uncertainty is many-target; the v1 Airtable shape was one-target

The 11 frozen Uncertainty records each retain one stable identity, but `target_refs[]` can contain several Claims and/or KnowledgeObjects. Cloning an Uncertainty once per target would change identity and break round-trip parity.

Decision: preserve the 11 `Uncertainties` unchanged and create `UncertaintyTargets` as a storage junction. Every junction row must bind exactly one Uncertainty to exactly one KnowledgeObject, ObjectPart or Claim. These rows are storage structure, not semantic Relations.

### 3.3 Legacy `Sources` cannot be reused losslessly without public-export risk

The current Architecture Atlas exporter reads reviewed legacy `Sources` into public `data/sources.json`. The frozen Gate C source registry also uses source-type tokens such as `institutional_reference`, `scholarly_publication` and `collection_catalogue` that are not the legacy Architecture Atlas Source enum.

Using legacy Sources would therefore require either a lossy source-type rewrite, a public-export risk, or an undocumented dual-model convention.

Decision: create shadow-only `WorldSources` and add `EvidenceLinks.world_source`. For Gate C import, legacy `EvidenceLinks.source` must remain empty.

A WorldSource is still not Evidence by itself. Claim-specific support remains only:

`Claim → EvidenceLink → WorldSource + locator`.

### 3.4 Source temporal tokens cannot be collapsed into normalized Airtable values

The frozen package uses source precision tokens including `range` and `pending`, while the normalized curation representation uses values such as `interval` and `unresolved`.

Decision: preserve exact `source_temporal_value` and `source_temporal_precision` separately from normalized temporal fields. Normalization may aid querying but cannot erase the source package token needed for round-trip parity.

## 4. Live preflight schema extensions

Created with zero records:

- `SliceLayers` — shadow-only per-slice layer identity/role;
- `UncertaintyTargets` — many-target uncertainty storage junction;
- `WorldSources` — lossless World Model source/rights registry.

Added parity/provenance fields to the existing shadow tables so the frozen package need not be collapsed into `notes` or rewritten tokens:

- `KnowledgeObjects`: `slice_layers`, exact source spatial/curation/temporal tokens, `temporal_assertion_status`, `world_sources`;
- `ObjectParts`: exact source kind/spatial/temporal tokens, geometry status, reconstruction alternative metadata and WorldSource refs;
- `Claims`: `confidence_basis`;
- `EvidenceLinks`: `world_source`;
- `Uncertainties`: `basis_kind`, `basis_claims`;
- `WorldSources`: source identity, source type, rights envelope, intended Claims and source-level candidate relation metadata.

All three new tables were explicitly read after creation and verified at 0 records. The original six #368 tables also remain empty under the v1 `--require-empty` guard.

## 5. Executable preflight

Versioned repository evidence is under:

`fixtures/airtable_curation/v2/`.

It contains:

- `extension_contract.json` — v2 shadow-storage extension and legacy-isolation rules;
- `live_extension_snapshot.json` — exact live table/field IDs with zero-record evidence;
- `mapping_contract.json` — deterministic frozen-package → shadow mapping rules;
- `row_plan_lock.json` — frozen semantic-ID row plan binding and write prohibition.

Executable controls:

- `scripts/validate_airtable_leonardo_shadow_preflight.py` — validates schema/package/ref/geometry/Gate boundaries;
- `scripts/build_airtable_leonardo_shadow_plan.py` — deterministically derives the semantic-ID candidate rows without network access or writes;
- `scripts/validate_airtable_leonardo_row_plan_lock.py` — recomputes the entire plan and rejects any digest/count/source/isolation drift.

Release Discipline executes all three plus their regression suites.

## 6. Frozen mapping and row plan

The mapping deterministically derives 11 ObjectParts:

- 7 Trajectory parts: four `presence` anchors plus three source `inferred_gap` parts normalized to shadow `unknown_route` while preserving the exact source token;
- 2 temporal Region states;
- 2 Region reconstruction alternatives.

No Process stage is invented because the frozen package does not define one.

The four Gate C layers map to `SliceLayers`, not legacy `Layers`.

The ten frozen Sources map to `WorldSources`, not legacy `Sources`.

The 11 frozen Uncertainty identities remain 11 records; their `target_refs[]` expand only into 40 deterministic `UncertaintyTargets` rows.

The complete deterministic candidate plan contains **154 rows**:

- 1 `WorldSlices`;
- 4 `SliceLayers`;
- 10 `WorldSources`;
- 17 `KnowledgeObjects`;
- 11 `ObjectParts`;
- 22 `Claims`;
- 38 `EvidenceLinks`;
- 11 `Uncertainties`;
- 40 `UncertaintyTargets`.

Release Discipline on exact head `2f28e5cd069b013cda7f04792a80ecc5435cf235` reproduced:

`ff63b8ed036ec79ac73e11c2eb4d3cad22b69b0e5a361c23cef767c5c5ac83f1`

as the canonical SHA-256 of that semantic row plan. `row_plan_lock.json` freezes this digest and binds it to the reviewed Gate C commit/tree/digest.

The lock explicitly states:

- `historical_rows_authorized=false`;
- `independent_mapping_review_required=true`;
- `round_trip_parity_required_after_write=true`;
- `gate_d_opened=false`.

## 7. What remains prohibited

At the row-plan-lock stage:

- no Leonardo/Gate C historical record may be created in Airtable shadow tables;
- no import status may claim parity;
- no legacy Layer or Source may be created for convenience;
- no route line or Region polygon may be invented;
- no stored Relation predicate may be added while #331 is deferred;
- no Claim or Source may be promoted from draft merely because it will be imported;
- no `data/*`, Architecture Atlas exporter or public runtime may change;
- this contour cannot open, advance or validate Gate D.

A green row-plan lock proves deterministic mapping, not the correctness of live write behavior and not round-trip parity.

## 8. Deferred transition inside #371

If #371 is explicitly reopened, the next allowed step is **independent review of the exact frozen row plan/mapping** under #373.

Only after that review is recorded against the same digest may #371 move to a separate controlled-write revision that:

1. changes write authorization explicitly;
2. writes the frozen plan in dependency order with stable IDs and draft/non-authoritative state;
3. reads every written row back from Airtable;
4. validates row-level cardinality and reference closure;
5. normalizes the live shadow copy back to repository semantics;
6. proves round-trip parity against the frozen Gate C package;
7. records any actual import/review cost;
8. only then closes #371 as completed data-governance evidence.

That future completion would still not open or advance Gate D. Gate D has its separate #355 lifecycle.
