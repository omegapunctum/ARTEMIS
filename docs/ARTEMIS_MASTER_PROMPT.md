# ARTEMIS — МАСТЕР-ПРОМПТ v6.0

Статус: canonical operational governance for AI agents and assistants.
Дата: 2026-07-28.

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
- epistemics: `docs/EPISTEMIC_CONTRACT.md`;
- entities: `docs/ENTITY_MODEL.md`;
- priorities/order: `docs/PRIORITIES.md`, `docs/PROJECT_PHASES.md`;
- working lifecycle: `docs/work/README.md`.

Working/audit/archive files cannot override canonical owners.

## 3. Current technical boundaries

- Vanilla JavaScript + MapLibre frontend.
- FastAPI backend.
- SQLite baseline; PostgreSQL may require later decision.
- Airtable curated source.
- ETL publishes canonical `data/*`.
- `data/features.geojson` is current public map source.
- GitHub Pages serves the static frontend; backend is separate.
- No React/Vue/Angular/TypeScript without architecture decision.
- No direct frontend Airtable access.
- No token/private research storage in Web Storage.
- No competing canonical public data source.

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

## 5. Current order

Active: Foundation v3.

1. Align canonical foundation.
2. Merge the decision.
3. Correct old backlog and create clean v3 issues.
4. Review world-model fixtures.
5. Freeze first World Slice.
6. Implement synchronized explorer.
7. Run contextual-learning validation.
8. Open at most one evidence-backed branch.

No #323–#325 migration and no PR #314 merge before Foundation decision.

## 6. Frozen work

- generative AI;
- causal/counterfactual engine;
- 3D/dynamic terrain;
- VR/AR;
- Stories/Courses expansion;
- open UGC;
- institutional workflow;
- universal corpus;
- heavy scaling/platform work.

Security/compatibility maintenance remains allowed.

## 7. Docs-first rule

For changes to mission, model, data, runtime, release, AI or governance:

1. analyze conflict;
2. identify owner docs;
3. define scope and decision;
4. update docs/contracts;
5. review consistency;
6. only then implement;
7. run checks and update current truth.

## 8. Prohibited shortcuts

- inventing date/geometry/route/evidence/locator;
- using smooth visual interpolation as historical fact;
- treating modern boundaries as timeless;
- converting co-presence/similarity into Relation;
- treating AI output as Source;
- hiding corpus coverage;
- claiming 3D/VR/AI/world coverage before implementation;
- rewriting old issues into new meaning;
- performing irreversible migration before fixtures/contract;
- using archive or audit as active owner.

## 9. Definition of Ready

A task is ready when:

- goal and expected result are explicit;
- owner docs and affected files are known;
- current vs target boundary is known;
- scope lock and non-goals are stated;
- happy path, uncertainty/error cases and checks are defined;
- migration/rollback is defined if data/runtime changes.

## 10. Definition of Done

- requested artifact exists;
- only intended scope changed;
- relevant checks pass;
- docs and lifecycle registry agree;
- current truth is honest;
- no invented epistemic/spatial/temporal precision;
- no hidden competing model;
- next dependency or stop decision is explicit.

## 11. Response format

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

## 12. Final rule

Do not expand ARTEMIS by losing its world-model identity.

Build small, source-aware World Slices that prove understanding before opening AI, 3D, VR or scale.
