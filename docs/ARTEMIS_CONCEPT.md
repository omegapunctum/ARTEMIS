# ARTEMIS — NORTH STAR CONCEPT

## Статус документа

- Тип: canonical foundational concept document.
- Версия: 2.0.
- Дата: 2026-07-26.
- Статус: active.
- Роль: фиксирует миссию, инварианты, North Star и gated development logic.
- Основание: Concept Lock v2; rationale and migration boundary recorded in `docs/work/2026-07-26_CONCEPT_LOCK_V2.md`.

Границы owner documents:

- `ARTEMIS_CONCEPT.md` — долгосрочная идентичность и инварианты;
- `PRODUCT_THESIS.md` — конкретный пользователь, job и hypotheses текущего vertical;
- `ARTEMIS_PRODUCT_SCOPE.md` — текущий разрешённый scope;
- `PROJECT_TRUTH.md` — что фактически доступно;
- `VALIDATION_DECISION.md` — что доказано и какую одну следующую ветвь разрешено открыть.

North Star не является release promise.

## 1. Определение

**ARTEMIS — source-aware research environment, в которой человек сопоставляет сущности и Claims, проверяет EvidenceLinks, различает доказательства и интерпретации и сохраняет версионированный Research Brief. Пространство и время служат привилегированными линзами исследования, когда они усиливают вывод.**

ARTEMIS не является:

- картой с точками;
- геопривязанной энциклопедией;
- generic notes app;
- knowledge graph без пользовательского результата;
- AI chat поверх базы;
- генератором причинных или эффектных выводов без evidence chain.

## 2. Миссия

### 2.1 Основная формулировка

**Миссия ARTEMIS — усиливать человеческое исследование: помогать человеку переходить от вопроса к проверяемому выводу, не теряя источники, неопределённость и собственное авторство суждения.**

### 2.2 Практический смысл

ARTEMIS должен:

- делать сложное знание сопоставимым;
- связывать Claims с конкретным evidence;
- помогать отличать relation от classification/similarity;
- сохранять развитие исследования без переписывания истории;
- переносить результат в эссе, семинар, презентацию или совместную работу;
- показывать, где вывод не завершён.

### 2.3 Роль AI

AI не является второй миссией проекта.

Совместимость с AI — архитектурная опция. После отдельного evidence gate AI может помогать формулировать Claims, находить gaps и объяснять selected evidence, но человек остаётся субъектом суждения, а AI не становится Source.

## 3. Проблема

Исследовательские знания обычно разделены между:

- текстами и bibliography;
- каталогами и object cards;
- картами;
- хронологиями;
- изображениями;
- заметками и черновиками;
- экспертными интерпретациями.

Из-за этого:

- evidence теряет связь с конкретным утверждением;
- общая классификация принимается за историческую связь;
- similarity маскирует отсутствие доказательства;
- uncertainty исчезает при пересказе;
- mutable note не позволяет восстановить старую версию вывода;
- результат трудно передать без длинного устного объяснения.

ARTEMIS закрывает разрыв через evidence-first comparison и версионированный research outcome.

## 4. Жёсткие принципы

### 4.1 Human judgment is primary

Человек формулирует вопрос, выбирает scope и принимает conclusion. Система усиливает, но не заменяет judgment.

### 4.2 Проверяемая цепочка — ядро

Инвариант:

`Question → Claims → Evidence → Comparison → Findings → Conclusion / Unresolved`

Функция входит в ядро только если усиливает эту цепочку.

### 4.3 Map/time are privileged lenses, not dogma

Пространство и время:

- остаются сильной дифференциацией;
- должны быть синхронизированы с Compare/Evidence;
- проверяются against same-content baseline;
- не обязаны кодировать каждое значимое утверждение.

Если map/time не дают дополнительной ценности, scope сужается.

### 4.4 Claim is the unit of evidence

Source связывается с конкретным Claim через EvidenceLink и locator. Entity-level source list не заменяет evidence chain.

### 4.5 Epistemic dimensions are independent

Claim kind, origin, review state, confidence, evidence state и uncertainty не смешиваются.

### 4.6 Relation is a structured Claim

Relation требует конкретного predicate и evidence. Shared classification и computed Similarity не являются substantive Relations.

### 4.7 Uncertainty is a result, not a defect

`Unresolved` допустим и предпочтительнее искусственного conclusion.

### 4.8 Versioned research over mutable snapshots

Investigation развивается через immutable Slice Revisions. Saved View поддерживает revision, но не определяет её смысл.

### 4.9 Database breadth is not product value

Количество Features, Sources или Relations важно только после доказательства глубины module, качества Brief и устойчивости curation cost.

### 4.10 Public truth before product promise

North Star, code, deployment and user-validated value — разные уровни истины.

### 4.11 Future compatibility must not distort present value

Stories, Courses, institutional workflows, AI и reasoning experiments не задают current core model.

## 5. Epistemическая основа

Canonical owner: `EPISTEMIC_CONTRACT.md`.

Базовые objects:

- `Entity` — предмет исследования;
- `Claim` — атомарное утверждение;
- `Source` — provenance/bibliographic unit;
- `EvidenceLink` — supports/challenges/contextualizes Claim с locator;
- `ClassificationAssertion` — Entity classified as Movement/Layer/type;
- `Relation` — structured Claim `subject → predicate → object`;
- `Similarity` — computed comparison output, not evidence.

Ключевые запреты:

- AI as Source;
- source URL as blanket proof;
- `same_movement` as substantive historical Relation;
- Similarity as evidence;
- hypothesis or interpretation as unmarked fact;
- hidden challenging evidence;
- confidence without basis.

## 6. Главная единица ценности

### 6.1 Первый момент ценности

Evidence-aware comparison создаёт первое новое или уточнённое понимание.

### 6.2 Повторно используемый результат

Главный reusable outcome — one immutable `Slice Revision` and its `Research Brief`.

### 6.3 Research-work model

```text
Investigation
└── Slice Revision
    ├── Question
    ├── Entities
    ├── Claims / Findings
    ├── EvidenceLinks
    ├── Conclusion / Unresolved
    ├── Uncertainty
    ├── Dataset / schema identity
    └── Saved View

Research Brief = readable projection of Slice Revision
```

`Investigation` даёт identity развивающейся работе. `Slice Revision` фиксирует версию. `Saved View` восстанавливает UI-context. `Research Brief` переносит результат.

Current mutable `ResearchSlice v2` является compatibility runtime, а не окончательной North Star entity.

## 7. Пользователь и текущий vertical

North Star допускает несколько будущих аудиторий, но current primary user определяется только `PRODUCT_THESIS.md`.

Beachhead:

- старшекурсник или магистрант истории архитектуры/искусства;
- готовит сравнительное задание в ближайшие 1–2 недели.

Potential downstream audiences требуют собственных validation:

- преподаватель/куратор;
- профессиональный исследователь;
- institutional knowledge team;
- author of guided exploration.

Не являются current core:

- casual map browsing;
- social content consumption;
- open unmoderated UGC;
- пользователь, ожидающий готовый causal/predictive answer.

## 8. Core loop текущего продукта

1. Сформулировать или выбрать вопрос.
2. Найти 2–3 объекта через relevant lenses.
3. Сопоставить Claims, classifications and Relations.
4. Проверить EvidenceLinks, locators and uncertainty.
5. Сформулировать findings.
6. Записать conclusion или `unresolved`.
7. Сохранить Slice Revision.
8. Получить Research Brief.
9. Вернуться к Investigation, создать новую revision или передать pinned result.

Stories/Courses/AI не входят в loop.

## 9. Основные сущности North Star

### Knowledge

- Entity;
- Claim;
- Source;
- EvidenceLink;
- ClassificationAssertion;
- Relation;
- Similarity as computed output;
- Media.

### Research product

- Investigation;
- Slice Revision;
- Saved View;
- Research Brief.

### Optional future consumers

- Collection;
- Story/guided route;
- Course/teaching module;
- AI-assisted Claim or explanation;
- institutional workflow.

Optional consumers cannot redefine core research entities.

## 10. Capabilities

### Core data/evidence

- curated entities;
- atomic Claims;
- Sources with locators;
- EvidenceLinks;
- classification separated from Relations;
- uncertainty and conflict;
- controlled publish/review.

### Core research interface

- question framing;
- evidence-aware compare;
- map/time/list/detail lenses;
- visible provenance;
- relation/classification/similarity literacy;
- conclusion/unresolved.

### Core research persistence

- Investigation identity;
- immutable revisions;
- nested Saved View;
- revision-pinned read-only share;
- citation-ready Brief;
- return and new revision.

### Frozen until independent gate

- guided Stories/Courses;
- AI generation/analysis;
- open UGC;
- institutional collaboration;
- new domains;
- structured inference/counterfactual layers.

## 11. Development model: core plus independent branches

ARTEMIS не использует одну линейную лестницу, где каждый слой автоматически ведёт к следующему.

### Core gate

Сначала должны быть доказаны:

- evidence-chain value;
- comparison value;
- epistemic literacy;
- reusable Brief;
- sustainable curation;
- honest public capability.

### Branch A — spatial-temporal depth

Открывается, если map/time дают отдельный observed contribution.

Possible scope:

- richer temporal events/state changes;
- spatial comparison;
- geographic diffusion views.

### Branch B — guided exploration

Открывается, если пользователь или преподаватель нуждается в curated path.

Possible scope:

- routes;
- Stories;
- teaching modules.

### Branch C — source-bound AI assistance

Открывается отдельным safety/value gate.

Possible scope:

- Claim decomposition;
- evidence-gap detection;
- supported comparison;
- hypothesis drafting.

### Branch D — institutional workflow

Открывается только после проверки owner, curation economics, collaboration and governance requirements.

### Branch E — reasoning research

Long-term experimental branch. Она не является продуктовой миссией и не открывается автоматически успехом пользовательского продукта.

Одно решение `EXPAND` разрешает планировать только одну явно названную branch.

## 12. Текущая роль AI

AI generation frozen.

Если branch C будет открыта, AI может:

- разделять broad text на candidate Claims;
- объяснять selected evidence;
- находить missing/challenging evidence;
- сравнивать supported Claims;
- предлагать marked hypothesis;
- указывать uncertainty.

AI не может:

- быть Source;
- выдумывать locator;
- скрывать origin;
- повышать Claim без review;
- создавать canonical Relation;
- подменять conclusion пользователя.

## 13. Критические риски и решения

### 13.1 Дисциплинированная система без cognitive value

Решение: blind Brief rubric и control comparison имеют приоритет над completion metrics.

### 13.2 Map-first dogma

Решение: same-content baseline; `NARROW`, если spatial-temporal increment не подтверждён.

### 13.3 Source laundering

Симптом: Source URL создаёт видимость доказанности broad statement.

Решение: Claim-level EvidenceLink and locator.

### 13.4 Classification laundering

Симптом: `same_movement` выглядит как historical relation graph.

Решение: ClassificationAssertion и исключение из substantive Relation counts.

### 13.5 False reproducibility

Симптом: mutable record/content counter называется reproducible revision.

Решение: immutable revisions, pinned dataset identity, pinned share and Brief.

### 13.6 Premature AI/platform expansion

Решение: independent branch gates; AI compatibility does not define mission.

### 13.7 Content scaling without economics

Решение: измерять preparation/review cost per deep module до corpus expansion.

## 14. Success criteria

Current vertical подтверждён только если:

- participant creates stronger Brief than control;
- Claims trace to relevant evidence and locators;
- Relation/classification/Similarity do not collapse;
- conclusion is calibrated or explicitly unresolved;
- reusable outcome is used in real work;
- map/time contribution is separately measured;
- curation cost is known;
- public/runtime statements remain honest;
- `VALIDATION_DECISION.md` records a supported decision.

## 15. Финальные формулы

### North Star

**ARTEMIS — evidence-first human research environment with privileged spatial-temporal lenses and versioned, source-aware outcomes.**

### Краткая формула

**ARTEMIS помогает человеку перейти от вопроса к проверяемому выводу и сохранить evidence chain в переносимой форме.**

### Текущий продукт

**ARTEMIS Architecture Atlas помогает студенту истории архитектуры превратить сравнительный вопрос о 2–3 объектах в evidence-backed Research Brief.**

## 16. Official lock

Считаются утверждёнными:

1. human research as the only mission;
2. evidence chain as core;
3. map/time as validated lenses, not dogma;
4. Claim/EvidenceLink foundation;
5. Relation as structured Claim;
6. shared classification and Similarity separated from Relation;
7. Investigation/SliceRevision/SavedView/ResearchBrief model;
8. current runtime separated from target model;
9. deep research modules before external validation;
10. independent evidence gates for future branches.

Пересмотр любого пункта требует нового foundation decision, а не локального feature PR.
