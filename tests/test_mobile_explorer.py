"""Owned mobile interaction tests; native viewport evidence is separate."""
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_mobile_behavior():
    if not shutil.which("node"):
        pytest.skip("Node is required for shipped mobile adapter behavior")
    result = subprocess.run(["node", "tests/mobile_explorer_behavior.cjs"], cwd=ROOT, check=True, text=True, capture_output=True)
    assert "MOBILE_EXPLORER_BEHAVIOR_PASS" in result.stdout
