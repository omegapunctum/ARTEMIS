# ARTEMIS — ARCHITECTURE ATLAS MVP

## Статус

- Тип: historical Architecture Layer MVP boundary document.
- Версия: 2.0 (superseded active scope).
- Дата: 2026-07-26.
- Зависит от: `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `PROJECT_TRUTH.md`, `PRODUCT_VALIDATION_PLAN.md`.

- Lifecycle: `SUPERSEDED AS ACTIVE MVP BY FOUNDATION V3`.
- Use: preserve Architecture Atlas vertical requirements and fixtures; do not treat this file as current ARTEMIS product scope.
- Active scope: `ARTEMIS_PRODUCT_SCOPE.md` v3.

## 1. Цель MVP

Доказать, что ARTEMIS помогает primary user создать более сильный evidence-backed Research Brief, чем same-content catalogue/list и обычный workflow, а spatial-temporal lenses дают либо не дают отдельный измеримый вклад.

MVP не доказывает universal platform, Stories, Courses, institutional workflow, AI generation or new domains.

## 2. Обязательный research outcome

Каждый completed run создаёт:

- question;
- selected 2–3 Features and rationale;
- major Claims;
- claim-level EvidenceLinks with locators;
- substantive Relations where supported;
- findings;
- conclusion or explicit `unresolved`;
- uncertainty;
- revision/dataset identity where implemented;
- Research Brief;
- optional Saved View.

Saved View or mutable ResearchSlice without this evidence chain does not satisfy outcome.

## 3. Обязательные пользовательские возможности

### Investigate

- сформулировать/выбрать вопрос;
- открыть ready research module;
- найти объект through list/search/map/time;
- see factual Claims, classifications and provenance;
- reach source locator.

### Compare

- select 2–3 Features;
- compare consistent lenses;
- distinguish substantive Relation, shared classification and computed Similarity;
- inspect supporting/challenging/contextual evidence;
- preserve uncertainty.

### Conclude

- create findings;
- link major findings/conclusion to evidence;
- choose `concluded` or `unresolved`;
- avoid forced certainty.

### Preserve and transfer

Target:

- create Investigation and immutable revision;
- reopen exact revision;
- generate Research Brief;
- share revision-pinned read-only result;
- create next revision.

Current mutable ResearchSlice v2 may support transitional E2E but cannot satisfy immutable-revision claims.

## 4. Content prerequisites

External pilot requires three `READY` modules from:

- `docs/work/2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md`.

Each module requires:

- 4–6 Features;
- 6–10 Claims;
- minimum eight EvidenceLinks with locators;
- minimum two substantive Relations;
- one material challenge/contest/uncertainty;
- hidden reference Brief;
- two-reviewer readiness check;
- recorded preparation/review cost.

Existing 31 Features/six cohorts/12 current Relations remain technical pilot corpus. Ten `same_movement` records are shared-classification compatibility data and do not count as substantive Relations.

## 5. Public runtime boundary

On public deployment, every user-visible step must match its capability label.

Required before external validation:

- investigate/compare/evidence works;
- output Brief can be produced in the test condition;
- save/open/share semantics are explicit;
- mutable live share is not called immutable;
- auth/backend unavailability fails closed;
- unavailable concept-target actions are hidden or marked.

## 6. UX target

Primary information hierarchy:

1. question;
2. compared Claims;
3. evidence and uncertainty;
4. conclusion/Brief;
5. spatial-temporal Saved View;
6. navigation/utilities.

Map remains a prominent synchronized lens, but it does not push evidence or conclusion below decorative browsing.

User-facing language avoids requiring knowledge of `Slice Revision`, `EvidenceLink` or other internal names before value is received.

## 7. Frozen scope

- Stories/Courses;
- AI generation;
- open UGC;
- new domains;
- institutional collaboration;
- causal/predictive/counterfactual layers;
- native apps;
- enterprise integration;
- framework rewrite;
- scaling unrelated to public pilot.

## 8. Engineering boundary

Allowed:

- docs/data/runtime migrations required by Concept Lock;
- claim/evidence schema and UI work;
- immutable revision migration;
- Brief rendering/export;
- research-module content work;
- public deployment and regression coverage;
- compatibility handling that does not invent evidence.

Not allowed:

- silent reinterpretation of legacy data;
- converting `same_movement` to influence;
- calling content counter a revision id;
- source URL without Claim linkage as validation evidence;
- UI-only simulation of backend target model;
- unrelated expansion.

## 9. MVP exit criteria

MVP exit requires:

- all three modules `READY`;
- semantic/release gates green;
- public capability truth recorded;
- six-person validation wave completed;
- at least 5/6 complete core tasks without critical assist;
- 6/6 avoid classification/Similarity-as-Relation error in final Brief;
- at least 4/6 ARTEMIS Briefs beat controlled baseline by at least 2 rubric points;
- no critical epistemic error in ARTEMIS Briefs;
- at least 3/6 perform unprompted real-task reuse within 7 days;
- map/time contribution assessed separately;
- module curation cost recorded;
- `VALIDATION_DECISION.md` records `ITERATE`, one-branch `EXPAND`, `NARROW` or `STOP/RETHINK`.
