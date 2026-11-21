# ARTEMIS — Amboise comprehension: seven-day diagnostic experiment v1

- **Owner request:** 2026-11-19, start one bounded engineering/research experiment, inspect the current repository, distinguish verified behavior from hypotheses, implement the smallest useful next step.
- **Window:** 2026-11-19 through 2026-11-25 inclusive. This is a review deadline, not an assumption that human research has occurred.
- **Class:** DECISION (owner-authorized research activation); any later user-facing correction is separately scoped REVIEW.
- **Status at creation:** `AUTHORIZED_RESEARCH_PREPARATION / SESSION_NOT_RUN / OBSERVATIONS_NOT_COLLECTED`.
- **Owner of this task:** this file; canonical product/gate state remains `docs/project_state.json`.
- **Source snapshot inspected:** `main@c50e0aca260b84f5b89e71a3e6327fe6aa248b4e` (2026-11-19). This is *repository evidence*, not proof of the currently loaded public Pages build.

## Decision and reason

**Question:** Can an independent first-time reader of the existing Explorer, using its current Amboise case, explain that Leonardo's residence and the 1518 baptism share a broad temporal/spatial context *without* inferring attendance, causality, exact canonical day, continuous physical presence, or a year-long event?

**Observed repository facts:** (a) the bounded Amboise context is already implemented; the accepted package attaches one source-relative 1518 event to the existing Clos Lucé residence; (b) its 1518 Scrub/Range behavior is checked in `tests/amboise_context_behavior.cjs` and `tests/test_amboise_context.py`; (c) recent PRs #489–#492 improve chronology, disclosures, inspector readability and WebGL fallback; (d) `project_state.json` still records user value as `unvalidated`, contextual composition historically `deferred` and `STOP` for new product branches; (e) `docs/work/amboise_comprehension_v1/` already contains five tasks, a moderator rubric and an empty session form.

**Hypotheses, not findings:** a novice might overlook the contextual section; might equate residence/overlap with participation; might mistake a calendar interpretation for an established exact date; might infer event absence when a year is filtered out. The code and the owner's prior review do not determine the frequency or even existence of these errors in independent users.

**Chosen minimal improvement:** activate and make executable the **existing** five-task diagnostic (one session, frozen rubric, recorded actual build, unassisted/assisted separation). No new UI, ontology, data, source, generic Event engine or second study protocol is justified before actual observation. This is a research-process improvement; it is **not yet a user-facing fix**.

## Frozen instrument and starting context

- Participant tasks: [participant_tasks.md](amboise_comprehension_v1/participant_tasks.md).
- Moderator reference and preregistered rubric: [observer_reference.md](amboise_comprehension_v1/observer_reference.md) — never show before first responses.
- Session fields: [session_template.json](amboise_comprehension_v1/session_template.json) — template only; do not commit participant raw notes.
- Procedure: [protocol README](amboise_comprehension_v1/README.md).
- Instrument version pinned to repository commit `c50e0aca260b84f5b89e71a3e6327fe6aa248b4e`; do not edit the questions or PASS rubric after seeing observations.
- Participant starting URL: https://omegapunctum.github.io/ARTEMIS/globe/?mode=scrub&at=1518&presence=presence-leonardo-amboise-clos-luce-1516-1519&lang=ru&view=map
- Required *actual-build* preflight: read https://omegapunctum.github.io/ARTEMIS/globe/build-meta.json in participant's browser, record the loaded revision and confirm the Amboise section under the selected residence before beginning. The assistant's current environment could not access this live metadata; **LIVE PREFLIGHT NOT VERIFIED**. Historical Pages #40465572963 is not assumed to be the currently loaded release.

## Operational seven-day sequence

| Day | Date | Bounded action / stop |
|---|---|---|
| 1 | 19 Nov | Repository and owner audit; pin existing instrument; open reviewable activation record; no fabricated observation. |
| 2 | 20 Nov | Check the actual live build and reproducible start URL on the observer's device; if not verifiable, mark `PREFLIGHT_BLOCKED`. |
| 3 | 21 Nov | **Only if** build confirmed and voluntary consent obtained, one independent novice completes T1–T5; preserve the verbatim, anonymized task record outside public GitHub. |
| 4 | 22 Nov | Separate task outcomes from interpretations; label any navigation, comprehension, evidence or protocol finding; do not infer population-wide effect from n=1. |
| 5 | 23 Nov | Select at most one observed, high-impact, reproducible problem for a minimal proposed UI fix; no fix if no supporting observation. |
| 6 | 24 Nov | If separately authorized, implement/test one bounded fix with exact-head checks and independent REVIEW; otherwise record why no code changed. |
| 7 | 25 Nov | Report evidence, uncertainties, cost, single next decision and stop. No automatic release, gate transition or larger context intake. |

This order is conditional, not a claim of autonomous user recruitment or actual daily completion. A missing participant by day 7 yields `INSUFFICIENT_USER_EVIDENCE`, not `PASS`.

## Precommitted acceptance criteria

- **Readiness:** identified consented independent adult novice; verified device/browser/viewport; loaded public build identity and working 1518 context; frozen pre-task instrument. Failure of any prerequisite means `NOT_RUN`, not a zero or PASS.
- **Diagnostic task success:** T1–T5 all `PASS` **without** prompt/help contamination; zero critical trust errors. Each task may instead be `ASSISTED`, `FAIL` or `NOT_RUN` according to the frozen rubric.
- **Critical trust errors:** assert proven Leonardo participation/encounter/causation from proximity, continuous presence from residence, a resolved exact calendar day, year-long duration from year membership, or historical absence from missing UI content.
- **Interpretation:** even if one participant passes every task, that establishes only a single diagnostic success, **not** formally validated user value, population performance or superiority of Globe over a text baseline.
- **Engineering exit:** at most one observed issue selected; smallest valid correction only after issue-specific evidence; relevant code/unit/native checks and independent exact-head REVIEW if applicable; report unverified checks explicitly.
- **No evidence:** close `NOT_COLLECTED/INSUFFICIENT_USER_EVIDENCE` and leave the runtime alone. Never replace a person with an AI-simulated test subject.

## Non-goals and preservation

Preserve Entity/Event/State/Process/Trajectory/Region/Relation and Claim/Evidence/Uncertainty semantics; computed temporal overlap must not become a historical Relation. Do not change `docs/project_state.json`, archived Gate E outcome, frozen packages, historical data, source qualifiers, rights, geometry, or public reader behavior in this activation PR. The September contextual-composition `DEFERRED` decision and formal/comparative `UNVALIDATED` status stay unchanged. No production mutation, participant outreach, recording or new deployment is implied by this research decision.

**Stop condition:** one evidence-backed user-comprehension diagnosis (or explicitly insufficient evidence) and one next-step recommendation on or before 2026-11-25.
