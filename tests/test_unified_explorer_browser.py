"""The native browser harness binds evidence to checked entries and rejects drift."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_unified_browser_evidence_rejects_wrong_bytes_and_state() -> None:
    subprocess.run(
        ["node", "tests/unified_browser_evidence.cjs"], cwd=ROOT, check=True, timeout=15
    )


def test_offline_visitor_guard_blocks_actual_wikimedia_hosts_only() -> None:
    """The native proof blocks external APIs and detects attempted live requests."""
    subprocess.run(
        [
            "node", "--input-type=module", "-e",
            """
            import assert from 'node:assert/strict';
            import {isWikimediaRequest,WIKIMEDIA_BLOCKED_URLS} from './scripts/capture_unified_explorer_browser_evidence.mjs';
            for (const url of ['https://www.wikidata.org/w/api.php','https://wikidata.org/wiki/Q83125','https://en.wikipedia.org/w/api.php','https://commons.wikimedia.org/wiki/File:x']) assert.equal(isWikimediaRequest(url),true,url);
            for (const url of ['http://127.0.0.1:8000/globe/unified-bundle.json','https://example.test/?next=https://wikidata.org','https://wikidata.org.example.test/w/api.php','not a URL']) assert.equal(isWikimediaRequest(url),false,url);
            assert.ok(WIKIMEDIA_BLOCKED_URLS.includes('*://*.wikidata.org/*'));
            assert.ok(WIKIMEDIA_BLOCKED_URLS.includes('*://*.wikipedia.org/*'));
            """,
        ], cwd=ROOT, check=True, timeout=15,
    )
