import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_module as fm  # noqa: E402


def _wheel() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("cdnfake/__init__.py", "VALUE = 42\n")
        z.writestr("cdnfake-1.0.dist-info/METADATA", "Name: cdnfake\n")
    return buf.getvalue()


def _serve(monkeypatch, wheel, sha=None, requires=None, filename="cdnfake-1.0-py3-none-any.whl"):
    meta = {"info": {"version": "1.0", "requires_dist": requires},
            "urls": [{"packagetype": "bdist_wheel", "filename": filename, "url": "https://files.example/w.whl",
                      "digests": {"sha256": sha or hashlib.sha256(wheel).hexdigest()}}]}
    calls = []

    def get(url):
        calls.append(url)
        return json.dumps(meta).encode() if url.endswith("/json") else wheel
    monkeypatch.setattr(fm, "_get", get)
    return calls


def test_fetch_verifies_caches_and_imports(monkeypatch, tmp_path):
    wheel = _wheel()
    calls = _serve(monkeypatch, wheel, requires=['pytest; extra == "testing"'])
    mod = fm.ensure("cdnfake", tmp_path)
    assert mod.VALUE == 42 and ".whl" in mod.__file__
    spec = fm.resolve("cdnfake")
    fm.fetch(spec, tmp_path)
    assert sum(not c.endswith("/json") for c in calls) == 1  # 2回目はキャッシュ
    out = fm.extract(tmp_path / spec["filename"], tmp_path / "x")
    assert (out / "cdnfake" / "__init__.py").exists() and not list(out.glob("*.dist-info"))
    sys.modules.pop("cdnfake", None)


def test_rejects_bad_hash_compiled_and_runtime_deps(monkeypatch, tmp_path):
    _serve(monkeypatch, _wheel(), sha="0" * 64)
    with pytest.raises(SystemExit, match="sha256"):
        fm.fetch(fm.resolve("cdnfake"), tmp_path)
    _serve(monkeypatch, _wheel(), filename="cdnfake-1.0-cp312-cp312-manylinux_2_17_x86_64.whl")
    with pytest.raises(SystemExit, match="pure-Python"):
        fm.resolve("cdnfake")
    _serve(monkeypatch, _wheel(), requires=["pluggy>=1"])
    with pytest.raises(SystemExit, match="依存"):
        fm.resolve("cdnfake")


def test_only_https():
    with pytest.raises(ValueError):
        fm._get("http://pypi.org/pypi/markdown/json")
