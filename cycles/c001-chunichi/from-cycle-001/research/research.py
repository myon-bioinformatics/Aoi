"""旧サイクル1（from-cycle-001）の研究 R31〜R76 の集計（記述。判定はしない。R75・R76 だけは命題の判定を呼ぶ）。

    python cycles/c001-chunichi/from-cycle-001/research/research.py <r31〜r76> [その研究の引数]

1 つの研究が 1 つのサブコマンド（旧 rNN_*.py の 1 本が 1 つ）。どれも手元のファイルだけを読み、ネットワークを使わない。
研究ごとの説明と引数は、各関数の説明（旧ファイルの冒頭の説明をそのまま移した）にある。ノートは同じフォルダの R*.md。
同じ中身の補助（2020年を除く EXCLUDED など）は 1 つにし、研究ごとに中身が違う名前には rNN_ を付けた。
"""

import argparse
import csv
import gzip
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
# R75・R76 の命題の判定（propositions・sets）。旧ファイルは from-cycle-001/ へ移る前の深さ（parents[3]）と
# 旧名の PythDRagoras/ のままで、外から PYTHONPATH を渡したときにしか動かなかった。今の場所と名前に直した
sys.path[:0] = [str(ROOT / "pythdragoras")]

import polars as pl  # noqa: E402
import propositions as pr  # noqa: E402
import sets as st_  # noqa: E402


# ==== r31（旧 r31_balance.py）

BANDS = ("floor", "mid", "ceiling", "total")
EARLY, LATE = range(2013, 2020), range(2021, 2026)  # 計画で先に決めた2つの期間（2020年は除く）
DIVERGE = 10.0  # 発散とみなす比（不足が優位の10倍以上）。実行後に決めた目安で、判定には使わない
MODE_BIN = 0.5  # 比の最頻値をとるときの幅。実行後に決めた


def r31_per_game(row: dict, col: str) -> float:
    return row[col] / row["G"]


def add_balance(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        others = [o for o in rows if o["season"] == r["season"] and o["league"] == r["league"] and o["team"] != r["team"]]
        ra_adv = sum(r31_per_game(o, "RA") for o in others) / len(others) - r31_per_game(r, "RA")
        out.append({**r, "ra_adv": ra_adv, "balance": r["rf_def_total"] + ra_adv})
    return out


def r31_mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def r31(argv: list[str]) -> int:
    """R31: 中日の得点の不足を帯ごとに分け、失点の優位と並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r31 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の既存の列だけを使う（rf_def_* は R3、得点・失点・試合数は観測）。ネットワークを使わない。
    失点の優位 ra_adv = 同じ年・同じリーグの他球団の失点／試合の平均 − 自分の失点／試合（プラスほど抑えた）。
    収支 balance = rf_def_total + ra_adv（得点の不足を、失点の優位で補えたか。プラスなら補えた）。
    """
    rows = add_balance([json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()])
    d = sorted((r for r in rows if r["team"] == "d"), key=lambda r: r["season"])

    print("| 年 | 順位 | 失点の順位 | 床 | 中 | 天井 | 得点の不足 | 失点の優位 | 収支 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in d:
        mark = "（除外）" if r["season"] == 2020 else ""
        print(f"| {r['season']}{mark} | {r['rank']} | {r['rank_ra']} | " + " | ".join(f"{r['rf_def_' + b]:+.2f}" for b in BANDS)
              + f" | {r['ra_adv']:+.2f} | {r['balance']:+.2f} |")

    print("\n| 期間 | 年数 | 床 | 中 | 天井 | 得点の不足 | 失点の優位 | 収支 |")
    print("|---|---|---|---|---|---|---|---|")
    means = {}
    for name, years in (("2013〜2019", EARLY), ("2021〜2025", LATE)):
        xs = [r for r in d if r["season"] in years]
        means[name] = {k: r31_mean([r[f"rf_def_{k}"] for r in xs]) for k in BANDS} | {
            "ra_adv": r31_mean([r["ra_adv"] for r in xs]), "balance": r31_mean([r["balance"] for r in xs])}
        m = means[name]
        print(f"| {name} | {len(xs)} | " + " | ".join(f"{m[k]:+.3f}" for k in [*BANDS, "ra_adv", "balance"]) + " |")
    a, b = means["2013〜2019"], means["2021〜2025"]
    change = b["total"] - a["total"]
    print(f"\n得点の不足の変化 {change:+.3f}。帯ごとの割合: " + "、".join(
        f"{k} {(b[k] - a[k]) / change:.0%}" for k in BANDS[:3]))

    # 失点だけ上位（失点3位以内・得点4位以下）の B クラス。2020年を除く
    one = [r for r in rows if r["season"] != 2020 and r["rank_ra"] <= 3 and r["rank_rf"] >= 4 and not r["upper_half"]]
    for name, xs in (("中日", [r for r in one if r["team"] == "d"]), ("中日以外", [r for r in one if r["team"] != "d"])):
        short = sum(r["balance"] < 0 for r in xs)
        print(f"\n失点だけ上位の B クラス・{name}: {len(xs)}単位、補えなかった（収支 < 0）{short}、"
              f"得点の不足 {r31_mean([r['rf_def_total'] for r in xs]):+.3f}、失点の優位 {r31_mean([r['ra_adv'] for r in xs]):+.3f}、"
              f"不足 ÷ 優位（平均の比）{-r31_mean([r['rf_def_total'] for r in xs]) / r31_mean([r['ra_adv'] for r in xs]):.2f}")
    # 計画では「不足 ÷ 優位」の各単位の比の平均を使うと決めていたが、優位がほぼ 0 の単位で比が発散し、
    # 平均が意味をなさなかった（実行後に分かった）。R31 の結果に変更として記録し、平均の比に置き換えた

    # 0 の近くの割り算への対策を並べる（ユーザーの指摘から。どれが正しいかは決めず、読みが保たれるかを見る）
    print("\n| 失点だけ上位の B | 比の平均（計画） | 平均の比 | 比の中央値 | 比の最頻値（幅 0.5） | 対数で平均（幾何平均） | 取り分の平均 → 比 | 対数で外した単位 |")
    print("|---|---|---|---|---|---|---|---|")
    groups = (("中日", [r for r in one if r["team"] == "d"]), ("中日以外", [r for r in one if r["team"] != "d"]))
    for name, xs in groups:
        v = ratio_variants([-r["rf_def_total"] for r in xs], [r["ra_adv"] for r in xs])
        modes = "・".join(f"{m:.2f}" for m in v["mode_of_ratios"])
        print(f"| {name} | {v['mean_of_ratios']:.3g} | {v['ratio_of_means']:.2f} | {v['median_of_ratios']:.2f} | {modes} "
              f"| {v['geometric_mean']:.2f} | {v['share_mean']:.2f} → {v['share_as_ratio']:.2f} | {v['dropped']} |")

    # 発散は失敗ではなく観測（ユーザーの見立て）。どの単位で発散したか・しなかったかを並べ、次の命題の種にする
    print(f"\n発散した単位（優位 ≤ 0、または 不足 ÷ 優位 ≥ {DIVERGE}）:")
    for name, xs in groups:
        hit = [r for r in xs if r["ra_adv"] <= 0 or -r["rf_def_total"] / r["ra_adv"] >= DIVERGE]
        print(f"- {name}: {len(hit)}/{len(xs)}単位 " + ", ".join(
            f"{r['team']}-{r['season']}（失点{r['rank_ra']}位、優位 {r['ra_adv']:+.3f}、不足 {r['rf_def_total']:+.2f}）"
            for r in sorted(hit, key=lambda r: r["ra_adv"])))
    return 0


def ratio_variants(deficit: list[float], advantage: list[float]) -> dict:
    """不足 ÷ 優位 を、割る数が 0 に近い単位に強いかどうかの違う形で並べる。

    - mean_of_ratios: 単位ごとの比の平均（計画の形）。優位が 0 に近いと発散する
    - ratio_of_means: 平均の比。割る数は平均なので、範囲全体の優位が 0 に近くない限り発散しない
    - median_of_ratios: 単位ごとの比の中央値。発散した少数の単位に引っ張られない
    - geometric_mean: 自然対数をとって平均し、戻したもの（exp(平均 ln(不足/優位))）。大きな比を圧縮する。
      対数は正の値にしか定義できないので、優位 ≤ 0 の単位は外す（dropped に数える）
    - mode_of_ratios: 比を幅 MODE_BIN の区間に分けたときの最頻の区間の中央（同数なら複数）。発散した単位は自分だけの区間に入る。
      すべての単位が同じ区間なら比べられない（区間を細かくする）
    - share_mean: 取り分 不足 ÷（不足 + 優位）の平均。0〜1 に収まり、優位が 0 なら 1（すべて補えなかった）。
      優位がマイナスの単位も 1 で止める。share_as_ratio = s ÷ (1 − s) で比の目盛りに戻す
    不足・優位はどちらもプラスの向き（不足 = 他球団より少ない得点の量）で渡す。
    """
    import math
    import statistics

    pos = [(d, a) for d, a in zip(deficit, advantage) if a > 0]
    ratios = [d / a for d, a in pos]
    logs = [math.log(d) - math.log(a) for d, a in pos if d > 0]
    shares = [1.0 if a <= 0 else min(1.0, max(0.0, d / (d + a))) for d, a in zip(deficit, advantage)]
    s = r31_mean(shares)
    from collections import Counter

    bins = Counter(math.floor(r / MODE_BIN) for r in ratios)
    top = max(bins.values()) if bins else 0
    modes = sorted((b + 0.5) * MODE_BIN for b, c in bins.items() if c == top)
    return {
        "mode_of_ratios": modes,
        "mean_of_ratios": r31_mean(ratios),
        "ratio_of_means": r31_mean(deficit) / r31_mean(advantage),
        "median_of_ratios": statistics.median(ratios) if ratios else float("nan"),
        "geometric_mean": math.exp(r31_mean(logs)) if logs else float("nan"),
        "share_mean": s,
        "share_as_ratio": s / (1 - s) if s < 1 else float("inf"),
        "dropped": len(deficit) - len(logs),
    }


# ==== r35（旧 r35_reference.py）

SHORTFALL = 0.6  # R32〜R34 の境（1試合あたりの得点の不足）


def r35_mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def r35_fmt(r: dict) -> str:
    return (f"| {r['team_name']} {r['season']} | {r['G']} | {r['rank']} | {r['rf_adv']:+.2f} | {r['rf_adv_se']:.2f} | {r['rf_zone_se']:+d} "
            f"| {r['ra_adv']:+.2f} | {r['ra_adv_se']:.2f} | {r['ra_zone_se']:+d} | {r['run_balance']:+.2f} |")


def r35(argv: list[str]) -> int:
    """R35: 2020年を参考として同じ物差し（誤差の幅）で並べ、中日の「失点だけ上位」の年を誤差の内側・外側に分ける（記述）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r35 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の既存の列だけを使う（*_adv・*_adv_se・*_zone_se は R32〜R34）。ネットワークを使わない。判定はしない。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    head = ("| 単位 | 試合 | 順位 | 得点の優位 | 誤差 | 区分 | 失点の優位 | 誤差 | 区分 | 収支 |\n"
            "|---|---|---|---|---|---|---|---|---|---|")

    print("## 1. 2020年（参考）\n")
    y20 = [r for r in rows if r["season"] == 2020 and r["league"] == "C"]
    print(head)
    for r in sorted(y20, key=lambda r: r["rank"]):
        print(r35_fmt(r))
    rest = [r for r in rows if r["season"] != 2020]
    print(f"\n誤差の中央値: 2020年 得点 {sorted(r['rf_adv_se'] for r in y20)[len(y20) // 2]:.3f}、"
          f"他の年 {sorted(r['rf_adv_se'] for r in rest)[len(rest) // 2]:.3f}")
    big = [r for r in rows if r["rf_adv"] < -SHORTFALL]
    print(f"\n不足 > {SHORTFALL} の単位: 全 {len(big)}、うち A {sum(r['upper_half'] for r in big)}"
          f"""（{', '.join(f'{r["team"]}-{r["season"]}' for r in big if r['upper_half'])}）""")
    for r in big:
        if r["upper_half"]:
            print(f"  {r['team']}-{r['season']}: 不足 ÷ 誤差 = {-r['rf_adv'] / r['rf_adv_se']:.2f}、"
                  f"不足 − 0.6 = {-r['rf_adv'] - SHORTFALL:.2f}（誤差 {r['rf_adv_se']:.2f} の {(-r['rf_adv'] - SHORTFALL) / r['rf_adv_se']:.2f} 倍）")

    print("\n## 2. 中日の「失点だけ上位」（順位: 失点3位以内・得点4位以下）の年\n")
    d = [r for r in rows if r["team"] == "d" and r["rank_ra"] <= 3 and r["rank_rf"] >= 4]
    print(head)
    for r in sorted(d, key=lambda r: r["season"]):
        print(r35_fmt(r))
    for name, xs in (("失点が誤差の外側（+1）", [r for r in d if r["ra_zone_se"] == 1]),
                     ("失点が誤差の内側（0）", [r for r in d if r["ra_zone_se"] == 0])):
        print(f"\n{name}: {', '.join(str(r['season']) for r in xs)}。A {sum(r['upper_half'] for r in xs)}／{len(xs)}、"
              f"得失点差の平均 {r35_mean(r['rd'] for r in xs):+.1f}、得点の優位の平均 {r35_mean(r['rf_adv'] for r in xs):+.2f}、"
              f"失点の優位の平均 {r35_mean(r['ra_adv'] for r in xs):+.2f}")
    return 0


# ==== r36（旧 r36_case.py）

R36_FOCUS = ("d", 2019)
R36_MEASURES = [  # (列, 中身)。計画で先に決めた順
    ("wins_vs_pythag", "点の差から見込まれる勝ち数との差"),
    ("one_run_net", "1点差の勝ち − 負け"),
    ("blowout_net", "4点差以上の勝ち − 負け"),
    ("alloc_z_strat", "得点・失点の組み合わせ方（R1）"),
    ("vs_top_wpct", "上の相手との勝率"),
    ("vs_lower_wpct", "下の相手との勝率"),
    ("opp_conv_top", "上の相手との試合で、点の差では説明できない勝ち負け"),
    ("opp_conv_mid", "中位の相手との同じもの"),
    ("opp_conv_low", "下の相手との同じもの"),
    ("opp_net_gap_top_c", "上の相手との試合の点の差（見込みとの差）"),
    ("opp_env_gap_top_c", "上の相手との試合全体の点の多さ（見込みとの差）"),
    ("course_wpct_diff", "後半の勝率 − 前半の勝率"),
    ("series_lost_pct", "負け越したカードの多さ（力が一定のときとの比べ）"),
]


def r36(argv: list[str]) -> int:
    """R36: 中日 2019年を、同じ形（得点 −1・失点 +1、誤差の幅）のチームと並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r36 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の既存の列だけを使う。ネットワークを使わない。並べる指標と読み方は R36 の計画で先に決めた。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    shape = [r for r in rows if r["season"] != 2020 and r["rf_zone_se"] == -1 and r["ra_zone_se"] == 1]
    focus = next(r for r in shape if (r["team"], r["season"]) == R36_FOCUS)
    a = [r for r in shape if r["team"] != "d" and r["upper_half"]]
    b = [r for r in shape if r["team"] != "d" and not r["upper_half"]]
    other_d = [r for r in shape if r["team"] == "d" and r is not focus]
    name = lambda r: f"{r['team']}-{r['season']}"  # noqa: E731

    print(f"同じ形の単位: 中日以外の A {len(a)}（{', '.join(map(name, a))}）、中日以外の B {len(b)}（{', '.join(map(name, b))}）、"
          f"中日 {', '.join(name(r) + ('(A)' if r['upper_half'] else '(B)') for r in [focus, *other_d])}\n")
    print("| 指標 | 中身 | 中日 2019 | A の範囲（中央値） | B の範囲（中央値） | 2019 は A の範囲の外 | A と B が重ならない |")
    print("|---|---|---|---|---|---|---|")
    for col, label in R36_MEASURES:
        av, bv, f = [r[col] for r in a if r[col] is not None], [r[col] for r in b if r[col] is not None], focus[col]
        if f is None or not av or not bv:
            print(f"| `{col}` | {label} | - | - | - | - | - |")
            continue
        outside = "**外**（下）" if f < min(av) else "**外**（上）" if f > max(av) else "内"
        split = "重ならない" if max(av) < min(bv) or min(av) > max(bv) else "重なる"
        print(f"| `{col}` | {label} | {f:+.2f} | {min(av):+.2f}〜{max(av):+.2f}（{statistics.median(av):+.2f}） "
              f"| {min(bv):+.2f}〜{max(bv):+.2f}（{statistics.median(bv):+.2f}） | {outside} | {split} |")
    return 0


# ==== r37（旧 r37_counterexamples.py）

def r37(argv: list[str]) -> int:
    """R37: 精度の高い命題の判例を、同じ形の反対の結果のチームと並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r37 cycles/c001-chunichi/outputs/season.jsonl t-2015 g-2016

    形は誤差の幅での区分（rf_zone_se, ra_zone_se）。同じ形で結果（A・B）が逆の単位を比べる相手にする。
    並べる指標は R36 と同じ13（R36_MEASURES）。2020年は除く。ネットワークを使わない。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if r["season"] != 2020]
    key = lambda r: f"{r['team']}-{r['season']}"  # noqa: E731
    by = {key(r): r for r in rows}
    for unit in argv[1:]:
        f = by[unit]
        shape = (f["rf_zone_se"], f["ra_zone_se"])
        same = [r for r in rows if (r["rf_zone_se"], r["ra_zone_se"]) == shape and r is not f]
        opp = [r for r in same if r["upper_half"] != f["upper_half"]]
        alike = [r for r in same if r["upper_half"] == f["upper_half"]]
        cls = "A" if f["upper_half"] else "B"
        print(f"\n### {f['team_name']} {f['season']}（{f['rank']}位、{cls}、形: 得点 {shape[0]:+d}・失点 {shape[1]:+d}、得失点差 {f['rd']:+d}）\n")
        print(f"同じ形: 結果が逆 {len(opp)}、同じ結果 {len(alike)}（{', '.join(map(key, alike)) or 'なし'}）\n")
        print("| 指標 | 中身 | この単位 | 結果が逆の範囲（中央値） | 範囲の外 |")
        print("|---|---|---|---|---|")
        for col, label in R36_MEASURES:
            v, ov = f[col], [r[col] for r in opp if r[col] is not None]
            if v is None or not ov:
                print(f"| `{col}` | {label} | - | - | - |")
                continue
            out = "**外**（上）" if v > max(ov) else "**外**（下）" if v < min(ov) else "内"
            print(f"| `{col}` | {label} | {v:+.2f} | {min(ov):+.2f}〜{max(ov):+.2f}（{statistics.median(ov):+.2f}） | {out} |")
    return 0


# ==== r38（旧 r38_plus_but_b.py）

def quartiles(xs):
    q = statistics.quantiles(xs, n=4)
    return q[0], q[2]


def r38(argv: list[str]) -> int:
    """R38: 得失点差プラスなのに B の単位を、得失点差プラスで A の単位と並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r38 cycles/c001-chunichi/outputs/season.jsonl

    1. 巨人 2017年を、同じ形（誤差の幅で得点 −1・失点 +1）の A と並べる（R36 の中日 2019年と同じ並べ方）
    2. 得失点差プラス（rd > 0）の B（P1 の判例）を、得失点差プラスの A と13の指標で並べる
    2020年は除く。指標は R36 と同じ13（r36_case.MEASURES）。ネットワークを使わない。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if r["season"] != 2020]
    key = lambda r: f"{r['team']}-{r['season']}"  # noqa: E731

    print("### 1. 巨人 2017年と中日 2019年（同じ形の A の範囲の外か）\n")
    shape = [r for r in rows if r["rf_zone_se"] == -1 and r["ra_zone_se"] == 1]
    a = [r for r in shape if r["upper_half"]]
    g, d = next(r for r in shape if key(r) == "g-2017"), next(r for r in shape if key(r) == "d-2019")
    print(f"同じ形の A: {', '.join(map(key, a))}\n")
    print("| 指標 | 中身 | 巨人 2017 | 中日 2019 | A の範囲 | 巨人 2017 は外 | 中日 2019 は外 |")
    print("|---|---|---|---|---|---|---|")
    side = lambda v, xs: "**外**（上）" if v > max(xs) else "**外**（下）" if v < min(xs) else "内"  # noqa: E731
    for col, label in R36_MEASURES:
        xs = [r[col] for r in a if r[col] is not None]
        print(f"| `{col}` | {label} | {g[col]:+.2f} | {d[col]:+.2f} | {min(xs):+.2f}〜{max(xs):+.2f} | {side(g[col], xs)} | {side(d[col], xs)} |")

    print("\n### 2. 得失点差プラスの B と A\n")
    plus = [r for r in rows if r["rd"] > 0]
    pb, pa = [r for r in plus if not r["upper_half"]], [r for r in plus if r["upper_half"]]
    print(f"得失点差プラスの B: {len(pb)}（{', '.join(map(key, sorted(pb, key=lambda r: (r['season'], r['team']))))}）、A: {len(pa)}\n")
    print("| 指標 | 中身 | B の中央値 | A の中央値 | A の四分位（25〜75%） | B のうち A の25%より下 | B のうち A の75%より上 |")
    print("|---|---|---|---|---|---|---|")
    for col, label in R36_MEASURES:
        bv, av = [r[col] for r in pb if r[col] is not None], [r[col] for r in pa if r[col] is not None]
        lo, hi = quartiles(av)
        below, above = sum(v < lo for v in bv), sum(v > hi for v in bv)
        print(f"| `{col}` | {label} | {statistics.median(bv):+.2f} | {statistics.median(av):+.2f} | {lo:+.2f}〜{hi:+.2f} "
              f"| {below}/{len(bv)} | {above}/{len(bv)} |")
    return 0


# ==== r44（旧 r44_cases.py）

def classify_fade(r: dict) -> list[str]:
    """大きく落ちた単位を、計画で決めた規則で分ける（複数に当たってよい）。"""
    tags = []
    if (r["half1_vs_pythag"] or 0) > 3 or (r["course_ra_h1_d"] or 0) < -0.5:
        tags.append("前半が出来すぎ")
    if (r["course_rf_d"] or 0) < 0 and (r["course_ra_d"] or 0) > 0 and (r["half2_vs_pythag"] or 0) < -2:
        tags.append("後半の崩れ")
    return tags or ["どちらでもない"]


def classify_big_inning_b(r: dict) -> list[str]:
    """大きさは上位なのに B の単位を、計画で決めた規則で分ける。"""
    tags = []
    if r["ra_zone_se"] == -1:
        tags.append("失点がはっきり劣る")
    if (r["wins_vs_pythag"] or 0) < -2 or (r["alloc_z_strat"] or 0) < -1:
        tags.append("点の差を勝ちに変えられない")
    return tags or ["どちらでもない"]


def r44(argv: list[str]) -> int:
    """R44: 大きく落ちた7単位と、大きさは上位なのに B の単位を、1単位ずつ並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r44 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の既存のチームの列だけを使う。分け方の規則は R44 の計画で先に決めた（下の classify_*）。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if r["season"] != 2020]

    print("### 大きく落ちた単位（前半の順位より3つ以上下で終わった）\n")
    print("| 単位 | 1/4 → 前半 → 3/4 → 最終 | 前半、点の差より | 前半の失点（他球団比） | 後半の得点 | 後半の失点 | 後半、点の差より | 分け方 |")
    print("|---|---|---|---|---|---|---|---|")
    for r in sorted((r for r in rows if (r["course_fade"] or 0) >= 3), key=lambda r: (r["season"], r["team"])):
        print(f"| {r['team_name']} {r['season']} | {r['course_rank_q1']} → {r['course_rank_h1']} → {r['course_rank_q3']} → {r['rank']} "
              f"| {r['half1_vs_pythag']:+.1f} | {r['course_ra_h1_d']:+.2f} | {r['course_rf_d']:+.2f} | {r['course_ra_d']:+.2f} "
              f"| {r['half2_vs_pythag']:+.1f} | {'・'.join(classify_fade(r))} |")

    print("\n### 得点した回の大きさが上位2位以内なのに B（2013〜2025年）\n")
    print("| 単位 | 順位 | 得点の順位 | 形 | 点の差より | 組み合わせ方 | 上の相手 − 下の相手 | 分け方 |")
    print("|---|---|---|---|---|---|---|---|")
    big = [r for r in rows if r["season"] >= 2013 and (r["inn_size_rank"] or 0) >= 5 and not r["upper_half"]]
    for r in sorted(big, key=lambda r: (r["season"], r["team"])):
        print(f"| {r['team_name']} {r['season']} | {r['rank']} | {r['rank_rf']} | {r['adv_shape_se']} | {r['wins_vs_pythag']:+.1f} "
              f"| {r['alloc_z_strat']:+.2f} | {r['vs_top_minus_lower']:+.2f} | {'・'.join(classify_big_inning_b(r))} |")
    return 0


# ==== r47（旧 r47_third_vs_fourth.py）

# (列, 中身, 大きいほうが3位らしい向きなら +1、小さいほうなら −1)
R47_MEASURES = [
    ("run_balance", "収支（得点の優位 + 失点の優位）", 1),
    ("rf_adv", "得点の優位", 1),
    ("ra_adv", "失点の優位", 1),
    ("wins_vs_pythag", "点の差から見込まれる勝ち数との差", 1),
    ("alloc_z_strat", "得点・失点の組み合わせ方", 1),
    ("one_run_net", "1点差の勝ち − 負け", 1),
    ("vs_top_wpct", "上の相手との勝率", 1),
    ("vs_lower_wpct", "下の相手との勝率", 1),
    ("course_wpct_diff", "後半の勝率 − 前半の勝率", 1),
    ("wave_limit_rank_h1", "前半の線から当てた行き先（小さいほど上）", -1),
    ("sim_p_upper", "得点・失点の分布から見た A の確率", 1),
]


def sign_test_p(k: int, n: int) -> float:
    """両側の符号検定（二項分布、p = 0.5）。"""
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def r47(argv: list[str]) -> int:
    """R47: 同じ年・同じリーグの3位と4位を1組ずつ並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r47 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の既存のチームの列だけを使う。2020年は除く。同率で3位・4位が決まらない年は、その年を外して数える。
    並べる指標と、「3位のほうが上」の向きは R47 の計画で先に決めた（MEASURES）。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line]
    rows = [r for r in rows if r["season"] != 2020]
    pairs = []
    for key in sorted({(r["season"], r["league"]) for r in rows}):
        lg = [r for r in rows if (r["season"], r["league"]) == key]
        third, fourth = [r for r in lg if r["rank"] == 3], [r for r in lg if r["rank"] == 4]
        if len(third) == 1 and len(fourth) == 1:
            pairs.append((third[0], fourth[0]))
    print(f"組: {len(pairs)}（3位・4位が1球団ずつ決まる年）\n")

    print("| 年 | リーグ | 3位 | 4位 | 勝ち数の差（ゲーム差） | 3位の道筋 | 4位の道筋 |")
    print("|---|---|---|---|---|---|---|")
    for t, f in pairs:
        gb = ((t["W"] - t["L"]) - (f["W"] - f["L"])) / 2
        mark = lambda r: f"**{r['team_name']}**" if r["team"] == "d" else r["team_name"]  # noqa: E731
        print(f"| {t['season']} | {t['league']} | {mark(t)} | {mark(f)} | {gb:+.1f} | {t['b_paths']} | {f['b_paths']} |")

    print("\n| 指標 | 中身 | 3位のほうが上の組 | 4位のほうが上 | 同じ・空 | 符号検定 p |")
    print("|---|---|---|---|---|---|")
    for col, label, direction in R47_MEASURES:
        up = down = other = 0
        for t, f in pairs:
            a, b = t[col], f[col]
            if a is None or b is None or a == b:
                other += 1
            elif (a - b) * direction > 0:
                up += 1
            else:
                down += 1
        print(f"| `{col}` | {label} | {up} | {down} | {other} | {sign_test_p(up, up + down):.3f} |")

    print("\n中日が4位の年と、その年の3位:\n")
    print("| 年 | 3位 | ゲーム差 | " + " | ".join(c for c, _, _ in R47_MEASURES[:8]) + " |")
    print("|---|---|---|" + "---|" * 8)
    for t, f in pairs:
        if f["team"] != "d":
            continue
        gb = ((t["W"] - t["L"]) - (f["W"] - f["L"])) / 2
        cells = []
        for col, _, direction in R47_MEASURES[:8]:
            a, b = t[col], f[col]
            cells.append("-" if a is None or b is None else f"{b:+.2f}（3位 {a:+.2f}）")
        print(f"| {f['season']} | {t['team_name']} | {gb:+.1f} | " + " | ".join(cells) + " |")
    return 0


# ==== r51（旧 r51_late.py）

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


def r51(argv: list[str]) -> int:
    """R51: 序盤・中盤・終盤の得点と失点（PR #3 のチーム×年の集計）を、同じ年・同じリーグの他球団と比べる（記述）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r51 cycles/c001-chunichi/references/pr3-inning-team-year-metrics.csv.gz         cycles/c001-chunichi/outputs/season.jsonl

    区切りは集計のまま: 序盤 1〜3回、中盤 4〜6回、終盤 7〜9回（延長は除く）。1回あたりの得点（攻撃）と失点（守備）。
    差し引き = 攻撃 − 守備 を、同じ年・同じリーグの他球団の平均と比べる。チーム単位の集計なので方針の範囲内。
    回ごとの配分は独立に照合していない（FINDINGS 7）。
    """
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


# ==== r52（旧 r52_lines.py）

EXCLUDED = {2020}
FOCUS = "d"
R52_FOCUS_YEARS = set(range(2013, 2026)) - EXCLUDED


def jenks2(wpcts: list[float]) -> int:
    """勝率を高い順に並べ、2つに分けたときに塊の中の偏差平方和の合計が最小になる k（k 位と k+1 位の間）。同じなら上位側。"""
    w = sorted(wpcts, reverse=True)

    def ss(xs):
        m = sum(xs) / len(xs)
        return sum((x - m) ** 2 for x in xs)

    best = min(range(1, len(w)), key=lambda k: (round(ss(w[:k]) + ss(w[k:]), 12), k))
    return best


def unit(r: dict) -> str:
    return f"{r['team']}-{r['season']}"


def r52(argv: list[str]) -> int:
    """R52: 勝率の散らばりから引く線を並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r52 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の既存の列（wpct・rank・upper_half・lg_*）だけを使う。2020年は除く。ネットワークを使わない。
    ばらつき最小の2つの塊（1次元の Jenks / 大津の方法）だけは列にせず、ここで計算する。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    jk = {key: jenks2([r["wpct"] for r in xs]) for key, xs in leagues.items()}
    for r in rows:
        r["jenks_after"] = jk[(r["season"], r["league"])]
    print(f"範囲: {len(leagues)} リーグ・年、{len(rows)} 単位（2020年を除く）")

    # 1・2. 切れ目の位置
    gap = Counter(xs[0]["lg_break_after"] for xs in leagues.values())
    jen = Counter(jk.values())
    agree = sum(xs[0]["lg_break_after"] == jk[key] for key, xs in leagues.items())
    print("\n| 切れ目（k 位と k+1 位の間） | 1 | 2 | 3 | 4 | 5 |\n|---|---|---|---|---|---|")
    print("| いちばん大きな隙間 | " + " | ".join(str(gap.get(k, 0)) for k in range(1, 6)) + " |")
    print("| ばらつき最小の2つの塊 | " + " | ".join(str(jen.get(k, 0)) for k in range(1, 6)) + " |")
    inner = sum(gap.get(k, 0) for k in (2, 3, 4))
    print(f"\nいちばん大きな隙間が 3 に来た: {gap.get(3, 0)}/{len(leagues)}（素朴な目安 1/5 = {len(leagues) / 5:.1f}）。"
          f"端を除いた 2〜4 の中で 3: {gap.get(3, 0)}/{inner}（目安 1/3）")
    print(f"ばらつき最小の切れ目が 3 に来た: {jen.get(3, 0)}/{len(leagues)}。いちばん大きな隙間と一致: {agree}/{len(leagues)}")
    print("\n| 年 | リーグ | 隙間 k | 隙間の差 | 塊の切れ目（2つ）| ばらつき最小 k | 3位と4位の差 |\n|---|---|---|---|---|---|---|")
    for (season, lg), xs in sorted(leagues.items()):
        t = sorted(xs, key=lambda r: r["rank"])
        tiers = [r["lg_tier"] for r in t]
        cuts = [k for k in range(1, 6) if tiers[k] != tiers[k - 1]]
        print(f"| {season} | {lg} | {t[0]['lg_break_after']} | {t[0]['lg_break_gap']:.3f} | {'・'.join(map(str, cuts))} "
              f"| {jk[(season, lg)]} | {t[0]['lg_gap34']:.3f} |")

    # 3. A かどうかと、自然な塊の上下が一致するか
    for name, col in (("いちばん大きな隙間", "lg_break_after"), ("ばらつき最小", "jenks_after")):
        same = sum((r["rank"] <= 3) == (r["rank"] <= r[col]) for r in rows)
        print(f"\nA（3位以内）と「{name}より上」が一致: {same}/{len(rows)} 単位")

    # 4. 中日の B の年
    d = sorted((r for r in rows if r["team"] == FOCUS and r["season"] in R52_FOCUS_YEARS and not r["upper_half"]),
               key=lambda r: r["season"])
    print(f"\n| 中日の B（{len(d)}年） | 順位 | 勝率 | A の線 | 自分の塊 / 3位の塊 | 隙間より上 | ばらつき最小で上 |\n|---|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['rank']} | {r['wpct']:.3f} | {r['lg_line']:.3f} | {r['lg_tier']} / {r['lg_tier_of_3rd']} "
              f"| {'上' if r['rank'] <= r['lg_break_after'] else '下'} | {'上' if r['rank'] <= r['jenks_after'] else '下'} |")
    print(f"3位と同じ塊: {sum(r['lg_tier'] == r['lg_tier_of_3rd'] for r in d)}/{len(d)}、"
          f"隙間より上（3位と同じ側）: {sum(r['rank'] <= r['lg_break_after'] for r in d)}/{len(d)}、"
          f"ばらつき最小で上: {sum(r['rank'] <= r['jenks_after'] for r in d)}/{len(d)}")

    # 5. 全体の四分位の線
    q1, med, q3 = statistics.quantiles([r["wpct"] for r in rows], n=4, method="inclusive")
    print(f"\n全体の四分位: Q1 {q1:.3f}、中央値 {med:.3f}、Q3 {q3:.3f}")
    band = Counter("Q1 未満" if r["wpct"] < q1 else "Q1〜中央値" if r["wpct"] < med else "中央値以上" for r in d)
    print("中日の B: " + "、".join(f"{k} {band.get(k, 0)}" for k in ("Q1 未満", "Q1〜中央値", "中央値以上")))
    for r in d:
        print(f"  {r['season']}: {r['wpct']:.3f}")
    off = sorted((r for r in rows if (r["wpct"] >= med) != bool(r["upper_half"])), key=lambda r: (r["season"], r["league"]))
    print(f"中央値と順位が食い違う単位 {len(off)}: " + ", ".join(
        f"{unit(r)}（{r['rank']}位 {r['wpct']:.3f}）" for r in off))
    above_q3_b = [unit(r) for r in rows if r["wpct"] >= q3 and not r["upper_half"]]
    below_q1_a = [unit(r) for r in rows if r["wpct"] < q1 and r["upper_half"]]
    print(f"Q3 以上の B: {above_q3_b or 'なし'}、Q1 未満の A: {below_q1_a or 'なし'}")
    # 実行後に足した: 四分位の帯ごとの A・B の数（どの帯で A と B が混ざるか）
    bands = (("Q1 未満", lambda w: w < q1), ("Q1〜中央値", lambda w: q1 <= w < med),
             ("中央値〜Q3", lambda w: med <= w < q3), ("Q3 以上", lambda w: w >= q3))
    print("\n| 帯 | A | B | うち中日の B |\n|---|---|---|---|")
    for name, f in bands:
        xs = [r for r in rows if f(r["wpct"])]
        print(f"| {name} | {sum(r['upper_half'] for r in xs)} | {sum(not r['upper_half'] for r in xs)} "
              f"| {sum(1 for r in d if f(r['wpct']))} |")

    # 6. 阪神 2015年
    h = next((r for r in rows if r["team"] == "t" and r["season"] == 2015), None)
    if h:
        print(f"\n阪神 2015年: {h['rank']}位 {h['wpct']:.3f}、A の線 {h['lg_line']:.3f}、塊 {h['lg_tier']} / 3位の塊 {h['lg_tier_of_3rd']}、"
              f"隙間 k {h['lg_break_after']}（{'上' if h['rank'] <= h['lg_break_after'] else '下'}）、"
              f"ばらつき最小 k {h['jenks_after']}（{'上' if h['rank'] <= h['jenks_after'] else '下'}）、"
              f"四分位: {'Q1 未満' if h['wpct'] < q1 else 'Q1〜中央値' if h['wpct'] < med else '中央値以上'}")
    return 0


# ==== r53（旧 r53_line_catalog.py）

R53_FOCUS, R53_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def quantile_lines(w: list[float], k: int) -> list[float]:
    return list(statistics.quantiles(w, n=k, method="inclusive"))


def equal_width_lines(w: list[float], k: int) -> list[float]:
    lo, hi = min(w), max(w)
    return [lo + (hi - lo) * i / k for i in range(1, k)]


def jenks_lines(w: list[float], k: int) -> list[float]:
    """1次元で、k 個の塊の偏差平方和の合計が最小になる分け方の境（隣り合う2つの値の中間）。動的計画法。"""
    x = sorted(w)
    n = len(x)
    s1, s2 = [0.0], [0.0]
    for v in x:
        s1.append(s1[-1] + v)
        s2.append(s2[-1] + v * v)

    def ss(i, j):  # x[i:j]
        m = j - i
        return s2[j] - s2[i] - (s1[j] - s1[i]) ** 2 / m

    inf = float("inf")
    cost = [[inf] * (n + 1) for _ in range(k + 1)]
    back = [[0] * (n + 1) for _ in range(k + 1)]
    cost[0][0] = 0.0
    for c in range(1, k + 1):
        for j in range(c, n + 1):
            for i in range(c - 1, j):
                v = cost[c - 1][i] + ss(i, j)
                if v < cost[c][j] - 1e-15:
                    cost[c][j], back[c][j] = v, i
    cuts, j = [], n
    for c in range(k, 0, -1):
        i = back[c][j]
        if c > 1:
            cuts.append((x[i - 1] + x[i]) / 2)
        j = i
    return sorted(cuts)


def sd_lines(w: list[float], _k: int) -> list[float]:
    m, s = statistics.mean(w), statistics.stdev(w)
    return [m - s, m + s]


FAMILIES = [("分位", quantile_lines, (4, 5, 7)), ("等幅", equal_width_lines, (4, 5, 7)),
            ("塊", jenks_lines, (2, 3, 4, 5, 7)), ("平均±SD", sd_lines, (1,))]


def side(rows: list[dict], line: float) -> tuple[int, int]:
    """（線より下の A の数, 線以上の B の数）"""
    return (sum(1 for r in rows if r["wpct"] < line and r["upper_half"]),
            sum(1 for r in rows if r["wpct"] >= line and not r["upper_half"]))


def r53(argv: list[str]) -> int:
    """R53: 線の引き方の一覧（分位・等幅・塊・平均 ± SD）と、1年抜きで複数年で使えるか（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r53 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の wpct・upper_half だけを使う。2020年は除く。ネットワークを使わない。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    seasons = sorted({r["season"] for r in rows})
    d = [r for r in rows if r["team"] == R53_FOCUS and r["season"] in R53_FOCUS_YEARS and not r["upper_half"]]
    h = next(r for r in rows if r["team"] == "t" and r["season"] == 2015)
    w = [r["wpct"] for r in rows]
    print(f"範囲: {len(rows)} 単位、{len(seasons)} 年（2020年を除く）。中日の B {len(d)}年")
    print("\n| 種類 | k | 番号 | 線 | 下の A | 上の B | 側 | 1年抜きで外れた年 | 中日の B が下 | 阪神 2015 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    usable = []
    for name, f, ks in FAMILIES:
        for k in ks:
            lines = f(w, k)
            held = {s: f([r["wpct"] for r in rows if r["season"] != s], k) for s in seasons}
            for i, line in enumerate(lines):
                a_below, b_above = side(rows, line)
                kind = "B 側" if a_below == 0 else "A 側" if b_above == 0 else "混ざる"
                miss = []
                mixed = 0
                for s in seasons:
                    test = [r for r in rows if r["season"] == s]
                    if len(held[s]) != len(lines):
                        miss.append(f"{s}(線の数が違う)")
                        continue
                    ab, ba = side(test, held[s][i])
                    if kind == "B 側" and ab:
                        miss.append(str(s))
                    elif kind == "A 側" and ba:
                        miss.append(str(s))
                    mixed += ab + ba
                if kind == "混ざる":
                    held_txt = f"混ざり計 {mixed}"
                else:
                    held_txt = f"{len(miss)}（{'・'.join(miss)}）" if miss else "0"
                    if not miss:
                        usable.append(f"{name}{k}-{i + 1} {kind} {line:.3f}")
                below = sum(r["wpct"] < line for r in d)
                print(f"| {name} | {k} | {i + 1} | {line:.3f} | {a_below} | {b_above} | {kind} | {held_txt} "
                      f"| {below}/{len(d)} | {'下' if h['wpct'] < line else '上'} |")
    print(f"\n1年抜きで外れた年が 0 の線（複数年で使える）: {len(usable)}")
    for u in usable:
        print(f"- {u}")
    return 0


# ==== r54（旧 r54_band_edges.py）

EDGES = [("g", 2017), ("g", 2018)]
R54_COLS = [  # (列, 見出し, 書式)。計画で先に決めた順
    ("rank", "順位", "d"), ("W", "勝", "d"), ("L", "負", "d"), ("T", "分", "d"), ("wl", "勝−負", "+d"), ("wpct", "勝率", ".3f"),
    ("lg_line", "A の線", ".3f"), ("to_line", "勝率−線", "+.3f"), ("line_gap_pythag", "点の差で線まで", "+.3f"),
    ("resid_fixed", "点の差より勝った分", "+.3f"),
    ("rf_adv", "得点の優位", "+.2f"), ("ra_adv", "失点の優位", "+.2f"), ("run_balance", "収支", "+.2f"), ("sim_p_upper", "分布から A の確率", ".2f"),
    ("wins_vs_pythag", "点の差より勝った数", "+.1f"), ("one_run_net", "1点差 勝−負", "+d"), ("alloc_z_strat", "組み合わせ方", "+.2f"),
    ("vs_top_wpct", "上の相手との勝率", ".3f"), ("vs_lower_wpct", "下の相手との勝率", ".3f"), ("pair34_net", "3位・4位の直接 勝−負", "+d"),
    ("course_wpct_h1", "前半の勝率", ".3f"), ("course_wpct_h2", "後半の勝率", ".3f"),
    ("clinch_in_x", "A 確定の位置", ".2f"), ("clinch_out_x", "B 確定の位置", ".2f"), ("decided_x", "リーグが決まった位置", ".2f"),
    ("b_paths", "道筋", "s"),
]
SHAPE = [("lg_lead_gap", "1位−2位"), ("lg_gap34", "3位−4位"), ("lg_rest_sd", "1位以外の散らばり"), ("lg_rank_at_500", ".500 の位置")]


def r54_fmt(v, f: str) -> str:
    if v is None or v == "":
        return "-"
    return v if f == "s" else format(v, f)


def r54(argv: list[str]) -> int:
    """R54: 帯の両端（巨人 2017年 = B の最高、巨人 2018年 = A の最低）を、その年のリーグの6球団と並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r54 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の既存のチームの列だけを使う。2020年は植え替え先から除く。ネットワークを使わない。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    for r in rows:
        r["wl"], r["to_line"] = r["W"] - r["L"], r["wpct"] - r["lg_line"]
    leagues: dict = {}
    for r in rows:
        if r["season"] not in EXCLUDED:
            leagues.setdefault((r["season"], r["league"]), []).append(r)

    for team, season in EDGES:
        me = next(r for r in rows if (r["team"], r["season"]) == (team, season))
        lg = sorted(leagues[(season, me["league"])], key=lambda r: r["rank"])
        print(f"\n## {me['team_name']} {season}（{me['rank']}位 {me['wpct']:.3f}）\n")
        print("| 列 | " + " | ".join(f"{r['rank']}位 {r['team_name']}" for r in lg) + " |")
        print("|---|" + "---|" * len(lg))
        for col, label, f in R54_COLS:
            print(f"| {label} | " + " | ".join(("**" + r54_fmt(r.get(col), f) + "**") if r is me else r54_fmt(r.get(col), f) for r in lg) + " |")
        print("\nリーグの形: " + "、".join(f"{label} {me[col]:.3f}" for col, label in SHAPE))
        print(f"恒等式: 勝率−線 {me['to_line']:+.3f} = 点の差で線まで {me['line_gap_pythag']:+.3f} + 点の差より勝った分 {me['resid_fixed']:+.3f}")

        # 植え替え: ほかのリーグ・年に置いたら
        others = [(k, v) for k, v in leagues.items() if k != (season, me["league"])]
        third = lambda v: sorted((r["wpct"] for r in v), reverse=True)[2]  # noqa: E731
        fourth = lambda v: sorted((r["wpct"] for r in v), reverse=True)[3]  # noqa: E731
        above_line = [k for k, v in others if me["wpct"] >= v[0]["lg_line"]]
        above_3rd = [k for k, v in others if me["wpct"] >= third(v)]
        below_4th = [k for k, v in others if me["wpct"] < fourth(v)]
        print(f"植え替え（ほかの {len(others)} リーグ・年）: A の線以上 {len(above_line)}、3位の勝率以上 {len(above_3rd)}、4位の勝率より下 {len(below_4th)}")
        side = above_line if not me["upper_half"] else [k for k, v in others if me["wpct"] < v[0]["lg_line"]]
        print(f"  反対側（{'A' if not me['upper_half'] else 'B'}）になる年: " + ", ".join(f"{s}{l}" for s, l in sorted(side)))
    return 0


# ==== r56（旧 r56_bar.py）

WATCH = [("t", 2015), ("g", 2017), ("g", 2018)]
R56_MEASURES = [  # (列, 中身, A らしい向き: +1 = A が高い, −1 = A が低い)。計画で先に決めた
    ("wpct", "勝率（自分）", 1), ("pythag_fixed", "点の差で見込む勝率（自分）", 1), ("resid_fixed", "点の差より勝った分（自分）", 1),
    ("bar", "越えるべき高さ（外）", -1), ("lg_rank_at_500", ".500 の位置（外）", -1),
]


def r56_share(a: list[float], b: list[float], sign: int) -> float:
    pairs = [(x, y) for x in a for y in b]
    score = sum(1.0 if sign * (x - y) > 0 else 0.5 if x == y else 0.0 for x, y in pairs)
    return score / len(pairs)


def r56(argv: list[str]) -> int:
    """R56: 帯の中（mix_zone = 0）の単位で、A・B を分けたのは自分の側か外の側（越えるべき高さ）か（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r56 cycles/c001-chunichi/outputs/season.jsonl

    bar = 同じ年・同じリーグのほかの5球団の中で3番目の勝率（A に入るために上回るべき高さ）。2020年は除く。ネットワークを使わない。
    比べ方: A と B のすべての組のうち、A の側が先に決めた「A らしい向き」になっている組の割合（同じ値は 0.5 と数える）。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    for r in rows:
        others = sorted((o["wpct"] for o in rows if (o["season"], o["league"]) == (r["season"], r["league"]) and o["team"] != r["team"]),
                        reverse=True)
        r["bar"] = others[2]
    band = [r for r in rows if r["mix_zone"] == 0]
    a, b = [r for r in band if r["upper_half"]], [r for r in band if not r["upper_half"]]
    print(f"帯の中: {len(band)} 単位（A {len(a)}・B {len(b)}）、組 {len(a) * len(b)}")
    print("\n| 列 | 中身 | A らしい向きの組の割合 | A の中央値 | B の中央値 |\n|---|---|---|---|---|")
    import statistics
    for col, label, sign in R56_MEASURES:
        av, bv = [r[col] for r in a], [r[col] for r in b]
        print(f"| `{col}` | {label} | {r56_share(av, bv, sign):.2f} | {statistics.median(av):.3f} | {statistics.median(bv):.3f} |")
    print("\n| 単位 | 順位 | 勝率 | bar | 勝率 − bar | 帯 |\n|---|---|---|---|---|---|")
    for r in sorted(band, key=lambda r: r["wpct"] - r["bar"]):
        mark = " ←" if (r["team"], r["season"]) in WATCH else ""
        print(f"| {r['team']}-{r['season']}{mark} | {r['rank']} | {r['wpct']:.3f} | {r['bar']:.3f} | {r['wpct'] - r['bar']:+.3f} | {r['mix_zone']} |")
    for t, s in WATCH:
        r = next(x for x in rows if (x["team"], x["season"]) == (t, s))
        print(f"{t}-{s}: 勝率 {r['wpct']:.3f}、bar {r['bar']:.3f}、帯 {r['mix_zone']}")
    return 0


# ==== r57（旧 r57_live_dead.py）

R57_FOCUS, R57_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def f(v, spec):
    return "-" if v is None else format(v, spec)


def r57(argv: list[str]) -> int:
    """R57: A・B に効く試合（live）と、決まった後の試合（dead）を並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r57 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の rank_fixed_*・live_*・dead_*・clinch_*・mix_* の列だけを使う。2020年は除く。ネットワークを使わない。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    a = [r for r in rows if r["upper_half"]]
    b = [r for r in rows if not r["upper_half"]]
    d = sorted((r for r in rows if r["team"] == R57_FOCUS and r["season"] in R57_FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])

    # 1. 効かない試合の量
    dg = [r["dead_g"] for r in rows]
    print(f"1. 効かない試合: 全 {len(rows)} 単位の中央値 {med(dg)}、最大 {max(dg)}、0 の単位 {sum(x == 0 for x in dg)}。"
          f"A の中央値 {med([r['dead_g'] for r in a])}、B の中央値 {med([r['dead_g'] for r in b])}")
    print("\n| 中日 | 順位 | B 確定の位置 | 残り | 効く試合 | 効かない試合 | 効く試合の勝率 | 効かない試合の勝率 | 順位確定の位置 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['rank']} | {f(r['clinch_out_x'], '.2f')} | {f(r['clinch_out_left'], 'd')} | {r['live_g']} | {r['dead_g']} "
              f"| {f(r['live_wpct'], '.3f')} | {f(r['dead_wpct'], '.3f')} | {f(r['rank_fixed_x'], '.2f')} |")

    # 2. 最終順位の確定
    print("\n2. | 順位 | 単位 | 確定した単位 | 確定の位置の中央値 | 確定した日の残り試合の中央値 |\n|---|---|---|---|---|")
    for k in range(1, 7):
        xs = [r for r in rows if r["rank"] == k]
        fx = [r for r in xs if r["rank_fixed_x"] is not None]
        print(f"| {k} | {len(xs)} | {len(fx)} | {f(med([r['rank_fixed_x'] for r in fx]), '.2f')} | {f(med([r['rank_fixed_left'] for r in fx]), '')} |")

    # 3. 決まった後に勝ち方が変わるか
    print("\n3. | 決まった側 | 単位（効かない試合あり） | 勝率の差（後 − 前）の中央値 | 点の差/試合の差の中央値 | 後のほうが勝率が高い単位 |\n|---|---|---|---|---|")
    for name, xs in (("A が確定", [r for r in a if r["dead_g"]]), ("B が確定", [r for r in b if r["dead_g"]]),
                     ("中日の B", [r for r in d if r["dead_g"]])):
        dw = [r["dead_wpct"] - r["live_wpct"] for r in xs if r["dead_wpct"] is not None and r["live_wpct"] is not None]
        dr = [r["dead_rd_g"] - r["live_rd_g"] for r in xs if r["dead_rd_g"] is not None and r["live_rd_g"] is not None]
        print(f"| {name} | {len(xs)} | {f(med(dw), '+.3f')} | {f(med(dr), '+.2f')} | {sum(x > 0 for x in dw)}/{len(dw)} |")

    # 4. 効く試合だけの勝率で、中日の B は帯のどこか
    lo, hi = med([r["mix_lo"] for r in rows]), med([r["mix_hi"] for r in rows])
    zone = lambda w: "下" if w < lo else "上" if w > hi else "中"  # noqa: E731
    print(f"\n4. 帯（全試合の勝率で引いた値の中央値）{lo:.3f}〜{hi:.3f}。中日の B の効く試合だけの勝率: "
          + "、".join(f"{r['season']} {r['live_wpct']:.3f}（{zone(r['live_wpct'])}）" for r in d))
    print("   帯の下 {} / 中 {} / 上 {}".format(*(sum(zone(r["live_wpct"]) == z for r in d) for z in "下中上")))

    # 5. 効かない試合が多い単位
    top = sorted(rows, key=lambda r: -r["dead_g"])[:12]
    print("\n5. 効かない試合が多い順: " + ", ".join(
        f"{r['team']}-{r['season']}（{r['rank']}位、{r['dead_g']}試合、前 {f(r['live_wpct'], '.3f')} → 後 {f(r['dead_wpct'], '.3f')}）" for r in top))
    return 0


# ==== r58（旧 r58_three_states.py）

R58_FOCUS, R58_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def band(pool, col):
    a = [r[col] for r in pool if r["upper_half"] and r[col] is not None]
    b = [r[col] for r in pool if not r["upper_half"] and r[col] is not None]
    return min(a), max(b)


SCHEMES = [  # (名前, 値の列, 線を引く関数)。計画で先に決めた
    ("帯", "wpct", lambda pool: band(pool, "wpct")),
    ("塊3", "wpct", lambda pool: tuple(jenks_lines([r["wpct"] for r in pool], 3))),
    ("三分位", "wpct", lambda pool: tuple(statistics.quantiles([r["wpct"] for r in pool], n=3, method="inclusive"))),
    ("平均±SD", "wpct", lambda pool: (statistics.mean(w := [r["wpct"] for r in pool]) - statistics.stdev(w),
                                      statistics.mean(w) + statistics.stdev(w))),
    ("効く試合の帯", "live_wpct", lambda pool: band(pool, "live_wpct")),
]


def state_of(v, lo, hi):
    return "B" if v < lo else "A" if v > hi else "AB"


def rank_state(k):
    return "A" if k <= 2 else "AB" if k <= 4 else "B"   # 2.5位と 4.5位の2本の線


def r58(argv: list[str]) -> int:
    """R58: 2本の線で3つの状態（A・AB・B）と、時期をまたぐ動き（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r58 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の wpct・live_wpct・upper_half・course_rank_* だけを使う。線は1年抜き（自分の年を除いたほかの年）。2020年は除く。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    seasons = sorted({r["season"] for r in rows})
    d = sorted((r for r in rows if r["team"] == R58_FOCUS and r["season"] in R58_FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    unit = lambda r: f"{r['team']}-{r['season']}"  # noqa: E731

    print("## 1. 2本の線で3つの状態\n")
    print("| 組 | 線（中央値） | A の状態: A / 計 | AB の状態: A / 計 | B の状態: B / 計 | 中日の B（A・AB・B） |\n|---|---|---|---|---|---|")
    states = {}
    for name, col, lines in SCHEMES:
        cut = {s: lines([r for r in rows if r["season"] != s]) for s in seasons}
        st = {unit(r): state_of(r[col], *cut[r["season"]]) for r in rows}
        states[name] = st
        c = Counter((st[unit(r)], r["upper_half"]) for r in rows)
        dd = Counter(st[unit(r)] for r in d)
        lo, hi = statistics.median(v[0] for v in cut.values()), statistics.median(v[1] for v in cut.values())
        print(f"| {name} | {lo:.3f}〜{hi:.3f} | {c[('A', True)]}/{c[('A', True)] + c[('A', False)]} "
              f"| {c[('AB', True)]}/{c[('AB', True)] + c[('AB', False)]} | {c[('B', False)]}/{c[('B', True)] + c[('B', False)]} "
              f"| {dd['A']}・{dd['AB']}・{dd['B']} |")
        if name == "効く試合の帯":
            print("\n効く試合の帯の年ごとの線: " + "、".join(f"{s} {v[0]:.3f}〜{v[1]:.3f}" for s, v in cut.items()))
            wrong = [f"{unit(r)}（{r['rank']}位 {r['live_wpct']:.3f}）" for r in rows
                     if (st[unit(r)] == "A" and not r["upper_half"]) or (st[unit(r)] == "B" and r["upper_half"])]
            print(f"状態と最後が食い違う単位: {', '.join(wrong) or 'なし'}")
            moved = [f"{unit(r)}（全試合 {states['帯'][unit(r)]} → 効く試合 {st[unit(r)]}）" for r in rows
                     if states["帯"][unit(r)] != st[unit(r)]]
            print(f"全試合の帯と状態が変わった単位 {len(moved)}: {', '.join(moved)}")
            for t, s in (("g", 2017), ("g", 2018), ("t", 2015)):
                r = next(x for x in rows if (x["team"], x["season"]) == (t, s))
                print(f"  {t}-{s}: 全試合 {r['wpct']:.3f}（{states['帯'][unit(r)]}）、効く試合 {r['live_wpct']:.3f}（{st[unit(r)]}）")

    print("\n## 2. 時期をまたぐ動き（順位の 2.5位・4.5位の線）\n")
    print("| 時点 | A の状態 → 最後 A | AB の状態 → 最後 A | B の状態 → 最後 A |\n|---|---|---|---|")
    for col, label in (("course_rank_q1", "1/4"), ("course_rank_h1", "1/2"), ("course_rank_q3", "3/4")):
        c = Counter((rank_state(r[col]), r["upper_half"]) for r in rows)
        print(f"| {label} | " + " | ".join(f"{c[(s, True)]}/{c[(s, True)] + c[(s, False)]}" for s in ("A", "AB", "B")) + " |")
    print("\n| 1/2 の時点の順位 | 1 | 2 | 3 | 4 | 5 | 6 |\n|---|---|---|---|---|---|---|")
    c = Counter((r["course_rank_h1"], r["upper_half"]) for r in rows)
    print("| 最後 A / 計 | " + " | ".join(f"{c[(k, True)]}/{c[(k, True)] + c[(k, False)]}" for k in range(1, 7)) + " |")

    path = lambda r: " → ".join(rank_state(r[c]) for c in ("course_rank_q1", "course_rank_h1", "course_rank_q3")) \
        + f" ⇒ {'A' if r['upper_half'] else 'B'}"  # noqa: E731
    paths = Counter(path(r) for r in rows)
    print("\n動きの型（多い順）: " + "、".join(f"{p}: {n}" for p, n in paths.most_common()))
    print("\n中日の B 12年: " + "、".join(f"{r['season']} {path(r)}" for r in d))
    a_to_b = [r for r in rows if not r["upper_half"] and "A" in [rank_state(r[c]) for c in ("course_rank_q1", "course_rank_h1", "course_rank_q3")]]
    print(f"\nA の状態を通って B で終わった（A から B）: {len(a_to_b)} 単位: " + ", ".join(f"{unit(r)}（{path(r)}）" for r in a_to_b))
    b_to_a = [r for r in rows if r["upper_half"] and "B" in [rank_state(r[c]) for c in ("course_rank_q1", "course_rank_h1", "course_rank_q3")]]
    print(f"B の状態を通って A で終わった（B から A）: {len(b_to_a)} 単位: " + ", ".join(f"{unit(r)}（{path(r)}）" for r in b_to_a))
    return 0


# ==== r59（旧 r59_fielding.py）

R59_FOCUS, R59_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED
R59_COLS = ["fld_d_e_g", "fld_d_fpct", "fld_d_dp_g", "fld_d_pb_g"]


def r59_share(a, b, sign):
    """a と b のすべての組のうち sign * (a − b) > 0 の割合（同じ値は 0.5）。"""
    pairs = [(x, y) for x in a for y in b]
    return sum(1.0 if sign * (x - y) > 0 else 0.5 if x == y else 0.0 for x, y in pairs) / len(pairs)


def r59(argv: list[str]) -> int:
    """R59: チームの失策と、勝ち方・帯の中・中日の B を並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r59 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の fld_*・resid_fixed・mix_zone・run_balance_t だけを使う。2020年は除く。ネットワークを使わない。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED and r.get("fld_e_g") is not None]
    d = sorted((r for r in rows if r["team"] == R59_FOCUS and r["season"] in R59_FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    print(f"範囲: {len(rows)} 単位")

    print("\n1. | 中日 | 順位 | 失策/試合 | 他球団との差 | 守備率の差 | 併殺/試合の差 |\n|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['rank']} | {r['fld_e_g']:.3f} | {r['fld_d_e_g']:+.3f} | {r['fld_d_fpct']:+.4f} | {r['fld_d_dp_g']:+.3f} |")
    print(f"他球団より失策が少ない年: {sum(r['fld_d_e_g'] < 0 for r in d)}/{len(d)}")

    print("\n| 比べ | 群 | 失策が少ない向きの割合（fld_d_e_g） | 守備率が高い向き | 併殺が多い向き |\n|---|---|---|---|---|")
    groups = [
        ("2. 勝ち方", [r for r in rows if r["resid_fixed"] > 0], [r for r in rows if r["resid_fixed"] < 0], "点の差より勝った / 負けた"),
        ("3. 帯の中", [r for r in rows if r["mix_zone"] == 0 and r["upper_half"]],
         [r for r in rows if r["mix_zone"] == 0 and not r["upper_half"]], "A / B"),
        ("参考: 全体", [r for r in rows if r["upper_half"]], [r for r in rows if not r["upper_half"]], "A / B"),
    ]
    for name, a, b, label in groups:
        print(f"| {name} | {label}（{len(a)} / {len(b)}） | {r59_share([r['fld_d_e_g'] for r in a], [r['fld_d_e_g'] for r in b], -1):.2f} "
              f"| {r59_share([r['fld_d_fpct'] for r in a], [r['fld_d_fpct'] for r in b], 1):.2f} "
              f"| {r59_share([r['fld_d_dp_g'] for r in a], [r['fld_d_dp_g'] for r in b], 1):.2f} |")

    big = [r for r in d if r["run_balance_t"] <= -1]
    small = [r for r in d if r["run_balance_t"] > -1]
    print(f"\n4. 中日の大きな不足 {len(big)}年: 失策の差の中央値 {statistics.median(r['fld_d_e_g'] for r in big):+.3f}、"
          f"勝ち方で落とした（不足は誤差の内）{len(small)}年: {statistics.median(r['fld_d_e_g'] for r in small):+.3f}"
          f"（{', '.join(str(r['season']) + ' ' + format(r['fld_d_e_g'], '+.3f') for r in small)}）")
    for t, s in (("t", 2015), ("g", 2017), ("g", 2018)):
        r = next(x for x in rows if (x["team"], x["season"]) == (t, s))
        print(f"5. {t}-{s}: 失策/試合 {r['fld_e_g']:.3f}、他球団との差 {r['fld_d_e_g']:+.3f}、守備率の差 {r['fld_d_fpct']:+.4f}")
    return 0


# ==== r60（旧 r60_settle.py）

R60_FOCUS, R60_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def q(xs):
    xs = sorted(xs)
    a, m, b = statistics.quantiles(xs, n=4, method="inclusive")
    return f"{a:.0f}・{m:.0f}・{b:.0f}"


def sign(v):
    return "+" if v > 0 else "−" if v < 0 else "0"


def r60(argv: list[str]) -> int:
    """R60: 順位表で A・B の側が落ち着いた試合数（N）と、区間ごとの勝 − 敗の並び（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r60 cycles/c001-chunichi/outputs/season.jsonl

    season.jsonl の lock_*・lg_set_lock_x・q_wl_*・lone_down_n・clinch_*・course_rank_q3 だけを使う。2020年は除く。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    a, b = [r for r in rows if r["upper_half"]], [r for r in rows if not r["upper_half"]]
    d = sorted((r for r in rows if r["team"] == R60_FOCUS and r["season"] in R60_FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    pat = lambda r: " ".join(sign(r[f"q_wl_{k}"]) for k in range(1, 5))  # noqa: E731

    print(f"1. N（lock_g）の四分位（Q1・中央値・Q3）: 全体 {q([r['lock_g'] for r in rows])}、A {q([r['lock_g'] for r in a])}、B {q([r['lock_g'] for r in b])}")
    print("   落ち着いていた単位の割合: " + "、".join(
        f"{n}試合 {sum(r['lock_g'] <= n for r in rows) / len(rows):.0%}" for n in range(10, 150, 10)))
    sets = {(r["season"], r["league"]): r["lg_set_lock_x"] for r in rows}
    print(f"   リーグの上位半分の顔ぶれが落ち着いた位置の中央値: {statistics.median(sets.values()):.2f}（{len(sets)} リーグ・年）")

    print("\n2. | 中日 | 順位 | N（試合） | 落ち着いた位置 | 数の上で B が決まった位置 | 間（位置） | 区間の並び |\n|---|---|---|---|---|---|---|")
    for r in d:
        gap = r["clinch_out_x"] - r["lock_x"] if r["clinch_out_x"] is not None else None
        print(f"| {r['season']} | {r['rank']} | {r['lock_g']} | {r['lock_x']:.2f} | {r['clinch_out_x']:.2f} | {gap:+.2f} | {pat(r)} |")
    ob = [r for r in b if r["team"] != R60_FOCUS]
    print(f"   中日以外の B の N の中央値 {statistics.median(r['lock_g'] for r in ob):.0f}、中日の B の N の中央値 {statistics.median(r['lock_g'] for r in d):.0f}")

    mid = [r for r in rows if 3 <= r["course_rank_q3"] <= 4]
    ma, mb = [r for r in mid if r["upper_half"]], [r for r in mid if not r["upper_half"]]
    print(f"\n3. 3/4 の時点で AB の状態: {len(mid)}（最後 A {len(ma)}・B {len(mb)}）")
    print(f"   N の中央値: 最後 A {statistics.median(r['lock_g'] for r in ma):.0f}、最後 B {statistics.median(r['lock_g'] for r in mb):.0f}")
    pairs = [(x, y) for x in ma for y in mb]
    sh = sum(1.0 if x["q_wl_4"] > y["q_wl_4"] else 0.5 if x["q_wl_4"] == y["q_wl_4"] else 0.0 for x, y in pairs) / len(pairs)
    print(f"   最後の区間の勝 − 敗が A の側で大きい組の割合: {sh:.2f}")
    for name, xs in (("最後 A", ma), ("最後 B", mb)):
        c = Counter(pat(r) for r in xs)
        print(f"   {name} の区間の並び: " + "、".join(f"{p}: {n}" for p, n in c.most_common()))
    print("   最後の区間の符号 × 最後: " + "、".join(
        f"{s} → A {sum(sign(r['q_wl_4']) == s for r in ma)}・B {sum(sign(r['q_wl_4']) == s for r in mb)}" for s in "+0−"))

    lone = [r for r in rows if r["lone_down_n"] >= 1]
    print(f"\n4. 自分だけ負け越した区間がある単位: {len(lone)}（A {sum(r['upper_half'] for r in lone)}・B {sum(not r['upper_half'] for r in lone)}）")
    print("   中日: " + ("、".join(f"{r['season']}（{r['lone_down_n']}区間、{pat(r)}）" for r in rows if r["team"] == R60_FOCUS and r["lone_down_n"]) or "なし"))

    for t, s in (("t", 2015), ("g", 2017), ("g", 2018)):
        r = next(x for x in rows if (x["team"], x["season"]) == (t, s))
        print(f"5. {t}-{s}: N {r['lock_g']}（位置 {r['lock_x']:.2f}）、区間 {pat(r)}（{', '.join(str(r[f'q_wl_{k}']) for k in range(1, 5))}）")
    return 0


# ==== r61（旧 r61_after.py）

R61_FOCUS, R61_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def r61(argv: list[str]) -> int:
    """R61: 落ち着いた後の戦い方、近似の線と N、12球団ごとの同じ指標（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r61 cycles/c001-chunichi/outputs/season.jsonl
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    a, b = [r for r in rows if r["upper_half"]], [r for r in rows if not r["upper_half"]]
    d = sorted((r for r in rows if r["team"] == R61_FOCUS and r["season"] in R61_FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    ob = [r for r in b if r["team"] != R61_FOCUS]

    print("## 1. 落ち着いた後\n")
    for name, xs in (("A", a), ("B", b), ("中日以外の B", ob), ("中日の B", d)):
        print(f"- {name}（{len(xs)}）: 前 {f(med([r['pre_lock_wpct'] for r in xs]), '.3f')} → 後 {f(med([r['post_lock_wpct'] for r in xs]), '.3f')}、"
              f"後の試合数の中央値 {f(med([r['post_lock_g'] for r in xs]), '.0f')}")
    print("\n| 中日 | N | 前の勝率 | 後の試合 | 後の勝率 |\n|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['lock_g']} | {f(r['pre_lock_wpct'], '.3f')} | {r['post_lock_g']} | {f(r['post_lock_wpct'], '.3f')} |")
    for name, xs in (("中日の B", d), ("中日以外の B", ob)):
        ok = [r for r in xs if r["post_lock_wpct"] is not None]
        print(f"落ち着いた後 .500 以上: {name} {sum(r['post_lock_wpct'] >= 0.5 for r in ok)}/{len(ok)}")

    print("\n## 2. 近似の線と N\n")
    pair = [r for r in rows if r.get("wave_settle_x") is not None and r["lock_x"] is not None]
    diff = [r["wave_settle_x"] - r["lock_x"] for r in pair]
    print(f"波の決まった位置 − 順位表の落ち着いた位置: {len(pair)} 単位、中央値 {med(diff):+.2f}、"
          f"波が早い {sum(x < 0 for x in diff)}・同じ {sum(x == 0 for x in diff)}・遅い {sum(x > 0 for x in diff)}")
    h1 = [r for r in rows if r.get("wave_limit_rank_h1") is not None]
    hit = sum((r["wave_limit_rank_h1"] <= 3.5) == bool(r["upper_half"]) for r in h1)
    print(f"前半だけの波の行き先の側と最後の A・B の一致: {hit}/{len(h1)}（行き先なし {len(rows) - len(h1)}）")
    print("\n| 中日 | 前半の波の行き先 | 全体の波の行き先 | 波の決まった位置 | 順位表の落ち着いた位置 | 波の当てはまりの差 |\n|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {f(r.get('wave_limit_rank_h1'), '.1f')} | {f(r.get('wave_limit_rank'), '.1f')} | {f(r.get('wave_settle_x'), '.2f')} "
              f"| {r['lock_x']:.2f} | {f(r.get('wave_rmse'), '.2f')} |")

    print("\n## 3. 12球団ごと\n")
    print("| 球団 | B の年 | N の中央値（B） | 4区間とも負け越し | 自分だけ負け越した区間 | 3/4 で3〜4位 → A | 落ち着いた後の勝率（B） |\n|---|---|---|---|---|---|---|")
    teams = sorted({(r["team"], r["team_name"]) for r in rows})
    table = []
    for t, name in teams:
        xs = [r for r in rows if r["team"] == t]
        bs = [r for r in xs if not r["upper_half"]]
        allneg = sum(all(r[f"q_wl_{k}"] < 0 for k in range(1, 5)) for r in xs)
        mid = [r for r in xs if 3 <= r["course_rank_q3"] <= 4]
        row = (name, len(bs), med([r["lock_g"] for r in bs]), allneg, sum(r["lone_down_n"] for r in xs),
               f"{sum(r['upper_half'] for r in mid)}/{len(mid)}", med([r["post_lock_wpct"] for r in bs]))
        table.append(row)
        print(f"| {row[0]} | {row[1]} | {f(row[2], '.0f')} | {row[3]} | {row[4]} | {row[5]} | {f(row[6], '.3f')} |")
    me = next(r for r in table if r[0] == "中日")
    print(f"\n中日の位置: B の年 {sorted((r[1] for r in table), reverse=True).index(me[1]) + 1}番目に多い、"
          f"4区間とも負け越し {sorted((r[3] for r in table), reverse=True).index(me[3]) + 1}番目に多い（同数は上の順位）")
    return 0


# ==== r62（旧 r62_last_quarter.py）

R62_FOCUS, R62_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED
R62_MEASURES = [  # (列, 中身, A らしい向き: +1 = A が大きい, −1 = A が小さい, 0 = 決めない)。計画で先に決めた
    ("q4_rd_g", "最後の区間の点の差/試合", 1), ("q4_one_run_net", "最後の区間の1点差 勝−負", 1),
    ("q4_wl_vs_upper", "最後の区間の上の相手 勝−負", 1), ("q4_wl_vs_lower", "最後の区間の下の相手 勝−負", 1),
    ("q4_live_g", "最後の区間の効く試合", 0), ("lg_bar", "越えるべき高さ", -1), ("fld_d_e_g", "失策の差（シーズン合計）", -1),
]


def share(a, b, sign):
    pairs = [(x, y) for x in a for y in b]
    return sum(1.0 if sign * (x - y) > 0 else 0.5 if x == y else 0.0 for x, y in pairs) / len(pairs)


def r62(argv: list[str]) -> int:
    """R62: 3/4 で3〜4位から最後の区間で何が分けたか、行き先の出ない線、決まった区切りでの比べ（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r62 cycles/c001-chunichi/outputs/season.jsonl
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    for r in rows:
        r["q4_live_g"] = max(0, r["q4_g"] - r["dead_g"])
    mid = [r for r in rows if 3 <= r["course_rank_q3"] <= 4]
    ma, mb = [r for r in mid if r["upper_half"]], [r for r in mid if not r["upper_half"]]

    print(f"## 1. 3/4 で3〜4位の {len(mid)} 単位（最後 A {len(ma)}・B {len(mb)}）\n")
    print("| 列 | 中身 | A らしい向きの組の割合 | A の中央値 | B の中央値 |\n|---|---|---|---|---|")
    for col, label, sign in R62_MEASURES:
        av, bv = [r[col] for r in ma if r[col] is not None], [r[col] for r in mb if r[col] is not None]
        sh = f"{share(av, bv, sign):.2f}" if sign else "（向きなし）"
        print(f"| `{col}` | {label} | {sh} | {med(av):+.2f} | {med(bv):+.2f} |")
    cols = ["q4_rd_g", "q4_one_run_net", "q4_wl_vs_upper", "q4_wl_vs_lower", "q4_live_g", "lg_bar", "fld_d_e_g", "q_wl_4"]
    print("\n| 単位 | 最後 | " + " | ".join(cols) + " |\n|---|---|" + "---|" * len(cols))
    for r in sorted((r for r in mid if r["team"] in ("d", "db")), key=lambda r: (r["team"], r["season"])):
        print(f"| {r['team']}-{r['season']} | {'A' if r['upper_half'] else 'B'} | " + " | ".join(
            f(r[c], "+.2f" if isinstance(r[c], float) else "+d") for c in cols) + " |")

    print("\n## 2. 前半の線の行き先が出ない単位\n")
    no = [r for r in rows if r.get("wave_limit_rank_h1") is None]
    yes = [r for r in rows if r.get("wave_limit_rank_h1") is not None]
    for name, xs in (("出ない", no), ("出る", yes)):
        print(f"- {name} {len(xs)}: A {sum(r['upper_half'] for r in xs)}・B {sum(not r['upper_half'] for r in xs)}、"
              f"最後の順位 {dict(sorted(Counter(r['rank'] for r in xs).items()))}、全体の行き先あり {sum(r.get('wave_limit_rank') is not None for r in xs)}、"
              f"波あり {sum(bool(r.get('wave_osc')) for r in xs)}、減衰の中央値 {f(med([r.get('wave_decay') for r in xs]), '.2f')}、"
              f"N の中央値 {f(med([r['lock_g'] for r in xs]), '.0f')}")
    print("  中日: " + "、".join(f"{r['season']}（{r['rank']}位）" for r in no if r["team"] == R62_FOCUS))

    print("\n## 3. 決まった区切りでの比べ\n")
    d = [r for r in rows if r["team"] == R62_FOCUS and r["season"] in R62_FOCUS_YEARS and not r["upper_half"]]
    ob = [r for r in rows if not r["upper_half"] and r["team"] != R62_FOCUS]
    print("| 群 | 後半 − 前半の勝率 | 区間1 | 区間2 | 区間3 | 区間4 |\n|---|---|---|---|---|---|")
    for name, xs in (("A", [r for r in rows if r["upper_half"]]), ("B", [r for r in rows if not r["upper_half"]]),
                     ("中日以外の B", ob), ("中日の B", d)):
        print(f"| {name}（{len(xs)}） | {med([r['course_wpct_diff'] for r in xs]):+.3f} | "
              + " | ".join(f"{med([r[f'q_wl_{k}'] for r in xs]):+.1f}" for k in range(1, 5)) + " |")
    return 0


# ==== r63（旧 r63_split.py）

R63_FOCUS, R63_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def route(r):
    big = r["run_balance_t"] <= -1
    return ("大きな不足" if big else "不足は誤差の内") + "・" + ("点の差より勝った" if r["resid_fixed"] > 0 else "点の差より負けた")


def r63(argv: list[str]) -> int:
    """R63: 中日の B の「前半から見えた6年」と「形が定まらなかった6年」、後半の下がりを効く試合で分ける（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r63 cycles/c001-chunichi/outputs/season.jsonl
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    d = sorted((r for r in rows if r["team"] == R63_FOCUS and r["season"] in R63_FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    seen = [r for r in d if r.get("wave_limit_rank_h1") is not None]
    unformed = [r for r in d if r.get("wave_limit_rank_h1") is None]

    print("## 1. 前半から見えた年と、形が定まらなかった年\n")
    print("| 組 | 年 | 順位 | 道 | 収支 ÷ 誤差 | 点の差より勝った分 | 得点の優位 | 失点の優位 |\n|---|---|---|---|---|---|---|---|")
    for name, xs in (("見えた", seen), ("定まらない", unformed)):
        for r in xs:
            print(f"| {name} | {r['season']} | {r['rank']} | {route(r)} | {r['run_balance_t']:+.2f} | {r['resid_fixed']:+.3f} "
                  f"| {r['rf_adv']:+.2f} | {r['ra_adv']:+.2f} |")
    for name, xs in (("見えた", seen), ("定まらない", unformed)):
        print(f"- {name}（{len(xs)}）: 収支 ÷ 誤差 {med([r['run_balance_t'] for r in xs]):+.2f}、点の差より勝った分 {med([r['resid_fixed'] for r in xs]):+.3f}、"
              f"得点の優位 {med([r['rf_adv'] for r in xs]):+.2f}、失点の優位 {med([r['ra_adv'] for r in xs]):+.2f}、"
              f"大きな不足 {sum(r['run_balance_t'] <= -1 for r in xs)}、点の差より勝った {sum(r['resid_fixed'] > 0 for r in xs)}")

    print("\n## 2. 後半の下がりは効く試合か\n")
    print("| 中日 | 前半 | 後半 | 後半の効く試合だけ | 後半の効く試合の数 |\n|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['course_wpct_h1']:.3f} | {r['course_wpct_h2']:.3f} | {r['h2_live_wpct']:.3f} | {r['h2_live_g']} |")
    ob = [r for r in rows if not r["upper_half"] and r["team"] != R63_FOCUS]
    for name, xs in (("中日の B", d), ("中日以外の B", ob), ("A", [r for r in rows if r["upper_half"]])):
        h1, h2, lv = med([r["course_wpct_h1"] for r in xs]), med([r["course_wpct_h2"] for r in xs]), med([r["h2_live_wpct"] for r in xs])
        print(f"- {name}（{len(xs)}）: 前半 {h1:.3f}、後半 {h2:.3f}（{h2 - h1:+.3f}）、後半の効く試合だけ {lv:.3f}（{lv - h1:+.3f}）、"
              f"後半の効く試合の数 {med([r['h2_live_g'] for r in xs]):.0f}")
    lower = sum(r["h2_live_wpct"] < r["course_wpct_h1"] for r in d)
    print(f"中日の B で、後半の効く試合だけでも前半より低い年: {lower}/{len(d)}")
    return 0


# ==== r64（旧 r64_halves.py）

R64_FOCUS, R64_FOCUS_YEARS = "d", set(range(2013, 2026)) - EXCLUDED


def r64_per_game(r, prefix, side):
    """勝 − 敗を、その半分の同じリーグの相手との試合数がわからないので、半分の試合数で割る（目安）。"""
    g = r["h2_live_g"] if prefix == "h2_live" else r["G"] // 2
    return r[f"{prefix}_wl_vs_{side}"] / g if g else None


def r64(argv: list[str]) -> int:
    """R64: 前半と後半の効く試合を、相手（上・下）と点の差で分ける。中日の見えた年の失点の優位（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r64 cycles/c001-chunichi/outputs/season.jsonl
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] not in EXCLUDED]
    d = sorted((r for r in rows if r["team"] == R64_FOCUS and r["season"] in R64_FOCUS_YEARS and not r["upper_half"]), key=lambda r: r["season"])
    groups = (("A", [r for r in rows if r["upper_half"]]), ("B", [r for r in rows if not r["upper_half"]]),
              ("中日以外の B", [r for r in rows if not r["upper_half"] and r["team"] != R64_FOCUS]), ("中日の B", d))

    print("## 1. 前半 → 後半の効く試合\n")
    print("| 群 | 点の差/試合 | 上の相手 勝−負 | 下の相手 勝−負 | 上の相手 /試合 | 下の相手 /試合 |\n|---|---|---|---|---|---|")
    for name, xs in groups:
        cell = lambda k: f"{med([r['h1_' + k] for r in xs]):+.2f} → {med([r['h2_live_' + k] for r in xs]):+.2f}"  # noqa: E731
        pg = lambda side: f"{med([r64_per_game(r, 'h1', side) for r in xs]):+.3f} → {med([r64_per_game(r, 'h2_live', side) for r in xs]):+.3f}"  # noqa: E731
        print(f"| {name}（{len(xs)}） | {cell('rd_g')} | {cell('wl_vs_upper')} | {cell('wl_vs_lower')} | {pg('upper')} | {pg('lower')} |")
    print("\n| 中日 | 前半 点の差 | 後半 点の差 | 前半 上 | 後半 上 | 前半 下 | 後半 下 | 後半の効く試合 |\n|---|---|---|---|---|---|---|---|")
    for r in d:
        print(f"| {r['season']} | {r['h1_rd_g']:+.2f} | {r['h2_live_rd_g']:+.2f} | {r['h1_wl_vs_upper']:+d} | {r['h2_live_wl_vs_upper']:+d} "
              f"| {r['h1_wl_vs_lower']:+d} | {r['h2_live_wl_vs_lower']:+d} | {r['h2_live_g']} |")
    up = sum(r["h2_live_wl_vs_upper"] < r["h1_wl_vs_upper"] for r in d)
    lo = sum(r["h2_live_wl_vs_lower"] < r["h1_wl_vs_lower"] for r in d)
    print(f"中日の B で後半に下がった年: 上の相手 {up}/{len(d)}、下の相手 {lo}/{len(d)}")

    print("\n## 2. 見えた年の失点の優位（プラスなら他球団より少ない）\n")
    for name, xs in (("見えた", [r for r in d if r.get("wave_limit_rank_h1") is not None]),
                     ("定まらない", [r for r in d if r.get("wave_limit_rank_h1") is None])):
        h1 = [-r["course_ra_h1_d"] for r in xs]
        h2 = [-(r["course_ra_h1_d"] + r["course_ra_d"]) for r in xs]
        print(f"- {name}（{len(xs)}）: 前半 {med(h1):+.2f} → 後半 {med(h2):+.2f}　"
              + "、".join(f"{r['season']} {a:+.2f}→{b:+.2f}" for r, a, b in zip(xs, h1, h2)))
    return 0


# ==== r65（旧 r65_game_errors.py）

R65_SEASON = 2025
R65_COLS = [("ls_e_net_g", "全試合"), ("ls_e_net_close", "1点差"), ("ls_e_net_win", "勝ち"), ("ls_e_net_loss", "負け"), ("ls_e_net_q4", "最後の区間")]


def r65(argv: list[str]) -> int:
    """R65: 試合ごとの失策（2025年の得点表）を、勝ち・負け・1点差・最後の区間で並べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r65 cycles/c001-chunichi/outputs/season.jsonl
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = sorted((r for r in rows if r["season"] == R65_SEASON), key=lambda r: (r["league"], r["rank"]))
    print(f"{R65_SEASON}年: {len(rows)} 球団、得点表のある試合の割合 {[round(r['ls_cov'], 3) for r in rows]}")

    same = sum(abs(r["ls_e_g"] - r["fld_e_g"]) < 0.0005 for r in rows)
    print(f"1. 照合: 得点表の失策／試合と守備成績の失策／試合が一致 {same}/{len(rows)}")

    print("\n| 球団 | 順位 | 自分の失策/試合 | 相手の失策/試合 | " + " | ".join(f"差（{n}）" for _, n in R65_COLS) + " |")
    print("|---|---|---|---|" + "---|" * len(R65_COLS))
    for r in rows:
        print(f"| {r['team_name']} | {r['rank']} | {r['ls_e_g']:.3f} | {r['ls_opp_e_g']:.3f} | "
              + " | ".join(f"{r[c]:+.3f}" if r[c] is not None else "-" for c, _ in R65_COLS) + " |")

    med = lambda xs: statistics.median(x for x in xs if x is not None)  # noqa: E731
    print(f"\n2. 12球団の中央値: 勝ち {med(r['ls_e_net_win'] for r in rows):+.3f}、負け {med(r['ls_e_net_loss'] for r in rows):+.3f}")
    a, b = [r for r in rows if r["upper_half"]], [r for r in rows if not r["upper_half"]]
    print("3〜4. | 列 | A の中央値 | B の中央値 | A が小さい向きの組の割合 |\n|---|---|---|---|")
    for c, n in R65_COLS:
        av, bv = [r[c] for r in a if r[c] is not None], [r[c] for r in b if r[c] is not None]
        print(f"| {n} | {statistics.median(av):+.3f} | {statistics.median(bv):+.3f} | {share(av, bv, -1):.2f} |")
    for t in ("d", "db"):
        r = next(x for x in rows if x["team"] == t)
        print(f"5. {r['team_name']}（{r['rank']}位）: " + "、".join(f"{n} {r[c]:+.3f}" for c, n in R65_COLS if r[c] is not None))
    return 0


# ==== r66（旧 r66_indicator_lines.py）

SCOPE = set(range(2013, 2026)) - EXCLUDED
INDICATORS = [  # (列, 中身, 向き +1/−1, 中立の値 or None)。計画で先に決めた
    ("rf_g", "得点／試合", 1, None), ("ra_g", "失点／試合", -1, None),
    ("rf_adv", "得点の優位", 1, 0.0), ("ra_adv", "失点の優位", 1, 0.0), ("run_balance", "収支", 1, 0.0),
    ("pythag_fixed", "点の差で見込む勝率", 1, 0.5), ("resid_fixed", "点の差より勝った分", 1, 0.0),
    ("one_run_net", "1点差 勝−負", 1, 0.0), ("alloc_z_strat", "組み合わせ方", 1, 0.0),
    ("bat_d_obp", "出塁率の差", 1, 0.0), ("bat_d_slg", "長打率の差", 1, 0.0), ("bat_d_iso", "ISO の差", 1, 0.0),
    ("bat_d_bb_pa", "四死球／打席の差", 1, 0.0), ("bat_d_so_pa", "三振／打席の差", -1, 0.0),
    ("bat_d_r_runner", "走者あたり得点の差", 1, 0.0),
    ("fld_d_e_g", "失策／試合の差", -1, 0.0), ("fld_d_fpct", "守備率の差", 1, 0.0),
    ("vs_top_wpct", "上の相手との勝率", 1, 0.5), ("vs_lower_wpct", "下の相手との勝率", 1, 0.5),
    ("course_wpct_h1", "前半の勝率", 1, 0.5),
    ("wpct", "（基準）勝率", 1, 0.5),
]
OWN = [  # R67: このプロジェクトで作った独自の指標（向きと中立の値は R67 の計画で先に決めた）
    ("sim_p_upper", "分布から見た A の確率（R10）", 1, 0.5), ("run_balance_t", "収支 ÷ 誤差（R39）", 1, 0.0),
    ("rf_adv_t", "得点の優位 ÷ 誤差", 1, 0.0), ("ra_adv_t", "失点の優位 ÷ 誤差", 1, 0.0),
    ("rf_def_total", "得点の不足（帯の合計、R3）", 1, 0.0), ("short_share", "不足の取り分（R32）", -1, 0.5),
    ("line_gap_pythag", "点の差で A の線まで（R50）", 1, 0.0), ("lg_bar", "越えるべき高さ（R56、外）", -1, 0.5),
    ("wins_vs_pythag", "点の差より勝った数", 1, 0.0), ("alloc_z", "組み合わせ方（全体、R1）", 1, 0.0),
    ("opp_conv_top", "上の相手で点の差より勝った分", 1, 0.0), ("opp_conv_mid", "中位の相手で同じ", 1, 0.0),
    ("opp_conv_low", "下の相手で同じ", 1, 0.0), ("inn_dlog_freq", "得点した回の頻度（R4）", 1, 0.0),
    ("inn_dlog_size", "得点した回の大きさ（R4）", 1, 0.0), ("half1_vs_pythag", "前半に点の差より勝った数", 1, 0.0),
    ("course_wpct_diff", "後半 − 前半の勝率（R20）", 1, 0.0), ("series_lost_pct", "負け越したカードの多さ（R24）", -1, 0.5),
    ("max_lose_streak", "最長連敗", -1, None), ("q4_rd_g", "最後の区間の点の差（R62）", 1, 0.0),
    ("h2_live_rd_g", "後半の効く試合の点の差（R64）", 1, 0.0), ("vs_battle_wpct", "競り合う相手との勝率", 1, 0.5),
    ("wpct", "（基準）勝率", 1, 0.5),
]


def mid(a, b):
    return (a + b) / 2


def r66(argv=None) -> int:
    """R66: 順位ではなく指標の値に線を引き、A・AB・B に分ける（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r66 cycles/c001-chunichi/outputs/season.jsonl [--season 2012]

    範囲は 2013〜2025年（2020年を除く）。--season を付けると、その年だけを確かめる（帯はほかの年から引く）。
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("season_jsonl", type=Path)
    ap.add_argument("--season", type=int, help="この年だけを確かめる（2012 など）")
    ap.add_argument("--set", choices=["base", "own"], default="base", help="base = R66 の20指標、own = R67 の独自指標")
    args = ap.parse_args(argv)
    indicators = OWN if args.set == "own" else INDICATORS
    rows = [json.loads(line) for line in args.season_jsonl.read_text(encoding="utf-8").splitlines()]
    for r in rows:
        r["rf_g"], r["ra_g"] = r["RF"] / r["G"], r["RA"] / r["G"]
    pool_all = [r for r in rows if r["season"] in SCOPE]
    target = [r for r in rows if r["season"] not in EXCLUDED and (r["season"] == args.season if args.season else r["season"] in SCOPE)]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    d = sorted((r for r in target if r["team"] == FOCUS and not r["upper_half"]), key=lambda r: r["season"])
    print(f"範囲: {len(target)} 単位（{'その年 ' + str(args.season) if args.season else '2013〜2025年、2020年を除く'}）、中日の B {len(d)}年\n")

    print("| 指標 | 3.5位の線で一致 | 中立の線で一致 | 2本線: A→A | AB→A | B→B | 帯の幅（AB の単位） | 帯: A→A・B→B | 中日の B: 2本線で B | 帯の下 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    out = []
    for col, label, sign, neutral in indicators:
        rs = [r for r in target if r.get(col) is not None]
        if not rs:
            continue
        agree35 = agreeN = 0
        st2, stb = {}, {}
        for r in rs:
            lg = sorted((sign * x[col] for x in leagues[(r["season"], r["league"])] if x.get(col) is not None), reverse=True)
            v = sign * r[col]
            if len(lg) >= 5:
                l35, l25, l45 = mid(lg[2], lg[3]), mid(lg[1], lg[2]), mid(lg[3], lg[4])
                agree35 += (v > l35) == bool(r["upper_half"])
                st2[id(r)] = "A" if v > l25 else "B" if v < l45 else "AB"
            if neutral is not None:
                agreeN += (v > sign * neutral) == bool(r["upper_half"])
            other = [x for x in pool_all if x["season"] != r["season"] and x.get(col) is not None]
            lo = min(sign * x[col] for x in other if x["upper_half"])      # ほかの年の A の最も悪い値
            hi = max(sign * x[col] for x in other if not x["upper_half"])  # ほかの年の B の最もよい値
            stb[id(r)] = "B" if v < lo else "A" if v > hi else "AB"

        def frac(states, s, final):
            xs = [r for r in rs if states.get(id(r)) == s]
            return f"{sum(bool(r['upper_half']) == final for r in xs)}/{len(xs)}"
        n = len(rs)
        a2 = frac(st2, "A", True)
        ab2 = frac(st2, "AB", True)
        b2 = frac(st2, "B", False)
        width = sum(stb[id(r)] == "AB" for r in rs)
        band = f"{frac(stb, 'A', True)}・{frac(stb, 'B', False)}"
        dd = [r for r in d if r.get(col) is not None]
        d_b2 = sum(st2.get(id(r)) == "B" for r in dd)
        d_bb = sum(stb.get(id(r)) == "B" for r in dd)
        out.append((agree35 / n, label))
        print(f"| `{col}` {label} | {agree35 / n:.2f} | {agreeN / n:.2f} | {a2} | {ab2} | {b2} | {width}/{n} | {band} "
              f"| {d_b2}/{len(dd)} | {d_bb}/{len(dd)} |" if neutral is not None else
              f"| `{col}` {label} | {agree35 / n:.2f} | - | {a2} | {ab2} | {b2} | {width}/{n} | {band} | {d_b2}/{len(dd)} | {d_bb}/{len(dd)} |")
    print("\n3.5位の線での一致の高い順: " + "、".join(f"{l} {a:.2f}" for a, l in sorted(out, reverse=True)))

    print(f"\n中日の B {len(d)}年の、2本線での状態（A・AB・B）:")
    for col, label, sign, _ in indicators:
        line = []
        for r in d:
            if r.get(col) is None:
                line.append("-")
                continue
            lg = sorted((sign * x[col] for x in leagues[(r["season"], r["league"])] if x.get(col) is not None), reverse=True)
            v = sign * r[col]
            if len(lg) < 5:   # 値のない球団があるリーグ年（short_share など）は状態を出さない
                line.append("-")
                continue
            line.append("A" if v > mid(lg[1], lg[2]) else "B" if v < mid(lg[3], lg[4]) else "AB")
        print((f"  {label}: " + " ".join(f"{r['season'] % 100:02d}{s}" for r, s in zip(d, line))).rstrip())
    return 0


# ==== r67（旧 r67_offense_defense.py）

R67_SCOPE = set(range(2013, 2026)) - {2020}
STATES = ("A", "AB", "B")


def r67_state(rows, r, col):
    lg = sorted((x[col] for x in rows if (x["season"], x["league"]) == (r["season"], r["league"])), reverse=True)
    v = r[col]
    return "A" if v > (lg[1] + lg[2]) / 2 else "B" if v < (lg[3] + lg[4]) / 2 else "AB"


def r67(argv: list[str]) -> int:
    """R67: 得点の側と失点の側の2本線の状態（A・AB・B）を組にした9通りで、最後に A になった割合（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r67 cycles/c001-chunichi/outputs/season.jsonl

    状態は R66 と同じ: 同じ年・同じリーグの6球団の値を並べ、2番目と3番目の真ん中・4番目と5番目の真ん中の2本線で分ける。
    得点の側 = rf_adv（得点の優位）、失点の側 = ra_adv（失点の優位、大きいほど失点が少ない）。範囲は 2013〜2025年（2020年を除く）。
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in R67_SCOPE]
    cells = defaultdict(list)
    for r in rows:
        r["off"], r["def"] = r67_state(rows, r, "rf_adv"), r67_state(rows, r, "ra_adv")
        cells[(r["off"], r["def"])].append(r)
    print(f"範囲: {len(rows)} 単位\n")
    print("| 得点の側 ＼ 失点の側 | A | AB | B |\n|---|---|---|---|")
    for o in STATES:
        print(f"| **{o}** | " + " | ".join(
            f"{sum(r['upper_half'] for r in cells[(o, d)])}/{len(cells[(o, d)])}" for d in STATES) + " |")
    print("\n各ます目の中日の B（年）・中日の A（年）:")
    for o in STATES:
        for dd in STATES:
            dB = [r["season"] for r in cells[(o, dd)] if r["team"] == "d" and not r["upper_half"]]
            dA = [r["season"] for r in cells[(o, dd)] if r["team"] == "d" and r["upper_half"]]
            if dB or dA:
                print(f"  得点 {o} × 失点 {dd}: B {dB}、A {dA}")
    print("\n五分に近います目（A の割合 0.3〜0.7、3単位以上）の単位:")
    for (o, dd), xs in sorted(cells.items()):
        if len(xs) >= 3 and 0.3 <= sum(r["upper_half"] for r in xs) / len(xs) <= 0.7:
            print(f"  得点 {o} × 失点 {dd}: " + ", ".join(f"{r['team']}-{r['season']}（{'A' if r['upper_half'] else 'B'}）" for r in xs))
    return 0


# ==== r68（旧 r68_same_cell.py）

R68_COLS = [  # (列, 中身, 向き +1 = 大きいほどよい)。計画で先に決めた
    ("rf_adv", "得点の優位", 1), ("ra_adv", "失点の優位", 1), ("run_balance", "収支", 1), ("run_balance_t", "収支 ÷ 誤差", 1),
    ("resid_fixed", "点の差より勝った分", 1), ("wins_vs_pythag", "点の差より勝った数", 1), ("one_run_net", "1点差 勝−負", 1),
    ("alloc_z_strat", "組み合わせ方", 1), ("vs_top_wpct", "上の相手との勝率", 1), ("vs_lower_wpct", "下の相手との勝率", 1),
    ("h2_live_wl_vs_upper", "後半の効く試合 上の相手 勝−負", 1), ("h2_live_wl_vs_lower", "後半の効く試合 下の相手 勝−負", 1),
    ("lg_bar", "越えるべき高さ", -1), ("course_wpct_h1", "前半の勝率", 1), ("course_wpct_h2", "後半の勝率", 1),
    ("q_wl_4", "最後の区間 勝−負", 1), ("lock_g", "落ち着いた試合数 N", 0),
    ("inn_dlog_freq", "得点した回の頻度", 1), ("inn_dlog_size", "得点した回の大きさ", 1),
    ("bat_d_obp", "出塁率の差", 1), ("bat_d_iso", "ISO の差", 1), ("bat_d_bb_pa", "四死球／打席の差", 1), ("fld_d_e_g", "失策／試合の差", -1),
]
HANSHIN = [2013, 2019, 2021, 2022]
CHUNICHI = [2014, 2019, 2021, 2022]


def r68_state(r, col, leagues):
    lg = sorted((x[col] for x in leagues[(r["season"], r["league"])]), reverse=True)
    v = r[col]
    return "A" if v > (lg[1] + lg[2]) / 2 else "B" if v < (lg[3] + lg[4]) / 2 else "AB"


def r68_f(v):
    return "-" if v is None else (f"{v:+.3f}" if isinstance(v, float) else f"{v:+d}")


def r68(argv: list[str]) -> int:
    """R68: 得点が下2つ × 失点が上2つのます目で、阪神の4年（A）と中日の4年（B）を比べる（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r68 cycles/c001-chunichi/outputs/season.jsonl
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in SCOPE]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    cell = [r for r in rows if r68_state(r, "rf_adv", leagues) == "B" and r68_state(r, "ra_adv", leagues) == "A"]
    get = lambda t, s: next(r for r in cell if (r["team"], r["season"]) == (t, s))  # noqa: E731
    h = [get("t", s) for s in HANSHIN]
    d = [get("d", s) for s in CHUNICHI]
    others = [r for r in cell if r not in h and r not in d]
    print(f"ます目の単位: {len(cell)}（A {sum(r['upper_half'] for r in cell)}）。阪神 {HANSHIN}、中日 {CHUNICHI}、"
          f"ほか: " + ", ".join(f"{r['team']}-{r['season']}({'A' if r['upper_half'] else 'B'})" for r in others))

    print("\n| 列 | 中身 | 阪神 4年 | 中日 4年 | 阪神の中央値 | 中日の中央値 | 阪神の4年すべてが中日の4年すべてよりよい |\n|---|---|---|---|---|---|---|")
    split = []
    for col, label, sign in R68_COLS:
        hv, dv = [r.get(col) for r in h], [r.get(col) for r in d]
        if None in hv + dv:
            print(f"| `{col}` | {label} | " + " ".join(map(r68_f, hv)) + " | " + " ".join(map(r68_f, dv)) + " | - | - | - |")
            continue
        all_better = sign and min(sign * x for x in hv) > max(sign * y for y in dv)
        if all_better:
            split.append(col)
        print(f"| `{col}` | {label} | " + " ".join(map(r68_f, hv)) + " | " + " ".join(map(r68_f, dv))
              + f" | {r68_f(statistics.median(hv))} | {r68_f(statistics.median(dv))} | {'**4対0**' if all_better else ''} |")
    print("\n4対0で分かれた列: " + (", ".join(split) or "なし"))

    print("\n| 同じ年の差（阪神 − 中日） | " + " | ".join(str(s) for s in (2019, 2021, 2022)) + " | 3年とも阪神がよい |\n|---|---|---|---|---|")
    same = []
    for col, label, sign in R68_COLS:
        diffs = [get("t", s).get(col) - get("d", s).get(col) if None not in (get("t", s).get(col), get("d", s).get(col)) else None
                 for s in (2019, 2021, 2022)]
        if None in diffs:
            continue
        ok = sign and all(sign * x > 0 for x in diffs)
        if ok:
            same.append(col)
        print(f"| {label} | " + " | ".join(r68_f(x) for x in diffs) + f" | {'はい' if ok else ''} |")
    print("\n同じ年の3組で、3年とも阪神がよい列: " + (", ".join(same) or "なし"))

    print("\n候補の列で、ほかの単位（西武 2022年とます目の残りの B）がどちら側か（阪神の最低・中日の最高と比べる）:")
    for col in sorted(set(split) | set(same)):
        sign = next(s for c, _, s in R68_COLS if c == col)
        hmin, dmax = min(sign * r[col] for r in h), max(sign * r[col] for r in d)
        print(f"  {col}: " + ", ".join(
            f"{r['team']}-{r['season']}({'A' if r['upper_half'] else 'B'}) {r[col]:+.3f}"
            f"→{'阪神側' if sign * r[col] >= hmin else '中日側' if sign * r[col] <= dmax else '間'}" for r in others))
    return 0


# ==== r69（旧 r69_flips.py）

def r69(argv: list[str]) -> int:
    """R69: 9通りのます目で収支の符号が A・B を分けるか、勝ち方が収支をひっくり返した単位（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r69 cycles/c001-chunichi/outputs/season.jsonl
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in SCOPE]
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    for r in rows:
        r["cell"] = f"{r68_state(r, 'rf_adv', leagues)}×{r68_state(r, 'ra_adv', leagues)}"
        r["pred"] = r["run_balance"] > 0
    print("## 1. ます目ごと（得点 × 失点）: 収支 > 0 の A / 単位、収支 ≤ 0 の A / 単位、収支の符号が当たった数\n")
    print("| ます目 | 収支 > 0 → A | 収支 ≤ 0 → A | 当たり |\n|---|---|---|---|")
    hit_all = 0
    for a in ("A", "AB", "B"):
        for b in ("A", "AB", "B"):
            xs = [r for r in rows if r["cell"] == f"{a}×{b}"]
            pos, neg = [r for r in xs if r["pred"]], [r for r in xs if not r["pred"]]
            hit = sum(r["pred"] == bool(r["upper_half"]) for r in xs)
            hit_all += hit
            print(f"| 得点{a}×失点{b} | {sum(r['upper_half'] for r in pos)}/{len(pos)} | {sum(r['upper_half'] for r in neg)}/{len(neg)} | {hit}/{len(xs)} |")
    print(f"\n全体: 収支の符号が当たった {hit_all}/{len(rows)} = {hit_all / len(rows):.2f}（R66 の点の差で見込む勝率の 3.5位の線は 0.86）")

    flips = sorted((r for r in rows if r["pred"] != bool(r["upper_half"])), key=lambda r: (r["season"], r["league"], r["rank"]))
    print(f"\n## 2. 収支の符号で読み違えた単位: {len(flips)}\n")
    print("| 単位 | 順位 | 最後 | 収支 | 点の差より勝った数 | 1点差 | 組み合わせ方 | 勝率 − 越えるべき高さ | ます目 |\n|---|---|---|---|---|---|---|---|---|")
    agree = 0
    for r in flips:
        ok = (r["wins_vs_pythag"] < 0) if r["pred"] else (r["wins_vs_pythag"] > 0)
        agree += ok
        print(f"| {r['team']}-{r['season']} | {r['rank']} | {'A' if r['upper_half'] else 'B'} | {r['run_balance']:+.2f} | {r['wins_vs_pythag']:+.1f} "
              f"| {r['one_run_net']:+d} | {r['alloc_z_strat']:+.2f} | {r['wpct'] - r['lg_bar']:+.3f} | {r['cell']} |")
    print(f"\n勝ち方の向きが読み違いと合う（収支 > 0 で B なら点の差より負け、≤ 0 で A なら勝ち）: {agree}/{len(flips)}")
    print("中日: " + (", ".join(f"{r['season']}" for r in flips if r["team"] == "d") or "なし")
          + "　阪神: " + (", ".join(f"{r['season']}" for r in flips if r["team"] == "t") or "なし"))
    return 0


# ==== r70（旧 r70_club.py）

COL = "wins_vs_pythag"
PERMS, SEED = 10_000, 20261006
CELL_COLS = [("lg_bar", "越えるべき高さ", -1), ("q_wl_4", "最後の区間 勝−負", 1), ("wins_vs_pythag", "点の差より勝った数", 1),
             ("one_run_net", "1点差 勝−負", 1), ("vs_lower_wpct", "下の相手との勝率", 1), ("vs_top_wpct", "上の相手との勝率", 1),
             ("run_balance", "収支", 1)]


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = statistics.mean(ra), statistics.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return num / (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5


def r70(argv: list[str]) -> int:
    """R70: 勝ち方（点の差より勝った数）は球団に付いているか・得点も失点も真ん中のます目（記述。判定はしない）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r70 cycles/c001-chunichi/outputs/season.jsonl
    """
    rows = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["season"] in SCOPE]
    by = {(r["team"], r["season"]): r for r in rows}
    seasons = sorted({r["season"] for r in rows})

    print("## 1. 勝ち方は球団に付いているか\n")
    pairs = [(by[(t, s)][COL], by[(t, s + 1)][COL]) for (t, s) in by if (t, s + 1) in by]
    print(f"続く2年の組: {len(pairs)}、順位相関 {spearman([a for a, _ in pairs], [b for _, b in pairs]):+.3f}")

    teams = sorted({r["team"] for r in rows})
    def spread(values):  # values[(team, season)] -> 球団の平均の分散
        means = [statistics.mean(values[(t, s)] for s in seasons if (t, s) in values) for t in teams]
        return statistics.pvariance(means)
    actual = {k: r[COL] for k, r in by.items()}
    obs = spread(actual)
    rng = random.Random(SEED)
    ge = 0
    for _ in range(PERMS):
        perm = {}
        for s in seasons:
            for lg in ("C", "P"):
                ks = [k for k in actual if k[1] == s and by[k]["league"] == lg]
                vs = [actual[k] for k in ks]
                rng.shuffle(vs)
                perm.update(zip(ks, vs))
        ge += spread(perm) >= obs
    print(f"球団の平均の分散: {obs:.3f}。年とリーグの中で入れ替えたとき、それ以上になった割合 {ge / PERMS:.4f}（{PERMS} 回、種 {SEED}）")
    means = sorted(((statistics.mean(actual[(t, s)] for s in seasons if (t, s) in actual), t) for t in teams), reverse=True)
    names = {r["team"]: r["team_name"] for r in rows}
    print("球団の平均（勝ち数、多い順）: " + "、".join(f"{names[t]} {m:+.2f}" for m, t in means))

    print("\n## 2. 得点も失点も真ん中のます目（AB × AB）\n")
    leagues: dict = {}
    for r in rows:
        leagues.setdefault((r["season"], r["league"]), []).append(r)
    cell = [r for r in rows if r68_state(r, "rf_adv", leagues) == "AB" and r68_state(r, "ra_adv", leagues) == "AB"]
    a, b = [r for r in cell if r["upper_half"]], [r for r in cell if not r["upper_half"]]
    print(f"{len(cell)} 単位（A {len(a)}・B {len(b)}）。B: " + ", ".join(f"{r['team_name']} {r['season']}（{r['rank']}位）" for r in b))
    print("\n| 列 | 中身 | A らしい向きの組の割合 | A の中央値 | B の中央値 |\n|---|---|---|---|---|")
    for col, label, sign in CELL_COLS:
        av, bv = [r[col] for r in a], [r[col] for r in b]
        print(f"| `{col}` | {label} | {share(av, bv, sign):.2f} | {statistics.median(av):+.3f} | {statistics.median(bv):+.3f} |")
    return 0


# ==== r75（旧 r75_provisional.py）

R75_SEASON = 2026
PROPS = [f"P{i}" for i in range(181, 211)]
EXPRS = ["E11", "E13", "E15", *(f"E{i}" for i in range(19, 33))]   # R76: 判例のない式と、その作り直し


def cell(v):
    return "-" if v is None else str(v)


def classify(flags):
    unknown = flags.filter(pl.col("x").is_null() | pl.col("y").is_null())
    known = flags.filter(pl.col("x").is_not_null() & pl.col("y").is_not_null())
    ins = known.filter(pl.col("x"))
    hold = ins.filter(pl.col("y"))
    cx = ins.filter(~pl.col("y"))["team"].to_list()
    dx = flags.filter(pl.col("team") == "d").rows(named=True)
    d = "-" if not dx else "入らない" if dx[0]["x"] is False else "判定不能" if dx[0]["x"] is None or dx[0]["y"] is None else "入る"
    return ins.height, hold.height, sorted(cx), unknown.height, d


def r75(argv: list[str]) -> int:
    """R74: 2026年の暫定データ（消化した試合だけ）で、結果を見た後に立てた命題と式を判定する（記述）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r75 cycles/c001-chunichi/outputs/provisional/season.jsonl         cycles/c001-chunichi/propositions.toml cycles/c001-chunichi/sets.toml --out cycles/c001-chunichi/outputs/provisional/check.md

    2026年の12単位だけで判定する。暫定なので、全日程の後に R18 の手順でもう一度判定する。
    """
    import contextlib
    import io

    if "--out" in argv:
        i = argv.index("--out")
        out, argv = Path(argv[i + 1]), argv[:i] + argv[i + 2:]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = r75(argv)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(buf.getvalue(), encoding="utf-8")
        print(buf.getvalue())
        return code
    season, props_path, sets_path = map(Path, argv[:3])
    df = pl.read_ndjson(season, infer_schema_length=None)
    d26 = df.filter(pl.col("season") == R75_SEASON)
    props, _ = pr.load(props_path)
    by_id = {p["id"]: p for p in props}
    sets, exprs, _ = st_.load_sets(sets_path, props)
    print(f"# 2026年の暫定の判定（消化した試合だけ、{d26.height} 単位）\n")
    print("暫定。R18 の手順（全球団が143試合を終えてから）で取り込んだ後、もう一度判定する。\n")
    print("| 球団 | 試合 | 勝率 | 順位 | A |\n|---|---|---|---|---|")
    for r in d26.sort("league", "rank").iter_rows(named=True):
        print(f"| {r['team_name']} | {r['G']} | {r['wpct']:.3f} | {r['rank']} | {'A' if r['upper_half'] else 'B'} |")

    def judge_rows(items):
        print("\n| id | 前件に入った | 後件も当たり | 判例 | 判定不能 | 中日 |\n|---|---|---|---|---|---|")
        for p in items:
            try:
                sub = pr.scope_filter(d26, p.get("scope"))
                flags = sub.select("team", x=pr._antecedent(p, sub.columns), y=pr._cond(p["then"], sub.columns))
                scope = p.get("scope") or {}
                if scope.get("where"):
                    base = pr.scope_filter(d26, {k: v for k, v in scope.items() if k != "where"})
                    unknown_scope = base.filter(pr._cond(scope["where"], base.columns).is_null())
                    flags = pl.concat([flags, unknown_scope.select("team", x=pl.lit(None, dtype=pl.Boolean), y=pl.lit(None, dtype=pl.Boolean))])
            except Exception as e:  # noqa: BLE001  列がない（暫定で測れない列）なども記録する
                print(f"| {p['id']} | 判定できない: {type(e).__name__} | | | | |")
                continue
            n, hold, cx, unknown, d = classify(flags)
            print(f"| {p['id']} | {n} | {hold} | {', '.join(cx) or 'なし'} | {unknown} | {d} |")

    print("\n## 命題（P181〜P210）")
    judge_rows([by_id[i] for i in PROPS if i in by_id])
    print("\n## 式（E11・E13・E15・E19〜E32）")
    judge_rows([st_.compile_expr(e, sets) for e in exprs if e["id"] in EXPRS])
    return 0


# ==== r76（旧 r76_remake.py）

PAIRS = [("E11", "E29"), ("E13", "E30"), ("E15", "E31"), ("E26", "E32")]
SETS = [("F96", "F96B"), ("TOP_WIN", "TOP_WIN_B"), ("BAL_NONPOS", "BALG_NONPOS")]


def members(df: pl.DataFrame, item: dict) -> set[str]:
    sub = pr.scope_filter(df, item.get("scope"))
    x = sub.select("unit", x=pr._antecedent(item, sub.columns)).filter(pl.col("x").fill_null(False))
    return set(x["unit"].to_list())


def r76(argv: list[str]) -> int:
    """R76: 判例のない式と、その年の高さで作り直した式の、入る単位の入れ替わりを並べる（記述。判定は sets.md）。

        python cycles/c001-chunichi/from-cycle-001/research/research.py r76 cycles/c001-chunichi/outputs/season.jsonl         cycles/c001-chunichi/propositions.toml cycles/c001-chunichi/sets.toml

    season.jsonl の既存のチームの列だけを使う。2020年は除く（判定と同じ [[exclude]]）。ネットワークを使わない。
    """
    df = pl.read_ndjson(argv[0], infer_schema_length=None).filter(~pl.col("season").is_in(sorted(EXCLUDED)))
    df = df.with_columns(unit=pl.col("team") + "-" + pl.col("season").cast(pl.Utf8))
    a = {r["unit"]: r["upper_half"] for r in df.select("unit", "upper_half").iter_rows(named=True)}
    props, _ = pr.load(Path(argv[1]))
    sets, exprs, _ = st_.load_sets(Path(argv[2]), props)
    by_e = {e["id"]: st_.compile_expr(e, sets) for e in exprs}

    def tag(u):
        return f"{u}（{'A' if a[u] else 'B'}）"

    print("## 集合の入れ替わり（元 → 作り直し）\n")
    for old, new in SETS:
        mo, mn = members(df, by_e_set(sets, old)), members(df, by_e_set(sets, new))
        print(f"- {old} {len(mo)} → {new} {len(mn)}。外れた: {', '.join(map(tag, sorted(mo - mn))) or 'なし'}。"
              f"入った: {', '.join(map(tag, sorted(mn - mo))) or 'なし'}")
    print("\n## 式の入れ替わり\n")
    for old, new in PAIRS:
        mo, mn = members(df, by_e[old]), members(df, by_e[new])
        print(f"- {old} {len(mo)} → {new} {len(mn)}。外れた: {', '.join(map(tag, sorted(mo - mn))) or 'なし'}。"
              f"入った: {', '.join(map(tag, sorted(mn - mo))) or 'なし'}")
    return 0


def by_e_set(sets: dict, sid: str) -> dict:
    """集合1つを、式として読める形にする（集合の式 = その集合だけ）。"""
    return st_.compile_expr({"id": sid, "expr": sid, "statement": sid}, sets)


# ==== 入口
COMMANDS = {
    "r31": r31,
    "r35": r35,
    "r36": r36,
    "r37": r37,
    "r38": r38,
    "r44": r44,
    "r47": r47,
    "r51": r51,
    "r52": r52,
    "r53": r53,
    "r54": r54,
    "r56": r56,
    "r57": r57,
    "r58": r58,
    "r59": r59,
    "r60": r60,
    "r61": r61,
    "r62": r62,
    "r63": r63,
    "r64": r64,
    "r65": r65,
    "r66": r66,
    "r67": r67,
    "r68": r68,
    "r69": r69,
    "r70": r70,
    "r75": r75,
    "r76": r76,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="research.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
