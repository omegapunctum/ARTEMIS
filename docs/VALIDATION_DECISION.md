# ARTEMIS — VALIDATION DECISION

Current decision: [owner-directed Gate E evidence bypass and bounded Region proof](work/2026-09-10_GATE_E_OWNER_BYPASS_AND_REGION_PROOF_v1.md). E1/E2 observations remain NOT COLLECTED; disposition `owner_directed_bypass`; formal user value remains UNVALIDATED / NOT ESTABLISHED. No positive value signal is inferred. Gate D remains COMPLETED / ADVANCE_TO_GATE_E. Exactly one Temporal Region universality proof is authorized after this decision PR is merged; implementation has not started.

## Статус

- Тип: canonical validation outcome document.
- Статус решения: `GATE D COMPLETED / ADVANCE_TO_GATE_E / M5 UX CORRECTION COMPLETED / PROCEED_TO_GATE_D_REVIEW / FORMAL USER VALUE PENDING`.
- Дата последнего обновления: 2026-09-10.
- Active product issue: GitHub issue `#355`.
- Current public proof: #419 / `a1479670d7f7628ffb85b887961ff27654e2fa2f`, stabilizing #418 Place-centric v4.5 / Temporal Map v1.3; 9 Places / 11 Presence episodes. Owner reports NO FINDINGS for #418 and accepted #419; this is not independent-user evidence.
- Recorded correction result: `PROCEED_TO_GATE_D_REVIEW` (owner acceptance, 2026-09-06).
- Active work: decision/specification only; bounded Temporal Region universality proof may start after decision merge.
- Formal Foundation v3 protocol: `docs/work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md` remains gated.

Этот документ фиксирует evidence-backed outcome. Foundation decisions, implementation completion, passing CI and public deployment do not by themselves prove user value.

## 1. Текущее решение

`ADVANCE_TO_GATE_E — GATE D COMPLETED`

Зафиксировано:

- Gate C remains completed/FREEZE for the non-public Leonardo-in-Romagna source boundary;
- Gate D is completed with ADVANCE_TO_GATE_E under #355;
- PR #393 completed Core Reset;
- PRs #395–#396 established and corrected the calendar-based Range/Scrub interaction;
- the post-#396 check recorded `ITERATE` and opened the completed major-life source/review branch;
- PR #400 froze the reviewed major-life candidate package;
- PR #401 completed M2 with `PROCEED_TO_M3`;
- PR #403 completed M3 with `PROCEED_TO_M4`;
- PR #405 recorded M4 `ADOPT` without opening implementation;
- the owner then directly instructed M5 without an intervening repository decision record;
- PR #406 published the bounded 11-Presence whole-life proof;
- PRs #407–#408 aligned governance and recorded the direct M5 result as exactly `ITERATE`;
- #409 scoped the bounded correction; #411 and #412 implemented and published it;
- the owner accepted published #412 in the 2026-09-06 closeout instruction; acceptance is an owner report, not an assistant-performed manual run;
- the correction is completed; the accepted bounded Gate D review is finalized by the separate explicit exit `ADVANCE_TO_GATE_E`;
- formal user value remains unvalidated.

## 2. Historical evidence and decision

The owner manually reviewed the published M5 and observed:

1. Presence markers did not read as one connected life path;
2. the compact popup remained open after the detail drawer opened;
3. markers and controls were too large;
4. the timeline region was too tall;
5. the header collided with map controls;
6. the current M5 interface lacked an `EN / RU` switch;
7. the drawer overlapped attribution/status text.

The historical #408 result was `ITERATE`. `NARROW` was not selected because the 1452–1519 whole-life scope remained understandable enough to continue. `STOP` was not selected because the Temporal Map direction remained viable.

That historical result authorized the now-completed decision-bounded UX correction described by `docs/work/2026-09-05_TEMPORAL_MAP_M5_BOUNDED_UX_SCOPE_v1.md`. It does not authorize another content, source, context, storage, backend, renderer or infrastructure branch.

## 3. Semantic and product boundary

The correction must improve chronological/relational legibility without turning chronology into historical route evidence:

- unsupported transitions remain `unknown_route` with `route_geometry=null`;
- no spatial connector may imply a documented travelled path;
- sequence, period and synchronized marker/timeline emphasis may communicate chronology as presentation;
- Range, Scrub, selection, URL state, popup-first disclosure and explicit double-click focus remain the accepted interaction baseline;
- the current 11 Presence anchors and six coarse periods remain the complete content boundary;
- present-day settlement coordinates remain qualified reference anchors.

## 4. Completed correction evidence and limits

The [2026-09-06 closeout and bounded review](work/2026-09-06_M5_UX_CLOSEOUT_AND_GATE_D_REVIEW_v1.md) records exact PR, Pages and CI identities. #412 is merged + published + manually accepted by the owner. Four exact-head gates passed, including hosted composition and executable interaction checks. The correction result is `PROCEED_TO_GATE_D_REVIEW`.

No new assistant manual test, physical-device matrix, real AT/performance pass or paired EN/RU screenshot evidence is invented. Earlier negative findings remain historical evidence. Acceptance closes this bounded correction; formal user value remains unvalidated.

Gate D retains `ADVANCE_TO_GATE_E / NARROW / REJECT`. M4 `ADOPT` is stored separately as a completed architecture checkpoint. Merged #413 accepted the bounded review. The separate explicit exit records `ADVANCE_TO_GATE_E`; Gate D is completed. The prepared E1/E2 evidence path is NOT EXECUTED and bypassed by explicit owner direction; formal user value remains unvalidated.

## 5. Current record

| Field | Value |
|---|---|
| Foundation decision | `ACCEPTED / PR #328` |
| Formal user-value decision | `PENDING` |
| Active vertical | `Life in Context / Leonardo Temporal Map` |
| Active issue | `#355` |
| Current gate | `D / COMPLETED / ADVANCE_TO_GATE_E` |
| Architecture Gate A fixtures | `3/3 READY` / preserved technical evidence, not user-value evidence |
| World-model contract evidence | `READY / #329 / PR #336` |
| Uncertainty semantics | `READY / #330 / PR #337` |
| Gate C | `FREEZE / PR #362` / non-public historical boundary |
| Core Reset | `COMPLETED / PR #393` |
| M1 | `ITERATE / PRs #395–#396` |
| Major-life package | `REVIEWED / PR #400` |
| M2 | `PROCEED_TO_M3 / PR #401` |
| M3 | `PROCEED_TO_M4 / PR #403` |
| M4 | `ADOPT / PR #405` |
| M5 implementation | `COMPLETED + PUBLISHED / PR #406` |
| M5 direct product decision | `ITERATE / PR #408` |
| Current corpus | 11 coarse Presence anchors / six periods / 1452–1519 |
| Public research surface | `/globe/` R&D research prototype |
| Completed correction | `Temporal Map M5 bounded UX correction v1` / `PROCEED_TO_GATE_D_REVIEW` |
| Current runtime implementation | `COMPLETED + PUBLISHED / PR #419`, after #418; earlier #409/#411/#412 remain completed evidence |
| Correction acceptance and publication | #412 merged/published; owner acceptance recorded 2026-09-06 |
| Gate D exit vocabulary | `ADVANCE_TO_GATE_E / NARROW / REJECT` |
| Gate D review recommendation | `ADVANCE_TO_GATE_E`; exit recorded as `ADVANCE_TO_GATE_E` |
| #410 maintenance | Scheduled Export Airtable success confirmed, run 34005145312 |
| Same-content formal baseline | `NOT RUN` |
| Formal participant wave | `NOT RUN` |

| Gate E planned evidence | `NOT COLLECTED / owner_directed_bypass`; E1/E2 not executed |
| Formal user value | `UNVALIDATED / NOT ESTABLISHED`; no positive value signal |
| Next authority | `explicit_owner_instruction`; one bounded Region proof after decision merge |

## 6. Change rule

Update this document when a user/product result is formally recorded, validation readiness changes, a controlled participant wave completes, the allowed next-decision vocabulary changes or one evidence-backed next branch is opened.

Do not infer user-value validation from code completion, passing CI, public deployment, design enthusiasm or the existence of a Globe interface.
