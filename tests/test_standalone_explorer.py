"""Server-free review preserves checked source bytes and executable order."""
import base64
import json
import re
from html.parser import HTMLParser

import pytest

from scripts import build_unified_explorer as unified
from scripts.package_unified_explorer_standalone import DATA_FILES, package_standalone


class EmbeddedParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = {}
        self.order = []
        self.current = None
        self.external = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "link"} and ("src" in attrs or "href" in attrs):
            self.external.append(attrs)
        key = attrs.get("data-embedded-source") or attrs.get("id")
        if tag in {"script", "style"} and key:
            self.current = key
            self.parts[key] = ""
            self.order.append(key)

    def handle_data(self, data):
        if self.current:
            self.parts[self.current] += data

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.current = None


def test_standalone_preserves_all_payloads_without_startup_urls(tmp_path):
    build = tmp_path / "preview"
    unified.build_unified_explorer(build)
    output = package_standalone(build)
    parser = EmbeddedParser()
    parser.feed(output.read_text())
    assert not parser.external
    for name in DATA_FILES:
        assert base64.b64decode(parser.parts["embedded-" + name]) == (build / name).read_bytes()
    for name in ("startup.js", "engine/maplibre-gl.js", "mobile.js", "desktop.js", "runtime.js", "style.css", "engine/maplibre-gl.css"):
        assert parser.parts[name].encode("utf-8") == (build / name).read_bytes()
    assert parser.parts["embedded-engine-license"].encode("utf-8") == (build / "engine/LICENSE.txt").read_bytes()
    assert [name for name in parser.order if name.endswith(".js")] == ["startup.js", "engine/maplibre-gl.js", "mobile.js", "desktop.js", "runtime.js"]
    assert parser.order.index("embedded-build-meta.json") < parser.order.index("startup.js")
    assert len(json.loads((build / "unified-bundle.json").read_bytes())["registry"]) == 55


@pytest.mark.parametrize("fault", ["runtime", "missing-startup", "release-stamp"])
def test_standalone_rejects_drift_without_replacing_existing_output(tmp_path, fault):
    build = tmp_path / "preview"
    unified.build_unified_explorer(build)
    output = build / "ARTEMIS.html"
    output.write_text("keep current artifact")
    if fault == "runtime":
        (build / "runtime.js").write_text("changed runtime")
        message = "resource URL does not bind"
    elif fault == "missing-startup":
        index = build / "index.html"
        index.write_text(re.sub(r'<script src="\./startup.js[^\"]*"></script>', '', index.read_text()))
        message = "required startup scripts"
    else:
        path = build / "build-meta.json"
        metadata = json.loads(path.read_text())
        metadata["release_provenance"] = {"source_sha": "release"}
        path.write_text(json.dumps(metadata))
        message = "separate unstamped build"
    with pytest.raises(ValueError, match=message):
        package_standalone(build)
    assert output.read_text() == "keep current artifact"
