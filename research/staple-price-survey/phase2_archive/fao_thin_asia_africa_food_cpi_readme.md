# FAOSTAT monthly Food CPI — thin Asia / Africa companion

## Panel
- File: `fao_thin_asia_africa_food_cpi_panel.csv`
- Rows: 5,088
- ISO3 (16): BGD, CIV, CMR, ETH, GHA, KHM, LAO, LKA, MMR, MNG, MOZ, NPL, PAK, SEN, TZA, UGA
- Span: 2000-01-01 → 2026-06-01 (monthly)
- Series: Food Indices (2015=100), FAOSTAT domain CP

## Coverage by country
iso3                          country   n  ymin  ymax       dmin       dmax
 BGD                       Bangladesh 318  2000  2026 2000-01-01 2026-06-01
 CIV                    Côte d'Ivoire 318  2000  2026 2000-01-01 2026-06-01
 CMR                         Cameroon 318  2000  2026 2000-01-01 2026-06-01
 ETH                         Ethiopia 318  2000  2026 2000-01-01 2026-06-01
 GHA                            Ghana 318  2000  2026 2000-01-01 2026-06-01
 KHM                         Cambodia 318  2000  2026 2000-01-01 2026-06-01
 LAO Lao People's Democratic Republic 318  2000  2026 2000-01-01 2026-06-01
 LKA                        Sri Lanka 318  2000  2026 2000-01-01 2026-06-01
 MMR                          Myanmar 318  2000  2026 2000-01-01 2026-06-01
 MNG                         Mongolia 318  2000  2026 2000-01-01 2026-06-01
 MOZ                       Mozambique 318  2000  2026 2000-01-01 2026-06-01
 NPL                            Nepal 318  2000  2026 2000-01-01 2026-06-01
 PAK                         Pakistan 318  2000  2026 2000-01-01 2026-06-01
 SEN                          Senegal 318  2000  2026 2000-01-01 2026-06-01
 TZA      United Republic of Tanzania 318  2000  2026 2000-01-01 2026-06-01
 UGA                           Uganda 318  2000  2026 2000-01-01 2026-06-01

## Source
- FAOSTAT Consumer Price Indices bulk (Normalized): https://fenixservices.fao.org/faostat/static/bulkdownloads/ConsumerPriceIndices_E_All_Data_(Normalized).zip
- Portal: https://www.fao.org/faostat/en/#data/CP
- Local raw (reused from prior Asia subgroup download): `raw/asia_food_subgroups/idn_bps/fao_cpi/ConsumerPriceIndices_E_All_Data_(Normalized).csv`
- Retrieved (this tidy): 2026-10-24

## Non-overlap / lane notes
- Explicitly **excludes** ISO3 already tidied in:
  - `asia_national_food_cpi_panel.csv` (IDN IND KOR MYS PHL THA VNM)
  - `africa_mena_national_food_cpi_panel.csv` (EGY ISR KEN MAR NGA SAU TUN TUR ZAF)
  - China / HKG / MAC / SGP packs
  - `fao_idn_phl_vnm_food_cpi_panel.csv` (IDN PHL VNM monthly)
- Non-exclusive companion extract from the same open bulk already on disk. Season2 owns FAO country CPI *bulk* lane — this is a narrow documented Aoi companion, not a bulk rebuild.
- No COICOP mid-tree subgroups (Food Indices aggregate only). No FX. No fabrication.

## Skips this turn (related)
- Canada SHS via open.canada: WAF “Request Rejected” (same class as prior 502); www150 avoided per rules; OECD food-share left to Season2.
