"""cycles/c001-chunichi/exploratory/kind_reask.py の確認。ゲート、4 つの形の件数、終了コード、読み。表示の文字は比べない。"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPLORATORY = ROOT / "cycles" / "c001-chunichi" / "exploratory"
RESULTS = EXPLORATORY / "kind_reask_results"
CANON_SHA = "0074801d0ede337a76c98624e8d206912ad0ee42a89fecde9d8eb7646d52a35a"

# 命題: (総合の終了コード, 元・対偶・逆・裏の終了コード, きっかけ以外の読み)
EXPECTED = {
    "K17": (4, (4, 4, 3, 3), 5), "K25": (4, (4, 4, 2, 4), 5), "K26": (4, (4, 4, 2, 2), 3), "K27": (4, (4, 1, 2, 2), 5),
    "K28": (4, (4, 4, 2, 4), 5), "K29": (4, (4, 4, 2, 2), 5), "K31": (4, (4, 1, 2, 2), 5), "K32": (1, (1, 1, 2, 4), 1),
    "K40": (2, (2, 4, 2, 2), 4), "K45": (3, (3, 4, 3, 3), 4), "K46": (1, (1, 1, 2, 4), 5), "K51": (1, (1, 1, 1, 1), 1),
    "K69": (3, (3, 3, 3, 3), 4), "K85": (1, (1, 3, 3, 3), 2), "K86": (4, (4, 2, 2, 2), 4), "K88": (3, (3, 3, 3, 3), 4),
    "K97": (1, (1, 4, 4, 3), 2), "K99": (4, (4, 4, 4, 4), 5), "K102": (4, (4, 4, 4, 1), 4), "K106": (4, (4, 4, 4, 4), 5),
    "K108": (4, (4, 4, 4, 4), 5), "K110": (4, (4, 4, 4, 4), 5),
}


def _load():
    spec = importlib.util.spec_from_file_location("c001_kind_reask", EXPLORATORY / "kind_reask.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kr = _load()
RES = kr.analyze(ROOT)


def test_gate_passes_and_the_canonical_file_is_untouched():
    assert RES["gate"] == {"ok": True, "problems": []}
    assert RES["inputs"]["propositions_sha256"] == CANON_SHA


def test_saved_result_is_what_the_script_produces():
    saved = json.loads((RESULTS / "kind_reask.json").read_text(encoding="utf-8"))
    assert saved == json.loads(json.dumps(RES, ensure_ascii=False, sort_keys=True))


def test_every_form_of_every_proposition_has_at_least_min_n_units():
    # 置き直しの目的: 4 つの形すべてに単位が入る（親は対偶が 0〜9 件、逆・裏は無し）
    assert len(RES["propositions"]) == 22
    for q in RES["propositions"]:
        assert all(q["forms"][f]["n"] >= 10 for f in kr.FORM_ORDER), q["id"]
        assert q["held_out"]["n"] >= 10, q["id"]


def test_exit_codes_and_readings():
    got = {q["id"]: (q["judgement"]["code"], tuple(q["forms"][f]["code"] for f in kr.FORM_ORDER), q["reading"])
           for q in RES["propositions"]}
    assert got == EXPECTED


def test_original_and_contrapositive_share_counterexamples_and_parents_stay_held():
    stored = {r["id"]: r for r in map(json.loads, (ROOT / "cycles/c001-chunichi/outputs/propositions.jsonl").read_text().splitlines())}
    for q in RES["propositions"]:
        assert q["forms"]["original"]["units"] == q["forms"]["contrapositive"]["units"]
        assert q["forms"]["converse"]["units"] == q["forms"]["inverse"]["units"]
        parent = {f["form"]: f["code"] for f in stored[q["parent"]]["forms"]}
        assert parent["original"] == 4 and parent["contrapositive"] == 4     # 親は保留のまま（書き換えていない）


def test_held_out_leaves_out_every_chunichi_unit():
    for q in RES["propositions"]:
        assert not [u for u in q["held_out"]["units"] if u.startswith("d-")]
        assert q["held_out"]["n"] < q["forms"]["original"]["n"]


def test_reading_follows_the_held_out_verdict_and_fisher_p():
    for verdict, p, want in (("Supported", 0.01, 1), ("Supported", 0.05, 2), ("Supported", 0.9, 2),
                             ("Refined", 0.01, 3), ("Rejected", 0.5, 4), ("Inconclusive", 0.001, 5)):
        assert kr.reading({"verdict": verdict, "fisher_p": p}) == want


def test_a_question_already_asked_in_the_canonical_file_stops_at_the_gate(tmp_path):
    # P5（低得点 ⇒ B クラス）と同じ問いを、P5 を親にせずに足すと、正本と同じ読み込みで止まる
    extra = tmp_path / "dup.toml"
    extra.write_text('[[proposition]]\nid = "K999"\nstatement = "x"\nstrength = "usually"\n'
                     'if = [{ col = "rank_rf", op = ">=", value = 5 }]\nthen = [{ col = "upper_half", op = "==", value = false }]\n'
                     'parent = "P17"\nchange = "x"\nmotivated_by = ["d-2019"]\n', encoding="utf-8")
    res = kr.analyze(ROOT, extra=extra)
    assert res["gate"]["ok"] is False and len(res["gate"]["problems"]) == 1
    assert res["propositions"] == [] and res["predictions"] == []


def test_main_writes_both_files_and_returns_zero(tmp_path):
    assert kr.main(["--outdir", str(tmp_path)]) == 0
    assert json.loads((tmp_path / "kind_reask.json").read_text(encoding="utf-8"))["summary"]["count"] == 22
    assert (tmp_path / "kind_reask.md").stat().st_size > 0
