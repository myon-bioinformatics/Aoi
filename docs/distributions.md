# Aoi の最小配布API

Aoi がサブプロジェクトの配布登録を管理する。親アカウントの共通ツールを使い、Aoi → 子（アカウント親から見ると孫）という責任範囲にする。

| プロジェクト | 単一ファイル | 提供範囲 |
|---|---|---|
| BlueProbe | `dist/blueprobe_min.py` | 観測・正規化・検証済みsnapshotの解析 |
| QueRyu | `dist/queryu_min.py` | Cache・本文検証・html-snapshot/1。取得・問いの索引は含めない |
| SakAnalytics | `dist/sakanalytics_min.py` | 列を明示した年次・期間比較、記述的な近傍比較 |
| DRAgoWing | `dist/dragowing_min.py` | 汎用系列・行列の図仕様、HTMLレポート・JSONL。描画時のPlotly.jsはブラウザ側の依存 |
| PythDRagoras | `dist/pythdragoras_min.py` | 汎用数値スコアの閾値走査、標本曲線、来歴ラベルの検証 |

5本とも Python 3.11 以降で標準ライブラリだけでimportできる。各ファイルの公開APIは独立しており、1つのプロセスでも併用できる。Polars/NumPyを使う分析本体は元のAPIとして維持する。全機能の置き換えとは扱わない。QueRyuの取得は現在も同期式である。

## 再利用APIの境界

NPB・野球の列名、勝敗、順位、CS確率、球団順序は分析本体に置く。min版に既定の球団・目的変数・成果判定を持ち込まない。汎用部分の入口と抽出した小さな核は `distributions/entries/` でAoiが管理し、子の登録済みsubtreeを変更せずに配布する。独立子リポジトリへの移管を完了したとは扱わない。

- SakAnalytics: `compare_periods(rows, entity=..., period=..., metrics=..., before=..., after=...)` は比較する2期間を明示し、整数差を丸めず保持する。欠けた期間・不明値は理由と `None`、基準0の相対変化も `None`。`discover(rows, identifier=..., features=..., group=None, excluded=(), limit=20)` は完全な数値を持つ行全体の母標準偏差で標準化し、指定群内の最近傍ペアを返す。一定の特徴量は距離から除き、欠測・除外理由を返す。順位や結果による絞り込みは行わない。記述的な距離であり、因果や有意性は判定しない。
- PythDRagoras: `threshold_curve(scores, outcomes, thresholds)` は任意の有限スコアとBoolean観測を使う。`score >= threshold` を陽性として混同行列・MCC等を計算する。既存 `season_sensitivity` の数値核を抽出し、並べ替え `O(n log n)` の後、単調な閾値を `O(n+t)` で走査する。各行の状態更新は最大1回。全件再集計との同値性をテストする。これは計算量の性質であり、全入力での実時間高速化を保証しない。`counts_metrics`、`shape` と `Provenance` / `classify` / `audit_record` も提供する。標本曲線の欠測区間は補間せず、分母0は不明とする。
- DRAgoWing: `series_figure(x, y, ...)` と `matrix_figure(x, y, z, ...)` はラベル・順序・欠測を保つPlotly仕様を作る。`render_report` は既存の汎用HTMLレポート、`read_jsonl` は記録読込。球団向けの図・式ID別ファイル選択は公開APIから外す。HTMLのブラウザ描画にはPlotly.js取得が必要で、Python単一ファイルの標準ライブラリ契約と分ける。
- BlueProbeとQueRyu: 観測・検証済みsnapshot・キャッシュ本文の整合性を提供する。取得の非同期化や未計測の高速化を提供済みとはしない。BlueProbe の HTML 木は標準ライブラリの `html.parser` で、`dom_patterns.py` は `blueprobe` の再エクスポートなので bundle の検索から外さない（入口の静的 import にも出てこない）。`html_source.py` は `main` から読まれ、自身が `blueprobe` を読む。minpy はこの往復を循環として止めるので、`omit_from_bundle` で stdlib bundle の検索から外す。任意の `mcp_toolcall_lab` import は `ImportError` を捕まえる関数の中にあり、subtree のファイル自体は残す。bundle の公開面は従来どおり `blueprobe.py` と `snapshot_source.py` である。

例えば野球と無関係な測定装置の年次比較も、列を変えるだけで使える。

```python
from sakanalytics_min import compare_periods, discover
from pythdragoras_min import threshold_curve
from dragowing_min import series_figure

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

## 登録と再生成

`distributions.json` が配布レジストリ。共通の `license: LICENSE` を1行で宣言し、完全なMIT通知を `dist/LICENSE` に同梱する。すべての配布元の通知が完全に同じバイト列であることを確認する。違う場合は勝手にまとめず停止する。ライセンス文に同期規則やSHAを追記しない。運用規則はこの文書、来歴は生成物のヘッダに置く。

- `source`: Aoiの入口と元モジュールを凍結したcommit。成果物を含める後続commitから参照し、自己参照を避ける。
- `tool`: 親の `tools/minpy.py` の取得元commitとSHA-256。実行前に照合する。
- `projects`: 入口・検索パス・出力・提供範囲。QueRyuのcache coreだけは独立した子mainの `repository` / `commit` を参照する。
- 生成はPython 3.12で固定。同じツール・ソースから全ファイルを再生成し、バイト一致を確認する。元コードが変わった場合はソースのcommitを更新して再生成する。入口だけでなく検索ディレクトリ内の依存核の変更・未追跡ファイルも検出して停止する。

```sh
python -S scripts/build_distributions.py --minpy /checkout/parent/tools/minpy.py --sources /checkouts
python -S scripts/build_distributions.py --minpy /checkout/parent/tools/minpy.py --sources /checkouts --check
```

`/checkouts/queryu` は登録したQueRyu commitの明示的なcheckout。自動探索・自動取得は行わない。`--check` は成果物を書き換えない。CIが固定SHAで元コードとツールを用意し、全5本とMIT通知を比較する。隔離テストはコピーした5本だけを `python -I -S` で読み、キャッシュ改ざん拒否・BlueProbe連携・期間比較・近傍・閾値・来歴・HTML生成を実行する。

## subtreeとの関係

開発履歴の同期は全体subtree、他プロジェクトへの小さな配布は上記minAPIであり、それぞれ独立した契約である。subtreeの子を丸ごとvendor lockに重複登録しない。minAPIを別の利用者がvendorするときは、その利用者が配布ファイルと通知を固定する。

既存の `child-heads.json` はその登録SHAとprefixの完全一致を維持する。QueRyuのcache coreを使うmin配布と全体subtree同期は独立した検証である。全体subtreeの初回joinでは、QueRyu main `5ce256d77d64b33d4c71c2cbb84fe201f9637567` を `git subtree add` で Aoi の `queryu/` に取り込み、登録SHA・tree・mirrorの一致を確認した（`distributions.json` の QueRyu `commit` pin は min 配布用の別checkout）。SakAnalyticsとDRAgoWingの公開リポジトリ新規作成も、この登録だけでは実行していない。

Aoi → 子の書き込みは親PR #102で比較ref必須になった `gh_ops.py subtree-push` を使う。指定refがない・比較対象を選べない・取得できない・祖先でない場合は止める。検証済みSHAだけを新しいブランチへ空の期待値のlease付きで送り、PRで確認する。既定ブランチへ直接pushしない。joinを含むAoi統合PRはmerge commitで履歴を残す。
