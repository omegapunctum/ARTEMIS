# ARTEMIS — Temporal Map M3 two-source proof v1

## Status

- Type: completed bounded evidence record.
- Date: 2026-09-01.
- Parent contour: issue `#355`.
- Entry decision: `PROCEED_TO_M3` through PR `#402`.
- Runtime effect: proof-only; public Leonardo Life Path is unchanged.
- Completion: PR `#403` merged.
- Recorded outcome: `PROCEED_TO_M4` through the separate M3 exit decision record.
- M4 effect: this proof does not self-authorize M4; the separate reviewed decision opens the decision-only stage.

## 1. Question

Can two publisher-independent source identities support and refine the same Leonardo Presence without collapsing provenance, hiding unequal precision or inventing geometry?

## 2. Selected sources

Provider 1 is the merged Wikidata M2 snapshot:

- `Q762 / P569` — 15 April 1452;
- `Q762 / P19` — Anchiano;
- linked `Q154184 / P625` — present-day named-settlement reference only.

Provider 2 is Museo Leonardiano di Vinci:

- `Leonardo’s places`, section `The Places of Birth and Childhood`, first paragraph;
- `Leonardo da Vinci`, timeline entry `15 April 1452`;
- publisher: Comune di Vinci — Museo Leonardiano;
- exact page revision: not published;
- factual use: citation and factual claims only;
- media reuse and geometry derivation from site media: not permitted.

The Museo provider was already indexed and source-audited in Google Drive. Its live institutional pages were rechecked on 1 September 2026 before the repository snapshot was prepared.

## 3. Comparison result

The two sources agree exactly on the date `1452-04-15`.

Their spatial statements have different granularity:

- Wikidata names Anchiano as place of birth;
- Museo Leonardiano states birth in Vinci and labels the Anchiano house as a traditional attribution.

This is recorded as `granularity_refinement_not_direct_conflict`. The proof does not convert the traditional house attribution into an exact historical coordinate. The existing Wikidata Anchiano point remains a present-day named-settlement reference and is not strengthened by the Museo source.

## 4. Independence boundary

The providers have independent publisher identities. Their upstream evidentiary dependence is unknown: both may ultimately rely on overlapping historical or scholarly material. M3 therefore does not claim statistically or historiographically independent corroboration.

This distinction is material and remains machine-readable as:

- `provider_independence = independent_publisher_identity_only`;
- `shared_upstream_evidence_unknown = true`.

## 5. Projection behavior

Both provider identities attach to one Event/Presence. The date basis contains both Claims. The Anchiano spatial basis remains bound only to the Wikidata Claim and P625 reference anchor. The Museo spatial qualification becomes a material Uncertainty visible through the existing projection source/uncertainty references.

The proof remains an overlay on the Gate D World Model. Its output therefore contains 13 Source records: two M3 inputs and 11 inherited Gate D references. The inherited records are listed separately and are explicitly not counted as M3 inputs.

No second Event, exact house, route, new map point or public runtime data is created.

## 6. Fail-closed boundary

The proof rejects drift in:

- provider and organization identity;
- retrieval date;
- page URLs and section locators;
- reviewed excerpts and their digest;
- normalized claims and their digest;
- factual/media/geometry rights policy.

The absence of an immutable page revision is preserved explicitly rather than disguised by the local reviewed excerpt.

## 7. Recorded M3 result

Final review recorded `PROCEED_TO_M4` in `2026-09-01_TEMPORAL_MAP_M3_EXIT_DECISION_v1.md`. The explicit agreement/refinement model and preserved unequal source strength are sufficient to open M4 as an architecture decision, while all proof limitations remain binding.

The generated proof retains `m4_authorized=false`. Evidence cannot authorize its own successor; the separate lifecycle decision is the authority to enter M4.
