"""research/unitcalc: 単位付き計算。次元のビット詰め、厳密な計算、δ の厳密さ、近似の包含、次元違反の拒否。

乱数はすべて seed 固定（パラメータの seed を増やせば別の組が試せる）。係数・ε のような「試す値」は
1e-3 の刻みで決め打ちせず、A x 10^-N の A と N を乱数で選んだ複数の値で確かめる（rand_an）。
判定は数（終了コード・厳密な分数）で比べ、表示の文字列そのものは比べない。
"""
import io
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "unitcalc"))
import unitcalc as u  # noqa: E402

SEEDS = range(5)
SUPD = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")


@pytest.fixture
def reg():
    return u.Reg()


def ev(text, reg):
    return u.evaluate(text, reg)[0]


def same(a, b):
    """厳密に同じ量か（中心・半径・次元）。"""
    return a.m == b.m and a.r == b.r and a.d == b.d


def rand_an(rng):
    """A x 10^-N（A は 1.00..9.99、N は 1..40）。決め打ちの刻みを避けるための乱数。"""
    return F(rng.randint(100, 999), 100) * F(10) ** -rng.randint(1, 40)


def shown_value(text):
    return F(text.translate(SUPD).replace("×10", "e"))


# ---- 次元のビット詰め ----------------------------------------------------------------------------------
@pytest.mark.parametrize("seed", SEEDS)
def test_dim_swar_matches_per_slot_arithmetic(seed):
    rng = random.Random(seed)
    for _ in range(2000):
        # 端（-32, 31）も出やすいようにする
        a = [rng.choice((-32, -1, 0, 1, 31, rng.randint(-32, 31))) for _ in range(u.SLOTS)]
        b = [rng.choice((-32, -1, 0, 1, 31, rng.randint(-32, 31))) for _ in range(u.SLOTS)]
        pa, pb = u.d_pack(a), u.d_pack(b)
        for op, f in ((u.d_mul, lambda x, y: x + y), (u.d_div, lambda x, y: x - y)):
            want = [f(x, y) for x, y in zip(a, b)]
            if all(-32 <= w <= 31 for w in want):
                assert u.d_unpack(op(pa, pb)) == want          # スロット間の桁上がり・借りが無い
            else:
                with pytest.raises(u.DimRange):
                    op(pa, pb)


def test_dim_edges_and_scale():
    top, bot = u.d_pack([31] + [0] * 31), u.d_pack([-32] + [0] * 31)
    one = u.d_pack([1] + [0] * 31)
    with pytest.raises(u.DimRange):
        u.d_mul(top, one)
    with pytest.raises(u.DimRange):
        u.d_div(bot, one)
    assert u.d_unpack(u.d_mul(bot, u.d_pack([31] + [0] * 31)))[0] == -1
    two = u.d_pack([2, -4] + [0] * 30)
    assert u.d_unpack(u.d_scale(two, 1, 2))[:2] == [1, -2]
    assert u.d_unpack(u.d_scale(two, 3, 2))[:2] == [3, -6]
    with pytest.raises(u.DimFrac):
        u.d_scale(one, 1, 2)
    assert u.DIM0 == u.d_pack([0] * u.SLOTS)


# ---- SI の恒等式（すべて厳密一致） ---------------------------------------------------------------------
@pytest.mark.parametrize("lhs,rhs", [
    ("1 W*s", "1 J"), ("1 kWh", "3.6e6 J"), ("1 N*m", "1 J"), ("1 V*A", "1 W"), ("1 Pa*m^2", "1 N"),
    ("1 Hz*s", "1"), ("1 C*V", "1 J"), ("1 ohm*A", "1 V"), ("1 T*m^2", "1 Wb"), ("1 H*A", "1 Wb"),
    ("1 F*V", "1 C"), ("1 S*V", "1 A"), ("1 L", "1 dm^3"), ("1 mi", "1609.344 m"),
    ("1 eV", "1.602176634e-19 J"), ("1 cal", "4.184 J"), ("1 atm", "101325 Pa"), ("60 min", "1 h"),
    ("1 Wh", "3600 J"), ("1 t", "1000 kg"), ("1 lb", "0.45359237 kg"), ("1 µm", "1e-6 m"),
    ("1 μm", "1e-6 m"), ("1 Ω", "1 ohm"), ("1 GW*h", "3.6e12 J"), ("1 hPa", "100 Pa"),
    ("1 dam", "10 m"), ("1 kg", "1000 g"), ("1 kg*m/s^2", "1 N"), ("1 kg*m^2/s^2", "1 J"),
    ("3 m² / 3 m", "1 m"), ("2 m⁻¹ * 1 m", "2"), ("1 mi/h", "0.44704 m/s"), ("1 yd", "3 ft"),
])
def test_si_identities_are_exact(lhs, rhs, reg):
    a, b = ev(lhs, reg), ev(rhs, reg)
    assert same(a, b), (a, b)
    assert a.r == 0


def test_no_float_in_arithmetic(reg):
    assert same(ev("0.1 m + 0.2 m", reg), ev("0.3 m", reg))       # float なら 0.30000000000000004
    with pytest.raises(TypeError):
        ev("1 m", reg) + 0.5


@pytest.mark.parametrize("seed", SEEDS)
def test_tiny_increments_are_kept(seed, reg):
    rng = random.Random(seed)
    one = ev("1 m", reg)
    for _ in range(100):
        eps = rand_an(rng)                                         # A x 10^-N
        e = u.Q(eps, u.Z, one.d)
        assert same((one + e) - one, e)                            # 1 に足した微小量が消えない
        assert same((one + e) - e, one)


@pytest.mark.parametrize("seed", SEEDS)
def test_arithmetic_laws_hold_exactly(seed, reg):
    rng = random.Random(seed)

    def r():
        return u.Q(F(rng.randint(-10 ** 9, 10 ** 9), rng.randint(1, 10 ** 6)), u.Z, ev("1 m", reg).d)

    for _ in range(200):
        a, b, c = r(), r(), r()
        assert same((a + b) + c, a + (b + c))
        assert same(a + b, b + a)
        assert same((a * b) * c, a * (b * c))
        assert same(a * (b + c), a * b + a * c)


# ---- 次元違反は入力でも出力でも拒否する ------------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "3 m + 2 s", "1 J - 1 W", "sqrt(1 m)", "2 m ^ (1/2)", "1 m ^ (2 s)", "5 degC", "1 foo", "5 / 0",
    "1 m // 0 m", "(-4 m^2)^(1/2)", "1 m ^ 40", "3 m +", "3 m )", "m m", "2^100000", "1e5000 m",
    "1 m // sqrt(2 m^2)", "", "3 $ m",
])
def test_bad_input_is_rejected(text, reg):
    with pytest.raises(u.CalcError):
        u.run(text, reg)


def test_output_dimension_is_enforced(reg):
    with pytest.raises(u.CalcError):
        u.run("6 kWh -> W", reg)
    assert u.run("6 kWh -> MJ", reg)[1]["mid"] == "108/5"        # 21.6 MJ
    assert u.run("6 kW * 1 h -> kWh", reg)[1]["shown"] == "6"
    # 出力の単位が無いときは、次元が一致する名前付きの単位（なければ SI 基本単位の形）で返す
    assert u.run("6 kW * 1 h", reg)[1]["unit"] == "J"
    assert u.run("3 m * 2 kg", reg)[1]["unit"] == "kg·m"


# ---- δ: 表示で落とした分を厳密に出す ----------------------------------------------------------------------
@pytest.mark.parametrize("seed", SEEDS)
def test_delta_reconstructs_the_exact_value(seed, reg):
    rng = random.Random(seed)
    for _ in range(300):
        n, d = rng.randint(1, 10 ** rng.randint(1, 30)) * rng.choice((1, -1)), rng.randint(1, 10 ** rng.randint(1, 20))
        sig = rng.randint(3, 20)
        _, rec = u.run("%d m / %d m" % (n, d), reg, sig)
        mid, shown, delta = F(rec["mid"]), shown_value(rec["shown"]), F(rec["delta"])
        assert mid == F(n, d)
        assert shown + delta == mid                                # 表示 + δ = 真の値（厳密）
        assert delta * mid >= 0                                    # 0 方向へ切り捨てなので δ は同符号
        assert abs(delta) < abs(mid) * F(10) ** -(sig - 1)         # 最後の桁の 1 つ分より小さい
        if delta == 0:
            assert shown == mid


def test_exact_decimals_show_no_delta(reg):
    for text in ("1 eV -> J", "1 m / 8 m", "123456789 m -> m", "1 kWh -> J"):
        lines, rec = u.run(text, reg)
        assert rec["delta"] == "0" and lines[0].startswith("="), text


def test_division_remainder_is_shown(reg):
    lines, rec = u.run("10 J / 3 s -> W", reg, 15)
    assert F(rec["delta"]) == F(1, 3) * F(10) ** -14             # 10/3 = 3.33333333333333 + (1/3)x10^-14
    assert lines[0].startswith("≈") and lines[1].startswith("δ +1/3×10")
    assert F(rec["mid"]) == F(10, 3)
    _, rec = u.run("-10 J / 3 s -> W", reg, 15)
    assert F(rec["delta"]) == -F(1, 3) * F(10) ** -14


@pytest.mark.parametrize("seed", SEEDS)
def test_e10_matches_definition(seed):
    rng = random.Random(seed)
    for _ in range(1000):
        a = F(rng.randint(1, 10 ** rng.randint(1, 60)), rng.randint(1, 10 ** rng.randint(1, 60)))
        e = u._e10(a)
        assert F(10) ** e <= a < F(10) ** (e + 1)
        q, s, frac = u._cut(a, 7)
        assert 10 ** 6 <= q < 10 ** 7 and 0 <= frac < 1 and (q + frac) * F(10) ** -s == a


# ---- 根: 完全冪は厳密、そうでなければ真の値を必ず含む誤差球 ----------------------------------------------------
def test_perfect_powers_are_exact(reg):
    for text, want in (("sqrt(4 m^2)", "2 m"), ("sqrt(9/4)", "3/2"), ("cbrt(-8 m^3)", "-2 m"),
                       ("(27 m^3)^(2/3)", "9 m^2"), ("sqrt(0 m^2)", "0 m"), ("(1/4)^(1/2)", "1/2"), ("4 m^2 ^ 0", "1")):
        got = ev(text, reg)
        assert got.r == 0 and got.n == (), text
        assert same(got, ev(want, reg)), text


def test_irrational_root_is_enclosed_with_derivation(reg):
    x = ev("sqrt(2 m^2)", reg)
    assert x.r > 0 and x.d == ev("1 m", reg).d
    assert (x.m - x.r) ** 2 <= 2 <= (x.m + x.r) ** 2              # 真の √2 を含む
    assert x.r < F(1, 2 ** 62)                                    # 既定 64 ビットの精度
    assert len(x.n) == 1 and "√" in x.n[0]
    lines, rec = u.run("sqrt(2 m^2) -> m", reg)
    assert lines[0].startswith("≈") and lines[1].startswith("δ ∈ [") and not rec["exact"]
    assert F(rec["delta_lo"]) < 0 < F(rec["delta_hi"]) or F(rec["delta_lo"]) >= 0


@pytest.mark.parametrize("seed", SEEDS)
def test_roots_always_contain_the_true_value(seed, reg):
    rng = random.Random(seed)
    for _ in range(150):
        x = F(rng.randint(1, 10 ** rng.randint(1, 40)), rng.randint(1, 10 ** rng.randint(1, 40)))
        q = rng.choice((2, 3, 5, 7))
        y = u._root(u.Q(x), q)
        assert (y.m - y.r) ** q <= x <= (y.m + y.r) ** q
        assert y.r <= y.m * F(1, 2 ** (u.PREC - 3))               # 相対精度が約 PREC ビット
        n = rng.randint(0, 10 ** rng.randint(1, 60))
        r = u._iroot(n, q)
        assert r ** q <= n < (r + 1) ** q                         # ⌊n^(1/q)⌋


def test_enclosures_propagate(reg):
    r2 = ev("sqrt(2)", reg)
    sq = r2 * r2
    assert (sq.m - sq.r) <= 2 <= (sq.m + sq.r) and sq.r > 0       # 2 を含むが、厳密な 2 にはならない
    inv = 1 / r2
    assert (inv.m - inv.r) ** 2 <= F(1, 2) <= (inv.m + inv.r) ** 2
    zero = r2 - r2
    assert zero.m == 0 and zero.r > 0                             # 0 と言い切らず、範囲として残す
    with pytest.raises(ZeroDivisionError):
        1 / zero                                                  # 0 を含む範囲では割らない
    with pytest.raises(u.DomainError):
        ev("sqrt(2 m^2) // 1 m", reg)


def test_precision_follows_bits(reg, monkeypatch):
    for bits in (16, 64, 200):
        monkeypatch.setattr(u, "PREC", bits)
        x = ev("sqrt(3)", reg)
        assert (x.m - x.r) ** 2 <= 3 <= (x.m + x.r) ** 2
        assert x.r < F(1, 2 ** (bits - 2))


# ---- // と %（個数販売のあまり） ---------------------------------------------------------------------------
def test_floor_division_and_remainder(reg):
    assert same(ev("7 h // 2 h", reg), ev("3", reg))
    assert same(ev("7 h % 2 h", reg), ev("1 h", reg))
    assert same(ev("-7 h // 2 h", reg), ev("-4", reg))
    assert same(ev("-7 h % 2 h", reg), ev("1 h", reg))
    assert same(ev("100 min % 1 h", reg), ev("40 min", reg))


@pytest.mark.parametrize("seed", SEEDS)
def test_divmod_identity(seed, reg):
    rng = random.Random(seed)
    for _ in range(300):
        a = u.Q(F(rng.randint(-10 ** 6, 10 ** 6), rng.randint(1, 100)), u.Z, ev("1 s", reg).d)
        b = u.Q(F(rng.randint(1, 10 ** 4), rng.randint(1, 100)), u.Z, ev("1 s", reg).d)
        assert same((a // b) * b + a % b, a)
        assert 0 <= (a % b).m < b.m


# ---- 係数探し: SI の定義値から厳密に決まる定数と、SI 以外の単位への換算 ----------------------------------------
def test_defined_constants_and_their_products_are_exact(reg):
    assert ev("R_gas", reg).m == F("8.31446261815324")             # N_A x k_B。定義値の積なので厳密
    assert ev("R_gas", reg).r == 0
    assert same(ev("R_gas", reg), ev("N_A * k_B", reg))
    assert same(ev("F_Far", reg), ev("N_A * q_e", reg))
    assert same(ev("R_gas", reg), ev("1 J/(mol*K)", reg) * F("8.31446261815324"))
    assert ev("F_Far", reg).m == F("6.02214076e23") * F("1.602176634e-19")
    assert ev("c_0", reg).m == 299792458 and ev("g_n", reg).m == F("9.80665")
    assert same(ev("k_B * T_0", reg), ev("1.380649e-23 J/K * 273.15 K", reg))   # 温度の値としての 0 °C
    with pytest.raises(u.CalcError):
        reg.define("R_gas", ev("1 m", reg))                        # 定数の名前は上書きしない
    with pytest.raises(u.CalcError):
        u.run("R_gas + 1 J", reg)                                  # 次元が違う（J/(mol·K) と J）


@pytest.mark.parametrize("target,lo,hi", [
    ("J/(mol*K)", "8.31446261815324", "8.31446261815324"),
    ("L*atm/(mol*K)", "0.082057366080959", "0.082057366080961"),    # 知られている値 0.082057366080960
    ("cal/(mol*K)", "1.98720425864082", "1.98720425864084"),
    ("L*Torr/(mol*K)", "62.36359822152", "62.36359822153"),
    ("L*mmHg/(mol*K)", "62.36358933681", "62.36358933682"),
])
def test_gas_constant_in_other_unit_systems(target, lo, hi, reg):
    _, rec = u.run("R_gas -> " + target, reg, 15)
    assert F(lo) <= F(rec["mid"]) <= F(hi)
    assert rec["exact"]                                            # 値は厳密な分数。表示だけが有限桁（δ が出る）
    assert F(rec["shown"].translate(SUPD).replace("×10", "e")) + F(rec["delta"]) == F(rec["mid"])


def test_molar_volume_and_coefficient_search(reg):
    _, rec = u.run("R_gas * T_0 / 1 atm -> L/mol", reg)             # 標準モル体積（0 °C, 1 atm）
    assert F("22.41396954") < F(rec["mid"]) < F("22.41396955")
    # 係数探し: PV = k nT の k を測定値から作ると、次元は R と一致し、値の比は 1 に近い
    k = ev("(101325 Pa * 22.414 L) / (1 mol * 273.15 K)", reg)
    assert k.d == ev("R_gas", reg).d
    ratio = k / ev("R_gas", reg)
    assert ratio.d == u.DIM0 and abs(ratio.m - 1) < F(1, 10 ** 5)
    # 定数との比が無次元なら係数として噛み合う。無次元でなければ、残った次元を知らせる
    assert u.run("(101325 Pa * 22.414 L) / (1 mol * 273.15 K) / R_gas", reg)[1]["dimensionless"] is True
    rec = u.run("(101325 Pa * 22.414 L) / R_gas", reg)[1]
    assert rec["dimensionless"] is False and rec["dim"] == "K·mol"


def test_unit_groups_in_parentheses(reg):
    assert same(ev("3 W/(m^2*K) * 2 m^2 * 5 K", reg), ev("30 W", reg))
    assert same(ev("10 m / (2 s)", reg), ev("5 m/s", reg))        # 数で始まる括弧は単位の連なりではない
    assert same(ev("2 m / (sqrt(4) s)", reg), ev("1 m/s", reg))
    assert same(ev("1 J/(kg*K)", reg), ev("1 m^2/(s^2*K)", reg))
    assert u.run("1 J/(kg*K) -> cal/(g*K)", reg)[1]["unit"] == "cal/(g*K)"
    with pytest.raises(u.CalcError):
        ev("1 J/(kg*K", reg)


# ---- SI 以外・個数・金額（買い物の例）。為替は扱わない -------------------------------------------------------
def test_added_dimensions_follow_the_same_rules(reg):
    for name in ("JPY", "item"):
        reg.add_dim(name)
    reg.define("dozen", ev("12 item", reg))
    assert same(ev("3 dozen", reg), ev("36 item", reg))
    assert same(ev("3 item * 298 JPY/item", reg), ev("894 JPY", reg))
    assert same(ev("1000 JPY // 300 JPY/item", reg), ev("3 item", reg))   # 買える個数
    assert same(ev("1000 JPY % 300 JPY/item", reg), ev("100 JPY", reg))   # あまり
    assert u.run("1000 JPY // 300 JPY/item -> dozen", reg)[1]["mid"] == "1/4"
    with pytest.raises(u.CalcError):
        u.run("1 JPY + 1 item", reg)                               # 金額と個数は足せない
    with pytest.raises(u.CalcError):
        reg.add_dim("JPY")                                         # 重複
    with pytest.raises(u.CalcError):
        reg.add_dim("m")
    with pytest.raises(u.CalcError):
        reg.add_dim("kg")                                          # 接頭辞つきで読める名前も使用済み
    with pytest.raises(u.CalcError):
        u.run("1 kJPY", reg)                                       # 追加した名前に接頭辞は付かない


def test_discount_rate_or_value_is_told_apart_by_dimension(reg):
    reg.add_dim("JPY")
    price = "1000 JPY"
    assert same(ev(price + " * (1 - 20 pct)", reg), ev("800 JPY", reg))      # 割引率（無次元）
    assert same(ev(price + " - 300 JPY", reg), ev("700 JPY", reg))           # 割引値（金額）
    assert u.run("300 JPY / " + price + " -> pct", reg)[1]["mid"] == "30"    # 値 → 率
    assert same(ev(price + " * 30 pct", reg), ev("300 JPY", reg))            # 率 → 値
    with pytest.raises(u.CalcError):
        u.run(price + " - 20 pct", reg)                            # 率を値として引かない
    with pytest.raises(u.CalcError):
        u.run(price + " * (1 - 300 JPY)", reg)                     # 値を率として掛けない
    # 支払ったあとから割引値が出る: 定価 − 支払額。率も同時に出る
    paid = ev("700 JPY", reg)
    assert same(ev(price, reg) - paid, ev("300 JPY", reg))
    assert (ev(price, reg) - paid) / ev(price, reg) == ev("30 pct", reg) or \
        ((ev(price, reg) - paid) / ev(price, reg)).m == F(3, 10)
    # 個数と率: 3 個 x 298 円 から 10 % 引き = 804.6 円（厳密）
    assert same(ev("3 * 298 JPY * (1 - 10 pct)", reg), u.Q(F("804.6"), u.Z, ev("1 JPY", reg).d))


def test_dimension_slots_run_out(reg):
    for i in range(u.SLOTS - len(u.BASE)):
        reg.add_dim("x%d" % i)
    with pytest.raises(u.CalcError):
        reg.add_dim("one_too_many")


def test_define_must_be_exact(reg):
    with pytest.raises(u.CalcError):
        reg.define("bad", ev("sqrt(2 m^2)", reg))
    with pytest.raises(u.CalcError):
        reg.define("zero", ev("0 m", reg))
    with pytest.raises(u.CalcError):
        reg.define("kg", ev("1 m", reg))
    reg.define("furlong", ev("201.168 m", reg))
    assert same(ev("8 furlong", reg), ev("1 mi", reg))


# ---- 構文 ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize("text,want", [
    ("10 m / 2 s", "5 m/s"), ("10 m / (2 s)", "5 m/s"), ("3 m/s * 2 s", "6 m"), ("2 m * 3 m", "6 m^2"),
    ("2^3", "8"), ("-2^2", "-4"), ("2^-2", "1/4"), ("2 ^ 3", "8"), ("(1+2)*3 m", "9 m"), ("1e3 m", "1000 m"),
    (".5 m", "(1/2) m"), ("(1/3) m * 3", "1 m"), ("sqrt(4) m", "2 m"), ("(6 m / 3 m) kg", "2 kg"), ("3×4 m", "12 m"), ("12 m ÷ 4 s", "3 m/s"), ("6 J / s", "6 W"), ("6 J / 2 s", "3 W"),
    ("2 m^2 * 3 m", "6 m^3"), ("1 kg*m/s^2 to N", "1 N"), ("1 J/kg*K", "1 J*K/kg"), ("sqrt(16)", "4"),
    ("2 kW + 500 W", "2.5 kW"), ("2 h - 30 min", "90 min"), ("-3 m", "0 m - 3 m"),
])
def test_expression_forms(text, want, reg):
    assert same(ev(text, reg), ev(want, reg)), text


def test_one_over_three_m_binds_number_and_unit(reg):
    # '1/3 m' は 1 ÷ (3 m)。(1/3) m は括弧で書く
    assert ev("1/3 m", reg).d == ev("1/m", reg).d
    assert same(ev("(1/3) m", reg), u.Q(F(1, 3), u.Z, ev("1 m", reg).d))


# ---- コマンドライン ---------------------------------------------------------------------------------------
def cli(argv, capsys, stdin=""):
    code = u.main(argv, io.StringIO(stdin))
    out = capsys.readouterr().out
    return code, out


def test_cli_exit_codes(capsys):
    assert cli(["3 kW * 2 h -> kWh"], capsys)[0] == 0
    assert cli(["3 m + 2 s"], capsys)[0] == 65
    assert cli(["6 kWh -> W"], capsys)[0] == 65
    assert cli([""], capsys)[0] == 66
    assert cli([], capsys, stdin="\n# コメント\n")[0] == 66
    assert cli(["--dim", "m", "1 m"], capsys)[0] == 65             # 重複する次元名
    assert cli(["-D", "x=sqrt(2 m^2)", "1 m"], capsys)[0] == 65      # 厳密でない定義


def test_cli_json_and_batch(capsys):
    code, out = cli(["--json", "3 kW * 2 h -> kWh"], capsys)
    rec = json.loads(out)
    assert code == 0 and rec["ok"] and rec["exact"] and rec["shown"] == "6" and rec["unit"] == "kWh"
    code, out = cli(["--json"], capsys, stdin="1 kWh -> J\n1 m + 1 s\n7 h // 2 h\n")
    recs = [json.loads(ln) for ln in out.splitlines()]
    assert code == 65                                              # 1 つでも誤りがあれば 65（残りは続けて計算する）
    assert [r["ok"] for r in recs] == [True, False, True]
    assert recs[0]["shown"] == "3600000" and recs[2]["mid"] == "3"


def test_cli_dim_define_and_precision(capsys):
    code, out = cli(["--json", "--dim", "JPY", "--dim", "item", "-D", "pack=12 item", "2 pack -> item"], capsys)
    assert code == 0 and json.loads(out)["mid"] == "24"
    code, out = cli(["--json", "--bits", "200", "--digits", "40", "sqrt(2)"], capsys)
    rec = json.loads(out)
    assert code == 0 and rec["notes"] and F(rec["rad"]) < F(1, 2 ** 198)
    assert shown_value(rec["shown"]) ** 2 <= 2 <= (shown_value(rec["shown"]) + F(10) ** -39) ** 2   # 40 桁の切り捨て


def test_cli_steps_lists_the_derivation(capsys):
    code, out = cli(["--steps", "--json", "sqrt(2 m^2) -> m"], capsys)
    assert code == 0 and json.loads(out)["notes"]
    code, out = cli(["--steps", "10 J / 3 s -> W"], capsys)
    assert code == 0 and "🪜" in out


# ---- 次元の知らせ: 無次元（単位なし）と 左辺 = 右辺 ---------------------------------------------------------------
def test_dimensionless_results_are_reported(reg):
    for text, free in (("7 h // 2 h", True), ("3 m / 2 m", True), ("20 pct", True), ("sqrt(2)", True),
                       ("3 m", False), ("1 kWh -> J", False), ("1 Hz * 1 s", True)):
        lines, rec = u.run(text, reg)
        assert rec["dimensionless"] is free, text
        assert ("単位なし" in lines[-1]) is free, text


def test_equation_reports_dimensions_of_both_sides(reg):
    lines, rec = u.run("1 kWh = 3.6e6 J", reg)
    assert rec["equal"] is True and rec["dimensionless"] is False and rec["dim_left"] == rec["dim_right"]
    _, rec = u.run("7 h // 2 h = 3", reg)
    assert rec["equal"] is True and rec["dimensionless"] is True and rec["dim_left"] == rec["dim_right"] == "無次元"
    _, rec = u.run("1 m / 3 m = 1/3", reg)
    assert rec["equal"] is True and rec["dimensionless"] is True
    _, rec = u.run("R_gas * T_0 * 1 mol = 101325 Pa * 22.41396954 L", reg)
    assert rec["equal"] is False and F(rec["diff_mid"]) > 0 and rec["diff_rad"] == "0"   # 厳密に異なる（差は厳密な分数）
    with pytest.raises(u.CalcError):
        u.run("1 kWh = 3.6e6 W", reg)                              # 左辺と右辺の次元が違う
    with pytest.raises(u.CalcError):
        u.run("1 m = 1", reg)                                      # 片方だけ無次元でも止まる
    with pytest.raises(u.CalcError):
        u.run("1 m = 1 m -> m", reg)                               # 等式に換算先は付けない


def test_equation_with_enclosures_never_claims_equality(reg):
    _, rec = u.run("sqrt(2) * sqrt(2) = 2", reg)
    assert rec["equal"] is None and F(rec["diff_rad"]) > 0         # 範囲が重なる = 判定できない（等しいとも言わない）
    _, rec = u.run("sqrt(2 m^2) = 1.5 m", reg)
    assert rec["equal"] is False                                   # 範囲が離れていれば異なると言える
    _, rec = u.run("sqrt(2 m^2) = 1.4 m", reg)
    assert rec["equal"] is False


def test_cli_equation_json(capsys):
    code, out = cli(["--json", "7 h // 2 h = 3"], capsys)
    rec = json.loads(out)
    assert code == 0 and rec["kind"] == "eq" and rec["equal"] is True and rec["dimensionless"] is True
    assert cli(["1 kWh = 3.6e6 W"], capsys)[0] == 65
