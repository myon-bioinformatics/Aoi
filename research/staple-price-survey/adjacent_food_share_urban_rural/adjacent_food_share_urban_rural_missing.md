# Missing / blocked — adjacent_food_share_urban_rural

| ISO3 | Status |
|---|---|
| CAN | StatCan SSL / WDS failure; not loaded |
| ARG | ENGHo urban-only — no rural companion |
| CHL | INE IX EPF urban (regional capitals) only — no rural |
| CHE, TUR | Not in Eurostat HBS_STR_T226 extract used |
| PAN | CEPALSTAT 5725 National only (no Urban/Rural) |
| URY | **HIT** INE ENGIH 2016-17 Cuadro 27 Montevideo 16.6 / Interior 20.4 (con VL) |
| HKG, SGP | City-state; no rural stratum — do not coerce |
| SAU, ARE | National/regional food % only in open HICES/HIES pubs; no urban/rural food Engel table loaded |
| PAK | **HIT** HIES 2011-12…2018-19 urban/rural Food & Non-Alc (8 rows); 2024-25 national-only noted |
| EGY | **HIT** CAPMAS HIECS 2019/2020 ERF 3948 Urban 28.63 / Rural 36.39 |
| VNM | GSO portal blocked (same as food×income) |
| ZAF | Sibling computerUse lane (Stats SA captcha cleared by user) — **not scraped here** |
| Hours-to-buy expand | No additional NSO-designed labour-minutes staple indicator beyond BMEL (DEU) + DIEESE PNCBA (BRA); pack stays DEU+BRA |

## Food×income still-miss (sibling pack `adjacent_food_share_by_income`; documented, not coerced)

| ISO3 | note |
|---|---|
| SAU | GASTAT HICES national food % only — no income quintile cut |
| ARE | SCAD HIES — no open food×income-quintile table |
| HKG | C&SD HES **expenditure quartiles** (37.3/30.0/26.0/19.0) — document miss; do not coerce to quintiles |
| VNM | GSO VHLSS / portal blocked |

## 2026-10-24 ZAF settlement append

Stats SA IES 2022/23 Table 8.2.7: Urban 14.2 / Traditional 26.6 (as rural) / Farms 20.3 noted not loaded.

## 2026-10-24 append

- ZAF IES 2022/23 Table 8.2.7 Urban 14.2 / Traditional→rural 26.6 (Farms 20.3 noted).
- AUS ABS HES 2015-16 Greater Capital City 16.6 / Rest of State 16.7 (food % of G&S).
- CHN NBS 2023 food+tobacco+liquor urban 28.8 / rural 32.3 (not COICOP food-only).
- VNM VHLSS 2022 Table 6.11 Food+Foodstuff urban 32.7 / rural 37.2.

## 2026-10-25 PAK urban/rural append

- **PAK HIT** 8 rows: PBS HIES Food & Non-Alc urban/rural — 2011-12, 2013-14, 2015-16, 2018-19 (years labelled 2012/2014/2016/2019). Pack → **359 / 55**.
- Corrects earlier miss note that claimed urban/rural food÷total absent from open writeups (Table 3.7.A/B publishes it).
- HIES 2024-25 presentation: national 36.72% only — urban/rural food % not in open slides.
- JOR DOS HEIS 2017 G4 tables: governorate / HH-size / expenditure-bracket commodity averages; **no** clean urban×rural food Engel % table loaded (Food Groups totals also mix tobacco/restaurants).
- CAN StatCan WDS/Daily still egress-blocked this run; EGY CAPMAS primary HIECS urban/rural food % table still not pinned; KOR kostat download egress failed.
- Hours-to-buy: still no additional NSO-designed labour-minutes staple series (FRA Histoprix/datapi = DIY wage÷price — refused).

## 2026-10-25 LKA append

- **LKA HIT** 2 rows: DCS HIES 2019 Final Results Table 10 Urban 28.2 / Rural 36.9 (Food÷total). Pack → **361 / 56**. Estate 50.9% noted not loaded.
- 2016 Final Report PDF download corrupt/unreadable this run — deferred.

## 2026-10-25 EGY + MAR + COL append

- **EGY HIT:** CAPMAS HIECS 2019/2020 (ERF download 3948) Food & Non-Alc ÷ Total consumption expenditure — Urban **28.63** / Rural **36.39** (year 2020). Primary PDF pinned.
- **MAR HIT:** HCP ENCDM/ENNVM Alimentation urban/rural — 2001 (37.9/49.9), 2007 (36.8/49.3), 2014 (33.3/47.3). Not Big Mac ISO3; Engel companion. Full q1–q5 food shares **not** in open tables (only Q1/Q5 extremes 49.6/29.1) → food×income miss.
- **COL thicken:** DANE ENPH 2016-2017 cabeceras **14.0** / centros poblados y rural disperso **31.2** (year 2017); CEPALSTAT 2016 retained.
- **SAU/ARE food×income:** still MISS (SAU terciles only; ARE no open quintile/decile) — reconfirmed, not loaded.
- **Hours-to-buy:** still no third-country NSO-designed labour-minutes staple series (DEU BMEL + BRA DIEESE only).

## 2026-10-25 URY/JOR/MDA append

- **URY HIT** INE ENGIH 2016-2017 Cuadro 27 con valor locativo: Montevideo (urban) 16.6 / Interior (rural proxy) 20.4; year 2017.
- **JOR HIT** DOS HEIS 2013 Table 4.25: Urban 33.42 / Rural 38.24 (Food Stuff/Grand Total member JD).
- **MDA HIT** NBS CBGC: 2024 Urban 34.4 / Rural 46.6; 2025 Urban 35.2 / Rural 47.4 (2025 methodology break noted).
- ARG ENGHo urban-only and CHL EPF urban-capitals-only reconfirmed — no rural companion.
- CAN StatCan SSL still blocked from box egress.
- Hours-to-buy: still DEU+BRA only (WIFO AT Kaufkraft / Histoprix DIY not loaded).

## 2026-10-25 UKR append + AZE probe

- **UKR HIT:** SSSU *Expenditure and resources of households* Table II.3 (2019–2021) — Food+non-alc % of household money expenditure; urban total / rural. Rural < urban noted (own-production). +6 rows.
- **AZE MISS (primary):** stat.gov.az household budget "Composition… urban and rural" listed but HTTPS from this box fails (SSL EOF); banker.az H1 2023 secondary cite (urban 44% / rural 46.78% food) **not loaded** without primary SSC xls.
- **TUR:** TURKSTAT HBS microdata notes say urban/rural estimates not reliable for recent years; no open primary urban/rural food % table loaded.
- **BHR:** 2024 HIES in field; no published urban/rural food Engel yet.
- SAU/ARE food×income miss unchanged (terciles / no open quintile-decile).

## 2026-10-25 OMN append

- **OMN HIT:** ONA 17 Mar 2020 release of NCSI HIES — food-and-drink % urban 23.4 / villages 28.8 (2019) and urban 26.0 / villages 34.3 (2011). Primary NCSI PDF 404; loaded from official ONA citation. +4 rows.

## 2026-10-25 CHN thicken

- **CHN:** +8 rows 2019–2022 NBS press-release Food, tobacco and liquor / PCE (same method as 2023). Series now 2019–2023.

## 2026-10-25 MEX ENIGH 2024 urban/rural

- **MEX HIT:** INEGI ENIGH 2024 Cuadro 13 — Alimentos, bebidas y tabaco % of gasto corriente monetario; urban 37.0 / rural 42.5. +2 rows → **399/63**. Note tobacco-included; companion to CEPALSTAT 2018 food-only.
- IDN 2024 Susenas: national 50.10% open; precise national urban/rural % not pinned from secondary cites this egress — not loaded.
- SAU/ARE food×income miss unchanged.

## 2026-10-25 MEX 2022 + BRA IBGE POF urban/rural

- **MEX HIT:** ENIGH 2022 Table 9 — alimentos+bebidas+tabaco urban 36.9 / rural 42.0. +2.
- **BRA HIT:** IBGE POF 2017-2018 Agência — alimentação urban 16.9 / rural 23.8 (year 2018). +2 → **403/63**.

## 2026-10-25 MEX 2020 + IDN 2020 + LKA 2016 thicken

- **MEX HIT:** INEGI ENIGH 2020 press/Nota técnica — Alimentos, bebidas y tabaco urban **37.2** / rural **42.9** (Cuadro 15 levels confirm). Pack → **409 / 63**.
- **IDN HIT:** BPS Susenas 2020 via Kompas — makanan urban **46.05** / rural **55.49** (national 49.22).
- **LKA HIT:** DCS HIES 2016 Final Results Table 8 — food ratio Urban **31.2** / Rural **35.4** (Estate 48.5 noted). 2016 PDF previously deferred; now loaded.
- **COL:** DANE ENPH 2017 already in pack — skip duplicate.
- Hours-to-buy: still DEU BMEL + BRA DIEESE only (no new NSO-designed labour-minutes series).
- SAU/ARE food×income: still MISS (no open quintile/decile).

## 2026-10-25 IND HCES 2023-24 thicken

- **IND HIT:** MOSPI HCES 2023-24 Factsheet Section I — food÷MPCE urban **39.68** / rural **47.04** (year 2024). Pack → **411 / 63**.
- AZE SSC HBS composition urban/rural table exists on portal but TLS egress failed this run — deferred.
- TUR TurkStat: urban/rural HBS estimates not published reliably after 2014 admin split — miss.
- ISR CBS: no open urban/rural food Engel % in published HES tables — miss.

## 2026-10-25 AZE H1 2023

- **AZE HIT:** SSC HBS H1 2023 via banker.az — urban **44.0** / rural **46.78** food÷consumption. Pack → **413 / 64**.
- SSC 2025 food-accessibility bulletin fetched: **not** Engel shares (skip coerce).
- SSC composition Excel still TLS-blocked from box.

## 2026-10-25 ARM + GEO + MDA thicken

- **ARM HIT:** ILCS 2024 Table 3.8 food+non-alc urban **39.1** / rural **44.7**.
- **GEO HIT:** Geostat 2025 Chart 6 food+bev+tobacco urban **37.5** / rural **41.6**.
- **MDA HIT:** Moldova in Figures — 2021 38.1/45.8; 2022 36.0/46.4; 2023 34.9/45.4 (pack already had 2024/2025).
- Pack → **423 / 66**.
- ARG ENGHo urban-only sample; CHL IX EPF urban-only — miss for rural.
- BHR/KWT/QAT: no open urban/rural food Engel — miss.

## 2026-10-25 BGD + TUN urban/rural

- **BGD HIT:** HIES 2022 food ÷ consumption → urban **39.7** / rural **50.1** (nat 45.8 published).
- **TUN HIT:** EBCNV 2021 Volume A food+non-alc urban **28.8** / rural **34.3**.
- Pack → **427 / 68**.

## 2026-10-25 IRN HEIS 1402

- **IRN HIT:** SCI HEIS 1402 food urban **25.0** / rural **39.6** (via IranStatis citing SCI; amar.org.ir TLS-blocked).
- Pack → **429 / 69**.

## 2026-10-25 KEN + NGA + DZA

- **KEN HIT:** KCHS 2021 Poverty Report Table 3.2 food urban **42.2** / rural **63.0**.
- **NGA HIT:** NLSS/CEP 2019 food urban **51.52** / rural **61.30** (food incl. alcohol in NBS basket).
- **DZA HIT:** ONS 2011 alimentation&boissons urban **40.1** / rural **45.9**.
- Pack → **435 / 72**.
