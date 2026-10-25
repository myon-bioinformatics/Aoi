# URY INE ENGIH 2016-2017 — food share by income decile

Source (fetched 2026-10-25 Asia/Tokyo):
https://www5.ine.gub.uy/documents/Demograf%C3%ADayEESS/PDF/ENGIH/Principales%20Resultados%20de%20la%20Encuesta%20Nacional%20de%20Gastos%20e%20Ingresos%20de%20los%20Hogares%20(2016-2017).pdf

## Loaded — Cuadro 31

Estructura del gasto de consumo **con valor locativo** por **deciles del ingreso per cápita con valor locativo**, CCIF, precios corrientes 2016-2017:

| | Total | d1 | d2 | d3 | d4 | d5 | d6 | d7 | d8 | d9 | d10 |
|--|------:|---:|---:|---:|---:|---:|---:|---:|---:|---:|----:|
| Alimentos y bebidas no alcohólicas | 18.5 | 26.0 | 24.4 | 23.4 | 21.1 | 20.1 | 19.1 | 18.2 | 17.1 | 15.2 | 12.8 |

- Variables: `engel_share:food_d1` … `food_d10`
- Year = survey end → **2017**
- Distinct from existing CEPALSTAT 5725 quintiles labeled year 2016 (different grain + denom methodology)

## Not loaded

- Cuadro 27/28 area splits → urban/rural pack
- Cuadro 39 food+alcohol+away historical series
