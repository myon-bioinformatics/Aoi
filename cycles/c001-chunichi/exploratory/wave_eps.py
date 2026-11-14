"""波の減衰 0 を ε に差し替える試し（探索。正本の season.jsonl と sakanalytics は変えない）。

    uv run --locked python cycles/c001-chunichi/exploratory/wave_eps.py <処理> [その処理の引数]

処理:
  trial                減衰 0 を ε に差し替えて当て直し、行を書く（旧 wave_eps_trial.py）
  sensitivity          ε・線の始まり・終わりを動かしたときの感度（旧 wave_eps_sensitivity.py）
  settle_coefficients  落ち着く位置を「係数 × 1 / 減衰」で読む（旧 wave_eps_settle_coefficients.py）
説明と引数は各関数の説明（旧ファイルの冒頭）にある。結果は wave_eps_*_results/ の README。
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
import tomllib
from pathlib import Path


# ==== trial（旧 wave_eps_trial.py）

TRIAL_CLI_DOC = """波の当てはめで、減衰 λ = 0 の境界を ε に置き換える試し（探索）。

サイクル1の確定した出力（season.jsonl など）は書き換えない。結果は --outdir にだけ書く。
ε の値はすべて暫定の置き場所で、出力に記録する。結論には使わない（扱いは今後決める）。

やること:
  1. 対照: 今のコードのまま season_trajectory を走らせ、確定済みの season.jsonl の wave_* と一致するか確かめる（一致しなければ止まる）
  2. 試し: wave_basis の「減衰 0」の行を ε に差し替えて走らせる（ε ごとに1回）
  3. 比べる: 減衰 0 だった行で wave_* がどう戻るか、ほかの行が動くか、ε を変えたときの動きを書き出す

使い方（試合ごとのデータ games.jsonl がある環境で。リポジトリの直下から）:
  uv run --locked python cycles/c001-chunichi/exploratory/wave_eps.py trial \
      --games data/observations/npb_calendar/games.jsonl \
      --config cycles/c001-chunichi/analysis.toml \
      --committed cycles/c001-chunichi/outputs/season.jsonl \
      --eps 1e-3 1e-6 1e-9 --outdir /tmp/wave-eps-trial
"""

WAVE_COLS = ["wave_limit_rank", "wave_end_rank", "wave_decay", "wave_period", "wave_osc", "wave_settle_x",
             "wave_rmse", "wave_settle_pct", "wave_osc_base", "wave_limit_rank_h1"]
TOL = 1e-9


def same(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))


def entry(lam, per, t, boundary=False):
    """sakanalytics.wave_basis の1格子分。式は同じ（self-check で eps=0 のとき完全に一致することを確かめる）。

    boundary: 減衰しない波の行（λ の境界）か。sakanalytics.wave_basis の各行の "boundary" と同じ意味。
    """
    w = 2 * math.pi / per if per else 0.0
    ec = [math.exp(-lam * u) * math.cos(w * u) for u in t]
    es = [math.exp(-lam * u) * math.sin(w * u) for u in t]
    sec, sec2, sese = sum(ec), sum(e * e for e in ec), sum(a * b for a, b in zip(ec, es))
    return {"lam": lam, "per": per, "w": w, "ec": ec, "es": es, "sec": sec, "sec2": sec2, "sese": sese,
            "uu": len(t) - 2 * sec + sec2, "uv": sum(es) - sese, "vv": sum(e * e for e in es), "boundary": boundary}


def make_wave_basis(sa, eps: float):
    orig = sa.wave_basis

    def wave_basis_eps(xs, _eps=None):
        # _eps: sakanalytics.season_trajectory が wave_basis(xs, wave_eps) と2つ目を渡すため受ける。ε はこの関数に固定済みなので使わない
        t = [x - xs[0] for x in xs]
        kept = [b for b in orig(xs) if b["lam"] != 0.0]          # λ > 0 の格子は元のまま
        tail = [entry(eps, per, t, True) for per in sa.WAVE_PERIODS if per]  # 末尾の「減衰しない波」だけ ε に差し替える
        return kept + tail

    return wave_basis_eps


def self_check(sa) -> None:
    xs = [i / 40 for i in range(41)]
    a, b = sa.wave_basis(xs), make_wave_basis(sa, 0.0)(xs)
    assert len(a) == len(b) and all(x == y for x, y in zip(a, b)), "差し替え版が eps=0 で元と一致しない"


def trajectory(sa, tg, wave_basis, sims, min_games, end):
    orig = sa.wave_basis
    sa.wave_basis = wave_basis
    try:
        t0 = time.time()
        df = sa.season_trajectory(tg, sims=sims, min_games=min_games, end=end)
        print(f"  season_trajectory {time.time() - t0:.0f}s", file=sys.stderr)
    finally:
        sa.wave_basis = orig
    cols = ["season", "team", "traj_start_x"] + WAVE_COLS
    return {(r["season"], r["team"]): r for r in df.select(cols).to_dicts()}


def diff_rows(a: dict, b: dict) -> dict:
    """キーごとに、wave_* のうち値が違う列の一覧。"""
    out = {}
    for k in sorted(a):
        cols = [c for c in WAVE_COLS if not same(a[k].get(c), b[k].get(c))]
        if cols:
            out[k] = cols
    return out


def trial_cli_gate(ctrl: dict, committed: dict, sims: int, new_seasons=()) -> dict:
    """対照の関門。new_seasons の年は、確定済みの season.jsonl にまだ行がない新しい年。その年の単位だけは対照の相手がないので
    比べず、数を記録する。ほかの年は今までどおり全部が確定済みと合う必要がある。新しい年に確定済みの行がある、
    またはその年の単位が 1 つもない（年の指定まちがい）ときは、関門を通さない。"""
    new = set(new_seasons)
    fresh = [k for k in ctrl if k[0] in new]
    old = {k: v for k, v in ctrl.items() if k[0] not in new}
    missing = [k for k in old if k not in committed]
    bad = diff_rows(old, {k: committed[k] for k in old if k in committed}) if not missing else {}
    in_committed = sorted(k for k in committed if k[0] in new)
    unknown = sorted(new - {k[0] for k in fresh})
    g = {"units": len(ctrl), "not_in_committed": len(missing), "rows_differ": len(bad), "sims": sims}
    if new:
        g |= {"new_seasons": sorted(new), "new_units": len(fresh), "new_seasons_with_committed_rows": len(in_committed),
              "new_seasons_without_units": unknown}
    g["pass"] = not missing and not bad and not in_committed and not unknown
    return g


def trial_cli(argv=None) -> int:
    ap = argparse.ArgumentParser(description=TRIAL_CLI_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--games", type=Path, nargs="+", required=True)
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--committed", type=Path, required=True, help="確定済みの season.jsonl（対照の相手）")
    ap.add_argument("--new-seasons", type=int, nargs="*", default=[],
                    help="確定済みの season.jsonl にまだ行がない新しい年（例: 2026）。その年の単位は対照から外して数だけ記録する")
    ap.add_argument("--eps", type=float, nargs="+", default=[1e-3, 1e-6, 1e-9], help="暫定の ε（記録する。結論には使わない）")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--sims", type=int, help="設定の sims と違う値で走らせる（対照が合わなくなるので、動作確認用）")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(args.repo / "sakanalytics"))
    import polars as pl  # noqa: F401
    import sakanalytics as sa

    cfg = tomllib.loads(args.config.read_text(encoding="utf-8"))
    traj = cfg.get("trajectory") or {}
    sims = args.sims or int(traj.get("sims", sa.TRAJ_SIMS))
    min_games, end = int(traj.get("min_games", sa.TRAJ_MIN_GAMES)), str(traj.get("end", "season"))
    tg = sa.to_team_games(sa.read_games(args.games), cfg["teams"])
    args.outdir.mkdir(parents=True, exist_ok=True)

    self_check(sa)
    committed = {}
    for line in args.committed.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        committed[(r["season"], r["team"])] = r

    print("対照（今のコード）", file=sys.stderr)
    ctrl = trajectory(sa, tg, sa.wave_basis, sims, min_games, end)
    g = trial_cli_gate(ctrl, committed, sims, args.new_seasons)
    (args.outdir / "wave_eps_trial_gate.json").write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
    if not g["pass"]:
        print(f"対照が合わない（{g}）。試しは走らせない。", file=sys.stderr)
        return 2

    zero = sorted(k for k, r in ctrl.items() if r["wave_decay"] == 0.0)
    results = {}
    for eps in args.eps:
        print(f"ε = {eps:g}（暫定）", file=sys.stderr)
        results[eps] = trajectory(sa, tg, make_wave_basis(sa, eps), sims, min_games, end)

    lines = [f"# 波の減衰 0 → ε の試し（探索）", "",
             "確定した出力は変更していない。ε の値は暫定の置き場所で、結論には使わない。扱いは今後決める。", "",
             f"- 単位数: {len(ctrl)}、sims: {sims}、対照（今のコード vs 確定済み season.jsonl）: 一致"
             + (f"（{', '.join(map(str, g['new_seasons']))} 年の {g['new_units']} 単位は確定済みの行がなく、対照の外）" if g.get('new_seasons') else ''),
             f"- 減衰 0 の単位: {len(zero)}（確定済みで wave_limit_rank が空欄の単位: "
             f"{sum(ctrl[k]['wave_limit_rank'] is None for k in zero)}）",
             f"- 暫定の ε: {', '.join(f'{e:g}' for e in args.eps)}", ""]
    lines += ["## 減衰 0 だった単位で、指標が戻るか", "",
              "| ε | 選ばれた式がまだ ε の波 | wave_limit_rank が出る | wave_settle_x が出る | 周期・減衰が別の式に変わった（全単位） | 対照と値が変わった単位（全体） |",
              "|---|---|---|---|---|---|"]
    for eps, res in results.items():
        still = [k for k in zero if res[k]["wave_decay"] == eps]
        limit_ok = sum(res[k]["wave_limit_rank"] is not None for k in zero)
        settle_ok = sum(res[k]["wave_settle_x"] is not None for k in zero)
        switched = [k for k in res
                    if ctrl[k]["wave_period"] != res[k]["wave_period"]
                    or not (ctrl[k]["wave_decay"] == res[k]["wave_decay"]
                            or (ctrl[k]["wave_decay"] == 0.0 and res[k]["wave_decay"] == eps))]
        changed = diff_rows(ctrl, res)
        lines.append(f"| {eps:g} | {len(still)}/{len(zero)} | {limit_ok}/{len(zero)} | {settle_ok}/{len(zero)} | {len(switched)} | {len(changed)} |")
    lines.append("")

    lines += ["## ε を変えても動かないもの・動くもの（減衰 0 だった単位、ε の波が残る単位のみ）", ""]
    base_eps = list(results)
    keep = [k for k in zero if all(results[e][k]["wave_decay"] == e for e in base_eps)]
    lines.append(f"- 全部の ε で ε の波が選ばれた単位: {len(keep)}/{len(zero)}")
    if keep:
        spread = max(max(results[e][k]["wave_limit_rank"] for e in base_eps) - min(results[e][k]["wave_limit_rank"] for e in base_eps)
                     for k in keep)
        lines.append(f"- wave_limit_rank の ε による最大のずれ（順位の単位）: {spread:.3g}")
        prod = {}
        for e in base_eps:
            for k in keep:
                s = results[e][k]["wave_settle_x"]
                if s is not None and s > results[e][k]["traj_start_x"]:
                    prod.setdefault(k, []).append((s - results[e][k]["traj_start_x"]) * e)
        if prod:
            rel = max((max(v) - min(v)) / max(abs(max(v)), 1e-300) for v in prod.values())
            lines.append(f"- (wave_settle_x − 始まり) × ε の ε による相対のずれ（最大。ln(振れ幅/0.5) が一定なら 0 に近い）: {rel:.3g}")
        orders = [tuple(sorted(keep, key=lambda k: (results[e][k]["wave_settle_x"] is None, results[e][k]["wave_settle_x"] or 0, k)))
                  for e in base_eps]
        lines.append(f"- wave_settle_x の並びが ε のあいだで同じ: {'はい' if len(set(orders)) == 1 else 'いいえ'}")
    lines.append("")

    lines += ["## ほかの単位への波及", ""]
    for eps, res in results.items():
        changed = diff_rows(ctrl, res)
        others = {k: v for k, v in changed.items() if k not in zero}
        cols = {}
        for v in others.values():
            for c in v:
                cols[c] = cols.get(c, 0) + 1
        h1_null_c = sum(ctrl[k]["wave_limit_rank_h1"] is None for k in ctrl)
        h1_null_r = sum(res[k]["wave_limit_rank_h1"] is None for k in res)
        flat = [k for k in others if (ctrl[k]["wave_rmse"] or 0.0) < 1e-6]
        lines.append(f"- ε = {eps:g}: 減衰 0 でなかった単位のうち値が動いたもの {len(others)}/{len(ctrl) - len(zero)}"
                     f"（列ごと: {cols or 'なし'}）。うち、線が完全に平ら（wave_rmse < 1e-6）の単位 {len(flat)}。"
                     f"wave_limit_rank_h1 の空欄 {h1_null_c} → {h1_null_r}")
    flat_all = [k for k in ctrl if (ctrl[k]["wave_rmse"] or 0.0) < 1e-6]
    lines.append(f"- 対照で線が完全に平ら（wave_rmse < 1e-6）の単位: {len(flat_all)}。"
                 f"うち波（周期あり）が選ばれている単位: {sum(ctrl[k]['wave_period'] is not None for k in flat_all)}")
    lines.append("")
    lines += ["## 読み方の注意", "",
              "- 減衰を ε にしても、当てはめの波そのもの（L・B・周期）は連続に動く。戻るのは「収束する先」と「落ち着く位置」の定義で、"
              "減衰がごく小さいので落ち着く位置は非常に大きい（1 を超える = シーズン中には決まらない）値になる。",
              "- 戻った wave_limit_rank は、減衰しない波では**波の中心**という形式的な値で、「収束する先」という意味ではない。"
              "`eps_used` で分けて読む。",
              "- wave_settle_pct が変わるのは、確定済みで settle_x が空欄だった単位（自分が無限大だったもの）。"
              "疑似シーズン側でも減衰 0 が選ばれると、以前は無限大どうしの同順位（0.5 と数える）だったものが、ε では有限の大きな値どうしの比較になり、並びが付く。",
              "- 線が完全に平らな単位では、どの式も誤差の2乗和がほぼ 0 になり、選ばれる式が丸め誤差と固定の許容値（1e-12）で決まる。"
              "その場合は ε に差し替えると選ばれる式が変わりうる（暗黙の許容値 = 前回の洗い出しの (C)）。",
              "- `eps_used` = 選ばれた式の減衰が ε そのもの。出力の行に付けている。"]
    (args.outdir / "wave_eps_trial.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for eps, res in results.items():
        with (args.outdir / f"wave_eps_rows_{eps:g}.jsonl").open("w", encoding="utf-8") as f:
            for k in sorted(res):
                row = {"season": k[0], "team": k[1], "eps_provisional": eps, "eps_used": int(res[k]["wave_decay"] == eps),
                       "zero_in_committed": int(k in zero)}
                row |= {f"committed_{c}": ctrl[k][c] for c in WAVE_COLS} | {f"eps_{c}": res[k][c] for c in WAVE_COLS}
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


# ==== sensitivity（旧 wave_eps_sensitivity.py）

SENSITIVITY_CLI_DOC = """波の減衰 0 → ε の試しを、動かし方を変えて読む（探索）。確定した出力は変更しない。

ε の値は暫定の置き場所で、結論には使わない。扱いは今後決める。wave_eps_trial.py（同じ置き場）の差し替え版 wave_basis を使って、
次の2つを調べる。

  1. ε を 1e-1 〜 1e-12 に振る（線の始まり・終わりは設定のまま）: 境界の単位が ε の波に戻るか、境界でなかった単位が乗り換わるのは
     ε がいくつからか、最後の日の順位・収束先・落ち着く位置が ε でどう動くか。
  2. 線の始まり（min_games）と終わり（season / decided）を動かす（ε は 1 つに固定）: 境界の単位がどう入れ替わるか、
     境界に残った単位の収束先は動かないか。

境界の単位 = 当てはめで選ばれた式が「減衰しない波」（λ = 0）だった単位。ε を渡した実行では、選ばれた式の減衰が ε そのものの単位。

使い方（試合ごとのデータ games.jsonl がある環境で。リポジトリの直下から）:
  uv run --locked python cycles/c001-chunichi/exploratory/wave_eps.py sensitivity \\
      --games data/observations/npb_calendar/games.jsonl --config cycles/c001-chunichi/analysis.toml \\
      --committed cycles/c001-chunichi/outputs/season.jsonl --outdir /tmp/wave-eps-sensitivity

線の始まり・終わりを設定のまま（対照）走らせた結果が確定済みの season.jsonl の wave_* と合わなければ止まる（wave_eps_trial.py と同じ関門）。
"""

HERE = Path(__file__).resolve().parent

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
            basis = self.sa.wave_basis if eps is None else make_wave_basis(self.sa, eps)
            self.cache[key] = trajectory(self.sa, self.tg, basis, self.sims, min_games, end)
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
        changed = diff_rows(ctrl, res)
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


def sensitivity_cli_render(report: dict) -> str:
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


def sensitivity_cli_gate(ctrl: dict, committed: dict, sims: int, new_seasons=()) -> dict:
    return trial_cli_gate(ctrl, committed, sims, new_seasons)


def sensitivity_cli(argv=None) -> int:
    ap = argparse.ArgumentParser(description=SENSITIVITY_CLI_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
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

    self_check(sa)
    committed = {}
    for line in args.committed.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        committed[(r["season"], r["team"])] = r
    run = Runner(sa, tg, sims)
    g = sensitivity_cli_gate(run(*base), committed, sims, args.new_seasons)
    (args.outdir / "wave_eps_sensitivity_gate.json").write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
    if not g["pass"]:
        print(f"対照が合わない（{g}）。分析は走らせない。", file=sys.stderr)
        return 2

    report = analyze(sa, tg, sims, tuple(args.grid), tuple(args.min_games), tuple(args.ends), args.variant_eps, base)
    (args.outdir / "wave_eps_sensitivity.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.outdir / "wave_eps_sensitivity.md").write_text(sensitivity_cli_render(report), encoding="utf-8")
    with (args.outdir / "wave_eps_boundary_membership.jsonl").open("w", encoding="utf-8") as f:
        for m in report["variants"]["membership"]:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


# ==== settle_coefficients（旧 wave_eps_settle_coefficients.py）

SETTLE_CLI_DOC = """波の減衰 0 → ε の試し: 落ち着く位置を「係数 × 10^n」で書く（探索）。

ε を ε = a × 10^-n（1 ≤ a < 10）と書くと、減衰 λ = ε の波の落ち着く位置は、ε を小さくした範囲で
「係数 × 10^n」の形になる（ε を 10 倍小さくすると指数 n が 1 上がり、係数はほとんど動かない）。
係数は決めた数ではなく、保存済みの行（wave_eps_trial.py の wave_eps_rows_<ε>.jsonl、ε が 2 つ以上）の
settle_x を 10^n で割って出てきた数で、a を替えれば 1/a 倍になる。
ここでは単位ごとに、ε ごとの落ち着く位置を「仮数 × 10^指数」で並べ、最小の ε の行の係数を基準に、
ほかの ε の位置がこの形からどれだけ外れるか（絶対・相対の最大）を出す。振れ幅は、落ち着く位置の式
（x0 + ln(振れ幅 / 0.5) / λ）に a = 1 の係数を入れて戻した値（0.5 × exp(係数)）。振れ幅が最初から小さい単位は、
落ち着く位置が ε によらず一定（settled_at_start）で、係数の形には載せない。

標準ライブラリのみ。ε の値は暫定の置き場所で、結論には使わない。

使い方（リポジトリの直下から）:
  python cycles/c001-chunichi/exploratory/wave_eps.py settle_coefficients \\
      --rows cycles/c001-chunichi/exploratory/wave_eps_trial_results/wave_eps_rows_*.jsonl \\
      --out-json /tmp/coef.json --out-md /tmp/coef.md
"""

SAME = 1e-9          # 2 つの ε で落ち着く位置が（相対で）これ以下しか違わなければ、ε によらない一定の位置とみなす
SETTLE = 0.5         # sakanalytics.WAVE_SETTLE（ゆれの幅が半順位を下回る位置）
NONE = "該当なし（動く単位がない）"


def validate_eps(eps: float) -> None:
    if isinstance(eps, bool) or not isinstance(eps, (int, float)) or not math.isfinite(eps) or eps <= 0:
        raise ValueError(f"ε は有限の正数でなければならない: {eps!r}")


def load(path: Path) -> tuple[float, dict]:
    eps, units = set(), {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        try:
            validate_eps(r["eps_provisional"])
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
        key = (r["season"], r["team"])
        if key in units:
            raise ValueError(f"{path}:{line_number}: 単位が重複している: {key}")
        eps.add(r["eps_provisional"])
        units[key] = r
    if len(eps) != 1:
        raise ValueError(f"{path}: ε が 1 つに決まらない {sorted(eps)}")
    return eps.pop(), units


def eps_form(eps: float) -> tuple[float, int]:
    """ε = a × 10^-n（1 ≤ a < 10）の (a, n)。"""
    validate_eps(eps)
    n = -math.floor(math.log10(eps) + 1e-12)
    return round(eps * 10 ** n, 12), n


def sci(x: float) -> str:
    """x を「仮数×10^指数」（仮数は有効数字 3 桁）で書く。"""
    m, e = f"{x:.2e}".split("e")
    return f"{m}×10^{int(e)}"


def coefficients(by_eps: dict) -> list[dict]:
    """by_eps: {ε: {(season, team): 行}}。減衰 0 だった単位ごとに、ε ごとの落ち着く位置と係数（位置 / 10^n）、
    最小の ε の係数を基準にしたときの外れ（与えた ε のうち最大）を返す。"""
    if len(by_eps) < 2:
        raise ValueError("ε が 2 つ以上いる")
    for e in by_eps:
        validate_eps(e)
    eps = sorted(by_eps)
    lo, mid = eps[0], eps[1]
    units = set(by_eps[lo])
    for e in eps[1:]:
        actual = set(by_eps[e])
        if actual != units:
            raise ValueError(f"ε={e:g}: 単位集合が ε={lo:g} と一致しない: "
                             f"欠落={sorted(units - actual)}, 余剰={sorted(actual - units)}")
    a_lo, n_lo = eps_form(lo)
    out = []
    for key in sorted(by_eps[lo]):
        if by_eps[lo][key]["committed_wave_decay"] != 0:
            continue
        s = {e: by_eps[e][key]["eps_wave_settle_x"] for e in eps}
        if any(v is None or by_eps[e][key]["eps_wave_decay"] != e for e, v in s.items()):
            raise ValueError(f"{key}: ε の波が選ばれていない行がある")
        if abs(s[lo] - s[mid]) <= SAME * max(1.0, abs(s[lo])):
            out.append({"season": key[0], "team": key[1], "settled_at_start": True, "position": s[lo], "coefficient": None,
                        "amp": None, "by_eps": [], "abs_miss": None, "rel_miss": None})
            continue
        ref = s[lo] * a_lo / 10 ** n_lo              # a = 1 に揃えた係数（a を替えると 1/a 倍になる）
        per, miss = [], []
        for e in eps:
            a, n = eps_form(e)
            predicted = ref / a * 10 ** n            # 最小の ε の係数を、この ε の a と n に置き直した位置
            per.append({"eps": e, "a": a, "n": n, "settle": s[e], "coefficient": s[e] / 10 ** n})
            miss.append((abs(s[e] - predicted), abs(s[e] - predicted) / abs(s[e])))
        out.append({"season": key[0], "team": key[1], "settled_at_start": False, "position": None, "coefficient": per[0]["coefficient"],
                    "amp": SETTLE * math.exp(ref), "by_eps": per, "abs_miss": max(m[0] for m in miss), "rel_miss": max(m[1] for m in miss)})
    return out


def _head(e: float) -> str:
    a, n = eps_form(e)
    return f"ε = {a:g}×10^-{n}"


def settle_cli_render(rows: list[dict], eps: list[float]) -> str:
    moving = [r for r in rows if not r["settled_at_start"]]
    lines = ["# 落ち着く位置 = 係数 × 10^n（ε = a × 10^-n）（探索・暫定）", "",
             f"ε = {', '.join(f'{e:g}' for e in eps)} の行から。ε を 10 倍小さくすると落ち着く位置は約 10 倍遠くなり（指数 n が 1 上がる）、"
             "係数（落ち着く位置 / 10^n）はほとんど動かない。係数は決めた数ではなく行から出てきた数で、a を替えれば 1/a 倍になる。"
             "ε の値は暫定で、結論には使わない。", "",
             f"- 減衰 0 だった単位: {len(rows)}。落ち着く位置が最初から ε によらず一定: {len(rows) - len(moving)}",
             f"- 係数（最小の ε の行、a = {eps_form(eps[0])[0]:g}）: " + (f"{min(r['coefficient'] for r in moving):.4f} 〜 {max(r['coefficient'] for r in moving):.4f}" if moving else NONE),
             "- 最小の ε の係数で、ほかの ε の位置を言い当てたときの外れ（最大）: " + (f"絶対 {max(r['abs_miss'] for r in moving):.3f}（シーズン 1 つぶんが 1）、"
                                                                                f"相対 {max(r['rel_miss'] for r in moving):.2e}" if moving else NONE), "",
             "| 年 | 球団 | " + " | ".join(_head(e) for e in reversed(eps)) + " | 係数（最小の ε） | 振れ幅 | 外れ（絶対 / 相対） |",
             "|---|---|" + "---|" * (len(eps) + 3)]
    for r in rows:
        if r["settled_at_start"]:
            lines.append(f"| {r['season']} | {r['team']} | （最初から一定。位置 {r['position']:.4f}）" + " | —" * (len(eps) + 2) + " |")
        else:
            by = {p["eps"]: p for p in r["by_eps"]}
            cells = " | ".join(sci(by[e]["settle"]) for e in reversed(eps))
            lines.append(f"| {r['season']} | {r['team']} | {cells} | {r['coefficient']:.4f} | {r['amp']:.3f} | {r['abs_miss']:.3f} / {r['rel_miss']:.1e} |")
    return "\n".join(lines) + "\n"


def settle_cli(argv=None) -> int:
    ap = argparse.ArgumentParser(description=SETTLE_CLI_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=Path, nargs="+", required=True, help="wave_eps_rows_<ε>.jsonl（ε が 2 つ以上）")
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args(argv)
    try:
        by_eps = dict(load(p) for p in args.rows)
        if len(by_eps) != len(args.rows):
            raise ValueError("同じ ε の行ファイルが重なっている")
        rows = coefficients(by_eps)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    # 本文は 2 つとも先にメモリ上で作ってから書き出す（途中で例外が出ても、片方だけ新しくなる状態を作らない）。
    json_text = json.dumps({"eps": sorted(by_eps), "units": rows}, ensure_ascii=False, indent=2) + "\n"
    md_text = settle_cli_render(rows, sorted(by_eps))
    args.out_json.write_text(json_text, encoding="utf-8")
    args.out_md.write_text(md_text, encoding="utf-8")
    print(f"書き出し: {args.out_json}, {args.out_md}")
    return 0


# ==== 入口
COMMANDS = {
    "trial": trial_cli,
    "sensitivity": sensitivity_cli,
    "settle_coefficients": settle_cli,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wave_eps.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"wave_eps.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
