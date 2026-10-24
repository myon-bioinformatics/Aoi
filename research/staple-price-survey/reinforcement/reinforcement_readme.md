# Reinforcement data: Engel-adjacent concepts（青いプロジェクト第2弾・補強）

Retrieval date: **2026-10-24 Asia/Tokyo**

This folder is a **reference / reinforcement** pack for concepts that look like Engel’s coefficient but measure something different. It is meant to sit beside `staple_survey_vertical.csv`, not replace the main Engel E series.

## Output files

| File | Role |
|------|------|
| `reinforcement_vertical.csv` | UTF-8 vertical observations |
| `reinforcement_readme.md` | This file |
| `reinforcement_missing.md` | Gaps and reasons |
| `raw/` | Downloaded source extracts |

Columns: `country,date,year,variable,value,unit,source,note,estimated_value`

Rules honored: **no FX conversion**, **no unit homogenization** (Eurostat food shares kept as **per mille**), **no gap-filling**. Derived shares from published FAO FBS kcal components are labeled `derived=...` in `note` and use variable names ending in `_derived` or explicit share names with formula in note. `estimated_value` is unused in this build (empty).

Country universe target: 56 ISO3 codes from `bigmac_vertical.csv` (includes `EUZ`). Extra countries appear mainly in FAO FS 21012 and USDA elasticities; each row’s `note` has `in_bigmac_universe=True/False`.

## How these differ from Engel E

| Family | What it measures | vs Engel E (`food / total expenditure`) |
|--------|------------------|----------------------------------------|
| **Bennett side** | Starchy staples (cereals + roots/tubers) as % of **dietary energy**, or breads/cereals as % of **food budget** | Looks at **composition of the diet / food basket**, not food vs all spending |
| **Working–Leser side** | Food share **by income quintile**, mean expenditure by quintile, or **published income elasticities** | Same broad “food share” idea as Engel, but for **slope / gradient** across income, not a single national E |
| **Orshansky-type** | **Normative** poverty multiplier (food basket × N) | Policy poverty line construction; **not** an observed Engel series |

Do **not** plug Orshansky multipliers into `b = k × E × M` as if they were E.

## Variable catalog

### 1) Bennett side (priority)

| variable | Meaning | Source |
|----------|---------|--------|
| `bennett_starchy_calorie_share` | Share of dietary energy from cereals + roots + tubers (%) | FAOSTAT Suite of Food Security Indicators **item 21012** (3-year average) |
| `bennett_starchy_calorie_share_owid` | Same concept as packaged by Our World in Data | OWID grapher (FAO-based) |
| `food_supply_kcal_total` / `_cereals` / `_roots_tubers` | Food supply kcal/capita/day | FAOSTAT Food Balances (2010–), items 2901 / 2905 / 2907 |
| `cereal_calorie_share` | 100 × kcal(2905) / kcal(2901) | Derived from published FBS kcal |
| `roots_tubers_calorie_share` | 100 × kcal(2907) / kcal(2901) | Derived |
| `bennett_starchy_calorie_share_fao_fbs_derived` | 100 × (2905+2907) / 2901 | Derived; may differ from FS 21012 |
| `bennett_staple_food_budget_share` | Breads & cereals share of **food** budget | USDA ERS International Food Consumption Patterns (1996) |

### 2) Working–Leser side (complementary; does **not** duplicate main-survey USDA 2021–2025 Engel rows)

| variable | Meaning | Source |
|----------|---------|--------|
| `food_share_by_income_quintile_qu1`…`qu5` | CP01 food & non-alcoholic beverages share by income quintile | Eurostat `hbs_str_t223` (**per mille** as published) |
| `mean_consumption_expenditure_pps_ae_qu1`…`qu5` | Mean consumption expenditure by quintile | Eurostat `hbs_exp_t133` (PPS per adult equivalent) |
| `food_budget_share_total_usda1996` | Total food expenditure share (1996 ICP-based) | USDA ERS IFCP |
| `income_elasticity_breads_cereals` / `income_elasticity_food_beverages_tobacco` | Published income elasticities (1996) | USDA ERS IFCP |
| `income_elasticity_cereals_usda2005` / `income_elasticity_food_broad_usda2005` | Published income elasticities (2005 ICP) | USDA ERS IFCP XLS |

We did **not** estimate Working–Leser coefficients ourselves. Quintile food shares + expenditures are provided so you can fit later.

### 3) Orshansky-type (kept separate)

| variable | Meaning | Source |
|----------|---------|--------|
| `official_poverty_food_share_assumed` | ~1/3 food share (USA 1955 survey, families 3+) | ASPE history of poverty thresholds |
| `orshansky_food_multiplier` | 3 (families 3+) and 3.7 (two-person) | ASPE / Census history |

Marked **NORMATIVE** in `note`.

## Coverage snapshot (Big Mac 56-country universe)

- Total rows in file: **11,477** (includes some non-universe FAO/USDA rows).
- Universe rows: **7,235**.
- **Bennett-related** countries in universe: **55** / 56. Missing: `EUZ`.
- **Working–Leser-related** countries in universe: **48** / 56 (USDA elasticities/budget and/or Eurostat quintiles).
- Eurostat quintile food shares in universe: **CZE, DNK, GBR, HUN, NOR, POL, ROU, SWE, TUR**.
- **Orshansky** rows: **USA only** (documented classic multipliers).

### Japan (JPN)

- Present: **yes**.
- FAO FS 21012 (`bennett_starchy_calorie_share`): years 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 (series stops early for Japan in this extract).
- OWID Bennett share: years 2001–2021 (21 valued years).
- FAO FBS 2010– kcal components: **not in** the FAO catalog FBS extract used here (Japan absent from that pull) — see missing file.
- USDA 1996/2005 budget share & elasticities: present.
- Eurostat HBS quintiles: **not applicable** (Japan not in Eurostat HBS).
- Japan income-quintile Engel from e-Stat: **not obtained** in this pass (wrong table download).

## Suggested use with `b = k × E × M`

1. Keep main-survey `engel_share_food` as **E**.
2. Use `bennett_starchy_calorie_share` (prefer FS 21012; OWID as cross-check) as a **diet-composition** companion when interpreting k.
3. Use Eurostat quintile shares (+ PPS expenditures) or USDA elasticities for **Working–Leser / slope** checks across countries that have them.
4. Keep Orshansky rows in a separate poverty-methods discussion only.
