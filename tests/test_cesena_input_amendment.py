"""One explicitly authorized statement deletion, with frozen input lineage."""
import copy
import hashlib
import json
from pathlib import Path, PureWindowsPath

import pytest

from scripts import build_leonardo_gate_d_inputs as gate_d
from scripts import build_globe_spike as spike
from scripts import build_unified_explorer as unified


def test_unified_rejects_copied_amendment_that_does_not_match_ledger(tmp_path, monkeypatch):
    original_copy = unified.shutil.copyfile

    def corrupt_amendment(source, destination, *args, **kwargs):
        result = original_copy(source, destination, *args, **kwargs)
        if Path(source) == gate_d.CESENA_AMENDMENT_PATH and "inputs" in Path(destination).parts:
            Path(destination).write_bytes(Path(destination).read_bytes() + b" ")
        return result

    monkeypatch.setattr(unified.shutil, "copyfile", corrupt_amendment)
    with pytest.raises(unified.UnifiedBuildError, match="copied input differs"):
        unified.build_unified_explorer(tmp_path / "unified")


def _inputs():
    payload = gate_d.CLAIMS_PATH.read_bytes()
    return json.loads(payload), json.loads(gate_d.CESENA_AMENDMENT_PATH.read_bytes()), payload


def test_only_one_statement_changes_and_original_package_is_not_mutated(monkeypatch):
    frozen_bytes = {p: p.read_bytes() for p in gate_d.SLICE_ROOT.rglob("*") if p.is_file()}
    package, amendment, payload = _inputs()
    original = copy.deepcopy(package)
    amended = gate_d._apply_cesena_amendment(package, amendment, payload)
    assert package == original
    expected = copy.deepcopy(original)
    claim = next(c for c in expected["claims"] if c["claim_id"] == amendment["claim_id"])
    claim["statement"] = amendment["after_statement"]
    assert amended == expected
    world, state = gate_d.build_gate_d_inputs()
    with monkeypatch.context() as patch:
        patch.setattr(gate_d, "_apply_cesena_amendment", lambda package, *_: copy.deepcopy(package))
        original_world, original_state = gate_d.build_gate_d_inputs()
    expected_world = copy.deepcopy(original_world)
    target = next(c for c in expected_world["claims"] if c["id"] == amendment["claim_id"])
    target["statement"] = amendment["after_statement"]
    assert world == expected_world  # All IDs, statuses, evidence, uncertainty, time and geometry.
    assert state == original_state
    assert frozen_bytes == {p: p.read_bytes() for p in frozen_bytes}


@pytest.mark.parametrize("case, message", [
    ("missing", "target Claim/object"),
    ("duplicate", "duplicate Claims"),
    ("object", "target Claim/object"),
    ("statement", "old statement"),
    ("other_claim", "differs from the frozen"),
    ("base_bytes", "byte hash"),
])
def test_amendment_rejects_changed_or_ambiguous_frozen_input(case, message):
    package, amendment, payload = _inputs()
    target = next(c for c in package["claims"] if c["claim_id"] == amendment["claim_id"])
    if case == "missing":
        package["claims"].remove(target)
    elif case == "duplicate":
        package["claims"].append(copy.deepcopy(target))
    elif case == "object":
        target["target_object_ref"] = "event-leonardo-rimini-note"
    elif case == "statement":
        target["statement"] = amendment["after_statement"]
    elif case == "other_claim":
        package["claims"][0]["confidence"] = "high"
    else:
        payload += b"\n"
    with pytest.raises(gate_d.GateDInputError, match=message):
        gate_d._apply_cesena_amendment(package, amendment, payload)


@pytest.mark.parametrize("field, value", [
    ("patch", {"review_state": "verified"}),
    ("after_statement", "Leonardo surveyed Cesena on 10 August 1502."),
    ("claim_id", "claim-rimini-presence-1502-08-08"),
    ("source_id", "new-unreviewed-source"),
    ("base_claims_sha256", "0" * 64),
])
def test_amendment_rejects_arbitrary_shape_target_wording_and_provenance(field, value):
    package, amendment, payload = _inputs()
    amendment[field] = value
    with pytest.raises(gate_d.GateDInputError, match="exact authorized shape and values"):
        gate_d._apply_cesena_amendment(package, amendment, payload)


def test_frozen_validator_runs_before_amendment(monkeypatch):
    from scripts import validate_leonardo_world_slice as frozen
    def refuse():
        raise ValueError("frozen package rejected")
    def forbidden(*_):
        pytest.fail("amendment applied before frozen validation")
    monkeypatch.setattr(frozen, "validate_package", refuse)
    monkeypatch.setattr(gate_d, "_apply_cesena_amendment", forbidden)
    with pytest.raises(ValueError, match="frozen package rejected"):
        gate_d.build_gate_d_inputs()


def test_real_builds_share_derived_identity_and_expose_original_and_amendment_bytes(tmp_path):
    world, state = gate_d.build_gate_d_inputs()
    provenance = gate_d.cesena_amendment_provenance()
    identity = state["dataset_identity"]
    assert identity == world["world_slice"]["dataset_identity"]
    assert identity["kind"] == "bounded_gate_c_input_amendment"
    assert identity["value"] == (
        f"{world['world_slice']['id']}@{world['gate_c_decision']['reviewed_content_digest']}"
        f"+{provenance['amendment_id']}@{hashlib.sha256(gate_d.CESENA_AMENDMENT_PATH.read_bytes()).hexdigest()}"
    )
    output = tmp_path / "native"
    meta = spike.build_spike(output)
    assert meta["dataset_identity"] == identity
    for name in ("projection.json", "globe-projection.json"):
        assert json.loads((output / name).read_bytes())["source"]["dataset_identity"] == identity
    assert (output / "input-amendments" / "cesena_presence_v1.json").read_bytes() == gate_d.CESENA_AMENDMENT_PATH.read_bytes()
    assert (output / "input-amendments" / "frozen_claims_manifest.json").read_bytes() == gate_d.CLAIMS_PATH.read_bytes()
    assert meta["input_amendment"]["historical_review_reaccepted"] is False
    unified_output = tmp_path / "unified"
    unified_meta = unified.build_unified_explorer(unified_output)
    bundle = json.loads((unified_output / "unified-bundle.json").read_bytes())
    assert unified_meta["leonardo_dataset_identity"] == bundle["leonardo"]["explorerState"]["dataset_identity"] == identity
    assert bundle["leonardo"]["projection"]["source"]["dataset_identity"] == identity
    assert bundle["leonardo"]["globe"]["source"]["dataset_identity"] == identity
    claims = [c for r in bundle["leonardo"]["knowledge"]["records"] for c in r["claims"] if c["id"] == provenance["claim_id"]]
    assert len(claims) == 1
    assert claims[0]["statement"] == provenance["after_statement"]
    assert (claims[0]["review_state"], claims[0]["confidence"], claims[0]["evidence_state"]) == ("draft", "unknown", "missing")
    for path in (gate_d.CLAIMS_PATH, gate_d.CESENA_AMENDMENT_PATH):
        relative = path.relative_to(gate_d.ROOT).as_posix()
        row = next(r for r in bundle["input_ledger"] if r["path"] == relative)
        assert row["sha256"] == unified_meta["input_sha256"][relative] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert (unified_output / "inputs" / relative).read_bytes() == path.read_bytes()
    assert unified_meta["leonardo_input_amendment"]["sha256"] == provenance["sha256"]


def test_amendment_provenance_uses_ledger_paths_on_windows(monkeypatch):
    original = gate_d.CESENA_AMENDMENT_PATH
    relative = original.relative_to(gate_d.ROOT).as_posix()
    class WindowsAmendmentPath:
        def relative_to(self, root):
            return PureWindowsPath(relative)
        def read_bytes(self):
            return original.read_bytes()
        def read_text(self, **kwargs):
            return original.read_text(**kwargs)
    monkeypatch.setattr(gate_d, "CESENA_AMENDMENT_PATH", WindowsAmendmentPath())
    provenance = gate_d.cesena_amendment_provenance()
    assert provenance["path"] == relative
    assert provenance["sha256"] == hashlib.sha256(original.read_bytes()).hexdigest()
