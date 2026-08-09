# Leonardo World Slice 1502–1504 — scope package v1

Status: `SCOPE_FROZEN / CURATION IN PROGRESS / NON-PUBLIC`.

Issues: [#355](https://github.com/omegapunctum/ARTEMIS/issues/355) and [#332](https://github.com/omegapunctum/ARTEMIS/issues/332).

## Purpose

This package freezes the smallest current content boundary for the first real ARTEMIS Globe MVP slice. It is a curation contract, not a READY historical dataset.

The analytical selection window is 1502–1504. The selected candidate story connects:

- Leonardo's appointment and documented Imola work context in 1502;
- his cartographic/engineering work in Borgia service without inventing a continuous route;
- the October 1503 Battle of Anghiari commission and the 4 May 1504 formal contract in Florence;
- one explicitly analytical, geometry-withheld Region built from separately catalogued map coverage;
- one sparse global simultaneity anchor under Safavid rule.

Every date, place and state remains a candidate until it is represented by atomic Claims, reviewed EvidenceLinks and reproducible locators.

## Files

| File | Role |
|---|---|
| `selection_manifest.json` | frozen time/space/layer/object boundary and relation/geometry policy |
| `source_registry.json` | institutional source candidates, locators, intended Claim scope and rights |
| `coverage_manifest.json` | explicit corpus limits, material gaps and exit conditions |
| `curation_cost.json` | preparation/review cost shape; all durations remain pending rather than estimated |
| `*.schema.json` | closed Draft 2020-12 structural contracts |
| `scripts/validate_leonardo_world_slice.py` | semantic fail-closed validator |
| `tests/test_leonardo_world_slice.py` | positive and controlled-corruption regression tests |

## Current evidence boundary

Candidate evidence comes from institutional catalogues and controlled vocabularies:

- Royal Collection Trust collection items [912284](https://www.rct.uk/collection/912284/a-map-of-imola) and [912278](https://www.rct.uk/collection/912278/a-map-of-southern-tuscany);
- the Comune di Imola Musei Civici history of the [Rocca Sforzesca](https://museiciviciimola.it/rocca-sforzesca-imola/luogo-rocca-sforzesca-imola-imola/) for the visit and local political-context candidates;
- the National Gallery scholarly catalogue entry for [The Procession to Calvary](https://www.nationalgallery.org.uk/paintings/catalogues/plazzotta-and-henry-2022/the-procession-to-calvary);
- Getty TGN records for [Imola](https://www.getty.edu/vow/TGNFullDisplay?find=&nation=&place=&subjectid=7004864) and [Florence](https://www.getty.edu/vow/TGNFullDisplay?find=&nation=&place=&subjectid=7000457), used as attributed approximate reference points under ODC-By 1.0;
- The Metropolitan Museum of Art's [List of Rulers of the Islamic World](https://www.metmuseum.org/toah/hd/isru/hd_isru.htm) for one global simultaneity candidate.

No Royal Collection image is copied or licensed by this package. Source URLs are not blanket proof. The registry limits each source to named candidate Claims and records the remaining immutable-locator gap.

## Fail-closed rules

- Candidate historical and analytical geometry is `null`.
- The Imola→Florence trajectory gap is `unknown_route` and has no line.
- Getty coordinates remain approximate present-day reference points, not historical footprints.
- The changing Region is an analytical document-coverage region, not a political boundary.
- No stored Relation is allowed while #331 is paused; only derived co-presence may later be computed.
- Candidate assertions are not READY and cannot be promoted.
- Unknown cost is `null`, not an estimate.
- Absence from the package never means historical absence.

## Validate

```bash
python scripts/validate_leonardo_world_slice.py
python -m pytest -q tests/test_leonardo_world_slice.py
```

## Next gate

Convert the frozen candidates into a versioned World Model package with atomic Claims, EvidenceLinks, locators, Uncertainty, source-rights evidence and reviewed geometry. Two independent reviews are required before READY.
