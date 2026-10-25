#!/usr/bin/env python3
"""Easy-only densify: IRL CPM12 + ESP INE 25169/73844 + FRA INSEE food idbanks (+ optional QAT NPC)."""
from __future__ import annotations

import csv
import gzip
import json
import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

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
WS = Path("/workspace/staple-price-survey")
AOI = Path("/workspace/repos/Aoi/research/staple-price-survey")
EUZ_DIR = AOI / "adjacent_euz_proxy_staple_levels"
HI_DIR = AOI / "adjacent_hi_staple_levels"
EUZ_CSV = EUZ_DIR / "adjacent_euz_proxy_staple_levels_vertical.csv"
HI_CSV = HI_DIR / "adjacent_hi_staple_levels_vertical.csv"
WS_EUZ = WS / "adjacent_euz_proxy_staple_levels"


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


def append_unique(existing, new):
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


def _parse_eu_num(s: str):
    s = (s or "").strip().replace(".", "").replace(",", ".")
    if not s or s in (".", "..", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def from_irl_cpm12() -> list[dict]:
    path = WS_EUZ / "raw/cso/CPM12.json"
    if not path.exists():
        path = EUZ_DIR / "raw/cso/CPM12.json"
    j = json.loads(path.read_text(encoding="utf-8"))
    mapping = {
        "10300": ("roast_beef_kg", "EUR per kg", "Roast beef - topside or rib per kg"),
        "10310": ("sliced_diced_beef_kg", "EUR per kg", "Sliced / diced beef pieces per kg"),
        "10320": ("pork_loin_chops_kg", "EUR per kg", "Pork loin chops per kg"),
        "10330": ("pork_steak_kg", "EUR per kg", "Pork steak per kg"),
        "10370": ("uncooked_chicken_1_6kg", "EUR per 1.6 kg bird", "Uncooked chicken medium size 1.6kg"),
        "10630": ("full_fat_milk_2l", "EUR per 2 litre", "Full fat milk per 2 litre"),
        "10640": ("low_fat_milk_l", "EUR per litre", "Low fat milk per 1 litre"),
        "10730": ("large_eggs_half_dozen", "EUR per half dozen", "Large eggs per half dozen"),
        "10740": ("medium_eggs_half_dozen", "EUR per half dozen", "Medium eggs per half dozen"),
        "10750": ("butter_lb", "EUR per lb", "Butter per lb"),
        "11150": ("white_granulated_sugar_kg", "EUR per kg", "White granulated sugar per 1 kg"),
    }
    dims = j["dimension"]
    ids = j["id"]
    size = j["size"]
    axes = []
    for dim in ids:
        idx = dims[dim]["category"]["index"]
        if isinstance(idx, list):
            axes.append(idx)
        else:
            inv = [None] * len(idx)
            for lab, pos in idx.items():
                inv[pos] = lab
            axes.append(inv)
    src = "https://data.cso.ie (PxStat CPM12 National Average Price; EUR)"
    out = []
    for i, val in enumerate(j["value"]):
        if val is None:
            continue
        try:
            valf = float(val)
        except (TypeError, ValueError):
            continue
        coords = []
        x = i
        for s in reversed(size):
            coords.append(x % s)
            x //= s
        coords = list(reversed(coords))
        lab = {dim: axes[d][coords[d]] for d, dim in enumerate(ids)}
        item = str(lab.get("C02363V03422", ""))
        if item not in mapping:
            continue
        tlist = str(lab.get("TLIST(M1)", ""))
        # CPM12 uses YYYYMM (e.g. 201112) not YYYYMmm
        m = re.match(r"^(\d{4})(\d{2})$", tlist)
        if not m:
            m = re.match(r"^(\d{4})M(\d{2})$", tlist)
        if not m:
            continue
        y, mo = int(m.group(1)), int(m.group(2))
        if mo < 1 or mo > 12:
            continue
        var, unit, label = mapping[item]
        note = (
            f"CSO CPM12 National Average Price; item={item}; as published='{label}'; "
            f"absolute national average retail EUR as published (Ireland — country proxy "
            f"for EUZ Big Mac gap, not euro-area aggregate); {RETRIEVED}"
        )
        out.append(
            row("IRL", f"{y}-{mo:02d}-01", y, f"staple_price:{var}", valf, unit, src, note)
        )
    return out


def from_esp_ine() -> list[dict]:
    mapping_25169 = {
        "01.1.2.1 T Beef (K)": ("beef_kg", "EUR per kg", "Beef (K)"),
        "01.1.2.2 T Pork (K)": ("pork_kg", "EUR per kg", "Pork (K)"),
        "01.1.4.1 T Whole milk (K)": ("whole_milk_kg", "EUR per kg", "Whole milk (K)"),
        "01.1.4.2 T Semi and non-fat milk (L)": (
            "semi_nonfat_milk_l",
            "EUR per litre",
            "Semi and non-fat milk (L)",
        ),
        "01.1.4.7 T Eggs (U)": ("eggs_unit", "EUR per egg", "Eggs (U)"),
        "01.1.5.1 T Butter and other animal fats (K)": (
            "butter_animal_fats_kg",
            "EUR per kg",
            "Butter and other animal fats (K)",
        ),
        "01.1.5.3 T Olive oil (L)": ("olive_oil_l", "EUR per litre", "Olive oil (L)"),
        "01.1.5.4 T Other oils (L)": ("other_oils_l", "EUR per litre", "Other oils (L)"),
        "01.1.8.1 T Sugar (K)": ("sugar_kg", "EUR per kg", "Sugar (K)"),
    }
    mapping_73844 = {
        "01.1.2.1 T (K) Beef and veal": ("beef_veal_kg", "EUR per kg", "Beef and veal (K)"),
        "01.1.4.1 T (L) Whole milk of animal origin": (
            "whole_milk_l",
            "EUR per litre",
            "Whole milk of animal origin (L)",
        ),
        "01.1.4.2 T (L) Skimmed and semi-skimmed milk of animal origin": (
            "skim_semi_milk_l",
            "EUR per litre",
            "Skimmed and semi-skimmed milk (L)",
        ),
        "01.1.4.8 T (U) Eggs": ("eggs_unit_epf", "EUR per egg", "Eggs (U)"),
        "01.1.5.1 T (L) Olive oil": ("olive_oil_l_epf", "EUR per litre", "Olive oil (L)"),
        "01.1.5.4 T (K) Animal butter and other edible animal fat": (
            "butter_animal_fat_kg",
            "EUR per kg",
            "Animal butter and other edible animal fat (K)",
        ),
        "01.1.8.1 T (K) Sugar (from cane and beet)": (
            "sugar_kg_epf",
            "EUR per kg",
            "Sugar from cane and beet (K)",
        ),
    }
    out = []
    path = WS_EUZ / "raw/ine/25169_en.csv"
    if not path.exists():
        path = EUZ_DIR / "raw/ine/25169_en.csv"
    src69 = "https://www.ine.es/jaxiT3/Tabla.htm?t=25169 (valor unitario, EPF/household budget)"
    with path.open(newline="", encoding="utf-8-sig") as f:
        for r in csv.reader(f, delimiter=";"):
            if len(r) < 4:
                continue
            code, metric, period, total = r[0], r[1], r[2], r[3]
            if "Unitary value" not in metric:
                continue
            if code not in mapping_25169:
                continue
            val = _parse_eu_num(total)
            if val is None:
                continue
            try:
                y = int(period)
            except ValueError:
                continue
            var, unit, label = mapping_25169[code]
            note = (
                f"INE table 25169 household budget survey unit value (valor unitario) for {label}; "
                f"code='{code}'; absolute EUR as published (Spain national — country proxy for EUZ "
                f"Big Mac gap, not euro-area aggregate; unit value from expenditure/quantity, not CPI "
                f"store quote); {RETRIEVED}"
            )
            out.append(row("ESP", f"{y}-01-01", y, f"staple_price:{var}", val, unit, src69, note))

    path2 = Path("/tmp/ine73844.csv")
    if not path2.exists():
        path2 = WS_EUZ / "raw/ine/73844_en.csv"
    if not path2.exists():
        path2 = EUZ_DIR / "raw/ine/73844_en.csv"
    if path2.exists():
        dst = WS_EUZ / "raw/ine/73844_en.csv"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if path2.resolve() != dst.resolve():
            shutil.copy2(path2, dst)
        src44 = "https://www.ine.es/jaxiT3/Tabla.htm?t=73844 (EPF unit value extension)"
        with path2.open(newline="", encoding="utf-8-sig") as f:
            for r in csv.reader(f, delimiter=";"):
                if len(r) < 4:
                    continue
                code, metric, period, total = r[0], r[1], r[2], r[3]
                if "unit value" not in metric.lower():
                    continue
                key_code = None
                for k in mapping_73844:
                    if code.strip() == k.strip() or code.rstrip() == k.rstrip():
                        key_code = k
                        break
                if key_code is None:
                    continue
                val = _parse_eu_num(total)
                if val is None:
                    continue
                try:
                    y = int(period)
                except ValueError:
                    continue
                var, unit, label = mapping_73844[key_code]
                note = (
                    f"INE table 73844 EPF unit value for {label}; code='{code.strip()}'; "
                    f"absolute EUR as published (Spain national — country proxy for EUZ Big Mac gap, "
                    f"not euro-area aggregate; unit value from expenditure/quantity, not CPI store "
                    f"quote); {RETRIEVED}"
                )
                out.append(
                    row("ESP", f"{y}-01-01", y, f"staple_price:{var}", val, unit, src44, note)
                )
    return out


def from_fra_insee_food() -> list[dict]:
    path = WS_EUZ / "raw/insee/prix_moyens_food.xml"
    if not path.exists():
        path = EUZ_DIR / "raw/insee/prix_moyens_food.xml"
    mapping = {
        "000442479": ("whole_milk_pasteurised_l", "EUR per litre", "Lait pasteurisé entier (1 litre)"),
        "000442480": ("uht_semi_skimmed_milk_l", "EUR per litre", "Lait UHT demi-écrémé (1 litre)"),
        "000442490": ("butter_extra_fin_250g", "EUR per 250 g", "Beurre extra fin (250 g)"),
        "000442491": ("olive_oil_extra_virgin_l", "EUR per litre", "Huile d'olive 'vierge extra' (1 litre)"),
        "000442493": ("sunflower_oil_l", "EUR per litre", "Huile de tournesol (1 litre)"),
        "000442544": ("sugar_cubes_kg", "EUR per kg", "Sucre en morceaux (1 kg)"),
        "000442452": ("industrial_chicken_kg", "EUR per kg", "Poulet industriel sans label (1 kg)"),
        "000442448": ("pork_fillet_roast_kg", "EUR per kg", "Porc : rôti dans le filet (1 kg)"),
        "000442434": ("beef_rump_kg", "EUR per kg", "Boeuf : rumsteack (1 kg)"),
    }
    src = "https://www.insee.fr (BDM Prix moyens de vente de détail; SDMX SERIES_BDM)"
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    out = []
    for series in root.iter():
        idbank = series.attrib.get("IDBANK")
        if idbank not in mapping:
            continue
        var, unit, label = mapping[idbank]
        for obs in series:
            if "Obs" not in (obs.tag or "") and "TIME_PERIOD" not in obs.attrib:
                continue
            tp = obs.attrib.get("TIME_PERIOD")
            obs_val = obs.attrib.get("OBS_VALUE")
            if not tp or obs_val in (None, "", "NaN"):
                continue
            try:
                valf = float(obs_val)
            except ValueError:
                continue
            m = re.match(r"^(\d{4})-(\d{2})$", tp)
            if not m:
                continue
            y, mo = int(m.group(1)), int(m.group(2))
            note = (
                f"INSEE BDM Prix moyens mensuels — {label}; idbank={idbank}; freq=monthly; "
                f"national metropolitan France absolute average retail EUR as published; "
                f"country proxy for EUZ Big Mac gap (not euro-area aggregate; not CPI/HICP index); "
                f"stopped series retained as published absolute history where applicable; {RETRIEVED}"
            )
            out.append(
                row("FRA", f"{y}-{mo:02d}-01", y, f"staple_price:{var}", valf, unit, src, note)
            )
    return out


def from_qat_npc_food() -> list[dict]:
    """Trivial hi densify from already-downloaded NPC annual average consumer prices."""
    path = WS / "adjacent_household_sku_levels/raw/qat_annual_avg_consumer_prices.csv"
    if not path.exists():
        return []
    # commodity substring -> (var, unit_label)
    want = [
        (
            "Full cream milk in plastic pack kind Al Marai",
            "full_cream_milk_l",
            "QAR per litre",
            "1ltr",
        ),
        (
            "Fresh egg medium size in paper tray",
            "fresh_eggs_30",
            "QAR per 30 eggs",
            "30plate",
        ),
        (
            "Sugar in plastic bag locally packed",
            "sugar_2kg",
            "QAR per 2 kg",
            "2kg",
        ),
        (
            "Corn oil in plastic pack kind Afia",
            "corn_oil_1_8l",
            "QAR per 1.8 litre",
            "1.8ltr",
        ),
        (
            "Frozen Whole Chicken kind Sadia",
            "frozen_whole_chicken_kg",
            "QAR per kg",
            "1kg",
        ),
        (
            "Fresh Whole Chicken Al Waha",
            "fresh_whole_chicken_kg",
            "QAR per kg",
            "1kg",
        ),
        (
            "Australian Mutton",
            "australian_mutton_kg",
            "QAR per kg",
            "1kg",
        ),
    ]
    src = "https://www.psa.gov.qa (NPC Annual Average Consumer Prices; QAR)"
    out = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader, None)
        for r in reader:
            if len(r) < 8:
                continue
            year_s, category, _lfy, commodity, _lsl, unit, _whd, price = r[:8]
            try:
                y = int(year_s)
                valf = float(price)
            except ValueError:
                continue
            for needle, var, unit_out, unit_expect in want:
                if needle.lower() not in commodity.lower():
                    continue
                if unit_expect.lower() not in unit.lower().replace(" ", ""):
                    # unit column may be '1ltr' or '1ltr' with Arabic twin already split
                    pass
                note = (
                    f"PSA/NPC Qatar Annual Average Consumer Prices; category='{category.strip()}'; "
                    f"commodity as published='{commodity.strip()}'; unit='{unit.strip()}'; "
                    f"absolute QAR as published (HI pack densify); {RETRIEVED}"
                )
                out.append(
                    row("QAT", f"{y}-01-01", y, f"staple_price:{var}", valf, unit_out, src, note)
                )
                break
    return out


def main():
    irl = from_irl_cpm12()
    esp = from_esp_ine()
    fra = from_fra_insee_food()
    qat = from_qat_npc_food()
    print(
        json.dumps(
            {
                "irl": len(irl),
                "irl_vars": sorted({r["variable"] for r in irl}),
                "esp": len(esp),
                "esp_vars": sorted({r["variable"] for r in esp}),
                "fra": len(fra),
                "fra_vars": sorted({r["variable"] for r in fra}),
                "qat": len(qat),
                "qat_vars": sorted({r["variable"] for r in qat}),
            },
            indent=2,
        )
    )

    euz = load_csv(EUZ_CSV)
    prior_euz = len(euz)
    euz2, added_euz = append_unique(euz, irl + esp + fra)
    write_csv(EUZ_CSV, euz2)

    hi = load_csv(HI_CSV)
    prior_hi = len(hi)
    hi2, added_hi = append_unique(hi, qat)
    write_csv(HI_CSV, hi2)

    # sync raw into AOI
    for sub in ["cso", "ine", "insee"]:
        src = WS_EUZ / "raw" / sub
        dst = EUZ_DIR / "raw" / sub
        if not src.exists():
            continue
        dst.mkdir(parents=True, exist_ok=True)
        for p in src.iterdir():
            if p.is_file():
                shutil.copy2(p, dst / p.name)

    # copy QAT source into hi raw for provenance
    qat_src = WS / "adjacent_household_sku_levels/raw/qat_annual_avg_consumer_prices.csv"
    if qat_src.exists() and added_hi:
        qat_dst = HI_DIR / "raw/psa_qat"
        qat_dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(qat_src, qat_dst / "qat_annual_avg_consumer_prices.csv")

    by_euz = defaultdict(int)
    for r in euz2:
        by_euz[r["country"]] += 1
    by_hi = defaultdict(int)
    for r in hi2:
        by_hi[r["country"]] += 1
    stats = {
        "euz_prior": prior_euz,
        "euz_added": added_euz,
        "euz_total": len(euz2),
        "euz_by_country": dict(sorted(by_euz.items())),
        "hi_prior": prior_hi,
        "hi_added": added_hi,
        "hi_total": len(hi2),
        "hi_by_country": dict(sorted(by_hi.items())),
    }
    (WS_EUZ / "_append_s3_stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
