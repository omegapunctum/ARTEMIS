# Author standalone-review verification — 2026-10-10

Implementation: `0dd5f4a23e0c777cc4fe398297d9d8ce789f6c3c`.
Owner evidence: `04-owner-connection-reset.png`, 2048 × 948, records ERR_CONNECTION_RESET on runtime.js. Earlier engine onerror and HTTP200/directory listing establish neither a missing engine nor complete response transfer. The reset cause remains unknown.

## Executed checks

- Targeted standalone, full entry-point startup, canonical selection/history and mobile checks: 7 passed in 26.94s. Subsequently added stamped-release rejection guard; its targeted regression passed in 3.94s. No complete single-run 8-test rerun is claimed.
- Full shipped-script DOM-port startup includes an embedded-data scenario at a file:// URL. Every fetch attempt throws in this scenario, yet normal application setup reaches the stubbed Map constructor, mounts adapters and paints the range. Viewport, Map events and renderer are stubbed. No actual engine, file-origin worker, browser history or WebGL pass is claimed.
- Standalone tests recover every embedded JSON payload byte-for-byte, every inline JS/CSS/license byte-for-byte and expected script order; reject altered runtime, missing startup script and release-stamped input before replacing an existing standalone artifact.
- Production build PASS: 55 registry records, unchanged bundle SHA-256 `a0c2046ea0862683167aef3b6d5f4b496a36fcabb0b2dcaa595c4534f91d5538`.
- Node runtime syntax and git diff whitespace checks passed.

## Exact delivered artifact

`ARTEMIS.html`: 4,493,206 bytes; SHA-256 `3d3d29fc513aa84600ac47b63714436cd65528a05df5deed6161ec9f9d2e4094`.

`ARTEMIS-standalone-preview-20261010.zip`: 68 files, 2,536,907 bytes; SHA-256 `59dc282ac7fd410fe6f56f489e3047dd731c8acd01a7d7e815dde342025a6143`.

Delivery-byte checks: actual HTML has no startup script/stylesheet/preload URL, its embedded scripts/styles equal implementation/build bytes, all four decoded JSON inputs equal their compiled artifacts and full license equals pinned upstream bytes. Archive CRC and every archive member against the delivery directory passed. Engine/source/input artifacts are retained beside the standalone HTML for existing local provenance links. The network index is also retained, but the owner's review instructions explicitly open ARTEMIS.html directly.

## Limits

This is a separately built, unstamped, local-review-only artifact. It is not publication, release-manifest verification or new live release provenance. Embedded build-meta is a preserved build snapshot. The packager rejects stamped builds.

Actual file:// WebGL/Blob-worker/history and source-link interactions, compact cards and responsive/native range behavior remain pending. Reported globe cutoff/stutter and reset cause are unresolved. No firewall/antivirus/browser-security change, external upload, push, merge or publication performed. Owner merge hold remains.
