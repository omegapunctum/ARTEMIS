# ARTEMIS #330 uncertainty semantics review

Status: `IN_PROGRESS / REVIEW_REQUIRED`

## Decision

Extend the reviewed `fixtures/world_model/v1` contract additively. The READY base remains
byte-for-byte unchanged. This work defines executable temporal/spatial uncertainty behavior; it
does not migrate the database, API, public data or UI.

Detailed #330 semantics are owned by `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md`. The two base owner
contracts remain byte-for-byte unchanged because they belong to the immutable #329 review scope.

## Required evidence

- canonical `not_before` / `not_after`, open and unknown endpoint semantics;
- inclusive/exclusive boundary behavior;
- deterministic `excluded / possible_overlap / contained / unknown` window result;
- temporal alternatives without silent winner selection;
- approximate, named-place, unknown and route uncertainty projections;
- non-inventive Architecture Atlas compatibility projection;
- positive and negative deterministic tests;
- semantic-model and validator-integrity reviews on one frozen commit.

## Immutable dependency

- base merge: `db60ffc89b93c8a3694b5f0b699e43e706786ba8`;
- base package: `fixtures/world_model/v1` (`READY`);
- base review artifacts and digest are not modified by #330.

## Review gate

The extension remains `REVIEW_REQUIRED` until two independent reviews agree that no unresolved
critical or material ambiguity remains. Finalization must be metadata-only and must not change the
reviewed semantic cases, schema, validator or tests.

### First frozen candidate `97025dcb0fb4f475abd2d040a925c18147f8e6b9`

- semantic-model: `CHANGES_REQUIRED` — `0 critical / 2 material / 1 minor`;
- validator-integrity: `CHANGES_REQUIRED` — `0 critical / 4 material / 0 minor`;
- shared blocker: unresolved Claim/Uncertainty provenance;
- additional blockers: descriptive-only projection policies, fail-open GeoJSON shapes, open
  compatibility envelope and READY metadata not bound to Git history/current release tree.

The correction keeps the immutable #329 package unchanged. It adds synthetic locator-bound
Claim/Evidence evidence, executable projection rules, strict geometry/compatibility validation and
a release-tree-bound READY gate. Fresh reviews are required on the next exact candidate SHA.

## Out of scope

Runtime/schema migration, probabilistic simulation, calendar conversion beyond the declared
proleptic Gregorian profile, AI adjudication, relation-ladder completion, Leonardo curation and UI
implementation.
