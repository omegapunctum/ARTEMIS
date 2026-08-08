# ARTEMIS working documents registry

## Status

- Type: working-layer lifecycle registry.
- Updated: 2026-08-08.
- Authority: this file decides whether a document under `docs/work/` is active, gated, completed evidence or historical context.
- Canonical rules remain in owner documents registered by `docs/FOUNDATION_INDEX.md`.

A filename containing `ACTIVE`, an old status header or an issue reference does not make a document active.

## Active execution

| Document | Role | Exit |
|---|---|---|
| `2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md` | #339 bounded parallel 3D Globe / renderer architecture R&D record | #340–#345 contracts/spike/parity/repository decisions complete or explicit stop decision |
| `2026-04-23_RUNTIME_READINESS_RUNBOOK_ACTIVE_v1_0.md` | Current operator interpretation for runtime/release signals | Replaced by a newer verified runbook |
| `moderation-runbook.md` | Current moderation recovery procedure | Replaced when moderation behavior changes |

Active execution rule for the Globe record:

- it cannot override `ARTEMIS_CONCEPT.md`, `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`, `UNCERTAINTY_SEMANTICS_CONTRACT.md`, `DATA_CONTRACT.md`, `PRIORITIES.md`, `PROJECT_PHASES.md` or `PROJECT_TRUTH.md`;
- it authorizes only the bounded #339–#345 R&D contour;
- it does not make 3D Globe a current public/product capability;
- it does not block #331 → #332 → #333 → #334.

## Gated under Foundation v3

| Document/group | Lifecycle | Rule |
|---|---|---|
| `2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md` | gated Life in Context validation design | Freeze only after #329–#333 dependencies are ready |
| `2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md` | completed Architecture Layer preparation program | Modules/fixtures may be reused; no longer the active product-validation gate |
| `validation_modules/` | completed Gate A executable package | Preserve as architecture fixtures and historical readiness evidence |
| `2026-07-27_CONCEPT_LOCK_MIGRATION_PLAN_v1.md` | superseded execution plan | Must not authorize #323–#325 or v2 migration order |
| `2026-07-22_PUBLIC_SLICE_E2E_v1.md` | compatibility evidence | Mutable ResearchSlice v2 only; not Foundation v3 target E2E |
| `ARTEMIS_UI_UX_IMPLEMENTATION_PLAN_v1_0.md` | superseded planning | Use only for implemented-shell context |
| `uiux/ARTEMIS_UI_UX_SYSTEM.md` | implemented/transitional context | Cannot override synchronized world-model hierarchy |
| `uiux/ARTEMIS_UI_UX_COMPONENT_MAP.md` | implemented/transitional context | Cannot reopen frozen product surfaces |
| `uiux/ARTEMIS_UI_UX_VISUAL_SYSTEM.md` | visual baseline | May guide consistency after v3 product/model dependencies |
| `uiux/2026-07-16_UIUX_MAIN_SCREEN_REFINEMENT_SPEC_ACTIVE_v1_0.md` | implemented-shell compatibility | `ACTIVE` in filename is historical |
| `uiux/2026-07-17_COMPARISON_FIRST_WIREFRAME_SPEC_v1.md` | partial interface input | Must not define first v3 value |
| `uiux/2026-07-17_CSS_OWNERSHIP_MIGRATION_AUDIT_v1.md` | measured technical baseline | Apply only where v3 explorer touches ownership |
| `uiux/2026-07-17_UX_CONCEPT_CORRECTION_v1.md` | historical decision context | Foundation v3 wins on conflict |
| `uiux/2026-04-26_UIUX_APP_STRUCTURE_SPEC_ACTIVE_v1_0.md` and `uiux/main-screen/**` | historical design context | Not current lifecycle authority |

## Superseded decision

- `2026-07-26_CONCEPT_LOCK_V2.md` — superseded by Foundation v3; preserve rationale/history.

Its retained Claim/Evidence, uncertainty and relation-discipline decisions apply only where Foundation v3 owner docs keep them.

## Completed execution evidence

- `2026-08-04_UNCERTAINTY_SEMANTICS_REVIEW.md` — #330 completed in PR `#337` with READY uncertainty semantics and independent review evidence.
- `2026-07-29_WORLD_MODEL_FIXTURE_REVIEW.md` — #329 completed in PR `#336` with READY package and two independent reviews.
- `2026-07-28_FOUNDATION_V3_DECISION.md` — accepted in PR `#328`.
- `2026-07-28_CONCEPT_V2_TO_V3_MIGRATION_MATRIX.md` — backlog disposition completed.
- `2026-07-16_CANONICAL_IDENTITY_MIGRATION_v1.md`
- `2026-07-16_RELATIONS_SIMILARITY_MIGRATION_v1.md`
- `2026-07-16_SOURCES_MEDIA_MIGRATION_v1.md`
- `2026-07-21_SEMANTIC_DATA_GATE_v1.md`
- `2026-07-21_VALIDATION_CORPUS_PILOT_v1.md`
- `2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md`
- `validation_modules/`

Technical/corpus readiness is not Foundation v3 user-value evidence.

## Archived plans

Documents under `docs/archive/` have no current authority. Explicitly archived plans include:

- `ARTEMIS_AI_STRATEGY_v1_0.md`;
- `COURSES_MVP_SCOPE.md`;
- `FUNCTIONAL_EXPANSION_ROADMAP.md`.

## Lifecycle rule

When lifecycle changes:

1. update this registry in the same PR;
2. remove stale active-order claims from canonical docs/issues;
3. preserve completed evidence and historical decisions;
4. do not silently repurpose old execution docs;
5. archive only when traceability is preserved;
6. never let working/audit/archive docs become hidden canonical owners.