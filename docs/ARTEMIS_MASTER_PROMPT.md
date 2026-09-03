# ARTEMIS — МАСТЕР-ПРОМПТ v6.6

Статус: canonical operational governance for AI agents and assistants.
Дата: 2026-09-03.

## 1. Роль проекта

ARTEMIS — source-aware spatial-temporal knowledge model about the world.

Технический `World Model` является semantic-core name. Identity-level North Star clarifies that ARTEMIS represents source-aware knowledge about the world rather than claiming to be objective reality itself; reviewed executable World Model semantics remain governed by their own frozen contracts.

Миссия:

> помогать человеку понимать мир как взаимосвязанную систему сущностей, событий, состояний и процессов, наблюдаемую в пространстве и времени.

Long-term attractor:

> explorable source-aware spatial-temporal model of human knowledge about the world, usable by people and future AI as one connected cognitive environment.

Core:

- synchronized space/time;
- Entity/Event/State/Process/Trajectory/Region/Layer;
- Claim/EvidenceLink/Source/locator;
- visible uncertainty and corpus coverage;
- explicit relation ladder;
- one semantic core across domains and interfaces;
- human judgment.

Architecture Atlas — thematic compatibility layer and preserved technical baseline. `Life in Context / Leonardo Temporal Map` — first active validation vertical.

Attractor guides architecture; it does not authorize implementation scope.

## 2. Source of truth

- canonical registry/routing: `docs/FOUNDATION_INDEX.md`;
- current capability: `docs/PROJECT_TRUTH.md`;
- North Star + attractor + identity-level World Model interpretation: `docs/ARTEMIS_CONCEPT.md`;
- active product: `docs/PRODUCT_THESIS.md`, `docs/ARTEMIS_PRODUCT_SCOPE.md`;
- application platform / delivery / renderer / repository-storage boundary: `docs/PLATFORM_ARCHITECTURE_DECISION.md`;
- reviewed spatial-temporal World Model semantics: `docs/SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- uncertainty profile: `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md`;
- epistemics: `docs/EPISTEMIC_CONTRACT.md`;
- entities: `docs/ENTITY_MODEL.md`;
- AI behavior: `docs/AI_POLICY.md`;
- current Architecture Atlas public-data/export contract: `docs/DATA_CONTRACT.md`;
- priorities/order: `docs/PRIORITIES.md`, `docs/PROJECT_PHASES.md`;
- development execution contract: `docs/DEVELOPMENT_OPERATING_SYSTEM.md`;
- machine-readable operational state: `docs/project_state.json`;
- working lifecycle: `docs/work/README.md`.

Working/audit/archive files cannot override canonical owners.

No separate `ATTRACTOR.md` or `NORTH_STAR.md` may become a competing canonical owner; the owner is `ARTEMIS_CONCEPT.md`.

A reviewed executable contract cannot be edited merely to make wording match a new identity-level clarification. Its own review/change-control path remains authoritative.

## 3. Current technical boundaries

- ARTEMIS is a web-first Web Application; browser execution is the current canonical client platform.
- 2D Map and Globe are presentation renderers over one World Model / Explorer State / Render Projection core, not separate products or truth models.
- Vanilla JavaScript + MapLibre remains the current frontend implementation baseline; no framework rewrite is authorized by current product evidence.
- FastAPI backend exists as frozen compatibility runtime outside the active static Core path.
- SQLite is the preserved backend baseline; future operational storage technology requires evidence-backed architecture decisions.
- Airtable remains the curated editorial source for the Architecture Atlas compatibility export and hosts empty/non-authoritative World Model shadow tables; it is not the current Leonardo historical runtime authority.
- ETL publishes checked-in Architecture Atlas `data/*` artifacts.
- `data/features.geojson` is the current public **2D Architecture Atlas projection/source**, not the universal representation of Foundation knowledge and not the historical source of the Leonardo Globe.
- A generated MapLibre GL JS 5.24.0 Globe R&D runtime is published at `/globe/` as the primary Leonardo research prototype. Public access does not make it a product-validated historical capability.
- Gate C Leonardo-in-Romagna World Slice boundary is frozen/non-public as historical authority input; its Claims remain draft/rejected rather than public historical truth.
- The current Globe consumes the frozen repository package through World Model → Explorer State → Render Projection, not through a live Airtable historical import.
- GitHub Pages serves the static Core landing, `/globe/` research prototype and `/atlas/` compatibility surface; backend is separate.
- No React/Vue/Angular/TypeScript without an explicit architecture decision.
- No direct frontend Airtable access.
- No token/private research storage in Web Storage.
- No competing semantic/world-model source of truth.

## 4. Foundation invariants

1. ARTEMIS identity models source-aware knowledge about the world; it does not claim to encode objective reality itself.
2. Reviewed semantic contracts retain their exact reviewed meaning until separately re-reviewed.
3. Space and time are mandatory coordinates.
4. Static cards/dates do not replace change objects.
5. Geometry and state may change over time.
6. Precision and uncertainty are explicit.
7. Co-presence is not encounter, interaction, influence or causality.
8. Relation is a structured Claim.
9. Claim kind, origin, review, confidence, evidence and uncertainty are independent.
10. AI is not Source and not a silent canonical writer.
11. Counterfactual world is isolated from historical assertions.
12. Dataset absence is not historical absence.
13. Current capability is separate from concept.
14. Compatibility runtime does not define target ontology.
15. One semantic core supports many domains; domains do not own separate truth models.
16. Renderer engines do not own domain semantics.
17. Renderer payloads are projections of one World Model / World Slice, not independent historical truth datasets.
18. Terrain/imagery/tiles are geospatial rendering assets unless they explicitly assert historical state through World Model semantics.
19. 2D/3D visual differences must not change active object identity, temporal validity, uncertainty, evidence or relation meaning.
20. Timeline state is renderer-neutral Explorer State, not renderer-owned domain semantics.
21. Future AI view/query actions must be visible, reversible and separate from knowledge mutation.
22. Personal knowledge context, VR/AR, universal corpus and causal/counterfactual runtime remain future branches until separately opened.
23. Attractor constrains direction, not schedule or current scope.

## 5. Current order

Active product vertical: `Life in Context / Leonardo Temporal Map` / issue `#355`.

Current operational truth:

1. Preserve reviewed #329 / PR #336 World Model and #330 / PR #337 uncertainty foundations byte-for-byte where their READY review scope requires it.
2. Preserve completed #344 / PR #351 semantic parity as a green renderer foundation.
3. Preserve Gate C `FREEZE` from #332/#360 / PR #362 as the only approved real Leonardo World Slice boundary.
4. Preserve accepted Foundation v3.1 / #363 / PR #364 attractor and governance rules; #363 is completed, not active maintenance.
5. Preserve PR `#393` Core Reset as completed: root Core landing, `/globe/` primary research surface, `/atlas/` compatibility-only, ARTEMIS Core Check as the required product signal.
6. Preserve PR `#395` as the calendar-based Temporal Map loop over the frozen four-Presence Romagna scaffold.
7. Preserve the first published #395 manual-feedback result as **`ITERATE`**, not as final user-value validation.
8. Preserve PR `#396` as the published bounded correction: full-width bottom timeline; two-handle `Range`; chosen build origin + one current-time cursor `Scrub`; popup-first selection; optional right drawer; no single-click camera jump; double-click focus.
9. Gate D remains **OPEN / IN PROGRESS** under #355. Implementation success and public R&D access do not by themselves close the gate.
10. The fresh user check of the published #396 interface recorded **`ITERATE`**: preserve the interaction and treat remaining visual issues as non-priority.
11. Preserve PR #400 as the reviewed major-life package, PR #401 as M2, PR #403 as M3 and PR #405 as the M4 `ADOPT` record that opened no successor.
12. Record honestly that the owner then instructed M5 without an intervening repository decision record; do not retrofit one.
13. Preserve PR #406 as the current bounded 11-Presence, six-period, 1452–1519 runtime proof.
14. Freeze new feature branches until the user manually checks the published M5 and records exactly `ITERATE`, `NARROW` or `STOP`.

Issue #331 is `DEFERRED`. It becomes blocking before documented Relation predicates enter a real corpus/runtime. Until it is explicitly reopened and accepted, only derived proximity/co-presence is allowed.

Issues #371/#373 are deferred outside the Gate D critical path. Their merged mapping preflight remains fail-closed: nine Airtable shadow tables are empty and `historical_rows_authorized=false`.

Issue #335 source-bound AI contract remains `GATED / NOT ACTIVE`.

Issues #339–#345 / PRs #346–#352 are accepted renderer foundations, including cross-renderer semantic parity.

Foundation v3 is accepted in PR `#328`; Foundation v3.1 attractor clarification is accepted in PR `#364`. The superseded #323–#325 path and PR #314 remain closed.

Formal D1/M1/A1/P1 closeout and the old automatic Gate E sequencing are not current roadmap drivers. Basic keyboard, responsive and accessible behavior remains required, but more evidence machinery does not precede the fresh user-value check.

## 6. Frozen / gated work

Frozen or gated outside the current M5 checkpoint:

- Leonardo detail beyond the reviewed 11-Presence M5 package;
- default local/global context and broad layer expansion;
- generative AI runtime;
- AI-controlled view/query runtime until a separate command/state contract is approved;
- causal/counterfactual engine;
- public production Globe before promotion evidence;
- universal or photorealistic historical terrain reconstruction;
- VR/AR;
- Stories/Courses expansion;
- open UGC;
- institutional workflow;
- universal corpus;
- personal knowledge model;
- heavy scaling/platform work.

Security/compatibility maintenance remains allowed.

The bounded source-aware Temporal Map/Globe MVP is allowed under #355 only through explicitly opened scope. The Globe is the primary public research prototype; this does not promote it into a validated product capability.

## 7. Attractor decision test

For every proposed capability, ask in order:

1. Does it strengthen ARTEMIS as an explorable source-aware spatial-temporal knowledge model?
2. Can it reuse the shared World Model / epistemic core rather than creating a second truth model?
3. Does it preserve space/time/change/provenance/uncertainty semantics?
4. Is it a domain extension, interface projection, analytical tool or knowledge mutation — and is that boundary explicit?
5. Does it require changing a reviewed contract? If yes, has that contract's review gate been explicitly reopened?
6. Is it current-scope work, or merely consistent with the long-term attractor?
7. What evidence/gate authorizes implementation now?

A capability may be strategically aligned with the attractor and still be **not allowed now**.

## 8. Renderer / Globe / Temporal Map rule

When working on 2D map, 3D Globe, timeline or future renderers:

1. start from World Model / World Slice semantics;
2. use renderer-neutral selected time/layers/object state;
3. convert through an explicit render projection boundary;
4. preserve canonical object identity and epistemic references;
5. expose unsupported semantics instead of silently dropping them;
6. never invent route, geometry, altitude, terrain history or temporal precision because a renderer can draw it;
7. keep engine-specific camera/GPU/tile/picking state outside the semantic core;
8. require semantic parity before promoting a second renderer;
9. treat screenshot equality as visual evidence only: **Screenshot equality is not semantic parity**;
10. treat 2D, Globe, local 3D, VR/AR and future clients as interfaces over one semantic core;
11. treat timeline as a controller/view over shared Explorer temporal state, not a third truth model;
12. `Range` and `Scrub` are interaction modes over the same temporal/Trajectory semantics, not separate domain entities;
13. current `Range` means interval overlap; current `Scrub` means a chosen build origin plus one current-time cursor with accumulated path;
14. presentation-only dashed chronology must never become historical route geometry;
15. single-click selection must not implicitly change camera state; explicit focus is a separate action.

Working architecture: `docs/work/2026-08-08_GLOBE_RENDERER_ARCHITECTURE_v1.md`.
Current Temporal Map interaction: `docs/work/2026-08-28_TEMPORAL_MAP_LIFE_PATH_V1.md`.
Active product decision: `docs/work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md` under #355.

## 9. AI rule

For future AI work, read `AI_POLICY.md` before designing prompts, tools or state actions.

Core distinction:

- AI may explain or propose knowledge candidates;
- AI may eventually change approved view/query state through explicit reversible actions;
- AI may not treat a view change as evidence;
- AI may not silently mutate canonical Claims/Evidence/Sources/Uncertainty;
- AI output is not Source;
- an AI command schema requires a separate implementation decision.

Do not implement AI behavior merely because it appears in the long-term attractor.

## 10. Docs-first rule

For changes to mission, model, data, runtime, release, AI or governance:

1. analyze conflict;
2. identify owner docs;
3. identify whether any owner belongs to a frozen reviewed scope;
4. define scope and decision;
5. update only documents/contracts whose own change-control allows the change;
6. review consistency;
7. only then implement;
8. run checks and update current truth.

Foundation identity changes require one synchronized decision PR and an executable regression guard.

A frozen reviewed semantic contract requires new review evidence before its bytes change; do not weaken the validator to avoid that requirement.

## 11. Prohibited shortcuts

- inventing date/geometry/route/evidence/locator;
- using smooth visual interpolation as historical fact;
- treating modern boundaries or modern terrain as timeless;
- converting co-presence/similarity into Relation;
- treating AI output as Source;
- hiding corpus coverage;
- describing ARTEMIS identity as an objective digital twin or complete historical reality;
- claiming 3D/VR/AI/world coverage before implementation;
- creating separate domain-specific or renderer-specific truth models;
- creating `*_2d`, `*_3d`, `history_core`, `earth_core` or similar source-of-truth forks without a foundation decision;
- allowing a map/globe/timeline engine to redefine temporal, spatial or epistemic semantics;
- allowing an AI view action to mutate canonical knowledge implicitly;
- rewriting a frozen reviewed contract while retaining its previous READY claim;
- weakening a review digest or validator because a documentation change touched reviewed scope;
- rewriting old issues into new meaning;
- performing irreversible migration before fixtures/contract;
- using archive or audit as active owner;
- using the attractor or broader Product Thesis itself as implementation authorization.

## 12. Definition of Ready

A task is ready when:

- goal and expected result are explicit;
- owner docs and affected files are known;
- reviewed/frozen ownership is known;
- current vs target boundary is known;
- scope lock and non-goals are stated;
- happy path, uncertainty/error cases and checks are defined;
- migration/rollback is defined if data/runtime changes;
- current gate/issue authorization is explicit.

## 13. Definition of Done

- requested artifact exists;
- only intended scope changed;
- relevant checks pass;
- docs and lifecycle registry agree;
- current truth is honest;
- no invented epistemic/spatial/temporal precision;
- no hidden competing model;
- no invalidated READY review claim;
- next dependency or stop decision is explicit.

For renderer/Temporal Map work, Done additionally requires no silent semantic divergence from the shared World Model/Explorer State/Trajectory contract.

For AI view-state work, Done additionally requires visible/reversible state transitions and no hidden canonical knowledge mutation.

## 14. Response format

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

## 15. Final rule

Do not expand ARTEMIS by losing its knowledge-model identity or reviewed-contract integrity.

Build toward one explorable source-aware spatial-temporal model of connected knowledge, but implement only the branch and gate that evidence currently authorizes.
