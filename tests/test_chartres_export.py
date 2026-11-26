import json

from scripts.export_chartres_pilot import export


def test_chartres_round_trip(tmp_path):
    export(tmp_path)
    first = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    export(tmp_path)
    assert first == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    feature = json.loads(first["chartres.geojson"])
    timeline = json.loads(first["chartres-timeline.json"])
    assert feature["id"] == timeline["subject_id"] == "dc4b7dde-e7b6-4a71-8bf2-0b7056266635"
    assert feature["geometry"] == {"type": "Point", "coordinates": [1.4878, 48.4478]}
    assert feature["properties"]["claims"] == timeline["entries"]
    claims = {entry["id"]: entry for entry in timeline["entries"]}
    assert sorted(c["glyph"] for c in claims.values()) == ["interval"] * 3 + ["marker"] * 3
    assert all(d["source"].startswith("https://") and d["locator"] for c in claims.values() for d in c["dates"])
    assert claims["fire"]["dates"][0]["date"] == "1194-06-10"
    assert claims["consecration"]["dates"][0]["date"] == "1260-10-17"
    assert claims["choir-in-use"]["role"] == "attested_in_use"
    assert claims["choir-in-use"]["dates"][0]["start"] == 1221
    rebuild = claims["gothic-rebuild"]["dates"][0]
    assert (rebuild["start"], rebuild["end"], rebuild["end_precision"]) == (1194, 1230, "circa_year")
    gables = claims["gables"]["dates"][0]
    assert (gables["start"], gables["end"]) == (1245, 1250)
    spire = claims["north-spire"]["dates"]
    assert [(d["start"], d["end"]) for d in spire] == [(1506, 1513), (1507, 1513)]
    assert spire[0]["source"].endswith("/les-grandes-dates/")
    assert spire[1]["source"].endswith("/Dossier-de-presse-Millenaire.pdf")
