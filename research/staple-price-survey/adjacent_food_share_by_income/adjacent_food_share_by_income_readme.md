# adjacent_food_share_by_income — food expenditure share by income quintile/decile

Retrieved: **2026-10-25 Asia/Tokyo** · Season2 adjacent for Aoi #118

## Result

**858 vertical rows** · **41 ISO3** with at least one series · year span **1988–2026**.

Food (COICOP CP01 / food+non-alc) share of household expenditure by **income quintile** (`engel_share:food_q1`…`q5`) or **income/expenditure decile** (`engel_share:food_d1`…`d10`). Where the source publishes both, **food-total** and **food-at-home** are separate variables (`engel_share:food_*` vs `engel_share:food_at_home_*`). **Not** average retail prices, CPI indexes, or national-mean Engel alone.

Schema: `country,date,year,variable,value,unit,source,note,estimated_value` (ISO3; `date=YYYY-01-01`; `unit=percent`; `estimated_value` empty — no FX, no gap-fill).

## Intentional skips (Aoi / Season2 lanes)

| ISO3 | note |
|------|------|
| JPN | Japan Engel quintiles already in Season2 |
| KOR | Aoi owns Korea food-share-by-income |
| TWN | Aoi owns Taiwan food-share-by-income |
| AUS | ABS HES food-share lives in Aoi `abs_hes_food_share_*` — **not** duplicated here |

Also skipped this pack (other Aoi / adjacent lanes): Orshansky memo, food CPI indexes, `hi_staple_levels_alt`, BLS **staple retail levels** / FAH·FAFH **indexes**, FPMA, Pink Sheet, UK ONS **avg retail prices** panel, CoAHD, producer prices, `adjacent_eating_out_shares`, JP CPI meals, DOSM/THA MOC CPI, housing share, SGP/HKG CPI, USDA FPO, Japan numeraire. ZAF: IES 1995 (DataFirst expenditure quintiles) kept; IES 2022/23 P0100 Table 8.2.13 income deciles (primary) + Table 8.2.10 expenditure deciles appended. NZL HES national-all-households only (Aoi).

## Variables

| variable | unit | definition |
|----------|------|------------|
| `engel_share:food_q1` … `food_q5` | percent | Food(+non-alc / food total) ÷ total HH expenditure (or total current consumption) ×100; quintile 1=lowest … 5=highest |
| `engel_share:food_d1` … `food_d10` | percent | Same share; income/expenditure decile |
| `engel_share:food_at_home_q1` … `q5` | percent | **Food at home only** ÷ total HH expenditure ×100 (USA BLS CE) |
| `engel_share:food_at_home_d1` … `d10` | percent | Food at home only; income decile (USA BLS CE) |

Defra Family Food publishes only **q1 / q3 / q5**; THA SES 2561 summary only **q1 / q5**; CAN 2021 Daily text only **q1 / q5**. HKG 2024/25 HES publishes **expenditure quartiles** only — not loaded (schema is q1–q5 / d1–d10).

## Sources (loaded)

1. **Eurostat** `HBS_STR_T223` — COICOP **CP01**; unit **PM** ÷10 → percent. Geos for pack ISO3 (+ **EUZ** from `EU27_2020`). Waves ~1988–2020.
2. **CEPALSTAT** indicator **5725** — LatAm food+non-alc share by income quintile.
3. **ONS** Family Spending workbook 2 **Table A8** — GBR food % by disposable-income **decile**.
4. **Defra** Family Food — GBR q1/q3/q5.
5. **MOSPI** HCES 2022-23 — **IND** q1–q5 + d1–d10.
6. **NSO Thailand** SES 2561 — **THA** q1/q5 only.
7. **BPS** Susenas via Kompas — **IDN** q1–q5.
8. **PSA** FIES 2023 Table 7 (bettergov) — **PHL** d1–d10 + q1–q5.
9. **BLS** CE Tables 2/3 — **USA** food + food_at_home.
10. **Statistics Canada** SHS via The Daily — **CAN**.
11. **CBS Israel** HES 2021 Table 1.1 / Intro D2 — **ISR** q1–q5 (net income per standard person).
12. **Swiss FSO** HBS dépenses par classe de revenu — **CHE** food÷consumption (not % of gross income); income classes ≈ quintiles; waves 2006–2008 … 2020–2021.
13. **SingStat** Table Builder **D10072** HES — **SGP** food+non-alc ÷ TOTAL (excl. imputed OO rental) by income quintile; waves 2002/03–2023.
14. **Stats SA IES 1995** via DataFirst *Earning and spending in South Africa* — **ZAF** food÷total expenditure by **expenditure** quintile (Stats SA site captcha skipped).
15. **PBS Pakistan HIES** Table 15 — **PAK** Food & Non Alcoholic Beverages by **consumption** quintiles; waves 2015-16, 2018-19.
16. **DOSM HES 2022** Table 1.13 — **MYS** income quintiles; **Censtatd HES 2019/20** Chart 3 — **HKG** expenditure quartiles; **NSO Vietnam VHLSS 2022** Table 6.15 — **VNM** income quintiles (Food+Foodstuff).

Eurostat preferred for GBR quintiles where both Eurostat and Defra overlap; ONS deciles kept. No national-accounts mean Engel as quintile proxy.

## Coverage (hits)

### Eurostat HBS_STR_T223 (quintiles)

| ISO3 | rows | years |
|------|-----:|-------|
| CZE | 15 | 2005–2015 |
| DNK | 30 | 1994–2020 |
| EUZ | 10 | 2015–2020 |
| GBR | 160 | 1988–2025 |
| HUN | 20 | 2005–2020 |
| NOR | 20 | 2005–2020 |
| POL | 20 | 2005–2020 |
| ROU | 20 | 2005–2020 |
| SWE | 25 | 1994–2015 |
| TUR | 20 | 2005–2020 |
| BEL | 35 | 1988–2020 |
| DEU | 35 | 1988–2020 |
| ESP | 35 | 1988–2020 |
| FRA | 35 | 1988–2020 |
| ITA | 20 | 1988–2005 |
| NLD | 35 | 1988–2020 |

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

| source | rows | years |
|--------|-----:|-------|
| ONS Family Spending workbook 2 Table A8 | 70 | 2019–2025 |
| Defra Family Food CSV | 60 | 2005–2025 |

### Asia / MENA / other append

| ISO3 | rows | years | source | grain |
|------|-----:|-------|--------|-------|
| IND | 15 | 2023 | MOSPI HCES 2022-23 | q1–q5 + d1–d10 |
| THA | 2 | 2018 | NSO SES 2561 | q1, q5 only |
| IDN | 10 | 2025–2026 | BPS via Kompas | q1–q5 × 2 |
| PHL | 15 | 2023 | PSA FIES Table 7 | d1–d10 + q1–q5 |
| PAK | 10 | 2016–2019 | PBS HIES Table 15 | consumption q1–q5 × 2 |
| ISR | 5 | 2021 | CBS Israel HES 2021 | q1–q5 |
| SGP | 25 | 2003–2023 | SingStat D10072 | q1–q5 × 5 waves |
| CHE | 30 | 2007–2021 | Swiss FSO HBS | q1–q5 × 6 waves |
| ZAF | 5 | 1995 | IES 1995 via DataFirst | expenditure q1–q5 |

### North America

| ISO3 | rows | years | source |
|------|-----:|-------|--------|
| USA | 110 | 2020–2024 | BLS CE Tables 2/3 |
| CAN | 7 | 2021, 2023 | StatCan SHS via The Daily |

## Files

| file | role |
|------|------|
| `adjacent_food_share_by_income_vertical.csv` | long panel |
| `adjacent_food_share_by_income_vertical.csv.gz` | gzip mirror |
| `_coverage_by_country.csv` | per-ISO3 summary |
| `_build_stats.json` | build counts |
| `missing.md` | misses + probe notes |
| `raw/` | source pulls |

Mirrored to `/workspace/aoi-phase2/staple-price-survey/adjacent_food_share_by_income/` (no git push).
