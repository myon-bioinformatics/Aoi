#!/usr/bin/env python3
"""Build adjacent_subscription_engel_shares vertical pack from raw/ tidy panels (stdlib only).

Values are as published (local currency, PPS, or percent). No FX conversion.
"""
import csv, gzip, io, json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "raw"
NAME = "adjacent_subscription_engel_shares"
COLS = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
EU2 = {"EL": "GRC", "UK": "GBR"}
ISO2 = {"AL":"ALB","AT":"AUT","BA":"BIH","BE":"BEL","BG":"BGR","CH":"CHE","CY":"CYP","CZ":"CZE","DE":"DEU","DK":"DNK","EE":"EST","EL":"GRC","ES":"ESP","FI":"FIN","FR":"FRA","HR":"HRV","HU":"HUN","IE":"IRL","IS":"ISL","IT":"ITA","LI":"LIE","LT":"LTU","LU":"LUX","LV":"LVA","ME":"MNE","MK":"MKD","MT":"MLT","NL":"NLD","NO":"NOR","PL":"POL","PT":"PRT","RO":"ROU","RS":"SRB","SE":"SWE","SI":"SVN","SK":"SVK","TR":"TUR","UK":"GBR","XK":"XKX","EU27_2020":"EU27","EU28":"EU28","EA20":"EA20","EA19":"EA19","EA":"EA","EU":"EU","EU27_2007":"EU27_2007","EA12":"EA12","EU15":"EU15","EA18":"EA18"}

def iso(g):
    return ISO2.get(g, g)

def rd(n):
    with open(RAW / n, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def row(c, y, var, v, unit, src, note=""):
    if v in ("", None, "n.a."):
        return None
    return {"country": c, "date": f"{y}-12-31", "year": str(y), "variable": var,
            "value": str(v), "unit": unit, "source": src, "note": note, "estimated_value": ""}

def build():
    out = []
    for r in rd("bls_ce_streaming_audio_panel.csv"):
        k = r["item"].lower().replace(",", "").replace(" ", "_")
        out += [row(r["country"], r["year"], f"bls_ce:{k}:mean", r["mean_usd_annual_per_cu"], "USD_annual_per_consumer_unit", r["source"], "mean over all CUs incl. non-purchasers"),
                row(r["country"], r["year"], f"bls_ce:{k}:share_of_spend", r["share_of_total_spend_pct"], "pct_of_total_expenditures", r["source"]),
                row(r["country"], r["year"], f"bls_ce:{k}:share_of_income", r["share_of_income_pct"], "pct_of_income_before_taxes", r["source"]),
                row(r["country"], r["year"], f"bls_ce:{k}:percent_reporting", r["percent_reporting"], "pct_of_consumer_units", r["source"])]
    for r in rd("bls_ce_entertainment_shares_panel.csv"):
        for col, var, unit in [("entertainment_usd","bls_ce:entertainment:mean","USD_annual_per_consumer_unit"),
                               ("av_equipment_services_usd","bls_ce:av_equipment_services:mean","USD_annual_per_consumer_unit"),
                               ("entertainment_share_of_spend_pct","bls_ce:entertainment:share_of_spend","pct_of_total_expenditures"),
                               ("av_share_of_spend_pct","bls_ce:av_equipment_services:share_of_spend","pct_of_total_expenditures"),
                               ("entertainment_share_of_income_pct","bls_ce:entertainment:share_of_income","pct_of_income_before_taxes")]:
            out.append(row(r["country"], r["year"], var, r[col], unit, r["source"]))
    for r in rd("eurostat_hbs_fees_share_of_total_panel.csv"):
        c = iso(r["geo"]); s = r["source"]
        out += [row(c, r["year"], "eurostat_hbs:fees_subscriptions:mean", r["fees_subscriptions_pps"], "PPS_annual_per_household", s, "TV/radio licence fees, subscriptions, hire (CP09423_09424); not SVOD-only"),
                row(c, r["year"], "eurostat_hbs:fees_subscriptions:share_of_spend", r["fees_share_of_total_spend_pct"], "pct_of_total_consumption", s),
                row(c, r["year"], "eurostat_hbs:culture:share_of_spend", r["culture_share_of_total_spend_pct"], "pct_of_total_consumption", s)]
    for fn, var in [("eurostat_cp094_share_hfce_panel.csv", "eurostat_nama:cp094:share_of_hfce"),
                    ("eurostat_cp09_share_hfce_panel.csv", "eurostat_nama:cp09:share_of_hfce")]:
        for r in rd(fn):
            out.append(row(iso(r["geo"]), r["year"], var, r["value"], "pct_of_HFCE", r["source"], "broader than subscriptions"))
    for r in rd("eurostat_paid_subscription_prevalence_panel.csv"):
        out.append(row(iso(r["geo"]), r["year"], f"eurostat_isoc:{r['indicator']}:{r['indicator_label']}", r["value"], r["unit"], r["source"], "PREVALENCE not expenditure"))
    for r in rd("japan_joukyou_digital_content_panel.csv"):
        out.append(row(r["country"], r["year"], f"mic_joukyou:{r['item']}", r["value"], r["unit"], r["source"], "internet-shopping channel only; two-or-more-person households"))
    for r in rd("statcan_cable_streaming_aggregate_panel.csv"):
        out.append(row(r["country"], r["year"], f"statcan:{r['item']}", r["value"], r["unit"], r["source"], "national aggregate, not per household"))
    out = [o for o in out if o]
    seen = set(); ded = []
    for o in out:
        k = (o["country"], o["year"], o["variable"])
        if k not in seen:
            seen.add(k); ded.append(o)
    ded.sort(key=lambda o: (o["variable"], o["country"], o["year"]))
    return ded

def main():
    rows = build()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    data = buf.getvalue().encode("utf-8")
    (HERE / f"{NAME}_vertical.csv").write_bytes(data)
    with gzip.GzipFile(HERE / f"{NAME}_vertical.csv.gz", "wb", mtime=0) as g:
        g.write(data)
    stats = {"rows": len(rows), "variables": len({r["variable"] for r in rows}),
             "countries": len({r["country"] for r in rows}),
             "years": [min(r["year"] for r in rows), max(r["year"] for r in rows)]}
    (HERE / "_build_stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(stats)

if __name__ == "__main__":
    main()
