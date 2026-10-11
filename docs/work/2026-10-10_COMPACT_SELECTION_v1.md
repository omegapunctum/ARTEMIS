# Compact selection and workspace correction — 2026-10-10

Class REVIEW, explicitly requested after owner Windows screenshots. Scope: compact first-click popup, explicit Details panel, denser closed disclosures/header and desktop calendar, single visual range track, bounded renderer workload corrections. No new domain data or historical precision.

Observed evidence: owner screenshots image(20261010-042308).png and image(20261010-042440).png show oversized closed-disclosure gaps, two native range tracks, sparse timeline rows and an upper horizontal globe cutoff. Owner reports stuttering; screenshots do not measure its cause.

Selection flow: first click selects and opens summary; Details opens inspector without selection/camera/history changes; Back returns to summary; close clears selection, as existing close did. A different record returns to summary; same-record language/time changes preserve current presentation and disclosures. Point cards use existing coordinates, region clicks use renderer-only click position; regions selected from chooser/history use an explicitly screen-positioned summary, not a made-up centroid. Summary retains temporal/applicability/source limitations.

Acceptance: semantic regression checks, UI-state tests, distinct reviewer, actual post-fix rendered screenshots and interaction checks. An unavailable WebGL-capable browser must remain a named blocker, not a passing visual result.

## Owner startup failure and bounded recovery

Owner screenshot `evidence/compact-selection-20261010/03-owner-startup-failure.png` (2048 × 1039, browser chrome; CSS viewport/DPR unknown) shows the delivered deba72c preview at localhost4174 with disabled initial markup, a full header, no map and an uninitialized blue range track. It does not show a successful corrected render. The browser loading indicator and parser-blocking CDN engine dependency are consistent with a pending upstream request, but no owner network/console evidence establishes the cause.

The bounded correction retains MapLibre 5.24.0 and all source/model bytes: ship upstream JS/CSS plus complete license and checked distribution manifest locally; emit local content-hash URLs; report missing scripts, data failures/timeouts and WebGL failure; keep failure visible until reload and require both presentation adapters. The startup wait message remains until first renderer idle. Before range values are painted, show a neutral track rather than a false full selection. This is a packaging/startup recovery within the already authorized workspace task, not an engine change, new feature domain or performance/cutoff acceptance.

Full application entry points are exercised with a DOM port from the actual HTML template; renderer construction/events and viewport are stubbed. Code/build checks and distinct review remain separate from owner WebGL/native acceptance.

## Server-free owner review after verified connection reset

Owner console evidence `evidence/compact-selection-20261010/04-owner-connection-reset.png` shows `net::ERR_CONNECTION_RESET` while loading local runtime.js. Earlier owner server logs showed HTTP200 for both engine/runtime, and the engine directory listing contained all four pinned files. HTTP200 does not establish receipt of the complete body. This establishes an asset-transfer failure, not its cause; no firewall/antivirus/browser-protection change is proposed.

Within the existing authorized startup correction, a separate unstamped build may be packaged as local-review-only `ARTEMIS.html`. Exact pinned JS/CSS/license bytes are inline, four startup JSON artifacts are embedded as base64 preserving original UTF-8 bytes, and the same runtime reads these inert elements before its existing fetch path. Initial HTML has no external script/stylesheet/preload dependency. Standard index/network delivery remains available. This is a review delivery variant, not an accepted release or new source/domain/renderer. Release-stamped builds are rejected by this packager; embedded metadata is a build snapshot, not new live release provenance.

At delivery, native file:// history, embedded Blob worker, WebGL/rendering, source links, card interactions and performance were pending. Original data, engine version, geometry and exact bundle identity remain unchanged. The reset cause, black globe cutoff and stutter are unresolved.

## Bounded owner acceptance — 2026-10-10

The owner replied “Да, принимаю.” and supplied a 2048 × 1048 desktop screenshot of the standalone `ARTEMIS.html` opened directly. It shows the rendered globe, compact records and explicit Details panels, and a single highlighted range track. The current preview is owner-accepted; [the acceptance receipt](evidence/compact-selection-20261010/owner-acceptance.md) binds the delivered artifact and describes the observable state.

This closes the missing-render blocker for the standalone preview, without promoting all native checks to PASS. Card placement/Details/Back interaction, keyboard/mobile, coincident range handles, history traversal/source links, dedicated worker diagnostics, cutoff diagnosis and measured gesture performance remain unverified. Existing independent code-review receipts retain their original verdicts. No product gate, release/publication or user-value disposition changes. At acceptance, merge remained paused; the subsequent authorization below supersedes that hold.

## Owner merge authorization — 2026-10-10

The owner explicitly instructed “Подтвержадю merge.” This lifts the task-specific merge hold and authorizes delivery of the accepted changes through the existing PR workflow, subject to current-head independent review, required CI and repository protections under Development Operating System §6.6. It does not mark remaining native/performance checks as passed. PR #480 currently contains the earlier `20d47847d18873076d799da2643eb73a33c78ae7` revision; its successful CI does not cover the later desktop/compact/startup/standalone changes. Upload, new-head CI, review and merge are still to be verified.

Delivery blocker: direct git push lacked credentials. The connected GitHub accepted seven text blob objects, but automatic approval review rejected screenshot upload for possible private UI/path disclosure. The safer public tree excludes all five newly added images, retaining textual provenance and hashes. Automatic approval review then also rejected documentation upload, stating that merge approval did not explicitly authorize disclosure of local paths, evidence identifiers and external artifact references. No tree/commit/ref update or merge was performed. A text/code-only patch package is prepared for explicit payload/destination publication approval; no retry through an alternate route is authorized by this receipt. Existing independent review accepts code conformity subject to required current-head CI.
