# Japan RPS — miso / soy sauce retail levels

## Panel
- File: `japan_retail_price_miso_shoyu_panel.csv`
- Rows: 504
- Years: 2005–2025 (monthly city-mean)
- Items: 1621 しょう油, 1631 みそ
- Schema matches `japan_retail_price_oil_sugar_coffee_panel.csv` / numeraire / extras.

## Counts
```
                        n    y0    y1
item_code item_label                 
1621      しょう油        252  2005  2025
1631      みそ          252  2005  2025
```

## Source
- e-Stat 小売物価統計調査（動向編） — same oil/seasonings annual city×month bulk parts already under `raw/japan_rps_oil_sugar/` (part01+7; **no new e-Stat download** this turn)
- Aggregation: unweighted mean of surveyed cities with published monthly price
- Layout: **年平均** then Jan–Dec (aligned with oil/sugar/coffee panel)
- No FX
- Distinct from oil/sugar/coffee panel (1601/1632/1921), numeraire, and extra staples

## Spec notes
- **しょう油 1621** / **みそ 1631**: yen as published per e-Stat pack unit for that year (pack grams can change — do not treat as constant pack without a break note).
- Parser validated against existing oil panel 2005-01 city-mean for item 1601 (same OLE stacked layout; month offset after annual).

- Retrieved: 2026-10-25 (Asia/Tokyo)
