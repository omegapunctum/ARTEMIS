"""Admission boundary for the separately reviewed temporal assertions."""
import copy
import json

import pytest

from scripts import validate_architecture_time_pilot as temporal


def packet():
    return json.loads(temporal.PACKET_PATH.read_bytes())


def test_accepted_packet_preserves_source_relative_and_withheld_states():
    value = temporal.load_accepted_packet()
    assert value == packet()
    assert value['status'] == 'proposed'
    assert all(c['confidence'] is None for c in value['claims'])
    assert len([o for o in value['objects'] if o['phases']]) == 2
    withheld = next(o for o in value['objects'] if o['conflict_ids'])
    assert withheld['existing_item_id'] == 'catalog:wikidata:Q642039'
    assert withheld['phases'] == []
    assert len(withheld['withheld_phases']) == 2


@pytest.mark.parametrize('mutation', [
    lambda p: p['objects'][0].update(existing_item_id='invented'),
    lambda p: p['objects'][0].update(historical_geometry={'type': 'Point'}),
    lambda p: p['objects'][0]['phases'][0].update(interval=[1885,1894]),
    lambda p: p['objects'][0]['phases'][0].update(interval=[1886,None]),
    lambda p: p['objects'][0]['phases'][0].update(precision='day'),
    lambda p: p['objects'][0]['phases'][0].update(basis_claim_ids=['missing']),
    lambda p: p['objects'][0]['phases'][0].update(basis_claim_ids=['c:monument-start']),
    lambda p: p['objects'][1].update(phases=[copy.deepcopy(p['objects'][0]['phases'][0])]),
    lambda p: p['objects'][2]['phases'][1].update(inference_ids=[]),
    lambda p: p['objects'][2]['phases'][1].update(support='source_reported',inference_ids=[]),
    lambda p: p['claims'][0]['time'].update(value='1886-04-31'),
    lambda p: p['claims'][0].update(confidence='high'),
    lambda p: p['claims'][0]['time'].update(precision='year'),
    lambda p: p['evidence_links'][0].update(locator=''),
    lambda p: p['conflicts'][0].update(status='resolved'),
])
def test_unsupported_projection_fails_closed(mutation):
    value = packet()
    mutation(value)
    with pytest.raises(temporal.ArchitectureTimeError):
        temporal.validate_packet(value)


def test_registry_identity_and_exact_review_bytes_are_required(tmp_path, monkeypatch):
    with pytest.raises(temporal.ArchitectureTimeError, match='absent'):
        temporal.load_accepted_packet(set())
    altered = tmp_path / 'evidence.json'
    altered.write_bytes(temporal.PACKET_PATH.read_bytes() + b'\n')
    monkeypatch.setattr(temporal, 'PACKET_PATH', altered)
    with pytest.raises(temporal.ArchitectureTimeError, match='reviewed bytes'):
        temporal.load_accepted_packet()


@pytest.mark.parametrize('field,value', [('admitted_phase_ids', []), ('withheld_object_ids', []), ('material_findings', 1), ('status','pending')])
def test_review_receipt_cannot_admit_different_phases(tmp_path, monkeypatch, field, value):
    receipt = json.loads(temporal.ACCEPTANCE_PATH.read_bytes())
    receipt[field] = value
    altered = tmp_path / 'acceptance.json'
    altered.write_text(json.dumps(receipt))
    monkeypatch.setattr(temporal, 'ACCEPTANCE_PATH', altered)
    with pytest.raises(temporal.ArchitectureTimeError):
        temporal.load_accepted_packet()
