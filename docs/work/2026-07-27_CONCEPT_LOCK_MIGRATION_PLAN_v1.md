# ARTEMIS — Concept Lock implementation migration plan v1

## Status

- Type: active working dependency and repository-audit plan.
- Date: 2026-07-27.
- Base: Concept Lock v2 merged in PR `#319`.
- Scope: turn the approved target model into executable, testable and publicly honest product behavior.
- Non-goal: broad runtime refactor, product expansion or a claim that target semantics already exist.

## 1. Verified current boundary

The repository currently has:

- public static map/time/detail baseline;
- canonical UUID and normalized Source/Media compatibility artifacts;
- technical Relation/Similarity separation;
- mutable ResearchSlice v2 CRUD/share compatibility runtime;
- fail-closed Pages API configuration;
- backend Stories/Courses/UGC breadth that is frozen, not part of the active product.

It does not yet have:

- `3/3 READY` deep research modules;
- first-class Claim, EvidenceLink or ClassificationAssertion artifacts;
- required source locators and evidence relation/strength;
- stable Investigation identity and immutable Slice Revisions;
- pinned dataset identity and revision-pinned sharing;
- deterministic citation-ready Research Brief export;
- target public E2E or user validation.

The current `comparison_ready` corpus and closed issue `#316` prove a compatibility envelope, not the target model approved by Concept Lock v2.

## 2. Ordered migration

### Gate A — Deep research modules

Prepare the three modules in `2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md` before designing UI around assumed content.

Exit:

- `3/3 READY`;
- 4–6 Features and 6–10 Claims per module;
- claim-level Source locators;
- at least two substantive Relations per module;
- challenge/contest/uncertainty;
- two independent reviewers;
- hidden reference revision/Brief;
- measured curation cost.

### Gate B — Claim/Evidence and classification migration

Add the first-class knowledge contract without inventing evidence:

- Claim kind, origin, review state, confidence, evidence state and uncertainty as independent axes;
- EvidenceLink with Source, locator, `supports|challenges|contextualizes` and strength;
- ClassificationAssertion;
- RelationClaim as a structured Claim;
- safe legacy projection for existing `relations.json`;
- `same_movement` removed from substantive Relation readiness;
- artifacts, ETL, semantic gate, UI adapters and tests migrated together.

Exit: all three modules can be represented losslessly and validated by executable cross-artifact checks.

### Gate C — Investigation, revision and Brief migration

Replace mutable-result semantics while preserving owner privacy:

- stable Investigation identity;
- append-only immutable Slice Revision;
- meaningful corpus/dataset/schema identity;
- revision-pinned share, or an explicitly labelled live share during migration;
- deterministic Markdown and plain-text Research Brief;
- deterministic legacy ResearchSlice v2 migration;
- rollback and owner-isolation evidence.

Exit: save/reopen/share/export reproduces one revision and its evidence chain.

### Gate D — Research interface and public target E2E

Align only the target path:

`Question → Claims → Evidence → Comparison → Findings → Conclusion / Unresolved → Revision → Brief → Reopen/Share`

Map/time stay synchronized lenses. Comparison, detail, accessibility, CSS/JS extraction and API deployment are accepted only where they support this path.

Exit: clean-browser desktop/tablet/mobile evidence on the canonical public deployment.

### Gate E — Controlled and field validation

Run exactly six primary participants with:

- same-content list/detail control;
- normal browser/notes workflow benchmark;
- counterbalanced order and equal timebox;
- two blinded Brief evaluators;
- absolute outcomes, not percentages;
- separate map/time contribution;
- 7-day unprompted reuse/revision/real share.

Exit: `VALIDATION_DECISION.md` records `ITERATE`, `EXPAND`, `NARROW` or `STOP/RETHINK`.

## 3. Existing GitHub issue remap

No existing issue should be closed as target evidence merely because its compatibility implementation passed.

| Existing item | Keep | Required correction before execution/closure |
|---|---|---|
| `#289` phase umbrella | yes | Replace pre-Concept-Lock order with Gates A–E and link new migration tracks |
| `#286` public Slice loop | rewrite | Target Investigation/revision/Brief E2E; mutable Slice CRUD is prerequisite evidence only |
| `#287` product validation | rewrite | Exactly six users, two baselines, blind two-reviewer Brief rubric and absolute decision rules |
| `#288` workspace UX | narrow | Depend on module and Claim/Evidence contracts; do not validate map-first purpose as the product thesis |
| `#310` comparison | revise | Compare Claims/evidence across 2–3 Features, not only object attributes |
| `#311` sourced detail | revise | Bind evidence to Claims with locators and challenging evidence |
| `#312` browser acceptance | keep later | Run after target interface semantics exist |
| `#313` CSS/JS stabilization | keep conditional | Only work needed by touched target surfaces |
| `#308` / draft PR `#314` deployment readiness | keep independent | Infrastructure may proceed, but cannot make mutable Slice v2 the final public contract |
| `#309` Pages/API E2E | rewrite | Remove immutable semantics from out-of-scope; depend on Gates B–C and test revision-pinned result |
| closed `#316` | historical compatibility evidence | Record as mutable ResearchSlice v2 completion; create a separate Gate C execution track |

Required new execution tracks, without assigning numbers in this document:

1. deep-module preparation and review;
2. Claim/Evidence/Classification data migration;
3. Investigation/Slice Revision/Research Brief runtime migration;
4. target interface and public E2E synchronization.

Issue bodies should be synchronized only after this plan is merged, so GitHub planning cannot outrank canonical repository truth during review.

## 4. Repository audit decisions

This audit permits:

- one agent entrypoint through `AGENTS.md`;
- one canonical registry through `FOUNDATION_INDEX.md`;
- one working lifecycle registry through `docs/work/README.md`;
- archival of obsolete AI/Courses/expansion plans;
- deletion of proven dead root artifacts and empty legacy shims;
- repair of the Pages artifact when a runtime-loaded public data file is omitted;
- executable guards for these boundaries.

This audit does not permit:

- Stories/Courses/UGC backend removal;
- broad `ui.js` or CSS refactor;
- schema or API implementation of Gates B–C;
- deployment/provider changes from draft PR `#314`;
- rewriting checked-in Airtable data;
- external product validation.

## 5. Rollback and evidence

Each migration gate must have:

- explicit owner documents;
- fixture or legacy-data migration path;
- rollback/recovery procedure;
- relevant focused tests and full release gate;
- current capability statement;
- no issue closure based only on structural checks.
