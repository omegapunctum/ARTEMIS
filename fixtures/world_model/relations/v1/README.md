# ARTEMIS relation ladder fixture package v1

Status: `REVIEW_REQUIRED`

This synthetic package makes issue #331 executable. The historical “ladder” name is retained for traceability;
the executable model is a set of independent typed predicates, not a total order or shared rank.

It binds to the reviewed #329 world-model package and consumes the reviewed #330 temporal/spatial extent
definitions exactly. Fixtures cover nested places, approximate/open/alternative time, uncertain route geometry,
distance interaction, intermediary action, posthumous influence and process causality. It does not modify either
base package or claim historical/runtime capability.

Validation:

```bash
python scripts/validate_relation_fixtures.py
pytest -q tests/test_relation_fixtures.py tests/test_repository_governance_contract.py tests/test_concept_lock_contract.py
```

`--require-ready` is valid only after two independent reviews are recorded against one frozen commit and digest.
