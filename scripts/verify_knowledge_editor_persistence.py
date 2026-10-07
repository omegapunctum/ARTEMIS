"""Compare real immutable public responses after restarting/restoring the pilot DB."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.knowledge_editor.public_export import validate_package


def verify(report_path: Path, base_url: str) -> dict:
    report = json.loads(report_path.read_text())
    snapshots = report["snapshots"]
    if not snapshots:
        raise ValueError("Browser report contains no verified public snapshots")
    checked = []
    for original in snapshots:
        endpoint = original["endpoint"]
        if endpoint != "/api/knowledge-editor/public/snapshots/" + original["snapshot_id"]:
            raise ValueError("Unexpected snapshot endpoint")
        with urlopen(base_url.rstrip("/") + endpoint, timeout=10) as response:
            raw = response.read()
        digest = hashlib.sha256(raw).hexdigest()
        if json.loads(raw) != original["payload"] or digest != original["response_sha256"]:
            raise ValueError("Immutable snapshot changed after restart/restore: " + original["snapshot_id"])
        checked.append({"snapshot_id": original["snapshot_id"], "response_sha256": digest})
    checked_exports = []
    exports = report.get("exports", [])
    if not exports:
        raise ValueError("Browser report contains no verified public exports")
    for original in exports:
        endpoint = original["endpoint"]
        if endpoint != "/api/knowledge-editor/public/objects/" + original["entity_id"] + "/export":
            raise ValueError("Unexpected export endpoint")
        with urlopen(base_url.rstrip("/") + endpoint, timeout=10) as response:
            raw = response.read()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != original["response_sha256"]:
            raise ValueError("Public export changed after restart/restore")
        payload = json.loads(raw)
        validate_package(payload)
        if payload["package_digest"] != original["package_digest"]:
            raise ValueError("Public export package digest changed after restart/restore")
        checked_exports.append({"entity_id": original["entity_id"], "response_sha256": digest,
                                "package_digest": payload["package_digest"]})
    return {"result": "PASS", "synthetic_data": True,
            "browser_source_commit": report["source_commit"], "snapshots": checked,
            "exports": checked_exports,
            "scope": "backend immutable public snapshots and export bytes after actual process restart/SQLite restore"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-report", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.browser_report, args.base_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: {len(result['snapshots'])} unchanged snapshots and {len(result['exports'])} unchanged exports after restart/restore")


if __name__ == "__main__":
    main()
