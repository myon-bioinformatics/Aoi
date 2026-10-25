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
| `ZERO` / `NaN` / `INF` | Recorded; the value is kept as it is (the `load` log) |
| `BLANK` | Not readable as a number; the row is not used (before, such a row stopped the run) |
| `SKIPPED` | Not used, and said so: an input that is 0, negative, NaN or inf in the analysis years (`input.<name>`), a panel row whose division collapsed to 0 / inf / NaN (`panel.<name>`), or a Big Mac ratio with a 0 year (before, silently `None`) |
| `DROPPED` | A bootstrap draw that failed (before, silently discarded) |

**Pre-check.** Before anything is divided, logged or regressed, `precheck` drops the inputs that cannot be used (`staple_bigmac_check.py` never lets a 0 / NaN / inf reach a division or the fit). It looks only at what the analysis would use (years 2021-2025, the chosen commodity, per-kg rows), keeps the values it does not drop unchanged, never replaces a value by an epsilon, and always logs what it dropped:

| Input (analysis years) | When unusable (0, negative, NaN, inf) |
|---|---|
| a monthly staple price | that month is not used (the year is still built if 6 months remain) |
| a Big Mac price | the whole year is not used if either of its 2 points is unusable (no mean of 0 and 100) |
| `E`, household consumption, population | that country-year is not used |
| a derived value (`C_pc`, `b`, `M`, `k`) that becomes 0 / inf / NaN | that panel row is not used (`unusable_derived:<country>`) |

Exit codes follow `docs/propositions.md`: `0` ran; `65` the data could not be computed even after the pre-check (the compute log and the reason are printed first); `66` the panel is empty (the log shows why). If no bootstrap draw succeeds the intervals are `NaN` and `DROPPED` is logged.

## Series identity

One series is `(country, variable, unit, source, note)`; `note` carries the market, price type and commodity variety. The 6-month minimum is counted inside one series, so 3 months of one market and 3 months of another are not a 6-month year, and two markets are never averaged. One series is used per country: the most years, then the most rows, then (a tie) the larger series text; ties are reported as `series_tie_broken_by_text:<country>` and the unused series as `other_series_not_used`. A date that appears twice inside one series counts as one month (their mean).

On the observed survey, the load log shows 12 zero rows of `household_consumption_total_lcu` (VEN, 2000-2011), outside the 2021-2025 panel.

This directory records no results. The numbers are a provisional reading, not a verdict: with few points, the honest statement is that the evidence is not yet enough.
