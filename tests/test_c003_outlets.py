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
}


def test_prelock_hash_matches_stamp():
    # 命題を書き換えたら、固定時のハッシュと合わなくなる（変えるときは新しい id を足し、スタンプも理由つきで更新する）
    stamp = (C003 / "prelock_stamp.txt").read_text(encoding="utf-8")
    for name in ("propositions.toml", "propositions_r2.toml", "propositions_r3.toml"):
        assert hashlib.sha256((C003 / name).read_bytes()).hexdigest() in stamp, name


def test_later_rounds_stay_outside_earlier_scopes():
    # 後の弾で足した組は、前の弾の命題の範囲（組の真偽の列）に入らない
    units = units_mod.read_units()
    r2 = [u for u in units if u["gentle"] or u["chain"]]
    r3 = [u for u in units if u["native"] or u["chain2"] or u["fed"]]
    assert (len(units) - len(r2) - len(r3), len(r2), len(r3)) == (338, 140, 460)
    assert not any(u["valve_only"] or u["mixed"] or u["pump_only"] or u["has_delay"] for u in r2 + r3)
    assert not any(u["gentle"] or u["chain"] for u in r3)


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
        if code == 4:
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
