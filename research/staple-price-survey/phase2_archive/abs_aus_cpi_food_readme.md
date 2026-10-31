# ABS Australia CPI food subgroups (monthly indexes)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi companion collect

## What
Australia **Consumer Price Index** food and meals-out subgroups — monthly **index numbers** (original, weighted average of eight capital cities) from the ABS Data API (`ABS,CPI,2.0.0`).

**Distinct from** `hi_staple_levels_alt_panel.csv` AUS block, which is the discontinued **June 2011** ABS 6403.0.55.001 average *retail price levels* snapshot (bread/milk/eggs etc. in AUD).

## Files
- Panel: `abs_aus_cpi_food_panel.csv` (~3,879 rows; 36 index codes)
- Raw: `raw/abs_cpi_food/cpi_food_subgroups_long.csv` (+ codelist/structure XML)
- API: https://data.api.abs.gov.au/rest/data/ABS,CPI,2.0.0/
- Release: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release

## Coverage (selected)
Food & non-alcoholic beverages group; bread/cereals (incl. bread, breakfast cereals); meat & seafoods; dairy (milk/cheese); eggs; fruit & vegetables; oils & fats; coffee/tea/cocoa; non-alcoholic beverages; snacks & confectionery; **meals out and take away** (restaurant meals; take away and fast foods); plus All groups CPI for context.

Span observed: **2017-09 – 2026-08** (series start dates differ by index; many food ECs begin with the monthly CPI redesign — check per `index_code`).

## Notes
- Measure = Index numbers; TSEST = Original; REGION = Australia (50); FREQ = Monthly.
- Reference base period as published by ABS in the response (`base_period` column; recent releases re-referenced, e.g. Sep 2025 = 100).
- No FX. No fabricated levels. Missing observations omitted.

## Frequency / span
| frequency | what | typical span in panel |
|---|---|---|
| monthly | Food expenditure classes (bread, milk, meat ECs, fruit/veg, oils, coffee, etc.) | **2017-09 – 2026-08** |
| monthly | Group Food / meals-out / All groups (short window in monthly dataflow) | **2024-04 – 2026-08** |
| quarterly | All groups + Food & non-alcoholic beverages + Meals out / Restaurant / Takeaway | **1980-Q1 – 2026-Q2** |

Quarterly group series were added because the monthly dataflow only returned ~2024-04+ for those group codes after the monthly CPI redesign/re-reference. EC monthly series remain the continuous companion beyond the discontinued 2011 ABS retail *level* snapshot.
