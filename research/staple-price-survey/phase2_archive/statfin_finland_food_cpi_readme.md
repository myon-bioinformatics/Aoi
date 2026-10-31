# Statistics Finland (StatFin) food CPI index panel

**File:** `statfin_finland_food_cpi_panel.csv`  
**ISO3:** FIN  
**Source:** Statistics Finland PxWeb — Consumer Price Index `khi/15b5.px` (2025=100).  
**API:** `https://statfin.stat.fi/PXWeb/api/v1/en/StatFin/khi/15b5.px`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: 18,371
- Series: 89 food / COICOP 01 tree subgroups
- Span: 1995-01-01 – 2026-09-01 (monthly)
- Unit: index, 2025=100 (as published in 15b5)

## Notes
- Richer than Eurostat HICP single CP011 for FIN → landed.
- No FX conversion; values as published.
- Raw: `raw/statfin_fi/15b5_food_index.csv` (+ meta).

## Columns
iso3, country, series, series_label, coicop, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
