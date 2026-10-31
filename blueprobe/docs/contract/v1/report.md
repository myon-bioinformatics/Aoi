# Report v1

The shape returned by `new_report()`. It returns not only what was accepted but also what wasn't.

| Item | Type | Promise |
|---|---|---|
| `records` | list[dict] | Accepted observations. Each element has `key` and is unique by `key` (`merge` keeps the first) |
| `counts` | Counter[str, int] | Counts per category of what was not accepted (e.g. `cancelled`, `non_regular`, `extraction_failed`) |
| `unknown` | list[dict] | Things that matched no category. Each element has the source text `raw`. Never silently discarded |

## Elements of records

- Required: `key`
- Recommended: put the source text `raw` and derived values `derived` side by side in the same record (no interpretation)
- Optional (added by `HtmlSource.parse_snapshot`): `url`, `snapshot`, `cache_entry`

## Elements of unknown

- Required: `raw` (source text; may be an empty string when extraction failed)
- Optional: `url`, `reason`, `snapshot`

## Summary rows (return value of inspect / inspect_snapshots)

One row per group.

| Item | Promise |
|---|---|
| `group` | The supplier entry's group |
| `pages` / `empty_pages` | Pages read / pages whose body was empty (e.g. a 404 saved as empty) |
| `records` | Number of accepted records |
| `n_<category>` | Count for each category in counts (categories may be added) |
| `unknown` / `unknown_shapes` | Unknown count / shapes with digits masked as `#` (up to 5) |
