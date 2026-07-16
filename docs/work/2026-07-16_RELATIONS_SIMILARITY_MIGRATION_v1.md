# ARTEMIS — RELATIONS / SIMILARITY MIGRATION v1

## Статус

- Issue: `#282`.
- Статус: pre-write audit and implementation contract.
- Snapshot date: 2026-07-16.
- Scope: reviewed Feature↔Feature Relations, Relation evidence, public export and explicit separation from computed Similarity for the 19-Feature Architecture Atlas pilot.

Документ фиксирует безопасный порядок работ до создания Airtable tables или canonical Relation records.

## 1. Verified pre-write baseline

Read-only audit of Airtable, public artifacts and runtime found:

| Check | Result |
|---|---:|
| Canonical Features | 19 UUID v4 |
| Reviewed primary Feature Sources | 19/19 |
| Airtable Relations table | absent |
| Airtable RelationSources table | absent |
| Checked-in `data/relations.json` | absent |
| Canonical Relation records | 0 |
| Runtime canonical Relation loader | absent |
| Runtime similarity heuristic | present |
| Similarity correctly labelled | no |

`js/ui.js#getRelatedFeatures` currently scores candidates by same `layer_id` and overlapping date range, then renders them inside an epistemic block labelled `Связь`. This is computed Similarity, not historical evidence. Renaming the label alone is insufficient: the runtime must also expose why an object is similar and reserve Relation presentation for records loaded from `relations.json`.

## 2. Contract decisions

1. Relation v1 connects exactly two canonical Feature UUIDs.
2. Predicate order is literal: `source_feature_id relation_type target_feature_id`.
3. A reviewed Relation requires at least one reviewed `RelationSources` row linked to a reviewed Source.
4. Relation review and evidence-link review are independent; both must be `reviewed` for publication.
5. Public Relation IDs are UUID v4 and never Airtable record IDs.
6. `epistemic_status` describes the knowledge claim; `review_status` describes editorial workflow. They are not interchangeable.
7. A reviewed `hypothesis` may be public only with visible hypothesis marking. The first pilot publishes only evidence-backed `fact` or `interpretation` records.
8. Similarity remains computed, non-canonical and source-free. It must never be serialized as a Relation automatically.
9. Causality is not implied by temporal order, same layer, spatial proximity or generic similarity.
10. Feature↔Feature v1 does not encode people or places as text targets. `designed_by` and `located_in` are deferred until canonical Person/Place identities exist.

## 3. Target Airtable schema

### Relations

| Field | Type | Rule |
|---|---|---|
| `id` | single line text | UUID v4, stable, unique |
| `source_feature` | link to Features | exactly one |
| `target_feature` | link to Features | exactly one and different from source |
| `relation_type` | single select | Feature↔Feature allowlist only |
| `description` | long text | concise sourced claim, not generic similarity |
| `epistemic_status` | single select | `fact`, `interpretation`, `hypothesis` |
| `confidence` | single select | `high`, `medium`, `low` |
| `valid_from` | single line text | optional signed year/date using Feature date conventions |
| `valid_to` | single line text | optional signed year/date |
| `review_status` | single select | `draft`, `reviewed`, `rejected` |
| `notes` | long text | internal review notes; not public evidence |

### RelationSources

| Field | Type | Rule |
|---|---|---|
| `id` | single line text | stable deterministic link ID |
| `relation` | link to Relations | exactly one |
| `source` | link to Sources | exactly one |
| `roles` | multiple select | initial allowlist: `relation_evidence` |
| `claim_note` | long text | exact claim/location supported by the Source |
| `review_status` | single select | `draft`, `reviewed`, `rejected` |

Airtable link fields may be exposed as `multipleRecordLinks`; ETL enforces one linked record on each side of a RelationSources row and one Feature on each endpoint of a Relation.

## 4. Relation type semantics

| Type | Direction | Publish requirement |
|---|---|---|
| `influenced` | source → target | evidence explicitly states influence or design reference |
| `inspired_by` | source → target | evidence explicitly states source was inspired/modelled after target |
| `same_movement` | symmetric | source names the movement for both Features; endpoint UUIDs sorted |
| `reconstructed_from` | source → target | evidence identifies target as reconstruction basis |
| `part_of` | source → target | both records are Features and evidence establishes containment |

Forbidden shortcuts:

- same layer → `same_movement`;
- earlier date → `influenced`;
- nearby coordinates → `part_of` or `located_in`;
- similar form/name → `inspired_by`;
- AI suggestion → canonical Relation.

## 5. Public artifact contract

`data/relations.json` is a deterministic array sorted by `id`:

```json
[
  {
    "id": "UUID-v4",
    "source_feature_id": "UUID-v4",
    "target_feature_id": "UUID-v4",
    "relation_type": "influenced",
    "description": "Sourced claim",
    "epistemic_status": "fact",
    "confidence": "medium",
    "valid_from": null,
    "valid_to": null,
    "source_ids": ["src_*"],
    "source_refs": [
      {
        "source_id": "src_*",
        "roles": ["relation_evidence"],
        "claim_note": "Evidence scope"
      }
    ]
  }
]
```

Publish validation rejects:

- non-UUID Relation or Feature IDs;
- missing/self/multiple endpoints;
- missing/deleted Feature endpoint;
- unknown relation type, epistemic status, confidence or review status;
- symmetric relation with unsorted endpoints;
- duplicate directed or symmetric predicate tuple;
- reviewed Relation without reviewed evidence;
- evidence linked to an unreviewed Source;
- invalid temporal range;
- causal wording unsupported by type and evidence.

Published Features receive deterministic `relation_ids`. Similarity results are not included in `relations.json` or `relation_ids`.

## 6. Runtime separation

The detail panel must expose two different sections:

### Документированные связи

- loaded from reviewed `relations.json`;
- shows relation type, direction, description, epistemic status, confidence and Source link;
- navigates to the other Feature without hiding evidence;
- shows a neutral empty state when no reviewed Relation exists.

### Похожие объекты

- computed from current Features;
- replaces `getRelatedFeatures` with an explicit similarity result containing `feature`, `score` and `criteria`;
- initial criteria: same layer, overlapping period and date distance;
- never uses words such as `relation`, `influence`, `cause` or `evidence` for the heuristic itself.

Preview and full-detail modes follow the same semantics. Fact, documented Relation, Similarity, Interpretation and AI suggestion remain visually and structurally distinct.

## 7. Initial evidence pilot

The first batch is intentionally small. A content quota is not a reason to create weak Relations.

| Source Feature | Predicate | Target Feature | Epistemic status | Confidence | Evidence candidate |
|---|---|---|---|---|---|
| Pantheon (Rome), `e2a3b4c5-1238-4f91-b0d2-e3f4a5b6c7d8` | `influenced` | St. Peter's Basilica, `393c7d17-d266-4e8b-8412-b96eb427f941` | `fact` | `medium` | reviewed `src_st_peters_basilica_wikipedia`; architecture section explicitly identifies the Pantheon dome as a design reference |
| Panthéon (Paris), `acfb7492-c49d-4e71-9bbc-bd446b52d32d` | `inspired_by` | Pantheon (Rome), `e2a3b4c5-1238-4f91-b0d2-e3f4a5b6c7d8` | `fact` | `medium` | reviewed `src_pantheon_paris_wikipedia`; use only the explicitly supported institutional/mausoleum model claim, not an inferred formal influence |

Both candidates remain `draft` until the precise source passage is checked during the data batch. If the passage supports a narrower statement than the candidate description, the Relation description is narrowed; the source is never stretched to fit the type.

## 8. Execution order and recovery

### Batch A — documentation

Commit this contract, reconcile allowlists and record the current mislabelling before schema writes.

### Batch B — additive schema

Create `Relations` and `RelationSources` without changing existing Feature/Source tables beyond reciprocal links. Record all table and field IDs here.

### Batch C — draft pilot data

Create candidate Relations and evidence links as `draft`. Verify UUID identity, endpoint direction, source passages and duplicate tuples before review.

### Batch D — ETL and artifacts

Export only reviewed Relations, add validation/tests and generate `relations.json` plus Feature `relation_ids`. Empty reviewed output remains valid while all candidates are draft.

### Batch E — runtime semantics

Load/render canonical Relations separately, rename heuristic UI to «Похожие объекты» and display criteria. No styling redesign is required for the semantic fix.

### Recovery

- schema changes are additive;
- draft rows never enter public artifacts;
- a rejected candidate is retained with `review_status=rejected` and a review note;
- runtime can fall back to an empty documented-relations state if `relations.json` is unavailable, but Similarity must remain correctly labelled;
- removal of a reviewed Relation requires a documented editorial decision, not silent deletion.

## 9. Documentation-phase acceptance

- [x] current Airtable/runtime/artifact baseline verified;
- [x] Relation predicate direction defined;
- [x] Feature↔Feature allowlist separated from future entity relations;
- [x] RelationSources evidence model defined;
- [x] public artifact and validation contract defined;
- [x] Relation and Similarity UI semantics separated;
- [x] initial evidence candidates recorded as draft-only;
- [ ] Airtable schema created and re-read;
- [ ] pilot Relations and evidence reviewed;
- [ ] ETL/public artifacts implemented;
- [ ] runtime and contract tests green.
