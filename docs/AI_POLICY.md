# ARTEMIS — AI POLICY

## Статус документа

- Тип: foundation AI policy document
- Версия: 3.1
- Дата: 2026-08-09
- Статус: active canonical policy after Foundation v3.1 attractor refinement / issue `#363`
- Роль: фиксирует допустимую и недопустимую роль AI в ARTEMIS
- Назначение: защитить проект от AI drift, source substitution, hallucinated authority, hidden state changes и смешения фактов, интерпретаций, гипотез и AI-output
- Scope: future source-bound analysis and exploration of the spatial-temporal knowledge model, Claim/Evidence discipline, reversible view actions, inference trace, counterfactual isolation and content governance

---

## 1. Главный принцип

AI in ARTEMIS is an assistant and exploration interface, not an authority.

ИИ в ARTEMIS в будущем может:
- объяснять;
- сравнивать;
- структурировать;
- помогать искать паттерны;
- предлагать гипотезы;
- указывать на слабые места данных;
- помогать готовить drafts for stories/courses;
- предлагать exploration plans;
- управлять обратимыми view/query actions в разрешённом model context.

ИИ в ARTEMIS не может:
- быть источником истины;
- заменять source/provenance;
- публиковать canonical content без review;
- превращать гипотезу в факт;
- скрывать неопределённость;
- выдавать causal claims без явной маркировки;
- смешивать counterfactual scenario с historical reality;
- изменять canonical knowledge через скрытое действие интерфейса.

Главные правила:

> AI output is never canonical knowledge by default.

> AI may control the VIEW. AI may propose KNOWLEDGE. AI may not silently rewrite TRUTH.

---

## 2. Зачем нужна AI policy

ARTEMIS строится как source-aware spatial-temporal knowledge model about the world. AI является future analytical/exploration branch над этой моделью, не Source, не второй canonical reality и не AI-authoritative layer.

AI policy нужна, чтобы:

- сохранить доверие к знаниям;
- защитить source/provenance discipline;
- не превратить ARTEMIS в chatbot over map;
- позволить AI взаимодействовать с самой exploration environment, не создавая hidden truth mutations;
- не дать AI подменить Investigation/revision/Brief model;
- не смешивать факт, interpretation, hypothesis и generation;
- обеспечить explainable AI assistance поверх structured context;
- подготовить безопасный фундамент для будущих reasoning layers;
- не превращать spatial/temporal correlation или co-presence в influence/causality;
- сохранять inference trace, model assumptions and reconstruction mode;
- изолировать counterfactual branches from historical assertions;
- отделить reversible interface actions от changes to canonical knowledge.

Эта policy **не открывает AI implementation scope**. Generative AI/runtime остаётся gated до отдельного product/architecture decision.

---

## 3. AI role in ARTEMIS

AI должен работать как:

### 3.1 Explainer

Объясняет selected Claims, EvidenceLinks, entities or revision context.

Rules:
- must use provided context;
- must distinguish known facts from interpretation;
- must expose uncertainty where relevant;
- must not invent missing data.

### 3.2 Comparator

Сравнивает Claims/entities/revisions and relevant lenses.

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

Помогает структурировать Claims/Evidence into a draft while preserving user authorship.

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

### 3.7 Knowledge Exploration Interface

После отдельного AI implementation gate AI может помогать пользователю исследовать ARTEMIS не только текстом, но и через явные изменения view/query state.

Допустимые будущие action classes:

- set/change time or time range;
- focus a Place, Region, Entity, Event or bounded spatial area;
- activate/deactivate thematic layers;
- select objects or establish comparison scope;
- switch approved reconstruction mode;
- change uncertainty visibility/detail level;
- assemble an exploration sequence from explicit reversible steps.

Requirements:

- action must be derived from explicit user intent or a visible AI proposal;
- action must be inspectable and reversible;
- before/after semantic state must be attributable to the action;
- action may change `SynchronizedView` / Explorer State or a future compatible query-state envelope;
- action must not mutate underlying Claims, Sources, EvidenceLinks, Uncertainty or canonical dataset identity;
- action must not silently geocode, infer route/geometry or upgrade temporal precision;
- a sequence of actions remains an exploration plan, not historical evidence.

A view action is not a Claim, Source, EvidenceLink or canonical Entity type merely because AI initiated it.

---

## 4. AI output and action types

AI output must have an explicit function and always has `origin=ai` where epistemic output is persisted or displayed.

Allowed baseline/future types:

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
| `exploration_plan` | последовательность предложенных reversible view/query steps | no |
| `view_action` | конкретное reversible изменение view/query state | no; not knowledge |

Rules:
- every AI epistemic output must be visibly marked as AI-generated;
- review does not erase AI origin from the original output;
- a human may create a new reviewed Claim based on independently verified evidence;
- AI output cannot become factual Claim or Relation without Source/EvidenceLink governance;
- `view_action` changes presentation/query context only and must never be serialized as historical evidence;
- a saved AI-driven view may persist state, but persistence does not promote the AI rationale into canonical knowledge.

---

## 5. Input context requirements

AI should operate from structured ARTEMIS context.

Preferred input contexts:
- immutable Slice Revision or explicitly labelled mutable ResearchSlice context;
- selected Claims and EvidenceLinks;
- selected entity/detail context;
- current SynchronizedView / Explorer State where available;
- Story step;
- Course module;
- Explainability Context Contract;
- curated source/data context;
- explicit user question scoped to current context.

Minimum context for strong AI output:
- entities considered;
- time range;
- spatial/layer context where relevant;
- current reconstruction mode where relevant;
- known Sources, EvidenceLinks and locators;
- claim kind, origin, review, confidence, evidence state and uncertainty;
- user note/question.

Minimum context for AI view action:
- current view/query state;
- target state or intended delta;
- dataset/World Slice identity;
- supported action capabilities;
- visible assumptions/limits where action depends on uncertain context.

Forbidden default:
- detached AI answer presented as ARTEMIS knowledge without reference to context;
- hidden interface action presented as if it reflected a canonical model change.

---

## 6. Source and provenance discipline

AI is not a source.

Rules:
- AI may summarize source-backed data;
- AI may suggest source candidates;
- AI may point out missing provenance;
- AI may not invent source-backed claims;
- AI may not invent locators;
- AI may not cite unverifiable source as confirmed;
- AI-suggested source must be verified before use;
- AI output must not overwrite source/provenance fields;
- AI navigation to a Source does not strengthen the evidentiary relation by itself.

If AI answer and source-backed data conflict:
- source-backed data and governance process take priority;
- AI output should be treated as warning/hypothesis until reviewed.

---

## 7. Epistemic rules for AI

AI must obey `EPISTEMIC_CONTRACT.md`.

Required separations:
- claim kind vs origin;
- review state vs confidence/evidence state;
- factual Claim vs interpretation/hypothesis;
- Source/EvidenceLink vs model-generated text;
- substantive Relation vs classification/Similarity;
- historical reality vs counterfactual scenario;
- canonical knowledge vs reversible view/query state.

AI must not:
- upgrade uncertainty to certainty;
- erase source conflict;
- convert correlation into causality;
- present narrative coherence as proof;
- hide that a claim is model-generated;
- use a view change as evidence that the viewed relationship exists.

AI should prefer:
- modest claims;
- explicit limitations;
- visible uncertainty;
- source-aware reasoning;
- asking for better data when necessary;
- reversible exploration before persistent mutation.

---

## 8. AI and view/query state

A future AI branch may act on the ARTEMIS exploration state only through an explicit action boundary.

Allowed state targets may include:
- temporal selection;
- spatial focus/view intent;
- active layer refs;
- selected/comparison object refs;
- reconstruction mode;
- uncertainty-display intent;
- bounded local/global context selection.

Forbidden state effects:
- changing World Slice/dataset identity without explicit user-visible transition;
- changing canonical Claim/Evidence/Source records;
- fabricating missing geometry to satisfy a focus action;
- silently resolving an unresolved route or Region;
- hiding material uncertainty because it makes a visualization cleaner;
- converting renderer-local camera state into domain truth.

View-state history should be auditable enough that a user can understand what the AI changed and undo it.

The exact runtime command schema is future implementation detail and does not become canonical ontology merely because this policy names the action class.

---

## 9. AI and research-work context

После отдельного AI branch decision immutable Slice Revision может стать primary AI context unit. AI generation не входит в active MVP.

AI over revision may:
- summarize selected Claims;
- explain why selected entities matter;
- compare revisions/Claims;
- identify visible patterns;
- suggest hypotheses;
- propose missing evidence checks;
- flag weak evidence;
- propose a reversible exploration plan over the revision's saved spatial-temporal context.

AI over revision must include or preserve:
- investigation/revision id;
- selected entities;
- selected Claims/EvidenceLinks and locators;
- time range;
- map/layer/filter state where relevant;
- independent epistemic dimensions;
- source/provenance limitations.

AI over revision must not:
- modify canonical public data;
- publish user Claims as facts;
- infer hidden causal structure without marking;
- detach answer from revision/evidence context;
- modify the immutable revision.

---

## 10. AI and Stories

AI may help create or refine stories.

Allowed:
- draft story step text;
- summarize slice sequence;
- suggest narrative order;
- identify missing transition;
- simplify explanation for audience;
- produce review checklist;
- suggest a view sequence that remains source-bound and reversible.

Forbidden:
- publish AI-generated story as curated without review;
- remove material uncertainty for narrative smoothness;
- invent missing links between story steps;
- make story detached from map/time/slice context.

Story AI output remains draft until human/editorial approval.

---

## 11. AI and Courses

AI may support course design.

Allowed:
- draft lesson explanation;
- generate comprehension questions;
- summarize story/course module;
- suggest learning sequence;
- identify gaps in source context;
- adapt explanation level;
- suggest spatial-temporal exploration steps.

Forbidden:
- replace curated educational design entirely;
- present AI-generated lesson content as verified without review;
- simplify away important epistemic uncertainty;
- turn ARTEMIS into generic LMS content without spatial-temporal research basis.

Course AI output remains draft until review.

---

## 12. AI and UGC / moderation

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

## 13. AI and public canonical data

AI must not directly alter canonical public data.

Rules:
- AI may propose candidate edits;
- AI may suggest source candidates;
- AI may create draft content;
- AI may generate validation warnings;
- AI may not write directly to `data/features.geojson` as source of truth;
- AI-generated candidate must pass content governance and ETL/release checks;
- AI-driven view/query state must not be mistaken for a data edit.

Public data changes must follow:
- source/governance review;
- validation;
- publish/export path;
- release checks.

---

## 14. Counterfactual and causal limits

Baseline does not promise causal engine or counterfactual simulation.

AI must not present:
- prediction as known outcome;
- counterfactual as history;
- causality as proven when only correlation exists;
- narrative plausibility as evidence.

Allowed with strict marking after appropriate future gates:
- hypothesis about possible relation;
- explanation of known scholarly interpretations;
- clearly marked counterfactual thought experiment outside canonical public history;
- caveated causal candidate if supported by sources and marked.

Counterfactual navigation/view state must remain visibly isolated from historical/reconstruction modes.

---

## 15. UI requirements for AI output and actions

AI output should be visibly distinct from source-backed data.

Minimum UI requirements for epistemic output:
- label AI-generated content;
- show output type where relevant;
- show uncertainty/limitations when material;
- provide path to source/provenance context where available;
- do not visually flatten AI hypothesis into factual card content;
- keep counterfactual/speculative mode separate.

Minimum UI requirements for AI actions:
- make material state changes visible;
- allow user undo/reversal for reversible actions;
- distinguish AI-changed view state from underlying knowledge change;
- preserve material uncertainty visibility;
- show when requested action cannot be performed without inventing missing semantics.

Failure mode:
- if user cannot tell whether content is source-backed, human-authored, AI-generated or merely an AI-driven view state, AI policy is violated.

---

## 16. AI memory and user context

AI may use user/session context only within explicit product boundaries.

Rules:
- private research slices remain private unless sharing policy says otherwise;
- AI should not expose private slice content to other users;
- AI should not use private user annotations as public source;
- AI summaries derived from private content remain private unless explicitly exported/shared;
- privacy and ownership rules override convenience;
- future personal knowledge context remains private/product-governed and is not canonical public knowledge.

Foundation v3.1 does not add a personal knowledge entity model or authorize its implementation.

---

## 17. Relationship to working AI strategy

`docs/archive/ARTEMIS_AI_STRATEGY_v1_0.md` preserves historical pre-Concept-Lock proposals only.

This file, `docs/AI_POLICY.md`, defines canonical constraints. The archived strategy has no authority, cannot open AI implementation scope and must not be used as active planning.

---

## 18. Relationship to other foundation docs

- `ARTEMIS_CONCEPT.md` defines the long-term attractor, the identity-level knowledge-about-world interpretation and why AI must not replace human judgment or source discipline.
- `ARTEMIS_PRODUCT_SCOPE.md` keeps AI generation outside the active Globe MVP unless a separate decision opens it.
- `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` remains the reviewed v1.0 owner of spatial-temporal/change/coverage/reconstruction semantics; Foundation v3.1 does not rewrite that frozen #329 review dependency.
- `RESEARCH_SLICE_CONTRACT.md` defines Investigation/revision as possible future AI context.
- `EPISTEMIC_CONTRACT.md` defines Claim/EvidenceLink and independent dimensions AI must obey.
- `ENTITY_MODEL.md` defines current/future named entity roles; view actions do not become entity types by implication.
- `CONTENT_GOVERNANCE.md` defines how AI-generated candidates may be reviewed/promoted/rejected.
- `DATA_CONTRACT.md` defines canonical public data artifacts AI must not bypass.

---

## 19. AI failure modes

AI policy is broken if:

- AI answer appears as verified fact;
- AI output becomes source;
- AI-generated relation becomes canonical without review;
- AI hides uncertainty;
- AI makes causal claims without marking;
- AI-generated content enters public data directly;
- AI story/course draft is published without review;
- AI works from detached prompt while UI implies it used current revision/evidence;
- AI treats private user context as public knowledge;
- AI suggests fake/unverified sources as confirmed;
- AI changes view/query state invisibly;
- AI view action fabricates geometry/time/relation semantics;
- AI-controlled navigation is presented as a change to canonical World Model truth.

---

## 20. Change-control rule

Any change to AI behavior must check impact on:

- `ARTEMIS_CONCEPT.md`;
- `ARTEMIS_PRODUCT_SCOPE.md`;
- `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- `RESEARCH_SLICE_CONTRACT.md`;
- `EPISTEMIC_CONTRACT.md`;
- `ENTITY_MODEL.md`;
- `CONTENT_GOVERNANCE.md`;
- `DATA_CONTRACT.md`;
- `docs/archive/ARTEMIS_AI_STRATEGY_v1_0.md` only when historical context is necessary;
- UI labels, action disclosure and output rendering;
- moderation/content governance;
- tests/release checks if executable behavior changes.

Checking impact on a frozen reviewed contract does not authorize editing it. If AI behavior requires a semantic-contract byte change, that contract's own review/change-control gate must be reopened.

No AI feature should be implemented only as a prompt or UI addition if it changes source/trust/product semantics or state-control authority.

A future runtime command schema must be separately reviewed before implementation; this policy does not define an executable API.

---

## 21. Итоговое правило

If an AI branch is ever opened, ARTEMIS should use AI to make structured knowledge easier to explore and evidence easier to understand, not to replace human research or canonical governance.

AI strengthens ARTEMIS only when it remains:

- context-bound;
- source-aware;
- epistemically marked;
- view-state transparent;
- reversible where it changes exploration state;
- human-reviewable;
- limited by product scope;
- unable to bypass content governance;
- unable to silently rewrite canonical knowledge.