# Gate E owner bypass and bounded Temporal Region universality proof v1

- Recorded: 2026-09-10; authority: explicit owner instruction.
- Decision/specification only. Implementation authorization becomes effective after this decision PR is merged. No implementation exists in this PR; do not merge automatically.
- Owner: issue #355; WIP limit 1; no new parallel product issue or automatic M6 name.
- Gate D remains COMPLETED / ADVANCE_TO_GATE_E. M4 ADOPT, original M5 ITERATE, its governance deviation and completed correction acceptance remain unchanged.

## Evidence disposition and current truth

The owner consciously bypasses the planned participant-evidence path: E1 = NOT COLLECTED; E2 = NOT COLLECTED; disposition = owner_directed_bypass. The prepared [Gate E protocol](2026-09-06_GATE_E_BOUNDED_TASK_PROTOCOL_v1.md) is retained as planned / NOT EXECUTED, superseded only for the current critical path. It is neither invalidated nor retrospectively passed. Formal user value remains UNVALIDATED; no positive value signal is inferred. This is not a successful Gate E exit.

The earlier owner statement that E1 was conducted had no task-level observations. This later explicit instruction replaces that interpretation; no participant sessions, dates, devices, metrics or task outcomes are inferred. The owner reports NO FINDINGS for the published #418 review, closing owner manual acceptance only, and accepted #419. Owner acceptance is not independent-user evidence.

Repository reality supersedes the supplied stale expected-main reference: #416 and #418 are merged; #419 is also merged and published. Current runtime is #419 / `a1479670d7f7628ffb85b887961ff27654e2fa2f`, not its predecessor #418 / `b628a80c4b0dd6c7c5485029c4ce4d1c49d4eec4`. Publication was verified on 2026-09-09 by byte equality of live runtime/CSS; runtime SHA-256 `623b409b3d615897553a06a9c58a18b2236a970082fc2d04e87aec38b6f1b282`.

#418 implements Place-centric v4.5 / Temporal Map v1.3 and #419 stabilizes label placement: 9 fixed canonical Place anchors, 11 distinct Presence episodes with separate timeline/selection/URL/details, visible repeated counts, no displacement/tethers, presentation-only chronology chevrons, one-handle default Scrub with deterministic legacy from/at restoration, Range interval semantics and unknown_route / route_geometry=null. Product Scope v4.6 changes the next authorized experiment only, not that runtime.

#416 is the earlier accepted decision for one canonical time with future Global Timeline and Focus Timeline as synchronized views at different scales/temporal viewports. There is no independent global_time/focus_time, and no dual-timeline implementation is authorized here.

## One next question

Can ARTEMIS represent and explore a fundamentally different spatiotemporal object — a time-varying Region such as the Roman Empire — through the same semantic and runtime boundaries already used by the Leonardo Temporal Map, without creating a separate object-specific engine?

Compare Leonardo Entity → Presence/State → Trajectory → point/chronology presentation with Roman Empire Entity → State/Region → temporally valid polygon/multipolygon. Both must use World Model → Explorer State → Render Projection → existing Map/Globe renderer boundary and one canonical temporal state. The [World Model contract](../SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md) already defines State, Region and temporal geometry; no ontology change is made by this decision.

## Source-first scope and stop rule

After decision merge, open exactly one bounded source/implementation branch:

- One Roman Empire Entity, 3–5 source-supported temporal Region states; one currently focused Region at a time.
- Dates/intervals come from actual source precision, not invented milestones. Geometry is polygon/multipolygon with explicit temporal validity, provenance, licensing and uncertainty/reconstruction status.
- First locate publicly accessible or otherwise usable, legally compatible, attributable and temporally interpretable structured/geospatial material supporting actual geometry or a clearly documented reconstruction. Record source identity/version, locator, license, transformations and limitations.
- AI may assist discovery/normalization; AI is not the Source. No LLM-generated boundary, plausible hand-drawn border, invented interpolation or unsupported exactness.
- If adequate material cannot support at least three states, stop with a source-feasibility limitation. Do not fabricate a substitute or call source unavailability an architecture failure. No implementation or GENERALIZES result follows from a source gap alone.
- Preserve source conflicts/alternatives only where necessary for honest uncertainty; do not collect multiple reconstructions merely to expand scope.

This is not a Roman Empire historical product: no full 27 BC–476 AD history, provinces, emperors, battles, roads, religions, cultures, cities, military movements, contextual people, historical terrain, complete-border claim or contextual layers. No backend/Airtable, provider federation infrastructure, selector redesign or unrelated refactoring.

### Source-state comparability rule

Treat snapshots as a temporal sequence only when they describe the same Region identity and territorial concept (for example, political control versus influence), with compatible coverage, inclusion criteria, spatial generalization and reconstruction method. Prefer a coherent versioned dataset. For each state record these dimensions and any change in source/method. Differences between incompatible definitions, coverage or reconstruction methods must not be presented as historical territorial change. Use a documented evidence-supported normalization only if it preserves provenance and uncertainty; otherwise keep alternatives separate or exclude the incompatible state. If fewer than three comparable source-supported states remain, stop with a source-feasibility limitation. Do not manufacture comparability by drawing borders or interpolating unsupported intervals.

## Shared architecture and temporal boundary

Before later implementation, inspect actual code and classify A: existing generic semantic/runtime machinery; B: Leonardo-specific presentation plumbing; C: genuinely missing generic capability. Adapt only the necessary B into reusable boundaries. A small TemporalObjectProjection with Trajectory and Region projections is a possible pattern, not a mandated new subsystem.

No romanEmpireRuntime, romanEmpireTimeline, romanEmpireRenderer, object-name condition or equivalent parallel engine. Do not over-generalize for hypothetical types. Minimum existing temporal control may select Region states through the canonical time. Do not implement Global/Focus; record a demonstrated need as evidence for a later separate decision. Leonardo remains the default published proof until a separate publication decision.

## Later implementation acceptance

1. Roman Empire uses canonical World Model Entity/State/Region semantics; data is not renderer-owned.
2. At least 3 source-supported temporal Region states can be selected/projected; target maximum 5.
3. Changing canonical time changes the visible Region state.
4. Geometry validity is temporal; no single polygon is eternally valid, and gaps are not silently interpolated.
5. Actual sources/locators, provenance and uncertainty remain inspectable.
6. No unsupported historical/spatial/temporal exactness is introduced.
7. Leonardo Presence/Place identity, Trajectory authority, Range/Scrub, URL and popup/camera semantics remain intact.
8. Region reuses Explorer State → Render Projection → existing renderer boundaries.
9. There is no Roman-specific temporal truth or second engine.
10. Another Region snapshot is primarily a data change, not another renderer feature.
11. Existing Core/Globe semantic gates remain green; executable temporal-validity, state-change, provenance and Leonardo regression checks accompany the proof.
12. Default Leonardo publication is preserved pending a separate publication decision.

## Later proof disposition

| Outcome | Meaning |
|---|---|
| GENERALIZES | Region traverses the same fundamental semantic/runtime path with only minimal reusable extension; technical generality only. |
| NARROW | Approach is viable but a specific bounded shared abstraction is missing; identify it without authorizing broad refactoring. |
| FAILS_GENERALITY | Region requires a substantially separate engine or contradicts the fundamental architecture; substantiate the contradiction. |

No outcome is selected now. A source-blocked or incomplete proof is explicitly unresolved rather than forced into these outcomes. GENERALIZES is not product-market validation. Formal user value remains unvalidated throughout subsequent development unless new independent evidence is collected under a separate explicit decision.

## Operational representation and closeout

project_state v1.5 adds a required gate_e record with status/e1/e2 = not_collected, disposition = owner_directed_bypass, formal_user_value = unvalidated, and this decision reference. next_transition.target points to TEMPORAL_REGION_PROOF (a work target, not a gate) with explicit_owner_instruction and the same reference. The gate field still records the historical Gate D completion; historical M4/M5 checkpoints are not repurposed. Schema/validator negative tests reject false passes, missing authority and unregistered decisions. WIP remains one; #355 remains the sole product issue.

Record the decision in one PR before synchronizing #355. While unmerged, distinguish the owner instruction from pending repository integration and do not open implementation. After merge, #355 should point to this single source-first proof; participant evidence remains not collected. No new issue is required.

## Exact follow-up prompt — use only AFTER this decision PR is merged

> ARTEMIS — bounded Roman Empire / Temporal Region universality proof. Work from current main of omegapunctum/ARTEMIS. First verify that docs/work/2026-09-10_GATE_E_OWNER_BYPASS_AND_REGION_PROOF_v1.md is merged. If not, stop; do not implement. Follow its scope and twelve acceptance criteria, current PROJECT_TRUTH, project_state, Product Scope and the existing World Model contract. E1/E2 were intentionally bypassed, remain NOT COLLECTED, and formal user value is UNVALIDATED. Do not claim a Gate E pass or positive user-value signal.
>
> Open one bounded branch, WIP 1. First assess source feasibility for one Roman Empire Entity and 3–5 temporally valid Region polygon/multipolygon states. Record source/version/locator/license, native date precision and uncertainty/reconstruction limits. AI is not the Source; no fabricated or plausibly drawn borders. If adequate sources cannot support at least three states, report the bounded source gap and stop without fabricating geometry or an architecture verdict.
>
> Apply the source-state comparability rule above before treating snapshots as one temporal sequence; fewer than three comparable states is a source-feasibility stop, not evidence of historical change.
>
> Before coding classify existing generic machinery, Leonardo-specific plumbing and missing generic capability. Reuse World Model → Explorer State → Render Projection → existing MapLibre renderer and one canonical temporal state. Generalize only the necessary shared boundary; no Roman-specific engine, independent time, Global/Focus implementation, contextual corpus, backend/Airtable or unrelated refactor. Keep one focused Region and preserve the published Leonardo default until a separate publication decision.
>
> Implement only if source feasibility is established. Add executable temporal validity/time-change/provenance tests and Leonardo regression checks. Run Core, Globe Boundary, relevant geospatial/browser evidence and public-preview build. Return source audit, abstraction diff, acceptance results, actual limitations, screenshots, exact head/CI and one PR. Recommend GENERALIZES, NARROW or FAILS_GENERALITY only from evidence; label blocked/incomplete evidence explicitly. Do not merge or publish automatically. Technical generality never establishes user value.
