# Eurostat HICP food (CP011) monthly panel

Date: **2026-10-24 Asia/Tokyo**. Companion to Africa/MENA food CPI batch. **No FX.**

File: `/workspace/aoi-phase2/eurostat_hicp_food_panel.csv`  
Raw: `/workspace/aoi-phase2/raw/africa_mena_cpi/prc_hicp_midx_cp011.tsv.gz` (+ JSON window copy)

## What

Monthly **HICP Food** index, COICOP **CP011**, unit **I15 (2015=100)**, Eurostat `PRC_HICP_MIDX`.

This is **not** the eating-out / restaurants share panel (`eurostat_eating_out_panel.csv`, CP11 HFCE shares).  
Subclass bread/milk/sugar/coffee numeraire items remain under `raw/numeraire/`; this file is the **aggregate food CP011** tidy panel.

## Coverage

- Geos: 44 codes in raw TSV (EU aggregates + countries); **37 country ISO3** in tidy panel plus aggregates (`is_aggregate=1`)
- Time: **1996-01 – 2025-12** (360 months; missing early cells left out, not filled)
- Includes **TUR** (TR); Africa/MENA national targets outside Eurostat scope are in `africa_mena_national_food_cpi_panel.csv`
- Rows: **14211**

## Columns

`iso3, geo, series, series_label, frequency, year, month, date, value, unit, base_year, coicop, is_aggregate, source, source_url, note, retrieval_date`

## Source

`https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/PRC_HICP_MIDX/M.I15.CP011.?format=TSV&compressed=true`

## Notes

- Observation flags (e.g. `d`) stripped; numeric token kept.
- Aggregates (EU/EA/EEA) kept with `is_aggregate=1` for convenience; filter them out for country panels.
- Catalog tag: **Aoi origin batch Africa/MENA**.
