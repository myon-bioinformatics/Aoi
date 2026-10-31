# CBS Netherlands Budgetonderzoek — national food expenditure share

## Panel
- File: `cbs_nl_hes_food_share_panel.csv`
- Rows: 21
- ISO3: NLD (1)
- Span: 1992–2020 (survey years; not continuous every year)

## Sources
1. **83676NED** (2015, 2020): Bestedingen van huishoudens; bestedingscategorieën — `Bestedingsaandeel` for CPI010000 (food & non-alc. beverages) and CPI011000 (food). Point estimates Marges=MW00000.
2. **60046ned** (1992–2010): Historic Budgetonderzoek — category code 102 «11 Voeding». Where CBS publishes only euro levels, share = 100 × food / total (codes 102 / 100), both from the same table.

## Distinct from
- `cbs_netherlands_food_cpi_panel.csv` (CPI indexes, not HES shares)
- Season2 food×income (income-decile columns in 60046ned intentionally unused)
- Season2 eating-out (restaurants/hotels not extracted)
- Eurostat NAMA food % HFCE (national accounts; separate companion)

## Skips / caveats
- 85420NED / 83679NED TypedDataSet returned HTTP 500 — used 83676NED which carries both amount and share.
- Classification break: pre-2015 «Voeding» ≠ post-2015 COICOP CPI01; keep `category`/`coicop` labels distinct.
- No FX. No fabrication beyond ratio of two published levels.
- Retrieved: 2026-10-24
