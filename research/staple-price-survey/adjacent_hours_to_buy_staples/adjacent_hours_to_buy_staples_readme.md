# adjacent_hours_to_buy_staples — labour-minutes/hours to buy 1 kg staple

Retrieved: **2026-10-24 Asia/Tokyo** · Season2 adjacent for Aoi #118

## Result

**240 vertical rows** · **2 ISO3** (DEU, BRA) · year span **1970–2024**.

Official / designed **minutes of work** to buy a published staple quantity (bread / rice / flour / potato or closest), kept as **minutes per kg**. **Not** DIY wage÷price from separate wage and price series. `estimated_value` empty.

Schema: `country,date,year,variable,value,unit,source,note,estimated_value` (ISO3; `unit=minutes` as published/normalized; DEU annual `date=YYYY-01-01`; BRA monthly `date=YYYY-MM-01`).

## Intentional skips (Aoi / Season2 lanes)

Skipped this pack: food CPI indexes, housing share, SGP/HKG CPI, USDA FPO, `hi_staple_levels_alt`, BLS, FPMA, Pink Sheet, UK ONS retail, CoAHD, KOR/TWN quintiles, Japan numeraire, `adjacent_food_share_by_income`, `adjacent_eating_out_shares`.

## Variables

| variable | rows | unit | definition |
|----------|-----:|------|------------|
| `hours_to_buy:rye_bread_kg` | 24 | minutes | DEU BMEL — Roggenmischbrot (counter), minutes of industrial worker **net** hourly wage per 1 kg |
| `hours_to_buy:potato_kg` | 72 | minutes | DEU Speisekartoffeln kg + BRA Batata normalized ÷6 kg basket |
| `hours_to_buy:rice_kg` | 48 | minutes | BRA Arroz 3 kg tempo ÷3 |
| `hours_to_buy:flour_kg` | 48 | minutes | BRA Farinha 1.5 kg tempo ÷1.5 |
| `hours_to_buy:bread_kg` | 48 | minutes | BRA Pão 6 kg tempo ÷6 |

Naming keeps `hours_to_buy:*` even when unit is **minutes** (as published); do not convert to hours.

## Sources (loaded)

1. **BMEL-Statistik 5050900** (DEU) — *Kaufkraft des Stundenlohnes eines Industriearbeiters bei einzelnen Nahrungsmitteln* (Destatis/AMI/BMLEH). Table unit: **Minuten je Mengeneinheit**. Staples in open table: **Roggenmischbrot** (kg), **Speisekartoffeln** (kg). No rice/flour rows in 5050900. Years: 1970, 1980, 1990, 2000, then annual 2005–2024. Raw: `raw/deu/5050900-0000_data.csv` + `5050900-0000.xlsx`.

2. **DIEESE PNCBA** (BRA) — *Pesquisa Nacional da Cesta Básica de Alimentos*, product-level HTML with «tempo necessário para adquirir» for a **minimum-wage** worker (`XhYYm` for basket qty). **São Paulo** city only → ISO3 BRA. Normalized to minutes/kg by ÷ published basket kg (Arroz 3, Farinha 1.5, Batata 6, Pão 6). Public product HTML densified **2005-01 … 2015-06** (48 months with usable SP rows); post-~2017/2018 product detail mostly 403/404. **Not IBGE** — trade-union research institute; cited explicitly as designed same-publication labour-time indicator (not DIY wage÷price).

## Coverage (hits)

| ISO3 | rows | years | source | staples |
|------|-----:|-------|--------|---------|
| DEU | 48 | 1970–2024 (24 pts) | BMEL 5050900 | rye_bread, potato |
| BRA | 192 | 2005–2015 (48 months) | DIEESE PNCBA SP | rice, flour, potato, bread |

## Files

| file | role |
|------|------|
| `adjacent_hours_to_buy_staples_vertical.csv` | long panel |
| `adjacent_hours_to_buy_staples_vertical.csv.gz` | gzip mirror |
| `_coverage_by_country.csv` | per-ISO3 summary |
| `_build_stats.json` | build stats + BRA month list |
| `readme.md` / `missing.md` | this pack |
| `raw/deu/` | BMEL CSV/XLSX + JSON sidecar |
| `raw/bra/tab_YYYYMM.html` | DIEESE monthly city tables |

## Method notes

- Only series where the **publisher** already combines wage and price into labour-time for the staple are loaded.
- BRA values are **normalized** (basket minutes ÷ kg) so variables are per-kg comparable; original basket qty and `XhYYm` string remain in `note`.
- UBS Prices & Earnings, WIFO/Statista press charts, ILO October Inquiry **absolute** bulk without a published minutes-to-buy staple table, and GovData «Preise und Löhne» separate series are **out of scope** (would be DIY).
