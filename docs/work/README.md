# ARTEMIS working documents registry

## Status

- Type: working-layer lifecycle registry.
- Updated: 2026-09-01.
- Authority: this file decides whether a document under `docs/work/` is active, gated, completed evidence or historical context.
- Canonical rules remain in owner documents registered by `docs/FOUNDATION_INDEX.md`.

A filename containing `ACTIVE`, an old status header or an issue reference does not make a document active.

## Active execution

| Document | Role | Exit |
|---|---|---|
| `2026-09-01_TEMPORAL_MAP_M4_ARCHITECTURE_DECISION_v1.md` | #355 completed M4 architecture decision | `ADOPT`; no implementation branch opened |
| `2026-09-01_TEMPORAL_MAP_M3_EXIT_DECISION_v1.md` | #355 recorded M3 exit decision and bounded M4 opening | completed by M4 `ADOPT` decision |
| `2026-09-01_TEMPORAL_MAP_M3_TWO_SOURCE_PROOF_v1.md` | #355 completed two-provider/one-Presence M3 evidence | completed with `PROCEED_TO_M4` through separate decision record |
| `2026-09-01_TEMPORAL_MAP_M2_EXIT_DECISION_v1.md` | #355 recorded M2 exit decision and bounded M3 opening | completed by M3 proof and decision |
| `2026-09-01_TEMPORAL_MAP_MILESTONES_AND_M2_PROOF_v1.md` | #355 completed milestone lifecycle and Wikidata M2 evidence | completed with `PROCEED_TO_M3` through separate decision record |
| `2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md` | #355 active Globe/Temporal Map MVP product/governance decision | Gate D promotion/stop outcome; the bounded post-#396 `ITERATE` does not close it |
| `2026-08-08_GLOBE_RUNTIME_SPIKE_RUNBOOK_v1.md` | executable generated Globe build/runbook used during #355 MVP work | replaced by a maintained-app runbook after an evidence-backed promotion decision or archived after stop decision |
| `2026-08-14_GATE_D_EARTH_CONTEXT_PROVIDER_POLICY_v1.md` | #355 current Earth-context provenance/license/cache/secret boundary | replaced only by a reviewed provider decision or archived with the Globe contour |
| `2026-08-14_GATE_D_BROWSER_EVIDENCE_v1.md` | #355 deterministic hosted browser evidence and explicit limitations | retained as technical evidence; superseded only by a newer scoped browser-evidence contract |
| `2026-08-14_GATE_D_REAL_DEVICE_REVIEW_PROTOCOL_v1.md` | paused historical closeout protocol; basic responsive/keyboard/accessibility behavior remains required | reconsider only if the fresh product decision makes this evidence necessary |
| `2026-08-14_GATE_D_PLACE_ANCHOR_CONTRACT_v1.md` | #355 source-bound present-day settlement reference overlay for Rimini, Cesena, Cesenatico and Imola | replaced only by a reviewed higher-precision source contract or archived with the Globe contour |
| `2026-08-28_TEMPORAL_MAP_LIFE_PATH_V1.md` | #355 current object → time → path → place → information interaction contract; implemented through PRs #395–#396 | replaced only by a later reviewed interaction contract; current #396 behavior is preserved |
| `2026-08-29_LEONARDO_MAJOR_LIFE_PRESENCE_SCOPE_v1.md` | completed source/review branch through PR #400; candidate package remains non-public and runtime-not-authorized | preserved evidence; any runtime use requires a later decision |
| `2026-04-23_RUNTIME_READINESS_RUNBOOK_ACTIVE_v1_0.md` | compatibility operator interpretation for legacy runtime/release signals | replaced by a newer verified compatibility runbook |
| `moderation-runbook.md` | current compatibility moderation recovery procedure | replaced when moderation behavior changes |

## Current #355 execution truth

Core Reset is **completed**, not active work:

- PR `#393` isolated ARTEMIS Core delivery;
- root is the Core landing;
- `/globe/` is the primary Leonardo research prototype;
- `/atlas/` is compatibility-only;
- ARTEMIS Core Check is the required product signal.

The first Leonardo Temporal Map implementation cycle is also completed:

- PR `#395` established calendar-based Range/Scrub and canonical Presence/Trajectory bindings;
- the first published manual check produced `ITERATE`;
- PR `#396` implemented that correction and is published.

Current interaction semantics:

- `Range` = two-handle calendar interval using temporal overlap;
- `Scrub` = chosen build origin + one current-time cursor, progressively accumulating the path;
- the full-width bottom timeline is the primary time instrument;
- map, timeline, selection and URL share one state;
- first click opens a compact popup and does not move the camera;
- optional further action opens the right detail drawer;
- double-click may focus the selected place;
- dashed connectors express chronology only and are never historical route geometry;
- no new Leonardo data, exact route, duration or historical coordinate is implied by the interaction.

The fresh user check of the published #396 loop completed M1 with `ITERATE`. PR #400 completed the reviewed major-life candidate package without runtime authorization. PR #401 completed M2 with `PROCEED_TO_M3`. PR #403 completed M3 with `PROCEED_TO_M4`. M4 completed with `ADOPT` for the source-federated semantic direction. **No post-M4 implementation branch is active.** Do not add another provider/Presence, local/global layers, backend/storage, public runtime data or federation infrastructure before a separate bounded branch decision.

## Foundation lifecycle records

| Document | Role | Authority |
|---|---|---|
| `2026-08-12_PROGRESSIVE_REFINEMENT_DECISION_v1.md` | #377 foundation-only coarse-to-fine knowledge refinement lifecycle record | exact status and decision recorded by its contract/registry; no capability authorization |

Issue #377 is accepted historical foundation evidence. Issue #392 isolates the stale repository-wide READY envelope from mutable routing and from the read-only Core path. Editable refinement remains deferred.
#371/#373 remain deferred.

#366 / PR #367 completed legacy Airtable truth alignment, canonical audit routing and the proposal-only schema decision. #368 / PR #369 completed the six-table empty non-authoritative shadow schema plus executable contract/snapshot validation. Neither opened Gate D, imported the frozen Gate C package or changed the Architecture Atlas public export authority.

#371 / merged PR #372 completed the fail-closed mapping preflight. It resolves three storage blockers without historical row writes: World Model layer identity moves to shadow-only `SliceLayers`, frozen source identity/rights move to shadow-only `WorldSources`, and many-target Uncertainty storage uses `UncertaintyTargets` without cloning the 11 canonical Uncertainty identities. The original six #368 tables and the three #371 extension tables remain empty. The import/review path is deferred outside Gate D.

The accepted/current Airtable working/evidence chain is:

- `2026-08-10_AIRTABLE_PRE_GATE_D_ALIGNMENT_v1.md` — compatibility boundary and architecture decision;
- `airtable/2026-08-10_AIRTABLE_CURATION_SCHEMA_PLAN_v1.json` — proposal-only schema plan;
- `2026-08-10_AIRTABLE_SHADOW_CURATION_SCHEMA_v1.md` — completed live empty schema implementation/evidence;
- `fixtures/airtable_curation/v1/` + `scripts/validate_airtable_curation_schema.py` — completed #368 executable schema evidence and guard;
- `2026-08-11_LEONARDO_AIRTABLE_SHADOW_IMPORT_v1.md` — completed preflight / deferred #371 import decision;
- `fixtures/airtable_curation/v2/` + `scripts/validate_airtable_leonardo_shadow_preflight.py` — accepted lossless mapping/schema-extension evidence and fail-closed preflight.

No real Gate C historical row import is active. PR #372 merged the schema/mapping preflight only; #371/#373 are deferred and historical writes remain prohibited.

## Active execution rule for the Temporal Map / Globe MVP

- working docs cannot override `ARTEMIS_CONCEPT.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `PLATFORM_ARCHITECTURE_DECISION.md`, `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`, `UNCERTAINTY_SEMANTICS_CONTRACT.md`, `DATA_CONTRACT.md`, `PRIORITIES.md`, `PROJECT_PHASES.md`, `PROJECT_TRUTH.md` or `DEVELOPMENT_OPERATING_SYSTEM.md`;
- #355 authorizes only the bounded current loop and the next evidence-backed decision;
- Gate C is completed/FREEZE in #332/#360 / PR #362 and is preserved as non-public source/semantic input;
- Gate D remains open/in progress under #355; implementation completion does not itself close the gate;
- the Globe consumes merged Explorer State + Render Projection rather than `data/features.geojson` as its historical source;
- `/globe/` is the primary research prototype; the root is a Core landing and Architecture Atlas is compatibility-only at `/atlas/`;
- 2D Map and Globe are renderer choices over one semantic core; timeline is shared Explorer temporal state, not a separate truth model;
- the reviewed unknown Trajectory gaps remain unresolved; any visible connecting line must remain explicitly presentation-only chronology unless source-bound route geometry exists;
- the current Earth context is pinned Natural Earth physical geography as `present_day_context`, not historical geography;
- the MVP decision and public `/globe/` access do not make the Globe a product-ready capability;
- #331 is deferred and documented Relation predicates remain prohibited until explicitly reopened/accepted;
- the completed #344 parity contract remains a fail-closed semantic requirement for renderer changes;
- the Leonardo-in-Romagna 1502 Gate C package remains frozen with draft/rejected historical Claims and geometry withheld where unsupported;
- the separate place-anchor overlay may resolve only the four present-day named-settlement points with source/rights/uncertainty closure; it cannot create exact historical positions, routes, boundaries, Relations or Airtable rows;
- broader 1452–1519 Presence data and default context/layer expansion are separate possible branches, not current scope.

## Accepted Attractor-refinement rule from #363 / PR #364

- `ARTEMIS_CONCEPT.md` remains the only North Star/attractor owner;
- `World Model` remains the technical semantic-core name while the North Star defines ARTEMIS as knowledge about the world rather than objective reality;
- no `ATTRACTOR.md`/`NORTH_STAR.md` competing canonical owner may be introduced;
- one semantic core must serve future domains and interfaces;
- future AI may only gain view/query control through a separate explicit reversible action contract;
- personal knowledge, AI runtime, universal corpus, VR/AR and causal/counterfactual runtime stay gated/future;
- Foundation v3.1 does not itself advance product capability;
- the reviewed `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` v1.0 remains byte-preserved until separately re-reviewed.

## Gated under Foundation v3

| Document/group | Lifecycle | Rule |
|---|---|---|
| `2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md` | gated broader Life in Context validation design | not the immediate post-#396 step; use only when the corresponding product scope/protocol is explicitly opened |
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
| `uiux/2026-07-17_UX_CONCEPT_CORRECTION_v1.md` | historical decision context | Foundation v3+ owner docs win on conflict |
| `uiux/2026-04-26_UIUX_APP_STRUCTURE_SPEC_ACTIVE_v1_0.md` and `uiux/main-screen/**` | historical design context | Not current lifecycle authority |

## Superseded decision

- `2026-07-26_CONCEPT_LOCK_V2.md` — superseded by Foundation v3; preserve rationale/history.

Its retained Claim/Evidence, uncertainty and relation-discipline decisions apply only where current Foundation owner docs keep them.

## Completed execution evidence

- `2026-08-29_GATE_D_POST_396_USER_CHECK_v1.md` — direct post-#396 product-feedback evidence; recorded `ITERATE`, left Gate D/formal validation open and authorized exactly one bounded source branch.
- `2026-08-12_GATE_D_OPENING_v1.md` — historical opening record; Gate D was explicitly opened, while Core Reset and later Temporal Map changes are owned by current canonical state and #355.
- `2026-08-28_TEMPORAL_MAP_LIFE_PATH_V1.md` implementation history — PR #395 established the calendar loop; first published check recorded `ITERATE`; PR #396 implemented/published the bounded feedback correction. The document remains active as the current interaction contract until replaced by a later accepted version.
- `2026-08-10_AIRTABLE_SHADOW_CURATION_SCHEMA_v1.md` — #368 completed in PR `#369`; six empty non-authoritative World Model curation tables, executable live schema snapshot/contract and Release Discipline guard were accepted, with no Gate C import or public export authority.
- `2026-08-10_AIRTABLE_PRE_GATE_D_ALIGNMENT_v1.md` — #366 completed in PR `#367`; current eight-table Architecture Atlas Airtable boundary, schema descriptions and canonical audit routing were aligned.
- `2026-08-09_ARTEMIS_ATTRACTOR_REFINEMENT_DECISION_v1.md` — #363 completed in PR `#364`; Foundation v3.1 fixes the long-term attractor and one-core invariant without changing public capability by itself.
- `2026-08-09_LEONARDO_WORLD_SLICE_SCOPE_v1.md` — #332/#360 completed Gate C in PR `#362` with a Git-bound `FREEZE`, two independent READY reviews, measured cost and a non-public scope boundary.
- `2026-08-08_CROSS_RENDERER_PARITY_CONTRACT_v1.md` — #344 completed in PR `#351`; renderer-neutral fingerprints and controlled corruption cases protect semantic equivalence across 2D and Globe adapters.
- `2026-08-08_GLOBE_REPOSITORY_RUNTIME_BOUNDARY_v1.md` — #345 completed in PR `#352`; generated/runtime and Pages boundaries accepted.
- `2026-08-08_GLOBE_ENGINE_SPIKE_DECISION_v1.md` — #343 completed in PR `#350`; MapLibre GL JS 5.24.0 selected for the bounded spike, with Cesium retained as measured-gap escalation.
- `2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md` — #339 completed in PR `#346`; one semantic core and multiple projection renderers established.
- `2026-08-08_GEOSPATIAL_ASSETS_CONTRACT_v1.md` — #342 completed in PR `#349`; provider/CRS/vertical/temporal/provenance/license/cache/runtime boundaries accepted.
- `2026-08-08_RENDER_PROJECTION_CONTRACT_v1.md` — #341 completed in PR `#348`; one World Slice + Explorer State deterministically produce 2D/Globe adapter payloads with explicit projection loss.
- `2026-08-08_EXPLORER_STATE_CONTRACT_v1.md` — #340 completed in PR `#347`; renderer-neutral state schema/fixture/validator accepted.
- `2026-08-04_UNCERTAINTY_SEMANTICS_REVIEW.md` — #330 completed in PR `#337` with READY uncertainty semantics and independent review evidence.
- `2026-07-29_WORLD_MODEL_FIXTURE_REVIEW.md` — #329 completed in PR `#336` with READY package and two independent reviews.
- `2026-07-28_FOUNDATION_V3_DECISION.md` — accepted in PR `#328`.
- `2026-07-28_CONCEPT_V2_TO_V3_MIGRATION_MATRIX.md` — backlog disposition completed.
- `2026-07-16_CANONICAL_IDENTITY_MIGRATION_v1.md`.
- `2026-07-16_RELATIONS_SIMILARITY_MIGRATION_v1.md`.
- `2026-07-16_SOURCES_MEDIA_MIGRATION_v1.md`.
- `2026-07-21_SEMANTIC_DATA_GATE_v1.md`.
- `2026-07-21_VALIDATION_CORPUS_PILOT_v1.md`.
- `2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md`.
- `validation_modules/`.

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
