# Japan 小売物価統計 — うるち米 (yen / 5kg)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi origin batch 2

## What
Monthly retail prices for **うるち米** from e-Stat 小売物価統計調査（動向編）年次表 第1表.  
Companion to Japan CPI rice **index** (`japan_cpi_food_cereals_panel.csv`) — this file is **yen per 5kg bag**, not an index.

## Files
- Panel: `japan_retail_price_rice_panel.csv`
- Raw annual: `raw/japan_rps_rice/estat_*_YYYY.xlsx` (2015–2025); older years via `rice_monthly_extended.csv` / `raw/rice_annual_*.xls`
- e-Stat file-download (`statInfId`), no API appId required

## Coverage
| Variable | Item | Agg | Span |
|---|---|---|---|
| `japan_rps_uruchi_rice_mean_city_yen_per_5kg` | 1002 | mean of surveyed cities | **1999-01 – 2025-12** |
| `japan_rps_uruchi_rice_mean_city_yen_per_5kg` | 1001 | mean of surveyed cities | **2015-01 – 2025-12** |
| `japan_rps_uruchi_rice_tokyo_yen_per_5kg` | 1001 & 1002 | 東京都区部 | **2015-01 – 2025-12** |

- Unit: **JPY per 5kg bag** (銘柄 as published; 1002 is typically コシヒカリを除く系)
- No FX. No city-level microfile beyond aggregates in panel.
- 2025 months reflect values present in the 2025 annual workbook at retrieval (may include months not yet “final” in survey terms — provenance = e-Stat file).

## Relation to CPI rice
Use CPI for inflation index; use this panel for **level** (yen) and shrinkflation / pack-price comparisons.
