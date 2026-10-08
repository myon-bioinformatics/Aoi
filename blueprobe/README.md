# BlueProbe

> まず見に行く。解釈はあとで。

![BlueProbe](../docs/images/blueprobe.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

観測と発見を担う。取得したページを読み、**何がそこにあるか**を記録する。勝敗や原因の判断はしない。

## 構成

| ファイル | 役割 |
|---|---|
| `blueprobe.py` | 取得元に依存しない部分: 正規化、報告の契約、オフライン再解析（`inspect`） |
| `npb_calendar.py` | 取得元: npb.jp の月別公式戦カレンダー |
| `docs/npb_calendar.md` | その取得元で、どの年の何を確認したか（観測と未確認を分ける） |
| `docs/antipatterns.md` | 繰り返しそうな失敗とその約束 |
| `tests/cases/*.jsonl` | 表記揺れのコーパス（xprobe と同じ id / category / value / reason 形式） |

## 報告の契約

1ページを読んだ結果は、採用したものだけでなく、採用しなかったものも返す。

```text
records : 採用した観測（原文と派生値を並べる）
counts  : 採用しなかったものの区分ごとの件数（例: cancelled, non_regular）
unknown : どの区分にも当たらなかったもの。原文を残す → 表記の変化を疑う
```

## 取得元を足す

`blueprobe/<name>.py` に次の2つを書けば、QueRyu と `inspect` からそのまま使える。

```python
def pages(scope) -> list[tuple[str, str, str]]: ...   # (key, url, group)
def parse(html: str, url: str) -> dict: ...          # new_report() の形で返す
def check(records) -> list[str]: ...                 # 任意。既知値との照合
```

正規表現は狭く、全体一致で書く。新しい表記を見つけたら、広げる前にコーパスへケースを足す。

## 実行

```bash
uv run python blueprobe/blueprobe.py --source npb_calendar --cache data/raw/npb_calendar --out observed.md
```

キャッシュだけを読み、ネットワークには出ない。未知の表記があれば件数を表示する（`--strict` で終了コード1）。

## 保存HTMLの共通抽出へ接続する

`html_source.HtmlSource(selector=..., extractor=...)` は、取得済みHTMLを信頼した
オフライン抽出関数へ渡し、既存の `inspect()` の報告形式に変換する。
取得・キャッシュ・NPB固有の観測は引き続き既存モジュールが担当する。
抽出できない構造は `extraction_failed` と原文付き `unknown` に残す。
同じページの抽出条件変更や再実行では、リンク先・CSSを含めて通信しない。

```python
from html_source import HtmlSource
from mcp_toolcall_lab.adapters.html_snapshot import extract

source = HtmlSource(selector="main#calendar > .day", extractor=extract)
rows = inspect(source, saved_pages, records_out)
```

上記は lab PR #110 とそのselector follow-upが提供する抽出関数を使う任意の接続例。
BlueProbeはそのパッケージを自動インストールしない。通常のNPB解析に新しい依存はない。
`--source html_source` はlabの抽出モジュールが利用可能な環境でgeneric抽出を行う。
selectorはタグ、`#id`、`.class`、子要素 `>`、子孫の限定的な構文で、
CSSの描画・JavaScript実行・HTML5ブラウザDOM再構築を意味しない。
全CSS構文への対応やPages上のPython実行は保証しない。

### CSSを読む・既存NPB解析と比べる

`HtmlSource(include_css=True, stylesheets={saved_url: saved_css}, extractor=extract)`
で埋め込み・inline・明示した保存CSSの宣言を読む。色番号、CSS変数、重要指定、
条件付きルール、selectorとHTML要素の一致をderived側に残す。
外部stylesheetと@importは取得せず未読参照として残す。CSSごとのハッシュも残す。
未対応selectorはunsupported、一致なしはunmatchedと区別する。
表示色・継承・詳細度・変数解決・画面サイズ条件は計算せず、computed_stylesはfalse。
CSSが読めたことを、画面を再現できたこととして扱わない。

`html_compare.compare_calendar()` は、保存HTMLからselectorで読んだリンク群と、
既存 `npb_calendar.parse()` が採用した試合URLを比較する。
採用試合の欠落、リンク重複、抽出失敗を返す。元HTMLをNPB parserにそのまま渡すので、
大会見出し・中止・未知表記の判定は既存処理が保持する。
`complete_for_adopted_games` は既存parserが採用した試合に対する被覆だけを意味し、
parser自身が未知の試合を取りこぼしていないという証明ではない。
NPB保存fixtureの4試合・中止1件・非公式戦1件を用いて比較する。
同じ原文を何度再解析しても新規GETはしない。labなしの通常NPBテストは従来どおり動く。

