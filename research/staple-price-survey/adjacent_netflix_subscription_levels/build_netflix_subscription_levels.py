#!/usr/bin/env python3
"""Build adjacent_netflix_subscription_levels vertical CSV.

Sources (LCU absolute subscription prices; no FX; no gap-fill; estimated_value empty):
  1. tompec/netflix-prices dated JSON 2023-01-07 … 2026-09-28 (primary history)
  2. fromabroad.org 2020-03-10 LCU table (curated unambiguous native-currency rows)
  3. apoorvgupta25/netflix-prices Kaggle CSV — Comparitech Dec-2021 LCU snapshot
     (currency must match tompec billing currency for that ISO3, or RUS/RUB)

Country universe = Big Mac ISO3 (countries_iso3.txt).
"""
from __future__ import annotations

import csv
import gzip
import json
import re
from collections import Counter
from pathlib import Path

try:
    import pycountry
except ImportError:  # pragma: no cover
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pycountry"])
    import pycountry

ROOT = Path(__file__).resolve().parent
SURVEY = ROOT.parent
AOI_RAW = Path(
    "/workspace/aoi-phase2/raw/numeraire_hist_2026-10-25/tompec-netflix-prices"
)
PRICES_ALL = Path(
    "/workspace/aoi-phase2/raw/numeraire_hist_2026-10-25/prices_all.csv"
)
PRE2023_RAW = Path(
    "/workspace/aoi-phase2/raw/numeraire_hist_2026-10-25/netflix_pre2023"
)
OUT_CSV = ROOT / "adjacent_netflix_subscription_levels_vertical.csv"
OUT_GZ = ROOT / "adjacent_netflix_subscription_levels_vertical.csv.gz"
STATS = ROOT / "_build_stats.json"
CROSS = ROOT / "_crosscheck_burgerparity.json"
COLS = [
    "country",
    "date",
    "year",
    "variable",
    "value",
    "unit",
    "source",
    "note",
    "estimated_value",
]
SOURCE_TOMPEC = (
    "https://github.com/tompec/netflix-prices "
    "(data/*.json; clone efa54e3 2026-09-28; retrieved 2026-10-25 Asia/Tokyo)"
)
NOTE_TOMPEC = (
    "tompec community scrape of Netflix list prices by plan; "
    "LCU as published; null plans omitted; "
    "source price_usd not loaded (no FX lane); "
    "retrieved 2026-10-25 Asia/Tokyo"
)
SOURCE_FROMABROAD = (
    "https://fromabroad.org/netflix/a-study-on-the-netflix-price-differences-"
    "between-countries-and-how-to-get-netflix-70-cheaper/ "
    "(2020-03-10 LCU table; curated native-currency rows; "
    "retrieved 2026-10-25 Asia/Tokyo)"
)
NOTE_FROMABROAD = (
    "fromabroad.org March 2020 LCU table; unambiguous native-currency rows only; "
    "skipped EUR-mislabeled (TR/EG), ARS-mislabeled (EC), incomplete TH, "
    "euro-area members (BM uses EUZ); retrieved 2026-10-25 Asia/Tokyo"
)
SOURCE_APOORV = (
    "https://www.kaggle.com/datasets/apoorvgupta25/netflix-prices "
    "(Netflix Prices.csv; Comparitech Dec-2021 LCU snapshot; "
    "zip mtime 2021-12-28; retrieved 2026-10-25 Asia/Tokyo)"
)
NOTE_APOORV = (
    "Comparitech Dec-2021 LCU via apoorvgupta25 Kaggle mirror; "
    "currency matched to tompec billing currency for ISO3 "
    "(RUS/RUB accepted though absent from tompec); "
    "dash Mobile omitted; retrieved 2026-10-25 Asia/Tokyo"
)
PLAN_ORDER = [
    "mobile",
    "basic_with_ads",
    "basic",
    "standard_with_ads",
    "standard",
    "premium",
]

# Currency-name → ISO4217 (Apoorv CSV). Ambiguous Krona/Krone resolved by ISO2.
CURRENCY_NAME_TO_CODE = {
    "Arab Emirates Dirham": "AED",
    "Argentine Peso": "ARS",
    "Australian Dollar": "AUD",
    "Brazilian Real": "BRL",
    "British Pound": "GBP",
    "Canadian dollars": "CAD",
    "Chilean Peso": "CLP",
    "Colombian Peso": "COP",
    "Czech Crowns": "CZK",
    "Danish Krone": "DKK",
    "Egyptian Pound": "EGP",
    "Euro": "EUR",
    "Hong Kong Dollar": "HKD",
    "Hungarian Forint": "HUF",
    "Indian Rupee": "INR",
    "Indonesian Rupiah": "IDR",
    "Israeli Shekel": "ILS",
    "Japanese Yen": "JPY",
    "Kenyan Shilling": "KES",
    "Korean Won": "KRW",
    "Malaysian Ringgit": "MYR",
    "Mexican Peso": "MXN",
    "Moroccan Dirham": "MAD",
    "New Taiwan Dollar": "TWD",
    "New Zealand Dollar": "NZD",
    "Nigerian Naira": "NGN",
    "Pakistani Rupee": "PKR",
    "Peruvian Sole": "PEN",
    "Philippine Peso": "PHP",
    "Polish Zloty": "PLN",
    "Russian Ruble": "RUB",
    "Saudi Riyal": "SAR",
    "Singapore Dollar": "SGD",
    "South African Rand": "ZAR",
    "Swiss Franc": "CHF",
    "Thai Baht": "THB",
    "Turkish Lira": "TRY",
    "United States Dollar": "USD",
    "Vietnamese Dong": "VND",
}


def iso2_to_iso3(cc: str) -> str | None:
    c = pycountry.countries.get(alpha_2=cc)
    return c.alpha_3 if c else None


def load_bm_iso3() -> set[str]:
    return set((SURVEY / "countries_iso3.txt").read_text().split())


def iter_snapshots(data_dir: Path):
    for path in sorted(data_dir.glob("*.json")):
        if path.name == "latest.json":
            continue
        yield path.stem, json.loads(path.read_text(encoding="utf-8"))


def tompec_currency_by_iso3(bm: set[str]) -> dict[str, str]:
    """Billing currency per BM ISO3 from earliest tompec snapshot (validation key)."""
    out: dict[str, str] = {}
    data_dir = AOI_RAW / "data"
    for _date, payload in iter_snapshots(data_dir):
        for entry in payload:
            iso3 = iso2_to_iso3(entry["country_code"])
            if iso3 in bm and iso3 not in out:
                cur = entry.get("currency") or ""
                if cur:
                    out[iso3] = cur
        if len(out) >= len(bm) - 3:  # CHN/EUZ/RUS often missing
            break
    return out


def parse_price(raw: str | float | int | None) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    if not s or s == "-":
        return None
    s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def append_plan_row(
    rows: list[dict],
    seen: set[tuple],
    *,
    iso3: str,
    date: str,
    plan: str,
    price: float,
    currency: str,
    source: str,
    note: str,
    plan_counts: Counter,
    iso_counts: Counter,
) -> None:
    variable = f"netflix:{plan}"
    key = (iso3, date, variable)
    if key in seen:
        return
    seen.add(key)
    rows.append(
        {
            "country": iso3,
            "date": date,
            "year": int(date[:4]),
            "variable": variable,
            "value": price,
            "unit": f"{currency} per monthly subscription",
            "source": source,
            "note": note + f"; plan={plan}; currency={currency}",
            "estimated_value": "",
        }
    )
    plan_counts[plan] += 1
    iso_counts[iso3] += 1


def build_tompec(
    bm: set[str],
    rows: list[dict],
    seen: set[tuple],
    plan_counts: Counter,
    iso_counts: Counter,
) -> list[str]:
    data_dir = AOI_RAW / "data"
    if not data_dir.is_dir():
        raise SystemExit(f"missing tompec data dir: {data_dir}")
    snapshot_dates: list[str] = []
    unmapped: Counter = Counter()
    skipped_non_bm: Counter = Counter()
    for date, payload in iter_snapshots(data_dir):
        snapshot_dates.append(date)
        for entry in payload:
            iso3 = iso2_to_iso3(entry["country_code"])
            if iso3 is None:
                unmapped[entry["country_code"]] += 1
                continue
            if iso3 not in bm:
                skipped_non_bm[iso3] += 1
                continue
            currency = entry.get("currency") or ""
            for plan in entry.get("plans") or []:
                name = plan.get("name")
                price = plan.get("price")
                if name is None or price is None:
                    continue
                append_plan_row(
                    rows,
                    seen,
                    iso3=iso3,
                    date=date,
                    plan=name,
                    price=price,
                    currency=currency,
                    source=SOURCE_TOMPEC,
                    note=NOTE_TOMPEC,
                    plan_counts=plan_counts,
                    iso_counts=iso_counts,
                )
    return snapshot_dates


def build_fromabroad(
    bm: set[str],
    rows: list[dict],
    seen: set[tuple],
    plan_counts: Counter,
    iso_counts: Counter,
) -> dict:
    path = ROOT / "raw" / "fromabroad_2020-03-10_lcu_curated.csv"
    date = "2020-03-10"
    n = 0
    isos: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            iso3 = r["iso3"]
            if iso3 not in bm:
                continue
            cur = r["currency"]
            for plan, col in (
                ("mobile", "mobile"),
                ("basic", "basic"),
                ("standard", "standard"),
                ("premium", "premium"),
            ):
                price = parse_price(r.get(col))
                if price is None:
                    continue
                append_plan_row(
                    rows,
                    seen,
                    iso3=iso3,
                    date=date,
                    plan=plan,
                    price=price,
                    currency=cur,
                    source=SOURCE_FROMABROAD,
                    note=NOTE_FROMABROAD,
                    plan_counts=plan_counts,
                    iso_counts=iso_counts,
                )
                n += 1
                isos.add(iso3)
    return {"date": date, "n_rows_added": n, "n_iso3": len(isos), "iso3": sorted(isos)}


def resolve_apoorv_currency(name: str, iso2: str) -> str | None:
    if name == "Krona":
        return "SEK" if iso2 == "SE" else None
    if name == "Krone":
        return "NOK" if iso2 in {"NO", "BV", "SJ"} else None
    return CURRENCY_NAME_TO_CODE.get(name)


def build_apoorv(
    bm: set[str],
    rows: list[dict],
    seen: set[tuple],
    plan_counts: Counter,
    iso_counts: Counter,
    tompec_cur: dict[str, str],
) -> dict:
    path = ROOT / "raw" / "apoorvgupta25_Netflix_Prices_Dec2021.csv"
    if not path.is_file():
        # fall back to box pre2023 mirror
        path = PRE2023_RAW / "Netflix Prices.csv"
    date = "2021-12-28"  # zip member mtime
    n = 0
    isos: set[str] = set()
    skipped_cur_mismatch: Counter = Counter()
    skipped_non_bm = 0
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            iso2 = (r.get("Code") or "").strip()
            iso3 = iso2_to_iso3(iso2)
            if iso3 is None or iso3 not in bm:
                skipped_non_bm += 1
                continue
            cur = resolve_apoorv_currency((r.get("Currency") or "").strip(), iso2)
            if cur is None:
                skipped_cur_mismatch[iso3] += 1
                continue
            expected = tompec_cur.get(iso3)
            if expected is None:
                # RUS (and any other BM miss in tompec): accept only clear native LCU
                if not (iso3 == "RUS" and cur == "RUB"):
                    skipped_cur_mismatch[iso3] += 1
                    continue
            elif cur != expected:
                skipped_cur_mismatch[iso3] += 1
                continue
            for plan, col in (
                ("mobile", "Mobile"),
                ("basic", "Basic"),
                ("standard", "Standard"),
                ("premium", "Premium"),
            ):
                price = parse_price(r.get(col))
                if price is None:
                    continue
                append_plan_row(
                    rows,
                    seen,
                    iso3=iso3,
                    date=date,
                    plan=plan,
                    price=price,
                    currency=cur,
                    source=SOURCE_APOORV,
                    note=NOTE_APOORV,
                    plan_counts=plan_counts,
                    iso_counts=iso_counts,
                )
                n += 1
                isos.add(iso3)
    return {
        "date": date,
        "n_rows_added": n,
        "n_iso3": len(isos),
        "iso3": sorted(isos),
        "skipped_currency_mismatch_iso3": dict(skipped_cur_mismatch),
    }


def build_rows(bm: set[str]) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    seen: set[tuple] = set()
    plan_counts: Counter = Counter()
    iso_counts: Counter = Counter()

    tompec_cur = tompec_currency_by_iso3(bm)
    snapshot_dates = build_tompec(bm, rows, seen, plan_counts, iso_counts)
    fa_meta = build_fromabroad(bm, rows, seen, plan_counts, iso_counts)
    ap_meta = build_apoorv(bm, rows, seen, plan_counts, iso_counts, tompec_cur)

    plan_rank = {p: i for i, p in enumerate(PLAN_ORDER)}

    def sort_key(r: dict):
        plan = r["variable"].split(":", 1)[1]
        return (r["country"], r["date"], plan_rank.get(plan, 99), plan)

    rows.sort(key=sort_key)

    dates = sorted({r["date"] for r in rows})
    meta = {
        "n_rows": len(rows),
        "n_iso3": len(iso_counts),
        "iso3_sorted": sorted(iso_counts),
        "plan_counts": dict(plan_counts),
        "earliest_date": dates[0] if dates else None,
        "latest_date": dates[-1] if dates else None,
        "n_distinct_dates": len(dates),
        "tompec_snapshot_dates": snapshot_dates,
        "n_tompec_snapshots": len(snapshot_dates),
        "pre2023": {
            "fromabroad_2020_03_10": fa_meta,
            "apoorv_comparitech_2021_12_28": ap_meta,
            "year_2022": {
                "status": "thin_no_easy_open_full_LCU_cross_section",
                "note": (
                    "No attributable open multi-country LCU table for 2022 found "
                    "via tompec history, Kaggle mirrors, or trivial Wayback; "
                    "USD-only prasertk/gist mirrors skipped (no FX lane)."
                ),
            },
            "before_2020": {
                "status": "not_in_scope",
                "note": "Owner ask: ~2020 onward (COVID-era); no pre-2020 dig.",
            },
        },
        "bm_miss_no_series": sorted(bm - set(iso_counts)),
        "tompec_clone_path": str(AOI_RAW),
        "tompec_commit": "efa54e3700976d2821d5f9379df0c9deedb4a5d0",
        "duplicate_keys": 0,
        "estimated_value_nonempty": sum(1 for r in rows if r["estimated_value"]),
        "sources": [
            "tompec/netflix-prices",
            "fromabroad.org 2020-03-10",
            "apoorvgupta25/netflix-prices (Comparitech Dec-2021)",
        ],
    }
    return rows, meta


def crosscheck_burgerparity(bm: set[str]) -> dict:
    """Snapshot cross-check only — prices_all.csv is NOT history."""
    if not PRICES_ALL.is_file():
        return {"status": "missing_prices_all"}

    hist: dict[str, list[tuple[str, float, str]]] = {}
    for date, payload in iter_snapshots(AOI_RAW / "data"):
        for entry in payload:
            iso3 = iso2_to_iso3(entry["country_code"])
            if iso3 not in bm:
                continue
            for plan in entry.get("plans") or []:
                if plan.get("name") == "standard" and plan.get("price") is not None:
                    hist.setdefault(iso3, []).append(
                        (date, float(plan["price"]), entry.get("currency") or "")
                    )

    bp = [
        r
        for r in csv.DictReader(PRICES_ALL.open(encoding="utf-8"))
        if r["product_slug"] == "netflix"
    ]
    exact, near, missing = [], [], []
    for r in bp:
        iso = r["country_code"]
        try:
            lp = float(r["local_price"])
        except ValueError:
            missing.append({"iso3": iso, "reason": "bad_local_price"})
            continue
        cur = r["currency_code"]
        if iso not in bm:
            missing.append(
                {
                    "iso3": iso,
                    "reason": "outside_bigmac_iso3_universe",
                    "burgerparity_local": lp,
                    "currency": cur,
                    "note": (
                        "Burger Parity lists this ISO3; Season2 panel filters to "
                        "countries_iso3.txt (EU members → EUZ aggregate in Big Mac)."
                    ),
                }
            )
            continue
        series = hist.get(iso, [])
        hits = [(d, p, c) for d, p, c in series if abs(p - lp) < 1e-6 and c == cur]
        if hits:
            exact.append(
                {
                    "iso3": iso,
                    "burgerparity_local": lp,
                    "currency": cur,
                    "tompec_dates_matching": [h[0] for h in hits],
                    "last_match_date": hits[-1][0],
                }
            )
        elif series:
            best = min(series, key=lambda t: abs(t[1] - lp))
            near.append(
                {
                    "iso3": iso,
                    "burgerparity_local": lp,
                    "currency": cur,
                    "nearest_tompec": {
                        "date": best[0],
                        "price": best[1],
                        "currency": best[2],
                    },
                }
            )
        else:
            missing.append({"iso3": iso, "reason": "in_bm_but_no_tompec_standard_series"})

    return {
        "role": "snapshot_crosscheck_only_not_history",
        "prices_all": str(PRICES_ALL),
        "burgerparity_netflix_n": len(bp),
        "exact_lcu_match_any_tompec_date": len(exact),
        "near_no_exact": len(near),
        "missing_in_tompec": len(missing),
        "exact": exact,
        "near": near,
        "missing": missing,
        "note": (
            "Burger Parity prices_all.csv is a single cross-section reference; "
            "tompec JSON is the historical panel source for 2023+. Mismatches "
            "expected when observation dates / plan definitions diverge. No values "
            "copied from prices_all into the vertical panel."
        ),
    }


def write_outputs(rows: list[dict], meta: dict, cross: dict) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with gzip.open(OUT_GZ, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    plain = OUT_CSV.read_text(encoding="utf-8")
    with gzip.open(OUT_GZ, "rt", encoding="utf-8") as f:
        gz_text = f.read()
    if plain != gz_text:
        raise SystemExit("csv/gz mismatch")

    STATS.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    CROSS.write_text(json.dumps(cross, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fa = meta["pre2023"]["fromabroad_2020_03_10"]
    ap = meta["pre2023"]["apoorv_comparitech_2021_12_28"]
    raw_src = ROOT / "raw" / "SOURCE.md"
    raw_src.write_text(
        "\n".join(
            [
                "# Raw provenance — Netflix subscription levels",
                "",
                "## 1. tompec/netflix-prices (2023-01-07 … 2026-09-28)",
                "",
                f"- Upstream: https://github.com/tompec/netflix-prices",
                f"- Clone commit: `{meta['tompec_commit']}` (2026-09-28)",
                f"- Box path: `{meta['tompec_clone_path']}`",
                f"- Snapshots: {meta['n_tompec_snapshots']} dated JSON under `data/`; "
                "`latest.json` ignored.",
                "- License: Creative Commons Attribution 4.0.",
                "",
                "## 2. fromabroad.org (2020-03-10)",
                "",
                "- Article: https://fromabroad.org/netflix/a-study-on-the-netflix-price-differences-between-countries-and-how-to-get-netflix-70-cheaper/",
                "- Dated: 2020-03-10 (COVID-era demand start).",
                f"- Curated extract in-pack: `fromabroad_2020-03-10_lcu_curated.csv` "
                f"({fa['n_iso3']} ISO3, unambiguous native LCU only).",
                f"- Box HTML archive: `{PRE2023_RAW}/fromabroad_2020-03-10.html`",
                "- Skipped: TR/EG EUR-mislabeled, EC ARS-mislabeled, TH incomplete, euro-area (BM→EUZ).",
                "",
                "## 3. Comparitech Dec-2021 via Kaggle apoorvgupta25 (2021-12-28)",
                "",
                "- Dataset: https://www.kaggle.com/datasets/apoorvgupta25/netflix-prices",
                "- In-pack: `apoorvgupta25_Netflix_Prices_Dec2021.csv`",
                f"- Box zip: `{PRE2023_RAW}/apoorvgupta25_netflix-prices.zip`",
                f"- Rows kept: {ap['n_rows_added']} / {ap['n_iso3']} ISO3 "
                "(currency matched to tompec billing currency; RUS/RUB added).",
                "- USD-only prasertk Dec-2021 mirror **not** used (no FX lane).",
                "",
                "## Not used / left alone",
                "",
                "- Aoi `netflix_standard_burgerparity_panel.csv` / `prices_all.csv` — snapshot only.",
                "- iPhone CSVs in numeraire_hist — leave alone.",
                "- 2022: no easy open full LCU cross-section found.",
                "- Pre-2020: out of owner scope (~2020+).",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_readme_missing(meta: dict) -> None:
    fa = meta["pre2023"]["fromabroad_2020_03_10"]
    ap = meta["pre2023"]["apoorv_comparitech_2021_12_28"]
    miss = meta["bm_miss_no_series"]
    readme = ROOT / "adjacent_netflix_subscription_levels_readme.md"
    readme.write_text(
        f"""# adjacent_netflix_subscription_levels — Netflix list prices (2020+)

Retrieved: 2026-10-25 Asia/Tokyo

## Hard rules

- Absolute subscription list prices in **local currency as published** (not CPI indices).
- No FX conversion; source `price_usd` / USD-only mirrors are **not** loaded.
- No gap-fill of null plans; `estimated_value` empty.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.
- Country universe = Big Mac ISO3 (`countries_iso3.txt`).

## What

Historical panel of Netflix plan list prices from three open LCU sources:

1. **tompec/netflix-prices** (CC-BY-4.0) — dated JSON 2023-01-07 … 2026-09-28
2. **fromabroad.org** — 2020-03-10 LCU table (curated native-currency rows)
3. **Comparitech Dec-2021** via Kaggle `apoorvgupta25/netflix-prices` — dated 2021-12-28

**Variables** (prefix `netflix:`):

| variable | plan |
|----------|------|
| `netflix:mobile` | Mobile |
| `netflix:basic_with_ads` | Basic with ads |
| `netflix:basic` | Basic |
| `netflix:standard_with_ads` | Standard with ads |
| `netflix:standard` | Standard ← primary numéraire-candidate plan |
| `netflix:premium` | Premium |

Unit: `{{ISO4217}} per monthly subscription`.

## Coverage (this pack)

| Metric | Value |
|--------|------:|
| Rows | **{meta['n_rows']}** |
| ISO3 | **{meta['n_iso3']}** / 56 Big Mac |
| Earliest date | **{meta['earliest_date']}** |
| Latest date | **{meta['latest_date']}** |
| Distinct dates | **{meta['n_distinct_dates']}** |
| tompec snapshots | {meta['n_tompec_snapshots']} (2023-01-07 … 2026-09-28) |
| fromabroad 2020-03-10 | {fa['n_rows_added']} rows / {fa['n_iso3']} ISO3 |
| Comparitech 2021-12-28 | {ap['n_rows_added']} rows / {ap['n_iso3']} ISO3 |
| `netflix:standard` | {meta['plan_counts'].get('standard', 0)} |
| `netflix:premium` | {meta['plan_counts'].get('premium', 0)} |
| `netflix:basic` | {meta['plan_counts'].get('basic', 0)} |
| `netflix:mobile` | {meta['plan_counts'].get('mobile', 0)} |

**Big Mac ISO3 with no series at all:** {', '.join(miss) if miss else '(none)'}.

- **EUZ**: Netflix prices by member state — not invented as euro-area aggregate.
- **CHN**: absent from open LCU tables used here.
- **RUS**: added from Comparitech Dec-2021 (RUB); absent from tompec / fromabroad curated set.

## Thin gaps

| Window | Status |
|--------|--------|
| Before 2020 | Out of scope (owner: ~2020+ COVID-era) |
| 2020 | Partial — fromabroad curated 20 BM ISO3 (native LCU only) |
| 2021 | Good BM overlap — Comparitech Dec-2021 via Kaggle (~50 ISO3 currency-matched) |
| 2022 | **Thin** — no easy open full multi-country LCU cross-section (USD-only mirrors skipped) |
| 2023-01 … 2026-09 | Dense — tompec dated JSON |

## Burger Parity snapshot cross-check (not history)

`prices_all.csv` is a **single cross-section** reference. **No values copied** into this panel.
See `_crosscheck_burgerparity.json`.

## Not collected / left alone

| Asset | Why |
|-------|-----|
| Aoi `netflix_standard_burgerparity_panel.csv` | Aoi lane — leave alone |
| iPhone CSVs in `numeraire_hist_2026-10-25/` | Aoi durables — **leave alone** |
| prasertk / danwaters gist (USD-only) | No FX lane |
| Netflix account / login walls | Not scraped |

## Files

- `adjacent_netflix_subscription_levels_vertical.csv` (+ `.gz`)
- `build_netflix_subscription_levels.py`
- `_build_stats.json` / `_crosscheck_burgerparity.json`
- `raw/SOURCE.md`, `raw/fromabroad_2020-03-10_lcu_curated.csv`, `raw/apoorvgupta25_Netflix_Prices_Dec2021.csv`
- `adjacent_netflix_subscription_levels_missing.md`
""",
        encoding="utf-8",
    )

    missing = ROOT / "adjacent_netflix_subscription_levels_missing.md"
    missing.write_text(
        f"""# Missing / thin — adjacent_netflix_subscription_levels

## Big Mac ISO3 with zero rows

{chr(10).join(f'- `{c}`' for c in miss) if miss else '_None_'}

## Pre-2023 windows

- **2020-03-10 (fromabroad curated):** {fa['n_iso3']} ISO3 — {', '.join(fa['iso3'])}
- **2021-12-28 (Comparitech/Apoorv):** {ap['n_iso3']} ISO3
- **2022:** thin — no easy open full LCU panel found (tompec starts 2023-01-07; USD-only Kaggle/gist skipped)
- **Before 2020:** not collected (owner scope ~2020+)

## Optional still thin

- Intra-2020 / mid-2021 / all of 2022 monthly density
- EUZ aggregate (would need a stated euro-area rule; not invented)
- CHN Netflix list prices (service historically unavailable / not in open LCU tables used)
""",
        encoding="utf-8",
    )


def main() -> None:
    bm = load_bm_iso3()
    rows, meta = build_rows(bm)
    cross = crosscheck_burgerparity(bm)
    write_outputs(rows, meta, cross)
    write_readme_missing(meta)
    print(
        json.dumps(
            {
                "n_rows": meta["n_rows"],
                "n_iso3": meta["n_iso3"],
                "earliest": meta["earliest_date"],
                "latest": meta["latest_date"],
                "plans": meta["plan_counts"],
                "bm_miss": meta["bm_miss_no_series"],
                "pre2023": meta["pre2023"],
                "crosscheck_exact": cross.get("exact_lcu_match_any_tompec_date"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
