#!/usr/bin/env python3
"""DRAgoWing の load_overlap を c001 の実データで動かし、結果の JSON と sha256 を出す（実験）。

    python shrink/run_overlap.py --numpy real  out.json   # 本物の numpy
    python shrink/run_overlap.py --numpy min   out.json   # shrink/numpy_min.py を numpy として使う

--numpy min では、本物の numpy が import できる環境なら失敗する（入っていないことを確かめる）。
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


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--numpy", choices=["real", "min"], required=True)
    p.add_argument("out")
    a = p.parse_args(argv)
    if a.numpy == "min":
        if importlib.util.find_spec("numpy") is not None:
            raise SystemExit("numpy が入っている。--numpy min は numpy なしの環境で動かす")
        spec = importlib.util.spec_from_file_location("numpy", ROOT / "shrink" / "numpy_min.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["numpy"] = mod
        spec.loader.exec_module(mod)
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras")]
    from dragowing.overlap import default_conditions, load_overlap
    from dragowing.records import read_jsonl

    import numpy

    rows = read_jsonl(SEASON)
    conds = default_conditions(read_jsonl(PROPS), rows)
    result = load_overlap(SEASON, conds)
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(a.out).write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    print(f"numpy={numpy.__version__} ({numpy.__file__}) rows={len(rows)} regions={len(result['regions'])} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
