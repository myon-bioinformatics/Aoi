# Japan CPI — 食料 / 穀類 / 米類 panel

Built: 2026-10-24 (Asia/Tokyo). Companion to Engel/staple phase-2; **not** FAO CPI.

## Deliverable

- Panel: `japan_cpi_food_cereals_panel.csv`
- Coverage: **1970-01 – 2026-09** monthly (681 months × 4 series) + calendar-year means
- Base: **2025=100** (総務省 2025年基準 長期時系列)
- Region: 全国
- Series: `all_items`（総合）, `food`（食料）, `cereals`（穀類）, `rice`（米類）

## Provenance

| field | value |
|-------|-------|
| source | 総務省 消費者物価指数（2025年基準）長期時系列 / 品目別価格指数 / 全国 / 月次 |
| table_id (statInfId) | `000040482945` |
| download | https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040482945&fileKind=1 |
| page | https://www.e-stat.go.jp/stat-search/files?page=1&stat_infid=000040482945 |
| raw | `raw/japan_cpi/estat_000040482945.csv` (+ `_utf8.csv`) |
| retrieval_date | 2026-10-24 |

Annual rows (`frequency=annual_calendar_mean`) are **calendar-year arithmetic means of monthly index levels** computed in this build (`n_months` records how many months entered the mean; latest year may be partial).

## Also in `raw/japan_cpi/`

- `estat_000040482943.csv` — 2025年基準 **中分類** 長期（食料・穀類列あり）
- `estat_000032103844.csv` — 2020年基準 品目別 長期（2020=100; 2026-12 まで並行提供予定）
- `zmi2025aa.csv` / `zmi2020aa.csv` — STAT.go.jp 短期窓 CSV

## Notes / gaps

1. **米類 vs うるち米**: Panel uses published aggregate **米類** (item code 0004). Sub-items うるち米Ａ/Ｂ are in the raw wide CSV if needed later.
2. **Base change**: Prefer 2025=100 for new work. 2020-base kept in raw for overlap checks; do not mix bases in one chart without rebasing.
3. **Season2 overlap**: Season2 A–F includes **FAO** food/cereals CPI (international). This file is **Japan 総務省 CPI** — complementary, not a double-pull of their lane.
4. No FX conversion, no unit harmonization beyond official index, no gap-filling of missing months (none observed in 1970-01–2026-09 for these four series).
