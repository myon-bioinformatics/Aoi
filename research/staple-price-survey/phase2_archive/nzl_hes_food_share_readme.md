# Stats NZ HES — New Zealand household food expenditure shares

Built: 2026-10-24 (Asia/Tokyo). Companion Engel/staple collect; **household expenditure shares / NZD levels**, not CPI.

## Deliverable

- Panel: `nzl_hes_food_share_panel.csv`
- Rows: **26**
- Span: survey years ended June **2016, 2019, 2023** (national all-households)
- Measures:
  - average weekly NZD Food (NZHEC 01) and subgroups 01.1–01.5
  - average weekly total **net** expenditure
  - food share % of net expenditure (computed Food/Net)
  - published headline food share % from release text (2019, 2023)
- Distinct from Stats NZ CPI (not landed here). Downloadable release CSV/XLSX — **not** Infoshare/API (avoid list).

## Provenance

| field | value |
|-------|-------|
| source | Stats NZ Household Expenditure Statistics |
| releases | Year ended June 2016 (via 2019 Table 1), 2019, 2023 |
| files | `household-expenditure-statistics-year-ended-june-2023.zip` → `exp-t1to4-datafile_2023.csv`; `household-expenditure-statistics-year-ended-june-2019.xlsx` |
| pages | https://www.stats.govt.nz/information-releases/household-expenditure-statistics-year-ended-june-2023 ; https://www.stats.govt.nz/information-releases/household-expenditure-statistics-year-ended-june-2019 |
| raw | `raw/asia_food_subgroups/nzl_hes/` |
| retrieval_date | 2026-10-24 |

## Notes / gaps

1. No FX. Values include GST; group expenditure is gross; share uses Total net expenditure (net of sales/trade-ins/refunds).
2. Published headline shares (16.8% in 2019; 18.7% in 2023) differ slightly from computed Food/Net (17.32% / 18.75%) — both retained with separate `measure` codes.
3. Subgroup labels follow release Table 1 (Grocery food as 01.3, etc.); NZHEC codes workbook descriptors diverge at some mid-tree nodes — publication labels preferred.
4. Table 4 demographics (household size/composition/tenure) not included; no income-quintile food×income (Season2 lane).
5. Pre-2016 HES open cubes not landed (2013 xlsx path 404).
