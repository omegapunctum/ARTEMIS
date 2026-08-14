# ARTEMIS working documents registry

## Status

- Type: working-layer lifecycle registry.
- Updated: 2026-08-12.
- Authority: this file decides whether a document under `docs/work/` is active, gated, completed evidence or historical context.
- Canonical rules remain in owner documents registered by `docs/FOUNDATION_INDEX.md`.

A filename containing `ACTIVE`, an old status header or an issue reference does not make a document active.

## Active execution

| Document | Role | Exit |
|---|---|---|
| `2026-08-12_GATE_D_OPENING_v1.md` | #355 active Gate D source-aware Globe contract | synchronized non-public experience and one Gate D exit decision: `ADVANCE_TO_GATE_E`, `NARROW` or `REJECT` |
| `2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md` | #355 active Globe MVP product/governance decision | Gate D evidence and one explicit next decision before Gate E |
| `2026-08-08_GLOBE_RUNTIME_SPIKE_RUNBOOK_v1.md` | executable generated Globe seed used during #355 MVP work | replaced by a maintained-app runbook after promotion or archived after stop decision |
| `2026-08-14_GATE_D_EARTH_CONTEXT_PROVIDER_POLICY_v1.md` | #355 real Earth-context selection, provenance, license, cache and secret boundary | replaced only by a reviewed provider decision or archived with Gate D |
| `2026-08-14_GATE_D_BROWSER_EVIDENCE_v1.md` | #355 deterministic desktop/tablet/hosted-mobile browser evidence and explicit limitations | replaced by normal-browser/real-device/assistive-technology evidence or archived with Gate D |
| `2026-08-14_GATE_D_REAL_DEVICE_REVIEW_PROTOCOL_v1.md` | #355 physical desktop/390px mobile/assistive-technology/non-virtual-performance evidence protocol; evidence remains pending | completed evidence record plus one Gate D decision, or archived after `NARROW`/`REJECT` |
| `2026-08-14_GATE_D_PLACE_ANCHOR_CONTRACT_v1.md` | #355 source-bound present-day settlement reference overlay for Rimini, Cesena, Cesenatico and Imola | replaced only by a reviewed higher-precision source contract or archived with Gate D |
| `2026-04-23_RUNTIME_READINESS_RUNBOOK_ACTIVE_v1_0.md` | Current operator interpretation for runtime/release signals | Replaced by a newer verified runbook |
| `moderation-runbook.md` | Current moderation recovery procedure | Replaced when moderation behavior changes |

## Foundation lifecycle records

| Document | Role | Authority |
|---|---|---|
| `2026-08-12_PROGRESSIVE_REFINEMENT_DECISION_v1.md` | #377 foundation-only coarse-to-fine knowledge refinement lifecycle record | exact status and decision recorded by its contract/registry; no capability authorization |

Issue #377 is foundation maintenance whose exact lifecycle is owned by its contract/registry and
does not consume the one-product-gate WIP slot. Candidate or accepted status cannot by itself change
Gate D state, runtime, public capability, Airtable data or the frozen Leonardo package.
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

Active execution rule for the Globe MVP:

- it cannot override `ARTEMIS_CONCEPT.md`, `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`, `UNCERTAINTY_SEMANTICS_CONTRACT.md`, `DATA_CONTRACT.md`, `PRIORITIES.md`, `PROJECT_PHASES.md`, `PROJECT_TRUTH.md` or `DEVELOPMENT_OPERATING_SYSTEM.md`;
- it authorizes the bounded #355 MVP only through explicitly opened product gates;
- Gate C is completed/FREEZE in #332/#360 / PR #362 and is preserved as non-public input;
- Gate D is separately opened and active under #355; Gate C completion and Foundation v3.1 did not open it by implication;
- the generated Globe artifact must consume merged Explorer State + Render Projection rather than `data/features.geojson` as its historical source;
- it is published only at the explicitly labelled `/globe/` R&D review route; this does not make it a product-ready capability, and root 2D remains the default/rollback entrypoint;
- MapLibre GL JS `5.24.0` is pinned for the #343 spike only and does not upgrade the current public MapLibre `4.7.1` runtime;
- the reviewed unknown Trajectory gaps remain unresolved; any polyline capability fixture must be explicitly non-semantic and carry no World Model identity;
- the default Gate D review artifact uses pinned Natural Earth physical geography as real `present_day_context`; it cannot be described as historical geography, while synthetic terrain remains non-live and cannot imply production provider readiness;
- live terrain/provider use, if later introduced, must pass the completed #342 provider/vertical/provenance/license/secret boundary;
- the MVP decision and `/globe/` review publication do not make 3D Globe a product-ready capability;
- #331 is deferred but becomes blocking before documented Relation predicates enter the real corpus/runtime;
- the completed #344 parity contract remains a fail-closed promotion gate for every runtime change;
- the Leonardo-in-Romagna 1502 Gate C package is frozen with two independent READY reviews, but its historical Claims remain draft, Region/route geometry remains withheld where unsupported and `promotion_allowed=false`.
- the separate Gate D place-anchor overlay may resolve only four present-day named-settlement points with source, rights and uncertainty closure; it cannot create exact historical positions, routes, boundaries, Relations or Airtable rows.

Accepted Attractor-refinement rule from #363 / PR #364:

- `ARTEMIS_CONCEPT.md` remains the only North Star/attractor owner;
- `World Model` remains the technical semantic-core name while the North Star defines ARTEMIS as knowledge about the world rather than objective reality;
- no `ATTRACTOR.md`/`NORTH_STAR.md` competing canonical owner may be introduced;
- one semantic core must serve future domains and interfaces;
- future AI may only gain view/query control through a separate explicit reversible action contract;
- personal knowledge, AI runtime, universal corpus, VR/AR and causal/counterfactual runtime stay gated/future;
- Foundation v3.1 does not itself advance Gate D or public capability;
- the reviewed `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` v1.0 remains byte-preserved until separately re-reviewed.

## Gated under Foundation v3

| Document/group | Lifecycle | Rule |
|---|---|---|
| `2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md` | gated Life in Context validation design | Use only when the corresponding product gate is opened and prerequisites are satisfied |
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

- `2026-08-10_AIRTABLE_SHADOW_CURATION_SCHEMA_v1.md` — #368 completed in PR `#369`; six empty non-authoritative World Model curation tables, executable live schema snapshot/contract and Release Discipline guard were accepted, with no Gate C import, no public export authority and an explicit unresolved Gate C Layer mapping blocker before any future import.
- `2026-08-10_AIRTABLE_PRE_GATE_D_ALIGNMENT_v1.md` — #366 completed in PR `#367`; current eight-table Architecture Atlas Airtable boundary, schema descriptions and canonical audit routing were aligned, with a proposal-only World Model curation plan and explicit Gate D prohibition.
- `2026-08-09_ARTEMIS_ATTRACTOR_REFINEMENT_DECISION_v1.md` — #363 completed in PR `#364`; Foundation v3.1 fixes the long-term attractor, knowledge-about-world identity, one-core/many-domains/many-interfaces invariant and future reversible AI exploration boundary without starting Gate D or changing public capability.
- `2026-08-09_LEONARDO_WORLD_SLICE_SCOPE_v1.md` — #332/#360 completed Gate C in PR `#362` with a Git-bound `FREEZE`, two independent READY reviews, measured cost and a non-public scope boundary; Claims remain draft and Gate D is not started by that decision.
- `2026-08-08_CROSS_RENDERER_PARITY_CONTRACT_v1.md` — #344 completed in PR `#351`; renderer-neutral fingerprints, temporal boundaries and controlled corruption cases protect semantic equivalence across 2D and Globe adapters.
- `2026-08-08_GLOBE_REPOSITORY_RUNTIME_BOUNDARY_v1.md` — #345 completed in PR `#352`; generated/non-public runtime and Pages boundaries accepted.
- `2026-08-08_GLOBE_ENGINE_SPIKE_DECISION_v1.md` — #343 completed in PR `#350`; MapLibre GL JS 5.24.0 selected for the bounded spike, with Cesium retained as measured-gap escalation; the generated runtime runbook remains active for #355.
- `2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md` — #339 completed in PR `#346`; one semantic core and multiple projection renderers established.
- `2026-08-08_GEOSPATIAL_ASSETS_CONTRACT_v1.md` — #342 completed in PR `#349`; provider/CRS/vertical/temporal/provenance/license/cache/runtime boundaries accepted with synthetic fixtures and dedicated CI.
- `2026-08-08_RENDER_PROJECTION_CONTRACT_v1.md` — #341 completed in PR `#348`; one World Slice + Explorer State deterministically produce semantically equivalent 2D/Globe adapter payloads with explicit projection loss.
- `2026-08-08_EXPLORER_STATE_CONTRACT_v1.md` — #340 completed in PR `#347`; renderer-neutral state schema/fixture/validator accepted, with two-adapter proof completed by PR `#348`.
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
