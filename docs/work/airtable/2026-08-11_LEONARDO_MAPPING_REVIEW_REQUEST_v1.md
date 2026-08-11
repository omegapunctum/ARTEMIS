# Leonardo Airtable mapping-integrity review request v1

Status: **REVIEW_REQUIRED / READ ONLY**  
Parent: #371 / PR #372  
Date: 2026-08-11

Review the exact frozen semantic row plan with SHA-256:

`ff63b8ed036ec79ac73e11c2eb4d3cad22b69b0e5a361c23cef767c5c5ac83f1`

The review must execute as a separate read-only agent task from implementation. It must not write Airtable records or modify the reviewed mapping while reviewing it.

Required track: `mapping-integrity`.

Inspect the authoritative Gate C package against the #371 extension/mapping/row-plan files and determine whether all 154 candidate rows preserve source semantics without adding public, geometry or Relation claims.

Critical review questions:

1. Are all 17 KnowledgeObjects, 11 derived ObjectParts, 10 WorldSources, 22 Claims, 38 EvidenceLinks, 11 Uncertainties, 40 UncertaintyTargets and 4 SliceLayers derived without omission/duplication?
2. Are exact source temporal tokens preserved independently of normalized temporal fields?
3. Do `SliceLayers` and `WorldSources` correctly avoid contaminating legacy Architecture Atlas `Layers`/`Sources` and public export?
4. Do UncertaintyTargets reproduce every source `target_refs[]` while keeping exactly 11 Uncertainty identities?
5. Are the three unknown-route gaps and all Region geometry states strictly geometry-free where frozen evidence withholds geometry?
6. Does the rejected Cesena `ff. 9r–10r` Claim remain rejected?
7. Are Claim → EvidenceLink → WorldSource/locator semantics and rights boundaries preserved?
8. Can the planned write phases be executed deterministically using stable semantic IDs without transient ambiguity or circular-resolution failure?
9. Does any mapping field invent a place, time, geometry, source relation, review promotion or substantive Relation not present in Gate C?
10. Does the contour remain Gate C `completed/FREEZE`, Gate D unopened and non-public?

A READY review requires zero open critical or material findings. Record the result as a JSON artifact conforming to `fixtures/airtable_curation/v2/review_artifact.schema.json`, then register it in `fixtures/airtable_curation/v2/review_registry.json` against the exact digest above.

Any semantic mapping change changes the row-plan digest and invalidates the review.
