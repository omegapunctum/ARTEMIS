# Leonardo Airtable mapping review

This directory is reserved for the independent `mapping-integrity` review required by #371 before any live historical Airtable write.

The reviewer must be a **separate read-only agent task** from the implementation task and must inspect the exact frozen row-plan SHA-256:

`ff63b8ed036ec79ac73e11c2eb4d3cad22b69b0e5a361c23cef767c5c5ac83f1`

Minimum review focus:

1. verify the deterministic 154-row plan against the frozen Gate C package rather than trusting generated counts;
2. detect semantic loss introduced by normalized Airtable fields, especially time, layer roles, source rights, Claims/EvidenceLinks and Uncertainty targets;
3. verify that legacy `KnowledgeObjects.layers` and `EvidenceLinks.source` remain empty in the plan;
4. verify that three unknown-route gaps have no invented line/place/source binding and Region geometry remains withheld;
5. verify that the 11 Uncertainty identities are not cloned and the 40 target junction rows reproduce source `target_refs[]` exactly;
6. verify that the rejected Cesena `ff. 9r–10r` Claim remains rejected and no draft Claim/Source is promoted;
7. verify that the proposed dependency order can be implemented without transient semantic corruption or ambiguous linked-record resolution;
8. verify that no Gate D/public capability/Relation semantics are introduced.

The resulting artifact must conform to `../review_artifact.schema.json` and be registered in `../review_registry.json`.

A `READY` decision requires zero open critical or material findings. Any semantic change to the mapping/row plan changes the digest and invalidates the review.
