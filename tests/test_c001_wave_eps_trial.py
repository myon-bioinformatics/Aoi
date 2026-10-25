"""cycles/c001-chunichi/exploratory/wave_eps_trial.py の確認。減衰 0 を ε に差し替える変換が、元の当てはめと整合するか。

合成の線（SYNTHETIC）を使う。実データではなく、変換の性質（ε = 0 で元と同一、ε → 0 で連続、落ち着く位置が 1/ε に比例）を確かめるだけで、結論には使わない。
"""
import importlib.util
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sakanalytics"))
import sakanalytics as sa  # noqa: E402

spec = importlib.util.spec_from_file_location("wave_eps_trial", ROOT / "cycles" / "c001-chunichi" / "exploratory" / "wave_eps_trial.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)

XS = [0.1 + 0.9 * i / 60 for i in range(61)]
# 減衰しない波 + ゆるい傾き（周期 2.0 の波が選ばれるはずの線）
YS = [3.5 + 1.2 * math.cos(math.pi * (x - XS[0])) + 0.6 * math.sin(math.pi * (x - XS[0])) for x in XS]


def test_swap_is_identity_at_eps_zero():
    trial.self_check(sa)


def test_original_has_no_limit_for_undamped_wave():
    f = sa.wave_fit(YS, sa.wave_basis(XS), XS[0])
    assert f["decay"] == 0.0 and f["limit"] is None and f["settle_x"] is None


def test_eps_restores_finite_limit_and_settle():
    f = sa.wave_fit(YS, trial.make_wave_basis(sa, 1e-6)(XS), XS[0])
    assert f["decay"] == 1e-6 and f["limit"] is not None and f["settle_x"] > 1


def test_limit_is_continuous_as_eps_goes_to_zero():
    lim = [sa.wave_fit(YS, trial.make_wave_basis(sa, e)(XS), XS[0])["limit"] for e in (1e-3, 1e-6, 1e-9)]
    assert abs(lim[1] - lim[2]) < 1e-5 and abs(lim[0] - lim[2]) < 1e-2


def test_settle_position_scales_with_inverse_eps():
    s = [sa.wave_fit(YS, trial.make_wave_basis(sa, e)(XS), XS[0]) for e in (1e-6, 1e-9)]
    a, b = ((f["settle_x"] - XS[0]) * e for f, e in zip(s, (1e-6, 1e-9)))
    assert abs(a - b) / b < 1e-3
