# Aoi phase-2 — Engel / staple companion inventory

Date: **2026-10-24 Asia/Tokyo**. Skimmable inventory of **companion panels** now in `/workspace/aoi-phase2/` for Engel × staple / shrinkflation / numeraire work.

**Excluded:** GohanTrust bakeoff/rolling/judgment artifacts (`gohantrust_*`, `bakeoff_*`, `*_year_wins*`, NHK political helpers, kinkyu sensitivity, pack-ratio overlap diagnostics). Those stay in the folder but are not Engel companions.

**Season2-adjacent:** Flagged when the same *theme* also lives (or is being collected) under Season2 PR #118 `research/staple-price-survey/` — Aoi keeps its own tidy files; do not wholesale-duplicate Season2 verticals.

Full scout notes: `engel_global_ref_catalog_2026-10-24.md`. China detail: `china_national_food_cpi_readme.md`.

---

## Status (one paragraph)

As of 2026-10-24 JST, Aoi phase-2 holds Japan Engel for **二人以上** (annual+monthly) and **単身世帯** (annual 用途 stitch 2001–2024; no monthly longtime youto for 単身), a global Engel/Bennett stub, OWID/USDA/CoAHD/SOFI companions, Japan CPI food/cereals + retail rice + retail numeraire (食パン/牛乳/鶏卵/ゆでうどん, 2005–2025) + food-service activity, regional food CPI packs (Asia7, China continuous OECD 1993–2026-09, Africa/MENA, East EU, Eurostat HICP food), Eurostat eating-out, FAO/IMF world food indices, FAOSTAT staple producer prices, FBS 2010– cereal energy share (non-Japan) + FBSH historic cereal energy share (incl. Japan 1961–2013), USDA PSD rice/wheat production & ending stocks, international rice + Pink Sheet coffee/sugar/**wheat+maize**, Taiwan FIES food×income-quintile WL panel (Korea SSL-blocked), Orshansky US 3/3.7 citation memo, HI staple retail levels alt (`hi_staple_levels_alt`: AUS+CHE hit, CAN/DNK/NOR miss), BLS USA staple retail (rice/bread/flour/milk promoted), curated FPMA domestic staple LCU levels (33 ISO3; AUS/CAN/CHE/DNK/NOR/USA absent from FPMA staples), Pink Sheet vegetable oils, UK ONS avg retail food/eating-out items (2018–2025-01 archive), BLS CPI-U FAH/FAFH indexes (complement to existing USDA FES shares), ABS monthly CPI food subgroups (indexes; ECs from 2017-09), FPMA **international** food benchmarks (79 series), Pink Sheet food extras (cocoa/tea/barley/sorghum/meats/fruit), ONS CPI/CPIH/RPI food long indexes, Defra UK agri price indexes, Swiss BFS national food/restaurant CPI (LIK25B25, beyond FOAG levels), SSB Norway + DST Denmark national food CPI subgroups (indexes; levels still open), SCB Sweden + StatFin Finland + CBS Netherlands national food CPI subgroups (indexes; SWE absolute Season2-exhausted; NLD absolute in Season2 EUZ-proxy lane), INSEE France + ISTAT Italy + Statistik Austria + INE Spain + CSO Ireland + Statbel Belgium + Statistics Portugal INE + ELSTAT Greece (HICP COICOP18) + CZSO Czechia national food CPI subgroups (indexes; FRA/IRL/ESP/PRT absolute in Season2 EUZ-proxy; ITA/AUT/BEL absolute Season2-exhausted; GRC HICP deep tree vs Eurostat single CP011; CZE richer than easteu IMF/OECD aggregates), and shrinkflation.info capacity plus **capacity index** (product×unit, 100=base) and sparse annual median. Diversified companions (not more thick EU food CPI): **housing-cost share reference** (Eurostat CP04 full + OECD HC1.1.2; reference-not-Engel-core), **SGP/HKG/MAC food CPI indexes** (SingStat deep food tree + HK Censtatd COICOP Food/restaurants + IMF PCPIF; indexes ≠ Season2 adjacent_hi levels), and **USDA ERS Food Price Outlook** annual % changes + forecast midpoints (complement to BLS FAH/FAFH index levels). Further Asia/AU companions: **Japan CPI 中分類 food+外食** (`japan_cpi_food_meals_midclass`; 2025=100; meals-out price index ≠ Season2 eating-out shares), **ABS HES food expenditure shares** 1984–2015-16 (+ income-quintile 2015-16; ≠ ABS CPI), **Malaysia DOSM MCOICOP food subgroup tree** 2d–5d (beyond asia_national MYS div01), and **Thailand MOC CPIG** partial food tree (monthly food+cereals/flour; API mid-codes mostly 500/timeout). Also **Stats NZ HES food shares** (`nzl_hes_food_share_panel`; YE June 2016/2019/2023; NZHEC food subgroups + Food/Net; open release CSV/XLSX, not Infoshare API), and **FAOSTAT CP monthly food CPI** for IDN/PHL/VNM (`fao_idn_phl_vnm_food_cpi_panel`; 2015=100 + YoY; richer than asia_national annual ADB CP01; non-exclusive companion tidy of Season2 FAO country CPI bulk). Also **UK ONS LCFS national food share** (`uk_ons_lcfs_food_share_panel`; Table 4.2 COICOP 01 % of total expenditure FYE2002–FYE2025; national only — not Season2 food×income 3.2*), and **FAOSTAT CP monthly Food Indices for 16 thin Asia/Africa ISO3** (`fao_thin_asia_africa_food_cpi_panel`; BGD/PAK/LKA/NPL/KHM/LAO/MMR/MNG + ETH/GHA/TZA/UGA/CIV/SEN/CMR/MOZ; excludes geos already in asia/africa_mena/china/fao_idn packs). Also **CBS NL Budgetonderzoek national food shares** (`cbs_nl_hes_food_share_panel`; 1992–2010 legacy Voeding + 2015/2020 COICOP CPI01/CPI011; ≠ CBS CPI index panel), **FAOSTAT LatAm/Caribbean + Central Asia/Caucasus + MENA-thin monthly Food CPI** (`fao_latam_casia_food_cpi_panel`; 33 ISO3; non-exclusive vs Season2 LatAm holes/FAO bulk), and **Eurostat NAMA_10_CO3_P3 CP01/CP011 % of HFCE** (`eurostat_nama_food_share_hfce_panel`; 36 ISO3 continuous NA food share; ≠ Season2 OECD food-share long; promotes beyond stub’s 9 geos). Also **SSB Norway + Statistics Finland national HES food shares** (`ssb_nor_hes_food_share_panel` 1999–2012; `statfin_fin_hes_food_share_panel` 2012/2016/2022; national only — quintiles unused), **FAOSTAT Food CPI Pacific/Europe-thin/Caribbean leftovers** (`fao_thin_pacific_ee_caribbean_food_cpi_panel`; 37 ISO3), and **World Bank WDI food production index** (`wdi_food_production_index_panel`; AG.PRD.FOOD.XD; ~197 ISO3). Also **FAOSTAT Food CPI other_thin Africa/MENA/Asia leftovers** (`fao_other_thin_africa_mena_food_cpi_panel`; **49** ISO3 deferred from pacific/ee/caribbean turn; africa_leftover 36 + mena_leftover 9 + asia_leftover 4; ~163 ISO3 across all FAO Food CPI packs), **DST Denmark HES national food share** (`dst_denmark_hes_food_share_panel`; FU12 COICOP 01/00 %; 2015–2024; ≠ CPI index panel; FU15 income unused), and **Statistics Iceland HES national food share** (`hagstofa_iceland_hes_food_share_panel`; VIS05302 Per cent; 14 rolling windows 2000-2002…2013-2016; ≠ eurostat_nama HFCE for ISL; VIS05304 income unused). Also **Swiss BFS HABE national food share** (`bfs_switzerland_hes_food_share_panel`; 2006–2023; food/Konsumausgaben %; ≠ swiss_bfs_food_cpi indexes; ≠ Season2 CHE food×income), **Statbel Belgium HBS national food share** (`statbel_belgium_hes_food_share_panel`; 2018, 2020, 2022, 2024; COICOP 01/0; ≠ CPI indexes; Austria Konsumerhebung OGD skip), and **FOAG CHE extra staple retail levels** (`foag_che_extra_staple_levels_panel`; milk/eggs/potato/sunflower_oil/butter; eggs Centime→CHF; merged into hi_staple_levels_alt now 2610 rows). Also **FAOSTAT QI food/crops/cereals/livestock/agriculture gross production indices** (`faostat_food_production_index_qi_panel`; element 432; 2014-2016=100; **53,421** / **184** ISO3; 1961–2024; volume indexes — distinct from WDI AG.PRD.FOOD.XD single series and from FAOSTAT PP PPI 5539 already inside `faostat_producer_prices_staples`), and **Japan RPS extra staple yen levels** (`japan_retail_price_extra_staples_panel`; 小麦粉/バター/豚肉; **756** monthly city-means; 2005–2025; same bulk as numeraire). Also **Japan RPS oil/sugar/instant-coffee yen levels** (`japan_retail_price_oil_sugar_coffee_panel`; 食用油/砂糖/インスタントコーヒー; **696** monthly city-means; 2005–2025 with gaps: oil miss 2007–2009, coffee miss 2014/2022; distinct from numeraire + extras + Pink Sheet), **WDI cereal yield** (`wdi_cereal_yield_panel`; AG.YLD.CREL.KG; **10,632** / **184** ISO3; 1961–2024; ≠ WDI food production index / FAO QI), and **USDA NASS All-Farm Prices Paid/Received indexes** (`usda_nass_farm_price_index_panel`; 2011=100; **376** rows / 188 months; 2011-01…2026-08; open chart text). Also **WDI food imports % of merchandise imports** (`wdi_food_imports_pct_merchandise_panel`; TM.VAL.FOOD.ZS.UN; **8116** / **199** ISO3; 1962–2025; FAO TI API 521 this turn — WDI substitute), and **Japan RPS miso/soy-sauce yen levels** (`japan_retail_price_miso_shoyu_panel`; 1621/1631; **504** monthly city-means; 2005–2025; reused oil_sugar bulk). Also **FAOSTAT TI food trade value indexes** (`faostat_food_trade_indices_panel`; Imp/Exp Value Index 2014-2016=100; **197280** / **184** ISO3; 1961–2024; bulk zip — API still 521). **DNK/NOR absolute retail** re-scouted via new open mirrors — still miss (see `raw/hi_staple_scout_dnk_nor/SKIP.txt`); CAN www150 not touched. Season2 owns Big Mac universe staples, ICP/FAO country CPI bulk, Japan quintile Engel, FBS/FBSH Japan *focus* in their vertical (Aoi FBSH is companion tidy of the same open bulk — not exclusive), OECD food-share long series, PIP, ILO, LatAm CPI holes, `adjacent_eating_out_shares` (~1626 / 55 ISO3; USA skip; non-exclusive), and high-income NSO retail price levels (Season2 primary; Aoi `hi_staple_levels_alt` for AUS/CHE only — CAN/DNK/NOR **levels** still open; DNK/NOR/SWE/FIN/NLD/FRA/ITA/AUT/ESP/IRL/BEL/PRT/GRC/CZE national food **CPI indexes** now in Aoi via DST/SSB/SCB/StatFin/CBS/INSEE/ISTAT/Statistik Austria/INE/CSO/Statbel/INE-PT/ELSTAT/CZSO; Season2 `adjacent_euz_proxy_staple_levels` now AUT/DEU/ESP/FIN/FRA/IRL/NLD/PRT (~7585; DEU BMEL bread/flour/potato absolute EUR; BEL index-only) — non-exclusive).

---

## Companion panels

| file | what | ~rows | year span | Season2-adj | group |
|---|---|---:|---|---|---|
| `engel_food_panel_annual.csv` | Japan HH survey Engel×food shares (用途分類, annual, 二人以上) | 26 | 2000–2025 | no | Japan core |
| `engel_food_panel_monthly.csv` | Japan HH survey food/外食 monthly panel (二人以上) | 320 | 2000–2026 | no | Japan core |
| `engel_food_panel_single_annual.csv` | Japan HH survey Engel×food shares (用途分類, annual, **単身世帯**) | 24 | 2001–2024 | no | Japan core |
| `engel_annual_extended.csv` | Japan Engel annual extended helper | 26 | 1998–2023 | no | Japan helper |
| `engel_annual_excl_farm_computed.csv` | Japan Engel excl-farm computed series | 16 | 1990–2005 | no | Japan helper |
| `engel_global_ref_panel_stub.csv` | Global Engel×food stub (USDA/OWID/FAO FS/Eurostat/FBS/OECD housing) | 6,154 | 1995–2024 | yes | Global ref |
| `owid_food_expenditure_share_panel.csv` | OWID food share of consumer expenditure | 727 | 2017–2023 | yes | Engel proxy |
| `owid_staple_energy_share_panel.csv` | OWID staple dietary energy share (Bennett-adj) | 3,709 | 2001–2021 | yes | Bennett |
| `usda_fes_usa_food_expenditure_panel.csv` | USDA Food Expenditure Series (USA) | 1,885 | 1929–2026 | no | Engel USA |
| `coa_healthy_diet_panel.csv` | FAO Cost & Affordability of a Healthy Diet (CoAHD) | 9,442 | 2017–2025 | no | Diet cost |
| `sofi_food_insecurity_panel.csv` | SOFI / FIES food insecurity indicators | 18,907 | 2000–2025 | no | SOFI |
| `japan_cpi_food_cereals_panel.csv` | Japan CPI food / cereals / rice (monthly) | 2,952 | 1970–2026 | no | Japan CPI |
| `asia_national_food_cpi_panel.csv` | Asia7 national food CPI (ADB/OECD/DOSM) | 1,754 | 1980–2026 | no | Asia CPI |
| `china_national_food_cpi_panel.csv` | China food CPI continuous (OECD/FRED/ADB-NBS) | 1,668 | 1993–2026 | no | China CPI |
| `africa_mena_national_food_cpi_panel.csv` | Africa/MENA national food CPI | 4,867 | 1963–2026 | no | AF/MENA CPI |
| `easteu_national_food_cpi_panel.csv` | East Europe national food CPI | 4,382 | 1980–2025 | no | EastEU CPI |
| `eurostat_hicp_food_panel.csv` | Eurostat HICP food (CP011) long panel | 14,211 | 1996–2025 | no | EU HICP |
| `eurostat_eating_out_panel.csv` | Eurostat CP11 restaurants+hotels share / levels | 952 | 2000–2025 | yes | Eating-out EU |
| `japan_food_service_activity_panel.csv` | Japan METI food-service activity index | 2,652 | 2003–2026 | no | Japan 外食 activity |
| `japan_retail_price_rice_panel.csv` | Japan retail price survey — uruchi rice | 720 | 1999–2025 | yes | Japan rice |
| `japan_retail_price_numeraire_panel.csv` | Japan RPS yen levels — 食パン/牛乳/鶏卵/ゆでうどん | 2,016 | 2005–2025 | no | Japan numeraire |
| `fao_fbs_cereal_energy_share_panel.csv` | FAOSTAT FBS cereal kcal share (2905/2901) | 7,275 | 2010–2023 | yes | Bennett/FBS |
| `fao_fbsh_cereal_energy_share_panel.csv` | FAOSTAT **FBSH** cereal kcal share (2905/2901), domain=FBSH | 25,026 | 1961–2013 | yes | Bennett/FBSH |
| `usda_psd_grains_panel.csv` | USDA PSD rice (milled)+wheat production & ending stocks | 29,790 | 1960–2026 | no | Grains balance |
| `pink_sheet_coffee_sugar_panel.csv` | Pink Sheet coffee+sugar (promoted tidy) | 4,005 | 1960–2026 | no | Numeraire/commod |
| `pink_sheet_wheat_maize_panel.csv` | Pink Sheet maize + wheat HRW/SRW (monthly USD/mt) | 2,175 | 1960–2026 | no | Intl staples |
| `hi_staple_levels_alt_panel.csv` | HI staple **retail levels** alt (AUS 2011 ABS + CHE FOAG bread/flour/**milk/eggs/potato/sunflower_oil/butter**; CAN/DNK/NOR miss) | 2610 | 2011; 2000–2026 | yes | HI staple levels |
| `korea_taiwan_food_share_by_income_panel.csv` | Taiwan FIES food share × income quintile (WL); **Korea blocked** | 150 | 2001–2025 | no | WL / Engel |
| `rice_international_price_panel.csv` | Intl rice prices (Pink Sheet / AMIS-style) | 2,038 | 1960–2026 | no | Intl rice |
| `faostat_producer_prices_staples.csv` | FAOSTAT producer prices rice/wheat/maize | 36,627 | 1991–2025 | no | Producer prices |
| `fao_food_price_index_panel.csv` | FAO Food Price Index (world, monthly) | 2,646 | 1990–2026 | no | World FPI |
| `imf_pcps_food_index_panel.csv` | IMF PCPS food commodity index | 417 | 1992–2026 | no | Numeraire/commod |
| `bls_us_staple_retail_panel.csv` | BLS USA city-avg retail levels rice/bread/**flour**/milk (promoted; flour added) | 2,028 | 1980–2026 | no | USA staple levels |
| `fpma_domestic_staple_prices_panel.csv` | FAO GIEWS FPMA domestic staple LCU prices (curated 107 series / 33 ISO3; not Season2 vertical) | 24,942 | 1991–2026 | yes | Domestic staple levels |
| `pink_sheet_vegetable_oils_panel.csv` | Pink Sheet coconut/palm/soy/rape/sunflower oils + soybeans | 4,961 | 1960–2026 | no | Numeraire/commod |
| `uk_ons_avg_retail_food_panel.csv` | UK ONS experimental avg retail prices — food + restaurants/hotels CPIH items (GBP levels) | 14,290 | 2018–2025 | no | UK retail / eating-out |
| `bls_us_cpi_fah_fafh_panel.csv` | BLS CPI-U NSA indexes Food / FAH / FAFH / All items + derived FAH&FAFH÷Food ratios (≠ FES shares) | 4,296 | 1967–2026 | no | USA eating-out CPI |
| `abs_aus_cpi_food_panel.csv` | ABS CPI food subgroups + meals-out (monthly ECs 2017– + quarterly Food group 1980–; beyond 2011 levels) | 3,879 | 1980–2026 | yes | AUS CPI food |
| `fpma_international_staple_prices_panel.csv` | FAO FPMA **international** food benchmarks (79 monthly series; distinct from domestic LCU panel) | 26,513 | 1989–2026 | yes | Intl staple levels |
| `pink_sheet_food_extras_panel.csv` | Pink Sheet food extras (cocoa/tea/barley/sorghum/groundnuts/banana/orange/meats/shrimp/fish&soy meal) | 12,392 | 1960–2026 | no | Numeraire/commod |
| `uk_ons_cpi_rpi_food_index_panel.csv` | ONS CPI/CPIH/RPI food indexes + catering + YoY (long MM23; beyond experimental item avgs) | 6,420 | 1948–2026 | no | UK food CPI |
| `defra_uk_agri_price_index_panel.csv` | Defra UK Agricultural Price Indices (farmgate output + food-related inputs) | 9,472 | 2014–2026 | no | UK farmgate |
| `swiss_bfs_food_cpi_panel.csv` | Swiss BFS/SFSO national CPI food+restaurants (LIK25B25 INDEX_m; Dec2025=100; beyond FOAG levels) | 34,323 | 1982–2026 | no | CHE food CPI |
| `ssb_norway_food_cpi_panel.csv` | SSB Norway national CPI food subgroups (table 03013; 2015=100; levels still open) | 12,240 | 1979–2025 | no | NOR food CPI |
| `dst_denmark_food_cpi_panel.csv` | DST Denmark national CPI food subgroups (PRIS01 Index; levels still open) | 21,168 | 2000–2026 | no | DNK food CPI |
| `scb_sweden_food_cpi_panel.csv` | SCB Sweden national CPI food COICOP subgroups (KPI2020COICOPM; 2020=100; absolute levels Season2-exhausted) | 43,443 | 1980–2026 | no | SWE food CPI |
| `statfin_finland_food_cpi_panel.csv` | Statistics Finland national CPI food subgroups (khi/15b5; 2025=100; richer than Eurostat HICP CP011) | 18,371 | 1995–2026 | no | FIN food CPI |
| `cbs_netherlands_food_cpi_panel.csv` | CBS Netherlands CPI food+restaurants expenditure categories (83131ENG; 2015=100; indexes; Season2 holds NLD absolute levels) | 26,402 | 1996–2025 | no | NLD food CPI |
| `insee_france_food_cpi_panel.csv` | INSEE France national CPI food+restaurants COICOP (IPC-2025; 2025=100; richer than Eurostat HICP CP011) | 32,874 | 1996–2026 | no | FRA food CPI |
| `istat_italy_food_cpi_panel.csv` | ISTAT Italy NIC food+restaurants ECOICOP (NIC1B2015; 2015=100; indexes; absolute Season2-exhausted) | 21,528 | 2016–2025 | no | ITA food CPI |
| `statistik_austria_food_cpi_panel.csv` | Statistik Austria VPI food+restaurants COICOP18 (bases 2015/2020/2025 Messzahl; indexes) | 16,224 | 2016–2026 | no | AUT food CPI |
| `ine_spain_food_cpi_panel.csv` | INE Spain IPC ECOICOP ver.2 food+restaurants (groups/subgroups/subclasses; 2025=100; richer than Eurostat HICP CP011) | 11,268 | 2002–2026 | no | ESP food CPI |
| `cso_ireland_food_cpi_panel.csv` | CSO Ireland CPI detailed sub-indices food+restaurants (PxStat CPM24; Dec2023=100; indexes; Season2 holds IRL absolute levels) | 29,035 | 1996–2026 | no | IRL food CPI |
| `statbel_belgium_food_cpi_panel.csv` | Statbel Belgium CPI COICOP food+restaurants (All groups open data; 2025=100; indexes; absolute Season2-exhausted) | 22,939 | 2006–2026 | no | BEL food CPI |
| `ine_portugal_food_cpi_panel.csv` | Statistics Portugal INE IPC Base-2025 COICOP food+restaurants (varcd 0014639; deep subclasses; richer than Eurostat HICP CP011) | 28,245 | 1948–2026 | no | PRT food CPI |
| `elstat_greece_food_cpi_panel.csv` | ELSTAT Greece HICP COICOP 2018 food+restaurants (data.gov.gr; deep subclasses; richer than Eurostat single CP011) | 17,974 | 1995–2025 | no | GRC food CPI |
| `czso_czechia_food_cpi_panel.csv` | CZSO Czechia CPI COICOP 2018 food+catering classes (CEN0101E; 2025=100; richer than easteu IMF/OECD aggregates) | 2,115 | 2015–2026 | no | CZE food CPI |
| `housing_cost_share_reference_panel.csv` | **REFERENCE-NOT-ENGEL-CORE** housing share: Eurostat CP04 % HFCE (full) + OECD AHD HC1.1.2 housing+energy % HFCE | 2,162 | 1995–2025 | yes | Housing ref |
| `sgp_hkg_food_cpi_index_panel.csv` | SGP SingStat food/F&B CPI subgroups (2024=100) + HKG Censtatd COICOP Food/restaurants Composite + IMF PCPIF SGP/HKG/MAC (indexes; ≠ Season2 levels) | 16,241 | 1961–2026 | yes | Thin-geo CPI |
| `usda_ers_food_price_outlook_panel.csv` | USDA ERS Food Price Outlook — annual food CPI % changes (22 items, 1974–2025) + historical forecast midpoints | 10,381 | 1974–2025 | no | USA FPO |
| `japan_cpi_food_meals_midclass_panel.csv` | Japan 総務省 CPI 2025-base **中分類** food tree + **外食** price index (nationwide monthly) | 14,022 | 1970–2026 | no | Japan CPI midclass |
| `abs_hes_food_share_panel.csv` | ABS HES Australia food expenditure shares (national 1984–2015-16 + equivalised income quintiles 2015-16); ≠ ABS CPI | 42 | 1984–2016 | no | AUS HES shares |
| `mys_dosm_food_cpi_subgroup_panel.csv` | Malaysia DOSM CPI MCOICOP food branch 2d–5d (73 codes; beyond asia_national MYS div01) | 14,553 | 1980–2026 | no | MYS food subgroups |
| `tha_moc_food_cpi_subgroup_panel.csv` | Thailand MOC CPIGIndexes **partial** food tree (all_items + food NAB + rice/flour monthly; mid-codes API-failed) | 780 | 2000–2024 | no | THA food CPI partial |
| `nzl_hes_food_share_panel.csv` | Stats NZ HES food expenditure shares + NZHEC 01.1–01.5 weekly NZD (national 2016/2019/2023; Food/Net + published headline %); downloadable CSV/XLSX ≠ Infoshare API | 26 | 2016–2023 | no | NZL HES shares |
| `fao_idn_phl_vnm_food_cpi_panel.csv` | FAOSTAT CP monthly Food Indices (2015=100) + food inflation YoY for IDN/PHL/VNM; richer freq than asia_national ADB annual CP01; aggregate Food only (no mid-tree); non-exclusive vs Season2 FAO country CPI bulk | 1,872 | 2000–2026 | yes | ASEAN FAO food CPI |
| `uk_ons_lcfs_food_share_panel.csv` | ONS LCFS / Family Spending **national** COICOP 01 food & non-alcoholic drinks % of total expenditure (Table 4.2; constant FYE2025 prices; FYE2002–FYE2025); ≠ Season2 food×income quintile/decile tables 3.2* | 26 | 2002–2025 | no | GBR LCFS Engel share |
| `fao_thin_asia_africa_food_cpi_panel.csv` | FAOSTAT CP monthly Food Indices (2015=100) for **16 thin** Asia/Africa ISO3 not in asia/africa_mena/china/fao_idn packs (BGD PAK LKA NPL KHM LAO MMR MNG ETH GHA TZA UGA CIV SEN CMR MOZ); non-exclusive companion tidy of open bulk | 5,088 | 2000–2026 | yes | Thin-geo FAO food CPI |
| `cbs_nl_hes_food_share_panel.csv` | CBS Netherlands Budgetonderzoek **national** food expenditure shares (60046ned Voeding 1992–2010 + 83676NED CPI01/CPI011 2015/2020); ≠ `cbs_netherlands_food_cpi_panel` indexes; income deciles unused | 21 | 1992–2020 | no | NLD HES Engel share |
| `fao_latam_casia_food_cpi_panel.csv` | FAOSTAT CP monthly Food Indices (2015=100) for **33** LatAm/Caribbean + Central Asia/Caucasus + MENA-thin ISO3 not in asia/africa_mena/china/fao_idn/fao_thin packs; non-exclusive companion tidy vs Season2 LatAm holes / FAO bulk | 10,444 | 2000–2026 | yes | LatAm/CA FAO food CPI |
| `eurostat_nama_food_share_hfce_panel.csv` | Eurostat NAMA_10_CO3_P3 CP01 + CP011 as **% of HFCE** (PC_TOT); 36 ISO3 (EU/EA aggregates skipped); full multi-country NA food share beyond stub’s 9 geos; ≠ Season2 OECD food-share long; ≠ eating-out CP11 | 2,084 | 1975–2025 | yes | EU NA food share |
| `ssb_nor_hes_food_share_panel.csv` | SSB Norway Forbruksundersøkelsen **national** food share of total consumption expenditure (table 10235 AndForbrUtg; COICOP 01/011); ≠ CPI index panel; income/HH-type unused | 24 | 1999–2012 | no | NOR HES Engel share |
| `statfin_fin_hes_food_share_panel.csv` | Statistics Finland ktutk **national** food share of HH consumption (14q8; COICOP 01/011; whole country; survey years 2012/2016/2022); ≠ CPI; 14pg quintiles unused | 6 | 2012–2022 | no | FIN HES Engel share |
| `fao_thin_pacific_ee_caribbean_food_cpi_panel.csv` | FAOSTAT CP monthly Food Indices (2015=100) for **37** leftover Pacific + Europe-thin + Caribbean ISO3 not in prior fao_*/asia/africa_mena/china packs; non-exclusive vs Season2 FAO bulk | 11,754 | 2000–2026 | yes | Thin-geo FAO food CPI |
| `wdi_food_production_index_panel.csv` | World Bank WDI AG.PRD.FOOD.XD Food production index (2014–2016=100); multi-country annual; aggregates excluded; Engel-adjacent supply companion ≠ CPI/HES | 11,516 | 1961–2024 | no | WDI food output |
| `fao_other_thin_africa_mena_food_cpi_panel.csv` | FAOSTAT CP monthly Food Indices (2015=100) for **49** other_thin Africa/MENA/Asia leftover ISO3 not in any prior fao_*/asia/africa_mena/china packs (deferred from pacific/ee/caribbean turn); region_group africa/mena/asia_leftover; non-exclusive vs Season2 FAO bulk | 14,914 | 2000–2026 | yes | Thin-geo FAO food CPI |
| `dst_denmark_hes_food_share_panel.csv` | DST Denmark Forbrugsundersøgelsen **national** food share of total expenditure (FU12; COICOP 01/00 current-price DKK); ≠ `dst_denmark_food_cpi_panel` indexes; FU15 income unused | 10 | 2015–2024 | no | DNK HES Engel share |
| `hagstofa_iceland_hes_food_share_panel.csv` | Statistics Iceland **HES** national food share of total expenditure (VIS05302 Per cent; Total residence; rolling multi-year windows); ≠ eurostat_nama HFCE (ISL already there); VIS05304 income unused | 14 | 2000–2016 | no | ISL HES Engel share |
| `bfs_switzerland_hes_food_share_panel.csv` | Swiss BFS HABE national food share of Konsumausgaben (51/50 %); + % of Bruttoeinkommen retained | 18 | 2006–2023 | no | CHE HES Engel |
| `statbel_belgium_hes_food_share_panel.csv` | Statbel HBS/EBM national food share (COICOP 01/0 %); biennial | 4 | 2018–2024 | no | BEL HES Engel |
| `foag_che_extra_staple_levels_panel.csv` | FOAG CHE extra staple **retail levels** (milk/eggs/potato/sunflower_oil/butter); also merged into hi_staple_levels_alt | 2233 | 2000-01…2026-09 | yes | CHE FOAG levels |
| `faostat_food_production_index_qi_panel.csv` | FAOSTAT QI Gross Production Index (2014-2016=100) Food/Crops/Livestock/Agriculture/Cereals primary; volume ≠ prices; distinct from WDI food output + PP PPI | 53421 | 1961–2024 | no | FAO QI production |
| `faostat_food_trade_indices_panel.csv` | FAOSTAT TI food Imp/Exp **Value** indexes (2014-2016=100; food aggregates; API 521→bulk) | 197280 | 1961–2024 | no | FAO trade |
| `japan_retail_price_extra_staples_panel.csv` | Japan RPS yen levels — **小麦粉/バター/豚肉** (city-mean monthly; same bulk/schema as numeraire) | 756 | 2005–2025 | no | Japan RPS extras |
| `japan_retail_price_oil_sugar_coffee_panel.csv` | Japan RPS yen levels — **食用油/砂糖/インスタントコーヒー** (city-mean monthly; oil pack-spec break noted; coffee ≠ Pink Sheet) | 696 | 2005–2025 | no | Japan RPS oil/sugar/coffee |
| `japan_retail_price_miso_shoyu_panel.csv` | Japan RPS しょう油/みそ yen levels (1621/1631; from oil_sugar bulk; full monthly) | 504 | 2005–2025 | no | Japan RPS levels |
| `wdi_cereal_yield_panel.csv` | World Bank WDI AG.YLD.CREL.KG Cereal yield (kg/ha); multi-country annual; aggregates excluded; ≠ WDI food production index / FAO QI | 10,632 | 1961–2024 | no | WDI cereal yield |
| `wdi_food_imports_pct_merchandise_panel.csv` | WDI food imports % of merchandise imports (TM.VAL.FOOD.ZS.UN; trade/import-dependence; FAO TI 521→WDI substitute) | 8116 | 1962–2025 | no | WDI trade |
| `usda_nass_farm_price_index_panel.csv` | USDA NASS All-Farm **Prices Paid** + **Prices Received** indexes (2011=100; monthly US; open chart text) | 376 | 2011–2026 | no | USA farm price index |
| `shrinkflation_capacity_panel.csv` | shrinkflation.info capacity/pack panel (bulk products) | 2,485 | 1973–2026 | no | Shrinkflation |
| `shrinkflation_capacity_index_panel.csv` | Capacity index (100=base per product×unit); derived, no new scrape | 2,476 | 1973–2026 | no | Shrinkflation |
| `shrinkflation_capacity_index_annual_median.csv` | Sparse annual median of capacity indexes (document n) | 43 | 1973–2026 | no | Shrinkflation |
| `shrinkflation_capacity_products.csv` | shrinkflation.info product master | 508 | ? | no | Shrinkflation |
| `country_maam_shrinkflation_series.csv` | Fujiya Country Ma'am pack/g/yen chronology | 12 | 1992–2024 | no | Shrinkflation JP |

## Readmes (pair with panels)

- `insee_france_food_cpi_readme.md`
- `istat_italy_food_cpi_readme.md`
- `statistik_austria_food_cpi_readme.md`
- `ine_spain_food_cpi_readme.md`
- `cso_ireland_food_cpi_readme.md`
- `statbel_belgium_food_cpi_readme.md`
- `ine_portugal_food_cpi_readme.md`
- `elstat_greece_food_cpi_readme.md`
- `czso_czechia_food_cpi_readme.md`
- `housing_cost_share_reference_readme.md`
- `sgp_hkg_food_cpi_index_readme.md`
- `usda_ers_food_price_outlook_readme.md`
- `japan_cpi_food_meals_midclass_readme.md`
- `abs_hes_food_share_readme.md`
- `mys_dosm_food_cpi_subgroup_readme.md`
- `tha_moc_food_cpi_subgroup_readme.md`
- `nzl_hes_food_share_readme.md`
- `fao_idn_phl_vnm_food_cpi_readme.md`
- `uk_ons_lcfs_food_share_readme.md`
- `fao_thin_asia_africa_food_cpi_readme.md`
- `cbs_nl_hes_food_share_readme.md`
- `fao_latam_casia_food_cpi_readme.md`
- `eurostat_nama_food_share_hfce_readme.md`
- `ssb_nor_hes_food_share_readme.md`
- `statfin_fin_hes_food_share_readme.md`
- `fao_thin_pacific_ee_caribbean_food_cpi_readme.md`
- `wdi_food_production_index_readme.md`
- `fao_other_thin_africa_mena_food_cpi_readme.md`
- `dst_denmark_hes_food_share_readme.md`
- `hagstofa_iceland_hes_food_share_readme.md`
- `foag_che_extra_staple_levels_readme.md`
- `faostat_food_production_index_qi_readme.md`
- `japan_retail_price_extra_staples_readme.md`
- `japan_retail_price_oil_sugar_coffee_readme.md`
- `wdi_cereal_yield_readme.md`
- `usda_nass_farm_price_index_readme.md`
- `statbel_belgium_hes_food_share_readme.md`
- `bfs_switzerland_hes_food_share_readme.md`
- `scb_sweden_food_cpi_readme.md`
- `statfin_finland_food_cpi_readme.md`
- `cbs_netherlands_food_cpi_readme.md`
- `swiss_bfs_food_cpi_readme.md`
- `ssb_norway_food_cpi_readme.md`
- `dst_denmark_food_cpi_readme.md`
- `fpma_international_staple_prices_readme.md`
- `pink_sheet_food_extras_readme.md`
- `uk_ons_cpi_rpi_food_index_readme.md`
- `defra_uk_agri_price_index_readme.md`
- `uk_ons_avg_retail_food_readme.md`
- `bls_us_cpi_fah_fafh_readme.md`
- `abs_aus_cpi_food_readme.md`
- `bls_us_staple_retail_readme.md`
- `fpma_domestic_staple_prices_readme.md`
- `pink_sheet_vegetable_oils_readme.md`
- `africa_mena_national_food_cpi_readme.md`
- `asia_national_food_cpi_readme.md`
- `china_national_food_cpi_readme.md`
- `coa_healthy_diet_readme.md`
- `easteu_national_food_cpi_readme.md`
- `engel_food_panel_monthly_readme.md`
- `engel_food_panel_readme.md`
- `engel_food_panel_single_readme.md`
- `eurostat_eating_out_readme.md`
- `eurostat_hicp_food_readme.md`
- `fao_fbs_cereal_energy_share_readme.md`
- `fao_fbsh_cereal_energy_share_readme.md`
- `fao_food_price_index_readme.md`
- `faostat_producer_prices_staples_readme.md`
- `imf_pcps_food_index_readme.md`
- `hi_staple_levels_alt_readme.md`
- `japan_cpi_food_cereals_readme.md`
- `japan_food_service_activity_readme.md`
- `japan_retail_price_numeraire_readme.md`
- `japan_retail_price_rice_readme.md`
- `owid_engel_companion_readme.md`
- `pink_sheet_coffee_sugar_readme.md`
- `pink_sheet_wheat_maize_readme.md`
- `korea_taiwan_food_share_by_income_readme.md`
- `orshansky_food_basket_multipliers_memo.md`
- `rice_international_price_readme.md`
- `shrinkflation_capacity_index_readme.md`
- `shrinkflation_capacity_readme.md`
- `sofi_food_insecurity_readme.md`
- `usda_fes_usa_food_expenditure_readme.md`
- `usda_psd_grains_readme.md`
- `engel_food_forms_prelock_2026-10-24.md`
- `engel_global_ref_catalog_2026-10-24.md`
- `extend_rerun_prelock_2026-10-24.md`
- `numeraire_candidate_catalog_2026-10-24.md`
- `pack_ratio_sensitivity_prelock_2026-10-24.md`
- `rolling_prelock_2026-10-24.md`
- `yoy_prelock_2026-10-24.md`

## Raw directories

- `raw/insee_fr/`
- `raw/istat_it/`
- `raw/statistik_at/`
- `raw/ine_es/`
- `raw/cso_ie/`
- `raw/statbel_be/`
- `raw/destatis_de/` (probes only; GENESIS auth blocked)
- `raw/scb_se/`
- `raw/statfin_fi/`
- `raw/cbs_nl/`
- `raw/oecd_can/` (probes only; no CAN panel landed)
- `raw/swiss_bfs/`
- `raw/ssb_no/`
- `raw/dst_dk/`
- `raw/hes_scout/dst/` (FU12 JSON-stat)
- `raw/hes_scout/iceland/` (VIS05302)
- `raw/fao_cp_other_thin/` (PROVENANCE; reuses idn_bps/fao_cpi bulk)
- `raw/statssa/`
- `raw/africa_mena_cpi/`
- `raw/asia_food_cpi/`
- `raw/china_cpi/`
- `raw/coa_fpn/`
- `raw/country_maam/`
- `raw/easteu_cpi/`
- `raw/engel_food/`
- `raw/engel_global_ref/`
- `raw/housing_ref/` (symlinks to engel_global_ref Eurostat/OECD housing sources)
- `raw/sgp_hkg_cpi/`
- `raw/usda_ers_fpo/`
- `raw/japan_cpi_meals/` (copy of e-Stat 000040482943 utf8)
- `raw/abs_hes/`
- `raw/asia_food_subgroups/mys_dosm/`
- `raw/asia_food_subgroups/tha_moc/`
- `raw/asia_food_subgroups/nzl_hes/`
- `raw/asia_food_subgroups/idn_bps/` (BPS 403 probes + FAOSTAT CP bulk extract)
- `raw/uk_lcfs/` (ONS Family Spending workbook1 FYE2025/2024/2001–2019 + Defra Family Food UKExp/UKHHcons ODS)
- `raw/fao_cp_thin/` (provenance stub; reuses idn_bps/fao_cpi bulk)
- `raw/bls_ce/` (BLS CE probes; download.bls.gov 403 / api.bls.gov 503 — no panel)
- `raw/asia_food_subgroups/phl_alt/` (PSA/BSP/CKAN probes; OpenSTAT 403)
- `raw/asia_food_subgroups/vnm_gso/` (GSO TLS probes)
- `raw/asia_food_subgroups/kor_oecd/` (OECD deep COICOP probe; CP011* absent)
- `raw/asia_food_subgroups/can_hes/` (Canada non-www150 probes; no multi-year HES)
- `raw/ine_pt/`
- `raw/elstat_gr/`
- `raw/czso_cz/`
- `raw/fpma/`
- `raw/fao_fpi/`
- `raw/faostat_fbs/`
- `raw/faostat_fbsh/`
- `raw/faostat_pp/`
- `raw/imf_pcps/`
- `raw/japan_cpi/`
- `raw/japan_food_service/`
- `raw/japan_rps_numeraire/`
- `raw/japan_rps_extra/`
- `raw/japan_rps_oil_sugar/`
- `raw/wdi_cereal_yield/`
- `raw/usda_nass_farm_price_index/`
- `raw/fao_qi/`
- `raw/fao_ppi/` (QI zip scout + Prices zip; PPI not re-extracted)
- `raw/hi_staple_scout_dnk_nor/`
- `raw/japan_rps_rice/`
- `raw/korea_taiwan_wl/`
- `raw/numeraire/`
- `raw/orshansky/`
- `raw/owid_extend/`
- `raw/rice_intl/`
- `raw/shrinkflation/`
- `raw/sofi_fs/`
- `raw/usda_fes/`
- `raw/usda_psd/`
- `raw/cbs_nl_hes/`
- `raw/fao_cp_latam_casia/`
- `raw/eurostat_nama_food_share/`
- `raw/ssb_nor_hes/`
- `raw/statfin_hes/`
- `raw/fao_cp_thin_pacific_ee/`
- `raw/wdi_food_production/`
- `raw/xlsx_probe/`

## Intentionally not in this inventory

- Season2 PR #118 lanes: ICP, FAO country CPI bulk, Japan quintile Engel, FBS Japan *focus*, OECD food-share long series, PIP, ILO food CPI, LatAm CPI holes, high-income Big Mac NSO retail price levels (rice/bread/flour). Aoi may keep companion tidies of the same open bulks (e.g. FBSH cereal share) when documented as non-exclusive.
- GohanTrust rice×NHK bakeoff panels and rolling-origin diagnostics.
- **Korea KOSIS/KOSTAT quintile food shares:** attempted; box SSL EOF to kostat/mods/data.go.kr — see `korea_taiwan_food_share_by_income_readme.md`.
- **単身・月次用途:** not built — e-Stat longtime has no 単身 monthly 用途表 (see `engel_food_panel_single_readme.md`).
- **FPMA gaps (staples keywords):** AUS/CAN/CHE/DNK/NOR/SGP/HKG/NZL/MYS/USA not in curated FPMA pull — API has no matching rice/wheat/maize/bread/flour domestic series for those ISO3 in the filter used.
- **Japan 総世帯 Engel:** longtime e-Stat has 総世帯 **品目分類** annual only (not 用途 longtime like 二人以上); yearbook 用途 exists as quarterly/annual slices — not built this turn (二人以上+単身 already cover core).

- **Season2 Aoi #118 `adjacent_euz_proxy_staple_levels`:** Season2 now AUT/DEU/ESP/FIN/FRA/IRL/NLD/PRT (~7585 rows; DEU BMEL bread/flour/potato absolute EUR; BEL exhausted → index-only). Aoi does not claim this lane exclusively (ESP/IRL/BEL/NLD/FIN/FRA/ITA/AUT/PRT national food **CPI indexes** + GRC ELSTAT HICP deep tree + CZE CZSO COICOP classes landed separately; DEU Destatis GENESIS guest 401 — skip).
- **Season2 Aoi #118 `adjacent_eating_out_shares`:** Season2 panel ~**1626** rows / **55** ISO3 (USA skip; non-exclusive). Aoi keeps Eurostat CP11 twin in `eurostat_eating_out_panel.csv` and does **not** rebuild a competing multi-country eating-out expenditure-share panel.
- **Season2 Aoi #118 `adjacent_food_share_by_income`:** Season2 panel now ~**814** rows / **37** ISO3 (incl. USA BLS CE + CAN SHS Daily; BEL/DEU/ESP/FRA/ITA/NLD HBS; ISR; CHE; SGP; ZAF IES1995; etc.; SAU/ARE/HKG-quartiles/VNM still Season2 miss; non-exclusive). Aoi does **not** rebuild food×income and does **not** rebuild USA CE or CAN SHS; keeps ABS HES + NZL HES + UK LCFS national share panels. National long HES for Nordic OK if distinct from Season2 quintile slices.
- **Season2 Aoi #118 `adjacent_hi_staple_levels`:** Season2 pushed HKG/MYS/NZL/QAT/SGP/TWN (~2385 rows). CAN/DNK/NOR remain open/miss on levels; StatCan not retried by either side. Aoi does not claim this lane exclusively (indexes for DNK/NOR landed separately above).
- **Stats SA / South Africa official CPI timeseries zips:** `statssa.gov.za` timeseries + P0141 PDF behind Incapsula (403/challenge from this box). ZAF food CPI index already in `africa_mena_national_food_cpi_panel.csv` (OECD CP01, 1970–2024). SA Data Hub third-party export is short YoY % only (~May 2025–Sep 2026) — not landed. Average-price zips not retrieved.
- **Swiss BFS SDMX API:** `disseminate.stats.swiss` dataflow probe failed (API version / dataflow errors); used official LIK25B25 XLSX instead.
- **FAO FFPI subgroups / IMF PCPS extras:** FFPI meat/dairy/cereal/oils/sugar already in `fao_food_price_index_panel.csv`; IMF PCPS only aggregate food index present — commodity extras largely covered by Pink Sheet panels; not re-pulled.
- **Destatis Germany food CPI (GENESIS 61111-0004):** skipped — GENESIS REST returned 401 for Guest/GOEST from this box; no open unauthenticated CSV mirror landed. Austria VPI subgroups cover the DEU/AUT third slot this turn.
- **GUS Poland / HCSO Hungary food CPI subgroups:** skipped this turn — `easteu_national_food_cpi_panel.csv` already holds POL/HUN IMF/OECD aggregate food CPI; no open multi-class national COICOP tree landed richer than that pack (GUS BDL shallow division-01 only in probe). Czechia CEN0101E filled the east-EU third slot instead.
- **Canada CPI food (FRED/OECD/DBnomics multi-series):** re-confirmed skip — still only aggregate CP01 / PCPIF_IX paths without www150; not multi-subgroup. See Canada note below.
- **Canada CPI food (national subgroups):** skipped — did not hit www150.statcan.gc.ca. OECD DF_PRICES_ALL for CAN exposes only aggregate CP01 (+ `_TXCP01_NRG`), not richer national food subgroups; IMF DBnomics `M.CA.PCPIF_IX` is likewise a single food index. Africa/Asia OECD packs already carry CP01-style aggregates elsewhere. Not richer than Eurostat/OECD CP01 → not landed.
- **Banxico / INEGI food CPI:** skipped — Season2 owns LatAm CPI holes lane; avoid exclusive-claim overlap.

- **Thailand MOC CPIG mid-tree (meat/eggs/veg/meals-away etc.):** index list downloaded; `dataapi.moc.go.th/cpig-indexes` returned 500 HTML or timeouts for most mid-codes after food NAB + rice/flour (+ all-items) succeeded. Partial panel landed; no fabrication from ADB aggregate.
- **PSA Philippines OpenSTAT CPI folder:** HTTP 403 — skipped.
- **Stats NZ HES food shares:** **landed** via release downloadable CSV/XLSX (`nzl_hes_food_share_panel.csv`); Infoshare/API still avoided.
- **Indonesia BPS / SUSENAS open tables:** BPS.go.id + webapi 403/TLS; BI inflation page is aggregate YoY pager only (no food-subgroup CSV). SUSENAS food×income left to Season2. ADB DF_PRI has no PCPI_CP_011* for INO.
- **Philippines / Vietnam NSO food CPI subgroups:** PSA OpenSTAT 403; data.gov.ph SPA/bot wall; GSO/NSO TLS EOF; BSP prices 403. No national mid-tree landed — used FAOSTAT CP monthly Food Indices instead (aggregate Food, not COICOP subgroups).
- **Korea OECD deep COICOP food indexes:** DF_PRICES_ALL for KOR exposes division CP01 (+ CP11 restaurants) only — CP011/CP011x return NoRecordsFound. **Not richer** than asia_national OECD CP01 monthly → not landed. KOSIS household avoided.
- **Canada HES/SHS food share (non-www150):** open.canada.ca 502 then WAF “Request Rejected” on retry; StatCan www150 avoided; OECD HSL/NA food-share left to Season2. No multi-year CAN HES/SHS panel.
- **More EU food CPI index panels:** skipped (saturated).

- **More EU national food CPI (SK/RO/BG/HU/PL):** skipped this diversify turn — EU food CPI indexes already thick; east_eu aggregates cover SK/RO/BG/HU/PL; no clearly richer open subgroup tree pulled (CZE already landed prior).
- **Korea national food CPI index redo:** skipped — `asia_national_food_cpi_panel.csv` already has KOR via OECD monthly CP01; KOSIS household SSL avoided (Season2 Korea SSL / TWN quintile lane).
- **Housing as Engel core:** not claimed — `housing_cost_share_reference_panel.csv` labeled **reference-not-Engel-core** only (Eurostat CP04 / OECD HC1.1.2).

- **Season2 Aoi #118 `adjacent_hours_to_buy_staples`:** Season2 panel (DEU BMEL + BRA DIEESE hours-to-buy staples). Leave hours-to-buy to Season2 — Aoi does not rebuild.
- **BLS Consumer Expenditure Survey FAH/FAFH shares of total CE:** skipped this turn — `download.bls.gov` / www.bls.gov/cex returned 403; `api.bls.gov` 503. USDA FES already covers USA FAH/FAFH **share of DPI** and share-of-food (1929–2026 in `usda_fes_usa_food_expenditure_panel.csv`). CE would add Engel-style **share of total household expenditure** (distinct from FES) but was unreachable; do not fabricate from FES. FRED CE series also unreachable (HTTP/2 / no API key).
- **Canada SHS food share (retry):** open.canada.ca WAF “Request Rejected” (same class as prior 502); www150 avoided; OECD food-share left to Season2. Still no multi-year CAN HES/SHS panel.

- **CBS NL HES food shares:** **landed** (`cbs_nl_hes_food_share_panel.csv`) via StatLine OData 83676NED + historic 60046ned; 85420NED/83679NED TypedDataSet HTTP 500 — unused. Income-decile columns in 60046ned unused (Season2 food×income). Distinct from `cbs_netherlands_food_cpi_panel.csv`.
- **FAO LatAm/CA/MENA-thin Food CPI:** **landed** (`fao_latam_casia_food_cpi_panel.csv`; 33 ISO3 / 10,444 rows) from local FAO CP bulk; labeled non-exclusive vs Season2 LatAm CPI holes / FAO bulk. Banxico/INEGI still avoided.
- **Eurostat NAMA food % HFCE:** **landed** (`eurostat_nama_food_share_hfce_panel.csv`; 36 ISO3 / 2,084 rows; CP01+CP011 PC_TOT). Distinct from Season2 OECD food-share long and from `eurostat_eating_out_panel.csv`. Stub `engel_global_ref_panel_stub.csv` still has the thin 9-geo NAMA food slice.
- **INSEE Budget de famille / Enquête budget food %:** skipped this turn — data.gouv / INSEE BdF open tables 404/500/tiny; no multi-year national food-share CSV landed. FRA CPI indexes already in `insee_france_food_cpi_panel.csv`.
- **Israel CBS household expenditure food share:** skipped — CBS pages returned tiny (~2KB) shells; no open multi-year food-share table landed.
- **Destatis EVS food share:** skipped — Destatis/GENESIS guest wall avoided (same class as Destatis CPI 401 skip).
- **USA BLS CE / CAN SHS rebuild:** skipped — Season2 `adjacent_food_share_by_income` now holds them; Aoi does not rebuild. download.bls.gov / open.canada SHS still avoided.

- **SSB Norway HES food shares:** **landed** (`ssb_nor_hes_food_share_panel.csv`; table 10235 shares 1999–2012). Distinct from `ssb_norway_food_cpi_panel.csv`.
- **Statistics Finland HES food shares:** **landed** (`statfin_fin_hes_food_share_panel.csv`; ktutk 14q8 2012/2016/2022). Income-quintile 14pg unused (Season2 food×income).
- **SCB Sweden HBS food share %:** skipped this turn — HE0201 open tables are SEK expenditure levels (2021 cross-section / 2006–2009) without published share measure; HE0203 is volume *indicator* (not expenditure share). SWE CPI indexes already landed; Season2 may hold SWE in food×income.
- **FAO Pacific/Europe-thin/Caribbean Food CPI:** **landed** (`fao_thin_pacific_ee_caribbean_food_cpi_panel.csv`; 37 ISO3 / 11,754). Other leftover Africa/MENA/Asia Food Indices deferred.
- **WDI food production index:** **landed** (`wdi_food_production_index_panel.csv`; AG.PRD.FOOD.XD; 11,516 / 197 ISO3; 1961–2024).

### Skips this turn (2026-10-24 Asia/Tokyo late)
- **Statistics Austria Konsumerhebung HBS national multi-year food share:** data.gv.at / statistik.at OGD search and theme URLs 404 or empty from box; no open multi-year COICOP 01 share CSV/XLS landed. Documented under `raw/hes_scout/statistik_austria/SKIP.txt`. AUT food **CPI indexes** already in `statistik_austria_food_cpi_panel`.
- **No more FAO Food CPI geo packs** — coverage already thick (~163 ISO3); inventory gap check confirmed.
- **DNK/NOR absolute retail (new-mirror scout):** dataforsyningen / lbst / matpriser→mattilbud / landbruksdirektoratet / data.norge — no usable NSO continuous absolute staple LCU panel. Documented `raw/hi_staple_scout_dnk_nor/SKIP.txt`. CAN www150 still avoided. `hi_staple_levels_alt` remains AUS+CHE only (CAN/DNK/NOR **still miss**).
- **FAOSTAT PP PPI (5539) re-extract:** skipped — already inside `faostat_producer_prices_staples.csv` (~11k PPI rows). Landed QI volume indexes instead.
- **IGC GOI / AMIS statistics:** IGC GOI URLs 404; AMIS SSL EOF — not landed this turn.
- Avoid-list sources untouched (StatCan www150, KOSIS, MOSPI, Stats SA, Destatis GENESIS, Eurostat absolute, Banxico/INEGI, BPS/PSA, BLS CE, open.canada, more EU food CPI indexes, more European HES food-share, food×income rebuild).

### Landed this turn (2026-10-24 Asia/Tokyo late)
- `faostat_food_production_index_qi_panel.csv` — 53,421 rows / 184 ISO3 / 1961–2024
- `japan_retail_price_extra_staples_panel.csv` — 756 rows / 3 items / 2005–2025

### Landed this turn (2026-10-25 Asia/Tokyo)
- `japan_retail_price_oil_sugar_coffee_panel.csv` — 696 rows / 3 items (1601×216, 1632×252, 1921×228) / 2005–2025
- `wdi_cereal_yield_panel.csv` — 10,632 rows / 184 ISO3 / 1961–2024
- `usda_nass_farm_price_index_panel.csv` — 376 rows (2 series × 188 months) / 2011-01…2026-08

### Skips this turn (2026-10-25 Asia/Tokyo)
- **Japan RPS coffee 2014:** e-Stat part 404; **2022:** no beverage/coffee part in sequential statInfId offsets from part01.
- **Japan RPS 食用油 1601 for 2007–2009:** absent from oil_sugar part (codes start at 1611); sugar 1632 present those years.
- **FAOSTAT PP PPI re-extract:** skipped again — already inside `faostat_producer_prices_staples` (~11k PPI rows).
- **OECD agri-food CPI / national food deflator multi-country:** not pulled — would thicken already-dense CPI index lane; USDA NASS + WDI yield filled the open-index gap instead.
- Avoid-list untouched; Season2 lanes (food×income, urban-rural, eating-out, hours-to-buy, absolute staples except Aoi hi_staple AUS+CHE, OECD food-share long, Japan quintile, LatAm CPI holes, FAO bulk, ILO, ICP) left alone.
- DNK/NOR/CAN absolute still miss (no new mirrors).


## 2026-10-25 collect (miso/shoyu + WDI food imports + gaps QC)
- **Landed:** `wdi_food_imports_pct_merchandise_panel.csv` (8116 / 199 ISO3; 1962–2025; TM.VAL.FOOD.ZS.UN).
- **Landed:** `japan_retail_price_miso_shoyu_panel.csv` (504; 1621×252 + 1631×252; 2005–2025; reused `raw/japan_rps_oil_sugar/`; parser validated vs oil panel 2005-01).
- **QC artifact:** `engel_companion_gaps_2026-10-25.md` (open/blocked/Season2-owned snapshot).
- **Skipped:** FAOSTAT TI (HTTP 521); USDA ERS Cost of Food at Home product page 404; no redo of oil/sugar/coffee, WDI cereal yield, USDA NASS.
- Avoid-list untouched; Season2 lanes left alone.


## 2026-10-25 collect (TI bulk + 総世帯 skip + status)
- **Landed:** `faostat_food_trade_indices_panel.csv` (197280 / 184 ISO3; 1961–2024; Imp/Exp Value indexes; food aggregates; bulk zip).
- **SKIP Japan 総世帯 Engel:** longtime = 品目年次 only; no 用途 continuous; yearbook stitch not forced (`raw/engel_food/sousetai/SKIP.txt`).
- **SKIP optional RPS new parts:** not easy (multi-year e-Stat downloads); existing bulks exhausted for easy items.
- **TI API:** still HTTP 521 on retry; bulk path used.
- **QC:** refreshed `engel_companion_gaps_2026-10-25.md`; wrote `engel_companion_collect_status_2026-10-25.md` (panels=85).
- Avoid-list / Season2 / CAN·DNK·NOR absolute untouched.

## Non-CPI resume addendum (2026-10-25 Asia/Tokyo)
| file | what | rows | span | ISO3 |
|------|------|-----:|------|-----:|
| `fao_fbs_kcal_supply_panel.csv` | FBS el664 kcal levels 2901/2905/2907/2903/2941 | 11960 | 2010–2023 | 176 |
| `fao_fs_cereal_root_tuber_energy_share_panel.csv` | FS 21012 cereal+roots+tubers energy % (3y→end-year) | 3732 | 2002–2023 | 185 |
| `fao_fbsh_kcal_supply_panel.csv` | FBSH el664 kcal levels 2901/2905/2907 | 24702 | 1961–2013 | 172 |
| `fao_fs_energy_protein_supply_panel.csv` | FS 22000 DES kcal + 21013/21014 protein | 11224 | 2002–2025 | 185 |

Panel count after addendum: **89**. CPI/HES net-new still paused.

## Addendum — supply companions (2026-10-25 Asia/Tokyo)
| file | what | rows | span | ISO3 |
|------|------|-----:|------|-----:|
| `fao_fs_avg_fat_supply_panel.csv` | FS 21061 avg fat supply g/cap/day (3y→end-year) | 3732 | 2002–2023 | 185 |
| `fao_fbs_animal_kcal_share_panel.csv` | 100×kcal(2941)/kcal(2901) derived share | 2392 | 2010–2023 | 176 |
| `fao_fbs_cereal_food_supply_kg_panel.csv` | FBS el645 cereals excl beer kg/cap/yr | 2392 | 2010–2023 | 176 |

Panel count after this addendum: **92**.
