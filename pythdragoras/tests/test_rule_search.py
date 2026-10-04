"""条件の組み合わせの総当たり。数え方は命題の判定（propositions.evaluate）と一致する。"""

import json

import polars as pl
import pytest

import propositions as pr
from rule_search import main, rule_text, search

ROWS = [  # team, season, rd, rank_ra, wins_vs_pythag, upper_half
    ("a", 2020, 40, 1, 2.0, True), ("b", 2020, 10, 3, -5.0, False), ("c", 2020, -20, 2, 4.0, True),
    ("d", 2020, -60, 5, 1.0, False), ("e", 2020, 5, 3, 0.5, True), ("f", 2020, -10, 6, -1.0, False),
    ("g", 2021, 30, 2, -6.0, False), ("h", 2021, -30, 5, 3.0, False), ("i", 2021, 60, 1, 0.0, True),
]
DF = pl.DataFrame([{"team": t, "team_name": t.upper(), "season": s, "league": "C", "rd": rd, "rank_ra": ra,
                    "wins_vs_pythag": w, "upper_half": u} for t, s, rd, ra, w, u in ROWS])
TARGET = [{"col": "upper_half", "op": "==", "value": False}]
CANDS = [{"col": "rd", "op": "<", "value": 0}, {"col": "rank_ra", "op": ">=", "value": 4},
         {"col": "wins_vs_pythag", "op": "<", "value": -4}]


def test_counts_agree_with_the_proposition_engine():
    for r in search(DF, TARGET, CANDS, max_terms=2, max_conds=2, top=50):
        p = {"id": "X", "statement": "s", "strength": "usually", "min_n": 1, "if_any": r["if_any"], "then": TARGET}
        f = {x["form"]: x for x in pr.evaluate(p, DF)["forms"]}
        assert (f["original"]["n"], f["original"]["hold"]) == (r["tp"] + r["fp"], r["tp"]), rule_text(r)
        assert (f["converse"]["n"], f["converse"]["hold"]) == (r["tp"] + r["fn"], r["tp"]), rule_text(r)


def test_best_rule_and_tie_break_by_fewer_conditions():
    best = search(DF, TARGET, CANDS, top=3)[0]
    # B クラス 5 件（b d f g h）をすべて言い当て、A クラスを含まない式: 失点の順位 4 以下 または 期待より −4 勝未満
    assert best["mcc"] == pytest.approx(1.0) and best["conditions"] == 2
    assert rule_text(best) == "[rank_ra >= 4] または [wins_vs_pythag < -4]"


def test_keeping_only_the_top_gives_the_same_order_as_sorting_everything():
    cands = CANDS + [{"col": "rd", "op": "<", "value": 20}, {"col": "rank_ra", "op": ">=", "value": 3},
                     {"col": "wins_vs_pythag", "op": "<", "value": 0}]
    everything = search(DF, TARGET, cands, max_terms=3, max_conds=2, top=10**9)
    assert len(everything) > 100 and len({r["mcc"] for r in everything[:12]}) < 12  # 同点を含む
    for top in (1, 5, 12):
        assert search(DF, TARGET, cands, max_terms=3, max_conds=2, top=top) == everything[:top]


def test_same_column_is_not_used_twice_in_one_group_and_bad_conditions_stop():
    rs = search(DF, TARGET, CANDS + [{"col": "rd", "op": "<", "value": 20}], top=500)
    assert all(len({c["col"] for c in g}) == len(g) for r in rs for g in r["if_any"])
    with pytest.raises(pr.PropositionError):
        search(DF, TARGET, [{"col": "rd", "op": "~", "value": 0}])


def test_cli_applies_exclusions_and_drops_missing(tmp_path, capsys):
    season = tmp_path / "season.jsonl"
    rows = DF.vstack(pl.DataFrame([{"team": "z", "team_name": "Z", "season": 2021, "league": "C", "rd": None, "rank_ra": 3,
                                    "wins_vs_pythag": 0.0, "upper_half": True}], schema=DF.schema))
    rows.write_ndjson(season)
    cfg = tmp_path / "a.toml"
    cfg.write_text('[[exclude]]\nseason = 2021\nreason = "テスト"\n', encoding="utf-8")
    cand = tmp_path / "c.toml"
    cand.write_text("target = [{col = \"upper_half\", op = \"==\", value = false}]\n"
                    + "".join(f"[[candidate]]\ncol = \"{c['col']}\"\nop = \"{c['op']}\"\nvalue = {c['value']}\n" for c in CANDS),
                    encoding="utf-8")
    out = tmp_path / "rules.jsonl"
    assert main(["--season", str(season), "--config", str(cfg), "--candidates", str(cand), "--out", str(out)]) == 0
    first = json.loads(out.read_text().splitlines()[0])
    assert first["units"] == 6 and first["dropped_for_missing_values"] == 0  # 2021 は除外（z も 2021）
