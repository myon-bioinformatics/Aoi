# adjacent_food_share_by_income — food expenditure share by income quintile/decile

Retrieved: **2026-10-25 Asia/Tokyo** · Season2 adjacent for Aoi #118

## Result

**1468 vertical rows** · **84 ISO3** with at least one series · year span **1988–2026**.

Food expenditure shares stratified by income, expenditure, consumption, or welfare. These strata are distinct and must not be pooled.

Schema v2 retains all original observations and source/note text. `legacy_variable` preserves the original variable spelling for provenance only; never use it as a series key. Defra Family Food retains a separate `food_defra` source variant to distinguish overlapping GBR observations from Eurostat CP01; it must not overwrite or be averaged with Eurostat. The canonical variable is `engel_share:food[_at_home]_<stratifier>_<bucket_type>_<index>`. Required columns `stratifier`, `bucket_type`, `bucket_count`, `bucket_index` also encode the classification explicitly. The observation key is `(country,date,variable,unit)`; `source` is not used to conceal collisions.

`quartile` = four 25% groups; `quintile` = five 20% groups; `decile` = ten 10% groups. Swiss CHF income brackets are `income_class` (five classes, no equal-population claim). `welfare` preserves the published bien-être label without inventing an income basis. Full source definitions remain in `note`; the broad stratifier alone does not establish international comparability. IND MPCE fractiles are expenditure strata, including the legacy quintile note that calls them income.

`classification.json` records reviewed source contracts, explicitly published partial series, and a SHA-256 of every original field/row. Missing intermediate groups remain missing: no gap filling. `estimated_value` stays unchanged. Run `python scripts/check_food_share_data.py` to verify classification, keys, preservation, CSV/gzip equality, and current README coverage.

## Intentional skips (Aoi / Season2 lanes)

| ISO3 | note |
|------|------|
| JPN | Japan Engel quintiles already in Season2 |
| KOR | Aoi owns Korea food-share-by-income |
| TWN | Aoi owns Taiwan food-share-by-income |
| AUS | ABS HES food-share lives in Aoi `abs_hes_food_share_*` — **not** duplicated here |

Also skipped this pack (other Aoi / adjacent lanes): Orshansky memo, food CPI indexes, `hi_staple_levels_alt`, BLS **staple retail levels** / FAH·FAFH **indexes**, FPMA, Pink Sheet, UK ONS **avg retail prices** panel, CoAHD, producer prices, `adjacent_eating_out_shares`, JP CPI meals, DOSM/THA MOC CPI, housing share, SGP/HKG CPI, USDA FPO, Japan numeraire. ZAF: IES 1995 (DataFirst expenditure quintiles) kept; IES 2022/23 P0100 Table 8.2.13 income deciles (primary) + Table 8.2.10 expenditure deciles appended. NZL HES national-all-households only (Aoi).

## Variables

Examples: `engel_share:food_income_decile_1` and `engel_share:food_expenditure_decile_1` retain both ZAF 2023 series (30.5 and 32.1). HKG 2020 uses `engel_share:food_expenditure_quartile_1`…`4`; all four observations are retained, separately from quintiles. HKG 2024/25 has not been added.

Defra q1/q3/q5, THA q1/q5 and CAN 2021 q1/q5 are explicit partial series in the manifest, not complete quintiles. Historical q/d labels in the source descriptions below refer to `legacy_variable` only.

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
16. **DCS Sri Lanka HIES 2016 & 2019 Final Report Table 3.13** — **LKA** income-decile food÷total (`food_d1`…`d10`); 2019 via OCR of image page.
17. **DOSM HES 2022** Table 1.13 — **MYS** income quintiles; **Censtatd HES 2019/20** Chart 3 — **HKG** expenditure quartiles; **NSO Vietnam VHLSS 2022** Table 6.15 — **VNM** income quintiles (Food+Foodstuff).

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
| BOL | 2015 | 5 |
| BRA | 2017 | 5 |
| CHL | 2021 | 5 |
| COL | 2016 | 5 |
| CRI | 2018 | 5 |
| DOM | 2018 | 5 |
| GTM | 2014 | 5 |
| HND | 2004 | 5 |
| MEX | 2018 | 5 |
| NIC | 2014 | 5 |
| PAN | 2007 | 5 |
| PER | 2019 | 5 |
| PRY | 2011 | 5 |
| SLV | 2006 | 5 |
| URY | 2016 | 5 |

### GBR national (ONS deciles + Defra q1/q3/q5)

| source | rows | years |
|--------|-----:|-------|
| ONS Family Spending workbook 2 Table A8 | 70 | 2019–2025 |
| Defra Family Food CSV | 60 | 2005–2025 |

### Asia / MENA / other append

- **LBN** 2012: CAS + World Bank *Measuring poverty in Lebanon using 2011 HBS* Table A5 — Food and beverages % of total expenditure by consumption per capita quintiles (35/31/30/25/22); alcohol/tobacco separate; year=2012 (HBS Sept 2011–Nov 2012); primary joint CAS+WB technical report PDF pinned under `raw/lbn/`.


| ISO3 | rows | years | source | grain |
|------|-----:|-------|--------|-------|
| EGY | 5 | 2013 | CAPMAS HIECS 2012/13 | q1–q5 |
| IND | 15 | 2023 | MOSPI HCES 2022-23 | q1–q5 + d1–d10 |
| THA | 2 | 2018 | NSO SES 2561 | q1, q5 only |
| IDN | 10 | 2025–2026 | BPS via Kompas | q1–q5 × 2 |
| PHL | 15 | 2023 | PSA FIES Table 7 | d1–d10 + q1–q5 |
| PAK | 10 | 2016–2019 | PBS HIES Table 15 | consumption q1–q5 × 2 |
| ISR | 5 | 2021 | CBS Israel HES 2021 | q1–q5 |
| LBN | 5 | 2012 | CAS+WB Measuring poverty 2011 HBS Table A5 | q1–q5 |
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

### 2026-10-25 Eurostat T223 densification

Added **AUT, BGR, CYP, EST, GRC, HRV, IRL, LTU, LUX, LVA, MKD, MLT, MNE, PRT, SRB, SVK, SVN, XKX** from `HBS_STR_T223` CP01 (PM÷10). Pack → **1428 / 81**. FIN omitted (Aoi national-HES lane).


## Validated coverage (current CSV)

<!-- coverage:start -->
**1468 vertical rows** · **84 ISO3** · year span **1988–2026**.

ISO3: ARG, ARM, AUT, AZE, BEL, BGR, BOL, BRA, CAN, CHE, CHL, COL, CRI, CYP, CZE, DEU, DNK, DOM, EGY, ESP, EST, EUZ, FJI, FRA, GBR, GMB, GRC, GTM, HKG, HND, HRV, HUN, IDN, IND, IRL, ISR, ITA, LBN, LBR, LKA, LTU, LUX, LVA, MDA, MDG, MEX, MKD, MLT, MMR, MNE, MUS, MYS, NIC, NLD, NOR, NPL, PAK, PAN, PER, PHL, POL, PRT, PRY, ROU, RUS, SDN, SGP, SLV, SRB, SVK, SVN, SWE, TCD, THA, TJK, TTO, TUR, TZA, UKR, URY, USA, VNM, XKX, ZAF.
<!-- coverage:end -->

Earlier append counts and source tables describe historical collection steps; current coverage is the validated block above.
