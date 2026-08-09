# ARTEMIS cross-renderer parity fixtures v1

Executable regression evidence for issue #344.

## Files

- `schema.json` — strict schema for the expected renderer-neutral semantic state.
- `expected.json` — positive parity anchors over the reviewed synthetic World Model + merged Explorer State.
- `negative_cases.json` — controlled corruptions that must be rejected by the parity harness.

## Boundary

These fixtures are **not historical data** and are not renderer styling specifications.

They pin semantic invariants only:

- canonical object/subobject identity;
- active / possible-active / context state;
- temporal boundary behavior;
- Region reconstruction identity and alternatives;
- Trajectory segment kind and uncertainty;
- Claim / EvidenceLink / Source refs;
- selected-object identity;
- active trajectory/Region focus from the accepted Explorer State;
- DerivedObservation vs documented Relation distinction.

Camera, color, projection pixels, label placement, clustering, LOD, GPU/tile/cache implementation and screenshots are renderer-only concerns and are deliberately outside semantic parity.

## Validation

```bash
python scripts/validate_renderer_parity.py
pytest -q tests/test_renderer_parity.py
```

Every case in `negative_cases.json` must make `assert_parity()` fail. A negative fixture may mutate only derived test payloads; reviewed upstream World Model fixtures are never rewritten to make parity pass.
