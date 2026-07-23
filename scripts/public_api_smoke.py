#!/usr/bin/env python3
"""Minimal public ARTEMIS API deployment smoke.

This script verifies HTTPS reachability, baseline health semantics, request
correlation, and the exact credentialed CORS contract required by GitHub Pages.
It intentionally does not create user data; the full Slice flow remains a
clean-browser acceptance step tracked separately.
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlparse

import requests


DEFAULT_TIMEOUT_SECONDS = 10.0


def _normalize_api_base(raw_value: str) -> str:
    api_base = raw_value.strip().rstrip("/")
    parsed = urlparse(api_base)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("--api-base must be an absolute http(s) URL")
    if not parsed.path.endswith("/api"):
        raise ValueError("--api-base must include the canonical /api base path")
    return api_base


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_smoke(
    *,
    api_base: str,
    origin: str | None,
    timeout_seconds: float,
    allow_http: bool,
    allow_degraded_health: bool,
) -> dict[str, object]:
    normalized_api_base = _normalize_api_base(api_base)
    parsed = urlparse(normalized_api_base)
    if parsed.scheme != "https" and not allow_http:
        raise RuntimeError("public smoke requires HTTPS; use --allow-http only for local testing")

    session = requests.Session()
    health_response = session.get(f"{normalized_api_base}/health", timeout=timeout_seconds)
    _require(health_response.status_code == 200, f"health returned {health_response.status_code}")

    try:
        health_payload = health_response.json()
    except ValueError as exc:
        raise RuntimeError("health response is not valid JSON") from exc

    _require(isinstance(health_payload, dict), "health response must be a JSON object")
    _require("ok" in health_payload, "health response is missing the baseline ok field")
    if not allow_degraded_health:
        _require(health_payload.get("ok") is True, "health reports a recent server error")

    request_id = health_response.headers.get("X-Request-ID", "").strip()
    _require(bool(request_id), "health response is missing X-Request-ID")

    cors_summary: dict[str, object] | None = None
    if origin:
        normalized_origin = origin.strip().rstrip("/")
        origin_parsed = urlparse(normalized_origin)
        _require(
            origin_parsed.scheme in {"http", "https"} and bool(origin_parsed.netloc),
            "--origin must be an absolute origin URL",
        )
        _require(origin_parsed.path in {"", "/"}, "--origin must not contain a path")

        preflight_response = session.options(
            f"{normalized_api_base}/auth/login",
            headers={
                "Origin": normalized_origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            timeout=timeout_seconds,
        )
        _require(
            preflight_response.status_code in {200, 204},
            f"CORS preflight returned {preflight_response.status_code}",
        )
        allow_origin = preflight_response.headers.get("Access-Control-Allow-Origin", "")
        allow_credentials = preflight_response.headers.get("Access-Control-Allow-Credentials", "")
        _require(allow_origin == normalized_origin, "CORS allow-origin does not match the Pages origin")
        _require(allow_credentials.lower() == "true", "credentialed CORS is not enabled")
        cors_summary = {
            "status": preflight_response.status_code,
            "allow_origin": allow_origin,
            "allow_credentials": True,
        }

    return {
        "api_base": normalized_api_base,
        "health": health_payload,
        "request_id": request_id,
        "cors": cors_summary,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", required=True, help="Absolute API base, for example https://api.example/api")
    parser.add_argument("--origin", help="Exact GitHub Pages origin to verify with a credentialed CORS preflight")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--allow-http", action="store_true", help="Allow HTTP for local-only smoke runs")
    parser.add_argument(
        "--allow-degraded-health",
        action="store_true",
        help="Accept health ok=false while still checking endpoint shape and reachability",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = run_smoke(
            api_base=args.api_base,
            origin=args.origin,
            timeout_seconds=args.timeout,
            allow_http=args.allow_http,
            allow_degraded_health=args.allow_degraded_health,
        )
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        print(f"PUBLIC API SMOKE: FAIL: {exc}", file=sys.stderr)
        return 1

    print("PUBLIC API SMOKE: PASS")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
