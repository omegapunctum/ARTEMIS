from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_airtable_leonardo_row_plan_lock.py"
LOCK = ROOT / "fixtures" / "airtable_curation" / "v2" / "row_plan_lock.json"


def _load_validator():
    spec = importlib.util.spec_from_file_location("artemis_leonardo_row_plan_lock", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_frozen_row_plan_lock_recomputes_exact_digest() -> None:
    result = _load_validator().validate()
    assert result == {
        "sha256": "ff63b8ed036ec79ac73e11c2eb4d3cad22b69b0e5a361c23cef767c5c5ac83f1",
        "total_rows": 154,
        "counts": {
            "WorldSlices": 1,
            "SliceLayers": 4,
            "WorldSources": 10,
            "KnowledgeObjects": 17,
            "ObjectParts": 11,
            "Claims": 22,
            "EvidenceLinks": 38,
            "Uncertainties": 11,
            "UncertaintyTargets": 40,
        },
        "historical_rows_authorized": False,
    }


def test_row_plan_lock_keeps_live_write_blocked_until_independent_review() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    authorization = lock["write_authorization"]

    assert lock["status"] == "ROW_PLAN_FROZEN"
    assert lock["authoritative"] is False
    assert authorization["historical_rows_authorized"] is False
    assert authorization["independent_mapping_review_required"] is True
    assert authorization["round_trip_parity_required_after_write"] is True
    assert authorization["gate_d_opened"] is False


def test_row_plan_lock_preserves_frozen_gate_c_identity() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    frozen = lock["frozen_gate_c"]

    assert frozen == {
        "commit": "bd2e103cdeec615cb19f0a4293c708fe37a4ae52",
        "tree": "757fc3d0701e825e865ceeec401d233484f066b7",
        "reviewed_content_digest": "1323ca8f0e85e0d1287cdf8d78db8fcfd907551d7a7dbb37646725cbba72ddca",
    }
    assert lock["legacy_isolation"] == {
        "KnowledgeObjects.layers": "must_remain_empty",
        "EvidenceLinks.source": "must_remain_empty",
    }
