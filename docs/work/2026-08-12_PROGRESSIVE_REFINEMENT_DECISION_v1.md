# ARTEMIS — Progressive Refinement decision v1

## Status

- Issue: `#377`.
- Lifecycle: `IN PROGRESS / REVIEW_REQUIRED`.
- Decision target: `ACCEPT | NARROW | REJECT`.
- Product gate impact: none; Gate D remains in progress under `#355`.
- Public capability impact: none.

## Problem

The project can represent uncertainty and alternatives but lacks one executable append-only
mechanism for progressively refining atomic knowledge without erasing evidence or confusing world
change with knowledge revision.

## Proposed decision

Adopt `docs/PROGRESSIVE_REFINEMENT_CONTRACT.md` as a scoped semantic extension with:

- stable object identity;
- immutable atomic revision series;
- separate valid and record time;
- `initial`, `refine`, `correct`, `add_alternative` and `withdraw` operations;
- source-native plus non-sharpening normalized values;
- deterministic current-frontier and record-time replay;
- a material-resolution budget and stop rule.

## Current versus target

Current behavior is a documented curation preference with partial uncertainty primitives. Target
behavior is a fail-closed, domain-neutral refinement ledger demonstrated by executable fixtures.

## Migration and disposition

- preserve reviewed #329/#330 bytes and evidence;
- add a scoped extension rather than editing their frozen packages;
- do not migrate Architecture Atlas, Airtable, public data or the frozen Leonardo package;
- require a later migration decision before runtime/storage adoption.

## Non-goals

- no Globe implementation or promotion;
- no historical recuration or new exactness research;
- no Airtable historical writes;
- no Relations, AI, VR/AR or universal corpus work;
- no claim of historical or product readiness.

## Required evidence

1. Contract and fixture schema/package.
2. Semantic validator and controlled-corruption tests.
3. Leonardo trajectory and ecological-range scenarios.
4. Repository checks on one frozen revision.
5. Two independent reviews with zero critical/material findings.
6. Recorded `ACCEPT`, `NARROW` or `REJECT` decision.

## Rollback

Before acceptance, close #377 and remove the draft extension/fixtures. No runtime or data migration
exists to undo. After acceptance, changes require a new version; accepted revision history is not
rewritten.
