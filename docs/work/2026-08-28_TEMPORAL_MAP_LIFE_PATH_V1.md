# ARTEMIS — Temporal Map / Leonardo Life Path v1.1

## Status

- Type: active Gate D product interaction contract.
- Updated: 2026-08-29.
- Owner: issue `#355`.
- Implemented sequence: PR `#395` established the calendar life-path loop; first published manual check recorded `ITERATE`; PR `#396` implemented and published the bounded feedback correction.
- Current lifecycle: Gate C remains `FREEZE`; Gate D remains `OPEN / IN PROGRESS`; a fresh user check of the published #396 interface is the next product step.
- Lifecycle effect: this contract does not promote any historical Claim, close Gate D, open Gate E or authorize a new product/data branch.

## 1. Product loop

The default experience answers one sequence of questions:

`object → time → path → place → information`

Leonardo is the selected object. Map and timeline are synchronized controls over one Explorer State:

- `Range` selects a calendar interval and shows every documented Presence whose temporal extent overlaps that interval;
- `Scrub` keeps a selected build origin and one current-time cursor, accumulating documented Presences as the cursor moves forward;
- selecting a visible Presence opens concise place/date/activity information;
- source, locator and uncertainty remain available under progressive disclosure.

The timeline is a calendar scale, not an ordinal list of stops. The current bounded 1502 corpus may use day/month precision only where source precision permits it. Future whole-life coverage should begin at a coarser honest scale and refine without requiring a new interaction model.

## 2. Current interaction specification

The published PR `#396` interaction is the current specification:

### Range

- one full-width bottom calendar track;
- two handles: start and end;
- temporal overlap determines visible Presences;
- URL state uses stable calendar values and Presence identity;
- Range represents an interval, not an accumulated path mode.

### Scrub

- one full-width bottom calendar track;
- one current-time cursor;
- a separate `Build from` / origin value establishes where accumulation begins;
- visible Presences accumulate from that origin through the current cursor;
- Scrub does not become a disguised two-ended range.

### Selection and detail

- timeline, map, selected Presence and URL share one Explorer State;
- one marker click selects the Presence and opens a compact map popup;
- a single click must not move the camera;
- explicit `Open details` / further action may open the right detail drawer;
- double-click may explicitly focus/zoom the selected place;
- selection state and camera state remain separate concepts.

### Visual hierarchy

- the timeline is the primary time-navigation instrument and remains full-width at the bottom;
- concise object/place meaning comes before diagnostic/source detail;
- sources and uncertainty use progressive disclosure rather than occupying the main canvas by default;
- advanced layer combinations and renderer diagnostics may remain underlying evidence, not default primary controls.

## 3. Canonical model boundary

`Trajectory` is the single semantic authority for the ordered life path. It binds `subject_ref` and contains ordered `presence`, `movement` or `inferred_gap` segments. Presentation configuration may select existing segments and supply stable UI identities, but it cannot create a second path model.

`Range` and `Scrub` are interaction modes over the same temporal/Trajectory semantics. They are not separate domain entities and do not define separate historical truth.

Time precision, spatial precision, route status and uncertainty are data. A category is a graph/query grouping over objects and relations; it is not automatically a GIS Layer or checkbox.

## 4. Line and route semantics

The life path is a primary visual object, but a connector is not automatically a historical route.

- documented `movement` geometry may be rendered only when evidence authorizes it;
- `inferred_gap` keeps `route_geometry=null` and `route_status=unknown_route`;
- the UI may derive a thin dashed connector between two visible Presence anchors solely to express chronology;
- that connector is presentation-only, has no World Model identity and must be distinguishable from historical route geometry;
- smooth interpolation, shortest-path drawing or visually plausible roads must not silently become historical assertions.

Future refinement may add intermediate Presences or authorized movement geometry while preserving stable identities, earlier evidence and uncertainty history.

## 5. Current bounded corpus

The repository currently closes four source-bound Romagna Presences to canonical Event, Trajectory, Claim, Evidence, Source and Uncertainty records:

- Rimini — 1502-08-08;
- Cesena — 1502-08-10;
- Cesenatico — 1502-09-06;
- Imola — source-native autumn 1502 range.

They are an **interaction scaffold**, not Leonardo's complete life path.

Their point coordinates are present-day named-settlement reference anchors. Exact historical positions, duration at each place and inter-place travel routes remain unknown where unsupported.

The current calendar contour covers the bounded 1502 material. A month-precision Presence overlaps the relevant source-supported interval; runtime/UI must not invent a more exact day.

No change to this interaction contract authorizes additional Leonardo data by itself.

## 6. Implemented evidence

### PR #395 — initial calendar loop

Implemented:

- calendar-based `Range` and `Scrub`;
- canonical Presence/Trajectory bindings;
- interactive map/sequence Presence selection;
- URL-restorable calendar/Presence state;
- chronology-only dashed connectors with unknown route geometry preserved;
- the four-Presence Romagna interaction scaffold.

### First published check — `ITERATE`

The first manual check of #395 found:

- Range and Scrub appeared too similar;
- timeline hierarchy was too weak;
- selected-place information was too persistent/heavy;
- single-click camera movement was too aggressive.

This was recorded as `ITERATE` for the same loop, not as final product validation.

### PR #396 — implemented feedback correction

Implemented and published:

- full-width bottom timeline with primary visual weight;
- structurally distinct two-handle Range and single-current-time Scrub;
- popup-first Presence selection;
- optional right detail drawer;
- no camera movement on single click;
- explicit double-click focus;
- preserved shared Explorer State and URL restoration;
- preserved frozen Gate C bytes, draft/rejected historical Claims and unknown-route semantics.

## 7. Acceptance for the current published interaction

The #396 interaction remains acceptable only if:

- Range and Scrub visibly produce their distinct temporal behaviors over the same canonical Presence set;
- an interval with no overlapping Presence produces an honest empty state;
- every visible marker is pointer- and keyboard-operable;
- one marker click selects/open the compact popup without moving the camera;
- explicit further action opens the detail drawer;
- only explicit focus/double-click changes camera focus;
- URL state stores calendar values and stable Presence identity rather than stop-array indexes;
- `Trajectory.subject_ref` resolves to Leonardo and presentation bindings close to its canonical segments;
- all unknown gaps retain null route geometry while dashed connectors remain chronology-only;
- source/locator/uncertainty are available without becoming the primary visual surface;
- frozen Gate C historical evidence remains unchanged/non-promoted;
- current Core and repository-boundary checks remain green.

## 8. Next product action

The **only immediate next product action** is a fresh user check of the published PR `#396` interface.

Observe whether the user can:

1. distinguish `Range` from `Scrub`;
2. understand the timeline as the primary time control;
3. understand why the visible Presence/path state changes as time changes;
4. use Scrub as accumulation from a chosen origin rather than as another range;
5. select a Presence without unexpected camera movement;
6. retrieve concise place/date/activity meaning and reach source/uncertainty details when needed;
7. understand that dashed connectors show chronology, not a known historical route.

After that check record exactly one result:

- `ITERATE` — improve the same loop;
- `NARROW` — reduce content or interaction scope;
- `STOP/RETHINK` — stop this Globe/Temporal Map approach and revisit the product hypothesis.

Implementation completion, successful CI and public R&D availability are not user-value validation.

## 9. Possible next branch — not authorized yet

Only a supported continuing decision may open **at most one** evidence-backed next branch.

Possible future branches include:

- a separate source-aware major-life Presence package with roughly 6–10 coarse anchors across 1452–1519;
- one measured local/global context or thematic-layer increment;
- curation/editorial storage;
- persistence/sharing;
- a measured renderer/provider improvement.

No candidate branch is current scope merely because it is compatible with the ARTEMIS North Star.

If a broader Leonardo package is later opened, it should use a coarse honest time scale first and refine toward months, days, roads or paths only when stronger evidence changes material understanding. The Roman Empire or other temporal polygon/state examples remain later universality tests and do not precede the current Leonardo user check.

## 10. Final rule

The Temporal Map interface must remain a projection/control surface over the shared spatial-temporal model:

`World Model → Explorer State → Temporal/Spatial Render Projection → Globe + Timeline`

UI convenience must not create a second path model, invent route/time precision, collapse selection into camera movement or turn future product hypotheses into current implementation scope.