# ARTEMIS progressive refinement fixtures v1

Status: `REVIEW_REQUIRED`.

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

## Boundary

Passing this fixture proves representability and validator behavior only. It does not implement a
database, Airtable workflow, runtime editing, public Globe or historical corpus revision.
