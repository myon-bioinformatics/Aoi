# Statbel Belgium food CPI (COICOP) index panel

**File:** `statbel_belgium_food_cpi_panel.csv`  
**ISO3:** BEL  
**Source:** Statbel open data “Indexes by product group” — `CPI All groups.xlsx`.  
**URL:** `https://statbel.fgov.be/en/open-data/indexes-product-group`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **22,939**
- Series: **98** (COICOP 01* food/non-alc + 11* restaurants/hotels)
- Span: **2006-01-01 – 2026-09-01** (monthly)
- Unit: index, **2025=100** (`NM_BASE_YR=2025`)

## Why landed
Eurostat HICP in aoi-phase2 is one `hicp_food_cp011_i15` for BEL (~360 rows). Statbel All-groups file has deep COICOP food subclasses. Season2 notes BEL **absolute** retail exhausted — **indexes OK**.

## Notes
- Weights / inflation columns in source XLSX not retained (index levels only).
- be.STAT L1 COICOP CSV also in raw (`coicop_l1.csv`) — shallow; panel uses All groups XLSX.
- No FX. Raw: `raw/statbel_be/CPI_All_groups.xlsx` (+ zip twin).

## Columns
iso3, country, series, series_label, coicop, coicop_level, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
