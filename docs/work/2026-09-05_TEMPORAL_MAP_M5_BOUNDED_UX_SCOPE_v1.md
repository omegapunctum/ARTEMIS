# Temporal Map M5 bounded UX correction v1

## Status

Post-publication amendment: [M5 post-#411 correction](2026-09-05_M5_POST_411_CORRECTION_v1.md) records the owner's fresh ITERATE and explicitly supersedes the no-map-connector presentation restriction below. Historical route geometry remains forbidden; dashed chronology links are now authorized. The original decision text below is preserved as history.

- Type: Gate D decision-only implementation scope.
- Date: 2026-09-05.
- Active product issue: `#355`.
- Parent evidence: `2026-09-04_TEMPORAL_MAP_M5_EXIT_DECISION_v1.md` / `ITERATE`.
- Decision: **authorize exactly one bounded UX implementation branch after this decision merges**.
- Runtime change in this decision: none.

## 1. Product question

Can the published 11-Presence, 1452–1519 Temporal Map read as one chronological life path and remain compositionally usable without drawing or implying unsupported historical routes?

This correction preserves the M5 content package, Range/Scrub semantics and the World Model → Explorer State → Render Projection path. It does not reopen data, source, Relation, context, storage or renderer architecture.

## 2. Must-fix scope

The implementation branch must deliver all seven recorded corrections as one bounded interface package:

1. Make chronological order and period membership legible through non-route presentation: stable Presence sequence cues, period cues and synchronized emphasis between visible map markers and the timeline. Do not connect Presence coordinates with a spatial path.
2. Close the compact popup when `Open details` opens the right drawer while preserving the selected Presence in shared Explorer State and the URL.
3. Reduce marker and interface-control visual density without weakening pointer targets, keyboard access or selected-state legibility.
4. Shorten the bottom timeline region while retaining Range/Scrub controls, readable calendar values and its role as the primary time instrument.
5. Remove the upper-left header/map-control collision at supported viewport profiles.
6. Add a current-M5 `EN / RU` presentation dictionary and explicit switch. Language changes presentation only; canonical IDs, Claims, source locators and URL-restorable exploration state remain unchanged.
7. Keep map attribution/status visible and non-overlapping when the right drawer is open.

The implementation may adjust layout tokens, marker styling and responsive breakpoints only where required by these seven corrections. Unrelated visual redesign is excluded.

## 3. Semantic constraints

- `Trajectory` remains the semantic authority.
- Every unsupported transition remains `unknown_route` with `route_geometry=null`.
- Sequence numbers, period colors, timeline segments, highlighting and accumulation are presentation of chronology, not evidence of a travelled route.
- No map line, corridor or animated interpolation may connect unsupported Presence coordinates.
- Present-day settlement anchors remain reference points, not exact historical positions.
- `Range` remains interval overlap; `Scrub` remains build origin plus one current-time cursor.
- Single click must not move the camera; double click remains the explicit focus action.
- No new Presence, source, Claim, Relation, historical coordinate, route or Region geometry is permitted.

## 4. Acceptance evidence

The implementation PR is acceptable only when all of the following are attached to or reproducible from the exact PR head:

1. ARTEMIS Core Check, Globe Repository Boundary Gate and Geospatial Assets Contract Gate pass.
2. Automated behavior checks cover chronological ordering, Range/Scrub filtering, marker/timeline synchronized emphasis, popup-to-drawer cleanup, language switching and URL restoration.
3. A fail-closed assertion proves the M5 projection still contains no route geometry for unsupported transitions and the renderer adds no spatial connector layer for them.
4. Deterministic desktop, tablet and hosted-mobile evidence shows no header/control or drawer/attribution overlap, no viewport overflow and usable pointer/keyboard targets.
5. English and Russian screenshots exercise the same selected Presence and time state.
6. A manual product check answers whether the 11 Presences now read as one chronological life path without being interpreted as a documented travel route.

Automated and screenshot evidence verifies behavior and composition. It does not establish formal user value or historical truth.

## 5. Exit and stop condition

After publication, record exactly one result:

- `PROCEED_TO_GATE_D_REVIEW` — the life path is legible, route meaning remains honest and all seven corrections meet acceptance evidence;
- `ITERATE` — one material defect remains and can be corrected without widening this scope;
- `NARROW` — relational legibility cannot be made clear within the current whole-life composition without reducing presentation scope;
- `STOP` — the Globe/Temporal Map direction is no longer viable for this product question.

Stop the implementation and return to a decision if any proposed fix requires route invention, new historical content, a second state model, backend/storage work, a framework rewrite or scope outside the seven findings.

## 6. Non-goals

- historical route reconstruction or map connectors between unknown gaps;
- new Leonardo data, sources, Places, Relations or context layers;
- reopening PR #394 or reusing its pre-M5 implementation as authority;
- Airtable writes, Export Airtable CI repair or Progressive Refinement changes;
- backend, persistence, sharing, AI, UGC or framework work;
- formal participant-wave validation;
- broad visual redesign.

## 7. Next action

After this decision PR merges, open one implementation PR under issue `#355` for this exact package. Export Airtable CI remains a separate technical maintenance PR and must not share the product branch or diff.
