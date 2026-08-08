# Render Projection fixture v1

This directory owns the executable #341 projection schema and fixture contour.

## Inputs

The deterministic fixture does **not** duplicate World Model data. It consumes:

- `fixtures/world_model/v1/package.json` — reviewed READY synthetic World Model package;
- `fixtures/explorer_state/v1/state-1504-local-global.json` — merged renderer-neutral Explorer State fixture.

## Files

- `schema.json` — neutral Render Projection Package schema `1.0.0`.
- `README.md` — lifecycle and validation boundary.

Generated adapter payloads (`projection.json`, `maplibre.geojson`, `globe.json`) are intentionally **not** committed as independent content artifacts. The builder materializes them deterministically for tests/inspection so they cannot become a second historical source of truth.

## Build / validation

```bash
python scripts/build_render_projection_fixtures.py --write
pytest -q tests/test_render_projection_contract.py
```

`--write` materializes derived files under this fixture directory in the current working tree. CI treats them as ephemeral generated artifacts.

The tests verify semantic anchors rather than snapshotting bulk derived JSON:

- explicit point geometry reaches both adapters;
- `named_place` without canonical geometry stays unresolved;
- unknown/inferred trajectory gap never becomes a line;
- primary and alternative Region reconstructions coexist;
- State/Process can resolve through temporal Region geometry without changing object identity;
- Claim/EvidenceLink/Source/Uncertainty refs survive both adapters;
- approximate temporal alternatives remain `possible_active`;
- Relation rendering remains deferred from v1;
- explicit source path geometry is supported;
- missing adapter capability fails closed;
- Globe v1 adds no altitude/terrain history.

## Output boundary

The MapLibre output is a future adapter shape and does not replace current public `data/features.geojson`.

The Globe output is engine-neutral cartographic data with `vertical_semantics=not_modeled`; #342 owns terrain/elevation semantics and #343 owns the runtime spike.