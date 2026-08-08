import json
from pathlib import Path

from scripts.validate_explorer_state_fixtures import validate_state


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "fixtures" / "explorer_state" / "v1" / "schema.json"
STATE_PATH = ROOT / "fixtures" / "explorer_state" / "v1" / "state-1504-local-global.json"
WORLD_PATH = ROOT / "fixtures" / "world_model" / "v1" / "package.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(mutator=None):
    state = _load(STATE_PATH)
    if mutator is not None:
        mutator(state)
    return validate_state(state, schema=_load(SCHEMA_PATH), world=_load(WORLD_PATH))


def test_explorer_state_fixture_is_valid() -> None:
    assert _validate() == []


def test_renderer_owned_zoom_is_rejected() -> None:
    errors = _validate(lambda state: state.update({"zoom": 6}))
    assert errors
    assert any("zoom" in error for error in errors)


def test_dataset_identity_drift_is_rejected() -> None:
    def mutate(state):
        state["dataset_identity"]["value"] = "artemis-world-model-contract-fixture-v1@different"

    errors = _validate(mutate)
    assert any("dataset_identity" in error for error in errors)


def test_unknown_selected_object_is_rejected() -> None:
    def mutate(state):
        state["selection"]["selected_object_refs"].append("entity-does-not-exist")

    errors = _validate(mutate)
    assert any("unknown selection object refs" in error for error in errors)


def test_primary_selection_must_be_in_selected_refs() -> None:
    def mutate(state):
        state["selection"]["selected_object_refs"] = ["entity-mara-vale"]

    errors = _validate(mutate)
    assert any("primary_object_ref must also be present" in error for error in errors)


def test_trajectory_segment_must_belong_to_trajectory() -> None:
    def mutate(state):
        state["active_focus"]["trajectory_segment_ref"] = "trajectory-segment-does-not-exist"

    errors = _validate(mutate)
    assert any("does not belong to trajectory" in error for error in errors)


def test_region_geometry_must_belong_to_region() -> None:
    def mutate(state):
        state["active_focus"]["region_geometry_ref"] = "region-geometry-does-not-exist"

    errors = _validate(mutate)
    assert any("does not belong to Region" in error for error in errors)


def test_instant_requires_identical_start_and_end() -> None:
    def mutate(state):
        state["temporal_selection"]["end"] = "1504-03-02"

    errors = _validate(mutate)
    assert any("mode=instant" in error for error in errors)


def test_reversed_temporal_interval_is_rejected() -> None:
    def mutate(state):
        state["temporal_selection"].update(
            {
                "mode": "interval",
                "start": "1505",
                "end": "1504",
                "precision": "year",
            }
        )

    errors = _validate(mutate)
    assert any("start must be <=" in error for error in errors)


def test_material_uncertainty_cannot_be_hidden() -> None:
    def mutate(state):
        state["epistemic_display"]["show_material_uncertainty"] = False

    errors = _validate(mutate)
    assert errors
    assert any("show_material_uncertainty" in error or "material uncertainty" in error for error in errors)


def test_authoritative_visible_object_cache_is_rejected() -> None:
    errors = _validate(lambda state: state.update({"visible_object_ids": ["entity-mara-vale"]}))
    assert errors
    assert any("visible_object_ids" in error for error in errors)


def test_focus_object_target_must_resolve() -> None:
    def mutate(state):
        state["view_intent"] = {
            "kind": "focus_object",
            "target_ref": "entity-does-not-exist",
            "coordinate_reference": "EPSG:4326",
        }

    errors = _validate(mutate)
    assert any("focus_object view_intent.target_ref" in error for error in errors)
