# UK ONS average retail food / eating-out item prices

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi companion collect

## What
United Kingdom **experimental average retail prices** for CPIH-basket food and restaurants/hotels items from the ONS Shopping Prices Comparison Tool (pre-2025-update archive).

## Files
- Panel: `uk_ons_avg_retail_food_panel.csv` (~14,290 rows)
- Raw: `raw/uk_ons/` (`avgprice.csv`, `metadata.csv`, `datadownload.xlsx`, growth/chained helpers, README)
- Primary archive: https://github.com/ONSvisual/cpi-items-actions-archive-mar25
- Official adhoc landing: https://www.ons.gov.uk/economy/inflationandpriceindices/adhocs/2724shoppingpricescomparisontooldatadownloadbeforethe2025update

## Coverage
| Block | Items | Span |
|---|---:|---|
| COICOP2 Food and non-alcoholic beverages | 142 | 2018-01 – 2025-01 |
| COICOP2 Restaurants and hotels | 36 | 2018-01 – 2025-01 |

## Notes
- Values are ONS experimental **average prices** (GBP) designed to track price change; absolute levels are indicative, not exact shelf prices.
- Archive ends **January 2025**. From March 2026 ONS no longer releases individual price quotes for COICOP Divisions 1–2 where scanner data are integrated.
- Alcoholic beverages / tobacco under other COICOP2 codes are **excluded** from this food companion panel.
- Licence: Open Government Licence v3.0. No FX. Missing months omitted (wide→long dropna).
