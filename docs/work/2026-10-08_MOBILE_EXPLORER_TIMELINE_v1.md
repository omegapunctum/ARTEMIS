# Mobile Explorer timeline v1

## Authorization and specification

Class: REVIEW. Direct owner instruction on 2026-10-08 authorizes applying the selected mobile composition, with compact vertical year wheels at the timeline edges, no visible “Time” heading/icon or “From”/“To” labels, and a collapsible bottom panel. This is a bounded presentation correction under the existing shared Explorer capability and Development Operating System §6.2, not a product/gate transition.

Visual direction: the owner-selected free map plus collapsible calendar, amended to small year controls alongside the timeline. The existing Natural Earth renderer is retained. Generated design imagery is layout guidance only and never data, a source, geography promotion or publication evidence.

For viewports at or below 640 CSS px, and short landscape viewports at or below 960 × 500 CSS px:

- keep the existing single map, compact brand/search and a permanently reachable shared calendar;
- disclose layers, chooser, presentation/language settings separately, preserving current controls and search semantics;
- default the calendar to a compact row, expand/collapse with an explicit accessible button or a vertical gesture on its handle;
- show 44 CSS px high start/end year spinbuttons around the range instrument, or one year spinbutton for Scrub; panel height follows content without an empty fixed-height region; retain accessible localized CE names when visible labels are absent;
- year-wheel touch, mouse-wheel and keyboard navigation creates a bounded local draft, committed through Apply or discarded through Cancel; no automatic keyboard or canonical/URL changes during wheel scrolling;
- retain incumbent slider release behavior, Range overlap, Scrub accumulation and trace origin, supported CE years 91–1519, presets, shared URL/history and selection;
- preserve all source/uncertainty disclosures and actual map attribution; compact mobile source access must open the full existing rights/context text;
- panels, wheel drafts and collapse gestures must not recreate the map, move the camera or create a source/network fetch;
- retain desktop composition and input compatibility.

Non-goals: new data, dates, spatial precision, historical applicability, routes, relations, confidence, Global/Focus timeline implementation, Explorer State schema changes, gate reopening, editor/storage changes, paid services or a new app/runtime. The generated mock does not authorize replacing real map geometry with artwork.

## Verification and stop condition

Owned checks cover bounded draft/year navigation, crossing/boundary behavior, canceled gestures, panel state and exact canonical commits. Native/browser inspection must cover fresh collapsed portrait, expanded calendar, actual wheel edit/Apply/Cancel, source/evidence cards, projection/layers/search/history preservation and desktop regression. Inspect narrow portrait and short landscape/safe-area layouts for overflow, accessible controls, map clearance and timeline reachability.

Distinct AI review must inspect the exact implementation head and relevant screenshots/test evidence before merge. Passing implementation checks does not establish physical-iPhone performance, complete accessibility or comparative/user-value validation. Stop after bounded implementation, review, exact-head checks and separately verified publication. No automatic successor.

## Implementation evidence

Implemented in [PR #479](https://github.com/omegapunctum/ARTEMIS/pull/479): a bounded mobile presentation adapter is mounted in the existing shared runtime and shipped/hashed by the builder at both compatible entries. The input bundle remains byte-identical (`a0c2046ea0862683167aef3b6d5f4b496a36fcabb0b2dcaa595c4534f91d5538`, 55 registry identities). Desktop state/source semantics and the incumbent renderer are retained.

Relevant local verification: 116 tests pass. Native Chromium evidence at `1381565c8f9430d08af0594bcebbfd466950d872` passes complete 1440 × 900, 500 × 900 and 390 × 844 scenarios. The 844 × 390 run verifies compact years, trusted wheel input, panels, source-card scroll-end clearance and search, reaching final map input before the helper attempted to pick through its still-open View panel. The final helper closes panels through genuine visible controls before map input and asserts unchanged state, camera, membership, card and map. Its syntax, Node and two owned pytest checks passed before the workspace connection interruption. No forced DOM input or weaker semantic assertion was substituted for native evidence.

Independent visual QA passes the actual narrow portrait, landscape and desktop composition. The one P2 inspector/tool overlap is closed by rendered post-fix raw-card tail captures and native clearance assertions; year wheels remain 44 px and the calendar has no fixed empty region. The project-root `design-qa.md` records the visual target, normalized comparison, required fidelity surfaces and verification limits.

Final exact-head Architecture/Product technical acceptance, complete native/CI outcomes, merge identity and separately verified public deployment are durable receipts in PR #479. This document records implementation evidence and does not infer public availability or validated value from preview checks. The task stops at that bounded delivery; no automatic successor or semantic/gate transition follows.
