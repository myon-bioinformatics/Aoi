#!/usr/bin/env python3
"""Append easy-open 主食 absolute retail to hi + euz packs (extend gaps; no rewrite)."""
from __future__ import annotations

import csv
import gzip
import json
import re
from calendar import month_abbr
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

TOKYO = timezone(timedelta(hours=9))
RETRIEVED = f"retrieved {datetime.now(TOKYO).strftime('%Y-%m-%d')} Asia/Tokyo"
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
_MONTH = {m: i for i, m in enumerate(month_abbr) if m}

WS = Path("/workspace/staple-price-survey")
AOI = Path("/workspace/repos/Aoi/research/staple-price-survey")
HI_DIR = AOI / "adjacent_hi_staple_levels"
EUZ_DIR = AOI / "adjacent_euz_proxy_staple_levels"
HI_CSV = HI_DIR / "adjacent_hi_staple_levels_vertical.csv"
EUZ_CSV = EUZ_DIR / "adjacent_euz_proxy_staple_levels_vertical.csv"


def row(country, date, year, variable, value, unit, source, note):
    return {
        "country": country,
        "date": date,
        "year": str(year),
        "variable": variable,
        "value": value,
        "unit": unit,
        "source": source,
        "note": note,
        "estimated_value": "",
    }


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    rows = sorted(rows, key=lambda r: (r["country"], r["variable"], r["date"]))
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    with gzip.open(str(path) + ".gz", "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)


def key(r):
    return (r["country"], r["date"], r["variable"])


def append_unique(existing: list[dict], new: list[dict]) -> tuple[list[dict], int]:
    seen = {key(r) for r in existing}
    added = 0
    out = list(existing)
    for r in new:
        k = key(r)
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
        added += 1
    return out, added


def from_nld_cbs_food() -> list[dict]:
    path = WS / "adjacent_euz_proxy_staple_levels/raw/cbs/80345eng_TypedDataSet.json"
    j = json.loads(path.read_text(encoding="utf-8"))
    # Skip Bread/Rice/Potatoes (already in pack); skip Coffee/Tea/Beer (hh / non-staple)
    mapping = {
        "Butter_3": (
            "butter_250g",
            "EUR per 250 g",
            "Butter; 250 g unsalted butter",
        ),
        "Cheese_4": (
            "gouda_cheese_kg",
            "EUR per kg",
            "Cheese; 1 kg matured Gouda",
        ),
        "Eggs_6": (
            "eggs_10",
            "EUR per 10 eggs",
            "Eggs; from 2000: 10 free-range medium; before: 1 egg (series break as published)",
        ),
        "Margarine_7": (
            "margarine_250g",
            "EUR per 250 g",
            "Margarine; from 2000: 250 g spreadable tub; before: 500 g (series break as published)",
        ),
        "Milk_8": (
            "milk_l",
            "EUR per litre",
            "Milk; from 2000: 1 L low-fat; before: 1 L whole (series break as published)",
        ),
        "PorkSteak_9": (
            "pork_steak_kg",
            "EUR per kg",
            "Pork steak; 1 kg",
        ),
        "StewingSteak_12": (
            "stewing_steak_kg",
            "EUR per kg",
            "Stewing steak; 1 kg",
        ),
        "Sugar_13": (
            "sugar_kg",
            "EUR per kg",
            "Sugar; 1 kg",
        ),
    }
    src = "https://opendata.cbs.nl (80345eng Consumer prices; average prices of food, 1800-2018)"
    out = []
    for v in j["value"]:
        per = v.get("Periods") or ""
        m = re.match(r"(\d{4})JJ", per)
        if not m:
            continue
        y = int(m.group(1))
        if y < 1999:
            continue
        for field, (var, unit, label) in mapping.items():
            val = v.get(field)
            if val is None:
                continue
            try:
                valf = float(val)
            except (TypeError, ValueError):
                continue
            note = (
                f"CBS average price {label}; period={per}; CBS table 80345eng "
                f"discontinued after 2018; values in euro as published by CBS; "
                f"Netherlands national average — country proxy for EUZ Big Mac gap "
                f"(not euro-area aggregate); {RETRIEVED}"
            )
            out.append(
                row(
                    "NLD",
                    f"{y}-01-01",
                    y,
                    f"staple_price:{var}",
                    valf,
                    unit,
                    src,
                    note,
                )
            )
    return out


def from_aut_preisradar_food() -> list[dict]:
    ep_dir = WS / "adjacent_euz_proxy_staple_levels/raw/statistik_at/ep"
    mapping = {
        "005661": (
            "fresh_milk_l",
            "EUR per litre",
            "Fresh milk (1000 milliliter)",
        ),
        "006500": (
            "eggs_6",
            "EUR per 6 eggs",
            "Eggs (6 piece)",
        ),
        "007300": (
            "butter_250g",
            "EUR per 250 g",
            "Butter (250 gram)",
        ),
        "007800": (
            "olive_oil_l",
            "EUR per litre",
            "Olive oil (1000 milliliter)",
        ),
        "013200": (
            "crystal_sugar_kg",
            "EUR per kg",
            "Crystal sugar (1000 gram)",
        ),
        "003700": (
            "pork_cutlet_kg",
            "EUR per kg",
            "Pork cutlet (1000 gram)",
        ),
        "003200": (
            "beef_round_kg",
            "EUR per kg",
            "Beef round (1000 gram)",
        ),
    }
    src = (
        "https://www.statistik.at/preisradar/ (Preisradar data/ep/{id}.json meanData; "
        "national scanner Durchschnittspreise)"
    )
    out = []
    for pid, (var, unit, title) in mapping.items():
        path = ep_dir / f"{pid}.json"
        j = json.loads(path.read_text(encoding="utf-8"))
        md = (j.get("price") or {}).get("meanData") or []
        for ts, val in md:
            if val is None:
                continue
            try:
                valf = float(val)
            except (TypeError, ValueError):
                continue
            # ms epoch UTC → Tokyo calendar month start
            dt = datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
            y, m = dt.year, dt.month
            note = (
                f"Statistik Austria Preisradar scanner average retail mean; "
                f"productId={pid}; title='{title}'; absolute EUR as published for "
                f"listed pack (Austria national — country proxy for EUZ Big Mac gap, "
                f"not euro-area aggregate; not VPI/HVPI CPI index; mean of scanner "
                f"prices, not HBS unit value); {RETRIEVED}"
            )
            out.append(
                row(
                    "AUT",
                    f"{y}-{m:02d}-01",
                    y,
                    f"staple_price:{var}",
                    valf,
                    unit,
                    src,
                    note,
                )
            )
    return out


def from_sgp_singstat_food() -> list[dict]:
    path = WS / "adjacent_hi_staple_levels/raw/singstat/M213761_food_staple.json"
    j = json.loads(path.read_text(encoding="utf-8"))
    # rice/bread already in hi pack — skip 1,2
    mapping = {
        "4": (
            "instant_noodles_5pack",
            "SGD per 5 packets",
            "Instant Noodles (Per 5 Packets)",
        ),
        "9": (
            "lean_pork_chilled_kg",
            "SGD per kg",
            "Lean Pork, Chilled (Per Kilogram)",
        ),
        "12": (
            "ribeye_beef_chilled_kg",
            "SGD per kg",
            "Ribeye Beef, Chilled (Per Kilogram)",
        ),
        "14": (
            "whole_chicken_chilled_kg",
            "SGD per kg",
            "Whole Chicken, Chilled (Per Kilogram)",
        ),
        "31": (
            "fresh_milk_l",
            "SGD per litre",
            "Fresh Milk (Per Litre)",
        ),
        "34": (
            "hen_eggs_10",
            "SGD per 10 eggs",
            "Hen Eggs (Per 10)",
        ),
        "35": (
            "cooking_oil_2kg",
            "SGD per 2 kg",
            "Cooking Oil (Per 2 Kilogram)",
        ),
        "47": (
            "potato_kg",
            "SGD per kg",
            "Potatoes (Per Kilogram)",
        ),
        "52": (
            "white_sugar_2kg",
            "SGD per 2 kg",
            "White Sugar (Per 2 Kilogram)",
        ),
    }
    src = "https://tablebuilder.singstat.gov.sg (M213761 Average Retail Prices of Selected Items)"
    out = []
    for series in j.get("Data", {}).get("row", []):
        sno = str(series.get("seriesNo"))
        if sno not in mapping:
            continue
        var, unit, label = mapping[sno]
        for c in series.get("columns", []):
            key_s = c.get("key", "")
            val = c.get("value")
            if val in (None, "", "-"):
                continue
            try:
                valf = float(val)
            except (TypeError, ValueError):
                continue
            m = re.match(r"(\d{4})\s+([A-Za-z]{3})", key_s)
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
                    f"staple_price:{var}",
                    valf,
                    unit,
                    src,
                    note,
                )
            )
    return out


def mirror_pack(src_dir: Path, name: str) -> None:
    dst = WS / name
    dst.mkdir(parents=True, exist_ok=True)
    for fn in [
        f"{name}_vertical.csv",
        f"{name}_vertical.csv.gz",
        f"{name}_readme.md",
        f"{name}_missing.md",
    ]:
        s = src_dir / fn
        if s.exists():
            (dst / fn).write_bytes(s.read_bytes())


def main() -> None:
    nld = from_nld_cbs_food()
    aut = from_aut_preisradar_food()
    sgp = from_sgp_singstat_food()
    print(
        json.dumps(
            {
                "nld_new_candidates": len(nld),
                "aut_new_candidates": len(aut),
                "sgp_new_candidates": len(sgp),
                "nld_vars": sorted({r["variable"] for r in nld}),
                "aut_vars": sorted({r["variable"] for r in aut}),
                "sgp_vars": sorted({r["variable"] for r in sgp}),
            },
            indent=2,
        )
    )

    euz = load_csv(EUZ_CSV)
    hi = load_csv(HI_CSV)
    euz2, a1 = append_unique(euz, nld + aut)
    hi2, a2 = append_unique(hi, sgp)
    write_csv(EUZ_CSV, euz2)
    write_csv(HI_CSV, hi2)

    # stats
    def by_c(rows):
        d = defaultdict(int)
        for r in rows:
            d[r["country"]] += 1
        return dict(sorted(d.items()))

    stats = {
        "euz_total": len(euz2),
        "hi_total": len(hi2),
        "euz_added": a1,
        "hi_added": a2,
        "euz_by_country": by_c(euz2),
        "hi_by_country": by_c(hi2),
        "retrieved": RETRIEVED,
    }
    (WS / "_append_staple_food_densify_s2_stats.json").write_text(
        json.dumps(stats, indent=2) + "\n"
    )
    print(json.dumps(stats, indent=2))

    # Patch readmes briefly
    euz_readme = EUZ_DIR / "adjacent_euz_proxy_staple_levels_readme.md"
    hi_readme = HI_DIR / "adjacent_hi_staple_levels_readme.md"
    patch_euz = (
        f"\n\n## Densify append ({RETRIEVED})\n\n"
        f"- **NLD** +{sum(1 for r in nld)}: butter_250g, gouda_cheese_kg, eggs_10, "
        f"margarine_250g, milk_l, pork_steak_kg, stewing_steak_kg, sugar_kg "
        f"(CBS 80345eng 1999–2018; bread/rice/potato already loaded; coffee/tea left in household pack).\n"
        f"- **AUT** +{sum(1 for r in aut)}: fresh_milk_l, eggs_6, butter_250g, olive_oil_l, "
        f"crystal_sugar_kg, pork_cutlet_kg, beef_round_kg (Preisradar meanData).\n"
        f"- Total rows now **{len(euz2)}** (prior {len(euz)}; +{a1} unique).\n"
    )
    euz_readme.write_text(euz_readme.read_text(encoding="utf-8") + patch_euz)
    patch_hi = (
        f"\n\n## Densify append ({RETRIEVED})\n\n"
        f"- **SGP** +{a2}: instant_noodles_5pack, lean_pork_chilled_kg, ribeye_beef_chilled_kg, "
        f"whole_chicken_chilled_kg, fresh_milk_l, hen_eggs_10, cooking_oil_2kg, potato_kg, "
        f"white_sugar_2kg (SingStat M213761; rice/bread already loaded).\n"
        f"- Total rows now **{len(hi2)}** (prior {len(hi)}; +{a2} unique).\n"
    )
    hi_readme.write_text(hi_readme.read_text(encoding="utf-8") + patch_hi)

    # Copy raw into Aoi packs
    for rel in [
        "adjacent_euz_proxy_staple_levels/raw/cbs/80345eng_TypedDataSet.json",
        "adjacent_euz_proxy_staple_levels/raw/cbs/80345eng_DataProperties.json",
        "adjacent_euz_proxy_staple_levels/raw/statistik_at/products.json",
    ]:
        src = WS / rel
        dst = AOI / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            dst.write_bytes(src.read_bytes())
    ep_src = WS / "adjacent_euz_proxy_staple_levels/raw/statistik_at/ep"
    ep_dst = AOI / "adjacent_euz_proxy_staple_levels/raw/statistik_at/ep"
    ep_dst.mkdir(parents=True, exist_ok=True)
    for p in ep_src.glob("*.json"):
        (ep_dst / p.name).write_bytes(p.read_bytes())
    ss_src = WS / "adjacent_hi_staple_levels/raw/singstat"
    ss_dst = AOI / "adjacent_hi_staple_levels/raw/singstat"
    ss_dst.mkdir(parents=True, exist_ok=True)
    for p in ss_src.glob("*.json"):
        (ss_dst / p.name).write_bytes(p.read_bytes())
    series_dst = ss_dst / "series"
    series_dst.mkdir(exist_ok=True)
    for p in (ss_src / "series").glob("*.json"):
        (series_dst / p.name).write_bytes(p.read_bytes())

    # builder script into both packs
    builder = Path(__file__).resolve()
    (EUZ_DIR / "append_staple_food_densify_s2.py").write_bytes(builder.read_bytes())
    (HI_DIR / "append_staple_food_densify_s2.py").write_bytes(builder.read_bytes())
    (WS / "append_staple_food_densify_s2.py")  # already here

    mirror_pack(EUZ_DIR, "adjacent_euz_proxy_staple_levels")
    mirror_pack(HI_DIR, "adjacent_hi_staple_levels")


if __name__ == "__main__":
    main()
