# FAOSTAT Food Balances (2010–) — cereal dietary-energy share

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi origin companion batch

## What
Annual **cereal energy share** derived from FAOSTAT domain **FBS** (Food Balances 2010–), element **664** Food supply (kcal/capita/day):

\[ \texttt{fbs_cereal_energy_share} = 100 \times \frac{\mathrm{kcal}(2905)}{\mathrm{kcal}(2901)} \]

- Item **2901** Grand Total  
- Item **2905** Cereals – Excluding Beer  

Also ships the two underlying kcal levels so the share is auditable.

## Files
- Panel: `fao_fbs_cereal_energy_share_panel.csv` (**7,275** rows; **178** ISO3; years **2010–2023**)
- Raw bulk: `raw/faostat_fbs/FoodBalanceSheets_E_All_Data_Normalized.zip` (FAOSTAT production bulk)
- Slim extract: `raw/faostat_fbs/fbs_kcal_2901_2905_slim.csv` (items 2901 & 2905, element 664 only)

## Variables
| variable | unit | notes |
|---|---|---|
| `food_supply_kcal_total_fbs` | kcal/capita/day | item 2901 |
| `food_supply_kcal_cereals_fbs` | kcal/capita/day | item 2905 |
| `fbs_cereal_energy_share` | % of dietary energy | derived; missing only when a level is missing |

## Japan / Season2
- **Japan is not present** in this FBS 2010– bulk pull (0 JPN rows) — known FBS Japan gap; Season2 owns FBSH Japan + historical Bennett.
- Distinct from Season2 adjacent **FBSH** (`*_fbsh`) and from FAO FS **21012** / OWID staple-energy companions already in Aoi.
- No FX. No interpolation. Regional aggregates dropped; country rows with ISO3 kept (178).

## Provenance
Source URL pattern: `https://bulks-faostat.fao.org/production/FoodBalanceSheets_E_All_Data_(Normalized).zip`  
Domain label in panel: `domain=FBS`.
