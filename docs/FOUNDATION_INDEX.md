# ARTEMIS — FOUNDATION INDEX

## Статус

- Тип: canonical foundation index.
- Версия: 3.0.
- Дата: 2026-07-28.
- Статус: active; Foundation v3 accepted in PR `#328`.
- Роль: единственный реестр canonical owner documents, reading order и conflict routing.

## 1. Foundation purpose

Foundation-layer сохраняет ARTEMIS как одну source-aware spatial-temporal world model, а не набор несвязанных map, timeline, cards, backend, courses, AI and 3D features.

Он определяет:

1. что такое ARTEMIS;
2. как моделируются space, time and change;
3. какие knowledge objects существуют;
4. как утверждения связываются с evidence;
5. как различаются proximity, encounter, interaction, influence and causality;
6. какой current vertical разрешён;
7. что действительно работает;
8. как content/runtime/release/AI остаются управляемыми.

## 2. Four truth levels

| Level | Owner | Question |
|---|---|---|
| North Star | `ARTEMIS_CONCEPT.md` | Чем является ARTEMIS и какие инварианты нельзя нарушить? |
| Active product | `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md` | Для кого и что проверяется сейчас? |
| Current reality | `PROJECT_TRUTH.md` | Что фактически работает? |
| Validated outcome | `VALIDATION_DECISION.md` + active validation record | Что доказано и какая одна ветвь разрешена? |

North Star не является release promise. Backend code не является public capability. Document/schema не является user-value evidence.

## 3. Canonical registry

### Identity and product

| Document | Owner role |
|---|---|
| `README.md` | Root entrypoint and concise current summary |
| `docs/FOUNDATION_INDEX.md` | Canonical registry, routing and reading order |
| `docs/ARTEMIS_CONCEPT.md` | North Star identity and invariants |
| `docs/PRODUCT_THESIS.md` | Active user, job, hypotheses and first value |
| `docs/ARTEMIS_PRODUCT_SCOPE.md` | Active scope, frozen work and exit gates |
| `docs/PROJECT_TRUTH.md` | Public/backend/pilot/target/future facts |
| `docs/PRIORITIES.md` | Current load-bearing priorities |
| `docs/PROJECT_PHASES.md` | Operational phase order |
| `docs/VALIDATION_DECISION.md` | Recorded evidence outcome and permission to expand |

### World and knowledge model

| Document | Owner role |
|---|---|
| `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` | Temporal/spatial/change/coverage/reconstruction semantics |
| `docs/ENTITY_MODEL.md` | Knowledge/research/runtime/context entity types |
| `docs/EPISTEMIC_CONTRACT.md` | Claim/Evidence/uncertainty/inference semantics |
| `docs/CONTENT_GOVERNANCE.md` | Candidate/review/correction/publish trust |
| `docs/AI_POLICY.md` | AI behavior, source and publish boundaries |
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

## 4. Active foundation decision records

- Foundation umbrella: GitHub issue `#327`.
- Accepted decision: `docs/work/2026-07-28_FOUNDATION_V3_DECISION.md` (PR `#328`).
- Migration/disposition: `docs/work/2026-07-28_CONCEPT_V2_TO_V3_MIGRATION_MATRIX.md`.
- Validation design: `docs/work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md`.

Historical:

- `docs/work/2026-07-26_CONCEPT_LOCK_V2.md` — `SUPERSEDED`, retained for rationale/history.
- Gate A architecture module package — completed Architecture Layer fixtures, not active v3 validation.

Working lifecycle authority remains only `docs/work/README.md`.

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
10. `docs/PRIORITIES.md` and `docs/PROJECT_PHASES.md`.
11. `docs/work/README.md`, then active Foundation v3 records.
12. Task-specific data/runtime/governance contracts.

## 6. Routing

### Mission / identity

Primary: `ARTEMIS_CONCEPT.md`.

### Current vertical / scope

Primary: `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`.

### Spatial-temporal semantics

Primary: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`.

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

Primary: `AI_POLICY.md`, constrained by world and epistemic contracts.

## 7. Conflict order

1. executable checks/workflows for runtime facts;
2. `PROJECT_TRUTH.md` for capability/maturity;
3. data/runtime/release owner contracts;
4. recorded validation decision;
5. active product thesis/scope;
6. `ARTEMIS_CONCEPT.md`;
7. spatial-temporal, entity, epistemic, governance and AI contracts;
8. priorities/phases;
9. repository/documentation governance;
10. working docs;
11. audits;
12. archive/reference.

Foundation owner documents must be synchronized in one decision PR when identity changes.

## 8. Foundation v3 invariants

- spatial-temporal world model is the mission;
- space/time are mandatory;
- change objects are first-class;
- evidence is trust layer;
- proximity does not create historical relation;
- epistemic forms and uncertainty are visible;
- corpus coverage is explicit;
- Architecture Atlas is a thematic layer;
- AI is future/source-bound and not Source;
- 3D/VR/dynamic Earth are future surfaces;
- one validation decision opens one branch.

## 9. Current work status

Active:

1. Issue `#329`: versioned executable world-model fixtures and two independent semantic reviews.

Gated:

2. Issue `#330`: temporal/spatial uncertainty semantics.
3. Issue `#331`: coexistence/encounter/interaction/influence distinctions.
4. Issue `#332`: Leonardo World Slice.
5. Issue `#333`: synchronized explorer.
6. Issue `#334`: contextual-learning pilot.
7. Issue `#335`: source-bound AI contract (`GATED / NOT ACTIVE`).

Frozen:

- old Concept v2 Gate B–E critical path;
- AI generation;
- causal/counterfactual runtime;
- 3D/VR;
- universal corpus;
- product/platform expansion.

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

## 11. Final rule

If a new feature cannot be expressed through the source-aware spatial-temporal world model without breaking its epistemic or capability truth, it is not part of ARTEMIS core.
