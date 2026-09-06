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

E1 requires one consenting independent novice unfamiliar with the implementation. An owner-only or agent session cannot substitute for E1. No recruitment or outreach is performed by this PR. E1 is a task-comprehension probe; E2 is the conditional formative comparison described below. Neither is market validation or the old formal participant wave. The older Foundation v3 plan remains deferred and its `EXPAND ONE BRANCH` requirements are not waived or satisfied here.

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

- All five tasks PASS unaided and zero critical trust errors: E1 passes and opens E2 preparation, not implementation or a user-value claim.
- Any ASSISTED/FAIL or critical trust error: record the exact task and observation. Identify whether the gap is interaction, comprehension, content/evidence or protocol ambiguity. A demonstrated material failure opens one bounded fix, then a retest of the failed task (and directly affected regression checks), not the whole general UI review. Preserve first-attempt and retest results separately. A previously assisted participant is no longer naive to that task; verify independent unaided completion with a fresh novice where learning could explain the retest pass. General preferences do not reopen M5. E2 waits until every task is passed and no material failure remains.
- Any NOT_RUN or untraceable observation: evidence incomplete. Complete only the missing observation, without repeating accepted general UI checks.
- If the prompt itself is ambiguous, record a protocol revision and keep pre/post-revision results separate; never rewrite criteria to turn a failure into success.

Stop E1 analysis after one completed session and a short evidence readout. Follow the owner's E1 → E2 sequence below; do not reread the architecture, add sources/layers, reopen #334 or widen infrastructure by default.

## E2 and Gate E decision — owner-directed sequence

After E1 passes, compare ARTEMIS with a linear baseline using **3–5 formative users**. The baseline must contain the same 11 Presences, six periods, sources/locators and uncertainty/coverage information; it must not be a deliberately weakened summary. Freeze both versions, task prompts, answer rubric and value-signal rule before E2 collection. Use equivalent content-understanding questions in both conditions rather than scoring interface-specific actions such as operating Scrub against a document. Alternate condition order as evenly as possible and record learning/order effects; report a returning E1 participant separately.

Compare correct reconstruction of chronology/time overlap, retrieval of supporting evidence, recognition of uncertainty and critical trust errors. Record assistance and effort/time descriptively; preference alone is not a value signal. Report per-user paired results and absolute counts, including ties and failures. Three to five users provide a formative signal, not statistical generalization. The exact baseline artifact and predeclared decision thresholds are E2 preparation deliverables, not completed by this PR.

The Gate E decision must explicitly classify the observed result as a **value signal** or **no value signal**, with supporting observations and limitations. Missing or inconclusive evidence must be labelled as such rather than forced into either result. This is not M4 `ADOPT` or a reuse of the Gate D exit vocabulary.

- Value signal: next is a bounded universality proof, using a second geometry type — **Roman Empire / temporal Region**. Write its concrete scope and source/uncertainty criteria after the Gate E decision; no Region implementation or data expansion is opened now. One second-geometry proof tests transferability, not universal validity.
- No value signal: rethink the current product proposition using the observed failure; do not automatically expand to Roman Empire or reopen the entire foundation architecture.

Current authorization is tiny protocol fixes and merge #415, then E1. E2 is conditional on E1; the Region proof is conditional on a positive Gate E value decision. No E1/E2 results are inferred from owner acceptance or CI.

## Initial evidence ledger

| Evidence | Status | What it supports |
|---|---|---|
| Earlier #412 publication and owner acceptance, closed by #413 | Completed; see accepted closeout review | Bounded UX correction acceptance |
| Owner report on 2026-09-06 quoted above | No findings reported; execution details not supplied | Additional owner acceptance only |
| T1–T5 structured observations | NOT COLLECTED | No task-comprehension conclusion yet |
| E1 independent novice session | NOT RUN | Required before E2; owner acceptance is not a substitute |
| E2 same-content comparison, 3–5 formative users | NOT RUN / conditional on E1 | No comparative value claim yet |
| Roman Empire / Region universality proof | NOT OPEN / conditional on positive Gate E value signal | No new geometry implementation authorized now |

References: [Gate D exit](2026-09-06_GATE_D_EXIT_DECISION_v1.md), [accepted bounded review](2026-09-06_M5_UX_CLOSEOUT_AND_GATE_D_REVIEW_v1.md), [current validation decision](../VALIDATION_DECISION.md).
