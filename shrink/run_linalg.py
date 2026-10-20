#!/usr/bin/env python3
"""suggest / littlebit / ビット行列を、本物の numpy と numpy_linalg_min で動かし、許容誤差で比べる（実験）。

    python shrink/run_linalg.py --numpy real --scope fixture out.json
    python shrink/run_linalg.py --numpy min  --scope fixture out.json
    python shrink/run_linalg.py --compare ref.json got.json

--scope c001 が既定。c001 の SVD は pure-Python だと数十秒かかる。pytest の既定には入れない。

--numpy min は、本物の numpy が import できる環境では失敗する。手元で両方を見るときは
--allow-installed を付ける（スタンドインを先に注入し、``__file__`` が numpy_linalg_min.py であることを確かめる）。
CI の numpy なしジョブは --allow-installed を付けない。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_FILE = ROOT / "shrink" / "numpy_linalg_min.py"

# 余弦・特異値・再構成。因子の符号は一意でないので比べない。
SUGGEST_RTOL, SUGGEST_ATOL = 1e-4, 1e-4
SIGMA_RTOL, SIGMA_ATOL = 1e-5, 1e-8
RECON_RTOL, RECON_ATOL = 1e-6, 1e-6
PINV_RTOL, PINV_ATOL = 1e-5, 1e-8

QUERY = "得失点差がプラスなら上位か"
DOCS = [
    ("P46", "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ないという命題"),
    ("P47", "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ないという隣の命題"),
    ("P1", "得失点差がプラスなら上位半分である"),
    ("P9", "1点差の試合で勝ち越すと期待勝利数を上回る"),
    ("N1", "明日の天気とビールの売上"),
    ("N2", "監督の名前と本拠地"),
]
ROWS = [
    ("a", 40, 1, 2.0, True), ("b", 10, 3, -5.0, False), ("c", -20, 2, 4.0, True),
    ("d", -60, 5, 1.0, False), ("e", 5, 3, 0.5, True), ("f", -10, 6, -1.0, False),
    ("g", 30, 2, -6.0, False), ("h", -30, 5, 3.0, False), ("i", 60, 1, 0.0, True),
]
TARGET = [{"col": "upper_half", "op": "==", "value": False}]
CANDS = [
    {"col": "rd", "op": "<", "value": 0},
    {"col": "rank_ra", "op": ">=", "value": 4},
    {"col": "wins_vs_pythag", "op": "<", "value": -4},
    {"col": "rd", "op": "<", "value": 20},
]
# 12×5。littlebit の段と pinv の形を小さく固定する。
MATRIX = [
    [1, 0, 1, 0, 1], [1, 1, 0, 0, 1], [0, 1, 1, 1, 0], [1, 0, 0, 1, 1],
    [0, 0, 1, 1, 0], [1, 1, 1, 0, 0], [0, 1, 0, 1, 1], [1, 0, 1, 1, 0],
    [0, 1, 1, 0, 1], [1, 1, 0, 1, 0], [0, 0, 0, 1, 1], [1, 0, 0, 0, 1],
]


def _prepare(which: str, allow_installed: bool) -> None:
    if which == "min":
        if not allow_installed and importlib.util.find_spec("numpy") is not None:
            raise SystemExit("numpy が入っている。--numpy min は numpy なしの環境で動かす（手元は --allow-installed）")
        spec = importlib.util.spec_from_file_location("numpy", MIN_FILE)
        if spec is None or spec.loader is None:
            raise SystemExit(f"読み込めない: {MIN_FILE}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["numpy"] = mod
        spec.loader.exec_module(mod)
        if not str(mod.__file__).endswith("numpy_linalg_min.py"):
            raise SystemExit(f"スタンドインではない: {mod.__file__}")
    for folder in (ROOT, ROOT / "pythdragoras", ROOT / "queryu", ROOT / "queryu" / "ask"):
        entry = str(folder)
        if entry not in sys.path:
            sys.path.insert(0, entry)


def _rule(row: dict) -> dict:
    return {
        "mcc": round(row["mcc"], 12),
        "conditions": row["conditions"],
        "tp": row["tp"],
        "fp": row["fp"],
        "if_any": row["if_any"],
    }


def _timed(bucket: dict, name: str, fn):
    start = time.perf_counter()
    value = fn()
    bucket[name] = round(time.perf_counter() - start, 6)
    return value


def collect(scope: str) -> dict:
    """numpy は呼び出す前に本物かスタンドインが入っている。"""
    import numpy as np
    import polars as pl

    import littlebit_prune as lp
    import rule_search as rs
    import suggest

    seconds: dict[str, float] = {}
    if scope == "fixture":
        docs, dim = DOCS, 4
        frame = pl.DataFrame(
            [{"rd": rd, "rank_ra": ra, "wins_vs_pythag": w, "upper_half": u} for _, rd, ra, w, u in ROWS]
        )
        target, cands = TARGET, CANDS
        kw = dict(max_terms=2, max_conds=2, top=20)
        rank, stages = 2, 1
        matrix = np.array(MATRIX, dtype=np.float64)
        als = 2
        pinv_src = matrix[:4, :]
    elif scope == "c001":
        import tomllib

        import aoi_paths
        import littlebit_approx as la
        from pythdragoras import apply_exclusions

        cycle = aoi_paths.resolve_cycle_path(ROOT)
        docs = suggest.load_docs(cycle / "outputs")
        dim = 128
        cfg = tomllib.loads((cycle / "analysis.toml").read_text(encoding="utf-8"))
        spec = tomllib.loads((cycle / "rule_candidates.toml").read_text(encoding="utf-8"))
        season = pl.read_ndjson(cycle / "outputs" / "season.jsonl")
        season, _dropped = apply_exclusions(season, cfg.get("exclude", []))
        cols = sorted({c["col"] for c in [*spec["target"], *spec["candidate"]]})
        frame = season.drop_nulls(cols)
        target, cands = spec["target"], spec["candidate"]
        kw = dict(max_terms=int(spec["max_terms"]), max_conds=int(spec["max_conds"]), top=20)
        rank, stages = 8, 2
        matrix = la.indicator_matrix(frame, cands).astype(np.float64)
        als = la.ALS_ITERS
        # holdout の decoder.T と同じ (rank, 条件数)。因子の符号には依存させない。
        pinv_src = matrix[:8, :]
    else:
        raise SystemExit(f"scope が違う: {scope}")

    def _index():
        return suggest.Index(docs, dim=dim)

    index = _timed(seconds, "suggest_index", _index)
    float_hits = _timed(seconds, "suggest_query", lambda: index.query(QUERY, mode="float", k=5))
    binary_hits = index.query(QUERY, mode="binary", k=5)
    singular = _timed(
        seconds, "indicator_svd",
        lambda: np.linalg.svd(matrix, full_matrices=False, compute_uv=False),
    )

    def _recon():
        parts = lp.littlebit(matrix, rank=min(rank, matrix.shape[1]), stages=stages, als_iters=als)
        return lp._dense(parts)

    recon = _timed(seconds, "littlebit_recon", _recon)
    pseudo = _timed(seconds, "pinv", lambda: np.linalg.pinv(pinv_src, rcond=1e-12))
    bit = _timed(seconds, "bitmatrix", lambda: rs.search(frame, target, cands, backend="bitmatrix", **kw))
    guaranteed = _timed(
        seconds, "guaranteed",
        lambda: rs.search(frame, target, cands, prune="littlebit", rank=rank, stages=stages, **kw),
    )
    return {
        "scope": scope,
        "numpy_file": str(np.__file__),
        "suggest": {
            "n_docs": len(docs),
            "vocab": len(index.vocab),
            "dim": dim,
            "float": [{"id": i, "similarity": float(s)} for i, s in float_hits],
            "binary": [{"id": i, "similarity": float(s)} for i, s in binary_hits],
            "sizes": index.sizes(),
        },
        "indicator": {"shape": list(matrix.shape), "singular_values": [float(v) for v in singular.tolist()]},
        "littlebit_recon": {"shape": list(recon.shape), "values": recon.tolist()},
        "pinv": {"shape": list(pseudo.shape), "rcond": 1e-12, "values": pseudo.tolist()},
        "bitmatrix": [_rule(row) for row in bit],
        "guaranteed": [_rule(row) for row in guaranteed],
        "meta": {"seconds": seconds},
    }


def _numbers(a, b, rtol: float, atol: float, path: str) -> list[str]:
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path} の長さ {len(a)} と {len(b)}"]
        bad = []
        for i, (left, right) in enumerate(zip(a, b)):
            bad.extend(_numbers(left, right, rtol, atol, f"{path}[{i}]"))
        return bad
    if isinstance(a, bool) or isinstance(b, bool):
        return [] if a == b else [f"{path} {a!r} != {b!r}"]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if math.isnan(a) and math.isnan(b):
            return []
        if math.isclose(float(a), float(b), rel_tol=rtol, abs_tol=atol):
            return []
        return [f"{path} {a} と {b}（rtol={rtol}, atol={atol}）"]
    return [] if a == b else [f"{path} {a!r} != {b!r}"]


def _hits(ref: list, got: list, path: str) -> list[str]:
    rid = [row["id"] for row in ref]
    gid = [row["id"] for row in got]
    if rid != gid:
        return [f"{path} の id {rid} と {gid}"]
    return _numbers(
        [row["similarity"] for row in ref],
        [row["similarity"] for row in got],
        SUGGEST_RTOL, SUGGEST_ATOL, path + " similarity",
    )


def compare(ref: dict, got: dict) -> list[str]:
    bad: list[str] = []
    if ref.get("scope") != got.get("scope"):
        bad.append(f"scope {ref.get('scope')} と {got.get('scope')}")
    for key in ("n_docs", "vocab", "dim", "sizes"):
        if ref["suggest"][key] != got["suggest"][key]:
            bad.append(f"suggest.{key} {ref['suggest'][key]!r} と {got['suggest'][key]!r}")
    bad.extend(_hits(ref["suggest"]["float"], got["suggest"]["float"], "suggest.float"))
    bad.extend(_hits(ref["suggest"]["binary"], got["suggest"]["binary"], "suggest.binary"))
    if ref["indicator"]["shape"] != got["indicator"]["shape"]:
        bad.append(f"indicator shape {ref['indicator']['shape']} と {got['indicator']['shape']}")
    bad.extend(_numbers(ref["indicator"]["singular_values"], got["indicator"]["singular_values"], SIGMA_RTOL, SIGMA_ATOL, "singular_values"))
    if ref["littlebit_recon"]["shape"] != got["littlebit_recon"]["shape"]:
        bad.append("littlebit_recon の shape が違う")
    bad.extend(_numbers(ref["littlebit_recon"]["values"], got["littlebit_recon"]["values"], RECON_RTOL, RECON_ATOL, "littlebit_recon"))
    if ref["pinv"]["shape"] != got["pinv"]["shape"]:
        bad.append(f"pinv shape {ref['pinv']['shape']} と {got['pinv']['shape']}")
    bad.extend(_numbers(ref["pinv"]["values"], got["pinv"]["values"], PINV_RTOL, PINV_ATOL, "pinv"))
    if ref["bitmatrix"] != got["bitmatrix"]:
        bad.append("bitmatrix の規則（mcc を 12 桁、tp、fp、if_any）が一致しない")
    if ref["guaranteed"] != got["guaranteed"]:
        bad.append("search_guaranteed の規則が一致しない（上限が整数境界をまたいだ可能性がある）")
    return bad


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--numpy", choices=["real", "min"])
    parser.add_argument("--scope", choices=["fixture", "c001"], default="c001")
    parser.add_argument("--allow-installed", action="store_true")
    parser.add_argument("--compare", nargs=2, metavar=("REF", "GOT"))
    parser.add_argument("out", nargs="?")
    args = parser.parse_args(argv)
    if args.compare:
        ref = json.loads(Path(args.compare[0]).read_text(encoding="utf-8"))
        got = json.loads(Path(args.compare[1]).read_text(encoding="utf-8"))
        bad = compare(ref, got)
        if bad:
            print("\n".join(bad))
            return 1
        print(f"ok scope={ref['scope']} suggest={ref['suggest']['n_docs']} docs indicator={ref['indicator']['shape']}")
        return 0
    if args.numpy is None or not args.out:
        raise SystemExit("--numpy と出力先、または --compare が必要")
    _prepare(args.numpy, args.allow_installed)
    import numpy
    payload = collect(args.scope)
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    seconds = payload["meta"]["seconds"]
    print(
        f"numpy={numpy.__version__} ({numpy.__file__}) scope={args.scope} "
        f"docs={payload['suggest']['n_docs']} indicator={payload['indicator']['shape']} "
        f"seconds={seconds}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
