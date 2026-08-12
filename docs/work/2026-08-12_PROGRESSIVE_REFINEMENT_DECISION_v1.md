# ARTEMIS — Progressive Refinement decision v1

## Status

- Issue: `#377`.
- Lifecycle: `IN PROGRESS / REVIEW_REQUIRED`.
- Decision target: `ACCEPT | NARROW | REJECT`.
- Product gate impact: none; Gate D remains in progress under `#355`.
- Public capability impact: none.

## Problem

The project can represent uncertainty and alternatives but lacks one executable append-only
mechanism for progressively refining atomic knowledge without erasing evidence or confusing world
change with knowledge revision.

## Proposed decision

Adopt `docs/PROGRESSIVE_REFINEMENT_CONTRACT.md` as a scoped semantic extension with:

- stable object identity;
- immutable atomic revision series;
- separate valid and record time;
- `initial`, `refine`, `correct`, `add_alternative` and `withdraw` operations;
- source-native plus non-sharpening normalized values;
- deterministic current-frontier and record-time replay;
- a material-resolution budget and stop rule.

## Current versus target

Current behavior is a documented curation preference with partial uncertainty primitives. Target
behavior is a fail-closed, domain-neutral refinement ledger demonstrated by executable fixtures.

## Migration and disposition

- preserve reviewed #329/#330 bytes and evidence;
- add a scoped extension rather than editing their frozen packages;
- do not migrate Architecture Atlas, Airtable, public data or the frozen Leonardo package;
- require a later migration decision before runtime/storage adoption.

## Non-goals

- no Globe implementation or promotion;
- no historical recuration or new exactness research;
- no Airtable historical writes;
- no Relations, AI, VR/AR or universal corpus work;
- no claim of historical or product readiness.

## Required evidence

1. Contract and fixture schema/package.
2. Semantic validator and controlled-corruption tests.
3. Leonardo trajectory and ecological-range scenarios.
4. Repository checks on one frozen revision.
5. Two independent reviews with zero critical/material findings.
6. Recorded `ACCEPT`, `NARROW` or `REJECT` decision.

## Review history

Round 1 froze commit `ba1b1846cd926ad83923ae8a7908a1c21b4d3e03` with reviewed-content
digest `6afc829a0f2bf6cb8fe9f8bacdb586da882627f11da7f61e59dec00b8a3e6afc`.
Both independent tracks returned `CHANGES_REQUIRED`:

- semantic-model: `0 critical / 3 material` — reproducible source locators, full #330 temporal
  envelope and atomic-target uniqueness;
- validator-integrity: `2 critical / 5 material / 1 minor` — findings/counter reconciliation,
  Git/reviewer-slot binding, safe metadata paths, legitimate READY transition, complete semantic
  lock, canonical require-ready scope and executable final decision.

The structured round-1 artifacts are retained under
`fixtures/world_model/refinement/v1/reviews/`.

Round 2 froze commit `f9ae1e9a362d7827cf0dc48fc68435df6c853362` with reviewed-content
digest `fb54684ae9f710e2e148baea7800928ff433c8915dd50e023c0f1e5444fcb840`.
Both tracks again returned `CHANGES_REQUIRED`, with no critical findings and four material findings:

- semantic-model: the full temporal envelope was not invariant during spatial refinement;
- validator-integrity: lifecycle normalization was too broad, EvidenceLink/Uncertainty closure
  could be detached, and `NARROW`/`REJECT` could omit the frozen revision binding.

The round-3 candidate closes all four paths with controlled-corruption tests. Earlier artifacts are
retained as history and do not count toward round 3; acceptance still requires two fresh independent
reviews on one new exact commit/digest.

Round 3 froze commit `3d0062a87b04599d4e3dcf3be2ff94770c850eaa` with reviewed-content
digest `848254c2dbd3d789f947c07b4d120d9b89b98639f09b95adedf479e6aa22c27b`.
Both tracks returned `CHANGES_REQUIRED`: temporal refinement did not constrain calendar profiles or
alternatives to the predecessor possible set, and mutable control metadata could replace review
scope/reviewer slots or authorize runtime/Airtable/public changes after review.

Round 4 binds the exact review request bytes to the frozen commit, enforces all capability
prohibitions in reviewed validator code, and validates the full temporal possible-set subset. The
round-3 artifacts remain immutable history and do not count toward round 4.

Round 4 froze commit `0aa4a7a72ff672004d1be9e38e781ab09b395929` with reviewed-content
digest `1f7ca23d70da78127636a5c506684cc99cd65e7b432ae742402922f70161d02d`.
Both tracks returned `CHANGES_REQUIRED`: the temporal union could remain universal through an
unchanged unknown alternative while the primary narrowed, open/inclusivity/precision-only
narrowing was mishandled, and mutable control schemas could introduce a new authorization field.

Round 5 evaluates strictness over the full temporal union and byte-binds all four review control
schemas to the frozen commit. Round-4 artifacts remain immutable history and do not count toward
the new reviews.

Round 5 froze commit `efb7b21ed4e62bb038701c79eda4769ad3e9eef9` with reviewed-content
digest `e9f60c26b458c5be14451b4f899f69751e8261c72865d1535c4d894637bf1e33`.
Both tracks returned `CHANGES_REQUIRED`: pairwise member containment still accepted an unchanged
union split across primary/alternative members, and prior negative review history could be erased
after freeze.

Round 6 canonicalizes merged temporal unions before strictness comparison and preserves
`prior_reviews` exactly from the frozen registry. Round-5 artifacts remain immutable history.

## Rollback

Before acceptance, close #377 and remove the draft extension/fixtures. No runtime or data migration
exists to undo. After acceptance, changes require a new version; accepted revision history is not
rewritten.
