# Desktop workspace v1

Current lifecycle synchronization — 2026-10-17: completed delivery and remaining
limits are recorded in [the factual closeout](2026-10-17_CURRENT_STATE_AND_DIRECT_ENTRY_v1.md).
This supersedes older pending-CI/upload/merge/publication wording below; dated
observations, failures and acceptance boundaries remain historical evidence.

Owner explicitly confirmed implementation of the refined second concept on 2026-10-09. Class REVIEW. Product Scope owns this bounded change.

Reference: ARTEMIS_Web_2026-10-09_02_Refined_Compact_Panels.png, Google Drive file 1ld-kcesAHc9zINl0_EOtTQu2aD89hz5P. Layout only: compact floating records left, inspector right, full-width calendar, existing simple Natural Earth globe. No generated geography, historical facts, decorative glow or new logo copied from the image.

Keep the same controls, IDs, map, history, source bundle and mobile composition. Desktop-only panel state never changes canonical state. At the mobile breakpoint restore original controls to their original parents. Selecting a different record reopens inspector content; collapsing must retain selection and disclosures. Provide named keyboard-operable controls and restore focus before hiding focused content.

Acceptance: desktop collapse/search/select/layers/language/time and responsive round trip; existing mobile and unified checks; byte-identical public bundle; native screenshots and independent code/visual review. Product Design QA remains blocked until the browser can render the actual application. Do not represent generated concepts or unit tests as browser evidence. Stop after this bounded implementation; no automatic merge or unrelated audit fixes.
