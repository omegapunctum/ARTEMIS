# ARTEMIS — МАСТЕР-ПРОМПТ v6.9

Статус: canonical on-demand operational governance for AI agents and assistants.
Дата: 2026-09-13.

Этот документ не является current-state registry. Текущие capability, phase/gate/checkpoint, active work и next transition брать из `PROJECT_TRUTH.md`, `project_state.json` и `work/README.md`, а не копировать сюда.

## 1. Роль проекта

ARTEMIS — source-aware spatial-temporal knowledge model about the world.

Технический `World Model` является semantic-core name. Identity-level North Star определяет ARTEMIS как source-aware representation of knowledge about the world, а не как утверждение об объективной или полной реальности.

Long-term attractor:

> explorable source-aware spatial-temporal model of human knowledge about the world, usable by people and future AI as one connected cognitive environment.

Attractor constrains direction; it does not authorize current implementation scope.

## 2. Source of truth and routing

Use the owner that matches the question:

- canonical registry / owner routing → `docs/FOUNDATION_INDEX.md`;
- current capability / maturity → `docs/PROJECT_TRUTH.md`;
- machine-readable execution state → `docs/project_state.json`;
- active working-document lifecycle → `docs/work/README.md`;
- North Star / attractor → `docs/ARTEMIS_CONCEPT.md`;
- active product scope → `docs/PRODUCT_THESIS.md`, `docs/ARTEMIS_PRODUCT_SCOPE.md`;
- platform / renderer / repository-storage boundary → `docs/PLATFORM_ARCHITECTURE_DECISION.md`;
- spatial-temporal semantics → `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- uncertainty → `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md`;
- entities / relation types → `docs/ENTITY_MODEL.md`;
- Claims / evidence / inference → `docs/EPISTEMIC_CONTRACT.md`;
- AI behavior → `docs/AI_POLICY.md`;
- execution process → `docs/DEVELOPMENT_OPERATING_SYSTEM.md`.

Working/audit/archive files cannot override canonical owners.

Do not require a fixed full-document stack before every edit. Read the minimum authoritative context needed for the task; use `FOUNDATION_INDEX.md` when owner routing is unclear or multiple owners may conflict.

No separate `ATTRACTOR.md`, `NORTH_STAR.md` or competing semantic owner may be created.

## 3. Foundation invariants

1. ARTEMIS models source-aware knowledge about the world; it does not claim objective completeness.
2. Space and time are mandatory coordinates.
3. Event, State, Process, Trajectory and Region are first-class change semantics where applicable.
4. Precision, uncertainty, provenance and corpus coverage remain explicit.
5. Co-presence is not encounter, interaction, influence or causality.
6. Relation is a structured Claim; AI output is not Source.
7. Dataset absence is not historical absence.
8. Current capability is separate from concept and validated user value.
9. One semantic core supports many domains and interfaces.
10. No competing semantic/world-model source of truth.
11. Renderer engines do not own domain semantics.
12. Renderer payloads are projections of one World Model / World Slice, not independent historical truth datasets.
13. 2D/3D differences must not change object identity, temporal validity, evidence or uncertainty meaning.
14. Timeline is renderer-neutral Explorer temporal state, not a separate truth model.
15. Reviewed/frozen contracts retain their reviewed meaning until their own change-control path is reopened.
16. AI view/query actions, if implemented, must be visible, reversible and separate from canonical knowledge mutation.

## 4. Stable technical and historical constraints

The following are preserved constraints/evidence, not a mutable current-work snapshot:

- ARTEMIS is web-first; PWA/native packaging is delivery, not a second product architecture.
- 2D Map and Globe share one World Model / Explorer State / Render Projection core.
- Vanilla JavaScript + MapLibre remains the current implementation baseline unless an explicit architecture decision changes it.
- FastAPI/SQLite remain compatibility runtime/storage baselines outside the static Core path.
- `data/features.geojson` is the Architecture Atlas 2D projection/source, not the universal Foundation representation or Leonardo historical authority.
- the root Core landing, `/globe/` research prototype and `/atlas/` compatibility-only surfaces must remain semantically distinct.
- Active product vertical: `Life in Context / Leonardo Temporal Map` / issue `#355`.
- Preserve completed #344 / PR #351 semantic parity as a green renderer foundation.
- Issue #331 is `DEFERRED`; documented Relation predicates must not enter the real corpus/runtime until explicitly reopened and accepted.
- Foundation v3 / v3.1 accepted history remains intact; the superseded #323–#325 path and PR #314 remain closed.
- Gate D is **COMPLETED / ADVANCE_TO_GATE_E** under #355 as historical lifecycle truth. Implementation success and public R&D access do not by themselves close the gate or prove user value.

Any more recent operational status, publication state or next action must come from the current-state owners in section 2.

## 5. Scope and decision boundaries

A capability may fit the long-term attractor and still be out of current scope.

Before a material change, determine:

- which owner authorizes the semantics;
- whether a reviewed/frozen contract is affected;
- whether the task changes product scope, implementation only, or evidence only;
- whether the requested outcome can be achieved with a smaller reversible change.

Do not stop merely because an older instruction once required a review checkpoint. Continue through ordinary implementation and local verification when the requested task and current owner clearly authorize it.

Stop when the next action is destructive/irreversible, affects production or an external system without approval, changes unauthorized product/domain semantics, reopens a frozen contract implicitly, or materially broadens the requested scope.

## 6. Renderer / Temporal Map rule

When work touches map, Globe, timeline or another renderer:

- start from shared World Model / World Slice semantics;
- keep selected time/layers/object state renderer-neutral where it belongs in Explorer State;
- convert through explicit render projection boundaries;
- preserve canonical object identity and epistemic references;
- expose unsupported semantics rather than inventing them;
- never invent route, geometry, altitude, terrain history or temporal precision because a renderer can draw it;
- keep camera/GPU/tile/picking details outside the semantic core;
- semantic parity is required when multiple renderers represent the same state; screenshot equality is not semantic parity;
- presentation-only chronology must never become historical route geometry.

Read the specific renderer/interaction owner only when the task touches that behavior.

## 7. AI rule

For AI behavior, use `AI_POLICY.md` and the relevant epistemic/world-model owners.

AI may explain, normalize or propose candidates. It may not silently mutate canonical Claims, Evidence, Sources or Uncertainty, and a view change is not evidence.

Do not implement AI behavior merely because it appears in the long-term attractor.

## 8. Change discipline

Prefer minimal, logically complete changes without unrelated refactoring.

For product/model/governance changes, update the correct owner document when the decision itself changes. Do not perform documentation ceremony for a local implementation change whose owner semantics remain unchanged.

A frozen reviewed semantic contract requires its own review evidence before semantic modification; do not weaken validators or digests to make a change pass.

Never:

- invent dates, geometry, routes, evidence, locators or certainty;
- use smooth interpolation as historical fact;
- treat modern boundaries/terrain as timeless historical state;
- convert co-presence/similarity into documented Relation;
- treat AI output as Source;
- create renderer/domain-specific truth-model forks;
- rewrite old issues into new meaning;
- use archive/audit as active owner;
- treat attractor or broad Product Thesis as implementation authorization.

## 9. Verification and persistence

Run the smallest relevant owned checks for the affected contour.

For ordinary local repository work, proceed through implementation, relevant local verification, fixes for failures caused by the requested change, and rerun affected checks without asking for approval at each intermediate step.

Do not run unrelated repo-wide suites by default. Broader suites are appropriate only when the changed contour or owner contract requires them.

Verification proves implementation behavior only. It does not prove product value.

## 10. Completion

A task is complete when:

- the requested artifact or behavior exists;
- only intended scope changed;
- relevant checks pass or remaining failures are honestly classified;
- canonical semantics and reviewed-contract integrity are preserved;
- no false epistemic/spatial/temporal precision was introduced;
- current-state owners are updated only if current state actually changed.

Do not create a new planning or evidence artifact merely to restate information already owned elsewhere.

## 11. Response format

For analysis: conclusion → conflicts/evidence → recommended decision → next action.

For implementation: outcome → changed artifacts → verification → remaining blocker, if any.

## 12. Final rule

Build toward one explorable source-aware spatial-temporal model of connected knowledge without losing epistemic truth, capability truth or reviewed-contract integrity.
