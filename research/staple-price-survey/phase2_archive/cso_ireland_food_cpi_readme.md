# CSO Ireland food CPI (ECOICOP) detailed sub-indices panel

**File:** `cso_ireland_food_cpi_panel.csv`  
**ISO3:** IRL  
**Source:** CSO Ireland PxStat table **CPM24** (Consumer Price Index by Detailed Sub Indices; replaces CPM19).  
**API:** `https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/CPM24/JSON-stat/2.0/en`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **29,035**
- Series: **84** (CP01* food/non-alc + CP11* restaurants/accommodation)
- Span: **1996-11-01 – 2026-09-01** (monthly)
- Unit: index, **December 2023 = 100** (CSO rebase note in CPM24)

## Why landed
Eurostat HICP in aoi-phase2 is one `hicp_food_cp011_i15` for IRL (~360 rows). CPM24 has deep ECOICOP food subclasses.

## Notes
- Statistic kept: `CPM24C01` index only (MoM/YoY % omitted).
- Season2 `adjacent_euz_proxy_staple_levels` holds IRL **absolute retail** levels; this panel is **CPI indexes only**.
- Archived CPM01/CPM03 also in `raw/cso_ie/` (longer calendar for coarse groups) — not merged (different code scheme / bases).
- No FX. Raw: `raw/cso_ie/CPM24.json` (+ CPM20/CPM01/CPM03 snapshots).

## Columns
iso3, country, series, series_label, coicop, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
