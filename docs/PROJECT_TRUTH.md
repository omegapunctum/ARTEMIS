# ARTEMIS — PROJECT TRUTH

## Статус

Latest operational update: #412 is merged/published and owner-accepted on 2026-09-06. M5 bounded UX correction is completed with `PROCEED_TO_GATE_D_REVIEW`; #409/#411/#412 are completed evidence. The [work/2026-09-06_M5_UX_CLOSEOUT_AND_GATE_D_REVIEW_v1.md](work/2026-09-06_M5_UX_CLOSEOUT_AND_GATE_D_REVIEW_v1.md) records a bounded Gate D review recommending `ADVANCE_TO_GATE_E`, not a final gate exit or formal user-value validation. #410 scheduled Export Airtable repair is confirmed green (run 34005145312).

- Тип: canonical current-state document.
- Дата фиксации: 2026-09-06.
- Владелец смысла: фактическая доступность продукта и граница между public, backend, R&D и future scope.
- Обновляется только при изменении фактической доступности runtime, данных, пользовательского сценария или когда active R&D/data-governance status иначе создаёт прямое противоречие с capability wording.

Этот документ отвечает на вопрос «что ARTEMIS действительно умеет сейчас». Он не заменяет продуктовую стратегию, data contract или release policy.

## 1. Принятое продуктовое направление

Foundation v3 / PR `#328` restored ARTEMIS as a source-aware spatial-temporal World Model. Foundation v3.1 / issue `#363` / PR `#364` clarifies that `World Model` is a source-aware **knowledge representation about the world**, not an objective digital twin or a claim of completeness. This accepted clarification changes North Star wording, not current capability.

Первый active validation vertical — `Life in Context / Leonardo Temporal Map`; issue #355 делает 3D Globe единственной активной product-development surface. Core Reset завершён PR `#393`: Architecture Atlas, backend и преждевременная инфраструктура отделены от текущего критического пути.

Важно:

- Foundation documentation не реализует world model runtime;
- root public runtime является малой ARTEMIS Core landing page;
- `/globe/` — primary public research prototype, явно не product-validated historical capability;
- `/atlas/` сохраняет прежний Architecture Atlas как compatibility-only surface;
- real validated Life in Context synchronized multi-layer experience ещё не доступен как продукт;
- Claim/Evidence discipline сохраняется как trust layer;
- Research Brief/revisions остаются optional future research capabilities, а не current public core;
- generative AI, causal/counterfactual runtime, personal knowledge model, VR/AR and universal corpus remain frozen/future;
- **A real executable 3D Globe R&D artifact exists** and uses MapLibre GL JS `5.24.0` in isolation; the compatibility Atlas at `/atlas/` remains on MapLibre GL JS `4.7.1`.
- PR `#389` first published the generated artifact at `/globe/` as a labelled experimental review preview. Core Reset makes it the primary route from the root landing without upgrading its content maturity. The selected Earth context remains a pinned, bundled Natural Earth present-day layer, not historical geography or a live provider capability.
- PR `#379` integrated the frozen Gate C package into the then non-public generated Globe artifact through the shared World Model → Explorer State → Render Projection path. It preserved `0` authorized historical geometries/primitives, all withheld Region alternatives and all unknown-route gaps.
- PR `#380` adds 96 deterministic Explorer views from six source-native temporal presets and all 16 combinations of four semantic layers, plus synchronized timeline/layers, canonical selection/picking, inspector, URL restoration, keyboard operation and reduced-motion behavior. This is completed technical interaction evidence, not a completed Gate D product-value decision.
- PR `#395` established the calendar-based `Leonardo Life Path` scaffold over the frozen material. `Range` shows Presences overlapping a selected calendar interval; `Scrub` progressively reveals the path from a chosen start. Dashed links are presentation-only chronology; all historical route gaps keep null geometry. The 96 Explorer views and layer semantics remain underlying technical evidence, not default controls.
- The first published manual check after #395 produced `ITERATE`: Range and Scrub looked too similar, the timeline lacked primary visual weight, place selection exposed too much persistent text and single-click camera movement was too aggressive.
- PR `#396` completed that bounded iteration and is published: the full-width bottom timeline is the primary time instrument; Range is a two-handle interval; Scrub keeps a chosen build origin plus one current-time cursor; first click opens a compact popup without moving the camera; optional further action opens the right detail drawer; double-click may focus/zoom the selected place.
- The fresh user check of the published #396 interface recorded `ITERATE`: the interaction is now good enough to continue, while remaining visual problems are explicitly non-priority.
- M1 — UX checkpoint is complete with `ITERATE`. PR #400 completed independent review of the major-life candidate package. PR #401 completed M2 with `PROCEED_TO_M3`. PR #403 completed M3 with `PROCEED_TO_M4`. M4 is complete with `ADOPT` for the source-federated semantic direction.
- After PR #405 explicitly closed M4 without opening a successor, the owner directly instructed M5. No intervening repository decision record exists. PR #406 then merged and published the bounded M5 Whole-Life Runtime Proof. This is recorded as a governance deviation, not retroactive M4 authorization.
- The direct owner review of published M5 recorded exactly `ITERATE`. The whole-life scope remains viable, while relational legibility, popup/drawer state, visual density, timeline height, map-control collisions, current-M5 localization and attribution placement required bounded correction. PR #409 merged the 2026-09-05 scope decision. PRs #411/#412 implemented and published the correction, now owner-accepted with `PROCEED_TO_GATE_D_REVIEW`. PR #410 separately repaired Export Airtable CI, confirmed by successful scheduled runs.
- PR `#382` adds pinned Natural Earth 1:110m Land as real `present_day_context` with explicit provenance, licensing, attribution, cache, secret and temporal-role policy. Historical geometry remains withheld and terrain remains synthetic/non-live.
- PR `#383` adds deterministic desktop/tablet/hosted-mobile Chromium evidence, accessible-name/target-size/overflow/overlay checks and responsive overlay fixes. Hosted evidence is not a complete WCAG audit, real-device result or production performance SLO.
- PR `#385` makes that hosted visual evidence fail closed on non-zero loaded/rendered Natural Earth features and captures DOM plus PNG from the same wall-clock CDP page. Reviewed screenshots now show legible present-day land/coastlines, but hosted 500 px Chrome still does not prove a real 390 CSS px mobile pass.
- The Gate D place-anchor overlay resolves Rimini, Cesena, Cesenatico and Imola only as CC0 present-day `named_settlement` reference points. Each point carries a Claim, EvidenceLink locator, Source/rights record and material spatial-precision Uncertainty. It does not modify the frozen Gate C package, claim an exact Leonardo/event position, connect a route or create a Region boundary.
- The current public M5 life-path presentation covers 11 Presence anchors: seven reviewed major-life anchors plus the four 1502 Romagna anchors, organized into six coarse periods across 1452–1519. It does not claim a complete biography, continuous residence, duration at each place or known routes between places.
- Issue #344 / PR #351 semantic parity is merged executable evidence; issue #355 remains the active product-facing MVP contour.
- Gate C is completed/FREEZE in #332/#360 / PR #362 for the non-public Leonardo-in-Romagna boundary, 8 August–31 December 1502.
- The Gate C package has two independent READY reviews and measured curation/review cost, but `historical_objects_ready=false`, `promotion_allowed=false`, Claims remain draft and unsupported route/Region geometry remains withheld.
- Foundation v3.1 / #363 / PR #364 is completed. Gate D is separately open/in progress under #355; current implementation and public R&D access do not themselves complete it or prove user value.
- #368 established the original six-table empty/non-authoritative Airtable World Model shadow schema. Merged PR #372 extends that preflight surface with three additional empty shadow-only tables plus parity fields, but **no Gate C historical row has been written**. Issues #371/#373 are deferred outside the Gate D critical path.

## 2. Что доступно публично

GitHub Pages публикует статический runtime:

- root Core landing без runtime dependencies;
- `/globe/` как primary Leonardo research prototype;
- `/atlas/` как frozen compatibility map с checked-in `data/*` и PWA behavior;
- все три entry points не требуют backend API.

GitHub Pages не исполняет FastAPI. Без отдельно настроенного `ARTEMIS_API_BASE` публичный сайт не предоставляет рабочие auth, Research Slices, Stories, Courses, uploads и moderation API.

## 3. Что реализовано в репозитории, но требует backend runtime

- auth и refresh-session flow;
- drafts и uploads;
- moderation lifecycle;
- Research Slice v2 owner create/edit/reopen/delete, explicit question/rationale/evidence/findings/conclusion/uncertainty, nested Saved View и unlisted read-only share/rotate/revoke;
- Stories CRUD как thin orchestration над slices;
- Courses CRUD как thin orchestration над stories;
- Explain Context Contract без генеративного AI-ответа;
- Redis-backed session paths и SQLite baseline persistence.

Наличие backend-кода не означает, что функция доступна на публичном GitHub Pages URL.

Research Slice schema/code sync выполнен как v2: migration 203, API, client и tests используют explicit question/rationale, fail-closed evidence state и Source/Relation refs, typed findings, conclusion/unresolved, uncertainty, schema/content version и вложенный Saved View.

После Concept Lock v2 current model честно классифицируется как mutable compatibility envelope. Она не реализует:

- first-class Investigation;
- immutable Slice Revisions;
- Claim/EvidenceLinks with locators and evidence relation/strength;
- pinned dataset identity;
- revision-pinned share;
- deterministic citation-ready Research Brief.

Migration preflight и release gate подтверждают current backend capability, но не target research model, public availability or product value.

## 4. Текущее состояние данных

Текущий Architecture Atlas Airtable/public export содержит:

- 31 Features;
- 6 comparison cohorts минимум по 3 Features;
- 35 reviewed Sources;
- 28 reviewed Media records linked as primary к 28 Features (`90.32%`);
- 12 reviewed current Relation records и 21 reviewed legacy relation-source links;
- только архитектурные объекты.

Известные ограничения public/Architecture Atlas corpus:

- canonical identity migration v1 завершена в PR `#290`: ETL и public artifacts используют `Features.id` UUID v4, а Airtable record ID отделён как `source_record_id`;
- source migration выполнена: контрольное чтение Airtable подтверждает `19/19 id_status=ok`; точная таблица, execution evidence и recovery-план зафиксированы в `docs/work/2026-07-16_CANONICAL_IDENTITY_MIGRATION_v1.md`;
- initial Source batch #283 закрыл `19/19` исходных Features; V2/V3 довели текущий corpus до 35 reviewed Sources и `31/31` Feature Source coverage;
- initial Media batch #283 содержал 16 reviewed direct assets; V2 довёл текущий корпус до `28/31` primary Media, а для трёх rights-blocked объектов public `image_url=null` (Бурдж-Халифа, Вилла Савой и Центр Помпиду); полный перечень исходной миграции и blockers находится в `docs/work/2026-07-16_SOURCES_MEDIA_MIGRATION_v1.md`;
- 7 enabled empty source Layers исключены из public `layers.json` и сохранены как actionable semantic warnings;
- Media semantics реализованы в ETL; текущая reviewed coverage составляет `28/31`, а для трёх rights-blocked объектов public `image_url=null`;
- Relations/Similarity pilot реализован технически: detail panel показывает 12 reviewed records, а computed Similarity — отдельно;
- 10 из 12 current Relation records имеют тип `same_movement`; Concept Lock v2 классифицирует их как documented shared-classification compatibility records, а не substantive historical Relations;
- только два current records (`influenced`, `inspired_by`) являются кандидатами на substantive Relation value, но ещё не имеют target claim-level locator/evidence semantics;
- semantic ETL/release gate проверяет blocking errors отдельно от budgeted warnings, cross-artifact evidence/review semantics, enabled populated Layers и отсутствие unreviewed legacy image URLs;
- текущий checked-in report имеет статус `ready_with_warnings`: 14 warnings (7 empty-Layer exclusions, 3 missing primary Media и 4 corpus-quality signals), 0 blocking errors;
- comparison-pilot profile имеет технический статус `comparison_ready`: 31 Feature, 6 cohorts, 12 legacy-counted Relations, 100% current link coverage и 90.32% primary Media;
- Architecture Gate A package завершён со статусом `3/3 READY` и двумя independent review processes; он сохраняется как reviewed fixture/evidence package, но не является Foundation v3 user-value validation;
- executable world-model fixtures #329 / PR #336 and uncertainty semantics #330 / PR #337 are reviewed READY contract evidence; they are fixtures/contracts, not public World Model data or a public Globe runtime.

### Airtable World Model shadow curation schema

После #366 / PR #367 существующие восемь legacy Airtable tables явно зафиксированы как Architecture Atlas compatibility/public-projection curation, а не как Foundation v3 semantic owner. Canonical current export остаётся:

`legacy Airtable tables → scripts/export_airtable.py → semantic data gate → checked-in public data/*`.

#368 / PR #369 создал исходный **empty/non-authoritative shadow schema** из шести таблиц:

- `WorldSlices`;
- `KnowledgeObjects`;
- `ObjectParts`;
- `Claims`;
- `EvidenceLinks`;
- `Uncertainties`.

Merged PR #372 завершил отдельный **schema/mapping preflight** для frozen Leonardo Gate C package. В live Airtable дополнительно существуют три shadow-only таблицы, также проверенные с `0` records:

- `SliceLayers` — exact per-WorldSlice layer identity/role без записи Gate C слоёв в legacy public-source `Layers`;
- `WorldSources` — lossless World Model source/rights registry без записи Leonardo Sources в legacy public `Sources`;
- `UncertaintyTargets` — storage junction для many-target `Uncertainty.target_refs[]` без клонирования 11 исходных Uncertainty identities.

Дополнительные parity/provenance fields в `KnowledgeObjects`, `ObjectParts`, `Claims`, `EvidenceLinks` и `Uncertainties` сохраняют source temporal tokens, source/reconstruction metadata, Claim confidence basis, Uncertainty basis и WorldSource refs. Эти поля являются storage representation, а не новой semantic ontology.

Фактическая граница shadow contour на 2026-08-12:

- все шесть исходных #368 tables по-прежнему проходят `--require-empty` с `0` historical records;
- все три #371 extension tables проверены с `0` records;
- legacy `KnowledgeObjects.layers` должен оставаться пустым для Gate C shadow import; World Model layer roles идут через `SliceLayers`;
- legacy `EvidenceLinks.source` должен оставаться пустым для Gate C shadow import; Claim-specific evidence идёт через `EvidenceLinks.world_source → WorldSources`;
- legacy Architecture Atlas `Layers`, `Sources`, `Media`, exporter и checked-in public `data/*` не изменены этим contour;
- новый Relation table не создавался; #331 deferred;
- live schema evidence v1 остаётся в `fixtures/airtable_curation/v1/`; #371 extensions/mapping/row-plan evidence находятся в `fixtures/airtable_curation/v2/`;
- `scripts/validate_airtable_leonardo_shadow_preflight.py` fail-closed проверяет frozen package, schema extensions, ref closure, unknown-route/geometry-withheld semantics и Gate C/Gate D boundary;
- deterministic semantic-ID row-plan builder воспроизводит ровно **154 candidate rows**: 1 WorldSlice, 4 SliceLayers, 10 WorldSources, 17 KnowledgeObjects, 11 ObjectParts, 22 Claims, 38 EvidenceLinks, 11 Uncertainties и 40 UncertaintyTargets;
- этот row plan frozen отдельным lock с SHA-256 `ff63b8ed036ec79ac73e11c2eb4d3cad22b69b0e5a361c23cef767c5c5ac83f1` и проверяется Release Discipline;
- **row-plan lock не является разрешением на historical write**: `historical_rows_authorized=false`, independent mapping review остаётся обязательным до первой записи;
- Airtable автоматически создаёт inverse-link fields; они являются storage implementation detail, а не новыми семантическими Relations;
- record-time `dateTime` fields используют Airtable display timezone `Europe/London`; это не historical valid time и не меняет temporal semantics World Model.

Наличие девяти empty shadow tables, deterministic mapping и frozen row plan означает только, что ARTEMIS имеет проверяемую editorial storage/preflight форму для возможного будущего controlled import. Оно **не** означает наличие World Model corpus в Airtable, historical readiness, round-trip parity, Gate D evidence или public capability.

Gate C historical curation package остаётся отдельным от public Airtable export и от пустого shadow storage:

- #332/#360 / PR #362 froze Leonardo-in-Romagna 1502 as a non-public World Slice boundary;
- 17 candidate objects, 10 Sources, 22 atomic Claims, 38 EvidenceLinks and 11 provenance-bearing Uncertainties are bound to the frozen reviewed revision;
- no documented Relations are stored while #331 remains deferred;
- three inter-place routes remain unknown with no invented geometry;
- Duchy of Romagna Region states remain geometry-withheld where evidence/rights do not support a boundary;
- this package is reviewed as a **Gate C boundary**, not promoted to public/READY historical product data;
- none of the 154 planned shadow rows has been written at the #371 row-plan-lock stage.

Public dataset остаётся Architecture Atlas pilot, Gate C package — non-public frozen authority, а Airtable World Model tables — empty non-authoritative shadow infrastructure. #371/#373 import/review work is deferred; Gate D consumes the repository package directly.

## 5. Что не считается реализованным продуктом

- universal spatial-temporal knowledge-model runtime;
- product-validated Life in Context / Leonardo Temporal Map experience; the current `/globe/` loop is a bounded public R&D prototype whose direct M1 and M5 checks recorded `ITERATE`, while formal validation remains pending;
- Airtable World Model shadow schema as a historical corpus, canonical storage authority or product capability;
- frozen 154-row Airtable plan as imported data, round-trip parity evidence or historical readiness;
- Gate C package integrated into Airtable as a validated shadow copy;
- a completed Gate D user-value decision; implementation of #393/#395/#396 does not itself close the gate;
- first-class State, Process, Trajectory and temporal Region schemas in current public runtime;
- product-ready 3D Globe, production dynamic terrain or VR experience; `/globe/` is only a bounded public R&D review route;
- production-hardened multi-node backend;
- публично развернутый end-to-end Research Slice workflow: share-контракт реализован в коде, но отдельный API runtime и `ARTEMIS_API_BASE` ещё не опубликованы;
- полноценные guided Stories и Courses;
- AI explanation/comparison/hypothesis generation runtime;
- AI Knowledge Exploration Interface or executable AI view-action contract;
- personal knowledge model;
- зрелый relation graph за пределами 12-record validation pilot;
- first-class public Claim/EvidenceLink corpus;
- immutable Investigation/revision model and Research Brief export;
- causal, predictive или counterfactual engine;
- universal corpus or objective digital twin of the world.

## 6. Главные риски текущего состояния

1. Public R&D availability may be mistaken for product validation or historical readiness.
2. Документация и backend breadth создают впечатление зрелости, не подтверждённое содержанием.
3. Identity/source/media contracts допускают формально успешный, но семантически слабый export.
4. Legacy `same_movement` count может создать впечатление relation graph, хотя 10/12 записей являются shared classification.
5. Scaling до доказательства product loop увеличивает стоимость неподтверждённой архитектуры.
6. Backend-complete mutable Slice v2 может быть ошибочно принят за target immutable research model.
7. Fresh usability feedback без cognitive и behavioral evidence может создать ложное впечатление полностью подтверждённой продуктовой ценности.
8. Globe MVP может стать shadow product, если он обойдёт shared World Model / Explorer State / Render Projection; public access itself does not prove value.
9. Long-term attractor может быть ошибочно воспринят как permission to implement AI/VR/universal corpus before gates; Foundation v3.1 explicitly forbids this.
10. `World Model` wording can drift back toward objective-digital-twin claims unless the knowledge-vs-world boundary remains explicit.
11. Airtable World Model schema может стать competing semantic/storage authority, если данные начнут вноситься вручную в обход deterministic import/export + row-level validation + round-trip parity against the frozen repository package.
12. Frozen 154-row plan может быть ошибочно принят за completed import evidence; поэтому live historical write остаётся fail-closed до отдельного independent mapping review и последующего readback/parity proof.
13. Accepted #377 / PR #378 refinement semantics can be mistaken for runtime/storage capability; #392 demonstrates that its immutable review envelope incorrectly captured mutable repository routing.
14. Required CI previously coupled the static Globe path to FastAPI, Redis, moderation, Airtable shadow plans and broad governance synchronization, obscuring the actual product signal; Core Reset fixed the required path, but compatibility breadth can still distract from the active user-value question.

## 7. Текущий operational verdict

ARTEMIS находится в состоянии **Gate C frozen / Core Reset completed / M1 completed with ITERATE / M2 completed with PROCEED_TO_M3 / M3 completed with PROCEED_TO_M4 / M4 completed with ADOPT / M5 whole-life runtime proof completed with ITERATE / M5 bounded UX correction completed with PROCEED_TO_GATE_D_REVIEW; bounded Gate D review complete, exit decision pending / formal user value not yet validated**.

Root is a small Core landing. `/globe/` is the primary research surface; `/atlas/` retains the Architecture Atlas compatibility runtime. The Globe remains non-product-validated and consumes draft/rejected historical Claims. Foundation contracts remain ahead of user evidence. The backend, legacy ETL and nine empty Airtable World Model shadow tables are preserved but frozen outside the Core critical path.

Reviewed/accepted foundation and implementation evidence includes:

- #329 / PR #336 world-model fixtures — READY;
- #330 / PR #337 uncertainty semantics — READY;
- #339–#345 / PRs #346–#352 renderer-neutral Globe foundations — accepted;
- #332/#360 / PR #362 Gate C World Slice boundary — FREEZE with two independent READY reviews;
- #363 / PR #364 Foundation v3.1 Attractor refinement — accepted with all required repository workflows green on its merge candidate;
- #377 / PR #378 Progressive Refinement Contract v1 — accepted foundation evidence without runtime/storage capability change;
- PR #379 — frozen Gate C package consumed by the initially non-public generated Globe artifact through the shared semantic path;
- PR #380 — synchronized time/layers/selection/inspector interaction increment with 96 deterministic Explorer views and all six PR workflows green;
- PR #382 — pinned bundled Natural Earth physical-land context with explicit provider/licensing/temporal-role boundary and all seven PR workflows green;
- PR #383 — desktop/tablet/hosted-mobile browser evidence, zero measured overflow/name/target/overlay failures and all six triggered PR workflows green;
- PR #385 — same-page wall-clock CDP visual-readiness evidence with non-zero Natural Earth source/render counts, legible reviewed hosted screenshots and all six triggered workflows green;
- PR #389 — bounded `/globe/` public R&D review publication;
- PR #390 — four source-bound present-day named-settlement anchors with provenance and uncertainty closure; no exact historical positions, routes or boundaries;
- PR #391 — evidence-aware Globe UX correction and canonical URL/state restoration;
- PR #393 — Core Reset completed; Globe primary, Atlas compatibility-only and ARTEMIS Core Check isolated as the required product signal;
- PR #395 — calendar-based Leonardo Temporal Map life-path interaction;
- first published #395 manual check — `ITERATE` product-feedback result;
- PR #396 — published first-feedback correction: primary bottom timeline, distinct Range/Scrub, popup-first selection, optional right drawer and double-click camera focus.
- PR #401 — M2 one-source proof completed through the existing semantic/projection path;
- PR #403 — M3 two-source/one-Presence proof completed with explicit agreement and spatial-granularity refinement; recorded result `PROCEED_TO_M4`.
- M4 architecture decision — `ADOPT` for the source-federated semantic direction; no live federation, generic ingestion/storage or public runtime authorization.
- PR #406 — owner-directed bounded M5 runtime proof with 11 Presence anchors and six periods across 1452–1519.
- M5 governance alignment — records that no pre-start repository decision existed and does not rewrite the M4 record.
- M5 direct product check — `ITERATE`; relational legibility and bounded interface correction are justified without narrowing the whole-life scope or inventing routes.

Completed/deferred Airtable data-governance evidence now includes:

- #366 / PR #367 — legacy Airtable boundary/schema truth and canonical audit path aligned;
- #368 / PR #369 — original six-table empty executable non-authoritative Airtable World Model shadow schema;
- #371 / merged PR #372 — completed lossless schema/mapping preflight with three additional empty shadow tables and a 154-row frozen semantic-ID plan; #371/#373 are deferred and historical writes remain unauthorized.

Issue #377 is foundation maintenance whose exact lifecycle is owned by `PROGRESSIVE_REFINEMENT_CONTRACT.md` and its review registry. It is completed through PR #378, but does not enter the product issue lifecycle sets, consume the product-gate WIP slot or change current capability. Gate D remains explicitly open under #355 as the sole active product gate. The runtime may read/render the frozen Gate C package plus the separate contextual place-anchor overlay, but contract acceptance does not authorize runtime/storage mutation, Airtable writes or product-ready capability. There is no active Airtable import issue.

#371/#373 могут возобновиться только отдельным lifecycle decision. Если #371 будет reopened, следующий разрешённый шаг — independent review frozen row plan; только после успешного review можно отдельно разрешить controlled live import, обязательный readback/row-level validation и normalized round-trip parity against the frozen Gate C package.

Для активного #355 primary order:

1. preserve M4 `ADOPT`, the honest M4 → M5 deviation record and PR #406 as the bounded 11-Presence proof;
2. preserve the direct M5 result as exactly `ITERATE`;
3. preserve #409/#411/#412 as completed scope/implementation/publication/owner-acceptance evidence; accept the decision-only closeout and then record a Gate D exit using `ADVANCE_TO_GATE_E / NARROW / REJECT`;
4. keep unknown routes geometry-free and distinguish chronology from historical travel;
5. preserve #410 as scheduled-CI-confirmed maintenance evidence; do not reopen that repair.

The work registry already paused the old D1/M1/A1/P1 matrix during later narrowing; its unperformed physical/AT/performance runs remain limitations, not passes. Basic keyboard, responsive and accessible behavior remains required. Gate D retains its original exit vocabulary and meaning; only an explicit `ADVANCE_TO_GATE_E` opens the next task-based evidence step.

Issue #331 is deferred outside this critical path. Until it is explicitly reopened and accepted, the real slice/runtime may expose only derived proximity/co-presence and must not publish documented encounter, interaction, influence or causal predicates.

The superseded #323–#325 path and PR #314 remain closed. Passing fixtures, storage schemas, row plans or Foundation documents prove neither public capability nor user value.

## 8. Правило честного описания

README, UI, issues, release notes и публичные материалы обязаны различать:

- `PUBLIC NOW` — работает на опубликованном URL;
- `BACKEND-AVAILABLE` — реализовано, но требует отдельного runtime/configuration;
- `PILOT` — существует, но недостаточно подтверждено данными или пользователями;
- `R&D` — bounded experimental architecture/runtime work that may be publicly reviewable but is not a product-readiness promise;
- `SHADOW` — non-authoritative storage/curation/evidence contour, not public capability and not canonical historical corpus;
- `CONCEPT TARGET` — утверждено концептуально, но не реализовано;
- `FUTURE` — концепция или запланированный слой.

Long-term attractor, AI view-control semantics, personal knowledge, universal corpus and VR/AR remain `FUTURE` until separately implemented and validated.

Формулировка более высокого уровня зрелости запрещена без исполнимого evidence.
