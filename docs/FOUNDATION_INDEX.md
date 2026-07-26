# ARTEMIS — FOUNDATION INDEX

## Статус документа

- Тип: canonical foundation index document
- Статус: active
- Роль: главный навигатор фундаментального слоя ARTEMIS
- Назначение: фиксирует, какие документы образуют foundation-layer, в каком порядке их читать и какой документ отвечает за какой тип решений
- Scope: concept, product scope, research-work model, epistemic/entity model, content governance, AI policy, data/release/runtime/documentation boundaries

---

## 1. Назначение foundation-layer

Foundation-layer ARTEMIS нужен, чтобы проект развивался как единая система, а не как набор отдельных модулей: карта, курсы, stories, AI, UGC, data pipeline и UI.

Фундаментальный слой отвечает на вопросы:

1. Что такое ARTEMIS.
2. Как устроена проверяемая цепочка от вопроса к выводу.
3. Что считается Claim, EvidenceLink, Relation, classification и Similarity.
4. Как Investigation, immutable Slice Revision, Saved View and Research Brief связаны.
5. Какие сущности существуют в системе.
6. Как проверяется и утверждается контент.
7. Что может и не может делать future AI.
8. Какие документы являются source of truth для architecture, data, release and documentation.

---

## 2. Главный принцип

ARTEMIS нельзя развивать через отдельные функции без проверки их связи с фундаментом.

Любое новое направление должно усиливать одну из базовых опор:

- evidence chain `Question → Claims → Evidence → Conclusion`;
- evidence-aware comparison as first value;
- spatial-temporal lenses with independently validated contribution;
- Investigation/Slice Revision/Research Brief as reusable research model;
- explainable knowledge structure;
- curated and governed content;
- clear epistemic separation of facts, interpretations, hypotheses and AI outputs;
- controlled release/data/runtime discipline.

Если функция не усиливает эти опоры, она не входит в ядро ARTEMIS.

---

## 3. Четыре уровня продуктовой истины

| Уровень | Owner documents | Вопрос |
|---|---|---|
| North Star | `ARTEMIS_CONCEPT.md` | Куда проект может прийти и какие принципы нельзя нарушать? |
| Current product | `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `MVP_ARCHITECTURE_ATLAS.md` | Для кого, какую проблему и какой scope мы проверяем сейчас? |
| Current reality | `PROJECT_TRUTH.md` | Что действительно работает и с какой зрелостью? |
| Validated outcome | `VALIDATION_DECISION.md` | Что доказано пользователями и какой следующий scope разрешён? |

Уровни нельзя смешивать. North Star не является release promise; реализованный backend-код не является public capability; пройденный usability task не является доказанной cognitive/behavioral ценностью; `PENDING` не разрешает expansion.

---

## 4. Текущий canonical foundation set

На текущем этапе foundation-layer состоит из действующих canonical docs.

| Документ | Роль |
|---|---|
| `README.md` | root entrypoint проекта |
| `docs/FOUNDATION_INDEX.md` | навигатор foundation-layer, порядок чтения и source-of-truth routing |
| `docs/ARTEMIS_CONCEPT.md` | North Star, human-research mission, principles и independent branch gates |
| `docs/PROJECT_TRUTH.md` | фактическая граница public/backend/pilot/future capabilities |
| `docs/PRODUCT_THESIS.md` | active Architecture Atlas audience, problem, hypotheses и value proposition |
| `docs/ARTEMIS_PRODUCT_SCOPE.md` | продуктовые границы текущего vertical и запреты против product drift |
| `docs/MVP_ARCHITECTURE_ATLAS.md` | vertical MVP boundary, content threshold и exit criteria |
| `docs/DATA_DICTIONARY.md` | semantic identity/source/media/relation data model |
| `docs/PRODUCT_VALIDATION_PLAN.md` | user evidence protocol и decision gate |
| `docs/VALIDATION_DECISION.md` | validation outcome и разрешённый следующий scope |
| `docs/RESEARCH_SLICE_CONTRACT.md` | canonical contract для Investigation, immutable Slice Revision, Saved View и Research Brief |
| `docs/RESEARCH_SLICE_SPEC.md` | current mutable ResearchSlice v2 runtime/API compatibility spec |
| `docs/EPISTEMIC_CONTRACT.md` | Claim/EvidenceLink model и независимые epistemic dimensions |
| `docs/ENTITY_MODEL.md` | knowledge/product/runtime/context entities, Claim and Relation model |
| `docs/CONTENT_GOVERNANCE.md` | правила источников, валидации, модерации, UGC promotion, trust, correction и publish governance |
| `docs/AI_POLICY.md` | canonical границы AI behavior, AI-output, source discipline и запреты против AI drift |
| `docs/ARTEMIS_MASTER_PROMPT.md` | operational governance для AI-агентов и docs-first discipline |
| `docs/PROJECT_STRUCTURE.md` | структура репозитория, runtime boundaries, canonical entrypoints, documentation layers |
| `docs/PROJECT_PHASES.md` | фазы, переходы и текущий active cycle |
| `docs/PRIORITIES.md` | текущие load-bearing приоритеты |
| `docs/DATA_CONTRACT.md` | ETL/data/public map/release artifact contract |
| `docs/CONTROLLED_RELEASE_DECISION.md` | controlled release baseline, release/readiness interpretation, production-grade limitations |
| `docs/DOCUMENTATION_SYSTEM.md` | documentation governance, роли слоёв, правила конфликтов |

Правило:
- эти документы считаются active canonical foundation/source-of-truth set;
- archive/reference/working/audit docs не могут переопределять этот набор;
- если новый документ начинает задавать устойчивое правило foundation-layer, он должен быть явно зарегистрирован в `PROJECT_STRUCTURE.md` и `DOCUMENTATION_SYSTEM.md`.

---

## 5. Порядок чтения foundation docs

Рекомендуемый порядок чтения:

1. `README.md` — быстрый вход в проект.
2. `docs/FOUNDATION_INDEX.md` — карта фундаментального слоя.
3. `docs/PROJECT_TRUTH.md` — что действительно работает сейчас.
4. `docs/PRODUCT_THESIS.md` — для кого и зачем строится активный vertical.
5. `docs/ARTEMIS_PRODUCT_SCOPE.md` — что входит и не входит в текущий scope.
6. `docs/MVP_ARCHITECTURE_ATLAS.md` — что должно быть доказано в MVP.
7. `docs/DATA_DICTIONARY.md` — какие semantic data rules обязательны.
8. `docs/PRODUCT_VALIDATION_PLAN.md` — какое evidence открывает следующий этап.
9. `docs/VALIDATION_DECISION.md` — что доказано и какой scope разрешён.
10. `docs/ARTEMIS_CONCEPT.md` — долгосрочная миссия и принципы.
11. `docs/RESEARCH_SLICE_CONTRACT.md` — Investigation/revision/Saved View/Brief model и current-runtime gap.
12. `docs/EPISTEMIC_CONTRACT.md`, `docs/ENTITY_MODEL.md`, `docs/CONTENT_GOVERNANCE.md` и `docs/AI_POLICY.md` — knowledge governance.
13. `docs/DATA_CONTRACT.md` — export/public artifact mechanics.
14. `docs/PROJECT_STRUCTURE.md`, `docs/PROJECT_PHASES.md` и `docs/PRIORITIES.md` — структура и active order.
15. `docs/DOCUMENTATION_SYSTEM.md`, `docs/CONTROLLED_RELEASE_DECISION.md` и `docs/ARTEMIS_MASTER_PROMPT.md` — governance/release/agent rules.

---

## 6. Решения по типам вопросов

### 6.1 Concept / mission questions

Primary authority:
- `docs/ARTEMIS_CONCEPT.md`

Secondary authority:
- `docs/PRODUCT_THESIS.md`
- `docs/ARTEMIS_PRODUCT_SCOPE.md`
- `docs/FOUNDATION_INDEX.md`

Примеры вопросов:
- чем является ARTEMIS;
- почему ARTEMIS не просто карта;
- почему AI не является source of truth;
- почему факт, интерпретация и гипотеза должны быть разделены.

### 6.2 Product scope questions

Primary authority:
- `docs/ARTEMIS_PRODUCT_SCOPE.md`

Secondary authority:
- `docs/PROJECT_TRUTH.md`
- `docs/PRODUCT_THESIS.md`
- `docs/MVP_ARCHITECTURE_ATLAS.md`
- `docs/PRODUCT_VALIDATION_PLAN.md`
- `docs/PROJECT_PHASES.md`
- `docs/PRIORITIES.md`
- `docs/RESEARCH_SLICE_CONTRACT.md`

Примеры вопросов:
- входит ли feature в active vertical MVP;
- что является primary user value;
- что делать сначала: evidence chain, research persistence или future branch;
- какие направления являются forbidden product drift.

### 6.3 Research-work questions

Primary authority:
- `docs/RESEARCH_SLICE_CONTRACT.md`

Runtime/API authority:
- `docs/RESEARCH_SLICE_SPEC.md`

Supporting authority:
- `docs/ARTEMIS_PRODUCT_SCOPE.md`
- `docs/EPISTEMIC_CONTRACT.md`
- `docs/ENTITY_MODEL.md`

Примеры вопросов:
- чем Investigation отличается от immutable Slice Revision;
- чем Saved View отличается от research result;
- как Research Brief связан с revision;
- что означает reproducibility и pinned dataset identity;
- чем target model отличается от current mutable ResearchSlice v2.

### 6.4 Knowledge / epistemic questions

Primary authority:
- `docs/EPISTEMIC_CONTRACT.md`

Supporting authority:
- `docs/ARTEMIS_CONCEPT.md`
- `docs/CONTENT_GOVERNANCE.md`
- `docs/AI_POLICY.md`

Примеры вопросов:
- что является atomic Claim;
- как Source связывается с Claim через EvidenceLink and locator;
- чем claim kind отличается от origin/review/confidence/evidence state;
- как показывать interpretation/hypothesis/AI origin;
- как работать с uncertainty and challenging evidence;
- почему counterfactual не является history.

### 6.5 Entity / relation questions

Primary authority:
- `docs/ENTITY_MODEL.md`

Supporting authority:
- `docs/EPISTEMIC_CONTRACT.md`
- `docs/DATA_CONTRACT.md`
- `docs/RESEARCH_SLICE_CONTRACT.md`

Примеры вопросов:
- что такое entity;
- чем object отличается от event/process/place;
- как RelationClaim связывает сущности;
- почему shared classification и Similarity не являются substantive Relation;
- как source/media относятся к entity;
- как entity входит в Investigation/revision/future consumer context.

### 6.6 Content trust / governance questions

Primary authority:
- `docs/CONTENT_GOVERNANCE.md`

Supporting authority:
- `docs/EPISTEMIC_CONTRACT.md`
- `docs/ENTITY_MODEL.md`
- `docs/DATA_CONTRACT.md`
- relevant moderation/runtime docs

Примеры вопросов:
- как объект становится canonical content;
- как решать конфликт источников;
- что делать со спорными координатами;
- как UGC становится trusted;
- когда запись отклоняется;
- почему AI-generated content не становится source-backed fact без review.

### 6.7 AI behavior questions

Primary authority:
- `docs/AI_POLICY.md`

Supporting authority:
- `docs/EPISTEMIC_CONTRACT.md`
- `docs/RESEARCH_SLICE_CONTRACT.md`
- `docs/CONTENT_GOVERNANCE.md`
- `docs/work/ARTEMIS_AI_STRATEGY_v1_0.md` where it does not conflict with canonical docs

Примеры вопросов:
- может ли AI генерировать historical claim;
- как маркировать AI hypothesis;
- может ли AI менять canonical data;
- как AI должен использовать slice context;
- почему AI не является source.

### 6.8 Data / release / runtime questions

Primary authority:
- `docs/DATA_CONTRACT.md`
- `docs/CONTROLLED_RELEASE_DECISION.md`
- `docs/PROJECT_STRUCTURE.md`

Executable authority:
- `scripts/release_check.py`
- tests
- GitHub workflows

Примеры вопросов:
- что является public map source;
- какие artifacts обязательны;
- какие release checks блокируют deploy;
- что считается controlled baseline, а что production-grade claim.

---

## 7. Правило разрешения конфликтов

Если документы расходятся, действует порядок:

1. executable checks / tests / workflows for runtime facts;
2. `PROJECT_TRUTH.md` for current capability/maturity statements;
3. `DATA_CONTRACT.md` and `DATA_DICTIONARY.md` for export and semantic data contracts;
4. `CONTROLLED_RELEASE_DECISION.md` for release/readiness interpretation;
5. `VALIDATION_DECISION.md` for validated outcomes and permission to expand;
6. `PRODUCT_THESIS.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `MVP_ARCHITECTURE_ATLAS.md` and `PRODUCT_VALIDATION_PLAN.md` for active product decisions;
7. `ARTEMIS_CONCEPT.md` for North Star mission/principles/epistemic constraints;
8. foundation contracts:
   - `RESEARCH_SLICE_CONTRACT.md`;
   - `EPISTEMIC_CONTRACT.md`;
   - `ENTITY_MODEL.md`;
   - `CONTENT_GOVERNANCE.md`;
   - `AI_POLICY.md`;
9. `PROJECT_STRUCTURE.md` for repo/runtime/docs boundaries;
10. `PROJECT_PHASES.md` and `PRIORITIES.md` for current work order;
11. `DOCUMENTATION_SYSTEM.md` for doc placement/governance conflicts;
12. working docs;
13. audits;
14. archive/reference.

Audit documents may reveal a conflict, but they do not become source of truth by themselves. The relevant canonical or working document must be updated.

---

## 8. Foundation change-control rule

A foundation document may be created or changed only if the change clearly states:

- what problem it solves;
- which existing canonical documents it affects;
- whether it changes product scope, data contract, AI behavior, content governance or runtime boundaries;
- which docs must be updated after the change;
- which tests/checks should be run if executable behavior is affected.

Foundation changes must not be mixed with unrelated UI/runtime refactors.

---

## 9. Forbidden shortcuts

Запрещено:

- добавлять AI-функции без проверки against `AI_POLICY.md` and `EPISTEMIC_CONTRACT.md`;
- развивать Stories/Courses вне independent validation gate;
- расширять entity/relation/source/media model вне `ENTITY_MODEL.md`;
- подменять evidence-aware comparison просмотром object cards;
- называть Saved View product-complete revision;
- называть mutable ResearchSlice immutable/reproducible revision;
- считать `same_movement` substantive Relation;
- прикреплять Source как blanket proof без Claim/EvidenceLink/locator;
- расширять scope при `VALIDATION_DECISION=PENDING`;
- использовать UGC as canonical content без `CONTENT_GOVERNANCE.md`;
- смешивать fact, interpretation, hypothesis, AI-output и counterfactual;
- создавать новый source of truth в working docs или audits;
- использовать archive/reference documents как current guidance;
- расширять ARTEMIS в generic GIS/LMS/social/wiki platform без foundation decision.

---

## 10. Текущий статус foundation work

Status:
- foundation-layer создан;
- ключевые foundation docs зарегистрированы в `PROJECT_STRUCTURE.md` и `DOCUMENTATION_SYSTEM.md`;
- `ARTEMIS_MASTER_PROMPT.md` обновлён под foundation invariants;
- archive index создан и Batch A cleanup выполнен;
- release/docs drift частично защищён через `scripts/release_check.py`.

Closed foundation setup items:

1. `docs/RESEARCH_SLICE_CONTRACT.md` создан.
2. `docs/EPISTEMIC_CONTRACT.md` создан.
3. `docs/ENTITY_MODEL.md` создан.
4. `docs/CONTENT_GOVERNANCE.md` создан.
5. `docs/AI_POLICY.md` создан.
6. `docs/PROJECT_STRUCTURE.md` обновлён.
7. `docs/DOCUMENTATION_SYSTEM.md` обновлён.
8. `docs/ARTEMIS_MASTER_PROMPT.md` обновлён.
9. `docs/archive/README.md` обновлён.
10. `docs/VALIDATION_DECISION.md` зарегистрирован с исходным статусом `PENDING`.

Concept Lock v2 status:

- rationale/migration record: `docs/work/2026-07-26_CONCEPT_LOCK_V2.md` (not an owner document);
- human research утверждено как единственная миссия;
- map/time переведены в independently validated lenses;
- Claim/EvidenceLink model утверждена;
- Investigation/SliceRevision/SavedView/ResearchBrief model утверждена;
- `same_movement` исключён из substantive relation-value;
- three-module validation prerequisite и blind Brief protocol утверждены;
- current runtime/data migrations ещё не выполнены.

Remaining follow-up:
- semantic review оставшихся `DO_NOT_DELETE_YET` archive files;
- three validation research modules;
- Claim/Evidence and immutable revision data/runtime migration;
- Architecture Atlas public runtime/validation tasks из active Phase 4.5;
- critical production constraints, только если они блокируют public MVP loop.

---

## 11. Итоговое правило

ARTEMIS должен развиваться от фундаментальной модели знания к продуктовым слоям, а не наоборот.

Порядок развития:

1. concept and product scope;
2. Claim/Evidence foundation;
3. evidence-aware comparison;
4. Investigation/SliceRevision/ResearchBrief contract;
5. epistemic and entity contracts;
6. content governance;
7. focused vertical validation;
8. только после recorded decision gate — one selected branch;
9. AI policy applies only if an AI branch is separately opened.

Если новый функциональный слой не может быть объяснён через foundation-layer, он не должен становиться частью ядра проекта.
