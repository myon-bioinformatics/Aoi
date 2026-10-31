# FAOSTAT FBS — animal-products dietary energy share (derived)

**Retrieved:** 2026-10-25 Asia/Tokyo · Aoi non-CPI supply companions

## What
Tidy **share** panel derived from existing `fao_fbs_kcal_supply_panel.csv` (element **664** levels):

\[
\texttt{fbs\_animal\_kcal\_share} = 100 \times \frac{\mathrm{kcal}(2941\ \mathrm{Animal\ Products})}{\mathrm{kcal}(2901\ \mathrm{Grand\ Total})}
\]

Only **iso3×year** rows where **both** items exist. Columns `kcal_animal` and `kcal_total` keep the input levels for audit.

## Files
- Panel: `fao_fbs_animal_kcal_share_panel.csv` (**2,392** rows; **176** ISO3; **2010–2023**)
- Source panel: `fao_fbs_kcal_supply_panel.csv` (no new FAO download)

## Notes
- **Japan absent** (same as FBS 2010– kcal bulk).
- **FBSH analog skipped:** `fao_fbsh_kcal_supply_panel.csv` has items 2901/2905/2907 only — **no 2941**.
- Distinct from FS animal **protein** (21014) and from cereal energy shares.
- Share range in file ≈ 1.45–45.18% (no all-null; no fill). No FX.
- **CHN**=mainland via source panel.
