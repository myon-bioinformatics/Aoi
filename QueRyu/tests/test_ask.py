"""問い合わせ（QueRyu/ask）: 読み取りは選べる値の中だけ、答えは判定済みの結果を引くだけ。結果は架空の小さなもの。"""

import json

from ask import Query, answer, main, parse, schema


def item(i, form="original", n=10, hold=9, cx=("t-2015",)):
    return {"id": i, "statement": i, "forms": [{"form": form, "n": n, "hold": hold, "undetermined": 0, "rate": hold / n,
                                                "counterexamples": [{"unit": u} for u in cx]}]}


ITEMS = [item("E25", n=64, hold=63), item("E26", n=60, hold=60, cx=()), item("P96", hold=8, cx=("t-2015", "d-2019")),
         item("P96x", form="converse")]


def test_reading_picks_only_known_values():
    q, unread = parse("Ｅ２５ に阪神 2015 以外の判例はある？")
    assert (q.ask, q.target, q.form, q.exclude, q.about) == ("has_counterexample", "E25", "original", ["t-2015"], [])
    assert unread == []
    q, _ = parse("P96 の対偶で、中日 2019年が判例か")
    assert (q.form, q.about) == ("contrapositive", ["d-2019"])
    q, _ = parse("判例がただ1つの式は？")
    assert (q.ask, q.kind) == ("unique_exception", "expression")
    q, _ = parse("成立率 95% 以上の逆の命題")
    assert (q.ask, q.form, q.kind, q.min_rate) == ("rate", "converse", "proposition", 0.95)
    assert parse("逆に、E1 の判例は？")[0].form == "original"   # 「逆に」は形ではない


def test_what_cannot_be_read_is_returned_not_dropped():
    q, unread = parse("なんかいい感じのやつ")
    assert q.ask == "counterexamples" and unread and "問いの種類" in unread[0]
    assert "2つ以上" in parse("E1 と E2 の判例")[1][0]


def test_answers_come_from_the_judged_results_only():
    q, _ = parse("E25 に阪神 2015 以外の判例はある？")
    assert answer(q, ITEMS)["answer"] == "いいえ"
    assert answer(Query(ask="has_counterexample", target="E25"), ITEMS)["answer"] == "はい"
    uniq = answer(Query(ask="unique_exception"), ITEMS)
    assert [r["id"] for r in uniq["rows"]] == ["E25"]
    about = answer(Query(about=["d"]), ITEMS)
    assert [r["id"] for r in about["rows"]] == ["P96"]
    assert answer(Query(target="E99"), ITEMS)["error"]


def test_schema_and_direct_query(tmp_path, capsys):
    s = schema()
    assert s["properties"]["form"]["enum"] == ["original", "contrapositive", "converse", "inverse"]
    (tmp_path / "sets.jsonl").write_text("\n".join(json.dumps(i) for i in ITEMS), encoding="utf-8")
    assert main(["--results", str(tmp_path), "--query", '{"ask": "has_counterexample", "target": "E26"}', "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["answer"] == "いいえ"
    assert main(["--results", str(tmp_path), "--query", '{"ask": "guess"}']) == 2   # 型の外の値は通さない
    log = tmp_path / "ask.jsonl"
    main(["--results", str(tmp_path), "E26 の判例は？", "--log", str(log)])
    assert json.loads(log.read_text(encoding="utf-8"))["query"]["target"] == "E26"


def test_invalid_query_values_are_controlled_errors(capsys):
    import pytest
    from ask import validate_query
    invalid = [[], None, {'ask': []}, {'form': {}}, {'kind': []}, {'target': 2},
               {'exclude': 'd'}, {'about': [2]}, {'min_rate': True}, {'max_rate': float('nan')},
               {'min_rate': 10**400}, {'min_rate': .9, 'max_rate': .1}]
    for raw in invalid:
        with pytest.raises(ValueError):
            validate_query(raw)
        assert main(['--query', json.dumps(raw)]) == 2
    assert main(['--query', '{']) == 2
    assert 'Traceback' not in capsys.readouterr().err


def test_form_labels_and_unknown_provenance():
    from ask import render, research_metadata
    for form, label in [('original','元'), ('contrapositive','対偶'), ('converse','逆'), ('inverse','裏')]:
        q = Query(target='P117', form=form)
        res = answer(q, [item('P117', form=form, n=72, hold=62)])
        assert label + 'の成立率 62/72' in render('question', q, [], res)
    assert research_metadata({})['posthoc'] is None
    assert research_metadata({'posthoc': False})['research_origin'] == 'unknown'
    assert research_metadata({'posthoc': True})['research_origin'] == 'posthoc'
    assert not research_metadata({'independently_confirmed': True})['independently_confirmed']
