# ARTEMIS — Leonardo Gate C Airtable Shadow Import v1

Status: **ACTIVE PREFLIGHT / NO HISTORICAL ROWS WRITTEN**  
Date: 2026-08-11  
Issue: #371  
Parent product contour: #355  
Predecessor: #368 / PR #369  
Product gate: Gate C remains `completed/FREEZE`; Gate D remains unopened.

## 1. Goal

Prove a deterministic and fail-closed mapping from the frozen, authoritative repository package:

`fixtures/world_slices/leonardo_romagna_1502/v1/`

into a non-authoritative Airtable shadow representation, then later prove round-trip semantic parity before Airtable can be used as a practical editorial surface for this World Slice.

This work is data-governance maintenance outside the one-product-gate WIP slot. It does not start Gate D, change the public runtime, promote historical Claims or resume #331 Relation semantics.

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

## 3. Preflight findings

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

Using legacy Sources would therefore require either:

- a lossy source-type rewrite; or
- adding new reviewed Sources that can leak into current public output; or
- an undocumented draft-only compatibility convention that makes one legacy table own two different models.

Decision: create shadow-only `WorldSources` and add `EvidenceLinks.world_source`. For Gate C import, legacy `EvidenceLinks.source` must remain empty.

A WorldSource is still not Evidence by itself. Claim-specific support remains only:

`Claim → EvidenceLink → WorldSource + locator`.

## 4. Live preflight schema extensions

Created with zero records:

- `SliceLayers` — shadow-only per-slice layer identity/role;
- `UncertaintyTargets` — many-target uncertainty storage junction;
- `WorldSources` — lossless World Model source/rights registry.

Added parity/provenance fields to the existing shadow tables so the frozen package need not be collapsed into `notes` or rewritten tokens:

- `KnowledgeObjects`: `slice_layers`, `source_spatial_mode`, `source_curation_state`, `temporal_assertion_status`, `world_sources`;
- `ObjectParts`: exact source kind/spatial/temporal tokens, geometry status, reconstruction alternative metadata and WorldSource refs;
- `Claims`: `confidence_basis`;
- `EvidenceLinks`: `world_source`;
- `Uncertainties`: `basis_kind`, `basis_claims`;
- `WorldSources`: source identity, source type, rights envelope, intended Claims and source-level candidate relation metadata.

All three new tables were explicitly read after creation and verified at 0 records.

## 5. Executable preflight

Versioned repository evidence is under:

`fixtures/airtable_curation/v2/`.

It contains:

- `extension_contract.json` — accepted v2 shadow-storage extension and legacy-isolation rules;
- `live_extension_snapshot.json` — exact live table/field IDs with zero-record evidence;
- `mapping_contract.json` — deterministic frozen-package → shadow mapping rules.

`scripts/validate_airtable_leonardo_shadow_preflight.py` fails closed on:

- drift of the completed #368 six-table empty schema;
- v2 table/field/link-target drift;
- Gate D opening or #331 resumption;
- changed layer IDs/roles;
- changed frozen counts;
- unresolved Claim/Evidence/Source/Uncertainty references;
- blank EvidenceLink locators or invalid relation/strength tokens;
- invented candidate geometry;
- non-empty unknown-route source/geometry/place bindings;
- Region geometry appearing where the source package withholds it;
- loss of exact reconstruction metadata;
- duplication of Uncertainty identity instead of target-junction expansion;
- any Uncertainty target that does not resolve to exactly one KnowledgeObject/ObjectPart/Claim.

Release Discipline runs this preflight and its regression tests.

## 6. Mapping boundary

The preflight deterministically derives 11 ObjectParts:

- 7 Trajectory parts: four `presence` anchors plus three source `inferred_gap` parts normalized to shadow `unknown_route` while preserving the exact source token;
- 2 temporal Region states;
- 2 Region reconstruction alternatives.

No Process stage is invented because the frozen package does not define one.

The four Gate C layers map to `SliceLayers`, not legacy `Layers`.

The ten frozen Sources map to `WorldSources`, not legacy `Sources`.

The 11 frozen Uncertainty identities remain 11 records; their `target_refs[]` expand only into deterministic `UncertaintyTargets` rows.

## 7. What remains prohibited

Until the preflight PR is green and the import revision explicitly changes the lifecycle:

- no Leonardo/Gate C historical record may be created in Airtable shadow tables;
- no import status may claim parity;
- no legacy Layer or Source may be created for convenience;
- no route line or Region polygon may be invented;
- no stored Relation predicate may be added while #331 is paused;
- no Claim or Source may be promoted from draft merely because it is imported;
- no `data/*`, Architecture Atlas exporter or public runtime may change;
- Gate D remains unopened.

## 8. Next transition inside #371

After exact-head CI proves the preflight:

1. freeze the deterministic normalized row plan;
2. independently inspect the mapping before live historical writes;
3. write records in dependency order with stable IDs and draft/non-authoritative state;
4. read every written row back from Airtable;
5. validate row-level cardinality and reference closure;
6. normalize the live shadow copy back to repository semantics;
7. prove round-trip parity against the frozen Gate C package;
8. only then close #371 as completed data-governance evidence.

That completion still does not open Gate D. Gate D requires its separate #355 lifecycle transition.
