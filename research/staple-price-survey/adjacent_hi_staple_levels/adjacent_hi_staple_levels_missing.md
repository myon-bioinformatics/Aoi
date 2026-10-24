# adjacent_hi_staple_levels — missing / blocked

Retrieved: 2026-10-24 Asia/Tokyo

## Gap-16 without absolute staple series (12)

| ISO3 | Status |
|------|--------|
| ARE | No open NSO average retail staple series found (FCSC probe 403). |
| AUS | ABS Average Retail Prices (6403.0.55.001) **discontinued 2011**; open cubes / Wayback not retrieved from this box; data.gov.au search did not surface a current absolute retail staple CSV. |
| BHR | data.gov.bh reachable; no staple average-price bulk secured. |
| CAN | StatsCan table **18-10-0245** (Monthly average retail prices) — **TLS `UNEXPECTED_EOF`** from box; open.canada.ca API returned empty/non-JSON; WebFetch 500. |
| CHE | BFS “average prices” page 404 / probe HTML without clear absolute food staple download. |
| DNK | Statbank tables inspected are CPI (`PRIS111` etc.), not absolute retail food levels. |
| EUZ | No euro-area absolute retail staple product prices in open Eurostat bulk (see below). |
| KWT | No open average retail staple bulk found. |
| NOR | SSB dataset probes returned 410; no absolute retail food product table secured. |
| OMN | No open average retail staple bulk found. |
| QAT | No open average retail staple bulk found. |
| TWN | MOA `RicepriceData` / data.moa.gov.tw — **TLS `UNEXPECTED_EOF`** / WebFetch 504; data.gov.tw API 405. |

## Optional (outside gap-16)

| ISO3 | Status |
|------|--------|
| SWE | SCB price tree under PR0101 is CPI/HICP family; no Medelpriser food absolute bulk secured. |
| USA | Skipped — BLS already in main survey. |
| JPN | Skipped — Japan rice absolute already in Aoi/main. |

## Eurostat absolute retail food prices

**Not included — no open absolute LCU retail product table found.**

| Code tried | Result |
|------------|--------|
| `prc_fpmt_m` | **Downloaded** — Food Price Monitoring Tool monthly. Units: `I25`, `RCH_A`, `RCH_M` only (indices & rates for HICP/PPI/ACPI/IPI). Bread/cereals/potatoes COICOP present but **not LCU levels**. |
| `prc_fsc_idx`, `prc_fsc_irt`, `prc_fsc_agg`, `prc_fpmt_a`, `prc_apc_a` | HTTP 404 / error XML on SDMX data API. |
| `prc_hicp_aind` | HICP annual — index / contribution metrics only. |
| `apri_ap` (agri absolute) | Farm-gate absolute prices — **out of scope** (retail required; producer already in Aoi FAOSTAT PP). |
| PPP / PLI food | Comparative price **levels** (index vs EU), not national average retail LCU series in open bulk. |

If Eurostat later publishes product-level average retail prices (EUR or national currency per kg/loaf), they should be added here as `staple_price:*` with pack size in `unit` and Eurostat code in `note`.

## TLS / egress failures to retry later

- `www150.statcan.gc.ca` table 18100245 CSV zip
- `data.moa.gov.tw` RicepriceData CSV
- Internet Archive CDX for ABS 6403 (TLS fail from this box)

## Intentionally not collected

- CPI / HICP / FAO food CPI / ILO food CPI (other adjacent packs)
- Aoi lanes: SOFI/FIES, Asia/Africa NSO CPI, Pink Sheet, CoAHD, producer prices, Japan food service, numeraire batch
- FX conversion, unit homogenization, gap-fill

Probe artifact retained: `raw/eurostat/prc_fpmt_m.tsv.gz` (indices only; not loaded into vertical CSV).
