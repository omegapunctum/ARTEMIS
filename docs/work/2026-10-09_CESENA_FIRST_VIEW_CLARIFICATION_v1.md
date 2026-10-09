# Cesena first-view clarification — 2026-10-09

Class: REVIEW. Owner: Product Scope, information hierarchy appendix. The owner continued after the independent audit recommended resolving Cesena's ambiguous first-view wording. Merge remains paused.

Question: how to preserve the literal candidate description without implying that the narrowed presence Claim establishes surveying? Replacing frozen text would exceed scope; leaving it unqualified preserves the ambiguity. Preferred action: an adjacent EN/RU first-view notice before the unchanged original description, scoped to `event-leonardo-cesena-survey`.

Scope acceptance: distinct reviewer `/root/hierarchy_review` returned `ACCEPT_SCOPE`. The notice must not promote the presence Claim from draft, declare surveying historically false, or generalize the rejection of one survey-folio association. All original data, Sources, Claims, statuses, temporal/spatial fields, identity, chooser and title remain unchanged. No corpus, editor, error-handling or product-gate successor is opened.

Acceptance: owned composition/behavior and Cesena amendment tests; native harness assertions for visible first-view notice, unchanged original description, EN/RU change and absence on other records. Compare composed bundle identity with the accepted baseline. Distinct final implementation review is required. Browser evidence not executed on this revision must remain explicitly pending; previous screenshots cannot establish current layout.

Stop after this bounded local correction and review. Remote publication, new-head CI and merge are separate delivery steps; the owner's merge hold remains in force.

## Local verification

35 owned tests passed (unified composition/behavior, browser-harness contracts and Cesena amendment) in 24.12 seconds. Both changed JavaScript files pass syntax checks. A full public Explorer build retains 55 registry records and exact bundle SHA-256 `a0c2046ea0862683167aef3b6d5f4b496a36fcabb0b2dcaa595c4534f91d5538`, matching the accepted pre-correction bundle. The smaller unit-test fixture is not the public build and is not used as its identity.

Native first-view EN/RU/other-record assertions have been added but have not been executed on this revision. The available cloud browser cannot initialize WebGL; its earlier failure screenshot is evidence of that limitation, not evidence of this changed card. Visual acceptance, remote new-head CI and publication remain pending.

## Remote baseline check

PR #480 remains open and unmerged at `0110370aa786de032b0b894b813eff4fc047d87f`. All six PR/push Core, Geospatial and Repository Boundary runs on that head now report SUCCESS, including PR Core `37916102050` and push Core `37916098046`. These results cover the earlier information-hierarchy correction, not the new Cesena clarification. The new runtime/harness commit is `fe79bea575a8fb33b300da9343227486489a532c`; its remote CI and native evidence remain pending.

## Independent code review

Reviewer `/root/hierarchy_review` returned `ACCEPT_CODE_CONFORMITY_PENDING_NATIVE` on exact implementation head `fe79bea575a8fb33b300da9343227486489a532c`: no unresolved critical/material code findings; event identity matches exactly one existing Presence, the original description and shared bundle are unchanged, and EN/RU qualification does not promote the presence Claim or declare surveying false. This is code conformity only. New native visual evidence, current-head remote checks and public delivery remain pending.

The previous automatic external upload was rejected by approval review. No retry or alternative upload is attempted here. Prepare an incremental git bundle based on the current remote `0110370` for the owner's established manual delivery route; the bundle does not perform a merge.
