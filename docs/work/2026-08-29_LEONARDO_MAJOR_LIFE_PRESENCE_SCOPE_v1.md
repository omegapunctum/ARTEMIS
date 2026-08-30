# ARTEMIS — Leonardo Major-Life Presence Scope v1

## Status

- Type: active Gate D bounded data-branch contract.
- Date opened: 2026-08-29.
- Owner: issue `#355`.
- Parent decision: `docs/work/2026-08-29_GATE_D_POST_396_USER_CHECK_v1.md` / `ITERATE`.
- Lifecycle: the only active next branch after the published #396 user check.
- Current stage: source discovery, candidate selection and review design; no runtime promotion.

## 1. Product question

Can the accepted #396 Temporal Map loop communicate Leonardo's life as a coherent coarse trajectory when it is supplied with a small, source-aware whole-life package rather than only four Romagna Presences from 1502?

The branch tests the same interaction model. It does not redesign the timeline, add new default layers or build infrastructure.

## 2. Bounded content scope

Prepare a candidate package with:

- one Person: Leonardo da Vinci;
- one canonical Trajectory authority;
- roughly **6–10 major-life Presence anchors** spanning **1452–1519**;
- places where Leonardo lived, worked or spent historically important time, selected by explicit significance criteria;
- coarse year/range precision by default, with finer source-native values retained only where already supported and materially useful;
- explicit chronological gaps between supported Presences;
- source, locator, uncertainty and corpus-coverage closure for every material assertion.

The selection must begin from the whole life and move from general to particular. It is not an attempt to reconstruct every trip, street, road, day or intermediate stop.

The existing four 1502 Romagna Presences remain preserved as the current interaction scaffold. Candidate review must decide whether they appear as individual primary anchors, a bounded detail cluster or later refinement; their existence does not automatically consume four of the 6–10 whole-life slots.

## 3. Selection criteria

A candidate Presence is eligible only when it materially contributes to at least one of:

1. whole-life temporal coverage;
2. a major change of residence, patronage, work or life phase;
3. a location/period necessary to understand the coarse trajectory;
4. a later refinement seam that can accept more detailed Presences without changing object identity.

Selection must avoid both exhaustive biography and arbitrary evenly spaced dates. Importance is justified in a Claim and source evidence, not inferred from visual convenience.

## 4. Required semantic package

Before runtime inclusion, the candidate package must define and close:

- stable semantic IDs for Person, Trajectory, Presence segments and supporting objects;
- source-native temporal tokens plus normalized bounds/precision;
- Place identity separated from any modern reference anchor geometry;
- `route_geometry=null` and `route_status=unknown_route` for unsupported transitions;
- atomic Claims for identity, time, place and selection significance;
- EvidenceLinks with reproducible locators;
- Source identity, rights and provenance;
- Uncertainty records for material temporal, spatial, attribution and coverage limits;
- a coverage manifest stating inclusion rationale, known exclusions and density limits;
- recorded curation and review cost.

Present-day settlement coordinates may be used only as visibly qualified reference anchors. They do not establish Leonardo's exact historical position.

## 5. Progressive-refinement rule

The package must support future refinement without changing the accepted interaction model:

- later evidence may narrow time or place;
- intermediate Presences may be inserted while stable parent identities remain traceable;
- documented movement geometry may replace an unknown gap only through new source-bound evidence and review;
- earlier evidence and uncertainty history are preserved;
- a smoother visual line never becomes permission to invent a path.

## 6. Work stages

### Stage A — Candidate manifest [active]

- identify candidate anchors and sources;
- record inclusion/exclusion rationale;
- record source-native time/place precision;
- identify evidence, rights and uncertainty gaps;
- estimate curation/review cost.

### Stage B — Frozen review package [not started]

- freeze the bounded candidate revision;
- validate reference closure and no-invented-geometry rules;
- run independent semantic/content and validator-integrity review if the package contract requires promotion;
- record unresolved critical/material findings and a branch decision.

### Stage C — Runtime increment [not authorized]

Runtime integration requires a separate reviewed decision after Stage B. It must reuse the existing World Model → Explorer State → Render Projection path and preserve #396 interaction behavior.

## 7. Acceptance for Stage A

Stage A is complete only when:

- the candidate count is within 6–10 or an explicit narrowing rationale is recorded;
- the candidate set covers 1452–1519 at a deliberately coarse and honest level;
- every candidate has a clear selection rationale and at least one identified source path;
- material Claims, source locators and uncertainties are mapped, even if some remain candidate/draft;
- all unsupported transitions remain unknown-route gaps with null geometry;
- current four-Presence Gate C evidence remains unchanged;
- no historical write is made to Airtable or another non-authoritative store;
- no runtime/public capability claim is introduced;
- the next decision is exactly one of `FREEZE FOR REVIEW`, `NARROW`, or `STOP` for this package.

## 8. Non-goals

- exact birth-to-death travel reconstruction;
- road-, trail-, day- or hour-level paths;
- invented duration at a place;
- default local/global context layers;
- documented Relation predicates while #331 is deferred;
- Airtable import or editorial-storage activation;
- backend, persistence, sharing, AI, UGC or framework work;
- visual polish unrelated to a direct blocker;
- automatic runtime integration.

## 9. Final rule

This branch adds breadth of evidence, not breadth of architecture. It succeeds only if a small whole-life package can be reviewed and later projected through the existing Temporal Map foundation without fabricated precision or a new engine.
