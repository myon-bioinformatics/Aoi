"""条件の組み合わせ（「または」でつないだ「かつ」の組）を総当たりで探し、目的の状態をどれだけ言い当てるかで並べる。

探索は命題を作るための材料で、命題の判定ではない。見つかった式は、それを見た後に作った命題として登録し、
作るきっかけになったデータとは別のデータ（翌年以降など）で確かめる（docs/propositions.md の Restating）。

  候補の条件は探索の前にファイルに書く（候補を後から足して探し直すと、それ自体が選び直しになる）
  式の形: (c1 かつ c2) または (c3 かつ c4)。組の数・組の中の条件の数の上限は引数で決める
  評価: 前件 ⇒ 目的（成立率 = precision）と 目的 ⇒ 前件（逆の成立率 = recall）の両方を数え、Matthews 相関係数で並べる。
        同点なら条件の少ない式を上にする

使い方:
  python pythdragoras/rule_search.py --season season.jsonl --config analysis.toml --candidates rule_candidates.toml \\
      --out outputs/rules.jsonl [--top 20]
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import tomllib
from pathlib import Path

import polars as pl

from propositions import OPS, PropositionError, _cond, text


def _mask(df: pl.DataFrame, conds: list[dict]) -> int:
    """条件を満たす単位をビットで表す（i 番目の単位が満たせば i ビット目が 1）。"""
    flags = df.select(x=_cond(conds, df.columns))["x"].to_list()
    return sum(1 << i for i, f in enumerate(flags) if f)


def _mcc(tp: int, fp: int, fn: int, tn: int) -> float:
    d = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return (tp * tn - fp * fn) / d if d else 0.0


def search(df: pl.DataFrame, target: list[dict], candidates: list[dict], max_terms: int = 2,
           max_conds: int = 2, top: int = 20) -> list[dict]:
    """df の各単位について、候補の条件からできる式を総当たりで評価する。値が空の単位は呼び出す側で除いておく。"""
    for c in [*target, *candidates]:
        if set(c) != {"col", "op", "value"} or c["op"] not in OPS:
            raise PropositionError(f"条件は {{col, op, value}}: {c}")
    n = df.height
    full = (1 << n) - 1
    y = _mask(df, target)
    cand = [(c, _mask(df, [c])) for c in candidates]
    terms = []  # 組 = 同じ列を2度使わない「かつ」
    for k in range(1, max_conds + 1):
        for combo in itertools.combinations(cand, k):
            if len({c["col"] for c, _ in combo}) < k:
                continue
            m = full
            for _, cm in combo:
                m &= cm
            terms.append(([c for c, _ in combo], m))
    out = []
    for k in range(1, max_terms + 1):
        for combo in itertools.combinations(terms, k):
            m = 0
            for _, tm in combo:
                m |= tm
            tp, fp = (m & y).bit_count(), (m & ~y & full).bit_count()
            fn, tn = (~m & y & full).bit_count(), n - (m | y).bit_count()
            groups = [g for g, _ in combo]
            out.append({"if_any": groups, "conditions": sum(len(g) for g in groups),
                        "tp": tp, "fp": fp, "fn": fn, "tn": tn, "mcc": _mcc(tp, fp, fn, tn),
                        "precision": tp / (tp + fp) if tp + fp else None, "recall": tp / (tp + fn) if tp + fn else None})
    out.sort(key=lambda r: (-round(r["mcc"], 12), r["conditions"], json.dumps(r["if_any"], ensure_ascii=False)))
    return out[:top]


def rule_text(r: dict) -> str:
    return " または ".join(f"[{text(g)}]" for g in r["if_any"])


def main(argv=None) -> int:
    from pythdragoras import apply_exclusions

    ap = argparse.ArgumentParser(description="条件の組み合わせを総当たりで探す（命題を作るための材料）")
    ap.add_argument("--season", type=Path, required=True)
    ap.add_argument("--config", type=Path, required=True, help="分析設定（除外を適用する）")
    ap.add_argument("--candidates", type=Path, required=True, help="目的と候補の条件（TOML）")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args(argv)

    cfg = tomllib.loads(args.config.read_text(encoding="utf-8"))
    spec = tomllib.loads(args.candidates.read_text(encoding="utf-8"))
    st = pl.read_ndjson(args.season)
    st, _ = apply_exclusions(st, cfg.get("exclude", []))
    cols = sorted({c["col"] for c in [*spec["target"], *spec["candidate"]]})
    usable = st.drop_nulls(cols)  # 値が空の単位は探索に入れない（件数は出力に残す）
    rules = search(usable, spec["target"], spec["candidate"], int(spec.get("max_terms", 2)),
                   int(spec.get("max_conds", 2)), args.top)
    meta = {"units": usable.height, "dropped_for_missing_values": st.height - usable.height,
            "target": text(spec["target"]), "candidates": len(spec["candidate"])}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps({**meta, "rank": i + 1, **r}, ensure_ascii=False) + "\n"
                                for i, r in enumerate(rules)), encoding="utf-8")
    print(f"units={meta['units']} dropped={meta['dropped_for_missing_values']} target: {meta['target']}")
    for i, r in enumerate(rules[:10], 1):
        print(f"{i:2d}. mcc={r['mcc']:.3f} 成立率={r['precision']:.2f} 逆={r['recall']:.2f} 条件={r['conditions']}  {rule_text(r)}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
