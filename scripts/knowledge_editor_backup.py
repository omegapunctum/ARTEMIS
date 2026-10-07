"""Consistent SQLite backup/restore to a new private file; never replace working data."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import os
import sqlite3
from urllib.parse import quote


def copy_database(source: Path, destination: Path) -> str:
    source = source.resolve()
    if not source.is_file():
        raise ValueError("Source database does not exist")
    destination = destination.absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination must be a new file; existing data will not be replaced")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # O_EXCL prevents a race from overwriting an existing backup or database.
    descriptor = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    try:
        with sqlite3.connect("file:" + quote(str(source)) + "?mode=ro", uri=True) as original:
            if original.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Source database integrity check failed")
            with sqlite3.connect(destination) as copied:
                original.backup(copied)
                if copied.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("Copied database integrity check failed")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["backup", "restore"])
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    digest = copy_database(args.source, args.destination)
    print(f"{args.operation}: integrity verified; SHA-256 {digest}")


if __name__ == "__main__":
    main()
