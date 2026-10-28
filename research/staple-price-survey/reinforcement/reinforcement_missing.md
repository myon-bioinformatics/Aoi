# Reinforcement data — missing / not obtained

Retrieval date: **2026-10-24 Asia/Tokyo**

## By family

### Bennett

| Gap | Reason |
|-----|--------|
| `EUZ` | Aggregate euro area is not a FAO / OWID country row. |
| Singapore (`SGP`) starchy calorie share | No valued OWID share in downloaded chart; check FAO FS 21012 row presence separately if needed. |
| Japan in FAO Food Balances (2010–) kcal extract | Japan (`m49=392`) did **not** appear in the FAO catalog BigQuery pull for items 2901/2905/2907 used here. Japan **does** appear in FS indicator 21012 (early years) and in OWID. |
| FAO historical FBSH 1961–2013 | Catalog SQL for the historical package returned the same 2010–2023 extract; pre-2010 FBS kcal components were **not** successfully downloaded. OWID/FS cover ~2001–2021/22 for shares. |
| Split “staple food budget share” beyond USDA 1996 breads & cereals | Few cross-country published series separate staples from total food expenditure on a comparable basis. |
| High-frequency / monthly Bennett shares | Not published; annual / 3-year averages only. |

### Working–Leser

| Gap | Reason |
|-----|--------|
| Published country-level Working–Leser coefficients (`w = α + β log x`) | No authoritative multi-country table ingested this pass; income **elasticities** (USDA) and **quintile food shares** (Eurostat) provided instead so slopes can be fitted later. |
| Food share by income decile/quintile outside Europe | Eurostat HBS covers European reporters only. Overlap with Big Mac universe: CZE, DNK, GBR, HUN, NOR, POL, ROU, SWE, TUR. |
| Japan household survey Engel by income quintile | e-Stat automated download hit the wrong table (nursing-care file). Needs a targeted e-Stat pull (家計調査 用途分類・年間収入五分位). |
| World Bank PIP / ICP 2021 household food shares by country | Not bulk-downloaded this pass (DataBank UI / API friction). USDA 1996 total food share and main-survey Engel remain the expenditure-side anchors. |
| `working_leser_coeff` rows | Intentionally **not** estimated by us. |

### Orshansky-type

| Gap | Reason |
|-----|--------|
| Non-US official food-basket multipliers | Many countries use cost-of-basic-needs with reference-group Engel inverses, but multipliers are method-specific and not always published as a single N. USA classic 3 / 3.7 documented only. Chile/Moldova/EU ABSPO noted in research but not encoded as comparable `poverty_food_multiplier` rows without a clear published N. |
| Current US SPM / official poverty updates as multipliers | Official US poverty is still historically Orshansky-based with CPI updates; we record the **original normative multiplier**, not a re-estimated Engel. |

## Universe countries missing Bennett-related rows entirely

- EUZ

## Universe countries missing WL-related rows entirely

- ARE
- CRI
- EUZ
- GTM
- HND
- KOR
- NIC
- TWN

## Row counts by variable (all countries in file)

- `bennett_starchy_calorie_share`: 3,698
- `bennett_starchy_calorie_share_owid`: 1,096
- `bennett_starchy_calorie_share_fao_fbs_derived`: 724
- `cereal_calorie_share`: 724
- `food_supply_kcal_cereals`: 724
- `food_supply_kcal_roots_tubers`: 724
- `food_supply_kcal_total`: 724
- `roots_tubers_calorie_share`: 724
- `food_share_by_income_quintile_qu1`: 162
- `food_share_by_income_quintile_qu2`: 162
- `food_share_by_income_quintile_qu3`: 162
- `food_share_by_income_quintile_qu4`: 162
- `food_share_by_income_quintile_qu5`: 162
- `mean_consumption_expenditure_pps_ae_qu1`: 162
- `mean_consumption_expenditure_pps_ae_qu2`: 162
- `mean_consumption_expenditure_pps_ae_qu3`: 162
- `mean_consumption_expenditure_pps_ae_qu4`: 162
- `mean_consumption_expenditure_pps_ae_qu5`: 162
- `income_elasticity_cereals_usda2005`: 138
- `income_elasticity_food_broad_usda2005`: 138
- `bennett_staple_food_budget_share`: 110
- `food_budget_share_total_usda1996`: 110
- `income_elasticity_breads_cereals`: 110
- `income_elasticity_food_beverages_tobacco`: 110
- `orshansky_food_multiplier`: 2
- `official_poverty_food_share_assumed`: 1
