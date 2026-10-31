# World Bank Pink Sheet — coffee & sugar (numeraire)

**Retrieved:** 2026-10-24 Asia/Tokyo · promoted from `raw/numeraire/`

## What
Tidy monthly companion for **coffee** (Arabica, Robusta) and **sugar** (EU, US, World) from the World Bank Pink Sheet (CMO Historical Data Monthly).

Rice Pink Sheet series stay in `rice_international_price_panel.csv` — not duplicated here.

## Files
- Panel: `pink_sheet_coffee_sugar_panel.csv` (**4,005** rows)
- Upstream tidy extract: `raw/numeraire/pink_sheet_rice_coffee_sugar_monthly.csv`
- Original workbook (shared with rice intl): `raw/rice_intl/CMO-Historical-Data-Monthly.xlsx`

## Coverage
| variable | span | n |
|---|---|---|
| `pink_sheet_coffee_arabica_usd_per_kg` | 1960–2026 | 801 |
| `pink_sheet_coffee_robusta_usd_per_kg` | 1960–2026 | 801 |
| `pink_sheet_sugar_eu_usd_per_kg` | 1960–2026 | 801 |
| `pink_sheet_sugar_us_usd_per_kg` | 1960–2026 | 801 |
| `pink_sheet_sugar_world_usd_per_kg` | 1960–2026 | 801 |

- Unit/currency as published (nominal USD / kg). **No FX conversion.** Missing months omitted (not filled).
