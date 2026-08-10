# ARTEMIS — Airtable Pre-Gate-D Alignment v1

Status: **ACTIVE PRE-GATE-D GOVERNANCE / NO GATE TRANSITION**  
Date: 2026-08-10  
Issue: #366  
Parent product contour: #355

## 1. Decision

The existing Airtable base remains the editorial/source system for the current **Architecture Atlas compatibility/public projection**. It is not the canonical Foundation v3 World Model and must not be expanded ad hoc into one.

This work does **not** open Gate D.

The accepted semantic authority remains the versioned repository contracts and frozen evidence packages:

`SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` → executable fixtures/validators → World Slice packages → Explorer State → Render Projection → renderers.

Airtable may become a human/AI curation surface for that model, but only through a separately validated curation schema that preserves the same semantics. Airtable convenience may not redefine object identity, temporal/spatial precision, Claims, EvidenceLinks, Uncertainty, reconstruction modes, or Relation semantics.

## 2. Current Airtable truth

The current base contains eight tables:

1. `Features`
2. `Layers`
3. `Sources`
4. `Media`
5. `FeatureSources`
6. `FeatureMedia`
7. `Relations`
8. `RelationSources`

Their current role is the Architecture Atlas compatibility data model used by `scripts/export_airtable.py` to produce the public `data/*` projection.

The current base is internally consistent with the repository's Architecture Atlas truth: 31 Features, 26 source Layers, 36 Sources with 35 reviewed, 28 reviewed Media, 32 FeatureSources, 28 FeatureMedia, 12 reviewed compatibility Relations and 21 reviewed RelationSources at the time of this decision.

Seven enabled but empty source Layers are deliberately excluded from the public `layers.json` by the semantic data gate. Three Features remain without reviewed primary Media because of rights blockers. Those are known compatibility-corpus conditions, not blockers for this alignment work.

## 3. Legacy table ownership

### `Features`

`Features` is a compatibility/public-projection curation table for the Architecture Atlas. A Feature is **not** a generic Foundation v3 knowledge object.

Do not add fields to `Features` merely to emulate Event, State, Process, Trajectory, Region, Claim or Uncertainty semantics. Foundation v3 distinctions must remain explicit in their own future curation model.

### `Layers`

`Layers` is display/query grouping for the compatibility projection. Layer membership is not evidence and does not determine historical truth.

### `Sources`

`Sources` is the one current table that is structurally close to the target model and may be reused by a future World Model curation layer after explicit migration validation. Stable Source identity must be preserved.

A Source does not prove a Feature or object globally. Evidence attaches to a specific Claim through an EvidenceLink.

### `Media` / `FeatureMedia`

These remain presentation/rights records for the compatibility corpus. Media is not factual evidence merely because it depicts an object.

### `FeatureSources`

This is a compatibility evidence-association table. `roles` and `claim_note` are useful legacy metadata but are **not** first-class Claims or EvidenceLinks. Migration must not infer missing locators, `supports/challenges/contextualizes`, or evidence strength.

### `Relations` / `RelationSources`

These are compatibility tables for the Architecture Atlas relation pilot. They do not authorize Foundation v3 Relation predicates.

Issue #331 remains paused. Gate C contains no stored Relations. No Airtable migration may promote `same_movement`, proximity, co-presence or other compatibility records into documented encounter, interaction, influence or causal claims without the separately accepted Relation contract.

## 4. Canonical audit path

There must be one executable audit path for the current Airtable/public-data contour:

`Airtable → scripts/export_airtable.py → scripts.semantic_data_gate.validate_semantic_release → scripts/release_check.py`

`scripts/audit_airtable.py` is retained only as a compatibility command/entrypoint. It must delegate to the canonical export and semantic-release logic rather than maintain a second allowlist/schema validator.

Why:

- linked-record and multiple-select fields already drifted beyond the old standalone audit assumptions;
- duplicated validation logic creates two competing definitions of a valid Airtable record;
- export semantics, cross-artifact integrity and warning budgets already live in the canonical pipeline.

The compatibility audit command may validate checked-in artifacts without network access. A live source refresh must be explicit and must run the canonical export before validation.

## 5. ETL write-back truth

The current export pipeline computes validation/projection state in generated artifacts. It does not currently write `date_valid`, `etl_status`, `etl_error`, `dedupe_key` or `version` back to Airtable as part of the canonical export path.

Therefore these Airtable fields must not describe themselves as current automatic ETL source-of-truth fields.

Until a separately tested write-back mechanism exists:

- generated `data/validation_report.json`, `data/export_meta.json`, `data/rejected.json` and the canonical public artifacts own export/run truth;
- empty legacy/reserved Airtable ETL fields are not errors by themselves;
- humans and agents must not manually fill those fields to simulate pipeline state;
- future write-back, if introduced, requires idempotency, conflict policy, version semantics, tests and explicit documentation.

## 6. Proposed World Model curation schema v1

This section is a **schema proposal only**. The tables below are not created by #366 and their absence does not block the current public Architecture Atlas export.

The smallest useful curation layer is six new normalized tables plus reuse of reviewed `Sources` and display `Layers` where appropriate.

### 6.1 `WorldSlices`

Purpose: define an explicit corpus/review boundary.

Minimum fields:

- `id` — stable semantic ID;
- `label`;
- `status` — `draft | frozen | reviewed | superseded`;
- `temporal_start`, `temporal_end` using signed-year/date compatible text semantics;
- `spatial_scope_note`;
- `selection_rationale`;
- `known_exclusions`;
- `coverage_limitations`;
- `source_package_ref`;
- `review_version`;
- `frozen_digest` where applicable;
- `promotion_allowed`;
- `notes`.

A World Slice describes corpus coverage. Absence from a slice never means historical absence.

### 6.2 `KnowledgeObjects`

Purpose: common envelope for Foundation v3 objects.

Minimum fields:

- `id`;
- `object_type` — `entity | event | state | process | trajectory | region`;
- `label`;
- linked `WorldSlices`;
- `temporal_start`, `temporal_end`;
- `temporal_precision`;
- `temporal_certainty`;
- `spatial_status` — e.g. `resolved | place_ref | geometry_withheld | not_spatial`;
- `place_ref` / geometry provenance reference as appropriate;
- `reconstruction_mode` where applicable;
- linked `Layers` for display/query grouping;
- `review_state`;
- `notes`.

This table carries only the common envelope. It must not flatten trajectory segments, Region states or reconstruction alternatives into ambiguous free text.

### 6.3 `ObjectParts`

Purpose: typed subobjects that need their own time/space/evidence identity.

Minimum fields:

- `id`;
- linked `KnowledgeObject`;
- `part_kind` — `trajectory_segment | process_stage | region_state | reconstruction_alternative | other_reviewed_part`;
- `sequence_order` where relevant;
- `temporal_start`, `temporal_end`, precision/certainty;
- `spatial_status`;
- `place_ref` / geometry reference;
- `segment_kind` for Trajectory parts (`presence | movement | unknown_route` in the current bounded use case);
- `reconstruction_mode`;
- `is_primary` where alternatives exist;
- `review_state`;
- `notes`.

Unknown routes may not receive line geometry merely to satisfy a renderer or Airtable view.

### 6.4 `Claims`

Purpose: atomic material assertions.

Minimum fields:

- `id`;
- `statement`;
- linked target `KnowledgeObject` and optional `ObjectPart`;
- `claim_kind`;
- `origin`;
- `review_state`;
- `confidence`;
- `evidence_state`;
- created/updated metadata.

A Claim must be atomic enough for a reviewer to decide what evidence supports or challenges it.

### 6.5 `EvidenceLinks`

Purpose: bind one Claim to one Source with reproducible evidence semantics.

Minimum fields:

- `id`;
- exactly one linked `Claim`;
- exactly one linked `Source`;
- `locator`;
- `relation_to_claim` — `supports | challenges | contextualizes`;
- `evidence_strength` — `direct | indirect | background`;
- `review_state`;
- reviewer/timestamp metadata.

A legacy FeatureSource or RelationSource may seed a candidate migration record only when the corresponding information actually exists. Missing locator or evidence semantics must stay missing; migration may not invent them.

### 6.6 `Uncertainties`

Purpose: first-class material uncertainty.

Minimum fields:

- `id`;
- target Claim, KnowledgeObject or ObjectPart;
- `dimension`;
- `description`;
- `effect`;
- `range_or_alternatives` where applicable;
- `basis`;
- `review_state`.

Uncertainty is attached to the affected assertion/object and must survive projection into the UI.

## 7. Reused current tables

### `Sources`

Prefer reuse over a second Source table, but only after a migration validator proves that the existing record satisfies the World Model Source contract. Existing stable `src_*` IDs should remain stable.

### `Layers`

May be linked from World Model objects only as display/query grouping. Layer does not become a Claim, evidence category or ontology substitute.

### `Media`

May remain a separate presentation/rights subsystem. It does not need to be duplicated inside World Model curation.

## 8. One-way migration/projection rule

The target direction is:

`Airtable World Model curation`  
`→ validated versioned canonical package/artifacts`  
`→ Explorer State / Render Projection`  
`→ 2D / Globe / future interfaces`

Compatibility outputs may additionally be derived for the current Architecture Atlas where semantics can be represented honestly.

The reverse direction is prohibited as an authority path:

`Features/Relations compatibility rows` **must not** be treated as sufficient input to reconstruct missing Foundation v3 Claims, EvidenceLinks, Uncertainty, temporal precision, geometry provenance or Relation meaning.

## 9. Gate C shadow-import policy

The frozen Leonardo-in-Romagna Gate C package remains the authority during this alignment phase.

No Gate C record is imported into the proposed Airtable World Model tables under #366.

A later shadow-import step may begin only after:

1. the curation schema is created from this accepted contract;
2. a deterministic export/validator exists for the new tables;
3. source IDs and all Claim/Evidence/Uncertainty references round-trip without semantic loss;
4. the output can be compared against the frozen Gate C package on IDs, counts, locators, uncertainty and reconstruction semantics;
5. unknown-route and geometry-withheld states remain unchanged;
6. the shadow copy is explicitly non-authoritative;
7. Gate C frozen files are not modified.

Only a later explicit governance decision may change which storage system is the operational curation authority.

## 10. Gate D boundary

#366 is pre-Gate-D maintenance. Completion of #366 does not start Gate D automatically.

Gate D remains unopened until #355 explicitly transitions the project under the existing lifecycle rules.

This issue may:

- repair current Airtable descriptions;
- repair/deprecate stale audit tooling;
- document the proposed curation schema;
- add tests/guards;
- prepare migration logic against synthetic/non-authoritative fixtures.

This issue may not:

- create or populate the new World Model tables;
- import the frozen real World Slice;
- integrate Gate C into the Globe runtime;
- change public capability;
- change the reviewed World Model contract;
- resume #331 Relations.

## 11. Exit criteria for #366

#366 is complete when:

- Airtable field/table descriptions tell the truth about the current compatibility role and ETL write-back status;
- `scripts/audit_airtable.py` no longer implements an independent stale schema contract;
- this curation-schema proposal is repository-visible and guarded against Gate-D implication;
- repository validation stays green;
- no public artifacts, Gate C frozen bytes, World Model contract bytes or runtime capability change;
- the next step is an explicit choice between creating the curation tables as a **shadow** system or postponing them until Gate D requires editorial write workflows.

## 12. Architectural conclusion

Airtable is useful to ARTEMIS as an editorial and curation surface, not as the owner of the world-model semantics.

The durable asset is the versioned spatial-temporal knowledge contract. Airtable, a future PostgreSQL/PostGIS store, an AI-assisted editor and later ingestion systems should all be replaceable implementations around that contract.
