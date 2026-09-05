# ARTEMIS — VALIDATION DECISION

## Статус

- Тип: canonical validation outcome document.
- Статус решения: `GATE D / M5 ITERATE / BOUNDED UX CORRECTION AUTHORIZED / FORMAL USER VALUE PENDING`.
- Дата последнего обновления: 2026-09-05.
- Active product issue: GitHub issue `#355`.
- Current public proof: M5 content from PR `#406`, UX from merged/published PR `#411` / 11 Presence anchors across 1452–1519.
- Recorded product result: `ITERATE`.
- Opened next branch: `Temporal Map M5 bounded UX correction v1`; fresh post-#411 `ITERATE` requires visible chronological links and a shorter timeline under [the owner's amendment](work/2026-09-05_M5_POST_411_CORRECTION_v1.md).
- Formal Foundation v3 protocol: `docs/work/2026-07-28_FOUNDATION_V3_VALIDATION_PLAN_v1.md` remains gated.

Этот документ фиксирует evidence-backed outcome. Foundation decisions, implementation completion, passing CI and public deployment do not by themselves prove user value.

## 1. Текущее решение

`ITERATE — ONE BOUNDED UX CORRECTION AUTHORIZED`

Зафиксировано:

- Gate C remains completed/FREEZE for the non-public Leonardo-in-Romagna source boundary;
- Gate D remains open/in progress under #355;
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
- the whole-life scale remains viable, while relational legibility and six interface-composition findings require one bounded correction;
- formal user value remains unvalidated.

## 2. Evidence and decision

The owner manually reviewed the published M5 and observed:

1. Presence markers did not read as one connected life path;
2. the compact popup remained open after the detail drawer opened;
3. markers and controls were too large;
4. the timeline region was too tall;
5. the header collided with map controls;
6. the current M5 interface lacked an `EN / RU` switch;
7. the drawer overlapped attribution/status text.

The selected result is `ITERATE`. `NARROW` was not selected because the 1452–1519 whole-life scope remained understandable enough to continue. `STOP` was not selected because the Temporal Map direction remained viable.

The result authorizes one decision-bounded UX correction described by `docs/work/2026-09-05_TEMPORAL_MAP_M5_BOUNDED_UX_SCOPE_v1.md`. It does not authorize another content, source, context, storage, backend, renderer or infrastructure branch.

## 3. Semantic and product boundary

The correction must improve chronological/relational legibility without turning chronology into historical route evidence:

- unsupported transitions remain `unknown_route` with `route_geometry=null`;
- no spatial connector may imply a documented travelled path;
- sequence, period and synchronized marker/timeline emphasis may communicate chronology as presentation;
- Range, Scrub, selection, URL state, popup-first disclosure and explicit double-click focus remain the accepted interaction baseline;
- the current 11 Presence anchors and six coarse periods remain the complete content boundary;
- present-day settlement coordinates remain qualified reference anchors.

## 4. Required evidence for the correction

The implementation PR must provide:

- green Core, Globe Repository Boundary and Geospatial Assets checks on the exact head;
- automated behavior evidence for chronology cues, Range/Scrub, selection, popup/drawer, localization and URL restoration;
- fail-closed no-route-geometry/no-spatial-connector evidence;
- deterministic desktop, tablet and hosted-mobile composition evidence;
- English and Russian parity for one shared semantic state;
- a fresh manual product check after publication.

That check records exactly one result: `PROCEED_TO_GATE_D_REVIEW`, `ITERATE`, `NARROW` or `STOP`.

## 5. Current record

| Field | Value |
|---|---|
| Foundation decision | `ACCEPTED / PR #328` |
| Formal user-value decision | `PENDING` |
| Active vertical | `Life in Context / Leonardo Temporal Map` |
| Active issue | `#355` |
| Current gate | `D / OPEN / IN PROGRESS` |
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
| Opened next branch | `Temporal Map M5 bounded UX correction v1` |
| Runtime implementation | `IN PROGRESS / PR #411`; scope authorized by merged PR #409 |
| Correction acceptance and publication | `PENDING`; no fresh manual product result recorded |
| Same-content formal baseline | `NOT RUN` |
| Formal participant wave | `NOT RUN` |

## 6. Change rule

Update this document when a user/product result is formally recorded, validation readiness changes, a controlled participant wave completes, the allowed next-decision vocabulary changes or one evidence-backed next branch is opened.

Do not infer user-value validation from code completion, passing CI, public deployment, design enthusiasm or the existence of a Globe interface.
