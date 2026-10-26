"""research/epsilon-generality/ の物理量の回（eps_generality.py の --profile、fetch_physical.py）の確認。

SYNTHETIC: 小さな合成の入力（実データではない）で、日次の刻み・プロファイル・値の単位の報告・変換・固定したハッシュの確認・
README の登録内容との一致を確かめる。結論には使わない。ネットワークは使わない。
"""
import csv
import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"


def load(name):
    spec = importlib.util.spec_from_file_location(name, DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gen = load("eps_generality")
fp = load("fetch_physical")
ph = load("posthoc_scale_tolerance")
sa, trial = gen.load_modules(ROOT)
COLS = fp.COLS


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    return path


def vrows(n, variable="physical:temp_max", country="Seattle", start=(2012, 1, 1), values=None, source="https://github.com/x/y@abcdefg (data/weather.csv)"):
    from datetime import date, timedelta
    d0 = date(*start)
    return [{"country": country, "date": (d0 + timedelta(days=i)).isoformat(), "year": str(d0.year), "variable": variable,
             "value": str(values[i] if values else float(i + 1)), "unit": "degC", "source": source, "note": "", "estimated_value": ""}
            for i in range(n)]


def wave(n, phase, decay=0.0, period=1.0):
    return [3.0 + 2.0 * math.exp(-decay * (i / (n - 1))) * math.cos(2 * math.pi * (i / (n - 1)) / period + phase) + 0.001 * ((i * 7) % 5)
            for i in range(n)]


# ---- 日次の刻み ---------------------------------------------------------------------------------------------------------
def test_day_index_counts_consecutive_days_across_month_and_year_ends_and_validates():
    assert gen.day_index("2020-03-01") - gen.day_index("2020-02-29") == 1
    assert gen.day_index("2021-01-01") - gen.day_index("2020-12-31") == 1
    assert gen.day_index("2020-03-01") - gen.day_index("2020-01-31") == 30
    assert gen.day_text(gen.day_index("2012-01-01")) == "2012-01-01"
    for bad in ("2020-1-1", "20200101", "2020-02-30", "2020-13-01", "2020-00-10"):
        with pytest.raises(ValueError):
            gen.day_index(bad)
    assert gen.CADENCE["month"]["index"] is gen.month_index and gen.CADENCE["day"]["index"] is gen.day_index


def test_read_series_takes_the_prefix_and_the_cadence_and_the_default_is_still_staple_by_month(tmp_path):
    rows = vrows(5) + vrows(1, variable="staple_price:rice", country="AAA") + vrows(3, variable="physical:wind_speed")
    p = write_rows(tmp_path / "s.csv", rows)
    s = gen.read_series(p, "physical:", "day")
    assert sorted(k[1] for k in s) == ["physical:temp_max", "physical:wind_speed"]
    assert sorted(len(v) for v in s.values()) == [3, 5]
    only = gen.read_series(p)                                   # 既定 = staple_price:、月の刻み
    assert list(only) == [("AAA", "staple_price:rice", "degC", "https://github.com/x/y@abcdefg (data/weather.csv)", "")]
    assert list(only.values())[0] == {gen.month_index("2012-01-01"): 1.0}


def test_read_series_stops_on_a_repeated_day_and_names_the_unit(tmp_path):
    dup = vrows(3) + [dict(vrows(1)[0])]
    with pytest.raises(ValueError, match="同じ日が 2 つある"):
        gen.read_series(write_rows(tmp_path / "a.csv", dup), "physical:", "day")
    with pytest.raises(ValueError, match="同じ月が 2 つある"):
        gen.read_series(write_rows(tmp_path / "b.csv", dup), "physical:", "month")
    with pytest.raises(ValueError, match="有限でない"):
        gen.read_series(write_rows(tmp_path / "c.csv", vrows(3, values=["1", "inf", "3"])), "physical:", "day")


def test_tile_labels_a_window_by_its_first_day_and_does_not_cross_a_missing_day():
    series = {"k": {gen.day_index("2012-01-30") + i: float(i) for i in range(6)} | {gen.day_index("2012-02-10") + i: float(i) for i in range(4)}}
    w = gen.tile(series, 3, gen.day_text)
    assert [(x["start"], x["values"]) for x in w] == [("2012-01-30", [0.0, 1.0, 2.0]), ("2012-02-02", [3.0, 4.0, 5.0]),
                                                     ("2012-02-10", [0.0, 1.0, 2.0])]
    assert gen.tile(series, 3)[0]["start"] == gen.month_text(gen.day_index("2012-01-30"))      # 既定は月の書き方


def test_source_group_names_for_the_physical_files():
    assert [gen.source_group(u) for u in (
        "https://github.com/vega/vega-datasets@5448e25 (data/weather.csv)", "https://github.com/vega/vega-datasets@5448e25 (data/co2-concentration.csv)",
        "https://github.com/datasets/global-temp@44571fe (data/monthly.csv)", "https://github.com/tezamo/FPMA (x)")] == [
        "NOAA-weather", "Scripps-CO2", "global-temp", "FPMA"]


# ---- 値の単位を変えたとき ------------------------------------------------------------------------------------------------
def three_windows_and_a_constant():
    xs = [i / 23 for i in range(24)]
    wins = [{"key": "k", "start": "2020-01", "values": wave(24, p)} for p in (0.1, 0.7, 1.9)]
    wins.append({"key": "k", "start": "2022-01", "values": wave(24, 0.3, decay=3.0, period=0.5)})
    wins.append({"key": "k", "start": "2024-01", "values": [4.0] * 24})
    return gen.make_bases(sa, trial, xs), wins


def test_scale_summary_has_one_entry_per_scale_skips_constant_windows_and_scale_one_is_the_reference():
    bases, wins = three_windows_and_a_constant()
    out = gen.scale_summary(sa, bases, wins)
    assert list(out) == ["1e-06", "0.001", "1", "1000", "1e+06"] and gen.SCALES == (1e-6, 1e-3, 1.0, 1e3, 1e6)
    assert {d["units"] for d in out.values()} == {4}
    ref = [gen.fit_row(sa, bases, gen.normalize(w["values"])[1], gen.PRIMARY_TAU) for w in wins[:4]]
    nb = sum(r["boundary"] for r in ref)
    one = out["1"]
    assert one["boundary"] == nb and 1 <= nb <= 3
    assert one["forms_changed"] == 0 and one["boundary_flag_changed"] == 0 and one["at_start_changed"] == 0
    assert one["eps_wave_kept"] == nb and one["coefficient_n"] == nb and one["coefficient_max_dev"] == 0.0


def test_scale_summary_counts_each_kind_of_change_separately(monkeypatch):
    bases, wins = three_windows_and_a_constant()
    wins = wins[:3]
    k6 = gen.ekey(1e-6)
    calls = []

    def scale_of(tau):
        return min(gen.SCALES, key=lambda s: abs(tau - gen.PRIMARY_TAU * s))

    def fake(sa_, b, ys, tau):
        f, idx = scale_of(tau), len(calls) % 3                    # 倍率ごとに窓 0, 1, 2 の順に呼ばれる
        calls.append(1)
        assert max(ys) - min(ys) == pytest.approx(gen.SCALE * f)        # y にも τ と同じ倍率がかかっている
        row = {"decay": 0.0, "period": 1.0, "rmse": 0.0, "limit": None, "settle_x": None, "boundary": True}
        for e in gen.EPS:
            row[gen.ekey(e)] = {"decay": e, "period": 1.0, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0,
                                "coefficient": 2.0 if f == 1.0 else 2.0 * (1 + 0.1 * (idx + 1)), "at_start": f == 1e3}
        if f == 1.0 and idx == 2:
            row.update(decay=0.5, boundary=False)
            row[k6]["decay"] = 0.5                                 # 境界でない単位では ε の波は選ばれない
        if f == 1e-6:
            row["period"] = 0.5                                    # 周期だけが変わる
        if f == 1e-3:
            row.update(decay=0.5, boundary=False)                  # 今のコードの式が変わる（境界でなくなる）
        if f == 1e6 and idx == 0:
            row[k6]["decay"] = 0.5                                 # ε の波が残らない
        return row
    monkeypatch.setattr(gen, "fit_row", fake)
    out = gen.scale_summary(sa, bases, wins)
    cols = ("units", "boundary", "forms_changed", "boundary_flag_changed", "eps_wave_kept", "at_start_changed", "coefficient_max_dev", "coefficient_n")
    want = {"1e-06": (3, 3, 3, 1, 2, 0, 0.1 * 2, 2),            # 比べた単位は w0, w1。ずれは 2.2/2.0, 2.4/2.0 → 0.1, 0.2
            "0.001": (3, 0, 2, 2, 2, 0, None, 0),
            "1": (3, 2, 0, 0, 2, 0, 0.0, 2),
            "1000": (3, 3, 1, 1, 2, 2, 0.1 * 2, 2),
            "1e+06": (3, 3, 1, 1, 1, 0, 0.1 * 2, 2)}
    assert list(out) == list(want)
    for k, w in want.items():
        got = tuple(out[k][c] for c in cols)
        assert got == pytest.approx(w) if None not in w else got == w, k
    assert len(calls) == 15


# ---- プロファイル --------------------------------------------------------------------------------------------------------
def daily_csv(tmp_path):
    rows = []
    for j in range(3):
        rows += vrows(60, variable=f"physical:v{j}", values=wave(60, 0.3 * j))
    rows += vrows(1, variable="staple_price:rice", country="AAA")
    return write_rows(tmp_path / "d.csv", rows)


def test_cli_physical_daily_profile_writes_the_report_without_synthetic_series_and_is_byte_reproducible(tmp_path):
    p = daily_csv(tmp_path)
    o1, o2 = tmp_path / "o1", tmp_path / "o2"
    for o in (o1, o2):
        assert gen.main(["--csv", str(p), "--outdir", str(o), "--repo", str(ROOT), "--profile", "physical-daily"]) == 0
    names = sorted(x.name for x in o1.iterdir())
    assert names == ["eps_generality.json", "eps_generality.md", "eps_generality_units_n24.jsonl"]
    for n in names:
        assert (o1 / n).read_bytes() == (o2 / n).read_bytes()
    res = json.loads((o1 / "eps_generality.json").read_text(encoding="utf-8"))
    assert res["profile"] == "physical-daily" and res["control"]["pass"] and res["repeat_identical"]
    assert [res["sets"][n]["windows"] for n in ("12", "24", "48")] == [15, 6, 3]          # staple の行は読まない
    assert res["synthetic_forms"] == {} and not [c for c in res["criteria"] if c["id"] == "C5"]
    assert [c["set"] for c in res["criteria"] if c["id"] == "C1"] == [f"N={n}" for n in (12, 24, 48) for _ in range(3)]
    assert list(res["scales"]) == ["1e-06", "0.001", "1", "1000", "1e+06"] and res["scales"]["1"]["units"] == 6
    units = [json.loads(x) for x in (o1 / "eps_generality_units_n24.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(units) == 6 and [u["start"] for u in units[:2]] == ["2012-01-01", "2012-01-25"] and {u["source"] for u in units} == {"NOAA-weather"}
    md = (o1 / "eps_generality.md").read_text(encoding="utf-8")
    assert "## 窓（物理量の日次）" in md and "| 24 日 |" in md and "| 24 か月 |" not in md
    assert "## 値の単位を変えたとき" in md and "合成の系列で今のコードが選んだ式" not in md
    assert "確かめられた" not in md.replace("「確かめられた」とは書かない", "")


def test_render_summary_names_the_physical_label_and_leaves_out_the_synthetic_series():
    res = {"control": {"eps0_basis_identical": {"24": True}, "pass": True}, "repeat_identical": True, "profile": "physical-daily", "tau": {},
           "synthetic_forms": {}, "criteria": [gen._v("C1", "N=24", "テスト", 1.0, 1.0, ">=", True)],
           "scales": {"1": {"units": 5, "boundary": 2, "forms_changed": 0, "boundary_flag_changed": 0, "eps_wave_kept": 2, "at_start_changed": 0,
                            "coefficient_max_dev": 0.0, "coefficient_n": 2}}}
    res["sets"] = {str(n): {"windows": 1, "constant_windows": 0, "series": 1, "by_source": {}, "stats": {
        "units": 1, "boundary": 1, "boundary_share": 1.0, "coefficient_range_eps6": None,
        "at_start": {gen.ekey(e): 0 for e in gen.EPS}}} for n in gen.LENGTHS}
    md = gen.render(res)
    tail = md.split("## まとめ")[1]
    assert "物理量の日次で**矛盾する材料はなかった**" in tail and "合成の系列" not in tail
    assert "| 12 日 |" in md and "| 1 | 5 | 2 | 0 | 0 | 2 | 0 | 0 | 2 |" in md
    res["profile"] = "staple"
    del res["scales"]
    assert "主食価格の月次と合成の系列で**矛盾する材料はなかった**" in gen.render(res).split("## まとめ")[1]


def test_cli_physical_monthly_profile_uses_months(tmp_path):
    rows = []
    y, m = 2000, 1
    vals = wave(48, 0.2)
    for i in range(48):
        rows.append({"country": "Global", "date": f"{y:04d}-{m:02d}-01", "year": str(y), "variable": "physical:temp_anomaly", "value": str(vals[i]),
                     "unit": "degC (anomaly)", "source": "https://github.com/datasets/global-temp@44571fe (data/monthly.csv)", "note": "GCAG",
                     "estimated_value": ""})
        m += 1
        if m == 13:
            y, m = y + 1, 1
    p = write_rows(tmp_path / "m.csv", rows)
    assert gen.main(["--csv", str(p), "--outdir", str(tmp_path / "o"), "--repo", str(ROOT), "--profile", "physical-monthly"]) == 0
    res = json.loads((tmp_path / "o" / "eps_generality.json").read_text(encoding="utf-8"))
    assert [res["sets"][n]["windows"] for n in ("12", "24", "48")] == [4, 2, 1]
    assert list(res["sets"]["24"]["by_source"]) == ["global-temp"] and res["sets"]["24"]["by_source"]["global-temp"]["units"] == 2
    md = (tmp_path / "o" / "eps_generality.md").read_text(encoding="utf-8")
    assert "## 窓（物理量の月次）" in md and "| 24 か月 |" in md


def test_the_default_staple_profile_adds_no_keys_and_keeps_the_synthetic_part(tmp_path):
    rows = []
    for j in range(2):
        vals = wave(48, 0.3 * j)
        rows += [{"country": "AAA", "date": f"{2020 + i // 12}-{i % 12 + 1:02d}-01", "year": str(2020 + i // 12), "variable": "staple_price:rice",
                  "value": str(vals[i]), "unit": "USD per kg", "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}",
                  "estimated_value": ""} for i in range(48)]
    rows += vrows(5)                                           # physical: の行は読まない
    p = write_rows(tmp_path / "s.csv", rows)
    assert gen.main(["--csv", str(p), "--outdir", str(tmp_path / "o"), "--repo", str(ROOT)]) == 0
    res = json.loads((tmp_path / "o" / "eps_generality.json").read_text(encoding="utf-8"))
    assert list(res) == ["spec_version", "seed", "control", "sets", "criteria", "synthetic_forms", "tau", "repeat_identical"]
    assert [res["sets"][n]["windows"] for n in ("12", "24", "48")] == [8, 4, 2]
    assert len(res["synthetic_forms"]) == len(gen.SYNTH) and any(c["id"] == "C5" for c in res["criteria"])


def test_profiles_are_registered_as_the_readme_says():
    assert sorted(gen.PROFILES) == ["physical-daily", "physical-monthly", "staple"]
    assert gen.PROFILES["staple"] == {"prefix": "staple_price:", "cadence": "month", "label": "主食価格の月次", "synth": True, "scales": False}
    assert gen.PROFILES["physical-monthly"] == {"prefix": "physical:", "cadence": "month", "label": "物理量の月次", "synth": False, "scales": True}
    assert gen.PROFILES["physical-daily"] == {"prefix": "physical:", "cadence": "day", "label": "物理量の日次", "synth": False, "scales": True}


# ---- fetch_physical.py -------------------------------------------------------------------------------------------------
WEATHER = "location,date,precipitation,temp_max,temp_min,wind,weather\nSeattle,2012-01-02,10.9,10.6,2.8,4.5,rain\nSeattle,2012-01-01,0.0,12.8,5.0,4.7,drizzle\n"
CO2 = "Date,CO2,adjusted CO2\n1958-03-01,315.70,314.44\n1958-04-01,317.46,315.16\n"
GT = "Source,Year,Mean\nGISTEMP,1880-01,-0.1\nGCAG,1850-02,-0.3604\nGCAG,1850-01,-0.7337\n"


def fixture_pins(raw_dir, texts=None):
    texts = texts or {"weather": WEATHER, "co2": CO2, "global-temp": GT}
    pins = {}
    for i, (name, text) in enumerate(texts.items()):
        (raw_dir / f"{name}.csv").write_text(text, encoding="utf-8")
        pins[name] = {"repo": f"o/r{i}", "commit": f"{i}abcdef0123456789abcdef0123456789abcdef"[:40].ljust(40, "0"), "path": f"data/{name}.csv",
                      "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "license": "L", "origin": "O"}
    return pins


def test_build_converts_the_three_files_into_sorted_vertical_rows(tmp_path):
    pins = fixture_pins(tmp_path)
    b = fp.build(tmp_path, pins)
    assert len(b["daily"]) == 8 and len(b["monthly"]) == 4 + 3
    d = b["daily"]
    assert [(r["variable"], r["date"]) for r in d[:2]] == [("physical:precipitation", "2012-01-01"), ("physical:precipitation", "2012-01-02")]   # 日付順
    assert {(r["variable"], r["unit"]) for r in d} == {("physical:precipitation", "mm"), ("physical:temp_max", "degC"),
                                                         ("physical:temp_min", "degC"), ("physical:wind_speed", "m/s")}
    r0 = next(r for r in d if r["variable"] == "physical:wind_speed" and r["date"] == "2012-01-01")
    assert r0 == {"country": "Seattle", "date": "2012-01-01", "year": "2012", "variable": "physical:wind_speed", "value": "4.7", "unit": "m/s",
                  "source": "https://github.com/o/r0@0abcdef (data/weather.csv)", "note": "", "estimated_value": ""}
    m = b["monthly"]
    gt = [r for r in m if r["variable"] == "physical:temp_anomaly"]
    assert [(r["note"], r["date"], r["value"]) for r in gt] == [("GCAG", "1850-01-01", "-0.7337"), ("GCAG", "1850-02-01", "-0.3604"),
                                                                 ("GISTEMP", "1880-01-01", "-0.1")]
    assert {r["unit"] for r in gt} == {"degC (anomaly)"} and {r["country"] for r in gt} == {"Global"}
    co2 = [r for r in m if r["variable"].startswith("physical:co2")]
    assert sorted({r["variable"] for r in co2}) == ["physical:co2", "physical:co2_seasonally_adjusted"] and {r["unit"] for r in co2} == {"ppm"}
    assert {(r["variable"], r["date"]): r["value"] for r in co2 if r["date"] == "1958-03-01"} == {
        ("physical:co2", "1958-03-01"): "315.70", ("physical:co2_seasonally_adjusted", "1958-03-01"): "314.44"}
    assert [r["country"] for r in m] == sorted(r["country"] for r in m)


def test_build_stops_when_a_file_differs_from_the_pinned_hash(tmp_path):
    pins = fixture_pins(tmp_path)
    (tmp_path / "co2.csv").write_text(CO2.replace("315.70", "315.71"), encoding="utf-8")
    with pytest.raises(ValueError, match="co2: sha256 が固定した値と違う"):
        fp.build(tmp_path, pins)


@pytest.mark.parametrize("name,text,msg", [
    ("weather", WEATHER.replace("10.9", ""), "値が空"),
    ("weather", WEATHER.replace("temp_min,wind", "tmin,wind"), "列が足りない"),
    ("co2", CO2.replace("315.70", "nan"), "有限でない"),
    ("global-temp", GT.replace("-0.1\n", "inf\n"), "有限でない"),
    ("global-temp", GT.replace("Source,", "Src,"), "列が足りない")])
def test_build_stops_on_blank_missing_or_non_finite_values(tmp_path, name, text, msg):
    texts = {"weather": WEATHER, "co2": CO2, "global-temp": GT} | {name: text}
    pins = fixture_pins(tmp_path, texts)
    with pytest.raises(ValueError, match=msg):
        fp.build(tmp_path, pins)


def test_main_writes_both_csvs_and_a_manifest_that_matches_the_files_and_the_harness_can_read_them(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    pins = fixture_pins(raw)
    monkeypatch.setattr(fp, "PINS", pins)
    out1, out2 = tmp_path / "o1", tmp_path / "o2"
    for o in (out1, out2):
        assert fp.main(["--raw-dir", str(raw), "--outdir", str(o)]) == 0
    names = sorted(x.name for x in out1.iterdir())
    assert names == ["physical_daily_vertical.csv", "physical_manifest.json", "physical_monthly_vertical.csv"]
    for n in names:
        assert (out1 / n).read_bytes() == (out2 / n).read_bytes()
    man = json.loads((out1 / "physical_manifest.json").read_text(encoding="utf-8"))
    for n in ("physical_daily_vertical.csv", "physical_monthly_vertical.csv"):
        data = (out1 / n).read_bytes()
        assert man["outputs"][n] == {"rows": data.count(b"\n") - 1, "sha256": hashlib.sha256(data).hexdigest()}
        assert b"\r" not in data
    assert set(man["inputs"]) == {"weather", "co2", "global-temp"} and man["inputs"]["co2"]["url"] == fp.raw_url(pins["co2"])
    s = gen.read_series(out1 / "physical_daily_vertical.csv", "physical:", "day")
    assert len(s) == 4 and all(len(v) == 2 for v in s.values())
    s = gen.read_series(out1 / "physical_monthly_vertical.csv", "physical:", "month")
    assert len(s) == 4 and sorted(len(v) for v in s.values()) == [1, 2, 2, 2]


def test_download_writes_only_files_whose_hash_matches_and_asks_the_pinned_urls(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    pins = fixture_pins(tmp_path / "src")
    bodies = {fp.raw_url(pins[n]): t.encode("utf-8") for n, t in (("weather", WEATHER), ("co2", CO2), ("global-temp", GT))}
    asked = []

    class Resp:
        def __init__(self, data):
            self.data = data

        def read(self):
            return self.data

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_open(url, timeout=None):
        asked.append(url)
        return Resp(bodies[url])
    monkeypatch.setattr(fp.urllib.request, "urlopen", fake_open)
    dest = tmp_path / "dl"
    fp.download(dest, pins)
    assert asked == [fp.raw_url(p) for p in pins.values()] and sorted(x.name for x in dest.iterdir()) == ["co2.csv", "global-temp.csv", "weather.csv"]
    bodies[fp.raw_url(pins["co2"])] = b"tampered"
    dest2 = tmp_path / "dl2"
    with pytest.raises(ValueError, match="co2: sha256 が固定した値と違う"):
        fp.download(dest2, pins)
    assert (dest2 / "weather.csv").exists() and not (dest2 / "co2.csv").exists() and not (dest2 / "global-temp.csv").exists()


def test_the_real_pins_are_well_formed():
    assert set(fp.PINS) == {"weather", "co2", "global-temp"}
    for name, p in fp.PINS.items():
        assert re.fullmatch(r"[0-9a-f]{40}", p["commit"]) and re.fullmatch(r"[0-9a-f]{64}", p["sha256"]), name
        assert p["license"] and p["origin"] and p["path"].startswith("data/") and "/" in p["repo"]
        assert fp.raw_url(p) == f"https://raw.githubusercontent.com/{p['repo']}/{p['commit']}/{p['path']}"
        assert fp.source_text(p) == f"https://github.com/{p['repo']}@{p['commit'][:7]} ({p['path']})"
    assert fp.PINS["weather"]["commit"] == fp.PINS["co2"]["commit"]


# ---- 事後: 値の単位と絶対値の許容（posthoc_scale_tolerance.py）------------------------------------------------------------
def synth_window(sid, i):
    spec = next(x for x in gen.SYNTH if x["id"] == sid)
    return {"key": "k", "start": "2020-01", "values": gen.synth_series(spec, i)}


def test_posthoc_unscaled_tolerance_moves_the_form_at_a_small_scale_and_a_scaled_tolerance_does_not():
    bases = gen.make_bases(sa, trial, [i / 23 for i in range(24)])
    wins = [synth_window("undamped_p1", 7), synth_window("damped_l1", 10)]       # 探して固定した窓（倍率 1e-6 で式が動く）
    old_tie = sa.EPS_WAVE_TIE
    for scale_tie, want_changed in ((False, 2), (True, 0)):
        with ph.patched(gen, sa, (1e-6, 1.0), scale_tie):
            out = gen.scale_summary(sa, bases, wins)
        assert out["1"]["forms_changed"] == 0 and out["1e-06"]["forms_changed"] == want_changed, scale_tie
        if scale_tie:
            assert out["1e-06"]["boundary_flag_changed"] == 0 and out["1e-06"]["coefficient_max_dev"] < 1e-9
    assert sa.EPS_WAVE_TIE == old_tie == ph.TIE


def test_posthoc_analyse_runs_the_unchanged_tolerance_first_and_the_scaled_one_second():
    series = {("k", f"physical:{i}", "u", "s", ""): {j: v for j, v in enumerate(synth_window(sid, k)["values"])}
              for i, (sid, k) in enumerate((("undamped_p1", 7), ("damped_l1", 10)))}
    res = ph.analyse(gen, sa, trial, series, "month")
    assert res["windows"] == 2 and res["n"] == 24
    assert res["tolerance_unchanged"]["1e-06"]["forms_changed"] == 2 and res["tolerance_scaled"]["1e-06"]["forms_changed"] == 0
    assert res["tolerance_unchanged"]["1"] == res["tolerance_scaled"]["1"]


def test_posthoc_patched_restores_everything_even_when_the_body_fails():
    old = (gen.SCALES, gen.fit_row, sa.EPS_WAVE_TIE)
    with pytest.raises(RuntimeError):
        with ph.patched(gen, sa, (0.5, 1.0), True):
            assert gen.SCALES == (0.5, 1.0) and gen.fit_row is not old[1]
            raise RuntimeError("x")
    assert (gen.SCALES, gen.fit_row, sa.EPS_WAVE_TIE) == old


def test_posthoc_patched_multiplies_the_tolerance_by_the_square_of_the_scale_only_while_fitting(monkeypatch):
    seen = []
    monkeypatch.setattr(gen, "fit_row", lambda sa_, b, ys, tau: seen.append((tau, sa_.EPS_WAVE_TIE)) or {"x": 1})
    for scale_tie in (True, False):
        seen.clear()
        with ph.patched(gen, sa, gen.SCALES, scale_tie):
            for f in (1e-3, 1.0, 1e3):
                assert gen.fit_row(sa, None, [0.0], gen.PRIMARY_TAU * f) == {"x": 1}
                assert sa.EPS_WAVE_TIE == ph.TIE                       # 当てはめの外では元の値
        want = [ph.TIE * f * f if scale_tie else ph.TIE for f in (1e-3, 1.0, 1e3)]
        assert [t for _, t in seen] == pytest.approx(want, rel=1e-9)
    assert sa.EPS_WAVE_TIE == ph.TIE and gen.fit_row is not None


def test_posthoc_cli_writes_both_variants_for_both_cadences_and_is_reproducible(tmp_path):
    monthly = write_rows(tmp_path / "m.csv", [dict(r, date=f"{2000 + i // 12}-{i % 12 + 1:02d}-01", variable="physical:temp_anomaly", note="GCAG")
                                               for i, r in enumerate(vrows(48, values=wave(48, 0.2)))])
    daily = write_rows(tmp_path / "d.csv", vrows(48, values=wave(48, 0.5)))
    outs = []
    for name in ("a", "b"):
        o = tmp_path / name
        assert ph.main(["--monthly-csv", str(monthly), "--daily-csv", str(daily), "--outdir", str(o), "--repo", str(ROOT)]) == 0
        outs.append(o)
    for n in ("posthoc_scale_tolerance.json", "posthoc_scale_tolerance.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes()
    res = json.loads((outs[0] / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))
    assert set(res) == {"monthly", "daily"} and all(res[k]["windows"] == 2 and res[k]["n"] == 24 for k in res)
    for k in res:
        for name in ("tolerance_unchanged", "tolerance_scaled"):
            assert list(res[k][name]) == ["1e-08", "1e-07", "1e-06", "1e-05", "0.0001", "0.001", "0.01", "1"]
            assert res[k][name]["1"]["forms_changed"] == 0 and res[k][name]["1"]["units"] == 2
    md = (outs[0] / "posthoc_scale_tolerance.md").read_text(encoding="utf-8")
    assert "## 月次（24 点の窓 2 個）" in md and "## 日次（24 点の窓 2 個）" in md and md.count("許容に倍率の2乗をかけた") == 2
    assert gen.SCALES == (1e-6, 1e-3, 1.0, 1e3, 1e6) and sa.EPS_WAVE_TIE == ph.TIE                      # 呼んだあとも元のまま


def test_posthoc_states_its_prediction_before_the_run_and_the_fine_scales():
    doc = ph.__doc__
    assert "予想（走らせる前に書く）" in doc and "(a)" in doc and "(b)" in doc and "EPS_WAVE_SOLVE" in doc
    assert ph.FINE == (1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1.0) and ph.TIE == 1e-12


# ---- README の登録内容との一致 --------------------------------------------------------------------------------------------
def test_readme_physical_section_states_the_pinned_inputs_the_scales_and_the_profiles():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    sec = text[text.index("## 物理量の確認（第 2 回）: 事前登録"):]
    for p in fp.PINS.values():
        for needle in (p["commit"], p["sha256"], p["path"], p["repo"]):
            assert needle in sec, needle
    for needle in ("SCALES = (1e-6, 1e-3, 1, 1e3, 1e6)", "`physical-monthly`", "`physical-daily`", "444 / 221 / 110", "968 / 480 / 240",
                   "13 / 2 / 0", "5,353 行", "11,688 行", "4f18c60d52e26f1ec84496619ee2aa656ae0e3994373064c8be78fd150ceefc9",
                   "1d1ea18b501abc473a9e27bc388a0433fb89551bbbcef396648c15f41caa9824", "tests/test_epsilon_generality_physical.py",
                   "基準は置かず、報告だけ", "矛盾する材料はなかった", "約 18% 未満", "results-physical/", "posthoc_scale_tolerance.py",
                   "走らせる前に", "EPS_WAVE_SOLVE", "直し方"):
        assert needle in sec, needle
    assert "98% 以上" in sec and "20 未満" in sec
    assert gen.CRIT["c1_eps3"] == 0.98 and gen.MIN_UNITS == 20                               # 第 1 回と同じ値のまま
