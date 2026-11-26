"""Write the two offline Chartres pilot projections into the supplied directory."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "fixtures/chartres_export/v1/claims.json"


def export(output):
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    subject, claims = packet["subject"], packet["claims"]
    ids = [claim["id"] for claim in claims]
    if len(ids) != 6 or len(set(ids)) != len(ids):
        raise ValueError("Expected six distinct Chartres claims")
    feature = {
        "type": "Feature",
        "id": subject["id"],
        "geometry": {"type": "Point", "coordinates": subject["modern_reference_point"]},
        "properties": {"label": subject["label"], "location_role": "modern_reference", "claims": claims},
    }
    timeline = {"subject_id": subject["id"], "label": subject["label"], "entries": claims}
    output.mkdir(parents=True, exist_ok=True)
    for name, projection in [("chartres.geojson", feature), ("chartres-timeline.json", timeline)]:
        (output / name).write_text(json.dumps(projection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    export(parser.parse_args().output)
