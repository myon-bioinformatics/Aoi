#!/usr/bin/env python3
"""物理量の公開データ（GitHub の固定コミットのファイル）を、eps_generality.py が読む縦持ちの CSV に直す（探索）。

README.md の「物理量の確認」に書いた 3 つのファイルだけを扱う。ファイルは固定したコミットと sha256 で指定し、違えば止まる。
結果（走らせたあとの数）は見ずに、走らせる前に決めた入力。ε の値には関わらない。

使い方（リポジトリの直下から）:
  uv run --locked python research/epsilon-generality/fetch_physical.py --raw-dir /tmp/physraw --outdir /tmp/physical --download
書き出すもの: physical_monthly_vertical.csv（CO2・全球気温偏差の月次）、physical_daily_vertical.csv（シアトル・ニューヨークの日次気象）、
physical_manifest.json（入力の URL・sha256、出力の行数・sha256）。--download を付けなければ、--raw-dir にあるファイルを読む。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import urllib.request
from pathlib import Path

COLS = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]

# ファイルは固定したコミット（git ls-remote で確かめたもの）と、そのファイルの sha256。ライセンスは各リポジトリの datapackage.json の記載のまま。
PINS = {
    "weather": {
        "repo": "vega/vega-datasets", "commit": "5448e25297c8f705be78e879d5423d55d04dc6f1", "path": "data/weather.csv",
        "sha256": "27219f1ca8dbd94c9b6f4b9f4f52ab2f1eb33dfdcf719cd9fc6481ed50b74549",
        "license": "other-pd（U.S. Government Dataset）", "origin": "NOAA Climate Data Online（シアトルとニューヨークの日次、2012〜2015）"},
    "co2": {
        "repo": "vega/vega-datasets", "commit": "5448e25297c8f705be78e879d5423d55d04dc6f1", "path": "data/co2-concentration.csv",
        "sha256": "c1a4a970864145940a28225cae288618b156cb32f9a2a1b6606ba7124134febb",
        "license": "CC-BY-4.0", "origin": "Scripps CO2 Program（マウナ・ロア、月次、1958〜2020）"},
    "global-temp": {
        "repo": "datasets/global-temp", "commit": "44571fe8c15e228c156bb19308e5ccc1e31cf9f7", "path": "data/monthly.csv",
        "sha256": "d61b268c8f4d1934c0a20297d4036a68f93a06f15442164637d3994c18a15186",
        "license": "CC-BY-4.0", "origin": "Source 列の GCAG と GISTEMP（全球の月次の気温偏差。上流は確かめていない）"},
}
# 単位は vega-datasets の説明（metric units）と NOAA の慣例からの想定で、確かめていない。ハーネスは値を正規化するので結果には響かない
WEATHER_VARS = {"precipitation": ("physical:precipitation", "mm"), "temp_max": ("physical:temp_max", "degC"),
                "temp_min": ("physical:temp_min", "degC"), "wind": ("physical:wind_speed", "m/s")}


def raw_url(pin: dict) -> str:
    return f"https://raw.githubusercontent.com/{pin['repo']}/{pin['commit']}/{pin['path']}"


def source_text(pin: dict) -> str:
    return f"https://github.com/{pin['repo']}@{pin['commit'][:7]} ({pin['path']})"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_hash(name: str, data: bytes, pins: dict) -> bytes:
    got = sha256_hex(data)
    if got != pins[name]["sha256"]:
        raise ValueError(f"{name}: sha256 が固定した値と違う（{got}）")
    return data


def download(raw_dir: Path, pins: dict = PINS) -> None:
    """固定した URL から取り、sha256 が合ったものだけを raw_dir/<名前>.csv に書く。"""
    raw_dir.mkdir(parents=True, exist_ok=True)
    for name, pin in pins.items():
        with urllib.request.urlopen(raw_url(pin), timeout=60) as r:
            data = check_hash(name, r.read(), pins)
        (raw_dir / f"{name}.csv").write_bytes(data)


def vrow(country: str, date: str, variable: str, value: str, unit: str, source: str, note: str = "") -> dict:
    if not math.isfinite(float(value)):
        raise ValueError(f"値が有限でない: {country} {date} {variable} {value!r}")
    return {"country": country, "date": date, "year": date[:4], "variable": variable, "value": value, "unit": unit,
            "source": source, "note": note, "estimated_value": ""}


def need(r: dict, cols: tuple, name: str) -> None:
    missing = [c for c in cols if r.get(c) in (None, "")]
    if missing:
        raise ValueError(f"{name}: 列が足りないか値が空: {missing} {r}")


def read_text(raw_dir: Path, name: str, pins: dict) -> str:
    return check_hash(name, (raw_dir / f"{name}.csv").read_bytes(), pins).decode("utf-8")


def convert_weather(text: str, source: str) -> list[dict]:
    out = []
    for r in csv.DictReader(text.splitlines()):
        need(r, ("location", "date") + tuple(WEATHER_VARS), "weather")
        out += [vrow(r["location"], r["date"], v, r[col], unit, source) for col, (v, unit) in WEATHER_VARS.items()]
    return out


def convert_co2(text: str, source: str) -> list[dict]:
    out = []
    for r in csv.DictReader(text.splitlines()):
        need(r, ("Date", "CO2", "adjusted CO2"), "co2")
        out.append(vrow("Mauna Loa", r["Date"], "physical:co2", r["CO2"], "ppm", source))
        out.append(vrow("Mauna Loa", r["Date"], "physical:co2_seasonally_adjusted", r["adjusted CO2"], "ppm", source))
    return out


def convert_global_temp(text: str, source: str) -> list[dict]:
    out = []
    for r in csv.DictReader(text.splitlines()):
        need(r, ("Source", "Year", "Mean"), "global-temp")
        out.append(vrow("Global", r["Year"] + "-01", "physical:temp_anomaly", r["Mean"], "degC (anomaly)", source, note=r["Source"]))
    return out


def build(raw_dir: Path, pins: dict = PINS) -> dict:
    """{"monthly": 行, "daily": 行}。行は (国, 変数, 注, 日付) の順に並べる。"""
    src = {k: source_text(p) for k, p in pins.items()}
    monthly = convert_co2(read_text(raw_dir, "co2", pins), src["co2"]) + convert_global_temp(read_text(raw_dir, "global-temp", pins), src["global-temp"])
    daily = convert_weather(read_text(raw_dir, "weather", pins), src["weather"])
    key = lambda r: (r["country"], r["variable"], r["note"], r["date"])        # noqa: E731
    return {"monthly": sorted(monthly, key=key), "daily": sorted(daily, key=key)}


def csv_bytes(rows: list[dict]) -> bytes:
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw-dir", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--download", action="store_true", help="固定した URL から --raw-dir に取る（sha256 が合ったものだけ書く）")
    args = ap.parse_args(argv)
    if args.download:
        download(args.raw_dir, PINS)
    built = build(args.raw_dir, PINS)
    args.outdir.mkdir(parents=True, exist_ok=True)
    manifest = {"inputs": {k: {"url": raw_url(p), "sha256": p["sha256"], "license": p["license"], "origin": p["origin"]} for k, p in PINS.items()},
                "outputs": {}}
    for kind, rows in built.items():
        name = f"physical_{kind}_vertical.csv"
        data = csv_bytes(rows)
        (args.outdir / name).write_bytes(data)
        manifest["outputs"][name] = {"rows": len(rows), "sha256": sha256_hex(data)}
    (args.outdir / "physical_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"書き出し: {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
