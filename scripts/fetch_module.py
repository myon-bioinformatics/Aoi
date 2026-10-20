#!/usr/bin/env python3
"""CDN のように、pure-Python の配布物を pip/uv なしで取って import する（実験）。

標準ライブラリだけで動く。PyPI JSON API で最新版（または --version）の
``py3-none-any`` wheel を選び、PyPI が公開する sha256 を照合してキャッシュに置く。
pure-Python の wheel は zip のまま ``sys.path`` に載せれば import できる。

    python scripts/fetch_module.py resolve markdown            # version と sha256 を表示
    python scripts/fetch_module.py fetch markdown --cache .cdn  # wheel のパスを表示
    PYTHONPATH="$(python scripts/fetch_module.py fetch markdown --cache .cdn)" python -c 'import markdown'

ワンライナー（sha256 照合つき）:

    python -c "import json,hashlib,urllib.request as u;f=[x for x in json.load(u.urlopen('https://pypi.org/pypi/markdown/json'))['urls'] if x['filename'].endswith('py3-none-any.whl')][0];b=u.urlopen(f['url']).read();assert hashlib.sha256(b).hexdigest()==f['digests']['sha256'];open(f['filename'],'wb').write(b);print(f['filename'])"

制限: compiled な wheel（selectolax など）と、extra 以外の依存（requires_dist）を持つ
配布物は既定で拒否する。依存の解決はしない。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

INDEX = os.environ.get("FETCH_MODULE_INDEX", "https://pypi.org/pypi")
PURE = re.compile(r"-py3-none-any\.whl$|-py2\.py3-none-any\.whl$")


def _get(url: str) -> bytes:
    if not url.startswith("https://"):
        raise ValueError(f"https 以外は取らない: {url}")
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def runtime_requirements(info: dict) -> list[str]:
    """extra を条件にしない依存。あれば推移的な依存が要る。"""
    return [r for r in (info.get("requires_dist") or []) if "extra ==" not in r.replace("extra==", "extra ==")]


def resolve(package: str, version: str | None = None, *, allow_deps: bool = False) -> dict:
    path = f"{package}/{version}/json" if version else f"{package}/json"
    meta = json.loads(_get(f"{INDEX}/{path}"))
    info = meta["info"]
    deps = runtime_requirements(info)
    if deps and not allow_deps:
        raise SystemExit(f"{package} {info['version']} は実行時の依存を持つ（未対応）: {deps}")
    wheels = [f for f in meta["urls"] if f["packagetype"] == "bdist_wheel" and PURE.search(f["filename"])]
    if not wheels:
        raise SystemExit(f"{package} {info['version']} に pure-Python の wheel がない（compiled は未対応）")
    f = wheels[0]
    return {"package": package, "version": info["version"], "filename": f["filename"],
            "url": f["url"], "sha256": f["digests"]["sha256"]}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(spec: dict, cache: Path) -> Path:
    """キャッシュにあり sha256 が合えばそれを使い、なければ取って照合する。"""
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / spec["filename"]
    if dest.exists() and _sha256(dest) == spec["sha256"]:
        return dest
    data = _get(spec["url"])
    got = hashlib.sha256(data).hexdigest()
    if got != spec["sha256"]:
        raise SystemExit(f"sha256 が一致しない: {spec['filename']} {got} != {spec['sha256']}")
    tmp = dest.with_suffix(".part")
    tmp.write_bytes(data)
    tmp.replace(dest)
    return dest


def extract(wheel: Path, out: Path) -> Path:
    """wheel から import に要るファイルだけ（*.dist-info を除く）を out に展開する。"""
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            top = name.split("/", 1)[0]
            if top.endswith((".dist-info", ".data")) or ".." in name.split("/"):
                continue
            z.extract(name, out)
    return out


def ensure(package: str, cache: str | os.PathLike = ".cdn-cache", version: str | None = None):
    """取ってきた wheel を sys.path の先頭に置いて import する。"""
    import importlib
    wheel = fetch(resolve(package, version), Path(cache))
    sys.path.insert(0, str(wheel))
    return importlib.import_module(package)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("command", choices=["resolve", "fetch"])
    p.add_argument("package")
    p.add_argument("--version")
    p.add_argument("--cache", default=".cdn-cache")
    p.add_argument("--extract", help="wheel を zip のまま使わず、このディレクトリに展開する")
    p.add_argument("--github-output", action="store_true", help="resolve の結果を $GITHUB_OUTPUT に書く")
    a = p.parse_args(argv)
    spec = resolve(a.package, a.version)
    if a.command == "resolve":
        if a.github_output:
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
                for k in ("version", "filename", "sha256"):
                    fh.write(f"{k}={spec[k]}\n")
        print(json.dumps(spec, indent=1))
        return 0
    wheel = fetch(spec, Path(a.cache))
    print(extract(wheel, Path(a.extract)) if a.extract else wheel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
