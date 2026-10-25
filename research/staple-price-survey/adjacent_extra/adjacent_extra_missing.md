# adjacent_extra — gaps / missing

Retrieved: 2026-10-24 Asia/Tokyo

## Deferred (not collected here)

- FAO CoAHD / Food Prices for Nutrition — Aoi lane
- FAOSTAT producer prices — Aoi lane
- Japan CPI food/cereals — Aoi lane
- FAO CPI food/cereals bulk — other executor (adjacent/)

## High-income Big Mac gap countries — food CPI

Present: ARE, AUS, BHR, CAN, CHE, DNK, EUZ, HKG, KWT, MYS, NOR, NZL, OMN, QAT, SGP, TWN

Missing food CPI: (none)

## LatAm targets — food CPI

Present: ARG, BRA, CHL, COL, CRI, MEX

Missing food CPI: GTM, HND, NIC, PER, URY

## Bread & cereals / rice component coverage

Countries with bread/cereals or rice CPI: ARG, CHE, CZE, DNK, EUZ, GBR, HKG, HUN, MYS, NOR, POL, ROU, SGP, SWE, TWN

Notable thin spots:
- GCC-Stat: food only (no CP0111 bread/cereals breakout in DF_ES_CPI)
- OECD COICOP 1999 feed: CP01 food only (CP0111 not returned for queried countries)
- GTM, HND, NIC, PER, URY: no open bulk NSO food CPI pulled this pass
- BRA: OECD food CPI annual/monthly available but annual series ends 2018 in OECD extract; no IBGE índice level for food subgroup (SIDRA 7060 exposes variation/weights, not número-índice by group)
- ARG: GBA regional only
- NZL: OECD annual food present; monthly CP01 not in OECD monthly extract

## Rebuild

```bash
python3 /workspace/staple-price-survey/adjacent_extra/build_adjacent_extra.py
```
