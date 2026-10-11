# Explorer zoom performance — 2026-10-11

Status: laboratory diagnosis complete; delivery subject to exact-head review/CI. Owner-device slowdown remains unresolved. No production optimization is included.

Authority: owner reports severe slowdown when approaching objects and explicitly accepts the bounded autonomous cycle “smooth map exploration while approaching objects”. Class REVIEW under `DEVELOPMENT_OPERATING_SYSTEM.md` §6.2. Baseline: merged main `ea96a3d56cf1b05a3be7fbff63570b914757c34b` (PR #480). Its green CI does not establish owner-device performance.

## Scope and invariants

Reproduce zoom toward existing architecture references; identify and measure avoidable CPU/render work; implement the smallest reversible correction supported by evidence. Preserve all 55 registry identities, bundle/source bytes, geometry, temporal applicability, uncertainty, selection, URL/state, native picking and the persistent map. Do not change renderer density, visual quality or source semantics without a recorded reviewed decision. Construction/existence dates and phase styling are a separate future task, not authorized implementation here. No broad renderer rewrite or corpus expansion.

## Measurement and acceptance

Use identical bundle, engine and viewport for before/after comparisons. Include native wheel zoom toward the architecture cluster, Globe and 2D, with no selection and an open compact card. Record zoom endpoints, frame intervals/long tasks, relevant script/layout/render counters and scene identity. Attribute observed work separately from hypotheses; software-rendered CI measurements are not owner-device FPS. Keep negative results and sampling/environment limitations visible.

Accept a correction only with a measured reduction of its targeted unnecessary work, unchanged semantic/picking/state invariants, relevant regressions and independent exact-head review. Existing required CI/merge policy applies. Verify publication separately when delivering a release. Stop after the bounded result and honest remaining limitations, or at a documented access/semantic blocker; no automatic architecture-time successor.

## Baseline receipt

PR #480 merged as `ea96a3d`; implementation/source tree matches its final accepted head. PR Core 38109571535, push Core 38109569161, boundary 38109571545 and geospatial 38109571539 succeeded; push reports 438 tests and all four native viewport scenarios. These supersede prior delivery-blocked/old-head statements in the compact-selection receipt, but do not resolve the new zoom report or prove live publication.

## Diagnostic implementation and interpretation

`scripts/capture_explorer_zoom.mjs` uses native CDP wheel input over Tower Bridge, zoom 3 → approximately 14 → approximately 3, in the existing Globe or 2D presentation. It records actual wheel counts/endpoints/trajectory, frame intervals by moving zoom band and explicit inbound/outbound leg, long tasks, CDP script/layout counters, source events, input hashes, registry/visible identities, persistent map/document and non-camera state. `--selected true` selects the target by native click before measuring with its compact card open. Optional screenshots and CPU profiling add overhead and are explicitly recorded.

Example (build first; ARTEMIS_BROWSER points to an installed Chromium executable):

```sh
python -m scripts.build_unified_explorer --output /tmp/artemis-zoom/globe
node scripts/capture_explorer_zoom.mjs --browser "$ARTEMIS_BROWSER" --artifact /tmp/artemis-zoom --output /tmp/artemis-zoom-results --view globe --repetitions 2
```

Repeat with `--view map`, or `--selected true`. `--hide-context true` is diagnostic-only: it hides the Earth fill; it is not a product proposal or proof isolating all source processing. Default product rendering is unchanged. This is a manually invoked diagnostic, not a new required CI performance threshold.

Frame intervals cover the interaction including input pacing/settlement, not GPU-only time. Moving-band classification uses the zoom, active leg and moving state at the end of each frame interval. Schema v2 records the leg on every frame sample and reports inbound and outbound bands separately; pooled legacy bands describe only the round trip. Adaptive input can overshoot endpoints; elapsed totals are not fixed-path benchmarks. Reloaded repetitions do not prove a warm tile-cache case. `success` means scenario and preservation assertions completed; browser diagnostics must also be inspected. Headless Chromium 134 with SwiftShader, 1440×900/DPR 1, is a laboratory comparison only. Owner-device performance, pinch gestures, other GPUs/browsers and high DPI remain unvalidated.

## Bounded decisions

- Old performance evidence moves camera center/bearing at nearly constant zoom; it cannot establish responsiveness when approaching objects. Keep that evidence as historical, with this limitation.
- Do not ship `earth-context maxzoom:6`. A scratch-only experiment reduced source event count, but did not establish an improvement in total time/script work and changes displayed coordinate precision when overzoomed. Same input bytes are insufficient visual equivalence. No source maxzoom, geometry, quality, density or runtime implementation change is included.
- Attempts to detach markers through unexposed runtime/private properties failed during diagnostic setup; these are not performance evidence. The unsupported intervention was removed from the delivered runner.
- Deliver the reproducible zoom diagnostic and evidence. A close-zoom-specific owner regression must not be declared fixed from these software-rendered results. No automatic temporal-architecture successor is authorized by this receipt.

## Evidence and result

Raw reports and frame samples: [evidence/2026-10-11_zoom](evidence/2026-10-11_zoom); `summary.json` indexes the runs. Runtime/source hashes identify the exact PR #480 artifact; only `z6.json` uses the disclosed scratch runtime intervention. The exploratory first/hidden/z6 reports precede final runner refinements and must not be treated as identical-instrumentation benchmark pairs. The six reports named final-* belong to the pre-direction diagnostic revision 6ece2b4; final Globe no-selection runs additionally predate selected-mode metadata. They remain round-trip evidence, not new schema-v2 evidence. Baseline reports that used registry array indices are exploratory only; final reports record all actual item IDs.

| Legacy round-trip scenario (both directions pooled) | Repeats | Moving frame p95, zoom 3–6 | Moving frame p95, zoom 10–15 |
| --- | ---: | ---: | ---: |
| Globe, no card | 2 | 667–700 ms | 100–117 ms |
| 2D, no card | 2 | 83–100 ms | 67 ms |
| Globe, compact card | 1 | 500 ms | 83 ms |
| 2D, compact card | 1 | 100 ms | 67 ms |

These are rounded descriptive laboratory samples, not device FPS or a statistically established causal effect. The Globe card run enabled screenshots; its elapsed total is not directly comparable. All final scenarios completed with 22 inward and 22 outward wheel events, reached approximately 14.07 and 3, preserved state/map/document and recorded no browser errors. Both selected runs selected Tower Bridge through native picking and retained its exact identity. The high-zoom compact-card screenshot was inspected: card, Details button and selected point are visible; no historical lifetime is inferred.

The legacy table pools both directions, so it cannot locate a penalty specific to approaching an object. The previous approach-specific interpretation is withdrawn following PR review #4241017571. The owner's specific close-zoom slowdown is not established or resolved. 2D is a useful comparison for reproduction, not an automatic product-mode replacement. Next action: obtain the owner's affected device/browser, view mode, target and gesture, then reproduce/profile that exact case. This closes the bounded laboratory exploration without opening speculative runtime work or temporal-model implementation.

Verification: builder PASS (55 records, unchanged digest); runner syntax PASS; repository governance tests 7 passed; six final native zoom repetitions passed. An additionally invoked legacy concept-lock suite produced 6 passes/1 failure because it expects an obsolete Gate D string in `VALIDATION_DECISION.md`; that test and its two input documents are byte-identical to baseline `ea96a3d`, and it is outside the required Core suite. No unrelated lifecycle text was altered to satisfy that stale assertion. Independent exact-head review and required CI are delivery gates, recorded on the PR separately.

## Directional review correction

PR inline review 4241017571 correctly identified that pooled inbound/outbound bands do not establish approach-specific behavior. Schema v2 tags each rAF sample with the active leg, set before input begins and switched only after the previous leg settles. `movingZoomBandsByDirection.in` and `.out` are computed independently; pooled values remain solely for legacy round-trip comparisons. No leg is inferred retrospectively for old evidence.

Fresh schema-v2 evidence: `evidence/2026-10-11_zoom/directional-globe.json`, one unselected Globe repetition, same baseline runtime/source inputs, screenshots/profiling disabled. Inbound used 22 wheel events and ended at 14.0697; outbound used 23 events and overshot to 2.4968 (within the one-sided ≤3.2 completion predicate). Map/document/non-camera invariants and 55 identities pass; browser errors are empty. This is not a fixed-distance benchmark; the old 22/22 and approximately-3 statements do not apply to this run. The six prior cases retain their explicitly legacy status. This one fresh run verifies the changed measurement path; it does not repeat unchanged selection/presentation logic.

| Direction | Zoom 3–6: count / p95 | Zoom 6–10: count / p95 | Zoom 10–15: count / p95 |
| --- | --- | --- | --- |
| Approach | 13 / 1050 ms | 39 / 383 ms | 35 / 200 ms |
| Retreat | 18 / 967 ms | 32 / 133 ms | 37 / 167 ms |

These are small single-run samples (the approach low-zoom p95 is the largest of only 13 observations), not a repeatable device-performance conclusion. This run has larger low-zoom intervals in both directions; neither the old pooled evidence nor this laboratory observation resolves the owner report. No product optimization is added. The next action remains reproduction in the affected desktop browser and gesture, as the owner confirmed the issue occurs on a computer.
