# Gate E — evidence recovery decision/specification v1

- Date: 2026-09-19.
- Status: **ACCEPTED / current Gate E execution authority**.
- Owner: issue #355.
- Authority: explicit owner instruction on 2026-09-19.
- Basis: [2026-09-06 Gate E bounded task/evidence protocol v1](2026-09-06_GATE_E_BOUNDED_TASK_PROTOCOL_v1.md).
- Supersedes for current execution only: the 2026-09-10 owner-directed E1/E2 bypass. That bypass remains historical truth and still explains why the Region proof was executed without participant evidence.
- Product scope: the existing published Leonardo Temporal Map only. This decision adds an evidence-recovery runway; it does not add a product capability, historical claim, source, geometry, relation, backend dependency or new interaction semantic.

## 1. Decision

Gate E participant evidence is reopened as one continuous, pre-authorized runway:

`E1 → (if required: one bounded correction + focused retest) → E2 with exactly 5 participants → final Gate E outcome`.

Once this specification is merged, no further Command Center decision is required to:

1. conduct E1;
2. record E1 evidence;
3. perform the single bounded correction/retest branch allowed below;
4. prepare and freeze the E2 linear baseline and comparison protocol;
5. conduct E2 with exactly five formative participants;
6. assemble the Gate E evidence package.

Execution stops for Command Center only when an escalation condition in this specification or `docs/DEVELOPMENT_OPERATING_SYSTEM.md` is met, or after E2 evidence is complete and the final Gate E outcome must be recorded.

The final Gate E outcome remains a human `DECISION`. This specification does not predetermine it and does not open any automatic successor product branch.

## 2. Question

Can a novice use the current ARTEMIS Temporal Map to reconstruct the displayed chronology, narrow it in time, inspect supporting evidence and uncertainty, and avoid converting presentation chronology or missing coverage into unsupported historical claims?

Gate E tests evidence of user value in this bounded contour. It is not market validation, statistical generalization, or proof that ARTEMIS is a complete historical product.

## 3. Frozen product and evidence boundary

The evaluated ARTEMIS condition is the current accepted Leonardo interaction baseline:

- 11 distinct Presence episodes at 9 canonical Place anchors;
- six coarse periods across 1452–1519;
- `Range` = bounded calendar interval using temporal overlap;
- `Scrub` = accumulation from the earliest/default origin to a current-time cursor;
- popup-first selection; optional details; no single-click camera move;
- map, timeline, selection and URL share one state;
- chronology connectors are presentation-only;
- unknown historical routes remain unknown/null;
- present-day source-bound place anchors are not exact historical positions;
- provenance, source locator, coverage limits and uncertainty remain inspectable.

Before each evidence phase, record the tested public URL, UTC time, language, device/browser and available deployment identity. If exact deployed revision cannot be established, record it as unknown rather than infer it.

Do not combine participant observations across materially different product revisions. The only product change permitted inside this runway before E2 is the single bounded E1 correction branch defined in section 6.

Existing owner acceptance, Region review, CI, browser automation and agent review do not substitute for E1 or E2 participant evidence.

## 4. E1 — one independent novice

E1 uses **one consenting independent novice** who is unfamiliar with the implementation and has not been coached on the answer key. The owner or an agent cannot substitute for the participant.

Read only the participant prompts. Observer criteria are hidden until the participant has attempted the task unaided.

| ID | Participant prompt | Observer evidence and success criterion |
|---|---|---|
| T1 | Describe the beginning, a middle phase and the end of the life sequence shown here. Is this a complete biography? | Identifies displayed places/periods in chronological order and recognizes sparse, incomplete coverage. Do not require outside historical knowledge. |
| T2 | Show only the part of the life overlapping 1502–1504. Explain what changed and what the interval does not tell you. | Uses Range; visible Presences reflect temporal overlap. Does not claim a precise day, continuous residence or historical absence from omitted points. Capture resulting state/URL and explanation. |
| T3 | Starting from 1452, show how the sequence accumulates up to 1504. Explain how this differs from your previous view. | Uses Scrub with origin 1452 and cursor 1504; distinguishes accumulated history from the bounded Range interval. Selection/time remain coherent. Capture resulting state/URL. |
| T4 | Choose one displayed Presence. Find the information supporting it and tell me what remains uncertain. | Opens supporting details; identifies an actual source/locator shown for the selected record; separates the historical assertion from the present-day reference location; states a relevant uncertainty/limit. Record selected ID and participant wording. |
| T5 | What can you conclude from the lines between points? Save or reopen this view so that you can explain the same selection and time later. | Explicitly distinguishes chronology links from documented travel routes and does not infer encounter, influence or causality. Restored state retains supported time/mode/selection. Capture before/after state and explanation. |

### E1 record

For every task retain:

- task ID;
- unaided action/answer;
- resulting URL/state or selected record ID;
- `PASS / ASSISTED / FAIL / NOT_RUN`;
- assistance given;
- observed problem;
- optional elapsed time.

`PASS` requires the observable criterion without help. `ASSISTED` is not PASS. `NOT_RUN` is incomplete evidence, not failure. Keep verbatim observation separate from interpretation.

Critical trust errors are:

- chronology presented as a documented route;
- invented source-supported temporal or spatial precision;
- completeness or historical absence inferred from missing coverage;
- proximity converted into a documented relation, encounter, influence or causality.

Lost shared state or inaccessible material provenance is a material task blocker.

### E1 pass condition

E1 clears when all five tasks are `PASS` unaided and there are zero critical trust errors.

A cleared E1 automatically opens E2 preparation under this same specification.

## 5. Evidence-completeness and protocol branch

These branches do not require a new Command Center decision:

- `NOT_RUN` or untraceable evidence: collect only the missing observation.
- Observer recording error that does not change the participant experience: repair the evidence record transparently; do not fabricate missing behavior.
- Prompt ambiguity: a clarification is permitted only when it does not lower, broaden or materially change the success criterion. Preserve pre- and post-clarification wording/results separately and rerun only the affected task with a fresh novice when learning could explain success.

Escalate instead of silently revising the protocol when a proposed clarification would change what the task means, change the pass bar, alter accepted product semantics or materially change the comparison question.

## 6. Single bounded E1 correction/retest branch

If E1 produces any `ASSISTED`, `FAIL` or critical trust error attributable to a demonstrated product interaction/comprehension/evidence-access problem, **one bounded correction cycle** is authorized without another Command Center decision.

The correction may address multiple findings from the same E1 session only when they fit one coherent bounded cause. It must:

- preserve the accepted temporal/spatial/domain semantics;
- preserve Place/Presence identity, uncertainty/provenance and unknown-route rules;
- add no new historical data, coordinates, routes, Relations, source claims or backend dependency;
- avoid unrelated visual redesign or feature expansion;
- remain the minimum change required to remove the demonstrated blocker;
- be implemented and verified under `docs/DEVELOPMENT_OPERATING_SYSTEM.md`.

Retest only the failed/assisted task(s) plus directly affected regression behavior. Preserve first-attempt and retest evidence separately.

Where prior assistance or exposure could explain a pass, the focused retest must use a fresh novice for that task.

### Correction branch exit

- If every affected task passes unaided after the bounded correction, no critical trust error remains, and regression checks are clean: E1 is cleared and E2 preparation opens automatically.
- If any affected task remains `ASSISTED`/`FAIL`, a critical trust error remains, or a second material product correction would be required: **stop and escalate**. Do not begin E2.
- Preferences or cosmetic observations that do not block the task and do not create a trust error are recorded but do not open a correction branch.

## 7. E2 preparation — same-content linear baseline

After E1 clears, prepare one bounded linear baseline as an **evaluation artifact**, not a new ARTEMIS product surface.

The baseline must contain the same material content available for the comparison questions:

- the same 11 Presence episodes;
- the same six periods;
- the same source/locator information needed by the tasks;
- the same material uncertainty and coverage limitations;
- the same explicit route/causality limits.

It must not deliberately weaken content, hide uncertainty, omit provenance required by the tasks, or add knowledge unavailable in ARTEMIS.

Before the first E2 participant, freeze and record:

1. ARTEMIS tested revision/URL;
2. baseline artifact revision/hash;
3. participant prompts and hidden rubric;
4. condition order plan;
5. the scoring and value-signal rule below.

No material product or baseline-content change is permitted after E2 collection begins. A technical evidence-harness defect may be repaired only if it does not change either compared experience; invalidate and rerun only affected participant records. Any product/baseline content change required after collection starts is an escalation because paired comparability has been broken.

## 8. E2 — exactly five formative participants

E2 requires **exactly 5 completed participant records**.

Each participant uses both ARTEMIS and the linear baseline. Alternate order as evenly as possible across five participants (3/2). Record actual order and any learning/order effect. If the E1 participant returns, mark that record explicitly and report it separately in the limitations; do not hide prior exposure.

Do not coach participants on interface operation or expected conclusions before unaided attempts.

Use equivalent, interface-neutral comparison tasks:

| ID | Comparison task | PASS criterion in either condition |
|---|---|---|
| C1 | Reconstruct the beginning, a middle phase and the end of the displayed chronology, and state whether coverage is complete. | Correct displayed sequence plus explicit recognition that coverage is incomplete. |
| C2 | Determine what is shown for 1502–1504 and explain what that interval does and does not establish. | Correct temporal-overlap interpretation; no exact-day, continuous-residence or absence invention. |
| C3 | Find support for one displayed Presence and explain a material uncertainty/limit. | Identifies available source/locator evidence and a relevant uncertainty/coverage limit. |
| C4 | Explain what can and cannot be inferred about movement or relationship between successive displayed Presences. | Does not convert chronology/proximity into documented route, encounter, influence or causality. |

For each participant and condition, record each task as `PASS / ASSISTED / FAIL / NOT_RUN`, assistance, critical trust errors and optional effort/time. Time and preference are descriptive only and cannot override correctness/trust evidence.

## 9. Predeclared E2 comparison rule

For each participant:

1. If exactly one condition produces a critical trust error, that condition is worse for the paired result regardless of task count.
2. Otherwise compare the number of unaided `PASS` results across C1–C4.
3. Classify the pair as `ARTEMIS_BETTER`, `BASELINE_BETTER` or `TIE`.

After five valid participant records, classify the **evidence pattern**:

- `VALUE_SIGNAL_CANDIDATE`: at least 3/5 are `ARTEMIS_BETTER`, no more than 1/5 is `BASELINE_BETTER`, and there are zero ARTEMIS-only critical trust errors.
- `NO_VALUE_SIGNAL_CANDIDATE`: at least 3/5 are `BASELINE_BETTER`, or ARTEMIS-only critical trust errors occur in at least 2/5 participants.
- `INCONCLUSIVE`: every other result.

These are formative directional rules, not statistical significance thresholds. Report absolute task counts, paired participant results, ties, assistance, order effects and limitations. Preference alone is not a value signal.

## 10. E2 branch rule and stopping condition

Once E2 collection begins, **do not open a product correction branch mid-study**. Preserve the frozen comparison.

Continue automatically until exactly five valid participant records exist unless:

- a real escalation condition occurs;
- a material product/baseline change becomes necessary;
- evidence integrity cannot be restored without changing the frozen comparison.

After five valid records, freeze the E2 evidence package and return to Command Center for the final Gate E outcome.

No additional participant wave, product iteration, Region work, new feature branch or universality branch opens automatically from this specification.

## 11. Final Gate E outcome

The final Gate E outcome is a human `DECISION` recorded after E2. Allowed outcome labels are:

- `VALUE_SIGNAL`;
- `NO_VALUE_SIGNAL`;
- `INCONCLUSIVE`.

The E2 evidence-pattern classification informs but does not replace this final decision. The decision record must state the observed pattern, limitations, any trust errors, and the single next action or stop condition.

The already-completed Roman Empire / Temporal Region proof remains **technical generalization evidence only**. It does not retroactively count as a positive Gate E value signal and is not an automatic successor after recovery.

## 12. Non-goals

This specification does not authorize:

- new historical research or source expansion;
- new Presence data;
- exact historical coordinates or routes;
- new Relation semantics;
- Global/Focus implementation;
- backend/Airtable historical writes;
- design-system/token/Figma work;
- new public capability or product-readiness claims;
- reinterpretation of completed Region evidence;
- treating E1/E2 as statistical or market validation.

## 13. Completion criteria for this decision

This decision/specification is complete when GitHub records it as the current Gate E execution authority and current-state owners point to it.

At that point:

- E1 may be conducted without another Command Center decision;
- the single bounded E1 correction/retest branch may execute if triggered;
- E2 preparation and exactly five-participant collection may proceed automatically after E1 clearance;
- the only planned human decision point is the final Gate E outcome;
- genuine escalation still stops execution under the governing operating system.

Until participant observations are actually collected, `E1 = NOT COLLECTED`, `E2 = NOT COLLECTED` and formal user value remains `UNVALIDATED`.
