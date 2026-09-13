# ARTEMIS — FOUNDATION INDEX

Current lifecycle and capability state are intentionally not duplicated here. Use `docs/PROJECT_TRUTH.md` for current reality, `docs/project_state.json` for machine-readable operational state, and `docs/work/README.md` for active working-document lifecycle.

## Статус

- Тип: canonical foundation index.
- Версия: 3.9.
- Дата: 2026-09-13.
- Статус: active; Foundation v3.1 attractor refinement accepted in PR `#364`.
- Роль: единственный реестр canonical owner documents, owner routing и conflict routing.

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
7. какой owner отвечает на конкретный тип вопроса;
8. как content/runtime/release/AI остаются управляемыми.

## 2. Four truth levels

| Level | Owner | Question |
|---|---|---|
| North Star | `ARTEMIS_CONCEPT.md` | Чем является ARTEMIS, каков его attractor и какие инварианты нельзя нарушить? |
| Active product | `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md` | Для кого и что проверяется сейчас? |
| Current reality | `PROJECT_TRUTH.md` | Что фактически работает? |
| Validated outcome | `VALIDATION_DECISION.md` + active validation record | Что доказано и какая одна следующая ветвь может быть разрешена? |

North Star не является release promise. Backend code не является public capability. Document/schema не является user-value evidence. Attractor and broader Product Thesis do not authorize implementation scope.

## 3. Canonical registry

### Identity and product

| Document | Owner role |
|---|---|
| `README.md` | Root entrypoint and concise current summary |
| `docs/FOUNDATION_INDEX.md` | Canonical registry and owner/conflict routing |
| `docs/ARTEMIS_CONCEPT.md` | North Star identity, long-term attractor and invariants |
| `docs/PRODUCT_THESIS.md` | Active user, job and broader product hypotheses |
| `docs/ARTEMIS_PRODUCT_SCOPE.md` | Active implementation/validation scope, frozen work and current exit condition |
| `docs/PROJECT_TRUTH.md` | Public/backend/R&D/target/future facts |
| `docs/PRIORITIES.md` | Current load-bearing priorities |
| `docs/PROJECT_PHASES.md` | Operational phase order |
| `docs/DEVELOPMENT_OPERATING_SYSTEM.md` | One-vertical/one-gate execution and tool responsibility contract |
| `docs/project_state.json` | Machine-readable operational status snapshot; validated mirror, not a semantic owner |
| `docs/VALIDATION_DECISION.md` | Recorded evidence outcome and next-decision vocabulary |

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

### Data, runtime and repository

| Document | Owner role |
|---|---|
| `docs/PLATFORM_ARCHITECTURE_DECISION.md` | Canonical web-first platform, delivery/PWA, shared-renderer, scaling and Git/GitHub versus corpus-storage boundary |
| `docs/DATA_DICTIONARY.md` | Current Architecture Atlas semantic fields/artifacts |
| `docs/DATA_CONTRACT.md` | Architecture Atlas ETL/public data contract and shared render-projection boundary |
| `docs/RESEARCH_SLICE_SPEC.md` | Current mutable runtime compatibility API/schema |
| `docs/PROJECT_STRUCTURE.md` | Repository and runtime boundaries |
| `docs/DOCUMENTATION_SYSTEM.md` | Documentation placement/governance |
| `docs/ARTEMIS_MASTER_PROMPT.md` | On-demand agent operational governance; not a current-state registry |

`docs/CONTROLLED_RELEASE_DECISION.md` is preserved as a historical compatibility release decision for the Architecture Atlas/backend baseline. It is **not** the current ARTEMIS Core release owner. Current product/release behavior is routed through `PROJECT_TRUTH.md`, `DEVELOPMENT_OPERATING_SYSTEM.md`, `project_state.json` and executable workflow files.

Historical vertical documents such as `MVP_ARCHITECTURE_ATLAS.md` and the Concept v2 `PRODUCT_VALIDATION_PLAN.md` remain traceable but are not active v3 scope owners.

## 4. Foundation decision records

Accepted:

- Foundation v3: `docs/work/2026-07-28_FOUNDATION_V3_DECISION.md` / PR `#328`.
- Foundation v3.1 attractor refinement: `docs/work/2026-08-09_ARTEMIS_ATTRACTOR_REFINEMENT_DECISION_v1.md` / issue `#363` / PR `#364`.
- Platform architecture: `docs/PLATFORM_ARCHITECTURE_DECISION.md` — accepted 2026-08-29; web-first application, PWA as delivery capability, 2D/Globe as shared-core renderers, Git/GitHub separated from future corpus storage.
- Migration/disposition: `docs/work/2026-07-28_CONCEPT_V2_TO_V3_MIGRATION_MATRIX.md`.
- Formal validation design: `docs/work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md` remains gated until its broader product protocol is explicitly opened.

Historical:

- `docs/work/2026-07-26_CONCEPT_LOCK_V2.md` — `SUPERSEDED`, retained for rationale/history.
- Gate A architecture module package — completed Architecture Layer fixtures, not active v3 validation.
- `docs/CONTROLLED_RELEASE_DECISION.md` — preserved Architecture Atlas/backend controlled-release compatibility decision, not current Core lifecycle authority.

The foundation-maintenance decision is issue `#377` / `docs/work/2026-08-12_PROGRESSIVE_REFINEMENT_DECISION_v1.md`; exact status is owned by the refinement contract/registry. It cannot by itself authorize runtime/data migration or capability change. Working lifecycle authority remains `docs/work/README.md`.

## 5. Contextual reading

There is no mandatory full-document reading stack for every repository edit.

Start from the task and use the minimum authoritative context needed:

1. For non-trivial work, check `docs/PROJECT_TRUTH.md`, `docs/project_state.json` and `docs/work/README.md`.
2. Read the one canonical or active-work owner that governs the change.
3. Use this index when owner routing is unclear or the task crosses multiple owner boundaries.
4. Read additional owners only if the proposed change touches their semantics or creates a conflict.
5. For a small local edit, inspect the affected files and directly owned checks; do not preload the full foundation stack.

Common contextual routes:

- identity / attractor → `ARTEMIS_CONCEPT.md`;
- product scope → `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`;
- platform / renderer / storage → `PLATFORM_ARCHITECTURE_DECISION.md`;
- space/time/change → `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- uncertainty → `UNCERTAINTY_SEMANTICS_CONTRACT.md`;
- entities / relations → `ENTITY_MODEL.md`;
- claims / evidence / inference → `EPISTEMIC_CONTRACT.md`;
- AI behavior → `AI_POLICY.md`;
- data/runtime layout → `DATA_CONTRACT.md`, `PROJECT_STRUCTURE.md` and executable checks according to the affected contour;
- working-document status → `work/README.md`.

## 6. Routing

### Mission / identity / long-term attractor

Primary: `ARTEMIS_CONCEPT.md`.

This owner defines the identity-level interpretation that ARTEMIS models source-aware knowledge **about** the world rather than claiming to be objective reality itself.

There must not be a second canonical `ATTRACTOR.md`, `NORTH_STAR.md` or equivalent owner.

### Current vertical / scope

Primary: `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`.

`PRODUCT_THESIS.md` may describe broader hypotheses than the current MVP. `ARTEMIS_PRODUCT_SCOPE.md` owns what is authorized now.

### Reviewed spatial-temporal World Model semantics

Primary: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`.

The active v1.0 file is part of the immutable #329 READY review scope. Foundation v3.1 does not edit or reinterpret its executable semantics through a hidden documentation change. A future contract revision requires its own semantic change-control and independent review evidence.

For executable temporal/spatial uncertainty normalization and query behavior, the scoped owner is `UNCERTAINTY_SEMANTICS_CONTRACT.md`. It extends the immutable #329 base; it does not redefine core object identity or runtime schemas.

For append-only coarse-to-fine Claim/reconstruction lineage, valid-time versus record-time separation and deterministic current-frontier behavior, the scoped owner is `PROGRESSIVE_REFINEMENT_CONTRACT.md`. Its contract/registry owns the exact lifecycle; neither candidate nor accepted status can by itself authorize runtime/storage migration.

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

### Platform / delivery / renderers / repository storage boundary

Primary: `PLATFORM_ARCHITECTURE_DECISION.md`.

This owner answers whether ARTEMIS is web/PWA/native, how 2D Map and Globe relate, how client loading must scale with corpus growth, and what belongs in Git/GitHub versus future operational corpus storage. It does not override `PROJECT_TRUTH.md` for current capability or `PROJECT_STRUCTURE.md` for concrete repository/runtime layout.

### Data/runtime/current executable behavior

Primary: `DATA_DICTIONARY.md`, `DATA_CONTRACT.md`, `RESEARCH_SLICE_SPEC.md`, `PROJECT_STRUCTURE.md`, `DEVELOPMENT_OPERATING_SYSTEM.md` and executable checks according to the affected contour.

Current Core product signal and legacy compatibility checks are distinct. `scripts/release_check.py` does not by itself define current #355 product readiness.

### Research persistence

Primary: `RESEARCH_SLICE_CONTRACT.md`.

This contract is supporting scope; it does not redefine first value.

### AI

Primary: `AI_POLICY.md`, constrained by reviewed world and epistemic contracts plus the North Star identity boundary.

Future AI exploration actions may affect view/query state only through a separately approved runtime contract; they do not create a second knowledge owner.

## 7. Conflict order

1. executable checks/workflows for runtime facts within their owned contour;
2. `PROJECT_TRUTH.md` for capability/maturity;
3. profile data/runtime/platform owner contracts;
4. recorded validation decision;
5. active product thesis/scope;
6. `ARTEMIS_CONCEPT.md`;
7. spatial-temporal, entity, epistemic, governance and AI contracts;
8. priorities/phases/development operating system;
9. repository/documentation governance;
10. working docs;
11. audits;
12. archive/reference/historical compatibility decisions.

Foundation owner documents must be synchronized in one decision PR when identity changes.

A reviewed executable contract cannot be changed merely to make identity-level wording match; its own review/change-control requirements still apply.

## 8. Foundation v3.1 invariants

- ARTEMIS is an explorable source-aware spatial-temporal knowledge model about the world;
- `World Model` is the technical semantic-core name; its reviewed v1.0 executable semantics remain unchanged by Foundation v3.1;
- ARTEMIS is web-first at the application-platform level; PWA/native wrappers are delivery choices rather than competing product architectures;
- 2D Map and Globe are presentation renderers over the same semantic core, Explorer State and projection boundary;
- timeline is renderer-neutral Explorer temporal state rather than a third semantic core;
- space/time are mandatory;
- change objects are first-class;
- evidence is trust layer;
- proximity does not create historical relation;
- epistemic forms and uncertainty are visible;
- corpus coverage is explicit;
- one semantic core supports many domains;
- one semantic core supports many interfaces/renderers;
- Architecture Atlas is a thematic compatibility layer;
- AI is future/source-bound, not Source and not a silent canonical writer;
- future AI view/query actions must be visible, reversible and separate from knowledge mutation;
- a bounded research preview may be public without becoming a second semantic core or validated product capability;
- personal knowledge context is future/private and not current canonical entity scope;
- VR/AR and production-scale dynamic Earth remain future surfaces;
- attractor guides architecture but does not authorize implementation scope;
- reviewed contract integrity is not weakened for documentation convenience;
- one product decision may open at most one next branch.

## 9. Current-state routing

This index does not own or restate the current phase, gate, checkpoint, active PR sequence, publication status or next execution step.

Use:

- `docs/PROJECT_TRUTH.md` for current capability and maturity;
- `docs/project_state.json` for current phase/gate/checkpoint and machine-readable next transition;
- `docs/work/README.md` for active, gated, completed and historical working records;
- `docs/PRIORITIES.md` and `docs/PROJECT_PHASES.md` for current operational ordering;
- executable code, tests and workflows for implementation facts.

If those sources disagree, resolve the conflict using the owner hierarchy above rather than copying a snapshot into this registry.

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
