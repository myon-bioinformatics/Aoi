"""nagoyaction/containers/llama.py（#48 で消えた NagoyAction/containers/llama.py を復元）。ネットワークは使わない。"""
import hashlib
import importlib.util
import io
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / "containers/llama.py"
IMAGE = "ghcr.io/ggml-org/llama.cpp:server@sha256:" + "a" * 64


def load(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("aoi_llama", PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "MODEL", tmp_path / ".models/model.gguf")
    return module


@pytest.mark.parametrize("image", ["", "ghcr.io/ggml-org/llama.cpp:server", "docker.io/other/llama.cpp@sha256:" + "a" * 64])
def test_image_must_be_the_official_digest_pinned_server(tmp_path, monkeypatch, image):
    llama = load(tmp_path, monkeypatch)
    monkeypatch.setenv("AOI_LLAMA_IMAGE", image)
    with pytest.raises(ValueError, match="digest"):
        llama.prepare()


@pytest.mark.parametrize("url,sha", [("http://example.invalid/m.gguf", "b" * 64), ("https://example.invalid/m.gguf", "xyz")])
def test_model_needs_https_and_sha256(tmp_path, monkeypatch, url, sha):
    llama = load(tmp_path, monkeypatch)
    monkeypatch.setenv("AOI_LLAMA_IMAGE", IMAGE)
    monkeypatch.setenv("AOI_LLAMA_MODEL_URL", url)
    monkeypatch.setenv("AOI_LLAMA_MODEL_SHA256", sha)
    with pytest.raises(ValueError, match="SHA-256"):
        llama.prepare()


def test_download_is_verified_before_it_replaces_the_model(tmp_path, monkeypatch):
    llama = load(tmp_path, monkeypatch)
    body = b"model-bytes"
    monkeypatch.setenv("AOI_LLAMA_IMAGE", IMAGE)
    monkeypatch.setenv("AOI_LLAMA_MODEL_URL", "https://example.invalid/m.gguf")
    monkeypatch.setenv("AOI_LLAMA_MODEL_SHA256", hashlib.sha256(b"other").hexdigest())
    monkeypatch.setattr(llama.urllib.request, "urlopen", lambda url, timeout: io.BytesIO(body))
    with pytest.raises(ValueError, match="一致しません"):
        llama.prepare()
    assert not llama.MODEL.exists() and not llama.MODEL.with_suffix(".tmp").exists()
    monkeypatch.setenv("AOI_LLAMA_MODEL_SHA256", hashlib.sha256(body).hexdigest())
    llama.prepare()
    assert llama.MODEL.read_bytes() == body
    assert '"model_sha256"' in (llama.MODEL.parent / "identity.json").read_text()
