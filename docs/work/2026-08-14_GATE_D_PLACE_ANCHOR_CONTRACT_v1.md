# Gate D Place Anchor Contract v1

Date: 2026-08-14  
Owner: issue #355  
Lifecycle effect: none; Gate D remains `IN_PROGRESS`

## Decision

The Gate D Globe may resolve Rimini, Cesena, Cesenatico and Imola through a separate, source-bound present-day settlement reference overlay. This overlay does not modify the frozen Gate C package and does not promote any historical Claim.

The authoritative runtime input is `fixtures/globe_runtime/v1/leonardo_place_anchors.json`, validated fail-closed by `fixtures/globe_runtime/v1/place_anchor_schema.json`.

## Evidence and precision

- Source: Wikidata P625 coordinate location for Q13369, Q6662, Q99937 and Q50195.
- Coordinate reference: WGS84 / `EPSG:4326`.
- Structured-data license: `CC0-1.0`.
- Render precision: `named_settlement`.
- Historical-location precision: `exact_position_within_named_settlement_unknown`.
- Semantic role: `present_day_settlement_reference`.

Each projected anchor keeps a Claim, EvidenceLink locator, Source, rights record and material spatial-precision Uncertainty available to the inspector.

## Permitted projection

- render the four named settlements as contextual points;
- reuse the matching settlement point for an already-reviewed Trajectory `presence` segment;
- expose the anchor role and named-settlement precision in the inspector;
- keep time/layer selection and 2D/Globe adapter semantics synchronized.

## Forbidden inference

- no point may be described as Leonardo's exact position or an exact event position;
- no line may connect presence segments;
- no route interpolation is permitted;
- no Duchy of Romagna boundary or historical footprint is permitted;
- no documented Relation is created;
- no Airtable historical row is written;
- no historical Claim is upgraded from draft/rejected status.

## Fail-closed checks

The build fails if:

- the registry does not close exactly the four reviewed Place identities;
- an anchor lacks its source entity, Claim, EvidenceLink, CC0 rights or uncertainty binding;
- a Gate D resolved geometry is not a Point with `place_reference_anchor` origin and `named_settlement` precision;
- a trajectory gap gains geometry;
- a Region alternative gains geometry;
- the frozen Gate C candidate package contains geometry or promoted Claims.

## Gate effect

This contract closes the place-level spatial-anchor gap only. It does not close Gate D. Normal-browser/physical-device evidence, 390 CSS px mobile review, assistive-technology review, representative non-virtual performance observations and one explicit Gate D exit decision remain pending.
