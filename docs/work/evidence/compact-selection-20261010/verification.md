# Author verification — compact selection, 2026-10-10

Implementation: `deba72ca6116d872abdaba315528a43ceec7eaaf`.
Independent review: `review.md`, ACCEPT_CODE_CONFORMITY_PENDING_NATIVE.

## Executed checks

- Owned suite: `python3 -m pytest -q tests/test_cesena_input_amendment.py tests/test_unified_explorer.py tests/test_mobile_explorer.py tests/test_unified_explorer_browser.py` — 38 passed in 16.48s. Subsequent changes were limited to native harness Back/hit-test/capture steps and passed Node syntax checks; these native scenarios were not executed.
- Runtime, desktop and changed native harness syntax checks passed; `git diff --check` passed.
- Production build completed with 55 shared registry records. Bundle SHA-256 remains `a0c2046ea0862683167aef3b6d5f4b496a36fcabb0b2dcaa595c4534f91d5538`.
- Built runtime, desktop, mobile and stylesheet bytes match implementation sources.
- Delivery ZIP CRC and every packaged file against the built directory passed. CRC and final archive digest checked again at delivery.

## Delivery

`ARTEMIS-compact-preview-20261010.zip`, 1,068,721 bytes.
SHA-256: `0ff40a24d6cf9891bb1e36aad301bb281a38b131c681f0680b082734390d9367`.
Includes the prebuilt app, Russian review instructions and `Start-ARTEMIS.cmd`, using the owner's installed Python path and localhost port 4174. No dependency installation or rebuild is required. MapLibre CDN requires connectivity.

## Limits

This is author build/package evidence, not an independent native browser acceptance. Current-head WebGL rendering, popup footprint/focus, actual gesture smoothness, responsive transitions and native range controls remain pending. The reported horizontal globe cutoff is unresolved. Reduced configured rendering work is not a measured performance improvement.

Owner Windows rebuild previously produced 55 records with a different bundle digest; cross-platform byte/path reproducibility remains unresolved. This prebuilt archive avoids a rebuild but does not resolve that issue.

No push, merge or publication performed. Owner merge hold remains in force.
