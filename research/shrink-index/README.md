# Shrink index (cycle 2, idea 2)

Code, observed data and **synthetic** data for the Country Ma'am index: how the total content of a product shrinks, with a danger level that stops before zero. The definition and the rules are in [`SHRINK.md`](SHRINK.md).

| File | Role |
|---|---|
| [`SHRINK.md`](SHRINK.md) | Definition, rules (fixed before results), the synthetic patterns |
| [`shrink_index.py`](shrink_index.py) | Total quantity, level, rate per interval, danger closeness, unit price (standard library only) |
| [`countrymaam_observed_vertical.csv`](countrymaam_observed_vertical.csv) | Observed rows from two media articles, with the source URL in each row |
| [`synthetic_shrink.py`](synthetic_shrink.py) | Eight fictional products with a known truth |
| [`synthetic_shrink_vertical.csv`](synthetic_shrink_vertical.csv) | The generated rows (**SYNTHETIC**) |

```bash
python research/shrink-index/shrink_index.py --product shrink:countrymaam_family_vanilla_cocoa
python research/shrink-index/synthetic_shrink.py --check
```

Tests: `tests/test_shrink_index.py`. This directory records no conclusion: with so few real points the honest statement is that the evidence is not yet enough.

Evidence uses only years with an observed `total_g` or a total derived from observed piece count and observed weight in the same year. `MIN_POINTS = 5`: fewer than five such years is `insufficient`; five or more is `sufficient` for this point-count check, not a research conclusion. Totals calculated with `--assume-weight` remain labelled `ASSUMED` in the output and remain in levels, interval rates, danger, unit prices and explicit WHAT-IF calculations, but never add evidence points. Thus five assumed years alone give `insufficient` (0 observed points), four observed plus one assumed give `insufficient` (4), and five observed plus any assumed years give `sufficient` (5). Observed weights and directly recorded totals take precedence over assumptions. Synthetic results remain checks of fictional data, not evidence about a real product.
