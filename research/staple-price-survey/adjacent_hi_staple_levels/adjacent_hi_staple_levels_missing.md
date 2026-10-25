# adjacent_hi_staple_levels — missing / blocked

Retrieved: 2026-10-24 Asia/Tokyo

## Active lane (this bot): ARE, BHR, KWT, OMN, QAT, TWN, EUZ

| ISO3 | Status |
|------|--------|
| **QAT** | **CLOSED** — NPC annual average consumer prices (selected commodities) via data.gov.qa; 48 rows / 7 series (bread 700 g, Lebanese bread 5 pcs, wheat flour ×2, rice 5 kg ×2, potato kg), 2017–2023. |
| **TWN** | **CLOSED** — NDC e-invoice midpoints (rice 3 kg, wheat flour kg, white toast) + Taipei potato 元/台斤. MOA `RicepriceData` still TLS `UNEXPECTED_EOF` (not required for close). |
| ARE | **Exhausted.** FCSC prices pages 403 from box. MOET Essential Goods Prices Platform reachable only via Brainy `official_shop_prices` with `license_id=source_terms_unconfirmed` / “no bulk redistribution” — **not loaded**. Dubai Pulse commodity series is financial-market, not grocery retail. |
| BHR | **Exhausted.** data.gov.bh catalog + `search(default,"average"|"retail"|"price"|"consumer price")` — CPI index datasets and unrelated averages only; no absolute staple retail bulk. |
| KWT | **Exhausted.** CSB CPI downloads only; `cprice.csb.gov.kw` is login/session consumer-price system, not open bulk. GCC-Stat `DF_ES_CPI` is CPI. |
| OMN | **Exhausted.** data.gov.om Price Index / CPI base-2018 datasets only; no open average retail staple CSV/API secured (search API 403). |
| EUZ | **Exhausted.** Eurostat open bulk has no ongoing absolute LCU/EUR retail staple product table (`prc_fpmt_m` indices/rates only; `prc_dap*` historical one-off not loaded; `apri_ap` farm-gate out of scope). |

## Kept from earlier (not in active-7, already in pack)

HKG, MYS, NZL, SGP — unchanged; still in vertical CSV.

## Handed to Aoi lane `hi_staple_levels_alt` (do not pursue here)

| ISO3 | Prior probe note (for Aoi) |
|------|----------------------------|
| AUS | ABS Average Retail Prices (6403.0.55.001) discontinued 2011; Wayback/TLS issues from this box. |
| CAN | StatsCan **18-10-0245** TLS `UNEXPECTED_EOF`; open.canada.ca empty/non-JSON. |
| CHE | BFS average-prices probe without clear absolute food staple download. |
| DNK | Statbank tables inspected are CPI, not absolute retail food levels. |
| NOR | SSB probes returned 410; no absolute retail food product table secured. |

## Optional (outside gap-16)

| ISO3 | Status |
|------|--------|
| SWE | SCB price tree under PR0101 is CPI/HICP family; no Medelpriser food absolute bulk secured. |
| USA | Skipped — BLS already in main survey. |
| JPN | Skipped — Japan rice absolute already in Aoi/main. |

## Eurostat absolute retail food prices

**Not included — no open absolute LCU retail product table found for EUZ.**

| Code tried | Result |
|------------|--------|
| `prc_fpmt_m` | Downloaded — units `I25`, `RCH_A`, `RCH_M` only (indices & rates). |
| `prc_fsc_*`, `prc_fpmt_a`, `prc_apc_a` | HTTP 404 / error XML on SDMX data API. |
| `prc_hicp_aind` | HICP annual — index / contribution metrics only. |
| `prc_dap*` (Detailed Average Prices) | Historical one-off (~2008–2015); not ongoing EA series; not loaded. |
| `apri_ap` | Farm-gate absolute — out of scope. |
| PPP / PLI food | Comparative levels (index vs EU), not national average retail LCU. |

## TLS / egress failures retained for later

- `www150.statcan.gc.ca` table 18100245 CSV zip (Aoi lane)
- `data.moa.gov.tw` RicepriceData CSV (TWN closed via NDC/Taipei instead)
- Internet Archive CDX for ABS 6403 (Aoi lane)
- `fcsc.gov.ae` prices pages (403)

## Intentionally not collected

- CPI / HICP / FAO food CPI / ILO food CPI (other adjacent packs)
- Brainy/MOET ARE bulk (license unconfirmed; no redistribution)
- Aoi lanes: SOFI/FIES, Asia/Africa NSO CPI, Pink Sheet, CoAHD, producer prices, Japan food service, numeraire batch, `hi_staple_levels_alt`
- FX conversion, unit homogenization, gap-fill

Probe artifacts: `raw/eurostat/prc_fpmt_m.tsv.gz` (indices only); `raw/gcc/` (Qatar CSV + BHR/ARE probes).
