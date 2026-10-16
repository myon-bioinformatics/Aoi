"""Issue #30: lossless input evidence, independent of decisions and presentation."""
from dataclasses import asdict
import json

import pytest

import ask
import inbox
from ask import Query, main, parse
from inbox import ask_question


Q5 = "P121 は 2026 年で確かめられた？"


@pytest.fixture
def results(tmp_path):
    # Deliberately make the written ID answerable, including a provisional 2026
    # counterexample. Unread input must block even when such a result exists.
    rows = [{"id": pid, "statement": "2026 年で確かめられた、という候補",
             "forms": [{"form": "original", "n": 1, "hold": 0, "rate": 0.0,
                        "counterexamples": [{"unit": "d-2026"}]}]}
            for pid in ("P121", "P117", "P1")]
    path = tmp_path / "results"
    path.mkdir()
    (path / "propositions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    (path / "sets.jsonl").write_text("", encoding="utf-8")
    return path


def test_q5_cli_preserves_original_unread_and_stays_undetermined(results, capsys):
    assert main([Q5, "--results", str(results), "--json", "--suggest-threshold", "0"]) == 1
    got = json.loads(capsys.readouterr().out)
    assert got["answer"] == "判定不能"
    assert got["query"]["target"] == "P121"
    assert got["rows"] == []
    assert any("2026 年で確かめられた" in part for part in got["unread"])
    assert got["raw_text"] == Q5
    assert got["parse_status"] == "undetermined"
    assert got["unread_spans"] == [{"start": 7, "end": 20, "raw_text": "2026 年で確かめられた"}]
    assert got["reason_codes"] == ["unrecognized_ask", "unsupported_text"]
    assert got["suggestions"] and got.get("selected") is None


@pytest.mark.parametrize("condition", ["とか", "のがでとか", "確かめられた", "年で", "がが", "zz-2026"])
def test_unknown_conditions_cannot_disappear_into_answerable_query(results, capsys, condition):
    text = f"P121 の反例はある？ {condition}"
    assert main([text, "--results", str(results), "--json"]) == 1
    got = json.loads(capsys.readouterr().out)
    assert got["answer"] == "判定不能" and got["rows"] == []
    assert got["query"] == asdict(Query(ask="has_counterexample", target="P121"))
    assert condition in [span["raw_text"] for span in got["unread_spans"]]


# These are the actual Q1-Q4 and the three original /ask requests from Issue #9.
# JSON requests bypass the natural-language reader, as they did before this fix.
@pytest.mark.parametrize("text, expected, blocked", [
    ("得点した回の平均得点が下位2なら B の命題に判例はある？",
     Query(ask="has_counterexample", kind="proposition"), True),
    ("P117 の対偶の判例", Query(target="P117", form="contrapositive"), False),
    ('{"ask":"counterexamples","target":"P117","form":"contrapositive"}',
     Query(target="P117", form="contrapositive"), False),
    ('{"ask":"has_counterexample","target":"E25","exclude":["t-2015"]}',
     Query(ask="has_counterexample", target="E25", exclude=["t-2015"]), False),
    ("E26 に判例はある？", Query(ask="has_counterexample", target="E26"), False),
    ('{"ask":"has_counterexample","target":"E30"}', Query(ask="has_counterexample", target="E30"), False),
    ("E25 に阪神 2015 以外の判例はある？", Query(ask="has_counterexample", target="E25", exclude=["t-2015"]), False),
    ('{"ask":"has_counterexample","target":"E25"}', Query(ask="has_counterexample", target="E25"), False),
    ("判例がただ1つの式は？", Query(ask="unique_exception", kind="expression"), False),
    ("Ｅ２６　に反例はある？", Query(ask="has_counterexample", target="E26"), False),
    ("成立率９５％以上の式", Query(ask="rate", kind="expression", min_rate=.95), False),
    ("中日が判例の命題", Query(kind="proposition", about=["d"]), False),
])
def test_existing_queries_keep_the_same_parse(results, text, expected, blocked):
    if not text.startswith("{"):
        query, unread = parse(text)
        assert query == expected and bool(unread) is blocked
    got, _ = ask_question(text, results)
    assert got["query"] == asdict(expected)
    if blocked:
        assert got["result"]["answer"] == "判定不能" and got["result"]["rows"] == []
    else:
        assert got["result"] == ask.answer_results(expected, results)


@pytest.mark.parametrize("text, fragment", [
    (Q5, "2026 年で確かめられた"),
    ("\tＰ１２１　は　２０２６ 年で確かめられた？\n", "２０２６ 年で確かめられた"),
    ("P121 は 2026\t年で\n確かめられた？", "2026\t年で\n確かめられた"),
    ("P121 の反例はある？ ｶﾞがかとのにはをでとか", "ｶﾞがかとのにはをでとか"),
    ("P121 の反例はある？ か\u3099🧪ﬃ㍿", "か\u3099🧪ﬃ㍿"),
    ("P121 の反例はある？ a\u0327\u0301\u1100\u1161", "a\u0327\u0301\u1100\u1161"),
    ("🧪 P121 の反例はある？", "🧪"),
    ("P121 の反例はある？ \0", "\0"),
])
def test_raw_spans_refer_to_original_unicode_not_normalized_offsets(text, fragment):
    parsed = ask.parse_input(text)
    assert parsed.status == "undetermined"
    assert parsed.raw_text == text
    assert fragment in [span.raw_text for span in parsed.unread_spans]
    for span in parsed.unread_spans:
        assert text[span.start:span.end] == span.raw_text
    assert parse(text) == (parsed.query, parsed.unread)


def test_disconnected_unread_spans_do_not_include_consumed_id_or_vocabulary():
    text = "あがか E25 の反例はある？ とか"
    parsed = ask.parse_input(text)
    assert [span.raw_text for span in parsed.unread_spans] == ["あがか", "とか"]
    assert all(text[span.start:span.end] == span.raw_text for span in parsed.unread_spans)


@pytest.mark.parametrize("text, reason", [
    ("E25 と E26 の反例", "multiple_targets"),
    ("成立率95%の式", "missing_rate_direction"),
    ("成立率の式", "missing_rate_value"),
    ("成立率95%未満の式", "unsupported_rate_comparison"),
    ("E25 の対偶の裏の反例", "multiple_forms"),
    ("成立率101%以上の式", "invalid_query"),
])
def test_reason_codes_do_not_depend_on_unread_display_text(text, reason):
    parsed = ask.parse_input(text)
    assert parsed.status == "undetermined"
    assert reason in [diagnostic.code for diagnostic in parsed.diagnostics]
    assert parsed.blocked_answer()["status"] == "undetermined"
    assert reason in parsed.blocked_answer()["reason_codes"]
    assert all(diagnostic.explanation for diagnostic in parsed.diagnostics)


def test_q5_log_and_inbox_preserve_the_same_parse_evidence(results, tmp_path, capsys):
    log = tmp_path / "asked.jsonl"
    assert main([Q5, "--results", str(results), "--json", "--log", str(log)]) == 1
    cli = json.loads(capsys.readouterr().out)
    record = json.loads(log.read_text(encoding="utf-8"))
    receipt, shown = ask_question(Q5, results)
    for key in ("raw_text", "parse_status", "parse_diagnostics", "unread_spans", "query", "unread"):
        assert cli[key] == record[key] == receipt[key]
    assert receipt["result"]["answer"] == "判定不能"
    assert receipt["result"]["reason_codes"] == cli["reason_codes"]
    assert "2026 年で確かめられた" in shown
    assert "判定不能" in shown


@pytest.mark.parametrize("mode", ["direct", "known", "cache", "both"])
def test_q5_never_consumes_or_changes_known_answers_or_cache(results, tmp_path, monkeypatch, mode):
    known, cache = tmp_path / "known", tmp_path / "answers"
    valid = "P121 の判例"
    # Same fallback Query as Q5, with a real saved answer and known snapshot.
    ask_question(valid, results, known=known, cycle="c001", result_sha="sha")
    expected, _ = ask_question(valid, results, cache=cache, cycle="c001", result_sha="sha")
    assert expected["result"]["answer"] == 1
    before = {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}

    def forbidden(*args, **kwargs):
        pytest.fail("uninterpreted input reached an answer or known-answer lookup")

    monkeypatch.setattr(inbox, "prepare", forbidden)
    monkeypatch.setattr(inbox, "lookup", forbidden)
    monkeypatch.setattr(inbox, "answer_results", forbidden)
    got, shown = ask_question(Q5, results,
                              known=known if mode in ("known", "both") else None,
                              cache=cache if mode in ("cache", "both") else None,
                              cycle="c001", result_sha="sha", suggest_threshold=0)
    assert got["query"] == expected["query"]
    assert got["result"]["answer"] == "判定不能" and got["result"]["rows"] == []
    assert got["suggestions"] and "候補。答えではない" in shown
    assert {str(p.relative_to(tmp_path)): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


def test_machine_decision_does_not_depend_on_human_wording(results, monkeypatch):
    parsed = ask.parse_input(Q5)
    parsed.diagnostics = [ask.ParseDiagnostic(d.code, "説明文を変更") for d in parsed.diagnostics]
    monkeypatch.setattr(inbox, "parse_input", lambda text: parsed)
    got, shown = ask_question(Q5, results)
    assert got["parse_status"] == "undetermined"
    assert got["result"]["reason_codes"] == ["unrecognized_ask", "unsupported_text"]
    assert got["result"]["answer"] == "判定不能" and got["result"]["rows"] == []
    assert got["unread_spans"] == [{"start": 7, "end": 20, "raw_text": "2026 年で確かめられた"}]
    assert "説明文を変更" in shown
