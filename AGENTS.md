# ARTEMIS repository instructions

This file is the single entrypoint for agents working in ARTEMIS. It routes to project-owned contracts and does not replace them.

## Required orientation

Before changing the repository:

1. Read `docs/FOUNDATION_INDEX.md`.
2. Read `docs/PROJECT_TRUTH.md`.
3. Read `docs/ARTEMIS_CONCEPT.md`.
4. Read `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` for knowledge-model work.
5. Read `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md` for issue #330 temporal/spatial uncertainty work.
6. Read `docs/PRIORITIES.md` and `docs/PROJECT_PHASES.md`.
7. Read `docs/work/README.md` before using a working document.
8. Read the task-specific owner documents.

Detailed operational governance lives in `docs/ARTEMIS_MASTER_PROMPT.md`.

## Active foundation boundary

- ARTEMIS is a source-aware spatial-temporal world model.
- Space and time are mandatory core coordinates.
- Core change objects are `Event`, `State`, `Process`, `Trajectory` and temporal `Region`.
- Evidence is a required trust layer: Claim → EvidenceLink → Source/locator.
- Co-presence, possible encounter, documented encounter, interaction, influence and causality are distinct.
- Facts, observations, interpretations, inferences, hypotheses and counterfactuals are distinct.
- Architecture Atlas is a preserved thematic layer and current technical/public baseline.
- First validation vertical: `Life in Context`.
- A bounded source-aware Globe MVP is active under #355; generative AI, causal/counterfactual runtime, VR/AR, universal corpus and production-scale dynamic Earth remain frozen.
- Current ResearchSlice v2 is compatibility code; #323–#325 are not the active path.

## Change discipline

- Preserve unrelated changes and completed history.
- One question has one canonical owner.
- Update documentation first for product/model/governance changes.
- Keep North Star, current implementation, public deployment and validated value separate.
- Do not invent evidence, locator, geometry, route, date precision, relation or migration success.
- Do not convert proximity/co-presence into historical Relation.
- Do not treat absence in a World Slice as historical absence.
- Keep public data publication in the ETL/release path.
- Do not put credentials, tokens, owner identity or private research in public artifacts/storage/logs.
- Do not harden a compatibility schema as target without a contract and migration decision.

## Current execution boundary

Foundation v3 is accepted in PR `#328`; the old Concept v2 implementation backlog and PR `#314` are closed.

Active work is issue `#355`: build the first source-aware Globe MVP vertical. Issue `#332` is the active Gate C delivery for the first real bounded World Slice.

- preserve #329 / PR #336 World Model fixtures and #330 / PR #337 uncertainty semantics as reviewed READY foundations;
- preserve completed #344 / PR #351 cross-renderer parity as a required green foundation;
- keep #331 `PAUSED`; derived proximity/co-presence remains separate and documented Relation predicates are prohibited until #331 is accepted;
- use one World Model → Explorer State → Render Projection path for both 2D and Globe;
- keep the current root 2D MapLibre runtime as the public baseline and rollback path;
- keep Globe artifacts non-public until a separate promotion decision;
- use MapLibre as the leading MVP engine unless measured evidence justifies a Cesium comparison;
- do not create a framework/backend/repository rewrite without a demonstrated blocker;
- security, compatibility and critical maintenance remain allowed.

The current active artifact is the non-public Leonardo-in-Romagna 1502 scope package under `fixtures/world_slices/leonardo_romagna_1502/v1/`. It is a curation boundary, not READY historical data. Do not add route or Region geometry until the package's evidence, rights and independent-review gaps are closed.

## Verification

Run the smallest relevant checks while iterating. Before handoff, run when a local checkout is available:

```bash
python scripts/release_check.py
pytest -q
```

Documentation-only connector work must still verify:

- changed-file scope;
- internal links/registry;
- no contradictory active status;
- current capability truth;
- PR diff and GitHub checks.

Report structural checks honestly; they are not user validation.
