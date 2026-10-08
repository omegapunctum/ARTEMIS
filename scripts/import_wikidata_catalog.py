#!/usr/bin/env python3
"""Bounded Wikimedia capture and offline, source-relative reference normalization."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "fixtures/source_catalog/london_architecture/v1"
DEFAULT_SOURCE_DIR = SOURCE_DIR
CATALOG_PATH = SOURCE_DIR / "catalog.json"
COHORT = ("Q83125", "Q62378", "Q5933", "Q62408", "Q173882", "Q42182", "Q642039", "Q205666", "Q207385", "Q607700")
EXCLUDED_QID = "Q193639"
MAX_BYTES = 16 * 1024 * 1024
USER_AGENT = "ARTEMIS-reference-catalog/1.0 (https://github.com/omegapunctum/ARTEMIS)"
LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"


class CatalogError(ValueError):
    """An integrity or bounded intake rule was violated."""


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CatalogError("Duplicate JSON key")
        result[key] = value
    return result


def _json(raw: bytes):
    if len(raw) > MAX_BYTES:
        raise CatalogError("Source exceeds bounded input size")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(CatalogError("Nonfinite JSON number")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError("Invalid source JSON") from exc


def _read(path: Path):
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    return _json(raw), raw


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _coordinate(entity: dict) -> dict:
    statements = entity.get("claims", {}).get("P625", [])
    candidates = [statement for statement in statements if statement.get("rank") != "deprecated"]
    if len(candidates) != 1:
        raise CatalogError("P625 missing or ambiguous")
    statement = candidates[0]
    snak = statement.get("mainsnak", {})
    if (statement.get("type") != "statement" or statement.get("rank") not in {"normal", "preferred"}
            or statement.get("qualifiers") or statement.get("qualifiers-order")
            or snak.get("snaktype") != "value" or snak.get("property") != "P625"
            or snak.get("datatype") != "globe-coordinate"
            or snak.get("datavalue", {}).get("type") != "globecoordinate"):
        raise CatalogError("P625 qualified or malformed")
    value = snak["datavalue"].get("value", {})
    if value.get("globe") != "http://www.wikidata.org/entity/Q2":
        raise CatalogError("P625 must use Earth")
    lat, lon = value.get("latitude"), value.get("longitude")
    if not _number(lat) or not _number(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise CatalogError("P625 outside finite WGS84 bounds")
    precision = value.get("precision")
    if precision is not None and (not _number(precision) or precision <= 0):
        raise CatalogError("P625 provider precision is invalid")
    if not isinstance(statement.get("id"), str) or statement["id"].split("$", 1)[0].upper() != entity["id"]:
        raise CatalogError("Coordinate statement identity mismatch")
    return statement


def _language_map(entity: dict, field: str):
    result = {}
    source = entity.get(field, {})
    if not isinstance(source, dict):
        raise CatalogError("Invalid multilingual source")
    for language, row in source.items():
        rows = row if field == "aliases" else [row]
        if not isinstance(language, str) or not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", language) or not isinstance(rows, list):
            raise CatalogError("Invalid language tag")
        for entry in rows:
            if not isinstance(entry, dict) or entry.get("language") != language or not isinstance(entry.get("value"), str) or not entry["value"].strip():
                raise CatalogError("Label language identity mismatch")
        result[language] = [entry["value"] for entry in rows] if field == "aliases" else rows[0]["value"]
    return result


def _normalized(text: str) -> str:
    return " ".join("".join(character if character.isalnum() else " " for character in unicodedata.normalize("NFKC", text).casefold()).split())


def _duplicate_guard(entities: list[dict], legacy: list[dict]) -> None:
    known_ids, names, titles = set(), set(), set()
    for row in legacy:
        fields = row.get("fields", {})
        for key, value in fields.items():
            if isinstance(value, str):
                known_ids.update(re.findall(r"\bQ[1-9][0-9]*\b", value))
                if key in {"name_en", "name_ru", "name", "title"}:
                    names.add(_normalized(value))
                if "url" in key and "wikipedia.org/wiki/" in value:
                    titles.add(_normalized(urllib.parse.unquote(value.split("/wiki/", 1)[1])))
    seen_ids = set()
    for entity in entities:
        qid = entity["id"]
        if qid in seen_ids or qid in known_ids:
            raise CatalogError("Duplicate external identity")
        seen_ids.add(qid)
        labels = _language_map(entity, "labels")
        aliases = _language_map(entity, "aliases")
        candidates = {_normalized(value) for value in labels.values()}
        candidates.update(_normalized(value) for values in aliases.values() for value in values)
        candidate_titles = {_normalized(row["title"]) for key, row in entity.get("sitelinks", {}).items() if key.endswith("wiki") and isinstance(row, dict) and isinstance(row.get("title"), str)}
        if names & candidates or titles & candidate_titles:
            raise CatalogError("Potential legacy duplicate requires review")


def source_input_paths(source_dir: Path = SOURCE_DIR) -> list[Path]:
    return [source_dir / "selection.json", source_dir / "manifest.json",
            *[source_dir / "snapshots" / f"{qid}.json" for qid in (*COHORT, EXCLUDED_QID)],
            source_dir / "catalog.json"]


def _derive(source_dir: Path, legacy_path: Path) -> dict:
    selection, selection_raw = _read(source_dir / "selection.json")
    manifest, _ = _read(source_dir / "manifest.json")
    legacy, legacy_raw = _read(legacy_path)
    if selection != {"schema_version": "wikidata-catalog-selection-v1", "qids": list(COHORT), "excluded_qids": [EXCLUDED_QID]}:
        raise CatalogError("Bounded cohort drift")
    if (manifest.get("schema_version") != "wikidata-catalog-capture-v1"
            or manifest.get("selection_sha256") != digest(selection_raw)
            or manifest.get("legacy_features_sha256") != digest(legacy_raw)
            or manifest.get("legacy_features_count") != len(legacy)
            or len(legacy) != 31):
        raise CatalogError("Manifest or legacy guard mismatch")
    entries = manifest.get("captures", [])
    if len(entries) != 11 or [row.get("qid") for row in entries] != [*COHORT, EXCLUDED_QID]:
        raise CatalogError("Capture cohort mismatch")
    entities, captures = [], {}
    for entry in entries:
        qid = entry["qid"]
        expected_path = f"snapshots/{qid}.json"
        if entry.get("path") != expected_path:
            raise CatalogError("Capture path mismatch")
        payload, raw = _read(source_dir / expected_path)
        if payload.get("error") or set(payload.get("entities", {})) != {qid}:
            raise CatalogError("Provider error or entity envelope mismatch")
        entity = payload["entities"][qid]
        revision = entity.get("lastrevid")
        if (entity.get("id") != qid or entity.get("type") != "item" or isinstance(revision, bool)
                or not isinstance(revision, int) or revision <= 0 or entry.get("revision") != revision
                or entry.get("original_json_sha256") != digest(raw)
                or entry.get("byte_count") != len(raw) or entry.get("modified") != entity.get("modified")
                or entry.get("request_url") != f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
                or entry.get("revision_json_url") != f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json?revision={revision}"
                or entry.get("revision_url") != f"https://www.wikidata.org/w/index.php?title={qid}&oldid={revision}"):
            raise CatalogError("Capture provenance mismatch")
        try:
            stamp = datetime.fromisoformat(entry["retrieved_at"].replace("Z", "+00:00"))
            if stamp.utcoffset().total_seconds() != 0:
                raise ValueError()
        except (KeyError, ValueError, AttributeError, TypeError) as exc:
            raise CatalogError("Invalid retrieval UTC") from exc
        _language_map(entity, "labels")
        _language_map(entity, "aliases")
        captures[qid] = (entity, entry)
        if qid != EXCLUDED_QID:
            entities.append(entity)
    _duplicate_guard(entities, legacy)
    excluded_entity, excluded_capture = captures[EXCLUDED_QID]
    try:
        _coordinate(excluded_entity)
    except CatalogError as exc:
        if str(exc) != "P625 provider precision is invalid":
            raise CatalogError("Excluded source reason drift") from exc
    else:
        raise CatalogError("Excluded source reason drift")
    excluded = [{"qid": EXCLUDED_QID, "reason": "invalid_provider_coordinate_precision",
                 "revision": excluded_capture["revision"], "original_json_sha256": excluded_capture["original_json_sha256"],
                 "coordinate_statements": excluded_entity["claims"]["P625"]}]
    references = []
    for entity in entities:
        qid = entity["id"]
        capture = captures[qid][1]
        labels, aliases = _language_map(entity, "labels"), _language_map(entity, "aliases")
        if not labels:
            raise CatalogError("No source label")
        statement = _coordinate(entity)
        value = statement["mainsnak"]["datavalue"]["value"]
        item_id = f"catalog:wikidata:{qid}"
        source_id, claim_id = f"source:wikidata:{qid}:{capture['revision']}", f"claim:wikidata:{qid}:coordinate"
        locator = f"claims.P625; statement {statement['id']}"
        source = {"id": source_id, "title": f"Wikidata {qid} · revision {capture['revision']}",
                  "url": capture["revision_url"], "license": "CC0-1.0", "license_url": LICENSE_URL,
                  "revision": capture["revision"], "original_json_sha256": capture["original_json_sha256"],
                  "retrieved_at": capture["retrieved_at"], "revision_json_url": capture["revision_json_url"],
                  "source_type": "structured_reference", "review_state": "draft", "provider": "wikidata"}
        claim = {"id": claim_id, "subject_ref": item_id,
                 "statement": f"Wikidata {qid} revision {capture['revision']} reports P625 longitude {value['longitude']} and latitude {value['latitude']}.",
                 "claim_kind": "factual", "origin": "imported", "review_state": "draft", "confidence": "unknown",
                 "confidence_basis": "Not assessed; deterministic extraction is not independent evidence review.",
                 "evidence_state": "missing", "source_refs": [source_id], "native_statement_id": statement["id"]}
        evidence = {"id": f"evidence:wikidata:{qid}:coordinate", "claim_id": claim_id, "source_id": source_id,
                    "locator": locator, "relation_to_claim": "supports", "evidence_strength": "direct", "reviewer": None,
                    "review_state": "draft", "scope": "The pinned Wikidata revision reports this coordinate; underlying reference reliability is not reviewed."}
        wiki_urls = {}
        for site, link in entity.get("sitelinks", {}).items():
            if site.endswith("wiki") and site not in {"commonswiki", "specieswiki", "wikidatawiki", "metawiki", "mediawikiwiki", "foundationwiki", "incubatorwiki", "outreachwiki", "sourceswiki", "testwiki", "test2wiki"}:
                language = site[:-4].replace("_", "-")
                url = link.get("url")
                if isinstance(url, str) and urllib.parse.urlparse(url).hostname and urllib.parse.urlparse(url).hostname.endswith(".wikipedia.org"):
                    wiki_urls[language] = url
        native_dates = {prop: statements for prop, statements in entity.get("claims", {}).items()
                        if any(statement.get("mainsnak", {}).get("datatype") == "time" for statement in statements)}
        references.append({"item_id": item_id, "qid": qid, "layer_id": "catalog", "kind": "catalog_reference",
                           "label": labels.get("en", labels[sorted(labels)[0]]), "labels": labels, "aliases": aliases,
                           "geometry": {"type": "Point", "coordinates": [value["longitude"], value["latitude"]]},
                           "temporal_extent": None, "historical_position": None, "historical_applicability": "unknown",
                           "spatial_precision": "unknown_precision", "coordinate_statement": statement, "sources": [source],
                           "wikipedia_urls": wiki_urls, "claims": [claim], "evidence_links": [evidence],
                           "uncertainties": [{"kind": "location", "statement": "Provider numeric precision is retained literally; measurement accuracy, reference-point meaning and site extent are unverified."},
                                             {"kind": "scope_limitation", "statement": "Modern reference context only; historical position, existence period and applicability are unknown."},
                                             {"kind": "missing_evidence", "statement": "Underlying Wikidata statement references are retained, not independently reviewed."}],
                           "native_dates": native_dates})
    catalog = {"schema_version": "wikidata-reference-catalog-v1", "catalog_id": "london-architecture-wikidata-v1",
               "region": {"en": "London", "ru": "Лондон"}, "role": "atemporal_reference_context",
               "historical_applicability": "unknown", "time_filtering": "excluded", "references": references,
               "excluded": excluded, "selection_sha256": digest(selection_raw), "legacy_features_sha256": digest(legacy_raw)}
    catalog["content_sha256"] = digest(canonical_bytes(catalog))
    return catalog


def build_catalog(source_dir: Path = DEFAULT_SOURCE_DIR, legacy_path: Path = ROOT / "data/features.json") -> dict:
    """Offline rebuild, rejecting any difference from the immutable normalized package."""
    catalog = _derive(Path(source_dir), Path(legacy_path))
    stored, raw = _read(Path(source_dir) / "catalog.json")
    if stored != catalog or raw != canonical_bytes(catalog):
        raise CatalogError("Stored catalog drift")
    return catalog


def _fetch(qid: str) -> tuple[bytes, str]:
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json", "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(request, timeout=30) as response:
                if urllib.parse.urlparse(response.url).hostname != "www.wikidata.org":
                    raise CatalogError("Unexpected provider redirect")
                raw = response.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise CatalogError("Provider response too large")
                if response.headers.get("Content-Encoding") == "gzip":
                    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as compressed:
                        raw = compressed.read(MAX_BYTES + 1)
                _json(raw)
                return raw, url
        except urllib.error.HTTPError as exc:
            if exc.code not in {429, 503} or attempt == 2:
                raise CatalogError(f"Provider HTTP failure {exc.code}") from exc
            retry = exc.headers.get("Retry-After", "")
            delay = int(retry) if retry.isdigit() else 2 ** (attempt + 1)
            if delay > 60:
                raise CatalogError("Provider backoff exceeds bounded operation; retry later") from exc
            time.sleep(max(1, delay))
    raise CatalogError("Capture failed")


def capture(output: Path, legacy_path: Path = ROOT / "data/features.json") -> dict:
    """Explicit operator action; a fresh directory is required, existing bytes never overwritten."""
    output.mkdir(parents=True, exist_ok=False)
    (output / "snapshots").mkdir()
    selection = {"schema_version": "wikidata-catalog-selection-v1", "qids": list(COHORT), "excluded_qids": [EXCLUDED_QID]}
    selection_raw = canonical_bytes(selection)
    (output / "selection.json").write_bytes(selection_raw)
    legacy, legacy_raw = _read(legacy_path)
    entries = []
    for qid in (*COHORT, EXCLUDED_QID):
        raw, url = _fetch(qid)
        data = _json(raw)
        if set(data.get("entities", {})) != {qid}:
            raise CatalogError("Provider entity identity mismatch")
        entity = data["entities"][qid]
        revision = entity.get("lastrevid")
        path = f"snapshots/{qid}.json"
        (output / path).write_bytes(raw)
        entries.append({"qid": qid, "path": path, "revision": revision, "modified": entity.get("modified"),
                        "original_json_sha256": digest(raw), "byte_count": len(raw), "request_url": url,
                        "revision_json_url": f"{url}?revision={revision}",
                        "revision_url": f"https://www.wikidata.org/w/index.php?title={qid}&oldid={revision}",
                        "retrieved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")})
    manifest = {"schema_version": "wikidata-catalog-capture-v1", "selection_sha256": digest(selection_raw),
                "legacy_features_sha256": digest(legacy_raw), "legacy_features_count": len(legacy), "captures": entries}
    (output / "manifest.json").write_bytes(canonical_bytes(manifest))
    catalog = _derive(output, legacy_path)
    (output / "catalog.json").write_bytes(canonical_bytes(catalog))
    return build_catalog(output, legacy_path)


def compare_catalogs(old: dict, new: dict) -> dict:
    old_rows = {row["qid"]: row for row in old["references"]}
    new_rows = {row["qid"]: row for row in new["references"]}
    return {"added": sorted(new_rows.keys() - old_rows.keys()), "removed": sorted(old_rows.keys() - new_rows.keys()),
            "changed": [{"qid": qid, "old_revision": old_rows[qid]["sources"][0]["revision"],
                         "new_revision": new_rows[qid]["sources"][0]["revision"]}
                        for qid in sorted(old_rows.keys() & new_rows.keys())
                        if (old_rows[qid]["sources"][0]["revision"], old_rows[qid]["sources"][0]["original_json_sha256"])
                        != (new_rows[qid]["sources"][0]["revision"], new_rows[qid]["sources"][0]["original_json_sha256"])]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify").add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    commands.add_parser("capture").add_argument("--output", type=Path, required=True)
    difference = commands.add_parser("diff")
    difference.add_argument("old", type=Path)
    difference.add_argument("new", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "capture":
            result = capture(args.output)
            print(f"Captured and verified {len(result['references'])} references in {args.output}")
        elif args.command == "verify":
            result = build_catalog(args.source_dir)
            print(f"Verified {len(result['references'])} references; {result['content_sha256']}")
        else:
            print(json.dumps(compare_catalogs(build_catalog(args.old), build_catalog(args.new)), ensure_ascii=False, indent=2))
    except (CatalogError, OSError, TypeError, KeyError, urllib.error.URLError) as exc:
        parser.exit(1, f"Catalog operation failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
