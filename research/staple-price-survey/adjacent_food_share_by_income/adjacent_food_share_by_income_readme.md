# adjacent_food_share_by_income — food expenditure share by income quintile/decile

Retrieved: **2026-10-24 Asia/Tokyo** · Season2 adjacent for Aoi #118

## Result

**395 vertical rows** · **21 / 56** Big Mac ISO3 with at least one series · year span **1988–2025**.

Food (COICOP CP01 / food+non-alc) share of household expenditure by **income quintile** (`engel_share:food_q1`…`q5`) or **disposable-income decile** (`engel_share:food_d1`…`d10`). **Not** average retail prices, CPI indexes, or national-mean Engel alone.

Schema: `country,date,year,variable,value,unit,source,note,estimated_value` (ISO3; `date=YYYY-01-01`; `unit=percent`; `estimated_value` empty — no FX, no gap-fill).

## Intentional skips (Aoi / Season2 lanes)

| ISO3 | note |
|------|------|
| JPN | Japan Engel quintiles already in Season2 |
| KOR | Aoi owns Korea food-share-by-income |
| TWN | Aoi owns Taiwan food-share-by-income |

Also skipped this pack (other Aoi / adjacent lanes): Orshansky memo, food CPI indexes, `hi_staple_levels_alt`, BLS, FPMA, Pink Sheet, UK ONS **avg retail prices** panel, CoAHD, producer prices, `adjacent_eating_out_shares` (just finished).

## Variables

| variable | rows | unit | definition |
|----------|-----:|------|------------|
| `engel_share:food_q1` … `food_q5` | 325 | percent | Food+non-alc ÷ total HH expenditure ×100; income quintile 1=lowest … 5=highest |
| `engel_share:food_d1` … `food_d10` | 70 | percent | Same share; disposable-income decile (ONS LCF / Family Spending; GBR only) |

Defra Family Food publishes only **q1 / q3 / q5** (lowest / middle / highest 20%); q2/q4 absent by source design (noted on those rows).

## Sources (loaded)

1. **Eurostat** `HBS_STR_T223` — structure of consumption expenditure by income quintile; COICOP **CP01**; unit **PM** (per mille) ÷10 → percent. Geos kept for Big Mac ISO3 (+ **EUZ** from `EU27_2020`, not EA). Waves ~1988–2020 where published.
2. **CEPALSTAT** indicator **5725** — LatAm food+non-alc share of total HH expenditure by income quintile (National). One HIES/HBS wave per country in the open pull.
3. **ONS** Family Spending workbook 2 **Table A8** — Food & non-alcoholic drinks % of total expenditure by disposable-income **decile**; UK FYE2019–FYE2025 workbooks.
4. **Defra** Family Food (GOV.UK CSV) — household share of spend on food by income group **q1/q3/q5**; FYE2005–FYE2025 (gap years as published).

Eurostat preferred for GBR quintiles where both Eurostat and Defra overlap; ONS deciles kept as complementary grain. No national-accounts mean Engel used as quintile proxy.

## Coverage (hits)

### Eurostat HBS_STR_T223 (quintiles)

| ISO3 | rows | years | note |
|------|-----:|-------|------|
| CZE | 15 | 2005–2015 | |
| DNK | 30 | 1994–2020 | |
| EUZ | 10 | 2015–2020 | mapped from EU27_2020 (not EA) |
| GBR | 30 | 1988–2015 | + ONS/Defra below |
| HUN | 20 | 2005–2020 | |
| NOR | 20 | 2005–2020 | |
| POL | 20 | 2005–2020 | |
| ROU | 20 | 2005–2020 | |
| SWE | 25 | 1994–2015 | |
| TUR | 20 | 2005–2020 | priority hit |

### CEPALSTAT 5725 (LatAm quintiles, one wave)

| ISO3 | year | rows |
|------|-----:|-----:|
| ARG | 2017 | 5 |
| BRA | 2017 | 5 |
| CHL | 2021 | 5 |
| COL | 2016 | 5 |
| CRI | 2018 | 5 |
| GTM | 2014 | 5 |
| HND | 2004 | 5 |
| MEX | 2018 | 5 |
| NIC | 2014 | 5 |
| PER | 2019 | 5 |
| URY | 2016 | 5 |

### GBR national (ONS deciles + Defra q1/q3/q5)

| source | rows | years | variables |
|--------|-----:|-------|-----------|
| ONS Family Spending workbook 2 Table A8 | 70 | 2019–2025 | food_d1…d10 |
| Defra Family Food CSV | 60 | 2005–2025 | food_q1, food_q3, food_q5 |

## Priority targets

| status | ISO3 |
|--------|------|
| **hit** | MEX, BRA, CHL, COL, PER, ARG, TUR, GBR |
| **miss** | ZAF, IND, THA, IDN, PHL |

## Files

- `adjacent_food_share_by_income_vertical.csv` (+ `.gz`)
- `_coverage_by_country.csv`, `_build_stats.json`, `raw/_hits.json`
- `readme.md`, `missing.md`
- `raw/` — Eurostat CSV, CEPALSTAT JSON, ONS xlsx, Defra CSV, probe artifacts for misses

Mirrored to `/workspace/aoi-phase2/staple-price-survey/adjacent_food_share_by_income/`. No git push.
