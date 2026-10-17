# cycle-001/chunichi から持ってきた研究記録

このディレクトリは、ブランチ `cycle-001/chunichi` の先端にある研究のうち、正本（このサイクルの `propositions.toml`・`outputs/`・`research/R1`〜`R29`）と衝突したものを、数値も識別子も書き換えずに置いたものです。

正本側は次を保ちます。

- LittleBit holdout が固定している `analysis.toml`・`outputs/season.jsonl`・`rule_candidates.toml` のバイト
- P1〜P114 の保存済み判定と、共通評価軸（metrics・seed）の診断
- 小文字のパッケージ名と、親ワークフローピン `b000e5967cb7596f6f9f20fe396a686fdc700c16`

こちらに置いたもの:

- `propositions.toml` は P115 以降を含む branch 側の命題定義
- `outputs/season.jsonl` は同じ168球団年に、後から足した派生列を加えた表。共有列の差は浮動小数の最終桁で、係数や判定の再基準化はしていません
- `analysis.toml` は 2026年の確かめ対象に branch 側の命題IDを足した版
- `pipeline.toml` は当時の PascalCase の入口を呼ぶ実行定義
- `outputs/` の index・objections・ledger・summary・propositions.jsonl・run.txt・observed.md は branch 側の生成物
- `research/` は branch 側の R27 以降。正本の R27（年次感度）・R28（P96）・R29（リーグ実験）とは別の研究で、同じ番号を後から付けたものです。番号は歴史どおり残し、正本のダイジェスト対象には混ぜていません

branch 側のパッケージ木（`BlueProbe/`・`QueRyu/`・`SakAnalytics/`・`PythDRagoras/`・`NagoyAction/`・`DRAgoWing/`）と `research/gpt-r001-score-allocation/` はリポジトリ直下にあります。正本の実行経路は小文字のディレクトリです。
