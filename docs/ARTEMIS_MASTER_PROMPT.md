# ARTEMIS — МАСТЕР-ПРОМПТ v6.3

Статус: canonical operational governance for AI agents and assistants.
Дата: 2026-08-09.

## 1. Роль проекта

ARTEMIS — source-aware spatial-temporal world model.

Миссия:

> помогать человеку понимать мир как взаимосвязанную систему сущностей, событий, состояний и процессов, наблюдаемую в пространстве и времени.

Core:

- synchronized space/time;
- Entity/Event/State/Process/Trajectory/Region/Layer;
- Claim/EvidenceLink/Source/locator;
- visible uncertainty and corpus coverage;
- explicit relation ladder;
- human judgment.

Architecture Atlas — thematic layer and technical baseline. `Life in Context` — first validation vertical.

## 2. Source of truth

- canonical registry/routing: `docs/FOUNDATION_INDEX.md`;
- current capability: `docs/PROJECT_TRUTH.md`;
- North Star: `docs/ARTEMIS_CONCEPT.md`;
- active product: `docs/PRODUCT_THESIS.md`, `docs/ARTEMIS_PRODUCT_SCOPE.md`;
- world model: `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- uncertainty profile: `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md`;
- epistemics: `docs/EPISTEMIC_CONTRACT.md`;
- entities: `docs/ENTITY_MODEL.md`;
- current public data/runtime contract: `docs/DATA_CONTRACT.md`;
- priorities/order: `docs/PRIORITIES.md`, `docs/PROJECT_PHASES.md`;
- working lifecycle: `docs/work/README.md`.

Working/audit/archive files cannot override canonical owners.

## 3. Current technical boundaries

- Vanilla JavaScript + MapLibre frontend is the current public 2D baseline.
- FastAPI backend.
- SQLite baseline; PostgreSQL may require later decision.
- Airtable curated source.
- ETL publishes current canonical public `data/*` artifacts.
- `data/features.geojson` is the current public **2D map projection/source**, not the universal representation of all Foundation v3 knowledge.
- A generated MapLibre GL JS 5.24.0 Globe R&D artifact exists, but it is not a public entrypoint or a real historical corpus.
- GitHub Pages serves the static frontend; backend is separate.
- No React/Vue/Angular/TypeScript without architecture decision.
- No direct frontend Airtable access.
- No token/private research storage in Web Storage.
- No competing semantic/world-model source of truth.

## 4. Foundation invariants

1. Space and time are mandatory coordinates.
2. Static cards/dates do not replace change objects.
3. Geometry and state may change over time.
4. Precision and uncertainty are explicit.
5. Co-presence is not encounter, interaction, influence or causality.
6. Relation is a structured Claim.
7. Claim kind, origin, review, confidence, evidence and uncertainty are independent.
8. AI is not Source.
9. Counterfactual world is isolated from historical assertions.
10. Dataset absence is not historical absence.
11. Current capability is separate from concept.
12. Compatibility runtime does not define target ontology.
13. Renderer engines do not own domain semantics.
14. Renderer payloads are projections of one World Model / World Slice, not independent historical truth datasets.
15. Terrain/imagery/tiles are geospatial rendering assets unless they explicitly assert historical state through World Model semantics.
16. 2D/3D visual differences must not change active object identity, temporal validity, uncertainty, evidence or relation meaning.

## 5. Current order

Active: Globe MVP / issue `#355`.

Execution path:

1. Preserve reviewed #329 / PR #336 World Model and #330 / PR #337 uncertainty foundations.
2. Preserve the completed PRs #356–#357 lifecycle recovery and green Release Discipline Gate.
3. Preserve completed #344 / PR #351 semantic parity as a green renderer foundation.
4. Freeze and curate the bounded Leonardo-in-Romagna slice for 8 August–31 December 1502 through #332/#360 inside #355.
5. Build the synchronized Globe/timeline/layers experience through Explorer State and Render Projection.
6. Keep the current 2D renderer as public baseline, same-content parity target and rollback path.
7. Collect semantic, UX, accessibility and performance evidence.
8. Record one explicit promotion/iterate/narrow/stop decision.

Issue #331 is `PAUSED`. It becomes blocking before documented Relation predicates enter a real corpus/runtime. Until then, only derived proximity/co-presence is allowed.

Issues #339–#345 / PRs #346–#352 are accepted renderer foundations, including the recovered cross-renderer semantic parity contract.

Foundation v3 is accepted in PR `#328`. The superseded #323–#325 path and PR #314 are closed and must not be reopened as the active ontology.

## 6. Frozen / gated work

Frozen or gated at product scale:

- generative AI;
- causal/counterfactual engine;
- public production Globe before promotion evidence;
- universal or photorealistic historical terrain reconstruction;
- VR/AR;
- Stories/Courses expansion;
- open UGC;
- institutional workflow;
- universal corpus;
- heavy scaling/platform work.

Security/compatibility maintenance remains allowed.

The bounded source-aware Globe MVP is explicitly allowed under #355. It remains non-public until a separate promotion decision.

## 7. Renderer / Globe rule

When working on 2D map, 3D Globe or future renderers:

1. start from World Model / World Slice semantics;
2. use renderer-neutral selected time/layers/object state;
3. convert through an explicit render projection boundary;
4. preserve canonical object identity and epistemic references;
5. expose unsupported semantics instead of silently dropping them;
6. never invent route, geometry, altitude, terrain history or temporal precision because a renderer can draw it;
7. keep engine-specific camera/GPU/tile/picking state outside the semantic core;
8. require semantic parity before promoting a second renderer;
9. treat screenshot equality as visual evidence only: **Screenshot equality is not semantic parity**.

Working architecture: `docs/work/2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md`.
Active product decision: `docs/work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md` under #355.

## 8. Docs-first rule

For changes to mission, model, data, runtime, release, AI or governance:

1. analyze conflict;
2. identify owner docs;
3. define scope and decision;
4. update docs/contracts;
5. review consistency;
6. only then implement;
7. run checks and update current truth.

## 9. Prohibited shortcuts

- inventing date/geometry/route/evidence/locator;
- using smooth visual interpolation as historical fact;
- treating modern boundaries or modern terrain as timeless;
- converting co-presence/similarity into Relation;
- treating AI output as Source;
- hiding corpus coverage;
- claiming 3D/VR/AI/world coverage before implementation;
- creating separate 2D/3D historical truth datasets or `*_2d` / `*_3d` source-of-truth forks;
- allowing a map/globe engine to redefine temporal, spatial or epistemic semantics;
- rewriting old issues into new meaning;
- performing irreversible migration before fixtures/contract;
- using archive or audit as active owner.

## 10. Definition of Ready

A task is ready when:

- goal and expected result are explicit;
- owner docs and affected files are known;
- current vs target boundary is known;
- scope lock and non-goals are stated;
- happy path, uncertainty/error cases and checks are defined;
- migration/rollback is defined if data/runtime changes.

## 11. Definition of Done

- requested artifact exists;
- only intended scope changed;
- relevant checks pass;
- docs and lifecycle registry agree;
- current truth is honest;
- no invented epistemic/spatial/temporal precision;
- no hidden competing model;
- next dependency or stop decision is explicit.

For renderer work, Done additionally requires no silent semantic divergence from the shared World Model/Explorer State contract.

## 12. Response format

For analysis:

1. conclusion;
2. conflicts/evidence;
3. recommended decision;
4. next action.

For implementation:

1. outcome;
2. changed artifacts;
3. verification;
4. remaining gate/blocker.

## 13. Final rule

Do not expand ARTEMIS by losing its world-model identity.

Build one small, source-aware Globe World Slice that proves understanding without becoming a second semantic source of truth. AI, VR, universal scale, public Globe promotion and production-scale dynamic Earth remain gated until evidence justifies them.
