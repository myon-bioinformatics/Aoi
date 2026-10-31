# Eurostat NAMA_10_CO3_P3 — food share of HFCE (multi-country)

## Panel
- File: `eurostat_nama_food_share_hfce_panel.csv`
- Rows: 2,084
- ISO3: 36 countries (EU/EA aggregates excluded)
- Span: 1975–2025 (annual)
- Measures: CP01 Food & non-alcoholic beverages, and CP011 Food, as **percent of total HFCE** (unit PC_TOT)

## Source
- Eurostat dataset `nama_10_co3_p3` — Household final consumption expenditure by purpose (COICOP 1999)
- Updated in feed: 2026-10-21T23:00:00+0200
- Databrowser: https://ec.europa.eu/eurostat/databrowser/view/nama_10_co3_p3/default/table
- Local raw: `raw/eurostat_nama_food_share/nama_10_co3_p3.json`
- Retrieved: 2026-10-24

## Distinct from
- Season2 **OECD food-share long** (left to Season2) — this is Eurostat **national accounts** COICOP % of HFCE, not OECD HSL/household-survey food-share.
- `eurostat_eating_out_panel.csv` (CP11 restaurants & hotels).
- `housing_cost_share_reference_panel.csv` (CP04 only).
- Stub `engel_global_ref_panel_stub.csv` NAMA food rows (9 geos CHE/CZE/DNK/HUN/NOR/POL/ROU/SWE/TUR, 2000–2023) — this panel is the full multi-country continuous extract.
- Aoi HES survey shares (UK LCFS, ABS, NZL) — different statistical family (survey vs NA).

## Notes
- Status flags preserved where Eurostat marks provisional/estimated (`status_flag`).
- No FX. No fabrication. Values as published.
