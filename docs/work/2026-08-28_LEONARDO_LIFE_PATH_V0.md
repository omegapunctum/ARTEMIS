# ARTEMIS — Leonardo Life Path v0

## Status

- Type: active Gate D product increment.
- Date: 2026-08-28.
- Owner: issue `#355`.
- Decision: narrow the default Globe presentation around one understandable Leonardo trajectory loop.
- Lifecycle effect: none; Gate D remains `IN_PROGRESS` and no historical Claim is promoted.

## 1. Problem observed

The current Globe exposes renderer and semantic diagnostics before it establishes a clear user task.
The map points do not explain themselves, the timeline appears not to change the path, layer
checkboxes have no obvious outcome, and the inspector presents too much text at once.

The default experience therefore fails the immediate question: **where is Leonardo in the selected
time window, what is the next documented stop, and what is actually known about that stop?**

## 2. Product decision

The default Gate D surface becomes one bounded `Leonardo Life Path` loop:

1. the selected subject is Leonardo da Vinci;
2. `Range` shows the source-bound stops between a selected start and end;
3. `Journey` progressively reveals the accumulated stops from a selected start to the current step;
4. every visible stop is keyboard- and pointer-operable;
5. selecting a stop opens a compact place/date/activity card;
6. source, locator, uncertainty and technical identity remain available under progressive disclosure;
7. advanced layer combinations, alternative-geometry controls and renderer diagnostics leave the
   default user surface.

The current corpus supports four source-bound 1502 stops only: Rimini, Cesena, Cesenatico and
Imola. The UI uses those source-native day/month steps. It does not claim to cover Leonardo's whole
life. A later separately curated 1452–1519 anchor package may use year steps without changing this
interaction contract.

## 3. Epistemic boundary

- Stop coordinates remain present-day `named_settlement` reference anchors.
- A stop does not claim Leonardo's exact position inside the settlement.
- The sequence is chronological presentation, not documented route geometry.
- Every inter-stop movement remains `unknown_route` with `geometry=null`.
- No line connects stops on the map in v0.
- The frozen Gate C package remains byte-preserved, non-public and non-promotable.
- Claims retain their exact draft/rejected state.
- No Relation, Airtable row, backend or mutable refinement behavior is added.

## 4. Presentation projection

The build produces one deterministic `life-path.json` artifact from existing frozen object,
Claim/Evidence and place-anchor references. It may bind a stop to an existing source-dated Event and
presence segment for display, but it cannot create a new Claim, Source, route or geometry.

Each stop carries:

- stable presentation id;
- Place ref and present-day anchor coordinates;
- source-native temporal value and precision;
- existing Event and Trajectory-presence item refs;
- concise activity label derived from the existing Event label;
- explicit duration-unavailable and exact-position-unknown notes;
- route-from-previous status `unknown_route` and `geometry=null`.

Every permitted range is precomputed in the generated artifact. The browser selects a generated
view rather than inventing intermediate historical dates or geometry.

## 5. Acceptance

The increment passes when:

- the default screen presents no unexplained layer, 2D or alternative-geometry controls;
- moving either time mode visibly changes the displayed stop set;
- every displayed map marker selects the matching compact card;
- the card exposes place, source date/range, activity, duration limitation and spatial uncertainty
  before optional evidence details;
- the URL restores mode, start, end/current stop and selection;
- four stops and three unknown-route gaps remain closed to existing source/evidence/uncertainty refs;
- generated output contains no life-path line geometry;
- Core, repository-boundary and browser acceptance checks remain green.

## 6. Next data decision

After this interaction is understandable, the next separate question is whether to curate a small
source-backed `Leonardo major life anchors 1452–1519` package. That package should begin with only
the most important long-duration or historically material places and refine later without changing
stable identities or erasing earlier evidence.
