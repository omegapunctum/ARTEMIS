# World-model fixture package — review record

## Status

- Issue: `#329`.
- Package: `fixtures/world_model/v1/`.
- Current decision: `REVIEW_REQUIRED`.
- Previous reviewed head: `4e2c6ac335b6cf8a3f57bd95a3aa37e4b7619894`.
- Previous verdicts: semantic-model `CHANGES_REQUIRED`; validator-integrity `CHANGES_REQUIRED`.
- Next frozen commit: pending publication of the complete correction set.
- Required fresh independent reviews: `2`.
- Runtime/data migration: none.

## Canonical review scope

The validator owns the immutable `world-model-v1-canonical` scope. Registry metadata can select that scope identifier but cannot remove paths from it. It contains:

- `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- `docs/ENTITY_MODEL.md`;
- `docs/EPISTEMIC_CONTRACT.md`;
- schema, package, coverage, compatibility and both synthetic source artifacts;
- validator and regression tests;
- dependency lock input in `requirements.txt`.

The reviewed digest must match both the current normalized scope and the same files resolved from the frozen Git commit.

## Required questions

1. Are all core object kinds distinguishable?
2. Are WorldSlice space/time bounds consistent with every included context?
3. Does any geometry, date, route, Process or comparison imply evidence that does not exist?
4. Are Claim dimensions independent and EvidenceLink locators reproducible?
5. Is computed co-presence bound to its premises and kept outside historical Relations?
6. Are Process stages temporally ordered, Region-bound and Claim-bound?
7. Are alternative reconstructions visible and non-destructive?
8. Does the compatibility projection resolve its pinned source commit and close every target reference without invented evidence?
9. Does each SynchronizedView context intersect view time and bind local/global comparison references?
10. Can review metadata, artifact drift or an unresolvable SHA bypass the READY gate?
11. Is corpus absence kept separate from historical absence?
12. Does any artifact overclaim current runtime capability?

## Review cycle history

The first repeated review cycle on `4e2c6ac…` found:

- incomplete WorldSlice bounds and alternative-date uncertainty basis;
- mutable review scope;
- artifact/registry finding drift;
- an unverified frozen SHA and compatibility source commit;
- incomplete co-presence, Process and SynchronizedView semantic bindings;
- under-constrained portable schema fields.

Those findings are correction inputs, not READY evidence. Both reviewers must inspect the next frozen head independently; earlier conclusions cannot be reused.

## Finalization rule

The package can become `READY` only when:

- two fresh, separate agent-task review artifacts inspect the same resolvable frozen commit;
- both structured artifact fields exactly match the registry;
- both decisions are `READY`;
- critical findings and unresolved material findings are zero;
- the frozen commit tree and current immutable review scope have the same digest;
- `record_time.reviewed_at`, `review_registry.json` and `package.json` are synchronized;
- `python scripts/validate_world_model_fixtures.py --require-ready` passes;
- repository release/governance checks pass.

Reviewer identity is an external operational fact: the validator verifies distinct invocation attestations and content bindings, while merge authority verifies the actual separate executions.

Until then #329 remains open and #332 remains gated.
