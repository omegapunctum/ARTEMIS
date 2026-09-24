"""Accepted one-artifact proof through existing semantic/projection boundaries."""

import json
from pathlib import Path

import pytest

from scripts import build_atl_conflict_proof as proof


def test_accepted_claims_survive_existing_world_state_projection_path(tmp_path: Path) -> None:
    payload = proof.build_payload()
    state = payload["explorer_state"]
    projected = payload["projection"]["items"]
    record = payload["record"]
    assert state["selection"]["selected_object_refs"] == [proof.ARTIFACT_ID]
    assert state["selection"]["primary_object_ref"] == record["object_ref"]
    assert len(projected) == 1
    assert projected[0]["object_ref"] == proof.ARTIFACT_ID
    assert projected[0]["temporal_membership"] == "atemporal_context"
    assert projected[0]["geometry_refs"] == []
    assert not record["geometries"]
    assert {claim["id"] for claim in record["claims"]} == {proof.CLAIM_H, proof.CLAIM_P}
    assert {e["claim_id"] for e in record["evidence_links"]} == {proof.CLAIM_H, proof.CLAIM_P}
    assert {e["source_id"] for e in record["evidence_links"]} == {proof.SOURCE_ID}
    assert all(e["review_state"] == "reviewed" and e["locator"] for e in record["evidence_links"])
    assert len(record["sources"]) == 1
    assert record["sources"][0]["uri"].startswith("https://teche.museogalileo.it/")
    assert {u["dimension"] for u in record["uncertainties"]} == {"source_conflict", "date"}
    conflict = next(u for u in record["uncertainties"] if u["dimension"] == "source_conflict")
    assert set(conflict["basis_claim_refs"]) == {proof.CLAIM_H, proof.CLAIM_P}
    assert conflict["alternatives"] == ["Heydenreich — c. 1490", "Pedretti — c. 1514–1515"]
    # The inherited query coordinate is unrelated to this atemporal artifact.
    assert "1502" not in json.dumps(record, ensure_ascii=False)
    assert "1490–1515" not in json.dumps(record, ensure_ascii=False)

    assert payload["reviewed_package_blob"] == json.loads(proof.STATE.read_text())["epistemic_conflict_proof"]["evidence_package_blob"]


def test_build_emits_non_public_review_and_fair_baseline(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["build_atl_conflict_proof.py", "--output", str(tmp_path)])
    proof.main()
    html = (tmp_path / "index.html").read_text()
    baseline = (tmp_path / "baseline.md").read_text()
    payload = json.loads((tmp_path / "proof.json").read_text())
    assert 'name="robots" content="noindex,nofollow"' in html
    assert "fetch('./proof.json')" in html
    assert "Dating disputed" in html
    assert "mode-range" not in html and "mode-scrub" not in html
    assert "c. 1490" in baseline and "c. 1514–1515" in baseline
    assert "Museo Galileo" in baseline and "two periods" in baseline
    assert len(payload["record"]["claims"]) == 2
    assert all(link["locator"] in baseline for link in payload["record"]["evidence_links"])
    assert "const conflict = record.uncertainties.find" in html
    assert "history.replaceState(null, '', url)" in html
    assert "target = '_blank'" in html


def test_builder_rejects_package_mutation(tmp_path: Path, monkeypatch) -> None:
    altered = tmp_path / "evidence.md"
    altered.write_bytes(proof.PACKAGE.read_bytes() + b"\nchanged\n")
    monkeypatch.setattr(proof, "PACKAGE", altered)
    with pytest.raises(proof.ConflictProofError, match="exact owner-accepted"):
        proof.build_payload()
