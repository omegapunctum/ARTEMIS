# ARTEMIS repository instructions

This file is the single entrypoint for agents working in ARTEMIS. It routes to project-owned contracts and does not replace them.

## Required orientation

Before changing the repository:

1. Read `docs/FOUNDATION_INDEX.md`.
2. Read `docs/PROJECT_TRUTH.md`.
3. Read `docs/ARTEMIS_CONCEPT.md`.
4. Read `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` for knowledge-model work.
5. Read `docs/PRIORITIES.md` and `docs/PROJECT_PHASES.md`.
6. Read `docs/work/README.md` before using a working document.
7. Read the task-specific owner documents.

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
- AI generation, causal/counterfactual runtime, 3D/VR, universal corpus and product expansion are frozen.
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

Issue `#329` is completed in PR `#336`. Active work is issue `#330`: executable temporal/spatial uncertainty semantics before relation-ladder or corpus work.

- follow clean v3 child issues `#329`–`#335` rather than rewriting old issues;
- preserve `fixtures/world_model/v1` as the reviewed READY base;
- no database/API/runtime migration before #330 and #331 pass;
- the fixture package must not be described as public/runtime capability;
- #332 Leonardo curation and #333 explorer remain gated;
- security, compatibility and critical maintenance remain allowed.

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
