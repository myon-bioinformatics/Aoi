# missing — adjacent_food_share_by_income

## Hits: 37 ISO3 · 814 rows

See `readme.md` coverage tables and `_coverage_by_country.csv`.

Hits: ARG, BEL, BRA, CAN, CHE, CHL, COL, CRI, CZE, DEU, DNK, ESP, EUZ, FRA, GBR, GTM, HND, HUN, IDN, IND, ISR, ITA, MEX, NIC, NLD, NOR, PER, PHL, POL, ROU, SGP, SWE, THA, TUR, URY, USA, ZAF

### By source

| source | countries |
|--------|-----------|
| Eurostat HBS_STR_T223 | CZE, DNK, EUZ, GBR, HUN, NOR, POL, ROU, SWE, TUR, **BEL, DEU, ESP, FRA, ITA, NLD** |
| CEPALSTAT indicator 5725 | ARG, BRA, CHL, COL, CRI, GTM, HND, MEX, NIC, PER, URY |
| ONS Family Spending workbook 2 Table A8 | GBR (deciles) |
| Defra Family Food (GOV.UK CSV) | GBR (q1/q3/q5) |
| MOSPI HCES 2022-23 Table A6 + A2 | IND |
| NSO Thailand SES 2561 summary PDF | THA (q1/q5 only) |
| BPS Susenas via Kompas | IDN |
| PSA FIES 2023 Table 7 (bettergov) | PHL |
| BLS CE opub Tables 2/3 | USA |
| StatCan SHS via The Daily | CAN |
| CBS Israel HES 2021 Table 1.1 / Intro D2 | ISR |
| Swiss FSO HBS dépenses par classe de revenu | CHE |
| SingStat Table Builder D10072 | SGP |
| Stats SA IES 1995 via DataFirst | ZAF (expenditure quintiles; kept) |
| Stats SA IES 2022/23 P0100 Table 8.2.13 / 8.2.10 | ZAF (HH income deciles primary; expenditure deciles also) |

## Priority status (this append)

| ISO3 | status | probe notes |
|------|--------|-------------|
| ISR | **HIT** 5 rows | CBS HES 2021 q1–q5; food÷consumption; net income per standard person |
| FRA | **HIT** 35 rows | Eurostat HBS_STR_T223 CP01 |
| DEU | **HIT** 35 rows | Eurostat |
| ITA | **HIT** 20 rows | Eurostat (fewer waves than FR/DE) |
| ESP | **HIT** 35 rows | Eurostat |
| NLD | **HIT** 35 rows | Eurostat |
| BEL | **HIT** 35 rows | Eurostat |
| CHE | **HIT** 30 rows | FSO HBS; food÷consumption computed from CHF amounts (published % are of gross income — not used) |
| SGP | **HIT** 25 rows | SingStat D10072; food+non-alc÷TOTAL excl. imputed OO rental; 5 waves |
| ZAF | **HIT** 25 rows | IES 1995 expenditure quintiles (DataFirst) **kept**; IES 2022/23 P0100 Table **8.2.13** income deciles (primary) + Table **8.2.10** expenditure deciles |
| SAU | **MISS** | GASTAT HICES 2013/2018/2023 national food % only — no income quintile cut in open pubs |
| ARE | **MISS** | SCAD HIES methodology/2007 stats; no open food×income-quintile table |
| HKG | **MISS** (grain mismatch) | C&SD 2024/25 HES food shares by **expenditure quartile** (37.3/30.0/26.0/19.0) — not quintiles; not coerced into q1–q5 |
| VNM | **MISS** | GSO VHLSS press notes / portal OLAP 500; no open published food×quintile share table loaded (microdata DIY out of scope) |

## Other Big Mac / priority misses (excl. Aoi skip)

AZE, BHR, CHN, EGY, JOR, KWT, LBN, LKA, MDA, NZL, OMN, PAK, QAT, RUS, SAU, ARE, UKR, VEN

No open HBS/FIES quintile×food share table loaded for these this run. National-mean Engel / ICP aggregate intentionally **not** used as quintile proxies.

## Intentional skip

| ISO3 | note |
|------|------|
| JPN | Season2 Japan Engel quintiles |
| KOR | Aoi Korea food-share-by-income |
| TWN | Aoi Taiwan food-share-by-income |
| AUS | Aoi ABS HES food-share panel |

## Probes not loaded / not reused as Engel

- HKG quartile food shares — wrong grain for schema
- SAU/ARE national-mean food shares — not quintile
- OECD-FAO global income-group food shares — not country quintiles
- VNM GSO portal OLAP HTTP 500; resampled VHLSS micro → DIY not used
- ZAF: IES 1995 (DataFirst) kept; IES 2022/23 P0100 Tables 8.2.13 (income deciles) + 8.2.10 (expenditure deciles) loaded from Stats SA PDF after captcha clear
- Aoi CPI / housing / FPO companions: not touched

## 2026-10-24 MYS append

DOSM HES 2022 Table 1.13 income quintiles Food & Beverages: 25.2, 21.7, 18.8, 15.8, 11.2 (Malaysian citizen households).

## 2026-10-24 HKG append

Censtatd HES 2019/20 Chart 3 expenditure quartiles Food % of total HH expenditure: 42, 31, 28, 22 (documented as expenditure quartiles — not income; not coerced to deciles).
SAU GaStat HIES 2018 Tables 44–45 only Low/Medium/High expenditure terciles (SAR levels); computed food shares Saudi 29.9/24.3/12.4 — left unloaded (terciles ≠ quintile schema).
ARE/VNM still miss open income-quintile food %.

## 2026-10-24 VNM append

VHLSS 2022 Table 6.15 Food+Foodstuff % of living consumption by income quintile: 49.9, 45.3, 42.1, 38.4, 26.1 (excludes outdoor meals, fuel, drinking & smoking).
