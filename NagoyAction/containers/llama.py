"""NagoyAction hooks: verified model acquisition and loopback readiness.

Docker lifecycle is declared in pipelines/inbox.toml and llama.compose.yml.
Only administrator configuration supplies image/model locations, never comments.
"""
import argparse
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / ".models/model.gguf"


def sha256(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def prepare():
    image = os.environ.get("AOI_LLAMA_IMAGE", "")
    expected = os.environ.get("AOI_LLAMA_MODEL_SHA256", "")
    url = os.environ.get("AOI_LLAMA_MODEL_URL", "")
    if not re.fullmatch(r"ghcr\.io/ggml-org/llama\.cpp(?::[a-zA-Z0-9_.-]+)?@sha256:[a-f0-9]{64}", image):
        raise ValueError("AOI_LLAMA_IMAGE は公式serverイメージをdigest固定してください")
    if not re.fullmatch(r"[a-f0-9]{64}", expected) or urllib.parse.urlsplit(url).scheme != "https":
        raise ValueError("モデルのHTTPS URLとSHA-256が必要")
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    if not MODEL.exists() or sha256(MODEL) != expected:
        temp = MODEL.with_suffix(".tmp")
        try:
            with urllib.request.urlopen(url, timeout=60) as response, temp.open("wb") as out:
                total = 0
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > 4 * 1024**3:
                        raise ValueError("CPU受付用モデルは4GiB以下")
                    out.write(chunk)
            if sha256(temp) != expected:
                raise ValueError("モデルのSHA-256が一致しません")
            temp.replace(MODEL)
        finally:
            temp.unlink(missing_ok=True)
    (MODEL.parent / "identity.json").write_text(json.dumps({"image": image, "model_sha256": expected}) + "\n")


def wait_ready():
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=5) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(1)
    raise TimeoutError("llama.cppが180秒以内に起動しませんでした")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=("prepare", "wait"))
    args = ap.parse_args(argv)
    (prepare if args.action == "prepare" else wait_ready)()


if __name__ == "__main__":
    main()
