# ARTEMIS — Leonardo World Slice Scope v1

## Status

- Type: active Gate C curation decision.
- Date: 2026-08-09.
- Parent: issue `#355`.
- Delivery issue: `#332`.
- State: `SCOPE_FROZEN / CURATION IN PROGRESS`.
- Public capability change: none.

## 1. Decision

The first real Globe MVP World Slice is narrowed to an analytical 1502–1504 window around Leonardo's documented work contexts in central Italy.

This is intentionally smaller than a 1452–1519 biography. It is large enough to exercise Event, State, Process, Trajectory, temporally versioned Region, evidence, uncertainty, local/global simultaneity and 2D/Globe parity, while remaining small enough for claim-level review.

Canonical machine-readable scope: `fixtures/world_slices/leonardo_1502_1504/v1/selection_manifest.json`.

## 2. Selected review story

The eventual review experience should let a user move between:

1. Leonardo's institutional-catalogue-supported appointment/work context in 1502;
2. a documented Imola presence context;
3. an explicit unknown-route gap;
4. the source-bound Florence commission/work context in 1503–1504;
5. analytical map-coverage Region versions that remain visibly reconstructed;
6. one sparse simultaneous world context with no implied Relation.

The slice is not a narrative assertion that these objects caused or influenced each other.

## 3. Source and rights decision

Initial candidates use curated institutional sources:

- Royal Collection Trust collection records for the Imola and southern Tuscany maps;
- Comune di Imola Musei Civici for the Imola visit and local political-context candidates;
- National Gallery scholarly catalogue notes for the Battle of Anghiari commission;
- Getty TGN controlled vocabulary for attributed approximate place reference points;
- The Metropolitan Museum of Art chronology for a sparse Safavid context candidate.

The package stores URLs, locators, intended Claim scope and rights policy. It does not copy RCT images. Live pages remain candidate evidence until rights-compliant immutable locator evidence or stable bibliographic locators are frozen.

## 4. Geometry and trajectory decision

- No historical polygon is included at scope freeze.
- No line connects Imola and Florence.
- The trajectory carries an `inferred_gap` with `unknown_route` and `geometry=null`.
- Getty TGN coordinates are approximate reference points only.
- The two Region candidates model changing analytical document coverage, not political control.
- Region geometries remain `pending_digitization_review` until method, CRS/control points, rights, alternatives and review are recorded.

## 5. Relation decision

Issue #331 remains paused.

The slice may later compute `derived_co_presence` from reviewed extents. It may not store possible encounter, documented encounter, interaction, influence or causal predicates. A work/service `State` is not rewritten as a Relation.

## 6. Coverage and cost

The package explicitly records:

- incomplete historical geometry;
- the unknown route;
- live-page locator risk;
- absent independent reviews;
- sparse global context;
- the prohibition on documented Relations.

The cost log exists now, but unknown durations remain `null`. Before READY, actual curation and review minutes must be recorded; estimates cannot be substituted for measurement.

## 7. Exit

Scope freeze exits when the candidates become a versioned real World Model package with:

- atomic Claims and EvidenceLinks;
- reproducible locators and explicit evidence states;
- Uncertainty and coverage bindings;
- reviewed place/Region/trajectory projection semantics;
- deterministic 2D/Globe projection and parity evidence;
- two independent reviews with no unresolved critical finding;
- measured preparation and review cost.

Until then, the package remains non-public and cannot support a historical capability claim.
