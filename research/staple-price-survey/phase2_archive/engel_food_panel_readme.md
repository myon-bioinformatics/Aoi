# Engel × food-shares panel (Japan household survey)

Built: 2026-10-24 (Asia/Tokyo). No GohanTrust judgment/rerun touched.

## Deliverable

- Panel: `engel_food_panel_annual.csv`
- Coverage: **2000–2025** (26 continuous calendar years), 二人以上の世帯・全国
- Primary classification: **用途分類** (use classification), 年平均1か月間・円/世帯

## Columns (panel)

| column | meaning |
|--------|---------|
| year | calendar year |
| E_pct / E_fraction | published Engel coefficient (食料/消費支出, 用途) |
| E_pct_calc_food_over_ce | cross-check from levels (should ≈ E_pct) |
| eatout_share_ce | 外食 / 消費支出 |
| eatout_share_food | 外食 / 食料 |
| general_eatout_share_food | 一般外食 / 食料 |
| school_lunch_share_food | 学校給食 / 食料 |
| cereals_share_food | 穀類 / 食料 (Bennett-style within-food share) |
| rice_share_food | 米 / 食料 |
| rice_share_cereals | 米 / 穀類 |
| *_yen_month | underlying levels (円, 月平均) |
| household / region / unit | fixed: 二人以上の世帯 / 全国 / 年平均1か月間 |
| source_* / definition_note | provenance |

Aligns with existing `engel_annual_extended.csv` for E_pct on 2000–2023 (zero mismatches). Panel adds **2024–2025** from the same longtime youto table.

## Official sources downloaded → `raw/engel_food/`

| file | what | e-Stat |
|------|------|--------|
| `youto_longtime_2plus.xls` (+ `.xlsx` convert) | 用途分類 長期時系列 二人以上（月・四半期・年・年度）2000～ | **statInfId=000040270657**, fileKind=4; listing: [長期時系列表](https://www.e-stat.go.jp/stat-search/files?cycle=0&layout=datalist&page=1&tclass1=000001228280&tclass2val=0&toukei=00200561&tstat=000000330001) |
| `youto_annual_levels_extracted.csv` | extracted annual levels used for the panel (sheet 支出金額（年）) | derived |
| `hinmoku_annual_2000plus.csv` (+ `_utf8`) | 品目分類（小分類まで）支出金額（年）2000～2025 | **statInfId=000040270652**, fileKind=1 |
| `yearbook2024_kokurui.xls` | 年報2024 表5 穀類時系列 | statInfId=000040297518 |
| `yearbook2024_gaishoku.xls` | 年報2024 表5 酒類～外食 | statInfId=000040297525 |
| `yearbook2024_engel.xls` | 年報2024 用途 時系列～エンゲル | statInfId=000040297510 |
| `hinmoku_excl_farm_1963_2007.xls` | 農林漁家世帯を除く 品目 1963–2007（参考・未マージ） | statInfId=000040270670 |

Toukei code: 家計調査 `00200561` / tstat `000000330001` / 長期時系列 tclass1 `000001228280`.

Download pattern: `https://www.e-stat.go.jp/stat-search/file-download?statInfId=…&fileKind=…`

## Definitions / caveats

1. **農林漁家**: Panel uses **二人以上の世帯（農林漁家を含む）** from 2000 onward — same universe as `engel_annual_extended` for 2000+. Pre-2000 excl-farm break in the extended Engel file is **not** joined here (no matching eatout/cereals series under that def in this build).
2. **外食**: Published **外食 = 一般外食 + 学校給食**. Delivery/テイクアウト that counts as 調理食品 is **not** in 外食; school lunch **is** in 外食. Panel keeps both aggregate 外食 and the two subshares.
3. **用途 vs 品目**: 用途分類の「食料」は贈答用食料などを「その他の消費支出」側に寄せるため、品目分類の「食料」合計と一致しない。公表エンゲルは用途。本パネルのシェアはすべて**用途分類の同一表**から計算（E と 外食/穀類 で分母が食い違わない）。
4. **品目年次CSV** (`hinmoku_annual_2000plus*`) は参考保管のみ。年間合計ベースで、用途の月平均×12とも完全一致しない。推定の一次系列には使っていない。
5. **分類改定**: 2015・2020・2025 の収支項目分類改定あり（名目増減率が欠ける年あり）。レベル系列は接続表として公表されているが、細品目の中身は改定点で定義が動く可能性がある。穀類・外食の大枠は長期時系列で継続。
6. **住居**: ユーザー指示どおりパネルから除外（住居シェア列なし）。

## Monthly ease

**Built 2026-10-24.** See `engel_food_panel_monthly.csv` + `engel_food_panel_monthly_readme.md`.
Same workbook sheet `支出金額（月）` (statInfId=000040270657); coverage 2000-01–2026-08 in the downloaded file.

## FAO scout (collection deferred)

- Domain: FAOSTAT **FBS** (Food Balances, ~2010–2023 current vintage; older FBSH for 1961–2013 legacy).
- Element of interest: **Food supply [kcal/capita/day]** (and optionally protein/fat).
- API base: `https://fenixservices.fao.org/faostat/api/v1` — e.g. `GET /en/data/FBS?output_type=csv&area=…&element=…&year=…` (Japan area code typically **351** — confirm at pull time).
- Bulk: `https://bulks-faostat.fao.org/production/` catalog `datasets_E.json`; normalized zip e.g. `FoodBalanceSheets*_E_All_Data_(Normalized).zip`.
- Catalog page: https://data.apps.fao.org/catalog/dataset/2f264bb6-1238-459a-bf8b-0e2d0a16804a
- Join key to this panel: **calendar year + country=Japan**; household Engel is national HH survey, FAO is national food supply — not the same micro unit; join is macro year-level only. USDA / World Bank Engel international series (if used later) join on country-year, not to this Japan HH panel’s shares.
- **Not downloaded this turn.**

## Related local files (do not overwrite for GohanTrust)

- `engel_annual_extended.csv` — E only, used for alignment check
- GohanTrust panels/judgment — untouched
