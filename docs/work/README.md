# ARTEMIS working documents registry

## Status

- Type: working-layer lifecycle registry.
- Updated: 2026-07-27.
- Authority: this file decides whether a document under `docs/work/` is active, gated, completed evidence or historical context.
- Canonical product and system rules remain in the owner documents registered by `docs/FOUNDATION_INDEX.md`.

A filename containing `ACTIVE`, a historical status header or an old issue reference does not make a working document active.

## Active execution

| Document | Role | Exit |
|---|---|---|
| `2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md` | Prepare exactly three deep validation modules | `3/3 READY` with claim-level evidence, two reviewers and hidden reference Briefs |
| `2026-07-27_CONCEPT_LOCK_MIGRATION_PLAN_v1.md` | Dependency map from Concept Lock v2 to implementation and validation | Replaced by synchronized execution issues and completed migrations |
| `2026-04-23_RUNTIME_READINESS_RUNBOOK_ACTIVE_v1_0.md` | Current operator interpretation for runtime/release signals | Replaced by a newer verified runbook |
| `moderation-runbook.md` | Current moderation recovery procedure | Replaced when moderation behavior changes |

## Gated or compatibility-only

These documents may describe current code or preserve implementation context. They do not authorize execution ahead of the active dependency order.

| Document/group | Lifecycle | Rule |
|---|---|---|
| `2026-07-22_PUBLIC_SLICE_E2E_v1.md` | compatibility evidence / gated | Describes mutable ResearchSlice v2; target public E2E waits for Claim/Evidence and immutable revision/Brief migrations |
| `ARTEMIS_UI_UX_IMPLEMENTATION_PLAN_v1_0.md` | superseded planning / gated | Use only for implemented-shell context; target UI follows Concept Lock v2 |
| `uiux/ARTEMIS_UI_UX_SYSTEM.md` | implemented/transitional context | Cannot override the evidence-chain hierarchy |
| `uiux/ARTEMIS_UI_UX_COMPONENT_MAP.md` | implemented/transitional context | Cannot open frozen sections or make Slice the product center |
| `uiux/ARTEMIS_UI_UX_VISUAL_SYSTEM.md` | visual baseline | May guide visual consistency after product dependencies are ready |
| `uiux/2026-07-16_UIUX_MAIN_SCREEN_REFINEMENT_SPEC_ACTIVE_v1_0.md` | implemented-shell compatibility | New work requires target research-interface owner issue |
| `uiux/2026-07-17_COMPARISON_FIRST_WIREFRAME_SPEC_v1.md` | partial current-interface input | Must be revised around Claims/Evidence before target acceptance |
| `uiux/2026-07-17_CSS_OWNERSHIP_MIGRATION_AUDIT_v1.md` | measured technical baseline | Apply only where target flow touches CSS/JS ownership |
| `uiux/2026-07-17_UX_CONCEPT_CORRECTION_v1.md` | pre-Concept-Lock decision history | Concept Lock v2 wins on any conflict |
| `uiux/2026-04-26_UIUX_APP_STRUCTURE_SPEC_ACTIVE_v1_0.md` and `uiux/main-screen/**` | historical design context | Names containing `ACTIVE` are legacy filenames, not current lifecycle |

## Completed execution evidence

These files remain in `docs/work/` because they are traceable migration/decision evidence referenced by current contracts. They are not active plans.

- `2026-07-16_CANONICAL_IDENTITY_MIGRATION_v1.md`
- `2026-07-16_RELATIONS_SIMILARITY_MIGRATION_v1.md`
- `2026-07-16_SOURCES_MEDIA_MIGRATION_v1.md`
- `2026-07-21_SEMANTIC_DATA_GATE_v1.md`
- `2026-07-21_VALIDATION_CORPUS_PILOT_v1.md`
- `2026-07-26_CONCEPT_LOCK_V2.md`

The corpus pilot's `comparison_ready` status is technical legacy evidence only. It does not satisfy the deep-module or external-validation gate.

## Archived plans

The following files moved to `docs/archive/` and have no current authority:

- `ARTEMIS_AI_STRATEGY_v1_0.md`
- `COURSES_MVP_SCOPE.md`
- `FUNCTIONAL_EXPANSION_ROADMAP.md`

## Lifecycle rule

When a working document changes lifecycle:

1. update this registry in the same change;
2. remove stale active-order claims from canonical docs and issues;
3. archive plans that can no longer safely guide work;
4. keep completed evidence only when a current contract links to it;
5. do not treat working, audit, reference or archive files as canonical owners.
