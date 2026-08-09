# Leonardo-in-Romagna World Slice 1502 — scope package v1

Status: `SCOPE_FROZEN / CURATION IN PROGRESS / NON-PUBLIC`.

Issues: [#355](https://github.com/omegapunctum/ARTEMIS/issues/355), [#332](https://github.com/omegapunctum/ARTEMIS/issues/332) and [#360](https://github.com/omegapunctum/ARTEMIS/issues/360).

## Purpose

This package freezes the smallest current content boundary for the first real ARTEMIS Globe MVP slice. It is a curation contract, not a READY historical dataset.

The analytical window is 8 August–31 December 1502. The selected candidate story contains:

- dated or datable contexts at Rimini, Cesena, Cesenatico and Imola;
- commissioned engineering service and a bounded surveying/fortification Process;
- a presence-only Trajectory with three explicit unknown-route gaps;
- a geometry-withheld Duchy of Romagna political Region candidate;
- one sparse global simultaneity anchor under Safavid rule.

Every date, place, State and Region version remains a candidate until it is represented by atomic Claims, reviewed EvidenceLinks and reproducible locators.

## Files

| File | Role |
|---|---|
| `selection_manifest.json` | frozen time/space/layer/object boundary and relation/geometry policy |
| `source_registry.json` | institutional source candidates, locators, intended Claim scope and rights |
| `claims_manifest.json` | atomic draft Claims, candidate EvidenceLinks and explicit Uncertainty bindings |
| `coverage_manifest.json` | explicit corpus limits, material gaps and exit conditions |
| `curation_cost.json` | preparation/review cost shape; durations remain pending rather than estimated |
| `*.schema.json` | closed Draft 2020-12 structural contracts |
| `scripts/validate_leonardo_world_slice.py` | semantic fail-closed validator |
| `tests/test_leonardo_world_slice.py` | positive and controlled-corruption regression tests |

## Current evidence boundary

Candidate evidence comes from institutional catalogues and references:

- [Museo Galileo Manuscript L](https://brunelleschi.imss.fi.it/genscheda.asp?appl=LIR&chiave=100790&lingua=ENG&xsl=manoscritto) for manuscript identity and the 1502 engineering context;
- [Visit Romagna](https://visitromagna.it/en/leonardo-da-vinci-and-cesare-borgia-ingenuity-and-intellect-at-the-service-of-the-duchy) for candidate dates, itinerary sections and folio references;
- Royal Collection Trust items [912284](https://www.rct.uk/collection/912284/a-map-of-imola) and [912686](https://www.rct.uk/collection/912686/recto-sketches-of-the-street-plan-of-imola-verso-notes-on-mathematics);
- [Comune di Imola Musei Civici](https://museiciviciimola.it/rocca-sforzesca-imola/luogo-rocca-sforzesca-imola-imola/) for the consultation and political-transition context;
- [Getty TGN Imola](https://www.getty.edu/vow/TGNFullDisplay?find=&nation=&place=&subjectid=7004864) under ODC-By 1.0;
- [The Met](https://www.metmuseum.org/toah/hd/isru/hd_isru.htm) for one global simultaneity candidate.

The institutional itinerary is not treated as direct manuscript evidence. Manuscript folios and the letter patent still require archival, facsimile or critical-edition locators before their atomic Claims can be reviewed. No RCT or manuscript image is copied.

## Fail-closed rules

- Candidate historical geometry is `null`.
- Every inter-place trajectory gap is `unknown_route` and has no line.
- The Duchy Region is not a modern administrative polygon.
- Candidate day precision remains draft where direct locators are missing.
- No stored Relation is allowed while #331 is paused.
- Candidate assertions are not READY and cannot be promoted.
- Unknown cost is `null`, not an estimate.
- Absence from the package never means historical absence.

## Validate

```bash
python scripts/validate_leonardo_world_slice.py
python -m pytest -q tests/test_leonardo_world_slice.py
```

## Next gate

Close manuscript/patent locators, review the atomic Claim/Evidence/Uncertainty inventory, then create the non-public historical World Model projection. Two independent reviews are required before READY.
