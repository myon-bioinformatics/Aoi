#!/usr/bin/env python3
"""波の当てはめで、減衰 λ = 0 の境界を ε に置き換える試し（探索）。

サイクル1の確定した出力（season.jsonl など）は書き換えない。結果は --outdir にだけ書く。
ε の値はすべて暫定の置き場所で、出力に記録する。結論には使わない（扱いは今後決める）。

やること:
  1. 対照: 今のコードのまま season_trajectory を走らせ、確定済みの season.jsonl の wave_* と一致するか確かめる（一致しなければ止まる）
  2. 試し: wave_basis の「減衰 0」の行を ε に差し替えて走らせる（ε ごとに1回）
  3. 比べる: 減衰 0 だった行で wave_* がどう戻るか、ほかの行が動くか、ε を変えたときの動きを書き出す

使い方（試合ごとのデータ games.jsonl がある環境で。リポジトリの直下から）:
  uv run --locked python wave_eps_trial.py \
      --games data/observations/npb_calendar/games.jsonl \
      --config cycles/c001-chunichi/analysis.toml \
      --committed cycles/c001-chunichi/outputs/season.jsonl \
      --eps 1e-3 1e-6 1e-9 --outdir /tmp/wave-eps-trial
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
import tomllib
from pathlib import Path

WAVE_COLS = ["wave_limit_rank", "wave_end_rank", "wave_decay", "wave_period", "wave_osc", "wave_settle_x",
             "wave_rmse", "wave_settle_pct", "wave_osc_base", "wave_limit_rank_h1"]
TOL = 1e-9


def same(a, b) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))


def entry(lam, per, t):
    """sakanalytics.wave_basis の1格子分。式は同じ（self-check で eps=0 のとき完全に一致することを確かめる）。"""
    w = 2 * math.pi / per if per else 0.0
    ec = [math.exp(-lam * u) * math.cos(w * u) for u in t]
    es = [math.exp(-lam * u) * math.sin(w * u) for u in t]
    sec, sec2, sese = sum(ec), sum(e * e for e in ec), sum(a * b for a, b in zip(ec, es))
    return {"lam": lam, "per": per, "w": w, "ec": ec, "es": es, "sec": sec, "sec2": sec2, "sese": sese,
            "uu": len(t) - 2 * sec + sec2, "uv": sum(es) - sese, "vv": sum(e * e for e in es)}


def make_wave_basis(sa, eps: float):
    orig = sa.wave_basis

    def wave_basis_eps(xs):
        t = [x - xs[0] for x in xs]
        kept = [b for b in orig(xs) if b["lam"] != 0.0]          # λ > 0 の格子は元のまま
        tail = [entry(eps, per, t) for per in sa.WAVE_PERIODS if per]  # 末尾の「減衰しない波」だけ ε に差し替える
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


def gate(ctrl: dict, committed: dict, sims: int, new_seasons=()) -> dict:
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
    g = gate(ctrl, committed, sims, args.new_seasons)
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


if __name__ == "__main__":
    raise SystemExit(main())
