# Singapore / Hong Kong / Macao food CPI **indexes** (thin geography)

**File:** `sgp_hkg_food_cpi_index_panel.csv`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **16,241**
- ISO3: HKG, MAC, SGP — counts {'HKG': 1770, 'MAC': 319, 'SGP': 14152}
- **Singapore (SingStat M213751):** 77 food/F&B-serving (+ All Items) series; monthly indexes **2024=100**; span **1961-01-01 – 2026-09-01** (series start dates vary; Food from 1961-01)
- **Hong Kong (Censtatd 510-60003):** Composite CPI COICOP division — Food & NAB, Restaurants & accommodation, Total; base Oct2019–Sep2020=100; monthly **2005-01-01 – 2026-09-01**
- **IMF PCPIF** (DBnomics): aggregate food CPI for SGP/HKG/MAC (MAC open path; parallels nationals)

## Why landed
`asia_national_food_cpi_panel.csv` has no SGP/HKG/MAC. Season2 `adjacent_hi_staple_levels` owns **absolute retail levels** for HKG/SGP — this panel is **indexes only**. OECD SDMX CP01 returned NoRecordsFound for SGP/HKG. Korea national food CPI already in Asia pack via OECD — not redone (KOSIS SSL avoided).

## Notes
- No FX, no fabricate, no levels.
- SingStat weighting: HES 2023 updated to 2024.
- HK Food is COICOP division (not deep subgroups in open full-series API used here); SingStat carries the deep staple tree.
- Raw: `raw/sgp_hkg_cpi/`.
