# ARTEMIS world-model contract fixtures v1

Status: `REVIEW_REQUIRED`.

Issue: [#329](https://github.com/omegapunctum/ARTEMIS/issues/329).

## Purpose

This package is an executable semantic boundary for the Foundation v3 world model. It exists before database, API and public-runtime migration.

The main package is deliberately fictional. That choice is explicit:

- it tests `Entity`, `Event`, `State`, `Process`, `Trajectory`, temporal `Region`, `Layer`, `Relation`, `Claim`, `EvidenceLink`, `Uncertainty` and `SynchronizedView` semantics;
- it cannot be mistaken for a curated historical corpus;
- every applicable Claim still reproduces its evidence through a checked-in source locator;
- real Leonardo curation remains owned by #332.

The Architecture Atlas compatibility projection is real and commit-pinned. It demonstrates what can and cannot be mapped from the current Villa Savoye record without inventing target semantics.

## Files

| Path | Role |
|---|---|
| `schema.json` | Versioned portable package shape |
| `package.json` | Complete synthetic world-model fixture |
| `coverage_manifest.json` | Object/scenario coverage and corpus exclusions |
| `sources/*.md` | Immutable synthetic evidence documents with reproducible locators |
| `compatibility/architecture_atlas_projection.json` | Non-inventive legacy projection |
| `review_registry.json` | Independent-review gate |

## Validate

Structural and semantic validation:

```bash
python scripts/validate_world_model_fixtures.py
```

Final acceptance after two independent reviews:

```bash
python scripts/validate_world_model_fixtures.py --require-ready
```

Negative regression tests:

```bash
python -m pytest -q tests/test_world_model_fixtures.py
```

## Important semantics

- `fixture_defined` precision is legal only inside this explicitly synthetic fixture.
- A non-unknown extent needs one or more basis Claims.
- An `inferred_gap` has no route geometry.
- `co_present`, overlap and Similarity are derived observations, never stored historical Relations.
- A compatibility adapter preserves missing evidence as missing.
- `known_exclusions` describe corpus coverage, never historical absence.
- Two reviews must inspect the same frozen commit and use different reviewer identities.

## Current boundary

Passing this package proves only that the contract is representable and executable. It does not prove:

- that the public runtime implements the model;
- that the current database/API supports these objects;
- that the Leonardo World Slice is curated;
- that user value is validated.

