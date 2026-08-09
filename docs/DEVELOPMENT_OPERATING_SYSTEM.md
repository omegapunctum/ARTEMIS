# ARTEMIS — Development Operating System v1

## Status

- Type: canonical operational governance.
- Version: 1.0.
- Date: 2026-08-09.
- Machine-readable state: `docs/project_state.json`.
- Schema: `docs/project_state.schema.json`.

This document connects the ARTEMIS North Star to one active validation vertical, one gate and the
GitHub issues/PRs that produce executable evidence. It does not replace any semantic, product,
runtime or release owner document.

## 1. Decision hierarchy

The permitted execution chain is:

`North Star → active product hypothesis → proof vertical → current gate → issues/PRs → verified decision`

Each lower level must reference the level above it. A passing PR cannot silently change the North
Star, active product hypothesis or public capability.

## 2. Single project state

`docs/project_state.json` is the only machine-readable operational status snapshot. It records:

- the active vertical, phase and gate;
- the one allowed decision at the gate;
- active, paused and completed GitHub work;
- blockers and the next transition;
- current public/non-public capability truth;
- links to canonical owner documents.

The snapshot is an operational index, not a new semantic owner. On conflict, the owner hierarchy in
`FOUNDATION_INDEX.md` wins and the snapshot must be corrected in the same PR that changes lifecycle.

## 3. Work-in-progress rule

- One product vertical is active.
- One gate may be `in_progress`.
- Product-scope work outside that gate is paused or frozen.
- Security, compatibility and critical reliability work may proceed separately when it does not
  redefine product scope.
- A gate transition must update `project_state.json`, canonical lifecycle documents and the affected
  GitHub issues in one decision PR.

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

## 7. Pull-request core gate

Every decision PR must show:

- intended file scope;
- current gate and issue references;
- targeted checks while iterating;
- the repository release/governance checks on exact head;
- frozen review SHA when independent review is required;
- no undocumented public capability change.

Baseline failures must be named and reproducible; they cannot be used to hide a new regression.

## 8. Current application

The active vertical is `Life in Context / Globe MVP` under issue `#355`. Gate C is the bounded
Leonardo-in-Romagna source boundary under issues `#332` and `#360`. Issue `#331` remains paused,
so documented Relation predicates are prohibited. The public runtime remains the root 2D
Architecture Atlas until a later explicit promotion decision.
