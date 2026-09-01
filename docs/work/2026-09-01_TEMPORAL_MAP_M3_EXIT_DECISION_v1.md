# ARTEMIS — Temporal Map M3 exit decision v1

## Status

- Type: completed decision record.
- Date: 2026-09-01.
- Parent contour: issue `#355`.
- Evidence implementation: PR `#403` (merged).
- Decision: `PROCEED_TO_M4`.
- Runtime effect: none; public Leonardo Life Path and its data remain unchanged.

## 1. Decision

M3 is complete. ARTEMIS proceeds to **M4 — Architecture decision**.

M4 is a decision-only stage. It must record exactly one outcome:

- `ADOPT` — adopt the source-federated semantic direction, still through bounded incremental packages rather than a general platform build;
- `NARROW` — retain source-aware comparison only for curated packages and postpone general federation;
- `REJECT` — do not pursue a federated-source architecture and retain curated static source packages.

This decision opens evaluation of the architecture direction. It does not select an M4 outcome and does not authorize implementation expansion.

## 2. Evidence used

PR `#403` completed one two-provider/one-Presence proof:

- Wikidata and Museo Leonardiano remain distinct publisher identities;
- both sources agree on Leonardo's birth date, `1452-04-15`;
- the spatial difference is represented as `granularity_refinement_not_direct_conflict`;
- Wikidata's Anchiano statement and the museum's traditional-attribution qualification are not collapsed into a stronger exact-place claim;
- unequal revision, locator and provenance strength remains visible;
- two M3 inputs are counted separately from 11 inherited Gate D sources;
- Claim, EvidenceLink, Source and Uncertainty references survive the existing World Model → Explorer State → Render Projection path;
- no new Event, route, exact historical coordinate, map point or public runtime data was created;
- the exact PR head passed the required Core, Geospatial and Globe Boundary checks.

## 3. Why `PROCEED_TO_M4`

The bounded proof demonstrates that ARTEMIS can carry more than one source identity for the same Presence, express agreement and spatial refinement without inventing geometry, and keep material uncertainty visible through projection. That is sufficient evidence to decide whether this direction belongs in the target architecture.

`NARROW_M3` is not selected because final review found no material defect that requires another reduced M3 implementation. `STOP_M3` is not selected because the two-source path works within the existing semantic core without source collapse or premature infrastructure.

## 4. Limitations carried into M4

- Publisher identities are independent; upstream historical or scholarly dependence remains unknown.
- M3 does not prove historiographically independent corroboration.
- The proof covers agreement plus granularity refinement, not a hard contradiction case.
- Museo Leonardiano does not publish an immutable page revision.
- M3 does not prove public user value or justify publishing the proof data.
- M3 does not prove production ingestion, storage, editorial workflow or generic reconciliation infrastructure.
- One Presence and two providers cannot establish the operational cost or value of broad federation.

M4 must treat these as decision constraints, not implementation TODOs to complete automatically.

## 5. M4 boundary

Authorized work is limited to comparing the M2 and M3 evidence and recording one architecture outcome: `ADOPT`, `NARROW` or `REJECT`.

Before that decision, do not:

- add a third provider or a second Presence;
- publish M2/M3 or PR #400 candidate data in the Leonardo runtime;
- build generic provider adapters, federation, reconciliation, ingestion or storage infrastructure;
- open context/layers, persistence/sharing or another product branch;
- reinterpret green technical checks as formal user-value evidence.

The M3 proof artifact retains `m4_authorized=false`: implementation evidence cannot authorize its own successor. This separate reviewed lifecycle decision is the authority to enter the bounded M4 decision stage.

## 6. Recorded M4 outcome

M4 subsequently recorded `ADOPT` in `2026-09-01_TEMPORAL_MAP_M4_ARCHITECTURE_DECISION_v1.md`. Adoption applies to the source-federated semantic direction only; no implementation branch, live federation or public data expansion is opened automatically.
