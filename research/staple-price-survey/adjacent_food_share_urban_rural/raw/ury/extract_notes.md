# URY INE ENGIH 2016-2017 — Montevideo / Interior food Engel

Source (fetched 2026-10-25 Asia/Tokyo):
https://www5.ine.gub.uy/documents/Demograf%C3%ADayEESS/PDF/ENGIH/Principales%20Resultados%20de%20la%20Encuesta%20Nacional%20de%20Gastos%20e%20Ingresos%20de%20los%20Hogares%20(2016-2017).pdf
(Principales Resultados ENGIH 2016-2017; ~1 MB PDF kept locally under workspace raw/ury, not committed)

## Loaded — Cuadro 27 (con valor locativo)

Estructura del gasto de consumo de los hogares **con valor locativo** por área geográfica, CCIF, precios corrientes 2016-2017:

| División | Total | Montevideo | Interior |
|--|------:|----------:|---------:|
| Alimentos y bebidas no alcohólicas | 18.5 | **16.6** | **20.4** |

- `engel_share:food_urban` ← Montevideo 16.6%
- `engel_share:food_rural` ← Interior del país 20.4% (INE area split; Interior mixes interior urbano + rural — pure rural not published separately in this cuadro)
- Year = survey end → **2017**
- Denominator includes imputed rent (valor locativo); Food = CCIF 01 only (alcohol/tobacco and Restaurantes y hoteles separate)

## Not loaded

- Cuadro 28 sin valor locativo (22.5 / 20.4 / 24.4) — alternate denom; prefer con VL as standard consumption structure.
- Cuadro 39 historical Montevideo vs Interior urbano (1971–2017) — food **plus** alcohol **plus** meals away; not COICOP-01 Engel.
- Cuadro 31 national deciles → food×income pack (separate).

El Observador secondary (MVD 16.6 / Interior 20.4) matches Cuadro 27 primary.
