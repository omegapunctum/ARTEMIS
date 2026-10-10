# Author startup/package verification — 2026-10-10

Implementation: `6b313ea3190c4c22ed0eeb38058363776b6980b8`.
Scope: recovery of the delivered preview's failed initial startup; no engine version, geometry or source corpus change.

## Observations versus hypothesis

Owner screenshot `03-owner-startup-failure.png`, 2048 × 1039, shows initial disabled controls/full header/no globe at localhost4174. Its loading indicator and parser-blocking CDN request path are consistent with an upstream wait, not proof of its cause. No owner console/network report is available.

Upstream MapLibre 5.24.0 JS/CSS were retrieved from the versioned unpkg distribution, and the complete license from the version-tagged upstream repository. JS/CSS digests independently match previously available local distributions. Exact digests and URLs are in the checked `engine/manifest.json`. `.gitattributes` preserves these upstream bytes on Windows; it does not resolve the separately recorded cross-platform source-bundle reproducibility issue.

## Executed author checks

- Affected suite: `tests/test_unified_explorer.py tests/test_mobile_explorer.py tests/test_unified_explorer_browser.py`: 23 passed, 1 failed in 43.44s. The failure was the new test accessing an absent runtime global in its deliberately missing-runtime scenario, not shipped behavior. Fixed that assertion; the affected startup test then passed in 5.42s. No single full-suite clean rerun is claimed.
- Complete application entry-point DOM port: `EXPLORER_STARTUP_BEHAVIOR_PASS`, covering adapter reparenting, calculated interval track, wait/ready status, sticky failure, missing engine, WebGL constructor failure, data connection failure, timeout, HTTP404 and missing mobile/desktop/runtime scripts. Actual template is parsed into the port. Map constructor/events and layout are stubbed; real vendor-engine execution/load/idle/rendering are not proven.
- Runtime/startup syntax and `git diff --check`: pass.
- Production build: PASS, 55 shared registry records; unchanged bundle SHA-256 `a0c2046ea0862683167aef3b6d5f4b496a36fcabb0b2dcaa595c4534f91d5538`.
- All built application script/style bytes equal reviewed source. Engine JS/CSS/LICENSE bytes match manifest. Every entry HTML script/stylesheet URL is local and points to a present file; no unresolved template token.
- Same-process Python standard-library HTTP server serves exact HTML, startup/runtime scripts, local engine JS/CSS and bundle bytes: `LOCAL_HTTP_BYTES_PASS`.
- Attempted separate long-running test-server connection and cloud browser navigation to localhost4175 returned connection refused. No browser render acceptance is claimed. Same-process HTTP proof does not show that the separate cloud browser can reach the app.

## Delivery archive

`ARTEMIS-startup-preview-20261010.zip`, 68 files, 1,347,900 bytes.
SHA-256: `87f7d9141322d48200f3062a07917d1bb94f528824334dfe92f581d08cb0b551`.
CRC pass; every packaged file byte-compared with the built directory. Prebuilt app includes pinned local engine, full license/manifest, Russian review instructions and Windows launcher for owner's installed Python at localhost4175. No CDN, dependency installation or rebuild is required for startup. Source links separately require internet.

Native load/idle, compact cards/focus, responsive transitions, actual range gestures, reported horizontal globe cutoff and real performance remain pending. Owner merge hold remains; no push, merge or publication.
