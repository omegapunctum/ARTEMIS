# ARTEMIS repository instructions

This file is the single entrypoint for agents working in this repository. It routes to the project-owned contracts; it does not replace them.

## Required orientation

Before changing the repository:

1. Read `docs/FOUNDATION_INDEX.md` for the canonical owner of each decision.
2. Read `docs/PROJECT_TRUTH.md` for the current public/backend/pilot/target boundary.
3. Read `docs/PRIORITIES.md` and `docs/PROJECT_PHASES.md` for the active dependency order.
4. Read `docs/work/README.md` before using a working document.
5. Read the task-specific owner documents named by `docs/FOUNDATION_INDEX.md`.

`docs/ARTEMIS_MASTER_PROMPT.md` contains the detailed agent governance and Definition of Done.

## Current product boundary

- Mission: strengthen human, evidence-based research.
- Core chain: `Question → Claims → Evidence → Comparison → Findings → Conclusion / Unresolved`.
- Map and time are research lenses whose incremental value must be validated.
- Target saved model: `Investigation → immutable Slice Revision → Research Brief`, with a nested Saved View.
- The current mutable ResearchSlice v2 runtime is a compatibility envelope, not the target model.
- Stories, Courses, AI generation, open UGC, new domains and speculative scaling are frozen unless a later canonical decision opens one named branch.
- `same_movement` and computed Similarity do not count as substantive historical Relations.

## Change discipline

- Inspect `git status` and preserve unrelated changes.
- One question has one canonical owner. Do not create a competing source of truth.
- Update documentation first when changing product, epistemic, data, runtime, release or governance contracts.
- Keep current capability claims separate from concept targets and future scope.
- Do not invent evidence, locators, certainty, relation semantics or migration success.
- Keep public data publication in the ETL/release path; runtime moderation must not publish directly.
- Do not put credentials, tokens, private research content or owner identity in Web Storage, public artifacts or logs.
- Do not expand frozen product surfaces while touching compatibility code.

## Verification

Run the smallest relevant tests while iterating, then before handoff run:

```bash
python scripts/release_check.py
pytest -q
```

Use the dedicated Redis and external-integration workflows where their dependencies are required. Report checks honestly; a structural or CI pass is not user-validation evidence.
