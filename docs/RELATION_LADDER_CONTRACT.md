# ARTEMIS — RELATION LADDER CONTRACT

## Status

- Type: scoped canonical extension.
- Version: 1.2.
- Date: 2026-08-05.
- Status: `REVIEW_REQUIRED`.
- Active issue: `#331`.
- Extends: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`, `EPISTEMIC_CONTRACT.md` and `UNCERTAINTY_SEMANTICS_CONTRACT.md`.
- Owns: executable relation predicates, inference barriers, evidence requirements and language rules.
- Does not own: runtime/database schemas, historical corpus curation, public UI implementation or automated causal discovery.

The reviewed #329 and #330 packages remain immutable dependencies. This contract adds a synthetic relation
profile without rewriting their semantic evidence.

## 1. Core decision

The historical name “relation ladder” is retained for issue and artifact traceability, but the model is **not a total order** and does not contain a shared rank.

- `co_present` is a computed spatial-temporal observation;
- `possible_encounter` is an assumption-bound inference from a co-presence signal;
- `documented_encounter`, `interaction`, `influence` and `causal` are independent typed Claims;
- a source may support more than one predicate, but every predicate needs its own atomic assertion and basis;
- no record is rewritten, promoted or inherited merely because another predicate is present.

Therefore correspondence, mediated action, institutional effects and posthumous influence remain representable
without inventing personal co-presence. A documented encounter does not imply exchange or influence. An
interaction does not imply influence. Influence does not imply causality.

## 2. Invariants

1. Spatial-temporal overlap produces only a computed observation.
2. No predicate is promoted automatically to another predicate.
3. `possible_encounter` requires a visible co-presence result, explicit assumptions and relation uncertainty.
4. Every documented predicate binds one atomic RelationClaim to reviewed EvidenceLinks and reproducible locators.
5. Documented predicates do not require a separately modeled co-presence record when their own source directly
   establishes the assertion; missing extents remain missing.
6. `interaction`, `influence` and `causal` require evidence for their own predicate.
7. Classification, Similarity, proximity and before/after remain structurally separate signals.
8. Direction, mechanism, transmission mode, scope and causal basis are explicit where required.
9. `no_relation_asserted` means only that the fixture creates no Relation; it never asserts historical absence.
10. Background evidence cannot support a documented Relation predicate.
11. Absence of a place-hierarchy edge is `unknown`; `excluded` requires explicit disjointness or non-overlapping geometry.
12. Every evidence Source is a canonical regular file inside the frozen semantic review scope.

## 3. Predicate profile

| Predicate | Storage form | Minimum basis | Co-presence prerequisite |
|---|---|---|---|
| `co_present` | computed observation | reviewed #330 extents, deterministic overlap, visible uncertainty | n/a |
| `possible_encounter` | explicit inference | confirmed/possible co-presence, assumptions, relation uncertainty | yes |
| `documented_encounter` | RelationClaim | source-supported meeting/contact with locator | no |
| `interaction` | RelationClaim | source-supported action plus channel | no |
| `influence` | RelationClaim | direction, mechanism, transmission mode, bounded scope and evidence | no |
| `causal` | RelationClaim | same-endpoint distinct causal basis and resolvable policy | no |

Ordinary language may make some predicates sound stronger than others, but this does not create logical
inheritance in storage or validation.

## 4. Extent and co-presence semantics

The relation fixture consumes the reviewed #330 `bound` definition exactly and preserves the reviewed temporal
`candidate` and `spatialCase` shapes with one deliberate field rename: `semantic_profile_refs`. These references
select a reviewed #330 kind/mode profile. They are not evidence bindings and cannot imply that an immutable #330
fixture Claim supports a different relation-fixture date, place, route or coordinate.

All relation extents in this package are declared synthetic test inputs. Historical/runtime extents must instead
bind their exact normalized assertion to corpus Claims, EvidenceLinks and source locators under the #329/#330
contracts. Changing an arbitrary relation extent while retaining a semantic profile therefore changes a test
vector, not historical evidence.

Supported inputs include:

- exact and closed temporal intervals;
- bounded and approximate ranges;
- open-start and open-end intervals;
- competing temporal or place reconstructions;
- named and nested places;
- exact and approximate points;
- inferred route corridors and unknown extents.

Polygon corridor evaluation includes interior rings, treats boundaries conservatively as included and unwraps
longitude edges across the antimeridian. An approximate point overlaps an inferred corridor when its declared
tolerance reaches the corridor boundary, even if the point centre lies outside. Non-finite coordinates or
tolerances are rejected at JSON load/validation.

Named places overlap when they are identical or ancestor-related. A closed `place_disjointness` set provides the
only fixture basis for excluding otherwise un-geometrized named places. Missing hierarchy or alias information
produces `unknown`, not a false negative.

The deterministic result is one of:

- `confirmed` — every represented candidate combination overlaps without an uncertainty promotion;
- `possible` — at least one reconstruction overlaps, or overlap depends on approximate/open/inferred extents;
- `excluded` — all candidate combinations are disjoint in time or space;
- `unknown` — the available extents cannot decide overlap.

`confirmed` and `possible` may be displayed as qualified co-presence observations. Neither creates a historical
Relation. `unknown` must not be converted to absence, and `excluded` does not invalidate an independently
documented correspondence, mediated interaction, influence or causal process.

## 5. Possible encounter

`possible_encounter` additionally requires:

- a `confirmed` or `possible` co-presence result;
- a system-visible inference Claim;
- all assumptions as structured records, never hidden defaults;
- at least one relation uncertainty record;
- no representation as a documented historical Relation.

Plausibility may be withdrawn when an assumption is contradicted. Missing evidence is not positive evidence of
an encounter.

## 6. Documented predicates

For `documented_encounter`, `interaction`, `influence` and `causal`, the RelationClaim binds exactly to the
fixture case subject, predicate and object. Every supporting EvidenceLink binds that Claim to a checked-in Source
through a reproducible locator. Only reviewed `direct` or `indirect` evidence can satisfy a documented predicate;
`background` evidence remains contextual and cannot do so.

The package selects exactly one canonical synthetic Source, and its path is part of the fixed review scope. A safe
repository path outside that scope is still invalid: evidence content cannot move outside the frozen digest.

Additional requirements:

- `documented_encounter`: the source names contact or meeting;
- `interaction`: `action` and `channel` identify in-person, correspondence, intermediary or institutional exchange;
- `influence`: direction is `subject_to_object`, with mechanism, transmission mode and bounded scope;
- `causal`: a distinct Claim supplies `causal_basis_claim_ref`; it has the same target, subject and object as the
  causal Claim, carries non-background supporting evidence, and `causal_policy_ref` resolves to the checked,
  digest-bound synthetic policy inside this package's review scope.

The included causal policy is only an executable fixture policy. Production causal assertions require a separate
governed and independently reviewed production policy; READY for this package cannot be presented as that approval.

An encounter source cannot be reused to claim interaction, influence or causality unless the located passage
supports the additional atomic predicate.

## 7. Promotion and implication barriers

The five rules below are regression boundaries, not links in an ordered chain. These are five explicit negative regression classes:

1. `co_present` permits `possible_encounter` only with explicit assumptions, uncertainty and an inference Claim;
2. `possible_encounter` does not imply `documented_encounter` without a source-bound encounter Claim;
3. `documented_encounter` does not imply `interaction` without evidence of action and channel;
4. `interaction` does not imply `influence` without direction, mechanism, transmission mode and scope;
5. `influence` does not imply `causal` without a distinct causal basis and policy reference.

The validator must also accept the inverse independence cases: interaction across distance, interaction through an
intermediary, posthumous influence, documented contact with unknown modeled extents and causality between
processes.

`same_movement`, shared Layer membership and Similarity never enter this predicate profile.

## 8. UI language

| Predicate | Required wording | Forbidden implication |
|---|---|---|
| `co_present` | `Extent overlap: {co_presence_result}` plus temporal/spatial precision and uncertainty | met, encountered, contact, knew, interacted, influenced, caused |
| `possible_encounter` | “Possible encounter under declared assumptions” plus overlap result, assumptions and relation uncertainty | documented meeting/contact, interaction, influence or cause |
| `documented_encounter` | “Documented meeting/contact” plus locator, contact kind and extent conflicts | exchange, interaction, influence or cause |
| `interaction` | “Documented action or exchange” plus locator, action and channel | influence or cause |
| `influence` | “Supported directional influence within stated scope” plus mechanism/transmission/scope | cause or necessity |
| `causal` | “Separately justified causal claim within stated scope” plus counterfactual basis and policy | certainty beyond the reviewed Claim |

The executable package fixes unique coverage, exact label templates, required-disclosure sets, forbidden-phrase
sets and source-access requirements. A possible extent overlap can never be rendered with an unqualified assertion
of actual presence. The public implementation under #333 must distinguish predicates without relying on colour alone.

## 9. Architecture Atlas compatibility

- `same_movement` projects to shared classification and never to a Relation predicate;
- Similarity remains a computed candidate signal without canonical Relation identity;
- current `influenced` and `inspired_by` records remain unresolved candidates until a Claim, locator, direction,
  mechanism, transmission mode and scope satisfy this contract;
- structural `part_of` and `reconstructed_from` remain substantive predicates outside this profile;
- compatibility adapters expose missing semantics and cannot invent them.

No current Airtable/public Relation is migrated by this contract.

## 10. Executable fixtures

The package covers same-city/no-contact, disjoint-place, plausible and ambiguous encounter, documented encounter,
contact with unknown extents, correspondence, intermediary action, posthumous influence, process causality,
approximate/open temporal overlap, competing place reconstruction, nested places and inferred route proximity.

Synthetic sources exist only to test the contract and are not historical evidence or corpus capability.

## 11. Capability boundary

Passing the package proves relation semantics are representable and fail closed. It does not create a mature
relation graph, curate the Leonardo World Slice, migrate current Relations or prove public UI comprehension.

## 12. Change control

Changes require synchronized contract, fixture schema/package, policy, validator, adversarial tests, compatibility
statement, working review record and two independent reviews on one frozen commit. READY additionally requires
closed canonical review artifacts, one reviewed digest recomputed from both the worktree and frozen Git tree,
regular tracked blobs, sanitized Git configuration, transition artifacts identical to HEAD and a current-HEAD
`--require-ready` CI gate. Only the declared READY metadata fields—package/owner status, reviewed timestamp,
working-record state, frozen SHA, digest and review summary—are normalized across that transition.
Normalization is not trust: the validator independently requires README status and every working-record lifecycle
field to equal the package/registry values, with exact `PENDING` values before review and exact two-track READY
wording after review.
