# Trajectories, team × year, condition overlap, and the list of propositions

`python -m dragowing` reads only the JSONL already in `cycles/c001-chunichi/outputs`. It does not fetch NPB data. It does not call the judge (`evaluate`). It does not round numbers into bins. It draws no regression, smoothing, or fitted lines.

```bash
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --id P1
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --column wins_vs_pythag
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --cond 'rd,>,0' --cond 'rank_ra,<=,2'
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --embed
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --team-order d,g,s   # top-to-bottom order of team × year; symbol order if omitted
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --png --svg
```

`--cond` values are JSON (`0`, `true`, `"d"`). If omitted, it looks at the `if` of `propositions.jsonl` in file order, takes 2 atoms on columns present in `season.jsonl`, and adds the B class (`upper_half == false`). That gives 2 or 3 sets.

By default, `index.html` loads Plotly.js from jsDelivr (`https://cdn.jsdelivr.net/npm/plotly.js-dist-min/plotly.min.js`, no SRI). `propositions.html` does not load Plotly. `plotly.min.js` is not copied to the output directory. The Python package `plotly` is not a dependency.

With `--embed`, Plotly.js is embedded into `index.html`. `propositions.html` is not embedded.

| File | Contents |
|---|---|
| `index.html` | Trajectories, team × year, and the table of condition-overlap counts and units |
| `propositions.html` | The list at the top, and per-proposition 2×2, logic notation, and counterexample tables |

Page headings, the list, the 2×2, counterexample tables, and the logic-notation box are written in Markdown and converted to HTML with Python-Markdown. Numbers stay exactly as in the files after conversion; they are not rounded.

The text-only 2×2 remains `dragowing/forms.py` in [forms.md](forms.md).

Add `--png` / `--svg` only when PNG / SVG is needed. Chrome is needed only then too (`--chrome` or the `CHROME` environment variable). Without Chrome, the HTML is written and the exit code is 2. The tests do not use Chrome either.

`sets.jsonl` is not in these results. The Hasse diagram of condition formulas (proposal C6) is not produced. Hold rates are not newly computed here for coloring.

The distribution contract shares web-ui's single file, pinned in `vendor.lock.json` by exact commit and
file hash. Version, URL, expected SHA-256, SRI, the 8 MiB limit,
and fetching and verification are managed there; DRAgoWing does not define them again.
`--embed` hash-checks the bytes from the fixed URL, converts them to UTF-8,
checks for HTML raw-text terminators, and then embeds them. HTTP errors, fetch failures, oversize,
CDN content mismatch, and tampering stop with an error, and only successful bytes are kept in an in-process cache.
Version updates are done as a pair: the upstream contract update and the lock update.

web-ui's `remote_scripts` / `remote_script_tag` / `fetch_plotly_js` are shared.
Since `plotly_figure` returns a `ui-panel` with inline initialization, the existing
`application/json` figure blocks, IDs, CSS, and DRAgoWing initialization are kept.
The PNG/SVG API and CLI `--png` copy Plotly.js under the same CDN contract as `export_draw` into a temporary directory and use it.

## Observation

The figures show only the record's column names and values, plus the following display rules.

### The list, the four forms (proposal C1), notation (C2), counterexample tables (C7), and one page (C8)

The top of `propositions.html` is a list. One row is one proposition, with its ID, `statement`, the `hold` of each of the four forms, counterexamples (`n - hold`), and `rate`. The ID links to its section on the same page. `rate` is shown as in the file; it is not recomputed here. When a form is missing, or the count can't be determined from `n` and `hold`, it is `不明` (unknown).

Below that is one section per proposition. The marker in the section heading is one of the same three values as `registration_status`.

| Record | Display |
|---|---|
| `posthoc` is true | 事後構成 (post-hoc) |
| `preregistered` is true, or there is a preregistration record | 事前登録 (preregistered) |
| Otherwise | 不明 (unknown) |

2×2 cells are counted from `n` and `hold`, as in [forms.md](forms.md). They are rendered as a Markdown table, not a Plotly table. A cell where two forms disagree is `不一致` (mismatch). A cell that is empty and undetermined is `不明`. The four forms are another 2×2, showing `hold/n（反例 n-hold）` (counterexamples n-hold) and, when the record has `rate`, that number. `rate` is shown as in the file, not as a percentage.

The logic-notation line is the `render_logic` string. `>` is not rewritten as `<=`.

Counterexamples get one table per form, with one row per element of `counterexamples`. If the original and contrapositive, or the converse and inverse, list the same units, they are merged into one table and the text says so. Only when the lists differ are both shown, with `不一致` in the heading. Tables are inside `<details>`, collapsed initially. Order is the record's order: descending `|surprise|`, ties by `season`, then `team`. The row count is the array length. The counterexample count in the 2×2 is `n - hold`. Columns are the record's `unit`, `season`, `team`, `team_name`, `focus`, `surprise`, `question`, `values`, and `context`. `excluded_counterexamples` and `held_out` go in separate sections with the same columns. The 0 placed in the ¬P row for an empty antecedent is written `0（前件が空）` (antecedent empty). `values` and `context` are shown as JSON text.

When `statement` is shown in a section, it is placed as the record's sentence with the field name `statement:`.

### Trajectories (proposal C3)

Each row of `season.jsonl` becomes one point. Horizontal is `rank_rf` (runs-scored rank), vertical is `rank_ra` (runs-allowed rank). Values are the record's integers, and 1 is on the origin side of each axis.

Point color is `upper_half`. `true` is written A, `false` B. `null` is not made B.

Lines connect rows with the same `league` and `team` in ascending `season`. No new values are placed between points. Lines are only straight segments.

Panels are per record `league` (C and P in these results). Ranks are within a league, so the panels are separate.

### Team × year (proposal C4)

The figure title is "球団 × 年" (team × year). Row labels are only the `team` symbols (`d`, `g`, `s`, `db`, `t`, `c`, `h`, `f`, `b`, `e`, `l`, `m`). Team names are not written on the axis. From the top in this order, Chunichi `d` is the top row. Symbols not in this order follow in symbol order. When the same symbol is in two leagues, it becomes `league:team` and the rows stay separate. Columns are ascending `season`. The default column is `wins_vs_pythag`. `--column` switches to a column present as a number (or null) in every row. String columns are rejected.

Color is the cell's column value (not `sigma_band`). `zmin` and `zmax` are placed near the figure. The only text in a cell is a single `A` or `B`: `upper_half == true` is A, `false` is B. Null cells get no text. Numbers are not written in cells. Cells with no row stay null, not 0.

The hover shows `team`, `team_name`, `season`, `class` (A or B), `rank` (when the row has the column), and the column's value. Values and `rank` are the record's numbers. The field name `upper_half` is not shown in the hover.

### Condition overlap (proposal C5)

For each condition, a bit matrix is built with `_mask` and `_masks_to_matrix` from `pythdragoras/rule_search.py`. Counts are integers from counting regions (combinations of in / not in) in that bool matrix. Comparisons with null do not count as true, just as `_mask` does not set bits for null.

No circles are drawn. Counts are the integers in the region table. The `unit` in the table below is `team-season` (e.g. `d-2012`), and `team_name` and the condition columns' values come from that row of `season.jsonl`.

B is the display name of the set `upper_half == false`.

## Interpretation

This page moves stored numbers and strings into cells, points, and tables.

A large 2×2 count is not read as meaning the proposition is true or will hold next year. `不明` does not mean "it was not preregistered"; it means there is no machine-readable record. See the interpretation in [forms.md](forms.md) for details.

Trajectory lines connect the recorded points in order. Slopes are not read as trends or predictions. A and B are display names of `upper_half`, not an explanation of why the points are colored.

The `wins_vs_pythag` color just makes the size of the number easier to see. Positive or negative is not read as a judgment of winning record or failure. A and B in cells are class display names. The hover's `rank` is the recorded rank; this page does not recompute ranks.

The overlap table counts where the chosen condition formulas were true at the same time in the records. It does not indicate that a formula was adopted or is the rule to use next.

`question` in counterexample tables is the stored question text. This page does not answer that question.

Candidate IDs (`もしかして`, "did you mean") are not shown. For the query side, see [ask.md](../../queryu/docs/ask.md).
