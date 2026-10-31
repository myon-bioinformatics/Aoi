# Japan CPI — 中分類 food + 外食 (meals-out) panel

Built: 2026-10-24 (Asia/Tokyo). Companion to Engel/staple phase-2; **price indexes**, not HH expenditure shares.

## Deliverable

- Panel: `japan_cpi_food_meals_midclass_panel.csv`
- Coverage: **1970-01 – 2026-09** monthly (12939 monthly rows) + calendar-year means (1083 annual rows)
- Rows total: **14022**
- Base: **2025=100** (総務省 2025年基準 長期時系列 中分類)
- Region: 全国
- Series (19): all_items + food mid-classes through **meals_out（外食, code 0042）** — cereals, fish, meat, dairy_eggs, vegetables_seaweed, fruit, oils_seasonings, confectionery, cooked_food, beverages, alcoholic_beverages, fresh_* re-listings, food_ex_fresh

## Provenance

| field | value |
|-------|-------|
| source | 総務省 消費者物価指数（2025年基準）長期時系列 / **中分類指数** / 全国 / 月次 |
| table_id (statInfId) | `000040482943` |
| download | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040482943&fileKind=1 |
| page | https://www.e-stat.go.jp/stat-search/files?page=1&stat_infid=000040482943 |
| raw | `raw/japan_cpi_meals/estat_000040482943_utf8.csv` (copy of `raw/japan_cpi/estat_000040482943_utf8.csv`) |
| retrieval_date | 2026-10-24 |

Distinct from `japan_cpi_food_cereals_panel.csv` (品目別 table `000040482945`: only all_items/food/cereals/rice). This panel exposes the full food **中分類** tree including **外食** price index (not Season2 eating-out *expenditure share*).

Annual rows (`frequency=annual_calendar_mean`) are calendar-year arithmetic means of monthly index levels computed in this build (`n_months` = months in mean; latest year may be partial).

## Notes / gaps

1. **Price index only** — not HH 外食支出シェア (Japan core Engel panels / Season2 eating-out shares).
2. No FX, no gap-fill, no rebasing.
3. Fresh-food re-listings (`*_re`) are 再掲 subgroups published in the same midclass table.
