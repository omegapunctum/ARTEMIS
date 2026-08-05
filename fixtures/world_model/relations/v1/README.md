# ARTEMIS relation ladder fixture package v1

Status: `REVIEW_REQUIRED`

This synthetic package makes issue #331 executable. The historical “ladder” name is retained for traceability;
the executable model is a set of independent typed predicates, not a total order or shared rank.

It binds exactly once to each reviewed #329/#330 package. Relation extent values are synthetic test inputs;
`semantic_profile_refs` select reviewed #330 kinds and modes but do not pretend that a #330 fixture Claim supports
a different date, place or geometry. The relation schema preserves the reviewed extent shapes while making that
distinction executable.

Fixtures cover nested places, approximate/open/alternative time, Polygon holes and antimeridian-safe corridor
evaluation, tolerance-aware approximate points and explicit place-disjointness. Missing hierarchy edges remain
`unknown`, never invented disjointness. Distance interaction, intermediary action, posthumous influence and process
causality are independent Relation fixtures. The single evidence Source is closed to the canonical review-scoped
file. The synthetic
causal policy is a checked, digest-bound package artifact and is not production causal approval. This package does
not modify either base package or claim historical/runtime capability.

Validation:

```bash
python scripts/validate_relation_fixtures.py
pytest -q tests/test_relation_fixtures.py tests/test_repository_governance_contract.py tests/test_concept_lock_contract.py
```

`--require-ready` is valid only after two independent reviews are recorded against one frozen commit and digest.
The validator recomputes that digest from the frozen Git tree, parses both review artifacts and rejects untracked,
symlinked, opaque or path-escaping evidence. Every normalized lifecycle field is also checked exactly against the
package and registry, so digest normalization cannot hide stale or false READY metadata.
