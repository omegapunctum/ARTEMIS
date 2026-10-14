#!/usr/bin/env python3
"""Fail closed when CI cannot resolve commit-bound fixture evidence."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
# An upstream source revision is not a commit in ARTEMIS history. Keep this
# exception bounded to the existing, source-qualified fixture contract.
EXTERNAL_MANIFEST = Path("world_slices/roman_empire_region/v1/source_manifest.json")
EXTERNAL_REPOSITORY = "https://github.com/Seshat-Global-History-Databank/cliopatria"
EXTERNAL_COMMIT = "ad28a691b7c07c1fca89d0e0636d324667d2a258"


class EvidenceHistoryError(RuntimeError):
    """Raised when authoritative fixture history is incomplete."""


def collect_commit_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if (key == "commit" or key.endswith("_commit")) and isinstance(item, str):
                if not COMMIT_PATTERN.fullmatch(item):
                    raise EvidenceHistoryError(f"invalid commit reference: {item}")
                refs.add(item)
            refs.update(collect_commit_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.update(collect_commit_refs(item))
    return refs


def fixture_document_refs(relative_path: Path, value: Any) -> set[str]:
    if relative_path != EXTERNAL_MANIFEST:
        return collect_commit_refs(value)
    if not isinstance(value, dict) or (
        value.get("repository") != EXTERNAL_REPOSITORY
        or value.get("commit") != EXTERNAL_COMMIT
    ):
        raise EvidenceHistoryError("external source repository/commit binding mismatch")
    # Validate all fields first, then exclude only this exact top-level binding.
    # Nested frozen_commit fields still require local history resolution.
    collect_commit_refs(value)
    return collect_commit_refs({key: item for key, item in value.items() if key != "commit"})


def fixture_commit_refs() -> set[str]:
    refs: set[str] = set()
    for path in sorted(FIXTURES.rglob("*.json")):
        refs.update(fixture_document_refs(path.relative_to(FIXTURES), json.loads(path.read_text(encoding="utf-8"))))
    if not refs:
        raise EvidenceHistoryError("no commit-bound fixture evidence found")
    return refs


def git(*args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise EvidenceHistoryError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def validate_history() -> int:
    if git("rev-parse", "--is-shallow-repository") != "false":
        raise EvidenceHistoryError("CI checkout is shallow; frozen evidence commits are unavailable")
    refs = fixture_commit_refs()
    missing: list[str] = []
    for commit in sorted(refs):
        result = subprocess.run(
            ("git", "cat-file", "-e", f"{commit}^{{commit}}"),
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            missing.append(commit)
    if missing:
        raise EvidenceHistoryError(
            "missing frozen evidence commits: " + ", ".join(missing)
        )
    return len(refs)


def main() -> int:
    try:
        count = validate_history()
    except (EvidenceHistoryError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"PASS: resolved {count} frozen evidence commits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
