# load_overlap の明示的な軽量経路

`load_overlap(path, conds)` は従来どおり NumPy・Polars と PythDRagoras の
`rule_search` を使う。`load_overlap(path, conds, backend="stdlib")` のときだけ、
専用の行評価で同じ形式の dict を返す。CLI は `--overlap-backend stdlib`。
未指定は `native`、未知の backend はエラー。未対応入力を native に黙って戻さない。

```python
from pathlib import Path
from dragowing.overlap import default_conditions, load_overlap
from dragowing.records import read_jsonl

results = Path("cycles/c001-chunichi/outputs")
conditions = default_conditions(read_jsonl(results / "propositions.jsonl"),
                                read_jsonl(results / "season.jsonl"))
result = load_overlap(results / "season.jsonl", conditions, backend="stdlib")
```

```sh
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --overlap-backend stdlib
```

NumPy・Polars がインストール済みでも未導入でも使える。モジュールの import 時には
それらを読み込まず、native を呼んだときだけ遅延 import する。
`parse_cond`・`default_conditions`・`finalize_conditions` も標準ライブラリだけで動く。
`sys.modules` のライブラリ差し替えや `sys.path` の変更はしない。

## 対応範囲

- 空でない JSON オブジェクトの JSONL。行順・条件順・列順・領域順・unit_index を保つ。
- 列の値は bool / Int64 整数 / 有限 float / 正常な Unicode 文字列 / null。
  同じ列は同じ型で、int と float の混在だけを許す。セルの欠損は null と同じ。
- `< <= > >= == !=`。数値同士、bool 同士、文字列同士のみ比較する。
  null との比較は全演算子で偽（`!= null` も偽）。
- Float64 比較では、整数は絶対値 `2**53` 以下に限定する。整数だけの比較は Int64 全域。
- native の既定 `infer_schema_length=100` と食い違わないよう、先頭100行のあとで
  新しい列や新しい非null型が出たら拒否する。100行以内も異種型混在は拒否する。
- `team` は文字列、`season` は整数。他の既存メタデータ（league・team_name・upper_half）も必要。

空入力は native と同じく結果を生成できない（例外クラス・文面の一致までは契約しない）。
重複JSONキー、surrogate、NaN/Infinity、リスト・オブジェクトのセル、巨大整数、
bool と数値/文字列の暗黙変換などは明示的に拒否する。native が扱える入力の全域を
置換する機能ではない。未対応の場合は利用者が `native` を選ぶ。

出力のキーや値の型は共通で、backend の印は追加しない。JSON の決定性を確認するときは
`json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False)` を使う。
既存APIの位置引数はそのままで、追加引数は keyword-only。通常のパイプラインの指定も変えない。

## 実験からの移行判断

Aoi の `shrink/run_overlap_stdlib.py --deps min` はプロセス全体の `numpy` と `polars` を
最小版に置き換える。既に読み込んだライブラリと混在すると、同じ名前が別の実装を指し、
他の分析やライブラリ内部の import に影響する。ライブラリ未導入を前提にする制約もある。
本番の切替にはこれを使わず、`_overlap_stdlib.py` の限定した行評価を呼ぶ。
実験用の生成物や注入ランナーは比較実験として残す。

## 検証と測定

`tests/test_overlap_stdlib.py` は c001 実データ（168行・8領域）、全演算子、空入力、
null/欠損、同一条件、条件なし、1/7/8/9/99/100/101/255/256/257行、
Int64・Float64境界、型推論範囲、未知の列、重複キー、不正Unicodeを検証する。
fresh `python -S` でライブラリと研究エンジンの import を禁止して成功すること、
既存モジュールがインストール済みでも差し替わらないこと、異なる PYTHONHASHSEED で
canonical JSON が一致すること、CLI の HTML が native とバイト一致することも確認する。

Linux / CPython 3.14.8、NumPy 2.5.4、Polars 2.0.0、c001の同じ入力で、
5組の fresh process と各7回の warm 呼出しを比較した中央値。
全サンプルの canonical JSON SHA-256 は
`12037df38eb301300768e0ef172e2e16e8e956dc7669aa08fd355414b7619e35`。
入力のSHAと生サンプルは [測定JSON](evidence/overlap-stdlib-benchmark.json)。

| 指標 | native | stdlib |
|---|---:|---:|
| プロセスの最大RSS | 159.46 MiB | 63.03 MiB |
| cold のPython追跡割当ピーク | 30.03 MiB | 20.43 MiB |
| fresh process 全体の時間 | 1.256 s | 0.871 s |
| 初回呼出し（tracemalloc有効） | 0.802 s | 0.458 s |
| warm 呼出し（tracemalloc無効） | 34.75 ms | 52.92 ms |

RSS は約60%減少した。この環境では初回起動も短くなったが、warm の反復計算は約1.52倍遅い。
小さい入力を少ない依存・メモリで読みたい場合の選択肢であり、大規模解析の高速化ではない。
RSS は native メモリを含み、tracemalloc はPython追跡対象のみ。測定器のオーバーヘッドと
共有実行環境の負荷を含む一例で、全OS・入力サイズでの保証ではない。

```sh
PYTHONPATH=/path/to/Aoi/pythdragoras python scripts/benchmark_overlap.py \
  --results /path/to/Aoi/cycles/c001-chunichi/outputs --repeats 5 --warm-repeats 7
```

ベンチマークのRSS計測は Linux/macOS 用。製品の軽量経路自体はOS依存の処理を持たない。
HTML生成は引き続き Markdown、PNG/SVG はChrome、登録状態の表示はQueRyuを必要とする。
`dist/dragowing_min.py` の公開面や依存宣言は変更しない。
研究入力・holdout履歴・研究結果ファイルには書き込まない。
