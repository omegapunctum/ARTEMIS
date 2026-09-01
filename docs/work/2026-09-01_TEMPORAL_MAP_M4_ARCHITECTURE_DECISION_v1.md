# ARTEMIS — Temporal Map M4 architecture decision v1

## Status

- Type: completed architecture decision record.
- Date: 2026-09-01.
- Parent contour: issue `#355`.
- Inputs: completed M2 through PR `#401` and completed M3 through PR `#403`.
- Entry authorization: `PROCEED_TO_M4` through PR `#404`.
- Decision: `ADOPT`.
- Runtime effect: none.
- Next implementation branch: not opened.

## 1. Decision

ARTEMIS adopts the **source-federated semantic direction**.

Adoption means that bounded source inputs may enter ARTEMIS through source-specific reviewed adapters or curated intake packages, but their normalized output must use one canonical semantic path:

`source snapshot/intake → Claim + EvidenceLink + Source + Uncertainty → World Model → Explorer State → Render Projection`

Provider identity, source-native locator/revision, rights, temporal and spatial precision, uncertainty and material agreement/challenge/refinement semantics must remain recoverable after normalization. No adapter may become a second ontology or silently merge competing Claims.

## 2. Why `ADOPT`

M2 established that one pinned real external structured fact can pass through the existing semantic and Globe projection path without invented time, place or route precision.

M3 established that two publisher identities can attach to the same bounded Presence while preserving:

- exact temporal agreement;
- spatial-granularity refinement rather than false conflict or false strengthening;
- separate Claim, EvidenceLink and Source identities;
- unequal revision and provenance strength;
- explicit uncertainty in the render projection;
- honest separation of two M3 inputs from inherited Gate D sources.

This evidence is sufficient to adopt the semantic direction because it works inside the existing World Model and renderer-neutral projection boundary. It does not require a competing data core or a speculative platform rewrite.

## 3. Alternatives not selected

### `NARROW`

Not selected. Restricting source-aware comparison permanently to manually curated packages would make a temporary operational constraint into an architectural limitation. Curated packages remain the current safe intake method, but the semantic boundary should also support later source-specific adapters when evidence justifies them.

### `REJECT`

Not selected. M2 and M3 did not reveal source collapse, incompatible semantics or a need to abandon the direction. Rejection would also conflict with the accepted ARTEMIS Claim → EvidenceLink → Source foundation without a demonstrated architectural failure.

## 4. What `ADOPT` does not mean

This decision does not authorize:

- live provider queries from the public Leonardo runtime;
- a generic federation, provider registry or reconciliation framework;
- automatic Claim merging or automatic conflict resolution;
- production ingestion, editorial storage, queues, caching or synchronization services;
- a database or backend migration;
- publication of the M2/M3 proof data or the PR #400 candidate package;
- a third provider, another Presence or another product branch;
- treating green technical checks as public user-value evidence.

The current safe implementation remains deterministic, reviewed and package-bound. `ADOPT` is an architecture direction, not a capability claim.

## 5. Evidence limitations

- M3 proves independent publisher identities, not independent upstream historical evidence.
- The proof covers agreement and granularity refinement, not a material hard-conflict case.
- The institutional source has no published immutable page revision.
- The second source is a reviewed snapshot adapter, not a production live integration.
- Operational cost, refresh behavior, provider failure and broad corpus scaling remain unmeasured.
- No public user-value gain from multi-source display has yet been demonstrated.

These limitations constrain later implementation; they do not invalidate the adopted semantic direction.

## 6. Future implementation triggers

Generic federation or shared ingestion infrastructure may be reconsidered only when bounded implementation evidence demonstrates at least one material need such as:

- repeated source-specific adapter logic that cannot remain small and reviewable;
- a real hard-conflict case requiring shared reconciliation behavior;
- measured refresh, reliability, storage or query requirements that static reviewed packages cannot satisfy;
- a user-facing scenario whose value depends on live or broader multi-source access.

Until then, build the smallest source-specific or curated package compatible with the adopted semantic boundary.

## 7. Post-M4 boundary

M4 is complete with `ADOPT`, but this record opens no implementation branch. A later decision must name exactly one bounded question, authorized artifact scope, evidence requirement and exit condition before data, runtime or infrastructure changes begin.

Gate D and formal user-value validation remain open. The public Leonardo Life Path remains unchanged.
