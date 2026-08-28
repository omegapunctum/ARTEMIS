# ARTEMIS — PRODUCT SCOPE

## Статус

- Тип: canonical current product scope.
- Версия: 3.4.
- Дата: 2026-08-28.
- Active vertical: `Life in Context` Globe MVP / issue `#355`.
- Current increment: Core Reset inside Gate D — one public read-only Leonardo Globe loop.
- Thematic compatibility surface retained: `Architecture Atlas` at `/atlas/`.
- North Star: `ARTEMIS_CONCEPT.md`.
- Current reality: `PROJECT_TRUTH.md`.
- World-model authority: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`.

Этот документ разрешает только Foundation v3 validation scope. Concept target не является утверждением о current implementation.

## 1. Формула текущего продукта

ARTEMIS Life in Context — **source-aware synchronized Globe/timeline/layer experience для исследования жизненного пути личности внутри локальных и глобальных процессов её времени**.

Продукт помогает:

- проследить trajectory;
- наблюдать events, states и processes в текущем пространственно-временном окне;
- переключать тематические layers;
- сравнивать локальный и глобальный контекст;
- различать co-presence, encounter, interaction и influence;
- проверять source, locator и uncertainty;
- сохранять view или исследовательский вопрос.

## 2. Scope lock текущего цикла

Текущий цикл состоит из двух последовательных частей:

### Foundation

- принять Concept v3;
- определить universal world-model contract;
- согласовать entity/epistemic/uncertainty semantics;
- зафиксировать migration disposition прежнего backlog;
- не выполнять schema/runtime migration.

### Globe MVP vertical / Core Reset

- подготовить ограниченный Leonardo `World Slice`;
- восстановить cross-renderer parity в #344 / PR #351;
- реализовать synchronized Globe, timeline and layers через общий Explorer State / Render Projection;
- сохранить Architecture Atlas только как compatibility surface, не как same-content Leonardo baseline;
- проверить contextual understanding against same-content baseline;
- записать decision.

## 3. Обязательный content scope

Минимальный World Slice:

- одна primary Person;
- ограниченный набор trajectory segments;
- selected Places and changing Regions;
- Events around selected stops/time windows;
- regional political/cultural States;
- at least one long Process;
- selected contemporaries;
- documented Relations only after #331 is accepted; before then, derived proximity/co-presence only;
- co-presence observations represented separately;
- selected synchronous global Events;
- Claim/EvidenceLink/locator for material content;
- explicit spatial, temporal and corpus uncertainty.

Каждый included element должен служить validation hypothesis. Полнота эпохи не является целью.

### 3.1 Progressive fidelity / достаточная точность

ARTEMIS развивается **от общего к частному**. Текущий gate требует не максимальной возможной детализации, а минимальной достаточной fidelity, которая честно поддерживает validation hypothesis и пользовательский сценарий.

Правила:

- source-native precision и raw/source values сохраняются, если они доступны и полезны для provenance;
- исследовательская и curation работа не обязана добиваться более тонкой temporal/spatial granularity, если это не меняет material product or validation semantics;
- более высокая точность приоритетна только когда она меняет identity, ordering, overlap/co-presence, geometry, relation interpretation, пользовательское понимание или gate decision;
- hour-level reconstruction движения исторического объекта не является требованием текущего Globe MVP, если day/month/year/range/unknown precision уже достаточна для сценария;
- UI/runtime может показывать более крупный масштаб времени/пространства, чем хранится в source-native metadata, но не может показывать более точное значение, чем подтверждено данными;
- последующая revision может уточнять время, место или geometry без смены object identity и без переписывания истории evidence;
- coarse current scope никогда не разрешает invented exactness: неизвестное остаётся неизвестным, а отсутствие точного route не заполняется правдоподобной линией.

Это правило экономит curation/research budget, но **не ослабляет accuracy, provenance, uncertainty или evidence requirements**.

The append-only recording/refinement mechanism is scoped by issue `#377` and
`PROGRESSIVE_REFINEMENT_CONTRACT.md`; its exact lifecycle is owned by the contract/registry. Gate D
must consume the frozen Gate C fidelity, and mutable precision/history behavior requires a separate
implementation authorization even after contract acceptance.

## 4. Обязательный interface scope

- 3D Globe as the primary MVP spatial surface;
- Architecture Atlas at `/atlas/` as a frozen compatibility surface;
- compact synchronized timeline;
- current time/time-range control;
- layer visibility and legend;
- trajectory rendering;
- temporal Region/State rendering at an honest precision;
- Event and Entity details;
- local-context and global-simultaneity views;
- visible distinction between co-presence and stronger Relations;
- source/locator/uncertainty access;
- save/share only if achievable without new backend dependency; otherwise local/session view state is enough for pilot.

Map and timeline must control one shared model state. Two adjacent but unsynchronized widgets do not satisfy scope.

## 5. Knowledge and epistemic scope

- `Entity`, `Event`, `State`, `Process`, `Trajectory`, `Region`, `Layer`;
- `Relation` as structured Claim;
- `Claim`, `Source`, `EvidenceLink`;
- independent claim kind/origin/review/confidence/evidence/uncertainty;
- explicit corpus coverage;
- alternative reconstructions may be represented where necessary;
- `Similarity` remains computed output, not evidence;
- `same_movement` remains legacy classification projection.

Full canonical schema implementation is not required before the contract and fixtures are reviewed. Compatibility adapters may be used only if they do not erase target semantics.

## 6. Architecture Atlas disposition

Architecture Atlas:

- remains a public compatibility surface at `/atlas/`;
- remains an architecture thematic layer;
- retains current Sources/Media/Relations and Gate A fixtures;
- may supply buildings and context to Life in Context;
- does not define the only user, loop or outcome.

No completed corpus or engineering work is deleted in this cycle.

## 7. Current persistence boundary

Target Investigation/SliceRevision/ResearchBrief remains a valid optional research-work capability.

For the first Life in Context pilot:

- immutable revisions and Research Brief are not prerequisites;
- current mutable ResearchSlice v2 remains compatibility backend code;
- issues #323–#325 are not executed;
- PR #314 is not merged as a Foundation prerequisite;
- no new public backend is required unless the validation design proves static runtime insufficient.

## 8. Frozen scope

Until a recorded decision opens one named branch:

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
- scaling unrelated to pilot blockers.

Security and compatibility maintenance remain allowed.

## 9. Public capability rule

Capability labels:

- `PUBLIC NOW`;
- `BACKEND-AVAILABLE`;
- `PILOT`;
- `CONCEPT TARGET`;
- `FUTURE`.

The public root is the ARTEMIS Core landing. It routes `/globe/` as the primary Leonardo research prototype and `/atlas/` as compatibility-only.

The #355 decision and Concept v3 do not make:

- Leonardo World Slice product-validated;
- temporal Regions implemented;
- AI available;
- the Globe product-validated;
- VR available;
- world-scale coverage real.

## 10. Exit gates

Foundation gate:

- canonical docs agree;
- world-model semantics are reviewable;
- Concept v2 is superseded without deleting history;
- old backlog is held, not silently repurposed;
- no runtime capability claim changed.

Dataset gate:

- World Slice scope and coverage are explicit;
- material Claims have EvidenceLinks/locators;
- trajectory/regions/time uncertainty are represented;
- co-presence and Relation fixtures cannot collapse;
- curation/review cost is recorded.

Experience gate:

- map/timeline/layers share one state;
- user can move time and observe meaningful change;
- local and global context are discoverable;
- source/uncertainty is accessible;
- required desktop/tablet/mobile states work.

Validation gate:

- same-content baseline is frozen;
- contextual understanding and simultaneity discovery are measured;
- relation overclaim errors are measured;
- decision is recorded before branch expansion.

## 11. Promotion decision

After the #355 evidence cycle, record exactly one result:

- continue as generated R&D evidence;
- promote to a maintained experimental Globe app;
- narrow/rework the vertical;
- stop/rethink.

Public deployment, richer historical terrain, guided learning, source-bound AI, broader World Slices, institutional workflow and VR/AR each remain separate decisions.

## 12. Owner documents

- North Star: `ARTEMIS_CONCEPT.md`;
- product thesis: `PRODUCT_THESIS.md`;
- current truth: `PROJECT_TRUTH.md`;
- world model: `SPATIOTEMPORAL_WORLD_MODEL_CONTRACT.md`;
- epistemic semantics: `EPISTEMIC_CONTRACT.md`;
- entities and relations: `ENTITY_MODEL.md`;
- current public data: `DATA_DICTIONARY.md` and `DATA_CONTRACT.md`;
- research persistence: `RESEARCH_SLICE_CONTRACT.md`;
- Foundation decision: `work/2026-07-28_FOUNDATION_V3_DECISION.md`;
- validation execution: `work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md`.
- active Globe decision: `work/2026-08-09_GLOBE_MVP_PROMOTION_DECISION_v1.md`.
