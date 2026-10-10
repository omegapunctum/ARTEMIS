# Compact selection design QA — 2026-10-10

final result: owner-accepted bounded standalone preview; remaining native checks pending

Current evidence: the owner accepted the standalone preview with “Да, принимаю.” and supplied a rendered desktop screenshot on 2026-10-10. Globe, compact records/details panels and one highlighted range track are visible. See [owner acceptance receipt](docs/work/evidence/compact-selection-20261010/owner-acceptance.md) for artifact identity, observation limits and remaining checks. This supersedes the earlier missing-render blocker for this preview. The owner subsequently authorized merge; required current-head review/CI remain prerequisites, as recorded in the active compact-selection task.

## Visual authority and evidence

Screenshot paths below are historical evidence identifiers. Images are retained outside the public repository following an upload privacy rejection; see [screenshot evidence locations](docs/work/evidence/compact-selection-20261010/screenshot-evidence.md) for hashes and distribution limits.

The owner selected the refined map-first concept on 2026-10-09 and amended it on 2026-10-10: compact first-click card near the selected object, optional right details, fewer empty panel/calendar rows.

Source visual truth: owner screenshots `docs/work/evidence/compact-selection-20261010/01-owner-rendering.png` and `02-owner-spacing.png` (2048 × 1051 and 2048 × 1049 pixels, browser chrome included; CSS viewport/DPR unknown). They show the prior desktop build on Windows, not this correction. Prior generated target: `exec-e0ff4dd6-3364-4ce4-84ab-92024429ef84.png`, Drive file `1ld-kcesAHc9zINl0_EOtTQu2aD89hz5P`.

Earlier implementation screenshot: the owner supplied `03-owner-startup-failure.png` (2048 × 1039) from the delivered correction, but it shows failed/incomplete startup with disabled initial markup and no globe. At that checkpoint no successful corrected render was available. The available cloud-browser run previously failed with WebGL Disabled; its screenshot remains `docs/work/evidence/desktop-workspace-20261009/webgl-blocked.jpg`. These earlier screenshots do not validate the new revision. The later owner acceptance receipt records a successful standalone render.

## Findings and correction history

- P1 reported globe stutter: owner report, no timing trace. Removed gesture-time label collision calculations and idle-only label callbacks, skip hover hit-testing while moving, avoid identical cue transforms, cap canvas DPR at 1.5. This reduces configured work; measured performance improvement is unverified.
- P1 horizontal globe cutoff: visible on both owner screenshots; cause unresolved. No geometry clipping, masking overlay, engine upgrade or invented map data used as a purported fix. Needs same-camera Globe/2D comparison, console and canvas diagnostics.
- P2 selection flow: restored compact summary, explicit Details, Back to card and clear selection. Original coordinates anchor point cards; region clicks are renderer-only anchors; chooser/history regions and occluded/offscreen points use a screen-positioned fallback. Native popup bounds/opacity trigger fallback without panning. Post-fix native interaction evidence pending.
- P2 wasted panel height: tightened closed disclosure spacing, inline heading controls and compact left search. The accepted standalone screenshot shows compact header/records/details panels; matched before/after fidelity comparison remains unverified.
- P2 timeline density/double track: one shared styled track with native accessible endpoint inputs, compact desktop row and smaller notes. Matching endpoints use separated thumb positions. Native pointer/keyboard and responsive verification pending.

## Fidelity surfaces and comparison

The corrected desktop render is now visible and owner-accepted as a bounded preview. Formal fidelity comparison across fonts/typography, spacing/layout rhythm, colors/tokens, image quality and copy/content remains unverified. Content is source-bound and includes source-native dates, historical-applicability limits, duration limits and the Cesena candidate-context warning. No combined before/after or focused-region comparison, normalization or matched viewport/density comparison is claimed.

Previous mobile QA is preserved verbatim in `docs/work/2026-10-09_MOBILE_DESIGN_QA_ARCHIVE.md`; its pass does not accept this revision.

## Verification and remaining checklist

Owned tests exercise canonical query/state/source identity, presentation state, source-coordinate anchors and shipped summary/inspector DOM functions against a minimal DOM/Popup port. They are not native rendering evidence. Browser/performance harnesses now open explicit Details and retain byte/state checks; they were not run through an alternative browser in this environment.

1. Completed for the standalone preview: owner opened the package directly and supplied a rendered globe screenshot.
2. Capture compact card, Details, closed disclosures and range controls at the same viewport; verify keyboard/mobile and coincident endpoints.
3. Compare combined old/new views and focused typography/spacing regions; close actionable visual issues with post-fix evidence.
4. Diagnose the globe cutoff and measure movement before accepting a performance fix.
5. Independent code review is separate from native acceptance. No merge/publication or user-value claim.

## Startup recovery after owner package test

P1 startup failure observed at localhost4174: empty map, full initial header, disabled controls; owner annotations identify these as defects. Cause remains unproven. Parser-blocking external engine dependency is removed by delivering the same pinned MapLibre 5.24.0 JS/CSS locally with license and a hash-validated manifest. Boot guard catches missing scripts/unhandled startup errors, preserves failure until reload, reports local data errors and a 15-second fetch timeout, and retains a 20-second waiting message until first idle. Required adapters are checked before mounting. The range stays neutral until computed endpoint values are painted.

The updated package has no external script/stylesheet or live data dependency. Local source artifacts and embedded worker code remain unchanged. At this checkpoint native load/idle, card placement, short landscape, the globe cutoff and real gesture performance were pending. Current-session cloud navigation to the local test server returned `ERR_CONNECTION_REFUSED`; that attempt supplies no browser rendering pass. Later owner evidence establishes a rendered standalone preview, with the remaining checks bounded in the acceptance receipt.

## Owner-confirmed transport failure and standalone review variant

Owner console screenshot `04-owner-connection-reset.png` (2048 × 948) confirms `ERR_CONNECTION_RESET` on runtime.js. Prior resource onerror named the engine; both files exist and HTTP200 appears in owner logs. Receipt of complete response bodies is not established. The source of the reset remains unknown.

A separate local-review-only standalone artifact embeds exact script/style/license bytes and original startup JSON bytes in inert base64 elements, removing startup asset/data HTTP requests. The normal deployment entry is retained; stamped releases are rejected as standalone inputs. Packaging and full entry-point DOM-port checks are not native file:// worker/history/WebGL proof. The later owner screenshot and explicit acceptance establish a rendered standalone preview. Dedicated worker/history tests and card/range interactions, mobile, cutoff diagnosis and measured performance remain pending; see the acceptance receipt.
