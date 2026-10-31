# Swiss BFS / SFSO CPI — food & restaurants (LIK25B25)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi Engel companion

## What
Swiss **national** Consumer Price Index detailed basket (structure 2025), monthly index, base **December 2025 = 100**.
Food (COICOP 01*) and restaurant/food-serving (COICOP 11 / 11.1*) positions from sheet `INDEX_m`, levels 2–6.
`series` uses BFS `Code` (e.g. `bfs_cpi_100_1`) so COICOP collisions do not duplicate keys.

Distinct from:
- Eurostat HICP food already in `eurostat_hicp_food_panel.csv` (CHE HICP CP011)
- CHE FOAG bread/flour **levels** in `hi_staple_levels_alt_panel.csv`

## Files
- Panel: `swiss_bfs_food_cpi_panel.csv` (34323 rows)
- Raw: `raw/swiss_bfs/LIK25B25.xlsx`
- Source asset: https://www.bfs.admin.ch/asset/en/36453490 (su-e-05.02.66)

## Coverage
- Geography: Switzerland (`iso3=CHE`)
- Span: **1982-12-01 – 2026-01-01**
- Series: 84 BFS positions (84 COICOP codes)
- Unit: `index_dec2025_eq_100`
- No FX fills; values as published.

## Notes
Official XLSX via BFS DAM master download. SDMX `disseminate.stats.swiss` dataflow probe returned API version/dataflow errors from this box; XLSX path used instead.
