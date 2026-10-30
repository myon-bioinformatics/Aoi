# ブラウザなしの出力検査（ブラウザ起動テストの前の層）

ブラウザを起動するテストは「Chromium が起動して描画できるか」を見る。この層は、その前に「描かれたもの、およびブラウザに渡すページが、頼んだ図そのものか」を、ブラウザ・JavaScript・ネットワークなしで見る。ここが赤ければ出力そのものが違い、ここが緑でブラウザ側だけ赤ければ、起動や環境の問題と切り分けられる。

## 見るもの

| 対象 | 検査（`scripts/rendered_output_checks.py`） | 等しくなければ失敗にする条件 |
|---|---|---|
| ブラウザに渡すページ | `check_page` | ライブラリの script が 1 つ、その後に `div#g`、その後に図の script の順。script 内の JSON が図の仕様と等しい（名前に `</script>` を入れても注入されない） |
| SVG | `check_svg` | 幅と高さ、タイトル、凡例（trace 名）、trace の数、点の数、マーカーの色、点の並び（x は右へ、y は上へ） |
| PNG | `check_png` | 8 ビット RGB/RGBA の正しい PNG（署名・各チャンクの CRC・IHDR・画素データの長さ）、レイアウトの大きさと一致、ほぼ単色でない、各 trace のマーカー色の画素がある |

どれも「ほかの図の仕様では通らない」ことをテストしている（3 図 × 3 図の総当たり）。

## 基準にする画像

`tests/fixtures/rendered_plotly/` に、診断用の合成図 3 点（`scripts/diagnose_dragowing_browser.py` の `_figures()`）を実際の Chromium で描いた PNG と SVG を置いている。記録は `manifest.json`（図の仕様の SHA-256、Plotly.js と Chromium の版、各ファイルの SHA-256）。

- これは「保存した観測」で、バイト単位の再現は求めない。PNG の画素は Chromium の版に、SVG は Plotly.js の版（と描くたびに変わる id）に依存する。テストは仕様との一致だけを見る。
- 合成図を変えると `manifest.json` の図の SHA-256 が合わなくなり、`test_manifest_matches_the_current_figures_and_files` が再生成を促す。
- 作り直し: `python scripts/render_static_fixtures.py --chrome <chromium の絶対パス> --plotly-js <plotly.min.js>`。保存の前に同じ検査を通し、通らない出力は保存しない。

## 検査そのものの確かさ

- PNG の読み取りは、5 種類の行フィルタ（None／Sub／Up／Average／Paeth）× RGB／RGBA を、テスト側で別に書いた符号化との往復で確かめている。実際の Chromium の PNG 3 枚（フィルタ 1〜4 を使う）は Pillow と画素単位で一致することを、作成時に確認した（リポジトリには入れていない）。
- 壊した入力（署名・切り詰め・CRC・大きさの偽り・空・色なし、SVG の改変、ページの順序や仕様の改変）はすべて拒否される。検査コードを 1 か所ずつ無効にする変異 26 通りで、すべてテストが落ちることを確かめた。
- ブラウザ実行側の `_validate_image`（診断スクリプト）が、保存した出力を受け入れることも同じテストで見ている。

## 限界

- 基準の画像は特定の Chromium と Plotly.js で描いた 1 回の観測。CI のブラウザ側は Plotly.js をバージョン指定なしの jsDelivr から取るので、構造が変われば、ここは通ってブラウザ側の比較で気づくことになる。
- PNG の読み取りは標準ライブラリだけの小さな実装で、Ironmate の `pillow_min.py` のようにリポジトリ間で共有した実装ではない。共有したい場合は、この関数を差し替える。
- 実際のブラウザで描けるか（起動・描画・タイムアウト）は、引き続きブラウザ起動のテストが見る。

## CI での位置

`ci.yml` の `Offline Chrome export` ジョブで、依存のインストールの直後、ブラウザを選ぶ前に
`tests/test_rendered_output_static.py` を実行する。通常の pytest ジョブでも同じテストが走る。
