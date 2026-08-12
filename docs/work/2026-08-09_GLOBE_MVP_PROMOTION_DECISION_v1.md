# ARTEMIS — Globe MVP Promotion Decision v1

## Status

- Type: active product/governance decision record.
- Date: 2026-08-12.
- Active epic: GitHub issue `#355`.
- Completed recovery: issue `#344` / PR `#351`.
- Completed Gate C delivery: issues `#332` / `#360` and `2026-08-09_LEONARDO_WORLD_SLICE_SCOPE_v1.md`.
- Active Gate D contract: `2026-08-12_GATE_D_OPENING_v1.md`.
- Public capability change: none.

## 1. Decision

The 3D Globe becomes the primary interface-development contour for the next ARTEMIS cycle.

This is a bounded product-facing MVP vertical over the accepted renderer-neutral architecture. It is not permission to create a second historical model, publish a production Globe, reconstruct the whole Earth or replace evidence with visual plausibility.

The required flow remains:

```text
World Model / World Slice
        +
Explorer State
        ↓
Render Projection
        ↓
2D renderer | Globe renderer
```

The current public 2D MapLibre runtime remains the compatibility baseline, same-content comparison surface and rollback path until a separate promotion decision.

## 2. Why the order changes

The bounded #339–#345 work established enough executable architecture to make a Globe vertical reversible:

- one semantic core;
- renderer-neutral Explorer State;
- deterministic Render Projection;
- geospatial asset/provider boundaries;
- a browser-executed MapLibre Globe spike;
- a repository/publication boundary.

However, the lifecycle was closed incorrectly:

- issue #344 was closed while PR #351 remained open and its parity workflow failed;
- PR #354 added a lifecycle test whose required canonical wording was not committed;
- canonical owners continued to force #331 as the active path after the user selected Globe as the project focus.

The recovery order is therefore:

1. restore canonical governance and a green Release Discipline Gate — completed in PRs #356–#357;
2. complete #344 / PR #351 on current `main` — completed;
3. freeze one small real World Slice boundary — completed/FREEZE through #332/#360;
4. build a source-aware Globe MVP through the shared semantic pipeline — active Gate D;
5. collect semantic, UX, accessibility and performance evidence;
6. record one promotion/iterate/narrow/stop decision.

## 3. Relation boundary

Issue #331 is `DEFERRED`, not rejected.

The Foundation distinction between co-presence, encounter, interaction, influence and causality remains mandatory. Until #331 is accepted:

- proximity/co-presence may appear only as a derived observation;
- documented Relation predicates may not be introduced into the real Globe MVP corpus/runtime;
- the MVP may still implement time, layers, Events, States, Processes, Trajectories, Regions, selection, evidence and uncertainty.

#331 becomes a blocking dependency only before documented Relations enter the real World Slice or product surface. It must be explicitly reopened before that work.

The #371/#373 Airtable import/review contour is also deferred. Gate D consumes the frozen repository package directly; nine shadow tables remain empty and no historical write is authorized.

## 4. MVP scope

The active #355 vertical must prove:

- one selected time or interval controls all views;
- layers and knowledge objects remain synchronized;
- canonical picking resolves to World Model identity;
- source, locator, uncertainty, reconstruction mode and projection losses remain accessible;
- unresolved routes and alternative Regions do not gain false precision;
- modern terrain/imagery is visibly contextual and correctly attributed;
- 2D and Globe preserve semantic parity;
- a small real World Slice can be prepared and reviewed at known cost.

The initial content candidate remains a bounded Leonardo / Life in Context slice. Scope may be narrowed if curation evidence shows that a smaller slice is required.

## 5. Repository and deployment boundary

The generated `scripts/globe_spike/` artifact remains the starting implementation boundary.

Moving to `apps/globe/` requires evidence that the Globe is becoming a maintained application. Public deployment requires an additional explicit decision, provider/licensing review, real-device validation, accessibility evidence, rollback plan and synchronized current-truth/release updates.

## 6. Engine decision

MapLibre GL JS remains the leading engine for the MVP because the executable spike already exists and consumes ARTEMIS projection contracts.

CesiumJS is evaluated only if real corpus/runtime evidence exposes a material MapLibre limitation in terrain, 3D Tiles, precision, scene complexity or performance.

## 7. Non-goals

- universal historical corpus;
- public production Globe in this decision;
- automatic Relation or causal inference;
- generative AI;
- VR/AR;
- photorealistic or universal historical terrain reconstruction;
- backend/framework/repository rewrite without a measured blocker;
- separate 2D/3D historical truth datasets.

## 8. Exit

This decision exits only when #355 records exactly one result:

- continue as generated R&D evidence;
- promote to a maintained experimental application;
- narrow/rework the vertical;
- stop/rethink.

No result automatically authorizes public deployment or broader product expansion.
