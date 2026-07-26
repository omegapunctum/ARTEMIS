# ARTEMIS — PRIORITIES v5.0

## Статус

- Тип: canonical active priorities.
- Дата: 2026-07-26.
- Active cycle: Concept-Locked Architecture Atlas Pre-Validation.

Приоритет получает работа, которая делает evidence chain, research outcome или validation честнее. Infrastructure does not outrank missing product semantics.

## P0 — обязательные блокеры

### P0.1 Concept Lock v2 [current]

- synchronize canonical concept/product/research/epistemic/entity docs;
- separate human mission from future AI option;
- lock Claim/EvidenceLink model;
- lock Investigation/SliceRevision/SavedView/ResearchBrief model;
- exclude `same_movement` from substantive Relation value;
- lock three-module and blind-Brief validation protocol;
- add executable concept-drift guard;
- complete full release/test gate.

Owner docs:

- `ARTEMIS_CONCEPT.md`;
- `PRODUCT_THESIS.md`;
- `ARTEMIS_PRODUCT_SCOPE.md`;
- `EPISTEMIC_CONTRACT.md`;
- `ENTITY_MODEL.md`;
- `RESEARCH_SLICE_CONTRACT.md`;
- `PRODUCT_VALIDATION_PLAN.md`.

### P0.2 Deep research modules

- prepare exactly three modules from approved execution contract;
- 4–6 Features and 6–10 Claims per module;
- claim-level Sources and locators;
- minimum two substantive Relations per module;
- challenge/contest/uncertainty;
- two-reviewer readiness;
- hidden reference Brief;
- record preparation/review cost.

External validation is blocked until `3/3 READY`.

### P0.3 Claim/Evidence data migration

- first-class Claim and EvidenceLink schema;
- independent epistemic dimensions;
- locator and evidence relation/strength;
- ClassificationAssertion model;
- retain legacy records without invented evidence;
- reclassify/exclude `same_movement` safely;
- update ETL/artifacts/UI/tests through a separate migration plan.

### P0.4 Investigation/revision runtime migration

- stable Investigation identity;
- immutable Slice Revisions;
- meaningful dataset/schema identity;
- revision-pinned share or visible `live` mode;
- deterministic Markdown/plain-text Research Brief;
- deterministic legacy migration;
- preserve privacy/owner isolation.

### P0.5 Public target E2E

- deploy/configure required backend only after target contract is ready;
- public Question → Claims → Evidence → Conclusion → Revision → Brief → Reopen/Share;
- fail-closed unavailable capabilities;
- honest capability labels;
- browser evidence and recovery/error states.

## P1 — product proof

### P1.1 Research interface

- question framing;
- Claim comparison across 2–3 Features;
- source locator access;
- substantive Relation / classification / Similarity distinction;
- challenging evidence and uncertainty;
- map/time as synchronized but non-dominating lenses.

### P1.2 Controlled validation

- one wave of six primary users;
- same-content baseline;
- normal-workflow benchmark;
- counterbalanced assignment;
- equal timebox;
- two blinded evaluators;
- absolute counts and critical errors;
- separate spatial-temporal contribution.

### P1.3 Behavioral validation

- 7-day unprompted Brief use, new revision or real share;
- moderator reminders excluded;
- evidence package and explicit decision.

## P2 — maintainability required by P0/P1

- CSS/JS ownership only where touched by target flow;
- browser regression at 1440×900, 1024×768 and 390×844;
- migration integrity;
- release/docs drift;
- security/reliability/dependency fixes;
- no framework rewrite.

## Completed technical foundations

- canonical UUID/source-record split;
- normalized Source/Media export baseline;
- current Relation/Similarity technical separation;
- semantic ETL/release gate;
- 31-Feature legacy corpus envelope;
- mutable ResearchSlice v2 backend capability;
- fail-closed Pages API configuration.

These are prerequisites, not product-validation evidence.

## Frozen backlog

- Stories/Courses;
- AI generation/analysis;
- open UGC;
- new domains;
- institutional workflow;
- causal/predictive/counterfactual systems;
- gamification/native apps;
- enterprise/platform integrations;
- corpus scaling beyond module need;
- heavy scaling.

## Execution order

1. P0.1 Concept Lock v2.
2. P0.2 three deep modules.
3. P0.3 Claim/Evidence migration design and implementation.
4. P0.4 Investigation/revision/Brief migration.
5. P1.1 interface alignment.
6. P0.5 public target E2E.
7. P1.2–P1.3 validation.
8. `VALIDATION_DECISION`.

Parallel work is allowed only when dependency and semantic ownership do not conflict.

## Completion rule

A priority closes only with:

- implemented artifact;
- relevant automated/manual evidence;
- synchronized owner docs;
- honest current capability statement;
- no known semantic contradiction;
- explicit next dependency or no-follow-up decision.
