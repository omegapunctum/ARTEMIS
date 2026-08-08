# ARTEMIS geospatial assets fixture v1

This directory is executable contract evidence for issue #342.

## Files

- `schema.json` — strict Geospatial Asset Manifest JSON Schema v1.
- `manifest.json` — synthetic terrain + imagery context fixture.

## Fixture status

The manifest is deliberately synthetic.

It does **not**:

- select or endorse a real terrain/imagery provider;
- contain production API endpoints or credentials;
- claim current real-world freshness/coverage;
- provide historical terrain, coastline or imagery;
- create World Model facts.

The fixture exists only to test provider separation, coordinate/vertical metadata, licensing, cache/runtime rules and the distinction between present-day context and historical reconstruction.

## Semantic boundary

Geospatial assets are renderer infrastructure/context. They do not replace:

- World Model / World Slice semantics;
- Explorer State;
- Render Projection;
- Claim / EvidenceLink / Uncertainty provenance.

`present_day_context` may help orient the user, but it does not assert that the same terrain/coastline/basemap was historically valid at the selected ARTEMIS time.

A `historical_reconstruction` asset must pass stricter validator rules for temporal validity, World Model claim bindings, uncertainty field and reconstruction method.

## Validation

Run:

```bash
python scripts/validate_geospatial_assets.py
pytest -q tests/test_geospatial_assets_contract.py
```

The validator rejects secret leakage, invalid vertical references, semantic-role/time mismatches, invalid cache/licensing combinations, broken fallbacks and duplicate asset identities.