# FAOSTAT FS 21012 — cereal+roots+tubers dietary energy share

**Retrieved:** 2026-10-25 Asia/Tokyo · Aoi non-CPI resume

## What
Canonical **Bennett-adjacent** international series: FAOSTAT Suite of Food Security Indicators (**FS**) item **21012** — *Share of dietary energy supply derived from cereals, roots and tubers (percent) (3-year average)*, element **6121** Value.

## Files
- Panel: `fao_fs_cereal_root_tuber_energy_share_panel.csv` (**3,732** rows; **185** ISO3; end-years **2002–2023**)
- Raw: `raw/engel_global_ref/faostat_fs_cereal_root_tuber_energy_share.csv` (from Food_Security bulk)

## Year convention
3-year average labels (e.g. `2000-2002`) → **`year` = end-year of window** (catalog join key). Original label kept as `year_label_3y`. Frequency = `annual_3y_avg_end_year`.

## Notes
- Promotes beyond stub `engel_global_ref_panel_stub.csv` (`fs_dietary_energy_share_cereals_roots_tubers_pct`).
- **Japan present** (8 end-years) — unlike FBS 2010– kcal bulk.
- Distinct from FBS/FBSH cereal-only share (2905/2901) and from OWID staple-energy companion.
- **CHN** = mainland. No FX. No fill. Invalid ISO3 / regions dropped.
