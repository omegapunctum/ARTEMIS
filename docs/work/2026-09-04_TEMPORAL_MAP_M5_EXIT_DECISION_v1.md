# Temporal Map M5 exit decision v1

## Status

- Type: direct product-check decision record.
- Date: 2026-09-04.
- Active product issue: `#355`.
- Checkpoint: `M5 — Whole-Life Runtime Proof`.
- Published surface checked: `https://omegapunctum.github.io/ARTEMIS/globe/?mode=range&start=1452&end=1519`.
- Decision: **`ITERATE`**.
- Next implementation branch: not opened by this record.

## 1. Evidence basis

The project owner manually reviewed the published M5 on a desktop browser and supplied an annotated screenshot. The observed runtime showed the 1452–1519 Range, 11 Presence markers, six macro-period controls, a selected Clos Lucé popup and the expanded right-hand details drawer.

The direct review identified seven product findings:

1. the map points do not yet read as elements of one connected life path;
2. the compact popup remains open after `Open details` opens the right drawer;
3. markers and interface elements are visually too large;
4. the bottom timeline region is too tall;
5. the upper-left `ARTEMIS · Leonardo Life Path` block overlaps map controls;
6. the current interface needs an `EN / RU` switch;
7. the right drawer overlaps the map-attribution/status text.

These are direct product observations, not automated evidence and not claims about historical truth.

## 2. Decision

**Decision: `ITERATE`.**

The whole-life scope remains understandable enough to continue: the complete 1452–1519 extent, coarse period structure, Presence selection and details path are all visible and operable. The review does not show that the temporal coverage itself must be reduced, so `NARROW` is not selected. It also does not invalidate the Temporal Map direction, so `STOP` is not selected.

The material weakness is relational legibility: M5 displays multiple documented Presences, but the user does not yet perceive them as one life path. This is more important than cosmetic polish and must be addressed in the next bounded UX scope.

## 3. Semantic constraint on “connections”

The finding “no connections between elements” does **not** authorize invented historical routes, roads or continuous body positions. All unsupported transitions remain `unknown_route` with `route_geometry=null`.

A later UX proposal may communicate chronological order, accumulation and period membership through clearly non-route presentation semantics. Any map connector must be explicitly distinguishable from historical route geometry; a non-geometric timeline/selection treatment is preferable if a line would imply unsupported movement.

## 4. Scope implications

The next scoping decision should consider one bounded correction package covering:

- chronological/relational legibility without invented routes;
- popup → drawer state cleanup;
- reduced marker/control density;
- a shorter bottom timeline region;
- map-control/header collision removal;
- a new current-M5 `EN / RU` presentation layer rather than reopening superseded PR #394;
- attribution/status placement that remains visible beside the drawer.

This list is input to scope design, not automatic authorization to implement every item in one branch.

## 5. Exit effect

- M5 is completed with exactly one result: `ITERATE`.
- Gate D remains open; formal user value is not yet established.
- PR #406 remains a bounded public R&D proof, not a product-ready capability.
- PR #394 remains closed and superseded.
- No source, Presence, route geometry, context/layer, backend, storage or federation expansion is authorized.
- No next feature branch opens automatically.
- Export Airtable CI remains a separate technical maintenance PR and must not be mixed with the UX scope.
