# 責務の境界: BlueProbe / QueRyu / web-ui

> 提案。web-ui や Aoi のコードはここでは動かさない。合意できたものから、各リポジトリで移す。

| | 担うこと | 担わないこと |
|---|---|---|
| **QueRyu**（Aoi/queryu） | 取得（間隔・条件付きGET・404 の記録）、キャッシュ、来歴（manifest）、データセットの書き出し | 本文の読み方（parser）、表記の判断 |
| **BlueProbe** | 保存済み本文を**見に行く**: HTML/CSS/DOM 構造の観測、抽出、表記の正規化、報告の契約、観測証跡の形式 | 取得・キャッシュ・ネットワーク、勝敗や原因の判断 |
| **web-ui** | Python から HTML を**出す側**: `web_ui.render_document`、共有 CSS/JS、HTML 構造の契約（contract/v1） | 外部ページの観測・抽出の方法論 |

## つなぎ目

- QueRyu → BlueProbe: 供給元の契約（[snapshot.md](contract/v1/snapshot.md)）。QueRyu は供給元の一つ
- BlueProbe → QueRyu / SakAnalytics: 報告の契約（[report.md](contract/v1/report.md)）
- web-ui → BlueProbe: web-ui が出す HTML は contract/v1 の構造を持つので、BlueProbe からは「読む対象の一つ」になる

## BlueProbe 側へ寄せたいもの（提案）

| 今の場所 | 内容 | 提案 |
|---|---|---|
| web-ui `docs/evidence/*-dom.json` | 観測した DOM の証跡（`source_url`, `observed_date`, `http_response.sha256`, `region`, `raw_html` / `dom_html` / `text_content` / `inner_text` / `page_text` を並べる） | 形式の定義を BlueProbe の契約（`dom-evidence/1` など）として持つ。web-ui の証跡はその形式に従う側にする |
| web-ui `docs/local-dom-lab.md`, `tests/integration/test_gradio_dom.py` | 描画後の `innerText` と保存 DOM の抽出結果の比較 | 「観測の比較」の考え方は BlueProbe の文書に。Gradio での配信・ブラウザ起動は web-ui に残す |
| browser-test-kit `scripts/page_text.py` | 本文抽出 | コピーしない。固定 SHA で参照し、BlueProbe 側に比較の観測を残す |

web-ui に残すもの: 配信（Gradio/HTML の生成）、CSS/テーマ、HTML 構造の契約。

## 未決: 「見に行く」側の持ち主

`inspect_cache` は当面 DeprecationWarning を出したまま残す。

「取りに行く・見に行く」側（保存済み本文の供給、および mcp-toolcall-lab の snapshot 証跡＝`html-snapshot/1` の生成と照合）は、
BlueProbe より QueRyu が持つほうが自然かもしれない。QueRyu はすでに取得・来歴・`Cache.snapshot()` を持つため。
その場合 BlueProbe は「読む・観測を報告する」に絞り、供給元の契約（`docs/contract/v1/snapshot.md`）だけを持つ。
どちらに置くかは未決（open question）。
