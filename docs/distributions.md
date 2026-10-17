# Aoi の最小配布API

Aoi がサブプロジェクトの配布登録を管理する。親アカウントの共通ツールを使い、Aoi → 子（アカウント親から見ると孫）という責任範囲にする。

| プロジェクト | 単一ファイル | 提供範囲 |
|---|---|---|
| BlueProbe | `dist/blueprobe_min.py` | 観測・正規化・検証済みsnapshotの解析 |
| QueRyu | `dist/queryu_min.py` | Cache・本文検証・html-snapshot/1。取得・問いの索引は含めない |
| SakAnalytics | `dist/sakanalytics_min.py` | 年次成績の正確な監査・記述的な近傍比較 |
| DRAgoWing | `dist/dragowing_min.py` | 図の仕様・HTMLレポート・JSONL。描画時のPlotly.jsはブラウザ側の依存 |
| PythDRagoras | `dist/pythdragoras_min.py` | 得点感度・来歴ラベルの検証 |

5本とも Python 3.11 以降で標準ライブラリだけでimportできる。各ファイルの公開APIは独立しており、1つのプロセスでも併用できる。Polars/NumPyを使う分析本体は元のAPIとして維持する。全機能の置き換えとは扱わない。QueRyuの取得は現在も同期式である。

## 登録と再生成

`distributions.json` が配布レジストリ。共通の `license: LICENSE` を1行で宣言し、完全なMIT通知を `dist/LICENSE` に同梱する。すべての配布元の通知が完全に同じバイト列であることを確認する。違う場合は勝手にまとめず停止する。ライセンス文に同期規則やSHAを追記しない。運用規則はこの文書、来歴は生成物のヘッダに置く。

- `source`: Aoiの入口と元モジュールを凍結したcommit。成果物を含める後続commitから参照し、自己参照を避ける。
- `tool`: 親の `tools/minpy.py` の取得元commitとSHA-256。実行前に照合する。
- `projects`: 入口・検索パス・出力・提供範囲。QueRyuのcache coreだけは独立した子mainの `repository` / `commit` を参照する。
- 生成はPython 3.12で固定。同じツール・ソースから全ファイルを再生成し、バイト一致を確認する。元コードが変わった場合はソースのcommitを更新して再生成する。

```sh
python -S scripts/build_distributions.py --minpy /checkout/parent/tools/minpy.py --sources /checkouts
python -S scripts/build_distributions.py --minpy /checkout/parent/tools/minpy.py --sources /checkouts --check
```

`/checkouts/queryu` は登録したQueRyu commitの明示的なcheckout。自動探索・自動取得は行わない。`--check` は成果物を書き換えない。CIが固定SHAで元コードとツールを用意し、全5本とMIT通知を比較する。隔離テストはコピーした5本だけを `python -I -S` で読み、キャッシュ改ざん拒否・BlueProbe連携・近傍・感度・来歴・HTML生成を実行する。

## subtreeとの関係

開発履歴の同期は全体subtree、他プロジェクトへの小さな配布は上記minAPIであり、それぞれ独立した契約である。subtreeの子を丸ごとvendor lockに重複登録しない。minAPIを別の利用者がvendorするときは、その利用者が配布ファイルと通知を固定する。

既存の `child-heads.json` はその登録SHAとprefixの完全一致を維持する。QueRyuの新しいcache coreを使うmin配布と、Aoi内の古いqueryu subtreeを新しい子mainへ更新する作業は区別する。後者には初回joinと全体pullの検証が必要であり、この配布登録だけで完了とはしない。SakAnalyticsとDRAgoWingの公開リポジトリ新規作成も、この登録だけでは実行していない。

Aoi → 子の書き込みは親PR #102で比較ref必須になった `gh_ops.py subtree-push` を使う。指定refがない・比較対象を選べない・取得できない・祖先でない場合は止める。検証済みSHAだけを新しいブランチへ空の期待値のlease付きで送り、PRで確認する。既定ブランチへ直接pushしない。joinを含むAoi統合PRはmerge commitで履歴を残す。
