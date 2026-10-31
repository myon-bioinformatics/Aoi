# Japan 小売物価統計 — numeraire foods (yen levels)

**Retrieved / extended:** 2026-10-24 Asia/Tokyo · Aoi origin companion batch

## What
Monthly **yen retail prices** from e-Stat 小売物価統計調査（動向編）年次表 第1表 for numeraire / staple-adjacent items beside rice:

| item_code | label | unit in survey | panel unit |
|---|---|---|---|
| 1021 | 食パン | 1kg | `JPY_per_kg` |
| 1031 | ゆでうどん | 1kg | `JPY_per_kg` |
| 1303 | 牛乳（紙パック） | 1本・1000mL | `JPY_per_1000mL` |
| 1341 | 鶏卵 | 1パック・10個 | `JPY_per_10pack` |

Companion to `japan_retail_price_rice_panel.csv` (うるち米) and to Japan CPI **indices** in `japan_cpi_food_cereals_panel.csv` / `raw/numeraire/japan_cpi_numeraire_items_monthly.csv` — this file is **price levels**, not indices.

## Files
- Panel: `japan_retail_price_numeraire_panel.csv` (**2,016** rows)
- Raw 2015–2025: `raw/japan_rps_numeraire/estat_*_{year}_part{01|04}.xls(x)`
- Raw **2005–2014 extension**: `raw/japan_rps_numeraire/pre2015/estat_*_{year}_part{01|04}.xls`
  - part01 ≈ 米～穀類麺（食パン・ゆでうどん）
  - part04 ≈ 肉～鶏卵／牛乳（紙パック 1303・鶏卵 1341）
- e-Stat file-download (`statInfId`), no API appId

## Coverage
| Variable | Agg | Span |
|---|---|---|
| `japan_rps_shokupan_*` | mean city / 東京都区部 | **2005-01 – 2025-12** |
| `japan_rps_yude_udon_*` | mean city / 東京都区部 | **2005-01 – 2025-12** |
| `japan_rps_milk_carton_*` | mean city / 東京都区部 | **2005-01 – 2025-12** (item **1303** 紙パック throughout) |
| `japan_rps_eggs_*` | mean city / 東京都区部 | **2005-01 – 2025-12** |

- No FX. Missing city-months omitted (not filled). Specs follow published 基本銘柄.
- Pre-2015 blocker: **none** for these four items — yearly 第1表 long tables exist continuously back through at least 2005 on e-Stat (older years not pulled this pass).
- Season2 is collecting high-income **non-Japan** NSO retail levels — this Japan pack does not overlap that lane.

## Relation to rice panel
Same survey table family and tidy schema as `japan_retail_price_rice_panel.csv`. Rice remains in its own file; do not merge without aligning pack units.
