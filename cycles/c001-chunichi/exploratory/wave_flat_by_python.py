#!/usr/bin/env python3
"""一定の線に当てはめる式が、Python のバージョンで変わるかの確認（探索・事後。確定した出力は変えない）。

きっかけ（結果を見たあとに気づいたこと。予想は置いていない）:
  CI の pytest（Python 3.11）で、誤差の2乗和が 1e-18 未満という私のテストだけが 3.11 で 7e-15 になって落ちた。
  組み込みの sum() は 3.12 から float の足し方が変わった（3.11: 0.1 を 10 回足すと 0.9999999999999999、3.12 以降: 1.0）。
  wave_fit の閉じた式は sum() で誤差の2乗和を作っているので、一定の線（どの式でも誤差が 0 のはずの線）では、
  丸めで決まる式が 3.11 と 3.12 以降で違いうる。

やること: 合成の一定の線（値 c を n 点。実データではない）32 本に、標準の波の基準（sa.wave_basis）で wave_fit を当て、
  選ばれた（減衰, 周期）を JSON で出す。インタプリタごとに 1 回走らせ、ファイルを並べて比べる。
限り: 合成の一定の線だけ。確定済みの出力が 3.11 で変わるかは、この確認では分からない。ε の波の基準（wave_eps_trial）では見ていない。

使い方（リポジトリの直下から。インタプリタごとに）:
  uv run --locked --python 3.11 python cycles/c001-chunichi/exploratory/wave_flat_by_python.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LENGTHS = (30, 60, 100, 150)
LEVELS = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 0.7, 2.3)


def load_sa(root: Path = ROOT):
    spec = importlib.util.spec_from_file_location("sakanalytics_flat", root / "sakanalytics" / "sakanalytics.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flat_forms(sa) -> dict[str, list]:
    out = {}
    for n in LENGTHS:
        basis = sa.wave_basis([i / (n - 1) for i in range(n)])
        for c in LEVELS:
            f = sa.wave_fit([c] * n, basis, 0.0, 1.0)
            out[f"n={n} c={c}"] = [f["decay"], f["period"]]
    return out


def main() -> int:
    print(json.dumps({"python": sys.version.split()[0], "forms": flat_forms(load_sa())}, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
