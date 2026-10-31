# International rice price panel (Aoi origin batch)

Date: **2026-10-24 Asia/Tokyo**.  
File: `rice_international_price_panel.csv`  
Raw workbook: `raw/rice_intl/CMO-Historical-Data-Monthly.xlsx`

## Source

| Field | Detail |
|---|---|
| Publisher | World Bank Prospects Group — **Commodity Markets “Pink Sheet”** |
| Landing | https://www.worldbank.org/en/research/commodity-markets |
| File | `CMO-Historical-Data-Monthly.xlsx` (Monthly Prices sheet; updated 2026-10-02) |
| License | World Bank data CC BY 4.0 (see Commodity Markets page terms) |
| Units | Nominal **USD/mt** (no FX conversion applied; already USD quotes) |
| Frequency | Monthly |
| Missing | `…` cells omitted — **not** filled |

Underlying quotations (Pink Sheet Description sheet): Thailand 5%/25%/A.1 and Vietnam 5% from Bloomberg / USDA / World Bank surveys (f.o.b. Bangkok / Hanoi).

## Series in panel

| series | span | n months | note |
|---|---|---:|---|
| `rice_thai_5pct` | 1960-01 → 2026-09 | 801 | Classic Thai 5% broken benchmark |
| `rice_thai_25pct` | 1986-01 → 2026-09 | 485 | |
| `rice_thai_a1` | 1986-01 → 2026-09 | 489 | A.1 Super from 2006; prior A1 Special |
| `rice_vietnam_5pct` | 2003-12 → 2026-09 | 263 | |

Columns: `series,year,month,date,value,unit,currency,source,source_url,file,note`

## Related / scouted but not primary here

- **FAO GIEWS FPMA** international tool (https://fpma.fao.org/giews/fpmat4/) — UI has ~90 international series; no stable open CSV API found this round (SPA returns HTML).
- **AMIS Market Database** — CBS supply/use oriented; smart-csv BigQuery wrapper exists on FAO catalog but is not a drop-in Thai-5% price panel. Catalog: https://data.apps.fao.org/catalog/dataset/amis-database
- **IRRI World Rice Statistics** — portal URLs 404/unstable this round; treat as scout-only.
- Companion Pink Sheet coffee/sugar extract (same workbook): `raw/numeraire/pink_sheet_rice_coffee_sugar_monthly.csv`

## Rules

No fabricated values; no unit unification across non-USD sources; missing stays missing. Distinct from Japan domestic rice retail in `rice_monthly_*.csv` / GohanTrust panels.
