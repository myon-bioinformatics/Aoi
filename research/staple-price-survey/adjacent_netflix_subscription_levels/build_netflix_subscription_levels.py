#!/usr/bin/env python3
"""Build adjacent_netflix_subscription_levels vertical CSV from tompec/netflix-prices JSON history.

Primary raw (already cloned on box):
  /workspace/aoi-phase2/raw/numeraire_hist_2026-10-25/tompec-netflix-prices/
Upstream: https://github.com/tompec/netflix-prices (CC-BY-4.0)

Rules: LCU absolute subscription prices only; no FX; no gap-fill; estimated_value empty.
Country universe = Big Mac ISO3 (countries_iso3.txt). price_usd from source is NOT loaded.
"""
from __future__ import annotations

import csv
import gzip
import json
import shutil
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
SOURCE = (
    "https://github.com/tompec/netflix-prices "
    "(data/*.json; clone efa54e3 2026-09-28; retrieved 2026-10-25 Asia/Tokyo)"
)
NOTE_BASE = (
    "tompec community scrape of Netflix list prices by plan; "
    "LCU as published; null plans omitted; "
    "source price_usd not loaded (no FX lane); "
    "retrieved 2026-10-25 Asia/Tokyo"
)
PLAN_ORDER = [
    "mobile",
    "basic_with_ads",
    "basic",
    "standard_with_ads",
    "standard",
    "premium",
]


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


def build_rows(bm: set[str]) -> tuple[list[dict], dict]:
    data_dir = AOI_RAW / "data"
    if not data_dir.is_dir():
        raise SystemExit(f"missing tompec data dir: {data_dir}")

    rows: list[dict] = []
    seen_keys: set[tuple] = set()
    unmapped: Counter = Counter()
    skipped_non_bm: Counter = Counter()
    plan_counts: Counter = Counter()
    iso_counts: Counter = Counter()
    snapshot_dates: list[str] = []

    for date, payload in iter_snapshots(data_dir):
        snapshot_dates.append(date)
        year = int(date[:4])
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
                variable = f"netflix:{name}"
                key = (iso3, date, variable)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                rows.append(
                    {
                        "country": iso3,
                        "date": date,
                        "year": year,
                        "variable": variable,
                        "value": price,
                        "unit": f"{currency} per monthly subscription",
                        "source": SOURCE,
                        "note": NOTE_BASE + f"; plan={name}; currency={currency}",
                        "estimated_value": "",
                    }
                )
                plan_counts[name] += 1
                iso_counts[iso3] += 1

    # stable sort: country, date, plan order
    plan_rank = {p: i for i, p in enumerate(PLAN_ORDER)}

    def sort_key(r: dict):
        plan = r["variable"].split(":", 1)[1]
        return (r["country"], r["date"], plan_rank.get(plan, 99), plan)

    rows.sort(key=sort_key)

    meta = {
        "n_rows": len(rows),
        "n_iso3": len(iso_counts),
        "iso3_sorted": sorted(iso_counts),
        "plan_counts": dict(plan_counts),
        "snapshot_dates": snapshot_dates,
        "n_snapshots": len(snapshot_dates),
        "bm_miss_no_tompec_iso3": sorted(bm - set(iso_counts)),
        "unmapped_iso2": dict(unmapped),
        "n_skipped_non_bm_country_snapshots": int(sum(skipped_non_bm.values())),
        "tompec_clone_path": str(AOI_RAW),
        "tompec_commit": "efa54e3700976d2821d5f9379df0c9deedb4a5d0",
        "duplicate_keys": 0,
        "estimated_value_nonempty": sum(1 for r in rows if r["estimated_value"]),
    }
    return rows, meta


def crosscheck_burgerparity(bm: set[str]) -> dict:
    """Snapshot cross-check only — prices_all.csv is NOT history."""
    if not PRICES_ALL.is_file():
        return {"status": "missing_prices_all"}

    # build standard LCU history from tompec for BM
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
            "tompec JSON is the historical panel source. Mismatches expected when "
            "observation dates / plan definitions diverge. No values copied from "
            "prices_all into the vertical panel."
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
    # verify gz == csv
    plain = OUT_CSV.read_text(encoding="utf-8")
    with gzip.open(OUT_GZ, "rt", encoding="utf-8") as f:
        gz_text = f.read()
    if plain != gz_text:
        raise SystemExit("csv/gz mismatch")

    STATS.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    CROSS.write_text(json.dumps(cross, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # slim raw provenance (do not vendor full 5MB JSON into Aoi)
    raw_src = ROOT / "raw" / "SOURCE.md"
    raw_src.write_text(
        "\n".join(
            [
                "# Raw provenance — tompec/netflix-prices",
                "",
                f"- Upstream: https://github.com/tompec/netflix-prices",
                f"- Clone commit: `{meta['tompec_commit']}` (2026-09-28)",
                f"- Box path (primary easy raw): `{meta['tompec_clone_path']}`",
                f"- Snapshots used: {meta['n_snapshots']} dated JSON under `data/` "
                f"({meta['snapshot_dates'][0]} … {meta['snapshot_dates'][-1]}); "
                "`latest.json` ignored (duplicate of newest dated file).",
                "- License: Creative Commons Attribution 4.0 (see upstream LICENSE.md).",
                "- iPhone / Burger Parity durable CSVs in the parent numeraire_hist dir "
                "are **not** inputs to this pack.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    bm = load_bm_iso3()
    rows, meta = build_rows(bm)
    cross = crosscheck_burgerparity(bm)
    write_outputs(rows, meta, cross)
    print(
        json.dumps(
            {
                "n_rows": meta["n_rows"],
                "n_iso3": meta["n_iso3"],
                "plans": meta["plan_counts"],
                "bm_miss": meta["bm_miss_no_tompec_iso3"],
                "crosscheck_exact": cross.get("exact_lcu_match_any_tompec_date"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
