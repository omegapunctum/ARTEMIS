# Gate E — bounded task/evidence protocol v1

- Date: 2026-09-06.
- Status: protocol prepared; task evidence NOT COLLECTED; no Gate E outcome recorded.
- Entry: Gate D completed with `ADVANCE_TO_GATE_E` in merged [PR #414](https://github.com/omegapunctum/ARTEMIS/pull/414), after accepted review #413.
- Owner: #355; current stage remains Gate E evidence preparation.
- Scope: the accepted read-only Leonardo Temporal Map, 11 coarse Presence anchors and six periods across 1452–1519. No runtime/data change.

## Additional owner acceptance

The owner reports in this conversation on 2026-09-06: “Я проверил все вручную. Замечаний теперь нет. Продолжай”. Record this as additional manual owner acceptance with no reported findings. It corroborates the accepted UX correction; it is not a new assistant test or a task-by-task Gate E result. Device, browser, duration, exact loaded deployment SHA and individual actions were not supplied. Do not infer them or mark the tasks below passed retrospectively. The previously accepted implementation is #412; a cache-busting URL does not prove the loaded build SHA.

M4 `ADOPT`, original M5 `ITERATE`, correction `PROCEED_TO_GATE_D_REVIEW` and Gate D `ADVANCE_TO_GATE_E` remain separate completed decisions. No repeat general UI acceptance check is required from the owner.

## Question and bounded design

Can someone use the current map to reconstruct Leonardo's documented chronology, narrow it in time, inspect its evidence and explain its limits without treating the displayed chronology as a known travelled route?

Use one formative session first, preferably with one consenting person unfamiliar with the implementation. An owner-only session must be labelled as such and cannot demonstrate novice usability. No recruitment or outreach is performed by this PR. This is a task-comprehension probe, not a comparative study, market validation or formal participant wave. The older Foundation v3 plan remains deferred and its `EXPAND ONE BRANCH` requirements are not waived or satisfied here.

Freeze these prompts and rubric before the session. Use the published [Temporal Map](https://omegapunctum.github.io/ARTEMIS/globe/?mode=range&start=1452&end=1519). Record UTC time, URL/state, displayed language, device/browser and available deployment identity. If exact build identity cannot be verified, say unknown and retain the timestamp; do not mix observations across a changed deployment. Give no interface walkthrough or answer key before unaided attempts. Record assistance explicitly, then allow it to diagnose a failed task. Time is descriptive only; there is no invented speed threshold.

## Five tasks

Read only the participant prompt column aloud. The observer criteria are an answer rubric, not hints to give beforehand.

| ID | Participant prompt | Observer evidence and success criterion |
|---|---|---|
| T1 | Describe the beginning, a middle phase and the end of the life sequence shown here. Is this a complete biography? | Written summary identifies displayed places/periods in chronological order and recognizes the sparse, incomplete coverage. Judge against the current displayed records; do not add historical knowledge as required content. |
| T2 | Show only the part of the life overlapping 1502–1504. Explain what changed and what the interval does not tell you. | Uses Range; visible Presences reflect overlap with the interval. Does not claim a precise day, continuous residence or historical absence from omitted points. Capture resulting URL and summary. |
| T3 | Starting from 1452, show how the sequence accumulates up to 1504. Explain how this differs from your previous view. | Uses Scrub with origin 1452 and cursor 1504; explains accumulated history versus the bounded Range interval. Selection/time remain coherent. Capture resulting URL. |
| T4 | Choose one displayed Presence. Find the information supporting it and tell me what remains uncertain. | Opens details; identifies an actual source and locator shown for the selected record, separates assertion from present-day reference location and states one relevant uncertainty/limit. Record selected ID, source/locator and participant wording. Do not require a precision or citation the interface does not provide; missing material evidence access is a finding. |
| T5 | What can you conclude from the lines between points? Save or reopen this view so that you can explain the same selection and time later. | Explicitly distinguishes chronology links from documented travel routes; does not infer encounter, influence or causality. Restored URL retains the time/mode and selection supported by the current loop. Capture before/after state and explanation. |

## Record and rubric

For each task retain: task ID, unaided answer/action, resulting URL or record ID, `PASS / ASSISTED / FAIL / NOT_RUN`, assistance, observed problem and optional elapsed time. PASS requires the stated observable criterion without help. ASSISTED is not silently counted as PASS. NOT_RUN is missing evidence, not failure. Keep interpretation separate from verbatim observation. Do not publish participant names, contact details or identifiable recordings; only a de-identified summary is needed in repository evidence.

Critical trust error: representing chronology as a documented route, inventing source-supported precision, asserting completeness/absence from missing coverage, or converting proximity into a documented relation. Distinguish participant misunderstanding from a demonstrated interface defect; both matter, but neither proves the other automatically. Lost shared state or inaccessible material provenance is a material task blocker.

## Decision rule and stopping condition

This first session produces a formative disposition, not a Gate E exit:

- All five tasks PASS unaided and zero critical trust errors: sufficient for this bounded comprehension probe. Record the result and decide whether one independent replication or a separately scoped comparison would change the next product decision. No automatic feature expansion or user-value claim.
- Any ASSISTED/FAIL or critical trust error: record the exact task and observation. Identify whether the gap is interaction, comprehension, content/evidence or protocol ambiguity. Propose implementation only if a concrete material defect is demonstrated; general preferences do not reopen M5.
- Any NOT_RUN or untraceable observation: evidence incomplete. Complete only the missing observation, without repeating accepted general UI checks.
- If the prompt itself is ambiguous, record a protocol revision and keep pre/post-revision results separate; never rewrite criteria to turn a failure into success.

Stop after one completed session and a short evidence readout. Do not recruit a larger wave, reread the architecture, add sources/layers, reopen #334 or widen infrastructure by default. A later Gate E exit must name its own evidence and scope; this protocol does not repurpose M4 `ADOPT` or Gate D vocabulary as a new gate outcome.

## Initial evidence ledger

| Evidence | Status | What it supports |
|---|---|---|
| Earlier #412 publication and owner acceptance, closed by #413 | Completed; see accepted closeout review | Bounded UX correction acceptance |
| Owner report on 2026-09-06 quoted above | No findings reported; execution details not supplied | Additional owner acceptance only |
| T1–T5 structured observations | NOT COLLECTED | No task-comprehension conclusion yet |
| Independent replication / same-content comparison | NOT RUN | No novice/generalized or comparative value claim |

References: [Gate D exit](2026-09-06_GATE_D_EXIT_DECISION_v1.md), [accepted bounded review](2026-09-06_M5_UX_CLOSEOUT_AND_GATE_D_REVIEW_v1.md), [current validation decision](../VALIDATION_DECISION.md).
