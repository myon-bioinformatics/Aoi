# Numeraire candidate catalog — continuous retail / CPI / commodity series beside Big Mac

Date: **2026-10-24 Asia/Tokyo**. Scout + downloads. **No FX conversion. Missing stays missing.**

Goal: series that can sit beside Big Mac as continuous “everyday” price/index companions for high-income / numeraire gaps.

---

## Downloaded this batch (use these)

### A. World Bank Pink Sheet — international commodity (USD levels)

| Series | Freq | Span | Unit | Path |
|---|---|---|---|---|
| Rice Thai 5% / 25% / A.1 / Vietnam 5% | M | 1960–2026-09 (Thai5%); shorter for others | USD/mt | `rice_international_price_panel.csv` |
| Coffee Arabica, Robusta | M | 1960-01–2026-09 | USD/kg | `raw/numeraire/pink_sheet_rice_coffee_sugar_monthly.csv` |
| Sugar World / US / EU | M | 1960-01–2026-09 | USD/kg | same |

- Landing: https://www.worldbank.org/en/research/commodity-markets  
- Raw XLSX: `raw/rice_intl/CMO-Historical-Data-Monthly.xlsx`  
- Best **global USD level** numeraires; not retail CPI.

### B. BLS CPI Average Price Data — USA retail USD levels

| Series ID | Label | Span (this pull) | n | Path |
|---|---|---|---:|---|
| APU0000702111 | Bread, white, pan | 1980-01–2026-09 | 560 | `raw/numeraire/bls_average_price_panel.csv` |
| APU0000709112 | Milk, whole, fortified / gal | 1995-07–2026-09 | 374 | same |
| APU0000717311 | Coffee, ground roast / lb | 1980-01–2026-09 | 520 | same |
| APU0000715211 | Sugar, white / lb | 1980-01–2026-09 | 560 | same |
| APU0000701312 | Rice, white long grain / lb | 1980-01–2026-09 | 535 | same |

- Source: https://www.bls.gov/cpi/factsheets/average-prices.htm  
- Pulled via BLS Public API v2 (decade chunks; bulk `download.bls.gov` returned 403).  
- U.S. city average, NSA. Closest **retail USD** companion to Big Mac (USA).

### C. Eurostat HICP monthly indices (2015=100) — Europe

| COICOP | Series | Countries | Span | Path |
|---|---|---:|---|---|
| CP01113 Bread | `hicp_bread_idx_2015` | 36 ISO3 | 1996-01–2025-12 | `raw/numeraire/eurostat_hicp_bread_milk_coffee_sugar_monthly.csv` |
| CP01141 Whole milk | `hicp_whole_milk_idx_2015` | 34 | 1996–2025 | same |
| CP01181 Sugar | `hicp_sugar_idx_2015` | 36 | 1996–2025 | same |
| CP01211 Coffee | `hicp_coffee_idx_2015` | 36 | 1996–2025 | same |

- Dataset: `PRC_HICP_MIDX` unit `I15`  
- Index (not currency levels) — good for **within-country** real comparisons / co-movement with Big Mac local price; do **not** FX-convert indices.

### D. Japan CPI 品目別 (2020=100) — 全国月次

| Item (code) | Series | Span | n | Path |
|---|---|---|---:|---|
| 食パン (1021) | `jpn_cpi_shokupan_idx_2020` | 1970-01–2026-09 | 681 | `raw/numeraire/japan_cpi_numeraire_items_monthly.csv` |
| 牛乳 (0018) | `jpn_cpi_gyunyu_idx_2020` | 1970-01–2026-09 | 681 | same |
| 砂糖 (1632) | `jpn_cpi_sugar_idx_2020` | 1970-01–2026-09 | 681 | same |
| インスタントコーヒー (1921) | `jpn_cpi_instant_coffee_idx_2020` | 1970-01–2026-09 | 681 | same |
| コーヒー豆 (1922) | `jpn_cpi_coffee_beans_idx_2020` | 1985-01–2026-09 | 501 | same |
| うるち米Ａ / 米類 / パン | rice/bread class | 1970/1975–2026-09 | 681/621 | same |

- e-Stat 2020-base long series, `statInfId=000032103844`  
- Raw wide CSV (cp932): `raw/numeraire/japan_cpi_item_monthly_2020base.csv`  
- Landing: https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00200573&tstat=000001150147&cycle=0&tclass1=000001150151&tclass2=000001150152&tclass3=000001150153&tclass4=000001150156

---

## Scout-only / deferred (downloadable but not pulled as tidy panels here)

| Candidate | Why interesting | Status |
|---|---|---|
| FAO GIEWS FPMA **international** rice/wheat/maize | Official staple benchmarks parallel to Pink Sheet | UI only; no clean CSV API this round |
| AMIS Market Database | Agency staple transparency | Mostly CBS supply/use; not a Thai-5% price dump |
| IRRI World Rice Statistics | Rice-centric | Portal unstable / 404 this round |
| IMF Primary Commodity Prices | Overlaps Pink Sheet | ExternalData URL 404 this round — prefer Pink Sheet |
| GOV.UK “world commodity prices for cereals” CSV | Rehosts Thai 5% etc. | Secondary mirror; Pink Sheet preferred as primary |
| Eurostat HICP **average prices** (prc_hicp_ap) if published for geo | EUR retail levels | Not verified continuous for all items; index path used instead |
| Canada / UK / AUS CPI food subclasses | High-income Big Mac gap countries | Easy in principle via national stats; not pulled this batch |
| Japan 小売物価統計 価格本體 (yen levels) | Yen retail levels vs CPI index | Separate survey from CPI; scout later if level numeraire needed |

---

## Suggested join keys beside Big Mac

| Numeraire family | Join | Caution |
|---|---|---|
| Pink Sheet rice/coffee/sugar | global month (no country) | USD commodity ≠ local retail |
| BLS average prices | USA × month | Levels; definition breaks over decades possible |
| Eurostat HICP subclasses | ISO3 × month | Index; CP codes ≠ HH survey baskets |
| Japan CPI items | JPN × month | 2020=100 index; splice across base years already done by SBJ in long file |
| Eurostat CP11 HFCE share | ISO3 × year | Expenditure share, not price — Engel companion not price numeraire |

---

## Intentionally not duplicated (Season2 mid-fetch)

ICP food PLI; FAO CPI food/cereals country panels; Japan income-quintile Engel; FBS Japan+pre-2010; OECD COICOP food-share long series; PIP poverty lines.
