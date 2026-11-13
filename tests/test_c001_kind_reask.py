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
    assert res["second"] == {} and res["third"] == {} and res["fourth"] == {}


# ---- 第2弾 A: まだ使っていない年の単位で照らす ------------------------------------------------------------------------
CONFIRM = {r["id"]: r for r in RES["second"]["confirm"]["rows"]}
COUNT_KEYS = ("hold", "counter", "converse_counter", "neither", "undetermined")


def test_round_two_leaves_round_one_untouched_and_confirms_only_the_reading_one_propositions():
    assert RES["second"]["summary"]["confirm_targets"] == ["K32", "K51"]
    assert sorted(i for i, r in CONFIRM.items() if r["role"] == "confirm") == ["K32", "K51"]
    assert RES["second"]["confirm"]["seasons"] == [2026] and len(RES["second"]["confirm"]["units"]) == 12
    assert len(CONFIRM) == 25                                              # K の 22 件と D の 3 件


def test_new_season_counts_and_readings():
    counts = {i: tuple(CONFIRM[i]["counts"][k] for k in COUNT_KEYS) for i in ("K32", "K51", "K85", "K97", "K102", "D86", "D102")}
    assert counts == {"K32": (0, 0, 0, 0, 12), "K51": (6, 0, 0, 6, 0), "K85": (6, 0, 6, 0, 0), "K97": (6, 0, 5, 1, 0),
                      "K102": (1, 5, 0, 6, 0), "D86": (1, 0, 2, 3, 0), "D102": (0, 1, 1, 4, 0)}
    assert RES["second"]["summary"]["confirm_readings"] == {"K32": 0, "K51": 1}
    assert all(r["reading"] is None for r in CONFIRM.values() if r["role"] == "record")
    blank = sorted(i for i, r in CONFIRM.items() if i.startswith("K") and r["counts"]["undetermined"] == r["in_scope"])
    assert blank == sorted(["K25", "K26", "K27", "K28", "K29", "K31", "K32", "K40", "K45", "K46"])   # イニング・打撃の列が無い


def test_expected_counts_come_from_the_training_rates():
    side = CONFIRM["K51"]["sides"]
    assert side["counter"]["n"] == 6 and abs(side["counter"]["expected"] - 6 * 9 / 78) < 1e-8            # 学習データ: 78 中 69
    assert side["converse_counter"]["n"] == 6 and abs(side["converse_counter"]["expected"] - 6 * 10 / 78) < 1e-8   # 裏: 78 中 68


def _panel_with(tmp_path, changes):
    rows = [json.loads(x) for x in (EXPLORATORY / "r18_partial_results" / "r18_partial_panel_2026.jsonl").read_text().splitlines()]
    for r in rows:
        if r["team"] in changes:
            r.update(changes[r["team"]])
    path = tmp_path / "panel.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def test_reading_turns_to_two_only_when_counterexamples_exceed_what_the_training_rate_allows(tmp_path):
    # B クラスの 6 単位のうち 1 つが判例（学習データの率 9/78 なら珍しくない）→ 1。4 つなら 0.05 未満 → 2
    one = kr.analyze(ROOT, panel=_panel_with(tmp_path, {"c": {"sim_p_upper": 0.9}}))
    row = {r["id"]: r for r in one["second"]["confirm"]["rows"]}["K51"]
    assert row["counts"]["counter"] == 1 and row["sides"]["counter"]["p_at_least"] > 0.05 and row["reading"] == 1
    four = kr.analyze(ROOT, panel=_panel_with(tmp_path, {t: {"sim_p_upper": 0.9} for t in ("c", "s", "b", "m")}))
    row = {r["id"]: r for r in four["second"]["confirm"]["rows"]}["K51"]
    assert row["counts"]["counter"] == 4 and row["sides"]["counter"]["p_at_least"] < 0.05 and row["reading"] == 2


# ---- 第2弾 B: 中日と、中日以外の同じ種類の差 ---------------------------------------------------------------------------
def test_difference_rows_compare_chunichi_with_the_rest_of_the_same_kind():
    got = {d["id"]: ((d["chunichi"]["hold"], d["chunichi"]["n"]), (d["others"]["hold"], d["others"]["n"]), d["reading"],
                     d["judgement"]["code"], tuple(d["forms"])) for d in RES["second"]["difference"]}
    assert got == {"D40": ((9, 11), (23, 41), 2, 4, ("original", "contrapositive")),
                   "D86": ((11, 12), (42, 66), 2, 4, ("original", "contrapositive")),
                   "D102": ((8, 12), (25, 66), 2, 4, ("original", "contrapositive"))}
    ps = {d["id"]: d["fisher_p"] for d in RES["second"]["difference"]}
    assert 0.05 <= ps["D86"] < ps["D102"] < ps["D40"] < 0.12              # どれも 0.05 に届かない（D86 は 0.05002）


def test_difference_counts_agree_with_round_one():
    # 中日以外の同じ種類 = 第1弾の「きっかけ以外」の元の命題と同じ単位
    held = {q["parent"]: (q["held_out"]["hold"], q["held_out"]["n"]) for q in RES["propositions"]}
    for d in RES["second"]["difference"]:
        assert (d["others"]["hold"], d["others"]["n"]) == held[d["parent"]]


def test_round_two_predictions_are_recorded_by_number():
    assert RES["second"]["summary"]["predictions"] == 6
    assert [x["ok"] for x in RES["second"]["predictions"]] == [True] * 6


# ---- 第3弾: 勝ち試合の得点 − 見込みが片側に寄る理由 --------------------------------------------------------------------
def test_stored_win_gap_is_rebuilt_from_the_saved_games():
    third = RES["third"]
    assert third["gate"]["ok"] and third["gate"]["compared"] == 156 and third["gate"]["max_abs_diff"] <= 1e-9
    assert third["units"] == 144 and third["games"] == 11028 and third["games_short_of_eight"] == 48


def test_the_one_sided_gap_disappears_with_eight_inning_scores():
    neg = {k: v["negative"] for k, v in RES["third"]["variants"].items()}
    assert neg == {"full": 133, "home": 128, "away": 101, "eight": 71}
    assert RES["third"]["reading"] == 1                                    # 8 回までで負が 65 % 以下 → 打ち切りが主な理由
    assert abs(RES["third"]["variants"]["eight"]["median_gap"]) < 0.01 < -RES["third"]["variants"]["full"]["median_gap"]
    assert [x["ok"] for x in RES["third"]["predictions"]] == [True, True, False, True]   # ビジターだけ 70 % 未満、は外れ


# ---- 第4弾 A: 2026年の表に、セ・リーグの打撃の列を足す ------------------------------------------------------------------
CONFIRM4 = {r["id"]: r for r in RES["fourth"]["confirm"]["rows"]}


def test_central_batting_is_filled_in_only_after_it_agrees_with_the_panel():
    ov = RES["fourth"]["confirm"]["overlay"]
    assert ov["agrees_with_panel"] and len(ov["teams"]) == 6 and ov["columns"] == ["bat_d_iso", "bat_d_obp", "bat_iso", "bat_obp"]
    counts = {i: tuple(CONFIRM4[i]["counts"][k] for k in COUNT_KEYS) for i in ("K31", "K32")}
    assert counts == {"K31": (2, 0, 1, 3, 6), "K32": (2, 0, 2, 2, 6)}
    assert CONFIRM4["K32"]["reading"] == 1 and CONFIRM4["K32"]["units"]["counter"] == []
    changed = sorted(i for i in CONFIRM if CONFIRM4[i]["counts"] != CONFIRM[i]["counts"])
    assert changed == ["K31", "K32"]                                       # ほかの命題と、第2弾 A の値は変わらない


def test_central_batting_is_not_used_when_a_total_disagrees(tmp_path):
    src = ROOT / "cycles" / "c001-chunichi" / "references" / "season-2026-central-summary.jsonl"
    rows = [json.loads(x) for x in src.read_text(encoding="utf-8").splitlines()]
    rows[0]["RF"] += 1                                                     # 得点が 2026年の表と合わない
    bad = tmp_path / "central.jsonl"
    bad.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    res = kr.analyze(ROOT, central=bad)
    row = {r["id"]: r for r in res["fourth"]["confirm"]["rows"]}["K32"]
    assert res["fourth"]["confirm"]["overlay"]["agrees_with_panel"] is False
    assert row["counts"]["undetermined"] == 12 and row["reading"] == 0


# ---- 第4弾 B: 8 回までの得点で作り直した列で P85 を問い直す --------------------------------------------------------------
def test_chunichi_is_no_longer_one_sided_on_the_eight_inning_column():
    q = {x["id"]: x for x in RES["fourth"]["propositions"]}
    assert (q["E85"]["forms"]["original"]["hold"], q["E85"]["forms"]["original"]["n"], q["E85"]["judgement"]["code"]) == (5, 12, 3)
    assert tuple(q["KE85"]["forms"][f]["code"] for f in kr.FORM_ORDER) == (3, 3, 3, 3)
    assert (q["KE85"]["held_out"]["hold"], q["KE85"]["held_out"]["n"], q["KE85"]["reading"]) == (28, 60, 4)
    assert (q["DE85"]["chunichi"], q["DE85"]["others"], q["DE85"]["reading"]) == ({"hold": 5, "n": 12}, {"hold": 28, "n": 60}, 2)
    assert q["DE85"]["fisher_p"] >= 0.05 and tuple(q["DE85"]["forms"]) == ("original", "contrapositive")


# ---- 第4弾 C: 片寄りを、延長の分と 9 回の終わり方の分に分ける --------------------------------------------------------------
def test_most_of_the_one_sided_gap_comes_from_extra_innings():
    sp, third = RES["fourth"]["split"], RES["third"]
    assert sum(sp["endings"].values()) == third["games"] and sp["endings"]["extra"] == 1019
    assert third["variants"]["eight"]["negative"] < sp["nine"]["negative"] == 93 < third["variants"]["full"]["negative"]
    assert sp["reading"] == 3 and sp["share_of_gap_from_extras"] > 0.5 > sp["share_of_gap_from_ninth"]
    assert abs(sp["share_of_gap_from_extras"] + sp["share_of_gap_from_ninth"] - 1) < 1e-8
    assert [x["ok"] for x in RES["fourth"]["predictions"]] == [True, True, True, True, True, False, False]


def test_main_writes_both_files_and_returns_zero(tmp_path):
    assert kr.main(["--outdir", str(tmp_path)]) == 0
    assert json.loads((tmp_path / "kind_reask.json").read_text(encoding="utf-8"))["summary"]["count"] == 22
    assert (tmp_path / "kind_reask.md").stat().st_size > 0
