# ARTEMIS — RELATION LADDER CONTRACT

## Status

- Type: scoped canonical extension.
- Version: 1.0.
- Date: 2026-08-05.
- Status: `REVIEW_REQUIRED`.
- Active issue: `#331`.
- Extends: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`, `EPISTEMIC_CONTRACT.md` and `UNCERTAINTY_SEMANTICS_CONTRACT.md`.
- Owns: executable relation-ladder predicates, promotion barriers, evidence requirements and language rules.
- Does not own: runtime/database schemas, historical corpus curation, public UI implementation or automated causal discovery.

The reviewed #329 and #330 packages remain immutable dependencies. This contract adds a versioned
relation profile without rewriting their semantic evidence.

## 1. Invariants

1. Spatial-temporal overlap produces only a computed observation.
2. No ladder level is promoted automatically to a stronger level.
3. `possible_encounter` is an inference with explicit assumptions and uncertainty, not a documented Relation.
4. Every documented level binds one atomic RelationClaim to reviewed EvidenceLinks and reproducible locators.
5. `interaction`, `influence` and `causal` require evidence for their own predicate, not merely for a weaker level.
6. Classification, Similarity, proximity and before/after remain structurally separate signals.
7. Direction, mechanism, scope and causal basis are explicit where the predicate requires them.

## 2. Non-overlapping ladder

| Level | Meaning | Storage form | Minimum basis |
|---|---|---|---|
| `co_present` | extents overlap in the declared place and time | computed observation | deterministic extent calculation plus visible uncertainty |
| `possible_encounter` | encounter is plausible under named assumptions | explicit inference | `co_present`, assumptions and relation uncertainty |
| `documented_encounter` | meeting or contact is documented | RelationClaim | reviewed supporting EvidenceLink with locator |
| `interaction` | exchange or action between entities is documented | RelationClaim | evidence of the specific exchange/action |
| `influence` | a directional historical effect is asserted | RelationClaim | named mechanism, bounded scope and supporting evidence |
| `causal` | a separately justified causal dependency is asserted | RelationClaim | distinct causal basis and approved policy reference |

Evidence for a stronger predicate may also imply a weaker ordinary-language fact, but the stored Claim keeps
the predicate actually supported. The system never rewrites or promotes a record merely because its rank is higher.

## 3. Deterministic derived levels

`co_present` requires at least one shared `place_ref` and an overlap between closed normalized temporal
intervals after uncertainty rules are applied. Different cities, disjoint intervals or unknown extents do not
produce co-presence.

`possible_encounter` additionally requires:

- a system-visible inference Claim;
- all assumptions as structured text, never hidden defaults;
- at least one relation uncertainty record;
- no representation as a documented historical Relation.

Plausibility may be withdrawn when an assumption is contradicted. Missing evidence is not positive evidence of
an encounter.

## 4. Documented predicates

For `documented_encounter`, `interaction`, `influence` and `causal`, the RelationClaim must bind exactly to the
fixture case subject, predicate and object. Every supporting EvidenceLink must bind to that Claim and to a checked-in
Source through a reproducible locator.

Additional requirements:

- `documented_encounter`: the source documents contact or meeting;
- `interaction`: `action` describes the supported exchange;
- `influence`: direction is `subject_to_object`, with explicit `mechanism` and `scope`;
- `causal`: a different Claim supplies `causal_basis_claim_ref`, and `causal_policy_ref` names the separately
  reviewed policy used by the synthetic contract fixture.

An encounter source cannot be reused to claim interaction, influence or causality unless the located passage
supports that stronger assertion.

## 5. Promotion barriers

The executable profile rejects these boundary collapses:

These are five explicit negative regression classes, one for every adjacent ladder boundary:

1. proximity or overlap → `possible_encounter` without assumptions;
2. `possible_encounter` → `documented_encounter` without a source-bound Claim;
3. `documented_encounter` → `interaction` without evidence of exchange/action;
4. `interaction` → `influence` without directional mechanism and scope;
5. `influence` → `causal` without a distinct causal basis and policy reference.

`same_movement`, shared Layer membership and Similarity never enter this ladder.

## 6. UI language

| Level | Required wording | Forbidden implication |
|---|---|---|
| `co_present` | “present in the same declared place/time” | “met”, “knew”, “interacted” |
| `possible_encounter` | “may have encountered, if …” plus assumptions | “met” without qualification |
| `documented_encounter` | “documented meeting/contact” plus source access | exchange, influence or causality |
| `interaction` | name the documented action/exchange | influence or causality |
| `influence` | name direction, mechanism and bounded scope | general causality |
| `causal` | name the causal basis and policy | certainty beyond the reviewed Claim |

The public implementation under #333 must distinguish these levels without relying on colour alone. This contract
defines language semantics only; it does not implement the UI.

## 7. Architecture Atlas compatibility

- `same_movement` projects to shared classification and never to a ladder Relation;
- Similarity remains a computed candidate signal without canonical Relation identity;
- current `influenced` and `inspired_by` records remain unresolved candidates until a Claim, locator, direction,
  mechanism and scope satisfy this contract;
- structural `part_of` and `reconstructed_from` remain substantive predicates outside the encounter ladder;
- compatibility adapters must expose missing semantics and cannot invent them.

No current Airtable/public Relation is migrated by this contract.

## 8. Executable fixtures

The package includes same-city/no-contact, disjoint-place, plausible encounter, ambiguous assumption,
documented encounter, interaction, influence, causal, shared-classification and Similarity cases. Synthetic sources
exist only to test the contract and are not historical evidence or corpus capability.

## 9. Capability boundary

Passing the package proves relation semantics are representable and fail closed. It does not create a mature
relation graph, curate the Leonardo World Slice, migrate current Relations or prove public UI comprehension.

## 10. Change control

Changes require synchronized contract, fixture schema/package, validator, negative boundary tests, compatibility
statement, working review record and two independent reviews on one frozen commit. READY additionally requires
canonical review artifacts, one reviewed digest, Git/tree binding and a current-HEAD `--require-ready` CI gate.
