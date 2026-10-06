"""R51: 序盤・中盤・終盤の得点と失点（PR #3 のチーム×年の集計）を、同じ年・同じリーグの他球団と比べる（記述）。

    python cycles/c001-chunichi/research/r51_late.py cycles/c001-chunichi/references/pr3-inning-team-year-metrics.csv.gz \
        cycles/c001-chunichi/outputs/season.jsonl

区切りは集計のまま: 序盤 1〜3回、中盤 4〜6回、終盤 7〜9回（延長は除く）。1回あたりの得点（攻撃）と失点（守備）。
差し引き = 攻撃 − 守備 を、同じ年・同じリーグの他球団の平均と比べる。チーム単位の集計なので方針の範囲内。
回ごとの配分は独立に照合していない（FINDINGS 7）。
"""

import csv
import gzip
import json
import statistics
import sys
from pathlib import Path

PHASES = ("early", "middle", "late")
NAMES = {"early": "序盤 1〜3回", "middle": "中盤 4〜6回", "late": "終盤 7〜9回"}


def load(path: str) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["venue"] == "all" and r["window"] == "all"]
    out = {}
    for r in rows:
        key = (int(r["year"]), r["team"])
        out.setdefault(key, {"league": r["league"]})[r["role"]] = {p: float(r[f"{p}_runs_per_inning"]) for p in PHASES}
    return out


def relative(data: dict) -> dict:
    """攻撃 − 守備（1回あたり）を、同じ年・同じリーグの他球団の平均との差にする。"""
    net = {k: {p: v["off"][p] - v["def"][p] for p in PHASES} for k, v in data.items() if "off" in v and "def" in v}
    out = {}
    for (y, t), v in net.items():
        others = [net[(y2, t2)] for (y2, t2) in net if y2 == y and t2 != t and data[(y2, t2)]["league"] == data[(y, t)]["league"]]
        out[(y, t)] = {p: v[p] - statistics.mean(o[p] for o in others) for p in PHASES}
    return out


def main(argv: list[str]) -> int:
    rel = relative(load(argv[0]))
    season = {(r["season"], r["team"]): r for r in map(json.loads, Path(argv[1]).read_text(encoding="utf-8").splitlines())}
    head = "| 単位 | 順位 | " + " | ".join(NAMES[p] for p in PHASES) + " | 終盤 − 序盤・中盤の平均 |"
    print(head + "\n|---|---|---|---|---|---|")
    focus = [(2015, "t"), (2022, "d"), (2017, "d"), (2024, "d"), (2019, "d"), (2014, "d"), (2018, "d")]
    for k in focus:
        v, s = rel[k], season[k]
        print(f"| {s['team_name']} {k[0]} | {s['rank']} | " + " | ".join(f"{v[p]:+.3f}" for p in PHASES)
              + f" | {v['late'] - (v['early'] + v['middle']) / 2:+.3f} |")

    # 点の差どおりでは線に届かない単位（line_gap_pythag < 0）を、A と B に分けて並べる
    below = [k for k, s in season.items() if k in rel and s["season"] != 2020 and (s.get("line_gap_pythag") or 0) < 0]
    for name, keep in (("線に届かないのに A", True), ("線に届かず B", False)):
        ks = [k for k in below if season[k]["upper_half"] == keep]
        if not ks:
            continue
        print(f"\n{name}: {len(ks)}単位。中央値 " + "、".join(f"{NAMES[p]} {statistics.median(rel[k][p] for k in ks):+.3f}" for p in PHASES)
              + f"、終盤 − 序盤・中盤 {statistics.median(rel[k]['late'] - (rel[k]['early'] + rel[k]['middle']) / 2 for k in ks):+.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
