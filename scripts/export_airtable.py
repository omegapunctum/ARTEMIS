#!/usr/bin/env python3
"""
Экспорт таблицы Airtable (обычно Features) в локальные JSON/GeoJSON файлы.

Пример запуска:
  AIRTABLE_TOKEN=pat_xxx AIRTABLE_BASE=appHmf8ubeUF9 AIRTABLE_TABLE=Features \
  python3 scripts/export_airtable.py --out-dir data

Переменные окружения:
  - AIRTABLE_TOKEN: персональный токен Airtable (Bearer)
  - AIRTABLE_BASE: ID базы Airtable (например appHmf8ubeUF9)
  - AIRTABLE_TABLE: имя таблицы (например Features)

Выходные файлы:
  - data/features.json        : сырые записи Airtable (records)
  - data/features.geojson     : GeoJSON FeatureCollection
  - data/id_aliases.json      : versioned legacy id -> canonical UUID map
  - data/sources.json         : reviewed canonical Sources
  - data/media.json           : reviewed display Media with attribution
  - data/relations.json       : reviewed evidence-backed Feature relations
  - data/rejected.json        : отклонённые записи с причинами валидации
  - data/layers.json          : агрегированные метаданные слоёв
  - data/export_errors.log    : ошибки в формате JSON Lines
  - data/export_meta.json     : метаданные экспорта (timestamp, counts, source)

Если передан --dry-run или нет обязательных переменных/параметров для API, скрипт
переходит в dry-run режим: не обращается к Airtable и пишет mock-выход в data/_test_*.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import uuid

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE = os.getenv("AIRTABLE_BASE")
AIRTABLE_TABLE = os.getenv("AIRTABLE_TABLE")

import re
import subprocess
import sys
import time
from urllib.parse import urlparse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from scripts.semantic_data_gate import collect_semantic_quality_warnings, select_publishable_layers
except ModuleNotFoundError:  # Direct `python scripts/export_airtable.py` execution.
    from semantic_data_gate import collect_semantic_quality_warnings, select_publishable_layers

# Установка зависимости: pip install requests
REQUESTS_AVAILABLE = importlib.util.find_spec("requests") is not None
if REQUESTS_AVAILABLE:
    import requests
else:
    requests = None  # type: ignore[assignment]

DATE_RE = re.compile(r"^-?\d{4}(?:-\d{2}-\d{2})?$")
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
TRUE_SET = {True, 1, "1", "true", "yes", "y", "да"}
FALSE_SET = {False, 0, "0", "false", "no", "n", "нет"}
ALLOWED_LICENSES = {"CC0", "CC BY", "CC BY-SA", "PD"}
ALLOWED_COORDINATES_CONFIDENCE = {"exact", "approximate", "conditional"}
# IMPORTANT:
# This allowlist MUST be kept in sync with Airtable 'coordinates_source' enum.
# Adding new source values in Airtable requires updating this list.
ALLOWED_COORDINATES_SOURCES = {
    "Wikipedia",
    "Pleiades",
    "GBIF",
    "IUCN",
    "expert estimate",
    "Official Site",
    "Britannica",
    "Vatican",
    "UNESCO",
    "Pompidou Site",
    "PBS",
    "Dezeen",
    "Saylor",
}
ALLOWED_LAYER_TYPES = {"architecture", "route_point", "biogeography", "biography"}
LAYERS_TABLE_NAME = "Layers"
SOURCES_TABLE_NAME = "Sources"
MEDIA_TABLE_NAME = "Media"
FEATURE_SOURCES_TABLE_NAME = "FeatureSources"
FEATURE_MEDIA_TABLE_NAME = "FeatureMedia"
RELATIONS_TABLE_NAME = "Relations"
RELATION_SOURCES_TABLE_NAME = "RelationSources"
ALLOWED_REVIEW_STATUSES = {"draft", "reviewed", "rejected"}
ALLOWED_SOURCE_TYPES = {"primary", "official", "academic", "institutional", "reference", "other"}
ALLOWED_SOURCE_ROLES = {
    "general_reference",
    "date_evidence",
    "coordinate_evidence",
    "description_evidence",
    "relation_evidence",
}
ALLOWED_MEDIA_TYPES = {"image", "map", "drawing", "diagram", "document"}
ALLOWED_MEDIA_DISPLAY_ROLES = {"primary", "gallery", "context", "detail"}
ALLOWED_RELATION_TYPES = {"influenced", "inspired_by", "same_movement", "reconstructed_from", "part_of"}
SYMMETRIC_RELATION_TYPES = {"same_movement"}
ALLOWED_EPISTEMIC_STATUSES = {"fact", "interpretation", "hypothesis"}
ALLOWED_RELATION_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_RELATION_SOURCE_ROLES = {"relation_evidence"}
CAUSAL_CLAIM_RE = re.compile(r"\b(caus(?:e|ed|es|al|ality)|resulted\s+in)\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Экспорт данных Features из Airtable")
    parser.add_argument("--base", help="Airtable base id (или AIRTABLE_BASE)")
    parser.add_argument("--table", help="Airtable table name (или AIRTABLE_TABLE)")
    parser.add_argument("--out-dir", default="data", help="Каталог для выходных файлов (по умолчанию: data)")
    parser.add_argument("--dry-run", action="store_true", help="Не ходить в сеть и сгенерировать mock-данные")
    parser.add_argument("--max-records", type=int, default=None, help="Ограничить число записей (для тестирования)")
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="Включать записи с is_active=False (по умолчанию такие записи пропускаются)",
    )
    parser.add_argument("--commit", action="store_true", help="После экспорта выполнить git add/commit")
    parser.add_argument("--self-test", action="store_true", help="Запустить минимальную самопроверку и выйти")
    return parser.parse_args()


def log_error(error_log_path: Path, payload: Dict[str, Any]) -> None:
    """Пишем ошибку в JSON Lines файл, не прерывая основной процесс."""
    try:
        error_log_path.parent.mkdir(parents=True, exist_ok=True)
        with error_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as exc:  # noqa: BLE001
        print(f"Не удалось записать ошибку в лог: {exc}", file=sys.stderr)


def append_diagnostic(
    issues: List[Dict[str, Any]],
    *,
    record_id: str,
    field: str,
    error: Optional[str] = None,
    warning: Optional[str] = None,
    value: Any = None,
    severity: Optional[str] = None,
    reason: Optional[str] = None,
) -> None:
    """Добавляет diagnostics payload в унифицированном формате, сохраняя legacy ключи."""
    normalized_id = record_id or "<missing>"
    payload: Dict[str, Any] = {
        "id": normalized_id,
        "record_id": normalized_id,
        "field": field,
    }
    if error is not None:
        payload["error"] = error
    if warning is not None:
        payload["warning"] = warning
    if value is not None:
        payload["value"] = value

    derived_reason = reason or error or warning
    if derived_reason is not None:
        payload["reason"] = derived_reason
    resolved_severity = severity or ("critical" if error is not None else "warning" if warning is not None else None)
    if resolved_severity is not None:
        payload["severity"] = resolved_severity
    issues.append(payload)


def append_warning_once(
    issues: List[Dict[str, Any]],
    *,
    record_id: str,
    field: str,
    warning: str,
    value: Any = None,
    reason: Optional[str] = None,
) -> None:
    """Append warning once per (field, reason) across one export run."""
    resolved_reason = reason or warning
    for issue in issues:
        if issue.get("severity") == "warning" and issue.get("field") == field and issue.get("reason") == resolved_reason:
            return
    append_diagnostic(
        issues,
        record_id=record_id,
        field=field,
        warning=warning,
        value=value,
        reason=resolved_reason,
    )


def to_date_or_none(value: Any, record_id: str, field: str, errors: List[Dict[str, Any]]) -> Optional[str]:
    if value in (None, ""):
        return None
    value_str = str(value).strip()
    if DATE_RE.match(value_str):
        return value_str
    append_diagnostic(errors, record_id=record_id, field=field, error=f"invalid date: {value}", value=value)
    return None


def to_float_or_none(value: Any, record_id: str, field: str, errors: List[Dict[str, Any]]) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        append_diagnostic(errors, record_id=record_id, field=field, error=f"invalid float: {value}", value=value)
        return None


def parse_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int_or_none(value: Any, record_id: str, field: str, errors: List[Dict[str, Any]]) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        append_diagnostic(errors, record_id=record_id, field=field, error=f"invalid int: {value}", value=value)
        return None


def to_bool_or_none(value: Any, record_id: str, field: str, errors: List[Dict[str, Any]]) -> Optional[bool]:
    if value in (None, ""):
        return None
    normalized = value.strip().lower() if isinstance(value, str) else value
    if normalized in TRUE_SET:
        return True
    if normalized in FALSE_SET:
        return False
    append_diagnostic(errors, record_id=record_id, field=field, error=f"invalid bool: {value}", value=value)
    return None


def parse_bool(value: Any) -> Optional[bool]:
    if value in (None, ""):
        return None
    normalized = value.strip().lower() if isinstance(value, str) else value
    if normalized in TRUE_SET:
        return True
    if normalized in FALSE_SET:
        return False
    return None


def is_valid_iso_date(value: Any) -> bool:
    if value is None:
        return True
    value_str = str(value).strip()
    if not DATE_RE.fullmatch(value_str):
        return False
    try:
        if len(value_str) == 4 or (value_str.startswith("-") and len(value_str) == 5):
            return True
        dt.date.fromisoformat(value_str)
    except ValueError:
        return False
    return True


def is_valid_license(value: Optional[str]) -> bool:
    return value in ALLOWED_LICENSES


def is_valid_layer_type(value: Optional[str]) -> bool:
    return value in ALLOWED_LAYER_TYPES


def is_valid_color_hex(value: Optional[str]) -> bool:
    return value is not None and HEX_COLOR_RE.fullmatch(value.strip()) is not None


def is_valid_url(value: Optional[str]) -> bool:
    if value is None:
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_uuid_v4(value: Any) -> bool:
    """Return True only for RFC 4122 UUID v4 values."""
    candidate = safe_str(value)
    if not candidate:
        return False
    try:
        parsed = uuid.UUID(candidate)
    except (ValueError, TypeError, AttributeError):
        return False
    return parsed.version == 4 and parsed.variant == uuid.RFC_4122


def normalize_coordinates_source(value: Any) -> Optional[str]:
    if isinstance(value, list):
        raw = safe_str(value[0]) if value else None
    else:
        raw = safe_str(value)
    if raw is None:
        return None

    normalized = " ".join(raw.split())
    # Keep ETL allowlist/aliases in sync with curated Airtable Features.coordinates_source enum.
    aliases = {
        "unesco / wikipedia": "Wikipedia",
        "unesco/wikipedia": "Wikipedia",
        "official site": "Official Site",
        "britannica": "Britannica",
        "vatican": "Vatican",
        "unesco": "UNESCO",
        "pompidou site": "Pompidou Site",
        "pbs": "PBS",
        "dezeen": "Dezeen",
        "saylor": "Saylor",
    }
    return aliases.get(normalized.lower(), normalized)


def normalize_single_select(value: Any) -> Optional[str]:
    raw = safe_str(value)
    if raw is None:
        return None
    return raw.strip()


def normalize_source_license(value: Any) -> Optional[str]:
    normalized = normalize_single_select(value)
    if normalized is None:
        return None
    upper = normalized.upper().replace("_", " ").replace("-", " ")
    compact = " ".join(upper.split())
    aliases = {
        "CC0": "CC0",
        "CC 0": "CC0",
        "CC BY": "CC BY",
        "CCBY": "CC BY",
        "CC BY SA": "CC BY-SA",
        "CC BY-SA": "CC BY-SA",
        "PD": "PD",
        "PUBLIC DOMAIN": "PD",
    }
    return aliases.get(compact)


def normalize_coordinates_confidence(value: Any) -> Optional[str]:
    raw = normalize_single_select(value)
    if raw is None:
        return None
    normalized = " ".join(raw.strip().lower().split())
    if normalized == "exact":
        return "exact"
    if normalized == "conditional":
        return "conditional"
    if normalized.startswith("approx"):
        return "approximate"
    if normalized in {"estimated", "estimate", "unknown"}:
        return "conditional"
    return None


def normalize_layer_type(value: Any) -> Optional[str]:
    normalized = normalize_single_select(value)
    if normalized is None:
        return None
    aliases = {
        "architecture": "architecture",
        "route_point": "route_point",
        "route point": "route_point",
        "biogeography": "biogeography",
        "biography": "biography",
    }
    return aliases.get(normalized.strip().lower())


def validate_coordinate_range(
    value: Optional[float],
    minimum: float,
    maximum: float,
    record_id: str,
    field: str,
    errors: List[Dict[str, Any]],
) -> Optional[float]:
    """Проверяем диапазон координаты, иначе логируем ошибку и возвращаем None."""
    if value is None:
        return None
    if minimum <= value <= maximum:
        return value
    append_diagnostic(
        errors,
        record_id=record_id,
        field=field,
        error=f"out of range [{minimum}, {maximum}]",
        warning="invalid coordinates",
        value=value,
        severity="critical",
        reason="invalid_coordinates",
    )
    return None


def to_tags(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        tags = [str(v).strip().lower() for v in value if str(v).strip()]
        return tags
    if isinstance(value, str):
        return [chunk.strip().lower() for chunk in value.split(",") if chunk.strip()]
    return []


def safe_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def normalize_linked_record_id(value: Any) -> Optional[str]:
    """Нормализация linked record из Airtable (обычно ['rec...'])."""
    if isinstance(value, list):
        if not value:
            return None
        return safe_str(value[0])
    return safe_str(value)


def normalize_linked_record_ids(value: Any) -> List[str]:
    """Normalize Airtable linked-record payloads to record IDs."""
    if value in (None, ""):
        return []
    items = value if isinstance(value, list) else [value]
    normalized: List[str] = []
    for item in items:
        candidate = item.get("id") if isinstance(item, dict) else item
        record_id = safe_str(candidate)
        if record_id:
            normalized.append(record_id)
    return normalized


def add_issue(issues: List[Dict[str, Any]], severity: str, record_id: str, reason: str, field: Optional[str] = None) -> None:
    normalized_id = record_id or "<missing>"
    payload: Dict[str, Any] = {
        "id": normalized_id,
        "record_id": normalized_id,
        "reason": reason,
        "severity": severity,
    }
    if field:
        payload["field"] = field
    if severity == "critical":
        payload["error"] = reason
    elif severity == "warning":
        payload["warning"] = reason
    issues.append(payload)


def map_record(
    record: Dict[str, Any],
    errors: List[Dict[str, Any]],
    linked_layer_to_public_id: Dict[str, str],
) -> Dict[str, Any]:
    """Преобразование записи Airtable в нормализованную структуру properties."""
    record_id = safe_str(record.get("id")) or ""
    fields = record.get("fields", {}) or {}
    canonical_id = safe_str(fields.get("id"))

    longitude_parse_error = False
    latitude_parse_error = False

    longitude_num_raw = fields.get("longitude_num")
    longitude = to_float_or_none(longitude_num_raw, record_id, "longitude_num", errors)
    if longitude_num_raw not in (None, "") and longitude is None:
        longitude_parse_error = True
    if longitude in (None, ""):
        legacy_longitude = fields.get("longitude")
        if legacy_longitude not in (None, ""):
            # Transitional signal only when canonical field was present but unusable.
            if longitude_num_raw not in (None, ""):
                append_warning_once(
                    errors,
                    record_id=record_id,
                    field="longitude",
                    warning="using legacy fallback field",
                    value=legacy_longitude,
                    reason="legacy_fallback_longitude",
                )
        longitude = to_float_or_none(legacy_longitude, record_id, "longitude", errors)
        if legacy_longitude not in (None, "") and longitude is None:
            longitude_parse_error = True

    latitude_num_raw = fields.get("latitude_num")
    latitude = to_float_or_none(latitude_num_raw, record_id, "latitude_num", errors)
    if latitude_num_raw not in (None, "") and latitude is None:
        latitude_parse_error = True
    if latitude in (None, ""):
        legacy_latitude = fields.get("latitude")
        if legacy_latitude not in (None, ""):
            # Transitional signal only when canonical field was present but unusable.
            if latitude_num_raw not in (None, ""):
                append_warning_once(
                    errors,
                    record_id=record_id,
                    field="latitude",
                    warning="using legacy fallback field",
                    value=legacy_latitude,
                    reason="legacy_fallback_latitude",
                )
        latitude = to_float_or_none(legacy_latitude, record_id, "latitude", errors)
        if legacy_latitude not in (None, "") and latitude is None:
            latitude_parse_error = True

    validated_raw = fields.get("validated")
    if validated_raw in (None, ""):
        validated_raw = fields.get("validated_bool")
    validated = parse_bool(validated_raw)
    if validated is None and validated_raw not in (None, ""):
        append_diagnostic(errors, record_id=record_id, field="validated", error="invalid bool", value=validated_raw)

    is_active_raw = fields.get("is_active")
    if is_active_raw in (None, ""):
        is_active_raw = fields.get("is_active_bool")
    is_active = parse_bool(is_active_raw)
    if is_active is None and is_active_raw not in (None, ""):
        append_diagnostic(errors, record_id=record_id, field="is_active", error="invalid bool", value=is_active_raw)

    source_license_enum_raw = fields.get("source_license_enum")
    source_license = normalize_source_license(source_license_enum_raw)
    if source_license is None:
        source_license = normalize_source_license(fields.get("source_license"))
        if source_license is not None:
            # Transitional signal only when canonical field was present but unusable.
            if source_license_enum_raw not in (None, ""):
                append_warning_once(
                    errors,
                    record_id=record_id,
                    field="source_license",
                    warning="using legacy fallback field",
                    value=source_license,
                    reason="legacy_fallback_source_license",
                )

    coordinates_confidence_enum_raw = fields.get("coordinates_confidence_enum")
    coordinates_confidence = normalize_coordinates_confidence(coordinates_confidence_enum_raw)
    if coordinates_confidence is None:
        coordinates_confidence = normalize_coordinates_confidence(fields.get("coordinates_confidence"))
        if coordinates_confidence is not None:
            # Transitional signal only when canonical field was present but unusable.
            if coordinates_confidence_enum_raw not in (None, ""):
                append_warning_once(
                    errors,
                    record_id=record_id,
                    field="coordinates_confidence",
                    warning="using legacy fallback field",
                    value=coordinates_confidence,
                    reason="legacy_fallback_coordinates_confidence",
                )

    validated_longitude = validate_coordinate_range(longitude, -180.0, 180.0, record_id, "longitude", errors)
    validated_latitude = validate_coordinate_range(latitude, -90.0, 90.0, record_id, "latitude", errors)
    longitude_range_error = longitude is not None and validated_longitude is None
    latitude_range_error = latitude is not None and validated_latitude is None
    longitude = validated_longitude
    latitude = validated_latitude
    source_url = safe_str(fields.get("source_url"))
        
    external_id = safe_str(fields.get("external_id"))
    source_draft_id = safe_str(fields.get("source_draft_id"))
    if source_draft_id is None and external_id and external_id.startswith("draft:"):
        source_draft_id = external_id

    layer_id_field = fields.get("layer_id")
    raw_layer_id: Optional[str] = None
    layer_id_used_legacy_fallback = False
    invalid_layer_link = False
    if isinstance(layer_id_field, list):
        if len(layer_id_field) == 1:
            raw_layer_id = safe_str(layer_id_field[0])
        elif len(layer_id_field) > 1:
            invalid_layer_link = True
    elif layer_id_field in (None, ""):
        raw_layer_id = None
    elif isinstance(layer_id_field, str):
        raw_layer_id = safe_str(layer_id_field)
        layer_id_used_legacy_fallback = raw_layer_id is not None
    else:
        invalid_layer_link = True

    if layer_id_used_legacy_fallback:
        append_warning_once(
            errors,
            record_id=record_id,
            field="layer_id",
            warning="using legacy string fallback",
            value=raw_layer_id,
            reason="legacy_string_layer_id",
        )

    mapped_layer_id = raw_layer_id
    unknown_layer_link = False
    if isinstance(layer_id_field, list) or (raw_layer_id and raw_layer_id.startswith("rec")):
        mapped_layer_id = linked_layer_to_public_id.get(raw_layer_id or "")
        if raw_layer_id and not mapped_layer_id:
            unknown_layer_link = True

    raw_date_start = fields.get("date_start")
    raw_date_end = fields.get("date_end")
    raw_date_start_present = raw_date_start not in (None, "")
    raw_date_end_present = raw_date_end not in (None, "")
    parsed_date_start = to_date_or_none(raw_date_start, record_id, "date_start", errors)
    parsed_date_end = to_date_or_none(raw_date_end, record_id, "date_end", errors)

    mapped = {
        "id": canonical_id,
        "source_record_id": record_id,
        # Deprecated compatibility alias. New consumers use source_record_id.
        "airtable_record_id": record_id,
        "external_id": external_id,
        "source_draft_id": source_draft_id,
        "layer_id": mapped_layer_id,
        "_raw_layer_link_id": raw_layer_id,
        "_unknown_layer_link": unknown_layer_link,
        "_invalid_layer_link": invalid_layer_link,
        "layer_type": normalize_layer_type(fields.get("layer_type_enum") or fields.get("layer_type")),
        "name_ru": safe_str(fields.get("name_ru")),
        "name_en": safe_str(fields.get("name_en")),
        "date_start": parsed_date_start,
        "date_construction_end": to_date_or_none(
            fields.get("date_construction_end"), record_id, "date_construction_end", errors
        ),
        "date_end": parsed_date_end,
        "_raw_date_start_present": raw_date_start_present,
        "_invalid_date_start": raw_date_start_present and parsed_date_start is None,
        "_raw_date_end_present": raw_date_end_present,
        "_invalid_date_end": raw_date_end_present and parsed_date_end is None,
        "longitude": longitude,
        "latitude": latitude,
        "_invalid_coordinates": longitude_parse_error or latitude_parse_error or longitude_range_error or latitude_range_error,
        "influence_radius_km": to_int_or_none(
            fields.get("influence_radius_km"), record_id, "influence_radius_km", errors
        ),
        "title_short": safe_str(fields.get("title_short")),
        "description": safe_str(fields.get("description")),
        "image_url": safe_str(fields.get("image_url")),
        "source_url": source_url,
        "source_license": source_license,
        "coordinates_confidence": coordinates_confidence,
        "coordinates_source": normalize_coordinates_source(fields.get("coordinates_source")),
        "sequence_order": to_int_or_none(fields.get("sequence_order"), record_id, "sequence_order", errors),
        "tags": to_tags(fields.get("tags")),
        "validated": validated,
        "is_active": is_active,
        # Доп. поля для слоёв (если в таблице присутствуют)
        "layer_name_ru": safe_str(fields.get("layer_name_ru") or fields.get("layer_name")),
        "layer_color_hex": safe_str(fields.get("layer_color_hex") or fields.get("color_hex")),
        "layer_icon": safe_str(fields.get("layer_icon") or fields.get("icon")),
    }
    return mapped


def get_origin_key(mapped: Dict[str, Any]) -> Optional[str]:
    # Source reference identity (non-canonical for publish dedupe).
    for field in ("external_id", "source_draft_id", "source_record_id", "airtable_record_id"):
        value = mapped.get(field)
        if value:
            return str(value)
    return None


def get_canonical_publish_id(mapped: Dict[str, Any]) -> Optional[str]:
    canonical_id = safe_str(mapped.get("id"))
    return canonical_id if is_uuid_v4(canonical_id) else None


def get_diagnostic_record_id(mapped: Dict[str, Any]) -> str:
    """Use source identity in diagnostics so invalid canonical ids stay traceable."""
    return str(
        mapped.get("source_record_id")
        or mapped.get("airtable_record_id")
        or mapped.get("id")
        or "<missing>"
    )


def load_id_aliases(path: Path) -> Dict[str, Any]:
    """Load and validate a versioned alias artifact, or return an empty v1 map."""
    if not path.exists():
        return {"schema_version": 1, "canonical_format": "uuid_v4", "aliases": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError(f"Unsupported id alias schema in {path}")
    aliases = payload.get("aliases")
    if not isinstance(aliases, dict):
        raise ValueError(f"id alias artifact must contain an aliases object: {path}")
    for legacy_id, canonical_id in aliases.items():
        if not safe_str(legacy_id) or not is_uuid_v4(canonical_id):
            raise ValueError(f"Invalid id alias {legacy_id!r} -> {canonical_id!r} in {path}")
    return {
        "schema_version": 1,
        "canonical_format": "uuid_v4",
        "aliases": dict(aliases),
    }


def build_id_aliases(
    mapped_records: Iterable[Dict[str, Any]],
    existing_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Merge durable historical aliases with current source-record aliases."""
    existing = existing_payload or {}
    existing_aliases = existing.get("aliases", existing)
    if not isinstance(existing_aliases, dict):
        raise ValueError("existing id aliases must be an object")

    aliases: Dict[str, str] = {}
    for legacy_id, canonical_id in existing_aliases.items():
        normalized_legacy = safe_str(legacy_id)
        normalized_canonical = safe_str(canonical_id)
        if not normalized_legacy or not is_uuid_v4(normalized_canonical):
            raise ValueError(f"Invalid id alias {legacy_id!r} -> {canonical_id!r}")
        if normalized_legacy != normalized_canonical:
            aliases[normalized_legacy] = normalized_canonical

    for mapped in mapped_records:
        canonical_id = get_canonical_publish_id(mapped)
        source_record_id = safe_str(mapped.get("source_record_id") or mapped.get("airtable_record_id"))
        if canonical_id and source_record_id and source_record_id != canonical_id:
            aliases[source_record_id] = canonical_id

    return {
        "schema_version": 1,
        "canonical_format": "uuid_v4",
        "aliases": dict(sorted(aliases.items())),
    }


def get_legacy_ids(canonical_id: Any, id_aliases: Dict[str, str]) -> List[str]:
    normalized_canonical = safe_str(canonical_id)
    if not normalized_canonical:
        return []
    return sorted(legacy_id for legacy_id, target in id_aliases.items() if target == normalized_canonical)


def get_dedupe_key(mapped: Dict[str, Any]) -> Tuple[Any, ...]:
    return (mapped.get("name_ru") or "", mapped.get("latitude"), mapped.get("longitude"))


def airtable_get_with_retry(
    session: requests.Session,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, Any],
    max_retries_429: int = 5,
) -> requests.Response:
    """GET с обработкой 429 (экспоненциальный бэкофф) и сетевых ошибок."""
    backoff = 30
    attempts_429 = 0

    while True:
        try:
            resp = session.get(url, headers=headers, params=params, timeout=30)
        except requests.RequestException as exc:
            raise RuntimeError(f"Сетевая ошибка при запросе к Airtable: {exc}") from exc

        if resp.status_code == 429:
            attempts_429 += 1
            if attempts_429 > max_retries_429:
                raise RuntimeError("Превышено число ретраев после 429 (rate limit)")
            print(f"Получен 429, ждём {backoff}s и повторяем ({attempts_429}/{max_retries_429})...")
            time.sleep(backoff)
            backoff *= 2
            continue

        return resp


def fetch_airtable_records(
    token: str,
    base: str,
    table: str,
    max_records: Optional[int],
) -> List[Dict[str, Any]]:
    """Чтение всех страниц Airtable по offset (pageSize=100)."""
    url = f"https://api.airtable.com/v0/{base}/{table}"
    headers = {"Authorization": f"Bearer {token}"}
    records: List[Dict[str, Any]] = []
    offset: Optional[str] = None
    page_no = 0

    with requests.Session() as session:
        while True:
            params: Dict[str, Any] = {"pageSize": 100}
            if offset:
                params["offset"] = offset

            resp = airtable_get_with_retry(session, url, headers, params)
            if resp.status_code in (401, 403):
                raise PermissionError("Ошибка авторизации Airtable (401/403). Проверьте AIRTABLE_TOKEN и права доступа.")
            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")

            try:
                payload = resp.json()
            except ValueError as exc:
                raise RuntimeError(f"Некорректный JSON в ответе Airtable: {exc}") from exc

            page_records = payload.get("records", [])
            page_no += 1
            records.extend(page_records)
            print(f"Страница {page_no}: +{len(page_records)} записей (всего: {len(records)})")

            if max_records is not None and len(records) >= max_records:
                return records[:max_records]

            offset = payload.get("offset")
            if not offset:
                break

            # Соблюдение лимита Airtable: до 5 req/s
            time.sleep(0.25)

    return records


def generate_mock_records() -> List[Dict[str, Any]]:
    """Dry-run для CI: не требует secrets и не ходит в Airtable."""
    return [
        {
            "id": "recTEST",
            "fields": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "layer_id": "test_layer",
                "layer_type_enum": "biography",
                "name_ru": "Тестовая запись",
                "date_start": "1348",
                "longitude": 37.6173,
                "latitude": 55.7558,
                "influence_radius_km": 12,
                "layer_color_hex": "#ABCDEF",
                "tags": "test",
                "validated": True,
                "source_license": "CC BY",
                "coordinates_confidence_enum": "exact",
                "source_url": "https://example.com/source",
                "coordinates_source": "Wikipedia",
                "sequence_order": 1,
            },
        },
        {
            "id": "recRelatedTEST",
            "fields": {
                "id": "8f14e45f-ea26-4c4b-9b29-7c1d0b6f9a22",
                "layer_id": "test_layer",
                "layer_type_enum": "biography",
                "name_ru": "Связанная тестовая запись",
                "date_start": "1400",
                "longitude": 38.0,
                "latitude": 56.0,
                "influence_radius_km": 8,
                "layer_color_hex": "#ABCDEF",
                "tags": "test",
                "validated": True,
                "source_license": "CC BY",
                "coordinates_confidence_enum": "exact",
                "source_url": "https://example.com/source",
                "coordinates_source": "Wikipedia",
                "sequence_order": 2,
            },
        },
    ]


def generate_mock_layers_records() -> List[Dict[str, Any]]:
    return [
        {
            "id": "recLayerTEST",
            "fields": {
                "layer_id": "test_layer",
                "name_ru": "Тестовый слой",
                "name_en": "Test layer",
                "color_hex": "#ABCDEF",
                "icon": "test",
                "is_enabled": True,
            },
        }
    ]


def generate_mock_sources_records() -> List[Dict[str, Any]]:
    return [
        {
            "id": "recSourceTEST",
            "fields": {
                "id": "src_test_reference",
                "url": "https://example.com/source",
                "title": "Test reference",
                "author_or_organization": "Example Organization",
                "source_type": "institutional",
                "accessed_at": "2026-07-16",
                "review_status": "reviewed",
                "content_license": "CC BY",
            },
        }
    ]


def generate_mock_media_records() -> List[Dict[str, Any]]:
    return [
        {
            "id": "recMediaTEST",
            "fields": {
                "id": "media_test_image",
                "asset_url": "https://example.com/image.jpg",
                "source_page_url": "https://example.com/media",
                "creator": "Example Creator",
                "license": "CC BY",
                "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "attribution_text": "Example Creator, CC BY 4.0",
                "media_type": "image",
                "review_status": "reviewed",
            },
        }
    ]


def generate_mock_feature_sources_records() -> List[Dict[str, Any]]:
    return [
        {
            "id": "recFeatureSourceTEST",
            "fields": {
                "feature": ["recTEST"],
                "source": ["recSourceTEST"],
                "roles": ["general_reference"],
                "is_primary": True,
                "review_status": "reviewed",
            },
        },
        {
            "id": "recRelatedFeatureSourceTEST",
            "fields": {
                "feature": ["recRelatedTEST"],
                "source": ["recSourceTEST"],
                "roles": ["general_reference"],
                "is_primary": True,
                "review_status": "reviewed",
            },
        },
    ]


def generate_mock_feature_media_records() -> List[Dict[str, Any]]:
    return [
        {
            "id": "recFeatureMediaTEST",
            "fields": {
                "feature": ["recTEST"],
                "media": ["recMediaTEST"],
                "display_role": "primary",
                "sort_order": 1,
                "review_status": "reviewed",
            },
        }
    ]


def generate_mock_relations_records() -> List[Dict[str, Any]]:
    return [
        {
            "id": "recRelationTEST",
            "fields": {
                "id": "c9f0f895-fb98-4f6f-91f6-7ca4f8d76a33",
                "source_feature": ["recTEST"],
                "target_feature": ["recRelatedTEST"],
                "relation_type": "influenced",
                "description": "The first test Feature influenced the second test Feature.",
                "epistemic_status": "fact",
                "confidence": "medium",
                "review_status": "reviewed",
            },
        }
    ]


def generate_mock_relation_sources_records() -> List[Dict[str, Any]]:
    return [
        {
            "id": "recRelationSourceTEST",
            "fields": {
                "relation": ["recRelationTEST"],
                "source": ["recSourceTEST"],
                "roles": ["relation_evidence"],
                "claim_note": "Test evidence supports the explicit influence claim.",
                "review_status": "reviewed",
            },
        }
    ]


def build_geojson_features(
    mapped_records: Iterable[Dict[str, Any]],
    warnings: List[Dict[str, Any]],
    errors: List[Dict[str, Any]],
    id_aliases: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    features = []
    resolved_aliases = id_aliases or {}
    for m in mapped_records:
        record_id = get_diagnostic_record_id(m)
        if parse_bool(m.get("validated")) is not True:
            add_issue(errors, "critical", record_id, "not_validated", "validated")
            continue
        etl_error = get_etl_error(m)
        if etl_error is not None:
            add_issue(errors, "critical", record_id, etl_error, "etl_error")
            continue
        lon = m.get("longitude")
        lat = m.get("latitude")
        if lat is None or lon is None:
            add_issue(errors, "critical", record_id, "missing_geometry", "geometry")
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            add_issue(errors, "critical", record_id, "invalid_coordinates", "geometry")
            continue
        geometry = {"type": "Point", "coordinates": [lon, lat]}
                
        features.append(
            {
                "type": "Feature",
                "id": m.get("id"),
                "geometry": geometry,
                "properties": {
                    "id": m.get("id"),
                    "canonical_publish_id": get_canonical_publish_id(m),
                    "source_record_id": m.get("source_record_id") or m.get("airtable_record_id"),
                    "legacy_ids": get_legacy_ids(m.get("id"), resolved_aliases),
                    # Deprecated compatibility alias. New consumers use source_record_id.
                    "airtable_record_id": m.get("airtable_record_id"),
                    "external_id": m.get("external_id"),
                    "source_draft_id": m.get("source_draft_id"),
                    "origin_key": get_origin_key(m),
                    "layer_id": m.get("layer_id"),
                    "layer_type": m.get("layer_type"),
                    "name_ru": m.get("name_ru"),
                    "name_en": m.get("name_en"),
                    "date_start": m.get("date_start"),
                    "date_construction_end": m.get("date_construction_end"),
                    "date_end": m.get("date_end"),
                    "longitude": m.get("longitude"),
                    "latitude": m.get("latitude"),
                    "influence_radius_km": m.get("influence_radius_km"),
                    "title_short": m.get("title_short"),
                    "description": m.get("description"),
                    "image_url": m.get("image_url"),
                    "source_url": m.get("source_url"),
                    "source_ids": m.get("source_ids", []),
                    "source_refs": m.get("source_refs", []),
                    "media_ids": m.get("media_ids", []),
                    "media_refs": m.get("media_refs", []),
                    "relation_ids": m.get("relation_ids", []),
                    "source_license": m.get("source_license"),
                    "coordinates_confidence": m.get("coordinates_confidence"),
                    "coordinates_source": m.get("coordinates_source"),
                    "sequence_order": m.get("sequence_order"),
                    "tags": m.get("tags"),
                    "validated": m.get("validated"),
                    "date_valid": m.get("date_valid"),
                    "has_geometry": geometry is not None,
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def get_etl_error(mapped: Dict[str, Any]) -> Optional[str]:
    existing_error = safe_str(mapped.get("etl_error"))
    if existing_error:
        return existing_error
    record_id = safe_str(mapped.get("id"))
    if not record_id:
        return "missing_id"
    if not is_uuid_v4(record_id):
        return "invalid_id_uuid_v4"
    if "name_ru" in mapped and not safe_str(mapped.get("name_ru")):
        return "missing_name_ru"
    if "layer_type" in mapped and mapped.get("layer_type") not in ALLOWED_LAYER_TYPES:
        return "invalid_layer_type"
    if mapped.get("_normalized_source_refs_checked"):
        source_refs = mapped.get("source_refs") or []
        if not source_refs:
            return "missing_reviewed_source"
        if len([ref for ref in source_refs if ref.get("is_primary")]) != 1:
            return "invalid_primary_source_count"
        if len({ref.get("source_id") for ref in source_refs}) != len(source_refs):
            return "duplicate_feature_source_reference"
        media_refs = mapped.get("media_refs") or []
        if len([ref for ref in media_refs if ref.get("display_role") == "primary"]) > 1:
            return "invalid_primary_media_count"
        if len({ref.get("media_id") for ref in media_refs}) != len(media_refs):
            return "duplicate_feature_media_reference"
    source_url = safe_str(mapped.get("source_url"))
    if not source_url:
        return "missing_source_url"
    parsed_source_url = urlparse(source_url.strip())
    if parsed_source_url.scheme not in ("http", "https") or parsed_source_url.netloc == "":
        return "invalid_source_url"
    image_url = safe_str(mapped.get("image_url"))
    if image_url and not is_valid_url(image_url):
        return "invalid_image_url"
    if not is_valid_license(mapped.get("source_license")):
        return "invalid_license"
    if mapped.get("_invalid_coordinates"):
        return "invalid_coordinates"
    latitude = parse_float(mapped.get("latitude"))
    longitude = parse_float(mapped.get("longitude"))
    if latitude is None or longitude is None:
        return "missing_geometry"
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return "invalid_coordinates"
    if "_raw_date_start_present" in mapped:
        if not mapped.get("_raw_date_start_present"):
            return "missing_date_start"
        if mapped.get("_invalid_date_start") or not is_valid_iso_date(mapped.get("date_start")):
            return "invalid_date_start"
    elif mapped.get("date_start") not in (None, "") and not is_valid_iso_date(mapped.get("date_start")):
        return "invalid_date_start"

    if "_raw_date_end_present" in mapped:
        if mapped.get("_raw_date_end_present") and (
            mapped.get("_invalid_date_end") or not is_valid_iso_date(mapped.get("date_end"))
        ):
            return "invalid_date_end"
    elif mapped.get("date_end") not in (None, "") and not is_valid_iso_date(mapped.get("date_end")):
        return "invalid_date_end"
    if mapped.get("_invalid_layer_link"):
        return "invalid_layer_link_format"
    layer_id = mapped.get("layer_id")
    if not layer_id:
        return "unknown_layer_link" if mapped.get("_unknown_layer_link") else "missing_layer_id"
    if mapped.get("_unknown_layer_link"):
        return "unknown_layer_link"
    return None


def normalize_hex_color(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip().lower()
    if HEX_COLOR_RE.match(cleaned):
        return cleaned
    return None


def map_layers(layer_records: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, str], List[Dict[str, Any]]]:
    linked_layer_to_public_id: Dict[str, str] = {}
    layers: List[Dict[str, Any]] = []

    for record in layer_records:
        record_id = record.get("id")
        fields = record.get("fields", {}) or {}
        layer_id = safe_str(fields.get("layer_id"))
        if record_id and layer_id:
            linked_layer_to_public_id[record_id] = layer_id
        layers.append(
            {
                "layer_id": layer_id,
                "name_ru": safe_str(fields.get("name_ru")),
                "name_en": safe_str(fields.get("name_en")),
                "color_hex": normalize_hex_color(safe_str(fields.get("color_hex"))),
                "icon": safe_str(fields.get("icon")),
                "is_enabled": parse_bool(fields.get("is_enabled")),
            }
        )
    return linked_layer_to_public_id, layers


def map_sources(
    source_records: Iterable[Dict[str, Any]],
    warnings: List[Dict[str, Any]],
    errors: List[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """Map all Source records and return the reviewed public subset."""
    by_record_id: Dict[str, Dict[str, Any]] = {}
    reviewed: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for record in source_records:
        record_id = safe_str(record.get("id")) or "<missing>"
        fields = record.get("fields", {}) or {}
        mapped = {
            "id": safe_str(fields.get("id")),
            "source_record_id": record_id,
            "url": safe_str(fields.get("url")),
            "bibliographic_locator": safe_str(fields.get("bibliographic_locator")),
            "title": safe_str(fields.get("title")),
            "author_or_organization": safe_str(fields.get("author_or_organization")),
            "source_type": normalize_single_select(fields.get("source_type")),
            "accessed_at": safe_str(fields.get("accessed_at")),
            "review_status": normalize_single_select(fields.get("review_status")),
            "content_license": safe_str(fields.get("content_license")),
        }
        by_record_id[record_id] = mapped
        if mapped["review_status"] != "reviewed":
            continue
        source_id = mapped["id"]
        if not source_id:
            add_issue(errors, "critical", record_id, "missing_source_id", "id")
            continue
        if source_id in seen_ids:
            add_issue(errors, "critical", record_id, "duplicate_source_id", "id")
            continue
        seen_ids.add(source_id)
        valid = True
        if not mapped["url"] and not mapped["bibliographic_locator"]:
            add_issue(errors, "critical", record_id, "missing_source_locator", "url")
            valid = False
        if mapped["url"] and not is_valid_url(mapped["url"]):
            add_issue(errors, "critical", record_id, "invalid_source_locator", "url")
            valid = False
        if not mapped["title"]:
            add_issue(errors, "critical", record_id, "missing_source_title", "title")
            valid = False
        if not mapped["author_or_organization"]:
            add_issue(errors, "critical", record_id, "missing_source_author", "author_or_organization")
            valid = False
        if mapped["source_type"] not in ALLOWED_SOURCE_TYPES:
            add_issue(errors, "critical", record_id, "invalid_source_type", "source_type")
            valid = False
        if valid:
            reviewed.append(mapped)
    return by_record_id, sorted(reviewed, key=lambda item: item.get("id") or "")


def is_direct_media_asset_url(value: Any) -> bool:
    url = safe_str(value)
    if not is_valid_url(url):
        return False
    parsed = urlparse(url or "")
    path = parsed.path.lower()
    return not ("commons.wikimedia.org" in parsed.netloc.lower() and "/wiki/file:" in path)


def map_media(
    media_records: Iterable[Dict[str, Any]],
    warnings: List[Dict[str, Any]],
    errors: List[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """Map all Media records and return the reviewed public subset."""
    by_record_id: Dict[str, Dict[str, Any]] = {}
    reviewed: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    for record in media_records:
        record_id = safe_str(record.get("id")) or "<missing>"
        fields = record.get("fields", {}) or {}
        mapped = {
            "id": safe_str(fields.get("id")),
            "source_record_id": record_id,
            "asset_url": safe_str(fields.get("asset_url")),
            "source_page_url": safe_str(fields.get("source_page_url")),
            "creator": safe_str(fields.get("creator")),
            "license": normalize_source_license(fields.get("license")),
            "license_url": safe_str(fields.get("license_url")),
            "attribution_text": safe_str(fields.get("attribution_text")),
            "media_type": normalize_single_select(fields.get("media_type")),
            "review_status": normalize_single_select(fields.get("review_status")),
        }
        by_record_id[record_id] = mapped
        if mapped["review_status"] != "reviewed":
            continue
        media_id = mapped["id"]
        if not media_id:
            add_issue(errors, "critical", record_id, "missing_media_id", "id")
            continue
        if media_id in seen_ids:
            add_issue(errors, "critical", record_id, "duplicate_media_id", "id")
            continue
        seen_ids.add(media_id)
        valid = True
        if not is_direct_media_asset_url(mapped["asset_url"]):
            add_issue(errors, "critical", record_id, "invalid_media_asset_url", "asset_url")
            valid = False
        if not is_valid_url(mapped["source_page_url"]):
            add_issue(errors, "critical", record_id, "invalid_media_source_page", "source_page_url")
            valid = False
        if not mapped["creator"]:
            add_issue(errors, "critical", record_id, "missing_media_creator", "creator")
            valid = False
        if not is_valid_license(mapped["license"]):
            add_issue(errors, "critical", record_id, "invalid_media_license", "license")
            valid = False
        if not mapped["attribution_text"]:
            add_issue(errors, "critical", record_id, "missing_media_attribution", "attribution_text")
            valid = False
        if mapped["media_type"] not in ALLOWED_MEDIA_TYPES:
            add_issue(errors, "critical", record_id, "invalid_media_type", "media_type")
            valid = False
        if valid:
            reviewed.append(mapped)
    return by_record_id, sorted(reviewed, key=lambda item: item.get("id") or "")


def map_feature_source_refs(
    records: Iterable[Dict[str, Any]],
    feature_id_by_record_id: Dict[str, str],
    source_by_record_id: Dict[str, Dict[str, Any]],
    errors: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    refs: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        record_id = safe_str(record.get("id")) or "<missing>"
        fields = record.get("fields", {}) or {}
        if normalize_single_select(fields.get("review_status")) != "reviewed":
            continue
        feature_links = normalize_linked_record_ids(fields.get("feature"))
        source_links = normalize_linked_record_ids(fields.get("source"))
        if len(feature_links) != 1 or len(source_links) != 1:
            add_issue(errors, "critical", record_id, "invalid_feature_source_cardinality", "feature/source")
            continue
        feature_id = feature_id_by_record_id.get(feature_links[0])
        source = source_by_record_id.get(source_links[0])
        if not feature_id or not source or source.get("review_status") != "reviewed":
            add_issue(errors, "critical", record_id, "invalid_feature_source_reference", "feature/source")
            continue
        roles = sorted(set(to_tags(fields.get("roles"))))
        if not roles or any(role not in ALLOWED_SOURCE_ROLES for role in roles):
            add_issue(errors, "critical", record_id, "invalid_source_roles", "roles")
            continue
        refs.setdefault(feature_id, []).append(
            {
                "source_id": source.get("id"),
                "roles": roles,
                "is_primary": parse_bool(fields.get("is_primary")) is True,
            }
        )
    return refs


def map_feature_media_refs(
    records: Iterable[Dict[str, Any]],
    feature_id_by_record_id: Dict[str, str],
    media_by_record_id: Dict[str, Dict[str, Any]],
    errors: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    refs: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        record_id = safe_str(record.get("id")) or "<missing>"
        fields = record.get("fields", {}) or {}
        if normalize_single_select(fields.get("review_status")) != "reviewed":
            continue
        feature_links = normalize_linked_record_ids(fields.get("feature"))
        media_links = normalize_linked_record_ids(fields.get("media"))
        if len(feature_links) != 1 or len(media_links) != 1:
            add_issue(errors, "critical", record_id, "invalid_feature_media_cardinality", "feature/media")
            continue
        feature_id = feature_id_by_record_id.get(feature_links[0])
        media = media_by_record_id.get(media_links[0])
        role = normalize_single_select(fields.get("display_role"))
        if not feature_id or not media or media.get("review_status") != "reviewed":
            add_issue(errors, "critical", record_id, "invalid_feature_media_reference", "feature/media")
            continue
        if role not in ALLOWED_MEDIA_DISPLAY_ROLES:
            add_issue(errors, "critical", record_id, "invalid_media_display_role", "display_role")
            continue
        refs.setdefault(feature_id, []).append(
            {
                "media_id": media.get("id"),
                "display_role": role,
                "sort_order": to_int_or_none(fields.get("sort_order"), record_id, "sort_order", errors) or 0,
            }
        )
    return refs


def attach_source_media_refs(
    features: Iterable[Dict[str, Any]],
    source_refs_by_feature: Dict[str, List[Dict[str, Any]]],
    sources_by_id: Dict[str, Dict[str, Any]],
    media_refs_by_feature: Dict[str, List[Dict[str, Any]]],
    media_by_id: Dict[str, Dict[str, Any]],
    warnings: List[Dict[str, Any]],
) -> None:
    for feature in features:
        feature_id = safe_str(feature.get("id")) or "<missing>"
        source_refs = sorted(source_refs_by_feature.get(feature_id, []), key=lambda item: item.get("source_id") or "")
        media_refs = sorted(
            media_refs_by_feature.get(feature_id, []),
            key=lambda item: (item.get("sort_order") or 0, item.get("media_id") or ""),
        )
        feature["source_refs"] = source_refs
        feature["source_ids"] = [ref["source_id"] for ref in source_refs]
        feature["media_refs"] = media_refs
        feature["media_ids"] = [ref["media_id"] for ref in media_refs]
        feature["_normalized_source_refs_checked"] = True

        primary_sources = [ref for ref in source_refs if ref.get("is_primary")]
        if len(primary_sources) == 1:
            primary_source = sources_by_id.get(primary_sources[0]["source_id"])
            if primary_source and primary_source.get("url"):
                feature["source_url"] = primary_source["url"]

        primary_media = [ref for ref in media_refs if ref.get("display_role") == "primary"]
        if len(primary_media) == 1:
            media = media_by_id.get(primary_media[0]["media_id"])
            if media and media.get("asset_url"):
                feature["image_url"] = media["asset_url"]
        else:
            # Legacy page URLs are not publishable Media. Missing reviewed Media
            # is reported later as an explicit semantic-quality warning.
            feature["image_url"] = None


def relation_date_sort_key(value: Optional[str]) -> Optional[Tuple[int, str]]:
    if not value:
        return None
    normalized = str(value).strip()
    year_text = normalized[:5] if normalized.startswith("-") else normalized[:4]
    try:
        return int(year_text), normalized
    except ValueError:
        return None


def map_relations(
    records: Iterable[Dict[str, Any]],
    feature_id_by_record_id: Dict[str, str],
    errors: List[Dict[str, Any]],
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """Map reviewed Relation candidates before evidence eligibility is applied."""
    by_record_id: Dict[str, Dict[str, Any]] = {}
    reviewed: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_predicates: set[Tuple[str, str, str]] = set()
    for record in records:
        record_id = safe_str(record.get("id")) or "<missing>"
        fields = record.get("fields", {}) or {}
        review_status = normalize_single_select(fields.get("review_status"))
        if review_status != "reviewed":
            continue
        source_links = normalize_linked_record_ids(fields.get("source_feature"))
        target_links = normalize_linked_record_ids(fields.get("target_feature"))
        if len(source_links) != 1 or len(target_links) != 1:
            add_issue(errors, "critical", record_id, "invalid_relation_endpoint_cardinality", "source_feature/target_feature")
            continue
        source_feature_id = feature_id_by_record_id.get(source_links[0])
        target_feature_id = feature_id_by_record_id.get(target_links[0])
        if not source_feature_id or not target_feature_id:
            add_issue(errors, "critical", record_id, "invalid_relation_feature_reference", "source_feature/target_feature")
            continue
        relation_id = safe_str(fields.get("id"))
        relation_type = normalize_single_select(fields.get("relation_type"))
        description = safe_str(fields.get("description"))
        epistemic_status = normalize_single_select(fields.get("epistemic_status"))
        confidence = normalize_single_select(fields.get("confidence"))
        valid_from = safe_str(fields.get("valid_from"))
        valid_to = safe_str(fields.get("valid_to"))
        valid = True

        def critical(field: str, reason: str) -> None:
            nonlocal valid
            valid = False
            add_issue(errors, "critical", record_id, reason, field)

        if not is_uuid_v4(relation_id):
            critical("id", "invalid_relation_id_uuid_v4")
        elif relation_id in seen_ids:
            critical("id", "duplicate_relation_id")
        if source_feature_id == target_feature_id:
            critical("source_feature/target_feature", "self_relation")
        if relation_type not in ALLOWED_RELATION_TYPES:
            critical("relation_type", "invalid_relation_type")
        if not description:
            critical("description", "missing_relation_description")
        elif CAUSAL_CLAIM_RE.search(description):
            critical("description", "unsupported_causal_relation_claim")
        if epistemic_status not in ALLOWED_EPISTEMIC_STATUSES:
            critical("epistemic_status", "invalid_relation_epistemic_status")
        if confidence not in ALLOWED_RELATION_CONFIDENCE:
            critical("confidence", "invalid_relation_confidence")
        if valid_from and not is_valid_iso_date(valid_from):
            critical("valid_from", "invalid_relation_valid_from")
        if valid_to and not is_valid_iso_date(valid_to):
            critical("valid_to", "invalid_relation_valid_to")
        from_key = relation_date_sort_key(valid_from)
        to_key = relation_date_sort_key(valid_to)
        if from_key and to_key and from_key > to_key:
            critical("valid_from/valid_to", "invalid_relation_temporal_range")
        if relation_type in SYMMETRIC_RELATION_TYPES and source_feature_id > target_feature_id:
            critical("source_feature/target_feature", "unsorted_symmetric_relation_endpoints")

        predicate = (source_feature_id, relation_type or "", target_feature_id)
        if predicate in seen_predicates:
            critical("source_feature/relation_type/target_feature", "duplicate_relation_predicate")
        if not valid:
            continue
        seen_ids.add(relation_id or "")
        seen_predicates.add(predicate)
        mapped = {
            "id": relation_id,
            "source_record_id": record_id,
            "source_feature_id": source_feature_id,
            "target_feature_id": target_feature_id,
            "relation_type": relation_type,
            "description": description,
            "epistemic_status": epistemic_status,
            "confidence": confidence,
            "valid_from": valid_from,
            "valid_to": valid_to,
            "review_status": review_status,
        }
        by_record_id[record_id] = mapped
        reviewed.append(mapped)
    return by_record_id, sorted(reviewed, key=lambda item: item.get("id") or "")


def map_relation_source_refs(
    records: Iterable[Dict[str, Any]],
    relation_by_record_id: Dict[str, Dict[str, Any]],
    source_by_record_id: Dict[str, Dict[str, Any]],
    errors: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    refs: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        record_id = safe_str(record.get("id")) or "<missing>"
        fields = record.get("fields", {}) or {}
        if normalize_single_select(fields.get("review_status")) != "reviewed":
            continue
        relation_links = normalize_linked_record_ids(fields.get("relation"))
        source_links = normalize_linked_record_ids(fields.get("source"))
        if len(relation_links) != 1 or len(source_links) != 1:
            add_issue(errors, "critical", record_id, "invalid_relation_source_cardinality", "relation/source")
            continue
        relation = relation_by_record_id.get(relation_links[0])
        source = source_by_record_id.get(source_links[0])
        if not relation or not source or source.get("review_status") != "reviewed":
            add_issue(errors, "critical", record_id, "invalid_relation_source_reference", "relation/source")
            continue
        roles = sorted(set(to_tags(fields.get("roles"))))
        claim_note = safe_str(fields.get("claim_note"))
        if not roles or any(role not in ALLOWED_RELATION_SOURCE_ROLES for role in roles):
            add_issue(errors, "critical", record_id, "invalid_relation_source_roles", "roles")
            continue
        if "relation_evidence" not in roles:
            add_issue(errors, "critical", record_id, "missing_relation_evidence_role", "roles")
            continue
        if not claim_note:
            add_issue(errors, "critical", record_id, "missing_relation_claim_note", "claim_note")
            continue
        refs.setdefault(relation["id"], []).append(
            {
                "source_id": source.get("id"),
                "roles": roles,
                "claim_note": claim_note,
                "title": source.get("title"),
                "url": source.get("url"),
            }
        )
    return refs


def finalize_relations(
    candidates: Iterable[Dict[str, Any]],
    source_refs_by_relation: Dict[str, List[Dict[str, Any]]],
    errors: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    reviewed: List[Dict[str, Any]] = []
    for candidate in candidates:
        relation_id = safe_str(candidate.get("id")) or "<missing>"
        refs = sorted(source_refs_by_relation.get(relation_id, []), key=lambda item: item.get("source_id") or "")
        source_ids = [ref.get("source_id") for ref in refs]
        if not refs:
            add_issue(errors, "critical", relation_id, "missing_reviewed_relation_evidence", "source_refs")
            continue
        if len(set(source_ids)) != len(source_ids):
            add_issue(errors, "critical", relation_id, "duplicate_relation_source_reference", "source_refs")
            continue
        public = {key: value for key, value in candidate.items() if key not in {"source_record_id", "review_status"}}
        public["source_ids"] = source_ids
        public["source_refs"] = refs
        reviewed.append(public)
    return sorted(reviewed, key=lambda item: item.get("id") or "")


def attach_relation_ids(features: Iterable[Dict[str, Any]], relations: Iterable[Dict[str, Any]]) -> None:
    ids_by_feature: Dict[str, List[str]] = {}
    for relation in relations:
        relation_id = safe_str(relation.get("id"))
        if not relation_id:
            continue
        for feature_id in (relation.get("source_feature_id"), relation.get("target_feature_id")):
            normalized = safe_str(feature_id)
            if normalized:
                ids_by_feature.setdefault(normalized, []).append(relation_id)
    for feature in features:
        feature_id = safe_str(feature.get("id")) or "<missing>"
        feature["relation_ids"] = sorted(set(ids_by_feature.get(feature_id, [])))


def validate_feature(mapped: Dict[str, Any], layer_ids: set[str], warnings: List[Dict[str, Any]], errors: List[Dict[str, Any]]) -> bool:
    record_id = get_diagnostic_record_id(mapped)
    valid = True

    def critical(field: str, reason: str) -> None:
        nonlocal valid
        valid = False
        add_issue(errors, "critical", record_id, reason, field)

    def warning(field: str, reason: str) -> None:
        add_issue(warnings, "warning", record_id, reason, field)

    if not mapped.get("id"):
        critical("id", "missing_id")
    elif not is_uuid_v4(mapped.get("id")):
        critical("id", "invalid_id_uuid_v4")
    if not mapped.get("name_ru"):
        critical("name_ru", "missing_name_ru")
    if mapped.get("_normalized_source_refs_checked"):
        source_refs = mapped.get("source_refs") or []
        if not source_refs:
            critical("source_refs", "missing_reviewed_source")
        elif len([ref for ref in source_refs if ref.get("is_primary")]) != 1:
            critical("source_refs", "invalid_primary_source_count")
        elif len({ref.get("source_id") for ref in source_refs}) != len(source_refs):
            critical("source_refs", "duplicate_feature_source_reference")
        media_refs = mapped.get("media_refs") or []
        if len([ref for ref in media_refs if ref.get("display_role") == "primary"]) > 1:
            critical("media_refs", "invalid_primary_media_count")
        elif len({ref.get("media_id") for ref in media_refs}) != len(media_refs):
            critical("media_refs", "duplicate_feature_media_reference")
    has_start = bool(mapped.get("_raw_date_start_present"))
    if not has_start:
        critical("date_start", "missing_date_start")
    elif mapped.get("_invalid_date_start") or not is_valid_iso_date(mapped.get("date_start")):
        critical("date_start", "invalid_date_start")
    if mapped.get("_raw_date_end_present") and (
        mapped.get("_invalid_date_end") or not is_valid_iso_date(mapped.get("date_end"))
    ):
        critical("date_end", "invalid_date_end")
    validated_value = parse_bool(mapped.get("validated"))
    if validated_value is not True:
        critical("validated", "not_validated")
    source_url = mapped.get("source_url")
    if not source_url:
        critical("source_url", "missing_source_url")
    else:
        parsed_source_url = urlparse(source_url.strip())
        if parsed_source_url.scheme not in ("http", "https") or parsed_source_url.netloc == "":
            critical("source_url", "invalid_source_url")
    if mapped.get("layer_type") not in ALLOWED_LAYER_TYPES:
        critical("layer_type", "invalid_layer_type")
    if mapped.get("_invalid_coordinates"):
        critical("geometry", "invalid_coordinates")
    raw_latitude = mapped.get("latitude")
    raw_longitude = mapped.get("longitude")
    latitude = parse_float(raw_latitude)
    longitude = parse_float(raw_longitude)
    if raw_latitude not in (None, "") and latitude is None:
        mapped["_invalid_coordinates"] = True
    if raw_longitude not in (None, "") and longitude is None:
        mapped["_invalid_coordinates"] = True
    mapped["latitude"] = latitude
    mapped["longitude"] = longitude
    if latitude is None and longitude is None:
        critical("geometry", "missing_geometry")
    elif (latitude is None) ^ (longitude is None):
        critical("geometry", "missing_geometry_coordinate")
    elif latitude is not None and longitude is not None and not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        critical("geometry", "invalid_coordinates")
    date_valid = (
        not mapped.get("_invalid_date_start")
        and not mapped.get("_invalid_date_end")
        and is_valid_iso_date(mapped.get("date_start"))
        and is_valid_iso_date(mapped.get("date_end"))
    )
    mapped["date_valid"] = date_valid
    if not is_valid_license(mapped.get("source_license")):
        critical("source_license", "invalid_license")
    if mapped.get("coordinates_confidence") not in ALLOWED_COORDINATES_CONFIDENCE:
        critical("coordinates_confidence", "invalid_coordinates_confidence")
    if mapped.get("coordinates_source") and mapped.get("coordinates_source") not in ALLOWED_COORDINATES_SOURCES:
        critical("coordinates_source", "invalid_coordinates_source")
    if mapped.get("image_url") and not is_valid_url(mapped.get("image_url")):
        critical("image_url", "invalid_image_url")
    title_short = mapped.get("title_short")
    if title_short is not None and len(title_short) > 120:
        critical("title_short", "title_short_too_long")
    description = mapped.get("description")
    if description is not None and len(description) > 2000:
        critical("description", "description_too_long")
    layer_id = mapped.get("layer_id")
    if mapped.get("_invalid_layer_link"):
        critical("layer_id", "invalid_layer_link_format")
    elif not layer_id:
        critical("layer_id", "unknown_layer_link" if mapped.get("_unknown_layer_link") else "missing_layer_id")
    elif layer_id not in layer_ids:
        critical("layer_id", "unknown_layer_link")
    return valid


def validate_layer(layer: Dict[str, Any], warnings: List[Dict[str, Any]], errors: List[Dict[str, Any]]) -> bool:
    layer_id = layer.get("layer_id") or "<missing>"
    valid = True
    if not layer.get("layer_id"):
        add_issue(errors, "critical", layer_id, "missing layer_id", "layer_id")
        valid = False
    if not layer.get("name_ru"):
        add_issue(errors, "critical", layer_id, "missing layer name_ru", "name_ru")
        valid = False
    if not is_valid_color_hex(layer.get("color_hex")):
        add_issue(errors, "critical", layer_id, "invalid color_hex", "color_hex")
        valid = False
    if not isinstance(layer.get("is_enabled"), bool):
        add_issue(errors, "critical", layer_id, "is_enabled must be boolean", "is_enabled")
        valid = False
    return valid


def build_validation_report(
    total_records: int,
    valid_records: int,
    skipped_records: int,
    warnings: List[Dict[str, Any]],
    errors: List[Dict[str, Any]],
) -> Dict[str, Any]:
    status = "blocked" if errors else "ready_with_warnings" if warnings else "ready"
    return {
        "schema_version": 2,
        "status": status,
        "total_records": total_records,
        "valid_records": valid_records,
        "skipped_records": skipped_records,
        "blocking_errors_count": len(errors),
        "warnings_count": len(warnings),
        "blocking_errors": errors,
        # Compatibility aliases retained for existing diagnostics consumers.
        "errors_count": len(errors),
        "warnings": warnings,
        "errors": errors,
    }


def aggregate_issues(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    stats: Dict[str, int] = {}
    for issue in issues:
        reason = issue.get("reason") or issue.get("error") or issue.get("warning")
        if not reason:
            continue
        stats[reason] = stats.get(reason, 0) + 1
    return stats


def aggregate_warning_categories(warnings: List[Dict[str, Any]]) -> Dict[str, int]:
    categories = {"expected_fallback": 0, "data_quality": 0}
    for issue in warnings:
        reason = str(issue.get("reason") or "").strip()
        if reason.startswith("legacy_"):
            categories["expected_fallback"] += 1
        else:
            categories["data_quality"] += 1
    return categories


def write_json(path: Path, data: Any) -> None:
    """Безопасная сериализация JSON в файл."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


def maybe_commit(paths: List[Path], records_count: int) -> None:
    message = f"Export Airtable: {dt.date.today().isoformat()} {records_count} records"
    existing = [str(p) for p in paths if p.exists()]
    if not existing:
        return
    try:
        status = subprocess.run(
            ["git", "status", "--porcelain", "--", *existing],
            check=True,
            capture_output=True,
            text=True,
        )
        if not status.stdout.strip():
            print("Флаг --commit указан, но изменений в экспортных файлах нет — commit пропущен.")
            return
        subprocess.run(["git", "add", *existing], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        print(f"Создан git commit: {message}")
    except Exception as exc:  # noqa: BLE001
        print(f"Флаг --commit указан, но git commit не выполнен: {exc}", file=sys.stderr)


def run_self_test() -> int:
    errors: List[Dict[str, Any]] = []
    sample = {
        "id": "recSELFTEST",
        "fields": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "layer_id": "history",
            "layer_type_enum": "architecture",
            "name_ru": "Тест",
            "date_start": "-0753",
            "longitude_num": 37.6173,
            "latitude_num": 55.7558,
            "influence_radius_km": "12",
            "layer_color_hex": "#ABCDEF",
            "tags": "A, b ,C",
            "validated": True,
            "source_license_enum": "CC BY",
            "coordinates_confidence_enum": "exact",
            "source_url": "https://example.com/source",
            "coordinates_source": "Wikipedia",
        },
    }
    m = map_record(sample, errors, {"history": "history"})
    assert m["date_start"] == "-0753"
    assert m["tags"] == ["a", "b", "c"]
    assert m["validated"] is True
    assert m["influence_radius_km"] == 12
    assert m["longitude"] == 37.6173
    assert m["latitude"] == 55.7558
    assert normalize_hex_color(m["layer_color_hex"]) == "#abcdef"
    assert not any(e.get("error") for e in errors if "error" in e)
    assert is_valid_iso_date(m["date_start"])
    assert is_valid_license(m["source_license"])
    assert normalize_source_license("cc by-sa") == "CC BY-SA"
    assert normalize_source_license("unsupported-license") is None
    assert normalize_layer_type("Route Point") == "route_point"
    assert normalize_layer_type("unsupported-layer") is None
    assert normalize_coordinates_confidence("EXACT") == "exact"
    assert normalize_coordinates_confidence("approximate±3km") == "approximate"
    assert normalize_coordinates_confidence("unknown") == "conditional"
    m_limit_ok = dict(m)
    m_limit_ok["title_short"] = "t" * 120
    m_limit_ok["description"] = "d" * 2000
    assert validate_feature(m_limit_ok, {"history"}, [], [])
    m_limit_fail = dict(m)
    m_limit_fail["title_short"] = "t" * 121
    m_limit_fail["description"] = "d" * 2001
    limit_errors: List[Dict[str, Any]] = []
    assert not validate_feature(m_limit_fail, {"history"}, [], limit_errors)
    assert any(issue.get("reason") == "title_short_too_long" for issue in limit_errors)
    assert any(issue.get("reason") == "description_too_long" for issue in limit_errors)
    assert get_etl_error(
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "source_url": "https://example.com",
            "source_license": "CC BY",
            "latitude": 55.0,
            "longitude": 37.0,
            "layer_id": "history",
        }
    ) is None
    assert get_etl_error(
        {
            "id": "recLEGACY",
            "source_url": "https://example.com",
            "source_license": "CC BY",
            "latitude": 55.0,
            "longitude": 37.0,
            "layer_id": "history",
        }
    ) == "invalid_id_uuid_v4"
    assert is_uuid_v4("550e8400-e29b-41d4-a716-446655440000")
    assert not is_uuid_v4("recLEGACY")
    assert (
        get_etl_error(
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "source_url": "https://example.com",
                "source_license": "bad",
                "latitude": 55.0,
                "longitude": 37.0,
                "layer_id": "history",
            }
        )
        == "invalid_license"
    )
    assert get_etl_error({"id": "550e8400-e29b-41d4-a716-446655440000", "source_url": "javascript:alert(1)"}) == "invalid_source_url"
    assert (
        get_etl_error(
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "source_url": "https://example.com",
                "source_license": "CC BY",
                "latitude": None,
                "longitude": 37.0,
                "layer_id": "history",
            }
        )
        == "missing_geometry"
    )
    assert (
        get_etl_error(
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "source_url": "https://example.com",
                "source_license": "CC BY",
                "latitude": 95.0,
                "longitude": 37.0,
                "layer_id": "history",
            }
        )
        == "invalid_coordinates"
    )
    assert get_etl_error({"id": "550e8400-e29b-41d4-a716-446655440000", "source_url": "https://example.com", "source_license": "CC BY", "latitude": 55.0, "longitude": 37.0, "layer_id": None}) == "missing_layer_id"
    assert get_etl_error({"id": "550e8400-e29b-41d4-a716-446655440000", "source_url": "https://example.com", "source_license": "CC BY", "latitude": 55.0, "longitude": 37.0, "layer_id": "history", "_unknown_layer_link": True}) == "unknown_layer_link"
    assert get_etl_error({"id": "", "source_url": "https://example.com"}) == "missing_id"
    name_ru_fixture = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name_ru": "Корректное имя",
        "source_url": "https://example.com",
        "source_license": "CC BY",
        "latitude": 55.0,
        "longitude": 37.0,
        "layer_id": "history",
        "layer_type": "architecture",
        "_raw_date_start_present": True,
        "date_start": "2020",
    }
    assert get_etl_error(name_ru_fixture) is None
    assert get_etl_error({**name_ru_fixture, "image_url": ""}) is None
    assert get_etl_error({**name_ru_fixture, "image_url": "https://example.com/image.jpg"}) is None
    assert get_etl_error({**name_ru_fixture, "image_url": "javascript:alert(1)"}) == "invalid_image_url"
    assert get_etl_error({**name_ru_fixture, "layer_type": "bad_layer"}) == "invalid_layer_type"
    assert get_etl_error({**name_ru_fixture, "name_ru": "   "}) == "missing_name_ru"
    assert get_etl_error({**name_ru_fixture, "name_ru": None}) == "missing_name_ru"
    bad_start = map_record(
        {"id": "550e8400-e29b-41d4-a716-446655440001", "fields": {**sample["fields"], "date_start": "2024-13-01"}},
        [],
        {"history": "history"},
    )
    assert not validate_feature(bad_start, {"history"}, [], [])
    bad_end = map_record(
        {"id": "550e8400-e29b-41d4-a716-446655440002", "fields": {**sample["fields"], "date_end": "2024-99-01"}},
        [],
        {"history": "history"},
    )
    assert not validate_feature(bad_end, {"history"}, [], [])
    missing_start = map_record(
        {"id": "550e8400-e29b-41d4-a716-446655440003", "fields": {k: v for k, v in sample["fields"].items() if k != "date_start"}},
        [],
        {"history": "history"},
    )
    missing_start_errors: List[Dict[str, Any]] = []
    assert not validate_feature(missing_start, {"history"}, [], missing_start_errors)
    start_reasons = [issue.get("reason") for issue in missing_start_errors if issue.get("field") == "date_start"]
    assert start_reasons.count("missing_date_start") == 1
    assert "invalid_date_start" not in start_reasons
    assert get_etl_error(missing_start) == "missing_date_start"

    no_end = map_record(
        {"id": "550e8400-e29b-41d4-a716-446655440004", "fields": {**sample["fields"], "date_end": ""}},
        [],
        {"history": "history"},
    )
    assert validate_feature(no_end, {"history"}, [], [])
    assert get_etl_error(no_end) is None
    assert get_etl_error(bad_start) == "invalid_date_start"
    assert get_etl_error(bad_end) == "invalid_date_end"
    print("Self-test OK")
    return 0


def sort_mapped_records(mapped_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Детерминированная сортировка для стабильных diff/commit."""
    def key(item: Dict[str, Any]) -> Tuple[Any, ...]:
        layer = item.get("layer_id")
        date_start = item.get("date_start")
        return (
            layer is None,
            layer or "",
            date_start is None,
            date_start or "",
            item.get("id") or "",
        )

    return sorted(mapped_records, key=key)
    
def main() -> int:
    started_at = time.time()
    args = parse_args()

    if args.self_test:
        return run_self_test()

    token = os.getenv("AIRTABLE_TOKEN")
    base = args.base or os.getenv("AIRTABLE_BASE")
    table = args.table or os.getenv("AIRTABLE_TABLE")

    dry_run = bool(args.dry_run)
    if not dry_run and (not token or not base or not table):
        dry_run = True
        print("Не заданы AIRTABLE_TOKEN/AIRTABLE_BASE/AIRTABLE_TABLE — включён dry-run.")

    if not dry_run and not REQUESTS_AVAILABLE:
        print("Не найден модуль 'requests'. Установите его: pip install requests", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    # В dry-run пишем в _test_* файлы, чтобы не затирать рабочие данные.
    prefix = "_test_" if dry_run else ""
    raw_path = out_dir / f"{prefix}features.json"
    geojson_path = out_dir / f"{prefix}features.geojson"
    id_aliases_path = out_dir / f"{prefix}id_aliases.json"
    id_aliases_seed_path = out_dir / "id_aliases.json"
    rejected_path = out_dir / f"{prefix}rejected.json"
    layers_path = out_dir / f"{prefix}layers.json"
    sources_path = out_dir / f"{prefix}sources.json"
    media_path = out_dir / f"{prefix}media.json"
    relations_path = out_dir / f"{prefix}relations.json"
    validation_report_path = out_dir / f"{prefix}validation_report.json"
    export_meta_path = out_dir / f"{prefix}export_meta.json"
    error_log_path = out_dir / f"{prefix}export_errors.log"

    records: List[Dict[str, Any]]
    layer_records: List[Dict[str, Any]]
    source_records: List[Dict[str, Any]]
    media_records: List[Dict[str, Any]]
    feature_source_records: List[Dict[str, Any]]
    feature_media_records: List[Dict[str, Any]]
    relation_records: List[Dict[str, Any]]
    relation_source_records: List[Dict[str, Any]]
    try:
        if dry_run:
            records = generate_mock_records()
            layer_records = generate_mock_layers_records()
            source_records = generate_mock_sources_records()
            media_records = generate_mock_media_records()
            feature_source_records = generate_mock_feature_sources_records()
            feature_media_records = generate_mock_feature_media_records()
            relation_records = generate_mock_relations_records()
            relation_source_records = generate_mock_relation_sources_records()
            if args.max_records is not None:
                records = records[: args.max_records]
            print("Dry-run: mock data generated")
        else:
            assert token is not None and base is not None and table is not None
            records = fetch_airtable_records(token, base, table, args.max_records)
            layer_records = fetch_airtable_records(token, base, LAYERS_TABLE_NAME, None)
            source_records = fetch_airtable_records(token, base, SOURCES_TABLE_NAME, None)
            media_records = fetch_airtable_records(token, base, MEDIA_TABLE_NAME, None)
            feature_source_records = fetch_airtable_records(token, base, FEATURE_SOURCES_TABLE_NAME, None)
            feature_media_records = fetch_airtable_records(token, base, FEATURE_MEDIA_TABLE_NAME, None)
            relation_records = fetch_airtable_records(token, base, RELATIONS_TABLE_NAME, None)
            relation_source_records = fetch_airtable_records(token, base, RELATION_SOURCES_TABLE_NAME, None)
    except PermissionError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"Критическая ошибка: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Непредвиденная ошибка: {exc}", file=sys.stderr)
        return 1

    print(f"Загружено Features: {len(records)}")
    print(f"Загружено Layers: {len(layer_records)}")
    print(f"Загружено Sources: {len(source_records)}")
    print(f"Загружено Media: {len(media_records)}")
    print(f"Загружено FeatureSources: {len(feature_source_records)}")
    print(f"Загружено FeatureMedia: {len(feature_media_records)}")
    print(f"Загружено Relations: {len(relation_records)}")
    print(f"Загружено RelationSources: {len(relation_source_records)}")

    warnings: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    candidate_records: List[Dict[str, Any]] = []

    linked_layer_to_public_id, layers = map_layers(layer_records)
    for record in records:
        mapped = map_record(record, warnings, linked_layer_to_public_id)
        candidate_records.append(mapped)

    _, reviewed_sources = map_sources(source_records, warnings, errors)
    _, reviewed_media = map_media(media_records, warnings, errors)
    feature_id_by_record_id = {
        safe_str(mapped.get("source_record_id")): safe_str(mapped.get("id"))
        for mapped in candidate_records
        if safe_str(mapped.get("source_record_id")) and safe_str(mapped.get("id"))
    }
    source_by_record_id = {item["source_record_id"]: item for item in reviewed_sources}
    media_by_record_id = {item["source_record_id"]: item for item in reviewed_media}
    source_refs_by_feature = map_feature_source_refs(
        feature_source_records,
        feature_id_by_record_id,
        source_by_record_id,
        errors,
    )
    media_refs_by_feature = map_feature_media_refs(
        feature_media_records,
        feature_id_by_record_id,
        media_by_record_id,
        errors,
    )
    attach_source_media_refs(
        candidate_records,
        source_refs_by_feature,
        {item["id"]: item for item in reviewed_sources},
        media_refs_by_feature,
        {item["id"]: item for item in reviewed_media},
        warnings,
    )

    validated_layers = [layer for layer in layers if validate_layer(layer, warnings, errors)]
    enabled_layer_ids = {
        layer["layer_id"]
        for layer in validated_layers
        if layer.get("is_enabled") is True
    }

    valid_features: List[Dict[str, Any]] = []
    rejected_features: List[Dict[str, Any]] = []
    seen_dedupe_keys: set[Tuple[Any, ...]] = set()
    for mapped in candidate_records:
        mapped["etl_status"] = "pending"
        mapped["etl_error"] = None

        if not args.include_inactive and mapped.get("is_active") is False:
            mapped["etl_status"] = "rejected"
            mapped["etl_error"] = "inactive"
            rejected_features.append(
                {
                    "id": mapped.get("id") or "<missing>",
                    "source_record_id": mapped.get("source_record_id"),
                    "name_ru": mapped.get("name_ru"),
                    "reasons": ["inactive"],
                }
            )
            continue

        if parse_bool(mapped.get("validated")) is not True:
            mapped["etl_status"] = "rejected"
            mapped["etl_error"] = "unreviewed_active_feature"
            add_issue(
                errors,
                "critical",
                get_diagnostic_record_id(mapped),
                "unreviewed_active_feature",
                "validated",
            )
            rejected_features.append(
                {
                    "id": mapped.get("id") or "<missing>",
                    "source_record_id": mapped.get("source_record_id"),
                    "name_ru": mapped.get("name_ru"),
                    "reasons": ["unreviewed_active_feature"],
                }
            )
            continue

        record_errors_start = len(errors)
        feature_valid = validate_feature(mapped, enabled_layer_ids, warnings, errors)
        if not feature_valid:
            diagnostic_record_id = get_diagnostic_record_id(mapped)
            critical_reasons = [
                issue.get("reason")
                for issue in errors[record_errors_start:]
                if issue.get("severity") == "critical" and issue.get("id") == diagnostic_record_id
            ]
            if not critical_reasons:
                critical_reasons = ["validation_failed"]
            mapped["etl_status"] = "rejected"
            mapped["etl_error"] = critical_reasons[0]
            rejected_features.append(
                {
                    "id": mapped.get("id") or "<missing>",
                    "source_record_id": mapped.get("source_record_id"),
                    "name_ru": mapped.get("name_ru"),
                    "reasons": critical_reasons,
                }
            )
            continue

        etl_error = get_etl_error(mapped)
        if etl_error is not None:
            mapped["etl_status"] = "rejected"
            mapped["etl_error"] = etl_error
            rejected_features.append(
                {
                    "id": mapped.get("id") or "<missing>",
                    "source_record_id": mapped.get("source_record_id"),
                    "name_ru": mapped.get("name_ru"),
                    "reasons": [etl_error],
                }
            )
            continue

        longitude = mapped.get("longitude")
        latitude = mapped.get("latitude")
        if longitude is None or latitude is None:
            mapped["etl_status"] = "rejected"
            mapped["etl_error"] = "missing_geometry"
            rejected_features.append(
                {
                    "id": mapped.get("id") or "<missing>",
                    "source_record_id": mapped.get("source_record_id"),
                    "name_ru": mapped.get("name_ru"),
                    "reasons": ["missing_geometry"],
                }
            )
            continue

        dedupe_key = get_dedupe_key(mapped)
        if dedupe_key in seen_dedupe_keys:
            mapped["etl_status"] = "rejected"
            mapped["etl_error"] = "duplicate"
            rejected_features.append(
                {
                    "id": mapped.get("id") or "<missing>",
                    "source_record_id": mapped.get("source_record_id"),
                    "name_ru": mapped.get("name_ru"),
                    "reasons": ["duplicate"],
                }
            )
            continue
        seen_dedupe_keys.add(dedupe_key)
        mapped["etl_status"] = "ok"
        mapped["etl_error"] = None
        valid_features.append(mapped)

    valid_features = sort_mapped_records(valid_features)

    valid_feature_id_by_record_id = {
        safe_str(mapped.get("source_record_id")): safe_str(mapped.get("id"))
        for mapped in valid_features
        if safe_str(mapped.get("source_record_id")) and safe_str(mapped.get("id"))
    }
    relation_by_record_id, reviewed_relation_candidates = map_relations(
        relation_records,
        valid_feature_id_by_record_id,
        errors,
    )
    relation_source_refs = map_relation_source_refs(
        relation_source_records,
        relation_by_record_id,
        source_by_record_id,
        errors,
    )
    reviewed_relations = finalize_relations(reviewed_relation_candidates, relation_source_refs, errors)
    attach_relation_ids(valid_features, reviewed_relations)

    published_layers, layer_warnings = select_publishable_layers(validated_layers, valid_features)
    warnings.extend(layer_warnings)
    warnings.extend(collect_semantic_quality_warnings(valid_features))

    try:
        existing_id_aliases = load_id_aliases(id_aliases_seed_path)
        id_aliases = build_id_aliases(valid_features, existing_id_aliases)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Критическая ошибка id alias map: {exc}", file=sys.stderr)
        return 1

    geojson = build_geojson_features(valid_features, warnings, errors, id_aliases["aliases"])
    total_records = len(records)
    exported_records = len(valid_features)
    geojson_records = len(geojson["features"])
    rejected_records = len(rejected_features)

    validation_report = build_validation_report(
        total_records=total_records,
        valid_records=exported_records,
        skipped_records=rejected_records,
        warnings=warnings,
        errors=errors,
    )
    error_stats = aggregate_issues(errors)
    warning_stats = aggregate_issues(warnings)
    warning_categories = aggregate_warning_categories(warnings)
    semantic_status = "blocked" if errors else "ready_with_warnings" if warnings else "ready"

    export_meta = {
        "timestamp": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": "dry-run" if dry_run else "airtable",
        "records_total_source": total_records,
        "records_exported": exported_records,
        "records_geojson": geojson_records,
        "records_rejected": rejected_records,
        "layers_total_source": len(layer_records),
        "layers_published": len(published_layers),
        "enabled_empty_layers_excluded": warning_stats.get("enabled_empty_layer_excluded", 0),
        "sources_total_source": len(source_records),
        "sources_reviewed": len(reviewed_sources),
        "media_total_source": len(media_records),
        "media_reviewed": len(reviewed_media),
        "feature_source_links_total": len(feature_source_records),
        "feature_media_links_total": len(feature_media_records),
        "relations_total_source": len(relation_records),
        "relations_reviewed": len(reviewed_relations),
        "relation_source_links_total": len(relation_source_records),
        "errors": len(errors),
        "warnings": len(warnings),
        "error_stats": error_stats,
        "warning_stats": warning_stats,
        "warning_categories": warning_categories,
        "semantic_gate": {
            "status": semantic_status,
            "blocking_errors": len(errors),
            "warnings": len(warnings),
        },
        "duration_seconds": round(time.time() - started_at, 3),
    }

    try:
        write_json(raw_path, records)
        write_json(geojson_path, geojson)
        write_json(id_aliases_path, id_aliases)
        write_json(rejected_path, rejected_features)
        write_json(layers_path, published_layers)
        write_json(sources_path, reviewed_sources)
        write_json(media_path, reviewed_media)
        write_json(relations_path, reviewed_relations)
        write_json(validation_report_path, validation_report)
        write_json(export_meta_path, export_meta)

        # Перезаписываем лог ошибок на каждый запуск
        if error_log_path.exists():
            error_log_path.unlink()
        error_log_path.parent.mkdir(parents=True, exist_ok=True)
        error_log_path.touch()
        for err in [*warnings, *errors]:
            log_error(error_log_path, err)
    except Exception as exc:  # noqa: BLE001
        print(f"Критическая ошибка сериализации/записи: {exc}", file=sys.stderr)
        return 1

    # Финальный вывод — в формате, согласованном с мастер-промптом
    print(f"OK: {len(valid_features)} | Errors: {len(errors)} | Rejected: {len(rejected_features)}")
    print(f"LAYERS: {len(published_layers)}")
    if rejected_features:
        preview = rejected_features[:3]
        print(f"REJECT_PREVIEW: {json.dumps(preview, ensure_ascii=False)}")
    if len(valid_features) == 0:
        print("WARNING: valid features = 0")

    if args.commit:
        maybe_commit(
            [
                raw_path,
                geojson_path,
                id_aliases_path,
                rejected_path,
                layers_path,
                sources_path,
                media_path,
                relations_path,
                validation_report_path,
                export_meta_path,
                error_log_path,
            ],
            len(valid_features),
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())

# --- Пример запуска ---
# AIRTABLE_TOKEN=pat_xxx AIRTABLE_BASE=appHmf8ubeUF9 AIRTABLE_TABLE=Features python3 scripts/export_airtable.py
# python3 scripts/export_airtable.py --dry-run --out-dir data --max-records 20
#
# --- Чеклист после запуска ---
# 1) Созданы data/features.json, data/features.geojson, data/layers.json, data/export_meta.json (или data/_test_* в dry-run).
# 2) В data/*export_errors.log есть JSON Lines с ключами record_id/field/error/value.
# 3) features.geojson имеет influence_radius_km и has_geometry в properties.
# 4) В выводе есть строка: Успешно: N | Ошибок: M | Source total: T.
#
# --- Как тестировать ---
# 1) Dry-run:
#    python scripts/export_airtable.py --dry-run --out-dir data --max-records 5
#    Проверить: data/_test_features.geojson, data/_test_export_meta.json, data/_test_export_errors.log
# 2) С реальным Airtable (если есть env):
#    AIRTABLE_TOKEN=... AIRTABLE_BASE=... python scripts/export_airtable.py --out-dir data --max-records 50
#    Проверить: data/features.geojson, data/export_meta.json и вывод "Успешно: ..."
# 3) Проверить, что features.geojson.features[*].properties содержит поля:
#    - influence_radius_km
#    - has_geometry
# 4) Проверить флаг --include-inactive:
#    а) по умолчанию: записи с is_active=False пропускаются
#    б) с --include-inactive: экспортируются все записи
