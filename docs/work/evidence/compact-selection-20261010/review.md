# Independent compact-selection code review — 2026-10-10

Verdict: **ACCEPT_CODE_CONFORMITY_PENDING_NATIVE**.

Exact implementation reviewed: `deba72ca6116d872abdaba315528a43ceec7eaaf`, on `feat/desktop-workspace-20261009`. Distinct reviewer: `/root/hierarchy_review`, under Development Operating System §6.2. Review covers the owner-authorized compact first-click selection/Details/Back flow, responsive presentation, timeline styling, configured renderer work, native proof compatibility and evidence limits. This receipt is the reviewer's only repository edit; no implementation edit, commit, publication, external message or merge was performed.

## Findings and disposition

No unresolved material code-conformity findings were identified in the bounded prepared correction. Selection presentation remains outside canonical WorkspaceState. Details and Back change presentation without calling the canonical state/history/camera update path; close retains clear-selection semantics. A different selected item resets presentation, while same-item language/time updates retain Details and disclosures. The map-ready path renders restored selection after initialization.

Point summary anchors use existing source-bound renderer coordinates. Region clicks use renderer-only click coordinates; chooser/history regions have no invented representative historical point. The source-native reference title is shared between summary and inspector, including available RU names. Presence summaries retain source-native date or exact input temporal extent, duration limits and the unchanged Cesena candidate context immediately after its unverified-context warning. Catalog and atemporal applicability limits and approximate-reconstruction wording remain explicit.

Earlier review findings are addressed: explicit Details opening in both native harnesses; current high-DPI cap expectation changed to 1.5 without relaxing source-payload/geometry identity checks; source-native RU title/date and coherent Cesena warning/context; popup height/bounds/opacity checks with a screen-positioned fallback. The fallback reuses the card node and restores focus. These are code/model findings, not proof of native placement or occlusion behavior.

Closed-disclosure/header spacing and calendar rows are tightened. Two accessible native endpoint inputs remain with one visible track; coincident endpoints receive separate thumb positions. Gesture-time collision layout and repeated idle-label callbacks are removed, identical cue transforms are skipped, moving-map hover queries are skipped, and canvas pixel ratio is capped at 1.5. These configure less work; no measured FPS, responsiveness or freeze cure is accepted.

The unified harness prepares first-card capture, Details/Back native transitions, state/camera/URL preservation and Details hit testing. Its owner-opening recursion is bounded. The high-DPI proof still compares actually disclosed native source payloads and retains native pick/drag/map identity checks. The updated native scenarios have not run on this revision.

## Independently executed checks at the reviewed commit

- `node tests/compact_selection_behavior.cjs /workspace/scratch/aaded34ca3ef/desktop-preview/unified-bundle.json`: `COMPACT_SELECTION_DOM_BEHAVIOR_PASS`.
- `node tests/desktop_explorer_behavior.cjs`: `DESKTOP_EXPLORER_BEHAVIOR_PASS`.
- `node tests/mobile_explorer_behavior.cjs`: `MOBILE_EXPLORER_BEHAVIOR_PASS`.
- `node --check` for shipped runtime and both changed native harnesses: exit 0.
- `git diff --check`: exit 0; reviewed HEAD remained the SHA above.

The independently inspected DOM-port input contains 55 records and SHA-256 `a0c2046ea0862683167aef3b6d5f4b496a36fcabb0b2dcaa595c4534f91d5538`. It is an existing local bundle used by the test, not independent verification of the final delivery archive. The test executes shipped source/summary/inspector functions against a minimal DOM/Popup port; Map/Popup/layout/selectItem and some inspector-language helpers are stubbed. It does not establish full application event wiring, real URL/camera behavior, native keyboard/pointer interaction, WebGL, measured placement or performance.

Author-executed evidence is distinct: 38 owned tests passed in 16.48s before the final prepared harness Back/hit-test/capture additions; those subsequent harness additions passed syntax checks and are included in this exact review. Final production-build and delivery-byte verification are separate author receipts, not an independently executed build claimed here.

## Outstanding product, native and platform limits

**Native/visual acceptance is BLOCKED/PENDING. The horizontal globe cutoff is UNRESOLVED.** The reviewer inspected both owner screenshots: they visibly show the earlier build's cutoff, disclosure gaps and duplicated tracks. They are prior-build evidence, not corrected-render acceptance. The available cloud browser previously failed WebGL initialization. Neither cause of the cutoff nor the reported stutter is established; geometry, map-engine version and source corpus were not changed as a purported fix.

Before release, verify current first-click cards, Details/Back/clear, exact source content, popup occlusion/fallback footprint/focus, desktop/mobile and short-landscape transitions, and both range inputs including coincident endpoints in a WebGL-capable browser. Diagnose the cutoff using identical-camera Globe/2D views and canvas/renderer diagnostics; measure movement before claiming a performance fix. Updated high-DPI/native gates and owner visual acceptance remain pending. Earlier branch/native/mobile passes do not accept these changed product files.

The prior Windows serialized amendment-path correction in `a9a28ec34529cee615ffe82933e22b8ff80be1b3` was independently reviewed separately. The owner-reported Windows build succeeded with 55 records after the manual patch, but its bundle hash differed from the Linux `a0c2046…` bundle (owner `e88…`). Cross-platform byte/path reproducibility remains unresolved; this review does not claim that the owner's rebuilt bundle is byte-identical. A separately verified prebuilt package can avoid requiring an owner rebuild; it does not resolve that reproducibility question.

No current-head remote CI, publication, merge, complete product-problem resolution or user-value acceptance is claimed. The owner's merge hold remains in force.

## Exact reviewed file hashes

| File | SHA-256 |
|---|---|
| `scripts/unified_explorer/runtime.js` | `228aaa6818bb883149b6d69a6bbfa082aaa308dbbc6f30fc553942d132a57757` |
| `scripts/unified_explorer/desktop.js` | `2fb43e253b8333f917b5a8b2bce9c4f126cfb458fafbb598444e6e3acc9da5f1` |
| `scripts/unified_explorer/style.css` | `3d78585d797a591bcafdca640181d7439e7b4a9d160ac82f6a71e6959f32ea80` |
| `scripts/unified_explorer/index.html.template` | `d12e40e5b498ffd2fcf53638b8e5c5d5bda9e61c1f3a69c0310c4753cf98444d` |
| `scripts/capture_unified_explorer_browser_evidence.mjs` | `ad27a3cbffa69bf94f1e4a995a36f536bc800b763b50f0ab69fc6cb2d95a2f66` |
| `scripts/capture_explorer_performance.mjs` | `adefc623d7d26f2ce01259b13eb8a2492b7210be915f6f7b03bbc5c46a732d9d` |
| `tests/compact_selection_behavior.cjs` | `7264cfb97471f862a8a3ed08eaac53dc9b1338a772c94b9410b215e459194e7d` |
| `01-owner-rendering.png` | `4ca0f93b5366e9af04fd31ce4d7323956211e50034ca32367a3f9cb42492d792` |
| `02-owner-spacing.png` | `6ab641c4c25666bd94d153a6a537510c6b573030699ae294ba87f5f477010df5` |
