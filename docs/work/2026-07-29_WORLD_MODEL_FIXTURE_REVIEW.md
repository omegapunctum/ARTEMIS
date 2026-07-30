# World-model fixture package — review record

## Status

- Issue: `#329`.
- Package: `fixtures/world_model/v1/`.
- Current decision: `REVIEW_REQUIRED`.
- Frozen commit: pending first published PR head.
- Required independent reviews: `2`.
- Runtime/data migration: none.

## Review scope

Each reviewer must inspect the same frozen commit against:

- `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- `docs/ENTITY_MODEL.md`;
- `docs/EPISTEMIC_CONTRACT.md`;
- issue `#329`;
- `fixtures/world_model/v1/coverage_manifest.json`;
- `scripts/validate_world_model_fixtures.py`;
- the negative tests in `tests/test_world_model_fixtures.py`.

## Required questions

1. Are all core object kinds distinguishable?
2. Are space, time, precision and geometry validity explicit?
3. Does any smooth geometry, date or route imply evidence that does not exist?
4. Are Claim dimensions independent and EvidenceLink locators reproducible?
5. Is computed overlap kept outside historical Relations?
6. Are alternative reconstructions visible and non-destructive?
7. Does the compatibility projection avoid inventing Claims, locators or precision?
8. Is corpus absence kept separate from historical absence?
9. Does any artifact overclaim current runtime capability?
10. Is there any unresolved critical semantic contradiction?

## Reviewer 1

Pending independent review.

## Reviewer 2

Pending independent review.

## Finalization rule

The package can become `READY` only when:

- two independent review artifacts inspect the same frozen commit;
- the artifacts have different reviewer identities, invocation identities and review tracks (`semantic-model`, `validator-integrity`);
- each review artifact checksum matches the registry;
- each review binds the same computed review-scope digest;
- both decisions are `READY`;
- critical findings are zero;
- unresolved material findings are zero;
- each reviewer records an explicit independence attestation;
- all material findings are resolved on the branch;
- `review_registry.json` and `package.json` are synchronized;
- `python scripts/validate_world_model_fixtures.py --require-ready` passes;
- repository release/governance checks pass.

Until then #329 remains open and #332 remains gated.

