#!/usr/bin/env python3
"""Build adjacent_household_sku_levels vertical CSV from NSO named-retail sources."""
from __future__ import annotations

import csv
import gzip
import json
import re
from calendar import month_abbr
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
AOI = Path("/workspace/aoi-phase2")
OUT_CSV = ROOT / "adjacent_household_sku_levels_vertical.csv"
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
RETRIEVED = "retrieved 2026-10-25 Asia/Tokyo"


def row(country, date, year, variable, value, unit, source, note):
    return {
        "country": country,
        "date": date,
        "year": int(year),
        "variable": variable,
        "value": value,
        "unit": unit,
        "source": source,
        "note": note,
        "estimated_value": "",
    }


def from_japan_rps() -> list[dict]:
    path = AOI / "japan_rps_everyday_clothing_household_panel.csv"
    coffee_path = AOI / "japan_retail_price_oil_sugar_coffee_panel.csv"
    keep = {
        "towel_yen": "towel_unit",
        "tissue_yen": "tissue_box_pack",
        "toilet_paper_yen": "toilet_paper_12rolls",
        "sanitary_napkin_yen": "sanitary_napkin_pack",
        "body_soap_yen": "body_soap_refill",
        "hand_soap_yen": "bar_soap_3pack",
        "dish_detergent_yen": "dish_detergent_refill",
        "laundry_detergent_yen": "laundry_detergent_refill",
        "shampoo_yen": "shampoo",
        "mens_briefs_yen": "mens_briefs_2pack",
        "mens_undershirt_yen": "mens_undershirt_2pack",
        "bra_yen": "bra",
        "womens_panties_yen": "womens_panties",
    }
    src = "https://www.e-stat.go.jp (Japan Retail Price Survey 動向編 Table 1; city mean)"
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            var0 = r["variable"]
            if var0 not in keep:
                continue
            y, m = int(r["year"]), int(r["month"])
            try:
                val = float(r["value"])
            except (TypeError, ValueError):
                continue
            sku = r.get("sku_spec") or r.get("item_label") or ""
            note = (
                f"e-Stat RPS city mean; item={r.get('item_label','')}; "
                f"sku_unit={r.get('sku_unit','')}; sku_spec={sku}; {RETRIEVED}"
            )
            out.append(
                row(
                    "JPN",
                    f"{y}-{m:02d}-01",
                    y,
                    f"household_sku:{keep[var0]}",
                    val,
                    "JPY per published SKU",
                    src,
                    note,
                )
            )
    # Instant coffee from oil/sugar/coffee panel (not in clothing/household panel)
    if coffee_path.exists():
        with coffee_path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if "coffee" not in r.get("variable", ""):
                    continue
                y, m = int(r["year"]), int(r["month"])
                try:
                    val = float(r["value"])
                except (TypeError, ValueError):
                    continue
                note = (
                    f"e-Stat RPS city mean; item={r.get('item_label','')}; "
                    f"item_code={r.get('item_code','')}; {RETRIEVED}"
                )
                out.append(
                    row(
                        "JPN",
                        f"{y}-{m:02d}-01",
                        y,
                        "household_sku:coffee_instant",
                        val,
                        "JPY per published SKU",
                        src,
                        note,
                    )
                )
    return out


def from_uk_ons() -> list[dict]:
    path = AOI / "uk_ons_avg_retail_household_clothing_panel.csv"
    # Target families only (skip jeans/t-shirts/deodorant/socks as out of lane families)
    keep = {
        "211901": ("tea_bags_80", "Small box of tea bags"),
        "213003": ("coffee_instant_90_100g", "Instant coffee"),
        "430228": ("bath_towel", "Bath towel"),
        "430533": ("kitchen_roll_2_4", "Kitchen roll"),
        "430540": ("washing_detergent_800ml_1_5l", "Washing detergent"),
        "510406": ("womens_pants", "Women's pants"),
        "510407": ("bra", "Bra"),
        "520213": ("tissues_large_box", "Tissues"),
        "520226": ("shampoo_250_400ml", "Shampoo"),
        "520247": ("liquid_soap_200_300ml", "Liquid soap"),
    }
    src = (
        "https://www.ons.gov.uk (ONS average retail prices / Shopping Prices "
        "avgprice archive; experimental)"
    )
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            iid = str(r["item_id"])
            if iid not in keep:
                continue
            var, label = keep[iid]
            y, m = int(r["year"]), int(r["month"])
            try:
                val = float(r["value"])
            except (TypeError, ValueError):
                continue
            ws = r.get("weight_size") or ""
            note = (
                f"ONS avg retail; item_id={iid}; {label}; pack={ws}; "
                f"category={r.get('category1','')}/{r.get('category2','')}; {RETRIEVED}"
            )
            out.append(
                row(
                    "GBR",
                    f"{y}-{m:02d}-01",
                    y,
                    f"household_sku:{var}",
                    val,
                    "GBP per published pack",
                    src,
                    note,
                )
            )
    return out


def from_usa_bls() -> list[dict]:
    path = AOI / "bls_us_everyday_product_prices_panel.csv"
    src = "https://www.bls.gov/cpi/factsheets/average-prices.htm (BLS CPI Average Price Data API v2)"
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("series") != "coffee_ground_roast_usd_per_lb":
                continue
            y, m = int(r["year"]), int(r["month"])
            try:
                val = float(r["value"])
            except (TypeError, ValueError):
                continue
            note = (
                f"BLS APU0000717311 Coffee 100% ground roast; U.S. city average NSA; "
                f"{RETRIEVED}"
            )
            out.append(
                row(
                    "USA",
                    f"{y}-{m:02d}-01",
                    y,
                    "household_sku:coffee_ground_roast_lb",
                    val,
                    "USD per lb",
                    src,
                    note,
                )
            )
    return out


_MONTH = {m: i for i, m in enumerate(month_abbr) if m}


def from_sgp_singstat() -> list[dict]:
    path = RAW / "singstat_M213761_hh.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    mapping = {
        "53": ("coffee_instant_200g", "Instant Coffee (Per 200 Gram)"),
        "78": ("laundry_liquid_detergent_kg", "Laundry Liquid Detergent (Per Kilogram)"),
        "79": ("toilet_paper_10rolls", "Toilet Paper (10 Rolls)"),
    }
    src = "https://tablebuilder.singstat.gov.sg (M213761 Average Retail Prices of Selected Consumer Items)"
    out = []
    for series in data.get("Data", {}).get("row", []):
        sno = str(series.get("seriesNo"))
        if sno not in mapping:
            continue
        var, label = mapping[sno]
        for c in series.get("columns", []):
            key = c.get("key", "")  # e.g. '2015 Jan'
            val = c.get("value")
            if val in (None, "", "-"):
                continue
            try:
                valf = float(val)
            except (TypeError, ValueError):
                continue
            m = re.match(r"(\d{4})\s+([A-Za-z]{3})", key)
            if not m:
                continue
            y = int(m.group(1))
            mo = _MONTH[m.group(2)]
            note = f"SingStat M213761 seriesNo={sno}; {label}; {RETRIEVED}"
            out.append(
                row(
                    "SGP",
                    f"{y}-{mo:02d}-01",
                    y,
                    f"household_sku:{var}",
                    valf,
                    "SGD per published pack",
                    src,
                    note,
                )
            )
    return out


def from_irl_cso() -> list[dict]:
    path = RAW / "cso" / "irl_tea_bags.csv"
    if not path.exists():
        return []
    src = "https://data.cso.ie (PxStat CPM12 National Average Price; Tea bags per 80)"
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y, m = int(r["year"]), int(r["month"])
            try:
                val = float(r["value"])
            except (TypeError, ValueError):
                continue
            note = f"CSO CPM12 item 11570 Tea bags per 80; EUR national average; {RETRIEVED}"
            out.append(
                row(
                    "IRL",
                    f"{y}-{m:02d}-01",
                    y,
                    "household_sku:tea_bags_80",
                    val,
                    "EUR per 80 bags",
                    src,
                    note,
                )
            )
    return out


def from_qat() -> list[dict]:
    path = RAW / "qat_household_annual.csv"
    if not path.exists():
        return []
    src = (
        "https://www.data.gov.qa (annual_average_consumer_prices_selected_commodities; "
        "NPC selected commodities)"
    )
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y = int(r["year"])
            try:
                val = float(r["value"])
            except (TypeError, ValueError):
                continue
            unit = (r.get("unit") or "QAR").strip() or "QAR"
            if "QR" not in unit.upper() and "QAR" not in unit.upper():
                unit = f"QAR ({unit})" if unit else "QAR"
            note = (
                f"Qatar NPC annual avg; commodity={r.get('commodity','')}; "
                f"category={r.get('category','')}; {RETRIEVED}"
            )
            out.append(
                row(
                    "QAT",
                    f"{y}-01-01",
                    y,
                    f"household_sku:{r['variable']}",
                    val,
                    unit if unit else "QAR per published pack",
                    src,
                    note,
                )
            )
    return out


def from_mys_dosm() -> list[dict]:
    path = RAW / "dosm" / "mys_household_monthly_means.csv"
    if not path.exists():
        return []
    src = "https://open.dosm.gov.my (pricecatcher monthly CSV + lookup_item; premise mean)"
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y, m = int(r["year"]), int(r["month"])
            try:
                val = float(r["mean_price"])
            except (TypeError, ValueError):
                continue
            note = (
                f"DOSM PriceCatcher monthly mean of positive premise prices; "
                f"item_code={r['item_code']}; {r.get('label','')}; "
                f"n_premises={r.get('n_premises','')}; {RETRIEVED}"
            )
            out.append(
                row(
                    "MYS",
                    f"{y}-{m:02d}-01",
                    y,
                    f"household_sku:{r['variable']}",
                    val,
                    "MYR per published pack",
                    src,
                    note,
                )
            )
    return out



def from_fin_statfin() -> list[dict]:
    path = RAW / "fin" / "fin_household_prices.csv"
    if not path.exists():
        return []
    mapping = {
        "0111500": ("coffee_500g", "Packet of coffee, 500 g"),
        "0111600": ("tea_bags_50g", "Tea bags, 50 g"),
        "0500100": ("dishwashing_detergent_machine_1kg", "Machine dishwashing detergent, 1 kg"),
        "0500200": ("laundry_detergent_1l", "Laundry detergent, 1 l"),
        "0500300": ("washing_up_liquid_1l", "Washing-up liquid, 1 l"),
        "0500400": ("general_purpose_cleanser_1l", "General purpose cleanser, 1 l"),
        "0500600": ("kitchen_towel_4rolls", "Kitchen towel, 4 rolls"),
        "1200300": ("toilet_paper_8rolls", "Toilet paper, 8 rolls"),
        "1200400": ("sanitary_towels_20pcs", "Sanitary towels, 20 pcs"),
    }
    src = (
        "https://pxdata.stat.fi (StatFin Passiivi / Average prices of commodities "
        "011; monthly national average)"
    )
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("freq") != "M":
                continue  # monthly only; skip annual M01-M12 averages
            code = r["commodity"]
            if code not in mapping:
                continue
            var, label = mapping[code]
            try:
                val = float(r["value"])
            except (TypeError, ValueError):
                continue
            y, m = int(r["year"]), int(r["month"])
            note = (
                f"StatFin 011 commodity={code}; {label}; EUR national average; "
                f"{RETRIEVED}"
            )
            out.append(
                row(
                    "FIN",
                    f"{y}-{m:02d}-01",
                    y,
                    f"household_sku:{var}",
                    val,
                    "EUR per published pack",
                    src,
                    note,
                )
            )
    return out


def from_aut_preisradar() -> list[dict]:
    path = RAW / "aut" / "aut_household_means.csv"
    if not path.exists():
        return []
    src = (
        "https://www.statistik.at (Preisradar / price radar product means; "
        "ep/{productId}.json meanData)"
    )
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                val = float(r["value"])
            except (TypeError, ValueError):
                continue
            y, m = int(r["year"]), int(r["month"])
            note = (
                f"Austria Preisradar monthly mean; productId={r['product_id']}; "
                f"{r.get('label','')}; {RETRIEVED}"
            )
            out.append(
                row(
                    "AUT",
                    f"{y}-{m:02d}-01",
                    y,
                    f"household_sku:{r['variable']}",
                    val,
                    "EUR per published pack",
                    src,
                    note,
                )
            )
    return out


def from_nld_cbs() -> list[dict]:
    path = RAW / "nld" / "nld_coffee_tea_annual.csv"
    if not path.exists():
        return []
    src = (
        "https://opendata.cbs.nl (80345eng Consumer prices of food; "
        "Coffee_5, Tea_14; annual)"
    )
    units = {"coffee": "EUR per published unit (CBS Coffee_5)", "tea": "EUR per published unit (CBS Tea_14)"}
    out = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                val = float(r["value"])
            except (TypeError, ValueError):
                continue
            y = int(r["year"])
            var = r["variable"]
            note = (
                f"CBS 80345eng annual; Periods={r.get('period','')}; "
                f"variable={var}; ends 2018 series close; {RETRIEVED}"
            )
            out.append(
                row(
                    "NLD",
                    f"{y}-01-01",
                    y,
                    f"household_sku:{var}",
                    val,
                    units.get(var, "EUR"),
                    src,
                    note,
                )
            )
    return out


def main() -> None:
    # Skip already-landed Aoi panels (do not duplicate into #118):
    # - japan_rps_everyday_clothing_household_panel.csv
    # - uk_ons_avg_retail_household_clothing_panel.csv
    # - bls_us_everyday_product_prices_panel.csv
    # - japan_retail_price_oil_sugar_coffee_panel.csv
    parts = [
        ("SGP", from_sgp_singstat()),
        ("IRL", from_irl_cso()),
        ("QAT", from_qat()),
        ("MYS", from_mys_dosm()),
        ("FIN", from_fin_statfin()),
        ("AUT", from_aut_preisradar()),
        ("NLD", from_nld_cbs()),
    ]
    rows: list[dict] = []
    stats = {}
    for name, part in parts:
        stats[name] = len(part)
        rows.extend(part)
    rows.sort(key=lambda r: (r["country"], r["variable"], r["date"]))
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    with gzip.open(str(OUT_CSV) + ".gz", "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    build_stats = {
        "rows": len(rows),
        "by_country": stats,
        "countries": sorted({r["country"] for r in rows}),
        "variables": sorted({r["variable"] for r in rows}),
    }
    (ROOT / "_build_stats.json").write_text(json.dumps(build_stats, indent=2) + "\n")
    print(json.dumps(build_stats, indent=2))


if __name__ == "__main__":
    main()
