# Leonardo First-Use correction — implementation/publication closeout

- Date: 2026-09-20.
- Type: completed implementation, human acceptance and publication evidence; not participant evidence.
- Scope/authority: issue #355; [accepted First-Use specification](2026-09-19_LEONARDO_FIRST_USE_COMPREHENSION_CORRECTION_v1.md) and [Gate E recovery specification](2026-09-19_GATE_E_EVIDENCE_RECOVERY_SPEC_v1.md).
- Implementation: [PR #439](https://github.com/omegapunctum/ARTEMIS/pull/439), reviewed head `782f4064b5c9e965c36f9fd2d21f4136090a3f5c`.
- Human presentation acceptance: owner explicitly replied “Подтверждаю. Произведи merge.” in the implementation task after the complete PR/evidence handoff. This satisfies the REVIEW boundary only; no novice observation is inferred.
- Merge: `be992184f04f020bb7f769b980403d0899f0950b`. GitHub reported merged; expected-head protection was used. Required checks passed, no review threads or blocking reviews existed, and mergeability was true.

## Implemented boundary

Existing selected-Presence details now prioritize Place, native time, documented context and short explicit limitations. Existing source identities and locators are directly reachable, with the three accepted “Why these sources?” meanings. Prototype coverage is separate. The six life-period and eleven Presence rows are named; selected coarse context stays visible. Short active-mode explanations and episode-specific chronology emphasis preserve temporal semantics, fixed Place anchors, distinct repeat-visit identities and unknown/null historical routes.

No historical data/source selection, Claim/Evidence/Uncertainty semantics, Region integration, second temporal state or capability/value claim changed. Exact diff self-review found no unresolved implementation findings. Source contrast, locator separation and narrow-screen period visibility were repaired before acceptance.

## Technical verification

At the reviewed head:

- [Core run 35504966105](https://github.com/omegapunctum/ARTEMIS/actions/runs/35504966105): SUCCESS, 320 tests passed in 28.93s, validators and public-preview build passed.
- [Globe run 35504966097](https://github.com/omegapunctum/ARTEMIS/actions/runs/35504966097): SUCCESS, 44 tests passed in 23.95s, existing desktop/tablet/hosted-mobile browser gates and separate Region gate passed.
- [Boundary run 35504966108](https://github.com/omegapunctum/ARTEMIS/actions/runs/35504966108): SUCCESS.
- [Browser artifact](https://github.com/omegapunctum/ARTEMIS/actions/runs/35504966097/artifacts/10602774727): captures of initial view, details, supporting sources, source-scope explanation, RU details and separate coverage for all three profiles, plus JSON provenance. Artifact retention ends 2026-09-27; SHA-256 `55d144e0fc8d439996bde9ba74233e660affe70ef0660664bb9b95d574079cec`.

Requested hosted windows: 1440×900, 1024×768, 500×844; actual Leonardo viewports: 1440×757, 1024×625, 500×701. Mobile used reduced motion. These are automated browser profiles, not real-device or full assistive-technology validation.

Local full Core verification initially showed five Windows uncertainty Git/digest/symlink-privilege failures; all five reproduced on unchanged base `0422d34`. Final Linux CI passed all 320. Frozen source bytes were not changed to accommodate Windows CRLF.

## Live publication verification

[Pages run 35505714814](https://github.com/omegapunctum/ARTEMIS/actions/runs/35505714814) deployed merge `be992184f04f020bb7f769b980403d0899f0950b` successfully; its published Region retest also passed.

The actual [public Leonardo runtime](https://omegapunctum.github.io/ARTEMIS/globe/) was checked on 2026-09-20. Live files equal the corresponding Git blobs at that merge byte-for-byte:

| File | Live SHA-256 |
|---|---|
| `runtime.js` | `327c271518b9a91bd6d9a1fc05b8f7dbb69196aff466ed4c089e44b1b84c020d` |
| `style.css` | `a1e827ef31915c964e527aa73c06125fa1dca5b718e1de149d2b32a6c32cfc0e` |
| `localization.js` | `3b39e7942ab6bfc760f4221451258224d90f88fc6b0bc0cd058f21b563c1d0d4` |

Live HTML equals the generated public-preview HTML after normalizing Windows line endings; live HTML SHA-256 is `a0c23b23ebfa16077b9c0e5d2d4565c6110362757f5498574cceb07e6012a8da`. Build metadata declares `public_r_and_d_preview`. Metadata has no embedded deployment SHA; revision verification rests on the successful SHA-bound Pages run and the asset equality above, not an invented metadata field.

The existing browser evidence harness ran directly against the public HTTPS URL, with no local asset substitution. Completed at **2026-09-20T10:42:13.612Z**, Edge 153.0.4234.48, requested desktop window 1440×900 (actual viewport 1410×758), EN/RU. Result: PASS for all 11 episodes, first-open hierarchy/limits, source titles and locators, the three source-scope meanings, separated collapsed global coverage, selected period/row/anchor/details/URL coherence, null historical routes, compact mode explanations, native source-disclosure keyboard activation and existing URL/camera/keyboard restoration assertions.

The live report identifies test checkout `be992184f04f020bb7f769b980403d0899f0950b`; checkout identity alone is not deployment proof. Initial DOM SHA-256: `723d74468ed89c24c6528d9d3aa7cb55f5f6421b58da59607c2a12d62472a82a`; initial screenshot SHA-256: `70ce84ba9dc50ab242ed972713dd6220253bb6ef8314346a577f8a8ebc3d1e5b`. Automated evidence still records visual acceptance as `not_assessed`; human acceptance is the separate owner statement above.

## Handoff

Implementation, human REVIEW acceptance, merge and publication verification are complete. **Fresh E1 is the next authorized transition**, using one consenting independent novice unfamiliar with the implementation. Do not reuse the earlier exploratory reviewer as a naive participant.

**E1 = NOT COLLECTED; E2 = NOT COLLECTED; formal user value = UNVALIDATED.** No E1 was conducted, simulated or scored. The single pre-E1 product-correction allowance is consumed; another material product correction after fresh E1 is escalation. E2 remains conditional on E1 clearance and requires exactly five participants, followed by the final human Gate E decision.
