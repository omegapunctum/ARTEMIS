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
| `schema.json` | Draft 2020-12 package schema, executed by the validator |
| `package.json` | Complete synthetic world-model fixture |
| `coverage_manifest.json` | Object/scenario coverage and corpus exclusions |
| `sources/*.md` | Immutable synthetic evidence documents with reproducible locators |
| `compatibility/architecture_atlas_projection.json` | Non-inventive legacy projection |
| `review_registry.json` | Frozen-content, distinct-artifact independent-review gate |

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
- An alternative date needs its own atomic, evidence-bound Claim.
- An `inferred_gap` has no route geometry.
- `co_present` requires both spatial and temporal overlap and never creates a historical Relation.
- A multi-region analytical Process does not imply diffusion, direction or mechanism.
- `evidence_state` is derived exactly from reviewed EvidenceLinks.
- A compatibility adapter is bound to the pinned source-record checksum, resolves every target reference and preserves missing evidence as missing.
- `known_exclusions` describe corpus coverage, never historical absence.
- `SynchronizedView` carries time, camera, layers, selection, comparison scope, reconstruction, uncertainty display and dataset identity.
- Two READY reviews must use different reviewer identities, invocation identities, tracks and checksummed artifacts, inspect one frozen commit, report zero unresolved critical/material findings and bind the current review-scope digest.

## Current boundary

Passing this package proves only that the contract is representable and executable. It does not prove:

- that the public runtime implements the model;
- that the current database/API supports these objects;
- that the Leonardo World Slice is curated;
- that user value is validated.

