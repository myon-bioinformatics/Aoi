# UK ONS CPI / CPIH / RPI food indexes (long series)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi companion collect

## What
Official ONS **index levels and 12-month % rates** for food (and catering) from MM23 — **beyond** the experimental item-level average prices in `uk_ons_avg_retail_food_panel.csv`.

## Series (CDIDs)
| CDID | series | unit |
|---|---|---|
| D7BU | cpi_food_non_alc_bev_index | index 2015=100 |
| D7C8 | cpi_food_index | index 2015=100 |
| D7CU–D7CX | bread/cereals, meat, fish, milk/cheese/eggs | index 2015=100 |
| D7D5 | cpi_catering_services_index | index 2015=100 |
| D7G8 / L55P | CPI / CPIH food YoY % | percent |
| L55O | cpih_food_non_alc_bev_index | index 2015=100 |
| DOBC / CZBH | RPI Food index / YoY % | index Jan1987=100 / percent |

## Files
- Panel: `uk_ons_cpi_rpi_food_index_panel.csv` (~6,420 rows)
- Raw generator CSVs: `raw/uk_ons_cpi_food/`
- Example: https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7bu/mm23

## Coverage
Span varies by CDID (RPI food long; CPI from mid-1990s). Rows: monthly and annual observations as published.

## Notes
- Open Government Licence. No FX. Mistaken non-food CDIDs (e.g. cigarettes) not included in panel.
