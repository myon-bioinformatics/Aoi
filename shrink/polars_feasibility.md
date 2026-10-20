# DRAgoWing は標準ライブラリだけで動くか（polars）

結論: `dragowing.overlap.load_overlap` は、numpy を `shrink/numpy_min.py`、polars を `shrink/polars_min.py` に差し替えれば、c001 の `season.jsonl` で本物と同じ JSON になる。DRAgoWing 全体を標準ライブラリだけにするのは、この面では足りない。

本番の依存とパイプラインは変えていない。差し替えは実験のランナーが `import` より前に行う。

## 調べ方

`scripts/shrink_module.py` の ast は `pl.名前` しか数えない。`dragowing/` では次だけである。

- `dragowing/overlap.py`: `read_ndjson` が 1 回
- `dragowing/tests/test_figures.py`: `read_ndjson` が 1 回（マスクの再計算）
- `dragowing/tests/test_forms_review.py`: `DataFrame` が 1 回（`propositions.evaluate` に渡す）

リポジトリ全体では 25 名前・933 回で、そのうち `sakanalytics/sakanalytics.py` が 23 名前・586 回ある。`load_overlap` だけをたどると `read_ndjson` と注釈の `DataFrame` しか出ない。`_mask` は `from propositions import _cond` なので、ast は `_cond` に入らない。

実行して足した。

- `trace` は本物の polars のメソッドを包み、c001 の `load_overlap` を動かす。ast が見逃したのは `DataFrame.height`、`DataFrame.columns`、`DataFrame.__getitem__`、`DataFrame.select`、`Series.to_list`、`Expr.__gt__`、`Expr.__le__`、`Expr.__eq__`。
- `absent` は polars を置かず、`AttributeError` の名前だけ足して同じ呼び出しをやり直す。11 回で通り、上と同じ名前に `polars.col` と `polars.lit` を足した集合になる。最初の失敗は `dragowing/overlap.py:121` の `polars.read_ndjson`。`&` は c001 では出ない（条件を 1 個ずつ `_mask` に渡すため）。

c001 が踏む面は `read_ndjson`、`height`、`columns`、列の `[]`、`Series.to_list`、`select` のキーワード引数、`col`、`lit`、`>`、`<=`、`==`。`_cond` の演算子（6 個と、条件が複数のときの `&`）は同じファイルに入れ、同値テストで本物の polars と比べる。c001 の実行では `&` は使わない。

## 一致

`shrink/polars_min.py` は標準ライブラリだけである。c001 の 168 行・286 列は、列名ごとの `to_list()` が polars 2.0.0 と一致する。列の順番は、小さいファイルでは最初に見た順で polars と一致し、c001 では polars 側がファイル順ではない。`load_overlap` は列があるかどうかしか見ない。null は比較の結果も null にする。bool と文字列は polars と同じく `"true"` / `"false"` にして比べ、数値と文字列は両方ともエラーにする。

`shrink/run_overlap_stdlib.py --deps real` と、numpy も polars も入れずに `--deps min` で動かした結果は同じバイト列である。sha256 は `12037df38eb301300768e0ef172e2e16e8e956dc7669aa08fd355414b7619e35`（領域 8）。numpy だけの実験（`shrink/run_overlap.py`）と同じ値である。CI は `.github/workflows/shrink-polars-experiment.yml` の 1 ジョブで、本物の実行、numpy・polars・compiled の `polars-runtime-32` を外した再インストール、最小版の実行、`cmp` まで行う。`polars` だけを外すと lock が runtime wheel を残すので、それも `--no-install-package` に入れる。

## 呼び出し側は min を使えるか

使えるのは、本物の `import polars` より前にこのファイルを `polars` という名前で載せる呼び出し側だけである。`shrink/run_overlap_stdlib.py` がそれをする。`dragowing/overlap.py` の `import polars` は変えていない。

`dist/dragowing_min.py` は minpy が束ねた別物である。ヘッダの `allow` は空で、`scripts/build_distributions.py` は stdlib 以外を拒む。中にあるのは `dragowing_api`、`plot_specs`、`records`、`research_report` で、`overlap` も `polars` も `load_overlap` も無い。この束ねの呼び出し側は polars を要求しないので、`polars_min` を渡す口が無い。`overlap.py` はモジュール先頭で numpy を import するため、今の minpy の契約のまま束ねに入れることもできない。配布のピンや `dist/` は変えていない。

## できないこと

- **DRAgoWing の HTML まで標準ライブラリだけにすること。** ページの文章は markdown のままである。PNG / SVG は Chrome が要る。今回外すのは polars と、load_overlap が使う numpy だけである。
- **polars の wheel を fetch_module で動かすこと。** PyPI の `polars` 2.0.0 は `py3-none-any` だが、実行時に compiled の `polars-runtime-32` を要求する。`scripts/fetch_module.py` は extra 以外の依存を拒み、依存は解決しない。runtime の wheel は pure-Python ではない。
- **`propositions.evaluate`（`dragowing/tests/test_forms_review.py`）。** 空の scope でも `_forms` が `~` をすぐ呼ぶ。`polars_min` はそこで `NotImplementedError` にする。その先には `filter`、`drop_nulls`、`Series.sum` / `mean`、`|`、`is_null`、`is_between`、`cast`、`concat_str`、`is_in`、`iter_rows` がある。load_overlap はこれらを使わない。
- **リポジトリの他の polars。** `pythdragoras.py` の join や `sakanalytics.py` の `when` / 横方向の集計は、この表に無い。名前が解析に増えると `generate` は失敗する。
- **入れ子の値、空ファイルの型推論、定数 null 同士の `&`。** 入れ子は `NotImplementedError`（polars は Struct / List にする）。空の NDJSON は両方とも失敗する。`lit(None) & lit(None)` は polars が null 型の bitand を拒み、`polars_min` は 1 行の null を返す。load_overlap は通らない。
- **大きな NDJSON の列順を polars と揃えること。** 値は揃う。順番に依存する呼び出し側はこの最小版では動かない。`load_overlap` は依存しない。
