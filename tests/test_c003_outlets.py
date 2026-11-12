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
}


def test_prelock_hash_matches_stamp():
    # 命題を書き換えたら、固定時のハッシュと合わなくなる（変えるときは新しい id を足し、スタンプも理由つきで更新する）
    digest = hashlib.sha256((C003 / "propositions.toml").read_bytes()).hexdigest()
    assert digest in (C003 / "prelock_stamp.txt").read_text(encoding="utf-8")


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
