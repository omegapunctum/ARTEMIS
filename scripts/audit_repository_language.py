"""Inventory Cyrillic in tracked text files outside Russian UI localization.

Usage: python scripts/audit_repository_language.py [--list] [--check]
The audit covers tracked files, including archives, fixtures, tests and hidden paths.
It reports Cyrillic script rather than attempting to infer the language of a file.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CYRILLIC = re.compile(r"[\u0400-\u04ff]")
UI_LOCALIZATION = {
    "scripts/globe_spike/localization.js",
}


def inventory() -> list[tuple[str, int]]:
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
    findings = []
    for raw_path in tracked:
        if not raw_path:
            continue
        path = raw_path.decode("utf-8", errors="surrogateescape")
        if path in UI_LOCALIZATION:
            continue
        try:
            text = (ROOT / path).read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        count = sum(bool(CYRILLIC.search(line)) for line in text.splitlines())
        if count:
            findings.append((path, count))
    return sorted(findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="print each matching path and line count")
    parser.add_argument("--check", action="store_true", help="fail while Cyrillic remains outside UI localization")
    args = parser.parse_args()
    findings = inventory()
    if args.list:
        for path, count in findings:
            print(f"{count:5} {path}")
    print(f"{len(findings)} tracked files, {sum(count for _, count in findings)} Cyrillic lines outside UI localization")
    return int(args.check and bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
