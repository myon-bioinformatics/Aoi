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

AZE, BHR, CHN, EGY, JOR, KWT, LBN, LKA, NZL, OMN, QAT, SAU, ARE, VEN

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

## 2026-10-25 PAK append (+ SAU/ARE miss reconfirm)

- **PAK HIT** 10 rows: PBS HIES 2015-16 + 2018-19 Table 15 national Food & Non Alcoholic Beverages by **consumption** quintiles (q1–q5). Pack → **858 / 41**.
- **SAU MISS (reconfirm):** GaStat HIES 2018 Tables 44–45 only Low/Medium/High **expenditure terciles** (computed food shares Saudi ~29.9/24.3/12.4) — **not loaded** (terciles ≠ quintile/decile schema). HICES national food % only otherwise.
- **ARE MISS (reconfirm):** No open FCSC/SCAD/Dubai Pulse food×income-quintile or -decile table; Dubai Pulse income distribution without food Engel cut.
- HIES 2013-14 Table 15 «Food, beverage and tobacco» quintiles **skipped** (tobacco in basket).
- HIES 2024-25 presentation: national Food & Non-Alc 36.72% only — no quintile food % in open slides.

## 2026-10-25 URY INE ENGIH deciles

- **URY HIT** INE ENGIH 2016-2017 Cuadro 31 food_d1–d10 (con valor locativo; income per-capita deciles): 26.0…12.8; year 2017. Kept alongside CEPALSTAT 5725 2016 quintiles.
- SAU/ARE miss unchanged (terciles / no open quintile-decile food Engel).

## 2026-10-25 MDA food×income append

- **MDA HIT:** NBS CBGC 2024 (Ed.2025) + 2025 (Ed.2026 Table 7.26) food_q1–q5; consumption-expenditure quintiles (not income); Food+non-alc % of avg monthly per-capita consumption expenditure. 2025 methodology break noted. +10 rows → **878/42**.
- SAU/ARE miss unchanged.

## 2026-10-25 UKR food×income deciles

- **UKR HIT:** SSSU Table II.45 (2020–2021) Food+non-alc % of money expenditure by per capita equivalent **money-income deciles** d1–d10. +20 rows → **898/43**.

## 2026-10-25 RUS food×income deciles

- **RUS HIT:** Rosstat HBS R_1-5_4k (via Roschart) IV quarter 2022–2023 — Food+non-alc % of consumer expenditures by income deciles d1–d10. +20 rows → **918/44**.
- SAU/ARE miss unchanged (terciles / no open quintile-decile).
- Hours-to-buy still DEU+BRA only (no new NSO-designed series).

## 2026-10-25 IDN Susenas 2022–2023 quintiles

- **IDN HIT:** March 2022 & 2023 Susenas food share by expenditure quintile (CNBC→BPS). +10 → **928/44**.
- SAU/ARE miss unchanged. Hours still DEU+BRA only.

## 2026-10-25 ARM ILCS 2024 food×income deciles

- **ARM HIT:** Table 3.11 food (old COICOP) by monetary-income deciles d1–d10: 52.5…34.3. Pack → **938 / 45**.
- SAU/ARE: still no open quintile/decile food×income (terciles / nationality cuts only) — miss.

## 2026-10-25 TZA HBS food×income append

- **TZA HIT:** NBS HBS 2017/18 Mainland Table 6.7.1 food % of HH consumption by consumption decile — d1–d10: 69.6, 67.3, 66.1, 64.2, 63.1, 60.9, 57.6, 53.5, 50.3, 33.9 (national 59.9). +10 rows. Pack → **948 / 46**.
- SAU/ARE/HKG/VNM food×income miss unchanged.

## 2026-10-25 MMR MLCS food×income append

- **MMR HIT:** CSO MLCS 2017 Figure 2-2b food % of consumption aggregate by consumption quintile — q1–q5: 64.5, 59.9, 56.9, 53.4, 40.7. +5 rows. Pack → **953 / 47**.

## 2026-10-25 FJI HIES food×income append

- **FJI HIT:** HIES 2019-20 Table 20 food share by expenditure decile — d1–d10: 36.5, 40.6, 42.5, 42.8, 43.1, 43.8, 42.5, 42.1, 39.3, 34.0. +10 rows. Pack → **963 / 48**.
