# ARTEMIS — Progressive Refinement decision v1

## Status

- Issue: `#377`.
- Lifecycle: exact candidate/READY state is owned by the contract and review registry.
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

Round 6 froze commit `080be920cf5a37c2e40aa282f066adc64491d076` with reviewed-content
digest `55520f88d419bff63159370f19c038f2ba901ea67563d5dfa99cac54b58954c6`.
Both tracks returned `CHANGES_REQUIRED`:

- semantic-model: exact normalized assertions were not bound to the unchanged Source/Claim locator,
  and duplicated temporal precision fields could diverge;
- validator-integrity: a READY descendant could change non-metadata paths, an exclusive instant
  could become an empty set, a non-temporal correction could move to another valid time, lifecycle
  headers could contradict the package/registry, and review/finding identifiers were not unique.

Round 7 binds every normalized assertion digest to its source locator, enforces one temporal
precision and non-empty temporal sets, preserves valid time for non-temporal successor operations,
restricts the post-freeze descendant to an exact metadata/lifecycle allowlist, reconciles lifecycle
state and closes review/finding identifier uniqueness. Round-6 artifacts remain immutable negative
history and do not count toward the new reviews.

Round 7 froze commit `a26e5029c1994e02f88c2feeabae2cb5851cf21b` with reviewed-content
digest `7878b28eb43c7e38ef1d2ed43c726110003426b54c88988a19153878316b938f`.
Both tracks returned `CHANGES_REQUIRED`:

- semantic-model: temporal alternative precision could exceed source/top-level support, and the
  locator did not bind the complete source-native value/precision;
- validator-integrity: staged, unstaged, untracked or ignored worktree bytes were outside the
  committed-diff allowlist, and control metadata could be committed as a symlink to an external
  mutable payload.

Round 8 binds both source and normalized payloads at the locator, constrains every temporal
alternative precision, requires a completely clean checkout for canonical READY and verifies every
allowed lifecycle/control path as a committed regular `100644` blob. Round-7 artifacts remain
immutable negative history and do not count toward new reviews.

Round 8 froze commit `01544ead1fb0e58bbd62fcab30b88fa55f841ddf` with reviewed-content
digest `09dfac0aef6571a3b07894400320db24d97e8f5dbdde41af58d7b4cf807970ff`.
The semantic-model track returned `READY`; validator-integrity returned `CHANGES_REQUIRED` because
Git `assume-unchanged` or `skip-worktree` flags could hide modified tracked governance/control bytes
from the clean-check while canonical READY still passed.

Round 9 rejects every nonstandard tracked-index visibility marker using NUL-safe enumeration and
forces `git update-index --really-refresh` before the ordinary dirty-state checks. Round-8 artifacts
remain immutable audit history and do not count toward the new reviews.

Round 9 froze commit `d3cae310ba63a547063ea856cf5153dc50f40edc` with reviewed-content
digest `b81fb1072ef1ce727525f3affe322116945244c4127bb2a12c11821bf8e6b239`.
The semantic-model track returned `READY`; validator-integrity returned `CHANGES_REQUIRED` because
caller-controlled `GIT_WORK_TREE`, weakened stat-cache configuration or `core.fileMode=false` could
still conceal unreviewed tracked bytes/modes.

Round 10 strips repository-changing Git environment, ignores global/system configuration, forces
trustworthy core settings, verifies the discovered top-level and independently hashes and `lstat`s
every tracked worktree object against HEAD. Round-9 artifacts remain immutable audit history and do
not count toward the new reviews.

Round 10 froze commit `c2eabcf30165ee6670790defbda16af562690490` with reviewed-content
digest `36d43c6a20bd362667322c37a6738f9cc05f1c147eb8f6042ddcff3a5a2359d8`.
Both independent tracks returned `READY`, and a clean metadata-only ACCEPT descendant passed
canonical `--require-ready`. The subsequent PR workflow exposed a lifecycle-harness defect: nine
frozen tests still asserted the pre-acceptance `REVIEW_REQUIRED` state, and ordinary validation
invoked canonical checkout cleanliness after pytest created its ignored cache.

Round 11 makes the frozen harness lifecycle-aware and reserves clean-check enforcement for explicit
canonical `--require-ready`. Round-10 READY artifacts remain immutable audit history; acceptance is
reopened until the same frozen test suite passes both before and after the metadata-only transition.

Round 11 froze commit `96b9719feecb2fad571431a1c7009974d227fe7a` with reviewed-content
digest `a7f8b29d0f5abf1252a6e5122599a8482a67ec29a5f52c83634a25595d4fd6e4`.
Both tracks returned `CHANGES_REQUIRED`: canonical routing docs still asserted permanent
`REVIEW_REQUIRED`, and the workflow ran canonical cleanliness after pytest created ignored caches.

Round 12 puts lifecycle-neutral routing docs inside the frozen review scope and runs canonical
`--require-ready` before pytest. Round-11 negative artifacts remain immutable history and do not
count toward the new reviews.

Round 12 froze commit `3c72acebcd8263b4ed6b5755fa2e91d484da5a58` with reviewed-content
digest `18c27bee1ca018f94150162a5244ac2dedac7c4c9856e4cf01dc37778a2fdaef`.
Validator-integrity returned `READY`; semantic-model returned `CHANGES_REQUIRED` because additional
canonical routing text in the operating system, priorities, work registry and decision header still
encoded a permanent candidate state.

Round 13 makes the remaining current routing corpus lifecycle-neutral and includes all of it in the
frozen review scope. Round-12 artifacts remain immutable history and do not count toward new reviews.

Round 13 froze commit `7076e79e9c8915ac9f16faad4e7cfbcdee4bb56e` with reviewed-content
digest `9234431ce6e302b06d4a513d05fa89bb9dad10fbfe1978c191133b37ce3665ca`.
Validator-integrity returned `READY`; semantic-model returned `CHANGES_REQUIRED` because product
scope and fixture README were still outside scope with candidate-only wording, and Foundation Index
retained one candidate-owner label.

Round 14 neutralizes and freezes those final current #377 documents. Round-13 artifacts remain
immutable history and do not count toward new reviews.

## Rollback

Before acceptance, close #377 and remove the draft extension/fixtures. No runtime or data migration
exists to undo. After acceptance, changes require a new version; accepted revision history is not
rewritten.
