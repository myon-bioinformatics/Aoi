"""❓ 問い合わせ（ask/）: 判定不能の返信に付ける候補 ID、ID 候補の提示（suggest.py）、読めなかった入力の証跡（Issue #30）。

候補は答えではない。suggest.py は ask.py の答えの経路を通さない。
"""
import json
from dataclasses import asdict
from pathlib import Path

import pytest

import aoi_paths
import ask
import inbox
import suggest
from ask import Query, answer_results, main, parse, suggestion_for
from inbox import ask_question

RESULTS = aoi_paths.default_cycle_outputs(aoi_paths.resolve_aoi_root(anchor=Path(__file__)))  # Aoi の既定のサイクルの結果


# ──── suggestions: 判定不能の返信に、答えではない候補 ID を最大 5 件付ける ────────────────────────────────────────────────────────

ASK_DOCS = [
    ("P46", "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ない"),
    ("P47", "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ない隣"),
    ("P1", "得失点差がプラスなら上位半分である"),
    ("P9", "1点差の試合で勝ち越すと期待勝利数を上回る"),
    ("P2", "失点順位が上位なら勝率も上位"),
    ("P3", "得点順位が下位ならBクラス"),
    ("P4", "本拠地の観客が多い年は順位が上"),
    ("P5", "救援の失点が少ない年は上位"),
]


def _write(results: Path, rows):
    results.mkdir(parents=True, exist_ok=True)
    (results / "propositions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _prop(pid, statement):
    return {
        "id": pid, "statement": statement,
        "if": [{"col": "rd", "op": ">", "value": 0}],
        "if_any": [], "then": [{"col": "upper_half", "op": "==", "value": True}],
        "forms": [{"form": "original", "n": 4, "hold": 3, "rate": 0.75,
                   "counterexamples": [{"unit": "t-2015"}]}],
    }


def test_similar_candidates_never_select_an_id():
    got = suggest.similar_candidates("P46 の隣の番号だったかもしれない", ASK_DOCS, threshold=0.0, dim=4, k=5)
    assert got["selected"] is None
    assert got["written_id"] == "P46"
    assert 1 <= len(got["candidates"]) <= 5
    assert "答えではない" in got["note"]


def test_unread_appends_candidates_and_does_not_answer_them(tmp_path, capsys):
    results = tmp_path / "out"
    _write(results, [_prop(i, t) for i, t in ASK_DOCS])
    (results / "sets.jsonl").write_text("", encoding="utf-8")
    text = "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ない、雨の日だけ"
    code = main([text, "--results", str(results), "--json", "--suggest-threshold", "0"])
    assert code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["answer"] == "判定不能"
    assert payload["query"]["target"] is None
    assert payload["suggestion_status"] in ("要確認", "判定不能")
    assert 1 <= len(payload["suggestions"]) <= 5
    assert payload.get("selected") is None
    rendered = main([text, "--results", str(results), "--suggest-threshold", "0"])
    shown = capsys.readouterr().out
    assert rendered == 1
    assert "もしかして: " in shown
    assert "（候補。答えではない）" in shown
    assert shown.split("もしかして: ", 1)[1].count(" / ") <= 4
    assert "［" not in shown.split("もしかして: ", 1)[1]


def test_unknown_id_is_not_auto_answered(tmp_path, capsys):
    results = tmp_path / "out"
    _write(results, [_prop(i, t) for i, t in ASK_DOCS])
    text = "P999 の判例は？"
    assert main([text, "--results", str(results), "--json", "--suggest-threshold", "-1"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["answer"] == "判定不能"
    assert "結果にない" in payload["error"]
    assert "結果が読めない" not in payload["error"]
    assert payload["query"]["target"] == "P999"
    ids = [c["id"] for c in payload["suggestions"]]
    assert ids and "P999" not in ids and len(ids) <= 5


def test_missing_sets_is_unreadable_and_has_no_candidates(tmp_path, capsys):
    results = tmp_path / "out"
    _write(results, [_prop("P1", "得失点差がプラスなら上位")])
    res = answer_results(Query(target="E25"), results)
    assert res["answer"] == "判定不能"
    assert res["error"] == "結果が読めない: sets.jsonl"
    assert "結果にない" not in res["error"]
    hinted = suggestion_for("E25 の判例は？", results, [], res, threshold=0.0)
    assert hinted["line"] == "" and hinted["candidates"] == []
    assert main(["E25 の判例は？", "--results", str(results), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["suggestions"] == []
    assert "もしかして" not in json.dumps(payload, ensure_ascii=False)


def test_present_file_without_the_id_stays_not_in_results(tmp_path):
    results = tmp_path / "out"
    results.mkdir()
    (results / "sets.jsonl").write_text(json.dumps(_prop("E1", "式")) + "\n", encoding="utf-8")
    res = answer_results(Query(target="E25"), results)
    assert "結果にない" in res["error"]
    assert "結果が読めない" not in res["error"]


def test_answered_question_has_no_moshikashite(tmp_path, capsys):
    results = tmp_path / "out"
    _write(results, [_prop("P1", "得失点差がプラスなら上位")])
    assert main(["P1 の判例は？", "--results", str(results), "--json", "--suggest-threshold", "0"]) == 0
    raw = capsys.readouterr().out
    payload = json.loads(raw)
    assert payload["answer"] == 1
    assert payload["suggestions"] == []
    assert "もしかして" not in raw


def test_threshold_comes_from_cycle_config_and_missing_means_unconfirmed(tmp_path):
    cycle = tmp_path / "cycles" / "c9"
    cycle.mkdir(parents=True)
    (cycle / "ask.toml").write_text("suggest_threshold = 0.2\n", encoding="utf-8")
    assert ask.load_suggest_threshold(cycle) == 0.2
    bare = tmp_path / "cycles" / "empty"
    bare.mkdir()
    (bare / "ask.toml").write_text("# 未設定\n", encoding="utf-8")
    assert ask.load_suggest_threshold(bare) is None
    results = tmp_path / "out"
    _write(results, [_prop(i, t) for i, t in ASK_DOCS])
    (results / "sets.jsonl").write_text("", encoding="utf-8")
    hinted = suggestion_for("雨の日だけ教えて", results, ["未対応の語・条件: 雨日だけ教えて"], {"answer": "判定不能", "error": "x", "rows": []}, None)
    assert hinted["status"] == "判定不能"
    assert hinted["selected"] is None
    assert hinted["line"].endswith("（候補。答えではない）")


def test_repo_without_sets_does_not_call_e25_missing():
    if (RESULTS / "sets.jsonl").is_file():
        return
    res = answer_results(Query(target="E25"), RESULTS)
    assert res["error"].startswith("結果が読めない")
    assert "結果にない" not in res["error"]


class _Queue:
    """パイプ・FIFO の代わり。端末ではない標準入力。"""

    def __init__(self, text):
        import io
        self._io = io.StringIO(text)

    def __iter__(self):
        return iter(self._io)

    def read(self):
        return self._io.read()

    def isatty(self):
        return False


def test_question_words_need_no_quotes_and_may_sit_between_options(tmp_path, capsys):
    results = tmp_path / "out"
    _write(results, [_prop("P1", "得失点差がプラスなら上位")])
    assert main(["P1", "--results", str(results), "の判例は？", "--json", "--suggest-threshold", "0"]) == 0
    assert json.loads(capsys.readouterr().out)["answer"] == 1


def test_questions_from_a_queue_are_answered_in_order(tmp_path, capsys, monkeypatch):
    results = tmp_path / "out"
    _write(results, [_prop("P1", "得失点差がプラスなら上位"), _prop("P2", "失点が少なければ上位")])
    monkeypatch.setattr("sys.stdin", _Queue("P1 の判例は？\n\nP2 の判例は？\n"))
    assert main(["--results", str(results), "--json", "--suggest-threshold", "0"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [json.loads(line)["query"]["target"] for line in lines] == ["P1", "P2"]


def test_query_json_can_come_from_stdin(tmp_path, capsys, monkeypatch):
    results = tmp_path / "out"
    _write(results, [_prop("P1", "得失点差がプラスなら上位")])
    monkeypatch.setattr("sys.stdin", _Queue(json.dumps({"target": "P1"})))
    assert main(["--query", "-", "--results", str(results), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["query"]["target"] == "P1"


def test_missing_sets_with_unread_text_never_suggests_propositions(tmp_path, capsys):
    (tmp_path / "propositions.jsonl").write_text(json.dumps({"id": "P1", "statement": "雨の日", "forms": []}))
    assert ask.main(["E25 に雨の日だけの反例はある？", "--results", str(tmp_path), "--json", "--suggest-threshold", "0"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["answer"] == "判定不能"
    assert payload["query"]["target"] == "E25"
    assert payload["suggestions"] == []
    assert payload["suggestion_status"] is None


# ──── id suggest: ID 候補の提示。ask.py の答えの経路は通さない ─────────────────────────────────────────────────────────────

QUESTIONS = Path(__file__).resolve().parent / "fixtures" / "id_suggest_questions.jsonl"

SUGGEST_DOCS = [
    ("P46", "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ないという命題"),
    ("P47", "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ないという隣の命題"),
    ("P1", "得失点差がプラスなら上位半分である"),
    ("P9", "1点差の試合で勝ち越すと期待勝利数を上回る"),
    ("N1", "明日の天気とビールの売上"),
    ("N2", "監督の名前と本拠地"),
]


def test_suggest_does_not_call_ask(monkeypatch):
    def fail(*_a, **_k):
        raise AssertionError("ask の答えの経路を呼んだ")

    # 読み取りは、候補モジュールを import しても ID を補完しない
    q, _unread = ask.parse("得失点差がプラスのチームはAクラスになる、という命題の判例は？")
    assert q.target is None
    monkeypatch.setattr(ask, "answer", fail)
    monkeypatch.setattr(ask, "parse", fail)
    monkeypatch.setattr(ask, "main", fail)
    got = suggest.suggest("得失点差がプラスなら上位か", SUGGEST_DOCS, threshold=0.0, dim=4, k=5)
    assert got["selected"] is None and got["candidates"]


def test_explicit_id_skips_the_index():
    built = {"n": 0}
    real = suggest.Index

    class Boom(suggest.Index):
        def __init__(self, *a, **k):
            built["n"] += 1
            raise AssertionError("書いてある ID では索引を作らない")

    suggest.Index = Boom
    try:
        got = suggest.suggest("E25 に阪神 2015 以外の判例はある？", SUGGEST_DOCS, threshold=0.99)
    finally:
        suggest.Index = real
    assert built["n"] == 0
    assert got["status"] == "explicit" and got["selected"] == "E25"
    assert got["candidates"] == [{"id": "E25", "similarity": None}]
    # E25 は SUGGEST_DOCS に無いので、known=False と note で知らせる
    assert got["known"] is False and "見つからない" in got["note"]


def test_handwritten_explicit_questions_keep_the_written_id():
    for line in QUESTIONS.read_text(encoding="utf-8").splitlines():
        q = json.loads(line)
        if q["type"] != "explicit":
            continue
        got = suggest.suggest(q["q"], SUGGEST_DOCS, threshold=0.99)
        assert got["status"] == "explicit" and got["selected"] == q["expect"]


def test_below_threshold_is_not_an_answer():
    idx = suggest.Index(SUGGEST_DOCS, dim=4)
    text = "明日の先発投手を教えて"
    top = idx.query(text, "float", 5)
    got = suggest.suggest(text, SUGGEST_DOCS, threshold=top[0][1] + 1e-6, dim=4, index=idx)
    assert got["status"] == "判定不能" and got["selected"] is None
    assert len(got["candidates"]) == 5
    above = suggest.suggest(text, SUGGEST_DOCS, threshold=top[0][1], dim=4, index=idx)
    assert above["status"] == "要確認" and above["selected"] is None


def test_near_duplicate_ids_stay_candidates():
    idx = suggest.Index(SUGGEST_DOCS, dim=4)
    got = suggest.suggest("中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ないか", SUGGEST_DOCS,
                          threshold=-1.0, dim=4, k=5, index=idx)
    ids = [c["id"] for c in got["candidates"]]
    assert got["status"] == "要確認" and got["selected"] is None
    assert "P46" in ids and "P47" in ids


def test_binary_index_is_smaller_and_still_returns_five():
    idx = suggest.Index(SUGGEST_DOCS, dim=4)
    sizes = idx.sizes()
    assert sizes["binary_bytes"] < sizes["float32_bytes"]
    got = suggest.suggest("得失点差がプラスなら上位半分か", SUGGEST_DOCS, threshold=-1.0, mode="binary", dim=4, index=idx)
    assert got["status"] == "要確認" and got["selected"] is None and len(got["candidates"]) == 5


def test_real_propositions_refuse_an_unrelated_question():
    docs = suggest.load_docs(RESULTS)
    assert len(docs) >= 50 and any(i == "P46" for i, _ in docs)
    assert (RESULTS / "sets.jsonl").exists() is False or any(i.startswith("E") for i, _ in docs)
    idx = suggest.Index(docs, dim=32)
    text = "明日の先発投手を教えて"
    top = idx.query(text, "float", 5)
    got = suggest.suggest(text, docs, threshold=top[0][1] + 1e-6, mode="float", index=idx)
    assert got["status"] == "判定不能" and got["selected"] is None
    assert len(got["candidates"]) == 5
    assert all(c["id"] in {i for i, _ in docs} for c in got["candidates"])


def test_cli_prints_candidates_and_does_not_answer(tmp_path, capsys):
    results = tmp_path / "out"
    results.mkdir()
    (results / "propositions.jsonl").write_text(
        "\n".join(json.dumps({"id": i, "statement": t, "if": [], "if_any": [], "then": []}, ensure_ascii=False)
                  for i, t in SUGGEST_DOCS) + "\n",
        encoding="utf-8")
    # float の類似度は正規化したベクトルの内積なので 1 を超えない。1.1 未満は判定不能になる。
    assert suggest.main(["量子暗号の株価を教えて", "--results", str(results), "--threshold", "1.1", "--dim", "4"]) == 0
    got = json.loads(capsys.readouterr().out)
    assert got["status"] == "判定不能" and got["selected"] is None


def test_explicit_id_present_in_docs_is_known():
    got = suggest.suggest("P46 の判例は？", SUGGEST_DOCS, threshold=0.99)
    assert got["selected"] == "P46" and got["known"] is True and "見つからない" not in got["note"]


def test_ties_are_ordered_by_document_order():
    # 類似度がちょうど同じ文書は、文書の並び（ids の順）で毎回同じ順に出る
    import math

    np = suggest.np  # vendor した numpy_min
    docs = [(f"P{i}", f"得失点差がプラスなら上位半分である {i}") for i in range(20, 0, -1)]
    idx = suggest.Index(docs, dim=4)
    n, d = idx.Zf.shape
    idx.Zf = np.ones((n, d), np.float32) * np.float32(1 / math.sqrt(d))
    idx.B = np.ones(idx.B.shape, np.int8)
    for mode in ("float", "binary"):
        got = idx.query("得失点差がプラスなら上位か", mode, 10)
        assert len({s for _, s in got}) == 1
        assert [i for i, _ in got] == [f"P{i}" for i in range(20, 10, -1)]


# ──── unread input: Issue #30 lossless input evidence, independent of decisions and presentation ──────────

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


def test_without_a_team_table_team_names_are_unread():
    import ask
    ask.set_teams({})
    parsed = ask.parse_input("中日が判例の命題")
    assert parsed.query.about == []
    assert any("中日" in u for u in parsed.unread)
    with __import__("pytest").raises(ValueError):
        ask.set_teams({"": "d"})
