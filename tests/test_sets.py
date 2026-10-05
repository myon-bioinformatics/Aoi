"""命題の集合（R48）。式の読み、¬ の展開、命題としての判定と覆い。"""

import polars as pl
import pytest

import propositions as pr
import sets as st_

C = lambda col, op, v: {"col": col, "op": op, "value": v}  # noqa: E731
PROPS = {
    "P1": {"id": "P1", "if": [C("a", ">", 0)], "then": [C("upper_half", "==", False)]},
    "P2": {"id": "P2", "if": [C("b", "<", 0), C("c", "==", 1)], "then": [C("upper_half", "==", False)]},
    "P3": {"id": "P3", "if_any": [[C("a", "<", -1)], [C("b", ">", 2)]], "then": [C("upper_half", "==", False)]},
    "P4": {"id": "P4", "if": [], "then": [C("x", "==", 1)]},
    "P5": {"id": "P5", "scope": {"where": [C("team", "!=", "d"), C("z", ">=", 1)]}, "if": [], "then": [C("x", "==", 1)]},
}


def sets_of(*pairs):
    return {name: st_.set_dnf({"id": name, "from": pid}, PROPS) for name, pid in pairs}


def test_set_from_proposition_parts_and_errors():
    assert st_.set_dnf({"id": "S", "from": "P3"}, PROPS) == [[C("a", "<", -1)], [C("b", ">", 2)]]
    assert st_.set_dnf({"id": "S", "from": "P4", "part": "then"}, PROPS) == [[C("x", "==", 1)]]
    with pytest.raises(st_.SetError, match="空"):
        st_.set_dnf({"id": "S", "from": "P4"}, PROPS)
    assert st_.set_dnf({"id": "S", "from": "P5", "part": "where"}, PROPS) == [[C("z", ">=", 1)]]
    with pytest.raises(st_.SetError, match="命題がない"):
        st_.set_dnf({"id": "S", "from": "P9"}, PROPS)


@pytest.mark.parametrize("bad", ["A &", "(A | B", "A B", "& A", "A | ~"])
def test_parse_rejects_malformed(bad):
    with pytest.raises(st_.SetError):
        st_.parse(bad)


def test_parse_precedence_not_and_or():
    assert st_.parse("A | B & ~C") == ("or", ("set", "A"), ("and", ("set", "B"), ("not", ("set", "C"))))


def test_dnf_and_or_not():
    s = sets_of(("A", "P1"), ("B", "P2"))
    assert st_.dnf(st_.parse("A & B"), s) == [[C("a", ">", 0), C("b", "<", 0), C("c", "==", 1)]]
    assert st_.dnf(st_.parse("A | B"), s) == [[C("a", ">", 0)], [C("b", "<", 0), C("c", "==", 1)]]
    # ¬(b < 0 ∧ c == 1) = (b ≥ 0) ∨ (c ≠ 1)
    assert st_.dnf(st_.parse("~B"), s) == [[C("b", ">=", 0)], [C("c", "!=", 1)]]


def test_dnf_drops_contradictory_equalities():
    s = {"E": [[C("c", "==", 1)]]}
    assert st_.dnf(st_.parse("E & ~E"), s) == []


def test_compiled_expression_matches_set_membership_on_data():
    """式を命題にして判定した前件が、集合の計算（行ごとの真偽）と一致する。"""
    rows = [{"team": t, "team_name": t, "season": 2000 + i, "league": "C", "a": a, "b": b, "c": c, "upper_half": u}
            for i, (t, a, b, c, u) in enumerate([("d", 1, -1, 1, False), ("d", 1, 1, 1, False), ("x", -2, 3, 0, False),
                                                  ("x", 0, -1, 1, True), ("y", 2, 0, 0, True), ("y", -1, 1, 1, False)])]
    df = pl.DataFrame(rows)
    s = sets_of(("A", "P1"), ("B", "P2"), ("K", "P3"))
    for expr in ["A & B", "A | K", "~A & ~K", "(A | B) & ~K", "~(A & B)"]:
        p = st_.compile_expr({"id": "E", "expr": expr}, s)
        got = df.select(pr._antecedent(p, df.columns)).to_series().to_list()
        a, b, k = df["a"] > 0, (df["b"] < 0) & (df["c"] == 1), (df["a"] < -1) | (df["b"] > 2)
        want = {"A & B": a & b, "A | K": a | k, "~A & ~K": ~a & ~k, "(A | B) & ~K": (a | b) & ~k, "~(A & B)": ~(a & b)}[expr]
        assert got == want.to_list(), expr


def test_coverage_and_passes(tmp_path):
    rows = [{"team": t, "team_name": t, "season": s, "league": "C", "a": a, "upper_half": u}
            for t, s, a, u in [("d", 2001, 1, False), ("d", 2002, 1, False), ("d", 2003, 0, True), ("x", 2001, 0, True),
                               ("x", 2002, 1, False), ("y", 2001, 0, True), ("y", 2002, 0, False)]]
    df = pl.DataFrame(rows)
    p = st_.compile_expr({"id": "E", "expr": "A", "strength": "always", "min_n": 1}, sets_of(("A", "P1")))
    r = pr.evaluate(p, df, None, "d")
    cov = st_.coverage(p, df, "d")
    forms = {f["form"]: f for f in r["forms"]}
    assert forms["original"]["code"] == 0 and forms["converse"]["code"] == 3   # 逆の判例: y-2002（a = 0 で B）
    assert cov == {"focus": "d", "n": 2, "covered": 2, "missed": []}
    miss = st_.coverage(st_.compile_expr({"id": "E", "expr": "~A"}, sets_of(("A", "P1"))), df, "d")
    assert miss["covered"] == 0 and miss["missed"] == ["d-2001", "d-2002"]


def test_load_sets_rejects_duplicates_and_bad_ids(tmp_path):
    f = tmp_path / "s.toml"
    f.write_text('[[set]]\nid="A"\nfrom="P1"\n[[set]]\nid="A"\nfrom="P2"\n', encoding="utf-8")
    with pytest.raises(st_.SetError, match="重なる"):
        st_.load_sets(f, list(PROPS.values()))
    f.write_text('[[set]]\nid="1A"\nfrom="P1"\n', encoding="utf-8")
    with pytest.raises(st_.SetError, match="英字"):
        st_.load_sets(f, list(PROPS.values()))
    f.write_text('[[set]]\nid="A"\nfrom="P1"\n[[expr]]\nid="P1"\nexpr="A"\n', encoding="utf-8")
    with pytest.raises(st_.SetError, match="一意"):
        st_.load_sets(f, list(PROPS.values()))
