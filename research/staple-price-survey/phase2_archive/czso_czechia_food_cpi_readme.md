# CZSO Czechia food CPI (COICOP 2018) index panel

**File:** `czso_czechia_food_cpi_panel.csv`  
**ISO3:** CZE  
**Source:** Czech Statistical Office (CZSO / ČSÚ) open data dataset **CEN0101E** — Consumer price index by COICOP 2018.  
**Download:** `https://data.csu.gov.cz/opendata/sady/CEN0101E/distribuce/csv` → `CEN0101E.csv`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **2,115**
- Series: **15** (division 01 + classes 011/0111–0119/012 + division 11 + 111/112)
- Levels: {'division': 282, 'group': 564, 'class': 1269}
- Span: **2015-01-01 – 2026-09-01** (monthly)
- Unit: index, **2025=100** (`TYPUDAJE4A=IZ2025`)

## Why landed
`easteu_national_food_cpi_panel.csv` holds only IMF/OECD **aggregate** food CPI for CZE. This pack adds COICOP class subgroups (cereals, meat, dairy, fruit, veg, catering, …).

## Notes
- Filters: households total (`EKAKTIOCDS=0`), territory Czechia (`UZ02P=CZ`), monthly `YYYY-MM` only (dropped cumulative `K`, quarters, years).
- Other bases (IZ2015, month-on-month IR/IM) not included — single base, levels only.
- No FX, no fabricate. Season2 absolute EUZ-proxy lane separate.
- Raw: `raw/czso_cz/CEN0101E.csv` (~67 MB).
