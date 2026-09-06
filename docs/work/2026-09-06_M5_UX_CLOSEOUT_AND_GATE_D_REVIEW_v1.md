# M5 UX closeout and bounded Gate D review

Later decision: this review was accepted in merged PR #413. Its recommendation is finalized by [the explicit Gate D exit](2026-09-06_GATE_D_EXIT_DECISION_v1.md). Exit-pending wording below records the review-stage state, not current execution.

## Decision

- Date recorded: 2026-09-06.
- Owner issue: #355.
- M5 bounded UX correction: **COMPLETED / PROCEED_TO_GATE_D_REVIEW**.
- #409 scope, #411 implementation and #412 follow-up: completed evidence, not active execution.
- #412: merged, published and **manually accepted by the owner**, as reported/authorized in the 2026-09-06 closeout instruction.
- Provenance: owner acceptance in the working conversation. No new assistant-performed browser session, physical-device test, task rubric or paired EN/RU screenshots are claimed. The acceptance report and automated evidence below are separate.
- Runtime, historical fixtures, sources, schema of historical knowledge and deployment code: unchanged by this decision.

Historical #408 and post-#411 `ITERATE` results remain valid records of their earlier checks. This later result closes the correction; it does not rewrite them or prove formal user value.

## Verified identities and maintenance

| Evidence | Identity / verified result |
| --- | --- |
| #409 | Merged scope decision; superseded for active execution by this closeout |
| #411 | Merged as `f1d54af5d3aa34229867f5b00aceaa138bd300aa`; first published UX package |
| #412 | Merged as `d100f2cb09d743c31184c4a4b33b32258678b929`; accepted published correction |
| Published artifact | [Pages run 33978249223](https://github.com/omegapunctum/ARTEMIS/actions/runs/33978249223), success on #412 merge |
| Public surface | [Leonardo Temporal Map](https://omegapunctum.github.io/ARTEMIS/globe/?v=d100f2c) |
| Exact published-commit Core | [33978249224](https://github.com/omegapunctum/ARTEMIS/actions/runs/33978249224), success; includes renderer parity regression modules |
| Exact published-commit boundaries | [Globe 33978249226](https://github.com/omegapunctum/ARTEMIS/actions/runs/33978249226), [Geospatial 33978249202](https://github.com/omegapunctum/ARTEMIS/actions/runs/33978249202), success |
| Hosted browser | [33978249204](https://github.com/omegapunctum/ARTEMIS/actions/runs/33978249204), success on published merge; reviewed PR-head [33978156210](https://github.com/omegapunctum/ARTEMIS/actions/runs/33978156210) measured dock 125/135/149 CSS px at desktop/tablet/hosted-mobile, 10 full-life links, no measured overlay collisions or horizontal overflow |
| #410 repair | Merged as `5591fcfbf8308708dc1a3eaa07a7d53796c38c50`; scheduled Export Airtable success verified in [33971160330](https://github.com/omegapunctum/ARTEMIS/actions/runs/33971160330), [33987911592](https://github.com/omegapunctum/ARTEMIS/actions/runs/33987911592), and [34005145312](https://github.com/omegapunctum/ARTEMIS/actions/runs/34005145312) on 2026-09-06 at `102ea0a9b0ca96cd8356956f5313055efde9021e` |

The current review base is a descendant of #412 whose intervening commits change only `data/export_meta.json`. No runtime delta invalidates the cited published-build evidence. The #410 result confirms the scheduled repair; it is not authorization for historical Airtable writes.

## Vocabulary repair

The [Gate D opening contract](2026-08-12_GATE_D_OPENING_v1.md), section 8, remains authoritative:

- `ADVANCE_TO_GATE_E` — ready for task-based evidence collection;
- `NARROW` — reduce the bounded scope and continue Gate D;
- `REJECT` — stop the current approach with reasons.

M4 `ADOPT / NARROW / REJECT` belongs only to the completed [M4 architecture decision](2026-09-01_TEMPORAL_MAP_M4_ARCHITECTURE_DECISION_v1.md). Move its recorded `ADOPT` out of the Gate D field into a separate architecture checkpoint. The M5 correction uses `PROCEED_TO_GATE_D_REVIEW / ITERATE / NARROW / STOP`. None of these checkpoint outcomes is a Gate D exit.

This PR restores the original Gate D meaning; it does not supersede Gate D or record its final exit. Gate D stays `in_progress`, with no `gate.decision`, while the evidence-review recommendation is explicit below.

## One bounded evidence review

Scope: only the twelve requirements and exit evidence of the Gate D opening contract, interpreted through the already adopted narrowing in `ARTEMIS_PRODUCT_SCOPE.md` §§1, 3–5 and the Temporal Map interaction contract. No foundation/architecture re-review was performed.

| Gate D requirement | Classification | Evidence / disposition |
| --- | --- | --- |
| 1. One shared instant/interval | satisfied | Range/Scrub and URL restoration checks in #412 Core/hosted gates; shared Explorer State retained |
| 2. Synchronized layers and time | superseded by later narrowing | Product Scope §§1, 4 and Temporal Map contract §4 make thematic layer controls non-primary; shared temporal filtering is satisfied; do not reopen layer UI |
| 3. Canonical picking | satisfied | Presence/event identity, map/sequence selection and URL restoration regressions |
| 4. Event/State/Process/Trajectory/Region UI breadth | superseded by later narrowing | Product Scope §§3, 5 explicitly permits the first Presence/Trajectory loop without exposing every type; underlying reviewed projection/parity evidence retained |
| 5. Unresolved routes and withheld geometry | satisfied | Historical `unknown_route`/null geometry guards pass; #412 dashed links are explicitly chronological presentation, not travel evidence; no historical Region polygon promotion |
| 6. Sources, locators, evidence state and uncertainty | satisfied | Frozen reviewed source packages, knowledge-inspector implementation and source/projection regression checks; acceptance is for the bounded prototype, not source truth promotion |
| 7. Coverage, gaps and projection losses | satisfied | Source/uncertainty/coverage disclosure retained; whole-life coverage explicitly coarse, incomplete and R&D; no complete-biography claim |
| 8. Local plus global simultaneity | superseded by later narrowing | Product Scope §§1, 3 excludes local/global/context hypotheses from this initial loop; broader contextual-value tasks are not prerequisites for it |
| 9. Earth provider/attribution policy | satisfied | Pinned Natural Earth policy, Geospatial gate and visible attribution; present-day anchors/context remain distinct from historical precision |
| 10. Executable 2D/Globe parity | satisfied | Accepted #344/#351 foundation; exact published-commit Core includes `test_renderer_parity.py` and `test_render_projection_contract.py`; no claim that Atlas is a same-content user-study baseline |
| 11a. Basic responsive, focus, keyboard, reduced-motion and diagnostic performance evidence | satisfied | #411/#412 executed behavior checks plus hosted profiles; owner acceptance of published loop; limited evidence, not WCAG/device certification or production SLO |
| 11b. Mandatory D1/M1/A1/P1 physical matrix, exact 390 px and six P1 timings before any next product step | superseded by later narrowing | At this PR base the authoritative work registry already labels the protocol **paused historical closeout**; DOS §9 and Project Truth explicitly remove it from current roadmap drivers. This review reconciles that existing disposition; it does not claim those runs passed. Revisit specific environments if the next task-based cohort needs them or a concrete defect appears |
| 12. Reproducible generated artifact | satisfied | Successful Pages/Core/Globe build on exact #412 merge; static read-only delivery and rollback via Git preserved |

No **still material** implementation defect was identified in this bounded evidence review. This means no demonstrated blocker for the currently narrowed loop, not proof that no defects exist.

### Exit-evidence cross-check

| Exit requirement | Classification | Basis |
| --- | --- | --- |
| Bounded experience exists and is reproducible | satisfied | #412 merge, Pages run and owner acceptance |
| Relevant release/boundary/geospatial/parity green | satisfied | Exact published-commit runs above; this governance PR must also pass its owned checks |
| No critical semantic loss or invented precision | satisfied | Frozen data boundaries and passing semantic negative tests; no new knowledge or runtime change in this PR |
| Known UX/accessibility/performance gaps and implementation cost recorded | satisfied | Two UX PRs, follow-up rationale, review/test evidence and named limitations below; human implementation hours were not measured and are not invented |
| Truthful R&D/candidate capability wording | satisfied | Public prototype label; owner acceptance is not formal user-value or historical-content validation |
| #355 and machine state agree on final Gate D exit | still material | Final Gate D decision is deliberately not made by this M5-closeout PR. After its review/merge, record one exit consistently before opening Gate E |

Unmeasured limitations retained: physical 390 px touch, real screen-reader behavior, normal-device performance distributions, independent paired EN/RU screenshot review, repeated-visit visual overlap, and formal same-content/participant outcomes. They are not fabricated passes. A reproducible keyboard/AT access failure, lost state, misleading route meaning or severe performance defect immediately reopens a bounded material finding.

## Recommendation and stop condition

Recommendation from this completed bounded review: **`ADVANCE_TO_GATE_E`**, conditional on acceptance of this closeout and a subsequent explicit Gate D exit record synchronized with #355. The only still-material closeout item is that decision synchronization; no implementation branch is opened.

Gate E means scoped task-based evidence collection, not proven product value, deployment permission, broad participant-wave activation or new runtime capability. Do not automatically reactivate the old context/layer-heavy participant protocol; map tasks to the accepted current loop before recruiting or collecting data.

Stop further architecture analysis here. Next action after this decision PR: record the Gate D exit using the restored vocabulary, or identify one concrete material gap with evidence. Do not launch another UX/data/backend branch merely because an old checklist contains a broader feature.
