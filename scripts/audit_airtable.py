#!/usr/bin/env python3
"""Compatibility Airtable audit entrypoint for ARTEMIS.

This command deliberately does not maintain a second Airtable schema validator.
The canonical current-data path is:

    Airtable -> scripts/export_airtable.py
             -> scripts.semantic_data_gate.validate_semantic_release
             -> scripts/release_check.py

By default this command validates the checked-in public artifacts without network
access. Pass ``--refresh-from-airtable`` to run the canonical Airtable export first
and then validate the generated ``data/*`` artifacts.

This script is pre-Gate-D maintenance. It does not write back to Airtable, change
the frozen Gate C package, or open a product gate.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Sequence

try:
    from scripts.semantic_data_gate import SemanticGateError, validate_semantic_release
except ModuleNotFoundError:  # Direct `python scripts/audit_airtable.py` execution.
    from semantic_data_gate import SemanticGateError, validate_semantic_release


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate ARTEMIS Airtable/public-data semantics through the canonical "
            "export + semantic-release path."
        )
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root containing scripts/ and data/ (default: current directory).",
    )
    parser.add_argument(
        "--refresh-from-airtable",
        action="store_true",
        help="Run scripts/export_airtable.py against Airtable before validating canonical data/* artifacts.",
    )
    parser.add_argument(
        "--base",
        default=None,
        help="Airtable base id. Defaults to AIRTABLE_BASE, then legacy AIRTABLE_BASE_ID.",
    )
    parser.add_argument(
        "--table",
        default="Features",
        help="Primary Airtable table passed to the canonical exporter (default: Features).",
    )
    return parser.parse_args(argv)


def _run_canonical_export(args: argparse.Namespace, root: Path) -> int:
    token = os.getenv("AIRTABLE_TOKEN")
    base = args.base or os.getenv("AIRTABLE_BASE") or os.getenv("AIRTABLE_BASE_ID")

    if not token:
        print(
            "Airtable refresh failed: AIRTABLE_TOKEN is required for --refresh-from-airtable.",
            file=sys.stderr,
        )
        return 2
    if not base:
        print(
            "Airtable refresh failed: pass --base or set AIRTABLE_BASE/AIRTABLE_BASE_ID.",
            file=sys.stderr,
        )
        return 2

    exporter = root / "scripts" / "export_airtable.py"
    if not exporter.exists():
        print(f"Airtable refresh failed: canonical exporter not found: {exporter}", file=sys.stderr)
        return 2

    command = [
        sys.executable,
        str(exporter),
        "--base",
        base,
        "--table",
        args.table,
        "--out-dir",
        "data",
    ]
    completed = subprocess.run(command, cwd=root, check=False)
    if completed.returncode != 0:
        print(
            f"Airtable refresh failed: canonical exporter exited {completed.returncode}.",
            file=sys.stderr,
        )
    return completed.returncode


def _print_summary(summary: dict[str, int | str]) -> None:
    print("Canonical Airtable/public-data audit: PASS")
    for key in sorted(summary):
        print(f"{key}: {summary[key]}")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()

    if args.refresh_from_airtable:
        export_status = _run_canonical_export(args, root)
        if export_status != 0:
            return export_status

    try:
        summary = validate_semantic_release(root)
    except SemanticGateError as exc:
        print(f"Canonical Airtable/public-data audit: FAIL — {exc}", file=sys.stderr)
        return 1

    _print_summary(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
