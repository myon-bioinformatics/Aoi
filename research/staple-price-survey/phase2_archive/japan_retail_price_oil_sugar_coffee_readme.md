# Japan RPS — edible oil / sugar / instant coffee retail levels

## Panel
- File: `japan_retail_price_oil_sugar_coffee_panel.csv`
- Rows: 696
- Years: 2005–2025 (monthly city-mean)
- Items: 1601 食用油, 1632 砂糖, 1921 インスタントコーヒー
- Schema matches `japan_retail_price_numeraire_panel.csv` / extra staples.

## Counts
```
item_code  item_label           n    y0    y1
1601       食用油                216  2005  2025
1632       砂糖                 252  2005  2025
1921       インスタントコーヒー         228  2005  2025
```

## Source
- e-Stat 小売物価統計調査（動向編） — annual city×month bulk parts for oils/seasonings (+7 from part01) and beverages/coffee (+10 part01 for 2005–2021; +11 for 2023–2025)
- Raw: `raw/japan_rps_oil_sugar/` (estat_*_oil_sugar.*, estat_*_coffee.*)
- Aggregation: unweighted mean of surveyed cities with published monthly price
- No FX

## Skips / gaps
- 2007–2009: 1601 食用油 absent from oil_sugar part (file codes start at 1611); 1632 砂糖 present
- 2014: coffee e-Stat part 404 (no file)
- 2022: no beverage/coffee part in sequential statInfId offsets from part01 (+10 industrial; +11 unrelated)

## Spec notes
- **食用油 1601**: published unit is 1本; brand/pack changed over the span (e.g. salad oil ~1500g early years → canola 900g by mid-2020s). Values are yen as published — do not treat as constant pack without a break note.
- **砂糖 1632**: 1袋 = 1kg 上白 (stable).
- **インスタントコーヒー 1921**: published bottle / 100g-basis; jar grams vary by year. Distinct from Pink Sheet coffee (world commodity USD).
- Not in numeraire (1021/1031/1303/1341) or extra staples (1071/1211/1321).

- Retrieved: 2026-10-25 (Asia/Tokyo)
