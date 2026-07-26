#!/usr/bin/env python3
"""Generate the public, non-secret Pages deployment configuration."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit


LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}


def normalize_api_base(raw_value: str) -> str:
    value = raw_value.strip().rstrip("/")
    if not value:
        return ""

    parsed = urlsplit(value)
    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("ARTEMIS_API_BASE must be an absolute URL without credentials")
    if parsed.query or parsed.fragment:
        raise ValueError("ARTEMIS_API_BASE must not contain a query or fragment")
    if parsed.scheme != "https" and not (
        parsed.scheme == "http" and parsed.hostname in LOOPBACK_HOSTS
    ):
        raise ValueError("ARTEMIS_API_BASE must use HTTPS (HTTP is allowed only for loopback development)")
    if parsed.path.rstrip("/") != "/api":
        raise ValueError("ARTEMIS_API_BASE must end with /api")
    return value


def render_config(api_base: str) -> str:
    enabled = bool(api_base)
    base_json = json.dumps(api_base, ensure_ascii=False)
    enabled_json = json.dumps(enabled)
    return (
        "window.ARTEMIS_DEPLOYMENT_CONFIG = Object.freeze({\n"
        f"  apiBase: {base_json},\n"
        "  capabilities: Object.freeze({\n"
        f"    account: {enabled_json},\n"
        f"    slices: {enabled_json},\n"
        "    stories: false\n"
        "  })\n"
        "});\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api-base",
        default=os.getenv("ARTEMIS_API_BASE", ""),
        help="Public API base ending in /api; defaults to ARTEMIS_API_BASE.",
    )
    parser.add_argument("--output", type=Path, default=Path("deployment-config.js"))
    args = parser.parse_args()

    api_base = normalize_api_base(args.api_base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_config(api_base), encoding="utf-8")
    print(f"Generated {args.output} ({'API enabled' if api_base else 'Explore-only'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
