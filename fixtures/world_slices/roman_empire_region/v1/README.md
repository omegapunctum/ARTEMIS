# Roman Empire bounded Temporal Region proof fixture

This fixture is a source-first, review-required input for the bounded universality
proof described in `docs/work/2026-09-10_GATE_E_OWNER_BYPASS_AND_REGION_PROOF_v1.md`.
It contains one canonical Roman Empire Entity and exactly three selected
Cliopatria polygon/multipolygon snapshots:

| State | Native source interval | Source identity |
| --- | --- | --- |
| 1 | 91–105 CE | `Name=Roman Empire`, `Wikidata=Q12544`, `SeshatID=it_roman_principate` |
| 2 | 106–113 CE | same identity |
| 3 | 114–116 CE | same identity |

The snapshots use the same political-territory concept and the same published
Cliopatria reconstruction method. They are not exact borders: the source paper
describes hand-redrawn source maps, coarse raster-derived polygons and smoothing.
The fixture keeps the source's inclusive year precision, does not interpolate
between intervals, and does not treat missing coverage as historical absence.

`source_manifest.json` pins the upstream repository commit, archive member,
CC BY 4.0 license, attribution, feature locators and exact feature digests.
`sources/cliopatria-excerpt.json` is an unchanged, reviewable excerpt. Run:

```bash
python scripts/build_temporal_region_inputs.py --verify-excerpt
```

To verify against a separately downloaded upstream archive, pass its path to
`--verify-upstream`. The archive is intentionally not vendored in ARTEMIS.

This is not a complete Roman Empire corpus, a product publication, a Gate E
user-value result, or a claim that the reconstructed borders are uncontested.
