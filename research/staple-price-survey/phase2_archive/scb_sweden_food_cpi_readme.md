# SCB Sweden food CPI (COICOP) index panel

**File:** `scb_sweden_food_cpi_panel.csv`  
**ISO3:** SWE  
**Source:** Statistics Sweden (SCB) PxWebApi — table `KPI2020COICOPM` (Consumer Price Index, COICOP, 2020=100, monthly).  
**API:** `https://api.scb.se/OV0104/v1/doris/en/ssd/PR/PR0101/PR0101A/KPI2020COICOPM`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: 43,443
- Series: 83 COICOP food / related subgroups
- Span: 1980-01-01 – 2026-09-01 (monthly)
- Unit: index, 2020=100

## Notes
- Season2 exhausted open **absolute retail price levels** for SWE; this panel is **indexes only**.
- Eurostat HICP in aoi-phase2 is one `hicp_food_cp011_i15` per ISO3; SCB national COICOP subgroups are richer → landed.
- No FX conversion; values as published.
- Raw: `raw/scb_se/KPI2020COICOPM_food_index.csv` (+ meta).

## Columns
iso3, country, series, series_label, coicop, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
