"""📥 取得（queryu.py）: 取得の礼儀（負荷）と来歴、観測データセット、未来の月・手動の凍結・--plan、単一ファイルの入口。

NPB には出ない。HandlerClient で応答を作る。PR #42 の独立レビューの境界（状態を書き換えない）も含む。
"""
import datetime as dt, importlib.util, json, shutil, subprocess, sys, urllib.request
from pathlib import Path
from types import SimpleNamespace

import pytest

import aoi_paths
import npb_calendar
import queryu
from queryu import (Cache, HandlerClient, HTTPStatusError, OfflineMiss, PoliteFetcher, Response, UrllibClient,
                    acquisition_plan, build, format_plan, live_groups, load_frozen, main, save_frozen,
                    split_future_months, write_dataset)

ROOT = Path(__file__).resolve().parents[1]

# Use this checkout's vendored CLI helper without importing a shared vendor namespace.
_cli_spec = importlib.util.spec_from_file_location("_queryu_test_cli_args", ROOT / "vendor" / "cli_args.py")
_cli_module = importlib.util.module_from_spec(_cli_spec)
sys.modules[_cli_spec.name] = _cli_module
_cli_spec.loader.exec_module(_cli_module)
run_cli = _cli_module.run_cli

MONTH_KEY = r"(?P<year>\d{4})_(?P<month>\d{2})"  # npb_calendar の key（年_月）。Aoi の pipeline と同じ
PAGE = (aoi_paths.resolve_aoi_root(anchor=Path(__file__)) / "blueprobe" / "tests" / "fixtures" / "npb_calendar_sample.html").read_text(encoding="utf-8")


# ──── fetch: 取得の礼儀（負荷）と来歴の記録 ──────────────────────────────────────────────────────────────────────────────

def fetcher(tmp_path, handler, **kw):
    return PoliteFetcher(Cache(tmp_path / "cache"), wait=0, client=HandlerClient(handler), **kw)


def only_april(req):
    if "index_04" in str(req.url):
        return Response(200, text=PAGE, headers={"Last-Modified": "Wed, 01 Oct 2025 00:00:00 GMT", "ETag": '"abc"'})
    return Response(404)


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
            return Response(404)
        if req.headers.get("If-None-Match"):
            return Response(304)
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
    f = fetcher(tmp_path, lambda r: Response(503))
    with pytest.raises(HTTPStatusError):
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


def test_write_dataset_drops_records_the_rebuilt_scope_no_longer_produces(tmp_path):
    # 解析ルールを直した後、前の規則で採用した試合（例: CS）が残らない。範囲外の年は残す
    path = tmp_path / "obs" / "games.jsonl"
    old = [{"key": "a", "date": "2013-10-12"}, {"key": "cs", "date": "2013-10-12"}, {"key": "z", "date": "2014-04-01"}]
    write_dataset(path, old, {"source": "s"})
    write_dataset(path, [{"key": "a", "date": "2013-10-12"}], {"source": "s"},
                  rebuilt=lambda r: npb_calendar.group(r) == "2013")
    assert [r["key"] for r in map(json.loads, path.read_text().splitlines())] == ["a", "z"]
    assert json.loads(path.with_suffix(".manifest.json").read_text())["removed"] == 1


def test_client_keeps_environment_proxy_settings(tmp_path, monkeypatch):
    # 環境変数のプロキシ設定を捨てない（PR #3 で判明）。urllib の既定の opener は ProxyHandler で環境変数を読む
    monkeypatch.setenv("https_proxy", "http://proxy.example.test:8080")
    client = PoliteFetcher(Cache(tmp_path / "cache"), wait=0).client
    assert isinstance(client, UrllibClient)
    proxies = [h.proxies for h in client.opener.handlers if isinstance(h, urllib.request.ProxyHandler)]
    assert proxies and proxies[0].get("https") == "http://proxy.example.test:8080"
    assert any(isinstance(h, urllib.request.HTTPRedirectHandler) for h in client.opener.handlers)
    assert client.headers["User-Agent"].startswith("Aoi-QueRyu/")


# ──── plan: 未来の月、手動の凍結、--plan ─────────────────────────────────────────────────────────────────────────────

def mock_client(monkeypatch, handler):
    monkeypatch.setattr(queryu, "UrllibClient", lambda **_kw: HandlerClient(handler))


def test_future_months_are_split_and_non_month_keys_stay():
    pages = [("2026_03", "u", "2026"), ("2026_04", "u", "2026"), ("2026_11", "u", "2026"), ("2026_c", "u", "2026")]
    kept, future = split_future_months(pages, dt.date(2026, 4, 1), MONTH_KEY)
    assert [p[0] for p in kept] == ["2026_03", "2026_04", "2026_c"]
    assert [p[0] for p in future] == ["2026_11"]
    assert live_groups([2024, 2026], dt.date(2026, 10, 16), set()) == {"2026"}
    assert live_groups([2024, 2026], dt.date(2026, 10, 16), {2026}) == set()


def test_plan_counts_cache_conditional_and_new_without_a_client(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(queryu, "UrllibClient", lambda **kw: pytest.fail("network"))
    cache = Cache(tmp_path / "cache")
    pages = npb_calendar.pages([2026])
    for key, url, group in pages:
        if key.endswith(("_03", "_04")):
            cache.put(key, url, group, 200, b"<html></html>", {"etag": '"v1"'})
    today = dt.date(2026, 5, 1)
    kept, future = split_future_months(pages, today, MONTH_KEY)
    plan = acquisition_plan(
        kept, cache, live=live_groups([2026], today, set()), wait=3,
        today=today, frozen=set(), future=future,
    )
    assert plan["future"] == 6
    assert plan["conditional"] == 2
    assert plan["new"] == 1
    assert plan["cached"] == 0
    assert plan["estimated_wait_seconds"] == 6
    text = format_plan(plan)
    assert text.split("解釈:")[0].count("条件付きGET: 2") == 1
    assert "待ち時間の見積もり: 6 秒" in text.split("解釈:")[1]
    frozen = tmp_path / "frozen.json"
    assert main(["--source", "npb_calendar", "--month-key", MONTH_KEY, "--years", "2026", "--cache", str(tmp_path / "cache"),
                 "--plan", "--today", "2026-05-01", "--frozen", str(frozen), "--wait", "3",
                 "--freeze", "2026"]) == 0
    shown = capsys.readouterr().out
    assert "キャッシュ済み（再確認しない）: 2" in shown
    assert "条件付きGET: 0" in shown
    assert "新規: 1" in shown
    assert "未来の月（取得しない）: 6" in shown
    assert not frozen.exists()


def test_freeze_is_manual_and_a_frozen_season_is_not_rechecked(tmp_path, monkeypatch, capsys):
    calls = []

    def handler(req):
        calls.append(str(req.url))
        if "index_04" in str(req.url):
            return Response(200, text=PAGE, headers={"Last-Modified": "Wed, 01 Oct 2025 00:00:00 GMT", "ETag": '"abc"'})
        return Response(404)

    mock_client(monkeypatch, handler)
    frozen = tmp_path / "frozen.json"
    out = tmp_path / "games.jsonl"
    args = ["--source", "npb_calendar", "--month-key", MONTH_KEY, "--years", "2026", "--cache", str(tmp_path / "cache"),
            "--out", str(out), "--wait", "0", "--today", "2026-10-16", "--frozen", str(frozen),
            "--freeze", "2026"]
    assert main(args) == 0
    assert load_frozen(frozen) == {2026}
    first = len(calls)
    assert first == 8  # 3〜10月。11月はまだ来ていない
    assert all("index_11" not in url for url in calls)
    assert main(args) == 0
    assert len(calls) == first
    assert "HTTP requests: 0" in capsys.readouterr().out


def test_unfrozen_current_season_is_rechecked(tmp_path, monkeypatch):
    calls = []

    def handler(req):
        calls.append(req.headers.get("If-None-Match"))
        return Response(404)

    mock_client(monkeypatch, handler)
    frozen = tmp_path / "frozen.json"
    out = tmp_path / "games.jsonl"
    args = ["--source", "npb_calendar", "--month-key", MONTH_KEY, "--years", "2026", "--cache", str(tmp_path / "cache"),
            "--out", str(out), "--wait", "0", "--today", "2026-04-02", "--frozen", str(frozen)]
    assert main(args) == 0
    assert len(calls) == 2  # 3月と4月
    assert main(args) == 0
    assert len(calls) == 4


def test_month_key_needs_year_and_month_groups_and_none_keeps_every_page():
    with pytest.raises(ValueError):
        queryu.month_key_pattern(r"(?P<year>\d{4})")
    pages = [("2026_11", "u", "2026")]
    assert split_future_months(pages, dt.date(2026, 4, 1)) == (pages, [])


def test_without_cache_pages_stay_in_memory_and_nothing_is_written(tmp_path, monkeypatch, capsys):
    calls = []

    def handler(req):
        calls.append(str(req.url))
        return Response(200, text=PAGE) if "index_04" in str(req.url) else Response(404)

    mock_client(monkeypatch, handler)
    monkeypatch.chdir(tmp_path)
    out = tmp_path / "games.jsonl"
    common = ["--source", "npb_calendar", "--month-key", "YYYY_MM", "--years", "2026", "--today", "2026-04-02",
              "--frozen", str(tmp_path / "frozen.json")]
    assert main([*common, "--plan"]) == 0
    assert "新規: 2" in capsys.readouterr().out  # キャッシュなしなら全部が新規
    assert main([*common, "--out", str(out), "--wait", "0"]) == 0
    assert len(calls) == 2
    assert sorted(p.name for p in tmp_path.iterdir()) == ["games.jsonl", "games.manifest.json"]
    assert json.loads((tmp_path / "games.manifest.json").read_text(encoding="utf-8"))["cache_manifest"] is None
    with pytest.raises(SystemExit) as exit_info:
        main([*common, "--plan", "--offline"])
    assert exit_info.value.code == 2


def test_month_key_template_needs_no_quotes():
    pattern = queryu.month_key_pattern("YYYY_MM")
    assert pattern.pattern == MONTH_KEY
    assert pattern.fullmatch("2024_03")["month"] == "03" and pattern.fullmatch("2024_c") is None


# ──── boundaries: PR #42 independent review probes (no persistent user state) ─────────────────────────────

@pytest.mark.parametrize("year", [26, 1899, 2101])
@pytest.mark.parametrize("plan", [False, True])
def test_invalid_freeze_never_changes_state(tmp_path, year, plan):
    frozen = tmp_path / "frozen.json"
    frozen.write_text('{"seasons": [2025]}\n')
    before = frozen.read_bytes()
    argv = ["--source", "npb_calendar", "--month-key", MONTH_KEY, "--years", "2026", "--cache", str(tmp_path / "cache"),
            "--frozen", str(frozen), "--freeze", str(year), "--out", str(tmp_path / "games.jsonl"), "--offline"]
    if plan:
        argv.append("--plan")
    with pytest.raises(SystemExit) as error:
        main(argv)
    assert error.value.code == 2
    assert frozen.read_bytes() == before
    assert not (tmp_path / "cache").exists()
    assert not (tmp_path / "games.jsonl").exists()


@pytest.mark.parametrize("year", [True, 2026.0, 1899, 2101])
def test_save_frozen_rejects_invalid_values_before_writing(tmp_path, year):
    path = tmp_path / "new-directory" / "frozen.json"
    with pytest.raises(ValueError, match="1900"):
        save_frozen(path, {year})
    assert not path.parent.exists()


def test_save_frozen_accepts_both_contract_endpoints(tmp_path):
    path = tmp_path / "frozen.json"
    save_frozen(path, {1900, 2100})
    assert load_frozen(path) == {1900, 2100}


def test_missing_output_does_not_persist_freeze(tmp_path):
    frozen = tmp_path / "frozen.json"
    with pytest.raises(SystemExit) as error:
        main(["--source", "npb_calendar", "--month-key", MONTH_KEY, "--years", "2026", "--cache", str(tmp_path / "cache"),
              "--frozen", str(frozen), "--freeze", "2026"])
    assert error.value.code == 2
    assert not frozen.exists()


def test_reversed_year_range_does_not_persist_freeze(tmp_path):
    frozen = tmp_path / "frozen.json"
    with pytest.raises(SystemExit) as error:
        main(["--source", "npb_calendar", "--month-key", MONTH_KEY, "--years", "2027-2026", "--cache", str(tmp_path / "cache"),
              "--frozen", str(frozen), "--freeze", "2026", "--out", str(tmp_path / "games.jsonl"), "--offline"])
    assert error.value.code == 2
    assert not frozen.exists()


@pytest.mark.parametrize("wait", ["-1", "nan", "inf"])
def test_invalid_wait_rejected_before_plan_or_state_write(tmp_path, wait):
    frozen = tmp_path / "frozen.json"
    with pytest.raises(SystemExit) as error:
        main(["--source", "npb_calendar", "--month-key", MONTH_KEY, "--years", "2026", "--cache", str(tmp_path / "cache"),
              "--frozen", str(frozen), "--freeze", "2026", "--wait", wait, "--plan"])
    assert error.value.code == 2
    assert not frozen.exists()


def test_plan_counts_actual_request_headers_and_sleeps(tmp_path, monkeypatch):
    cache = Cache(tmp_path / "cache")
    pages = [("2025_03", "https://example.test/old", "2025"),
             ("2026_03", "https://example.test/etag", "2026"),
             ("2026_04", "https://example.test/not-found", "2026"),
             ("2026_05", "https://example.test/new", "2026")]
    cache.put(*pages[0], 200, b"old", {})
    cache.put(*pages[1], 200, b"etag", {"etag": '"v1"'})
    cache.put(*pages[2], 404, b"", {})
    plan = acquisition_plan(pages, cache, live={"2026"}, wait=2,
                            today=dt.date(2026, 5, 1), frozen=set(), future=[])
    calls, sleeps = [], []
    # Do not replace time.sleep process-wide: code_version() uses subprocess,
    # whose Python 3.11 polling also sleeps and must not pollute these counts.
    monkeypatch.setattr(queryu, "time", SimpleNamespace(sleep=sleeps.append))

    def handler(request):
        calls.append(request)
        return queryu.Response(304 if request.headers.get("If-None-Match") else 404)

    fetcher = PoliteFetcher(cache, wait=2, client=queryu.HandlerClient(handler))
    for key, url, group in pages:
        fetcher.get(key, url, group, live=group == "2026")
    conditional = sum(bool(r.headers.get("If-None-Match") or r.headers.get("If-Modified-Since")) for r in calls)
    assert plan["cached"] == 1
    assert plan["conditional"] == conditional == 1
    assert plan["unconditional"] == 1
    assert plan["new"] == 1
    assert plan["requests"] == len(calls) == 3
    assert plan["gaps"] == len(sleeps) == 2
    assert plan["estimated_wait_seconds"] == sum(sleeps) == 4


@pytest.mark.parametrize("count", [0, 1, 2])
def test_plan_wait_boundaries(tmp_path, count):
    pages = [(str(i), "https://example.test/", "2026") for i in range(count)]
    plan = acquisition_plan(pages, Cache(tmp_path), live=set(), wait=3,
                            today=dt.date(2026, 1, 1), frozen=set(), future=[])
    assert plan["requests"] == count
    assert plan["estimated_wait_seconds"] == 3 * max(0, count - 1)


def test_offline_plan_has_no_http_or_sleep_and_reports_missing(tmp_path, monkeypatch, capsys):
    cache = Cache(tmp_path / "cache")
    cache.put("2026_03", "https://example.test/march", "2026", 200, b"cached", {"etag": '"v1"'})
    monkeypatch.setattr(queryu, "UrllibClient", lambda **kw: pytest.fail("offline plan created a client"))
    assert main(["--source", "npb_calendar", "--month-key", MONTH_KEY, "--years", "2026", "--cache", str(cache.root),
                 "--frozen", str(tmp_path / "frozen.json"), "--today", "2026-04-01", "--offline", "--plan"]) == 0
    output = capsys.readouterr().out
    assert "キャッシュ済み（再確認しない）: 1" in output
    assert "条件付きGET: 0" in output
    assert "オフラインで不足するページ: 1" in output
    assert "待ち時間の見積もり: 0" in output


@pytest.mark.parametrize("today,kept", [("2026-12-31", ["2026_12"]), ("2027-01-01", ["2026_12", "2027_01"])])
def test_future_filter_at_year_boundary_keeps_non_month_keys(today, kept):
    pages = [(key, "u", key[:4]) for key in ["2026_12", "2027_01", "2027_03", "2027_c"]]
    actual, future = queryu.split_future_months(pages, dt.date.fromisoformat(today), MONTH_KEY)
    assert [p[0] for p in actual] == [*kept, "2027_c"]
    assert len(actual) + len(future) == len(pages)


# ──── single file: scripts/build_single_file.py の自己完結エントリ ─────────────────────────────────────────────────

def test_single_file_help_and_cache_in_isolation(tmp_path):
    output = tmp_path / "queryu.py"
    built = run_cli(ROOT / "scripts/build_single_file.py", str(output))
    assert built.returncode == 0, built.stderr
    result = subprocess.run([sys.executable, "-I", str(output), "--help"], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "--source" in result.stdout
    spec = importlib.util.spec_from_file_location("single_queryu", output)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cache = module.Cache(tmp_path / "cache")
    assert cache.latest() == {}


def test_single_file_missing_blueprobe_is_explained(tmp_path):
    output = tmp_path / "queryu.py"
    built = run_cli(ROOT / "scripts/build_single_file.py", str(output))
    assert built.returncode == 0, built.stderr
    result = subprocess.run([sys.executable, "-I", str(output), "--source", "example", "--years", "2024",
                             "--cache", str(tmp_path / "cache"), "--plan"], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 2
    assert "BlueProbe" in result.stderr
    assert "Traceback" not in result.stderr


def test_single_file_offline_plan_with_blueprobe(tmp_path):
    import blueprobe
    import npb_calendar
    output = tmp_path / "queryu.py"
    built = run_cli(ROOT / "scripts/build_single_file.py", str(output))
    assert built.returncode == 0, built.stderr
    for module in (blueprobe, npb_calendar):
        source = Path(module.__file__)
        shutil.copy2(source, tmp_path / source.name)
    result = subprocess.run([sys.executable, "-I", str(output), "--source", "npb_calendar", "--years", "2024",
                             "--cache", str(tmp_path / "cache"), "--plan", "--offline"], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "オフラインで不足するページ: 9" in result.stdout
