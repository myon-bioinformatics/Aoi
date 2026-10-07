# DRAgoWing

集計結果を、分母・適用範囲・留保と一緒に伝える可視化サブプロジェクト。
`dragowing.py` は標準ライブラリだけで Plotly HTML を生成する。統計計算や命題判定は行わず、研究側のアダプターから図・表・注記を受け取る。Matplotlib は使用しない。

最初の利用例は [得点時期レポート](https://github.com/myon-bioinformatics/Aoi/blob/cycle-001/chunichi/research/gpt-r001-score-allocation/outputs/score_timing.html)。HTMLをダウンロードしてブラウザーで開く。Plotly.js 3.6.0 は固定URLから読み込むため、グラフにはインターネット接続が必要。読み込み失敗時も数値表と注記は表示する。HTMLに含めるのは既存の球団年集計のみで、生の試合・イニング行は含めない。

```sh
python research/gpt-r001-score-allocation/render_score_report.py
```

年（2013〜2025）と切点（6回・7回）を選べる。2020年は参考表示。各図の「数値と分母を表示」で合計・割合の分母を確認できる。

## レンダラーの入力

`render_report(spec)` は HTML 文字列を返す。`title`, `intro`, `notes`, `provenance` は説明文、`controls` は選択肢、`default` は `|` 区切りの初期選択値、`frames` は選択値ごとの画面。各画面の `panels` は `title`, `note`, Plotly の `data` / `layout`, 表の `headers` / `rows` を持つ。入力はリポジトリ内の信頼できるアダプターで作る。説明文は DOM の textContent、埋め込みJSONは script 終端をエスケープして配置する。非有限数は拒否し、分母0は値なしとして表示する。

検証は `pytest` に組み込む。研究固有の数値対応、2020年の表示、script終端のエスケープをテストする。

## 既存Markdown実装との接続

[DRAgoWing reports ワークフロー](https://github.com/myon-bioinformatics/Aoi/blob/cycle-001/chunichi/.github/workflows/dragowing.yml) は、PR・main更新・手動実行時に `myon-bioinformatics/markdown` の最新mainを一度チェックアウトしてから `build_reports.py` で研究文書を描画する。通常pytestのdocs-onlyスキップは維持し、文書だけの変更でもレポート生成は実行する。上流だけの更新で自動実行するスケジュールは設けていない。

成果物 `dragowing-reports` をダウンロード・展開し、`index.html` を開く。研究文書とDRAgoWingのREADME、Plotlyレポートへの入口がある。現在Aoiに公開サイトのデプロイ経路はないため、今回はActions成果物までを接続する。将来のデプロイはこの生成ディレクトリを公開対象にできる。実データ取得・再集計はこのワークフローでは行わない。

各文書の「変更比較」は、PRでは比較先commit、main pushでは直前commitを使い、同じMarkdown実装で旧版・新版を描画する。下部にはMarkdownソースの行差分を色付きで表示する。描画結果そのものの単語単位rich diffは未実装。比較元が取得できない場合は「比較不能」を明記し、変更なしとは扱わない。数値・判定の意味を理解して照合する研究用の差分は、さらに別の機能になる。

`build-provenance.json` にAoiのcommit、MarkdownのcommitとSHA-256、比較元、各文書の状態・ハッシュを記録する。`_renderer/` に実際に使った `markdown.py` と上流LICENSEを保存する。最新版の取り込みが失敗したらビルドも失敗し、古い版へ黙って戻らない。手動実行の `markdown-ref` にcommit SHAを指定すれば同じ実装版を使える。

ローカルでの例（出力先は空のディレクトリを指定）：

```sh
git clone https://github.com/myon-bioinformatics/markdown.git .deps/markdown
python -S DRAgoWing/reports/build_reports.py --markdown-root .deps/markdown --output build/dragowing --previous-ref HEAD~1
```

描画は上流の `markdown_to_html()` / `default_stylesheet()` を使用する。上流は完全なCommonMark/GFM実装ではなく、数式・Mermaid・生HTMLなどは対応範囲外。元文書へのリンクは固定Aoi commitに解決し、Plotlyは引き続きグラフを担当する。
