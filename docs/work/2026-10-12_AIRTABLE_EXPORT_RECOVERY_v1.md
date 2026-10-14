# Airtable export recovery — 2026-10-12

## Authority and scope

Owner accepted restoration of the existing Airtable export, retaining its integrity
checks, on 2026-10-11. Classification: AUTO under Development Operating System §6.1
(CI repair restoring existing behavior). Baseline: `3089b09`.

This task restores the Architecture Atlas export path. It does not authorize writes
to Airtable, historical imports, temporal-model changes or modifications of frozen
evidence. Implementation and live export success are separate receipts.

## Diagnosis and repair

Export run `38136881796` stopped before Airtable access because the history scanner
interpreted the Cliopatria source revision as an ARTEMIS commit. Its source manifest
explicitly binds revision `ad28a691b7c07c1fca89d0e0636d324667d2a258` to the external
Seshat Cliopatria repository. This revision must not be rebound to local history.

The scanner now recognizes only that exact manifest path and repository/revision
pair. It rejects changed bindings and excludes only the external top-level `commit`
from local lookup. All nested and other commit references retain local fail-closed
checks. Unknown repositories do not create exemptions. Frozen fixture bytes and
source hashes are unchanged. Existing Region excerpt checksum tests remain active.

The export runs a broader pytest contour than Core CI. Its attractor-refinement
contract test still expected Gate D to be open. Those stale current-state assertions
are aligned with canonical completed Gate D / ADVANCE_TO_GATE_E and the later
Gate E owner-directed closeout; foundation and capability invariants remain checked.
The three Airtable offline validators accept the separate, explicitly referenced
Gate D exit decision while retaining the frozen Gate C package, zero historical
records, preflight-only status and blocked historical writes. No lifecycle decision
is changed.

The first completed workflow contour exposed six progressive-refinement failures
(1195 passed, 3 skipped). Five cascaded from the accepted PR #472 Cesena extension
to the refinement contract, which was absent from the historical digest normalizer;
the sixth still expected mutable lifecycle routing in AGENTS rather than the work
registry. The normalizer now removes only that exact additive paragraph extension
when comparing original v1 semantics to the unchanged frozen digest. Altered
extension wording, changed original semantics and all other content still fail
integrity comparison. The lifecycle assertion now uses the work registry. No
frozen bytes, recorded hashes, reviews or acceptance identity are regenerated.

## Verification

- `validate_ci_evidence_history.py`: PASS, 20 local frozen commits resolved.
- `release_check.py`: PASS, all seven lanes (memory-session single-node warning).
- Focused history, Airtable and attractor tests: 42 passed.
- Full workflow non-Redis pytest contour: PASS on implementation `5bbdf14`,
  1205 passed, 3 skipped (Python 3.12 local runtime; remote workflow uses 3.11).
- Follow-up refinement contour: 80 passed, including exact-extension and three
  negative semantic-change checks; original frozen reviewed digest unchanged.
- Distinct-agent exact-commit review of `2970b69` and the follow-up `5bbdf14`:
  ACCEPTED with no blocking findings; release gate and history rerun PASS.

## Delivery boundary

Remote delivery remains blocked. Automatic approval review rejected branch push
to `omegapunctum/ARTEMIS`, stating that transmitting repository contents lacked
end-user authorization naming that repository and disclosure. No retry or
alternate upload was attempted. The latest observed live export, run
`38502419048` on unchanged `main` `3089b09`, failed at frozen evidence history;
Airtable export was skipped. Local implementation success is not a live-export
receipt. No Airtable writes or fixture/data modifications were performed.
