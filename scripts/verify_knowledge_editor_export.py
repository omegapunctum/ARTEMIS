#!/usr/bin/env python3
"""Verify a public export offline: python scripts/verify_knowledge_editor_export.py FILE.json.

No import/promotion, database access, networking, writes or content output.
Successful integrity verification is not authenticity or historical acceptance.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> int:
    try:
        if len(sys.argv) != 2:
            raise ValueError("invalid_arguments")
        from app.knowledge_editor.public_export import verify_file
        verify_file(sys.argv[1])
    except Exception:
        print("Public export verification failed.")
        return 1
    print("Public export integrity verified (unsigned; no authenticity or historical acceptance).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
