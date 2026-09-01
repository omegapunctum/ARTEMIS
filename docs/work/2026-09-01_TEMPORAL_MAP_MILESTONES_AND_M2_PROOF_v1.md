# ARTEMIS — Temporal Map milestones and M2 one-source proof v1

## Status

- Type: active milestone decision and bounded implementation record.
- Date: 2026-09-01.
- Parent contour: issue `#355`.
- Current milestone: `M2 — One-source proof`.
- Runtime effect: proof-only; public Leonardo Life Path is unchanged.
- Next milestone effect: `M3` remains closed until the M2 exit decision is recorded.

## 1. Correct milestone lifecycle

| Milestone | Question | Exit evidence |
|---|---|---|
| M1 — UX checkpoint | Is the current Temporal Map interaction understandable enough to continue? | Direct check of the published #396 loop and one `ITERATE / NARROW / STOP` decision. |
| M2 — One-source proof | Can one real external structured fact pass through ARTEMIS and the existing Globe without semantic invention? | One pinned provider, one adapter, one normalized fact, provenance/rights/uncertainty closure and a Globe projection. |
| M3 — Multi-source proof | Can two or more sources corroborate, refine or conflict without losing their identities? | Explicit multi-source reconciliation semantics and visible disagreement/uncertainty behavior. |
| M4 — Architecture decision | Is the federated-source architecture adopted, narrowed or rejected? | Recorded `ADOPT / NARROW / REJECT` decision based on M2 and M3 evidence. |

M1 is complete. The direct post-#396 check recorded `ITERATE`: the interaction is good enough to continue, while remaining visual polish is not the active question.

The machine-checkable package merged through PR #400 is not M2 completion. It is a manually curated multi-source candidate package and does not demonstrate an external-source adapter feeding the current runtime path.

## 2. Drive discovery result

Google Drive contains a reviewed Wikidata coordinate-anchor record for Rimini, Cesena, Cesenatico and Imola. It establishes provenance, CC0 reuse and the rule that current coordinates are named-settlement references only.

It does not contain a complete M2 package. The existing Drive material supplies spatial anchors but no single external fact that closes Leonardo identity, time and place for this proof.

## 3. Selected M2 source and fact

Provider: Wikidata.

Pinned source entities:

- Leonardo da Vinci `Q762`, revision `2533380508`;
- Anchiano `Q154184`, revision `2504702048`.

Selected structured statements:

- `Q762 / P569` — preferred date of birth: `15 April 1452`, day precision;
- `Q762 / P19` — place of birth: `Q154184` (Anchiano);
- `Q154184 / P625` — current coordinate location for the named settlement.

This is one provider and one normalized Presence fact. Following a linked entity inside the same pinned Wikidata snapshot does not add a second source.

Rights: Wikidata structured data are reused under `CC0-1.0`.

The source excerpt also records SHA-256 digests of both exact revision-bound JSON responses, so review can distinguish the inspected provider payloads from a later hand-reconstructed equivalent.

## 4. Normalization

The adapter creates a proof-only Event and one-segment Trajectory:

`Wikidata snapshot → Claim/EvidenceLink/Source → Event + named Place + Presence segment → Explorer State → Render Projection → existing Globe adapter`

Normalized time is `1452-04-15`, day precision, proleptic Gregorian. Anchiano geometry is only a present-day named-settlement reference; exact historical position remains unknown.

## 5. Fail-closed boundaries

The proof rejects a second provider, changed pinned revisions, loss of the preferred `P569` value, an unclosed `P19` target, invalid/non-Earth `P625` coordinates and missing statement/reference identities.

The proof does not assert an exact birth position or house, residence duration, route geometry, a complete life trajectory, public runtime authorization or M3 readiness.

## 6. Repository artifacts

- `fixtures/source_proofs/leonardo_wikidata_birth/v1/source_snapshot.json` — pinned structured excerpt;
- `scripts/build_temporal_map_m2_proof.py` — fail-closed source adapter and existing projection-path runner;
- `tests/test_temporal_map_m2_proof.py` — positive Globe projection and controlled-corruption tests.

The public `leonardo_life_path_presentation.json`, frozen Romagna package and PR #400 multi-source candidate package remain unchanged.

## 7. M2 exit decision

Record exactly one result after code review and green bounded checks:

- `PROCEED_TO_M3` — the one-source path is reproducible, source-bound and rendered without invention;
- `NARROW_M2` — keep the same source/fact but reduce or correct adapter semantics;
- `STOP_M2` — the source path cannot meet the semantic/provenance/runtime boundary.

Until that decision is recorded, do not add a second source and do not make the M4 architecture decision.
