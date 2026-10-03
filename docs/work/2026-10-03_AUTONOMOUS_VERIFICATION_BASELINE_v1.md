# Autonomous Verification Baseline v1

Type: bounded engineering verification specification and owner-delegation record.
Authority: owner requested fully AI development and subagent tasks on 2026-10-02;
owner instructed execution to begin on 2026-10-03. Lifecycle: `docs/work/README.md`.
Operational policy: `docs/DEVELOPMENT_OPERATING_SYSTEM.md` v1.9.

## Decision and scope

Open `AUTONOMOUS_VERIFICATION_BASELINE_V1` as engineering maintenance of existing
accepted artifacts. It is not a new product gate, historical case or public capability.
Preferred action: close reproducible interaction and release-provenance gaps before
the next Leonardo research task. Repeating isolated semantic proofs or expanding
the corpus does not close those gaps and is deferred.

1. Synchronize the current #355 header and registered runtime entrypoints.
2. Execute the existing ATL proof in a real browser: both dating attributions,
   reversible focus, source/locator disclosure, URL restoration, keyboard operation,
   narrow viewport, unavailable payload and a deliberately broken acceptance case.
3. Bind public build metadata and file hashes to source revision and workflow identity;
   reject revision/hash mismatch and validate the deployed artifact separately.
4. Obtain independent AI review of the current commit, tests and browser evidence;
   merge only with relevant green checks and no material findings.

No change to the accepted ATL evidence blob, native dating expressions, historical
winner, query envelopes, Range/Scrub, geometry, sources or public ATL availability.
Existing Gate E, contextual composition and frozen Gate C dispositions remain intact.
This maintenance baseline does not change the product lifecycle snapshot; #355 is
the same umbrella, and the completed conflict proof remains completed.

## Assignment and acceptance

| Agent | Responsibility | Acceptance |
|---|---|---|
| Orchestrator | policy/current-owner sync and integration | correct owners, relevant governance checks, explicit scope |
| Engineering subagent | ATL browser regression + Core integration | real interactions, fail-closed assertions, durable JSON/screenshots |
| Release engineer | revision/run identity + artifact hash verification | mismatch rejected; checked and live artifacts compared |
| Independent architecture reviewer | delegation, boundaries and final diff | distinct reviewer instance, exact commit verdict, zero material findings |
| Product/evidence subagent | prepare the later Leonardo task contract | existing Claims/locators and uncertainty only; preparation opens no runtime scope |

Browser evidence must name the tested commit and preserve runtime errors and measured
viewport. Successful agents/tests establish technical behavior only. Previous human
acceptance is preserved; neither new AI review nor release availability establishes
comparative/formal user value.

## Stop and next action

Close as `TECHNICAL_PASS` only after the scoped checks, independent review and relevant
release evidence succeed. A missing credential, unavailable required browser/source,
protection failure or unresolved material finding is `BLOCKED`, not PASS.
After two failed correction cycles for the same material finding, narrow only within
the accepted contract; otherwise record BLOCKED. Never remove required acceptance
checks to obtain PASS.

After closure, record one independently reviewed `SOURCE_AWARE_RESEARCH_LOOP_V1`
specification over existing Leonardo data before its implementation. No automatic
new corpus, source write, renderer, backend, agent product feature or background
scheduler is authorized. Local/PR checks may be completed separately, but the overall
baseline remains pending or BLOCKED until required live release verification exists.

## Technical closeout — 2026-10-03

Disposition: **TECHNICAL_PASS** for this engineering maintenance baseline.

- Implementation: PR #457, reviewed head `3c52af04becfdfade63464ee46ac53b3880008ae`,
  merged `b0b16223fe519bdd702df020576a97df876061c6`.
- Independent reviewer: distinct agent `/root/architecture_audit`; no unresolved
  material findings. Durable exact-head review: PR review `5398979164`.
- PR Core run [37096247978](https://github.com/omegapunctum/ARTEMIS/actions/runs/37096247978):
  354 tests and six Chromium interaction/failure/negative-control scenarios PASS;
  zero page errors; measured widths 1280/375; clean source tree. Browser checkout
  is the PR merge candidate `cc4751b9876eafa20d9f9e485d4862cb9ba3e21e`, not a deployment claim.
- Boundary [37096247853](https://github.com/omegapunctum/ARTEMIS/actions/runs/37096247853)
  and Geospatial [37096247727](https://github.com/omegapunctum/ARTEMIS/actions/runs/37096247727): PASS.
- Merge Core run [37096385989](https://github.com/omegapunctum/ARTEMIS/actions/runs/37096385989): PASS.
- Pages [37096385991](https://github.com/omegapunctum/ARTEMIS/actions/runs/37096385991): SUCCESS
  on `b0b16223fe519bdd702df020576a97df876061c6`. Live verification compared
  metadata and every manifest-listed file against the checked artifact:
  `/ARTEMIS/globe/` — 16 files PASS; `/ARTEMIS/region/` — 20 files PASS.
  Both release records name that source commit, run identity and attempt 1.
- The same Pages run passed the existing live Region provenance/license disclosure,
  explicit approximate-reconstruction disclosure and three-snapshot switching retest.
- #355 current header/title synchronized; superseded handoff retained as history.

External ATL source activation was intercepted locally; source reachability or new
historical review is not asserted. Prior human acceptance, accepted evidence blob,
non-public ATL, Gate E closeout and contextual DEFERRED remain preserved.
Comparative/formal value remains UNVALIDATED. No new product gate or feature is open.

Next authorized preparation: one independently reviewed source-aware Leonardo task
specification using existing records and locators. Implementation starts only after
that specification is recorded in its proper owner; this closeout does not create
an automatic feature branch.
