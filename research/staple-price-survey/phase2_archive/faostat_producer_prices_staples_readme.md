# FAOSTAT producer prices — rice / wheat / maize

Date: **2026-10-24 Asia/Tokyo**

| Field | Detail |
|---|---|
| Panel | `faostat_producer_prices_staples.csv` |
| Raw | `raw/faostat_pp/Prices_E_All_Data_(Normalized).zip` (+ extracted CSV) |
| Source | FAOSTAT domain **PP** (Producer Prices) |
| Bulk URL | https://bulks-faostat.fao.org/production/Prices_E_All_Data_(Normalized).zip |
| Landing | https://www.fao.org/faostat/en/#data/PP |
| Items | 15 Wheat; 27 Rice; 56 Maize (corn) |
| Elements | 5530 LCU/t; 5531 SLC/t; 5532 USD/t (FAO-published); 5539 PPI 2014–2016=100 |
| Frequency | Annual (`Months Code` 7021) |
| Rows | 36,627 |
| Countries (ISO3) | 156 |
| Years | 1991–2025 |
| Schema | iso3, year, indicator, value, unit, source_url, note |
| Rules | No FX by us; USD column is **as published by FAOSTAT**, not converted here |
| Big Mac universe | 50/56 with ≥1 staple PP row |

Full download path recorded in `raw/faostat_pp/DOWNLOAD_NOTE.md`.
