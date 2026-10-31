# CBS Netherlands CPI food index panel

**File:** `cbs_netherlands_food_cpi_panel.csv`  
**ISO3:** NLD  
**Source:** Statistics Netherlands (CBS) OData — `83131ENG` Consumer prices; expenditure categories CPI01* / CPI11*, 2015=100.  
**API:** `https://opendata.cbs.nl/ODataApi/odata/83131ENG/`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: 26,402
- Series: 79 (CPI01 food/non-alc + CPI11 restaurants/hotels)
- Span: 1996-01-01 – 2025-12-01 (monthly)
- Unit: index, 2015=100 (`CPI_1`)

## Notes
- Season2 `adjacent_euz_proxy_staple_levels` already holds NLD **absolute retail** levels; this panel is **CPI indexes only**.
- Richer than Eurostat HICP single CP011 for NLD → landed.
- OData TypedDataSet <10000-record filter limit; pulled in batches of 15 `ExpenditureCategories` keys.
- No FX conversion.
- Raw: `raw/cbs_nl/83131ENG_food_cpi.json` (+ DataProperties).

## Columns
iso3, country, series, series_label, coicop, cbs_key, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
