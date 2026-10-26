#!/usr/bin/env python3
"""波の減衰 0 → ε の試しを、動かし方を変えて読む（探索）。確定した出力は変更しない。

ε の値は暫定の置き場所で、結論には使わない。扱いは今後決める。wave_eps_trial.py（同じ置き場）の差し替え版 wave_basis を使って、
次の2つを調べる。

  1. ε を 1e-1 〜 1e-12 に振る（線の始まり・終わりは設定のまま）: 境界の単位が ε の波に戻るか、境界でなかった単位が乗り換わるのは
     ε がいくつからか、最後の日の順位・収束先・落ち着く位置が ε でどう動くか。
  2. 線の始まり（min_games）と終わり（season / decided）を動かす（ε は 1 つに固定）: 境界の単位がどう入れ替わるか、
     境界に残った単位の収束先は動かないか。

境界の単位 = 当てはめで選ばれた式が「減衰しない波」（λ = 0）だった単位。ε を渡した実行では、選ばれた式の減衰が ε そのものの単位。

使い方（試合ごとのデータ games.jsonl がある環境で。リポジトリの直下から）:
  uv run --locked python cycles/c001-chunichi/exploratory/wave_eps_sensitivity.py \\
      --games data/observations/npb_calendar/games.jsonl --config cycles/c001-chunichi/analysis.toml \\
      --committed cycles/c001-chunichi/outputs/season.jsonl --outdir /tmp/wave-eps-sensitivity

線の始まり・終わりを設定のまま（対照）走らせた結果が確定済みの season.jsonl の wave_* と合わなければ止まる（wave_eps_trial.py と同じ関門）。
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wave_eps_trial as trial  # noqa: E402

GRID = (1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 1e-4, 1e-6, 1e-9, 1e-12)
MIN_GAMES = (5, 10, 20, 30)
ENDS = ("season", "decided")
VARIANT_EPS = 1e-6


def label(key: tuple) -> str:
    return f"{key[0]}-{key[1]}"


class Runner:
    """同じ (min_games, end, ε) を二度走らせない。ε が None なら今のコードのまま。"""

    def __init__(self, sa, tg, sims: int):
        self.sa, self.tg, self.sims, self.cache = sa, tg, sims, {}

    def __call__(self, min_games: int, end: str, eps: float | None = None) -> dict:
        key = (min_games, end, eps)
        if key not in self.cache:
            basis = self.sa.wave_basis if eps is None else trial.make_wave_basis(self.sa, eps)
            self.cache[key] = trial.trajectory(self.sa, self.tg, basis, self.sims, min_games, end)
        return self.cache[key]


def on_boundary(res: dict, eps: float | None = None) -> set:
    """選ばれた式が境界の行の単位。ε なし: 減衰が 0。ε あり: 減衰が ε そのもの。"""
    want = 0.0 if eps is None else eps
    return {k for k, r in res.items() if r["wave_decay"] == want}


def _median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def grid_report(run: Runner, min_games: int, end: str, grid) -> list[dict]:
    """ε ごとの読み。対照 = ε なし（今のコード）。"""
    ctrl = run(min_games, end)
    zero = on_boundary(ctrl)
    results = {eps: run(min_games, end, eps) for eps in grid}
    ref_eps = min(grid)
    ref, ref_lifted = results[ref_eps], on_boundary(results[ref_eps], ref_eps)
    rows = []
    for eps in grid:
        res = results[eps]
        lifted = on_boundary(res, eps)
        still = sorted(zero & lifted)
        changed = trial.diff_rows(ctrl, res)
        others = {k: v for k, v in changed.items() if k not in zero and k not in lifted}
        cols: dict[str, int] = {}
        for v in others.values():
            for c in v:
                cols[c] = cols.get(c, 0) + 1
        end_shift = [abs(res[k]["wave_end_rank"] - ctrl[k]["wave_end_rank"]) for k in still
                     if res[k]["wave_end_rank"] is not None and ctrl[k]["wave_end_rank"] is not None]
        both_ref = sorted(lifted & ref_lifted)
        limit_shift = [abs(res[k]["wave_limit_rank"] - ref[k]["wave_limit_rank"]) for k in both_ref
                       if res[k]["wave_limit_rank"] is not None and ref[k]["wave_limit_rank"] is not None]
        big = [k for k in still if res[k]["wave_settle_x"] is not None and res[k]["wave_settle_x"] > 1]
        rows.append({
            "eps": eps, "units": len(res), "boundary_without_eps": len(zero), "lifted": len(lifted), "still_boundary": len(still),
            "switched_in": [label(k) for k in sorted(lifted - zero)], "left": [label(k) for k in sorted(zero - lifted)],
            "other_changed": len(others), "other_changed_cols": cols,
            "end_shift_max": max(end_shift) if end_shift else None,
            "end_shift_over_eps": (max(end_shift) / eps) if end_shift else None,
            "limit_shift_vs_smallest_eps": max(limit_shift) if limit_shift else None,
            "settle_over_1": len(big), "settle_within_season": len(still) - len(big),
            "settle_x_median_over_1": _median([res[k]["wave_settle_x"] for k in big]),
            "settle_times_eps_median": _median([(res[k]["wave_settle_x"] - res[k]["traj_start_x"]) * eps for k in big]),
            "limit_h1_blank": sum(r["wave_limit_rank_h1"] is None for r in res.values()),
        })
    return rows


def variant_report(run: Runner, variants, eps: float, base: tuple[int, str]) -> dict:
    """線の始まり・終わりを動かした実行ごとの読み。基準 = base（設定のままの線）。"""
    base_ctrl, base_res = run(*base), run(*base, eps)
    base_zero, base_lifted = on_boundary(base_ctrl), on_boundary(base_res, eps)
    rows, runs = [], {}
    for m, end in variants:
        ctrl, res = run(m, end), run(m, end, eps)
        zero, lifted = on_boundary(ctrl), on_boundary(res, eps)
        runs[(m, end)] = (set(ctrl), zero)
        common = set(ctrl) & set(base_ctrl)
        z_c, b_c = zero & common, base_zero & common
        inter, union = z_c & b_c, z_c | b_c
        stay = sorted(inter & lifted & base_lifted)
        shifts = [abs(res[k]["wave_limit_rank"] - base_res[k]["wave_limit_rank"]) for k in stay
                  if res[k]["wave_limit_rank"] is not None and base_res[k]["wave_limit_rank"] is not None]
        rows.append({
            "min_games": m, "end": end, "units": len(ctrl), "units_in_common_with_base": len(common),
            "boundary": len(zero), "lifted": len(lifted), "lifted_equals_boundary": lifted == zero,
            "boundary_in_common_units": len(z_c), "base_boundary_in_common_units": len(b_c),
            "kept_from_base": len(inter), "added": len(z_c - b_c), "dropped": len(b_c - z_c),
            "jaccard": (len(inter) / len(union)) if union else None,
            "limit_shift_median": _median(shifts), "limit_shift_max": max(shifts) if shifts else None,
            "same_period": sum(res[k]["wave_period"] == base_res[k]["wave_period"] for k in stay), "compared": len(stay),
        })
    # 基準の境界の単位が、動かした線のうち何本で境界に残るか（その単位がある線のうち）
    membership = []
    for k in sorted(base_zero):
        present = [v for v, (units, _) in runs.items() if k in units]
        on = [v for v in present if k in runs[v][1]]
        membership.append({"unit": label(k), "present_in": len(present), "on_boundary_in": len(on)})
    histogram: dict[str, int] = {}
    for m in membership:
        key = f"{m['on_boundary_in']}/{m['present_in']}"
        histogram[key] = histogram.get(key, 0) + 1
    return {"eps": eps, "base": {"min_games": base[0], "end": base[1]}, "variants": rows,
            "membership": membership, "membership_histogram": dict(sorted(histogram.items()))}


def _f(x, digits=4):
    return "—" if x is None else f"{x:.{digits}g}"


def render(report: dict) -> str:
    g, v = report["grid"], report["variants"]
    lines = ["# 波の減衰 0 → ε: 動かし方を変えた読み（探索・暫定）", "",
             "確定した出力は変更していない。ε の値は暫定の置き場所で、結論には使わない。", "",
             f"- 単位数: {report['units']}、sims: {report['sims']}、基準の線: min_games = {report['base']['min_games']}、end = {report['base']['end']}",
             "", "## 1. ε を振る", "",
             "| ε | ε なしで境界 | ε の波が選ばれた | うち元から境界 | 乗り換え（元は境界でない） | 外れた | 最後の値のずれ（最大） | ずれ/ε | 収束先のずれ（最小 ε 比） | 落ち着く位置 > 1 | 落ち着く位置（中央値） | (落ち着く位置−始まり)×ε | ほかの単位で動いた数 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in g:
        lines.append(f"| {r['eps']:g} | {r['boundary_without_eps']} | {r['lifted']} | {r['still_boundary']} | "
                     f"{len(r['switched_in'])}{(' (' + ', '.join(r['switched_in']) + ')') if r['switched_in'] else ''} | {len(r['left'])} | "
                     f"{_f(r['end_shift_max'])} | {_f(r['end_shift_over_eps'])} | {_f(r['limit_shift_vs_smallest_eps'])} | "
                     f"{r['settle_over_1']}/{r['still_boundary']} | {_f(r['settle_x_median_over_1'])} | {_f(r['settle_times_eps_median'])} | {r['other_changed']} |")
    lines += ["", f"## 2. 線の始まり・終わりを動かす（ε = {v['eps']:g}）", "",
              "| 始まり（試合数） | 終わり | 単位数 | 境界（ε なし） | 基準から残る | 加わる | 外れる | 重なり（Jaccard） | 残った単位の収束先のずれ（中央値 / 最大） | 周期が同じ |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in v["variants"]:
        lines.append(f"| {r['min_games']} | {r['end']} | {r['units']} | {r['boundary']} | {r['kept_from_base']} | {r['added']} | {r['dropped']} | "
                     f"{_f(r['jaccard'], 3)} | {_f(r['limit_shift_median'])} / {_f(r['limit_shift_max'])} | {r['same_period']}/{r['compared']} |")
    lines += ["", "## 3. 基準の境界の単位は、動かした線のうち何本で境界に残るか", "",
              "| 境界に残った線の数 / その単位がある線の数 | 単位の数 |", "|---|---|"]
    for key, n in v["membership_histogram"].items():
        lines.append(f"| {key} | {n} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def analyze(sa, tg, sims: int, grid=GRID, min_games=MIN_GAMES, ends=ENDS, variant_eps: float = VARIANT_EPS,
            base: tuple[int, str] = (10, "season")) -> dict:
    run = Runner(sa, tg, sims)
    variants = [(m, e) for e in ends for m in min_games]
    return {"sims": sims, "units": len(run(*base)), "base": {"min_games": base[0], "end": base[1]},
            "grid": grid_report(run, *base, grid), "variants": variant_report(run, variants, variant_eps, base)}


def gate(ctrl: dict, committed: dict, sims: int, new_seasons=()) -> dict:
    return trial.gate(ctrl, committed, sims, new_seasons)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--games", type=Path, nargs="+", required=True)
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--committed", type=Path, required=True, help="確定済みの season.jsonl（基準の線の対照の相手）")
    ap.add_argument("--new-seasons", type=int, nargs="*", default=[],
                    help="確定済みの season.jsonl にまだ行がない新しい年（例: 2026）。その年の単位は対照から外して数だけ記録する")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--sims", type=int, help="設定の sims と違う値で走らせる（対照が合わなくなるので、動作確認用）")
    ap.add_argument("--grid", type=float, nargs="+", default=list(GRID), help="振る ε（暫定。結論には使わない）")
    ap.add_argument("--min-games", type=int, nargs="+", default=list(MIN_GAMES))
    ap.add_argument("--ends", nargs="+", default=list(ENDS), choices=ENDS)
    ap.add_argument("--variant-eps", type=float, default=VARIANT_EPS, help="線を動かす実行で使う ε（暫定）")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(args.repo / "sakanalytics"))
    import sakanalytics as sa

    cfg = tomllib.loads(args.config.read_text(encoding="utf-8"))
    traj = cfg.get("trajectory") or {}
    sims = args.sims or int(traj.get("sims", sa.TRAJ_SIMS))
    base = (int(traj.get("min_games", sa.TRAJ_MIN_GAMES)), str(traj.get("end", "season")))
    tg = sa.to_team_games(sa.read_games(args.games), cfg["teams"])
    args.outdir.mkdir(parents=True, exist_ok=True)

    trial.self_check(sa)
    committed = {}
    for line in args.committed.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        committed[(r["season"], r["team"])] = r
    run = Runner(sa, tg, sims)
    g = gate(run(*base), committed, sims, args.new_seasons)
    (args.outdir / "wave_eps_sensitivity_gate.json").write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
    if not g["pass"]:
        print(f"対照が合わない（{g}）。分析は走らせない。", file=sys.stderr)
        return 2

    report = analyze(sa, tg, sims, tuple(args.grid), tuple(args.min_games), tuple(args.ends), args.variant_eps, base)
    (args.outdir / "wave_eps_sensitivity.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.outdir / "wave_eps_sensitivity.md").write_text(render(report), encoding="utf-8")
    with (args.outdir / "wave_eps_boundary_membership.jsonl").open("w", encoding="utf-8") as f:
        for m in report["variants"]["membership"]:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
