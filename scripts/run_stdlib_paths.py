#!/usr/bin/env python3
"""render_md と load_overlap を、入っている numpy か numpy_min で動かし、同じ JSON を書く（実験）。

    python scripts/run_stdlib_paths.py --deps real reference.json
    python scripts/run_stdlib_paths.py --deps min  minimal.json

--deps real は pip/uv で入った numpy を使う。
--deps min は numpy が入っていないときだけ動く。vendor/aoi の numpy_min.py を sys.modules['numpy'] に、
overlap も兄弟の rule_search も import するより前に置く。polars はそのまま使う。
render_md はどちらも自作の markdown.py（vendor/markdown）なので、標準ライブラリだけで同じものになる。

AOI_ROOT は Aoi の checkout（cycles/ があること）。rule_search（PythDRagoras）の場所は Aoi の aoi.py が入れる:
    eval "$(python /path/to/Aoi/aoi.py)"   # AOI_ROOT と兄弟の path（このシェルだけ）
本番の import は変えない。
"""
from __future__ import annotations

import argparse, hashlib, importlib.machinery, importlib.util, json, os, sys, types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = "| a | b |\n|---|---|\n| 1 | 2 |\n\n```\ncode\n```\n\nText\n{: .provenance}\n"
PAGES = ("README.md", "docs/figures.md")


def _register_dragowing(root: Path) -> None:
    """このディレクトリをパッケージ dragowing として登録する（conftest と同じ）。"""
    existing = sys.modules.get("dragowing")
    if existing is not None:
        locations = getattr(existing, "__path__", None) or []
        if any(Path(path).resolve() == root for path in locations):
            return
    pkg = types.ModuleType("dragowing")
    pkg.__path__ = [str(root)]
    pkg.__package__ = "dragowing"
    spec = importlib.machinery.ModuleSpec("dragowing", loader=None, is_package=True)
    spec.submodule_search_locations = pkg.__path__
    pkg.__spec__ = spec
    sys.modules["dragowing"] = pkg


def _require_absent(names: tuple[str, ...]) -> None:
    present = [name for name in names if importlib.util.find_spec(name) is not None]
    if present:
        raise SystemExit(f"入っている: {', '.join(present)}。--deps min は外してから動かす")


def _load_py(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"読めない: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _entry_rel(entry: dict) -> str:
    """写しの相対パス。古い lock は path、driver の lock は source。"""
    if isinstance(entry.get("path"), str):
        return entry["path"]
    source = entry.get("source")
    if isinstance(source, str):
        return source
    raise SystemExit("vendor.lock.json の path がない")


def _vendored(name: str) -> Path:
    """vendor.lock.json の path を vendor/aoi の下で開く。"""
    document = json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))
    matches = [_entry_rel(entry) for entry in document["files"] if Path(_entry_rel(entry)).name == name]
    if len(matches) != 1:
        raise SystemExit(f"vendor.lock.json に {name} が一つない")
    rel = Path(matches[0])
    if rel.is_absolute() or ".." in rel.parts:
        raise SystemExit(f"vendor.lock.json の path が相対パスでない: {matches[0]}")
    return ROOT / "vendor" / "aoi" / rel


def _preload_numpy_min():
    """rule_search の `import numpy` が最小版を見るように、先に載せる。"""
    if "rule_search" in sys.modules or "dragowing.overlap" in sys.modules:
        raise SystemExit("numpy_min を載せる前に overlap か rule_search が import されている")
    # This path is the stdlib substitute, not an opt-in native backend.
    # Called during single-threaded CLI startup, before overlap/rule_search.
    # Restrict only module initialization, then restore the caller environment.
    previous = os.environ.get("NUMPY_MIN_PURE")
    os.environ["NUMPY_MIN_PURE"] = "1"
    try:
        module = _load_py("numpy", _vendored("numpy_min.py"))
    finally:
        if previous is None:
            os.environ.pop("NUMPY_MIN_PURE", None)
        else:
            os.environ["NUMPY_MIN_PURE"] = previous
    if not Path(module.__file__ or "").name == "numpy_min.py":
        raise SystemExit(f"numpy_min ではない: {module.__file__}")
    return module


def _prepare(deps: str):
    if deps == "min":
        _require_absent(("numpy",))
        return _preload_numpy_min()
    import numpy

    numpy_origin = Path(getattr(numpy, "__file__", "") or "").as_posix()
    if numpy_origin.endswith("/numpy_min.py"):
        raise SystemExit(f"インストールされた numpy ではない: {numpy_origin}")
    return numpy


def _results_dir() -> Path:
    value = os.environ.get("AOI_ROOT")
    if not value:
        raise SystemExit("AOI_ROOT=<Aoi のルート> を渡す（.github/workflows/ci.yml と同じ）")
    out = Path(value).expanduser().resolve() / "cycles" / "c001-chunichi" / "outputs"
    if not (out / "season.jsonl").is_file() or not (out / "propositions.jsonl").is_file():
        raise SystemExit(f"c001 の結果が無い: {out}")
    return out


def run(deps: str) -> dict:
    numpy = _prepare(deps)
    _register_dragowing(ROOT)
    from dragowing.dragowing import render_md
    from dragowing.overlap import default_conditions, load_overlap
    from dragowing.dragowing import read_jsonl

    if "rule_search" in sys.modules:
        raise SystemExit("rule_search が overlap の読み込みで import されている")
    sample = render_md(SAMPLE)
    if "<table>" not in sample or "<pre><code>" not in sample or 'class="provenance"' not in sample:
        raise SystemExit(f"sample の HTML が想定と違う: {sample}")
    pages = {}
    for name in PAGES:
        html = render_md((ROOT / name).read_text(encoding="utf-8"))
        if "<h1" not in html:
            raise SystemExit(f"{name} の HTML に見出しが無い")
        pages[name] = html
    if "rule_search" in sys.modules:
        raise SystemExit("render_md が rule_search を import した")

    results = _results_dir()
    rows = read_jsonl(results / "season.jsonl")
    items = read_jsonl(results / "propositions.jsonl")
    conds = default_conditions(items, rows)
    overlap = load_overlap(results / "season.jsonl", conds)
    if sys.modules["rule_search"].np is not numpy or sys.modules["numpy"] is not numpy:
        raise SystemExit("load_overlap の途中で numpy が入れ替わった")
    return {
        "sample_html": sample,
        "pages": pages,
        "overlap": overlap,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--deps", choices=("real", "min"), required=True)
    parser.add_argument("out")
    args = parser.parse_args(argv)
    payload = run(args.deps)
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    regions = payload["overlap"]["regions"]
    numpy = sys.modules["numpy"]
    print(
        f"deps={args.deps} "
        f"numpy={numpy.__version__} ({numpy.__file__}) "
        f"regions={len(regions)} sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
