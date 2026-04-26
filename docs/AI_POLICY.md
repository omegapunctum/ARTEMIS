# ARTEMIS — AI POLICY

## Статус документа

- Тип: foundation AI policy document
- Статус: active, pending canonical registration in `PROJECT_STRUCTURE.md` and `DOCUMENTATION_SYSTEM.md`
- Роль: фиксирует допустимую и недопустимую роль AI в ARTEMIS
- Назначение: защитить проект от AI drift, source substitution, hallucinated authority и смешения фактов, интерпретаций, гипотез и AI-output
- Scope: AI behavior, AI outputs, AI limits, source/provenance discipline, slice/story/course AI use, moderation/content governance integration

---

## 1. Главный принцип

AI in ARTEMIS is an assistant, not an authority.

ИИ в ARTEMIS может:
- объяснять;
- сравнивать;
- структурировать;
- помогать искать паттерны;
- предлагать гипотезы;
- указывать на слабые места данных;
- помогать готовить drafts for stories/courses.

ИИ в ARTEMIS не может:
- быть источником истины;
- заменять source/provenance;
- публиковать canonical content без review;
- превращать гипотезу в факт;
- скрывать неопределённость;
- выдавать causal claims без явной маркировки;
- смешивать counterfactual scenario с historical reality.

Главное правило:

> AI output is never canonical knowledge by default.

---

## 2. Зачем нужна AI policy

ARTEMIS строится как AI-native explainable spatial-temporal research platform, но AI-native не означает AI-authoritative.

AI policy нужна, чтобы:

- сохранить доверие к знаниям;
- защитить source/provenance discipline;
- не превратить ARTEMIS в chatbot over map;
- не дать AI подменить research slice model;
- не смешивать факт, интерпретацию, гипотезу и генерацию;
- обеспечить explainable AI assistance поверх structured context;
- подготовить безопасный фундамент для будущих reasoning layers.

---

## 3. AI role in ARTEMIS

AI должен работать как:

### 3.1 Explainer

Объясняет выбранный объект, slice, story step или course context.

Rules:
- must use provided context;
- must distinguish known facts from interpretation;
- must expose uncertainty where relevant;
- must not invent missing data.

### 3.2 Comparator

Сравнивает entities, slices, time ranges or layer configurations.

Rules:
- comparison must name compared contexts;
- must not infer causality from similarity;
- must mark weak/limited basis.

### 3.3 Pattern assistant

Помогает увидеть возможные spatial-temporal patterns.

Rules:
- pattern is not proof;
- pattern may become hypothesis;
- must show what data points support the pattern.

### 3.4 Hypothesis generator

Формулирует возможные объяснения и исследовательские гипотезы.

Rules:
- hypothesis must be explicitly marked;
- hypothesis must not be displayed as fact;
- hypothesis should include what evidence would strengthen or weaken it.

### 3.5 Structuring assistant

Помогает превращать slice context into story/course draft.

Rules:
- draft remains draft;
- educational simplification must preserve epistemic honesty;
- AI-generated narrative requires human/editorial review before public curated use.

### 3.6 Weakness detector

Указывает:
- missing source;
- low confidence coordinates;
- date uncertainty;
- unsupported relation;
- possible conflict;
- overstrong interpretation.

Rules:
- AI may flag risk;
- AI flag does not equal final governance decision.

---

## 4. AI output types

AI output must have an explicit type.

Allowed baseline types:

| Type | Meaning | Canonical by default |
|---|---|---:|
| `summary` | краткое изложение provided context | no |
| `explanation` | объяснение объектов/среза/связей | no |
| `comparison` | сопоставление contexts/entities/slices | no |
| `hypothesis` | предположение | no |
| `pattern_candidate` | возможный pattern | no |
| `draft` | черновик story/course/content | no |
| `warning` | указание на слабость данных/логики | no |
| `source_candidate` | потенциальный источник для проверки | no |

Rules:
- every AI output must be visibly marked as AI-generated;
- AI output may be reviewed, edited and promoted to human-authored interpretation/draft;
- AI output cannot become fact without source-backed governance review.

---

## 5. Input context requirements

AI should operate from structured ARTEMIS context.

Preferred input contexts:
- Research Slice;
- selected entity/detail context;
- Story step;
- Course module;
- Explainability Context Contract;
- curated source/data context;
- explicit user question scoped to current context.

Minimum context for strong AI output:
- entities considered;
- time range;
- spatial/layer context where relevant;
- known sources/provenance where available;
- epistemic status of claims;
- user note/question.

Forbidden default:
- detached AI answer presented as ARTEMIS knowledge without reference to context.

---

## 6. Source and provenance discipline

AI is not a source.

Rules:
- AI may summarize source-backed data;
- AI may suggest source candidates;
- AI may point out missing provenance;
- AI may not invent source-backed claims;
- AI may not cite unverifiable source as confirmed;
- AI-suggested source must be verified before use;
- AI output must not overwrite source/provenance fields.

If AI answer and source-backed data conflict:
- source-backed data and governance process take priority;
- AI output should be treated as warning/hypothesis until reviewed.

---

## 7. Epistemic rules for AI

AI must obey `EPISTEMIC_CONTRACT.md`.

Required separations:
- fact vs interpretation;
- interpretation vs hypothesis;
- hypothesis vs AI-generated speculation;
- source-backed claim vs model-generated text;
- historical reality vs counterfactual scenario.

AI must not:
- upgrade uncertainty to certainty;
- erase source conflict;
- convert correlation into causality;
- present narrative coherence as proof;
- hide that a claim is model-generated.

AI should prefer:
- modest claims;
- explicit limitations;
- visible uncertainty;
- source-aware reasoning;
- asking for better data when necessary.

---

## 8. AI and Research Slice

Research Slice is the primary AI context unit in ARTEMIS v1.0.

AI over slice may:
- summarize slice;
- explain why selected entities matter;
- compare current slice with another slice;
- identify visible patterns;
- suggest hypotheses;
- prepare story/course draft from slice;
- flag weak evidence.

AI over slice must include or preserve:
- slice id/context;
- selected entities;
- time range;
- map/layer/filter state where relevant;
- annotation epistemic types;
- source/provenance limitations.

AI over slice must not:
- modify canonical public data;
- publish slice annotations as facts;
- infer hidden causal structure without marking;
- detach answer from slice context.

---

## 9. AI and Stories

AI may help create or refine stories.

Allowed:
- draft story step text;
- summarize slice sequence;
- suggest narrative order;
- identify missing transition;
- simplify explanation for audience;
- produce review checklist.

Forbidden:
- publish AI-generated story as curated without review;
- remove material uncertainty for narrative smoothness;
- invent missing links between story steps;
- make story detached from map/time/slice context.

Story AI output remains draft until human/editorial approval.

---

## 10. AI and Courses

AI may support course design.

Allowed:
- draft lesson explanation;
- generate comprehension questions;
- summarize story/course module;
- suggest learning sequence;
- identify gaps in source context;
- adapt explanation level.

Forbidden:
- replace curated educational design entirely;
- present AI-generated lesson content as verified without review;
- simplify away important epistemic uncertainty;
- turn ARTEMIS into generic LMS content without spatial-temporal research basis.

Course AI output remains draft until review.

---

## 11. AI and UGC / moderation

AI may assist moderation but must not be final moderator by default.

Allowed:
- flag missing source;
- detect likely duplicate;
- suggest rejection reason;
- identify weak coordinates/date;
- classify possible epistemic type;
- propose review checklist.

Forbidden:
- automatically approve public content;
- automatically reject without review where human judgment is required;
- treat user text as fact without source;
- create canonical publish record directly.

Moderation decision remains governance process, not raw AI output.

---

## 12. AI and public canonical data

AI must not directly alter canonical public data.

Rules:
- AI may propose candidate edits;
- AI may suggest source candidates;
- AI may create draft content;
- AI may generate validation warnings;
- AI may not write directly to `data/features.geojson` as source of truth;
- AI-generated candidate must pass content governance and ETL/release checks.

Public data changes must follow:
- source/governance review;
- validation;
- publish/export path;
- release checks.

---

## 13. Counterfactual and causal limits

Baseline v1.0 does not promise causal engine or counterfactual simulation.

AI must not present:
- prediction as known outcome;
- counterfactual as history;
- causality as proven when only correlation exists;
- narrative plausibility as evidence.

Allowed with strict marking:
- hypothesis about possible relation;
- explanation of known scholarly interpretations;
- clearly marked counterfactual thought experiment outside canonical public history;
- caveated causal candidate if supported by sources and marked.

---

## 14. UI requirements for AI output

AI output should be visibly distinct from source-backed data.

Minimum UI requirements:
- label AI-generated content;
- show output type where relevant;
- show uncertainty/limitations when material;
- provide path to source/provenance context where available;
- do not visually flatten AI hypothesis into factual card content;
- keep counterfactual/speculative mode separate.

Failure mode:
- if user cannot tell whether content is source-backed, human-authored or AI-generated, AI policy is violated.

---

## 15. AI memory and user context

AI may use user/session context only within explicit product boundaries.

Rules:
- private research slices remain private unless sharing policy says otherwise;
- AI should not expose private slice content to other users;
- AI should not use private user annotations as public source;
- AI summaries derived from private content remain private unless explicitly exported/shared;
- privacy and ownership rules override convenience.

---

## 16. Relationship to working AI strategy

`docs/work/ARTEMIS_AI_STRATEGY_v1_0.md` may define:
- implementation ideas;
- AI roadmap;
- prompt patterns;
- UX experiments;
- model behavior proposals;
- next product layers.

This file, `docs/AI_POLICY.md`, defines canonical constraints.

If working AI strategy conflicts with this policy:
- `AI_POLICY.md` wins;
- the working strategy must be corrected;
- no implementation task should proceed until conflict is resolved.

---

## 17. Relationship to other foundation docs

- `ARTEMIS_CONCEPT.md` defines why AI must not replace human judgment or source discipline.
- `ARTEMIS_PRODUCT_SCOPE.md` defines AI assistance as part of v1.0 scope, with full generation/explanation layer still future relative to ECC baseline where applicable.
- `RESEARCH_SLICE_CONTRACT.md` defines slice as primary AI context unit.
- `EPISTEMIC_CONTRACT.md` defines epistemic marking rules AI must obey.
- `ENTITY_MODEL.md` defines AIInsight and ExplainabilityContext.
- `CONTENT_GOVERNANCE.md` defines how AI-generated candidates may be reviewed/promoted/rejected.
- `DATA_CONTRACT.md` defines canonical public data artifacts AI must not bypass.

---

## 18. AI failure modes

AI policy is broken if:

- AI answer appears as verified fact;
- AI output becomes source;
- AI-generated relation becomes canonical without review;
- AI hides uncertainty;
- AI makes causal claims without marking;
- AI-generated content enters public data directly;
- AI story/course draft is published without review;
- AI works from detached prompt while UI implies it used current slice;
- AI treats private user context as public knowledge;
- AI suggests fake/unverified sources as confirmed.

---

## 19. Change-control rule

Any change to AI behavior must check impact on:

- `ARTEMIS_CONCEPT.md`;
- `ARTEMIS_PRODUCT_SCOPE.md`;
- `RESEARCH_SLICE_CONTRACT.md`;
- `EPISTEMIC_CONTRACT.md`;
- `ENTITY_MODEL.md`;
- `CONTENT_GOVERNANCE.md`;
- `DATA_CONTRACT.md`;
- `docs/work/ARTEMIS_AI_STRATEGY_v1_0.md`;
- UI labels and output rendering;
- moderation/content governance;
- tests/release checks if executable behavior changes.

No AI feature should be implemented only as a prompt or UI addition if it changes source/trust/product semantics.

---

## 20. Итоговое правило

ARTEMIS should use AI to make structured knowledge more understandable, not to replace structured knowledge.

AI strengthens ARTEMIS only when it remains:

- context-bound;
- source-aware;
- epistemically marked;
- human-reviewable;
- limited by product scope;
- unable to bypass content governance.
