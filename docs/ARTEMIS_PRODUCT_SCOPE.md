# ARTEMIS — PRODUCT SCOPE

## Статус

- Тип: canonical current product scope.
- Версия: 2.0.
- Дата: 2026-07-26.
- Active vertical: Architecture Atlas.
- North Star: `ARTEMIS_CONCEPT.md`.
- Current reality: `PROJECT_TRUTH.md`.
- Validation authority: `PRODUCT_VALIDATION_PLAN.md` and `VALIDATION_DECISION.md`.

Этот документ запрещает feature/product drift. Concept target не является утверждением о current implementation.

## 1. Формула текущего продукта

ARTEMIS Architecture Atlas — **инструмент evidence-first сравнения архитектурных объектов с пространственно-временными линзами и переносимым Research Brief**.

Продукт помогает:

- поставить сравнительный вопрос;
- выбрать 2–3 объекта;
- сопоставить Claims;
- проверить EvidenceLinks and locators;
- отличить substantive Relation от classification and Similarity;
- сформулировать conclusion or unresolved;
- сохранить revision и перенести Brief в реальную работу.

## 2. Primary user

Первичный пользователь:

- старшекурсник или магистрант истории архитектуры/искусства;
- готовит сравнительное эссе, семинар или исследовательское задание в ближайшие 1–2 недели.

Primary job:

> Собрать и проверить сравнительный вывод по 2–3 объектам и перенести evidence chain в свою работу без повторной ручной сборки.

Преподаватель/куратор и профессиональный исследователь являются exploratory audiences.

## 3. Главная ценность

Первая ценность — evidence-aware comparison.

Reusable outcome:

- Investigation;
- immutable Slice Revision;
- Research Brief;
- optional nested Saved View.

Saved View without question/Claims/Evidence/conclusion is not a complete research result.

## 4. Core product loop

1. Question.
2. Entity selection.
3. Claim comparison.
4. Evidence and locator review.
5. Relation/classification/Similarity distinction.
6. Findings.
7. Conclusion or unresolved.
8. Save revision.
9. Generate/open/share Brief.
10. Return and create next revision.

Stories, Courses and AI are not part of the active loop.

## 5. Обязательный scope

### 5.1 Curated research modules

- ровно три deep validation modules before external pilot;
- 4–6 Features per module;
- 6–10 atomic Claims per module;
- reviewed EvidenceLinks with locators;
- минимум две substantive Relations per module;
- challenging/contested/medium-confidence evidence;
- reference revision and hidden reference Brief;
- measured preparation and review cost.

Execution owner:

- `docs/work/2026-07-26_VALIDATION_RESEARCH_MODULES_v1.md`.

The existing 31-Feature/six-cohort corpus remains useful exploration content and technical release evidence, but it is not sufficient validation corpus by itself.

### 5.2 Research interface

- question framing;
- list/detail/evidence surface;
- Compare for 2–3 Features;
- map and compact timeline as synchronized lenses;
- filters/search;
- visible source and locator;
- visible classification/Relation/Similarity distinction;
- uncertainty and challenged evidence.

Map/time must not hide non-spatial evidence dimensions such as function, material, patronage, construction and interpretation.

### 5.3 Claim/Evidence

- Claim is the unit of evidence;
- Source is not blanket proof of Entity;
- EvidenceLink identifies `supports/challenges/contextualizes`;
- locator enables independent re-finding;
- claim kind/origin/review/confidence/evidence/uncertainty remain independent;
- user Claim is private until separate governance promotion.

Current artifacts do not yet implement this full schema. Data/runtime migration is separate work.

### 5.4 Relations, classification and Similarity

- Relation is a specific structured Claim;
- substantive Relation requires reviewed evidence and locator;
- shared Movement/Layer is ClassificationAssertion;
- `same_movement` is legacy compatibility projection and excluded from substantive Relation threshold;
- Similarity is computed and displays criteria;
- causal claims remain out of scope.

### 5.5 Research persistence

Target baseline:

- stable Investigation identity;
- immutable revisions;
- question, Claims/findings, EvidenceLinks, conclusion/unresolved and uncertainty;
- meaningful dataset/schema identity;
- nested Saved View;
- revision-pinned read-only share;
- Markdown/plain-text Research Brief;
- return and new revision.

Current mutable ResearchSlice v2 remains `BACKEND-AVAILABLE/COMPATIBILITY` until separate migration.

### 5.6 Optional curated entry

One or more curated entry points may lead into a ready research module.

They:

- do not create a separate Story product;
- must lead to Question/Compare/Evidence;
- do not block MVP exit if absent.

## 6. Public capability rule

Capability enters primary navigation only when it works on the public deployment end-to-end.

Labels:

- `PUBLIC NOW`;
- `BACKEND-AVAILABLE`;
- `PILOT`;
- `CONCEPT TARGET`;
- `FUTURE`.

Code or schema without public runtime is not a user capability. Public mutable share is not revision-pinned reproducibility.

## 7. Frozen scope

Until `VALIDATION_DECISION` opens one named branch:

- Stories/Courses product depth;
- AI generation/explanation;
- open-ended UGC;
- multi-domain expansion;
- institutional collaboration;
- causal/predictive/counterfactual engine;
- native apps;
- enterprise APIs/integrations;
- framework rewrite;
- corpus scaling beyond module prerequisites;
- non-critical scaling.

Security and compatibility maintenance of existing frozen code remains allowed.

## 8. Content readiness

Technical release readiness and product-validation readiness are separate.

### Technical corpus envelope

Existing profile:

- 31 Features;
- six comparison cohorts;
- 12 current Relations;
- Source and Media coverage thresholds;
- semantic release gate.

This supports exploration/runtime tests.

### Validation-ready corpus

Requires all three deep modules `READY`.

Pairwise `same_movement` records:

- remain legacy data until migration;
- do not count toward substantive Relation readiness;
- do not prove H3 relation literacy/value;
- must not be upgraded to influence by inference.

## 9. Temporal claim boundary

Current product is time-indexed, not a full model of change.

Dates/timeline do not prove:

- reconstruction;
- destruction;
- function change;
- evolving geometry;
- transmission;
- causality.

Future `Entity → Event → State change → Evidence` requires branch-specific scope after validation.

## 10. AI boundary

AI generation is frozen.

Future AI, if separately approved:

- uses selected Claims/EvidenceLinks;
- preserves locators;
- exposes `origin=ai`;
- may propose hypothesis or evidence gap;
- does not become Source;
- does not publish canonical Claims/Relations.

AI compatibility does not determine current product architecture beyond preserving clean evidence/context boundaries.

## 11. Validation gate

Canonical protocol: `PRODUCT_VALIDATION_PLAN.md`.

External pilot cannot start until:

- three modules are `READY`;
- public capability truth is recorded;
- output Brief is available in every condition;
- assignment and scoring rubric are frozen;
- current share semantics are honestly described.

Possible decision:

- `ITERATE`;
- `EXPAND` one named branch;
- `NARROW`;
- `STOP/RETHINK`.

## 12. Owner documents

- audience/job/hypotheses: `PRODUCT_THESIS.md`;
- North Star: `ARTEMIS_CONCEPT.md`;
- current reality: `PROJECT_TRUTH.md`;
- MVP exit: `MVP_ARCHITECTURE_ATLAS.md`;
- validation: `PRODUCT_VALIDATION_PLAN.md`;
- research-work model: `RESEARCH_SLICE_CONTRACT.md`;
- current runtime schema: `RESEARCH_SLICE_SPEC.md`;
- Claim/Evidence semantics: `EPISTEMIC_CONTRACT.md`;
- entities/relations: `ENTITY_MODEL.md`;
- content promotion: `CONTENT_GOVERNANCE.md`;
- data artifacts: `DATA_DICTIONARY.md` and `DATA_CONTRACT.md`.
