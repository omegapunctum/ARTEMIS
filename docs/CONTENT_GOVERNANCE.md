# ARTEMIS — CONTENT GOVERNANCE

## Статус документа

- Тип: foundation content governance document
- Статус: active, canonical registration confirmed in `PROJECT_STRUCTURE.md` and `DOCUMENTATION_SYSTEM.md`
- Роль: фиксирует правила доверия к данным, источникам, UGC, модерации и публикации content в ARTEMIS
- Назначение: определить, как candidate content становится trusted/canonical content и какие данные не могут попасть в public knowledge layer без проверки
- Scope: source policy, content lifecycle, validation, moderation, UGC promotion, uncertainty, corrections, public publish boundaries
- Progressive refinement owner: `PROGRESSIVE_REFINEMENT_CONTRACT.md` defines append-only revision
  semantics; this document owns the intake, review and promotion workflow around those revisions.

---

## 1. Главный принцип

ARTEMIS не должен публиковать знание только потому, что оно технически валидно.

Техническая валидность означает:
- данные имеют правильный формат;
- обязательные поля заполнены;
- coordinates/date/layer проходят базовую проверку;
- record может пройти ETL/runtime validation.

Content governance означает:
- источник понятен;
- статус утверждения ясен;
- неопределённость промаркирована;
- спорные данные не скрыты;
- UGC не становится canonical content автоматически;
- AI-generated content не становится source-backed fact без review.

Главное правило:

> Public ARTEMIS content must be technically valid, source-aware, epistemically marked and governance-approved.

---

## 2. Зачем нужен content governance

Без content governance ARTEMIS рискует стать:

- картой с красивыми, но методологически слабыми объектами;
- системой, где user drafts выглядят как curated facts;
- AI-assisted продуктом, где AI-output постепенно смешивается с source-backed knowledge;
- образовательной платформой с неявными ошибками в датах, координатах и интерпретациях;
- knowledge base без доверия.

Content governance нужен, чтобы:

- защитить публичную базу знаний;
- обеспечить прозрачность источников;
- отделить curated data от draft/runtime/user content;
- поддерживать epistemic contract;
- дать модерации понятные решения;
- сохранить возможность исправлений и уточнений без потери traceability.

---

## 3. Content layers

ARTEMIS различает несколько слоёв content.

### 3.1 Candidate content

Candidate content — материал, который может стать частью ARTEMIS, но ещё не принят.

Источники:
- Airtable/editorial row;
- user draft;
- imported dataset;
- curator note;
- AI-suggested candidate;
- research/source discovery output.

Правила:
- candidate content не является public canonical content;
- candidate content может быть полезным, но требует validation/review;
- AI-suggested candidate требует человеческой и источниковой проверки.

### 3.2 Runtime/private content

Runtime/private content — пользовательские или временные данные внутри приложения.

Примеры:
- private research slice;
- user annotation;
- draft;
- uploaded media;
- owner-only story/course draft.

Правила:
- runtime/private content не становится public knowledge автоматически;
- owner visibility не равна content trust;
- private slice annotation не является curated fact.

### 3.3 Curated content

Curated content — материал, принятый editorial/governance process.

Правила:
- curated content должен иметь достаточное source/provenance basis;
- curated content может содержать uncertainty, если она явно маркирована;
- curated content должен быть совместим с `EPISTEMIC_CONTRACT.md`.

### 3.4 Canonical public content

Canonical public content — опубликованный слой, используемый public map/runtime.

Текущий public map baseline:
- `data/features.geojson`.

Правила:
- canonical public content проходит ETL/export validation;
- canonical public content не должен напрямую подменяться runtime API;
- public publish flow должен быть управляемым, а не случайным результатом UI action.

### 3.5 Archive/historical content

Archive content — historical/deprecated content, не являющийся текущей публичной истиной.

Правила:
- archive content may preserve traceability;
- archive content must not be treated as current canonical content;
- archived claims may be superseded by later governance decisions.

---

## 4. Content lifecycle

### 4.1 Discovery

Материал обнаруживается через:
- curator research;
- source search;
- user contribution;
- dataset import;
- AI-assisted source discovery;
- editorial planning.

Результат:
- candidate content, not public content.

### 4.2 Intake

Candidate content заносится в рабочий контур.

На intake фиксируется:
- source or source candidate;
- proposed atomic Claim;
- proposed entity type;
- proposed date/spatial attribution;
- contributor/curator if known;
- claim kind/origin/review/confidence/evidence/uncertainty where known;
- required review notes.

Intake also records the active decision target and the minimum material temporal/spatial fidelity
needed for that decision. Coarse, approximate, range-based or unknown values are valid candidate
inputs when they preserve the source-native expression and make the uncertainty explicit. Intake
must not create a day, point, path or boundary merely because the storage/UI supports one.

### 4.2.1 Progressive intake and promotion path

The controlled path is:

`source/research artifact → candidate intake → atomic Claim/revision → epistemic review → accepted ledger revision → deterministic current frontier → separately authorized export/publication`

System responsibilities do not collapse along that path:

- Google Drive may retain research originals, GIS/media and validation material;
- Airtable may hold curated corpus records only when the corresponding lifecycle explicitly
  authorizes the schema/write contour;
- GitHub owns versioned contracts, fixtures, review evidence, decisions and development truth;
- runtime/public artifacts consume only an authorized versioned package or controlled export;
- ChatGPT/AI may discover sources or propose candidate revisions, but is neither Source nor a
  silent canonical writer.

For the current #377 contour, the executable fixture and review evidence live in GitHub. The nine
Airtable World Model shadow tables remain empty and no historical write is authorized.

When the target already has an accepted revision series, intake must classify the proposal as
`refine`, `correct`, `add_alternative` or `withdraw`; a generic field update is not an allowed
semantic operation. Object identity and unrelated dimensions remain unchanged unless separately
claimed and reviewed.

### 4.3 Technical validation

Проверяется:
- required fields;
- format;
- coordinates;
- dates;
- layer/category;
- allowed enums;
- public artifact compatibility.

For a refinement candidate, technical validation additionally checks immutable lineage, stable
target identity, valid-time/record-time separation, source-native precision and the prohibition on
normalized precision finer than its evidence.

Результат:
- pass technical validation;
- reject technically;
- request correction.

Technical validation does not equal content approval.

### 4.4 Epistemic review

Проверяется:
- source quality;
- Claim atomicity and scope;
- evidence relevance to the specific Claim;
- reproducible locator;
- `supports/challenges/contextualizes`;
- direct/indirect/background evidence strength;
- date confidence;
- coordinate confidence;
- relation support;
- uncertainty markers;
- claim kind/origin/review/confidence separation;
- AI-output contamination risk.

Результат:
- accept reviewed factual Claim;
- accept with confidence/uncertainty;
- accept as interpretation;
- keep as hypothesis/missing evidence;
- mark mixed/contested;
- reject;
- request narrower Claim, better Source or locator.

### 4.5 Editorial approval

Curator/editor approves content for publish path.

Approval means:
- content is acceptable within current governance baseline;
- known uncertainty is marked;
- source/provenance is adequate or limitation is explicit.

Approval does not mean:
- absolute historical certainty;
- absence of future corrections;
- AI-derived authority.

### 4.6 Publish

Approved content enters ETL/export/public artifact path.

Rules:
- public map content is published through controlled data pipeline;
- moderation/runtime UI must not directly overwrite canonical public dataset;
- publish result must be auditable through artifacts and release checks.

### 4.7 Correction

Published content may be corrected.

Corrections are appended as a `correct` revision under
`PROGRESSIVE_REFINEMENT_CONTRACT.md`; an accepted assertion is never edited in place. Corrections
must preserve:
- what changed;
- why it changed;
- source or governance basis;
- impact on confidence/uncertainty;
- whether public artifact must be regenerated.

### 4.8 Deprecation / archival

Content may be deprecated if:
- source is invalidated;
- duplicate/identity merge occurs;
- object was wrongly classified;
- interpretation is superseded;
- content no longer fits scope.

Accepted content is withdrawn or superseded through an append-only revision. It must not silently
disappear from the ledger even when it is absent from the current frontier or public projection.

---

## 5. Source policy

### 5.1 Source types

ARTEMIS may use:
- primary/official sources;
- academic sources;
- institutional sources;
- reputable reference sources;
- curated expert estimates;
- user-provided sources pending review;
- AI-suggested source candidates pending verification.

### 5.2 Source hierarchy

Default trust order:

1. primary/official source;
2. peer-reviewed academic source;
3. curated institutional source;
4. reputable reference source;
5. expert estimate with explanation;
6. user-provided source pending review;
7. AI-suggested source candidate pending verification.

### 5.3 Source rules

- AI is not a source.
- Source URL alone is not enough if the claim is not supported by that source.
- Every validation-module EvidenceLink requires a locator.
- Source review does not approve every Claim that cites that Source.
- Challenging evidence must not be omitted because supporting evidence exists.
- Indirect cross-source synthesis must be labelled and reviewable.
- A weak source may be used only if uncertainty is explicit.
- Conflicting sources must not be flattened into false certainty.
- Media source/license is separate from factual source.

---

## 6. Date governance

Dates may be:
- exact;
- approximate;
- range-based;
- disputed;
- reconstructed;
- unknown;
- BCE/negative-year.

Rules:
- uncertain dates must be marked;
- BCE dates must not be normalized into misleading modern values;
- date range should be used when point date is misleading;
- conflicting dates require source/conflict note;
- AI must not invent missing dates as facts.

---

## 7. Coordinate governance

Coordinates may be:
- exact;
- approximate;
- estimated;
- reconstructed;
- disputed;
- representative/centroid;
- unknown.

Rules:
- coordinate confidence must be explicit where relevant;
- representative coordinate must not imply exact site;
- uncertain coordinate can be published if marked honestly;
- invalid coordinates must be rejected from public map artifact;
- approximate coordinates should not support precise spatial claims.

---

## 8. Relation governance

Relations are structured Claims and require stricter governance than standalone fields.

Rules:
- relation must have precise predicate;
- relation must have Claim-level EvidenceLinks and locator;
- relation must expose independent claim kind, origin, review, confidence, evidence state and uncertainty;
- relation must not imply causality unless supported;
- AI-suggested relation remains hypothesis until reviewed;
- weak relation must be marked as weak/uncertain/hypothesis;
- relation used in any downstream Brief/Story/Course must preserve epistemic dimensions;
- shared classification is modelled through ClassificationAssertions;
- `same_movement` compatibility record is not substantive Relation;
- computed Similarity is not evidence.

Examples:
- `associated-with` is rejected when it substitutes for an unknown predicate;
- `influenced-by` requires stronger support than spatial/temporal proximity;
- same Movement requires classification evidence but does not prove influence;
- `caused-by` should be avoided unless there is explicit evidentiary basis and policy approval.

---

## 9. UGC governance

UGC is useful but dangerous if promoted without discipline.

### 9.1 UGC states

- draft;
- submitted;
- pending review;
- review stage 1;
- review stage 2 if needed;
- approved candidate;
- publish-attempt;
- published;
- rejected;
- returned for correction;
- archived.

### 9.2 UGC rules

- UGC does not become canonical content automatically.
- User authority does not replace source/provenance.
- UGC may be accepted as note, hypothesis or draft without becoming public fact.
- UGC with media requires media/source/license checks.
- UGC promotion must preserve contributor traceability where appropriate.
- Rejection reason should be preserved where relevant.

### 9.3 UGC promotion

UGC may become canonical public content only if:

1. it passes technical validation;
2. it has sufficient source/provenance;
3. claim kind/origin/review/confidence/evidence/uncertainty are explicit where applicable;
4. moderation/editorial approval is complete;
5. it enters controlled publish/export path;
6. public artifact is regenerated and checked.

---

## 10. AI-generated content governance

AI-generated content is not trusted by default.

AI may produce:
- summary;
- explanation;
- comparison;
- hypothesis;
- draft story/course text;
- source search suggestions;
- uncertainty warnings;
- relation candidates.

Rules:
- AI output must be marked;
- AI output is not source;
- AI output cannot create public canonical fact without human/source review;
- AI-suggested source must be verified;
- AI relation/hypothesis must remain hypothesis until reviewed;
- AI-generated story/course drafts require editorial review before public/curated use.

---

## 11. Moderation decision types

Moderation should support these decisions:

| Decision | Meaning |
|---|---|
| accept_as_fact | accepted as source-backed factual content |
| accept_as_uncertain | accepted but with uncertainty/confidence marker |
| accept_as_interpretation | accepted as interpretation, not fact |
| keep_as_hypothesis | useful but not confirmed |
| request_source | source/provenance insufficient |
| request_correction | technically or editorially incomplete |
| reject | not accepted |
| archive | preserved for traceability but not active |

Current runtime may not implement all states yet. This table defines governance target semantics.

---

## 12. Rejection reasons

Common rejection reasons:

- missing required fields;
- invalid coordinates;
- invalid date;
- invalid layer/category;
- weak or missing source;
- unsupported relation;
- AI-generated unsupported claim;
- duplicate unresolved entity;
- media/license problem;
- outside product scope;
- violates epistemic contract;
- insufficient moderation context.

Rejection reason should be actionable where possible.

---

## 13. Public publish boundaries

Public publish must remain controlled.

Rules:
- runtime draft approval is not the same as public data publish unless explicitly connected by controlled publish flow;
- direct runtime publish outside moderation/governance path is forbidden;
- public map source remains `data/features.geojson` for current baseline;
- public content changes must be compatible with `DATA_CONTRACT.md`;
- release gate must guard required artifacts and public map discipline.

---

## 14. Content correction policy

Corrections are normal.

A correction should identify:
- affected entity/field/relation;
- previous value;
- new value;
- source/governance basis;
- confidence change;
- need for artifact regeneration;
- whether downstream slices/stories/courses may be affected.

If correction changes meaning materially, related stories/courses/AI summaries may need review.

---

## 15. Scope boundaries

Content must fit ARTEMIS scope.

Acceptable content generally has:
- spatial relevance;
- temporal relevance;
- relation to entity/event/process/place/person/layer;
- source/provenance path;
- research value.

Reject or defer content that is:
- generic encyclopedia text without spatial-temporal role;
- purely social content;
- unsupported AI narrative;
- arbitrary media upload;
- topic outside ARTEMIS core;
- content that turns ARTEMIS into generic LMS/GIS/wiki/social feed.

---

## 16. Relationship to other foundation docs

- `ARTEMIS_CONCEPT.md` defines why ARTEMIS requires verifiable and explainable knowledge.
- `ARTEMIS_PRODUCT_SCOPE.md` defines the active Life in Context/Foundation v3 boundaries and frozen scope. Architecture Atlas remains a thematic-layer baseline.
- `EPISTEMIC_CONTRACT.md` defines Claim/EvidenceLink and independent epistemic dimensions.
- `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md` defines temporal/spatial/change/coverage semantics; `ENTITY_MODEL.md` defines entities, Claims, Relations, Sources and product/runtime/context entities.
- `DATA_CONTRACT.md` defines current ETL/public artifact shape.
- `RESEARCH_SLICE_CONTRACT.md` defines how content is used inside Investigation/revision context.
- `AI_POLICY.md` will define AI-specific behavior boundaries after creation.
- `CONTROLLED_RELEASE_DECISION.md` defines release/readiness interpretation and baseline limitations.

---

## 17. Governance failure modes

Content governance is broken if:

- UGC becomes public fact without review;
- AI output becomes source-backed content without verification;
- weak source is shown as high confidence;
- approximate coordinates are shown as exact;
- disputed dates are flattened into one unmarked value;
- relation implies causality without support;
- shared classification or Similarity is published as substantive Relation;
- a Source is accepted as blanket proof without Claim/locator review;
- challenging evidence is silently dropped;
- media is used publicly without source/license confidence;
- public dataset changes without controlled publish/export path;
- rejected records are not traceable;
- course/story narratives hide material uncertainty.

---

## 18. Change-control rule

Any change to content governance must check impact on:

- `EPISTEMIC_CONTRACT.md`;
- `ENTITY_MODEL.md`;
- `DATA_CONTRACT.md`;
- `RESEARCH_SLICE_CONTRACT.md`;
- `AI_POLICY.md` after creation;
- moderation runtime;
- UGC/drafts runtime;
- ETL/export scripts;
- public data artifacts;
- UI labels/detail panels;
- tests and release checks if executable behavior changes.

A content-related change is incomplete if technical validation, Claim/Evidence semantics and publish governance are not synchronized.

---

## 19. Итоговое правило

ARTEMIS should publish less rather than publish untrusted knowledge as certainty.

A smaller curated dataset with visible provenance and uncertainty is stronger than a larger dataset with hidden epistemic weakness.
