# Missing / blocked — adjacent_food_share_urban_rural


### Session append (2026-10-25 ~01:56 JST)

| ISO3 | status | notes |
|------|--------|-------|
| XKX | **HIT** +2 | Eurostat HBS_STR_T226 2015 DEG1/DEG3 CP01 (geo=XK) |
| TUR | **MISS** (T226) | TR listed in T226 geo but **no values**; TUIK bulletin pages JS-only this egress |
| ARG / CHL | **MISS** UR | CEPALSTAT 5725 National-only (no Urban/Rural area) |
| SAU / ARE / SGP / HKG | **MISS / N/A** | no open UR primary / city-state |
| CHE | **MISS** UR | HABE Grossregion ≠ urban/rural; Einkommensklasse absolute CHF bands (INC already loaded) |

Hits now: **108 ISO3 · 525 rows**.

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

## 2026-10-25 UGA/TZA/ETH/KHM append

- **UGA HIT:** UBOS UNHS Table 6.4 food+non-alc — 2016/17 Urban 37.8 / Rural 50.8; 2019/20 Urban 33.8 / Rural 49.0. +4 rows.
- **TZA HIT:** NBS HBS 2017/18 Mainland Table 6.3.1 food % — Urban 52.6 / Rural 63.2 (prefer over Table 6.7.1 Total urban 55.2). +2 rows. Sibling food×income: Table 6.7.1 national deciles d1–d10 loaded.
- **ETH HIT:** CSA HCES 2015/16 via WFP CFSVA — Urban 40.6 / Rural 51.2. +2 rows.
- **KHM HIT:** NIS CSES 2019/20 Table 4 food share — Urban (Phnom Penh+Other urban from published food/total) 40.2 / Other rural 46.6; Food share includes alcoholic beverages. +2 rows.
- Pack → **445 / 76**. Hours-to-buy still DEU+BRA only.

## 2026-10-25 ZMB/MOZ append

- **ZMB HIT:** ZamStats LCMS 2022 executive summary — food expenditure % of household incomes Urban **34.7** / Rural **56.4**. +2 rows.
- **MOZ HIT:** INE IOF 2022 via AIM (10 Aug 2023) — food+non-alc % of total expenditure Urban **27.8** / Rural **49.3**. Primary IOF PDF egress-blocked; AIM quotes INE. +2 rows.
- Pack → **449 / 78**.

## 2026-10-25 CIV/RWA append

- **CIV HIT:** INS ENV 2015 — alimentation % dépense totale Urbain **39.1** / Rural **55.8** (national 45.6). +2 rows.
- **RWA HIT:** NISR EICV3 Patterns of Consumption — food % of total purchases Urban **36** / Rural **42** (2010–11). EICV6 final PDF lacked open food-share table this run. +2 rows.
- Pack with ZMB/MOZ → **453 / 80**.

## 2026-10-25 BWA/NAM/MLI append

- **BWA HIT:** Stats Botswana BMTHS 2015/16 Annexure 3 — Food % FCE; Urban (Cities+Urban Villages weighted) **10.5** / Rural **21.4**. +2 rows.
- **NAM HIT:** NSA NHIES 2015/16 Table 11.1.1 — Food and beverages Urban **26.9** / Rural **56.6**. Percentile bands not quintile/decile → food×income miss. +2 rows.
- **MLI HIT:** INSTAT EMOP 2023-P3 Tableau 2-4 — Alimentation+boissons non alc Urbain **63.3** / Rural **75.6**. +2 rows.
- Pack → **459 / 83**.

## 2026-10-25 LAO/MMR append

- **LAO HIT:** LSB LECS via WB Poverty Profile — food % total consumption; 2012/13 Urban 49.9 / Rural 64.8; 2018/19 Urban 53.1 / Rural 68.0. +4 rows.
- **MMR HIT:** CSO MLCS 2017 Figure 2-1b — food % consumption Urban **42.7** / Rural **55.7**. Sibling food×income q1–q5 from Figure 2-2b. +2 rows.
- Pack → **465 / 85**.

## 2026-10-25 FJI append

- **FJI HIT:** Fiji Bureau of Statistics HIES 2019-20 Figure 42 — food % per-AE consumption Urban **36.1** / Rural **46.6** (national 40.8). Sibling Table 20 food×income deciles. +2 rows.
- Pack → **467 / 86**.

## 2026-10-25 LSO/MUS/MDG append

- **LSO HIT:** BOS CMS 2011/12 Q3 — food&non-alc Urban **48.1** / Rural **66.7**. +2.
- **MUS HIT:** Statistics Mauritius HBS 2023 Table 5.3.2 — Food&non-alc Urban **28.2** / Rural **30.5**. +2. Sibling income quintiles.
- **MDG HIT:** INSTAT EPM 2021-22 Tableau 7.3 — alimentation Urbain **59.2** / Rural **68.5** (national 65.8). +2. Sibling Graphique 7.2 quintiles.
- Pack → **473 / 89**.

## 2026-10-25 BTN/NPL append

- **BTN HIT:** NSB BLSS 2017 — food Urban **30** / Rural **38** (national 34). +2. (BLSS 2022 urban 40.7 published; rural aggregate not stated — skip.)
- **NPL HIT:** CBS NLSS 2010/11 via WFP Table 17 — food Urban **52** / Rural **55** (national 54). +2. Sibling Table 18 quintiles.
- Pack → **477 / 91**.

## 2026-10-25 LBR/GMB/TON append

- **LBR HIT:** LISGIS HIES 2016 Table 3.5 — food Urban **61.3** / Rural **74.1**. +2. Sibling Table 3.6 quintiles.
- **GMB HIT:** GBoS IHS 2015/16 Table 4.7 — food Urban **52.9** / Rural **68.9**. +2. Sibling Table 4.8 deciles.
- **TON HIT:** Tonga HIES 2009 Table 2.5 — food Urban **44** / Rural **53**. +2.
- Pack → **483 / 94**.

## 2026-10-25 VUT/KIR append

- **VUT HIT:** VNSO HIES 2010 — food Urban **42.5** / Rural **62.1** (from published annual expenditure totals; national 56). +2.
- **KIR HIT:** NSO HIES 2023–24 Table 17 — Food&non-alc Urban **38.1** / Rural **42.4**. +2.
- Pack → **487 / 96**. SLB PDF still blocked (403/404).

## 2026-10-25 ~03:00 JST stop — Big Mac ISO3 remainder (urban/rural)

Pack: **525 rows / 108 ISO3**. Hours sibling still DEU+BRA only.

### Still-miss Big Mac ISO3 (excl. Aoi JPN/KOR/TWN/NZL)

| ISO3 | status | note |
|------|--------|------|
| HKG / SGP | **N/A** | City-state — no rural stratum; do not coerce |
| ARG / CHL | **MISS** (no rural) | ENGHo / EPF urban-only; CEPALSTAT 5725 National-only for UR |
| CAN | **MISS** (egress) | StatCan Daily SHS 2019 CMA vs rural food shares exist (reported 14.7/16.7) but www150 SSL/000 this box; not loaded without primary pin |
| CHE | **MISS** | HABE Grossregion ≠ urban/rural |
| TUR | **MISS** | Eurostat HBS_STR_T226 TR only publishes deg_urb=**UNK** (19.7%/20.4% PM÷10) — not Cities/Rural |
| ISR | **MISS** | CBS HES defines urban/rural localities but open pubs lack food-share×locality-type table |
| ARE / BHR / KWT / QAT / SAU | **MISS / N/A** | Gulf: no open UR food Engel; city-state-like / national-only |
| LBN / VEN | **MISS** (egress) | CAS/BCV primary UR food Engel not pinned |

No UR append this final stretch; INC densified LKA only.

## 2026-10-25 ~10:10 JST resume — CAN HIT + AZE 2024 primary

Pack: **529 rows / 109 ISO3**. Hours sibling still DEU+BRA (240/2).

| ISO3 | status | notes |
|------|--------|-------|
| CAN | **HIT** +2 | StatCan The Daily SHS 2019 Table 3 (t003b) via Wayback HTML pin (www150 TLS 000 this box): food÷goods&services — largest CMA ≥1M **14.7** / rural **16.7**; year=2019; Table 11-10-0226-01; `estimated_value` empty. Urban = largest-CMA proxy (not all urban). |
| AZE | **HIT refresh** +2 | SSC `evtes_2025.pdf` Cədvəl 38/39 2024 primary: urban **43.3** / rural **43.9** (kept prior banker.az 2023 rows) |
| ARG / CHL | **MISS** (no rural) | reconfirmed CEPALSTAT 5725 National-only (no Urban/Rural members); ENGHo / IX EPF urban-only |
| CHE | **MISS** | HABE Grossregion ≠ urban/rural; FSO HBS no Stadt/Land food÷total Engel |
| HKG / SGP | **N/A** | city-state; HES has district/housing tenure splits, not rural stratum — do not coerce |
| TUR ISR | **MISS** | unchanged |
| ARE BHR KWT QAT SAU LBN VEN | **MISS / N/A** | Gulf / egress — unchanged |

### Still-miss Big Mac ISO3 (urban/rural; excl. Aoi JPN/KOR/TWN/NZL)
ARE ARG BHR CHE CHL ISR KWT LBN QAT SAU TUR VEN (+ HKG/SGP **N/A**)
