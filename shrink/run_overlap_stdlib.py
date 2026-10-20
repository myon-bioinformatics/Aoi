#!/usr/bin/env python3
"""DRAgoWing の load_overlap を c001 の実データで動かし、結果の JSON と sha256 を出す（実験）。

    python shrink/run_overlap_stdlib.py --deps real out.json   # 本物の numpy と polars
    python shrink/run_overlap_stdlib.py --deps min  out.json   # numpy_min と polars_min

--deps min では、本物の numpy か polars が import できる環境なら失敗する（両方入っていないことを確かめる）。
本番のパイプラインは変えない。呼び出し側が min を使うときは、import より前に同じ差し替えをする。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEASON = ROOT / "cycles/c001-chunichi/outputs/season.jsonl"
PROPS = ROOT / "cycles/c001-chunichi/outputs/propositions.jsonl"


def inject(name: str, filename: Path) -> None:
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deps", choices=["real", "min"], required=True)
    parser.add_argument("out")
    args = parser.parse_args(argv)
    if args.deps == "min":
        present = [name for name in ("numpy", "polars") if importlib.util.find_spec(name) is not None]
        if present:
            raise SystemExit(f"{' と '.join(present)} が入っている。--deps min は両方ない環境で動かす")
        inject("numpy", ROOT / "shrink" / "numpy_min.py")
        inject("polars", ROOT / "shrink" / "polars_min.py")
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras")]
    from dragowing.overlap import default_conditions, load_overlap
    from dragowing.records import read_jsonl

    import numpy
    import polars

    rows = read_jsonl(SEASON)
    result = load_overlap(SEASON, default_conditions(read_jsonl(PROPS), rows))
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(args.out).write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    print(
        f"numpy={numpy.__version__} ({numpy.__file__}) polars={polars.__version__} ({polars.__file__}) "
        f"rows={len(rows)} regions={len(result['regions'])} sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
