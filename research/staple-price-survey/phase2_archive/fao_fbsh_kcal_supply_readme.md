# FAOSTAT Food Balances Historic (FBSH) — food supply kcal/cap/day levels

**Retrieved:** 2026-10-25 Asia/Tokyo · Aoi non-CPI resume

## What
Annual **kcal/capita/day** levels from FAOSTAT domain **FBSH** (Food Balances −2013, old methodology), element **664**:

| variable | item | label |
|---|---:|---|
| `fbsh_kcal_cap_day_total` | 2901 | Grand Total |
| `fbsh_kcal_cap_day_cereals_excl_beer` | 2905 | Cereals – Excluding Beer |
| `fbsh_kcal_cap_day_starchy_roots` | 2907 | Starchy Roots |

## Files
- Panel: `fao_fbsh_kcal_supply_panel.csv` (**24,702** rows; **172** ISO3; years **1961–2013**)
- Raw slim: `raw/faostat_fbsh/fao_fbsh_kcal_2901_2905_2907.csv`

## Notes
- **Japan present** 1961–2013 (53 years × 3 items).
- Levels-focused; total/cereals also appear inside `fao_fbsh_cereal_energy_share_panel.csv`. **New** here: tidy starchy-roots **2907** levels for Bennett (cereals+roots) arithmetic.
- Does **not** replace the cereal-share panel; domain=`FBSH`; **CHN**=mainland; no FX; no fill.
- Bulk URL: `https://bulks-faostat.fao.org/production/FoodBalanceSheetsHistoric_E_All_Data_(Normalized).zip`
