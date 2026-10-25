# Big Mac ruler (cycle 2)

Code for reading a staple price as a multiple of the Big Mac price (`b`, local currency only, no exchange rate), and synthetic staples for preparing propositions.

Observed data stays in [`../staple-price-survey/`](../staple-price-survey/) (data only). This directory holds code and **synthetic** data, kept apart so that observed and generated records are never mixed (`docs/data-policy.md`).

| File | Role |
|---|---|
| [`staple_bigmac_check.py`](staple_bigmac_check.py) | Builds a country x year panel for one commodity (per-kg unit, no conversion) and fits `log b = a + beta*log E + gamma*log M` with a country-level bootstrap |
| [`synthetic_staples.py`](synthetic_staples.py) | Generates fictional staples with a known truth and checks that the fit recovers it |
| [`SYNTHETIC.md`](SYNTHETIC.md) | The generation rules, fixed before results are read |
| [`synthetic_staples_vertical.csv`](synthetic_staples_vertical.csv) | The generated rows (**SYNTHETIC**) |

```bash
python research/bigmac-ruler/staple_bigmac_check.py --prefix staple_price:rice
python research/bigmac-ruler/staple_bigmac_check.py --prefix staple_price:wheat_flour --exclude-inflation 2.0
python research/bigmac-ruler/synthetic_staples.py --check
```

The default input is `research/staple-price-survey/staple_survey_vertical.csv` (from PR #118). Tests: `tests/test_bigmac_ruler.py`.

## Zero / NaN log

`staple_bigmac_check.py` always prints `[zero/NaN log]` lines, once for loading (`load`) and once for the computed results (`compute`), and prints `none` when nothing happened. Values are never changed and nothing is replaced by an epsilon (how to place epsilon is decided separately).

| Kind | Meaning |
|---|---|
| `ZERO` / `NaN` / `INF` | Recorded; the value is used as it is |
| `BLANK` | Not readable as a number; the row is not used (before, such a row stopped the run) |
| `SKIPPED` | Not computed because of a zero (the Big Mac ratio when either year is 0; before, silently `None`) |
| `DROPPED` | A bootstrap draw that failed (before, silently discarded) |

On the observed survey, the load log shows 12 zero rows of `household_consumption_total_lcu` (VEN, 2000-2011), outside the 2021-2025 panel.

This directory records no results. The numbers are a provisional reading, not a verdict: with few points, the honest statement is that the evidence is not yet enough.
