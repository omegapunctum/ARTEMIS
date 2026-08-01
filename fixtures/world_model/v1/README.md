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
| `review_registry.json` | Review attestations and one immutable validator-owned scope identifier |

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
- Every `State` subject/value pair is reproduced as an exact structured binding in each basis Claim and in a reviewed supporting locator.
- `State.state_kind` is typed; computed co-presence accepts only two distinct positive `presence/present` States.
- Every reviewed EvidenceLink locator carries an exact digest of the complete Claim payload; the complete normalized v1 semantic package is additionally pinned by a validator-owned digest independent of mutable package/source assertions.
- Every Trajectory segment binds the Trajectory, its exact subject, coverage, segment payload, Claim and reviewed locator.
- WorldSlice time/space bounds participate in the same context-bound extent gate as Events, States, Processes, Trajectories and Region versions.
- An `inferred_gap` has no route geometry.
- Every `Uncertainty` dimension has an exhaustive owner/basis rule; adding a plausible but dimension-ineligible backlink is invalid.
- An alternative Region reconstruction names its Region/version set and must differ geometrically from every temporally overlapping primary reconstruction.
- Polygon comparison normalizes ring rotation/orientation and rejects degenerate, self-intersecting or backtracking rings, exterior holes and overlapping/nested components, so byte-different but topologically identical alternatives do not count as competing geometry.
- `co_present` requires both spatial and temporal overlap and never creates a historical Relation.
- Relation endpoints, Relation target and canonical time/space expressions must be stated by both its basis Claim and a reviewed supporting locator.
- A multi-region analytical Process does not imply diffusion, direction or mechanism.
- `evidence_state` is derived exactly from reviewed EvidenceLinks.
- A compatibility adapter resolves the pinned source commit/file in READY mode and compares the complete target object, including epistemic fields, to one deterministic mapping; missing evidence and uncertainty cannot be promoted away.
- The coverage manifest has a closed v1 envelope, exactly mirrors the WorldSlice layer set and requires a stable-ID exclusion registry for sparse context, missing route geometry and the corpus-absence/historical-absence boundary.
- WorldSlice coverage policy and Uncertainty effects are typed and fixed to the sparse synthetic scope; the contract view must expose material, alternative and corpus uncertainty and activate every local/global context layer.
- Every Source is parsed by one closed locator tokenizer; malformed, nested, truncated or duplicate markers cannot shadow or truncate a canonical passage.
- Semantically duplicate EvidenceLink tuples are rejected before evidence state is derived.
- Every JSON artifact is read with one strict parser that rejects duplicate keys, lexical non-finite constants and exponent overflow before schema, semantic or review-digest processing; canonical serialization also refuses non-finite values.
- Package and review completion timestamps use strict second-precision UTC ISO-8601; reviews cannot predate their frozen commit or be future-dated, and package `reviewed_at` must follow both reviews.
- `SynchronizedView` carries time, camera, layers, selection, comparison scope, reconstruction, uncertainty display and dataset identity; selected objects must belong to or participate in temporally visible context.
- The review scope is an immutable validator constant; registry metadata cannot shrink it.
- Two READY reviews must use different reviewer identities, invocation identities, tracks and checksummed structured attestations with bound completion times, inspect one resolvable ancestor commit, report zero unresolved critical/material findings and bind both that commit tree and the current review-scope digest.
- Review artifacts are closed machine-readable attestations: structured findings derive the decision and counts, while unknown narrative/verdict fields fail closed.
- Review identifiers are non-empty stable strings; finding counts are non-negative integers and booleans are rejected.
- `independence_attestation` records the operational fact of separate agent tasks. The validator verifies the two distinct attestations and their content bindings; merge authority remains responsible for authenticating reviewer identity outside the repository.

## Current boundary

Passing this package proves only that the contract is representable and executable. It does not prove:

- that the public runtime implements the model;
- that the current database/API supports these objects;
- that the Leonardo World Slice is curated;
- that user value is validated.
