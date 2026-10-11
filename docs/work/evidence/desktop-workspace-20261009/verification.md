# Local verification — desktop workspace

Implementation revision: `5a1a2e19aa2ad12cd34ae1cec10d68f642d57c2b`.

- `python3 -m pytest -q tests/test_unified_explorer.py tests/test_mobile_explorer.py tests/test_unified_explorer_browser.py`: 22 passed (21.52 s). These are owned non-native checks; they do not demonstrate visual conformance.
- `node tests/desktop_explorer_behavior.cjs`: PASS, including focus owner routing.
- `node --check scripts/capture_unified_explorer_browser_evidence.mjs`: PASS.
- `git diff --check`: PASS.
- Full production builder: PASS, 55 shared registry records.
- Bundle SHA256 unchanged: `a0c2046ea0862683167aef3b6d5f4b496a36fcabb0b2dcaa595c4534f91d5538`.
- Browser startup: BLOCKED, WebGL disabled; screenshot and root design QA record this limitation.
- Native harness includes new desktop owner/collapse checks but has not been executed on this revision.

## Resume visual acceptance

Import the supplied git bundle into an existing ARTEMIS clone containing base `20d47847d18873076d799da2643eb73a33c78ae7`:

```sh
git bundle verify /path/to/ARTEMIS-desktop-workspace.bundle
git fetch /path/to/ARTEMIS-desktop-workspace.bundle feat/desktop-workspace-20261009:review/desktop-workspace
git switch review/desktop-workspace
python3 -m scripts.build_unified_explorer --output /tmp/artemis-desktop-review
python3 -m http.server 4173 --directory /tmp/artemis-desktop-review
```

Open `http://localhost:4173` in a WebGL-capable browser. Check wide desktop and mobile/short landscape, EN/RU, record selection, both panel toggles, Layers, dates, camera continuity and source disclosures. Complete the source/implementation visual comparison required by `design-qa.md`. This procedure imports a review branch; it does not merge or publish it.
