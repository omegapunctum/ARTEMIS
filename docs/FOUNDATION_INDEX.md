# ARTEMIS — FOUNDATION INDEX

## Статус документа

- Тип: canonical foundation index document
- Статус: active
- Роль: главный навигатор фундаментального слоя ARTEMIS
- Назначение: фиксирует, какие документы образуют foundation-layer, в каком порядке их читать и какой документ отвечает за какой тип решений
- Scope: concept, product scope, research slice, epistemic model, entity model, content governance, AI policy, data/release/runtime/documentation boundaries

---

## 1. Назначение foundation-layer

Foundation-layer ARTEMIS нужен, чтобы проект развивался как единая система, а не как набор отдельных модулей: карта, курсы, stories, AI, UGC, data pipeline и UI.

Фундаментальный слой отвечает на вопросы:

1. Что такое ARTEMIS.
2. Что является главной единицей ценности.
3. Что считается знанием внутри ARTEMIS.
4. Какие сущности существуют в системе.
5. Как проверяется и утверждается контент.
6. Что может и не может делать AI.
7. Какие документы являются source of truth для архитектуры, данных, release и документационной системы.

---

## 2. Главный принцип

ARTEMIS нельзя развивать через отдельные функции без проверки их связи с фундаментом.

Любое новое направление должно усиливать одну из базовых опор:

- spatial-temporal research workspace;
- research slice as primary value unit;
- explainable knowledge structure;
- curated and governed content;
- clear epistemic separation of facts, interpretations, hypotheses and AI outputs;
- controlled release/data/runtime discipline.

Если функция не усиливает эти опоры, она не входит в ядро ARTEMIS.

---

## 3. Текущий canonical foundation set

На текущем этапе foundation-layer состоит из уже действующих canonical docs и planned foundation docs.

### 3.1 Already canonical

| Документ | Роль |
|---|---|
| `README.md` | root entrypoint проекта |
| `docs/ARTEMIS_CONCEPT.md` | миссия, видение, принципы, epistemic model, стратегическая лестница развития |
| `docs/ARTEMIS_PRODUCT_SCOPE.md` | продуктовые границы v1.0, главная единица ценности, product loop, запреты против product drift |
| `docs/ARTEMIS_MASTER_PROMPT.md` | operational governance для AI-агентов и docs-first discipline |
| `docs/PROJECT_STRUCTURE.md` | структура репозитория, runtime boundaries, canonical entrypoints, documentation layers |
| `docs/PROJECT_PHASES.md` | фазы, переходы и текущий active cycle |
| `docs/PRIORITIES.md` | текущие load-bearing приоритеты |
| `docs/DATA_CONTRACT.md` | ETL/data/public map/release artifact contract |
| `docs/CONTROLLED_RELEASE_DECISION.md` | controlled release baseline, release/readiness interpretation, production-grade limitations |
| `docs/DOCUMENTATION_SYSTEM.md` | documentation governance, роли слоёв, правила конфликтов |

### 3.2 Foundation docs to be added

| Документ | Статус | Назначение |
|---|---|---|
| `docs/RESEARCH_SLICE_CONTRACT.md` | planned | canonical product/data/UI/AI contract для research slice как главной единицы ценности |
| `docs/EPISTEMIC_CONTRACT.md` | planned | operational contract для fact/source/relation/interpretation/hypothesis/AI-output/uncertainty/provenance |
| `docs/ENTITY_MODEL.md` | planned | единая модель сущностей ARTEMIS и их отношений |
| `docs/CONTENT_GOVERNANCE.md` | planned | правила источников, валидации, модерации, UGC promotion и доверия к данным |
| `docs/AI_POLICY.md` | planned | canonical границы AI: допустимые функции, запреты, маркировка AI-output и source discipline |

Planned foundation docs не считаются действующими source of truth, пока они не созданы и не добавлены в `PROJECT_STRUCTURE.md` / `DOCUMENTATION_SYSTEM.md` как часть canonical layer.

---

## 4. Порядок чтения foundation docs

Рекомендуемый порядок чтения:

1. `README.md` — быстрый вход в проект.
2. `docs/FOUNDATION_INDEX.md` — карта фундаментального слоя.
3. `docs/ARTEMIS_CONCEPT.md` — зачем существует ARTEMIS и какие принципы нельзя нарушать.
4. `docs/ARTEMIS_PRODUCT_SCOPE.md` — что входит и не входит в ARTEMIS v1.0.
5. `docs/RESEARCH_SLICE_CONTRACT.md` — что является главной единицей ценности и как она работает.
6. `docs/EPISTEMIC_CONTRACT.md` — что считается знанием и как маркируется достоверность.
7. `docs/ENTITY_MODEL.md` — какие сущности и связи существуют в системе.
8. `docs/CONTENT_GOVERNANCE.md` — как данные становятся trusted content.
9. `docs/AI_POLICY.md` — что AI может и не может делать.
10. `docs/DATA_CONTRACT.md` — как данные проходят через ETL/export/public artifacts.
11. `docs/PROJECT_STRUCTURE.md` — где это живёт в repo/runtime/docs system.
12. `docs/PROJECT_PHASES.md` и `docs/PRIORITIES.md` — что делать сейчас.
13. `docs/CONTROLLED_RELEASE_DECISION.md` — как трактовать release baseline.
14. `docs/DOCUMENTATION_SYSTEM.md` — как разрешать doc-conflicts и где хранить документы.
15. `docs/ARTEMIS_MASTER_PROMPT.md` — как AI-агенты должны работать с проектом.

Если planned foundation document ещё не создан, временным authority является ближайший действующий canonical doc:

- research slice → `ARTEMIS_PRODUCT_SCOPE.md` + `RESEARCH_SLICE_SPEC.md`;
- epistemic model → `ARTEMIS_CONCEPT.md`;
- entity model → `ARTEMIS_CONCEPT.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `DATA_CONTRACT.md`;
- content governance → `DATA_CONTRACT.md`, moderation docs, release/audit notes;
- AI policy → `ARTEMIS_CONCEPT.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `docs/work/ARTEMIS_AI_STRATEGY_v1_0.md`.

---

## 5. Решения по типам вопросов

### 5.1 Concept / mission questions

Primary authority:
- `docs/ARTEMIS_CONCEPT.md`

Secondary authority:
- `docs/ARTEMIS_PRODUCT_SCOPE.md`

Примеры вопросов:
- чем является ARTEMIS;
- почему ARTEMIS не просто карта;
- почему AI не является source of truth;
- почему факт, интерпретация и гипотеза должны быть разделены.

### 5.2 Product scope questions

Primary authority:
- `docs/ARTEMIS_PRODUCT_SCOPE.md`

Secondary authority:
- `docs/PROJECT_PHASES.md`
- `docs/PRIORITIES.md`

Примеры вопросов:
- входит ли feature в v1.0;
- что является primary user value;
- что делать сначала: slice, story, course или AI;
- какие направления являются forbidden product drift.

### 5.3 Research slice questions

Current authority:
- `docs/ARTEMIS_PRODUCT_SCOPE.md`
- `docs/RESEARCH_SLICE_SPEC.md`

Future primary authority:
- `docs/RESEARCH_SLICE_CONTRACT.md`

Примеры вопросов:
- чем slice отличается от saved view;
- как slice связан со story/course/AI;
- что входит в minimal slice;
- как работает lifecycle slice.

### 5.4 Knowledge / epistemic questions

Current authority:
- `docs/ARTEMIS_CONCEPT.md`

Future primary authority:
- `docs/EPISTEMIC_CONTRACT.md`

Примеры вопросов:
- что является фактом;
- что является интерпретацией;
- как маркировать гипотезу;
- как показывать AI-output;
- как работать с uncertainty.

### 5.5 Entity / relation questions

Current authority:
- `docs/ARTEMIS_CONCEPT.md`
- `docs/ARTEMIS_PRODUCT_SCOPE.md`
- `docs/DATA_CONTRACT.md`

Future primary authority:
- `docs/ENTITY_MODEL.md`

Примеры вопросов:
- что такое entity;
- чем object отличается от event/process/place;
- как relation связывает сущности;
- как source/media относятся к entity.

### 5.6 Content trust / governance questions

Current authority:
- `docs/DATA_CONTRACT.md`
- moderation/runtime docs
- relevant audit notes

Future primary authority:
- `docs/CONTENT_GOVERNANCE.md`

Примеры вопросов:
- как объект становится canonical content;
- как решать конфликт источников;
- что делать со спорными координатами;
- как UGC становится trusted;
- когда запись отклоняется.

### 5.7 AI behavior questions

Current authority:
- `docs/ARTEMIS_CONCEPT.md`
- `docs/ARTEMIS_PRODUCT_SCOPE.md`
- `docs/work/ARTEMIS_AI_STRATEGY_v1_0.md`

Future primary authority:
- `docs/AI_POLICY.md`

Примеры вопросов:
- может ли AI генерировать historical claim;
- как маркировать AI hypothesis;
- может ли AI менять canonical data;
- как AI должен использовать slice context.

### 5.8 Data / release / runtime questions

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

## 6. Правило разрешения конфликтов

Если документы расходятся, действует порядок:

1. executable checks / tests / workflows for runtime facts;
2. `DATA_CONTRACT.md` for data/export/public map contract;
3. `CONTROLLED_RELEASE_DECISION.md` for release/readiness interpretation;
4. `ARTEMIS_CONCEPT.md` for mission/principles/epistemic constraints;
5. `ARTEMIS_PRODUCT_SCOPE.md` for v1.0 scope/product boundaries;
6. planned foundation docs after creation and canonical registration;
7. `PROJECT_STRUCTURE.md` for repo/runtime/docs boundaries;
8. `PROJECT_PHASES.md` and `PRIORITIES.md` for current work order;
9. `DOCUMENTATION_SYSTEM.md` for doc placement/governance conflicts;
10. working docs;
11. audits;
12. archive/reference.

Audit documents may reveal a conflict, but they do not become source of truth by themselves. The relevant canonical or working document must be updated.

---

## 7. Foundation change-control rule

A foundation document may be created or changed only if the change clearly states:

- what problem it solves;
- which existing canonical documents it affects;
- whether it changes product scope, data contract, AI behavior, content governance or runtime boundaries;
- which docs must be updated after the change;
- which tests/checks should be run if executable behavior is affected.

Foundation changes must not be mixed with unrelated UI/runtime refactors.

---

## 8. Forbidden shortcuts

Запрещено:

- добавлять AI-функции без проверки against AI policy / concept principles;
- развивать stories/courses вне research slice model;
- превращать object card в главную продуктовую единицу вместо slice;
- использовать UGC as canonical content без governance;
- смешивать fact, interpretation, hypothesis и AI-output;
- создавать новый source of truth в working docs или audits;
- использовать archive/reference documents как current guidance;
- расширять ARTEMIS в generic GIS/LMS/social/wiki platform без foundation decision.

---

## 9. Ближайший порядок foundation work

P0:
1. создать `docs/RESEARCH_SLICE_CONTRACT.md`;
2. создать `docs/EPISTEMIC_CONTRACT.md`;
3. сверить оба документа с `ARTEMIS_CONCEPT.md`, `ARTEMIS_PRODUCT_SCOPE.md`, `DATA_CONTRACT.md` и `RESEARCH_SLICE_SPEC.md`.

P1:
4. создать `docs/ENTITY_MODEL.md`;
5. создать `docs/CONTENT_GOVERNANCE.md`;
6. создать `docs/AI_POLICY.md`.

P2:
7. обновить `docs/PROJECT_STRUCTURE.md`;
8. обновить `docs/DOCUMENTATION_SYSTEM.md`;
9. обновить `docs/ARTEMIS_MASTER_PROMPT.md`;
10. создать или обновить `docs/archive/README.md` для управляемого archive cleanup.

---

## 10. Итоговое правило

ARTEMIS должен развиваться от фундаментальной модели знания к продуктовым слоям, а не наоборот.

Порядок развития:

1. concept and product scope;
2. research slice contract;
3. epistemic contract;
4. entity model;
5. content governance;
6. AI policy;
7. stories/courses/AI/runtime expansion.

Если новый функциональный слой не может быть объяснён через foundation-layer, он не должен становиться частью ядра проекта.
