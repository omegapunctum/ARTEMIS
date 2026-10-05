# Park Hill coordinate check v1

## Authority and bounded specification

- Owner continuation **«Продолжай»**, 2026-10-05, executes the coordinate-check proposal after completed mapping PR #466. Standing repository-write permission and the fully AI development/review delegation apply; no further intake is implied.
- Classification: `DECISION` for separately authorized research under [Product Scope §2](../ARTEMIS_PRODUCT_SCOPE.md#2-scope-lock-текущего-цикла), followed by research tooling implementation and technical verification. The [prior mapping](2026-10-04_ATLAS_ONE_RECORD_MAPPING_PROOF_v1.md) remains historical completed evidence.
- Baseline main `a439167641f0a9a1413dfb68418149abf137b17d`, tree `d992c123e91db405d774aa29a710589fa093aee8`.
- Prospective independent review: `/root/coordinate_method`, `ACCEPT_METHOD_AND_BOUNDED_SCOPE`; independently reproduced the numbers and primary grid convention before implementation.

Question: does the official listing grid reference reproduce the existing Atlas WGS84 point, and what may a converted coordinate mean?

Allowed: one existing Park Hill record, primary-source locators, an explicit offline approximate transformation, point comparison, evidence, small reproduction script and checks, scope/registry synchronization. No corpus/data/runtime write, adapter, new ontology/schema, frozen fixture mutation, map/photo reuse or historical Claim/geometry promotion. Product/gate machine state and public capability stay unchanged. The spatiotemporal contract §5 and uncertainty contract own precision and validity; this research cannot override them.

Method specification: only the `SK` square with five digits per axis; expand the source reference without adding a cell-centre offset. Use the explicitly recorded pipeline derived from inverse EPSG:19916 and EPSG:1314, not an automatically selected fallback. Pin pyproj 3.7.2 / bundled PROJ 9.5.1, disable network, reject changed engines/source snapshots, keep GIS longitude/latitude order, and measure separation on the WGS84 ellipsoid. No claim of OSTN15 accuracy. Independent method review accepted the bounded script, stdlib tests and path-restricted CI.

## Result

**REFERENCE_POINT_DISCREPANCY**. [Historic England NHLE 1246881](https://historicengland.org.uk/listing/the-list/list-entry/1246881), Official list entry → Location → National Grid Reference and Details → Listing NGR, displays matching spaced and compact references. The [OS reference convention](https://docs.os.uk/more-than-maps/a-guide-to-coordinate-systems-in-great-britain/transverse-mercator-map-projections/the-national-grid-reference-convention) defines local easting/northing in 100 km squares. SK's southwest origin `400000,300000` was visually checked in the [OS Guide v3.6](https://www.ordnancesurvey.co.uk/documents/resources/guide-coordinate-systems-great-britain.pdf), §7.1 Figure 8, printed page 42. Sources accessed 2026-10-05; no full-page immutable source snapshot or map reproduction is included.

| Input/result | Value |
|---|---|
| Official reference | `SK 36064 87093` / `SK3606487093` |
| Expanded OSGB36 / British National Grid, EPSG:27700 | E `436064`, N `387093` metres |
| Approximate WGS84 candidate, longitude/latitude | `[-1.4593291070, 53.3794641186]` |
| Existing Atlas point, longitude/latitude | `[-1.4582, 53.38163]` |
| WGS84 ellipsoidal point separation | `252.487357 m`, report as about **252.5 m** |
| Datum-operation expected accuracy metadata | EPSG:1314 / OSGB36 to WGS 84 (6): `2 m` |
| Source position accuracy / historical spatial validity | unknown / unknown |

The [evidence JSON](evidence/2026-10-05_park_hill_coordinate_v1.json) retains full pipeline and digest, input file/selected-record hashes, source baseline, axis order, versions, diagnostic observation and holds. Selected-record SHA uses UTF-8 JSON with `ensure_ascii=False`, sorted keys and compact separators. It is research evidence, not a World Model payload. The calculation uses the imported point's declared WGS84 interpretation; that declaration is not independently verified ground truth.

An offline TransformerGroup diagnostic with Sheffield area of interest and ballpark disabled found the OSTN15-backed operation (9) unavailable because `uk_os_OSTN15_NTv2_OSGBtoETRS.tif` was absent. No grid was downloaded. The reproduction script directly applies the recorded Helmert pipeline regardless of installed grid availability. [OS OSTN15 guidance](https://docs.os.uk/more-than-maps/a-guide-to-coordinate-systems-in-great-britain/from-one-coordinate-system-to-another-geodetic-transformations/national-grid-transformation-ostn15-etrs89-osgb36) describes OSTN15 as definitive for OSGB36/ETRS89 and Helmert applications as limited to about 3 metres. That guidance and the operation's 2 m metadata describe different contexts; neither supplies total source uncertainty or a guaranteed error bound. [pyproj's accuracy/pipeline API](https://pyproj4.github.io/pyproj/stable/api/transformer.html) and [PROJ's Helmert convention](https://proj.org/en/stable/operations/transformations/helmert.html) support the declared implementation.

## Permitted interpretation and holds

The converted value is a **source-bound listing-reference anchor candidate** for further research. Five digits per axis encode 1 m resolution; they do not establish metre-accurate source location. Decimal places serve numerical reproduction. Temporary zero height in the 2D operation is computational, not site elevation. Coordinate epoch and specific WGS84 realization are not established.

The two coordinate values differ under the declared operation. This does not establish that either point is erroneous: they may identify different parts of the complex. Neither source defines a verified footprint, centroid, entrance or geometry valid for 1957–60 or all historical periods. Target geometry stays null, spatial accuracy and historical validity unknown; no automatic replacement of the legacy point or adoption of its `exact` confidence. Listing text, maps and media retain separate rights treatment; no Commons asset or official map is included.

## Implementation and verification

Declared scope: this document, evidence JSON, `scripts/check_park_hill_coordinate.py`, its isolated requirements file, `scripts/research_tests/test_park_hill_coordinate.py`, path-restricted research workflow, Product Scope and work registry. Research tests stay outside the general `tests/` collector so scheduled Atlas export requires neither this dependency nor the frozen snapshot. No `data/*`, runtime, backend, canonical semantic contract or frozen proof changed. The source-hash guard intentionally requires the research snapshot; future Atlas edits do not invalidate this historical comparison. Reproduce from this PR's revision with its pinned data rather than regenerating old evidence against new data.

```sh
python -m pip install --only-binary=:all: -r scripts/requirements-coordinate-research.txt
python scripts/check_park_hill_coordinate.py --check
python -m unittest discover -s scripts/research_tests -p test_park_hill_coordinate.py -v
```

Local reproduction and six tests PASS: reference resolution/rejection, numeric output/axis order, inverse round trip, source drift failure, engine drift failure, and withheld geometry/promotion. The 98 relevant repository-governance, project-state, R&D lifecycle and Core-boundary checks also PASS. Exact-head independent review/CI are recorded in this PR's durable review/checks before merge under [DOS §6](../DEVELOPMENT_OPERATING_SYSTEM.md). These are technical research checks, not historical acceptance, publication or user-value validation.

## Stop condition

Stop after this coordinate comparison. One next proposed research task: determine which parts of the Park Hill complex the official reference and legacy point identify from a primary location description, before choosing any runtime anchor. No adapter, public architectural layer, bulk intake or projection switch is authorized by this result. Gate E remains closed without VALUE_SIGNAL; contextual composition DEFERRED; comparative/formal value UNVALIDATED.
