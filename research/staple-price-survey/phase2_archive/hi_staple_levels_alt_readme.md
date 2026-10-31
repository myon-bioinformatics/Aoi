# hi_staple_levels_alt — high-income staple retail *price levels* (alt path)

**Lane:** `hi_staple_levels_alt` (Aoi phase-2). Absolute retail averages in local currency — **not** CPI indices, **not** ICP PLIs.

**Target ISO3:** AUS, CAN, CHE, DNK, NOR (Season2 owns HI staple levels overall; they hold HKG/MYS/NZL/SGP and continue MENA+TWN/EUZ. Eurostat absolute food-price bulk does not exist — not chased.)

**Panel:** `hi_staple_levels_alt_panel.csv`  
**Raw:** `raw/hi_staple_levels_alt/`  
**Rules:** no FX conversion; missing stays missing; units documented per row; partial coverage OK.

Date assembled: **2026-10-24 Asia/Tokyo**.

---

## Hit / miss

| ISO3 | Status | Rows | Span | Staples | Source |
|------|--------|-----:|------|---------|--------|
| **AUS** | **HIT** (discontinued snapshot) | 24 | 2011-06 | rice 1kg; white bread 650–750g loaf; self-raising flour 2kg — 8 capital cities | ABS 6403.0.55.001 June quarter 2011 |
| **CHE** | **HIT** (monthly) | 2586 | 2000-01 … 2026-09 | bread + wheat flour + milk + eggs + potato + sunflower_oil + butter (FOAG) | FOAG Lindas Consumption_Price_Month cubes |
| **CAN** | **MISS** | 0 | — | — | StatCan table **18-10-0245** (Average retail prices for food) exists; box egress TLS EOF to `www150.statcan.gc.ca` CSV/zip; open.canada only mirrors same host; Wayback CDX also TLS-failed from box. Machines offline for alternate egress. Retry via browser / user egress. |
| **DNK** | **MISS** | 0 | — | — | Statistics Denmark publishes HICP/net price **indices**, not item-level average krone prices for rice/bread/flour in open bulk. No official absolute series located. |
| **NOR** | **MISS** | 0 | — | — | SSB Norway likewise CPI/index-oriented for food; no open average NOK retail series for rice/bread/flour found. |

**Total panel rows:** 2610 (AUS 24 + CHE 2586).

---

## Column schema

| column | meaning |
|--------|---------|
| `iso3` | Country |
| `item` | Canonical staple: `rice`, `bread` / `bread_white`, `wheat_flour` / `wheat_flour_self_raising` |
| `item_label` | Source product wording |
| `unit` | Price unit as charged (e.g. `AUD per 1kg`, `CHF per kg`) — **do not convert packs** |
| `date` | `YYYY-MM` (month or quarter-end month) |
| `year` | Calendar year |
| `value` | Price in `currency` (AUS converted from source cents → AUD) |
| `currency` | LCU ISO code |
| `source_url` | Primary download / cube URL |
| `source` | Short attribution |
| `note` | Unit / coverage caveats |
| `geo_detail` | Capital city (AUS) or national (CHE) |

---

## Source notes

### AUS — ABS 6403.0.55.001 (HIT, closed series)
- File: `raw/hi_staple_levels_alt/aus_6403_201106.xls` (from ABS DetailsPage Jun 2011 zip).
- Source values are **cents**; panel stores **AUD** (`cents/100`).
- Geography: Sydney, Melbourne, Brisbane, Adelaide, Perth, Hobart, Darwin, Canberra (not a national average).
- Series **discontinued** after 2011; later ABS CPI collection no longer publishes this absolute selected-items table. Optional 2023 narrative point estimates in ABS articles were not folded in (need careful unit/geo checks; not in this panel).

### CHE — FOAG consumer prices (HIT)
- SPARQL against Lindas FOAG cube `Consumption_Price_Month`; tidy raw `foag_che_bread_flour_raw.csv`.
- Prices are **CHF per kg** (cube unit) for bread and flour product variants (white / semi-white / brown / wholemeal / spelt / low-price; organic and non-organic).
- **Rice** is not in this bread–cereals–flour cube.
- BFS LIK “Durchschnittspreise ausgewählter Produkte” monthly XLSX (`che_avg_prices_sep2026.xlsx`, `che_avg_prices_201901.xlsx`) was checked: published selected list is meat/dairy/eggs/sugar/potatoes/etc. — **no rice, bread, or flour**. Do not use BFS selected averages for these staples.

### CAN — blocker
- Target: Statistics Canada table **18-10-0245** Average retail prices for food and other selected items (rice ~2 kg, white bread ~675 g, etc.).
- Blocker: TLS `unexpected eof` from this box to `www150.statcan.gc.ca` for CSV/zip/SDMX; CKAN on open.canada.ca points at the same URLs.
- **2026-10-25 re-probe:** Wayback CDX lists `18100245-eng.zip` snapshots (e.g. 20221208); box download of Wayback `id_` URL also TLS EOF. DBnomics: no absolute retail series. Still need browser/user copy into `raw/hi_staple_levels_alt/`. See `raw/hi_staple_probe_2026-10-25/SKIP.txt`.

### DNK / NOR — blocker
- No NSO open dataset of average retail DKK/NOK prices for rice, bread, wheat flour found; public materials are index-based. Eurostat absolute food-price tables are unavailable in open bulk (Season2 confirmed). Documented as miss rather than fabricating or using PLIs.

### Explicitly excluded
- OECD/ICP **price level indices** (relative, not LCU retail) — probe saved as `oecd_ppp_probe.csv` but **not** in the panel.
- CPI / HICP food or bread-and-cereals indices (Season2 FAO/ILO CPI lanes).

---

## Relation to Season2

Season2 lane `adjacent_hi_staple_levels` holds HKG/MYS/NZL/SGP absolute hits. This Aoi alt lane covers the five countries they asked Aoi to try. Overlap with Season2 files should stay zero for these five until CAN/DNK/NOR succeed elsewhere.
