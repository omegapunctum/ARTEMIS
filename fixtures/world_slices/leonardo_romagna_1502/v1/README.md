# Leonardo-in-Romagna World Slice 1502 — scope package v1

Status: `SCOPE_FROZEN / CURATION IN PROGRESS / NON-PUBLIC`.

Issues: [#355](https://github.com/omegapunctum/ARTEMIS/issues/355), [#332](https://github.com/omegapunctum/ARTEMIS/issues/332) and [#360](https://github.com/omegapunctum/ARTEMIS/issues/360).

## Purpose

This package freezes the smallest current content boundary for the first real ARTEMIS Globe MVP slice. It is a curation contract, not a READY historical dataset.

The analytical window is 8 August–31 December 1502. The selected candidate story contains:

- dated or datable contexts at Rimini, Cesena, Cesenatico and Imola;
- commissioned engineering service and a bounded surveying/fortification Process;
- a presence-only Trajectory with three explicit unknown-route gaps;
- a geometry-withheld Duchy of Romagna Region with two source-bound temporal states plus explicit title-based and documented-place-only alternatives using canonical reconstruction modes;
- one sparse Safavid State plus one year-precision Ottoman displacement Event for global simultaneity.

Every date, place, State and Region version remains a candidate until it is represented by atomic Claims, reviewed EvidenceLinks and reproducible locators.

## Files

| File | Role |
|---|---|
| `selection_manifest.json` | frozen time/space/layer/object boundary and relation/geometry policy |
| `source_registry.json` | institutional/scholarly source candidates, locators, intended Claim scope, access, text/media and derived-geometry rights |
| `claims_manifest.json` | atomic draft Claims, candidate EvidenceLinks and explicit Uncertainty bindings |
| `coverage_manifest.json` | explicit corpus limits, material gaps and exit conditions |
| `curation_cost.json` | measured activities plus explicit null history superseded by one measured full recuration; unknown time is never estimated |
| `review_artifact.schema.json`, `review_registry.schema.json`, `gate_c_decision.schema.json` | fail-closed Git/digest/chronology contract for two same-revision reviews and the final gate decision |
| `*.schema.json` | closed Draft 2020-12 structural contracts |
| `scripts/validate_leonardo_world_slice.py` | semantic fail-closed validator |
| `tests/test_leonardo_world_slice.py` | positive and controlled-corruption regression tests |

## Current evidence boundary

Candidate evidence comes from institutional catalogues/references and scholarly publications:

- [Museo Galileo Manuscript L](https://brunelleschi.imss.fi.it/genscheda.asp?appl=LIR&chiave=100790&lingua=ENG&xsl=manoscritto) for manuscript identity and the 1502 engineering context;
- [Urbino University Press — Gianni Volpe, *Cronologia vinciana (1502–1503)*](https://press.uniurb.it/index.php/urbinoelaprospettiva/catalog/download/34/75/236?inline=1), printed p. 16, for the dated Manuscript L locators `78r`, `46v`, `66v` and the complete letter-patent transcription at note 26;
- [Visit Romagna](https://visitromagna.it/en/leonardo-da-vinci-and-cesare-borgia-ingenuity-and-intellect-at-the-service-of-the-duchy) for candidate dates, itinerary sections and folio references;
- Royal Collection Trust items [912284](https://www.rct.uk/collection/912284/a-map-of-imola) and [912686](https://www.rct.uk/collection/912686/recto-sketches-of-the-street-plan-of-imola-verso-notes-on-mathematics);
- [Comune di Imola Musei Civici](https://museiciviciimola.it/rocca-sforzesca-imola/luogo-rocca-sforzesca-imola-imola/) for the consultation and political-transition context;
- [Getty TGN Imola](https://www.getty.edu/vow/TGNFullDisplay?find=&nation=&place=&subjectid=7004864) under ODC-By 1.0;
- [The Met](https://www.metmuseum.org/toah/hd/isru/hd_isru.htm) for the sparse global State candidate;
- [Atçıl, Cambridge University Press, DOI 10.1017/S002074381700006X](https://doi.org/10.1017/S002074381700006X), printed p. 298 and note 13, for the year-precision global Event candidate.

The institutional itinerary is not treated as direct manuscript evidence. The university-press chronology closes the bibliographic locators for the dated Rimini (`78r`), Cesena (`46v`) and Cesenatico (`66v`) entries and for the 18 August patent. The separate Cesena wall-survey association with folios `9r–10r` lacks a direct facsimile or critical-edition binding and is explicitly `rejected` from the supported Gate C Claim set without being declared historically false. All EvidenceLinks remain draft pending content review. No RCT, patent or manuscript image is copied.

The package contains 17 candidate objects, 10 registered sources, 22 atomic Claims, 38 EvidenceLinks and 11 provenance-bearing Uncertainty records. Every candidate object has at least one atomic Claim target. Source access, text/data use, image reuse and derived-geometry use are separate fields.

## Fail-closed rules

- Candidate historical geometry is `null`.
- Every inter-place trajectory gap is `unknown_route` and has no line.
- The Duchy Region is not a modern administrative polygon.
- Two source-bound Region states expose temporal change without fabricating dates or boundaries.
- Both Region alternatives answer one explicit reconstruction question, use canonical reconstruction modes and keep geometry `null`.
- Candidate day precision remains draft where direct locators are missing.
- No stored Relation is allowed while #331 is paused.
- Candidate assertions are not READY and cannot be promoted.
- Historical unmeasured cost is `null`, not an estimate, and is superseded only by a measured full recuration.
- Absence from the package never means historical absence.

## Validate

```bash
python scripts/validate_leonardo_world_slice.py
python -m pytest -q tests/test_leonardo_world_slice.py
```

## Next gate

Independently re-review the corrected frozen Claim/Evidence/Uncertainty inventory and Git-bound gate-transition guards, then record exactly one `FREEZE`/`NARROW`/`REJECT` decision. Two earlier review rounds returned `CHANGES_REQUIRED`; two independent `READY` reviews on one corrected frozen revision are required to close Gate C.
