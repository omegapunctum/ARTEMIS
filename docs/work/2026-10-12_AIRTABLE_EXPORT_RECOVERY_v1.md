# Airtable export recovery — 2026-10-12

Current lifecycle synchronization — 2026-10-17: completed delivery and remaining
limits are recorded in [the factual closeout](2026-10-17_CURRENT_STATE_AND_DIRECT_ENTRY_v1.md).
This supersedes older pending-CI/upload/merge/publication wording below; dated
observations, failures and acceptance boundaries remain historical evidence.

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

Historical local delivery receipt: automatic approval review rejected branch push
to `omegapunctum/ARTEMIS`, stating that transmitting repository contents lacked
end-user authorization naming that repository and disclosure. No retry or
alternate upload was attempted. The latest observed live export, run
`38502419048` on unchanged `main` `3089b09`, failed at frozen evidence history;
Airtable export was skipped. Local implementation success is not a live-export
receipt. No Airtable writes or fixture/data modifications were performed.

## Authorized remote delivery and follow-up — 2026-10-14

The owner explicitly approved public transmission to `omegapunctum/ARTEMIS`,
resolving the earlier disclosure hold. PR #482 published an exact tree-equivalent
copy of accepted local `78aff2c`; independent remote acceptance binds its initial
head `3f6db277` to tree `29be98eae7d2312038b2ddbd702175f20d375ecd`.

PR review found that deleting the entire accepted Cesena amendment could still
produce the original frozen digest. The current review envelope now requires
exactly one unchanged amendment at its accepted location; historical frozen
content still uses the original normalization path. Deletion and duplication
are rejected by executable negative envelope tests. The expanded refinement
contour passes 82 tests and the frozen reviewed digest remains unchanged.
Current-head CI and merge are separate from live Airtable export verification.

## Fresh export-environment correction — 2026-10-14

PR #482 merged as `8d24ec4dcd076fe3480ca2d32190cef50dcb9506`.
Scheduled export run `38552367173` on that source passed frozen evidence history,
then stopped during collection of `test_knowledge_editor.py` and
`test_knowledge_editor_export.py`: the freshly installed Starlette `1.8.0`
requires its optional TestClient HTTP dependency. The previous local environment
already contained `httpx` `0.28.1`, which provided Starlette's deprecated fallback;
that successful local suite was not proof of fresh workflow dependency parity.
Airtable access, artifact export and data commit were skipped in the failed run.

This bounded AUTO follow-up adds `httpx2==2.13.1` only to the export workflow's
dependency-install command. It follows the current
[Starlette TestClient documentation](https://www.starlette.io/testclient/).
Production `requirements.txt`, workflow triggers, permissions, test exclusions,
integrity/release gates and export/data-commit behavior are unchanged.

Verification uses a new isolated Python 3.12 environment, since Python 3.11 is
not installed locally. Installing only the original workflow requirements and
pytest reproduced both collection failures. Adding the pinned client resolves
that dependency with FastAPI `0.136.1`, Starlette `1.8.0`, pytest `9.1.1`,
httpx2/httpcore2 `2.13.1` and no plain `httpx` installed. Frozen history validation
resolves all 20 commits; all reported release lanes pass with the existing memory
session single-node warning. The full unchanged non-Redis pytest contour passes:
1228 passed, 3 skipped in 221.75 seconds (Python 3.12.14); `pip check` also passes.
Exact-head independent review and CI control delivery. A subsequent Python 3.11
live export success remains a separate receipt; this correction claims no
Airtable write or historical-data promotion.
