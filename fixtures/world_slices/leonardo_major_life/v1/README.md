# Leonardo major-life Presence candidate package v1

Status: `CANDIDATE_SOURCE_AUDITED / INDEPENDENT_REVIEW_COMPLETE / FREEZE_FOR_REVIEW / NON_PUBLIC`.

Parent: issue `#355` and the `Leonardo Major-Life Presence Scope v1` transition recorded in PR `#399`.

## Purpose

This package turns the seven Google Drive Presence-audit rows into a versioned, machine-checkable GitHub candidate. It is the coarse 1452–1519 breadth increment requested after the post-#396 `ITERATE` decision.

The package does not change the public Globe, the frozen Gate C files, Airtable, or historical route geometry. It is not accepted historical truth and is not runtime input.

## Contents

- six presentation-only macro-periods;
- five named Place identities with unresolved geometry;
- seven new source-audited Presence candidates;
- a reviewed-commit/tree/digest-pinned reference to the frozen four-Presence Romagna 1502 segment;
- eleven external institutional source records with link-only rights policy;
- twenty-eight atomic identity/time/place/selection-significance Claims and thirty-five EvidenceLinks;
- seven Presence-specific Uncertainties plus one shared route/coverage Uncertainty;
- seven new inter-segment transitions, all `unknown_route` with `geometry=null`;
- a deterministic SHA-256 envelope over substantive content and immutable research provenance;
- explicit coverage, exclusions, audit state and lifecycle guards.

When composed later, the seven new candidates plus the four existing Romagna Presences provide eleven coarse/fine anchors. The four Gate C objects are referenced, never copied or rewritten.

## Files

| File | Role |
|---|---|
| `package.json` | candidate macro-period, Presence, source, Claim, EvidenceLink, Uncertainty, transition and coverage data |
| `package.schema.json` | closed Draft 2020-12 structural schema |
| `scripts/validate_leonardo_major_life_package.py` | fail-closed semantic validator |
| `tests/test_leonardo_major_life_package.py` | positive and controlled-corruption regression tests |

## Boundaries

- Macro-periods are presentation/curation groupings, not World Model entities.
- Every Presence retains source-native time and honest normalized precision.
- The 1483 Milan commission is normalized to a year/context anchor, not a day-level body position.
- The Clos Lucé autumn 1516 start retains explicit September–November possible bounds.
- Place identity is separate from geometry; all new candidate geometry is `null`.
- Present-day reference coordinates may be added only by a later reviewed spatial package.
- Every unsupported transition is an evidence-free `unknown_route`.
- Uncertainty uses canonical `review_state`; its explicit missing-evidence condition remains separate
  from Claim `evidence_state`.
- Claim text, source/evidence locators, labels, rationales and Uncertainty meaning are digest-locked.
- The first five recorded review rounds form an immutable prefix; later complete two-track rounds
  append without changing the content digest.
- Git history must prove every later pair was appended once, directly after the exact revision it
  reviewed; deleting or rewriting an appended pair or artifact is rejected. After the empty-suffix
  baseline, every package revision must remain readable, even a transient immutable-prefix change
  fails, and an append commit's direct parent must carry the previously accepted review history.
- Every appended row binds the recomputed historical candidate digest plus a review-envelope digest
  covering the exact reviewed package, schema and validator Git content. Artifacts are read as Git
  blobs, not from an uncommitted working tree; every later ancestor revision touching an artifact
  must preserve its original blob, so deletion or modification followed by restoration also fails.
- A GitHub review URL is retained only as a human locator. The offline validator explicitly does not
  treat its comment number as authenticated evidence.
- A reviewed decision-only descendant may change only lifecycle status, current decision and the
  append-only review log; `FREEZE_FOR_REVIEW` requires two positive latest tracks.
- The frozen `trajectory-leonardo-romagna-1502` segment remains authoritative for its four Presences and three internal gaps.
- `READY_FOR_CANONICAL_REVIEW` is a research-audit decision, not canonical acceptance.
- Runtime integration remains blocked until a later reviewed package decision.

## Validate

```bash
python scripts/validate_leonardo_major_life_package.py
pytest -q tests/test_leonardo_major_life_package.py
```

## Next decision

PR `#399` established the lifecycle transition. Diagnostic review cycles after the immutable
five-round prefix narrowed only the review-envelope validator; no candidate content changed. The
first authenticated appended pair reviewed exact head `946e64d686a538b61a525941c22733e2ddba0997`
and returned semantic and validator-integrity `FREEZE_FOR_REVIEW` with zero unresolved findings.
Package audit round 6 is therefore complete and the candidate decision is `FREEZE_FOR_REVIEW`.

GitHub evaluates pull requests on a synthetic merge commit. The original first-parent traversal did
not retain the feature-branch baseline in that topology, so Core Check correctly failed while the
branch-head checks passed. Review history now uses topologically ordered ancestor traversal. Because
this changed the reviewed validator after round 6, lifecycle was deliberately reset and round 6 was
retained only as immutable history.

Authenticated package round 7 then reviewed exact merge-compatible head
`9ceadaeb00d32b982628563c9bdd2fe09bfd85d1`. Both tracks returned `FREEZE_FOR_REVIEW` with zero
unresolved findings after branch-head, synthetic-merge and later-main checks. The candidate package
is therefore ready for PR review and merge. Runtime/public integration of the eleven composed
anchors still requires a separate bounded PR.
