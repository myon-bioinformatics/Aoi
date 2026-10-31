# Statistics Norway (SSB) CPI — food subgroups (table 03013)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi Engel companion

## What
Norway **national** CPI by COICOP consumption group, monthly index **2015 = 100**.
Selected food, non-alcoholic beverages, and restaurant groups (01*, 11.1*) via SSB JSON-stat API.

Distinct from Eurostat HICP food (`eurostat_hicp_food_panel.csv`, NOR). Retail **levels** for NOR remain open/miss (Season2 `adjacent_hi_staple_levels` also missed NOR; Aoi does not claim exclusive HI levels).

## Files
- Panel: `ssb_norway_food_cpi_panel.csv` (12240 rows)
- Raw: `raw/ssb_no/ssb_03013_food_kpi.csv`, `meta_03013.json`
- API: https://data.ssb.no/api/v0/en/table/03013

## Coverage
- Geography: Norway (`iso3=NOR`)
- Span: **1979-01-01 – 2025-12-01**
- Series: 34 groups
- Unit: `index_2015_eq_100`
- No FX.
