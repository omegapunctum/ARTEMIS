#!/usr/bin/env python3
"""Reproduce one pinned research comparison; never write Atlas or World Model data."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import pyproj
from pyproj import Geod, Transformer

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/work/evidence/2026-10-05_park_hill_coordinate_v1.json"
FEATURE_ID = "08c92f35-cc8b-4164-a6ea-1f9c89e777dd"
SOURCE_HASH = "caf734481a3a182e4861af1daef00bac2273c87d54c0d459d172778258c8a9d1"
RECORD_HASH = "c3cb885af0847784d457575f47da5b4beb11fcb1578b37193d580b3c83124f45"
NGR = "SK 36064 87093"
# Inverse EPSG:19916 projection, EPSG:1314 datum operation, GIS lon/lat order.
# Explicit pipeline: no CRS operation selection, grid download or silent fallback.
PIPELINE = (
    "+proj=pipeline "
    "+step +inv +proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 "
    "+x_0=400000 +y_0=-100000 +ellps=airy "
    "+step +proj=push +v_3 +step +proj=cart +ellps=airy "
    "+step +proj=helmert +x=446.448 +y=-125.157 +z=542.06 "
    "+rx=0.15 +ry=0.247 +rz=0.842 +s=-20.489 +convention=position_vector "
    "+step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 "
    "+step +proj=unitconvert +xy_in=rad +xy_out=deg"
)


def expand_sk_reference(value):
    """Only this research square and five digits per axis; not a general importer."""
    compact = re.sub(r"\s+", "", value)
    if not re.fullmatch(r"SK[0-9]{10}", compact):
        raise ValueError("Expected SK and exactly five digits per axis")
    return 400000 + int(compact[2:7]), 300000 + int(compact[7:12])


def calculate(root=ROOT):
    if (pyproj.__version__, pyproj.proj_version_str) != ("3.7.2", "9.5.1"):
        raise RuntimeError("Reproduce with pyproj 3.7.2 / PROJ 9.5.1")
    pyproj.network.set_network_enabled(False)
    raw = (root / "data/features.geojson").read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_HASH:
        raise ValueError("Source snapshot changed; use this research's pinned revision")
    records = [f for f in json.loads(raw)["features"] if f["properties"]["id"] == FEATURE_ID]
    if len(records) != 1:
        raise ValueError("Expected exactly one Park Hill record")
    record = records[0]
    canonical = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(canonical).hexdigest() != RECORD_HASH:
        raise ValueError("Selected record differs from the research snapshot")
    legacy = record["geometry"]["coordinates"]
    if record["geometry"]["type"] != "Point" or legacy != [-1.4582, 53.38163]:
        raise ValueError("Unexpected legacy point")
    easting, northing = expand_sk_reference(NGR)
    # 2D operation's temporary zero height is computational, not a site elevation.
    longitude, latitude = Transformer.from_pipeline(PIPELINE).transform(easting, northing, errcheck=True)
    distance = Geod(ellps="WGS84").inv(longitude, latitude, *legacy)[2]
    return {
        "pyproj_version": pyproj.__version__,
        "proj_version": pyproj.proj_version_str,
        "network_enabled": pyproj.network.is_network_enabled(),
        "input_crs": "EPSG:27700", "output_crs": "EPSG:4326",
        "input_axis_order": ["easting", "northing"],
        "output_axis_order": ["longitude", "latitude"],
        "native_reference": NGR, "easting_m": easting, "northing_m": northing,
        "pipeline": PIPELINE,
        "pipeline_sha256": hashlib.sha256(PIPELINE.encode()).hexdigest(),
        "datum_operation": "EPSG:1314 / OSGB36 to WGS 84 (6)",
        "operation_accuracy_metadata_m": 2.0,
        "source_file": "data/features.geojson", "source_sha256": SOURCE_HASH,
        "feature_id": FEATURE_ID, "selected_record_sha256": RECORD_HASH,
        "legacy_point_lon_lat": legacy,
        "reference_candidate_lon_lat": [round(longitude, 10), round(latitude, 10)],
        "ellipsoidal_point_separation_m": round(distance, 6),
        "distance_method": "WGS84 ellipsoid inverse geodesic / pyproj.Geod",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare with committed research evidence")
    args = parser.parse_args()
    result = calculate()
    if args.check:
        if result != json.loads(EVIDENCE.read_text())["calculation"]:
            raise SystemExit("FAIL: calculation differs from research evidence")
        print("PASS: pinned Park Hill coordinate calculation reproduced")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
