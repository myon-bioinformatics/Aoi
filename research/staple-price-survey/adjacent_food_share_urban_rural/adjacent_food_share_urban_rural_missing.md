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
