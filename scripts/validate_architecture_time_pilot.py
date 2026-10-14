#!/usr/bin/env python3
"""Validate the finite, separately reviewed architecture-time overlay offline.

The receipt admits exact packet bytes for source-relative display. It does not
rewrite pending source-native review states or confer historical certainty.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "fixtures/architecture_time_pilot/v1/evidence.json"
ACCEPTANCE_PATH = PACKET_PATH.with_name("acceptance.json")
COHORT = {"catalog:wikidata:Q83125", "catalog:wikidata:Q642039", "catalog:wikidata:Q607700"}


class ArchitectureTimeError(ValueError):
    """Packet cannot safely supply historical matches."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArchitectureTimeError(message)


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def index_rows(packet: dict, key: str, id_key: str = "id") -> dict:
    rows = packet.get(key)
    require(isinstance(rows, list), f"{key} must be an array")
    result = {}
    for row in rows:
        require(isinstance(row, dict) and text(row.get(id_key)), f"{key} identity missing")
        require(row[id_key] not in result, f"{key} duplicate identity")
        result[row[id_key]] = row
    return result


def references(row: dict, key: str, targets: dict, *, nonempty: bool = True) -> list:
    refs = row.get(key)
    require(isinstance(refs, list) and (bool(refs) or not nonempty), f"{key} missing")
    require(all(isinstance(ref, str) and ref in targets for ref in refs), f"{key} unresolved reference")
    require(len(refs) == len(set(refs)), f"{key} duplicate reference")
    return refs


def time_years(temporal: Any) -> set[int]:
    require(isinstance(temporal, dict), "claim time must be an object")
    require(temporal.get("calendar") == "source_native_CE" and temporal.get("conversion") is None,
            "source-native calendar must remain unconverted")
    precision = temporal.get("precision")
    require(precision in {"year", "month", "day"}, "unsupported or invented temporal precision")
    if "value" in temporal:
        value = temporal["value"]
        require("start" not in temporal and "end" not in temporal, "ambiguous claim time")
        if precision == "year":
            require(type(value) is int and 1 <= value <= 9999, "year precision requires an integer year")
            return {value}
        pattern = r"\d{4}-\d{2}" if precision == "month" else r"\d{4}-\d{2}-\d{2}"
        require(isinstance(value, str) and re.fullmatch(pattern, value) is not None,
                "time value exceeds or contradicts native precision")
        try:
            date.fromisoformat(value + "-01" if precision == "month" else value)
        except ValueError as exc:
            raise ArchitectureTimeError("invalid native date") from exc
        return {int(value[:4])}
    require(precision == "year", "interval precision must preserve source years")
    start, end = temporal.get("start"), temporal.get("end")
    require(type(start) is int and type(end) is int and 1 <= start <= end <= 9999,
            "claim interval must be finite and ordered")
    return {start, end}


def validate_packet(packet: Any, registry_ids: set[str] | None = None) -> None:
    require(isinstance(packet, dict), "packet must be an object")
    require(packet.get("schema_version") == "1.0.0" and packet.get("package_id") == "architecture_time_pilot_v1",
            "unsupported architecture time package")
    require(packet.get("status") == "proposed" and packet.get("review_state") == "pending_review",
            "native packet status must not be silently promoted")
    require(packet.get("calendar") == {"era": "CE", "selection_calendar": "proleptic_gregorian",
            "selection_precision": "year", "min": 91, "max": 1894,
            "source_calendar_conversion_performed": False}, "calendar scope differs from decision")
    require(packet.get("coverage") == {"end_year": 1894, "end_semantics": "coverage_cut_not_demolition", "complete": False},
            "finite coverage must not become a lifetime")
    sources = index_rows(packet, "sources")
    claims = index_rows(packet, "claims")
    evidence = index_rows(packet, "evidence_links")
    inferences = index_rows(packet, "inferences")
    conflicts = index_rows(packet, "conflicts")
    objects = index_rows(packet, "objects", "existing_item_id")
    require(set(objects) == COHORT, "pilot requires exactly the three authorized existing identities")
    if registry_ids is not None:
        require(COHORT <= registry_ids, "pilot identity absent from native registry")
    require(bool(sources) and bool(claims) and bool(evidence), "source/claim/evidence chains required")
    for source in sources.values():
        require(all(text(source.get(k)) for k in ("title", "publisher", "url", "retrieved_at", "source_type")),
                "source bibliographic metadata incomplete")
        require(source["url"].startswith("https://"), "source URL must use HTTPS")
        require(isinstance(source.get("rights"), dict) and text(source["rights"].get("reuse")), "source reuse limits missing")
    claim_years = {}
    used_evidence = set()
    for cid, claim in claims.items():
        require(claim.get("subject_id") in objects, "claim has unsupported subject")
        require(claim.get("claim_kind") == "source_relative_assertion" and text(claim.get("statement")),
                "claim must remain an explicit source-relative assertion")
        require(claim.get("confidence") is None and isinstance(claim.get("uncertainty"), list), "claim confidence or uncertainty promotion")
        for eid in references(claim, "evidence_link_ids", evidence):
            require(evidence[eid].get("claim_id") == cid, "evidence link points to a different claim")
            used_evidence.add(eid)
        claim_years[cid] = time_years(claim["time"]) if "time" in claim else set()
    require(used_evidence == set(evidence), "orphan evidence link")
    require(any(1894 in years for years in claim_years.values()), "calendar endpoint needs a finite accepted event")
    used_sources = set()
    for link in evidence.values():
        require(link.get("claim_id") in claims and link.get("source_id") in sources, "evidence has orphan claim/source")
        require(text(link.get("locator")) and link.get("relation_to_claim") == "supports", "evidence locator/support missing")
        used_sources.add(link["source_id"])
    require(used_sources == set(sources), "orphan source")
    for inference in inferences.values():
        require(inference.get("subject_id") in objects and inference.get("claim_kind") == "inference", "inference subject/kind invalid")
        basis = references(inference, "basis_claim_ids", claims)
        require(all(claims[c]["subject_id"] == inference["subject_id"] for c in basis), "cross-subject inference")
        require(inference.get("coverage_end") == 1894 and text(inference.get("rule")) and text(inference.get("statement")), "inference requires finite coverage and explicit rule")
        require(isinstance(inference.get("limitations"), list) and bool(inference["limitations"]), "inference limitations missing")
        require(inference.get("admission") in {"pending_review", "withheld_conflict"}, "inference admission invalid")
    for conflict in conflicts.values():
        require(conflict.get("subject_id") in objects and conflict.get("status") == "unresolved" and conflict.get("resolution") is None,
                "conflict must remain unresolved")
        require(text(conflict.get("reason")), "conflict explanation missing")
        basis = references(conflict, "claim_ids", claims)
        require(len(basis) >= 2 and all(claims[c]["subject_id"] == conflict["subject_id"] for c in basis), "conflict alternatives invalid")
    phase_ids = set()
    for oid, obj in objects.items():
        require(text(obj.get("subject_scope")) and obj.get("modern_point_only") is True and obj.get("historical_geometry") is None and obj.get("loss_date") is None,
                "modern anchor cannot become historical geometry or loss date")
        conflict_refs = references(obj, "conflict_ids", conflicts, nonempty=False)
        expected_conflicts = {cid for cid, c in conflicts.items() if c["subject_id"] == oid}
        require(set(conflict_refs) == expected_conflicts, "object conflict references incomplete")
        phases = obj.get("phases")
        require(isinstance(phases, list), "object phases missing")
        if conflict_refs:
            require(not phases and obj.get("temporal_classification") == "unknown_context_conflict",
                    "unresolved conflict must withhold every phase")
        else:
            require(obj.get("temporal_classification") in {"proposed_dated", "unknown_context"}, "unknown temporal classification")
            require(bool(phases) == (obj["temporal_classification"] == "proposed_dated"), "dated classification requires phases")
        for phase in phases:
            require(isinstance(phase, dict) and text(phase.get("id")) and phase["id"] not in phase_ids, "phase identity missing/duplicated")
            phase_ids.add(phase["id"])
            require(phase.get("kind") in {"construction", "completed"} and phase.get("admission") == "pending_review", "phase kind/admission unsupported")
            interval = phase.get("interval")
            require(isinstance(interval, list) and len(interval) == 2 and all(type(v) is int for v in interval)
                    and 91 <= interval[0] <= interval[1] <= 1894, "phase interval must be finite within reviewed coverage")
            require(phase.get("precision") == "year" and phase.get("boundary_rule") == "inclusive_year_overlap_not_full_year_presence",
                    "phase must preserve year intersection, not invented day precision")
            basis = references(phase, "basis_claim_ids", claims)
            require(all(claims[c]["subject_id"] == oid for c in basis), "phase has cross-subject basis")
            years = set().union(*(claim_years[c] for c in basis))
            require(interval[0] in years, "phase start has no source-native boundary")
            inference_refs = references(phase, "inference_ids", inferences, nonempty=False)
            require(all(inferences[i]["subject_id"] == oid and inferences[i]["admission"] == "pending_review" for i in inference_refs), "phase uses withheld or cross-subject inference")
            if phase["kind"] == "construction":
                require(phase.get("end_semantics") == "completion_year" and interval[1] in years, "construction end has no source-native boundary")
            else:
                require(phase.get("end_semantics") == "coverage_cut_not_demolition", "completed phase must disclose coverage cut")
                require(interval[1] == 1894, "completed phase exceeds finite coverage")
            if phase.get("support") == "inferred":
                require(bool(inference_refs), "inferred persistence requires explicit inference")
                require(all(set(inferences[i]["basis_claim_ids"]) <= set(basis) for i in inference_refs), "phase omits inference basis")
            else:
                require(phase.get("support") == "source_reported" and not inference_refs, "phase support invalid")
                require(phase["kind"] != "completed" or interval[0] == interval[1], "multi-year persistence cannot be directly asserted without inference")


def load_accepted_packet(registry_ids: set[str] | None = None) -> dict:
    payload = PACKET_PATH.read_bytes()
    packet = json.loads(payload)
    validate_packet(packet, registry_ids)
    receipt = json.loads(ACCEPTANCE_PATH.read_bytes())
    require(isinstance(receipt, dict) and receipt.get("status") == "accepted"
            and receipt.get("scope") == "architecture-time-pilot-v1", "packet requires distinct acceptance receipt")
    require(receipt.get("packet_sha256") == hashlib.sha256(payload).hexdigest(), "packet differs from reviewed bytes")
    require(text(receipt.get("reviewer")) and text(receipt.get("reviewed_at")), "review identity/date missing")
    admitted = [phase["id"] for obj in packet["objects"] for phase in obj["phases"]]
    withheld = [obj["existing_item_id"] for obj in packet["objects"] if obj["conflict_ids"]]
    require(isinstance(receipt.get("admitted_phase_ids"), list)
            and sorted(receipt["admitted_phase_ids"]) == sorted(admitted), "receipt phase admission differs from packet")
    require(isinstance(receipt.get("withheld_object_ids"), list)
            and sorted(receipt["withheld_object_ids"]) == sorted(withheld), "receipt withheld identities differ from packet")
    require(receipt.get("material_findings") == 0, "receipt has unresolved material findings")
    return packet


if __name__ == "__main__":
    load_accepted_packet()
    print("PASS: accepted finite architecture time packet")
