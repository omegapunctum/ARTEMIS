# ARTEMIS — Temporal Map M2 exit decision v1

## Status

- Type: completed milestone decision record.
- Date: 2026-09-01.
- Parent contour: issue `#355`.
- Evidence PR: `#401`.
- Decision: `PROCEED_TO_M3`.
- Runtime effect: none; public Leonardo Life Path remains unchanged.
- Architecture effect: none; M4 remains closed.

## 1. Decision

Decision: `PROCEED_TO_M3`.

M2 demonstrated that one real external structured fact can pass through the existing ARTEMIS World Model → Explorer State → Render Projection → Globe path while retaining source identity, rights, temporal/spatial precision and explicit uncertainty.

This is sufficient to test multi-source behavior. It is not evidence that a federated architecture should yet be adopted.

The immutable PR #401 proof output intentionally retains `m3_authorized=false`: an evidence artifact cannot authorize its own successor. This separate decision record is the lifecycle authorization to begin bounded M3 work.

## 2. Evidence

- PR `#401` merged as `a3ce916458e1bbd96a25df2fd6221215e1a0e4ac`.
- One provider: Wikidata.
- One normalized fact: Leonardo birth Presence using pinned `Q762 / P569`, `Q762 / P19` and linked `Q154184 / P625` statements.
- Exact revision URLs, raw-response digests, statement IDs and reference hashes fail closed.
- CC0 rights and source locators survive normalization.
- The coordinate remains a present-day named-settlement reference; exact historical position, house, duration and route remain unknown.
- The existing Globe adapter renders the proof without public runtime promotion.
- Required Core, Geospatial and Globe Boundary checks passed on the reviewed PR head.

## 3. Why not NARROW or STOP

`NARROW_M2` is not selected because review found and corrected the material identity and inherited-source-count boundaries before merge. The final proof remains one provider and one normalized Presence.

`STOP_M2` is not selected because the merged implementation reproduces the bounded fact, preserves the reviewed semantics and fails closed on controlled source drift.

## 4. What M2 does not prove

M2 does not prove:

- corroboration between independent providers;
- handling of source disagreement or unequal precision;
- public usefulness of the additional Presence;
- safe integration of the PR #400 whole-life candidate package;
- production ingestion, persistence or editorial workflow;
- adoption of a federated-source architecture.

## 5. Authorized M3 scope

M3 is limited to:

1. the existing Leonardo birth Presence;
2. the merged Wikidata M2 source;
3. exactly one independent second provider;
4. separate Source, Claim, EvidenceLink, locator, rights and uncertainty identity for both providers;
5. explicit representation of agreement, refinement or conflict through the existing semantic/projection path.

The second provider has not yet been selected. Source selection is the first M3 task and must prefer stable revision identity, usable rights and a precise locator.

M3 does not authorize a third provider, another Presence, public runtime data, generic federation infrastructure or the M4 architecture decision.

## 6. M3 exit

Record exactly one result after review of the two-provider proof:

- `PROCEED_TO_M4` — multi-source identity and disagreement semantics are sufficient for an architecture decision;
- `NARROW_M3` — retain the same two-provider proof but reduce or correct its semantics;
- `STOP_M3` — the bounded multi-source path does not justify continuing to M4.
