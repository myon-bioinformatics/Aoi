# Missing / blocked — adjacent_food_share_urban_rural

| ISO3 | Status |
|---|---|
| CAN | StatCan SSL / WDS failure; not loaded |
| ARG | ENGHo urban-only — no rural companion |
| CHL | INE IX EPF urban (regional capitals) only — no rural |
| CHE, TUR | Not in Eurostat HBS_STR_T226 extract used |
| URY, PAN | CEPALSTAT 5725 National only (no Urban/Rural) |
| HKG, SGP | City-state; no rural stratum — do not coerce |
| SAU, ARE | National/regional food % only in open HICES/HIES pubs; no urban/rural food Engel table loaded |
| PAK | HIES 2024–25 national Food & Non-Alc 36.72%; urban/rural food÷total not in open writeup; PPRI 34.2/48.1 not used |
| EGY | CAPMAS HIECS urban/rural cited in journals; primary CAPMAS table not pinned — deferred |
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
