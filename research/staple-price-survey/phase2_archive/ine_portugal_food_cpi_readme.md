# Statistics Portugal INE food CPI (COICOP) index panel

**File:** `ine_portugal_food_cpi_panel.csv`  
**ISO3:** PRT  
**Source:** Statistics Portugal (INE) — Consumer price index by COICOP, Base 2025 (indicator **0014639**).  
**API:** `https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0014639&Dim1=T&Dim2=PT&lang=EN`  
**Meta:** `pindicaMeta.jsp?varcd=0014639` (Dim1=`S3AyyyyMM`).  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **28,245**
- Series: **85** (COICOP **01*** food/non-alcoholic + **11*** restaurants/accommodation)
- Levels: {'division': 1890, 'group': 3216, 'class': 14574, 'subclass': 8565}
- Span: **1948-01-01 – 2026-09-01** (monthly)
- Unit: index, **2025=100**

## Why landed
Eurostat HICP in aoi-phase2 is one `hicp_food_cp011_i15` for PRT. National IPC Base-2025 tree is deep COICOP (to 5-digit subclasses).

## Notes
- Geography: Portugal national (`Dim2=PT`) only — regional slices in raw full dump not kept in panel.
- Deep COICOP subclasses largely populate from **~2015** onward (~84–85 series); earlier decades carry fewer aggregate 01/11 codes only (source basket evolution — not backfilled).
- Blank / missing `valor` dropped — no fabricate, no FX, no rebase.
- Season2 owns eating-out *expenditure shares* and absolute EUZ-proxy levels; this panel is **CPI indexes only**.
- Raw: `raw/ine_pt/0014639_PT_all.json` (~109 MB), `0014639_meta.json`, sample month JSON.
