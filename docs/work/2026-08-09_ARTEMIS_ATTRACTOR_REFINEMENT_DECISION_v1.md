# ARTEMIS — Attractor Refinement Decision v1

## Status

- Type: working foundation decision record.
- Date: 2026-08-09.
- Issue: #363.
- Foundation base: v3 / PR #328.
- Product state at decision: Gate C completed/FREEZE in PR #362; Gate D is next but not started by this decision.
- Public capability change: none.

## 1. Problem

Foundation v3 correctly restored ARTEMIS as a source-aware spatial-temporal world model, but the phrase `world model` can be read too literally: as if ARTEMIS claimed to reproduce objective reality itself.

The project actually operates through source-bound knowledge: Claims, EvidenceLinks, Sources, reconstructions, derived observations, uncertainty and explicit corpus coverage. The long-term direction also extends beyond a map/globe interface toward a shared environment in which a human and future AI can explore connected knowledge through space and time.

Without an explicit attractor, several future drifts become plausible:

- treating the Globe as the product identity rather than one interface;
- treating a renderer or dataset as the world itself;
- building domain-specific semantic cores for history, ecology, culture or future professional modes;
- reducing AI to detached chat over documents;
- allowing AI-generated text or navigation to blur into canonical knowledge;
- interpreting universal-knowledge, VR/AR or personal-knowledge ideas as present implementation scope.

## 2. Decision

ARTEMIS keeps the technical term **World Model**, but Foundation v3.1 clarifies its identity-level epistemic meaning:

> The ARTEMIS World Model is a source-aware spatial-temporal representation of knowledge, claims, observations and reconstructions about the world. It is not the world itself, not an objective digital twin and not a claim of completeness.

The long-term attractor is:

> **ARTEMIS aims toward an explorable, source-aware spatial-temporal model of human knowledge about the world, where people and future AI can traverse entities, events, states, processes, places, time, claims, evidence and uncertainty as one connected cognitive environment.**

This attractor guides architecture; it does **not** authorize implementation scope.

The clarification belongs primarily to `ARTEMIS_CONCEPT.md`. It does not silently rewrite reviewed executable semantic contracts.

## 3. Architectural consequences

### 3.1 One semantic core, many domains

History is the first proof domain, not the final boundary. Future historical, cultural, ecological, geological, scientific, technological or professional layers must reuse the same spatial-temporal/epistemic core or introduce an explicitly reviewed domain extension without creating a second truth model.

### 3.2 One semantic core, many interfaces

2D map, 3D Globe, local 3D scenes, mobile, API, VR and AR are projections/interfaces over ARTEMIS Core. No interface owns a separate historical/world truth dataset.

### 3.3 AI as a future exploration interface

AI may eventually do more than generate text. Under a separate AI implementation gate it may propose or execute reversible operations over `SynchronizedView` / Explorer State, including time selection, spatial focus, active layers, selected objects, comparisons, reconstruction mode and uncertainty visibility.

AI view actions are control operations, not Claims or Sources. AI may control the **view**, may propose **knowledge candidates**, and may not silently rewrite **canonical knowledge**.

### 3.4 Personal knowledge remains a future branch

A future personal knowledge context may model what a user has explored, learned or left unresolved. It is not added to `ENTITY_MODEL.md` by this decision and does not become current product scope.

## 4. Affected owner documents

This decision synchronizes:

- `docs/ARTEMIS_CONCEPT.md` — sole owner of North Star and long-term attractor;
- `docs/AI_POLICY.md` — future AI knowledge-exploration/view-control semantics;
- `docs/FOUNDATION_INDEX.md` — owner wording, routing and invariants;
- `docs/ARTEMIS_MASTER_PROMPT.md` — agent interpretation and decision test;
- `docs/PROJECT_TRUTH.md` — current-vs-future wording after Gate C;
- `docs/DEVELOPMENT_OPERATING_SYSTEM.md` — foundation-maintenance vs product-gate boundary;
- `docs/work/README.md` — lifecycle registration;
- release/governance tests — regression barrier.

### Reviewed World Model contract disposition

`docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` remains **byte-preserved v1.0** in this refinement.

Reason: it is part of the immutable READY review scope of #329. Changing it would correctly invalidate the reviewed digest and therefore requires a separate semantic-contract revision with new independent review evidence. Foundation v3.1 does not weaken that gate or re-declare the old package READY.

The Concept-level clarification is compatible with the existing v1.0 contract because that contract already models Claims, EvidenceLinks, uncertainty, reconstruction modes and corpus coverage. A future contract version may make the world-vs-knowledge wording explicit only through a separately reviewed decision.

`README.md` may receive a concise summary after the canonical set is stable; README cannot become a second owner.

## 5. Current vs target boundary

Current implementation remains unchanged:

- public runtime: root 2D Architecture Atlas baseline;
- Globe: non-public R&D/MVP surface;
- Gate C: completed/FREEZE;
- Gate D: next product gate, not started here;
- AI generation/runtime: gated;
- documented Relation predicates: gated by #331;
- universal corpus, causal engine, VR/AR and personal knowledge: future.

Target meaning changes only at the foundation-description level: ARTEMIS is explicitly an explorable knowledge model **about** the world rather than a claim to encode the world directly.

## 6. Migration and compatibility

No runtime, database, API, Airtable, ETL, World Slice or reviewed #329 fixture migration is required.

The existing names `World Model`, `World Slice`, `Explorer State` and `Render Projection` remain valid. Existing fixtures do not need semantic rewrites solely because the North Star interpretation is now explicit.

Future contracts must be interpreted consistently with the North Star, but a reviewed contract is changed only through its own change-control/review path.

## 7. Non-goals

This decision does not:

- start Gate D;
- make the Globe public;
- open generative AI implementation;
- add a causal/predictive engine;
- add counterfactual runtime;
- create a universal corpus promise;
- implement VR/AR;
- add personal-knowledge entities to the canonical model;
- create separate `ARTEMIS History`, `ARTEMIS Earth` or other semantic cores;
- create a second canonical `ATTRACTOR.md` / `NORTH_STAR.md` owner;
- invalidate or silently replace the #329 READY World Model review package.

## 8. Acceptance checks

The refinement is acceptable only if:

1. `ARTEMIS_CONCEPT.md` remains the sole North Star/attractor owner;
2. concept wording distinguishes the external world from ARTEMIS knowledge about it;
3. `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` remains byte-identical to the reviewed v1.0 dependency unless a new independent review is performed;
4. AI policy defines reversible view/exploration actions without granting canonical write authority;
5. one-core/many-domains/many-interfaces is explicit;
6. current product scope and `project_state.json` are not advanced to Gate D;
7. an executable documentation guard blocks regression;
8. #329 `--require-ready` remains valid;
9. Release Discipline Gate passes on the exact PR head.

## 9. Evidence reachability note

Gate C / PR #362 was squash-merged after its reviewers inspected frozen commit `bd2e103cdeec615cb19f0a4293c708fe37a4ae52`. Because `project_state.json` intentionally verifies that exact revision, the frozen commit must remain reachable in Git.

A durable evidence branch `evidence/gate-c-leonardo-romagna-1502-frozen` now points to that exact reviewed commit. This preserves evidence reachability; it does not reopen Gate C or create a product branch.

## 10. Rollback

Because this is documentation/governance only, rollback is a normal revert of the decision PR. No data or runtime recovery is required.

The Gate C evidence branch is independent evidence retention and should not be deleted while `project_state.json` references its frozen commit.

## 11. Final rule

**The attractor constrains direction, not schedule.**

A future capability belongs in ARTEMIS core when it strengthens the explorable source-aware spatial-temporal knowledge model without creating a competing truth model, hiding uncertainty or overstating current capability.