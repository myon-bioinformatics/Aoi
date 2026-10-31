# Engel × food-shares panel — **monthly** (Japan household survey)

Built: 2026-10-24 (Asia/Tokyo). Companion to `engel_food_panel_annual.csv`.

## Deliverable

- Panel: `engel_food_panel_monthly.csv`
- Coverage: **2000-01 – 2026-08** (continuous months present in source workbook)
- Universe: **二人以上の世帯・全国・用途分類**（農林漁家を含む）
- Unit: 1か月間・円/世帯

## Definition alignment with annual panel

| item | monthly | annual (`engel_food_panel_annual.csv`) |
|------|---------|----------------------------------------|
| classification | 用途分類 | 用途分類（same workbook） |
| household / region | 二人以上 / 全国 | same |
| 外食 | 一般外食 + 学校給食 | same |
| E | published エンゲル係数(％) on monthly sheet | published annual E |
| 穀類 / 米 / 外食 shares | level ÷ 食料 or 消費支出 | same formulas |

Source workbook: `raw/engel_food/youto_longtime_2plus.xlsx` sheet **`支出金額（月）`**  
e-Stat: **statInfId=000040270657**, fileKind=4  
Download: https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040270657&fileKind=4  
Listing: https://www.e-stat.go.jp/stat-search/files?cycle=0&layout=datalist&page=1&tclass1=000001228280&tclass2val=0&toukei=00200561&tstat=000000330001

Annual is **not** the arithmetic mean of these monthly levels in the official tables (調査の年平均は別掲の「支出金額（年）」）。Share columns here are computed from monthly levels the same way as the annual panel’s share columns.

## Columns

Same share/level family as the annual panel, plus `year`/`month`/`ym`, `bread_yen_month`, `noodles_yen_month`, and provenance (`source`, `table_id`, `url`, `page_url`, `raw_file`, `retrieval_date`).

## Status

**Available — not blocked.** Monthly 外食 / 食料 / 穀類 / 米 / エンゲル are continuous in the longtime youto file from 2000-01 onward (through latest month in the downloaded workbook).
