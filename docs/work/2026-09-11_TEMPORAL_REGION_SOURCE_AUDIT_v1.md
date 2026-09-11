# Temporal Region proof — source feasibility and bounded implementation audit v1

- Date: 2026-09-11
- Owner: issue #355
- Status: bounded implementation branch; not merged or published
- Decision context: [Gate E owner bypass and bounded Temporal Region universality proof](2026-09-10_GATE_E_OWNER_BYPASS_AND_REGION_PROOF_v1.md)

## Source feasibility result

Source feasibility is **established for a bounded proof**, not for a complete
Roman Empire historical corpus. The proof uses the public Cliopatria release at
commit `ad28a691b7c07c1fca89d0e0636d324667d2a258`, archive member
`cliopatria_polities_only.geojson` in `cliopatria.geojson.zip`.

- Repository: <https://github.com/Seshat-Global-History-Databank/cliopatria>
- Dataset release: <https://zenodo.org/records/13363121>
- Method/source description: Bennett et al., *Scientific Data* 12 (2025),
  DOI <https://doi.org/10.1038/s41597-025-04516-9>
- License: CC BY 4.0; attribution and change notice are retained in
  `fixtures/world_slices/roman_empire_region/v1/source_manifest.json`.

The selected rows are one `Roman Empire` polity (`Wikidata=Q12544`,
`SeshatID=it_roman_principate`) with non-overlapping native inclusive CE year
intervals: 91–105, 106–113 and 114–116. All three use the same political
territory concept and the same published reconstruction method. The checked-in
excerpt is unchanged source geometry; `source_manifest.json` records feature
locators and digests.

The source is explicitly approximate. The paper describes hand-redrawn source
maps, raster-to-polygon conversion, coarse resolution and smoothing, and notes
coastline alignment and border uncertainty limits. ARTEMIS therefore preserves
year precision, marks geometry as scholarly reconstruction, does not interpolate
between snapshots, and does not interpret unselected time as historical absence.

The repeatable operation is intentionally narrow: `scripts/build_temporal_region_inputs.py`
verifies the pinned excerpt and maps it into one canonical Entity/Region package.
It does not download data, repair borders, infer dates, or provide a generic
ingestion framework. `tests/test_temporal_region_proof.py` exercises the
verification, comparability rejection, temporal projection and artifact build.

## Architecture classification

**A — already generic:** World Model `Entity`/`State`/`Region`, temporal geometry
versions, Claims → EvidenceLinks → Sources, Explorer State, Render Projection,
MapLibre GeoJSON projection and the existing Globe renderer.

**B — Leonardo-specific plumbing:** Life Path presence/timeline controls and
their `Range`/`Scrub` semantics. They remain the default Leonardo path and are
not reused as a second Region timeline.

**C — minimal proof boundary:** a build-time source adapter and a hidden-by-
default semantic time selector for non-Life-Path datasets. The selector changes
the shared canonical Explorer State and reloads the precomputed projection; it
does not create Roman-specific time, renderer or state logic.

## Technical disposition

The bounded proof supports **GENERALIZES (technical only)**: changing the
canonical time selects a different temporally valid Region geometry through the
existing projection and Globe adapters. This does not establish Gate E user
value, product readiness, or historical exactness. E1/E2 remain NOT COLLECTED
and formal user value remains UNVALIDATED under the owner decision.

The artifact is review-only and remains unpublished. Leonardo’s published
default remains unchanged pending a separate publication decision.
