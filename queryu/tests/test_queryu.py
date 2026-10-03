"""取得の礼儀（負荷）と来歴の記録。ネットワークには出ず、httpx.MockTransport で応答を作る。"""

import json
from pathlib import Path

import httpx
import pytest

import npb_calendar
from queryu import Cache, OfflineMiss, PoliteFetcher, build, main, write_dataset

PAGE = (Path(__file__).resolve().parents[2] / "blueprobe" / "tests" / "fixtures" / "npb_calendar_sample.html").read_text(encoding="utf-8")


def fetcher(tmp_path, handler, **kw):
    return PoliteFetcher(Cache(tmp_path / "cache"), wait=0, client=httpx.Client(transport=httpx.MockTransport(handler)), **kw)


def only_april(req):
    if "index_04" in str(req.url):
        return httpx.Response(200, text=PAGE, headers={"Last-Modified": "Wed, 01 Oct 2025 00:00:00 GMT", "ETag": '"abc"'})
    return httpx.Response(404)


def test_finished_season_hits_network_once(tmp_path):
    calls = []
    f = fetcher(tmp_path, lambda r: calls.append(r) or only_april(r))
    pages = npb_calendar.pages([2024])
    assert len(build(npb_calendar, pages, f)["2024"]["records"]) == 4
    assert len(calls) == 9  # 3〜11月。404 の月も1回だけ
    f2 = fetcher(tmp_path, lambda r: pytest.fail("終了済みシーズンは再取得しない"))
    assert len(build(npb_calendar, pages, f2)["2024"]["records"]) == 4


def test_manifest_records_provenance(tmp_path):
    f = fetcher(tmp_path, only_april)
    build(npb_calendar, npb_calendar.pages([2024]), f)
    entries = [json.loads(line) for line in (tmp_path / "cache" / "manifest.jsonl").read_text().splitlines()]
    assert len(entries) == 9
    april = next(e for e in entries if e["key"] == "2024_04")
    assert april["status"] == 200 and april["url"].endswith("/bis/2024/calendar/index_04.html")
    assert april["last_modified"] and april["etag"] == '"abc"' and len(april["sha256"]) == 64
    assert april["fetched_at"].endswith("+00:00")
    assert {e["status"] for e in entries} == {200, 404}
    assert "code_version" in april  # 測れなければ None。推測で埋めない


def test_live_season_sends_conditional_headers_and_logs_304(tmp_path):
    seen = []

    def handler(req):
        seen.append((req.headers.get("If-Modified-Since"), req.headers.get("If-None-Match")))
        if "index_04" not in str(req.url):
            return httpx.Response(404)
        if req.headers.get("If-None-Match"):
            return httpx.Response(304)
        return only_april(req)

    f = fetcher(tmp_path, handler)
    pages = [p for p in npb_calendar.pages([2024]) if p[0] == "2024_04"]
    build(npb_calendar, pages, f, live_groups={"2024"})
    got = build(npb_calendar, pages, f, live_groups={"2024"})
    assert len(got["2024"]["records"]) == 4  # 304 → 保存済みの本文を再利用
    assert seen[-1] == ("Wed, 01 Oct 2025 00:00:00 GMT", '"abc"')
    statuses = [json.loads(line)["status"] for line in (tmp_path / "cache" / "manifest.jsonl").read_text().splitlines()]
    assert statuses == [200, 304]  # 「確認した」ことも記録に残る


def test_offline_never_touches_network(tmp_path):
    fetcher(tmp_path, only_april).get("2024_04", npb_calendar.pages([2024])[1][1], "2024")
    off = fetcher(tmp_path, lambda r: pytest.fail("offline"), offline=True)
    assert off.get("2024_04", "u", "2024", live=True)  # live 指定でもキャッシュを使う
    with pytest.raises(OfflineMiss):
        off.get("2024_05", "u", "2024")


def test_server_error_is_not_cached(tmp_path):
    f = fetcher(tmp_path, lambda r: httpx.Response(503))
    with pytest.raises(httpx.HTTPStatusError):
        f.get("2024_04", "https://npb.jp/x", "2024")
    assert not (tmp_path / "cache" / "manifest.jsonl").exists()


def test_write_dataset_merges_and_writes_manifest(tmp_path):
    path = tmp_path / "obs" / "games.jsonl"
    write_dataset(path, [{"key": "b", "date": "2024-04-02"}, {"key": "a", "date": "2024-04-01"}], {"source": "s"})
    write_dataset(path, [{"key": "b", "date": "2024-04-02", "x": 1}], {"source": "s"})
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert rows == [{"key": "a", "date": "2024-04-01"}, {"key": "b", "date": "2024-04-02", "x": 1}]
    meta = json.loads(path.with_suffix(".manifest.json").read_text())
    assert meta["records"] == 2 and meta["source"] == "s" and len(meta["sha256"]) == 64


def test_cli_offline_end_to_end(tmp_path, capsys):
    fetcher(tmp_path, only_april).get("2024_04", npb_calendar.pages([2024])[1][1], "2024")
    for key, url, group in npb_calendar.pages([2024]):  # 他の月は 404 として記録済みにする
        if key != "2024_04":
            Cache(tmp_path / "cache").put(key, url, group, 404, b"", {})
    out = tmp_path / "obs" / "games.jsonl"
    assert main(["--source", "npb_calendar", "--years", "2024", "--cache", str(tmp_path / "cache"),
                 "--out", str(out), "--offline"]) == 0
    text = capsys.readouterr().out
    assert "2024: records=4 cancelled=1 non_regular=1 unknown=0" in text and "HTTP requests: 0" in text
    meta = json.loads(out.with_suffix(".manifest.json").read_text())
    assert meta["dropped"] == {"cancelled": 1, "non_regular": 1} and meta["unknown"] == 0
    assert "NFKC" in meta["normalization"]
