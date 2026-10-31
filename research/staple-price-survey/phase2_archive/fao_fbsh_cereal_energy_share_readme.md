# FAOSTAT Food Balances Historic (FBSH) — cereal dietary-energy share

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi origin companion batch

## What
Annual **cereal energy share** derived from FAOSTAT domain **FBSH** (Food Balances −2013, old methodology), element **664** Food supply (kcal/capita/day):

\[ \texttt{fbsh_cereal_energy_share} = 100 \times \frac{\mathrm{kcal}(2905)}{\mathrm{kcal}(2901)} \]

- Item **2901** Grand Total
- Item **2905** Cereals – Excluding Beer

Also ships the two underlying kcal levels. Panel variable names use the `fbsh_` / `_fbsh` suffix; column `domain=FBSH`.

## Files
- Panel: `fao_fbsh_cereal_energy_share_panel.csv` (**25,026** rows; **175** ISO3 with share; years **1961–2013**)
- Raw bulk: `raw/faostat_fbsh/FoodBalanceSheetsHistoric_E_All_Data_Normalized.zip` (FAOSTAT production bulk)
- Slim extract: `raw/faostat_fbsh/fao_fbsh_kcal_2901_2905_2907.csv` (items 2901/2905/2907, element 664)

## Variables
| variable | unit | notes |
|---|---|---|
| `food_supply_kcal_total_fbsh` | kcal/capita/day | item 2901 |
| `food_supply_kcal_cereals_fbsh` | kcal/capita/day | item 2905 |
| `fbsh_cereal_energy_share` | % of dietary energy | derived; missing only when a level is missing |

## Japan / Season2
- **Japan is present** historically in FBSH (share years **1961–2013**, n=53).
- Season2 adjacent also holds FBSH Bennett-style shares for the Big Mac universe — this Aoi file is a **companion tidy** of the same open bulk (cereal share 2905/2901), not an exclusive claim.
- Distinct from Aoi `fao_fbs_cereal_energy_share_panel.csv` (domain **FBS** 2010–) and from FAO FS **21012** / OWID staple-energy companions.
- No FX. No interpolation. Regional / former-entity rows without a stable ISO3 dropped.

## Provenance
Source URL pattern: `https://bulks-faostat.fao.org/production/FoodBalanceSheetsHistoric_E_All_Data_(Normalized).zip`  
Domain label in panel: `domain=FBSH`.
