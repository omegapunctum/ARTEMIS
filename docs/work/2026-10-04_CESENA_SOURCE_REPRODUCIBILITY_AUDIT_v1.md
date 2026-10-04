# Cesena source reproducibility audit v1

Status: completed read-only research / **WORDING_OR_LOCATOR_DISCREPANCY**. Date/place/folio binding reproduced; the complete Claim wording is not reproduced at the selected locator. This is a wording-scope limitation, not a locator error or a determination that the Claim is historically false.

Authority: the owner's 2026-10-04 continuation executes the one-source read-only candidate prepared in [the completed source-aware task](2026-10-03_SOURCE_AWARE_RESEARCH_LOOP_v1.md#limits-stop-and-one-next-candidate). This research does not reopen historical evidence review or authorize a frozen edit. Classification: bounded read-only research, independently inspected before publication; any subsequent knowledge correction remains DECISION under the relevant owner/change-control path.

## Scope and reproducible access

Repository base: main `15c9c29c6013cc13b2ba4f93662b3205acb87d67`, tree `c067951caa754e1857396c2fcc6be2de88323cc8`.

| Item | Existing identity/value |
|---|---|
| Claim | `claim-cesena-presence-1502-08-10` |
| Statement | Leonardo was present in Cesena by 10 August 1502 in the selected survey context. |
| EvidenceLink | `evidence-cesena-uniurb-f46v` |
| Source | `source-uniurb-volpe-chronology` |
| Locator | Printed p. 16; chronological Cesena entry; Manuscript L folio 46v |
| Recorded Claim status | draft / unknown / missing |
| Recorded EvidenceLink status | draft |

Official source: Gianni Volpe, *Cronologia vinciana (1502–1503)*, in *Leonardo a Urbino*, Urbino University Press, 2023, pp. 7–27. [Registered PDF](https://press.uniurb.it/index.php/urbinoelaprospettiva/catalog/download/34/75/236?inline=1). Research agent retrieval: 2026-10-04 04:06:17 UTC, HTTP 200, application/pdf, 224671 bytes; SHA-256 `103262db506c3de5303441e2ccffd684472a42b6d1ff73f42babd89db607068c`. PDF has 21 pages; printed p. 16 is PDF page 10 (zero-based index 9). Research agent rendered and visually inspected that page; orchestrator independently opened the official PDF and inspected its page screenshot/text. Reproduction is retrieval of the publication, not inspection of the manuscript original.

## Literal comparison

The dated chronology entry assigns Leonardo's presence in Cesena to 10 August. Its embedded manuscript quotation is: “alla fiera di Santo Lorenzo a Cesena 1502”; the citation identifies ms. L, f. 46v. The numeric day/month is Volpe's chronology heading, rather than a literal numeral in that quoted manuscript phrase.

| Component | Result |
|---|---|
| Leonardo / Cesena / 1502 | Reproduced in the entry and its attribution |
| By 10 August 1502 | Compatible with the publication's dated presence entry; no arrival time or earlier duration established |
| Printed p. 16 / L 46v | Reproduced; printed and PDF pagination distinguished |
| Selected survey context | Not established by this dated entry: it concerns a fair. Note 27 mentions Cesena surveys generally but does not bind them to 10 August or 46v |

Thus the presence/date/folio subset matches, while calling the whole statement REPRODUCIBLE_MATCH would overstate the locator's scope. The initial Research shorthand for the subset is superseded by the whole-Claim outcome above. No unrelated source or folio is borrowed to complete it.

## Preservation, independent review and stop

The separate `claim-cesena-survey-folios-9r-10r` remains rejected / low / missing. Its rejection does not assert historical falsity; this audit supplies no independent manuscript verification for that association. No Claim, EvidenceLink, source registry, confidence, review status, temporal value, geometry or frozen-package byte is changed. Source rights remain citation/factual use only; the PDF, rendered page and manuscript images are not republished in the repository.

Research agent `/root/engineering_audit` independently retrieved/inspected the official page and corrected its subset-match shorthand after whole-Claim scope review. Product agent `/root/product_direction` independently checked the full statement and rejected-Claim separation. Independent final documentation review is recorded on the exact PR head before merge.

Stop after this source and comparison. A future correction proposal would need the frozen package's own change-control path and independently reviewed evidence; this result does not authorize it, broader Claim auditing, source substitution or status promotion. Gate E closed, contextual composition DEFERRED, conflict proof non-public and formal/comparative value UNVALIDATED remain unchanged.
