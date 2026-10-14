# 報告（report）v1

`new_report()` が返す形。採用したものだけでなく、採用しなかったものも返す。

| 項目 | 型 | 約束 |
|---|---|---|
| `records` | list[dict] | 採用した観測。各要素は `key` を持ち、`key` で一意（`merge` は最初のものを残す） |
| `counts` | Counter[str, int] | 採用しなかったものの区分ごとの件数（例: `cancelled`, `non_regular`, `extraction_failed`） |
| `unknown` | list[dict] | どの区分にも当たらなかったもの。各要素は原文 `raw` を持つ。黙って捨てない |

## records の要素

- 必須: `key`
- 推奨: 原文 `raw` と派生値 `derived` を同じ記録に並べる（解釈は入れない）
- 任意（`HtmlSource.parse_snapshot` が付ける）: `url`, `snapshot`, `cache_entry`

## unknown の要素

- 必須: `raw`（原文。抽出に失敗したときは空文字のこともある）
- 任意: `url`, `reason`, `snapshot`

## 集計行（inspect / inspect_snapshots の返り値）

group ごとに1行。

| 項目 | 約束 |
|---|---|
| `group` | 供給元 entry の group |
| `pages` / `empty_pages` | 読んだページ数 / 本文が空（例: 404 を空として保存）だったページ数 |
| `records` | 採用した記録の件数 |
| `n_<区分>` | counts の各区分の件数（区分は増えてよい） |
| `unknown` / `unknown_shapes` | 未知の件数 / 数字を `#` に伏せた形（最大5件） |
