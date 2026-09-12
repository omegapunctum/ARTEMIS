# Temporal Region proof — source feasibility and bounded implementation audit v1

- Date: 2026-09-11
- Owner: issue #355
- Original 2026-09-11 status: bounded implementation branch; not merged or published
- Current status (2026-09-12): merged in #421; Region artifact remains unpublished
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

## Post-merge closeout — 2026-09-12

PR #421 merged at `5875498b0d8febbdadbd036ec703908408ff8ae4`.
The source/implementation audit above is preserved; GENERALIZES remains a
bounded technical finding, not proof of universal domain coverage or user value.

Exact-merge CI succeeded:

- [Core 34684007001](https://github.com/omegapunctum/ARTEMIS/actions/runs/34684007001).
- [Globe Boundary 34684006999](https://github.com/omegapunctum/ARTEMIS/actions/runs/34684006999).
- [Geospatial 34684007028](https://github.com/omegapunctum/ARTEMIS/actions/runs/34684007028).
- [Globe/browser 34684006973](https://github.com/omegapunctum/ARTEMIS/actions/runs/34684006973),
  including a 1440×900 Region capture and temporal Region browser assertions.
  Artifact: [artemis-globe-runtime-spike](https://github.com/omegapunctum/ARTEMIS/actions/runs/34684006973/artifacts/10294708665).
- [Pages 34684871951](https://github.com/omegapunctum/ARTEMIS/actions/runs/34684871951)
  succeeded after configuration recovery. The owner reports that the public
  site works; this is not a report of Region artifact acceptance.

Pages publishes the Leonardo default, not the separately generated Region proof.
The next bounded action is owner review of this existing Region artifact and an
explicit publication decision. Review should check the three periods 91–105,
106–113 and 114–116 CE, changing outlines, source/license access and approximate
reconstruction wording. It must not interpret omitted years as historical
absence or changes in snapshot geometry as precise boundary-change dates.

Stop implementation here unless review identifies a concrete material gap.
No additional state, new feature, Global/Focus timeline, participant session or
Gate E pass is opened. E1/E2 remain NOT COLLECTED under the accepted bypass;
formal user value remains UNVALIDATED.

## Separate Region publication decision — 2026-09-12

After #422 closeout, the owner explicitly confirms merge and publication of the
existing bounded Region proof at `/ARTEMIS/region/` for interactive review.
This is the separate publication authorization required by #420; it supersedes
the earlier publication hold, not the source/uncertainty or user-value limits.

Pages builds `roman_region_proof` with `--public-preview` into its own `region`
directory. Leonardo remains the default on `/globe/`; root and Atlas routing
stay unchanged. Public build metadata and labels describe a research preview.
No historical data, coordinates, runtime interaction, new temporal state or
Global/Focus implementation is introduced. Rollback is removal of the Region
build step and redeployment, leaving Leonardo intact.

Merge/deployment require green CI. Verify the resulting Pages deployment and
`/ARTEMIS/region/build-meta.json` before reporting publication complete. The
owner's screenshot-level confirmation does not substitute for an interactive
review: switching the three source-native periods and inspecting provenance
remain the next check. E1/E2 NOT COLLECTED; formal user value UNVALIDATED.
