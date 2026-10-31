# ISTAT Italy NIC food CPI index panel

**File:** `istat_italy_food_cpi_panel.csv`  
**ISO3:** ITA  
**Source:** ISTAT SDMX dataflow `167_744_DF_DCSP_NIC1B2015_4` (NIC base 2015=100, national, detailed ECOICOP).  
**API:** `https://esploradati.istat.it/SDMXWS/rest/data/167_744_DF_DCSP_NIC1B2015_4`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: 21,528
- Series: 182 (COICOP 01* food + 11* restaurants/hotels)
- Span: 2016-01-01 – 2025-12-01 (monthly)
- Unit: index, 2015=100
- Key filter: `M.IT.39.4.<COICOP>` (FREQ=M, REF_AREA=IT, DATA_TYPE=39, MEASURE=4 index)

## Notes
- Eurostat HICP FRA/ITA/… is one CP011 series each; ISTAT NIC ECOICOP subgroups are richer → landed.
- Season2 exhausted open **absolute retail** for ITA; this panel is **indexes only**.
- Older dataflow `144_180_DF_DCSP_NICUNOB_3` also has national detailed COICOP but shorter/older base; used NIC1B2015 for current base.
- Raw: `raw/istat_it/NIC1B2015_4_food.xml` (+ `nic1b2015_chunks/`).

## Columns
iso3, country, series, series_label, coicop, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
