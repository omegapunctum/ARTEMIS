# ARTEMIS — PRODUCT SCOPE

## Статус

- Тип: canonical current product scope.
- Версия: 3.8.
- Дата: 2026-09-01.
- Active vertical: `Life in Context / Leonardo Temporal Map` / issue `#355`.
- Current increment: `M3 — Multi-source proof`; M1 is complete, PR #400 remains non-public, and PR #401 completed M2 with `PROCEED_TO_M3`.
- Gate C: completed / `FREEZE`.
- Gate D: `OPEN / IN PROGRESS`.
- Thematic compatibility surface retained: `Architecture Atlas` at `/atlas/`.
- North Star: `ARTEMIS_CONCEPT.md`.
- Current reality: `PROJECT_TRUTH.md`.
- World-model authority: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`.

Этот документ разрешает только текущий Foundation v3 product-validation scope. Concept target не является утверждением о current implementation.

## 1. Формула текущего продукта

ARTEMIS Life in Context — **source-aware synchronized Globe/timeline experience для исследования жизненного пути личности с постепенным добавлением контекста только после подтверждения ценности базового пространственно-временного loop**.

Текущая проверяемая ценность существенно уже long-term thesis:

`object → time → path → place → information`

Для Leonardo текущий loop должен позволять:

- выбрать календарное время;
- увидеть подтверждённые Presence в соответствующем temporal state;
- проследить coarse trajectory без выдуманного маршрута;
- выбрать Presence;
- понять место, source-native time, principal activity и границы известного;
- открыть source/locator/uncertainty по необходимости.

Local/global context, тематические layers, richer Events/States/Processes и broader simultaneity остаются следующими hypotheses, а не обязательными элементами текущей проверки.

## 2. Scope lock текущего цикла

Foundation и Core Reset уже завершены как prerequisites. Текущий Gate D cycle не должен повторно открывать их.

Completed prerequisites:

- Foundation v3 / v3.1 identity and World Model boundaries;
- reviewed World Model, uncertainty and renderer contracts;
- Gate C `FREEZE` for the Leonardo-in-Romagna 1502 package;
- Core Reset / PR `#393`;
- calendar-based Temporal Map loop / PR `#395`;
- first manual feedback result `ITERATE`;
- feedback correction / PR `#396`.

Current authorized work:

- preserve the published #396 interaction;
- preserve the recorded post-#396 `ITERATE` and its evidence limitations;
- preserve the reviewed PR #400 package without promoting it to runtime;
- preserve the merged PR #401 one-source proof unchanged as M2 evidence;
- add exactly one independent second provider for the same bounded Leonardo birth Presence;
- preserve each source's Claim/EvidenceLink/Source identity and expose agreement, refinement or conflict explicitly;
- do not add a third provider, another Presence, public runtime data, infrastructure or context layers before the M3 exit decision.

## 3. Обязательный current content scope

Текущий validation scaffold содержит:

- одна primary Person: Leonardo da Vinci;
- canonical Trajectory as semantic authority;
- четыре source-bound Presence anchors in Romagna, 1502:
  - Rimini — 1502-08-08;
  - Cesena — 1502-08-10;
  - Cesenatico — 1502-09-06;
  - Imola — source-native autumn 1502 range;
- Claim/EvidenceLink/locator closure для material assertions;
- explicit temporal/spatial/corpus uncertainty;
- unknown route gaps with `route_geometry=null`;
- present-day settlement anchors explicitly separated from exact historical position claims.

Это **interaction scaffold**, а не Leonardo's complete biography и не полный `Life in Context` corpus.

Не являются обязательными для текущего M3 proof:

- changing historical Region geometry;
- complete local political/cultural State context;
- long Processes;
- selected contemporaries;
- documented Relation predicates;
- global simultaneous Events;
- broad thematic layer set;
- runtime publication of the PR #400 candidate package;
- expansion beyond the one selected two-provider Presence.

The reviewed PR #400 candidate package remains separate non-public evidence; M3 does not promote it or expand its Presence set.

### 3.1 Progressive fidelity / достаточная точность

ARTEMIS развивается **от общего к частному**. Текущий gate требует не максимальной возможной детализации, а минимальной достаточной fidelity, которая честно поддерживает пользовательский сценарий.

Правила:

- source-native precision и raw/source values сохраняются, если они доступны и полезны для provenance;
- исследовательская и curation работа не обязана добиваться более тонкой temporal/spatial granularity, если это не меняет material product or validation semantics;
- более высокая точность приоритетна только когда она меняет identity, ordering, overlap/co-presence, geometry, relation interpretation, пользовательское понимание или gate decision;
- hour-level reconstruction движения исторического объекта не является требованием текущего Globe MVP, если day/month/year/range/unknown precision уже достаточна для сценария;
- UI/runtime может показывать более крупный масштаб времени/пространства, чем хранится в source-native metadata, но не может показывать более точное значение, чем подтверждено данными;
- последующая revision может уточнять время, место или geometry без смены object identity и без переписывания истории evidence;
- coarse current scope никогда не разрешает invented exactness: неизвестное остаётся неизвестным, а отсутствие точного route не заполняется правдоподобной линией.

Это правило экономит curation/research budget, но **не ослабляет accuracy, provenance, uncertainty или evidence requirements**.

The append-only recording/refinement mechanism is scoped by issue `#377` and `PROGRESSIVE_REFINEMENT_CONTRACT.md`; its accepted semantics do not authorize editable runtime/storage behavior in Gate D.

## 4. Обязательный interface scope

Current required interface behavior:

- 3D Globe as the primary MVP spatial surface;
- Architecture Atlas at `/atlas/` as a frozen compatibility surface;
- full-width bottom calendar timeline as the primary time instrument;
- `Range` as a two-handle calendar interval using temporal overlap;
- `Scrub` as a chosen build origin plus one current-time cursor that accumulates the path forward;
- selectable start/end or start/current calendar values at an honest display granularity;
- map, timeline, selection and URL controlling one shared Explorer State;
- interactive Presence markers with a compact first-click popup;
- no map-camera movement on single click;
- optional right detail drawer for deeper information;
- explicit double-click may focus/zoom the selected place;
- coarse trajectory presentation where a dashed chronological connector is explicitly not historical route geometry;
- concise place/date/activity information first;
- source/locator/uncertainty under progressive disclosure;
- URL-restorable state without a backend dependency.

Layer combinations, Region alternatives and renderer diagnostics may remain available as underlying evidence/advanced inspection, but they are not default primary controls for the current user check.

`Trajectory` remains the semantic authority. A presentation-only chronological connector must remain distinguishable from unknown route geometry.

## 5. Knowledge and epistemic scope

The canonical World Model remains broader than the current visible loop:

- `Entity`, `Event`, `State`, `Process`, `Trajectory`, `Region`, `Layer`;
- `Relation` as structured Claim;
- `Claim`, `Source`, `EvidenceLink`;
- independent claim kind/origin/review/confidence/evidence/uncertainty;
- explicit corpus coverage;
- alternative reconstructions where necessary;
- `Similarity` as computed output, not evidence;
- `same_movement` as legacy classification projection.

The current UI does not need to expose every canonical object type to prove the first Temporal Map interaction. Compatibility adapters may be used only if they do not erase target semantics.

## 6. Architecture Atlas disposition

Architecture Atlas:

- remains a public compatibility surface at `/atlas/`;
- remains an architecture thematic layer;
- retains current Sources/Media/Relations and Gate A fixtures;
- may later supply contextual material to Life in Context through the shared core;
- does not define the active user, loop or outcome.

No completed corpus or engineering work is deleted in this cycle.

## 7. Current persistence boundary

Target Investigation/SliceRevision/ResearchBrief remains a valid optional research-work capability.

For the current M3 multi-source proof:

- immutable revisions and Research Brief are not prerequisites;
- current mutable ResearchSlice v2 remains compatibility backend code;
- issues #323–#325 are not executed;
- PR #314 is not a Foundation prerequisite;
- no new public backend is required unless evidence shows the static read-only loop is insufficient.

## 8. Frozen scope

Outside the currently opened `M3 — Multi-source proof` branch:

- public runtime integration of the PR #400 candidate package;
- any third-provider integration, second Presence or broad reconciliation framework before the M3 exit decision;
- default local/global context layers;
- generative AI and AI analysis runtime;
- causal/predictive engine;
- counterfactual simulation;
- public production Globe before promotion evidence;
- photorealistic or universal historical terrain reconstruction;
- VR/AR;
- open-ended UGC;
- institutional collaboration;
- Stories/Courses product depth;
- universal multi-domain corpus;
- native apps;
- enterprise APIs/integrations;
- framework rewrite;
- scaling unrelated to current blockers.

Security and compatibility maintenance remain allowed.

## 9. Public capability rule

Capability labels:

- `PUBLIC NOW`;
- `BACKEND-AVAILABLE`;
- `PILOT`;
- `R&D`;
- `CONCEPT TARGET`;
- `FUTURE`.

The public root is the ARTEMIS Core landing. It routes `/globe/` as the primary Leonardo research prototype and `/atlas/` as compatibility-only.

The #355 decision, public deployment and #396 implementation do not make:

- Leonardo historical content product-validated;
- broader local/global context implemented as the current default experience;
- AI available;
- the Globe product-validated;
- VR available;
- world-scale coverage real.

## 10. Current exit condition

The corrected #396 loop completed M1 with `ITERATE`. PR #400 completed the reviewed candidate package without runtime authorization. PR #401 completed M2, and the recorded result is `PROCEED_TO_M3`. The current increment is complete only when the bounded two-provider proof records exactly one outcome:

- `PROCEED_TO_M4`;
- `NARROW_M3`;
- `STOP_M3`.

M3 must demonstrate two independent provider identities for the same bounded Presence, explicit agreement/refinement/conflict semantics and visible uncertainty without public runtime promotion. M4 remains a later architecture decision.

This package outcome does not automatically mean Gate D is globally complete or authorize another product branch.

Formal same-content baseline, broader contextual-understanding metrics and participant protocol remain available for a later validation step when the tested scope actually contains the corresponding context/layer hypotheses.

## 11. Next-branch rule

The post-#396 result vocabulary was:

- `ITERATE` — improve the same loop;
- `NARROW` — reduce the loop/content scope;
- `STOP/RETHINK` — stop this approach and revisit the hypothesis.

The recorded M1 result is `ITERATE`; M2 completed through PR #401 with `PROCEED_TO_M3`. The one active branch is M3. M4, context/layers, curation/editorial storage, persistence/sharing and broad renderer/provider improvement remain unopened.

Public deployment, richer historical terrain, guided learning, source-bound AI, broader World Slices, institutional workflow and VR/AR remain separate decisions.

## 12. Owner documents

- North Star: `ARTEMIS_CONCEPT.md`;
- product thesis: `PRODUCT_THESIS.md`;
- current truth: `PROJECT_TRUTH.md`;
- platform architecture: `PLATFORM_ARCHITECTURE_DECISION.md`;
- world model: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- epistemic semantics: `EPISTEMIC_CONTRACT.md`;
- entities and relations: `ENTITY_MODEL.md`;
- current public data: `DATA_DICTIONARY.md` and `DATA_CONTRACT.md`;
- research persistence: `RESEARCH_SLICE_CONTRACT.md`;
- Foundation decision: `work/2026-07-28_FOUNDATION_V3_DECISION.md`;
- formal validation design: `work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md`;
- active Globe decision: `work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md`;
- current Temporal Map interaction: `work/2026-08-28_TEMPORAL_MAP_LIFE_PATH_V1.md`.
