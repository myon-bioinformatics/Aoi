"""命題エンジン。docs/propositions.md の規則をそのままテストにする。"""

import math
from itertools import product

import polars as pl
import pytest

import propositions as pr


def table(rows):
    """rows: (team, season, rd, rank, rank_pythag)"""
    return pl.DataFrame([{"team": t, "team_name": t.upper(), "season": s, "league": "C", "rd": rd,
                          "rank": rk, "rank_pythag": rp, "rank_gap": rk - rp}
                         for t, s, rd, rk, rp in rows])


P1 = {"id": "P1", "statement": "得失点差がプラスならAクラス", "strength": "usually", "min_n": 1,
      "if": [{"col": "rd", "op": ">", "value": 0}], "then": [{"col": "rank", "op": "<=", "value": 3}],
      "surprise": "rank_gap", "context": ["rank_pythag"], "links": ["H3"]}


# ---------- 読み込み ----------

@pytest.mark.parametrize("bad,msg", [
    ({"id": "X", "statement": "s", "then": [{"col": "a", "op": ">", "value": 1}]}, "strength"),
    ({"id": "X", "statement": "s", "strength": "sometimes", "then": [{"col": "a", "op": ">", "value": 1}]}, "strength"),
    ({"id": "X", "statement": "s", "strength": "usually", "then": [{"col": "a", "op": "~", "value": 1}]}, "op"),
    ({"id": "X", "statement": "s", "strength": "usually", "then": [{"col": "a", "op": ">"}]}, "col, op, value"),
    ({"id": "X", "statement": "s", "strength": "usually", "then": []}, "then"),
])
def test_validate_rejects_bad_propositions(bad, msg):
    with pytest.raises(pr.PropositionError, match=msg):
        pr.validate(bad)


def test_load_returns_sha_and_rejects_duplicate_ids(tmp_path):
    body = '[[proposition]]\nid="A"\nstatement="s"\nstrength="always"\nthen=[{col="x",op=">",value=0}]\n'
    f = tmp_path / "p.toml"
    f.write_text(body, encoding="utf-8")
    props, sha = pr.load(f)
    assert props[0]["id"] == "A" and len(sha) == 64
    f.write_text(body * 2, encoding="utf-8")
    with pytest.raises(pr.PropositionError, match="一意"):
        pr.load(f)


# ---------- 統計 ----------

def test_wilson_known_values():
    assert pr.wilson(0, 0) == (0.0, 1.0)
    lo, hi = pr.wilson(5, 10)
    assert lo == pytest.approx(0.2366, abs=1e-4) and hi == pytest.approx(0.7634, abs=1e-4)
    assert pr.wilson(10, 10)[1] == 1.0 and pr.wilson(0, 10)[0] == 0.0


@pytest.mark.parametrize("a,b,c,d", [(3, 1, 1, 3), (5, 0, 0, 5), (0, 4, 4, 0), (2, 3, 4, 1), (0, 0, 3, 3), (6, 2, 3, 9)])
def test_fisher_matches_enumeration(a, b, c, d):
    r1, c1, n = a + b, a + c, a + b + c + d
    if r1 == 0 or c1 == 0:
        assert pr.fisher_greater(a, b, c, d) == 1.0
        return
    total = math.comb(n, c1)
    expect = sum(math.comb(r1, i) * math.comb(n - r1, c1 - i) for i in range(0, min(r1, c1) + 1) if i >= a) / total
    assert pr.fisher_greater(a, b, c, d) == pytest.approx(expect)
    assert pr.fisher_greater(3, 1, 1, 3) == pytest.approx(17 / 70)


# ---------- 判定表（docs の上から順） ----------

@pytest.mark.parametrize("args,expected", [
    (("statistical", 0.75, 5, 5, (0.9, 1.0), 0.0, 10, 0.05), "Inconclusive"),   # 1: n < min_n
    (("universal", None, 10, 10, (0.7, 1.0), 0.0, 10, 0.05), "Supported"),      # 2
    (("universal", None, 10, 9, (0.6, 0.99), 0.0, 10, 0.05), "Rejected"),       # 3: 反例1件で棄却
    (("statistical", 0.75, 50, 45, (0.75, 0.95), 0.0, 10, 0.05), "Supported"),  # 4: 下限ちょうど
    (("statistical", 0.75, 50, 38, (0.62, 0.75), 0.0, 10, 0.05), "Inconclusive"),  # 5: 上限ちょうど
    (("statistical", 0.75, 50, 30, (0.46, 0.73), 0.01, 10, 0.05), "Refined"),   # 6
    (("statistical", 0.75, 50, 30, (0.46, 0.73), 0.20, 10, 0.05), "Rejected"),  # 7
    (("statistical", 0.75, 50, 30, (0.46, 0.73), 0.05, 10, 0.05), "Rejected"),  # p == alpha は有意でない
])
def test_verdict_table(args, expected):
    assert pr.verdict(*args) == expected


# ---------- 評価 ----------

ROWS = [("d", 2019, 19, 5, 2), ("d", 2021, -30, 5, 5), ("g", 2019, 50, 1, 1), ("g", 2021, 40, 2, 1),
        ("t", 2019, -5, 3, 4), ("t", 2021, 10, 4, 2), ("c", 2019, -20, 6, 6), ("c", 2021, 5, 1, 3)]


def test_four_forms_counts_and_counterexamples():
    r = pr.evaluate(P1, table(ROWS), focus="d")
    f = {x["form"]: x for x in r["forms"]}
    # rd>0: d19 g19 g21 t21 c21 の5件、そのうち rank<=3 は g19 g21 c21 の3件
    assert (f["original"]["n"], f["original"]["hold"]) == (5, 3)
    assert [c["unit"] for c in f["original"]["counterexamples"]] == ["d-2019", "t-2021"]  # rank_gap 3 > 2 の順
    assert f["original"]["counterexamples"][0]["focus"] is True
    assert {c["unit"] for c in f["contrapositive"]["counterexamples"]} == {"d-2019", "t-2021"}
    # 逆: rank<=3 は g19 g21 t19 c21 の4件。rd>0 でないのは t19
    assert (f["converse"]["n"], f["converse"]["hold"]) == (4, 3)
    assert [c["unit"] for c in f["converse"]["counterexamples"]] == ["t-2019"]
    assert {c["unit"] for c in f["inverse"]["counterexamples"]} == {"t-2019"}
    assert r["objection"] is True
    c = f["original"]["counterexamples"][0]
    assert c["values"] == {"rd": 19, "rank": 5} and c["context"] == {"rank_pythag": 2} and c["surprise"] == 3
    assert "rd > 0" in c["question"] and "rank <= 3" in c["question"] and c["links"] == ["H3"]


def test_contrapositive_invariant_holds_on_random_tables():
    import random
    rnd = random.Random(0)
    for _ in range(50):
        rows = [(t, s, rnd.randint(-30, 30), rnd.randint(1, 6), rnd.randint(1, 6))
                for t, s in product("abcdef", range(2012, 2016))]
        r = pr.evaluate(P1, table(rows))  # 不一致なら evaluate が AssertionError を出す
        f = {x["form"]: x for x in r["forms"]}
        assert f["original"]["n"] - f["original"]["hold"] == len(f["original"]["counterexamples"])


def test_empty_if_means_every_unit_and_has_no_converse():
    p = {**P1, "if": []}
    r = pr.evaluate(p, table(ROWS))
    assert [f["form"] for f in r["forms"]] == ["original", "contrapositive"]
    assert r["forms"][0]["n"] == len(ROWS)


def test_missing_column_is_an_error():
    with pytest.raises(pr.PropositionError, match="存在しない列"):
        pr.evaluate({**P1, "then": [{"col": "nope", "op": "<=", "value": 3}]}, table(ROWS))
    with pytest.raises(pr.PropositionError, match="surprise"):
        pr.evaluate({**P1, "surprise": "nope"}, table(ROWS))


def test_null_values_are_counted_not_dropped():
    st = table(ROWS).with_columns(rd=pl.when(pl.col("team") == "c").then(None).otherwise(pl.col("rd")))
    f = pr.evaluate(P1, st)["forms"][0]
    assert f["undetermined"] == 2 and f["n"] == 4


def test_scope_filter():
    r = pr.evaluate({**P1, "scope": {"seasons": "2021"}}, table(ROWS))
    assert r["units"] == 4
    assert pr.evaluate({**P1, "scope": {"team": "d"}}, table(ROWS))["units"] == 2


def test_excluded_units_keep_their_counterexamples():
    excluded = table([("d", 2020, -60, 3, 6), ("g", 2020, 30, 5, 1)])
    r = pr.evaluate(P1, table(ROWS), excluded, focus="d")
    assert [c["unit"] for c in r["excluded_counterexamples"]] == ["g-2020"]
    # 統計には入らない
    assert r["forms"][0]["n"] == 5


def test_render_shows_objection_and_excluded_and_sha():
    excluded = table([("g", 2020, 30, 5, 1)])
    r = pr.evaluate(P1, table(ROWS), excluded, focus="d")
    md = pr.render([r], {"sha256": "abc123", "code_version": None})
    assert "異議あり！" in md and "D 2019 **(focus)**" in md and "除外中の判例" in md
    assert "abc123" in md and "測定なし" in md and "原因は示さない" in md


# ---------- 外部の主張 ----------

def test_check_claims_statuses():
    st = table(ROWS).with_columns(wins_vs_pythag=pl.Series([1.5, -2.0, 0.5, 3.0, -1.0, 0.0, 2.0, 1.0]))
    claims = [
        {"id": "C1", "statement": "d の合計", "kind": "sum", "column": "wins_vs_pythag", "value": -0.5, "tolerance": 0.01,
         "scope": {"team": "d"}},
        {"id": "C2", "statement": "外れ", "kind": "sum", "column": "wins_vs_pythag", "value": 99, "tolerance": 1,
         "scope": {"team": "d"}},
        {"id": "C3", "statement": "範囲外", "kind": "sum", "column": "wins_vs_pythag", "value": 1, "scope": {"seasons": "1990"}},
        {"id": "C4", "statement": "運が悪かったわけではない", "kind": "interpretation"},
        {"id": "C5", "statement": "列なし", "kind": "mean", "column": "nope", "value": 1},
        {"id": "C6", "statement": "件数", "kind": "count", "filter": [{"col": "rank", "op": "<=", "value": 3}], "value": 4},
    ]
    got = {c["id"]: c["status"] for c in pr.check_claims(claims, st)}
    assert got == {"C1": "reproduced", "C2": "not-reproduced", "C3": "not-measurable",
                   "C4": "interpretation", "C5": "not-measurable", "C6": "reproduced"}


def test_cycle1_files_reference_real_columns():
    import tomllib
    from pathlib import Path

    from sakanalytics import season_table, to_team_games

    root = Path(__file__).resolve().parents[2] / "cycles" / "c001-chunichi"
    teams = tomllib.loads((root / "analysis.toml").read_text(encoding="utf-8"))["teams"]
    games = pl.DataFrame([{"key": "1", "date": "2024-04-01", "home": "d", "away": "g", "hs": 3, "as": 2},
                          {"key": "2", "date": "2024-04-02", "home": "t", "away": "d", "hs": 1, "as": 0}])
    cols = set(season_table(to_team_games(games, teams)).columns)
    props, _ = pr.load(root / "propositions.toml")
    for p in props:
        for c in [*p.get("if", []), *p["then"]]:
            assert c["col"] in cols, (p["id"], c["col"])
        for c in [p.get("surprise"), *p.get("context", [])]:
            assert c is None or c in cols, (p["id"], c)
    claims = tomllib.loads((root / "claims.toml").read_text(encoding="utf-8"))["claim"]
    for c in claims:
        for f in c.get("filter", []):
            assert f["col"] in cols, (c["id"], f["col"])
        assert c.get("column") is None or c["column"] in cols, c["id"]
        assert c["kind"] in ("sum", "mean", "count", "interpretation")


def test_claim_premise_not_met_is_not_reproduced_but_missing_data_is_not_measurable():
    st = table(ROWS).with_columns(wins_vs_pythag=pl.lit(0.0))
    claims = [
        {"id": "A", "statement": "2019 d はピタゴラス2位", "kind": "count", "scope": {"team": "d", "seasons": "2019"},
         "filter": [{"col": "rank_pythag", "op": "==", "value": 9}], "value": 1},
        {"id": "B", "statement": "条件つき合計", "kind": "sum", "column": "wins_vs_pythag", "scope": {"team": "d"},
         "filter": [{"col": "rd", "op": "==", "value": -60}], "value": 9.4},
        {"id": "C", "statement": "範囲外", "kind": "count", "scope": {"seasons": "1958"}, "value": 1},
    ]
    got = {c["id"]: c for c in pr.check_claims(claims, st)}
    assert got["A"]["status"] == "not-reproduced" and got["A"]["computed"] == 0
    assert got["B"]["status"] == "not-reproduced" and "条件" in got["B"]["note"]
    assert got["C"]["status"] == "not-measurable"


def test_claim_table_escapes_pipes():
    md = pr.render_claims([{"id": "X", "statement": "P(B | A)=0.6", "source": "s", "date": "d", "status": "interpretation"}])
    assert "P(B \\| A)" in md


@pytest.mark.parametrize("skip,reason,ok", [
    (["converse", "inverse"], "主語の選択", True),
    (["converse", "inverse"], "", False),
    (["converse"], "x", False),
    (["original", "contrapositive"], "x", False),
])
def test_skip_forms_rules(skip, reason, ok):
    p = {**P1, "skip_forms": skip, "skip_reason": reason}
    if ok:
        pr.validate(p)
        r = pr.evaluate(p, table(ROWS))
        assert [f["form"] for f in r["forms"]] == ["original", "contrapositive"]
        assert "理由: 主語の選択" in pr.render([r], {})
    else:
        with pytest.raises(pr.PropositionError):
            pr.validate(p)
