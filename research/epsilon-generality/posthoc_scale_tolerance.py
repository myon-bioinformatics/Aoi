#!/usr/bin/env python3
"""物理量の回で、値の単位を 1e-6 倍にしたときだけ選ばれる式が大きく動いた理由の確認（事後。登録した基準の外）。

仮説: sakanalytics の絶対値の許容 EPS_WAVE_TIE（誤差の2乗和の差がこれ以下なら、先に並べた式のままにする）が、
値を c 倍すると c² 倍になる誤差の2乗和の尺度に対して大きくなりすぎ、ほぼ同点でない式まで「同点」にしてしまう。
EPS_WAVE_SOLVE は基準の格子だけで決まり y によらないので、仮説の外。

予想（走らせる前に書く）:
  (a) 許容をそのままにして倍率を細かく動かすと、式が動き始める倍率が見つかる（README の 1e-3 以上では動かず、1e-6 では動いた）
  (b) 許容に倍率の2乗をかけると、どの倍率でも式は変わらない（係数は浮動小数点の誤差の範囲）
(b) で変わるなら、この仮説は足りない。(b) で変わらなくても、それは「この許容が原因の全部」を示すだけで、直し方は決めない。

使い方（リポジトリの直下から）:
  uv run --locked python research/epsilon-generality/posthoc_scale_tolerance.py \\
      --monthly-csv out/physical/physical_monthly_vertical.csv --daily-csv out/physical/physical_daily_vertical.csv \\
      --outdir out/posthoc --repo .
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINE = (1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1.0)        # 値の幅 5 にそろえたあとの y と τ にかける倍率。1 が基準
TIE = 1e-12                                                   # sakanalytics.EPS_WAVE_TIE の今の値（比べるための参照）


def load_gen():
    spec = importlib.util.spec_from_file_location("eps_generality", HERE / "eps_generality.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["eps_generality"] = mod
    spec.loader.exec_module(mod)
    return mod


@contextmanager
def patched(gen, sa, scales, scale_tie: bool):
    """gen.SCALES を差し替え、scale_tie なら fit_row の間だけ EPS_WAVE_TIE を（倍率の2乗）倍にする。終わったら必ず元に戻す。"""
    old_scales, old_fit, old_tie = gen.SCALES, gen.fit_row, sa.EPS_WAVE_TIE      # 許容は wrapped が当てはめのたびに戻す

    def wrapped(sa_, bases, ys, tau):
        f = tau / gen.PRIMARY_TAU
        sa_.EPS_WAVE_TIE = old_tie * f * f if scale_tie else old_tie
        try:
            return old_fit(sa_, bases, ys, tau)
        finally:
            sa_.EPS_WAVE_TIE = old_tie
    gen.SCALES, gen.fit_row = scales, wrapped
    try:
        yield
    finally:
        gen.SCALES, gen.fit_row = old_scales, old_fit


def analyse(gen, sa, mod, series: dict, cadence: str, scales=FINE) -> dict:
    n = gen.PRIMARY
    windows = gen.tile(series, n, gen.CADENCE[cadence]["text"])
    bases = gen.make_bases(sa, mod, [i / (n - 1) for i in range(n)])
    out = {"windows": len(windows), "n": n}
    for name, scale_tie in (("tolerance_unchanged", False), ("tolerance_scaled", True)):
        with patched(gen, sa, scales, scale_tie):
            out[name] = gen.scale_summary(sa, bases, windows)
    return out


def fmt(v) -> str:
    return "—" if v is None else (f"{v:.3g}" if isinstance(v, float) else str(v))


def render(res: dict) -> str:
    L = ["# 値の単位を変えたときの許容の確認（事後。登録した基準の外）", "",
         "予想は [posthoc_scale_tolerance.py](../posthoc_scale_tolerance.py) の冒頭に、走らせる前に書いたもの。"
         "倍率 1 が基準。「式が変わった」は選ばれる（減衰, 周期）が倍率 1 と違う単位の数。", ""]
    for kind, label in (("monthly", "月次"), ("daily", "日次")):
        d = res[kind]
        L += [f"## {label}（{d['n']} 点の窓 {d['windows']} 個）", ""]
        for name, title in (("tolerance_unchanged", "許容 EPS_WAVE_TIE をそのまま（1e-12）"),
                            ("tolerance_scaled", "許容に倍率の2乗をかけた")):
            L += [f"### {title}", "", "| 倍率 | 単位 | 境界 | 式が変わった | 境界かどうかが変わった | 係数のずれの最大（相対）| 比べた単位 |", "|---|---|---|---|---|---|---|"]
            for f, s in d[name].items():
                L.append(f"| {f} | {s['units']} | {s['boundary']} | {s['forms_changed']} | {s['boundary_flag_changed']} | "
                         f"{fmt(s['coefficient_max_dev'])} | {s['coefficient_n']} |")
            L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--monthly-csv", type=Path, required=True)
    ap.add_argument("--daily-csv", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    gen = load_gen()
    sa, mod = gen.load_modules(args.repo)
    res = {}
    for kind, path, profile in (("monthly", args.monthly_csv, "physical-monthly"), ("daily", args.daily_csv, "physical-daily")):
        p = gen.PROFILES[profile]
        res[kind] = analyse(gen, sa, mod, gen.read_series(path, p["prefix"], p["cadence"]), p["cadence"])
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "posthoc_scale_tolerance.json").write_text(gen.dumps(res) + "\n", encoding="utf-8")
    (args.outdir / "posthoc_scale_tolerance.md").write_text(render(res), encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
