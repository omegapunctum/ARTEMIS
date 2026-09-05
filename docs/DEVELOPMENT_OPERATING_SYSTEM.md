# ARTEMIS — Development Operating System v1.6

## Status

- Type: canonical operational governance.
- Version: 1.6.
- Date: 2026-09-01.
- Machine-readable state: `docs/project_state.json`.
- Schema: `docs/project_state.schema.json`.

This document connects the ARTEMIS North Star to one active validation vertical, one gate and the GitHub issues/PRs that produce executable evidence. It does not replace any semantic, product, runtime or platform owner document.

Foundation maintenance may refine the North Star between product gates, but it must remain explicit, documentation/governance-bounded and unable to advance product state by implication.

## 1. Decision hierarchy

The permitted execution chain is:

`North Star → active product hypothesis → proof vertical → current gate → issues/PRs → verified decision`

Each lower level must reference the level above it. A passing PR cannot silently change the North Star, active product hypothesis, active scope or public capability.

The long-term attractor is architectural direction, not an implementation authorization. A feature may fit the North Star and still remain frozen until a product/technical gate explicitly opens it.

A broad Product Thesis is likewise not implementation authorization. `ARTEMIS_PRODUCT_SCOPE.md` owns the current product boundary.

## 2. Single project state

`docs/project_state.json` is the only machine-readable operational status snapshot. It records:

- the active vertical, phase and gate;
- the allowed decision set at the current gate;
- active, paused, deferred and completed GitHub work;
- blockers and the next transition;
- current public/non-public capability truth;
- links to canonical owner documents.

The snapshot is an operational index, not a new semantic owner. On conflict, the owner hierarchy in `FOUNDATION_INDEX.md` wins and the snapshot must be corrected in the same PR that changes lifecycle.

A foundation-only issue is not added to `active_issues` merely because it is being worked. The machine-readable product state changes only when the product lifecycle itself changes.

## 3. Work-in-progress rule

- One product vertical is active.
- At most one product gate may be `in_progress`.
- A completed gate may point to a next gate without starting it.
- Product-scope work outside the opened gate is paused or frozen.
- Security, compatibility and critical reliability work may proceed separately when it does not redefine product scope.
- Foundation maintenance may proceed between gates if its non-goals explicitly prohibit product/runtime expansion.
- A product gate transition must update `project_state.json`, canonical lifecycle documents and the affected GitHub issue in one decision change.
- An `ITERATE` result improves the same active loop; it does not automatically open multiple product branches.
- A continuing decision may open at most one evidence-backed next branch when the active scope explicitly permits it.

### 3.1 Progressive fidelity execution rule

ARTEMIS develops **from coarse to fine**. Research, curation and engineering should stop at the minimum sufficient fidelity that answers the current product hypothesis or gate decision; they should not pursue maximum possible detail by default.

Execution rules:

- first establish broad identity, time range, place/context, object type and uncertainty; refine only when the next decision requires it;
- preserve finer source-native values when already available, but do not create a new research task solely to obtain finer precision unless it changes product or validation semantics;
- prioritize refinement when it changes identity, ordering, overlap/co-presence, geometry, relation interpretation, UX behavior, safety/trust or the gate decision;
- hour-level historical movement, building-level coordinates, exact route geometry, exhaustive source coverage and similar high-resolution work are **not default MVP requirements**;
- later work may refine an existing object without replacing its identity or erasing earlier evidence/revisions;
- progressive fidelity never permits fabricated precision: `unknown`, approximate and range semantics remain explicit until stronger evidence exists.

This is a resource-allocation rule, not a relaxation of accuracy. ARTEMIS may be intentionally coarse at a given stage, but it must not be falsely precise.

Issue `#377` defines the accepted knowledge-refinement semantics for this rule; its exact lifecycle is owned by the contract/registry. No adapter may assume that an in-place field update preserves revision history without a separate implementation authorization. The mechanism keeps object identity stable, separates valid time from record time and appends atomic `refine`, `correct`, `add_alternative` or `withdraw` revisions. It does not change Gate D state or authorize storage/runtime migration.

## 4. Documentation classes

| Class | Purpose | Registry |
|---|---|---|
| `canonical` | Owns identity, semantics, product scope or current truth | `FOUNDATION_INDEX.md` |
| `operational` | Defines current execution and gates | this document, `PRIORITIES.md`, `PROJECT_PHASES.md` |
| `working` | Temporary decision/review evidence | `docs/work/README.md` |
| `generated` | Reproducible reports or projections | producing validator/workflow |
| `historical` | Superseded/completed/compatibility context | `docs/work/README.md`, `docs/archive/` or an explicitly classified historical decision |

A document name or old status header cannot make it active.

## 5. Tool responsibilities

| System | Authoritative role |
|---|---|
| GitHub | Product, architecture, code, schemas, decisions and development status |
| Airtable | Curated editorial records inside an explicitly authorized contour; current World Model shadow tables are non-authoritative until separately opened |
| Google Drive | External research files, large source/GIS/media artifacts and validation materials |
| Miro | Optional explanatory system map; never an architectural source of truth |
| ChatGPT | Orchestration, analysis and execution; never durable project truth by itself |

New tools are introduced only when their information flow, owner and synchronization rule are named.

The default knowledge-promotion chain is:

`Drive research originals → authorized curated corpus intake → versioned GitHub contract/evidence → controlled runtime/export projection`

This is a responsibility flow, not an automatic synchronization promise. A stage may be skipped when the active decision deliberately uses a frozen repository fixture/package, as Gate D currently does. No Drive file, Airtable row, AI output or runtime edit becomes canonical merely by existing; promotion requires the owner contract, review state and write/release gate for that contour.

## 6. Gate transition contract

A gate closes only when:

1. its bounded artifact exists;
2. relevant validators and regression checks pass;
3. required review/evidence for that gate inspects the intended revision;
4. unresolved critical or material findings are zero, or the gate-specific decision explicitly narrows/rejects/stops the contour;
5. cost and known gaps are recorded honestly where required;
6. current capability wording remains truthful;
7. exactly one next decision or stop condition is recorded.

For a machine-readable completed evidence gate such as Gate C, stronger frozen-review bindings may apply:

- `project_state.json` names the frozen commit and tree, review registry, decision artifact and cost log;
- required independent review records name distinct reviewer instances, the same frozen revision, required tracks, measured durations and durable artifacts;
- review decisions meet the gate contract with zero unresolved critical/material findings;
- blockers are empty, the delivery issue moves out of `active_issues`, capability truth is updated and `next_transition` advances honestly.

The validator must reject a partial transition. Review artifacts are added only after the reviewed content revision is frozen when the gate contract requires immutable review identity.

`next_transition` is permission/instruction for the next step, not evidence that a later gate or branch is already open.

## 7. Foundation-maintenance contract

A foundation-maintenance PR may run between product gates when all of the following hold:

1. the affected canonical owner documents are named;
2. the issue states current vs target meaning and explicit non-goals;
3. no runtime/data/schema/product implementation is introduced unless separately authorized;
4. `project_state.json` stays unchanged unless product lifecycle actually changes;
5. current capability wording stays truthful;
6. an executable guard protects the new invariant when drift risk is material;
7. the change does not create a second North Star, ontology or semantic source of truth.

Foundation maintenance does not consume the one-product-gate WIP slot, but it also cannot be used to circumvent that limit.

When a foundation-maintenance issue closes, the working decision record moves to completed evidence and canonical lifecycle owners must stop describing it as active.

## 8. Pull-request core check

Every product PR must show:

- intended file scope;
- the user-facing question and issue reference;
- targeted checks while iterating;
- ARTEMIS Core Check on the exact head for current Core-owned changes;
- frozen review identity only when reviewed semantic evidence changes;
- no undocumented public capability change.

Compatibility/backend/data paths run their owned checks when touched. Historical broad release checks are not a substitute for the Core signal.

Baseline failures must be named and reproducible; they cannot be used to hide a new regression.

## 9. Current application

The active product vertical is `Life in Context / Leonardo Temporal Map` under issue `#355`.

Gate C (`#332` / `#360`) is **completed/FREEZE** in PR `#362`; it produced the non-public Leonardo-in-Romagna source/semantic boundary. `docs/project_state.json` preserves that exact completed-gate evidence and records Gate D as **in progress** under #355.

Foundation v3.1 Attractor refinement (`#363` / PR `#364`) is **completed**. Its accepted rules belong to the canonical owners and executable guards.

Progressive Refinement v1 (`#377`) remains accepted historical evidence. Its repository-wide READY envelope is manual under #392 because mutable routing documents cannot be an immutable product dependency. Editable knowledge behavior is deferred.

Current product implementation sequence:

1. PR `#393` completed Core Reset: root Core landing, `/globe/` primary research surface, `/atlas/` compatibility-only, and one bounded `ARTEMIS Core Check` product signal.
2. PR `#395` established the calendar-based Leonardo Temporal Map loop over the frozen four-Presence Romagna scaffold.
3. The first published manual check recorded **`ITERATE`** because Range/Scrub looked too similar, timeline hierarchy was weak, place details were too persistent and single-click camera movement was too aggressive.
4. PR `#396` implemented and published the bounded correction: full-width bottom timeline, two-handle `Range`, build-origin + single-current-time `Scrub`, popup-first selection, optional right drawer, no single-click camera jump and double-click focus.
5. The fresh user check of the published #396 interface recorded **`ITERATE`**: preserve the interaction and treat remaining visual issues as non-priority.
6. PR #400 completed the reviewed major-life candidate package without runtime authorization.
7. PR #401 completed M2 with one pinned provider, one normalized external fact and the existing World Model → Explorer State → Render Projection → Globe path.
8. The recorded M2 result is `PROCEED_TO_M3`.
9. PR #403 completed M3 with two publisher identities, one Presence and explicit agreement/spatial-refinement semantics; the recorded result is `PROCEED_TO_M4`.
10. M4 records `ADOPT` for the source-federated semantic direction: source-specific reviewed intake may normalize into the canonical Claim/EvidenceLink/Source/Uncertainty path without becoming a second ontology.
11. PR #405 closed M4 without opening a successor. The owner then explicitly instructed M5 without an intervening repository decision record; this is a governance deviation and must not be rewritten as prior authorization.
12. PR #406 merged and published M5 as a bounded 11-Presence, six-period, 1452–1519 runtime proof.
13. The direct owner check recorded exactly `ITERATE`: preserve whole-life scope, address relational legibility without inventing routes, and scope the six remaining interface-composition findings.
14. The 2026-09-05 decision defines the bounded UX artifact, semantic limits, acceptance evidence and stop condition; after merge it opens exactly one implementation branch.
15. The correction uses non-route chronology cues and cannot add historical content, spatial connectors for unknown routes or a second product branch.

Current Temporal Map semantic/UI boundary:

- `Range` selects a calendar interval and uses temporal overlap;
- `Scrub` keeps a chosen build origin plus one current-time cursor and accumulates the path forward;
- map, timeline, selection and URL operate on shared Explorer State;
- `Trajectory` remains semantic authority;
- dashed connectors are chronology-only presentation, never historical route geometry;
- single-click selection does not implicitly change camera state;
- all current settlement geometries are present-day source-bound reference anchors, not exact historical positions or route evidence.

Issue `#331` is deferred, so documented Relation predicates are prohibited until it is explicitly reopened and accepted. Issues `#371` and `#373` are deferred: the nine Airtable World Model shadow tables remain empty and the merged preflight does not authorize historical writes. Issue `#335` remains gated.

Formal D1/M1/A1/P1 closeout and the old automatic Gate E sequencing are not current roadmap drivers. Basic responsive, keyboard and accessibility behavior still belongs to implementation quality, but additional evidence machinery and visual polish do not displace the active bounded source branch.

The preserved `CONTROLLED_RELEASE_DECISION.md` describes an older Architecture Atlas/backend compatibility baseline. It does not own current #355 product readiness; use current workflow files and this operating system for the active Core contour.
