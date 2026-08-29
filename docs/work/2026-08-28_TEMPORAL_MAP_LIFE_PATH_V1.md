# ARTEMIS — Temporal Map / Leonardo Life Path v1

## Status

- Type: active Gate D product increment.
- Date: 2026-08-28.
- Owner: issue `#355`.
- Decision: revise PR `#395` before merge around one universal object/time/path interaction.
- Lifecycle effect: none; Gate D remains `IN_PROGRESS` and no historical Claim is promoted.

## 1. Product loop

The default experience answers one sequence of questions:

`object → time → path → place → information`

Leonardo is the selected object. The map and timeline are two controls over the same Explorer State:

- `Range` selects a calendar interval and shows every documented presence whose temporal extent overlaps it;
- `Scrub` starts at a selected calendar point and accumulates documented presences as the current-time cursor moves forward;
- selecting a visible marker or list item opens one compact place/date/activity card;
- sources, locators and uncertainty remain available under progressive disclosure.

The timeline is a calendar scale, not an ordinal list of stops. Whole-life coverage begins at year
granularity; a bounded corpus may use month or day granularity when its source precision supports it.
Finer future precision must not require a new interaction model.

After the first published user check, the two modes must also be visually distinct:

- `Range` uses one interval track with two handles and URL keys `start/end`;
- `Scrub` uses one current-time cursor, a secondary `Build from` value and URL keys `from/at`;
- the timeline is a full-width bottom dock because time is a primary navigation instrument, not inspector metadata.

## 2. Canonical model boundary

`Trajectory` is the single semantic authority for the ordered life path. It binds `subject_ref` and
contains ordered `presence`, `movement` or `inferred_gap` segments. Presentation configuration may
select existing segments and supply stable UI identities, but it cannot create a second path model.

Time precision, spatial precision, route status and uncertainty are data. A category is a graph
filter over objects and relations; it is not automatically a GIS layer or checkbox.

## 3. Line semantics

The life path is the primary visual object, but a connector is not automatically a historical route.

- documented `movement` geometry may be rendered only when evidence authorizes it;
- `inferred_gap` keeps `route_geometry=null` and `route_status=unknown_route`;
- the UI may derive a thin dashed connector between two visible presence anchors solely to express chronology;
- that connector is presentation-only, has no World Model identity and is explicitly labelled as not historical route geometry.

Future refinement may add intermediate presences or authorized movement geometry while preserving
stable identities, earlier evidence and uncertainty history.

## 4. Current PR #395 boundary

The repository currently closes four source-bound Romagna presences to canonical Event,
Trajectory, Claim, Evidence, Source and Uncertainty records: Rimini, Cesena, Cesenatico and Imola in
1502. They are an interaction scaffold, not Leonardo's complete life path. Their point coordinates
are present-day named-settlement references; exact historical positions and duration remain unknown.

The current daily calendar scale covers `1502-08-08` through `1502-11-30`. A month-precision
presence overlaps every calendar day allowed by its source interval; the runtime must not silently
invent a more exact day.

## 5. Acceptance for PR #395

- `Range` and `Scrub` visibly change the same presence set on timeline, map and URL;
- an interval with no overlapping presence produces an honest empty state;
- every visible marker is pointer- and keyboard-operable and selects the matching compact card;
- one marker click opens a compact map popup without moving the camera;
- a second click or explicit `Open details` action opens the right detail drawer;
- only a marker double-click focuses/zooms the map;
- URL state stores calendar values and stable `presence` identity, not stop-array indexes;
- `Trajectory.subject_ref` resolves to Leonardo and presentation bindings close to its canonical segments;
- all three gaps retain null route geometry while dashed connectors identify chronology only;
- frozen Gate C files remain byte-preserved, non-public and non-promotable;
- Core, repository-boundary and browser checks remain green.

## 6. Next bounded data increment

After the interaction scaffold is reviewed, prepare a separate source-aware major-life-presence
package with roughly 6–10 coarse anchors across 1452–1519. Candidate research scope includes Vinci,
Florence, Milan, the 1502 Romagna stage, Mantua, Venice, Rome and Amboise; no candidate enters the
runtime until its identity, temporal extent, place anchor, evidence and uncertainty close.

This package should use a year-scale timeline first and refine toward months, days, roads or paths
only when new evidence changes material understanding. The Roman Empire is a later universality test
for temporal polygon states versus point/path objects; it does not precede Leonardo validation.

## 7. Decision after review

Observe one user completing the loop and record exactly one result: `ITERATE`, `NARROW` or
`STOP/RETHINK`. Only an evidence-backed result may open the next product or infrastructure branch.
