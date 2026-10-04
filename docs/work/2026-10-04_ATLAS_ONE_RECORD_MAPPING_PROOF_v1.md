# Architecture Atlas one-record mapping proof v1

- Status: completed read-only research and semantic mapping; independent AI review required before merge.
- Date: 2026-10-04.
- Authority: the owner's explicit continuation after the completed navigation task, followed by **«Хорошо. Продолжай»** after the proposed bounded Atlas mapping step. This newly authorizes the one-record study; the earlier advisory and standing merge permission alone did not authorize intake.
- Classification: `DECISION` records this separately owner-authorized research contour in [Product Scope §2](../ARTEMIS_PRODUCT_SCOPE.md); no runtime implementation is authorized. Review/merge follows [Development Operating System §6](../DEVELOPMENT_OPERATING_SYSTEM.md).
- Repository baseline: main `636e70befce5738a7fb764076cc32797c2252ae0`, tree `a10b619a2b480f06e6b88e6bb1bf62d093a2d12c`; completed navigation PRs #464/#465.

## Question and bounded choice

Can one existing architectural record be mapped to the shared core without importing legacy dates, coordinates, licences or validation flags as accepted historical meaning?

Choose **Park Hill, Sheffield**, existing UUID `08c92f35-cc8b-4164-a6ea-1f9c89e777dd`, alias `recs15CbqhEKwSKen`, and its already-linked Historic England list entry `1246881`. The exported corpus has 31 Features; this proof selects exactly one. Park Hill has a stable source locator and separate Source/Media records, so it can expose the important migration limits without a corpus search.

Alternatives: directly wrap all 31 Features on Globe; reuse the frozen Villa Savoye compatibility fixture; or perform one explicit research mapping. Prefer the last: it tests the real architecture boundary while preserving the existing corpus and reviewed fixture. The [unified Explorer advisory](2026-10-04_UNIFIED_EXPLORER_ADVISORY_v1.md) supplies the architectural order, not intake authority.

Allowed outputs: this decision/result, one commit-pinned research JSON mapping, scope/registry synchronization and independent AI review. No adapter, World Model package, new schema, runtime route, 2D switch, corpus write, image/map download or change to frozen evidence. Machine product/gate state and public capability remain unchanged.

## Findings and field mapping

**ONE_RECORD_MAPPING_FEASIBLE_WITH_GAPS**. Existing [Entity Model §4](../ENTITY_MODEL.md#4-entity-subtypes) already supports an architectural building as `Entity` / `Object`; no new fundamental type or second ontology is required. The map rendering and source-state questions remain separate.

| Existing field/context | Shared-core candidate / retained meaning | Explicit loss or hold |
|---|---|---|
| UUID and existing alias | Same Object identity; retain source identity separately | No new UUID or duplicate Entity |
| EN/RU names | Imported labels | Names alone do not prove identity |
| `date_start=1957`, `date_end=1960`, construction-end null | Preserve exact legacy fields; construction candidate assessed separately | Entity lifetime unknown; no automatic Event/State or existence end |
| WGS84 Point `[-1.4582, 53.38163]`, legacy `exact` | Preserve imported point candidate separately | Target geometry withheld; precision unknown pending source-bound location check |
| `source_refs` roles / Source `reviewed` | Existing institutional bibliography and candidate evidence roles | Compatibility review does not become new Claim/EvidenceLink acceptance |
| Description, short title, tags | Raw metadata and possible atomic Claim candidates | No blanket Source support or high confidence |
| Feature `source_license`, separate Media record | Preserve source and media declarations independently | Image licence cannot license institutional text/maps |
| Two `same_movement` links | Legacy link inventory only | No substantive Relation, causal influence or second endpoint intake |
| `influence_radius_km=1` | Legacy presentation metadata | No Region geometry, historical influence or uncertainty radius |

Legacy date/point Claim candidates describe what the pinned record contains: `origin=imported`, `review_state=draft`, `confidence=unknown`, `evidence_state=missing`, no fabricated EvidenceLinks. The JSON is **research evidence**, not an executable World Model payload; its Entity extents and official-source normalization remain unapproved.

## One-source check — 2026-10-04

Primary source: [Historic England, NHLE 1246881](https://historicengland.org.uk/listing/the-list/list-entry/1246881), inspected live by the research agent and orchestrator.

| Assertion candidate | Reproduced native value / locator | Bound |
|---|---|---|
| Identity | Official List Entry: name, number and statutory addresses | Corresponding listed architectural object |
| Construction | `1957-60`; Details, first paragraph | Year precision; construction rather than whole lifetime |
| Formal opening | `1961`; Details, first paragraph | Separate assertion, not a replacement construction end |
| Listing reference location | `SK 36064 87093`; Location → National Grid Reference; Details → Listing NGR | Reference location; no verified equivalence to legacy WGS84 point, footprint, centroid or entrance |
| Text rights | End-of-entry licence statement declares OGL v3.0 with exceptions | Detailed licence page returned 403 to research retrieval; clause-level verification incomplete |

The entry separates text reuse from map restrictions and cautions that its map is a reference display. No map was downloaded. The Commons photograph and its repository-declared attribution/licence were inventoried, not independently rights-verified; omit media from a subsequent bounded proof until checked. Live locators were reproduced, but no immutable full-page source snapshot or fresh historical acceptance is claimed.

These observations support claim-level preparation under the [Epistemic Contract](../EPISTEMIC_CONTRACT.md) and [spatiotemporal contract](../SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md); they do not silently update legacy content or approve normalization.

## Existing evidence and validation boundary

The frozen World Model v1 compatibility fixture is commit-pinned and specifically illustrates Villa Savoye. Its validator and mandatory synthetic scenarios are not a general Atlas intake validator. Preserve that package unchanged.

[Module B's reviewed reference brief](validation_modules/briefs/module_b_reference_brief.md) already records Park Hill deck/community design-intent evidence (`B-C3` / `B-E3`) with its own Source `B-S2`. Reference that historical package separately; do not copy its review status, silently merge Source identities or import the Unité relation/another endpoint. This one-record source check did not re-review that package.

The [research JSON](evidence/2026-10-04_atlas_park_hill_mapping_v1.json) pins six input file hashes, selected record hashes and canonicalization, the preserved Feature/Source/Media snapshot, proposed core meanings, legacy-link inventory and explicit exclusions. It sets historical promotion, runtime intake and bulk intake to **false**. It creates no replacement data model.

## Acceptance and stop

Verify: one selected UUID and existing alias; pinned input/record hashes; unchanged native legacy date/point fields; unknown lifetime and withheld geometry; no automatic EvidenceLink/Relation; separate Source/Media rights; raw data, reviewed fixtures, runtime and machine product/gate state unchanged. Relevant governance/state/lifecycle checks and exact-head independent AI review must pass before merge.

Local verification: six pinned file hashes, four canonical selected-record hashes, both legacy-link hashes, UUID/alias and temporal/spatial/promotion assertions **PASS**. The 95 relevant repository-governance/project-state/lifecycle tests **PASS** (2.39 seconds); JSON parsing and diff checks **PASS**. No data, schema, fixture, runtime or machine product/gate file changed.

Architecture agent `/root/atlas_mapping` checked the existing core and compatibility/reviewed packages. Research agent `/root/atlas_source` checked the one official entry and rights boundaries. Independent final review is recorded durably on the exact PR revision. Agent acceptance concerns mapping conformity, not a new historical Claim or human-comprehension/value result.

Stop after recording this result. One next proposed action: check the meaning of Park Hill's official grid reference and a reproducible coordinate transformation for a source-bound reference anchor, keeping historical footprint/time unknown and media omitted. This proposal does not authorize an adapter, public architecture preview, mass intake or 2D/Globe switch. Gate E remains closed without VALUE_SIGNAL; contextual composition DEFERRED, conflict proof non-public, comparative/formal value UNVALIDATED.
