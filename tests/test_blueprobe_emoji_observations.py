"""emoji_observations: where and how emoji appear in saved HTML (offline, observation only)."""
import json
from pathlib import Path

import pytest

import emoji_observations as eo

CASES = Path(__file__).resolve().parent / "cases"
HOME, MAP, MAP_VS = "\U0001F3E0", "\U0001F5FA", "\U0001F5FA\ufe0f"

# Synthetic page (not a real site; see SYNTHETIC_FIXTURE_AS_REAL): every place emoji can hide.
PAGE = (
    f"<html><head><title>{HOME} Home</title><meta name='description' content='map {MAP_VS}'>"
    "<meta name='viewport' content='width=device-width'>"
    "<style>.x:before{content:'\U0001F389'}</style></head><body>"
    f"<nav><a href='#/' aria-label='Home'>{HOME}</a><button>{MAP}</button>"
    "<span aria-hidden='true'>\u2728</span><img alt='\U0001F44D\U0001F3FD ok'><br>"
    "<div role='button' title='Settings'>\u2699\ufe0f</div></nav>"
    "<p>\u00a9\ufe0f and \u00a9 and \U0001F469\u200d\U0001F4BB coder \u3030 wave</p>"
    "<script>'\U0001F6AB'</script><template>\U0001F6AB</template>"
    "<input placeholder='\U0001F50D search' value='\U0001F6AB typed'></body></html>")


def rows(report):
    return [(r["emoji"], r["where"], r["element"], r["in_control"], r["control_label"], r["aria_hidden"])
            for r in report["records"]]


def test_records_every_visible_place_with_context():
    report = eo.observe(PAGE, "https://example.test/")
    assert rows(report) == [
        (HOME, "title", "html > head > title", None, None, False),
        (MAP_VS, "meta:description", "html > head > meta", None, None, False),
        (HOME, "text", "html > body > nav > a", "a", "Home", False),
        (MAP, "text", "html > body > nav > button", "button", None, False),
        ("\u2728", "text", "html > body > nav > span", None, None, True),
        ("\U0001F44D\U0001F3FD", "attr:alt", "html > body > nav > img", None, None, False),
        ("\u2699\ufe0f", "text", "html > body > nav > div", "div", "Settings", False),
        ("\u00a9\ufe0f", "text", "html > body > p", None, None, False),
        ("\U0001F469\u200d\U0001F4BB", "text", "html > body > p", None, None, False),
        ("\U0001F50D", "attr:placeholder", "html > body > input", None, None, False)]
    first = report["records"][0]
    assert first["key"] == "https://example.test/#0" and first["identity"] == HOME and first["raw_text"] == f"{HOME} Home"
    assert report["counts"][MAP] == 2 and report["unknown"] == []
    assert "\U0001F6AB" not in report["counts"] and "\U0001F389" not in report["counts"]  # script/style/template/value


def test_summary_forms_places_and_unlabelled_controls():
    summary = {row["identity"]: row for row in eo.summarize(eo.observe(PAGE))}
    assert summary[MAP]["forms"] == {MAP_VS: 1, MAP: 1}
    assert summary[MAP]["where"] == {"meta:description": 1, "text": 1}
    assert summary[MAP]["unlabelled_control"] == 1 and summary[HOME]["unlabelled_control"] == 0
    assert summary["\u2728"]["aria_hidden"] == 1 and summary["\u2699"]["unlabelled_control"] == 0
    assert list(summary)[:2] == [HOME, MAP]


def test_contract_with_xprobe_sequences():
    expected = json.loads((CASES / "emoji_corpus.expected.json").read_text(encoding="utf-8"))
    assert expected["source"]["repository"] == "myon-bioinformatics/xprobe"
    assert eo.emoji_sequences((CASES / "emoji_corpus.txt").read_text(encoding="utf-8")) == expected["sequences"]


def test_truncation_is_recorded_not_silent():
    report = eo.observe("<p>" + HOME * 5 + "</p>", "u", max_records=3)
    assert len(report["records"]) == 3 and report["unknown"] == [{"url": "u", "reason": "truncated after 3 emoji"}]


def test_snapshot_provenance_is_carried():
    snapshot = {"schema": "html-snapshot/1", "html": f"<p>{HOME}</p>", "url": "https://example.test/",
                "response_sha256": "a" * 64, "fetched_at": "2026-10-18T00:00:00+00:00", "encoding": "utf-8"}
    record = eo.observe_snapshot(snapshot)["records"][0]
    assert record["response_sha256"] == "a" * 64 and record["fetched_at"].startswith("2026") and record["url"]
    with pytest.raises(ValueError):
        eo.observe_snapshot({"schema": "other", "html": ""})
    with pytest.raises(TypeError):
        eo.observe(b"<p></p>")


def test_cli(tmp_path, capsys):
    page = tmp_path / "page.html"
    page.write_text(PAGE, encoding="utf-8")
    assert eo.main([str(page)]) == 0
    out = capsys.readouterr().out
    assert f"{MAP}\t2\t{MAP_VS}x1 {MAP}x1\tmeta:descriptionx1 textx1 unlabelled_control=1" in out
    assert out.rstrip().endswith("emoji: 8 distinct, 10 occurrence(s)")
    assert eo.main([str(page), "--json", "--url", "https://example.test/"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["records"][0]["url"] == "https://example.test/" and data["summary"][0]["identity"] == HOME
    assert eo.main([str(tmp_path / "missing.html")]) == 2
