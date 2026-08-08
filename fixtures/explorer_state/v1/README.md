# Explorer State fixture v1

This directory contains the executable renderer-neutral Explorer State contract for issue #340.

## Files

- `schema.json` — JSON Schema for Explorer State `1.0.0`.
- `state-1504-local-global.json` — positive deterministic state derived from the reviewed synthetic World Model fixture.

The fixture is synthetic contract evidence. It is not historical content and cannot support a 3D/public capability claim.

## Validation

```bash
python scripts/validate_explorer_state_fixtures.py
pytest -q tests/test_explorer_state_fixtures.py
```

Validation uses `fixtures/world_model/v1/package.json` as the pinned World Slice dependency and checks:

- exact dataset identity;
- layer/object/context references;
- trajectory → segment ownership;
- Region → geometry ownership;
- temporal selection consistency;
- mandatory uncertainty/corpus visibility;
- renderer-neutral view intent;
- rejection of renderer-owned shared keys such as `zoom`, `pitch`, `bearing`, `camera_state`, `viewer` and `scene`.

Renderer-specific camera conversion belongs to adapters under later #341/#343 work.