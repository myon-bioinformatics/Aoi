"""cycles/c001-chunichi/exploratory/kind_reask.py の確認。ゲート、4 つの形の件数、終了コード、読み。表示の文字は比べない。"""
import importlib.util
import json
from pathlib import Path

import pytest

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
pl, P, _ = kr.load_modules(ROOT)
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
    assert res["second"] == {} and res["third"] == {} and res["fourth"] == {} and res["fifth"] == {} and res["sixth"] == {} and res["seventh"] == {} and res["eighth"] == {} and res["ninth"] == {}


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


C001 = ROOT / "cycles" / "c001-chunichi"
KS = {p["id"]: p for p in kr.load_joined(C001 / "propositions.toml", [RESULTS / "kind_reask_propositions.toml"], P)[0]}
FULL = pl.read_ndjson(C001 / "outputs" / "season.jsonl")
TRAINED = {q["id"]: {f: {"n": v["n"], "hold": v["hold"]} for f, v in q["forms"].items()} for q in RES["propositions"]}


def _confirm(pid, **kw):
    """全体を走らせ直さず、2026年の数え方（confirm_new_season）だけを呼ぶ。"""
    res = kr.confirm_new_season([KS[pid]], TRAINED, [pid], FULL, kw.pop("panel", EXPLORATORY / "r18_partial_results" /
                                "r18_partial_panel_2026.jsonl"), P, pl, **kw)
    return res, res["rows"][0]


def test_reading_turns_to_two_only_when_counterexamples_exceed_what_the_training_rate_allows(tmp_path):
    # B クラスの 6 単位のうち 1 つが判例（学習データの率 9/78 なら珍しくない）→ 1。4 つなら 0.05 未満 → 2
    _, row = _confirm("K51")
    assert row["counts"] == CONFIRM["K51"]["counts"]                       # 全体を走らせたときと同じ
    _, row = _confirm("K51", panel=_panel_with(tmp_path, {"c": {"sim_p_upper": 0.9}}))
    assert row["counts"]["counter"] == 1 and row["sides"]["counter"]["p_at_least"] > 0.05 and row["reading"] == 1
    _, row = _confirm("K51", panel=_panel_with(tmp_path, {t: {"sim_p_upper": 0.9} for t in ("c", "s", "b", "m")}))
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
    good, row = _confirm("K32", overlay=src)
    assert good["overlay"]["agrees_with_panel"] and row["counts"] == CONFIRM4["K32"]["counts"]
    res, row = _confirm("K32", overlay=bad)
    assert res["overlay"]["agrees_with_panel"] is False
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


# ---- 第5弾: 4 つの「実際 − 見込み」の列の片寄りと、列の値だけを替えたときの判定 ------------------------------------------
FIFTH = {r["id"]: r for r in RES["fifth"]["propositions"]}


def test_only_the_win_runs_column_is_one_sided():
    s5, bias = RES["fifth"]["summary"], RES["fifth"]["bias"]
    assert (s5["one_sided_full"], s5["one_sided_nine"], s5["one_sided_eight"]) == (["wl_rf_win_gap"], [], [])
    pos = {c: tuple(bias[c][k]["positive"] for k in ("full", "nine", "eight")) for c in ("wl_rf_win_gap", "wl_rf_loss_gap")}
    assert pos == {"wl_rf_win_gap": (11, 51, 73), "wl_rf_loss_gap": (86, 74, 65)}
    assert all(v["units"] == 144 for by_table in bias.values() for v in by_table.values())


def test_swapping_the_column_values_changes_some_exit_codes():
    assert RES["fifth"]["gate"] == {"ok": True, "problems": []}
    got = {i: [(r["treatments"][t]["forms"]["original"]["hold"], r["treatments"][t]["forms"]["original"]["n"],
                r["treatments"][t]["judgement"]) for t in "abcd"] for i, r in FIFTH.items()}
    assert got == {"P85": [(12, 13, 4), (11, 12, 4), (7, 12, 4), (5, 12, 3)], "P86": [(11, 13, 4), (11, 12, 4), (8, 12, 4), (8, 12, 4)],
                   "P87": [(6, 13, 3), (6, 12, 3), (7, 12, 4), (6, 12, 3)], "K85": [(69, 78, 1), (64, 72, 1), (41, 72, 3), (33, 72, 3)],
                   "K86": [(53, 78, 4), (50, 72, 4), (41, 72, 3), (35, 72, 3)], "D86": [(11, 12, 4), (11, 12, 4), (8, 12, 4), (8, 12, 4)]}
    assert RES["fifth"]["summary"]["changed_c"] == ["P87", "K85", "K86", "D86"]
    assert RES["fifth"]["summary"]["changed_d"] == ["P85", "K85", "K86"]
    assert [x["ok"] for x in RES["fifth"]["predictions"]] == [True] * 6


def test_the_eight_inning_treatment_agrees_with_the_round_four_propositions():
    # 列を替えた P85・K85 は、8 回までの列で書いた E85・KE85 と同じ数になる
    q = {x["id"]: x["forms"]["original"] for x in RES["fourth"]["propositions"]}
    for old_id, new_id in (("P85", "E85"), ("K85", "KE85")):
        d = FIFTH[old_id]["treatments"]["d"]["forms"]["original"]
        assert (d["hold"], d["n"]) == (q[new_id]["hold"], q[new_id]["n"])


# ---- 第6弾 A: 試合の表から作った 8 回までの列 ----------------------------------------------------------------------
SIXTH = {q["id"]: q for q in RES["sixth"]["propositions"]}


def test_the_tool_column_matches_the_exploratory_one_and_round_four():
    six = RES["sixth"]
    assert six["gate"] == {"ok": True, "problems": []}
    assert six["eighth"]["units"] == 156 and six["eighth"]["units_2026"] == 12 and six["eighth"]["max_abs_diff_vs_round_four"] == 0
    assert len(six["eighth"]["columns"]) == 12 and all(c.endswith("8") for c in six["eighth"]["columns"])
    old = {q["id"]: q for q in RES["fourth"]["propositions"]}
    for i in ("E85", "KE85", "DE85"):
        assert {f: (v["n"], v["hold"], v["code"]) for f, v in SIXTH[i]["forms"].items()} == \
            {f: (v["n"], v["hold"], v["code"]) for f, v in old[i]["forms"].items()}


def test_loss_side_propositions_on_the_eight_inning_column():
    got = {i: (SIXTH[i]["forms"]["original"]["hold"], SIXTH[i]["forms"]["original"]["n"], SIXTH[i]["judgement"]["code"])
           for i in ("E86", "KE86", "DE86")}
    assert got == {"E86": (8, 12, 4), "KE86": (35, 72, 3), "DE86": (8, 12, 4)}
    assert SIXTH["KE86"]["reading"] == 4 and SIXTH["DE86"]["reading"] == 2 and 0.14 < SIXTH["DE86"]["fisher_p"] < 0.15


def test_new_season_records_on_the_eight_inning_column():
    rows = {r["id"]: r for r in RES["sixth"]["confirm_2026"]["rows"]}
    assert all(r["role"] == "record" and r["reading"] is None for r in rows.values())
    assert rows["E85"]["units"]["counter"] == ["d-2026"] and rows["E86"]["units"]["hold"] == ["d-2026"]
    assert (rows["KE85"]["counts"]["hold"], rows["KE86"]["counts"]["hold"]) == (3, 4)
    assert all(r["counts"]["undetermined"] == 0 for r in rows.values())


def test_eighth_split_uses_eight_inning_scores_by_hand():
    import sakanalytics as SA
    teams = {"d": {"name": "中日", "league": "C"}, "g": {"name": "巨人", "league": "C"}}
    rows = [("2024-04-01", 1, 0, 0, 0), ("2024-04-02", 5, 4, 5, 4), ("2024-04-03", 0, 3, 0, 3), ("2024-04-04", 2, 6, None, None)]
    games = [{"key": str(i), "date": d, "home": "d", "away": "g", "hs": hs, "as": as_, "hs8": h8, "as8": a8}
             for i, (d, hs, as_, h8, a8) in enumerate(rows)]
    got = kr.eighth_split(games, teams, pl, SA).filter(pl.col("team") == "d").row(0, named=True)
    # 8 回までの得点だけの 3 試合（1 試合目は 0-0 の引き分け、4 試合目は 8 回に届かず数えない）で、同じ関数を回した値と同じ
    plain = SA.to_team_games(pl.DataFrame([{"key": str(i), "date": d, "home": "d", "away": "g", "hs": h, "as": a}
                                           for i, (d, h, a) in enumerate([("2024-04-01", 0, 0), ("2024-04-02", 5, 4), ("2024-04-03", 0, 3)])]), teams)
    want = SA.win_loss_split(plain).filter(pl.col("team") == "d").row(0, named=True)
    assert {k[:-1]: v for k, v in got.items() if k.endswith("8")} == {k: v for k, v in want.items() if k.startswith("wl_")}


# ---- 第6弾 B: 配分の効果と作り直しの列 ------------------------------------------------------------------------------------
def test_allocation_leans_with_strength_and_the_lean_is_not_from_extra_innings():
    bias = RES["sixth"]["paired"]["bias"]
    assert not any(v["one_sided"] for by_table in bias.values() for v in by_table.values())
    strat = [round(bias["alloc_net_strat"][k]["a_minus_b"], 3) for k in ("full", "nine", "eight")]
    assert strat == [0.347, 0.347, 0.139]                                  # 延長を外しても変わらず、9 回も外すと下がる
    assert [bias["wpct_minus_sim"][k]["strength_sided"] for k in ("full", "nine", "eight")] == [False, True, False]


def test_swapping_allocation_and_simulation_columns():
    pb = RES["sixth"]["paired"]
    assert len(pb["propositions"]) == 13 and len(pb["columns"]) == 25
    assert pb["changed_c"] == ["P13", "P52"]
    assert pb["changed_d"] == ["P13", "P14", "P50", "P52", "P56", "P60", "K51"]
    p52 = {r["id"]: r for r in pb["propositions"]}["P52"]["treatments"]
    assert [p52[t]["judgement"] for t in "abcd"] == [1, 1, 1, 1]          # 式1 の総合の判定は変わらない
    assert [x["ok"] for x in RES["sixth"]["predictions"]] == [True, True, True, True, True, False, False, True, False]


# ---- 第7弾: 配分の効果の強さに沿った寄りを分ける ---------------------------------------------------------------------------
def test_home_and_away_allocation_lean_and_the_imputed_ninth():
    f7 = RES["seventh"]
    assert f7["gate"] == {"ok": True, "problems": []} and f7["imputed_games"] == 4866 and f7["games"] == 11028
    share = {c: [f7["home_away"][c][k]["share_positive"] for k in ("full", "eight")] + [f7["imputed"][c]["share_positive"]]
             for c in ("alloc_net_home", "alloc_net_away")}
    assert [round(v, 2) for v in share["alloc_net_home"]] == [0.76, 0.5, 0.61]
    assert [round(v, 2) for v in share["alloc_net_away"]] == [0.26, 0.47, 0.38]
    assert f7["home_away"]["alloc_net_home"]["full"]["one_sided"] and not f7["imputed"]["alloc_net_home"]["one_sided"]
    assert round(f7["imputed"]["alloc_net_strat"]["a_minus_b"], 3) == 0.333 and f7["reading"] == 3
    assert [x["ok"] for x in f7["predictions"]] == [True, False, False, True, False]


def test_imputed_allocation_by_hand():
    # 1 試合: ホーム d が 9 回表の時点で 2-1 で勝っていて、9 回裏に入らなかった。補う点の分布はこの年・リーグの 9 回表の得点（0 か 1）
    teams = {"d": {"name": "中日", "league": "C"}, "g": {"name": "巨人", "league": "C"}}
    games = [{"key": "a", "date": "2024-04-01", "home": "d", "away": "g", "hs": 2, "as": 1},
             {"key": "b", "date": "2024-04-02", "home": "d", "away": "g", "hs": 0, "as": 3}]
    innings = {"a": {"home": [0, 0, 0, 0, 2, 0, 0, 0, "X"], "away": [0, 0, 0, 0, 0, 0, 0, 1, 0]},
               "b": {"home": [0] * 9, "away": [0, 0, 0, 0, 0, 0, 0, 2, 1]}}
    plain = kr.imputed_allocation(games, innings, teams, impute=False)["units"][(2024, "d")]
    filled = kr.imputed_allocation(games, innings, teams)
    # 補わない: 得点 {2, 0}・失点 {1, 3} の 4 組で勝ち 1・負け 3 → 見込み −1、実際は 1 勝 1 敗で 0 → 配分の効果 +1
    assert (plain["alloc_net_home"], plain["alloc_net_away"], plain["alloc_net_strat"]) == (1.0, 0.0, 1.0)
    # 補う: 9 回表の得点は 0 と 1 が半分ずつ。得点 2 は 2 か 3 になり、失点 3 との組は半分が引き分け → 見込み −0.75、配分の効果 +0.75
    assert filled["units"][(2024, "d")]["alloc_net_home"] == 0.75 and filled["imputed_games"] == 1
    assert filled["top9_mean"] == {"2024-C": 0.5}


# ---- 第8弾: 勝ち負けの側と得点の分布の側 -----------------------------------------------------------------------------------
def test_the_remaining_lean_comes_from_results_not_from_run_distributions():
    f8 = RES["eighth"]
    assert f8["gate"] == {"ok": True, "problems": []} and f8["games"] == 10980
    ab = {k: round(v["a_minus_b"], 3) for k, v in f8["cells"].items()}
    assert ab == {"8,8": 0.139, "8,9": 0.097, "9,8": 0.417, "9,9": 0.375} and f8["reading"] == 1
    assert ab["8,8"] == round(RES["sixth"]["paired"]["bias"]["alloc_net_strat"]["eight"]["a_minus_b"], 3)
    a, b = f8["states"]["A"], f8["states"]["B"]
    assert (a["lead_games"], b["lead_games"], a["tie_decided"], b["tie_decided"]) == (4970, 4123, 429, 431)
    assert a["lead_held"] > b["lead_held"] and a["behind_won"] > b["behind_won"]
    assert [x["ok"] for x in f8["predictions"]] == [True] * 5


# ---- 第9弾: 最終順位を使わない強さで群を分ける -----------------------------------------------------------------------------
def test_the_lean_disappears_when_groups_do_not_use_the_final_rank():
    f9 = RES["ninth"]
    assert f9["gate"] == {"ok": True, "problems": []} and f9["reading"] == 3
    ab = {g: round(v["cells"]["9,9"]["a_minus_b"], 3) for g, v in f9["groups"].items()}
    assert ab == {"final": 0.375, "run_diff": 0.082, "previous": 0.014}
    assert f9["groups"]["final"]["cells"] == RES["eighth"]["cells"]
    assert [v["upper_units"] for v in f9["groups"].values()] == [72, 73, 72]
    held = f9["groups"]["run_diff"]["states"]
    assert held["A"]["lead_held"] - held["B"]["lead_held"] > 0.01           # 守る割合の差は、得失点差で分けても残る
    assert [x["ok"] for x in f9["predictions"]] == [True] * 5


# ---- 年次シミュレーションの GIF ------------------------------------------------------------------------------------------
GIF = RESULTS / "c001_sim-p-upper_y2012-2026_r01.gif"


def test_season_sim_years_count_k51_the_same_way_as_round_one():
    years = kr.season_sim_years(ROOT, pl)
    assert [y["season"] for y in years] == list(range(2012, 2027)) and [y["season"] for y in years if y["excluded"]] == [2020]
    assert all(len(y["leagues"][lg]) == 6 for y in years for lg in ("C", "P"))
    k51 = {f: (v["hold"], v["n"]) for f, v in {q["id"]: q for q in RES["propositions"]}["K51"]["forms"].items()}
    train = [y for y in years if not y["excluded"] and y["season"] <= 2025]
    assert sum(y["consistent"] for y in train) == k51["original"][0] + k51["inverse"][0] == 137     # B で 0.5 未満 + A で 0.5 以上
    assert years[-1]["consistent"] == 12                                                           # 2026年
    d = [next(t for t in y["leagues"]["C"] if t["team"] == "d") for y in years]
    assert [y["season"] for y, t in zip(years, d) if not t["upper"] and not t["ok"]] == [2014, 2019]


def test_saved_gif_matches_its_receipt_and_the_data():
    import hashlib
    data = GIF.read_bytes()
    receipt = json.loads(GIF.with_suffix(".json").read_text(encoding="utf-8"))
    assert receipt["schema"] == kr.GIF_RECEIPT_SCHEMA and receipt["files"]["gif"]["sha256"] == hashlib.sha256(data).hexdigest()
    assert data[:6] == b"GIF89a" and int.from_bytes(data[6:8], "little") == 512 and int.from_bytes(data[8:10], "little") == 320
    assert data.count(b"\x21\xf9\x04") == receipt["frames"] == 17                                       # 1 年 1 コマ + まとめ 2 枚
    assert [s["frames"] for s in receipt["scenes"]] == [15, 1, 1] and receipt["plan"]["delays_cs"][-3:] == [400, 500, 500]
    assert receipt["summary"] == {"k51_2012_2025": [137, 156], "k51_2026": [12, 12], "win_runs_gap_negative": [133, 93, 71, 144]}
    assert receipt["plan"]["palette"] == [list(c) for c in kr.GIF_PALETTE]
    years = kr.season_sim_years(ROOT, pl)
    assert [(y["season"], y["consistent"]) for y in receipt["years"]] == [(y["season"], y["consistent"]) for y in years]


def test_season_sim_grid_shapes_and_marks():
    years = kr.season_sim_years(ROOT, pl)
    g = kr.season_sim_grid(years, len(years) - 1)
    assert len(g) == 160 and {len(r) for r in g} == {256}
    assert max(max(r) for r in g) < len(kr.GIF_PALETTE)
    assert sum(r.count(4) for r in g) > 0                                     # 中日の棒
    assert sum(r.count(7) for r in g) > 0                                     # 除外した 2020年の帯


def test_summary_grids_draw_chunichi_and_the_one_sided_column():
    g1, g2 = kr.summary_grids(kr.season_sim_years(ROOT, pl), RES)
    assert all(len(g) == 160 and {len(r) for r in g} == {256} for g in (g1, g2))
    assert sum(r.count(6) for r in g1) == 2 * 12 * 3                          # 中日の 2014年・2019年の棒の頭
    dots = [sum(1 for x in range(40 + n * 64, 40 + n * 64 + 48, 4) if g2[142][x] == 4) for n in range(3)]
    assert dots == [11, 7, 5]                                                 # 棒の下の点: 中日の年


def test_main_needs_ffs_for_the_gif(capsys):
    with pytest.raises(SystemExit):
        kr.main(["--gif-dir", "x"])
    with pytest.raises(SystemExit):
        kr.main([])


def test_main_writes_both_files_and_returns_zero(tmp_path, monkeypatch):
    monkeypatch.setattr(kr, "analyze", lambda repo: RES)                   # 全体の計算は RES で済ませてある
    assert kr.main(["--outdir", str(tmp_path)]) == 0
    assert json.loads((tmp_path / "kind_reask.json").read_text(encoding="utf-8"))["summary"]["count"] == 22
    assert (tmp_path / "kind_reask.md").stat().st_size > 0
