#!/usr/bin/env python3
"""Package an existing checked Explorer build for server-free owner review.

The network build is retained. Sources, engine and application code are copied
unchanged; base64 preserves the exact UTF-8 JSON bytes in inert HTML elements.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

DATA_FILES = ("unified-bundle.json", "earth-context.geojson", "geospatial-assets.json", "build-meta.json")


def package_standalone(build: Path) -> Path:
    html = (build / "index.html").read_text(encoding="utf-8")
    manifest = json.loads((build / "engine/manifest.json").read_text(encoding="utf-8"))
    metadata = json.loads((build / "build-meta.json").read_text(encoding="utf-8"))
    if "release_provenance" in metadata:
        raise ValueError("standalone review requires a separate unstamped build")
    if manifest["engine_id"] != metadata["engine_id"]:
        raise ValueError("engine identity differs from build metadata")
    for name, digest in manifest["sha256"].items():
        if hashlib.sha256((build / "engine" / name).read_bytes()).hexdigest() != digest:
            raise ValueError("engine pin mismatch: " + name)
    if hashlib.sha256((build / "unified-bundle.json").read_bytes()).hexdigest() != metadata["bundle_sha256"]:
        raise ValueError("bundle pin mismatch")

    def inline(match: re.Match, tag: str) -> str:
        url = match.group(1)
        relative, _, query = url.partition("?")
        if not relative.startswith("./") or ".." in Path(relative).parts:
            raise ValueError("only local build assets may be embedded")
        payload = (build / relative[2:]).read_bytes()
        if query != "v=" + hashlib.sha256(payload).hexdigest():
            raise ValueError("resource URL does not bind its actual bytes: " + relative)
        source = payload.decode("utf-8")
        if "</" + tag in source.lower():
            raise ValueError("unsafe raw-text terminator in " + relative)
        return f'<{tag} data-embedded-source="{relative[2:]}">{source}</{tag}>'

    scripts = re.findall(r'<script src="([^"]+)"></script>', html)
    styles = re.findall(r'<link rel="stylesheet" href="([^"]+)">', html)
    if [url.partition("?")[0] for url in scripts] != ["./startup.js", "./engine/maplibre-gl.js", "./mobile.js", "./desktop.js", "./runtime.js"]:
        raise ValueError("required startup scripts or their order differ")
    if [url.partition("?")[0] for url in styles] != ["./engine/maplibre-gl.css", "./style.css"]:
        raise ValueError("required stylesheets or their order differ")
    html = re.sub(r'<link rel="preload"[^>]*>', "", html)
    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', lambda m: inline(m, "style"), html)
    html = re.sub(r'<script src="([^"]+)"></script>', lambda m: inline(m, "script"), html)
    if re.search(r'<script[^>]*\bsrc=|<link[^>]*\b(?:href|rel="preload")=', html):
        raise ValueError("startup resource dependency remains")
    embedded = "".join(
        f'<script type="application/octet-stream" id="embedded-{name}">'
        + base64.b64encode((build / name).read_bytes()).decode("ascii")
        + "</script>" for name in DATA_FILES
    )
    license_text = (build / "engine/LICENSE.txt").read_bytes().decode("utf-8")
    if "</script" in license_text.lower():
        raise ValueError("unsafe license terminator")
    embedded += '<script type="text/plain" id="embedded-engine-license">' + license_text + "</script>"
    marker = '<script data-embedded-source="startup.js">'
    if html.count(marker) != 1:
        raise ValueError("exactly one startup guard is required")
    html = html.replace(marker, embedded + marker, 1)
    html = html.replace("<head>", '<head><meta name="artemis-artifact-role" content="local-review-only">', 1)
    output = build / "ARTEMIS.html"
    output.write_bytes(html.encode("utf-8"))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    args = parser.parse_args()
    print(package_standalone(args.build))
