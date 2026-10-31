# Engel companion gaps — QC snapshot (2026-10-25 Asia/Tokyo)

Inventory-driven open / blocked / Season2-owned gaps. **No fabricate.** Updated after supply-companion resume (fat / animal kcal share / cereal kg).

## Landed 2026-10-25 (non-CPI resume)
| file | rows | ISO3 | span | notes |
|------|-----:|-----:|------|-------|
| `fao_fbs_kcal_supply_panel.csv` | 11960 | 176 | 2010–2023 | el 664; items 2901/2905/2907/2903/2941; **JPN absent** |
| `fao_fs_cereal_root_tuber_energy_share_panel.csv` | 3732 | 185 | 2002–2023 | FS **21012**; 3y→end-year; Bennett-adj; JPN yes |
| `fao_fbsh_kcal_supply_panel.csv` | 24702 | 172 | 1961–2013 | el 664; 2901/2905/**2907**; JPN 1961–2013 |
| `fao_fs_energy_protein_supply_panel.csv` | 11224 | 185 | 2002–2025 | FS 22000 DES kcal + 21013/21014 protein |
| `fao_fs_avg_fat_supply_panel.csv` | 3732 | 185 | 2002–2023 | FS **21061**; 3y→end-year; JPN 8 |
| `fao_fbs_animal_kcal_share_panel.csv` | 2392 | 176 | 2010–2023 | 100×2941/2901; derived; JPN absent |
| `fao_fbs_cereal_food_supply_kg_panel.csv` | 2392 | 176 | 2010–2023 | el **645** item 2905; JPN absent |

Prior same-day (CPI/trade pause path): WDI food imports; Japan RPS miso/shoyu; FAOSTAT TI value indexes.

## Probe outcomes this turn (post calorie/Bennett QC)
| probe | result |
|-------|--------|
| Light QC on 4 calorie/Bennett panels | **PASS** → `engel_companion_qc_resume_2026-10-25.md` |
| FS 21061 average fat supply (local FS zip) | **HIT** → panel |
| FBS animal kcal share 2941/2901 (from kcal panel) | **HIT** → panel |
| FBS cereal food supply kg el645/2905 (local FBS zip) | **HIT** → panel |
| FBSH animal kcal share | **SKIP** — no item 2941 in FBSH kcal panel |
| Extra WDI food series | **SKIP** — no unused local WDI food raw |
| CAN/DNK/NOR absolute / avoid-list / Season2 / more CPI·HES | **not touched** |

## Explicit remaining gaps

### Still miss / open
- **CAN / DNK / NOR absolute staple retail levels** — **re-probed SKIP** 2026-10-25 (see hard-hole section); avoid further grind.
- **Korea food×income / KOSIS** — SSL-blocked; avoid.
- **Japan 総世帯 Engel (用途 continuous)** — **re-probed SKIP** 2026-10-25; longtime 品目-only.
- **FBS Japan 2010–** — still absent from bulk (use FBSH / FS 21012 / OWID).
- **FBSH animal kcal share** — would need 2941 in historic bulk (not in current slim/panel).

### Blocked / known-fail
- Avoid-list hosts (StatCan www150, KOSIS, MOSPI, Stats SA, Destatis, Banxico/INEGI, BPS/PSA, BLS CE, open.canada, Eurostat absolute).
- FAOSTAT TI API 521 (bulk path already used).
- USDA ERS Cost of Food at Home URL 404 (prior).

### Season2-owned (do not rebuild)
Eating-out shares · food×income · urban-rural · hours-to-buy · absolute staples (exc. Aoi hi_staple AUS+CHE) · OECD food-share long · Japan quintile · LatAm CPI holes · FAO country CPI bulk · ILO · ICP · Big Mac · PIP.

### Thick / stop collecting CPI
More EU food CPI · more FAO Food CPI geos · more European HES · IMF PCPS / Pink / CoAHD / shrinkflation covered.

## Hard-hole re-probe 2026-10-25 (post Season2 joint read)

Brief one-path probes only; **no Big-Mac-like yet**. Details: `raw/hi_staple_probe_2026-10-25/SKIP.txt`.

| hole | result | reason |
|------|--------|--------|
| CAN absolute staple retail | **SKIP** | Wayback CDX sees 18100245 zip; box TLS EOF on Wayback download (same as www150). No local absolute CSV. |
| DNK absolute staple retail | **SKIP** | DST catalog: 0 non-index food average-DKK tables (indexes only). |
| NOR absolute staple retail | **SKIP** | SSB search → electricity averages / KPI indexes; no food NOK levels. |
| Japan 総世帯 Engel 用途 | **SKIP** | longtime still 品目-only for 総世帯; no continuous 用途. |

Panel count unchanged: **92**. Prefer next: Big-Mac-like world product prices (user ask), not more absolute grind.

## Prefer next
Hard absolute holes re-probed → all SKIP. **Next per user:** Big-Mac-like world product prices (not forced digs). No more CAN/DNK/NOR/総世帯 grind.

## Avoid-list (unchanged)
StatCan www150, KOSIS, MOSPI, Stats SA, Destatis, Eurostat absolute, Banxico/INEGI, BPS/PSA, BLS CE, open.canada, more EU food CPI, more FAO Food CPI geos, more European HES, DNK/NOR/CAN absolute retry, food×income/urban-rural rebuild.

- Panel count: **92** `*_panel.csv`
- Snapshot: 2026-10-25 (Asia/Tokyo) — hard-hole re-probe same day


---

## Product indices pass (2026-10-25 Asia/Tokyo) — Big-Mac-like companions

Hard holes (CAN/DNK/NOR absolute retail; Japan 総世帯 用途 continuous): **all SKIP** (no new open path; no retry).

CPI/HES thickening: still paused.

### Landed (Aoi)
| File | Rows | Geos | Span | Notes |
|------|------|------|------|-------|
| `ubs_prices_earnings_price_level_panel.csv` | 1892 | 68 | 1970–2018 | UBS P&E via Hammar city price levels (NYC2015=100); not single-SKU |
| `starbucks_latte_burgerparity_panel.csv` | 30 | 30 | snapshot | Burger Parity; not continuous |
| `coca_cola_330ml_burgerparity_panel.csv` | 30 | 30 | snapshot | Burger Parity; not continuous |
| `numbeo_staples_restaurant_crowd_panel.csv` | 714 | ~101 | snapshot-2026-10-25 | **Crowd-sourced**; 7 items |
| `usb_flash_hblok_panel.csv` | 96 | global USD | 2003–2017 | USB/flash $/MB |
| `dram_memory_hblok_panel.csv` | 342 | global USD | 1957–2017 | DRAM/memory $/MB |

Panel CSV count after product pass: **98** (later tariff/parts pass → see below).

### Skipped (no open continuous multi-country without paywall/login)
- **UBS official open data microsite / High-D .mhd:** gone or unreachable; Drive “All Years of Data.xlsx” was **wrong source** (US residential property).
- **iPhone / flagship MSRP country panels:** Zenodo API empty/blocked; App Store / bigmacindex-style live scrapes login or unstable — SKIP (no force dig).
- **IKEA Billy / catalogue index:** OpenTheRank 404; other historical Billy series login/paywalled — SKIP.
- **Deutsche Bank latte / official Starbucks multi-year:** no open downloadable continuous panel found.
- **Coke company global MSRP time series:** not found open.
- **Numbeo historical bulk / API:** premium — only public HTML snapshot used.

Season2 owns Big Mac + staple absolute levels + hours-to-buy — untouched.


---

## Tariff / parts / trade pass (2026-10-25 Asia/Tokyo)

User ask: annual OK; **monthly also OK** if annual hard. Global multi-country preferred (not Japan-only). JETRO-like + WITS/WTO/UNCTAD/parts prices.

### Landed (Aoi)
| File | Rows | Geos | Span | Notes |
|------|------|------|------|-------|
| `wdi_tariff_rates_manufactures_panel.csv` | 30230 | 189 | 1988–2022 annual | **Tariff rates %** (applied/MFN; manuf/all/primary) via WDI←WITS/TRAINS/WTO |
| `wdi_trade_structure_manuf_tech_metals_panel.csv` | 18897 | 199 | 1962–2025 annual | High-tech export share; manuf / ores-metals import shares |
| `pink_sheet_industrial_metals_inputs_panel.csv` | 11463 | GLOBAL_USD | 1960–2026 monthly | Al/Cu/Fe/Ni/Zn/Sn/Pb + fertilizers + cotton/rubber |
| `fred_us_ppi_electronics_parts_panel.csv` | 3861 | USA | 1939–2026 monthly | US PPI semiconductors/computers/electrical (index) |
| `unctad_us_import_tariff_dashboard_snapshot_panel.csv` | 2421 | 172 | snapshot | US-import-weighted scenario tariffs — not continuous history |

Panel CSV count after this pass: **103**.

### Probe outcomes
| probe | result |
|-------|--------|
| WDI TM.TAX.* manuf/MRCH/primary + trade structure | **HIT** |
| Pink Sheet industrial metals/inputs (local CMO xlsx) | **HIT** |
| FRED/BLS US PPI electronics/parts (graph CSV) | **HIT** |
| UNCTAD tariff dashboard CSV | **HIT** (snapshot only) |
| JETRO WorldTariff | **SKIP** — registration; redistribution forbidden |
| WITS TRAINS API (HS product queries) | **SKIP** — 400 invalid product / timeouts; product metadata 405 |
| WITS public bulk zips (trade summary / at-a-glance) | **SKIP** — URLs return HTML 404 |
| WTO data.wto.org Analytical DB / avg tariff xlsx | **SKIP** — HTTP 403 from box |
| CEPII BACI / TUV full zips | **SKIP** — 0.7–2.4 GB; overkill for companion (open but not fetched) |
| UN Comtrade public API unit values | **SKIP** — no usable open response this turn |
| Japan MOF/Customs e-Stat HS unit values | **not dug** — global panels preferred; Japan OK as later supplement |

### Caveats
- Tariff panels are **rates (%)**, not prices.
- US PPI is **index**, USA-only; Pink metals are global USD levels.
- No food CPI/HES restart; Season2 Big Mac / staple absolutes untouched.


---

## Broaden pass — simple prices / 衣食住 (2026-10-25 Asia/Tokyo)

User ask: prefer **simple prices** (any genre); food OK; clothing/housing/other Engel-like shares; de-emphasize tariffs. Annual or monthly OK.

### Landed (Aoi) — type noted
| File | Rows | Geos | Span | Type |
|------|-----:|-----:|------|------|
| `eurostat_nama_engel_like_shares_panel.csv` | 5370 | 36 | 1975–2025 | **expenditure_share** (CP03/06/07/09/10 % HFCE) |
| `eurostat_hicp_clothing_housing_panel.csv` | 4024 | 37 | 1996–2025 | **price_index** (HICP CP03/031/04/041) |
| `eurostat_house_price_index_panel.csv` | 580 | 30 | 2005–2025 | **price_index** (HPI) |
| `oecd_house_prices_rents_panel.csv` | 8380 | 48 | 1956–2025 | **price_index_and_ratio** (HPI/RHP/RPI + ratios) |
| `bis_selected_residential_property_prices_panel.csv` | 17368 | 57 | 1927–2026Q | **price_index** (nom/real RPP 2010=100) |
| `oecd_cpi_clothing_housing_panel.csv` | 4050 | 45 | 1948–2025 | **price_index** (CPI CP03/04/041) |
| `faostat_producer_prices_usd_staples_panel.csv` | 24311 | 158 | 1991–2024 | **price_level** (USD/tonne PP) |
| `faostat_trade_unit_values_staples_panel.csv` | 197853 | 184 | 1961–2024 | **price_level** (derived trade UV USD/t) |

Panel CSV count after this pass: **111**.

### Probe outcomes
| probe | result |
|-------|--------|
| Eurostat NAMA CP03/06/07/09/10 % HFCE | **HIT** |
| Eurostat HICP clothing/housing annual index | **HIT** |
| Eurostat HPI annual | **HIT** |
| OECD DF_HOUSE_PRICES (+ rents, ratios) | **HIT** |
| BIS selected RPP (WS_SPP zip) | **HIT** |
| OECD CPI CP03/CP04/CP041 annual | **HIT** |
| OECD CPI CP031 garments annual | **SKIP** — NoResultsFound in DF_PRICES_ALL |
| FAOSTAT PP USD/tonne staples+fibre (local bulk) | **HIT** |
| FAOSTAT TCL derived UV limited items (~273MB bulk) | **HIT** |
| Full CEPII BACI | **SKIP** — not needed; FAO TCL subset used |
| More WDI/WITS/JETRO tariff grind | **SKIP** — per user de-emphasize |
| FRED US apparel/shelter CPI | **SKIP** — box timeout/HTTP2 errors |
| CAN/DNK/NOR absolute / Season2 verticals / more EU food CPI | **not touched** |

### Caveats
- Trade UVs are **derived** (value/qty), not an official UV product; extreme UV>500k USD/t dropped in QC.
- Housing panels are **indices/ratios/shares**, not absolute €/m² or rent levels.
- Distinct from existing `housing_cost_share_reference_panel` (CP04 share only) and thick FAO Food CPI packs.

## Specific-product / everyday SKU pass (2026-10-25 Asia/Tokyo)

User ask: named everyday SKUs (underwear, towels, tissue, soap, coffee, utilities…) for synthetic-country refs. **Handoff:** further **NSO** named-retail household SKU work → **Season2 #118**. Aoi stops new NSO scrapes after this land.

### Landed (Aoi)
| File | Rows | Geos | Span | Type | Crowd? |
|------|-----:|-----:|------|------|--------|
| `uk_ons_avg_retail_household_clothing_panel.csv` | 1385 | 1 (GBR) | 2018–2025m | named retail GBP | No |
| `eurostat_household_electricity_price_panel.csv` | 1491 | 43 | 2007–2026S | EUR/kWh unit | No |
| `eurostat_household_gas_price_panel.csv` | 2400 | 36 | 2007–2026S | EUR/GJ unit | No |
| `numbeo_clothing_utilities_markets_crowd_panel.csv` | 1020 | ~102 | snapshot | COL item USD | **Yes** |
| `bls_us_everyday_product_prices_panel.csv` | 520 | 1 (USA) | 1980–2026m | coffee APU USD | No |
| `japan_rps_everyday_clothing_household_panel.csv` | 1482 | 1 (JPN) | 2020–2025m | named retail JPY | No |

Panel CSV count after this pass: **117**.

### HIT / SKIP
| probe | result |
|-------|--------|
| UK ONS avgprice household/clothing SKUs | **HIT** |
| Eurostat nrg_pc_204 / nrg_pc_202 household electricity & gas | **HIT** |
| Numbeo clothing + utilities + selected markets (open HTML) | **HIT** (crowd) |
| Japan RPS everyday clothing/household/utilities (2020–2025 city mean) | **HIT** (landed; no further NSO dig) |
| BLS coffee APU (from existing numeraire raw) | **HIT** |
| BLS eggs / US electricity / gas APU live | **SKIP** — BLS 403/503, FRED empty |
| Numbeo underwear / toothpaste | **SKIP** — not in COL catalogue |
| Numbeo chicken/bananas/oranges/lettuce | **SKIP** — 429 throttle; not retried |
| Japan RPS 2015–16 / 2017–19 parse | **SKIP** — wrong IDs or old layout; raw kept for Season2 |
| ILO October Inquiry / ICP detailed continuous named goods | **SKIP** — no usable open continuous panel this turn |
| Season2 Big Mac / hi·euz staples / food×income | **not touched** |
| More NSO named-retail SKUs (other countries) | **STOP** — Season2 #118 |

### NSO raw handoff paths (for Season2)
- Japan RPS scrapes: `/workspace/aoi-phase2/raw/specific_products_2026-10-25/japan_rps/` (~177 `y*.xlsx` + 2025 `off*.bin` probes; hinmoku list `../hinmoku2025.txt`)
- UK ONS avgprice: `/workspace/aoi-phase2/raw/uk_ons/avgprice.csv`
- Panels already built from those: `japan_rps_everyday_clothing_household_panel.csv`, `uk_ons_avg_retail_household_clothing_panel.csv` (+ matching `*_readme.md`)

### Non-NSO raw kept
- Numbeo HTML: `/workspace/aoi-phase2/raw/specific_products_2026-10-25/numbeo/`
- Eurostat TSV: `nrg_pc_204.tsv.gz`, `nrg_pc_202.tsv.gz` (same folder)

---

## Household COL / index split resume (2026-10-25 Asia/Tokyo) — Aoi lane

User: resume household-adjacent after staples priority; **split with Season2**. Aoi = Numbeo/COL baskets + branded/product **indices** only. Season2 densifies NSO named-retail on #118 (from 3015/8).

### Landed (Aoi)
| File | Rows | Geos | Span | Type | Crowd? |
|------|-----:|-----:|------|------|--------|
| `numbeo_household_rent_comms_crowd_panel.csv` | 408 | 102 | snapshot | COL USD (rent 1-bed ×2, broadband, mobile) | **Yes** |
| `oecd_cpi_household_furnishings_panel.csv` | 1156 | 45 | 1990–2025 | CPI index CP05 | No |
| `eurostat_hicp_household_furnishings_panel.csv` | 2997 | 37 | 1996–2025 | HICP index CP05/CP056/CP0561 | No |

Panel CSV count after this pass: **120** top-level (`*_panel.csv`); **121** including nested raw.

### HIT / SKIP
| probe | result |
|-------|--------|
| Numbeo itemId 33 broadband + 34 mobile (open HTML) | **HIT** |
| Numbeo itemId 26/27 1-bed rent (reuse on-disk HTML) | **HIT** |
| OECD DF_PRICES_ALL annual CPI IX CP05 | **HIT** |
| Eurostat prc_hicp_aind CP05/CP056/CP0561 from existing bulk | **HIT** |
| OECD CP056/CP0561 | **SKIP** — NoRecordsFound |
| World Bank ICP household PLI | **SKIP** — Season2-owned (gaps avoid-list) |
| Numbeo toothpaste/underwear/detergent named SKUs | **SKIP** — not in COL catalogue |
| NSO named-retail household SKUs (new digs) | **STOP** — Season2 #118 |
| CAN/DNK/NOR absolute / Japan 総世帯 | **not touched** |

### For Season2 (not Aoi)
- Continue NSO named-retail densify (coffee/tea, soap/detergent, TP/tissue, towels/underwear) on #118.
- ICP detailed PLI / named goods if they want open DataBank path.
- CAN StatCan / KOR 참가격 alternate paths remain hard on this box.
