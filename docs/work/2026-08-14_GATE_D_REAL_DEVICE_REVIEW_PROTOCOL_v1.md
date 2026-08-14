# ARTEMIS — Gate D Real-Device Review Protocol v1

## Status

- Type: active Gate D operator evidence protocol.
- Date: 2026-08-14.
- Owner issue: `#355`.
- Evidence status: `PENDING` until every mandatory run is recorded.
- Runtime: isolated generated Globe artifact only.
- Public capability change: none.
- Gate E: closed until an explicit Gate D `ADVANCE_TO_GATE_E` decision.

## 1. Purpose

This protocol closes the manual-evidence gap left by the hosted Chromium evidence in PRs `#383` and `#385`. It records reproducible observations from physical devices, a normal interactive browser, real assistive technology and non-virtual performance runs.

It does not:

- run participant validation;
- claim WCAG conformance;
- define a production performance SLO;
- publish or promote the Globe;
- authorize historical geometry, live terrain, Cesium, backend work or Airtable historical writes.

The tested artifact must continue to use the single semantic path:

`World Model → Explorer State → Render Projection → renderer`

## 2. Evidence identity

Before testing, record all of the following. A run without exact artifact identity is not Gate D evidence.

| Field | Required value |
|---|---|
| Repository commit | Full 40-character SHA used to generate the artifact |
| Workflow run | GitHub Actions run URL or reproducible local build command |
| Artifact digest | SHA-256 of the reviewed archive or generated directory manifest |
| Browser evidence contract | `fixtures/globe_runtime/v1/gate_d_acceptance_profiles.json` version/digest |
| Review date | ISO date |
| Reviewer | Stable non-sensitive reviewer identifier |
| Network condition | Connection type and whether throttling was used |

Use a local HTTP server or another non-public review surface. Do not add a public Pages route. Do not include credentials, private research notes or personal data in screenshots, logs or recordings.

## 3. Mandatory environment matrix

| Run | Environment | Mandatory proof |
|---|---|---|
| D1 | Physical desktop or laptop; current normal interactive browser; no headless mode or virtual time | OS/browser/GPU/WebGL renderer, CSS viewport, display scale, keyboard pass and visual review |
| M1 | Physical mobile device whose page reports `window.innerWidth === 390` CSS px | Device/OS/browser, portrait viewport, touch pass, screenshots and overflow/overlay review |
| A1 | Real screen reader on a physical desktop or mobile environment | AT name/version, browser/OS pairing, reading order and control announcements |
| P1 | Physical representative desktop; normal interactive browser; no CPU/virtual-time acceleration | Three cold and three warm runs plus interaction observations |

Emulation alone cannot satisfy M1. If the physical device does not report exactly `390` CSS px, record the run as supplementary and keep M1 `PENDING`.

## 4. Shared preflight

For every mandatory run:

1. Start from a fresh browser profile or record all extensions and custom settings.
2. Record `navigator.userAgent`, `window.innerWidth`, `window.innerHeight`, `devicePixelRatio` and the WebGL renderer/vendor exposed by the browser.
3. Load the exact non-public artifact and wait for `data-artemis-visual-ready="true"`.
4. Confirm that present-day land/coastlines are visibly legible and that the runtime reports non-zero Earth-context source and rendered feature counts.
5. Confirm the artifact is labelled non-public/R&D and Natural Earth is identified as `present_day_context`, not historical geography.
6. Record console errors, WebGL warnings, failed network requests and any browser fallback.
7. Keep the frozen Leonardo boundary unchanged: 8 August–31 December 1502; Claims draft/rejected; unknown routes unresolved; Region geometry withheld.

## 5. Core interaction script

Run the following sequence on D1 and M1. Record `PASS`, `FAIL`, `NOT RUN` and a short observation for every step.

1. Load the default view and confirm a visible Earth context, timeline, layer controls, inspector entry point and attribution.
2. Move through all six source-native temporal presets: full slice, Rimini, Cesena, patent, Cesenatico and Imola autumn; verify that visible objects and inspector context remain synchronized.
3. Exercise all four semantic layer controls individually and at least one multi-layer combination.
4. Select an object from the rendered surface and from a non-map control; confirm the same canonical identity and selection state.
5. Inspect at least one Event, State, Process, Trajectory and temporal Region.
6. Confirm that sources, locators, Claim/evidence state, material uncertainty, alternatives, coverage and projection loss are reachable from the selected object.
7. Confirm that unknown route segments are not rendered as invented lines and geometry-withheld Regions are not rendered as historical polygons.
8. Copy the stateful URL, reload it and verify restoration of time, active layers and selected object.
9. Enable reduced motion at OS/browser level and verify that essential state change remains understandable without non-essential animation.
10. Return to the default state and verify there is no persistent stale selection, hidden overlay or broken focus state.

### Desktop keyboard extension

On D1, repeat the core path without a pointer:

- traverse all controls in a logical order;
- verify a visible focus indicator;
- operate the temporal range, layer toggles, selection controls and inspector;
- confirm there is no keyboard trap;
- confirm focus remains meaningful after inspector updates and URL restoration.

### Mobile touch extension

On M1 at exactly 390 CSS px:

- verify no document-level horizontal overflow beyond 1 CSS px;
- verify the Globe remains usable and overlays do not cover core controls;
- verify touch targets are operable without accidental adjacent activation;
- test portrait orientation and record any orientation change as supplementary evidence;
- verify browser chrome appearing/disappearing does not hide the timeline or inspector actions.

## 6. Assistive-technology script

Run A1 with a real screen reader and record the exact AT/browser/OS combination.

1. Navigate by landmarks/headings and verify that the page purpose and Globe R&D status are announced.
2. Navigate by form controls and verify accessible names for timeline, layer controls and other buttons/inputs.
3. Change the temporal preset and verify that the current value/state is announced or otherwise programmatically available.
4. Toggle layers and confirm pressed/checked state is exposed.
5. Select an object without relying on the WebGL canvas alone; verify that canonical identity and inspector content become reachable.
6. Read sources, locator, uncertainty, alternatives, coverage and projection-loss content in a coherent order.
7. Verify that present-day context and withheld/unknown historical geometry are not announced as historical facts.
8. Record keyboard traps, silent state changes, misleading names, duplicate announcements and focus loss.

A1 is an assistive-technology review, not certification or a complete WCAG audit.

## 7. Representative performance observations

Run P1 with browser cache/storage cleared before each cold run and preserved before each warm run. Do not use virtual time, synthetic CPU acceleration or a hosted CI runner. Record three cold and three warm observations.

For each run record:

- navigation start to `data-artemis-visual-ready="true"`;
- timeline change to visually settled state;
- layer toggle to visually settled state;
- selection to complete inspector update;
- long tasks, visible jank, input lockups, memory pressure, WebGL context loss and console warnings;
- whether developer tools were open and whether network/CPU throttling was enabled.

Report raw values plus median and range. These measurements are evidence for the Gate D decision, not a production SLO. Do not convert the hosted headless timings from PR `#385` into pass/fail thresholds.

## 8. Finding severity

| Severity | Definition | Gate effect |
|---|---|---|
| Critical | Artifact cannot load; Earth context is absent; core time/layer/selection/inspector path cannot be completed; semantic boundary is violated; or required content is inaccessible with the tested AT | Blocks `ADVANCE_TO_GATE_E` |
| Material | Real 390 px overflow/collision, keyboard trap, silent or lost state, missing source/uncertainty access, repeated interaction lockup or reproducible serious performance degradation | Blocks `ADVANCE_TO_GATE_E` until fixed or explicitly narrowed |
| Minor | Does not prevent the core path or materially distort meaning | Record with disposition; does not alone decide the gate |
| Observation | Context or improvement note without demonstrated failure | Preserve for the decision record |

A browser or renderer limitation becomes a MapLibre blocker only when it is reproducible, tied to the bounded MVP requirement and recorded with environment, steps and evidence. Only then may a separate bounded Cesium comparison be proposed.

## 9. Evidence record

Complete this section in a follow-up evidence PR. Do not mark a row `PASS` without an attached durable artifact or reproducible observation.

| Run | Status | Environment | Evidence refs | Critical | Material | Minor |
|---|---|---|---|---:|---:|---:|
| D1 desktop | PENDING | — | — | — | — | — |
| M1 390 px mobile | PENDING | — | — | — | — | — |
| A1 assistive technology | PENDING | — | — | — | — | — |
| P1 representative performance | PENDING | — | — | — | — | — |

For every finding record:

- stable finding ID;
- run/environment;
- severity;
- exact reproduction steps;
- expected and observed result;
- screenshot/log/recording reference;
- semantic/public-capability impact;
- disposition: `FIX`, `NARROW`, `ACCEPT_MINOR`, or `REJECT_PATH`.

## 10. Completion and decision boundary

This protocol is complete only when D1, M1, A1 and P1 have durable evidence, no mandatory step is `NOT RUN`, and critical/material findings are either closed or explicitly drive `NARROW`/`REJECT`.

Completion makes Gate D eligible for one recorded decision; it does not choose the decision automatically:

- `ADVANCE_TO_GATE_E`;
- `NARROW`;
- `REJECT`.

Only `ADVANCE_TO_GATE_E` may open task-based participant validation. Public deployment remains a separate later decision with its own provider, licensing, security, rollback and current-truth evidence.

GitHub remains canonical truth. Airtable remains an empty, non-authoritative curation shadow for this contour, and no historical import is authorized by this protocol.
