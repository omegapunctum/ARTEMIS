# Unified Explorer advisory v1

Status: completed read-only architecture/product audit; recommendation only. No runtime implementation, corpus intake or product-gate transition is opened.

Authority: the owner's 2026-10-04 instruction to continue and question whether Globe, Region and the architectural 2D map should share one display. This document answers that question under the accepted [platform decision](../PLATFORM_ARCHITECTURE_DECISION.md); it does not replace that owner or expand the completed autonomous audit sequence. Repository base: main `15c9c29c6013cc13b2ba4f93662b3205acb87d67`, tree `c067951caa754e1857396c2fcc6be2de88323cc8`.

## Finding

Recommend one ARTEMIS Explorer, with Globe as the current primary spatial presentation and a future 2D option over the same semantic input and exploration state. Region is a domain object/data proof, not a competing renderer. Globe-only superiority over 2D has not been established by user evidence.

| Surface | Inspected implementation | Consequence |
|---|---|---|
| Leonardo Globe | `scripts/build_globe_spike.py`, shared template/runtime, World Model → Explorer State → Render Projection | Existing active research example; 11 Presence episodes, 1452–1519 |
| Roman Region | Same builder/template/runtime; separate `roman_region_proof` semantic inputs, `life_path.available=false` | Existing bounded R&D example; three reconstructed snapshots, 91–116 CE; different temporal controls |
| Architecture Atlas 2D | `js/data.js` loads `data/features.geojson`; separate `js/map.js` and compatibility UI/state | 31 legacy Features; not yet the 2D projection of the current Explorer core |

The builder's `_load_semantic_inputs` dispatch accepts Leonardo, Roman Region and contract fixture inputs; it has no Atlas adapter. Atlas fields such as `validated`, `date_valid`, `source_refs` and construction dates cannot silently become reviewed Claims, EvidenceLinks or an object's entire existence interval. Rendering those records on a globe would not establish semantic migration.

## Recommended order

1. Prepare a separately bounded decision/specification for common navigation between the existing Leonardo and Region examples. Identify active example, coverage and R&D limitations. Keep existing routes and dataset-specific time/selection behavior; retain Atlas as an explicitly named compatibility link. Avoid introducing a generic application framework for this small step.
2. Before architecture intake, prepare a one-record mapping proof: identity, temporal meaning/precision, coordinate meaning, source-native locator, rights, Claim/evidence state and explicit losses. Unknowns remain unknown; legacy validation flags do not confer historical acceptance. Bulk intake is outside that proof.
3. When a concrete research need justifies it, implement a 2D/Globe switch over one slice/state and verify it against the existing Cross-Renderer Parity Contract. Camera and projection remain renderer-local; memberships, identity, time, uncertainty and evidence remain shared.

Common navigation should be checked from both examples; time/selection parameters from incompatible inputs must not leak across routes; reopening a saved URL must reproduce its original example; provenance and limitations must remain accessible. These are proposed acceptance criteria, not evidence that the feature exists.

Do not combine Roman 91–116 CE and Leonardo 1452–1519 into a synchronous historical scene. A future multi-domain composition needs compatible coverage and explicit evidence; selection/proximity must not imply encounter, influence or causality. Contextual composition remains DEFERRED.

## Delegation and stop

Architecture agent `/root/architecture_audit` independently inspected builder dispatch, shared runtime and actual Atlas records. Product agent `/root/product_direction` independently checked owner boundaries, temporal coverage and the minimum useful navigation candidate. Both recommended the order above. Engineering agent `/root/engineering_audit` was assigned the separate one-source Cesena research audit.

For a future authorized navigation task: Product writes the bounded interaction specification; Engineering implements existing-route navigation and verifies restore/isolation; Architecture reviews exact revision and evidence independently. For architecture intake, Research first checks the one-record source/rights/locator mapping. No successor implementation follows automatically from this advisory.

Gate E remains closed without VALUE_SIGNAL; formal/comparative value remains UNVALIDATED. Canonical owners, machine state, frozen packages and public routes are unchanged. Stop at this audit and the separately recorded Cesena read-only result.
