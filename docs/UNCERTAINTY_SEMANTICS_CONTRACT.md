# ARTEMIS — UNCERTAINTY SEMANTICS CONTRACT

## Status

- Type: scoped canonical extension.
- Version: 1.0.
- Date: 2026-08-04.
- Status: `READY`.
- Active issue: `#330`.
- Extends: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` and `EPISTEMIC_CONTRACT.md`.
- Owns: deterministic temporal/spatial uncertainty normalization, filtering and projection rules.
- Does not own: core object identity, runtime/database schemas, relation ladder or public capability.

The two base contracts are part of the immutable reviewed scope of #329 / PR #336. This document
adds the #330 profile without rewriting that completed evidence package.

## 1. Invariants

1. Uncertainty is evaluated from explicit bounds, alternatives and evidence, never implicit tolerance.
2. Precision is not duration.
3. Query determinism does not turn an uncertain historical value into an exact value.
4. Open and unknown values remain open or unknown.
5. Alternatives remain separate; array order cannot select a winner.
6. Geometry coordinates alone do not prove exactness.
7. Inferred or unknown routes are never rendered as documented paths.

## 2. Temporal bounds

- `not_before` is a lower bound;
- `not_after` is an upper bound;
- open-start and open-end extents keep the missing endpoint unbounded;
- an unknown extent has neither bound;
- approximate values require an explicit possible range;
- every boundary is inclusive or exclusive;
- each alternative has its own Claim basis.

The executable profile uses proleptic Gregorian dates with one canonical lexical form:

- `YYYY` for year precision;
- `YYYY-MM` for month precision;
- `YYYY-MM-DD` for day precision.

Unsupported calendars remain source text plus unresolved normalization state until a separately
reviewed calendar policy exists.

## 3. Window classification

A selected closed time window returns exactly one result:

| Result | Rule |
|---|---|
| `excluded` | every candidate is disjoint after boundary inclusivity is applied |
| `contained` | every candidate has finite bounds and is wholly contained in the window |
| `possible_overlap` | at least one candidate overlaps, but the candidate set is not wholly contained |
| `unknown` | no temporal bound exists; ordinary time filtering excludes it unless unknown-time content is requested |

Touching boundaries overlap only when both touching sides are inclusive. A UI may include
`possible_overlap`, but must preserve that label and must not center it as an exact placement.

## 4. Spatial precision and route modes

| Mode | Required meaning |
|---|---|
| `exact_point` | coordinate precision is supported by the represented Claim/evidence |
| `approximate_point` | point plus explicit tolerance/area and visible uncertainty |
| `named_place` | place identity without invented point geometry |
| `unknown` | no location geometry is projected |
| `documented_path` | source-bound route geometry |
| `inferred_corridor` | analytical geometry with explicit assumptions and uncertainty |
| `unknown_route` | endpoints may be known; connecting geometry is prohibited |

Current legacy coordinates without Claim-level precision evidence project as
`unknown_precision`, even if a legacy field says `exact`.

## 5. Epistemic payload

A material spatial-temporal uncertainty record declares:

- affected dimension;
- explicit possible bound(s), tolerance or alternatives when known;
- boundary inclusivity where relevant;
- projection effect (`show_possible`, `show_unknown`, `show_alternatives`,
  `show_exact`, `show_open_bound`, `show_inferred_geometry` or `prohibit_geometry`);
- supporting Claim refs or explicit missing-evidence state.

Every executable `basis_claim_ref` resolves to a checked-in Claim. A supported Claim resolves through
a reviewed EvidenceLink and reproducible locator to the synthetic fixture source; the locator binds
the exact normalized temporal or spatial assertion digest. `exact_point` and `documented_path`
require direct, reviewed, high-confidence support. Open, approximate, unknown and inferred modes
cannot select an exact projection policy.

Approximation without a declared range/tolerance is unresolved. `not_before` and `not_after`
constrain possible time; they do not assert an exact date.

## 6. Compatibility

A current Architecture Atlas year/coordinate projection:

- preserves year precision and values;
- does not invent day/month precision;
- does not promote legacy coordinate confidence to target exactness;
- does not create a locator or EvidenceLink;
- exposes every material loss and unknown.

## 7. Executable fixtures

The versioned package covers:

1. exact day;
2. `not_before` / open end;
3. `not_after` / open start;
4. finite bounded constraints;
5. inclusive/exclusive touching boundaries;
6. explicit approximate range;
7. conflicting temporal alternatives;
8. wholly unknown time;
9. all seven spatial/route modes;
10. non-inventive legacy compatibility projection.

The package additionally closes all Claim, EvidenceLink, Source and Uncertainty references, validates
type-specific GeoJSON cardinality/ring closure, and treats the compatibility projection as a closed
value-bound envelope derived from the reviewed v1 input snapshot.

## 8. Capability boundary

This contract and its fixtures do not migrate current Feature fields, implement runtime filtering,
publish a Leonardo corpus or prove that the public UI renders these states.

## 9. Change control

Changes require synchronized fixture schema/package, validator, negative tests, compatibility
statement, working review record and two independent reviews on one frozen commit. READY additionally
requires canonical non-symlink review files, regular current/frozen Git blobs, one reviewed digest,
distinct structured review artifacts and a current-HEAD CI invocation of the READY gate.
