# ARTEMIS — FOUNDATION INDEX

## Статус

- Тип: canonical foundation index.
- Версия: 3.3.
- Дата: 2026-08-12.
- Статус: active; Foundation v3.1 attractor refinement accepted in PR `#364`.
- Роль: единственный реестр canonical owner documents, reading order и conflict routing.

## 1. Foundation purpose

Foundation-layer сохраняет ARTEMIS как одну source-aware spatial-temporal knowledge model about the world, а не набор несвязанных map, timeline, cards, backend, courses, AI and 3D features.

Технический термин `World Model` сохраняется. Его identity-level interpretation принадлежит `ARTEMIS_CONCEPT.md`; reviewed executable spatial-temporal semantics остаются в `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` и меняются только через собственный review path.

Foundation определяет:

1. что такое ARTEMIS и каков его long-term attractor;
2. как моделируются space, time and change;
3. какие knowledge objects существуют;
4. как утверждения связываются с evidence;
5. как различаются proximity, encounter, interaction, influence and causality;
6. как один semantic core поддерживает many domains and many interfaces;
7. какой current vertical разрешён;
8. что действительно работает;
9. как content/runtime/release/AI остаются управляемыми.

## 2. Four truth levels

| Level | Owner | Question |
|---|---|---|
| North Star | `ARTEMIS_CONCEPT.md` | Чем является ARTEMIS, каков его attractor и какие инварианты нельзя нарушить? |
| Active product | `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md` | Для кого и что проверяется сейчас? |
| Current reality | `PROJECT_TRUTH.md` | Что фактически работает? |
| Validated outcome | `VALIDATION_DECISION.md` + active validation record | Что доказано и какая одна ветвь разрешена? |

North Star не является release promise. Backend code не является public capability. Document/schema не является user-value evidence. Attractor does not authorize implementation scope.

## 3. Canonical registry

### Identity and product

| Document | Owner role |
|---|---|
| `README.md` | Root entrypoint and concise current summary |
| `docs/FOUNDATION_INDEX.md` | Canonical registry, routing and reading order |
| `docs/ARTEMIS_CONCEPT.md` | North Star identity, long-term attractor and invariants |
| `docs/PRODUCT_THESIS.md` | Active user, job, hypotheses and first value |
| `docs/ARTEMIS_PRODUCT_SCOPE.md` | Active scope, frozen work and exit gates |
| `docs/PROJECT_TRUTH.md` | Public/backend/pilot/target/future facts |
| `docs/PRIORITIES.md` | Current load-bearing priorities |
| `docs/PROJECT_PHASES.md` | Operational phase order |
| `docs/DEVELOPMENT_OPERATING_SYSTEM.md` | One-vertical/one-gate execution and tool responsibility contract |
| `docs/project_state.json` | Machine-readable operational status snapshot; validated mirror, not a semantic owner |
| `docs/VALIDATION_DECISION.md` | Recorded evidence outcome and permission to expand |

### World and knowledge model

| Document | Owner role |
|---|---|
| `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` | Reviewed temporal/spatial/change/coverage/reconstruction semantics; immutable #329 review dependency until separately re-reviewed |
| `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md` | Scoped #330 normalization, filtering and projection profile |
| `docs/PROGRESSIVE_REFINEMENT_CONTRACT.md` | #377 non-destructive coarse-to-fine revision semantics; exact lifecycle owned by its contract/registry, never runtime capability by itself |
| `docs/ENTITY_MODEL.md` | Knowledge/research/runtime/context entity types |
| `docs/EPISTEMIC_CONTRACT.md` | Claim/Evidence/uncertainty/inference semantics |
| `docs/CONTENT_GOVERNANCE.md` | Candidate intake, review, progressive correction/withdrawal and publish trust |
| `docs/AI_POLICY.md` | AI behavior, source/publish boundaries and future reversible exploration actions |
| `docs/RESEARCH_SLICE_CONTRACT.md` | Optional Investigation/revision/Brief model |

### Data, runtime, release and repository

| Document | Owner role |
|---|---|
| `docs/DATA_DICTIONARY.md` | Current semantic fields/artifacts |
| `docs/DATA_CONTRACT.md` | ETL and public data contract |
| `docs/RESEARCH_SLICE_SPEC.md` | Current mutable runtime compatibility API/schema |
| `docs/PROJECT_STRUCTURE.md` | Repository and runtime boundaries |
| `docs/CONTROLLED_RELEASE_DECISION.md` | Release/readiness interpretation |
| `docs/DOCUMENTATION_SYSTEM.md` | Documentation placement/governance |
| `docs/ARTEMIS_MASTER_PROMPT.md` | Agent operational governance |

Historical vertical documents such as `MVP_ARCHITECTURE_ATLAS.md` and the Concept v2 `PRODUCT_VALIDATION_PLAN.md` remain traceable but are not active v3 scope owners.

## 4. Foundation decision records

Accepted:

- Foundation v3: `docs/work/2026-07-28_FOUNDATION_V3_DECISION.md` / PR `#328`.
- Foundation v3.1 attractor refinement: `docs/work/2026-08-09_ARTEMIS_ATTRACTOR_REFINEMENT_DECISION_v1.md` / issue `#363` / PR `#364`.
- Migration/disposition: `docs/work/2026-07-28_CONCEPT_V2_TO_V3_MIGRATION_MATRIX.md`.
- Validation design: `docs/work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md` remains gated until its corresponding product gate is explicitly opened.

Historical:

- `docs/work/2026-07-26_CONCEPT_LOCK_V2.md` — `SUPERSEDED`, retained for rationale/history.
- Gate A architecture module package — completed Architecture Layer fixtures, not active v3 validation.

The foundation-maintenance decision is issue `#377` /
`docs/work/2026-08-12_PROGRESSIVE_REFINEMENT_DECISION_v1.md`; exact status is owned by the refinement
contract/registry. It does not consume the Gate D product WIP slot and cannot by itself authorize
runtime/data migration or capability change. Working lifecycle authority remains `docs/work/README.md`.

## 5. Reading order

1. `README.md`.
2. `docs/FOUNDATION_INDEX.md`.
3. `docs/PROJECT_TRUTH.md`.
4. `docs/ARTEMIS_CONCEPT.md`.
5. `docs/PRODUCT_THESIS.md`.
6. `docs/ARTEMIS_PRODUCT_SCOPE.md`.
7. `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`.
8. `docs/ENTITY_MODEL.md`.
9. `docs/EPISTEMIC_CONTRACT.md`.
10. `docs/AI_POLICY.md` when AI behavior or future AI interaction is relevant.
11. `docs/PRIORITIES.md`, `docs/PROJECT_PHASES.md` and `docs/DEVELOPMENT_OPERATING_SYSTEM.md`.
12. `docs/project_state.json`.
13. `docs/work/README.md`, then active/accepted Foundation records.
14. Task-specific data/runtime/governance contracts.

## 6. Routing

### Mission / identity / long-term attractor

Primary: `ARTEMIS_CONCEPT.md`.

This owner defines the identity-level interpretation that ARTEMIS models source-aware knowledge **about** the world rather than claiming to be objective reality itself.

There must not be a second canonical `ATTRACTOR.md`, `NORTH_STAR.md` or equivalent owner.

### Current vertical / scope

Primary: `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`.

### Reviewed spatial-temporal World Model semantics

Primary: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`.

The active v1.0 file is part of the immutable #329 READY review scope. Foundation v3.1 does not edit or reinterpret its executable semantics through a hidden documentation change. A future contract revision requires its own semantic change-control and independent review evidence.

For executable temporal/spatial uncertainty normalization and query behavior, the scoped owner is `UNCERTAINTY_SEMANTICS_CONTRACT.md`. It extends the immutable #329 base; it does not redefine core object identity or runtime schemas.

For append-only coarse-to-fine Claim/reconstruction lineage, valid-time versus record-time
separation and deterministic current-frontier behavior, the scoped candidate owner is
`PROGRESSIVE_REFINEMENT_CONTRACT.md`. Its contract/registry owns the exact lifecycle; neither
candidate nor accepted status can by itself authorize runtime/storage migration.

Examples:

- temporal precision;
- changing geometry;
- Event/State/Process/Trajectory/Region;
- corpus coverage;
- reconstruction mode;
- synchronized view state.

### Entity / relation types

Primary: `ENTITY_MODEL.md`.

### Claims / evidence / inference

Primary: `EPISTEMIC_CONTRACT.md`.

### Current capability

Primary: `PROJECT_TRUTH.md`.

### Data/runtime/release

Primary: `DATA_DICTIONARY.md`, `DATA_CONTRACT.md`, `RESEARCH_SLICE_SPEC.md`, `PROJECT_STRUCTURE.md`, executable checks.

### Research persistence

Primary: `RESEARCH_SLICE_CONTRACT.md`.

This contract is supporting scope; it does not redefine first value.

### AI

Primary: `AI_POLICY.md`, constrained by reviewed world and epistemic contracts plus the North Star identity boundary.

Future AI exploration actions may affect view/query state only through a separately approved runtime contract; they do not create a second knowledge owner.

## 7. Conflict order

1. executable checks/workflows for runtime facts;
2. `PROJECT_TRUTH.md` for capability/maturity;
3. data/runtime/release owner contracts;
4. recorded validation decision;
5. active product thesis/scope;
6. `ARTEMIS_CONCEPT.md`;
7. spatial-temporal, entity, epistemic, governance and AI contracts;
8. priorities/phases/development operating system;
9. repository/documentation governance;
10. working docs;
11. audits;
12. archive/reference.

Foundation owner documents must be synchronized in one decision PR when identity changes.

A reviewed executable contract cannot be changed merely to make identity-level wording match; its own review/change-control requirements still apply.

## 8. Foundation v3.1 invariants

- ARTEMIS is an explorable source-aware spatial-temporal knowledge model about the world;
- `World Model` is the technical semantic-core name; its reviewed v1.0 executable semantics remain unchanged by Foundation v3.1;
- space/time are mandatory;
- change objects are first-class;
- evidence is trust layer;
- proximity does not create historical relation;
- epistemic forms and uncertainty are visible;
- corpus coverage is explicit;
- one semantic core supports many domains;
- one semantic core supports many interfaces/renderers;
- Architecture Atlas is a thematic layer;
- AI is future/source-bound, not Source and not a silent canonical writer;
- future AI view/query actions must be visible, reversible and separate from knowledge mutation;
- the bounded Globe MVP may be an active interface surface without becoming a second semantic core or a public capability claim;
- personal knowledge context is future/private and not current canonical entity scope;
- VR/AR and production-scale dynamic Earth remain future surfaces;
- attractor guides architecture but does not authorize implementation scope;
- reviewed contract integrity is not weakened for documentation convenience;
- one validation decision opens one branch.

## 9. Current work status

Active product vertical:

1. Issue `#355`: first source-aware Globe MVP vertical.

Completed product gate:

2. Issues `#332` / `#360` + PR `#362`: Gate C `FREEZE` for the non-public Leonardo-in-Romagna World Slice, 8 August–31 December 1502.

Active product gate:

3. Gate D — source-aware Globe experience. It is **in progress** under #355 as a non-public contour over the frozen Gate C package.

Foundation status:

4. Issue `#363` / PR `#364`: Foundation v3.1 Attractor refinement — **COMPLETED**.
5. Issue `#377`: Progressive Refinement Contract v1 — **FOUNDATION MAINTENANCE**; exact lifecycle in its contract/registry, no product-gate or capability change.

Deferred/gated:

6. Issue `#331`: deferred; required before documented Relation predicates enter the real corpus/runtime.
7. Issue `#333`: superseded by #355 Gate D. Issue `#334`: deferred until Gate E.
8. Issues `#371` / `#373`: deferred; no Airtable historical import or review is active, and `historical_rows_authorized=false` remains fail-closed.
9. Issue `#335`: source-bound AI contract (`GATED / NOT ACTIVE`).

Frozen:

- old Concept v2 Gate B–E critical path;
- AI generation/runtime;
- causal/counterfactual runtime;
- public production Globe, universal historical terrain and VR/AR;
- universal corpus;
- personal knowledge model;
- product/platform expansion not opened by evidence.

Completed evidence:

- issue `#363` / PR `#364`: Foundation v3.1 long-term attractor and governance guard;
- issue `#329` / PR `#336`: READY world-model fixture package v1;
- issue `#330` / PR `#337`: READY uncertainty semantics v1;
- issues `#339`–`#345` / PRs `#346`–`#352`: renderer architecture, state, projection, asset, runtime-spike, cross-renderer parity and repository-boundary evidence;
- issues `#332` / `#360` / PR `#362`: Gate C frozen real World Slice boundary and independent review evidence.

Active product/governance decision:

- `docs/work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md`.

Accepted foundation decision:

- `docs/work/2026-08-09_ARTEMIS_ATTRACTOR_REFINEMENT_DECISION_v1.md`.

## 10. Change control

A foundation change must state:

- problem and decision;
- affected owner docs;
- current vs target boundary;
- migration/disposition;
- non-goals;
- checks;
- rollback/recovery where executable state changes.

Foundation changes must not be hidden inside UI/runtime work.

A foundation clarification between product gates must not silently advance `project_state.json` to the next product gate.

A reviewed semantic contract in a frozen READY scope must remain byte-identical unless its own review gate is deliberately reopened.

## 11. Final rule

If a new feature cannot strengthen the explorable source-aware spatial-temporal knowledge model without breaking epistemic truth, capability truth, reviewed-contract integrity or the one-semantic-core invariant, it is not part of ARTEMIS core.
