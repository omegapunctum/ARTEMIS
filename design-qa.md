# Desktop workspace design QA — 2026-10-09

final result: blocked

Previous mobile QA is preserved verbatim in `docs/work/2026-10-09_MOBILE_DESIGN_QA_ARCHIVE.md`; its historical pass does not accept this desktop revision.

## Target and evidence

- Source visual truth: owner-approved `exec-e0ff4dd6-3364-4ce4-84ab-92024429ef84.png`, Drive file `1ld-kcesAHc9zINl0_EOtTQu2aD89hz5P`.
- Implementation: local production build at `http://terminal.local:4173/`, branch `feat/desktop-workspace-20261009` over `20d4784`.
- Browser-rendered screenshot: `docs/work/evidence/desktop-workspace-20261009/webgl-blocked.jpg` (1363 × 936 pixels).
- State: default EN / Globe / 1452–1519; startup failed before map readiness.
- Console checked: MapLibre reports `webglcontextcreationerror`, `GL_VENDOR = Disabled`, `GL_RENDERER = Disabled`, `Failed to initialize WebGL`.
- Viewport/density normalization: matching target viewport and density could not be established for a functioning implementation. No normalized comparison is claimed.

## Findings

[P1 / acceptance blocker] The available browser cannot initialize WebGL. The fatal-error surface covers the workspace. Native selection, camera continuity, panel interactions and responsive focus cannot be accepted from this screen. This is an environment limitation observed in this browser; it does not establish a production rendering defect.

## Comparison history and fidelity surfaces

No valid full-view or focused-region source/implementation comparison has been completed. Fonts/typography, spacing/layout rhythm, colors/tokens, image quality, and copy/content fidelity are all **unverified visually**. No fabricated comparison or passing iteration is recorded.

Code review found responsive focus loss and obsolete native harness ownership assumptions. Both were corrected; model-based tests pass. The harness now opens collapsible owners through native controls and includes desktop collapse/reopen state checks. These are prepared checks, not executed native evidence.

## Remaining implementation checklist

1. Run the native harness in a WebGL-capable browser, including desktop panels and mobile regression scenarios.
2. Verify keyboard focus across wide/narrow and short-landscape breakpoints, including Layers summary and collapsed inspector.
3. Capture EN/RU selected-record states, layers and both collapsed panels at matching viewport/density.
4. Compare combined source/implementation full view and focused regions; fix any P0/P1/P2 differences and recapture.
5. Complete independent exact-revision review and owner visual acceptance before merge/publication.

No release readiness, public delivery or user-value validation is implied.
