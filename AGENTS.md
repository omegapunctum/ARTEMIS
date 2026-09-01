# ARTEMIS repository instructions

This file is the single entrypoint for agents working in ARTEMIS. It routes to project-owned contracts and does not replace them.

## Required orientation

Before changing the repository:

1. Read `docs/FOUNDATION_INDEX.md`.
2. Read `docs/PROJECT_TRUTH.md`.
3. Read `docs/ARTEMIS_CONCEPT.md`.
4. Read `docs/ARTEMIS_PRODUCT_SCOPE.md` for the active implementation boundary.
5. Read `docs/PLATFORM_ARCHITECTURE_DECISION.md` for web/PWA/native, renderer, scaling or repository/storage questions.
6. Read `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` for knowledge-model work.
7. Read `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md` for temporal/spatial uncertainty semantics.
8. Read `docs/PRIORITIES.md` and `docs/PROJECT_PHASES.md`.
9. Read `docs/DEVELOPMENT_OPERATING_SYSTEM.md` and `docs/project_state.json` for current execution state.
10. Read `docs/work/README.md` before using a working document.
11. Read the task-specific owner documents.

Detailed operational governance lives in `docs/ARTEMIS_MASTER_PROMPT.md`.

## Active foundation boundary

- ARTEMIS is a source-aware spatial-temporal knowledge model about the world.
- Space and time are mandatory core coordinates.
- Core change objects are `Event`, `State`, `Process`, `Trajectory` and temporal `Region`.
- Evidence is a required trust layer: Claim → EvidenceLink → Source/locator.
- Co-presence, possible encounter, documented encounter, interaction, influence and causality are distinct.
- Facts, observations, interpretations, inferences, hypotheses and counterfactuals are distinct.
- ARTEMIS is web-first; PWA/native packaging is delivery, not a second product architecture.
- 2D Map and Globe are renderers over one semantic core; timeline is shared Explorer temporal state.
- Architecture Atlas is a preserved thematic compatibility layer at `/atlas/`.
- First validation vertical: `Life in Context / Leonardo Temporal Map`.
- A bounded source-aware Globe/Temporal Map MVP is active under #355; generative AI, causal/counterfactual runtime, VR/AR, universal corpus and production-scale dynamic Earth remain frozen.
- Current ResearchSlice v2 is compatibility code; #323–#325 are not the active path.

## Change discipline

- Preserve unrelated changes and completed history.
- One question has one canonical owner.
- Update documentation first for product/model/governance changes.
- Keep North Star, Product Thesis, active scope, current implementation, public deployment and validated value separate.
- Do not invent evidence, locator, geometry, route, date precision, relation or migration success.
- Do not convert proximity/co-presence into historical Relation.
- Do not treat absence in a World Slice as historical absence.
- Keep Architecture Atlas public data publication in the ETL/release path.
- Keep Leonardo historical runtime input on the reviewed repository World Model → Explorer State → Render Projection path unless a separate data/storage decision changes it.
- Do not put credentials, tokens, owner identity or private research in public artifacts/storage/logs.
- Do not harden a compatibility schema as target without a contract and migration decision.
- Do not expand a broad product thesis into current implementation without explicit scope/gate authorization.

## Current execution boundary

Foundation v3 is accepted in PR `#328`; the old Concept v2 implementation backlog and PR `#314` are closed.

Active work is issue `#355`. Gate C delivery `#332` / `#360` is completed/FREEZE. Gate D remains OPEN / IN PROGRESS, but its current product step is **after** Core Reset and the first Temporal Map iteration:

- PR `#393` completed Core Reset: root Core landing, `/globe/` primary research surface, `/atlas/` compatibility-only and `ARTEMIS Core Check` isolated as the required product signal;
- PR `#395` established the calendar-based Leonardo Temporal Map life-path loop;
- the first published #395 manual check recorded `ITERATE`;
- PR `#396` implemented and published that bounded correction.

Current Temporal Map behavior:

- `Range` is a two-handle calendar interval using temporal overlap;
- `Scrub` keeps a chosen build origin plus one current-time cursor and accumulates the path forward;
- the full-width bottom timeline is the primary time instrument;
- map, timeline, selection and URL share one state;
- first click opens a compact popup without moving the camera;
- optional further action opens the right detail drawer;
- double-click may focus the selected place;
- dashed connectors are chronology only, never historical route geometry.

The fresh user check of the published #396 loop completed **M1 — UX checkpoint** with `ITERATE`: preserve the current interaction and treat remaining visual issues as non-priority. PR `#400` subsequently completed the reviewed major-life candidate package without runtime authorization. The current milestone is **M2 — One-source proof**: pass exactly one real structured external fact through the existing World Model → Explorer State → Render Projection → Globe path with provenance, rights and uncertainty closure. M3 (multi-source proof) and M4 (architecture decision) remain closed until the M2 exit decision.

Preserve these boundaries:

- #329 / PR #336 World Model fixtures and #330 / PR #337 uncertainty semantics as reviewed READY foundations;
- completed #344 / PR #351 cross-renderer parity as a required green foundation;
- #377 as accepted historical foundation evidence; editable refinement remains deferred;
- #331 `DEFERRED`; derived proximity/co-presence remains separate and documented Relation predicates are prohibited until #331 is explicitly reopened and accepted;
- #371/#373 deferred and the nine Airtable World Model shadow tables empty; the merged mapping preflight does not authorize historical writes;
- one World Model → Explorer State → Render Projection path for both 2D and Globe;
- the Globe explicitly labelled as a public research prototype, not product-validated historical truth;
- MapLibre as the leading current MVP engine unless measured evidence justifies a different renderer decision;
- security, compatibility and critical maintenance remain allowed.

The current Gate D historical input is the non-public Leonardo-in-Romagna 1502 scope package under `fixtures/world_slices/leonardo_romagna_1502/v1/`. It is a frozen curation boundary, not READY public historical data. Exact routes, Region boundaries, durations and historical coordinates remain unknown/withheld where unsupported.

## Verification

Run the smallest relevant checks while iterating. The required product signal is the `ARTEMIS Core Check` workflow. Before handoff for Core/Temporal Map changes, build the public-preview artifact and run the bounded Core tests listed in `.github/workflows/release-gate.yml` plus any directly owned Globe/runtime checks.

Legacy/backend/data work must additionally run its owned checks. The historical repository-wide suite is not a substitute for the Core signal and known #392 review-envelope failures must not be represented as product regressions.

Useful compatibility checks remain:

```bash
python scripts/release_check.py  # Architecture Atlas/backend compatibility only
pytest -q                       # broad suite; report known baseline failures honestly
```

Documentation-only connector work must still verify:

- changed-file scope;
- internal links/registry;
- no contradictory active status;
- current capability truth;
- current decision vocabulary;
- PR diff and GitHub checks.

Report structural checks honestly; they are not user validation.
