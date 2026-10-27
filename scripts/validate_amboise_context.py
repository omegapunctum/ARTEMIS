"""Fail-closed validation of the bounded source-relative Amboise packet."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / 'fixtures/amboise_context/v1/packet.json'
DIGEST_PATH = PACKET_PATH.with_suffix('.sha256')
def require(condition, message):
    if not condition:
        raise ValueError(message)
def load_packet(packet_path=PACKET_PATH, digest_path=DIGEST_PATH):
    raw = Path(packet_path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == Path(digest_path).read_text().strip(), 'Amboise packet digest mismatch')
    p = json.loads(raw)
    require(p['schema_version'] == 1 and p['event_id'] == 'event-amboise-dauphin-baptism-1518', 'event identity')
    require(p['residence_ref'] == 'presence-leonardo-amboise-clos-luce-1516-1519', 'residence identity')
    require(p['source_native_date'] == '25 April 1518 (n. st.)' and p['place'] == 'Amboise', 'source date/place')
    require(all(p[k] is None for k in ('canonical_exact_day','geometry','duration')), 'unresolved day/geometry/duration')
    n = p['normalization']
    require(n['policy_id'] == 'amboise-baptism-1518-calendar-year-v1' and n['resolution'] == 'year' and n['year'] == 1518, 'bounded year policy')
    require(n['alternatives'] == [{'interpretation':'Julian','gregorian_date':'1518-05-05'},{'interpretation':'already Gregorian','gregorian_date':'1518-04-25'}], 'calendar alternatives')
    ids = [s['source_id'] for s in p['sources']]
    require(ids == ['bnf-bp16','tours-gaugain','bnf-calendar-manual','observatory-calendar'], 'source identity/uniqueness')
    require(all(s['url'].startswith('https://') and s['locator'] for s in p['sources']), 'source locators')
    require(n['source_ids'] == ['bnf-calendar-manual','observatory-calendar'], 'normalization sources')
    require([c['claim_id'] for c in p['claims']] == ['amboise-event','amboise-date','amboise-date-agreement'], 'claim identity/uniqueness')
    require([c['source_ids'] for c in p['claims']] == [['bnf-bp16','tours-gaugain'],['bnf-bp16'],['tours-gaugain']], 'atomic evidence scope/closure')
    return p
if __name__ == '__main__':
    load_packet()
    print('Amboise packet valid')
