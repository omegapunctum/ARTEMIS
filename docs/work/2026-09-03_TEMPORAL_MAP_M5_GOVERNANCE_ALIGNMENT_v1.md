# Temporal Map M5 governance alignment v1

## Status

- Type: current housekeeping and governance-alignment record.
- Date: 2026-09-03.
- Active product issue: `#355`.
- Current checkpoint: `M5 — Whole-Life Runtime Proof`.
- Product result: pending manual check; no `ITERATE`, `NARROW` or `STOP` decision is recorded yet.

## 1. Observed sequence

1. PR `#404` recorded the M3 exit as `PROCEED_TO_M4` and opened M4 as decision-only.
2. PR `#405` recorded M4 as `ADOPT` and explicitly stated that no successor implementation branch was opened.
3. The project owner then gave an explicit owner instruction to build `M5 — Whole-Life Runtime Proof` from the already reviewed PR `#400` major-life package.
4. PR `#406` implemented, merged and published that bounded proof.

Between steps 2 and 3, **no intervening repository decision record exists**. This document must not invent one.

## 2. Governance deviation

The M4 → M5 transition entered implementation through explicit owner instruction rather than through the separate pre-start repository decision required by the M4 record. That is a governance/documentation deviation. It is not evidence that the North Star, World Model or M4 semantic decision changed.

Current M5 authority derives from the explicit owner instruction already given. This housekeeping checkpoint **does not convert that later instruction into a retroactive pre-start decision**, rewrite PR `#405`, or manufacture a missing record. It records the actual sequence after the fact and aligns current lifecycle owners with the runtime that now exists.

## 3. Current bounded proof

M5 remains limited to:

- one Person: Leonardo da Vinci;
- 11 reviewed Presence anchors: 7 major-life anchors from PR `#400` plus 4 preserved Romagna anchors;
- six coarse life periods across 1452–1519;
- the existing `Range` and `Scrub` Temporal Map interaction;
- present-day source-bound place anchors, explicit uncertainty and unknown route geometry;
- the published R&D runtime at `https://omegapunctum.github.io/ARTEMIS/globe/?mode=range&start=1452&end=1519`.

M5 does not authorize new sources, additional Presences, historical route reconstruction, context/layer expansion, live federation, generic ingestion/storage, Airtable historical writes or another feature branch.

## 4. Housekeeping freeze

Until this alignment is reviewed and merged:

- no new feature branch may start;
- only this lifecycle synchronization and separately scoped defect/security maintenance may proceed;
- North Star and World Model owners remain unchanged;
- historical decision records remain unchanged.

The Export Airtable CI repair is a separate technical maintenance PR after this checkpoint. It must first provide sufficient Git history and required evidence refs, rerun the suite, and only then address genuine stale lifecycle/governance assertions or Progressive Refinement digest failures.

## 5. Product exit

The next product action is a manual check of the published M5. Record exactly one result:

- `ITERATE` — the whole-life product loop is understandable and worth improving in place;
- `NARROW` — reduce the data or interaction scope before continuing;
- `STOP` — stop this product direction and revisit the hypothesis.

No decision is implied by publication or automated tests. The user has not yet performed this check. No new feature branch opens automatically after the result.
