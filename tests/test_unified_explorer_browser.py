"""The native browser harness binds evidence to checked entries and rejects drift."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_unified_browser_evidence_rejects_wrong_bytes_and_state() -> None:
    subprocess.run(
        ["node", "tests/unified_browser_evidence.cjs"], cwd=ROOT, check=True, timeout=15
    )
