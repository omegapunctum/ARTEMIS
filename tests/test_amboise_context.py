import hashlib
import json
import subprocess
import pytest
from scripts import validate_amboise_context as amboise

def test_packet_and_calendar():
    p=amboise.load_packet()
    def jdn(y,m,d,gregorian):
        a=(14-m)//12;y=y+4800-a;m=m+12*a-3
        return d+(153*m+2)//5+365*y+y//4+(-(y//100)+y//400-32045 if gregorian else -32083)
    # Independently derived leap-century offset: 1500/100 - 1500/400 - 2 = 10.
    assert 1500//100-1500//400-2 == 10
    assert jdn(1518,4,25,False) == jdn(1518,5,5,True)
    assert p['canonical_exact_day'] is None

@pytest.mark.parametrize('field,value',[('canonical_exact_day','1518-04-25'),('geometry',{'type':'Point'}),('source_native_date','25 April 1518')])
def test_rehashed_semantic_mutation(tmp_path,field,value):
    p=amboise.load_packet();p[field]=value
    raw=json.dumps(p).encode();path=tmp_path/'packet.json';path.write_bytes(raw)
    digest=tmp_path/'packet.sha256';digest.write_text(hashlib.sha256(raw).hexdigest())
    with pytest.raises(ValueError):amboise.load_packet(path,digest)

def test_digest(tmp_path):
    path=tmp_path/'packet.json';path.write_bytes(amboise.PACKET_PATH.read_bytes()+b' ')
    with pytest.raises(ValueError):amboise.load_packet(path)

def test_year_query():
    subprocess.run(['node','tests/amboise_context_behavior.cjs'],cwd=amboise.ROOT,check=True)
