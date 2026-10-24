# missing — adjacent_ilo_october_inquiry

**Status:** complete miss for `staple_price` (absolute LCU retail food).

## Hits

| Country (ISO3) | Years | Staple variables | Rows |
|----------------|-------|------------------|------|
| _(none)_ | — | — | **0** |

## Misses / blockers

1. **ILOSTAT has no absolute retail-food series.** Full indicator TOC (1964) + SDMX dataflows: PRICES database is CPI / FX / PPP / labour cost only.
2. **October Inquiry food prices not on open APIs.** Historical dissemination was LABORSTA interactive + annual CD-ROM (93 items, ~1985–2009). LABORSTA host is gone; UNdata did not keep the absolute retail table; Wayback page bodies could not be fetched from this environment.
3. **No open academic CSV** of the published Inquiry food panel found (Moatsos/de Zwart digitization still “in preparation”; NBER OWW is wages-only).
4. **Indices must not be substituted.** Food CPI already in `adjacent_ilo/`; loading CPI/PPP/PLI as `staple_price` is forbidden.

## Big Mac ISO3 coverage implication

For every Big Mac ISO3 country: **no ILO October Inquiry / ILOSTAT absolute retail staple rows** in this pack. Use national NSOs / prior EUZ proxy / other adjacent level packs instead.

## Next steps if revisiting

- Obtain ILO Library / sales CD-ROM *Occupational wages and hours of work and retail food prices. Statistics from the ILO October Inquiry* (ISBN 978-92-2-022242-0) and extract LCU item prices.
- Watch for Moatsos–de Zwart open release of the digitized Inquiry prices panel.
- Browser + Wayback interactive STP download of archived LABORSTA “02 Retail prices of selected food items” (DEU browser track is separate).
