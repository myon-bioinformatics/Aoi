# ABS HES — Australia household food expenditure shares

Built: 2026-10-24 (Asia/Tokyo). Companion Engel/staple collect; **household expenditure shares**, not CPI.

## Deliverable

- Panel: `abs_hes_food_share_panel.csv`
- Rows: **42** (21 national long + 21 income-quintile 2015–16)
- Span: survey periods **1984 – 2015-16** (national); quintile cross-section **2015-16**
- Measures: average weekly AUD food & non-alcoholic beverages; average weekly total goods & services; food share % of total goods & services
- Distinct from `abs_aus_cpi_food_panel.csv` (CPI price indexes)

## Provenance

| field | value |
|-------|-------|
| source | ABS Household Expenditure Survey, Australia: Summary of Results, 2015–16 |
| catalogue | 6530.0 |
| tables | 65300DO001 Table 1.1; 65300DO003 Table 3.1 |
| page | https://www.abs.gov.au/statistics/economy/finance/household-expenditure-survey-australia-summary-results/2015-16 |
| raw | `raw/abs_hes/` |
| retrieval_date | 2026-10-24 |

## Notes / gaps

1. Latest published HES summary cubes in this release are **2015–16** (released 2017-09-29); no newer open HES summary cube landed here.
2. Stats NZ HES not attempted this turn (known API 502 / avoid list).
3. No FX. ABS random perturbation applies to some 2015–16 cells.
4. Quintile breakdown is AUS HES only — not Season2 Japan quintile Engel lane.
