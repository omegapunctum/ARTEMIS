#!/usr/bin/env python3
"""Bounded, deterministic Cliopatria excerpt verification and World Model mapping.

No downloading, border repair, resampling, interpolation or generic ingestion API.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'fixtures/world_slices/roman_empire_region/v1'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def extract(archive: Path, manifest: dict):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest['archive_sha256']:
        raise ValueError('upstream archive checksum mismatch')
    with zipfile.ZipFile(archive) as z:
        data = json.loads(z.read(manifest['member']))
    features = [data['features'][row['feature_index']] for row in manifest['selection']]
    verify(features, manifest)
    return {'type': 'FeatureCollection', 'features': features}


def verify(features, manifest):
    if not 3 <= len(features) <= 5 or len(features) != len(manifest['selection']):
        raise ValueError('bounded proof requires 3–5 audited states')
    previous = None
    for f, row in zip(features, manifest['selection']):
        p = f['properties']
        if digest(f) != row['feature_sha256']:
            raise ValueError('source feature checksum mismatch')
        if (p['Name'], p['Type'], p['Wikidata'], p['SeshatID']) != (
            'Roman Empire', 'POLITY', 'Q12544', 'it_roman_principate'
        ):
            raise ValueError('source identity/comparability mismatch')
        start, end = p['FromYear'], p['ToYear']
        if type(start) is not int or type(end) is not int or start < 1 or start > end:
            raise ValueError('invalid native CE year interval')
        if (start, end) != (row['from_year'], row['to_year']):
            raise ValueError('native interval mismatch')
        if previous is not None and start <= previous:
            raise ValueError('overlapping or unordered intervals')
        previous = end
        g = f['geometry']
        if g['type'] not in ('Polygon', 'MultiPolygon'):
            raise ValueError('Region needs polygon geometry')
        polygons = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        if not polygons:
            raise ValueError('empty geometry')
        for polygon in polygons:
            if not polygon:
                raise ValueError('empty polygon')
            for ring in polygon:
                if len(ring) < 4 or ring[0] != ring[-1]:
                    raise ValueError('unclosed polygon ring')
                for point in ring:
                    if len(point) != 2 or not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90):
                        raise ValueError('invalid longitude/latitude')


def build_inputs():
    manifest = json.loads((PACKAGE / 'source_manifest.json').read_text())
    features = json.loads((PACKAGE / 'sources/cliopatria-excerpt.json').read_text())['features']
    verify(features, manifest)
    source_id, entity_id, region_id = 'source-cliopatria', 'entity-roman-empire', 'region-roman-empire'
    layer_id, uncertainty_id = 'layer-political-territory', 'uncertainty-cliopatria-reconstruction'
    limits = ('Source reconstruction, not exact historical borders. Native inclusive year intervals; '
              'no day precision or interpolation. Coarse raster-derived, smoothed boundaries; '
              'coastline misalignment and unencoded disputes remain. Only three selected states; '
              'missing coverage is not historical absence. Formal user value UNVALIDATED.')
    world = {
        'schema_version': '1.0.0', 'package_id': 'roman-empire-region-proof-v1',
        'fixture_mode': 'historical_fixture', 'status': 'REVIEW_REQUIRED',
        'historical_corpus_ready': False, 'promotion_allowed': False,
        'corpus_status': limits,
        'world_slice': {
            'id': 'world-slice-roman-region-v1', 'type': 'WorldSlice',
            'label': 'Roman Empire: three source reconstructions', 'version': 1,
            'selection_rationale': 'A source-first, bounded universality proof selects three adjacent Cliopatria snapshots with one political identity and native year precision.',
            'temporal_bounds': {'kind': 'closed_interval', 'start': '0091', 'end': '0116', 'precision': 'year', 'calendar': 'proleptic_gregorian', 'certainty': 'approximate', 'basis_claim_refs': []},
            'spatial_bounds': {'kind': 'composite_scope', 'region_refs': ['region-roman-empire'], 'precision': 'source_reconstruction', 'basis_claim_refs': []},
            'included_layer_refs': [layer_id], 'uncertainty_refs': [uncertainty_id],
            'dataset_identity': {'kind': 'fixture_package', 'value': 'roman-empire-region-proof-v1@1.0.0'},
            'coverage_manifest_ref': 'coverage_manifest.json',
            'coverage_policy': {'corpus_completeness': 'explicitly_incomplete', 'absence_semantics': 'not_historical_absence', 'source_scope': 'published_reconstruction_only', 'known_exclusion_ids': ['unselected-cliopatria-snapshots', 'unsupported-border-interpolation', 'contextual-roman-history']},
        },
        'layers': [{'id': layer_id, 'type': 'Layer', 'label': 'Political territory reconstruction', 'claim_refs': [], 'uncertainty_refs': [uncertainty_id]}],
        'entities': [{'id': entity_id, 'type': 'Entity', 'entity_kind': 'Polity', 'label': 'Roman Empire',
                      'claim_refs': [], 'uncertainty_refs': [uncertainty_id], 'layer_refs': [layer_id]}],
        'regions': [], 'states': [], 'places': [], 'events': [], 'processes': [], 'trajectories': [],
        'relations': [], 'derived_observations': [], 'claims': [], 'evidence_links': [],
        'sources': [{'id': source_id, 'type': 'Source', 'title': manifest['attribution'],
                     'source_type': 'published_geospatial_reconstruction',
                     'uri': 'sources/cliopatria-excerpt.json',
                     'sha256': hashlib.sha256((PACKAGE/'sources/cliopatria-excerpt.json').read_bytes()).hexdigest(),
                     'review_state': 'draft', 'provenance': manifest}],
        'uncertainties': [{'id': uncertainty_id, 'type': 'Uncertainty', 'subject_or_claim_ref': region_id,
                          'dimension': 'spatial_temporal_reconstruction', 'description': limits,
                          'effect': 'Show reconstruction limits with the selected geometry; never interpolate outside source intervals.',
                          'effect_policy': 'prohibit_historical_absence_inference', 'alternatives': [], 'basis_claim_refs': [], 'review_state': 'draft'}],
    }
    versions, presets = [], []
    for f, row in zip(features, manifest['selection']):
        start, end = row['from_year'], row['to_year']
        suffix = f'{start}-{end}'
        claim_id, version_id = f'claim-region-{suffix}', f'region-geometry-{suffix}'
        extent = {'kind': 'closed_interval', 'start': f'{start:04d}', 'end': f'{end:04d}',
                  'precision': 'year', 'calendar': 'proleptic_gregorian', 'certainty': 'approximate', 'basis_claim_refs': [claim_id]}
        spatial = {'kind': f['geometry']['type'].lower(), 'geometry': f['geometry'],
                   'precision': 'source_reconstruction', 'basis_claim_refs': [claim_id]}
        versions.append({'id': version_id, 'reconstruction_mode': 'scholarly_reconstruction', 'is_primary': True,
                         'temporal_extent': extent, 'spatial_extent': spatial, 'claim_refs': [claim_id], 'uncertainty_refs': [uncertainty_id]})
        world['states'].append({'id': f'state-territory-{suffix}', 'type': 'State', 'label': f'Territory reconstruction {start}–{end} CE',
                                'subject_ref': entity_id, 'state_kind': 'administration', 'value': version_id,
                                'temporal_extent': extent, 'spatial_extent': {'kind': 'region_ref', 'region_ref': region_id,
                                'precision': 'versioned_reconstruction', 'basis_claim_refs': [claim_id]},
                                'claim_refs': [claim_id], 'uncertainty_refs': [uncertainty_id], 'layer_refs': [layer_id]})
        world['claims'].append({'id': claim_id, 'type': 'Claim', 'statement': f'Cliopatria reconstructs Roman Empire territory for the inclusive source interval {start}–{end} CE. {limits}',
                                'target_refs': [entity_id, region_id, version_id], 'claim_kind': 'interpretation',
                                'origin': 'imported', 'review_state': 'draft', 'confidence': 'unknown', 'evidence_state': 'supported', 'uncertainty_refs': [uncertainty_id]})
        world['entities'][0]['claim_refs'].append(claim_id)
        world['evidence_links'].append({'id': f'evidence-region-{suffix}', 'type': 'EvidenceLink', 'claim_id': claim_id,
                                        'source_id': source_id, 'locator': f"{manifest['repository']}/blob/{manifest['commit']}/{manifest['archive']} :: {manifest['member']} /features/{row['feature_index']} :: {manifest['license']} :: unchanged geometry; source_manifest.json",
                                        'relation_to_claim': 'supports', 'evidence_strength': 'direct', 'review_state': 'draft'})
        presets.append({'preset_id': f'year-{start}', 'label': f'{start} CE · source interval {start}–{end} CE',
                        'temporal_selection': {'mode': 'instant', 'start': f'{start:04d}', 'end': f'{start:04d}', 'precision': 'year', 'calendar': 'proleptic_gregorian'}})
    world['regions'] = [{'id': region_id, 'type': 'Region', 'label': 'Roman Empire territory (reconstruction)', 'region_kind': 'political_territory',
                         'geometry_versions': versions, 'claim_refs': [c['id'] for c in world['claims']], 'uncertainty_refs': [uncertainty_id], 'layer_refs': [layer_id]}]
    state = {'schema_version': '1.0.0', 'state_id': 'explorer-state-region-proof', 'world_slice_ref': world['world_slice']['id'],
             'dataset_identity': {'kind': 'fixture_package', 'value': world['package_id']},
             'temporal_selection': presets[0]['temporal_selection'], 'active_layer_refs': [layer_id],
             'selection': {'primary_object_ref': region_id, 'selected_object_refs': [region_id], 'comparison_object_refs': []},
             'context': {'local_context_refs': [region_id], 'global_context_refs': [], 'derived_observation_refs': []},
             'active_focus': {'trajectory_ref': None, 'trajectory_segment_ref': None, 'region_ref': region_id, 'region_geometry_ref': None, 'reconstruction_ref': None},
             'comparison_scope': {'mode': 'none', 'reference_refs': []},
             'epistemic_display': {'show_material_uncertainty': True, 'show_alternatives': True, 'show_corpus_limits': True},
             'view_intent': {'kind': 'bounds', 'bbox': [-12, 20, 48, 60], 'target_ref': region_id, 'coordinate_reference': 'EPSG:4326'}}
    world["world_slice"]["dataset_identity"] = state["dataset_identity"]
    return world, state, presets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-upstream', type=Path, help='verify pinned archive and exact checked-in excerpt')
    parser.add_argument('--verify-excerpt', action='store_true', help='verify the checked-in excerpt against its pinned feature digests')
    args = parser.parse_args()
    if args.verify_upstream:
        manifest = json.loads((PACKAGE/'source_manifest.json').read_text())
        actual = extract(args.verify_upstream, manifest)
        expected = json.loads((PACKAGE/'sources/cliopatria-excerpt.json').read_text())
        if actual != expected:
            raise ValueError('checked-in excerpt differs from pinned upstream extraction')
    if args.verify_excerpt:
        manifest = json.loads((PACKAGE/'source_manifest.json').read_text())
        features = json.loads((PACKAGE/'sources/cliopatria-excerpt.json').read_text())['features']
        verify(features, manifest)
    world, _, _ = build_inputs()
    print(f"PASS: {len(world['regions'][0]['geometry_versions'])} unchanged source states mapped to one Region")


if __name__ == '__main__':
    main()
