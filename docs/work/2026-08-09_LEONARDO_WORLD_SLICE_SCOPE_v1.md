# ARTEMIS — Leonardo-in-Romagna World Slice Scope v1

## Status

- Type: active Gate C curation decision.
- Date: 2026-08-09.
- Parent: issue `#355`.
- Delivery issues: `#332`, `#360`.
- State: `SCOPE_FROZEN / CURATION IN PROGRESS`.
- Public capability change: none.

## 1. Decision

The first real Globe MVP World Slice is narrowed to Leonardo's source-bound Romagna contexts from **8 August through 31 December 1502**.

This supersedes the earlier 1502–1504 candidate inside the same unmerged Gate C PR. Florence and the Battle of Anghiari material are excluded from v1. The smaller boundary is better suited to folio-level review while still exercising Event, State, Process, Trajectory, changing Region, evidence, uncertainty, local/global simultaneity and 2D/Globe parity.

Canonical machine-readable scope: `fixtures/world_slices/leonardo_romagna_1502/v1/selection_manifest.json`.

## 2. Selected review story

The eventual review experience should let a user move between:

1. Leonardo's dated Rimini context on 8 August 1502;
2. the Cesena 10 August context bound to Manuscript L folio 46v; the separate wall-survey association at folios 9r–10r is rejected from the supported Gate C Claim set pending stronger evidence;
3. the 18 August letter-patent candidate bound to the complete university-press transcription at printed p. 16 n. 26;
4. the Cesenatico port context dated 6 September and bound to Manuscript L folio 66v, without conflating it with the separate perspective at folio 68r;
5. the autumn Imola map-work context represented by RCT collection items 912284 and 912686;
6. explicit unresolved movement gaps between those presence contexts;
7. a geometry-withheld Duchy of Romagna political Region with source-bound 1499/1502 transition and selected-interval states, plus explicit title-based and documented-place-only reconstruction alternatives;
8. one sparse simultaneous Safavid State;
9. one year-precision Ottoman displacement Event sourced to a Cambridge University Press article, with possible rather than exact overlap and no implied Relation.

The slice does not assert that itinerary order proves a route, or that any selected object caused or influenced another.

## 3. Source and rights decision

Initial candidates use curated institutional and scholarly sources:

- Museo Galileo's Manuscript L catalogue record for manuscript identity and 1502 engineering context;
- Gianni Volpe's university-press chronology for the dated Manuscript L folios and full letter-patent transcription;
- Visit Romagna's institutional itinerary for candidate dates, sections and folio references;
- Royal Collection Trust records 912284 and 912686 for the Imola map and street-plan sketches;
- Comune di Imola Musei Civici for the Imola consultation and political-transition context;
- Getty TGN for the attributed approximate Imola reference point and its ODC-By policy;
- The Metropolitan Museum of Art chronology for one sparse Safavid State;
- Abdurrahman Atçıl's Cambridge University Press article, printed p. 298 and note 13, for the year-precision global Event.

Visit Romagna is an institutional secondary orientation source, not a substitute for Manuscript L or the letter patent. The package contains 17 candidate objects, 10 sources, 22 atomic Claims, 38 candidate EvidenceLinks and 11 provenance-bearing Uncertainty records; every candidate object is a Claim target. The dated Rimini, Cesena and Cesenatico Claims use stable folio-level university-press locators, and the patent uses a complete critical transcription. The Imola civic-history locator supports only a broad post-1499 transition sequence, not a precise political handover date. The separate Cesena wall-survey folio Claim remains traceable but is `rejected` from the supported set because only the institutional itinerary names `9r/9v–10r`; rejection does not assert historical falsity. Draft links still derive `evidence_state=missing`; they cannot masquerade as reviewed support. No RCT, patent or manuscript image is copied or licensed by this package.

For every source, verified access, data/text use, media reuse and derived-geometry use are recorded separately. RCT image reuse and derived geometry remain prohibited without permission; Getty TGN structured data retains ODC-By attribution. No source with unresolved derived-geometry rights authorizes a polygon.

## 4. Geometry and trajectory decision

- No historical polygon is included at scope freeze.
- No line connects the selected presence contexts.
- Three trajectory gaps use `unknown_route` and `geometry=null`.
- Named places remain geometry-null except a later optional attributed Getty reference point for Imola.
- The Duchy of Romagna cannot be substituted with modern Emilia-Romagna.
- A broad post-1499 Imola transition state and a selected-interval Borgia title state expose temporal change without asserting precise handover dates or stable territorial control.
- The title-based alternative uses `scholarly_reconstruction`; the documented-place-only alternative uses `analytical_model`. Both remain `pending_digitization_review` with `geometry=null` until positive rights, method, CRS/control points, residuals and independent geometry review are recorded.

## 5. Relation decision

Issue #331 remains paused.

The slice may later compute `derived_co_presence` from reviewed extents. It may not store possible encounter, documented encounter, interaction, influence or causal predicates. A commissioned-service `State` is not rewritten as a Relation.

## 6. Coverage and cost

The package explicitly records:

- absent reviewed Romagna Region geometry;
- unknown inter-place routes;
- missing original patent call number/rights-cleared surrogate despite the closed critical-transcription locator;
- missing frozen Manuscript L facsimiles and the evidence-based rejection of the separate Cesena wall-survey folios 9r–10r Claim from the supported set;
- two independent review rounds that returned `CHANGES_REQUIRED`, with a final same-revision `READY` pair still absent;
- intentionally sparse global context limited to one State and one year-precision Event;
- the prohibition on documented Relations.

Original unmeasured duration remains `null` and is marked superseded rather than estimated. A complete replacement recuration session and every review round use measured UTC wall-clock intervals. No pending cost entry is allowed at READY.

## 7. Exit

Scope freeze exits when the candidates become a versioned real World Model package with:

- atomic Claims and EvidenceLinks;
- reproducible locators and derived evidence states;
- Uncertainty and coverage bindings;
- reviewed place/Region/trajectory projection semantics;
- deterministic 2D/Globe projection and parity evidence;
- two independent reviews with no unresolved critical or material finding;
- measured preparation and review cost.

Until then, the package remains non-public and cannot support a historical capability claim.
