# Statistik Austria VPI food CPI index panel

**File:** `statistik_austria_food_cpi_panel.csv`  
**ISO3:** AUT  
**Source:** Statistik Austria Open Data — VPI COICOP18 Messzahlen (bases 2015, 2020, 2025).  
**URLs:** `https://data.statistik.gv.at/data/OGD_vpi15c18_VPI_2015COICOP18_1.csv` (and vpi20 / vpi25 siblings)  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: 16,224
- Series: 236 (food 01* + restaurants 11* × three bases)
- Span: 2016-01-01 – 2026-09-01 (monthly; base-specific windows)
- Unit: `index_2015_eq_100` / `index_2020_eq_100` / `index_2025_eq_100` (not spliced across bases)
- Value field: `F-VPIMZBM` (Messzahl / index level)

## Notes
- Eurostat HICP AUT is one CP011 series; national VPI COICOP18 subgroups are richer → landed.
- Season2 exhausted open **absolute retail** for AUT; this panel is **indexes only**.
- Destatis Germany GENESIS API required authenticated credentials from this box (401 Guest) — skipped this turn; Austria fills the DEU/AUT slot.
- Raw: `raw/statistik_at/OGD_vpi{15,20,25}c18_*.csv` + meta JSON.

## Columns
iso3, country, series, series_label, coicop, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
