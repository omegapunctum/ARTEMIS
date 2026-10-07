"""Compare real immutable public responses after restarting/restoring the pilot DB."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


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
    return {"result": "PASS", "synthetic_data": True,
            "browser_source_commit": report["source_commit"], "snapshots": checked,
            "scope": "backend immutable public responses after actual process restart/SQLite restore"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-report", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.browser_report, args.base_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: {len(result['snapshots'])} unchanged snapshots after restart/restore")


if __name__ == "__main__":
    main()
