# ARTEMIS relation ladder fixture package v1

Status: `REVIEW_REQUIRED`

This synthetic package makes issue #331 executable. It binds to the reviewed #329 world-model and #330
uncertainty packages, but it does not modify them or claim historical/runtime capability.

Validation:

```bash
python scripts/validate_relation_fixtures.py
pytest -q tests/test_relation_fixtures.py tests/test_repository_governance_contract.py tests/test_concept_lock_contract.py
```

`--require-ready` is valid only after two independent reviews are recorded against one frozen commit and digest.
