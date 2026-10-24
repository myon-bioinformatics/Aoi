# Staple price survey — readme

## Retrieval
- Date: **2026-10-24 Asia/Tokyo**
- Output: `staple_survey_vertical.csv` (UTF-8), `staple_survey_missing.md`

## Country universe
- **User-supplied** `/workspace/staple-price-survey/bigmac_vertical.csv` (2056 Big Mac rows; note on file: retrieved 2026-10-24 from The Economist big-mac-data).
- ISO3 list: `countries_iso3.txt` (56 codes including **EUZ**).
- Interim `bigmac_vertical_from_economist.csv` was **not** used for the final country universe or Big Mac rows.

## Column conventions
- `country,date,year,variable,value,unit,source,note[,estimated_value]`
- `date`: monthly → `YYYY-MM-01`; annual tables → `YYYY-01-01` (join key is `year`).
- **No FX conversion. No unit homogenization.** Currencies/pack sizes left as published.
- Estimates/conversions would go in `estimated_value` only; this build leaves that column empty.

## A. Staple prices
Sources used:
1. **FAO GIEWS/FPMA domestic** via `tezamo/FPMA` raw `domestic_commodity.csv` (local `price_local`).
2. **WFP VAM** HDX yearly global files 2022–2026 + legacy `wfpvam_foodprices.csv` (≤2021).
3. **USA BLS** Average Price Data (rice, flour, white/whole-wheat bread, potatoes), 2000–2025 monthly.
4. **Japan e-Stat** 小売物価統計調査 rice (うるち米) monthly series reused from `/workspace/aoi-phase2/rice_monthly_*.csv`.

Thinning rule for FPMA/WFP: longest market series per (country, commodity, unit, price_type).

## B. Engel / food share
- **USDA ERS** “Percent of consumer expenditures spent on food, alcoholic beverages, and tobacco that were consumed at home, by selected countries, 2021-2025” (XLSX).
  - Download: `https://ers.usda.gov/media/29442/percent-of-consumer-expenditures-spent-on-food-alcoholic-beverages-and-tobacco-that-were-consumed-at-home-by-selected-countries-2021-2025.xlsx?v=25801`
  - **Japan included:** YES (e.g. 2025 food share ≈ 16.32%).
  - **Food includes nonalcoholic beverages:** YES (footnote 3).
  - **At-home:** YES (table title).
  - Shares computed from **domestic currency** units (footnote 2); USD amount columns ignored.
  - Underlying vendor: Euromonitor (2021–2024 sheets) / Oxford Economics (2025 sheet).
  - **Terms:** ERS publishes the spreadsheet as a U.S. government data product (generally public-domain U.S. government work under 17 U.S.C. §105 / open-data practice). Page itself does not paste a separate commercial redistributor license; underlying Euromonitor/Oxford Economics subscription terms are restrictive for *their* raw databases — we record USDA’s published share tables with attribution to USDA ERS + vendor footnote as shown in-file. Use for analysis with standard USDA citation.
- **Japan national series:** `engel_share_food_national_hh_survey` from e-Stat 家計調査 (aoi-phase2 `engel_annual_extended.csv`), 2000–2023; definition differs from USDA — keep separate.
  - **2024–2025 added 2026-10-24** from the Statistics Bureau 家計調査報告（家計収支編）年平均結果の概要 (PDF): 2024 = 28.3 (`https://www.stat.go.jp/data/kakei/sokuhou/tsuki/pdf/fies_gaikyo2024.pdf`), 2025 = 28.6 (`https://www.stat.go.jp/data/kakei/sokuhou/tsuki/pdf/fies_gaikyo2025.pdf`). Values as published to one decimal.
  - **Seam:** the 2000–2023 rows come from a rehosted e-Stat long-term table, the 2024–2025 rows from a different file (the published summaries). Check recorded in each row's `note`: the summaries state +0.5 pt for 2024 and +0.3 pt for 2025 versus the previous year, which matches 27.8 → 28.3 → 28.6 (2023 = 27.8 in the existing series). The household scope (二人以上の世帯) rests on that match and on the summary's headline figures; the e-Stat table itself was not re-read for 2024–2025.

## C. Household consumption + population
- World Bank **NE.CON.PRVT.CN** — Households and NPISHs final consumption expenditure (current LCU), CC BY 4.0.
- World Bank **SP.POP.TOTL** — total population.
- Bulk CSV via `api.worldbank.org` downloadformat=csv; filtered to universe ISO3; year≥2000.
- EUZ not a WB country code → no rows (see missing.md).

## Row-count summary
| family | rows | countries |
|--------|------|-----------|
| staple_price:* | 61157 | 40 |
| engel* | 556 | 53 |
| household_consumption_total_lcu | 1344 | 54 |
| population_total | 1404 | 54 |
| bigmac_local_price | 2056 | 56 |
| **total** | **66517** | |

## Confirmation
- No foreign-exchange conversion applied.
- No unit/pack homogenization applied.
- No gap-filling / interpolation of missing values.
