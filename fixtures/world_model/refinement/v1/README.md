# ARTEMIS progressive refinement fixtures v1

Lifecycle: exact candidate/READY status is owned by `review_registry.json` and the contract.

Issue: [#377](https://github.com/omegapunctum/ARTEMIS/issues/377).

## Purpose

This synthetic package proves that ARTEMIS can append coarse-to-fine knowledge revisions without
changing object identity, erasing provenance or confusing a changed world state with changed
knowledge about one state.

It covers:

- independent temporal and spatial refinement for a Leonardo-like subject;
- an `unknown_route` with no connecting geometry;
- refinement of one ecological-range state;
- a different-valid-time ecological state outside that refinement chain;
- correction, competing alternative and withdrawal;
- deterministic current-frontier and record-time replay.

The package is deliberately synthetic. It does not alter or improve the frozen Leonardo Gate C
corpus and makes no historical truth claim.

## Validate

```bash
python scripts/validate_progressive_refinement_fixtures.py
python -m pytest -q tests/test_progressive_refinement_fixtures.py
```

## Independent review

`review_request.json` freezes the two review tracks and the exact reviewed-file scope.
`review_registry.json` stays fail-closed in candidate state and binds both independent read-only
tasks to one remote commit and one computed content digest before READY. Review artifacts must
validate against `review_artifact.schema.json`; green CI alone cannot change package lifecycle.
All prior round artifacts remain immutable review history; only the two pre-issued slots in the
registry-designated request can satisfy its declared review round.

## Boundary

Passing this fixture proves representability and validator behavior only. It does not implement a
database, Airtable workflow, runtime editing, public Globe or historical corpus revision.
