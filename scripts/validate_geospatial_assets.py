#!/usr/bin/env python3
"""Validate ARTEMIS geospatial asset manifests for issue #342."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "geospatial_assets" / "v1"
MANIFEST_PATH = FIXTURE_DIR / "manifest.json"
SCHEMA_PATH = FIXTURE_DIR / "schema.json"
WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"

ENV_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,127}$")
DATE_RE = re.compile(r"^-?\d{1,6}(?:-\d{2}(?:-\d{2})?)?$")
SECRET_QUERY_NAMES = {
    "access_token",
    "apikey",
    "api_key",
    "auth",
    "authorization",
    "key",
    "password",
    "secret",
    "signature",
    "sig",
    "token",
}
HEIGHT_BEARING_KINDS = {"terrain_elevation", "three_d_tiles"}


class ManifestError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ManifestError(f"{path} must contain a JSON object")
    return value


def _schema_errors(manifest: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(manifest),
        key=lambda error: list(error.absolute_path),
    )
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def _date_key(value: str) -> tuple[int, int, int]:
    if not DATE_RE.fullmatch(value):
        raise ValueError(f"unsupported date lexical value: {value!r}")
    parts = value.split("-")
    # Negative years are outside the current synthetic fixture. Preserve a clear
    # validation failure rather than pretending Python split semantics are a calendar.
    if value.startswith("-"):
        raise ValueError("negative/BCE lexical dates require the future shared temporal parser")
    year = int(parts[0])
    month = int(parts[1]) if len(parts) >= 2 else 1
    day = int(parts[2]) if len(parts) >= 3 else 1
    if not 1 <= month <= 12 or not 1 <= day <= 31:
        raise ValueError(f"invalid date components: {value!r}")
    return year, month, day


def _world_claim_ids(world: dict[str, Any] | None) -> set[str]:
    if not world:
        return set()
    return {str(claim["id"]) for claim in world.get("claims", []) if claim.get("id")}


def _world_uncertainty_ids(world: dict[str, Any] | None) -> set[str]:
    if not world:
        return set()
    return {
        str(item["id"])
        for item in world.get("uncertainties", [])
        if item.get("id")
    }


def semantic_asset_signature(asset: dict[str, Any]) -> dict[str, Any]:
    """Return fields whose meaning must survive a provider infrastructure swap."""
    return {
        "asset_id": asset["asset_id"],
        "asset_kind": asset["asset_kind"],
        "semantic_role": asset["semantic_role"],
        "spatial_reference": asset["spatial_reference"],
        "coverage": asset["coverage"],
        "temporal_semantics": asset["temporal_semantics"],
    }


def _validate_bbox(asset: dict[str, Any], errors: list[str], prefix: str) -> None:
    west, south, east, north = asset["coverage"]["bbox_wgs84"]
    if not (-180 <= west <= 180 and -180 <= east <= 180):
        errors.append(f"{prefix}: bbox longitude must be within [-180, 180]")
    if not (-90 <= south <= 90 and -90 <= north <= 90):
        errors.append(f"{prefix}: bbox latitude must be within [-90, 90]")
    if west >= east:
        errors.append(f"{prefix}: bbox west must be less than east")
    if south >= north:
        errors.append(f"{prefix}: bbox south must be less than north")

    coverage = asset["coverage"]
    min_res = coverage["min_resolution_m"]
    max_res = coverage["max_resolution_m"]
    if min_res is not None and max_res is not None and min_res > max_res:
        errors.append(f"{prefix}: min_resolution_m must be <= max_resolution_m")
    min_lod = coverage["min_lod"]
    max_lod = coverage["max_lod"]
    if min_lod is not None and max_lod is not None and min_lod > max_lod:
        errors.append(f"{prefix}: min_lod must be <= max_lod")


def _validate_vertical(asset: dict[str, Any], errors: list[str], prefix: str) -> None:
    vertical = asset["spatial_reference"]["vertical_reference"]
    mode = vertical["mode"]
    height_bearing = asset["asset_kind"] in HEIGHT_BEARING_KINDS

    if height_bearing and mode not in {"ellipsoidal_height", "orthometric_height"}:
        errors.append(
            f"{prefix}: height-bearing asset requires explicit ellipsoidal/orthometric vertical reference"
        )
    if mode in {"ellipsoidal_height", "orthometric_height"}:
        if not vertical["datum"]:
            errors.append(f"{prefix}: vertical datum is required for height-bearing data")
        if vertical["unit"] not in {"meter", "foot"}:
            errors.append(f"{prefix}: vertical unit is required for height-bearing data")
        if vertical["positive_direction"] not in {"up", "down"}:
            errors.append(f"{prefix}: vertical positive direction is required")
    if mode == "not_applicable" and any(
        vertical[field] is not None for field in ("datum", "unit", "positive_direction")
    ):
        errors.append(
            f"{prefix}: not_applicable vertical reference must not carry datum/unit/direction"
        )


def _validate_provider(asset: dict[str, Any], errors: list[str], prefix: str) -> None:
    provider = asset["provider"]
    runtime = asset["runtime_policy"]
    credential_mode = provider["credential_mode"]
    credential_env = provider["credential_env"]

    if credential_mode == "none":
        if credential_env is not None:
            errors.append(f"{prefix}: credential_mode=none requires credential_env=null")
        if runtime["secret_required"]:
            errors.append(f"{prefix}: credential_mode=none conflicts with secret_required=true")
    elif credential_mode == "runtime_secret":
        if not isinstance(credential_env, str) or not ENV_RE.fullmatch(credential_env):
            errors.append(f"{prefix}: runtime_secret requires a valid environment variable name")
        if not runtime["secret_required"]:
            errors.append(f"{prefix}: runtime_secret requires secret_required=true")
        if runtime["public_pages_allowed"]:
            errors.append(f"{prefix}: private runtime secret cannot be exposed to public Pages")

    endpoint = provider["endpoint_template"]
    if endpoint:
        parsed = urlparse(endpoint)
        for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
            if key.lower() in SECRET_QUERY_NAMES:
                errors.append(
                    f"{prefix}: endpoint_template contains credential-like query parameter {key!r}"
                )
        if parsed.scheme in {"http", "https"} and not runtime["network_required"]:
            errors.append(f"{prefix}: http(s) provider requires network_required=true")
        if parsed.scheme == "fixture" and runtime["network_required"]:
            errors.append(f"{prefix}: fixture provider must not require network access")


def _validate_temporal(
    asset: dict[str, Any],
    errors: list[str],
    prefix: str,
    claim_ids: set[str],
    uncertainty_ids: set[str],
) -> None:
    role = asset["semantic_role"]
    temporal = asset["temporal_semantics"]
    mode = temporal["mode"]
    claims = temporal["world_model_claim_refs"]
    uncertainties = temporal["uncertainty_refs"]
    valid_from = temporal["valid_from"]
    valid_to = temporal["valid_to"]
    method = temporal["reconstruction_method"]
    reference_date = temporal["reference_date"]

    if role == "present_day_context":
        if mode not in {"current_context", "dated_snapshot"}:
            errors.append(
                f"{prefix}: present_day_context must use current_context or dated_snapshot"
            )
        if valid_from is not None or valid_to is not None:
            errors.append(f"{prefix}: present_day_context cannot declare historical validity")
        if claims:
            errors.append(f"{prefix}: present_day_context cannot carry historical Claim bindings")
        if method is not None:
            errors.append(f"{prefix}: present_day_context cannot declare reconstruction_method")

    elif role == "analytical_context":
        if mode == "historical_validity":
            errors.append(f"{prefix}: analytical_context cannot masquerade as historical_validity")
        if valid_from is not None or valid_to is not None:
            errors.append(f"{prefix}: analytical_context cannot declare historical validity interval")
        if method is not None:
            errors.append(f"{prefix}: analytical_context cannot declare historical reconstruction method")

    elif role == "historical_reconstruction":
        if mode != "historical_validity":
            errors.append(f"{prefix}: historical_reconstruction requires historical_validity")
        if not valid_from or not valid_to:
            errors.append(f"{prefix}: historical_reconstruction requires valid_from and valid_to")
        if not claims:
            errors.append(f"{prefix}: historical_reconstruction requires World Model Claim bindings")
        if not method:
            errors.append(f"{prefix}: historical_reconstruction requires reconstruction_method")
        if claim_ids:
            unknown = sorted(set(claims) - claim_ids)
            if unknown:
                errors.append(f"{prefix}: unknown World Model Claim refs: {unknown}")
        if uncertainty_ids:
            unknown_u = sorted(set(uncertainties) - uncertainty_ids)
            if unknown_u:
                errors.append(f"{prefix}: unknown World Model Uncertainty refs: {unknown_u}")

    if mode == "dated_snapshot" and not reference_date:
        errors.append(f"{prefix}: dated_snapshot requires reference_date")
    if mode != "dated_snapshot" and reference_date is not None:
        errors.append(f"{prefix}: reference_date is reserved for dated_snapshot")

    if valid_from and valid_to:
        try:
            if _date_key(valid_from) > _date_key(valid_to):
                errors.append(f"{prefix}: valid_from must not be after valid_to")
        except ValueError as exc:
            errors.append(f"{prefix}: {exc}")


def _validate_licensing(asset: dict[str, Any], errors: list[str], prefix: str) -> None:
    licensing = asset["licensing"]
    cache = asset["cache_policy"]
    redistribution = licensing["redistribution"]

    if redistribution in {"restricted", "prohibited"} and cache[
        "cached_bytes_redistribution_allowed"
    ]:
        errors.append(
            f"{prefix}: restricted/prohibited redistribution forbids cached byte redistribution"
        )
    if redistribution == "prohibited" and cache["offline_cache_allowed"]:
        errors.append(f"{prefix}: prohibited redistribution forbids offline cache in v1")
    if not cache["runtime_cache_allowed"] and cache["max_age_seconds"] not in {None, 0}:
        errors.append(f"{prefix}: disabled runtime cache cannot declare positive max_age_seconds")


def _validate_fallbacks(
    manifest: dict[str, Any], errors: list[str], asset_ids: set[str]
) -> None:
    for asset in manifest["assets"]:
        prefix = f"asset[{asset['asset_id']}]"
        runtime = asset["runtime_policy"]
        fallback = runtime["fallback_asset_ref"]
        if runtime["failure_mode"] == "fallback_allowed":
            if not fallback:
                errors.append(f"{prefix}: fallback_allowed requires fallback_asset_ref")
            elif fallback not in asset_ids:
                errors.append(f"{prefix}: fallback asset does not exist: {fallback}")
            elif fallback == asset["asset_id"]:
                errors.append(f"{prefix}: asset cannot fall back to itself")
        elif fallback is not None:
            errors.append(f"{prefix}: fail_closed requires fallback_asset_ref=null")


def validate_manifest(
    manifest: dict[str, Any],
    *,
    schema: dict[str, Any],
    world: dict[str, Any] | None = None,
) -> list[str]:
    errors = _schema_errors(manifest, schema)
    if errors:
        return errors

    asset_ids_list = [str(asset["asset_id"]) for asset in manifest["assets"]]
    asset_ids = set(asset_ids_list)
    if len(asset_ids_list) != len(asset_ids):
        errors.append("manifest: duplicate asset_id values are forbidden")

    claim_ids = _world_claim_ids(world)
    uncertainty_ids = _world_uncertainty_ids(world)

    for asset in manifest["assets"]:
        prefix = f"asset[{asset['asset_id']}]"
        _validate_bbox(asset, errors, prefix)
        _validate_vertical(asset, errors, prefix)
        _validate_provider(asset, errors, prefix)
        _validate_temporal(asset, errors, prefix, claim_ids, uncertainty_ids)
        _validate_licensing(asset, errors, prefix)

    _validate_fallbacks(manifest, errors, asset_ids)
    return errors


def main() -> int:
    try:
        manifest = _load(MANIFEST_PATH)
        schema = _load(SCHEMA_PATH)
        world = _load(WORLD_PATH)
        errors = validate_manifest(manifest, schema=schema, world=world)
        if errors:
            for error in errors:
                print(f"[FAIL] {error}", file=sys.stderr)
            return 1
        print(
            "[PASS] Geospatial Asset Manifest v1: "
            f"manifest={manifest['manifest_id']}; assets={len(manifest['assets'])}; "
            "provider/CRS/vertical/temporal/licensing/cache/runtime rules valid"
        )
        return 0
    except (ManifestError, KeyError, TypeError, ValueError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
