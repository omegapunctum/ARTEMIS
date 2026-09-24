# ATL.1466.1 / fol. 733 verso — conflict evidence package v1

- Package ID: `atl-1466-1-733v-dating-attribution-v1`
- Research review date: 2026-09-24.
- Baseline: `main` at `fbe1815cf3932369f1858ad21cb3fc0fa5165493` (PR #450).
- Authority: `docs/work/2026-09-24_EPISTEMIC_CONFLICT_PROOF_AUTHORIZATION_v1.md` and its accepted v1.1 specification.
- Scope: one artifact, two attributed dating assertions. Non-public research/curation package; no runtime import, publication, Range/Scrub membership or lifecycle-state change.

## Identity and exact subject

**Artifact identity:** Codex Atlanticus, Museo Galileo catalogue key `ATL.1466.1`, Marinoni fol. 733 verso (Pedretti 733 verso; former Hoepli 271 verso d). This is one artifact identity, not two date-specific copies.

**Common dated subject:** the architectural studies/drawings **on fol. 733 verso concerning a centrally planned church and referable to the plan of San Lorenzo in Milan**. The Heydenreich position, as reported by Cordera in the catalogue, concerns the *other architectural drawings* referable to that Milanese building; Pedretti's reproduced note dates the architectural studies on this theme, and the catalogue's account of his reasoning expressly encompasses the drawings on the folio. Their asserted dating scopes therefore overlap on this thematic group. This does not identify an individual mark or claim that every drawing, annotation, crane sketch, geometric study, physical paper support or Codex entry has both attributed dates. The catalogue does not enumerate every included mark; no image-level segmentation is reviewed.

**Nature of conflict:** alternative scholarly datings of that bounded group; neither production date is established by this package. The date expressions are source-native, approximate, and left unresolved.

## Institutional Source S-MG-733V

- Identity: Museo Galileo, `leonardo//thek@`, **Codice Atlantico Foglio: 733 v**, catalogue entry `ATL.1466.1`; critical notes attributed on the entry to Carlo Pedretti [1979] and Paola Cordera [2010].
- Type: curated institutional scholarly catalogue, mediating attributions to named researchers; the reproduced Pedretti note is still accessed through the catalogue.
- Stable entry URL: https://teche.museogalileo.it/leonardo/foglio/index.html?lang=it&num=ATL.1466.1
- Version/revision: no per-entry publication revision or stable text checksum supplied by the catalogue. The indexed institutional entry was checked on 2026-09-24; the result reports a crawl approximately three months earlier. A current direct page-text retrieval was unavailable through this research environment. The section headings, author labels, table rows and distinctive passage descriptions below are the reproducible locators. Recheck against the live catalogue on review if its text changes.
- Bibliography **reported by**, but not directly inspected independently of, this entry: L. H. Heydenreich, “Studi archeologici di Leonardo da Vinci a Civitavecchia,” *Raccolta Vinciana* XIV (1934), 39–53; C. Pedretti [1979] catalogue note for fol. 733v, cited in entry bibliography as *Pedretti 1978–79*, sub numero / p. 92; C. Pedretti (1962), p. 88, cited for the two-period discussion. These references are provenance pointers, **not** direct Sources/EvidenceLinks in this package.
- Reviewed scope: attribution table and the Pedretti/Cordera critical-note passages specified below, not the entire catalogue or any linked edition. Source review state within this scope: `reviewed`.

## Claim H — one atomic mediated attribution

| Field | Reviewed value |
|---|---|
| ID | `claim-atl-1466-1-733v-heydenreich-date-v1` |
| Subject | The common architectural drawing group defined above |
| Statement | The Museo Galileo catalogue reports Heydenreich's attribution of that group to `c. 1490`. |
| Claim kind / origin | `factual` report of a scholarly attribution / `curator`; **not** an assertion that the drawings were in fact made in 1490 |
| Review / evidence state | `reviewed` in the attribution scope / `supported` by reviewed EvidenceLink H |
| Confidence | `medium`: explicit catalogue date row and explanatory note, with direct Heydenreich passage uninspected and thematic group not segmented mark by mark |
| Uncertainty | Approximate source-native date; unresolved conflict with P on historical dating; mediated provenance and group-scope limits |
| Temporal query envelope | `unresolved / not provided for v1`; no exact-year normalization |

**EvidenceLink H — `evidence-atl-1466-1-733v-heydenreich-v1`:**
`claim_id=claim-atl-1466-1-733v-heydenreich-date-v1`;
`source_id=S-MG-733V`;
`relation_to_claim=supports`;
`evidence_strength=direct` **for the narrow reported-attribution Claim only**;
`review_state=reviewed`.
Locator: entry URL above → “datazione proposta” table → row “Heydenreich, Ludwig H. [1934] | c. 1490”; then “Note Critiche” → “Cordera, Paola [2010]” → paragraph on the *other architectural drawings* of the Milanese building that explains why Heydenreich referred them to 1490. This link does not provide direct inspection of Heydenreich's publication.

## Claim P — one atomic mediated attribution

| Field | Reviewed value |
|---|---|
| ID | `claim-atl-1466-1-733v-pedretti-date-v1` |
| Subject | **The same** common architectural drawing group |
| Statement | The Museo Galileo catalogue reports Pedretti's attribution of the architectural studies on this theme to `c. 1514-15`. |
| Claim kind / origin | `factual` report of a scholarly attribution / `curator`; **not** an assertion that the drawings were in fact made in 1514–1515 |
| Review / evidence state | `reviewed` in the attribution scope / `supported` by reviewed EvidenceLink P |
| Confidence | `medium`: explicit date row and catalogue reproduction of the Pedretti note; original edition not independently inspected |
| Uncertainty | Approximate source-native range, unresolved conflict with H on historical dating, mediated provenance |
| Temporal query envelope | `unresolved / not provided for v1`; no closed 1514–1515 bounds |

**EvidenceLink P — `evidence-atl-1466-1-733v-pedretti-v1`:**
`claim_id=claim-atl-1466-1-733v-pedretti-date-v1`;
`source_id=S-MG-733V`;
`relation_to_claim=supports`;
`evidence_strength=direct` **for the narrow reported-attribution Claim only**;
`review_state=reviewed`.
Locator: entry URL above → “datazione proposta” → “Pedretti, Carlo [1979] | c. 1514-15”; “Note Critiche” → “Pedretti, Carlo [1979]” → opening lines with `c. 1514-15` and description of architectural studies on a centralized church resembling the plan of San Lorenzo in Milan. For the catalogue's account of the reasoning, “Note Critiche” → “Cordera, Paola [2010]” → paragraph discussing Pedretti (1962, p. 88), the two-period possibility and his conclusion that the drawings/annotations are assignable to one Roman-period epoch. This is a **catalogue-mediated account**, not a verified direct reading of Pedretti 1962 or 1979.

## Conflict and qualifier

- Existing semantics: the two `factual` Claims report what each scholar is attributed as saying. Each is `reviewed` and `supported` **as an attribution**; neither entails a supported historical-production-date Claim. Record `source_conflict` uncertainty **on the underlying dating question** with references to H and P, and `date` uncertainty **inside** each approximate expression. The attributed alternatives have no selected winner, combined interval, midpoint or probability. A `challenges` EvidenceLink between the attribution reports would falsely suggest that one report disproves the other.
- Two-period qualifier, **conditional and historically considered, not a third dating**: the catalogue's Cordera [2010] note reports that Pedretti examined the possibility that the sheet was used at two different times, then argued the drawings and notes belong to the same Roman-period epoch. Locator: S-MG-733V → “Note Critiche” → “Cordera, Paola [2010]” → sentence beginning “Dopo aver esaminato la possibilità che il foglio fosse stato utilizzato in due tempi diversi” and its conclusion citing Pedretti (1962, p. 88). It is a reported discarded possibility, not proof of use in two periods and not an ARTEMIS reconciliation of H and P. No third Claim or EvidenceLink is created for this note.
- `query_envelope` for H and P: **unresolved / not provided for v1**. Their source-native strings remain `c. 1490` and `c. 1514-15`. No numerical `±N`, exact 1490, bounded query interval, continuous 1490–1515 period or Range/Scrub membership is supplied.

## Research review record and limitations

- Review ID: `research-review-atl-1466-1-733v-v1-20260924`.
- Reviewer: ARTEMIS Research agent; scope: entry identity, two catalogue attributions, a narrow common subject, locator-to-Claim fit, existing Claim/EvidenceLink/Uncertainty classification and conditional qualifier. Status of this **bounded source/Claim review**: `reviewed`. This is an explicitly scoped research review, **not** an independent human or second reviewer acceptance and not a historical finding of either production date.
- Method: checked the indexed text of the named Museo Galileo entry, its dating table, Pedretti [1979] note, Cordera [2010] note and its bibliographic pointers; compared the two described drawing scopes; checked classification against `docs/EPISTEMIC_CONTRACT.md` v3.0 and source-native temporal handling against `docs/UNCERTAINTY_SEMANTICS_CONTRACT.md` v1.0. Direct linked publications and image-level delineation were **not** checked.
- Provenance limit: both EvidenceLinks cite **one catalogue Source at two separate locators**, not two independently inspected scholarly publications. Catalogue revision and direct-publication textual variants remain unknown.
- This package is reviewable evidence for the already-authorized bounded proof; no runtime/published Claim, historical date choice, canonical semantics change, product value claim or approval for an implementation merge follows from its existence. On `main`, the `EVIDENCE_CLOSURE_REQUIRED` gate remains until this package is accepted and merged. Any human acceptance required by the governing REVIEW workflow must be recorded before the later implementation merge.
