# Explorer example navigation v1

- Status: completed bounded navigation maintenance; specification and prospective source-access amendment independently AI-accepted before their runtime edits. Exact-head implementation review and separate live publication verification are recorded below.
- Date: 2026-10-04.
- Authority: the owner's explicit **«Начинай»** in response to the recommended next step of common Leonardo ↔ Region navigation. This specific instruction opens this navigation task; the earlier [Unified Explorer advisory](2026-10-04_UNIFIED_EXPLORER_ADVISORY_v1.md) alone did not authorize implementation.
- Classification: explicit owner decision; subsequent implementation is `REVIEW` under current [Development Operating System](../DEVELOPMENT_OPERATING_SYSTEM.md). Independent specification acceptance must precede runtime edits; independent implementation review must inspect the exact PR revision and relevant browser evidence before merge.
- Baseline: merged advisory/research PR #462, main `ea7a4bf` (orchestrator-supplied baseline), matching inspected repository content. Current truth and product/gate dispositions remain owned by `PROJECT_TRUTH.md`, `project_state.json` and the work registry.

## Question, choice and boundaries

Can someone move between the two existing public research examples, understand which example and time coverage they are viewing, and retain access to sources without confusing navigation with combining historical datasets?

Preferred action: add a compact common navigation area to the existing shared preview header, using native links between the existing Leonardo and Roman Empire routes. Identify the active example and its bounded coverage. Retain the clearly labelled Architecture Atlas compatibility link. Reuse the current template, build dispatch, styling and localization rather than introduce an application framework, router or new landing screen.

Alternatives considered: leaving the previews disconnected preserves needless navigation friction; merging their datasets would introduce unrelated periods and additional temporal/source semantics; importing Atlas would require an independently authorized mapping proof. Neither data composition nor Atlas intake is needed for this navigation question.

This is navigation maintenance inside the existing public R&D surfaces, not implementation of the full unified Explorer target. No new product gate, user-value result or historical capability is established. Gate E remains closed without VALUE_SIGNAL, contextual composition DEFERRED and conflict proof non-public; formal/comparative value remains UNVALIDATED. Preserve the separately recorded Cesena wording-scope finding and all historical statuses. This task neither resolves that finding nor reopens its frozen package.

## Interaction and routing contract

1. On each public Leonardo/Region page, show both example names together and unambiguously identify the current one. Use a labelled `nav`; the current example may be non-link text with `aria-current="page"`, while the other example is a native `<a href>` usable by keyboard, browser history and open-in-new-tab. Do not present these as thematic layer toggles or 2D/3D controls.
2. Existing public paths remain `/ARTEMIS/globe/` and `/ARTEMIS/region/`. Resolve sibling targets relative to the actual deployment base using `../globe/` and `../region/`, rather than hard-coded origin or root-absolute `/globe/`. Preserve the sibling Atlas path `../atlas/` and its compatibility label. Root-mounted and repository-prefix builds must work without separate routing infrastructure. The root landing page is outside this task and remains unchanged.
3. Navigation to the other example starts that example's existing default temporal/selection state. It must not copy any source query or hash except the allowlisted language preference defined below. In particular do not transfer `mode`, `start`, `end`, `from`, `at`, `presence`, `item`, `time`, `layers`, `stop`, camera intent, diagnostics or unknown parameters.
4. The current example's saved URL remains valid and continues to restore its own state under the existing contract. Browser Back returns to the source URL; restoration is judged by semantic time/selection, not identical camera animation or drawer openness. Navigation is ordinary document navigation, not mutation of one loaded dataset into another.
5. Keep one dataset loaded per existing page. Region retains its own three period controls and `life_path.available=false`; Leonardo retains Range/Scrub and its 11 episodes. Do not add a common timeline, shared selection store, simultaneous overlay or an implied synchronous relationship between 91–116 CE and 1452–1519.
6. Extend only the public-preview navigation for the supported Leonardo and Roman Region datasets. Non-public contract/review artifacts must not gain an implied public capability, and the non-public conflict proof must not gain a link or publication path.

## Language decision

Inspection found EN as the existing in-memory default, with EN/RU buttons calling `ARTEMIS_I18N.setLanguage`; there is no existing locale URL or persistent-storage contract. Engineering inspection also found language-button handlers inside the Leonardo life-path binding, leaving Region language buttons inert. This task authorizes extracting/reusing a shared language binding for the two public examples so Region EN/RU controls work while Leonardo behavior is preserved. It explicitly adds the smallest presentation-only URL convention needed for language continuity between these two pages:

- Scope this new URL convention and shared language-control behavior to the public Leonardo and Roman Region examples; non-public review/contract fixtures retain their existing behavior.
- Accept exactly `lang=en` and `lang=ru`; missing or invalid values select EN. Language never changes World Model, temporal selection, source text, IDs or historical assertions.
- On initial page load apply the selected language and correct pressed-button state. A language-button change replaces only `lang` in the current URL with the chosen value, retaining all existing semantic query values and the hash. Existing URL synchronization must retain `lang`.
- The outgoing Leonardo/Region link contains only `?lang=<active language>` in addition to its clean sibling path. Switching language updates that link. An explicit EN value is allowed; old saved URLs without `lang` remain valid and default to EN.
- The Atlas compatibility link remains a clean `../atlas/` link. Do not promise or implement language/state continuity into that separate compatibility runtime.
- Use no localStorage, cookies, global preference service or new session-state model. Native fallback links must still resolve if scripting has not initialized; they may open the target in default EN.

## Product copy

Use the following meaning and wording for the new navigation/status content. Current selected-example coverage may reuse an existing nearby coverage element instead of duplicating it. Coverage and status must remain visible without opening technical details.

| Role | EN | RU |
|---|---|---|
| Navigation accessible label | Research examples | Исследовательские примеры |
| Leonardo example | Leonardo · 1452–1519 | Леонардо · 1452–1519 |
| Region example | Roman Empire · 91–116 CE | Римская империя · 91–116 н. э. |
| Leonardo current coverage | 11 selected presence episodes · 1452–1519 | 11 выбранных эпизодов присутствия · 1452–1519 |
| Region current coverage | 3 reconstructed periods · 91–116 CE | 3 реконструированных периода · 91–116 н. э. |
| Public status | Public research prototype · not a validated product | Публичный исследовательский прототип · продуктовая ценность не подтверждена |
| Atlas link | Architecture Atlas · compatibility | Архитектурный атлас · режим совместимости |

Do not describe the three Roman periods as complete political history or precise historical borders. Preserve the existing approximate scholarly reconstruction note, Cliopatria attribution/license link, and source/uncertainty access. Leonardo's source-status explanation, draft/rejected disclosure, route-null limitations and incomplete-coverage note remain intact. Translate new labels and accessible names in both locales; this does not authorize a wholesale localization rewrite of unrelated existing source content.

## Layout and accessibility

Keep the navigation compact within the existing header. Permit wrapping or a similarly minimal responsive arrangement; do not add a large permanent sidebar or hide core provenance to make room. Current-example indication must not rely on color alone. Native links must have meaningful names, visible keyboard focus and usable targets under the existing acceptance profiles. Header growth must continue to respect the existing measured overlay/layout behavior so navigation cannot obstruct map controls, time controls, source/license links or the drawer.

## Acceptance evidence

Use existing Core/browser tooling and add only coverage needed for this change. Freeze the tested revision and record browser, viewport, dataset and locale.

- Build both public examples and verify native sibling routes under repository-prefixed and root-mounted deployment bases; retain a clearly labelled clean Atlas link. Check that non-public/default contract fixtures do not receive unintended public navigation.
- In a real browser, navigate Leonardo → Region → Leonardo using the links, in EN and RU. Verify active-example indication, bounded coverage, R&D status, locale continuity and target dataset/default state. Verify the target URL contains no foreign semantic or unknown query/hash state.
- Begin from a non-default saved Leonardo Range or Scrub URL with a selected Presence, change language, navigate away, and use Back or explicitly reopen the captured URL. Original mode/calendar/Presence restore; locale is correct when the URL contains its valid `lang` parameter. Reopen a non-default Region period/selection URL likewise. No requirement to restore open drawer state is added.
- Test a missing/invalid language value and a source URL containing extra query/hash values. Invalid language falls back to EN, while generated cross-example links propagate only normalized language. Changing language in place does not change semantic values.
- Exercise navigation by keyboard at desktop and an existing supported narrow viewport. Source links and disclosures remain reachable in both examples; Region license/reconstruction notes remain visible and the Leonardo source-status task remains passing. Confirm no new header/control overlap or horizontal overflow introduced by either locale.
- Keep relevant deterministic tests and current required Core checks green on the exact implementation PR head. Independent AI review must inspect scope, code, screenshots/task evidence and dataset isolation; an AI verdict is technical acceptance, not human-comprehension or comparative-value evidence.
- After any authorized publication, verify the actual live Globe and Region artifacts separately from merge/CI completion using the existing publication manifest/byte-verification procedure. Never infer live success solely from a green build.

## Risks, readiness and stop

### Bounded source-access correction — 2026-10-04

The first actual navigation browser run (`37198362254`, head `f8c7a8d99d28adf5d3567e386a81d5c246216fad`) failed on Region source-disclosure focus. Inspection found an existing UI defect: Region renders its selected record into an always-hidden inspector, and close/Escape handlers are bound only for Leonardo. This is a real source-access failure; earlier checks that assigned disclosure state did not establish visibility. The accepted requirement that both examples expose sources/uncertainty cannot be satisfied by altering the verifier to reveal hidden product DOM.

Authorize only this corrective public-Region interaction:

- Add a native **Region details / Сведения о регионе** button in the existing header, with `aria-controls` and `aria-expanded`; enable it only when the existing current Region record can be inspected.
- Open the already-rendered record and focus its detail card. Opening changes no selection, temporal state, query or historical assertion. Keep the inspector closed initially and on cross-example navigation; do not add automatic map-picking/selection behavior.
- Bind closing and Escape for this public Region drawer, restore focus to the opening button, and keep expanded/disabled state truthful when selection is cleared.
- Give the Region inspector/close control and selected-record eyebrow accurate EN/RU Region wording, preserving the existing record title, native source content, reconstruction note and license.
- Verify opening, close/Escape, focus restoration and semantic/URL invariance with actual input and focused local behavior checks. The browser scenario must open the drawer through its native control, open disclosures through native Space, then close before navigating; no synthetic visibility/open assignment may establish PASS.

This amendment restores required source access inside the same task. It does not authorize a general drawer redesign, new Region knowledge, non-public behavior, dataset composition or a new product gate. Independent exact-byte specification amendment acceptance must be recorded before these runtime edits.

| Corrected Region control | EN | RU |
|---|---|---|
| Opening button / initial title | Region details | Сведения о регионе |
| Inspector accessible name | Selected region details | Сведения о выбранном регионе |
| Selected-record eyebrow | Selected region | Выбранный регион |
| Close accessible name | Close region details | Закрыть сведения о регионе |

Amendment acceptance: independent agent `/root/navigation_review` returned **ACCEPT_SPECIFICATION_AMENDMENT**, no material findings, for SHA-256 `a02dc3d196b5e8d8421f58f63c3584328f2fee9c57de092d45cf557bdcbec097` and the canonical scope source-access paragraph on 2026-10-04. The hash identifies the reviewed bytes before this verdict paragraph, not a self-hash. This acceptance was recorded before corrective runtime edits; exact-head implementation/browser review remains required.

Main risks are cross-dataset query leakage, misleading combined-context presentation, deployment-prefix breakage, untranslated labels and additional header collisions. The allowlist, explicit example/coverage labels, native relative links and scoped browser checks address those risks without changing domain meaning.

Specification readiness — historical: independent agent `/root/architecture_audit` returned **ACCEPT_SPECIFICATION**, no material findings, on 2026-10-04 for specification SHA-256 `42f562d103efc90754a2ac2300cf3eb0aa0502b7766c005ddab166dfbeb14546`, the canonical scope amendment and registry entry. This hash identifies the reviewed bytes before the status/verdict paragraph update, not a self-hash of this resulting document. This acceptance preceded implementation; exact-head implementation review and live publication verification are recorded below. No historical/source data edit is authorized. If a required fix needs a new semantic owner decision, a broader dataset/state design or removal of an existing provenance obligation, record the precise blocker and stop that expansion.

Complete when the two existing examples are mutually reachable with honest labels, isolated restorable state, EN/RU continuity, passing relevant checks and independent implementation acceptance; record live verification separately. Then stop. No Atlas migration, 2D toggle, new dataset, common timeline, general shell framework, context overlay or automatic successor follows.

## Technical implementation and publication closeout — 2026-10-04

PR [#464](https://github.com/omegapunctum/ARTEMIS/pull/464) implemented native navigation between the existing public Leonardo and Roman Region examples, visible example/coverage/R&D labels and presentation-only EN/RU continuity. Cross-example links transfer only normalized language and start the target's own defaults. Each page retains its separate semantic time/selection URL contract. The native public-Region details control restores access to its existing selected record; opening/closing changes no selection, time or URL. Non-public behavior and frozen historical/source data remain unchanged.

| Evidence | Recorded identity / outcome |
|---|---|
| Reviewed implementation head / tree | `3ff8627e446f67d81763f26ddc570376a57abb21` / `67fa762b1b6b9207023a9644b26f934efdda7f0b` |
| CI candidate | `d752b0eceaf90c0f3512c4a8d282f725774be376`; identical tree |
| Independent AI review | `/root/navigation_review`: **ACCEPT_IMPLEMENTATION**, no material findings; exact-head GitHub review `5405924597`, recorded before merge |
| Required checks | Core [37199995243](https://github.com/omegapunctum/ARTEMIS/actions/runs/37199995243): SUCCESS, **363 tests PASS**, source-aware/ATL/browser scenarios PASS; Runtime [37199995365](https://github.com/omegapunctum/ARTEMIS/actions/runs/37199995365) and Boundary [37199995270](https://github.com/omegapunctum/ARTEMIS/actions/runs/37199995270): SUCCESS |
| CI browser evidence | Artifact `11302304167`, Chrome `134.0.6998.35`, actual widths 1440/500 and heights 760/761, EN/RU; all 26 navigation PNG hashes verified and relevant screenshots independently inspected |
| Merge / verified publication source | `ee352ba6ec1a213e4ff2e2eb5f322d12598c2717` |
| Separate live verification | Pages [37200481441](https://github.com/omegapunctum/ARTEMIS/actions/runs/37200481441): SUCCESS; Globe **16 files**, Region **20 files**, manifest/byte verification **PASS**; Region three-snapshot provenance/license/reconstruction retest **PASS** |
| Live navigation evidence | Artifact `11302594285`, Chrome `154.0.8037.57`, actual viewport **1440×757**, EN/RU; native navigation, Back and independent saved-URL reopening **PASS**; all 13 navigation PNG hashes verified |
| Durable evidence summary | [Exact identities, reports, capture hashes and limits](evidence/2026-10-04_explorer_navigation_summary.json) |

Browser checks compare the selected Leonardo Range/Presence and non-default Region period/item after native Back and a separate reopening from another document. The first Region source-access failure and accepted prospective correction remain recorded above. Two later harness failures were corrected without weakening semantic equality: a same-URL fragment navigation did not reconstruct a document, and the first Region view for a period had empty layers. The final verifier leaves for the other document before reopening the exact saved URL, and selects the actual current-layer Region view. No product state is injected to establish PASS.

Local functional checks exercised language/URL and Region drawer behavior; public/private generated semantic JSON/GeoJSON were byte-identical excluding build metadata. The 137 affected runtime/Region/governance checks passed after the source-access correction; 95 relevant governance/state/lifecycle checks also passed. The mechanical UI scan reported only three pre-existing stylesheet warnings, confirmed identical in the baseline; it was not a visual acceptance result.

This is technical/UI conformity and public availability evidence. It does not establish a full accessibility audit, camera/drawer restoration, human comprehension, fresh historical-source validation or comparative/formal product value. The task is closed. Gate E remains closed without VALUE_SIGNAL, contextual composition DEFERRED and conflict proof non-public; value remains UNVALIDATED. No automatic successor, Atlas migration, combined dataset/timeline or 2D toggle is opened.
