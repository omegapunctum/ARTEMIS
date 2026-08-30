# Leonardo major-life Presence candidate package v1

Status: `CANDIDATE_SOURCE_AUDITED / ROUND_1_NARROW / INDEPENDENT_REREVIEW_PENDING / NON_PUBLIC`.

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
- The frozen `trajectory-leonardo-romagna-1502` segment remains authoritative for its four Presences and three internal gaps.
- `READY_FOR_CANONICAL_REVIEW` is a research-audit decision, not canonical acceptance.
- Runtime integration remains blocked until a later reviewed package decision.

## Validate

```bash
python scripts/validate_leonardo_major_life_package.py
pytest -q tests/test_leonardo_major_life_package.py
```

## Next decision

PR `#399` has established the lifecycle transition. Independent review round 1 returned `NARROW`
on head `5672fbae6f224b0fb90ccc09080ca47d4574c511`; that decision is preserved in package audit history.
Review the remediated exact revision again. The allowed result remains `FREEZE_FOR_REVIEW`, `NARROW`
or `STOP`; none silently authorizes runtime publication.
