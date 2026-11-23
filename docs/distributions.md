# Aoi の最小配布API

Aoi がサブプロジェクトの小さな再利用APIを管理する。どれも束ねず、元のファイルをそのまま写して使う（2026-11-23 から。束ねる道具 `tools/minpy.py` と `dist/`・`distributions.json` は使わない）。

| プロジェクト | 写すファイル | 提供範囲 |
|---|---|---|
| 🔵 BlueProbe | `blueprobe/blueprobe.py` | 観測・正規化・検証済みsnapshotの解析、ほか BlueProbe の全部 |
| 🔎 QueRyu | `queryu/core/cache_core.py` | Cache・本文検証・html-snapshot/1。取得・問いの索引は含めない |
| 🐟 SakAnalytics | `distributions/entries/sakanalytics_api.py`・`period_comparison.py`・`neighbor_comparison.py` | 列を明示した年次・期間比較、記述的な近傍比較 |
| 🐉 DRAgoWing | `dragowing/dragowing.py` | 汎用系列・行列の図仕様、HTMLレポート・JSONL、ほか DRAgoWing の全部。描画時のPlotly.jsはブラウザ側の依存 |
| 📐 PythDRagoras | `distributions/entries/pythdragoras_api.py`・`score_math.py`・`period_comparison.py` と `pythdragoras/core/registration_audit.py` | 汎用数値スコアの閾値走査、標本曲線、来歴ラベルの検証 |

どれも Python 3.11 以降で標準ライブラリだけで import できる。複数のファイルを写すものは、同じディレクトリに並べればそのまま読める（互いを最上位の名前で import する）。各ファイルの公開APIは独立しており、1つのプロセスでも併用できる。ライセンスはリポジトリの `LICENSE`（MIT）で、写す側がファイルと一緒に通知を持つ。Polars/NumPyを使う分析本体は元のAPIとして維持する。全機能の置き換えとは扱わない。QueRyuの取得は現在も同期式である。

`tests/test_distributions.py` は表のファイルだけを空のディレクトリへ写し、`python -I -S` で読んで、キャッシュ改ざん拒否・BlueProbe連携・期間比較・近傍・閾値・来歴・HTML生成を実行する。

## 再利用APIの境界

NPB・野球の列名、勝敗、順位、CS確率、球団順序は分析本体に置く。min版に既定の球団・目的変数・成果判定を持ち込まない。汎用部分の入口と抽出した小さな核は `distributions/entries/` でAoiが管理し、子の登録済みsubtreeを変更せずに配布する。独立子リポジトリへの移管を完了したとは扱わない。

- SakAnalytics: `compare_periods(rows, entity=..., period=..., metrics=..., before=..., after=...)` は比較する2期間を明示し、整数差を丸めず保持する。欠けた期間・不明値は理由と `None`、基準0の相対変化も `None`。`discover(rows, identifier=..., features=..., group=None, excluded=(), limit=20)` は完全な数値を持つ行全体の母標準偏差で標準化し、指定群内の最近傍ペアを返す。一定の特徴量は距離から除き、欠測・除外理由を返す。順位や結果による絞り込みは行わない。記述的な距離であり、因果や有意性は判定しない。
- PythDRagoras: `threshold_curve(scores, outcomes, thresholds)` は任意の有限スコアとBoolean観測を使う。`score >= threshold` を陽性として混同行列・MCC等を計算する。既存 `season_sensitivity` の数値核を抽出し、並べ替え `O(n log n)` の後、単調な閾値を `O(n+t)` で走査する。各行の状態更新は最大1回。全件再集計との同値性をテストする。これは計算量の性質であり、全入力での実時間高速化を保証しない。`counts_metrics`、`shape` と `Provenance` / `classify` / `audit_record` も提供する。標本曲線の欠測区間は補間せず、分母0は不明とする。
- DRAgoWing: `series_figure(x, y, ...)` と `matrix_figure(x, y, z, ...)` はラベル・順序・欠測を保つPlotly仕様を作る（`dragowing.py` の中、旧 `distributions/entries/plot_specs.py`）。`render_report` は既存の汎用HTMLレポート、`read_jsonl` は記録読込。`dragowing.py` には球団向けの図も同じファイルにある。HTMLのブラウザ描画にはPlotly.js取得が必要で、Python単一ファイルの標準ライブラリ契約と分ける。
- BlueProbeとQueRyu: 観測・検証済みsnapshot・キャッシュ本文の整合性を提供する。取得の非同期化や未計測の高速化を提供済みとはしない。BlueProbe の HTML 木は標準ライブラリの `html.parser` で、DOM パターン表も `blueprobe.py` 1 ファイルにある。汎用の HTML 観測と snapshot 契約も `blueprobe.py` にまとまっている（`html_source.py` と `snapshot_source.py` はそこへ入った）。NPB の取得元は `npb/` にあり、写すファイルには入らない。

例えば野球と無関係な測定装置の年次比較も、列を変えるだけで使える。

```python
from sakanalytics_api import compare_periods, discover   # distributions/entries/
from pythdragoras_api import threshold_curve             # distributions/entries/ と registration_audit.py
from dragowing import series_figure   # dragowing/dragowing.py

rows = [dict(sensor="north", year=2024, energy=10),
        dict(sensor="north", year=2025, energy=12)]
comparison = compare_periods(rows, entity="sensor", period="year",
                             metrics=["energy"], before=2024, after=2025)
pairs = discover([dict(id="a", latency=10), dict(id="b", latency=12)],
                 identifier="id", features=["latency"])
curve = threshold_curve([0.1, 0.4, 0.9], [False, True, True], [0.1, 0.4, 1.0])
figure = series_figure([p["threshold"] for p in curve],
                       [p["mcc"] for p in curve], y_title="MCC")
```

## subtreeとの関係

開発履歴の同期は全体subtree、他プロジェクトへの小さな配布は上記minAPIであり、それぞれ独立した契約である。subtreeの子を丸ごとvendor lockに重複登録しない。minAPIを別の利用者がvendorするときは、その利用者が写したファイルと通知を固定する。

`child-heads.json` に登録した子は、履歴から導いた同期済みcommitとprefixの完全一致を維持する（shaは書かない）。QueRyuの `core/cache_core.py` は全体subtreeで取り込んだものをそのまま使う。全体subtreeの初回joinでは、QueRyu main `5ce256d77d64b33d4c71c2cbb84fe201f9637567` を `git subtree add` で Aoi の `queryu/` に取り込み、登録SHA・tree・mirrorの一致を確認した。SakAnalyticsとDRAgoWingの公開リポジトリ新規作成も、この登録だけでは実行していない。

Aoi → 子の書き込みは親PR #102で比較ref必須になった `gh_ops.py subtree-push` を使う。指定refがない・比較対象を選べない・取得できない・祖先でない場合は止める。検証済みSHAだけを新しいブランチへ空の期待値のlease付きで送り、PRで確認する。既定ブランチへ直接pushしない。joinを含むAoi統合PRはmerge commitで履歴を残す。
