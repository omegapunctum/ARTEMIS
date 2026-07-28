# Gate A research-module package

## Status

- Issue: `#322`.
- Package status: `READY`.
- Scope: exactly three deep modules, their hidden calibration revisions, citation-ready reference Briefs and independent-review registry.
- Authority: working validation evidence only; this directory does not change public data, target schema or canonical product rules.

## Package

| Module | Question family | Structured artifact | Hidden reference Brief |
|---|---|---|---|
| A | precedent and architectural reinterpretation | `modules/module_a.json` | `briefs/module_a_reference_brief.md` |
| B | modernism, program and post-war public architecture | `modules/module_b.json` | `briefs/module_b_reference_brief.md` |
| C | Gothic classification, transmission and independent development | `modules/module_c.json` | `briefs/module_c_reference_brief.md` |

Each module records:

- 4–6 selected Features and rationale;
- 4–6 lenses;
- 6–10 atomic Claims with independent epistemic axes;
- Source records and claim-level EvidenceLinks with reproducible locators;
- at least two substantive RelationClaims;
- challenging, limiting or medium-confidence evidence;
- explicit uncertainty;
- a commit-pinned immutable reference revision and Saved View;
- preparation/review cost without fabricated estimates.

Module-candidate Features have scoped UUID v4 identities here but are not silently added to the public corpus.
`preparation_log.json` preserves the shared implementation session, correction-only sessions, reviewer-rejected short verification passes and a new full measured replacement curation for every module. `recuration_checklists.json` enumerates every Claim, EvidenceLink, counted Relation and Source covered by those new sessions; the validator checks the IDs, source-to-locator mapping and timestamp arithmetic. Earlier source discovery remains explicitly unmeasured rather than being reconstructed after the fact.

## Review boundary

`preparation_state=curator_checked` means the preparer opened the cited source and verified the locator and summary. It is workflow provenance, not a canonical `review_state`. Both independent processes have now accepted the frozen revision, so the accepted Claims and EvidenceLinks are `review_state=reviewed`.

`READY` requires exactly two distinct reviewers per module. Each reviewer must:

1. use `reviews/REVIEW_TEMPLATE.md`;
2. inspect every Claim, EvidenceLink, locator, Relation predicate, finding, conclusion and uncertainty;
3. record corrections and decisions;
4. record elapsed review minutes;
5. return `READY` only if no blocking correction remains.

The reviewer identity must represent a person or independently assigned review process that did not prepare the module. Re-running the curator’s own checks does not satisfy independence.

Initial `BLOCKED` decisions, requested corrections and final re-review decisions are retained in each reviewer artifact. `review_state=reviewed` and module `READY` are written only after both final decisions are `READY`.

## Commands

Structural/content contract:

```bash
python scripts/validation_modules.py
pytest -q tests/test_validation_research_modules.py
```

Regenerate deterministic reference Briefs:

```bash
python scripts/validation_modules.py --write-briefs
```

Final Gate A acceptance:

```bash
python scripts/validation_modules.py --require-ready
```

The strict command must pass only while `review_registry.json` preserves two independent `READY` reviews and measured review sessions for every module.

## Disclosure rule

The reference Briefs are checked in for reproducibility, but must be withheld from validation participants until their own Brief has been frozen and blind scoring has been recorded.
