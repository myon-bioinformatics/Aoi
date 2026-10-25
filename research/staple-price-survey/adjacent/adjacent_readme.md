# adjacent — A–F fill-in pack (staple-price survey)

Retrieved: 2026-10-24 Asia/Tokyo

## Hard rules (confirmed)

- No foreign-exchange conversion.
- No unit/pack homogenization (units recorded as published).
- No gap-filling / interpolation / invented values (PIP `is_interpolated=true` excluded).
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value` (estimated_value left empty).
- Families kept separable by variable prefix.
- Working–Leser slopes NOT estimated; Orshansky / normative multipliers NOT mixed into Engel rows.

## Universe

56 ISO3 codes from `countries_iso3.txt` (includes EUZ). EUZ kept only when a source publishes a euro-area aggregate (Eurostat EA*, OECD EA20).

## Families

### A. ICP food / bread-cereals PLI & expenditure shares

- Source: World Bank ICP API `sources/90` (2017 & 2021 benchmarks).
- Headings: `1101000` Food & non-alcoholic beverages; `1101100` FOOD; `1101110` Bread and cereals.
- Measures → variables: `PX.WL`→`icp_pli_*`; `AICZS`→`icp_exp_share_aic_*`; `ZS`→`icp_exp_share_gdp_*`; `PCAP.PP`→`icp_exp_pcap_ppp_*`.
- Null ICP observations dropped (e.g. some AICZS food cells).

### B. FAO food CPI

- Source: FAOSTAT CP normalized bulk.
- `fao_cpi_food` (2015=100), monthly where published; `fao_food_price_inflation` YoY %.
- **No cereals-specific CPI** in this FAOSTAT domain (documented; see missing.md).

### C. Japan household survey Engel by income quintile

- Source: e-Stat 家計調査 年報 二人以上の世帯, 年間収入五分位 (2018–2024).
- `food_share_by_income_quintile_qu1`…`qu5` (+ `_avg`) = 食料/消費支出×100 (%).
- Also `mean_consumption_expenditure_by_income_quintile_*` and `mean_food_expenditure_*` in JPY/month.
- **Definition break vs Eurostat reinforcement**: Eurostat uses COICOP CP01 per mille; Japan uses 食料 % of 消費支出 (includes 外食 within 食料).

### D. FAO FBSH Japan + historical Bennett

- Source: FAOSTAT FBSH (historical food balances).
- Levels: `food_supply_kcal_{total,cereals,roots}_fbsh`.
- Shares: `cereal_calorie_share_fbsh`, `roots_tubers_calorie_share_fbsh`, `bennett_starchy_calorie_share_fao_fbsh_derived` = (2905+2907)/2901×100.
- **Japan present** in FBSH (1961–2013). Modern FBS (2010+) still has **no Japan** in this pull (see missing.md).

### E. PIP poverty reference (+ normative notes)

- Source: PIP API headcount / poverty gap / mean welfare at $2.15 / $3.65 / $6.85 lines.
- Variables `pip_headcount_ratio_*`, `pip_poverty_gap_*`, `pip_mean_welfare_ppp_*`.
- Normative poverty food-basket multipliers beyond USA: **not invented as data rows** — see `adjacent_missing.md`.

### F. Longer Engel / food-share time series

- OECD: derived `engel_share_food_oecd` (CP01/_T), `engel_share_food_only_oecd` (CP011/_T), `engel_share_nonalc_bev_oecd` (CP012/_T) from published LCU current prices (within-currency ratio, not FX).
- Eurostat: `engel_share_food_eurostat_coicop` etc. from `nama_10_co3_p3` PC_TOT.
- Names chosen to avoid collision with main-survey USDA Engel.

## Coverage (countries hit / 56)

- **A_icp**: 53 / 56 — 1155 rows
- **B_fao_cpi**: 54 / 56 — 33594 rows
- **C_jp_quintile**: 1 / 56 — 126 rows
- **D_fbsh_bennett**: 52 / 56 — 15585 rows
- **E_pip**: 47 / 56 — 9585 rows
- **F_engel_ts**: 22 / 56 — 2167 rows

## Variable dictionary (prefixes)

| Prefix / pattern | Family | Unit (typical) |
|-------------------|--------|----------------|
| `icp_pli_*` | A | PLI World=100 |
| `icp_exp_share_aic_*` | A | % of AIC |
| `icp_exp_share_gdp_*` | A | % of GDP |
| `icp_exp_pcap_ppp_*` | A | PPP US$ / capita (as published) |
| `fao_cpi_food` | B | index 2015=100 |
| `fao_food_price_inflation` | B | % YoY |
| `food_share_by_income_quintile_*` | C | % of 消費支出 (JPN) |
| `mean_*_expenditure_by_income_quintile_*` | C | JPY / household / month |
| `food_supply_kcal_*_fbsh` | D | kcal/capita/day |
| `*_calorie_share_fbsh` / `bennett_starchy_calorie_share_fao_fbsh_derived` | D | % of dietary energy |
| `pip_*` | E | proportion or PPP$/day |
| `engel_share_*_oecd` | F | % of household FCE |
| `engel_share_*_eurostat_coicop` | F | % of HH consumption |

## Totals

- Rows: 62212
- Distinct variables: 52

## Rebuild

```bash
python3 /workspace/staple-price-survey/adjacent/build_adjacent.py
```

Raw extracts live under `adjacent/raw/`.

