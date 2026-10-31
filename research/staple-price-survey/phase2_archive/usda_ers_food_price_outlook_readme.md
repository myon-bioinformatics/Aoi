# USDA ERS Food Price Outlook — food CPI % changes (USA)

**File:** `usda_ers_food_price_outlook_panel.csv`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **10,381**
  - Annual realized % changes: **1,119** rows; **22** CPI items; span **1974–2025**
  - Historical forecast midpoints: **9,262** rows (Attribute = Midpoint of forecast interval)
- ISO3: USA only

## Why landed
Different companion **type** from BLS FAH/FAFH **index levels** already in Aoi: ERS publishes curated annual % changes and a long forecast-vs-outcome archive for food CPI categories (All food, FAH, FAFH, meats, dairy, fruits/veg, etc.). Open media CSVs from ERS Food Price Outlook.

## Notes
- Values are **percent changes**, not index levels — do not splice onto BLS indexes without transforming.
- No FX, no fabricate.
- Raw: `raw/usda_ers_fpo/` (also holds near-term 2024–2027 changes CSV and landing.html).
