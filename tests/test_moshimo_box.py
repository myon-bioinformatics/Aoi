import inspect
import json
import math
import random

import pytest

import moshimo_box as mb


def logit(p):
    return math.log(p / (1 - p))


def test_original_is_not_a_dial():
    assert set(inspect.signature(mb.build).parameters) == {"converse", "inverse", "contrapositive", "n"}
    with pytest.raises(TypeError):
        mb.build(original=0.9, converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    with pytest.raises(mb.MoshimoError, match="cannot be set"):
        mb.sweep("original", [0.5, 0.6], converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    with pytest.raises(SystemExit) as exc:
        mb.main(["--converse", "0.6", "--inverse", "0.7", "--contrapositive", "0.8", "--n", "168", "--original", "0.9"])
    assert exc.value.code == 2


def test_table_by_hand():
    # cells a=30 (A and B), b=10 (A, not B), c=20 (not A, B), d=40: converse 30/50, inverse 40/60, contrapositive 40/50
    t = mb.build(converse=0.6, inverse=2 / 3, contrapositive=0.8, n=100)
    assert t["cells"] == {"a": 30, "b": 10, "c": 20, "d": 40} and t["synthetic"] is True
    assert {f: (v["hold"], v["n"]) for f, v in t["forms"].items()} == {
        "original": (30, 40), "contrapositive": (40, 50), "converse": (30, 50), "inverse": (40, 60)}
    assert t["forms"]["original"]["rate"] == pytest.approx(0.75) and t["original_rate_exact"] == pytest.approx(0.75)
    assert t["dial_error"] < 1e-12


def test_logit_of_the_original_is_converse_plus_contrapositive_minus_inverse():
    rng = random.Random(20261025)
    for _ in range(200):
        c, i, k = (rng.uniform(0.05, 0.95) for _ in range(3))
        t = mb.build(converse=c, inverse=i, contrapositive=k, n=2_000_000)
        assert logit(t["original_rate_exact"]) == pytest.approx(logit(c) + logit(k) - logit(i), abs=1e-9)
        assert t["forms"]["original"]["rate"] == pytest.approx(t["original_rate_exact"], abs=1e-3)
        assert t["dial_error"] < 1e-3


@pytest.mark.parametrize("dial,direction", [("converse", +1), ("contrapositive", +1), ("inverse", -1)])
def test_each_dial_moves_the_original_in_a_fixed_direction(dial, direction):
    values = [0.2, 0.35, 0.5, 0.65, 0.8]
    tables = mb.sweep(dial, values, converse=0.6, inverse=0.7, contrapositive=0.8, n=100_000)
    exact = [t["original_rate_exact"] for t in tables]
    realized = [t["forms"]["original"]["rate"] for t in tables]
    for series in (exact, realized):
        assert all(direction * (y - x) > 0 for x, y in zip(series, series[1:]))
    # the other two dials stay where they were
    others = [k for k in mb.DIALS if k != dial]
    assert all(t["dials"][k] == {"converse": 0.6, "inverse": 0.7, "contrapositive": 0.8}[k] for t in tables for k in others)


def test_counterexamples_are_shared_between_original_and_contrapositive_and_between_converse_and_inverse():
    t = mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    cx = t["counterexamples"]
    assert cx["original"] == cx["contrapositive"] == t["cells"]["b"]
    assert cx["converse"] == cx["inverse"] == t["cells"]["c"]
    assert sum(t["cells"].values()) == 168


@pytest.mark.parametrize("bad", [0, 1, 0.0, 1.0, -0.2, 1.5, float("nan"), float("inf"), True, "0.5", None])
def test_dials_at_or_beyond_the_boundary_stop(bad):
    with pytest.raises(mb.MoshimoError, match="strictly between 0 and 1"):
        mb.build(converse=bad, inverse=0.7, contrapositive=0.8, n=168)


def test_an_empty_cell_is_refused_not_patched():
    with pytest.raises(mb.MoshimoError, match="rounds to 0"):
        mb.build(converse=0.99, inverse=0.99, contrapositive=0.01, n=20)
    for n in (3, 4.0, "168", None):
        with pytest.raises(mb.MoshimoError, match="integer of at least 4"):
            mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=n)


def test_same_dials_give_the_same_table():
    args = dict(converse=0.61, inverse=0.72, contrapositive=0.83, n=168)
    assert mb.build(**args) == mb.build(**args)


def test_units_carry_exactly_the_cells():
    t = mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    rows = mb.units(t)
    assert len(rows) == 168 and len({r["team"] for r in rows}) == 168
    flags = {"a": (1, 1), "b": (1, 0), "c": (0, 1), "d": (0, 0)}
    for cell, (x, y) in flags.items():
        assert sum(1 for r in rows if (r["A"], r["B"]) == (x, y)) == t["cells"][cell]


@pytest.mark.parametrize("strength", ["always", "usually"])
def test_the_real_evaluator_reads_back_the_same_four_forms(strength):
    pytest.importorskip("propositions")
    t = mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    r = mb.readout(t, strength)
    assert set(r["forms"]) == set(mb.FORMS)
    for form, f in r["forms"].items():
        assert (f["hold"], f["n"]) == (t["forms"][form]["hold"], t["forms"][form]["n"])
        assert f["rate"] == pytest.approx(t["forms"][form]["rate"])
    assert isinstance(r["judgement_code"], int)


def test_cli_prints_a_table_and_writes_json(tmp_path, capsys):
    out = tmp_path / "moshimo" / "tables.json"
    rc = mb.main(["--converse", "0.6", "--inverse", "0.7", "--contrapositive", "0.8", "--n", "168",
                  "--sweep", "contrapositive=0.5,0.8", "--json", str(out)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "original (readout)" in text and "**0.500**" in text and "**0.800**" in text
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [t["dials"]["contrapositive"] for t in data["tables"]] == [0.5, 0.8] and data["readouts"] is None
