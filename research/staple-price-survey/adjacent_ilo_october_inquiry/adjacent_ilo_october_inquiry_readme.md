# adjacent_ilo_october_inquiry — ILO October Inquiry / ILOSTAT retail food (MISS for staple_price)

Retrieved: 2026-10-24 Asia/Tokyo

## Result

**No vertical `staple_price` rows loaded.** Public ILOSTAT and reachable UN/ILO mirrors do **not** expose absolute local-currency retail prices for bread, rice, flour, pasta, potatoes (or the historical October Inquiry 93-food-item panel).

What ILOSTAT *does* publish under Prices is **CPI** (incl. food COICOP), **official FX**, and **private-consumption PPP** — indices / conversion factors, not item LCU levels. Per Season2 hard rules those must **not** be loaded as `staple_price`. Sibling pack `adjacent_ilo/` already holds ILO food CPI indices for index work; this pack is documentation + raw probes only.

## What was checked

| Source | Content | Absolute LCU retail food item prices? |
|--------|---------|--------------------------------------|
| ILOSTAT rplumber TOC (`metadata/toc/indicator`) | 1964 indicators; PRICES db = 15 series | **No** — only `CPI_*`, `CCF_XOXR_*`, `CCF_XPPP_*`, discontinued labour-cost |
| rplumber `data/search?q=retail prices food` | Hits = CPI COICOP series | **No** |
| rplumber `data/search?q=October Inquiry` | Unrelated (strikes/lockouts etc.) | **No** |
| SDMX `sdmx.ilo.org` dataflows (~1215) | Price flows = `DF_CPI_*` family | **No** absolute retail |
| UNdata LABORSTA `tableCode:8` / `C5` / `RP` | “Series not found” | **No** (absolute retail not on UNdata) |
| UNdata LABORSTA `tableCode:7C` | Consumer prices, food indices (2000=100) | **Index only** (not loaded here) |
| laborsta.ilo.org live | Host gone / migrated | Unreachable |
| Wayback LABORSTA (`applv8/data/c5e.html`, STP, topic pages) | Snapshots listed by availability API | Content fetch from this box timed out (HTTP 000); no CSV recovered |
| ILO publication “Statistics from the ILO October Inquiry, 2009” CD-ROM | 93 food items, ~1985–2009, LCU retail | **CD-ROM / paid pub only** — no open CSV/API |
| NBER OWW3 | October Inquiry **wages** 1953–2008 | Wages, not food prices |
| Moatsos / de Zwart digitization | CV: “century long ILO October Inquiry Wages and Prices… 1911–2008” / “full ILO October Inquiry dataset” | Listed **in preparation**; no open Dataverse/DANS/IISH download found |
| DANS / IISH / Zenodo / Figshare / Harvard Dataverse keyword search | No matching absolute-price Inquiry food CSV | Miss |
| Classic ILO `WEB_bulk_download` / guessed `RPR_*` indicator IDs | 404 / invalid | Miss |

## Schema note (if data appear later)

Vertical target: `country,date,year,variable,value,unit,source,note,estimated_value` with ISO3; `note` must cite “ILO October Inquiry / ILOSTAT retail food prices as published”; absolute LCU only; no FX; no unit homogenization; no gap-fill; `estimated_value=false` for published cells.

## Raw artifacts

- `raw/toc_indicator.csv` — full ILOSTAT indicator TOC
- `raw/sdmx_dataflows.xml` — SDMX dataflow catalogue
- `raw/rplumber_openapi.json`, `raw/rplumber_search_*.json` — API probes
- `raw/undata/` — UNdata LABORSTA series-not-found HTML
- `raw/academic/CV_Moatsos.txt` — CV excerpt noting unpublished Inquiry digitization
- `_build_stats.json` — machine-readable miss summary

## URLs

- https://ilostat.ilo.org/
- https://rplumber.ilo.org/metadata/toc/indicator/?type=label&lang=en&fmt=csv
- https://rplumber.ilo.org/data/search?q=retail%20prices%20food&type=indicator
- https://sdmx.ilo.org/rest/dataflow/ILO/all/latest
- https://data.un.org/Data.aspx?d=LABORSTA&f=tableCode%3A7C
- https://www.ilo.org/publications/occupational-wages-and-hours-work-and-retail-food-prices-statistics-ilo-1
- https://www.nber.org/research/data/occupational-wages-around-world-oww-database
- http://laborsta.ilo.org/ (historical; offline)

## Mirror

`/workspace/aoi-phase2/staple-price-survey/adjacent_ilo_october_inquiry/`

## Explicit non-touches

- Did not modify Aoi CPI-index companions or `hi_staple_levels_alt`.
- Did not reload or alter `adjacent_ilo/` (CPI food indices).
- Skipped DEU browser work (handled elsewhere).
- BEL/AUT/FIN/PRT/FRA/IRL/NLD/ESP already handled in other packs — not re-collected here.
