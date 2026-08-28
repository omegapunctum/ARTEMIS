# ARTEMIS — PRIORITIES v7.0

## Status

- Type: canonical active priorities.
- Date: 2026-08-28.
- Active cycle: Core Reset inside the Globe MVP vertical.
- Active primary issue: GitHub issue `#355`.
- Foundation-maintenance incident: issue `#392`, reduced to historical-control isolation.
- Public entrypoint: ARTEMIS Core landing; Leonardo Globe is primary at `/globe/`, Architecture Atlas is compatibility-only at `/atlas/`.

## P0 — One working ARTEMIS Core

The only active product question is whether a source-aware spatial-temporal
configuration helps a user understand Leonardo in context.

The load-bearing path is:

`Leonardo sources/manifests → World Model → Explorer State → Render Projection → Globe + inspector`

Required behavior:

- one shared time/interval state;
- synchronized layers and selection;
- Event, State, Process, Trajectory and Region semantics;
- source, locator, uncertainty, coverage and projection-loss access;
- explicit unknown routes and geometry-withheld alternatives;
- present-day context clearly separated from historical assertions;
- URL-restorable exploration without a backend.

The current bounded package remains honest:

- Gate C `FREEZE` evidence for #332/#360 is preserved byte-for-byte;
- historical Claims remain draft/rejected;
- no route or Region geometry is invented;
- `historical_corpus_ready=false` and `promotion_allowed=false`;
- four settlement coordinates are present-day source-bound reference anchors only.

## P1 — Reduce the active delivery surface

Core Reset rules:

1. Leonardo Globe is the primary product-development surface.
2. Architecture Atlas is preserved at `/atlas/` as a compatibility baseline, not a second active product.
3. FastAPI, auth, Redis, drafts, moderation, Research Slices, Stories, Courses and uploads are frozen compatibility code.
4. Airtable legacy export and the nine empty World Model shadow tables are outside the Core critical path.
5. Progressive Refinement v1 remains accepted historical evidence, but its repository-wide READY envelope is manual while #392 separates immutable semantics from mutable routing.
6. The required CI signal is ARTEMIS Core Check. Legacy checks run only when their owned paths change or by manual dispatch.

Security fixes and preservation of accepted evidence remain allowed. New backend,
storage, Airtable, UGC or platform capability requires evidence that the static
read-only product loop is insufficient.

## P2 — Validate value before further infrastructure

The next product increment is one complete user journey:

1. choose a date or interval;
2. see Leonardo's local context and simultaneous global context;
3. select an object;
4. distinguish what is supported, contextual, uncertain or unresolved;
5. return to the same state through the URL.

After that increment, run a small observed validation against the same-content
baseline. Do not wait for a second infrastructure gate before learning from users.

Minimum decision evidence:

- users can reconstruct the spatial-temporal context;
- users discover at least one relevant simultaneous event or process;
- source and uncertainty displays do not cause systematic overclaim;
- Globe value is not only visual novelty;
- the curation and review cost remains bounded.

Record one result:

- `ITERATE`;
- `NARROW`;
- `STOP/RETHINK`.

Only `ITERATE` may reopen persistence, editorial storage or broader corpus work.

## Preserved foundations

- #329 / PR #336 — reviewed World Model fixtures;
- #330 / PR #337 — uncertainty semantics;
- #339 / PR #346 — renderer-neutral architecture;
- #340 / PR #347 — Explorer State;
- #341 / PR #348 — Render Projection;
- #342 / PR #349 — geospatial asset boundary;
- #343 / PR #350 — MapLibre Globe spike;
- #344 / PR #351 — cross-renderer semantic parity;
- #345 / PR #352 — repository/runtime boundary;
- #332/#360 / PR #362 — frozen Leonardo-in-Romagna source boundary.

These are technical foundations, not user-value evidence.

## Deferred

- #331 documented Relation predicates;
- #334 formal participant protocol as previously sequenced;
- #371/#373 Airtable historical import/review;
- editable Progressive Refinement runtime;
- generative AI, causal/counterfactual runtime, universal corpus, VR/AR;
- production backend and dynamic Earth infrastructure.

## Execution order

1. Merge the Core Reset boundary and restore one trustworthy required check.
2. Complete one Leonardo Globe user journey.
3. Observe users and record `ITERATE`, `NARROW` or `STOP/RETHINK`.
4. Open at most one evidence-backed next branch.

## Completion rule

A change is complete when the core artifact works, source/uncertainty semantics are
preserved, the relevant core tests pass and the next user-facing question is explicit.
Routine PRs do not require synchronized edits across historical gate records.
