#!/usr/bin/env python3
"""Create and verify ARTEMIS SQLite backups using the SQLite backup API."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sqlite3
import sys


def _integrity_check(database_path: Path) -> None:
    if not database_path.is_file():
        raise RuntimeError(f"database does not exist: {database_path}")

    with sqlite3.connect(f"file:{database_path}?mode=ro", uri=True) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        detail = result[0] if result else "no result"
        raise RuntimeError(f"SQLite integrity_check failed: {detail}")


def create_backup(source: Path, destination: Path) -> None:
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()

    if source == destination:
        raise RuntimeError("source and destination must be different paths")
    if not source.is_file():
        raise RuntimeError(f"source database does not exist: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_destination = destination.with_name(f".{destination.name}.tmp")
    temporary_destination.unlink(missing_ok=True)

    try:
        with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as source_connection:
            with sqlite3.connect(temporary_destination) as destination_connection:
                source_connection.backup(destination_connection)
        _integrity_check(temporary_destination)
        os.replace(temporary_destination, destination)
    except Exception:
        temporary_destination.unlink(missing_ok=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup", help="Create an atomic verified backup")
    backup_parser.add_argument("source", type=Path)
    backup_parser.add_argument("destination", type=Path)

    verify_parser = subparsers.add_parser("verify", help="Run SQLite integrity_check")
    verify_parser.add_argument("database", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "backup":
            create_backup(args.source, args.destination)
            print(f"SQLITE BACKUP: PASS: {args.destination}")
        else:
            _integrity_check(args.database.expanduser().resolve())
            print(f"SQLITE VERIFY: PASS: {args.database}")
    except (OSError, RuntimeError, sqlite3.Error) as exc:
        print(f"SQLITE {args.command.upper()}: FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
