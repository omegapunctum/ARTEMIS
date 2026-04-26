# ARTEMIS — EPISTEMIC CONTRACT

## Статус документа

- Тип: foundation epistemic contract document
- Статус: active, pending canonical registration in `PROJECT_STRUCTURE.md` and `DOCUMENTATION_SYSTEM.md`
- Роль: фиксирует операционную модель знания ARTEMIS
- Назначение: определить, как ARTEMIS различает факты, источники, связи, интерпретации, гипотезы, AI-output, неопределённость и контрфактические сценарии
- Scope: data, UI, moderation, research slices, stories, courses, AI assistance, content governance

---

## 1. Главный принцип

ARTEMIS не должен притворяться системой абсолютного знания.

ARTEMIS должен явно различать:

- что известно;
- откуда это известно;
- насколько это надёжно;
- что является фактом;
- что является связью;
- что является интерпретацией;
- что является гипотезой;
- что сгенерировано AI;
- где есть неопределённость;
- что является альтернативным или контрфактическим сценарием.

Главное правило:

> Fact, interpretation, hypothesis, AI output and counterfactual scenario must never be presented as the same epistemic type.

---

## 2. Зачем нужен epistemic contract

Без epistemic contract ARTEMIS рискует стать:

- красивой картой с непроверяемыми утверждениями;
- AI-слоем, который смешивает факты и предположения;
- образовательным продуктом с неявной достоверностью;
- базой данных, где источник и интерпретация неразличимы;
- псевдоисследовательской системой, выдающей уверенные выводы без оснований.

Epistemic contract нужен, чтобы:

- сохранить научную и логическую дисциплину;
- сделать AI-output объяснимым и ограниченным;
- обеспечить trust model для content governance;
- дать UI понятные статусы знания;
- защитить stories/courses от смешения факта и narrative interpretation;
- подготовить фундамент для будущих reasoning layers.

---

## 3. Epistemic layers

ARTEMIS использует несколько уровней знания.

### 3.1 Fact

Fact — утверждение, которое ARTEMIS принимает как проверенное в пределах текущего источникового и data-governance baseline.

Примеры:
- объект существует;
- объект имеет название;
- объект связан с координатами;
- событие относится к определённой дате или диапазону;
- источник подтверждает указанный атрибут.

Правила:
- fact должен иметь provenance или быть частью curated baseline;
- fact может иметь confidence/uncertainty;
- fact не обязан быть абсолютно бесспорным, но его статус должен быть обоснован;
- contested fact должен быть маркирован как contested или uncertain, если конфликт известен.

### 3.2 Source

Source — происхождение данных или утверждения.

Source может быть:
- primary source;
- academic/curated secondary source;
- official source;
- reference source;
- expert estimate;
- user-provided source;
- AI-generated reference candidate, not accepted as source until reviewed.

Правила:
- AI не является source;
- source должен быть отделён от текста интерпретации;
- отсутствие source должно быть видимо для curator/reviewer;
- source quality влияет на confidence.

### 3.3 Relation

Relation — связь между сущностями.

Relation может быть:
- spatial;
- temporal;
- part-of;
- located-in;
- influenced-by;
- caused-by candidate;
- associated-with;
- sequence;
- membership;
- authorship;
- provenance relation.

Правила:
- relation должна иметь type;
- relation должна иметь epistemic status;
- relation не должна автоматически означать causality;
- weak relation должна быть маркирована как weak/uncertain/hypothesis;
- AI-suggested relation не становится canonical relation без review.

### 3.4 Interpretation

Interpretation — объяснительная рамка или прочтение фактов и связей.

Примеры:
- почему группа объектов важна;
- как можно понимать пространственное распределение;
- как один historical pattern связан с другим;
- что означает выбранная конфигурация объектов.

Правила:
- interpretation не является fact;
- interpretation должна быть маркирована;
- interpretation должна показывать, на каких facts/relations она основана;
- competing interpretations допустимы и не должны подавляться ложной уверенностью.

### 3.5 Hypothesis

Hypothesis — предположение, которое может объяснять данные, но не подтверждено как факт.

Примеры:
- возможная связь между двумя процессами;
- вероятная причина spatial pattern;
- возможная реконструкция отсутствующих данных;
- AI-suggested explanation.

Правила:
- hypothesis всегда маркируется явно;
- hypothesis не может быть показана как fact;
- hypothesis должна иметь основание или объяснение, почему она предложена;
- hypothesis может быть rejected, promoted или archived after review.

### 3.6 AI Output

AI Output — любой вывод, summary, comparison, explanation, hypothesis или draft, созданный AI.

Правила:
- AI output не является source;
- AI output не является fact by default;
- AI output должен иметь visible AI marking;
- AI output должен быть привязан к input context where possible;
- AI output must expose epistemic type: summary, explanation, comparison, hypothesis, draft, warning;
- AI output может стать human-reviewed interpretation или draft content, но не automatically canonical fact.

### 3.7 Uncertainty

Uncertainty — явная неполнота, спорность или ограниченность знания.

Типы uncertainty:
- date uncertainty;
- coordinate uncertainty;
- source conflict;
- attribution uncertainty;
- identity ambiguity;
- reconstruction uncertainty;
- AI confidence limitation;
- incomplete data.

Правила:
- uncertainty must be visible when relevant;
- uncertainty is not a failure of ARTEMIS, but part of the knowledge model;
- hiding uncertainty is epistemic degradation;
- uncertain records may still be useful if correctly marked.

### 3.8 Counterfactual

Counterfactual — альтернативный сценарий, который не описывает фактически произошедшую историю.

Правила:
- counterfactual must be separated from historical reality;
- counterfactual is not baseline v1.0 product promise;
- counterfactual cannot be mixed into public data as event/fact;
- future counterfactual layers require explicit product, epistemic and UI contract.

---

## 4. Epistemic status vocabulary

Базовые статусы:

| Status | Meaning |
|---|---|
| `verified` | принято как проверенное в curated baseline |
| `source_backed` | поддержано источником, но может требовать контекста |
| `curated` | принято curator/editorial process |
| `estimated` | оценочное значение, например coordinates/date |
| `uncertain` | достоверность ограничена или неполна |
| `contested` | есть конфликт источников или интерпретаций |
| `interpretation` | объяснительное прочтение, не fact |
| `hypothesis` | предположение, не подтверждённое как fact |
| `ai_generated` | создано AI, не source-backed by default |
| `counterfactual` | альтернативный сценарий, не historical reality |
| `rejected` | отклонено moderation/validation process |

Status vocabulary может расширяться, но новые статусы должны быть согласованы с `CONTENT_GOVERNANCE.md`, `DATA_CONTRACT.md` и UI labels.

---

## 5. Source hierarchy

Базовая иерархия источников:

1. primary/official source;
2. peer-reviewed academic source;
3. curated institutional source;
4. reputable reference source;
5. expert estimate with explanation;
6. user-provided source pending review;
7. AI-suggested source candidate pending verification.

Правила:
- source hierarchy влияет на confidence, но не заменяет curator judgment;
- lower-tier source может быть принят, если он явно маркирован и лучше недоступен;
- conflicting high-quality sources должны сохранять conflict marker;
- AI-suggested sources require human/source verification before use.

---

## 6. Confidence model

Confidence не должен быть декоративным полем.

Confidence используется для:
- coordinates;
- dates;
- attribution;
- identity matching;
- relation strength;
- AI output limitations;
- source quality.

Минимальная шкала:

| Confidence | Meaning |
|---|---|
| `high` | хорошо подтверждено, low known uncertainty |
| `medium` | подтверждено, но есть ограничения |
| `low` | слабое основание, нужна осторожность |
| `unknown` | confidence не установлен |

Для coordinates допустимы отдельные domain-specific значения, если они закреплены в `DATA_CONTRACT.md`.

Правило:
- confidence не должен скрываться в UI, если от него зависит смысл вывода.

---

## 7. Data requirements

Data layer должен поддерживать epistemic clarity.

Минимальные требования:

- entity/feature должен иметь source/provenance where available;
- date uncertainty должна быть представима;
- coordinate confidence должна быть представима;
- relation должен иметь type and epistemic status;
- AI-generated data must not enter canonical dataset without review;
- rejected or uncertain data must be traceable in validation/moderation flow.

`DATA_CONTRACT.md` определяет текущую checked-in/public artifact shape. Этот document определяет epistemic meaning, который должен учитываться при расширении data schema.

---

## 8. UI requirements

UI должен помогать пользователю различать epistemic types.

Минимальные требования:

- fact-like content must not look identical to hypothesis;
- AI-generated summary must be marked as AI-generated;
- uncertainty/confidence should be visible where relevant;
- source/provenance should be reachable from detail context;
- contested/estimated data must not be visually flattened into verified data;
- counterfactual mode, if ever introduced, must be visually and structurally separated.

Failure mode:
- if UI makes uncertain/AI/hypothesis content look like verified fact, epistemic contract is broken.

---

## 9. Research Slice requirements

Research Slice may contain:
- facts;
- selected source-backed entities;
- user annotations;
- interpretations;
- hypotheses;
- AI summaries;
- AI comparisons.

Rules:
- annotations must have epistemic type;
- AI annotations must be marked;
- hypothesis annotations must be marked;
- user note must not be treated as source-backed fact;
- slice-level AI summary must expose input context;
- slice compare must not imply causality unless explicitly marked and supported.

`RESEARCH_SLICE_CONTRACT.md` owns product semantics of slice. This document owns epistemic rules for content inside or derived from slice.

---

## 10. Stories and courses requirements

Stories and courses may simplify, sequence and explain content, but they must not erase epistemic distinctions.

Rules:
- narrative compression must not remove uncertainty when uncertainty is material;
- course explanations must not present hypothesis as established fact;
- story steps should preserve source/provenance access where relevant;
- AI-assisted story/course drafts must remain drafts until reviewed;
- educational clarity must not override epistemic honesty.

---

## 11. AI requirements

AI in ARTEMIS is assistant, explainer and hypothesis generator, not source of truth.

Allowed AI functions:

- summarize source-backed context;
- explain visible slice configuration;
- compare selected entities/slices;
- identify possible patterns;
- suggest hypotheses;
- expose uncertainty;
- draft story/course explanations;
- point out weak evidence or missing data.

Forbidden AI functions:

- invent source-backed facts;
- silently upgrade hypothesis to fact;
- hide uncertainty;
- make causal claims without status marking;
- publish canonical content without review;
- treat AI answer as evidence;
- mix counterfactual and historical reality.

AI output must include, where relevant:

- input context;
- entities considered;
- source/provenance basis;
- epistemic status;
- uncertainty note;
- whether output is summary, interpretation, hypothesis or draft.

---

## 12. Moderation and content governance requirements

Moderation must distinguish data validity from epistemic validity.

A record may be technically valid but epistemically weak.

Examples:
- correct JSON but weak source;
- valid coordinates but low confidence;
- plausible relation but unsupported;
- useful user note but not canonical fact;
- AI-generated draft that requires human review.

Moderation decisions should be able to classify:

- accept as fact;
- accept as source-backed but uncertain;
- accept as interpretation;
- keep as hypothesis;
- request better source;
- reject;
- archive as non-canonical note.

`CONTENT_GOVERNANCE.md` will own the full governance lifecycle after creation.

---

## 13. Conflict handling

When sources or interpretations conflict:

1. Do not silently choose one unless governance policy allows it.
2. Preserve conflict marker if material.
3. Prefer better source quality, but document uncertainty.
4. Keep interpretations separate from source-backed facts.
5. Do not let AI resolve source conflicts without review.
6. If conflict affects public display, UI should expose uncertainty or contested status.

---

## 14. Epistemic failure modes

The system violates this contract if:

- AI output appears as verified fact;
- hypothesis appears as fact;
- counterfactual appears as history;
- source is missing but confidence is shown as high;
- user annotation becomes canonical content automatically;
- relation implies causality without support;
- uncertainty is hidden because it is visually inconvenient;
- course/story text simplifies away essential source conflict;
- public data includes AI-generated facts without review.

---

## 15. Relationship to other foundation docs

- `ARTEMIS_CONCEPT.md` defines the philosophical and strategic need for epistemic separation.
- `EPISTEMIC_CONTRACT.md` defines operational epistemic rules.
- `DATA_CONTRACT.md` defines current data artifact shape.
- `RESEARCH_SLICE_CONTRACT.md` defines how epistemic content appears inside slice context.
- `CONTENT_GOVERNANCE.md` will define how epistemic claims are accepted, rejected, reviewed or promoted.
- `AI_POLICY.md` will define AI behavior boundaries.
- `ENTITY_MODEL.md` will define entity/relation/source/media model.

If those documents conflict after creation, the conflict must be resolved by updating the relevant foundation docs rather than relying on an audit note.

---

## 16. Change-control rule

Any change that affects epistemic status, source confidence, AI output marking, moderation classification, relation types or public presentation of uncertainty must check impact on:

- `ARTEMIS_CONCEPT.md`;
- `ARTEMIS_PRODUCT_SCOPE.md`;
- `DATA_CONTRACT.md`;
- `RESEARCH_SLICE_CONTRACT.md`;
- `CONTENT_GOVERNANCE.md` after creation;
- `AI_POLICY.md` after creation;
- UI labels and detail panels;
- moderation flows;
- tests/release checks if executable behavior changes.

---

## 17. Итоговое правило

ARTEMIS should be confident only where the knowledge model justifies confidence.

The project must prefer visible uncertainty over false certainty.

A weaker but honest epistemic state is better than a strong but unsupported claim.
