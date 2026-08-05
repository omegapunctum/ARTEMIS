# Relation Ladder v1 — implementation and review record

## Status

- Issue: `#331`.
- Package: `fixtures/world_model/relations/v1`.
- State: `REVIEW_REQUIRED`.
- Base `main`: `94f559e8c836f1a2e4ba66b79635f8c606e18a6e`.
- Frozen commit: `PENDING`.
- Reviewed digest: `PENDING`.
- Reviews: `PENDING`.

## Scope lock

Implement six distinct relation predicates as a synthetic executable contract extension. Preserve the historical
relation-ladder name for issue/artifact traceability, but do not encode a total order, shared rank or co-presence
prerequisite for documented predicates. Preserve the reviewed #329 world-model and #330 uncertainty packages
byte-for-byte. Do not migrate runtime/database/Airtable data, curate Leonardo content, implement UI, score
confidence with AI or introduce automated causal discovery.

## Acceptance map

| Issue criterion | Executable evidence |
|---|---|
| Non-overlapping predicates | closed unranked `relation_predicates` plus validator |
| Co-presence cannot create Relation | four-state #330 extent derivation and negative mutation |
| Possible encounter assumptions | structured assumptions, uncertainty and inference Claim |
| Independent documented predicates | distance/mediated/posthumous/process fixtures plus item-bound Claim → EvidenceLink → Source/locator checks |
| Distinct causal basis | same-endpoint causal-basis Claim plus checked, digest-bound synthetic policy artifact |
| Classification/Similarity separate | `non_relation_cases` and closed compatibility mapping |
| Required scenarios | fourteen positive/negative/ambiguous cases |
| Boundary overpromotion | five regression boundaries without logical inheritance |
| #329/#330 consumption | closed unique base bindings plus explicit semantic-profile refs that cannot masquerade as evidence |
| UI language | unique complete rules with label templates, disclosures, source access and forbidden implications |
| Validator integrity | strict finite JSON, safe repo paths, Polygon holes/antimeridian/boundaries and fail-closed endpoint binding |
| Frozen review integrity | digest recomputed from frozen tree; closed parsed artifacts and transition blobs bound to HEAD |
| Independent review | pending frozen semantic and validator tracks |

## Review protocol

Both reviewers must inspect the same frozen commit and reviewed digest. One track reviews predicate independence,
extent interpretation and overclaim paths; the other reviews validator integrity, #330 binding, provenance,
Git/tree binding and adversarial bypasses. No prior #329/#330 verdict transfers to this package.

## Superseded candidate review

Candidate `d2bfd14a617de0672e80174bb96e2c2868a23a96` with normalized digest
`4fdc2f95cfa93a6d47ea5830ed73b7f24a36712c9e088cfeb2aacbf4d3be9528` was independently rejected by both
tracks and is not eligible for READY. The new candidate must be reviewed from scratch.

The semantic review found false evidence appearance in reused #330 basis references, an unresolved causal-policy
literal and UI rules that could hide possible overlap. The validator-integrity review found the frozen-tree digest
bypass, opaque review artifacts, Polygon hole/antimeridian errors, weak causal endpoints, background evidence
promotion, duplicate dependency acceptance and non-finite JSON. Version 1.2 addresses every critical/material
finding with executable negative tests; this statement is implementation evidence, not a replacement verdict.

Candidate `18bd8304176a0873464a7e7bf3d824f440dbf628` passed CI but was superseded before either rereview issued a
verdict. Its working record did not normalize the final review-summary line, so a truthful READY transition would
have changed the reviewed digest. The replacement candidate normalizes and mutation-tests that explicitly declared
metadata field; no attestation from the interrupted review attempt transfers.

Candidate `bf99f01a3c823c24d8c9953ea04f92ce5b101b44` passed 5/5 CI but both independent tracks returned
`CHANGES_REQUIRED`. They agreed that normalized lifecycle values were not checked against the registry. The
validator-integrity track also found that the package could select a regular Source outside the review scope and
that spatial exclusion ignored approximate-point tolerance while treating missing place hierarchy as disjointness.
The replacement closes the Source set, adds explicit place-disjointness, preserves `unknown` for incomplete place
knowledge, evaluates corridor/tolerance intersection and mutation-tests exact lifecycle truth. No verdict transfers.
