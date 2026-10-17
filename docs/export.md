# Chrome による PNG / SVG 出力

画像出力 API は Python の `plotly` パッケージも kaleido も使わない。Plotly.js は HTML と同じ web-ui の CDN 契約（`dragowing/plotly_cdn.py`）から取得し、各書き出し用の一時ディレクトリへコピーして `file:` URL で読み込む。CLI の `--png` も同じ `export_draw` 経路である。

元の PR #44・#43・#42 の変更は、PR 整理で同じ統合ブランチに取り込んでいる。既存の HTML の既定出力、研究記録、整数得点、正式判定器には触れない。

```python
from dragowing.export import PLOTLY, export_draw, plotly_figure_content
from dragowing.render import RenderSession

fig = {"data": [{"type": "scatter", "x": [1, 2], "y": [3, 4]}],
       "layout": {"width": 640, "height": 480, "title": {"text": "Example"}}}
with RenderSession(offline=True) as session:
    for fmt in ("png", "svg"):
        export_draw(PLOTLY, plotly_figure_content(fig), f"example.{fmt}", fmt, session=session)
```

`PLOTLY` は Mermaid と同様にブラウザ側の JS で描く汎用 `DrawConfig` である。オフライン検証では環境変数 `DRAGOWING_PINNED_PLOTLY_JS` に、事前に検証済みの `plotly.min.js` を置ける。図のデータもローカルに用意する必要がある（外部 URL の地図・画像・フォント等を自動取得する機能ではない）。

HTML の外部タグと `--embed` は locked web-ui の固定版＋ハッシュ契約を共用する。

`Plotly.newPlot` の Promise 完了を待つ。PNG は図のコンテナ全体をスクリーンショットにし、SVG はローカルの `Plotly.toImage` で全レイヤーを直列化する。最初の `svg.main-svg` だけを取得すると欠落するタイトル・凡例も含める。SVG の WebGL 部分等の扱いは Plotly.js の仕様による。

パイプ通信は Python 標準ライブラリのみ。POSIX の Chrome/Chromium を使い、Windows のパイプは未対応。引数 `chrome=`、環境変数 `CHROME` / `CHROMIUM`、PATH の順に検索する。実行権限のないファイルもエラーとする。Kaleido / choreographer はこの API には不要である。

`Timeouts(launch=30, load=30, ready=30, capture=15)` で各段階の上限を指定できる。通信の送信側も上限内に収め、部分書き込みを最後まで送る。起動時に `Browser.getVersion` を確認する。JSON 不正、EOF、起動失敗は例外にする。タイムアウト・取得失敗を成功や空画像として扱わない。各描画の成功・失敗のどちらでも target を閉じ、破棄イベントまで待つ。close 失敗時にはブラウザ全体を終了する。

`RenderSession(offline=True)` は描画ページの CDP ネットワークを無効にする。既定の汎用レンダラのネットワーク動作は変えない。`MERMAID` は引き続き CDN を使うサンプル設定であり、オフライン対応の対象は `PLOTLY` である。

## 検証

```bash
CHROME=/path/to/chrome DRAGOWING_REQUIRE_CHROME=1 uv run --locked --python 3.14 pytest -q dragowing/tests
```

Chrome がない通常環境では実ブラウザのテストを理由付きで skip する。`DRAGOWING_REQUIRE_CHROME=1` のときは skip せず失敗する。Mermaid の CDN テストだけは `DRAGOWING_TEST_NETWORK=1` の明示指定が必要。

CI の専用ジョブは依存導入後、`sudo unshare --net` でネットワークを分離し、実 Chrome を必須としてパイプ・PNG/SVG テストを実行する。JUnit は `junit-chrome-export-py3.14` として保存する。通常の Python 3.11–3.15 マトリクスも維持する。

テストはネットワーク遮断中の同梱 JS バージョン、3 図 × 2 形式の同一 PID、PNG の寸法・CRC・展開データの非空白性、SVG の XML・タイトル・凡例・点数、target 数が増えないことを確認する。Chrome 不在・実行権限なし・起動失敗・応答なし・送信詰まり・途中終了・不正 JSON・部分書き込み・大きな応答・早着イベント・ready タイムアウト・capture 失敗後の解放と再利用も確認する。画像のバイト一致は判定基準にしない。
