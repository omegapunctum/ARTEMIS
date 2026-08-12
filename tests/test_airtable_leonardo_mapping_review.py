from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_airtable_leonardo_mapping_review.py"
REGISTRY = ROOT / "fixtures" / "airtable_curation" / "v2" / "review_registry.json"


def _load_validator():
    spec = importlib.util.spec_from_file_location("artemis_leonardo_mapping_review", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mapping_review_registry_is_explicitly_review_required() -> None:
    module = _load_validator()
    assert module.validate() == {
        "status": "REVIEW_REQUIRED",
        "reviews": 0,
        "row_plan_sha256": "ff63b8ed036ec79ac73e11c2eb4d3cad22b69b0e5a361c23cef767c5c5ac83f1",
        "historical_rows_authorized": False,
    }


def test_require_ready_fails_until_separate_agent_review_exists() -> None:
    module = _load_validator()
    with pytest.raises(module.MappingReviewError, match="independent mapping review is still required"):
        module.validate(require_ready=True)


def test_review_registry_requires_separate_read_only_agent_and_blocks_write() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert registry["status"] == "REVIEW_REQUIRED"
    assert registry["required_review_count"] == 1
    assert registry["required_track"] == "mapping-integrity"
    assert registry["required_independence_method"] == "separate_agent_task_read_only"
    assert registry["reviews"] == []
    assert registry["write_gate"] == {
        "ready_required_before_historical_write": True,
        "historical_rows_authorized": False,
        "gate_d_opened": False,
    }
