# USDA NASS — All-Farm Prices Paid / Prices Received indexes

## Panel
- File: `usda_nass_farm_price_index_panel.csv`
- Rows: 376 (2 series × 188 months)
- Span: 2011-01 … 2026-08
- Series: Prices Paid, All Farms; Prices Received, All Farms
- Base: 2011 = 100

## Source
- USDA NASS Charts and Maps — Agricultural Prices open text
- https://www.nass.usda.gov/Charts_and_Maps/graphics/data/allprpd.txt (2016–2026-08)
- https://www.nass.usda.gov/Charts_and_Maps/Agricultural_Prices/allprpd.txt (2011–2020)
- Raw: `raw/usda_nass_farm_price_index/`
- Retrieved: 2026-10-25 (Asia/Tokyo)

## Distinct from
- `usda_ers_food_price_outlook_panel.csv` (ERS food CPI % changes / forecasts)
- `usda_fes_usa_food_expenditure_panel.csv` (Food Expenditure Series shares)
- `usda_psd_grains_panel.csv` (PSD production/stocks)
- BLS CPI-U FAH/FAFH (consumer indexes)
- FAOSTAT PP PPI (already inside producer_prices_staples; not re-extracted)

## Notes
- Farm-gate / input price indexes for US agriculture — Engel-adjacent cost/return companion, not household food CPI.
- QuickStats API unauthorized without key; open chart text used instead.
- No FX.
