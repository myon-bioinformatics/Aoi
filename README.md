# DRAgoWing

集計結果を、分母・適用範囲・留保と一緒に伝える可視化サブプロジェクト。
`dragowing.py` は標準ライブラリだけで Plotly HTML を生成する。統計計算や命題判定は行わず、研究側のアダプターから図・表・注記を受け取る。Matplotlib は使用しない。

最初の利用例は [得点時期レポート](../research/gpt-r001-score-allocation/outputs/score_timing.html)。HTMLをダウンロードしてブラウザーで開く。Plotly.js 3.6.0 は固定URLから読み込むため、グラフにはインターネット接続が必要。読み込み失敗時も数値表と注記は表示する。HTMLに含めるのは既存の球団年集計のみで、生の試合・イニング行は含めない。

```sh
python research/gpt-r001-score-allocation/render_score_report.py
```

年（2013〜2025）と切点（6回・7回）を選べる。2020年は参考表示。各図の「数値と分母を表示」で合計・割合の分母を確認できる。

## レンダラーの入力

`render_report(spec)` は HTML 文字列を返す。`title`, `intro`, `notes`, `provenance` は説明文、`controls` は選択肢、`default` は `|` 区切りの初期選択値、`frames` は選択値ごとの画面。各画面の `panels` は `title`, `note`, Plotly の `data` / `layout`, 表の `headers` / `rows` を持つ。入力はリポジトリ内の信頼できるアダプターで作る。説明文は DOM の textContent、埋め込みJSONは script 終端をエスケープして配置する。非有限数は拒否し、分母0は値なしとして表示する。

検証は `pytest` に組み込む。研究固有の数値対応、2020年の表示、script終端のエスケープをテストする。
