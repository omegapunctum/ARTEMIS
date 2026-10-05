"""Bounded research checks; runnable with stdlib unittest, no backend imports."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("park_hill_coordinate", ROOT / "scripts/check_park_hill_coordinate.py")
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)


class ParkHillCoordinateTests(unittest.TestCase):
    def test_reference_expansion_and_resolution(self):
        for value in ("SK 36064 87093", "SK3606487093"):
            self.assertEqual(research.expand_sk_reference(value), (436064, 387093))
        for value in ("SK 3606 8709", "SK36064870931", "SJ3606487093", "SK-3606487093"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                research.expand_sk_reference(value)

    def test_numeric_result_axes_and_snapshot(self):
        result = research.calculate()
        self.assertEqual(result, json.loads(research.EVIDENCE.read_text())["calculation"])
        lon, lat = result["reference_candidate_lon_lat"]
        self.assertAlmostEqual(lon, -1.459329107, places=8)
        self.assertAlmostEqual(lat, 53.379464119, places=8)
        self.assertAlmostEqual(result["ellipsoidal_point_separation_m"], 252.487357, places=5)
        self.assertFalse(result["network_enabled"])

    def test_pipeline_inverse_roundtrip(self):
        transformer = research.Transformer.from_pipeline(research.PIPELINE)
        point = transformer.transform(436064, 387093, errcheck=True)
        easting, northing = transformer.transform(*point, direction="INVERSE", errcheck=True)
        self.assertAlmostEqual(easting, 436064, places=2)
        self.assertAlmostEqual(northing, 387093, places=2)

    def test_source_drift_fails_instead_of_reinterpreting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data/features.geojson").write_text('{"features": []}')
            with self.assertRaisesRegex(ValueError, "snapshot changed"):
                research.calculate(root)

    def test_engine_drift_fails(self):
        with patch.object(research.pyproj, "proj_version_str", "different"):
            with self.assertRaisesRegex(RuntimeError, "PROJ 9.5.1"):
                research.calculate()

    def test_research_does_not_approve_geometry(self):
        evidence = json.loads(research.EVIDENCE.read_text())
        self.assertEqual(evidence["result"], "REFERENCE_POINT_DISCREPANCY")
        self.assertIsNone(evidence["disposition"]["approved_geometry"])
        self.assertFalse(evidence["disposition"]["runtime_intake_allowed"])
        self.assertFalse(evidence["disposition"]["historical_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
