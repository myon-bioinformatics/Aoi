# adjacent_food_share_by_income — food expenditure share by income quintile/decile

Retrieved: **2026-10-24 Asia/Tokyo** · Season2 adjacent for Aoi #118

## Result

**437 vertical rows** · **25 / 56** Big Mac ISO3 with at least one series · year span **1988–2026**.

Food (COICOP CP01 / food+non-alc) share of household expenditure by **income quintile** (`engel_share:food_q1`…`q5`) or **income/expenditure decile** (`engel_share:food_d1`…`d10`). **Not** average retail prices, CPI indexes, or national-mean Engel alone.

Schema: `country,date,year,variable,value,unit,source,note,estimated_value` (ISO3; `date=YYYY-01-01`; `unit=percent`; `estimated_value` empty — no FX, no gap-fill).

## Intentional skips (Aoi / Season2 lanes)

| ISO3 | note |
|------|------|
| JPN | Japan Engel quintiles already in Season2 |
| KOR | Aoi owns Korea food-share-by-income |
| TWN | Aoi owns Taiwan food-share-by-income |

Also skipped this pack (other Aoi / adjacent lanes): Orshansky memo, food CPI indexes, `hi_staple_levels_alt`, BLS, FPMA, Pink Sheet, UK ONS **avg retail prices** panel, CoAHD, producer prices, `adjacent_eating_out_shares`.

## Variables

| variable | rows | unit | definition |
|----------|-----:|------|------------|
| `engel_share:food_q1` … `food_q5` | 347 | percent | Food(+non-alc) ÷ total HH expenditure ×100; quintile 1=lowest … 5=highest |
| `engel_share:food_d1` … `food_d10` | 90 | percent | Same share; income/expenditure decile |

Defra Family Food publishes only **q1 / q3 / q5** (lowest / middle / highest 20%); q2/q4 absent by source design (noted on those rows). THA SES 2561 summary publishes only **q1 / q5** (food+bev+tobacco).

## Sources (loaded)

1. **Eurostat** `HBS_STR_T223` — structure of consumption expenditure by income quintile; COICOP **CP01**; unit **PM** (per mille) ÷10 → percent. Geos kept for Big Mac ISO3 (+ **EUZ** from `EU27_2020`, not EA). Waves ~1988–2020 where published.
2. **CEPALSTAT** indicator **5725** — LatAm food+non-alc share of total HH expenditure by income quintile (National). One HIES/HBS wave per country in the open pull.
3. **ONS** Family Spending workbook 2 **Table A8** — Food & non-alcoholic drinks % of total expenditure by disposable-income **decile**; UK FYE2019–FYE2025 workbooks.
4. **Defra** Family Food (GOV.UK CSV) — household share of spend on food by income group **q1/q3/q5**; FYE2005–FYE2025 (gap years as published).
5. **MOSPI** HCES 2022-23 **Table A6** (Food:Total & total expenditure by 12 MPCE fractiles) + **Table A2** (estimated households) — rural+urban pop-weighted national Engel → **IND** q1–q5 and d1–d10 (year coded 2023).
6. **NSO Thailand** SES 2561 (2018) summary PDF `SD10_04_189_7` — **THA** food+beverages+tobacco share for expenditure **q1 and q5 only**.
7. **BPS** Susenas *Pengeluaran untuk Konsumsi Penduduk Indonesia* March 2025 & March 2026 — **IDN** q1–q5 as reported by Kompas 2026-10-06 (primary `bps.go.id` Cloudflare/403 from this egress; secondary citation noted on rows).
8. **PSA** FIES 2023 **Table 7** via bettergov OpenSTAT mirror (`0071E3ATME0.px`) — **PHL** food+non-alc % by per-capita income **d1–d10** (published percent) plus expenditure-weighted **q1–q5**.

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

### Asia priority append (2026-10-24)

| ISO3 | rows | years | source | grain |
|------|-----:|-------|--------|-------|
| IND | 15 | 2023 | MOSPI HCES 2022-23 A6+A2 | q1–q5 + d1–d10 |
| THA | 2 | 2018 | NSO SES 2561 summary PDF | q1, q5 only (food+bev+tobacco) |
| IDN | 10 | 2025–2026 | BPS Susenas via Kompas | q1–q5 × 2 waves |
| PHL | 15 | 2023 | PSA FIES Table 7 (bettergov) | d1–d10 + weighted q1–q5 |

## Files

| file | role |
|------|------|
| `adjacent_food_share_by_income_vertical.csv` | long panel |
| `adjacent_food_share_by_income_vertical.csv.gz` | gzip mirror |
| `_coverage_by_country.csv` | per-ISO3 row/year/variable summary |
| `_build_stats.json` | build counts |
| `missing.md` | misses + probe notes |
| `raw/` | source pulls (eurostat, cepal, gbr, ind, tha, idn, phl, zaf, …) |

Mirrored to `/workspace/aoi-phase2/staple-price-survey/adjacent_food_share_by_income/` (no git push).
