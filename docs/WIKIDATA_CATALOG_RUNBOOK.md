# Wikidata pilot catalog: use and maintenance

The ready catalog adds ten selected London architectural structures or complexes
to the existing shared Explorer. Visitors search and inspect the prepared layer;
they do not need to enter a Wikipedia link, register, or fill an editor form.
This selected pilot does not claim comprehensive London coverage.

## Visitor path

Open the Globe or Region entry, enable the London pilot catalog layer if a saved
URL has it disabled, and search by name, original-language alias or Wikidata QID.
Select a result to inspect its source revision. Search changes only the visible
record chooser, not map membership, camera, selected record or time. Use the
explicit focus action to move the map to the selected point. Globe and 2D use
the same shared environment and records.

The point is the location reported by a particular Wikidata revision. Its
measurement accuracy, site extent, historical position and existence period have
not been independently established. Source numeric precision is retained as
metadata, not a guarantee of accuracy. Imported references are outside historical
time filtering. Native dates are accessible as raw source metadata and never
silently become lifespans. Wikipedia links are context navigation, not independent
corroboration. There is no confidence score or verified badge.

## Frozen package and offline verification

The owned package is `fixtures/source_catalog/london_architecture/v1/`:

- `selection.json`: the exact ten prospective QIDs and one excluded source QID;
- `snapshots/*.json`: full downloaded EntityData JSON bytes, including original
  languages, aliases, sitelinks, ranks, qualifiers and references;
- `manifest.json`: byte hashes, revisions, source modification/retrieval times,
  request/revision URLs and the unchanged 31-record Atlas duplicate-check guard;
- `catalog.json`: deterministic normalized reference package, checked against the
  raw captures on every build.

From the repository root, with the project's Python environment:

```bash
python scripts/import_wikidata_catalog.py verify
python -m pytest tests/test_wikidata_catalog.py -q
```

Verification and catalog rebuilding require no external request. Input tampering,
cohort drift, revision mismatch, existing-object identity/name/sitelink duplicates,
ambiguous or qualified/non-Earth coordinates, and invalid coordinates/precision
fail closed. Repeated verification leaves source bytes unchanged and produces the
same catalog bytes. The shared builder includes this package in its source ledger.

The captured Q193639 Royal Albert Hall statement has negative coordinate precision
`-1e-06` and is retained solely as exclusion evidence. It is not a rendered item.
No absolute-value repair or inferred replacement occurs. Banqueting House Q642039
was prospectively selected in its place. Westminster Palace, Kensington Palace
and Banqueting House have no underlying references on their captured coordinate
statements; the importer preserves that absence.

## Explicit capture and comparison

Capture is an operator maintenance command, not a visitor action or scheduled job.
It requests only the prospective ten QIDs plus the excluded audit QID. Supply a
**new directory**, preferably outside the checkout during review:

```bash
python scripts/import_wikidata_catalog.py capture --output ../ARTEMIS-catalog-candidate
python scripts/import_wikidata_catalog.py diff fixtures/source_catalog/london_architecture/v1 ../ARTEMIS-catalog-candidate
```

Existing output directories are rejected before requests or writes. A failed
capture may leave a partial directory for diagnosis; it is not a verified package
and never substitutes for the published inputs. Fix the reported issue and choose
another fresh directory. Do not overwrite old captures.

Diff reports QIDs added/removed and changes of source revision or raw source bytes.
A repeated capture of identical revisions/bytes is not reported as a source change
merely because its retrieval timestamp is newer. Review source changes separately;
capturing a candidate never updates the public bundle. Any failed or ambiguous
cohort item stops normalization; a replacement or cohort expansion requires a new
prospective scope decision. Existing Atlas changes likewise require a new reviewed
duplicate-check guard, not hand editing the manifest to bypass a failure.

The capture uses HTTPS EntityData, an identifying User-Agent with repository
contact, JSON/gzip, serial bounded reads, 30-second request timeout and up to three
attempts for HTTP 429/503 with bounded Retry-After/backoff. Responses are limited
to 16 MiB after decompression. Backoff exceeding 60 seconds stops the operation
for a later operator retry. It uses no credentials and writes nothing to Wikimedia.
The browser, normalizer and release checks never fetch Wikidata live.

## Data meaning and rights

Each row has stable identity `catalog:wikidata:QID`. The native P625 statement,
including its references, is retained. A source-relative Claim says that the pinned
revision reports a coordinate; `origin=imported`, `review_state=draft`,
`confidence=unknown`, `evidence_state=missing`. The linked Source and EvidenceLink
also remain draft. Deterministic extraction/technical acceptance does not certify
underlying facts or reference quality.

Wikidata structured entity data uses CC0-1.0. This package does not copy Wikipedia
article prose, photographs or external reference-page content; CC0 does not license
those resources. Original multilingual names are preserved without AI translation.

Official access and rights guidance:

- [Wikidata data access](https://www.wikidata.org/wiki/Wikidata:Data_access):
  full EntityData, revision pinning, small-batch API access and access etiquette.
- [MediaWiki API etiquette](https://www.mediawiki.org/wiki/API:Etiquette):
  descriptive User-Agent, caching, serial/grouped requests, gzip and Action API maxlag.
- [Wikidata licensing](https://www.wikidata.org/wiki/Wikidata:Licensing).

This package uses EntityData; Action API maxlag applies if an operator later uses
that separate API. No paid hosting, Render resource, live universal corpus,
relations, editorial-publication promotion or user-value validation is implied.
