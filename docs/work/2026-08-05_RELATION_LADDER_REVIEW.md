# Relation Ladder v1 — implementation and review record

## Status

- Issue: `#331`.
- Package: `fixtures/world_model/relations/v1`.
- State: `REVIEW_REQUIRED`.
- Base `main`: `94f559e8c836f1a2e4ba66b79635f8c606e18a6e`.
- Frozen commit: `PENDING`.
- Reviewed digest: `PENDING`.
- Reviews: not yet frozen.

## Scope lock

Implement the six-level relation ladder as a synthetic executable contract extension. Preserve the reviewed #329
world-model and #330 uncertainty packages byte-for-byte. Do not migrate runtime/database/Airtable data, curate
Leonardo content, implement UI, score confidence with AI or introduce automated causal discovery.

## Acceptance map

| Issue criterion | Executable evidence |
|---|---|
| Non-overlapping levels | closed ordered `ladder_levels` plus validator |
| Co-presence cannot create Relation | deterministic presence derivation and negative mutation |
| Possible encounter assumptions | structured assumptions, uncertainty and inference Claim |
| Documented source binding | item-bound Claim → EvidenceLink → Source/locator checks |
| Distinct causal basis | separate causal-basis Claim and policy reference |
| Classification/Similarity separate | `non_relation_cases` and closed compatibility mapping |
| Required scenarios | ten positive/negative/ambiguous cases |
| Boundary overpromotion | five explicit negative regression classes |
| #329 consumption | exact reviewed base-package bindings |
| Independent review | pending frozen semantic and validator tracks |

## Review protocol

Both reviewers must inspect the same frozen commit and reviewed digest. One track reviews predicate semantics and
overclaim paths; the other reviews validator integrity, provenance binding, Git/tree binding and adversarial bypasses.
No prior #329/#330 verdict transfers to this package.
