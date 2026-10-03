"""Release evidence rejects wrong revisions and changed bytes, locally and over HTTP."""

import functools
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import pytest

from scripts.verify_public_artifact import ArtifactError, stamp, verify


SHA = 'a' * 40


@pytest.fixture
def artifact(tmp_path):
    (tmp_path / 'build-meta.json').write_text(json.dumps({
        'semantic_dataset': 'roman_region_proof', 'public_pages_entrypoint': True,
    }))
    (tmp_path / 'index.html').write_text('source-aware preview')
    stamp(tmp_path, SHA, '123', '1')
    return tmp_path


def test_revision_and_local_file_tampering_fail(artifact):
    assert verify(artifact, SHA)['verification'] == 'local'
    with pytest.raises(ArtifactError, match='revision mismatch'):
        verify(artifact, 'b' * 40)
    (artifact / 'index.html').write_text('changed')
    with pytest.raises(ArtifactError, match='manifest mismatch'):
        verify(artifact, SHA)


def test_non_public_proof_cannot_receive_release_identity(tmp_path):
    (tmp_path / 'build-meta.json').write_text('{"public_pages_entrypoint": false}')
    with pytest.raises(ArtifactError, match='only registered public'):
        stamp(tmp_path, SHA, '123', '1')


def test_live_verification_rejects_changed_published_bytes(artifact, tmp_path_factory):
    import shutil

    remote = tmp_path_factory.mktemp('remote') / 'served'
    shutil.copytree(artifact, remote)
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(remote))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f'http://127.0.0.1:{server.server_port}'
        assert verify(artifact, SHA, url)['verification'] == 'live'
        (remote / 'index.html').write_text('wrong deployment')
        with pytest.raises(ArtifactError, match='published artifact hash mismatch'):
            verify(artifact, SHA, url)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
