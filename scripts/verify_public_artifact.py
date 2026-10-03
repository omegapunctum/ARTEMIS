#!/usr/bin/env python3
"""Bind a generated public preview to a checked revision and verify its bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


class ArtifactError(ValueError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): digest(path.read_bytes())
        for path in sorted(directory.rglob('*'))
        if path.is_file() and path.relative_to(directory).as_posix() != 'build-meta.json'
    }


def stamp(directory: Path, source_sha: str, run_id: str, attempt: str) -> None:
    if not re.fullmatch(r'[0-9a-f]{40}', source_sha):
        raise ArtifactError('source revision must be a full commit SHA')
    if not run_id.isdecimal() or int(run_id) < 1 or not attempt.isdecimal() or int(attempt) < 1:
        raise ArtifactError('positive workflow run identity and attempt required')
    path = directory / 'build-meta.json'
    metadata = json.loads(path.read_text())
    if metadata.get('public_pages_entrypoint') is not True:
        raise ArtifactError('only registered public previews may receive release identity')
    metadata['release_provenance'] = {
        'source_commit': source_sha,
        'workflow_run_id': run_id,
        'workflow_run_attempt': attempt,
        'file_sha256': manifest(directory),
    }
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')


def verify(directory: Path, expected_sha: str, url: str | None = None) -> dict:
    expected_bytes = (directory / 'build-meta.json').read_bytes()
    metadata = json.loads(expected_bytes)
    provenance = metadata.get('release_provenance', {})
    if provenance.get('source_commit') != expected_sha:
        raise ArtifactError('source revision mismatch')
    files = provenance.get('file_sha256')
    if not isinstance(files, dict) or not files or files != manifest(directory):
        raise ArtifactError('local artifact manifest mismatch')
    if url:
        base = url.rstrip('/')

        def read(relative: str) -> bytes:
            # No user-supplied URL or remote manifest is allowed to select file paths.
            request = Request(
                base + '/' + quote(relative, safe='/') + '?artemis_revision=' + expected_sha,
                headers={'Cache-Control': 'no-cache'},
            )
            with urlopen(request, timeout=30) as response:
                return response.read()

        if read('build-meta.json') != expected_bytes:
            raise ArtifactError('published metadata differs from checked artifact')
        for relative, expected_hash in files.items():
            if digest(read(relative)) != expected_hash:
                raise ArtifactError(f'published artifact hash mismatch: {relative}')
    return {
        'status': 'PASS', 'source_commit': expected_sha,
        'workflow_run_id': provenance['workflow_run_id'],
        'workflow_run_attempt': provenance['workflow_run_attempt'],
        'semantic_dataset': metadata['semantic_dataset'],
        'file_count': len(files), 'verification': 'live' if url else 'local',
        'url': url,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['stamp', 'verify'])
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--source-sha', required=True)
    parser.add_argument('--run-id')
    parser.add_argument('--run-attempt', default='1')
    parser.add_argument('--url')
    args = parser.parse_args()
    try:
        if args.operation == 'stamp':
            actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            if actual != args.source_sha:
                raise ArtifactError('checkout revision differs from requested source revision')
            subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--'], cwd=ROOT, check=True)
            stamp(args.directory, args.source_sha, args.run_id or '', args.run_attempt)
        print(json.dumps(verify(args.directory, args.source_sha, args.url)))
        return 0
    except (ArtifactError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f'[FAIL] {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
