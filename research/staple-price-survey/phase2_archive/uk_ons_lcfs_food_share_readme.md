# UK ONS LCFS / Family Spending — national food expenditure share

## Panel
- File: `uk_ons_lcfs_food_share_panel.csv`
- Rows: 26
- Span: survey_year_end 2002–2025 (26 period columns)
- Geography: GBR (United Kingdom), national all-households
- Measure: Food & non-alcoholic drinks (COICOP 01) as **percent of total household expenditure**

## Source
- ONS Family Spending workbook 1: Detailed expenditure and trends, FYE 2025 release
- Table 4.2 — Household expenditure as a percentage of total expenditure based on COICOP classification, 2001-02 to 2024-25 at 2024-25 prices
- Dataset: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/datasets/familyspendingworkbook1detailedexpenditureandtrends
- Bulletin: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/latest
- Local raw: `raw/uk_lcfs/workbook1_fye2025.xlsx` (also `workbook1_fye2024.xlsx`, `workbook1_fye2001_2019.xlsx` retained)
- Retrieved: 2026-10-24

## Notes / non-overlap
- National continuous share only. Income-decile/quintile percentage tables (3.2 / 3.2E / 3.2E5) **not** ingested — those sit with Season2 `adjacent_food_share_by_income` / food×income pack.
- Distinct from existing `uk_ons_cpi_rpi_food_index_panel.csv`, `uk_ons_avg_retail_food_panel.csv`, `defra_uk_agri_price_index_panel.csv`.
- COICOP 11 Restaurants & hotels shares present in the same Table 4.2 but **left to Season2** eating-out lane.
- Price basis is constant FYE 2025 prices as published (real expenditure composition). Values transcribed as published (typically whole percent).
- Period labelling follows ONS: financial years FYE 2002–2006 and FYE 2015–2025; calendar years 2006–2014. Two overlapping 2006 sample columns kept as `2006_a` / `2006_b`.
- No FX conversion. No fabrication.

## Defra Family Food
- Defra `UKExp_17Sep26.ods` / `UKHHcons_17Sep26.ods` downloaded to `raw/uk_lcfs/` for reference (household food expenditure £ and quantities). Not required for this national COICOP-share panel once Table 4.2 was available.
