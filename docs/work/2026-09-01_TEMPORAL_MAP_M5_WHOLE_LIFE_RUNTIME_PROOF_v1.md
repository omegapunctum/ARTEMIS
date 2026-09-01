# ARTEMIS — Temporal Map M5 whole-life runtime proof v1

## Status

- Type: bounded runtime-proof implementation.
- Date: 2026-09-01.
- Parent contour: issue `#355`.
- Architecture entry: M4 `ADOPT` through PR `#405`.
- Historical input: reviewed PR `#400` major-life package plus its frozen Romagna 1502 reference.
- Coverage: `1452–1519`.
- Runtime scope: existing Leonardo Temporal Map only.
- Publication status: R&D proof; not canonical public data publication.
- Manual exit decision: pending `ITERATE`, `NARROW` or `STOP`.

## 1. Question

Does the existing ARTEMIS Temporal Map remain understandable and useful when it must present Leonardo's whole life at deliberately coarse, source-bound resolution rather than only the four-point Romagna 1502 segment?

M5 tests product behavior, not a complete itinerary and not a new data architecture.

## 2. Authorized composition

M5 composes exactly eleven reviewed Presence anchors:

- seven major-life Presence candidates from PR `#400`;
- four frozen Romagna 1502 Presences referenced by that package.

The seven source-package Place and Presence geometries remain `null`. Five separate CC0 Wikidata P625 values are used only as present-day map reference points for Vinci, Florence, Milan, Cortile del Belvedere and Clos Lucé. Together with the four existing Romagna references, the map displays nine unique places. Repeated Florence and Milan Presence markers use a small screen-space offset; their source coordinates are not changed.

## 3. Product contract under test

- The bottom, full-width timeline remains the primary control.
- Six presentation-only major periods provide the first progressive-refinement layer.
- `Range` uses two year handles and includes every Presence whose source extent overlaps the selected interval.
- `Scrub` uses one chosen build origin and one current-year cursor, progressively revealing Presence anchors reached by that year.
- Single click opens a compact popup and does not move the camera.
- A second explicit details action opens the right drawer.
- Double click is the only Presence action that focuses the map.
- Long residence extents do not assert continuous daily body position.
- Missing Presence data never means historical absence.

## 4. Route and geometry boundary

All ten inter-Presence transitions remain `unknown_route` with `route_geometry=null`. M5 renders no chronological connector and no route line. It does not interpolate roads, trails, curves or movement between anchors.

The M5 map points are contextual references only. They are not exact historical positions, reconstructed footprints or evidence that Leonardo occupied the displayed coordinate.

## 5. Automated acceptance

The generated proof must fail closed unless:

- the PR `#400` package remains `CANDIDATE_SOURCE_AUDITED` with `FREEZE_FOR_REVIEW`;
- the package's own `runtime_authorized` flag remains `false`;
- exactly seven new and four referenced Presence anchors compose to eleven;
- the time axis is exactly 68 years, `1452` through `1519`;
- exactly six macro periods are present;
- all ten transitions remain geometry-free and no connector is authorized;
- the five added map anchors resolve only to the five reviewed Place identities and retain a non-historical semantic role;
- the existing Range, Scrub, popup, drawer, URL-state and double-click contracts remain covered by tests.

## 6. Manual check and exit

After PR review and deployment, the user check should answer:

1. Can a person understand the whole-life outline before opening details?
2. Does `Range` clearly answer “what reviewed Presence anchors overlap these years?”
3. Does `Scrub` clearly build the life path from the selected starting year to the current year?
4. Can every one of the eleven Presence anchors be selected and understood without involuntary camera jumps?
5. Are major periods, exact Presence anchors, uncertainties and unknown routes visually distinct without excessive text noise?

Record exactly one result:

- `ITERATE` — the whole-life product direction works, but a bounded UX/data refinement is justified;
- `NARROW` — the proof is useful only at a smaller coverage, detail or interaction scope;
- `STOP` — the whole-life Temporal Map does not currently produce sufficient product value.

No post-M5 implementation branch is opened automatically.

## 7. Non-goals

M5 does not authorize live provider access, generic federation, ingestion, backend/storage, new historical claims, new Presence discovery, exact routes, automatic conflict resolution, contextual layers or canonical public promotion of PR `#400`.
