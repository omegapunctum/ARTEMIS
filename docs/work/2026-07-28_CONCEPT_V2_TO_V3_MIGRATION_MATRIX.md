# ARTEMIS — CONCEPT v2 → FOUNDATION v3 MIGRATION MATRIX

## Статус

- Тип: foundation migration/disposition record.
- Дата: 2026-07-28.
- Parent: issue `#327`.
- Scope: decisions and backlog meaning, not runtime data migration.

## 1. Decision matrix

| Concept v2 item | Foundation v3 disposition | Reason |
|---|---|---|
| Human judgment | Keep | The user remains the subject of interpretation and choice |
| Human research as only mission | Supersede | Mission is understanding a spatial-temporal world model |
| Evidence chain as core mission | Reposition | Mandatory trust layer, not product identity |
| Map/time as optional validated lenses | Supersede | Space/time are mandatory core coordinates |
| Claim as unit of evidence | Keep | Required for trustworthy model assertions |
| EvidenceLink + locator | Keep | Provenance must remain reproducible |
| Independent epistemic dimensions | Keep and extend | Add observation/inference/model assumptions |
| Relation as structured Claim | Keep | Strong relations require explicit evidence |
| Classification vs Relation vs Similarity | Keep | Prevents false historical links |
| Investigation/SliceRevision/Brief as target | Keep as optional research model | Useful outcome, not first value or whole ontology |
| Research Brief as primary outcome | Supersede | First value is contextual spatial-temporal understanding |
| Architecture Atlas as active identity | Reclassify | Thematic layer and technical baseline |
| Three architecture modules | Preserve | Reusable architecture fixtures/evidence |
| Spatial-temporal depth as future branch | Supersede | Becomes foundation |
| AI as optional future assistant | Keep and broaden contract | Future source-bound model analysis, still not Source |
| 3D/VR absent from active North Star | Add as future surfaces | Explicit direction, not release promise |
| Independent gates | Keep | One decision opens one branch |

## 2. Knowledge model

| v2 | v3 |
|---|---|
| Entity | Entity plus typed subtypes |
| Claim | Claim |
| Source | Source |
| EvidenceLink | EvidenceLink |
| Relation | RelationClaim |
| ClassificationAssertion | ClassificationAssertion |
| Similarity | Computed output |
| Date/time attribution | TemporalExtent + validity/precision |
| Geometry/coordinates | SpatialExtent + precision/temporal geometry |
| Limited Event/Process reservations | First-class Event/State/Process |
| No canonical Trajectory | First-class Trajectory |
| Static region/layer assumptions | Temporal Region + Layer coverage |
| Uncertainty mainly Claim-bound | Claim, spatial, temporal, reconstruction and corpus uncertainty |

## 3. Product loop

v2:

`Question → Claims → Evidence → Comparison → Findings → Conclusion → Revision → Brief`

v3 first value:

`Time + Place + Layers → World configuration → Change/Simultaneity → Inspect evidence/uncertainty → Observation/Question`

Deep research may continue:

`Observation/Question → Claims → Evidence → Investigation → Revision → Brief`

## 4. Runtime/data disposition

| Existing asset | Action in Foundation PR | Later decision |
|---|---|---|
| Public MapLibre/GeoJSON site | Preserve unchanged | Adapt as first explorer contour |
| 31 architecture Features | Preserve | Use as architecture layer/selected context |
| Sources/Media | Preserve | Map to model assertions where needed |
| 12 legacy Relations | Preserve honestly | Reclassify only with evidence |
| Gate A validation modules | Preserve | Architecture fixtures, not active validation gate |
| Mutable ResearchSlice v2 | Preserve as backend compatibility | No migration in Foundation cycle |
| Stories/Courses code | Preserve frozen | Independent future decision |
| Explain Context contract | Preserve frozen | Input to later AI contract review |
| PR #314 public backend contour | Hold/close without merge after decision | Reopen only if v3 pilot requires backend |

## 5. GitHub backlog disposition

### Keep

- #283 as architecture-layer support;
- #322 and PR #326 as completed Architecture Layer fixtures/history;
- PR #319 and PR #321 as foundation history/audit evidence.

### Held before Foundation merge — completed disposition

- #286–#289;
- #308–#313;
- #323–#325;
- PR #314.

### Post-merge disposition — completed

Old Concept v2 implementation issues were closed `not planned` with a link to #327 without rewriting their titles or bodies.

Clean child issues were created for:

1. universal world-model contract and fixtures;
2. spatial-temporal uncertainty;
3. Leonardo World Slice;
4. synchronized explorer;
5. relation ladder;
6. contextual-learning validation;
7. source-bound AI reasoning contract.

## 6. Documentation disposition

| Document | v3 action |
|---|---|
| `ARTEMIS_CONCEPT.md` | Replace with v3 |
| `PRODUCT_THESIS.md` | Replace active vertical |
| `ARTEMIS_PRODUCT_SCOPE.md` | Replace active scope |
| `PROJECT_TRUTH.md` | Update direction; preserve factual runtime/data sections |
| `EPISTEMIC_CONTRACT.md` | Extend to world-model assertions/inference |
| `ENTITY_MODEL.md` | Add State/Trajectory/Region and re-center change |
| `RESEARCH_SLICE_CONTRACT.md` | Retain as optional research-work contract |
| `PRODUCT_VALIDATION_PLAN.md` | Gate as Concept v2 plan |
| `MVP_ARCHITECTURE_ATLAS.md` | Reclassify as architecture-layer historical vertical |
| `VALIDATION_DECISION.md` | Keep current evidence truth; no false EXPAND claim |
| `PRIORITIES.md` / `PROJECT_PHASES.md` | Replace active order with Foundation v3 |
| `FOUNDATION_INDEX.md` | Register new contract and routing |
| `AGENTS.md` / `ARTEMIS_MASTER_PROMPT.md` | Synchronize operational invariants |

## 7. Migration rule

No runtime or data record is migrated solely because this matrix exists.

Every later migration requires:

- target schema;
- fixtures;
- non-inventive legacy mapping;
- rollback/recovery;
- current capability truth;
- executable checks;
- separate approval/issue.
