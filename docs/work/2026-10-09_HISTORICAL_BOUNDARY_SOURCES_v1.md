# Historical polity boundaries — source comparison v1

Date: 2026-10-09. Research-only response to the owner's question about boundaries of all known states through history. No source/corpus intake, runtime geometry or temporal expansion is authorized by this report.

## Finding and evidence

**A usable broad starting dataset exists; complete exact coverage is not established.** Neither the available source descriptions nor ARTEMIS's existing three Roman records prove coverage of every known polity, year or disputed territorial interpretation. Treat political territory as a source-attributed reconstruction with its own dates and limitations, not an exhaustive world partition. A polity is not necessarily a modern sovereign state.

Primary sources checked on 2026-10-09:

| Dataset | Reported coverage and format | Rights stated by provider | ARTEMIS suitability and limits |
| --- | --- | --- | --- |
| [Cliopatria](https://github.com/Seshat-Global-History-Databank/cliopatria) | 3400 BCE–2024 CE; over 1,600 political entities and approximately 14,000 records; GeoJSON EPSG:4326, native inclusive FromYear/ToYear intervals; differing temporal/spatial sampling | [CC BY 4.0](https://github.com/Seshat-Global-History-Databank/cliopatria/blob/main/LICENSE.md), attribution and change notice | Preferred broad candidate. Provider explicitly acknowledges uncertain borders and alternative territory/name/duration interpretations. Intervals indicate source applicability, not exact border-change observations. POLITY and RELATION records must be distinguished. |
| [CShapes 2.0 / CShapes-Europe](https://icr.ethz.ch/data/cshapes/) | States/dependent territories, 1886–2019; Europe from 1816. GeoJSON and other GIS formats. Two state codings: Gleditsch/Ward and Correlates of War | Provider states CC BY-NC-SA 4.0 | Useful modern-period comparison; neither ancient coverage nor unrestricted commercial reuse. Keep this dataset out of the current public runtime pending an explicit rights/scope disposition. |
| [OpenHistoricalMap](https://www.openhistoricalmap.org/copyright) | Collaborative historical geospatial database; this inspected page does not establish a complete state/year coverage matrix | CC0 except individual features with other licenses, including CC BY/CC BY-SA; per-feature license tags matter | Supplement for particular areas/periods after source/feature inspection. Do not treat default CC0 as a blanket license for every element. Coverage and source quality must be assessed per proposed subset. |

Cliopatria's [method publication](https://doi.org/10.1038/s41597-025-04516-9) is already identified in the repository's [Roman source audit](2026-09-11_TEMPORAL_REGION_SOURCE_AUDIT_v1.md). The direct publisher page was inaccessible during this session; no new claim here relies on an uninspected passage from that paper. The provider README/license and ETH/OHM pages above were retrieved directly. Counts/coverage are provider descriptions, not independently counted or completeness-verified results.

## Existing implementation versus proposed direction

ARTEMIS already pins Cliopatria commit `ad28a691b7c07c1fca89d0e0636d324667d2a258` and three Roman Empire reconstructions: 91–105, 106–113, 114–116 CE. Existing source manifests, locators, rights, approximate reconstruction and unknown status remain authoritative. No original excerpt/package was changed.

The current shared calendar supports CE 91–1519 only. Cliopatria's negative BCE years, additional modern years and native identity/RELATION rows do not automatically fit that runtime. A broad dataset cannot be inserted by silently widening the slider or interpreting imported IDs as canonical political identities.

## Recommended next candidate — not implementation authority

Prefer one pinned, small Cliopatria **POLITY-only subset for Italy around 1502**, chosen for geographic/temporal relevance to the existing Leonardo loop. First count actual available rows and record gaps; do not assume particular states are present or that the result covers all Italian territory. Retain native polygons/intervals and source identities; compare with existing Entity/Region/temporal-version/source/uncertainty contracts before proposing intake. Overlapping interpretations or gaps remain explicit and must not be repaired by union, interpolation or invented borders.

This is the minimum useful follow-up to evaluate whether contextual boundaries help the current research loop. A universal corpus, full BCE/modern calendar and multi-provider reconciliation would add substantial scope before that value is known. The current session stops at this comparison and candidate; a separate accepted source/intake specification is required before any download/promotion/runtime integration.

## Verification limits

Verified: provider descriptions and stated licenses; comparison with existing repository source audit and shared runtime calendar. Not verified: full dataset bytes/current release hash, complete polity coverage, date/geometry correctness, feature-level OHM licenses or historical acceptance. No live source queries or imported geometry were added to visitor sessions.

Independent verdict: `ACCEPT_RESEARCH_COMPARISON` by `/root/hierarchy_review`, after checking the cited primary-provider descriptions and licenses directly. This accepts the bounded comparison, not source intake or historical truth.
