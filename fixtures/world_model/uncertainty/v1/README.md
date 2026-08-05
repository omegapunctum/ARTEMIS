# ARTEMIS uncertainty semantics fixtures v1

Status: `REVIEW_REQUIRED`

This additive package makes issue #330 temporal/spatial uncertainty rules executable. It depends on
the reviewed READY world-model package at `fixtures/world_model/v1` and does not modify that base.
Its scoped canonical owner is `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md`.

## Deterministic temporal result

For a closed query window, every temporal case resolves to exactly one of:

- `excluded` — all candidates are disjoint;
- `contained` — every finite candidate is wholly inside the query;
- `possible_overlap` — at least one candidate overlaps but the candidate set is not wholly contained;
- `unknown` — no temporal bound exists.

Touching boundaries overlap only when both touching sides are inclusive. Alternatives are evaluated
as a set; array order cannot select a reconstruction.

## Spatial boundary

The package distinguishes exact and approximate points, named places, unknown location,
documented paths, inferred analytical corridors and unknown routes. Unknown routes cannot contain
geometry. Approximate and inferred geometry require explicit uncertainty and disclosure.

Every case is bound to one checked-in Claim and a reviewed synthetic EvidenceLink/locator. The
locator carries the digest of the exact normalized assertion; arbitrary reference strings, geometry
precision promotion and projection-policy promotion are rejected.

## Compatibility

The Villa Savoye companion projection consumes the reviewed v1 compatibility record. It preserves
legacy year and coordinate values but explicitly refuses to manufacture day precision, target exact
spatial precision, a locator or EvidenceLink.

## Validation

```bash
python scripts/validate_uncertainty_fixtures.py
pytest -q tests/test_uncertainty_fixtures.py
```

`--require-ready` must fail until two independent review artifacts are committed and the transition
metadata is finalized without changing the reviewed semantic files.

READY also requires current bytes, `HEAD` and the frozen commit to agree on the normalized semantic
scope, with canonical regular review artifacts and Git replacement/graft mechanisms disabled.

## Capability boundary

These fixtures prove contract behavior only. They do not implement database/API/runtime schemas,
historical content, UI rendering, probabilistic reconstruction or calendar conversion.
