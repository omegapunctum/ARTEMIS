# ARTEMIS — Development Operating System v1.3

## Status

- Type: canonical operational governance.
- Version: 1.3.
- Date: 2026-08-12.
- Machine-readable state: `docs/project_state.json`.
- Schema: `docs/project_state.schema.json`.

This document connects the ARTEMIS North Star to one active validation vertical, one gate and the GitHub issues/PRs that produce executable evidence. It does not replace any semantic, product, runtime or release owner document.

Foundation maintenance may refine the North Star between product gates, but it must remain explicit, documentation/governance-bounded and unable to advance product state by implication.

## 1. Decision hierarchy

The permitted execution chain is:

`North Star → active product hypothesis → proof vertical → current gate → issues/PRs → verified decision`

Each lower level must reference the level above it. A passing PR cannot silently change the North Star, active product hypothesis or public capability.

The long-term attractor is architectural direction, not an implementation authorization. A feature may fit the North Star and still remain frozen until a product/technical gate explicitly opens it.

## 2. Single project state

`docs/project_state.json` is the only machine-readable operational status snapshot. It records:

- the active vertical, phase and gate;
- the one allowed decision at the gate;
- active, paused and completed GitHub work;
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
- A product gate transition must update `project_state.json`, canonical lifecycle documents and the affected GitHub issues in one decision PR.

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

## 4. Documentation classes

| Class | Purpose | Registry |
|---|---|---|
| `canonical` | Owns identity, semantics, product scope or current truth | `FOUNDATION_INDEX.md` |
| `operational` | Defines current execution and gates | this document, `PRIORITIES.md`, `PROJECT_PHASES.md` |
| `working` | Temporary decision/review evidence | `docs/work/README.md` |
| `generated` | Reproducible reports or projections | producing validator/workflow |
| `historical` | Superseded or completed context | `docs/work/README.md` or `docs/archive/` |

A document name or old status header cannot make it active.

## 5. Tool responsibilities

| System | Authoritative role |
|---|---|
| GitHub | Product, architecture, code, schemas, decisions and development status |
| Airtable | Curated World Corpus records before controlled export |
| Google Drive | External research files, large source/GIS/media artifacts and validation materials |
| Miro | Optional explanatory system map; never an architectural source of truth |
| ChatGPT | Orchestration, analysis and execution; never durable project truth by itself |

New tools are introduced only when their information flow, owner and synchronization rule are named.

## 6. Gate transition contract

A gate closes only when:

1. its bounded artifact exists;
2. relevant validators and regression checks pass;
3. required independent reviews inspect one frozen content revision;
4. unresolved critical or material findings are zero, or the decision is explicitly `NARROW`/`REJECT`;
5. cost and known gaps are recorded honestly;
6. current capability wording remains truthful;
7. exactly one next decision or stop condition is recorded.

For a machine-readable `completed` gate, these conditions are bindings rather than prose:

- `project_state.json` names the frozen commit and tree, review registry, decision artifact and cost log;
- exactly two independent review records name distinct reviewer instances, the same frozen revision, both required tracks, measured durations and durable artifacts;
- both review decisions are `READY` with zero unresolved critical and material findings;
- blockers are empty, the delivery issue moves out of `active_issues`, capability truth is updated and `next_transition` advances to the next gate or `STOP`.

The validator must reject a partial transition. Review artifacts are added only after the reviewed content revision is frozen, so the final metadata commit cannot rewrite the content that reviewers inspected.

`next_transition` is permission to consider/open the next gate, not evidence that the gate is already in progress.

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

## 8. Pull-request core gate

Every decision PR must show:

- intended file scope;
- current gate and issue references;
- targeted checks while iterating;
- the repository release/governance checks on exact head;
- frozen review SHA when independent review is required;
- no undocumented public capability change.

Baseline failures must be named and reproducible; they cannot be used to hide a new regression.

## 9. Current application

The active product vertical is `Life in Context / Globe MVP` under issue `#355`.

Gate C (`#332` / `#360`) is **completed/FREEZE** in PR `#362`; it produced the non-public Leonardo-in-Romagna source/semantic boundary. `docs/project_state.json` v1.1 preserves that exact completed-gate evidence and records Gate D as **in progress** under #355.

Foundation v3.1 Attractor refinement (`#363` / PR `#364`) is **completed**. Its accepted rules now belong to the canonical owners and executable guards; there is no active foundation-maintenance issue at this moment.

Issue `#331` is deferred, so documented Relation predicates are prohibited until it is explicitly reopened and accepted. Issues `#371` and `#373` are deferred: the nine Airtable World Model shadow tables remain empty and the merged preflight does not authorize historical writes. Issue `#335` remains gated, so AI runtime and AI view-action implementation are not active work. The public runtime remains the root 2D Architecture Atlas until a later explicit promotion decision.
