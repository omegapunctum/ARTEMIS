#!/usr/bin/env python3
"""Build the one-artifact, non-public epistemic conflict review proof.

The accepted Research package is the input; the World Model, Explorer State and
Render Projection builders remain the only semantic/projection machinery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_globe_spike import _build_knowledge_index
from scripts.build_leonardo_gate_d_inputs import build_gate_d_inputs
from scripts.build_render_projection_fixtures import build_all


PACKAGE = ROOT / "docs/work/2026-09-24_ATL_1466_1_CONFLICT_EVIDENCE_PACKAGE_v1.md"
STATE = ROOT / "docs/project_state.json"
PROJECTION_SCHEMA = ROOT / "fixtures/render_projection/v1/schema.json"
ARTIFACT_ID = "entity-atl-1466-1-733v"
CLAIM_H = "claim-atl-1466-1-733v-heydenreich-date-v1"
CLAIM_P = "claim-atl-1466-1-733v-pedretti-date-v1"
SOURCE_ID = "S-MG-733V"


class ConflictProofError(ValueError):
    pass


def _reviewed_input() -> tuple[dict, str]:
    state = json.loads(STATE.read_text(encoding="utf-8"))["epistemic_conflict_proof"]
    raw = PACKAGE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if state["status"] not in {"implementation_ready", "implementation_in_progress", "technical_implementation_completed"} or state["evidence_state"] != "accepted" or blob != state["evidence_package_blob"]:
        raise ConflictProofError("proof requires the exact owner-accepted evidence package")
    text = raw.decode("utf-8")
    required = (
        state["evidence_package_id"], CLAIM_H, CLAIM_P,
        "The Museo Galileo catalogue reports Heydenreich's attribution of that group to `c. 1490`.",
        "The Museo Galileo catalogue reports Pedretti's attribution of the architectural studies on this theme to `c. 1514-15`.",
        "unresolved / not provided for v1", "one artifact identity, not two date-specific copies",
    )
    if (text.count(required[0]) != 1 or
        any(text.count(term) < 2 for term in required[1:3]) or
        any(text.count(term) != 1 for term in required[3:5]) or
        any(term not in text for term in required[5:])):
        raise ConflictProofError("accepted Claim wording or one-artifact identity drifted")
    return state, text


def _locator(text: str, scholar: str) -> str:
    match = re.search(
        rf"\*\*EvidenceLink {scholar} — `[^`]+`:\*\*.*?Locator: (.*?)(?=\n\n##|\Z)",
        text, flags=re.S,
    )
    if not match:
        raise ConflictProofError(f"accepted {scholar} EvidenceLink locator missing")
    return " ".join(match.group(1).split())


def build_payload() -> dict:
    state_snapshot, package_text = _reviewed_input()
    world, explorer = build_gate_d_inputs()
    # The existing Leonardo-selected time is a required query-state coordinate,
    # never an artifact dating: this Entity has no temporal/spatial extent and
    # the proof displays neither that query time nor any Globe geometry.
    claim_ids = [CLAIM_H, CLAIM_P]
    world["entities"].append({
        "id": ARTIFACT_ID, "type": "Entity", "entity_kind": "Artifact",
        "label": "ATL.1466.1 / fol. 733 verso", "claim_refs": claim_ids,
        "uncertainty_refs": ["uncertainty-atl-733v-source-conflict"],
        "layer_refs": [],
    })
    world["sources"].append({
        "id": SOURCE_ID, "type": "Source", "title": "Museo Galileo · Codice Atlantico Foglio 733 v",
        "source_type": "institutional_catalogue",
        "uri": "https://teche.museogalileo.it/leonardo/foglio/index.html?lang=it&num=ATL.1466.1",
        "review_state": "reviewed",
    })
    positions = (
        (CLAIM_H, "Heydenreich", "c. 1490", "evidence-atl-1466-1-733v-heydenreich-v1", "H"),
        (CLAIM_P, "Pedretti", "c. 1514–1515", "evidence-atl-1466-1-733v-pedretti-v1", "P"),
    )
    for claim_id, scholar, dating, evidence_id, short in positions:
        uncertainty_id = f"uncertainty-atl-733v-date-{short.lower()}"
        world["claims"].append({
            "id": claim_id, "type": "Claim", "target_refs": [ARTIFACT_ID],
            "statement": f"The Museo Galileo catalogue attributes the dating {dating} of the centrally planned church drawings on fol. 733 verso to {scholar}.",
            "claim_kind": "factual", "origin": "curator", "review_state": "reviewed",
            "confidence": "medium", "evidence_state": "supported",
            "evidence_link_refs": [evidence_id], "uncertainty_refs": [uncertainty_id],
        })
        world["evidence_links"].append({
            "id": evidence_id, "type": "EvidenceLink", "claim_id": claim_id,
            "source_id": SOURCE_ID, "relation_to_claim": "supports",
            "evidence_strength": "direct", "review_state": "reviewed",
            "locator": _locator(package_text, short),
        })
        world["uncertainties"].append({
            "id": uncertainty_id, "type": "Uncertainty", "subject_or_claim_ref": claim_id,
            "dimension": "date", "description": f"{dating} is source-native and approximate; no numeric query envelope was reviewed.",
            "effect": "Do not infer an exact year or calendar membership.",
            "effect_policy": "preserve_temporal_alternatives", "alternatives": [],
            "basis_claim_refs": [claim_id], "review_state": "reviewed",
        })
    world["uncertainties"].append({
        "id": "uncertainty-atl-733v-source-conflict", "type": "Uncertainty",
        "subject_or_claim_ref": ARTIFACT_ID, "dimension": "source_conflict",
        "description": "Two unresolved scholarly datings of one bounded architectural drawing group.",
        "effect": "Keep both attributed positions visible; no canonical production date or winner.",
        "effect_policy": "preserve_temporal_alternatives",
        "alternatives": ["Heydenreich — c. 1490", "Pedretti — c. 1514–1515"],
        "basis_claim_refs": claim_ids, "review_state": "reviewed",
    })
    explorer["state_id"] = "explorer-state-atl-733v-conflict-v1"
    explorer["selection"] = {
        "primary_object_ref": ARTIFACT_ID,
        "selected_object_refs": [ARTIFACT_ID], "comparison_object_refs": [],
    }
    explorer["active_layer_refs"] = []
    explorer["context"] = {"local_context_refs": [], "global_context_refs": [], "derived_observation_refs": []}
    explorer["active_focus"] = {key: None for key in explorer["active_focus"]}
    explorer["comparison_scope"] = {"mode": "none", "reference_refs": []}
    projection, _, globe = build_all(world, explorer, json.loads(PROJECTION_SCHEMA.read_text()))
    records = _build_knowledge_index(world, projection)["records"]
    if len(records) != 1 or records[0]["object_ref"] != ARTIFACT_ID or records[0]["temporal_membership"] != "atemporal_context" or records[0]["geometries"] or globe["primitives"]:
        raise ConflictProofError("proof escaped single atemporal, geometry-free artifact")
    record = records[0]
    if {item["id"] for item in record["claims"]} != set(claim_ids) or len(record["evidence_links"]) != 2:
        raise ConflictProofError("two distinct Claim/EvidenceLink paths are required")
    return {
        "reviewed_package_id": state_snapshot["evidence_package_id"],
        "reviewed_package_blob": state_snapshot["evidence_package_blob"],
        "explorer_state": explorer, "projection": projection,
        "record": record,
        "subject_scope": "Architectural studies on fol. 733 verso concerning a centrally planned church referable to San Lorenzo in Milan; not every mark on the sheet.",
        "conditional_qualifier": "The catalogue reports Pedretti considered possible use of the sheet in two periods, then argued for a single Roman-period epoch. This does not establish use in two periods or resolve the dating dispute.",
        "review_status": "Non-public technical review proof; formal/comparative user value unvalidated.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = build_payload()
    args.output.mkdir(parents=True, exist_ok=True)
    template = (ROOT / "scripts/atl_conflict_proof/index.html").read_text(encoding="utf-8")
    (args.output / "index.html").write_text(template, encoding="utf-8")
    (args.output / "proof.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    locators = {link["claim_id"]: link["locator"] for link in data["record"]["evidence_links"]}
    (args.output / "baseline.md").write_text(
        "# Conventional scholarly prose comparator · same-content draft\n\n"
        "Codex Atlanticus ATL.1466.1 / fol. 733 verso is one artifact. The bounded dated subject is the architectural studies on this folio concerning a centrally planned church referable to San Lorenzo in Milan; the record does not date every mark on the sheet. "
        "The Museo Galileo catalogue attributes to Heydenreich a dating of c. 1490 and to Pedretti a dating of c. 1514–1515. These are unresolved alternative scholarly datings, not two established production dates or a combined interval. "
        "Both attributions are mediated by the Museo Galileo catalogue; the direct Heydenreich and Pedretti publications were not independently inspected. "
        "Pedretti's discussion of possible two-period use is attributed and conditional; the catalogue reports he favored one Roman-period epoch. This does not prove two periods of use or settle the dating. "
        "Source: https://teche.museogalileo.it/leonardo/foglio/index.html?lang=it&num=ATL.1466.1 . "
        "Heydenreich locator: " + locators[CLAIM_H] + "\n\n"
        "Pedretti locator: " + locators[CLAIM_P] + "\n\n"
        "Both dates are approximate source expressions. The source-conflict uncertainty remains unresolved. "
        "No numerical query envelope, exact year or timeline membership is established. Missing evidence is not historical absence.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
