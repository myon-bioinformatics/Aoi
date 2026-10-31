# Japan RPS — extra staple retail levels (小麦粉 / バター / 豚肉)

## Panel
- File: `japan_retail_price_extra_staples_panel.csv`
- Rows: 756
- Years: 2005–2025 (monthly city-mean)
- Items: 1071 小麦粉 (JPY/1kg袋), 1321 バター (JPY/200g箱), 1211 豚肉 (JPY/100g)
- Schema matches `japan_retail_price_numeraire_panel.csv`.

## Counts
                        n    y0    y1
item_code item_label                 
1071      小麦粉         252  2005  2025
1211      豚肉          252  2005  2025
1321      バター         252  2005  2025

## Source
- e-Stat 小売物価統計調査（動向編） — same annual city×month bulk as numeraire/rice
- Raw: `raw/japan_rps_numeraire/` (+ `converted_xls/`); provenance `raw/japan_rps_extra/`
- Aggregation: unweighted mean of surveyed cities with published monthly price
- No FX

## Notes
- Extends Japan absolute retail beyond rice + numeraire (食パン/牛乳/鶏卵/ゆでうどん).
- Distinct from CPI indexes and Season2 Japan quintile Engel.
- Retrieved: 2026-10-24 (Asia/Tokyo)
