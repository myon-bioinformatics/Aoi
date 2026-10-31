# USDA FAS PSD — rice (milled) & wheat production / ending stocks

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi origin companion batch

## What
Annual **Production** and **Ending Stocks** from the USDA Foreign Agricultural Service **PSD Online** bulk CSV for:

- **Rice, Milled**
- **Wheat**

Country rows with a resolvable ISO3 (plus a few published EU aggregates as `EUE` / `EU15` when names resolve). Values keep published units (typically **1000 MT**). `year` = PSD `Market_Year` (marketing year, not necessarily calendar year).

**Note:** This `psd_alldata_csv.zip` release does **not** include a World aggregate country row — use country sums only if you deliberately construct them; this panel does not invent a WLD total.

## Files
- Panel: `usda_psd_grains_panel.csv` (**29,790** rows; **147** ISO3; years **1960–2026**)
- Raw: `raw/usda_psd/psd_alldata_csv.zip` ← `https://apps.fas.usda.gov/psdonline/downloads/psd_alldata_csv.zip`

## Variables
| variable | coverage (approx) |
|---|---|
| `usda_psd_rice_milled_production` | 129 ISO3 · 1960–2026 |
| `usda_psd_rice_milled_ending_stocks` | 129 ISO3 · 1960–2026 |
| `usda_psd_wheat_production` | 137 ISO3 · 1960–2026 |
| `usda_psd_wheat_ending_stocks` | 137 ISO3 · 1960–2026 |

## Notes
- No FX. No fills. Recent market years may include forecasts (as in PSD).
- Not Season2-owned. Distinct from FAOSTAT producer prices and Pink Sheet international prices.
