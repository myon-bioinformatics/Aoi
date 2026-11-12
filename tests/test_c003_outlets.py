"""cycles/c003-outlets の確認。事前登録の固定、単位の検算、判定のコード、判例の数。

表示の文字列は比べない（docs/propositions.md: 判定は数で比べる）。
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

C003 = Path(__file__).resolve().parent.parent / "cycles" / "c003-outlets"


def _load(name):
    sys.path.insert(0, str(C003))
    spec = importlib.util.spec_from_file_location(f"c003_{name}", C003 / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


units_mod = _load("outlet_units")
judge_mod = _load("outlet_judge")

# 元の命題の (コード, 判例の数)。コードは命題全体（4 つの形のうち最初に 0 でないもの）
EXPECTED = {
    "O1": (0, 0), "O2": (0, 0), "O6": (4, 0), "O3": (3, 34), "O4": (3, 0), "O5": (3, 2), "O7": (4, 0), "O8": (3, 0),
    "O9": (4, 0), "O10": (3, 27), "O11": (4, 0), "O12": (4, 0), "O13": (4, 0), "O14": (4, 0), "O15": (4, 0),
    # 第2弾（propositions_r2.toml）
    "O16": (4, 0), "O17": (3, 8), "O18": (3, 20), "O19": (4, 0), "O20": (3, 30), "O21": (0, 0), "O22": (4, 0),
    "O23": (3, 50), "O24": (4, 0), "O25": (4, 0),
    # 第3弾（propositions_r3.toml）
    "O26": (4, 0), "O27": (3, 0), "O28": (3, 30), "O29": (4, 0), "O30": (4, 0), "O31": (3, 80), "O32": (4, 0),
    "O33": (4, 0), "O34": (4, 0),
    # 第4弾（propositions_r4.toml）
    "O35": (4, 0), "O36": (4, 0), "O37": (4, 0), "O38": (4, 0), "O39": (3, 12), "O40": (3, 0), "O41": (4, 0),
    "O42": (4, 0), "O43": (3, 1), "O44": (4, 0),
    # 第5弾（propositions_r5.toml）
    "O45": (3, 0), "O46": (4, 0), "O49": (3, 0), "O47": (3, 0), "O48": (3, 0),
    # 第6弾（propositions_r6.toml）
    "O50": (4, 0), "O51": (3, 0), "O52": (3, 8), "O53": (3, 18),
    # 第7弾（propositions_r7.toml）
    "O54": (3, 6), "O55": (3, 0), "O56": (3, 0),
    # 第8弾（propositions_r8.toml）
    "O57": (3, 9), "O58": (3, 2), "O59": (3, 0), "O60": (3, 0), "O61": (3, 14),
    "O62": (4, 0), "O63": (3, 0), "O64": (4, 0), "O65": (3, 1), "O66": (4, 0),
    # 第9弾（propositions_r9.toml）
    "O67": (4, 0), "O68": (4, 0), "O69": (4, 0), "O70": (4, 0), "O71": (4, 0), "O72": (4, 0),
    # 第10弾（propositions_r10.toml）
    "O73": (4, 0), "O74": (4, 0), "O75": (4, 0), "O76": (4, 0), "O77": (4, 0), "O78": (4, 0),
    # 第11弾（propositions_r11.toml）。両側に単位がある形で書いた命題は、4 つの形とも異議なし（コード 0）
    "O79": (0, 0), "O80": (0, 0), "O81": (0, 0), "O82": (0, 0), "O83": (0, 0), "O84": (0, 0),
    "O85": (3, 0), "O86": (3, 0), "O87": (3, 0),
    "O88": (0, 0), "O89": (0, 0), "O90": (0, 0), "O91": (0, 0),
    # 第12弾（propositions_r12.toml）
    "O92": (3, 3), "O93": (0, 0), "O94": (0, 0), "O95": (0, 0), "O96": (0, 0), "O97": (0, 0), "O98": (3, 2),
    # 第13弾（propositions_r13.toml）
    "O99": (0, 0), "O100": (3, 1), "O101": (3, 0), "O102": (3, 0), "O103": (3, 1),
}
TOO_FEW = {"O41"}  # 元の命題に当たる単位が 8 件（min_n = 10 に足りない）。元の命題そのものが判断保留


def test_prelock_hash_matches_stamp():
    # 命題を書き換えたら、固定時のハッシュと合わなくなる（変えるときは新しい id を足し、スタンプも理由つきで更新する）
    stamp = (C003 / "prelock_stamp.txt").read_text(encoding="utf-8")
    for name in ("propositions.toml", "propositions_r2.toml", "propositions_r3.toml", "propositions_r4.toml",
                 "propositions_r5.toml", "propositions_r6.toml",
                 "propositions_r7.toml", "propositions_r8.toml", "propositions_r9.toml",
                 "propositions_r10.toml", "propositions_r11.toml", "propositions_r12.toml",
                 "propositions_r13.toml"):
        assert hashlib.sha256((C003 / name).read_bytes()).hexdigest() in stamp, name


def test_later_rounds_stay_outside_earlier_scopes():
    # 後の弾で足した組は、前の弾の命題の範囲（組の真偽の列）に入らない
    units = units_mod.read_units()
    r2 = [u for u in units if u["gentle"] or u["chain"]]
    r3 = [u for u in units if u["native"] or u["chain2"] or u["fed"]]
    r4 = [u for u in units if u["flow"] or u["combo"] or u["chain3"] or u["ring"]]
    r5 = [u for u in units if u["chain3b"] or u["chain4"]]
    r6 = [u for u in units if u["edge3"] or u["edge2"]]
    assert len(r6) == 704 and not any(u["chain3b"] or u["chain4"] or u["chain3"] or u["chain2"] for u in r6)
    r7 = [u for u in units if u["cross3"]]
    assert len(r7) == 490 and not any(u["edge3"] or u["edge2"] or u["chain3b"] or u["chain3"] for u in r7)
    assert len({(u["h"], u["tau2_ratio"], u["steps"], u["uniform_in"]) for u in r7}) == len(r7)  # 同じ計算を 2 度数えない
    r8 = [u for u in units if u["cross3c"] or u["cross4"] or u["vary"]]
    assert len(r8) == 1108 and not any(u["cross3"] or u["edge3"] or u["edge2"] or u["chain3b"] or u["chain4"] for u in r8)
    assert len({(u["team"], u["h"], u["steps"]) for u in r8}) == len(r8)  # 同じ計算を 2 度数えない
    r9 = [u for u in units if u["pipe"]]
    assert len(r9) == 528 and not any(u["vary"] or u["cross3c"] or u["cross4"] or u["ring"] or u["flow"] for u in r9)
    assert all(u["p_branch"] + u["p_merge"] + u["p_pump"] + u["p_ring"] == 1 for u in r9)
    units = [u for u in units if not (u["edge3"] or u["edge2"] or u["cross3"] or u["cross3c"] or u["cross4"] or u["vary"]
                                      or u["pipe"] or u["ladder"] or u["olad"] or u["ilad"] or u["pipe2"] or u["coarse2"]
                                      or u["tlad"] or u["pipe3"] or u["rnd"])]
    r13 = [u for u in units_mod.read_units() if u["pipe3"] or u["rnd"]]
    assert len(r13) == 1512 and not any(u["pipe"] or u["pipe2"] or u["tlad"] or u["ladder"] or u["vary"] for u in r13)
    assert len({(u["team"], u["h"], u["steps"]) for u in r13}) == len(r13)  # 同じ計算を 2 度数えない
    r12 = [u for u in units_mod.read_units() if u["pipe2"] or u["coarse2"] or u["tlad"]]
    assert len(r12) == 1576 and not any(u["pipe"] or u["p_branch"] or u["p_ring"] or u["ladder"] or u["ilad"] or u["vary"]
                                        for u in r12)
    assert len({(u["team"], u["h"], u["steps"]) for u in r12}) == len(r12)  # 同じ計算を 2 度数えない
    r11 = [u for u in units_mod.read_units() if u["olad"] or u["ilad"]]
    assert len(r11) == 1428 and not any(u["ladder"] or u["valve_only"] or u["independent"] or u["two_stage"] for u in r11)
    assert len({(u["team"], u["h"]) for u in r11}) == len(r11)  # 同じ計算を 2 度数えない
    r10 = [u for u in units_mod.read_units() if u["ladder"]]
    assert len(r10) == 264 and not any(u["vary"] or u["pipe"] or u["chain3b"] or u["edge2"] for u in r10)
    assert (len(units) - len(r2) - len(r3) - len(r4) - len(r5), len(r2), len(r3), len(r4), len(r5)) == (338, 140, 460, 450, 308)
    assert not any(u["valve_only"] or u["mixed"] or u["pump_only"] or u["has_delay"] for u in r2 + r3 + r4 + r5)
    assert not any(u["gentle"] or u["chain"] for u in r3 + r4 + r5)
    assert not any(u["native"] or u["chain2"] or u["fed"] for u in r4 + r5)
    assert not any(u["flow"] or u["combo"] or u["chain3"] or u["ring"] for u in r5)


def test_stage_prediction_reduces_to_known_forms():
    # 2 段なら dt/(2·τ2)（O27）。3 段は (dt/2)·[(k2 + k3) − k2·P13/C]（README の式）
    import math
    k1, k2, k3, dt, t = 1 / 32, 3 / 32, 1 / 96, 0.125, 64.0
    assert abs(units_mod.stage_prediction([k1, k2], dt, t) / (k2 * dt / 2) - 1) < 0.01
    p13 = k1 / (k3 - k1) * (math.exp(-k1 * t) - math.exp(-k3 * t))
    c = units_mod.bateman_last([k1, k2, k3], t) / units_mod.V0
    closed = dt / 2 * ((k2 + k3) - k2 * p13 / c)
    assert abs(units_mod.stage_prediction([k1, k2, k3], dt, t) / closed - 1) < 0.01


def test_uniform_prediction_reduces_to_the_two_stage_form():
    # 2 段なら k1·k2·dt²/12（時刻によらない）
    k1, k2, dt = 1 / 32, 3 / 32, 0.125
    for t in (16.0, 64.0):
        assert abs(units_mod.uniform_prediction([k1, k2], dt, t) / (k1 * k2 * dt * dt / 12) - 1) < 1e-3


def test_boundary_formula_never_lands_on_the_wrong_side():
    # 第7弾: 式が言い切った単位（比 ≥ 1.25 か ≤ 0.8）で、実際の大小が逆だったものは無い
    decided = [u for u in units_mod.read_units() if u["cross3"] and u["uniform_in"]
               and (u["pred_margin"] >= 1.25 or u["pred_margin"] <= 0.8)]
    assert len(decided) == 233
    assert all((u["pred_margin"] >= 1.25) == (u["gain_vs_end"] < 1.0) for u in decided)


def test_every_unit_keeps_the_total():
    # O15 の列。エンジンの単位も、整数の漸化式で進めた単位（uniform・through）も 0
    assert {u["conservation_q"] for u in units_mod.read_units()} == {0}


def test_units_match_provenance():
    prov = json.loads((C003 / "units_provenance.json").read_text(encoding="utf-8"))
    assert hashlib.sha256((C003 / "units.jsonl").read_bytes()).hexdigest() == prov["units_sha256"]
    assert len(units_mod.read_units()) == prov["units"] == len(units_mod.plan(prov["h_extra"]))


def test_units_agree_with_plain_recurrence():
    # エンジンを使わない素の漸化式で err を出し直す。違えば 65
    assert units_mod.check() == 0


def test_no_unit_is_undetermined_inside_its_scope():
    for r in judge_mod.evaluate_all(outdir=None):
        assert all(f["undetermined"] == 0 for f in r["forms"]), r["id"]


def test_verdict_codes_and_counterexamples():
    got = {r["id"]: (r["judgement"]["code"], len(r["forms"][0]["counterexamples"]))
           for r in judge_mod.evaluate_all(outdir=None)}
    assert got == EXPECTED


def test_original_form_is_supported_where_no_counterexample():
    # コード 4 の命題は、元の命題は支持で、対偶に当たる単位（B でない単位）が 0 件のため保留になっている
    for r in judge_mod.evaluate_all(outdir=None):
        code, cx = EXPECTED[r["id"]]
        if code == 4 and r["id"] in TOO_FEW:
            assert r["forms"][0]["hold"] == r["forms"][0]["n"] < 10 and r["judgement"]["form"] == "original", r["id"]
        elif code == 4:
            assert r["forms"][0]["hold"] == r["forms"][0]["n"] >= 10, r["id"]
            assert r["judgement"]["form"] != "original", r["id"]


def test_committed_outputs_are_the_current_verdicts():
    rows = [json.loads(line) for line in (C003 / "outputs" / "propositions.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {r["id"]: (r["judgement"]["code"], len(r["forms"][0]["counterexamples"])) for r in rows} == EXPECTED


def test_judge_exit_codes(tmp_path, monkeypatch):
    monkeypatch.setattr(judge_mod, "OUT", tmp_path)  # リポジトリの outputs/ は書き換えない
    assert judge_mod.main(["--report-only"]) == 0
    assert {p.name for p in tmp_path.iterdir()} == {"propositions.jsonl", "objections.md", "index.md", "ledger.jsonl"}
    assert judge_mod.main([]) == 4  # 最初に 0 でない命題（O6 の対偶が 0 件で保留）
