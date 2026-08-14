# ARTEMIS geospatial assets fixture v1

This directory is executable contract evidence for issue #342.

## Files

- `schema.json` — strict Geospatial Asset Manifest JSON Schema v1.
- `manifest.json` — synthetic terrain + imagery context fixture.
- `gate_d_runtime.json` — runtime configuration selecting the bundled Natural Earth land layer while keeping terrain synthetic/non-live.

## Fixture status

The contract fixture in `manifest.json` is deliberately synthetic. The separate Gate D runtime profile applies the same schema and validator to a pinned real physical-geography dataset under `docs/work/2026-08-14_GATE_D_EARTH_CONTEXT_PROVIDER_POLICY_v1.md`.

It does **not**:

- select or endorse a real terrain/imagery provider;
- contain production API endpoints or credentials;
- claim current real-world freshness/coverage;
- provide historical terrain, coastline or imagery;
- create World Model facts.

The synthetic fixture exists only to test provider separation, coordinate/vertical metadata, licensing, cache/runtime rules and the distinction between present-day context and historical reconstruction. The Gate D runtime profile does not convert Natural Earth data into historical truth.

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
