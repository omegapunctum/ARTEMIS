"""Real bounded source package integrity and negative intake semantics."""
import copy
import gzip
import io
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from scripts import import_wikidata_catalog as catalog


@pytest.fixture
def package(tmp_path):
    source = tmp_path / "source"
    shutil.copytree(catalog.SOURCE_DIR, source)
    legacy = tmp_path / "features.json"
    shutil.copyfile(catalog.ROOT / "data/features.json", legacy)
    return source, legacy


def rewrite_source(source, qid, mutate):
    path = source / "snapshots" / f"{qid}.json"
    payload = json.loads(path.read_bytes())
    mutate(payload["entities"][qid])
    raw = catalog.canonical_bytes(payload)
    path.write_bytes(raw)
    manifest_path = source / "manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    entry = next(row for row in manifest["captures"] if row["qid"] == qid)
    entry["original_json_sha256"] = catalog.digest(raw)
    entry["byte_count"] = len(raw)
    manifest_path.write_bytes(catalog.canonical_bytes(manifest))


def point(entity):
    return entity["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]


def test_frozen_rebuild_is_byte_identical_and_offline(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: pytest.fail("offline build requested network"))
    first, second = catalog.build_catalog(), catalog.build_catalog()
    assert catalog.canonical_bytes(first) == catalog.canonical_bytes(second) == catalog.CATALOG_PATH.read_bytes()
    assert len(first["references"]) == len(set(row["item_id"] for row in first["references"])) == 10
    assert [row["qid"] for row in first["references"]] == list(catalog.COHORT)
    assert first["time_filtering"] == "excluded"


def test_native_values_languages_and_provenance_are_preserved():
    result = catalog.build_catalog()
    manifest = json.loads((catalog.SOURCE_DIR / "manifest.json").read_bytes())
    assert len(catalog.source_input_paths()) == 14
    assert all(path.is_file() for path in catalog.source_input_paths())
    for row, capture in zip(result["references"], manifest["captures"]):
        entity = json.loads((catalog.SOURCE_DIR / capture["path"]).read_bytes())["entities"][row["qid"]]
        assert row["labels"] == {lang: entry["value"] for lang, entry in entity["labels"].items()}
        assert row["aliases"] == {lang: [entry["value"] for entry in entries] for lang, entries in entity["aliases"].items()}
        assert row["coordinate_statement"] == entity["claims"]["P625"][0]
        assert row["geometry"]["coordinates"] == [point(entity)["longitude"], point(entity)["latitude"]]
        assert row["sources"][0]["revision"] == entity["lastrevid"]
        assert row["sources"][0]["original_json_sha256"] == catalog.digest((catalog.SOURCE_DIR / capture["path"]).read_bytes())
        assert row["native_dates"] == {prop: statements for prop, statements in entity["claims"].items() if any(statement.get("mainsnak", {}).get("datatype") == "time" for statement in statements)}
        assert row["temporal_extent"] is None and row["historical_position"] is None
        assert row["historical_applicability"] == "unknown" and row["spatial_precision"] == "unknown_precision"
        claim, evidence, source = row["claims"][0], row["evidence_links"][0], row["sources"][0]
        assert (claim["claim_kind"], claim["origin"], claim["review_state"], claim["confidence"], claim["evidence_state"]) == ("factual", "imported", "draft", "unknown", "missing")
        assert evidence["review_state"] == source["review_state"] == "draft"
        assert evidence["reviewer"] is None and entity["claims"]["P625"][0]["id"] in evidence["locator"]
        assert source["license"] == "CC0-1.0"
        assert source["revision_json_url"].endswith(f"revision={entity['lastrevid']}")
        assert all(".wikipedia.org" in url for url in row["wikipedia_urls"].values())
        assert {"location", "scope_limitation", "missing_evidence"} == {entry["kind"] for entry in row["uncertainties"]}


def test_source_missing_references_are_not_fabricated():
    result = catalog.build_catalog()
    rows = {row["qid"]: row for row in result["references"]}
    for qid in ("Q62408", "Q207385", "Q642039"):
        assert "references" not in rows[qid]["coordinate_statement"]
        assert rows[qid]["claims"][0]["evidence_state"] == "missing"
    assert result["excluded"][0]["qid"] == "Q193639"
    assert result["excluded"][0]["coordinate_statements"][0]["mainsnak"]["datavalue"]["value"]["precision"] == -1e-06


@pytest.mark.parametrize("mutation", [
    lambda entity: entity["claims"].pop("P625"),
    lambda entity: entity["claims"]["P625"].append(copy.deepcopy(entity["claims"]["P625"][0])),
    lambda entity: entity["claims"]["P625"][0].update(qualifiers={"P580": [{"snaktype": "somevalue"}]}),
    lambda entity: entity["claims"]["P625"][0].update(rank="deprecated"),
    lambda entity: entity["claims"]["P625"][0]["mainsnak"].update(snaktype="somevalue"),
    lambda entity: point(entity).update(globe="http://www.wikidata.org/entity/Q405"),
    lambda entity: point(entity).update(latitude=91),
    lambda entity: point(entity).update(longitude=-181),
    lambda entity: point(entity).update(latitude=True),
    lambda entity: point(entity).update(precision=-1e-06),
    lambda entity: point(entity).update(precision=0),
    lambda entity: point(entity).update(precision="0.001"),
    lambda entity: entity["claims"]["P625"][0].update(id="Q999$wrong"),
    lambda entity: entity.update(id="Q999"),
    lambda entity: entity.update(lastrevid=entity["lastrevid"] + 1),
    lambda entity: entity["labels"]["en"].update(language="ru"),
])
def test_malformed_coordinates_and_identities_fail_closed_even_after_rehash(package, mutation):
    source, legacy = package
    rewrite_source(source, "Q83125", mutation)
    with pytest.raises(catalog.CatalogError):
        catalog.build_catalog(source, legacy)


def test_raw_hash_and_stored_catalog_guard(package):
    source, legacy = package
    path = source / "snapshots/Q83125.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(catalog.CatalogError, match="provenance"):
        catalog.build_catalog(source, legacy)
    shutil.copyfile(catalog.SOURCE_DIR / "snapshots/Q83125.json", path)
    stored_path = source / "catalog.json"
    stored = json.loads(stored_path.read_bytes())
    stored["references"][0]["geometry"]["coordinates"][0] += 1
    stored_path.write_bytes(catalog.canonical_bytes(stored))
    with pytest.raises(catalog.CatalogError, match="Stored catalog drift"):
        catalog.build_catalog(source, legacy)


def test_duplicate_selection_and_legacy_drift_fail(package):
    source, legacy = package
    selection = json.loads((source / "selection.json").read_bytes())
    selection["qids"][1] = selection["qids"][0]
    (source / "selection.json").write_bytes(catalog.canonical_bytes(selection))
    with pytest.raises(catalog.CatalogError, match="cohort"):
        catalog.build_catalog(source, legacy)
    shutil.copyfile(catalog.SOURCE_DIR / "selection.json", source / "selection.json")
    legacy.write_bytes(legacy.read_bytes() + b" ")
    with pytest.raises(catalog.CatalogError, match="legacy guard"):
        catalog.build_catalog(source, legacy)


@pytest.mark.parametrize("value", [{"name_en": "Tower Bridge"}, {"name_ru": "Тауэрский мост"}, {"wikidata_id": "Q83125"}, {"source_url": "https://en.wikipedia.org/wiki/Tower_Bridge"}, {"name_en": "Ｔｏｗｅｒ　Ｂｒｉｄｇｅ"}])
def test_explicit_external_id_name_and_sitelink_duplicates_rejected(value):
    entity = json.loads((catalog.SOURCE_DIR / "snapshots/Q83125.json").read_bytes())["entities"]["Q83125"]
    with pytest.raises(catalog.CatalogError, match="[Dd]uplicate"):
        catalog._duplicate_guard([entity], [{"fields": value}])


def test_absent_precision_retained_as_unknown(package):
    source, legacy = package
    rewrite_source(source, "Q83125", lambda entity: point(entity).update(precision=None))
    result = catalog._derive(source, legacy)
    assert result["references"][0]["coordinate_statement"]["mainsnak"]["datavalue"]["value"]["precision"] is None
    assert result["references"][0]["spatial_precision"] == "unknown_precision"


def test_duplicate_json_keys_nonfinite_and_oversize_rejected():
    for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'\xff', b' ' * (catalog.MAX_BYTES + 1)):
        with pytest.raises(catalog.CatalogError):
            catalog._json(raw)


def test_capture_fresh_directory_no_overwrite_and_no_duplicate_reimport(tmp_path, monkeypatch):
    monkeypatch.setattr(catalog, "_fetch", lambda qid: ((catalog.SOURCE_DIR / "snapshots" / f"{qid}.json").read_bytes(), f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"))
    output = tmp_path / "fresh"
    result = catalog.capture(output)
    before = {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
    with pytest.raises(FileExistsError):
        catalog.capture(output)
    assert before == {path.relative_to(output): path.read_bytes() for path in output.rglob("*") if path.is_file()}
    assert len(result["references"]) == len(set(row["qid"] for row in result["references"])) == 10
    assert catalog.compare_catalogs(catalog.build_catalog(), result) == {"added": [], "removed": [], "changed": []}


def test_explicit_revision_comparison_preserves_original():
    original = catalog.build_catalog()
    before = catalog.canonical_bytes(original)
    changed = copy.deepcopy(original)
    changed["references"][0]["sources"][0]["revision"] += 1
    difference = catalog.compare_catalogs(original, changed)
    assert difference["changed"] == [{"qid": "Q83125", "old_revision": original["references"][0]["sources"][0]["revision"], "new_revision": changed["references"][0]["sources"][0]["revision"]}]
    assert catalog.canonical_bytes(original) == before


class ProviderResponse(io.BytesIO):
    def __init__(self, raw, url="https://www.wikidata.org/wiki/Special:EntityData/Q83125.json", encoding=None):
        super().__init__(raw)
        self.url = url
        self.headers = {"Content-Encoding": encoding} if encoding else {}


def test_capture_headers_and_gzip_are_bounded(monkeypatch):
    raw = b'{"entities":{}}'
    requests = []
    def respond(request, timeout):
        requests.append((request, timeout))
        return ProviderResponse(gzip.compress(raw), encoding="gzip")
    monkeypatch.setattr(urllib.request, "urlopen", respond)
    assert catalog._fetch("Q83125")[0] == raw
    request, timeout = requests[0]
    assert request.get_header("User-agent") == catalog.USER_AGENT
    assert request.get_header("Accept-encoding") == "gzip"
    assert timeout == 30
    monkeypatch.setattr(catalog, "MAX_BYTES", 100)
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: ProviderResponse(gzip.compress(b" " * 101), encoding="gzip"))
    with pytest.raises(catalog.CatalogError, match="bounded input size"):
        catalog._fetch("Q83125")


def test_external_provider_redirect_is_rejected(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: ProviderResponse(b"{}", url="https://example.com/source.json"))
    with pytest.raises(catalog.CatalogError, match="redirect"):
        catalog._fetch("Q83125")


def test_provider_retry_after_and_bounded_exhaustion(monkeypatch):
    sleeps, attempts = [], []
    def respond(*args, **kwargs):
        attempts.append(1)
        if len(attempts) < 3:
            raise urllib.error.HTTPError("https://www.wikidata.org", 429, "busy", {"Retry-After": "2"}, None)
        return ProviderResponse(b"{}")
    monkeypatch.setattr(urllib.request, "urlopen", respond)
    monkeypatch.setattr(catalog.time, "sleep", sleeps.append)
    assert catalog._fetch("Q83125")[0] == b"{}"
    assert sleeps == [2, 2] and len(attempts) == 3
    def too_long(*args, **kwargs):
        raise urllib.error.HTTPError("https://www.wikidata.org", 503, "busy", {"Retry-After": "120"}, None)
    monkeypatch.setattr(urllib.request, "urlopen", too_long)
    with pytest.raises(catalog.CatalogError, match="backoff"):
        catalog._fetch("Q83125")
    def permanent(*args, **kwargs):
        raise urllib.error.HTTPError("https://www.wikidata.org", 404, "missing", {}, None)
    monkeypatch.setattr(urllib.request, "urlopen", permanent)
    with pytest.raises(catalog.CatalogError, match="404"):
        catalog._fetch("Q83125")
