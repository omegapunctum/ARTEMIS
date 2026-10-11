# Explorer zoom performance — 2026-10-11

Status: active bounded diagnosis; no improvement or owner-device resolution claimed.

Authority: owner reports severe slowdown when approaching objects and explicitly accepts the bounded autonomous cycle “smooth map exploration while approaching objects”. Class REVIEW under `DEVELOPMENT_OPERATING_SYSTEM.md` §6.2. Baseline: merged main `ea96a3d56cf1b05a3be7fbff63570b914757c34b` (PR #480). Its green CI does not establish owner-device performance.

## Scope and invariants

Reproduce zoom toward existing architecture references; identify and measure avoidable CPU/render work; implement the smallest reversible correction supported by evidence. Preserve all 55 registry identities, bundle/source bytes, geometry, temporal applicability, uncertainty, selection, URL/state, native picking and the persistent map. Do not change renderer density, visual quality or source semantics without a recorded reviewed decision. Construction/existence dates and phase styling are a separate future task, not authorized implementation here. No broad renderer rewrite or corpus expansion.

## Measurement and acceptance

Use identical bundle, engine and viewport for before/after comparisons. Include native wheel zoom toward the architecture cluster, Globe and 2D, with no selection and an open compact card. Record zoom endpoints, frame intervals/long tasks, relevant script/layout/render counters and scene identity. Attribute observed work separately from hypotheses; software-rendered CI measurements are not owner-device FPS. Keep negative results and sampling/environment limitations visible.

Accept a correction only with a measured reduction of its targeted unnecessary work, unchanged semantic/picking/state invariants, relevant regressions and independent exact-head review. Existing required CI/merge policy applies. Verify publication separately when delivering a release. Stop after the bounded result and honest remaining limitations, or at a documented access/semantic blocker; no automatic architecture-time successor.

## Baseline receipt

PR #480 merged as `ea96a3d`; implementation/source tree matches its final accepted head. PR Core 38109571535, push Core 38109569161, boundary 38109571545 and geospatial 38109571539 succeeded; push reports 438 tests and all four native viewport scenarios. These supersede prior delivery-blocked/old-head statements in the compact-selection receipt, but do not resolve the new zoom report or prove live publication.
