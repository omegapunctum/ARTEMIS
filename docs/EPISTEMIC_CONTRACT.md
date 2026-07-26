# ARTEMIS — EPISTEMIC CONTRACT

## Статус документа

- Тип: canonical foundation epistemic contract.
- Версия: 2.0.
- Дата: 2026-07-26.
- Статус: active.
- Роль: определяет Claim/Evidence model и независимые epistemic dimensions.
- Scope: canonical knowledge, user research, UI, moderation, future AI assistance and migration compatibility.

## 1. Главный принцип

ARTEMIS не должен притворяться системой абсолютного знания.

Проверяемая единица — не объект, карточка или source URL, а конкретный `Claim` и его evidence chain.

Главное правило:

> Claim kind, origin, review state, confidence, evidence state and uncertainty are independent dimensions and must never be collapsed into one ambiguous status.

Следствия:

- Source не подтверждает сущность «в целом»;
- AI является origin, а не типом истины;
- `reviewed` не означает `high confidence`;
- `source-backed` не означает, что source действительно supports claim;
- uncertainty не превращает автоматически factual Claim в hypothesis;
- Relation не имеет особой эпистемологии: это структурированный Claim.

## 2. Core objects

### 2.1 Claim

`Claim` — атомарное утверждение, которое можно понять, проверить, поддержать, оспорить или оставить unresolved.

Минимальный conceptual shape:

```text
Claim
├── id
├── statement
├── subject/reference context
├── claim_kind
├── origin
├── review_state
├── confidence
├── evidence_state
├── uncertainty[]
└── evidence_links[]
```

Claim должен быть достаточно узким, чтобы один EvidenceLink имел ясный смысл.

Плохо:

> Объект важен, красив, повлиял на архитектуру и относится к движению X.

Хорошо:

> Источник датирует завершение объекта 1931 годом.

> Автор интерпретирует композицию как переосмысление конкретного прецедента.

### 2.2 Source

`Source` — библиографическая/provenance единица. Source может содержать множество утверждений и не принимается целиком как доказательство любого Claim.

Минимальные свойства:

- stable id;
- title;
- author/organization;
- source type;
- URL or bibliographic locator;
- review state;
- optional publication metadata.

AI output не является Source. AI может предложить source candidate, который требует отдельной проверки.

### 2.3 EvidenceLink

`EvidenceLink` связывает один Claim с одним Source.

Минимальный conceptual shape:

```text
EvidenceLink
├── claim_id
├── source_id
├── locator
├── relation_to_claim
├── evidence_strength
├── reviewer
└── review_state
```

`relation_to_claim`:

| Value | Meaning |
|---|---|
| `supports` | source даёт основание принять Claim в заявленной форме |
| `challenges` | source противоречит Claim или существенно его ограничивает |
| `contextualizes` | source объясняет контекст, но сам по себе не доказывает Claim |

`evidence_strength`:

| Value | Meaning |
|---|---|
| `direct` | source явно утверждает или документирует Claim |
| `indirect` | Claim следует из допустимого ограниченного синтеза |
| `background` | source даёт общий контекст, не достаточный для сильного вывода |

Locator обязателен для validation modules. Это может быть page, section, chapter, figure, stable fragment or equivalent bibliographic pointer.

### 2.4 RelationClaim

`Relation` — структурированная форма Claim:

`subject → predicate → object`

RelationClaim дополнительно определяет:

- directionality;
- temporal validity where relevant;
- scope/qualifiers;
- allowed predicate;
- evidence chain.

Relation не становится доказанной только потому, что endpoints существуют или похожи.

### 2.5 ClassificationAssertion

`ClassificationAssertion` связывает Entity с Movement, Layer, typology or other classification.

`Feature A` и `Feature B` в одном Movement означают две assertions:

- `Feature A classified_as Movement X`;
- `Feature B classified_as Movement X`.

Pairwise `same_movement` является derived shared-classification view, а не substantive historical Relation.

### 2.6 Similarity

`Similarity` — вычисляемая близость по явно названным критериям.

Similarity:

- не имеет canonical Relation identity;
- не является evidence;
- не становится influence/derivation claim без editorial review и EvidenceLinks;
- должна показывать критерии расчёта.

## 3. Independent epistemic dimensions

### 3.1 Claim kind

| Value | Meaning |
|---|---|
| `factual` | утверждение о внешнем мире, принимаемое как проверяемое |
| `interpretation` | объяснительное или аналитическое прочтение |
| `hypothesis` | проверяемое предположение с недостаточным подтверждением |
| `counterfactual` | условный сценарий, не описывающий фактически произошедшее |

`RelationClaim` и `ClassificationAssertion` являются structural forms, а не отдельными claim kinds. Например, influence Relation может быть factual, interpretive or hypothetical.

### 3.2 Origin

| Value | Meaning |
|---|---|
| `curator` | сформулировано редактором/исследователем corpus |
| `user` | сформулировано пользователем Investigation |
| `ai` | предложено AI |
| `system` | детерминированно сформировано системой из явных данных |
| `imported` | пришло из source system и ещё требует ownership/review context |

Origin не определяет истинность. Human-authored Claim может быть слабым; AI-origin Claim может быть полезной hypothesis, но не Source.

### 3.3 Review state

| Value | Meaning |
|---|---|
| `draft` | не прошёл review |
| `reviewed` | проверен в заявленном scope |
| `contested` | существует существенное несогласие или конфликт |
| `rejected` | отклонён для заявленного использования |
| `superseded` | заменён новой revision, сохранён для traceability |

`curated` — governance role/process label, а не отдельный epistemic state.

### 3.4 Confidence

| Value | Meaning |
|---|---|
| `high` | сильное основание, low known uncertainty |
| `medium` | достаточное основание с material limitations |
| `low` | слабое основание, требуется осторожность |
| `unknown` | оценка не проведена |

Confidence должен иметь basis. Декоративная уверенность запрещена.

### 3.5 Evidence state

| Value | Meaning |
|---|---|
| `supported` | есть reviewed supporting EvidenceLink |
| `mixed` | supporting и challenging evidence materially coexist |
| `challenged` | available evidence существенно противоречит Claim |
| `missing` | evidence отсутствует |
| `not_applicable` | evidence link не применим, например к явно личной заметке |

Evidence state является derived summary EvidenceLinks, а не ручным substitute для них.

### 3.6 Uncertainty

Uncertainty хранится отдельно и может включать:

- date;
- location;
- attribution;
- identity;
- classification;
- relation;
- source conflict;
- reconstruction;
- missing evidence;
- scope limitation;
- translation/terminology.

Uncertainty должна описывать, что именно неизвестно и как это влияет на Claim.

## 4. Compatibility vocabulary

Current data/runtime использует смешанное поле `epistemic_status`. Оно сохраняется до отдельной migration, но считается compatibility projection.

| Legacy value | Target interpretation |
|---|---|
| `verified` | `review_state=reviewed`; evidence/confidence определяются отдельно |
| `source_backed` | derived `evidence_state=supported`, если EvidenceLink действительно supports |
| `curated` | governance provenance; обычно `origin=curator`, но не review/confidence |
| `estimated` | factual Claim + explicit uncertainty; confidence отдельно |
| `uncertain` | explicit uncertainty; не claim kind |
| `contested` | `review_state=contested` и обычно `evidence_state=mixed/challenged` |
| `interpretation` | `claim_kind=interpretation` |
| `hypothesis` | `claim_kind=hypothesis` |
| `ai_generated` | `origin=ai` |
| `counterfactual` | `claim_kind=counterfactual` |
| `rejected` | `review_state=rejected` |

Запрещено:

- добавлять новые target capabilities, полагаясь только на legacy status;
- мигрировать legacy records догадкой;
- назначать EvidenceLinks, locators или confidence без evidence;
- считать compatibility mapping lossless.

## 5. Source quality

Default source-quality order:

1. primary/official source;
2. peer-reviewed academic source;
3. curated institutional source;
4. reputable reference source;
5. expert estimate with explanation;
6. user-provided source pending review;
7. AI-suggested source candidate pending verification.

Source hierarchy:

- помогает оценить evidence strength;
- не заменяет проверку конкретного passage;
- не гарантирует поддержку любого Claim;
- не разрешает скрывать конфликт качественных sources.

## 6. Relation rules

Substantive Relation predicates должны быть конкретными.

Current Architecture Atlas target families:

| Family | Examples |
|---|---|
| structural | `part_of`, `contains` |
| derivation/reception | `influenced`, `modelled_on`, `derived_from`, `adapted_from`, `inspired_by` |
| reconstruction | `reconstructed_from` |
| agency/authorship | reserved for entity-model expansion |
| event/state | reserved for temporal-state expansion |

Rules:

- `associated_with` не используется как замена неизвестному predicate;
- before/after from dates is a comparison result, not automatically a stored Relation;
- `same_movement` is ClassificationAssertion projection;
- influence/derivation needs Claim-level evidence and locator;
- indirect cross-source synthesis must be marked `indirect` and explain the inference;
- AI-suggested Relation remains `origin=ai`, `review_state=draft`, usually `claim_kind=hypothesis`;
- causal predicate requires separate approved policy and is out of current scope.

## 7. Research-work requirements

Slice Revision contains or references:

- research question;
- compared entities;
- user-authored Claims/findings;
- EvidenceLinks selected for major Claims;
- conclusion Claim or explicit `unresolved`;
- uncertainty;
- dataset/schema revision;
- Saved View.

Rules:

- major conclusion must be traceable to Claims and EvidenceLinks;
- unsupported user Claim may be preserved as hypothesis or missing-evidence finding;
- user note is not canonical fact;
- revision does not promote Claims into public knowledge;
- Research Brief must preserve epistemic dimensions material to the conclusion;
- shared output must pin a revision or explicitly identify itself as mutable/live.

`RESEARCH_SLICE_CONTRACT.md` owns the research-work lifecycle. This document owns epistemic meaning inside it.

## 8. UI requirements

Primary UI may simplify labels, but must not erase target meaning.

At minimum the user can distinguish:

- source-supported factual Claim;
- interpretation;
- hypothesis/unresolved;
- substantive Relation;
- shared classification;
- computed Similarity;
- challenging or missing evidence;
- material uncertainty;
- AI-origin content if introduced.

Source title without locator is insufficient for claim-level validation.

Failure mode:

- if shared classification, Similarity or AI output looks like reviewed substantive Relation, this contract is broken.

## 9. Moderation and governance

Technical validity and epistemic validity are separate.

A valid record may still contain:

- irrelevant EvidenceLink;
- source that does not support the Claim;
- locator that cannot be reproduced;
- overbroad Claim;
- unmarked synthesis;
- wrong claim kind;
- hidden conflict;
- unsupported Relation.

Review decisions operate on Claim/EvidenceLink where possible:

- accept as reviewed Claim;
- accept with medium/low confidence;
- accept as interpretation;
- keep as hypothesis;
- mark mixed/contested;
- request better evidence/locator;
- reject;
- supersede without erasing history.

Canonical promotion requires explicit governance. Investigation content remains private/user-authored unless separately submitted and reviewed.

## 10. Conflict handling

When sources conflict:

1. Preserve both EvidenceLinks when material.
2. Mark `relation_to_claim=challenges` where appropriate.
3. Set evidence state to `mixed` or `challenged`.
4. Record uncertainty and scope.
5. Do not let AI silently resolve conflict.
6. Do not flatten competing interpretations into a factual Claim.

## 11. AI requirements

AI is future optional assistance, not current mission.

If introduced, AI may:

- propose atomic Claims;
- summarize selected source passages;
- identify missing EvidenceLinks;
- compare supported Claims;
- suggest hypotheses;
- point out conflicts and uncertainty.

AI must not:

- become Source;
- invent locator;
- promote its Claim without review;
- hide `origin=ai`;
- turn Similarity/classification into Relation;
- resolve contested evidence as fact;
- publish canonical knowledge automatically.

## 12. Failure modes

The system violates this contract if:

- one ambiguous status carries kind, origin, review and confidence;
- Source is attached only to Entity while strong Claim remains untraceable;
- source URL is treated as proof without locator/relevance;
- `same_movement` counts as substantive relation-value;
- Similarity becomes evidence;
- Relation implies influence/causality without support;
- AI output appears as Source or reviewed fact;
- uncertainty is hidden;
- user conclusion is silently promoted into canonical data;
- mutable shared state is described as immutable/reproducible revision.

## 13. Current implementation boundary

Current checked-in artifacts implement only part of this contract:

- Sources and RelationSources exist;
- Relation `claim_note` provides limited context;
- ResearchSlice v2 has evidence refs and typed findings;
- legacy `epistemic_status` remains mixed;
- first-class Claims, EvidenceLinks with locator/relation/strength and immutable revisions are not implemented;
- current `same_movement` data remains compatibility content.

Therefore schema/code sync of current models is not evidence that Epistemic Contract v2 is fully implemented.

## 14. Change control

Any change to Claim, EvidenceLink, Source, Relation, classification, Similarity, confidence, uncertainty, AI origin or public labels must check:

- `ARTEMIS_CONCEPT.md`;
- `PRODUCT_THESIS.md`;
- `ARTEMIS_PRODUCT_SCOPE.md`;
- `DATA_DICTIONARY.md`;
- `DATA_CONTRACT.md`;
- `ENTITY_MODEL.md`;
- `RESEARCH_SLICE_CONTRACT.md`;
- `CONTENT_GOVERNANCE.md`;
- `AI_POLICY.md`;
- current runtime/spec and migration requirements;
- UI labels and validation rubric;
- executable tests if behavior changes.

## 15. Итоговое правило

ARTEMIS should be confident only where a specific Claim has a reviewable evidence chain.

A narrower honest Claim is better than a broad unsupported conclusion.
