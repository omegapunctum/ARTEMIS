# ARTEMIS repository instructions

This file is the single entrypoint for agents working in ARTEMIS. It provides repository-wide routing, execution boundaries and invariants. It is not a source of current project state and must not duplicate mutable lifecycle status.

## Context routing

Read only what the task needs.

For non-trivial work, start with:

1. `docs/PROJECT_TRUTH.md` for current capability and factual repository/runtime state;
2. `docs/project_state.json` for machine-readable phase/gate/checkpoint state;
3. `docs/work/README.md` for active working-document lifecycle;
4. one task-specific canonical or active-work owner.

Use `docs/FOUNDATION_INDEX.md` when the correct owner is unclear or the task crosses owner boundaries. Read additional canonical documents only when the task touches their semantics.

For small local edits, inspect the affected files and the directly relevant owner/checks instead of loading the full documentation stack.

`docs/ARTEMIS_MASTER_PROMPT.md` is an on-demand agent-governance reference, not a second current-state registry.

## Owner routing

Use the owner that matches the question:

- identity / North Star / attractor → `docs/ARTEMIS_CONCEPT.md`;
- active product scope → `docs/PRODUCT_THESIS.md`, `docs/ARTEMIS_PRODUCT_SCOPE.md`;
- current capability → `docs/PROJECT_TRUTH.md`;
- spatial-temporal semantics → `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- uncertainty → `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md`;
- entities / relations → `docs/ENTITY_MODEL.md`;
- claims / evidence / inference → `docs/EPISTEMIC_CONTRACT.md`;
- AI behavior → `docs/AI_POLICY.md`;
- platform / renderer / storage boundary → `docs/PLATFORM_ARCHITECTURE_DECISION.md`;
- repository/runtime layout → `docs/PROJECT_STRUCTURE.md`;
- execution process → `docs/DEVELOPMENT_OPERATING_SYSTEM.md`.

Working, audit and archive files cannot override the relevant canonical owner.

## Repository invariants

- Distinguish Idea, Decision, Specification, Implementation and Verification.
- Keep North Star, active scope, implementation, public availability and validated user value separate.
- Preserve reviewed/frozen contracts unless their own change-control path is explicitly reopened.
- Do not invent evidence, locators, dates, temporal precision, coordinates, geometry, routes, relations, confidence or migration success.
- Dataset absence is not historical absence.
- Co-presence/proximity is not encounter, interaction, influence or causality.
- AI output is not Source and must not silently mutate canonical knowledge.
- Preserve one World Model / epistemic core across domains and renderers; renderer/UI state must not redefine domain semantics.
- Keep secrets, credentials, owner identity and private research out of public repository artifacts and logs.
- Do not expand implementation scope merely because a change is compatible with the long-term attractor.

## Execution

Work within the requested task and the scope authorized by its current owner.

For ordinary local repository work, proceed through implementation, the smallest relevant local verification, fixes for failures caused by the requested change, and rerun affected checks without asking for approval at each intermediate step.

Stop and surface the blocker when:

- the next action is destructive, irreversible or affects an external/production system and approval is required;
- the task would change an unauthorized product/domain semantic or a frozen reviewed contract;
- authoritative sources conflict and the correct owner cannot be resolved;
- completing the task would materially broaden scope beyond the request.

Prefer the smallest complete change. Preserve unrelated work and avoid opportunistic refactoring.

## Verification

Run the smallest relevant owned checks for the affected contour. Fix failures caused by the change and rerun affected checks.

Do not run unrelated repository-wide suites merely because they exist. Use broader suites only when the changed scope or owner contract requires them.

For documentation/governance-only changes, verify at minimum:

- changed-file scope;
- owner/routing consistency;
- no duplicated or contradictory mutable current state;
- relevant governance tests or structural checks.

Report verification honestly. Passing checks are implementation evidence, not user-value validation.
