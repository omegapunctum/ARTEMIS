# World-model fixture package — review record

## Status

- Issue: `#329`.
- Package: `fixtures/world_model/v1/`.
- Current decision: `REVIEW_REQUIRED`.
- Previous reviewed head: `2da475092223a839f029f9a69334524fd205537a`.
- Previous verdicts: semantic-model `CHANGES_REQUIRED` (`0/1/0`); validator-integrity `CHANGES_REQUIRED` (`0/1/0`).
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

The second repeated review cycle on `9fed7d5…` additionally found:

- Relation time/place precision not stated by the basis Claim and supporting locator;
- empty/null reviewer identities and boolean finding counts accepted by READY;
- open temporal/spatial/view shapes and incomplete temporal alternatives;
- reversed temporal intervals and modeled contexts outside WorldSlice time;
- compatibility Claims accepted from self-declared rather than deterministic mappings;
- camera bounds accepted under a non-geographic CRS.

The next correction makes these cases executable failures and remains `REVIEW_REQUIRED` until another fresh pair of reviews.

The third repeated review cycle on `2d620365…` confirmed semantic readiness but found two remaining validator-integrity gaps:

- Relation Claim/evidence did not fully bind both endpoints, the Relation target, non-place geometry and the exact interval expression;
- compatibility mapping fixed IDs/statements/coordinates but still allowed confidence/review promotion or uncertainty rewriting.

The next correction binds Relation endpoints and canonical extent expressions, compares the full compatibility target to one deterministic pinned mapping, and adds adversarial regressions for each bypass.

The review cycle on `6ed30e67…` confirmed the previous geometry-set, exclusion-ID, locator-uniqueness and timestamp fixes, then found:

- unbound Trajectory subject and generic Claim/identity payload;
- co-presence accepted from an `absent` State;
- WorldSlice bounds, manifest reference and corpus meaning outside the exact semantic gate;
- background evidence accepted as sufficient for a strong supported Claim;
- mutable uncertainty effect/visibility and hidden local/global layers;
- topologically identical alternative polygons with rotated rings;
- READY artifacts whose free narrative could contradict self-declared decision/count fields;
- a truncated locator token and premature `reviewed_at` metadata.

The pending correction makes these executable failures through typed State/coverage/uncertainty policies, exact Claim/identity/Trajectory and WorldSlice assertions, normalized polygon topology, evidence-strength derivation and closed structured review findings. These changes remain `REVIEW_REQUIRED` until a new frozen head passes CI and two fresh independent reviews.

The review cycle on `fdcec3f4…` confirmed those corrections and then found:

- complete Claim epistemic fields and exact target/backlink roles could be rewritten together with their source assertion;
- structured State, Relation, Trajectory and extent payload could contradict the fixed Claim statement after coordinated assertion/checksum updates;
- Event participant sets, change-object labels, Layer coverage and object-to-layer membership were outside one closed scenario envelope;
- SynchronizedView local/global roles, camera, reconstruction mode and selection were not one executable spatial configuration;
- an unclosed locator delimiter could truncate the reviewed passage, semantically duplicate EvidenceLinks could inflate evidence, and invalid polygon backtracking or exterior holes were accepted;
- an otherwise READY package could use a future `reviewed_at` timestamp.

The next correction pins the complete normalized v1 semantic payload to a validator-owned digest while preserving specialized structural checks. It also uses one strict locator tokenizer, rejects duplicate EvidenceLink tuples, validates polygon ring/hole/component topology, binds View selection to temporally visible context and bounds READY review time. The package remains `REVIEW_REQUIRED` until publication, CI and another fresh pair of independent reviews.

The review cycle on `7c006211…` found no unresolved semantic-model blocker and confirmed that the normalized digest permits only the intended status/reviewed-at transition. Validator-integrity review found two remaining READY-envelope gaps:

- duplicate JSON keys could be interpreted differently by first-wins consumers and Python's last-wins parser while the canonical review digest hid the ambiguity;
- review/package timestamps could predate the frozen commit because attestations had no independently bound completion time.

The pending correction applies one duplicate-key/non-finite rejecting loader to every JSON artifact. Each review and its closed artifact gains a strict UTC completion timestamp; every completion must follow the frozen commit and precede validation, while package `reviewed_at` must follow both reviews. These changes remain `REVIEW_REQUIRED` until a new exact SHA passes CI and two fresh independent reviews.

The review cycle on `7a1c92b…` confirmed the full semantic, duplicate-key and chronology contours. Validator-integrity review found one remaining parser-divergence case: valid JSON exponent syntax such as `1e999` overflowed Python's default float conversion to infinity without invoking the lexical non-finite hook.

The pending correction adds strict finite float parsing, a recursive finiteness assertion and non-finite-rejecting canonical serialization. Full-READY regressions cover positive and negative exponent overflow. The package remains `REVIEW_REQUIRED` until the resulting SHA passes CI and another fresh review pair.

The review cycle on `2da47509…` confirmed overflow rejection but found one shared finite-number class: precision-rich decimal tokens and nonzero underflow could round to the same binary64 value before semantic and review-scope hashing, allowing post-freeze raw package drift.

The pending correction defines an explicit canonical binary64 lexical contract. A JSON decimal must be numerically equal to the shortest round-trip representation of its parsed float; precision loss, nonzero underflow and signed zero are rejected. Full-READY regressions cover coordinate precision drift, positive/negative underflow and integer/decimal signed zero. The package remains `REVIEW_REQUIRED` pending CI and fresh reviews.

## Finalization rule

The package can become `READY` only when:

- two fresh, separate agent-task review artifacts inspect the same resolvable frozen commit;
- both structured artifact fields exactly match the registry;
- both decisions are `READY`;
- critical findings and unresolved material findings are zero;
- the frozen commit tree and current immutable review scope have the same digest;
- `record_time.reviewed_at`, `review_registry.json` and `package.json` are synchronized;
- every review completion time is after the frozen commit, no review/package time is future-dated, and package `reviewed_at` is not earlier than either review;
- `python scripts/validate_world_model_fixtures.py --require-ready` passes;
- repository release/governance checks pass.

Reviewer identity is an external operational fact: the validator verifies distinct invocation attestations and content bindings, while merge authority verifies the actual separate executions.

Until then #329 remains open and #332 remains gated.
