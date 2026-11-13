"""cycles/c002-gohantrust の確認。lag1（事前宣言の固定、再現ゲート、テスト年の構成、符号検定、L1r）と monthly（月次の命題）。"""
import hashlib
import importlib.util
from pathlib import Path

LAG1 = Path(__file__).resolve().parent.parent / "cycles" / "c002-gohantrust" / "lag1"


def _load():
    spec = importlib.util.spec_from_file_location("c002_lag_run", LAG1 / "lag_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lag_run = _load()


def test_prelock_hash_matches_stamp():
    # 事前宣言を書き換えたら、固定時のハッシュと合わなくなる
    digest = hashlib.sha256((LAG1 / "lag_prelock_2026-10-24.md").read_bytes()).hexdigest()
    stamp = (LAG1 / "lag_prelock_timestamp.txt").read_text()
    assert digest in stamp


def test_replication_gate_passes():
    # 同年版が Grok の報告（勝敗件数・γ̂・順列 p）を再現できること。通らなければ遅れ版は走らせない
    ok, lines, _ = lag_run.gate()
    assert ok, "\n".join(lines)


def test_inputs_match_staple_survey_japan_series():
    # 転記した E と P のうち、research/staple-price-survey（e-Stat）で裏が取れる範囲を固定する。
    # E: 2005–2025 は家計調査（二人以上の世帯。2024–2025 は統計局の年平均結果の概要）、
    # P: 2005–2015 は小売物価統計調査の 5kg 月次の年平均
    import csv
    import statistics

    import pytest

    path = LAG1.parent.parent.parent / "research" / "staple-price-survey" / "staple_survey_vertical.csv"
    if not path.exists():
        pytest.skip("staple-price-survey is not in this checkout")
    engel, rice = {}, {}
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["country"] != "JPN":
                continue
            if r["variable"] == "engel_share_food_national_hh_survey":
                engel[int(r["year"])] = float(r["value"]) / 100
            elif r["variable"] == "staple_price:rice_uruchi_5kg":
                rice.setdefault(int(r["year"]), []).append(float(r["value"]))
    for y in range(2005, 2026):
        assert abs(lag_run.E[y] - engel[y]) < 5e-4, y
    for y in range(2005, 2016):
        assert len(rice[y]) == 12, y
        assert abs(lag_run.P[y] - statistics.mean(rice[y])) < 0.05, y


def test_lag_test_years_follow_the_prelock():
    assert [r["t"] for r in lag_run.rolling(2005, 1)] == list(range(2012, 2026))
    assert [r["t"] for r in lag_run.rolling(2015, 1)] == list(range(2022, 2026))


def test_sign_p_is_one_sided_binomial():
    assert lag_run.sign_p(0, 7) == 1.0
    assert lag_run.sign_p(4, 4) == 1 / 16
    assert abs(lag_run.sign_p(7, 14) - 0.6047) < 1e-4


# ---- 順列検定の母集団（2026-10-25 レビュー指摘：lag=1 は最終年の ΔlogE を読まない）-------------------

def test_perm_years_are_exactly_the_years_the_statistic_reads():
    for ws in (2005, 2015):
        used = lag_run.used_years(ws, 1)
        assert used == list(range(ws + 1, lag_run.LAST))              # ΔlogE[win_start+1 .. LAST-1]
        assert lag_run.LAST not in used                                # 最終年は統計に入らない
        assert lag_run.used_years(ws, 0) == list(range(ws + 1, lag_run.LAST + 1))  # 同年版は最終年まで読む


def test_permuted_keys_are_all_read_and_the_last_year_is_never_shuffled(monkeypatch):
    seen = []
    real = lag_run.rolling

    def spy(win_start, lag, dE=None):
        if dE is not None and not hasattr(dE, "read"):                # 順列の呼び出し（読み取り記録用の辞書は除く）
            seen.append(sorted(dE))
        return real(win_start, lag, dE=dE)

    monkeypatch.setattr(lag_run, "rolling", spy)
    monkeypatch.setattr(lag_run, "B", 3)
    lag_run.perm_test(2005, 1)
    assert len(seen) == 3 and all(k == list(range(2006, lag_run.LAST)) for k in seen)
    seen.clear()
    lag_run.perm_test(2005, 1, scope="declared")                       # 宣言 §7.2 の文面どおりの版は、最終年も混ぜる
    assert len(seen) == 3 and all(k == list(range(2006, lag_run.LAST + 1)) for k in seen)


def test_gate_permutation_is_unchanged_by_the_scope_fix(monkeypatch):
    monkeypatch.setattr(lag_run, "B", 50)
    assert lag_run.perm_test(2015, 0, "used") == lag_run.perm_test(2015, 0, "declared")   # lag=0 は同じ母集団


def test_committed_lag_results_are_what_the_code_produces():
    import json

    committed = json.loads((LAG1 / "lag_results.json").read_text(encoding="utf-8"))
    assert json.loads(json.dumps(lag_run.run_lag(), default=float)) == committed
    for name, ws in (("extended", 2005), ("legacy", 2015)):
        scope = committed[name]["perm_scope"]
        assert scope["main"] == "used" and scope["years_used"] == list(range(ws + 1, lag_run.LAST))
        assert scope["years_declared"] == list(range(ws + 1, lag_run.LAST + 1))


def test_gamma_stops_with_a_reason_when_every_training_dlogE_is_zero():
    # 分母 Σx² が 0 のとき、numpy は警告だけで nan を返し、その年が「負け」に数えられる。置き換えず、理由を書いて止める
    import pytest

    zero = {t: 0.0 for t in lag_run.DE}
    for lag in (0, 1):
        with pytest.raises(ValueError, match=rf"分母ゼロ.*win_start=2015, lag={lag}, t=\d{{4}}"):
            lag_run.rolling(2015, lag, dE=zero)


def test_gamma_is_still_computed_when_only_some_training_dlogE_are_zero():
    # E が同じ値の年（ΔlogE = 0）はデータにもある。分母が 0 でなければ、これまでの値のまま
    assert any(v == 0.0 for v in lag_run.DE.values())
    rows = lag_run.rolling(2015, 0)
    assert rows and all(r["gamma"] == r["gamma"] for r in rows)         # nan でない


# ---- L1r（入力差し替えの再検証、lag_reverify_prelock_2026-11-13.md）----------------------------------

def test_reverify_prelock_hash_matches_stamp():
    digest = hashlib.sha256((LAG1 / "lag_reverify_prelock_2026-11-13.md").read_bytes()).hexdigest()
    assert digest in (LAG1 / "lag_prelock_timestamp.txt").read_text()


def test_estat_inputs_pass_gate_g2():
    # 宣言 §2 G2: P は各年 0.05 % 以内、E は公表刻みの半分（0.0005）以内で転記値と合う
    p, e = lag_run.estat_inputs()
    assert sorted(p) == sorted(lag_run.P_TRANSCRIBED) == list(range(2005, 2026))
    for t in p:
        assert abs(p[t] / lag_run.P_TRANSCRIBED[t] - 1) <= 5e-4, t
        assert abs(e[t] - lag_run.E_TRANSCRIBED[t]) <= 5e-4, t


def test_estat_inputs_remove_the_zeros_made_by_rounding():
    # 転記値（0.1 ポイント刻み）では ΔlogE_2018 = ΔlogE_2019 = 0。実額の比では 0 にならない（宣言 §1.1）
    assert [t for t, v in lag_run.logdiff(lag_run.E_TRANSCRIBED).items() if v == 0.0] == [2018, 2019]
    _, e = lag_run.estat_inputs()
    assert all(v != 0.0 for v in lag_run.logdiff(e).values())


def test_set_inputs_rejects_unknown_names_and_the_default_is_transcribed():
    import pytest

    with pytest.raises(ValueError):
        lag_run.set_inputs("tokyo")
    assert lag_run.P == lag_run.P_TRANSCRIBED and lag_run.E == lag_run.E_TRANSCRIBED


def test_committed_estat_results_are_what_the_code_produces():
    import json

    committed = json.loads((LAG1 / "lag_results_estat.json").read_text(encoding="utf-8"))
    ok, lines = lag_run.reverify_gate()
    assert ok and committed["gate_ok"] and committed["gate_lines"] == lines
    fresh = json.loads(json.dumps(lag_run.run_reverify(), default=float))
    for key in ("inputs", "main", "same_year_record", "decomposition"):
        assert fresh[key] == committed[key], key
    assert lag_run.P == lag_run.P_TRANSCRIBED                          # 走らせたあと既定の入力に戻っている


# ---- 月次の命題（cycles/c002-gohantrust/monthly、monthly_prelock_2026-11-13.md）--------------------------

MONTHLY = LAG1.parent / "monthly"


def _load_monthly(name):
    spec = importlib.util.spec_from_file_location(f"c002_{name}", MONTHLY / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_monthly_prelock_and_propositions_hash_match_stamp():
    stamp = (MONTHLY / "monthly_prelock_timestamp.txt").read_text(encoding="utf-8")
    for name in ("monthly_prelock_2026-11-13.md", "monthly_propositions.toml",
                 "monthly_prelock_r2_2026-11-13.md", "monthly_propositions_r2.toml",
                 "monthly_prelock_r3_2026-11-13.md", "monthly_propositions_r3.toml",
                 "monthly_prelock_r4_2026-11-13.md", "monthly_propositions_r4.toml",
                 "monthly_prelock_r5_2026-11-13.md", "monthly_propositions_r5.toml"):
        assert hashlib.sha256((MONTHLY / name).read_bytes()).hexdigest() in stamp, name


def test_monthly_condition_counts_are_the_ones_in_the_prelock():
    # 宣言 §4 の表（条件の側だけで数えた件数）
    run = _load_monthly("monthly_run")
    c = run.count(run.load())
    def pick(d, keys):
        return {k: d[k] for k in keys}

    a_keys = ("units", "say(ax>=1)", "band(ax<1)")
    assert pick(c["A"]["incl2025"], a_keys) == {"units": 239, "say(ax>=1)": 203, "band(ax<1)": 36}
    assert pick(c["A"]["excl2025"], a_keys) == {"units": 227, "say(ax>=1)": 196, "band(ax<1)": 31}
    want = {1: (27, 15, 23, 250), 2: (51, 39, 10, 239), 3: (178, 166, 57, 65), 4: (181, 169, 37, 82)}
    for k, (up_in, up_ex, down, band) in want.items():
        assert pick(c["B"]["incl2025"][f"step{k}"], ("up(c>=tau)", "down(c<=-tau)", "band")) == {
            "up(c>=tau)": up_in, "down(c<=-tau)": down, "band": band}
        assert c["B"]["excl2025"][f"step{k}"]["up(c>=tau)"] == up_ex


def test_monthly_exit_codes_are_reproduced(tmp_path):
    # 置いてある判定（終了コードと 4 つの形の件数）が、コードを走らせ直した結果と同じ。表示の文字は比べない
    import json

    run = _load_monthly("monthly_run")
    fresh = run.judge(run.load(), outdir=tmp_path)
    committed = [json.loads(x) for x in (MONTHLY / "outputs" / "propositions.jsonl").read_text(encoding="utf-8").splitlines()]

    def key(rs):
        return {r["id"]: (r["judgement"]["code"], [(f["form"], f["n"], f["hold"], f["code"]) for f in r["forms"]]) for r in rs}

    assert key(fresh) == key(committed)
    # LAPACK/BLAS may differ in final bits across platforms. Preserve the recorded
    # evidence; require exact schema, identifiers and non-regression fields.
    # Only continuous least-squares fields get a tight numerical tolerance.
    import math
    regression_fields = {"f2", "f3", "rho", "gamma", "gain2", "gain3",
                         "f3r", "f3c", "gamma_r", "gamma_c", "gain3r", "gain3c"}   # 第3弾の最小二乗の列も同じ扱い
    actual_units = [json.loads(x) for x in (tmp_path / "units.jsonl").read_text().splitlines()]
    saved_units = [json.loads(x) for x in (MONTHLY / "outputs" / "units.jsonl").read_text().splitlines()]
    assert len(actual_units) == len(saved_units)
    for actual, saved in zip(actual_units, saved_units):
        assert actual.keys() == saved.keys()
        for field, value in saved.items():
            if field in regression_fields:
                assert math.isfinite(value) and math.isfinite(actual[field])
                assert math.isclose(actual[field], value, rel_tol=1e-12, abs_tol=1e-14), field
            else:
                assert actual[field] == value, field
    codes = {r["id"]: r["judgement"]["code"] for r in committed}
    assert codes["C2A2"] == codes["C2A2x"] == 1 and codes["C2L2"] == codes["C2L2x"] == 1   # 支持（例外あり）
    assert all(codes[f"C2B{k}{v}"] == 3 for k in range(1, 5) for v in ("", "x"))           # 向きは 4 段とも判例あり
    assert codes["C2A3s"] == codes["C2A3sx"] == 3                                           # 第2弾: σ の帯でも E の段は棄却
    assert all(codes[f"C2B{k}s{v}"] == 3 for k in (3, 4) for v in ("", "x"))
    assert codes["C2A3r"] == codes["C2A3c"] == codes["C2A3cx"] == 1                        # 第3弾: 米・穀類の寄与は支持
    assert all(codes[pid] == 3 for pid in ("C2Y3", "C2Y3x", "C2Y4", "C2Y4x", "C2Y3f", "C2Y4f", "C2Y4fx"))
    assert all(codes[pid] == 3 for pid in ("C2Y4ax", "C2Y5x", "C2Y6x"))                     # 第4弾: 量の段も判例あり
    assert codes["C2YL5x"] == codes["C2YL6x"] == 4
    c5 = next(r for r in committed if r["id"] == "C2Y5x")["forms"][0]
    assert (c5["hold"], c5["n"], [c["unit"] for c in c5["counterexamples"]]) == (15, 16, ["y-2013"])
    assert codes["C2Y5"] == 3 and codes["C2Y5fx"] == codes["C2Y5f"] == 4                    # 第5弾（対偶の単位が 0 なので 4）
    f5 = next(r for r in committed if r["id"] == "C2Y5f")["forms"][0]
    assert (f5["hold"], f5["n"], f5["counterexamples"]) == (11, 11, [])


def test_monthly_contribution_is_exact_not_linear():
    # 量を固定した会計上の寄与は ln(1+s·g) − ln(1+E·s·g)。g が小さいと (1−E)·s·g に近づく
    import math

    run = _load_monthly("monthly_run")
    assert run._contrib(0.04, 0.0, 0.28) == 0.0
    assert abs(run._contrib(0.04, 1e-6, 0.28) - (1 - 0.28) * 0.04 * 1e-6) < 1e-15
    assert abs(run._contrib(0.04, 0.65, 0.28) - (math.log(1.026) - math.log(1 + 0.28 * 0.026))) < 1e-15


def test_monthly_sigma_band_comes_from_the_published_rates():
    # 宣言 r2 §2: σ = √2·√(r_C² + r_F²)、r_C = 1.5 %、r_F = r_C·0.9/1.7。件数（§3）も宣言どおり
    import math

    run = _load_monthly("monthly_run")
    assert abs(run.SIGMA - math.sqrt(2) * math.hypot(0.015, 0.015 * 0.9 / 1.7)) < 1e-15
    assert abs(run.SIGMA - 0.0240) < 5e-5
    c = run.count(run.load())
    assert (c["A"]["incl2025"]["say(axs>=1)"], c["A"]["excl2025"]["say(axs>=1)"]) == (98, 96)
    want = {1: (0, 1), 2: (0, 0), 3: (64, 2), 4: (43, 1)}
    for k, (up, down) in want.items():
        b = c["B"]["incl2025"][f"step{k}"]
        assert (b["up(c>=sigma)"], b["down(c<=-sigma)"]) == (up, down), k


def test_monthly_r3_counts_are_the_ones_in_the_prelock():
    # 宣言 r3 §5 の表（族 A は条件の側、族 Y は年の帯 σ_Y = √2·√(0.4² + 0.2²) %）
    import math

    run = _load_monthly("monthly_run")
    assert abs(run.SIGMA_YEAR - math.sqrt(2) * math.hypot(0.004, 0.002)) < 1e-15
    c = run.count(run.load())
    assert (c["A"]["incl2025"]["say(axr>=1)"], c["A"]["excl2025"]["say(axr>=1)"]) == (16, 4)
    assert (c["A"]["incl2025"]["say(axc>=1)"], c["A"]["excl2025"]["say(axc>=1)"]) == (43, 31)
    want = {1: (1, 1, 23), 2: (1, 0, 24), 3: (11, 2, 12), 4: (11, 1, 13)}
    for k, (up, down, band) in want.items():
        y = c["Y"]["incl2025"][f"step{k}"]
        assert (y["up(c>=sigmaY)"], y["down(c<=-sigmaY)"], y["band"]) == (up, down, band), k


def test_monthly_r4_quantity_step_counts_and_source():
    # 宣言 r4 §1・§4: q は世界銀行の名目 ÷ 総合の物価指数 ÷ 人口、η は USDA ERS 2005 年の日本の値。件数は宣言どおり
    run = _load_monthly("monthly_run")
    d = run.load()
    assert d["eta_food"] == 0.492
    qty = run.count(d)["Y"]["quantity"]
    assert qty["units"] == 24 and qty["years"] == [2001, 2024]
    for k, want in {4: (10, 1, 13), 5: (8, 8, 8), 6: (9, 4, 11)}.items():
        s = qty[f"step{k}"]
        assert (s["up(c>=sigmaY)"], s["down(c<=-sigmaY)"], s["band"]) == want, k
    assert 2025 not in d["macro"]["hfce"]                      # 世界銀行の値は 2024 年まで（2025 年は第5弾で内閣府の表から。埋めない）


def test_monthly_r5_first_check_of_2025():
    # 宣言 r5 §5: 2025 年の q は内閣府の同じ公表の 2025 ÷ 2024 だけで作る。2024 年までは世界銀行のまま
    import math

    run = _load_monthly("monthly_run")
    d = run.load()
    assert d["macro"]["esri"] == {2024: 336602.0, 2025: 350908.3}
    rows = {r["k"]: r for r in run.y_conditions(d)}
    rel_a = d["cpi_year"]["all_items"][2025] / d["cpi_year"]["all_items"][2024]
    pop = d["macro"]["pop"][2025] / d["macro"]["pop"][2024]
    assert abs(rows[2025]["q"] - (math.log(350908.3 / 336602.0) - math.log(rel_a) - math.log(pop))) < 1e-15
    assert rows[2025]["c5"] >= run.SIGMA_YEAR                                             # 上げを言い切る
    y2025 = next(u for u in run.y_units(d) if u["season"] == 2025)
    assert y2025["agree5"] is True and y2025["yE"] > 0
    # 2004 年は世界銀行と内閣府の表で一致していた（転記の確かめ）
    assert d["macro"]["hfce"][2004] == 288414100000000.0


def test_monthly_residual_split_is_an_identity():
    # 宣言 r5 §3.2: 段 5 の残り yE − c5 = qF_hh − gap（恒等式）
    run = _load_monthly("monthly_run")
    for u in run.y_units(run.load()):
        if u["c5"] is not None:
            assert abs((u["yE"] - u["c5"]) - (u["qF_hh"] - u["gap"])) < 1e-12, u["season"]


def test_monthly_separate_implementation_agrees():
    verify = _load_monthly("monthly_verify")
    assert verify.main() == 0
