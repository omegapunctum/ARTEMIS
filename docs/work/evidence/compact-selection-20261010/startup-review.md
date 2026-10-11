# Independent startup/local-engine review — 2026-10-10

Verdict: **ACCEPT_CODE_CONFORMITY_PENDING_NATIVE**.

Exact implementation reviewed: `6b313ea3190c4c22ed0eeb38058363776b6980b8`, on `feat/desktop-workspace-20261009`. Distinct reviewer: `/root/hierarchy_review`, under Development Operating System §6.2. Scope is the owner-authorized startup recovery, local delivery of the existing pinned engine and neutral initial timeline track. This receipt is the reviewer's only repository edit for this revision; no implementation edit, commit, publication, external message or merge was performed. The earlier `deba72c…` compact-selection receipt remains historical.

## Code and packaging findings

No unresolved material code-conformity finding remains in this bounded correction. The template loads a local startup guard before local engine/mobile/desktop/runtime scripts. Existing MapLibre 5.24.0 is retained; this is a delivery change, not an engine upgrade. The builder validates engine identity and the JS/CSS/license byte hashes before replacing an existing output, copies all engine assets and the manifest, binds runtime resource URLs to their actual hashes and records local-engine delivery metadata. The full license is included. Independent file hashing matches the checked manifest; upstream retrieval provenance is author-supplied, not a separately performed reviewer download.

`.gitattributes` marks `scripts/unified_explorer/engine/* -text`; independently checked JS/CSS/license attributes are unset for text conversion. This preserves the pinned upstream distribution bytes against Git newline conversion on Windows. It does not resolve the previously reported Windows/Linux historical-bundle hash difference.

Local data requests have a 15-second abort bound covering response-body JSON processing, HTTP diagnostics and timer cleanup. Missing required mobile/desktop adapters are rejected explicitly. Script errors, startup exceptions, rejected promises and map errors expose a diagnostic; failures remain sticky when later phase/readiness calls arrive. Readiness now follows the first map idle callback and the existing runtime/visual flags, rather than map construction. The 20-second watchdog reports the pending phase without inventing a failure cause. The timeline receives its blue interval only after canonical endpoint values are painted.

Earlier review findings are addressed: a late readiness call cannot erase a failed diagnostic; missing workspace adapters cannot silently continue; readiness no longer hides the startup notice before the first idle callback. The missing-runtime test's optional-state access is corrected and independently passes.

## Independently executed checks at the reviewed commit

- `test_full_startup_reaches_map_and_reports_failures`: **1 passed in 4.54s**.
- `test_corrupt_engine_does_not_replace_existing_build` and `test_preload_and_cache_urls_bind_actual_resource_bytes`: **2 passed in 8.19s**.
- `node --check` for `startup.js`, `runtime.js` and `tests/explorer_startup_behavior.cjs`: exit 0.
- Engine JS/CSS/license SHA-256 comparison to the manifest, `git check-attr text` and `git diff --check`: pass. HEAD was the exact SHA above and the worktree was clean before this receipt.

The entry-point test parses the actual template and executes shipped startup/mobile/desktop/runtime scripts against a minimal DOM port. It covers successful initialization reaching the Map constructor and desktop reparenting/range painting, missing engine, WebGL constructor failure, network failure, timeout, HTTP error, missing mobile/desktop/runtime scripts and sticky failure. Its Map constructor, viewport, layout and Map events are stubbed. The successful scenario calls the startup readiness API explicitly; it does **not** independently execute native map load/idle, prove the runtime's real idle wiring, render the engine, or establish WebGL/CSS/network/visual acceptance. The code placement of readiness inside the real first-idle callback was inspected separately.

Author-executed evidence is distinct: the fixed targeted startup test passed in 5.42s, and the production build passed with 55 records and bundle SHA-256 `a0c2046ea0862683167aef3b6d5f4b496a36fcabb0b2dcaa595c4534f91d5538`. The earlier affected 24-test run had 23 passes and the subsequently corrected startup-test failure; this receipt does not claim a complete final-head 24-test rerun. Independent narrow build tests above do not constitute verification of the final delivery ZIP.

## Native, product and release limits

**Native/visual acceptance remains BLOCKED/PENDING. The horizontal globe cutoff and reported stutter remain UNRESOLVED.** The inspected owner screenshot is 2048×1039 and shows the earlier localhost:4174 page at initial markup with disabled controls, absent globe and a full blue range. It establishes the visible failure, not its network cause. A pending external CDN request is a hypothesis; no verified network trace establishes it. Local engine delivery removes that startup dependency without proving the owner's failure is cured.

The author reports that the current cloud browser's direct localhost:4175 connection was refused. There is no current-head rendered acceptance capture, executed updated native/high-DPI gate or measured performance evidence. Earlier WebGL-disabled captures and historical branch passes do not accept the changed product files. No cutoff correction, FPS improvement, complete owner-problem resolution, current-head remote CI, public delivery or merge is claimed. The owner's merge hold remains in force.

The next verifiable release step is to serve the byte-verified current package on the documented port in the owner's WebGL-capable browser, confirm current startup/readiness or record the new visible diagnostic, and execute the prepared compact-card/Details/Back/source/range/native checks. Diagnose the cutoff and measure movement separately. A prebuilt package avoids requiring an owner rebuild; it does not establish cross-platform corpus-byte reproducibility.

## Exact reviewed bindings

| File | SHA-256 |
|---|---|
| `scripts/build_unified_explorer.py` | `2876ff2dee2cc5914c639de256a6f4f083000395e80462861ec7a7220303712f` |
| `scripts/unified_explorer/startup.js` | `04bce6783243769a395cbd6f97c87493ffd410a8db9f38598210caf3d3783b19` |
| `scripts/unified_explorer/runtime.js` | `43f713c70f285dac00e52867f2d65e073141febb6a0dd20d5c18068fce9fb4aa` |
| `scripts/unified_explorer/index.html.template` | `47970b2fe83c406dc353b6185403e71c40984aadd5ad0120636007ce1e52906f` |
| `scripts/unified_explorer/style.css` | `a80a444c6be27d14bba82b57125f4e5719aa0d027db84a4cf9c3fc1959d21734` |
| `tests/explorer_startup_behavior.cjs` | `dcd34790915dbf2267c81ad83b42102a3c15d78fa39f70a57c07f2bd268713d1` |
| `engine/maplibre-gl.js` | `45a9b07a9189ce56054c620a947ccf41e291e58c95e9b61533b740aaa65ee5cb` |
| `engine/maplibre-gl.css` | `ab1e70d59ec40465bae7e7030da2f3ccf28133fd502e62bd598eefbadfd7a732` |
| `engine/LICENSE.txt` | `ee5fc05a0677eaf69601d2c7db0d9ecd6cc27c3abc1d0733bc9ed34707cf8ef2` |
| `engine/manifest.json` | `2267562695e0c4446c2c5d5c62e3f38642212211fcfabef19a8d189ea0d20c1e` |
| `03-owner-startup-failure.png` | `567a713dd3cf1a8ab5c0aa555d474ed8af490f42cabe2e96cbcf4d517f34f20c` |
