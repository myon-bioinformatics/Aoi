# Global reference catalog — Engel × food (scout)

Date: **2026-10-24 Asia/Tokyo**. Scout + easy pulls only. **No estimation. No FX.**  
Does **not** touch GohanTrust judgment files or re-estimate Japan 家計調査 panels.

**Status 2026-10-24 JST:** Companion panels collected in Aoi phase-2 (Japan Engel annual/monthly, global stub, OWID/USDA/CoAHD/SOFI, Japan CPI+rice+food-service, Asia/China/Africa-MENA/EastEU/Eurostat food CPI, eating-out, FAO/IMF indices, producer prices, intl rice, shrinkflation capacity) are inventoried in `engel_companion_inventory_2026-10-24.md` — use that table for file paths/spans. This catalog remains the definition/scout note for global E / Bennett / Eurostat joins; it does not replace the inventory.


Related local track (do not splice definitions):

- Japan annual panel: `/workspace/aoi-phase2/engel_food_panel_annual.csv` (2000–2025; 用途分類)
- Prelock forms: `/workspace/aoi-phase2/engel_food_forms_prelock_2026-10-24.md` (F1 product; F3 Bennett)
- Season2 staples/Engel/Big Mac: `/workspace/aoi-phase2/staple-price-survey/` (reuse; do not wholesale-duplicate)

Raw downloads: `/workspace/aoi-phase2/raw/engel_global_ref/`  
Tidy stub (vertical): `/workspace/aoi-phase2/engel_global_ref_panel_stub.csv`

---

## Claude-facing — ready vs deferred

### Ready now (cite these first when asked)

| Priority | What | Path / variable | Use for |
|---|---|---|---|
| 1 | **USDA/OWID at-home food share** (international Engel proxy) | stub `engel_food_athome_share_pct`; raw `owid_food_share_consumer_expenditure.csv` + `usda_ers_food_share_2021_2025.xlsx` | Cross-country **E**; join on ISO3×year with Big Mac / staples universe |
| 2 | **FAO FS 21012** cereal+roots+tubers **energy** share (3y avg) | stub `fs_dietary_energy_share_cereals_roots_tubers_pct`; raw `faostat_fs_*.csv` | Global **F3 / Bennett-adjacent** (energy, not ¥ share) |
| 3 | **Eurostat COICOP** food / restaurants+hotels / housing % of HFCE | stub `eurostat_*_share_hfce_pct`; raw `eurostat_nama_co3_pc_tot_*.csv` | Europe **F1-like** (E × restaurants/HFCE) and housing **reference** |
| 4 | **FAOSTAT FBS** kcal/cap/day total + cereals excl. beer + starchy roots | stub `fbs_kcal_cap_day_*`; raw zip + subset CSV | Levels for kcal track; cereals/total = arithmetic F3 candidate (**not** precomputed in stub) |
| 5 | **OECD AHD** housing cost / rent burden + housing+energy share of HFCE | stub `oecd_rent_burden_*`, `oecd_housing_energy_share_hfce_pct` | Housing **reference only** |

### Deferred / blocked

| Item | Status |
|---|---|
| OECD SDMX full COICOP Table5 (food+CP11 global OECD) | **404 / dataflow not found** on tried URLs (`DSD_NAMAIN10@DF_TABLE5*`, `SNA_TABLE5_ARCHIVE`). Use Eurostat for EU; OECD HC1.1.2 for housing share. |
| World Bank ICP food share | **Not continuous** (benchmark years 2017/2021 + short PPP bridge). Catalog only — do not treat as annual panel. |
| FAOSTAT FBS **Japan** (2010– bulk) | **Absent** from `FoodBalanceSheets_E_All_Data_(Normalized)` (no “Japan” area). Japan **is** in FS 21012 and OWID staple-energy. Prefer those for JPN kcal-structure refs until FBS Japan reappears / historic FBSH is pulled. |
| Singapore in FAO FS/FBS | **Missing** from FAO areas in this pull (SGP still in USDA/OWID Engel where published). |
| Eating-out share **global continuous** | No single global “外食/CE” series found. Closest: Eurostat **CP11** (restaurants & hotels) for Europe; USDA Engel is **at-home only**. |
| Longer USDA history pre-2017 | Official ERS XLSX still **2021–2025** sheets (same as Season2). OWID compilation extends **2017–2023**. No public ERS multi-decade country panel located without login. |

### Definition cite order (when Claude asks)

1. **COICOP / HFCE** (Eurostat `NAMA_10_CO3_P3`, OECD HC1.1) — national-accounts consumption purpose; **domestic concept** for Eurostat nama_10_co3_p3.
2. **USDA “food at home” share of consumer expenditure** — Euromonitor/Oxford Economics via ERS; **excludes** F&B away from home, alcohol, tobacco (OWID note).
3. **Japan 家計調査 用途分類** — household survey; 食料 ≠ COICOP CP01; 外食 = 一般外食+学校給食 in local panel; **do not splice** onto USDA levels.
4. **外食 vs restaurants**: Japan 外食 (HH survey) ≠ Eurostat **CP11** (restaurants *and hotels*) ≠ USDA (which omits away-from-home).
5. **Bennett**: classical = **dietary energy** from starchy staples falls as income rises. Prefer **FS 21012** / OWID staple-energy over expenditure “穀類/食料” when speaking internationally; Japan F3 uses **expenditure** 穀類/食料 (用途) — different object.
6. **Housing reference**: OECD rent burden (% disposable income) ≠ Eurostat CP04 (% HFCE, includes imputed rent/utilities) ≠ Japan 住居費.

---

## Sources (≥6)

### 1. USDA ERS — food / alcohol / tobacco shares (at home)

| Field | Detail |
|---|---|
| Measures | % of consumer expenditures on **food at home** (and alcohol, tobacco sheets); per-capita USD amounts also in file (ignore for FX-free share work) |
| Geography / years | ~100+ countries; official workbook **2021–2025** (annual sheets). OWID mirror **2017–2023** |
| Download | ERS XLSX: `https://ers.usda.gov/media/29442/percent-of-consumer-expenditures-spent-on-food-alcoholic-beverages-and-tobacco-that-were-consumed-at-home-by-selected-countries-2021-2025.xlsx` — landing: `https://ers.usda.gov/topics/international-markets-us-trade/international-consumer-and-food-industry-trends/data` |
| License | U.S. government publication; attribute USDA ERS. Underlying Euromonitor / Oxford Economics vendor DBs are proprietary — we keep **ERS published share tables** only |
| Join keys | Country name → ISO3; year |
| Why for F1/F3 | Best **global E** proxy already used in Season2; F1 needs a separate eating-out series (not in USDA) |
| vs 家計調査 | USDA Japan ~15–16% at-home ≠ 用途エンゲル (~22–23%+). Definition break — keep parallel |
| Local copy | `raw/engel_global_ref/usda_ers_food_share_2021_2025.xlsx`; Season2 vertical also has engel* rows |

### 2. Our World in Data — food share of consumer expenditure

| Field | Detail |
|---|---|
| Measures | Same USDA concept, cleaned; ISO3 `Code` |
| Geography / years | 104 entities; **2017–2023** continuous where published (2023 gaps may show 2022 — see OWID note) |
| Download | `https://ourworldindata.org/grapher/share-of-consumer-expenditure-spent-on-food.csv?v=1&csvType=full&useColumnShortNames=false` |
| License | OWID CC BY; underlying USDA terms apply |
| Join keys | `Code` (ISO3), `Year` |
| Why | Easiest machine-readable multi-year Engel for product/ratio scouting |
| Local copy | `owid_food_share_consumer_expenditure.csv` |

### 3. FAOSTAT Food Balance Sheets (FBS, 2010–)

| Field | Detail |
|---|---|
| Measures | Food supply **kcal/capita/day** (element **664**): Item **2901** Grand Total; **2905** Cereals – Excluding Beer; **2907** Starchy Roots |
| Geography / years | ~200+ areas; **2010–2023** in current bulk. **Japan not present** in this bulk file |
| Download | Bulk zip: `https://bulks-faostat.fao.org/production/FoodBalanceSheets_E_All_Data_(Normalized).zip` — catalog `https://bulks-faostat.fao.org/production/datasets_E.json` — UI `https://www.fao.org/faostat/en/#data/FBS` |
| License | FAO terms of use (attribution; generally open for research) — `https://www.fao.org/contact-us/terms/db-terms-of-use/en/` |
| Join keys | Area → ISO3 (see `faostat_area_iso3_map.csv`); Year |
| Why | Continuous **kcal levels**; cereals/total = global F3-style **energy** ratio candidate |
| vs 家計調査 | Supply/availability ≠ household expenditure shares |
| Local copy | full zip + `faostat_fbs_kcal_cereals_subset.csv` |
| Historic | `FoodBalanceSheetsHistoric_E_All_Data_(Normalized).zip` (FBSH, old methodology, –2013) **not pulled** this round |

### 4. FAOSTAT Suite of Food Security Indicators (FS) — item 21012

| Field | Detail |
|---|---|
| Measures | **Share of dietary energy supply from cereals, roots and tubers (%)**, 3-year average |
| Geography / years | ~230 areas incl. **Japan**; year labels `2000-2002` … `2021-2023` (stub uses **end year**) |
| Download | `https://bulks-faostat.fao.org/production/Food_Security_Data_E_All_Data_(Normalized).zip` |
| License | FAO terms (as above) |
| Join keys | Area → ISO3; end-year of 3y window |
| Why | Canonical **Bennett-adjacent** international series; best F3 global reference |
| Local copy | `faostat_fs_cereal_root_tuber_energy_share.csv` |

### 5. Our World in Data — calories from cereals, roots and tubers

| Field | Detail |
|---|---|
| Measures | Staple energy share (%) + GDP per capita (ignore GDP if FX/PPP mixing undesired) |
| Geography / years | Broad; staple values roughly **2001–2021** in pull |
| Download | `https://ourworldindata.org/grapher/share-of-energy-from-cereals-roots-and-tubers-vs-gdp-per-capita.csv?v=1&csvType=full&useColumnShortNames=false` |
| License | OWID CC BY; FAO underlying |
| Join keys | ISO3 `Code`, Year |
| Why | Convenient ISO3 panel parallel to FS 21012 |
| Local copy | `owid_staple_energy_share_vs_gdp.csv` |

### 6. Eurostat — HFCE by COICOP 1999 (`nama_10_co3_p3`)

| Field | Detail |
|---|---|
| Measures | **PC_TOT**: CP01 Food & non-alcoholic beverages; **CP04** Housing, water, electricity, gas & other fuels; **CP11** Restaurants & hotels — % of household final consumption expenditure. Also pulled CP_MEUR levels |
| Geography / years | European countries (+TR, CH, etc.); **2000–2025** where reported |
| Download | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/NAMA_10_CO3_P3/A.PC_TOT.CP01+CP04+CP11+TOTAL.?format=SDMX-CSV&startPeriod=2000` — meta `https://ec.europa.eu/eurostat/cache/metadata/en/nama_10_co3_p3_esms.htm` |
| License | Eurostat reuse policy (attribution; generally free) |
| Join keys | `geo` ISO2 → ISO3; `TIME_PERIOD` |
| Why | Only easy **continuous restaurants** share for F1-style products; housing CP04 as reference |
| vs 家計調査 | COICOP CP01 ≠ 用途食料; CP11 includes **hotels**; domestic HFCE concept |
| Local copy | `eurostat_nama_co3_pc_tot_food_housing_rest.csv`, `eurostat_nama_co3_cp_meur_*.csv` |
| Note | Newer COICOP 2018 table `nama_10_cp18` exists; this scout used long COICOP1999 series for continuity |

### 7. OECD Affordable Housing Database — HC1.1 / HC1.2 (housing **reference**)

| Field | Detail |
|---|---|
| Measures | HC1.1.2: housing+water+fuels **% of HFCE** (1995–~2022/24). HC1.2.A1: median **rent burden** % disposable income (2010–2024, tenure split) |
| Geography / years | OECD (+ some partners); continuous but gappy by country |
| Download | `https://webfs.oecd.org/Els-com/Affordable_Housing_Database/HC1-1-Housing-related-expenditure-of-households.xlsx` ; `.../HC1-2-Housing-costs-over-income.xlsx` — hub `https://www.oecd.org/en/data/datasets/oecd-affordable-housing-database.html` |
| License | OECD data terms (attribution; non-commercial restrictions may apply — check OECD ToS for redistribution) |
| Join keys | Country name → ISO3; year |
| Why | Housing reference if Engel×housing returns; **not** primary food form |
| Local copy | both XLSX; stub vars `oecd_housing_energy_share_hfce_pct`, `oecd_rent_burden_pct_disp_income` |

### 8. World Bank — household consumption & population (already in Season2)

| Field | Detail |
|---|---|
| Measures | `NE.CON.PRVT.CN` HH+NPISH final consumption (LCU); `SP.POP.TOTL` |
| Geography / years | Broad; 2000+ in staple survey |
| Download | World Bank API CSV (see `staple-price-survey/staple_survey_readme.md`) |
| License | CC BY 4.0 |
| Join keys | ISO3, year |
| Why | Denominator / scale reference; **not** food share |
| Local copy | Reuse Season2 vertical — not re-downloaded here |

### 9. World Bank ICP (catalog only — not continuous)

| Field | Detail |
|---|---|
| Measures | Food (basic heading) / HH consumption structure in PPP benchmark years |
| Geography / years | ICP 2017 / 2021 cycles — **not** a dense annual Engel panel |
| Download | DataBank ICP 2021: `https://databank.worldbank.org/source/icp-2021` |
| Why deferred | Good for level checks in benchmark years; poor for continuous F1/F3 products |

---

## Classification cheat-sheet

| Concept | International object | Japan local panel object |
|---|---|---|
| Engel E | USDA/OWID **food at home** / CE; or Eurostat **CP01**/HFCE | 用途 **食料/消費支出** published E |
| Eating out | Eurostat **CP11** restaurants & hotels; no clean global HH “外食” | 用途 **外食** (=一般外食+学校給食) |
| Cereals / Bennett | FS **21012** energy %; FBS **2905/2901** kcal | 用途 **穀類/食料** expenditure share |
| Housing (ref) | Eurostat CP04; OECD HC1.1 / rent burden | 住居費 (out of primary forms) |

---

## Stub panel summary

File: `/workspace/aoi-phase2/engel_global_ref_panel_stub.csv`  
Columns: `country,year,variable,value,unit,source,note`  
Universe filter: Season2 Big Mac ISO3 list (excl. EUZ), **55** countries with ≥1 series.

| variable | rows | countries | years |
|---|---:|---:|---|
| engel_food_athome_share_pct | 371 | 53 | 2017–2023 |
| fs_dietary_energy_share_cereals_roots_tubers_pct | 1136 | 54 | 2002–2023 |
| staple_energy_share_cereals_roots_tubers_pct | 1096 | 54 | 2001–2021 |
| fbs_kcal_cap_day_total / cereals / starchy_roots | 724 each | 53 | 2010–2023 |
| eurostat_food_nabev_share_hfce_pct | 201 | 9* | 2000–2023 |
| eurostat_restaurants_hotels_share_hfce_pct | 201 | 9* | 2000–2023 |
| eurostat_housing_utilities_share_hfce_pct | 201 | 9* | 2000–2023 |
| oecd_housing_energy_share_hfce_pct | 552 | 21 | 1995–2024 |
| oecd_rent_burden_pct_disp_income | 224 | 19 | 2010–2024 |

*Eurostat∩Big Mac universe only: CHE, CZE, DNK, HUN, NOR, POL, ROU, SWE, TUR (other EU geos available in raw CSV if universe expands).

**F1-style global product** (E × restaurants/HFCE): feasible for those 9 with USDA/OWID E ∩ Eurostat CP11 (short overlap 2017–2023).  
**F3-style global**: FS 21012 vs USDA E — wide country coverage; remember energy% vs at-home food% mismatch.

---

## Suggested next pulls (when Claude asks)

1. FAO **FBSH** historic zip if pre-2010 kcal needed; re-check FBS for Japan reinstatement.
2. Eurostat / OECD **CP11** for a larger country set (drop Big Mac filter) if F1 Europe is the track.
3. National HH surveys with COICOP eating-out (e.g. CE / HBS micro) — not bulk-easy.
4. ICP 2021 food structure as **benchmark cross-check** only.

---

## Addendum — Country Ma'am (カントリーマアム) snack reference (2026-10-24)

Japan-only cookie brand (Fujiya). User asked for 「カントリーマアム指数／指標」 as volunteer-compiled reference.

| Field | Detail |
|---|---|
| What exists | No formal statistical series named カントリーマアム指数 found. Volunteer **shrinkflation grams/pack-count** panel: **いつの間にか容量が減っている商品wiki** (index = 枚数・g, not official retail) |
| URL | https://shrinkflation.info/index.php?カントリーマアム |
| Local CSV | `country_maam_shrinkflation_series.csv` (+ `raw/country_maam/README.md`) |
| Coverage | Event years 1992–2024-04 (12 points); not monthly |
| Derived | yen_per_cookie, yen_per_g from listed 税別価格 ÷ pack/g |
| Use | Japan local “snack numeraire” / shrinkflation companion to Big Mac; **not** global; pack-count breaks are the signal |
| Caveat | Wiki keeps 323円税別 through 2024-04; open-price retail and 2023 announced hikes may diverge — treat as shrink chronology first |

## Addendum — Shrinkflation capacity panel (batch, 2026-10-24)

Broader Japan **capacity/g** dump from the same wiki (not price index), beyond Country Ma'am alone.

| Field | Detail |
|---|---|
| Source | https://shrinkflation.info/ （いつの間にか容量が減っている商品wiki） |
| Local panel | `shrinkflation_capacity_panel.csv` |
| Product index | `shrinkflation_capacity_products.csv` |
| Readme | `shrinkflation_capacity_readme.md` |
| Products / rows | **508** products, **2485** rows |
| Year span | 1973–2026 (event dates) |
| Units | g / count / ml — capacity-first; price nullable |
| Includes | カントリーマアム + snacks, sweets, drinks, instant, dairy, household with ≥3 capacity points |
| Skips | Edit-only stubs (e.g. ホームパイ, チキンラーメン); capacity-blank price-only pages (e.g. カップヌードル) |
| Use | Japan shrinkflation / snack-numeraire companions; **not** global; **not** official statistics |
| Caveat | Wiki is volunteer/AI-assisted; sparse event dates; verify before inference |

Country Ma'am–only series remains at `country_maam_shrinkflation_series.csv` (see prior addendum).

## Addendum — Aoi origin batch (2026-10-24, post–Season2 consult)

Aggressive companion pulls that **avoid Season2 mid-fetch A–F** (ICP PLI, FAO CPI food/cereals panels, Japan quintile Engel, FBS Japan+pre-2010, OECD COICOP food-share long series, PIP). Discussion mode: collect continuous free series; stub/scout the rest.

### Added files

| Deliverable | Path | Coverage |
|---|---|---|
| **International rice** (Pink Sheet) | `rice_international_price_panel.csv` + `rice_international_price_readme.md` | Thai 5% 1960-01–2026-09 (801m); Thai 25%/A.1; Vietnam 5% |
| **Eurostat eating-out (CP11)** | `eurostat_eating_out_panel.csv` + `eurostat_eating_out_readme.md` | 36 ISO3 (+aggregates), 952 rows, 2000–2025; **fuller than stub’s 9 Big Mac∩EU rows** |
| **Numeraire catalog** | `numeraire_candidate_catalog_2026-10-24.md` | Scout table + downloads |
| Pink Sheet coffee/sugar | `raw/numeraire/pink_sheet_rice_coffee_sugar_monthly.csv` | Arabica/Robusta/Sugar × month from 1960 |
| BLS USA retail average prices | `raw/numeraire/bls_average_price_panel.csv` | Bread/milk/coffee/sugar/rice USD, ~1980–2026-09 |
| Eurostat HICP subclasses | `raw/numeraire/eurostat_hicp_bread_milk_coffee_sugar_monthly.csv` | Bread/milk/sugar/coffee I15, ~36 geos, 1996–2025 |
| Japan CPI 品目 | `raw/numeraire/japan_cpi_numeraire_items_monthly.csv` (+ wide raw) | 食パン/牛乳/砂糖/コーヒー豆・ｲﾝｽﾀﾝﾄ/米・パン, 1970–2026-09 |

### Stub note

`engel_global_ref_panel_stub.csv` Eurostat CP01/CP04/CP11 rows remain Big Mac∩EU (~9 geos) for join discipline. Prefer **`eurostat_eating_out_panel.csv`** when Europe F1/eating-out coverage is the object.

### Scout-only (not tidy-downloaded)

FAO FPMA international API (UI-only), AMIS CBS (not Thai-5% price panel), IRRI WRS (portal unstable), IMF ExternalData (404 this round). Details in numeraire catalog.

### Still Season2’s lane (do not duplicate)

ICP 2017/2021 food PLI/expenditure; FAO food/cereals CPI country panels; Japan 五分位エンゲル; FBS Japan + pre-2010; OECD COICOP food-share long series; PIP / Orshansky country lines.

---

## Aoi origin CoAHD/PP (2026-10-24 Asia/Tokyo)

Pulled on Aoi side as Engel companions (not Season2 A–F). No FX; vertical tidy.

### FAO Cost of a Healthy Diet / Food Prices for Nutrition (CoAHD)

| Field | Detail |
|---|---|
| What | Cost of a healthy diet (LCU + PPP Int$), prevalence/number unable to afford, six food-group costs |
| Source | FAOSTAT domain **CAHD** (July 2026 SOFI release); partnership with World Bank Food Prices for Nutrition |
| Bulk | `https://bulks-faostat.fao.org/production/Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized).zip` |
| Landing | https://www.fao.org/faostat/en/#data/CAHD |
| Local panel | `coa_healthy_diet_panel.csv` + `coa_healthy_diet_readme.md` |
| Raw | `raw/coa_fpn/` |
| Coverage | **9,442** rows; **161** ISO3 (+ aggregates blank iso3); years **2017–2025** |
| Big Mac overlap | 52/56 (missing EUZ, SGP, UKR, VEN in this pull’s mapped set) |
| Notes | World Bank Databank `FPN_CSV.zip` BlobNotFound at retrieval — FAOSTAT bulk used. LCU and PPP kept as separate published indicators (we do not convert). |

### FAOSTAT Producer Prices — rice / wheat / maize

| Field | Detail |
|---|---|
| What | Annual farm-gate prices for Item Codes **15** Wheat, **27** Rice, **56** Maize (corn) |
| Source | FAOSTAT domain **PP** |
| Bulk | `https://bulks-faostat.fao.org/production/Prices_E_All_Data_(Normalized).zip` (full ~12 MB zip / ~214 MB CSV in `raw/faostat_pp/`) |
| Landing | https://www.fao.org/faostat/en/#data/PP |
| Local panel | `faostat_producer_prices_staples.csv` + `faostat_producer_prices_staples_readme.md` |
| Elements | 5530 LCU/t; 5531 SLC/t; 5532 USD/t (**FAO-published**, not converted here); 5539 PPI 2014–2016=100 |
| Coverage | **36,627** annual rows; **156** ISO3; years **1991–2025** |
| Big Mac overlap | 50/56 (missing ARE, BHR, EUZ, HKG, SGP, TWN) |
| Use | Retail-gap / producer-price bench for staples; join on ISO3×year with CoAHD / Engel stubs |

Season2 continues A–F (ICP PLI, FAO consumer CPI food/cereals, Japan quintile Engel, FBS Japan+pre-2010, OECD food share, PIP) and high-income/LatAm national CPI lanes — do not duplicate those here.

---

## Aoi origin batch 2 (2026-10-24 Asia/Tokyo)

Continuous Engel × staple companions pulled on Aoi side after CoAHD/PP. **No FX. No fabricated fills.** Season2 A–F / high-income+LatAm CPI lanes still skipped.

| Priority | What | Path | Coverage |
|---|---|---|---|
| 1 | **FAO Food Price Index + Cereal (global)** | `fao_food_price_index_panel.csv` + `fao_food_price_index_readme.md` · raw `raw/fao_fpi/` | WORLD monthly **1990-01–2026-09**; FFPI + meat/dairy/cereal/oils/sugar; 2014–2016=100; **≠** Season2 country FAO CPI |
| 2 | **USDA ERS FES USA** FAH/FAFH %DPI + monthly sales | `usda_fes_usa_food_expenditure_panel.csv` + `usda_fes_usa_food_expenditure_readme.md` · raw `raw/usda_fes/` | Current shares **1997–2025**; monthly sales ~**1997–2026-08**; archived %DPI **1929–2014** (`usa_fes_archive_*`, methodology break). Names distinct from Season2 international at-home share |
| 3 | **OWID** staple energy + food share tidy | `owid_staple_energy_share_panel.csv`, `owid_food_expenditure_share_panel.csv` + `owid_engel_companion_readme.md` | Staple non-null **2001–2021** (191 ISO3); food share **2017–2023** (104 ISO3). Stub **not** poorly duplicated — no newer staple years exist in source |
| 4 | **Japan 小売物価統計 うるち米** (yen/5kg) | `japan_retail_price_rice_panel.csv` + `japan_retail_price_rice_readme.md` · raw `raw/japan_rps_rice/` | Item **1002** city-mean **1999–2025**; 1001 + Tokyo **2015–2025**. Level companion to CPI rice index |
| 5 | **IMF PCPS Food index** (via FRED) | `imf_pcps_food_index_panel.csv` + `imf_pcps_food_index_readme.md` · raw `raw/imf_pcps/PFOODINDEXM_fred.csv` | WORLD monthly **1992-01–2026-09**; index 2016=100; numeraire / global food commodity |

### Catalog corrections from batch 2
- “Longer USDA history pre-2017” deferred note (international country panel) still stands for **cross-country** ERS shares; **USA FES** archive now local through **1929**.
- IMF ExternalData direct download remains flaky from this box; FRED mirror is the working path.

### Scout-only leftovers (batch 2)
- IMF PCPS cereal/beverage sub-indices (SDMX TLS failures)
- IRRI WRS / AMIS rice (portals unstable; Pink Sheet rice already landed earlier)
- e-Stat API (`appId`) — file-download used instead; vault connector not available in this executor

## Aoi origin batch Asia/FS (2026-10-24 Asia/Tokyo)

Companion pulls on Aoi side after Season2 consult. **No FX. No fabricated fills.** Skips Season2 lanes (ICP; FAO country CPI food/cereals; Japan quintile Engel; FBS Japan+pre-2010; OECD food-share; PIP; high-income Big Mac national CPI; LatAm national food CPI; ILO bulk).

### Asia national food CPI

| Field | Detail |
|---|---|
| Panel | `asia_national_food_cpi_panel.csv` + `asia_national_food_cpi_readme.md` |
| Raw | `raw/asia_food_cpi/` |
| Rows | **1754** |
| Countries | **IDN, THA, PHL, VNM, IND, KOR, MYS** (all 7 targets represented) |
| Series | ADB KIDB `PCPI_CP_01_IX` **annual** food CPI (all 7); OECD monthly CP01 index+YoY (**KOR** long 1990–2026-09, **IND** shorter); DOSM Malaysia monthly division 01 (**1980-01–2026-09**) |
| Cereals-only | OECD CP011 keys → NoResultsFound; not in this panel |
| Notes | ADB economy codes INO/PHI/VIE/MAL → ISO3 IDN/PHL/VNM/MYS. Indices **not** rebased to common base. Not FAO country CPI. |

### Japan food-service activity index

| Field | Detail |
|---|---|
| Panel | `japan_food_service_activity_panel.csv` (**1932 rows**) + readme |
| Content | METI ITA 2020基準 飲食店・飲食サービス業 7 series, monthly 原/季調 2018-01–2026-08 + quarterly 2018Q1–2026Q2 |
| Status | **DONE** — Excel browser-downloaded after curl 403; linked 1988– file not yet parsed |

### Optional WDI

Skipped this round (Season2 already holds WB `NE.CON.PRVT.CN` + population; no clearly superior long food-share WDI series without duplicating).

---

## Aoi origin batch Africa/MENA

Date: **2026-10-24 Asia/Tokyo**. Companion food CPI for Engel/staple work outside Season2 FAO/high-income lanes and outside the Asia national panel.

| Deliverable | Path | Coverage |
|---|---|---|
| Africa/MENA national food CPI | `africa_mena_national_food_cpi_panel.csv` | EGY/ZAF/NGA/KEN/MAR/TUN/TUR/ISR/SAU; IMF PCPIF_IX (+ OECD CP01 for ZAF & parallels); **4867** rows |
| Eurostat HICP food CP011 | `eurostat_hicp_food_panel.csv` | EU+TR etc., monthly 1996–2025, I15; **14211** rows; ≠ eating-out CP11 shares |
| Readmes | `africa_mena_national_food_cpi_readme.md`, `eurostat_hicp_food_readme.md` | provenance / blockers |
| Raw | `raw/africa_mena_cpi/` | DBnomics IMF JSON, OECD CSV, Eurostat TSV |

**Not duplicated:** Season2 FAO country CPI; Season2 high-income national CPI; Asia `asia_national_food_cpi_panel.csv`.

## Aoi origin batch SOFI/EastEU

Date: **2026-10-24 Asia/Tokyo**. Companion pulls (not Season2 lanes).

| Deliverable | Path | Coverage |
|---|---|---|
| SOFI PoU + FIES prevalence | `sofi_food_insecurity_panel.csv` + `sofi_food_insecurity_readme.md` | ~18.9k rows; **184** country ISO3; PoU/FIES **3y avg** country panels 2002–2025 / 2016–2025; annual PoU/FIES = regions only; censored `<2.5` kept as null+`value_raw` |
| East EU / gap national food CPI | `easteu_national_food_cpi_panel.csv` + `easteu_national_food_cpi_readme.md` | **4382** rows; BGR/CZE/HUN/POL/ROU/RUS/SRB/UKR; UKR+RUS fill HICP holes; HUN back to **1980** |
| Raw | `raw/sofi_fs/`, `raw/easteu_cpi/` | FAOSTAT FS zip; IMF via DBnomics; OECD CP01 |

**Skipped / deferred (Season2 or no value-add):** ICP; FAO country CPI; Japan quintile Engel; FBS Japan+pre-2010; OECD food share; PIP; high-income Big Mac national CPI; LatAm national food CPI; ILO food CPI; HRV national (HICP already long enough).

**Rules:** no FX; no fabricated fills; provenance on every row.

