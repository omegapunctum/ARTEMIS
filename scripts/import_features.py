#!/usr/bin/env python3
"""Import architectural objects from CSV into Airtable table `Features`.

Usage:
    python scripts/import_features.py gothic.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
from typing import Any

import requests

# Airtable configuration (base and table are fixed by project requirements).
BASE_ID = "appHmf8ubeUF9nfkO"
TABLE_NAME = "Features"
API_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

# Strict schema expected in input CSV.
EXPECTED_FIELDS = [
    "id",
    "layer_id",
    "layer_type",
    "name_ru",
    "name_en",
    "date_start",
    "date_end",
    "longitude",
    "latitude",
    "coordinates_confidence",
    "coordinates_source",
    "influence_radius_km",
    "sequence_order",
    "title_short",
    "description",
    "image_url",
    "source_url",
    "source_license",
    "tags",
    "is_active",
]

LICENSE_VALUES = {"CC0", "CC BY", "CC BY-SA", "PD"}
DATE_PATTERN = re.compile(r"^(\d{4}|\d{4}-\d{2}-\d{2})$")


class ValidationError(Exception):
    """Raised when a CSV row fails validation."""


def _is_empty(value: Any) -> bool:
    """Return True if a CSV value should be treated as null/empty."""
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    return value.strip().lower() in {"", "null"}


def _to_number_or_none(value: str, field_name: str) -> float | None:
    """Convert text to float or return None for null-like values."""
    if _is_empty(value):
        return None

    try:
        return float(value)
    except ValueError as exc:
        raise ValidationError(f"{field_name} должно быть числом") from exc


def _validate_date(value: str, field_name: str) -> str | None:
    """Validate date format (YYYY or YYYY-MM-DD)."""
    if _is_empty(value):
        return None

    normalized = value.strip()
    if not DATE_PATTERN.fullmatch(normalized):
        raise ValidationError(f"{field_name} должно быть в формате YYYY или YYYY-MM-DD")
    return normalized


def _normalize_text(value: str) -> str | None:
    """Normalize plain text value, preserving content and mapping null-like values to None."""
    if _is_empty(value):
        return None
    return value.strip()


def validate_row(row: dict[str, str], row_num: int) -> dict[str, Any]:
    """Validate one CSV row and convert it to Airtable fields payload."""
    fields: dict[str, Any] = {}

    # Ensure all expected keys are present in this row.
    missing_keys = [key for key in EXPECTED_FIELDS if key not in row]
    if missing_keys:
        raise ValidationError(f"отсутствуют поля: {', '.join(missing_keys)}")

    # Basic normalization for all fields.
    for key in EXPECTED_FIELDS:
        fields[key] = _normalize_text(row.get(key, ""))

    # name_ru is used in logs and should exist.
    if not fields["name_ru"]:
        raise ValidationError("name_ru обязательно")

    # Validate date formats.
    fields["date_start"] = _validate_date(row.get("date_start", ""), "date_start")
    fields["date_end"] = _validate_date(row.get("date_end", ""), "date_end")

    # Validate allowed licenses.
    license_value = fields["source_license"]
    if license_value is not None and license_value not in LICENSE_VALUES:
        raise ValidationError(
            "source_license должно быть одним из: " + ", ".join(sorted(LICENSE_VALUES))
        )

    # Validate coordinates. Unknown coordinates must be null for both longitude and latitude.
    lon = _to_number_or_none(row.get("longitude", ""), "longitude")
    lat = _to_number_or_none(row.get("latitude", ""), "latitude")

    if (lon is None) != (lat is None):
        raise ValidationError("если координаты неизвестны, longitude и latitude должны быть null")

    if lon is not None and not (-180 <= lon <= 180):
        raise ValidationError("longitude должно быть в диапазоне [-180, 180]")

    if lat is not None and not (-90 <= lat <= 90):
        raise ValidationError("latitude должно быть в диапазоне [-90, 90]")

    fields["longitude"] = lon
    fields["latitude"] = lat

    # Numeric optional fields.
    influence_radius = _to_number_or_none(row.get("influence_radius_km", ""), "influence_radius_km")
    sequence_order_raw = row.get("sequence_order", "")

    fields["influence_radius_km"] = influence_radius
    if _is_empty(sequence_order_raw):
        fields["sequence_order"] = None
    else:
        try:
            fields["sequence_order"] = int(sequence_order_raw)
        except ValueError as exc:
            raise ValidationError("sequence_order должно быть целым числом") from exc

    # Log-friendly row position (available for future extensions/debugging).
    fields["_row_num"] = row_num
    return fields


def load_csv(path: str) -> list[dict[str, str]]:
    """Load and validate CSV file structure (UTF-8, comma delimiter, expected columns)."""
    with open(path, "r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")

        if reader.fieldnames is None:
            raise ValidationError("CSV не содержит заголовок")

        actual_fields = reader.fieldnames
        if actual_fields != EXPECTED_FIELDS:
            raise ValidationError(
                "поля CSV должны точно соответствовать схеме Airtable. "
                f"Ожидалось: {EXPECTED_FIELDS}. Получено: {actual_fields}"
            )

        return list(reader)


def send_to_airtable(token: str, fields: dict[str, Any]) -> None:
    """Send one record to Airtable API and raise on any API/network error."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Remove internal helper keys from payload.
    payload_fields = {k: v for k, v in fields.items() if not k.startswith("_")}

    response = requests.post(
        API_URL,
        headers=headers,
        json={"fields": payload_fields},
        timeout=30,
    )

    if response.status_code >= 400:
        detail = response.text.strip()
        raise RuntimeError(f"Airtable API вернул {response.status_code}: {detail}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Импорт объектов архитектуры из CSV в Airtable таблицу Features"
    )
    parser.add_argument("csv_file", help="Путь к CSV файлу (UTF-8, разделитель запятая)")
    return parser.parse_args()


def main() -> int:
    """Main workflow: load CSV, validate rows, upload with per-record error handling."""
    args = parse_args()

    token = os.getenv("AIRTABLE_TOKEN")
    if not token:
        print("Ошибка: AIRTABLE_TOKEN не задан в переменных окружения")
        return 1

    try:
        rows = load_csv(args.csv_file)
    except (OSError, ValidationError) as exc:
        print(f"Ошибка загрузки CSV: {exc}")
        return 1

    success_count = 0
    error_count = 0

    for index, row in enumerate(rows, start=2):  # row 1 is header
        name_ru = (row.get("name_ru") or "").strip() or "<без названия>"
        try:
            validated_fields = validate_row(row, row_num=index)
            send_to_airtable(token, validated_fields)
            success_count += 1
            print(f"Загружено: {name_ru}")
        except Exception as exc:  # noqa: BLE001 (intentional per-record protection)
            error_count += 1
            print(f"Ошибка: {name_ru} — {exc}")

        # Airtable rate-limit friendly pause.
        time.sleep(0.2)

    print(f"Успешно: {success_count} | Ошибок: {error_count}")
    return 0 if error_count == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
