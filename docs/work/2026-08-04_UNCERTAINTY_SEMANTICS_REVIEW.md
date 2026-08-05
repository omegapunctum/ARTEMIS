# ARTEMIS #330 uncertainty semantics review

Status: `COMPLETE / READY`

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

### Second frozen candidate `2fed830a0d44494993fff3499554b670451e4d32`

- semantic-model: `READY` — `0 critical / 0 material / 0 minor`;
- validator-integrity: `CHANGES_REQUIRED` — `0 critical / 1 material / 1 minor`;
- material blocker: provenance references resolved globally but were not bound to the individual
  semantic item that declared them, so claim and uncertainty references could be swapped between
  cases while preserving the global sets;
- minor: several hardened Git/READY paths were code-inspected but lacked direct extension-specific
  regressions.

The correction enforces exact item-to-target-Claim and item-to-subject-Uncertainty binding plus
global semantic target-ID uniqueness. Swap/collision regressions reproduce the material finding;
direct graft-rejection and inherited-Git-environment regressions reduce the minor test debt. Fresh
reviews are required on the next exact candidate SHA.

### Final frozen candidate `a6367bbaa17368b9285d7aecb963a07c70c6c50c`

- semantic-model: `READY` — `0 critical / 0 material / 0 minor`;
- validator-integrity: `READY` — `0 critical / 0 material / 1 minor`;
- exact CI: `4/4` green; current #330 contract/governance `51 passed`; frozen #329
  `518 passed`; export validations green;
- the validator minor records remaining extension-specific negative-test breadth for already
  fail-closed Git defenses and is resolved/nonblocking under the completion rule.

Both independent reviews bind the same frozen commit and reviewed semantic digest. The final
transition is metadata-only: semantic cases, schema, source, compatibility projection, validator,
tests and workflow remain byte-for-byte identical to the frozen candidate.

## Out of scope

Runtime/schema migration, probabilistic simulation, calendar conversion beyond the declared
proleptic Gregorian profile, AI adjudication, relation-ladder completion, Leonardo curation and UI
implementation.
