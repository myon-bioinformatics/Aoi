# Apple Mac — multi-country absolute prices

Date: **2026-10-25 Asia/Tokyo**. Easy open paths only. Companion to iPhone numéraire work.

## Why

User asked whether **iMac / Mac mini / MacBook** are similarly stable across countries (Big Mac–style substitutes). Absolute multi-country panels + quick USD CVs.

## Panels landed

| File | Rows | ISO3 | Products | Obs | USD |
|---|---:|---:|---|---|---|
| `mac_zenodo_aos_2022_panel.csv` | 216 | 36 | Air M1/M2, Pro 13/14/16, iMac 24 | 2022-11-20 | Zenodo bundled FX |
| `mac_paulcollas_aos_panel.csv` | 48 | 24 | MacBook Air, iMac 24 | ~2021–2022 | repo bundled FX |

## Dispersion (USD CV)

| Series | n | mean USD | CV |
|---|---:|---:|---:|
| Zenodo MacBook Air M1 | 35 | ~1195 | **0.171** |
| Zenodo MacBook Air M2 | 35 | ~1642 | 0.165 |
| Zenodo MacBook Pro 14-inch | 35 | ~2589 | 0.173 |
| Zenodo MacBook Pro 16-inch | 35 | ~3094 | 0.169 |
| Zenodo iMac 24-inch | 35 | ~1709 | 0.166 |
| PaulCollas MacBook Air | 24 | ~1244 | **0.092** |
| PaulCollas iMac 24-inch | 24 | ~1603 | 0.093 |

### Read vs iPhone / Big Mac screens

- Zenodo Mac CVs (~0.16–0.17) sit **near iPhone 15 Burger Parity (~0.19)** and **above** Zenodo iPhone 14 128GB (~0.15) and DB iPhone 7 (~0.09).
- Still usable as branded durable absolutes; not clearly *more* stable than recent iPhones in the Zenodo vintage.
- PaulCollas subset looks tighter (0.09) but on a smaller/easier country set — treat as supportive, not definitive.

## Mac mini

**Not landed.** Zenodo `category=mac` had no Mac mini / Studio rows. World Price Index tracks Mac mini in 40 markets but requires API key — skipped this pass. EveryMac launch MSRP is HTML multi-page — skipped.

## Sources

1. Zenodo DOI [10.5281/zenodo.7344067](https://doi.org/10.5281/zenodo.7344067) — same package as iPhone 14 panel.
2. [PaulCollas/apache-spark](https://github.com/PaulCollas/apache-spark) `ApplePrices.csv` + `CurrencyConversion.csv`.

## SKIP

| Item | Why |
|---|---|
| World Price Index `/v1/apple` | API key / signup |
| restockowl `apple-prices-by-country.csv` | Ratios only, not absolute prices |
| EveryMac global Mac MSRP index | HTML grind |
| Invented FX / archive.org digs | Policy |
