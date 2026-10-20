# DOM 構造パターン・プリセット設計

実装はすべて [`blueprobe.py`](../blueprobe.py) の1ファイル（型は同じファイル内の TypedDict）。実行時は標準ライブラリの `html.parser` だけを使い、selectolax はテストでの照合専用。

BlueProbe は保存済み HTML の DOM 構造から特定の主要コンテンツを抽出する際、CSS セレクタを直接指定する代わりに、
ドロップダウン/プリセット指定可能な DOM パターン識別子（`github_readme` や `portfolio_profile` 等）を選択・分類できるようにしています。

## 定義されている DOM パターン一覧

| パターンキー (`key`) | カテゴリ | ラベル | CSS セレクタ (`selector`) | 対象の例 |
|---|---|---|---|---|
| `github_readme` | `repository_readme` | GitHub README / Markdown Body | `article.markdown-body, .markdown-body` | GitHub, Gitea, npm README |
| `article_body` | `article_reader` | Article / Blog Main Body | `article, [role='main'] article, .article-body, .entry-content, .post-content` | ブログ・ニュース記事本文 |
| `documentation_main` | `documentation` | Documentation Main Section | `main, [role='main'], article.doc-content, .docs-content, .md-content` | Read the Docs, Docusaurus |
| `portfolio_profile` | `portfolio_bio` | Portfolio / Profile Section | `section#about, #about, .profile, .portfolio, section.bio, #portfolio` | ポートフォリオ・自己紹介 |
| `reader_page` | `reader_view` | Distraction-free Reader View | `#reader-content, .reader-view, article, main` | リーダーモード・Web クリップ |
| `npb_calendar` | `npb_sports` | NPB Schedule Calendar Table | `#calendar, .calendar, table.calendar` | NPB 公式戦カレンダー表 |
| `npb_linescore` | `npb_sports` | NPB Game Linescore Table | `table.score_table, .linescore, #linescore` | NPB 試合得点表 |
| `generic_main` | `generic` | Generic Main Region | `main, #main, #content, .main-content` | 一般 Web ページの main |
| `social_timeline` | `social` | Social Timeline / Comment Thread | `[role='feed'], [role='feed'] > article, .timeline, .thread-comments, .comment-list` | SNS タイムライン・コメント欄 |
| `ecommerce_product` | `ecommerce` | E-commerce Product Detail / Grid | `[itemtype='https://schema.org/Product'], [itemtype='http://schema.org/Product'], [itemprop='price'], .product-detail, .product-grid` | 商品詳細・商品一覧 |
| `forum_qa` | `forum` | Q&A / Forum Question and Answers | `[itemtype='https://schema.org/Question'], [itemtype='https://schema.org/Answer'], [itemprop='acceptedAnswer'], [itemprop='suggestedAnswer'], .question, .answer` | Q&A サイト・フォーラム |
| `dashboard_grid` | `dashboard` | Dashboard Card / Widget Grid | `.dashboard, .widget-card, .grid-item, .card-grid` | 分析・管理画面 |

セレクタはどれも `HtmlTree` が受け付ける範囲（タグ、`#id`、`.class`、`[attr]`、`[attr=value]`、子孫、`>`）に収める。
`[itemtype*=...]` のような部分一致は使えないので、schema.org の URL は完全一致で並べる。

## 使い方

### Python コードでプリセット指定する (`HtmlSource`)

```python
from html_source import HtmlSource

# パターンキーで指定 (selector は自動設定されます)
source = HtmlSource(pattern="github_readme")
report = source.parse(html, url)
```

### 自動パターン判定機能 (`detect_pattern`)

DOM 構造を解析し、マッチするパターンを候補順（スコア順）で返します。

```python
import blueprobe

matches = blueprobe.detect_pattern(html)
if matches:
    top_pattern = matches[0]["pattern"]
    print(f"判定されたパターン: {top_pattern['key']} ({top_pattern['label']})")
```

### CLI から一覧と指定を実行する

```bash
# 利用可能なパターン一覧を表示
uv run python blueprobe.py --list-patterns

# 特定のパターンプリセットを指定して再解析を実行
uv run python blueprobe.py --source html_source --pattern github_readme --cache <QueRyuのキャッシュ>
```

`--pattern` は `--source html_source` 専用です。別の取得元との組み合わせや、
未知・空のパターン名はキャッシュを読む前に CLI エラー（終了コード 2）になります。
大文字小文字と前後の空白は `get_pattern()` と同様に正規化します。
`--list-patterns` は取得元・キャッシュ不要で、`--pattern` とは同時指定できません。
再解析は保存済み本文と検証済み snapshot を利用し、ネットワークで再取得しません。

既定の抽出器には、セレクタのカンマ区切りと `[role='main']` に対応した
`mcp-toolcall-lab` が必要です（[互換修正 PR #140](https://github.com/myon-bioinformatics/mcp-toolcall-lab/pull/140)）。
CI は対応済みの commit を固定し、全8プリセットを実際の抽出器で再解析します。

## 文書の分類 (`classify_document`) と出力契約

`detect_pattern()` はセレクタが当たった数だけで並べる（既存の互換のため変更しない）。
`classify_document(html)` はそれに加えて、空の要素を数えず、構造データ・Shadow DOM・表の種類・CSR の空殻を観測する。
**観測と抽出だけ**で、変換・整形はしない（変換は別プロジェクト、並べ替え・絞り込みは QueRyu の担当）。

CLI: `uv run python blueprobe.py --classify saved.html`（JSON を出力、ネットワークなし）

### derived の形 (`blueprobe-dom-classification/1`)

```json
{
  "schema": "blueprobe-dom-classification/1",
  "status": "matched | fallback | client_rendered | insufficient | empty",
  "patterns": [{"pattern": {"key": "...", "label": "...", "category": "...", "selector": "...",
                "description": "...", "example_sites": []},
                "score": 0, "matched_nodes": 0, "selector_used": "<部分セレクタ> | structured_data"}],
  "signals": ["hashed_class_names", "declarative_shadow_dom", "multiple_articles", "nested_articles",
              "layout_tables", "json_ld", "json_ld_invalid", "microdata", "opengraph",
              "empty_app_shell", "fallback:main_landmark | fallback:article | fallback:body"],
  "landmarks": {"main": 1, "article": 2, "role=main": 1},
  "articles": {"total": 0, "top_level": 0, "nested": 0},
  "structured_data": {"json_ld_types": ["Product"], "json_ld_invalid": 0,
                      "microdata_types": ["https://schema.org/Product"], "itemprops": ["name", "price"],
                      "opengraph": {"og:type": "product"}},
  "shadow_roots": {"open": 0, "closed": 0},
  "tables": [{"index": 0, "kind": "data | layout", "reasons": ["th", "caption"], "rows": 2, "nested": false}],
  "text_chars": 0,
  "hashed_class_ratio": 0.0
}
```

下流はこの形だけに依存する。キーを消す・意味を変えるときは `schema` の版を上げる。

### status の意味

| status | 条件 |
|---|---|
| `empty` | 入力が空 |
| `client_rendered` | 見える文字が 20 字未満で、`#app` / `#root` / `#__next` などの空のマウント先か、`src` 付き・module の script がある（CSR の空殻）。`patterns` は空にして誤判定しない |
| `insufficient` | 見える文字が 20 字未満で、空殻の手がかりもない |
| `matched` | 汎用（`generic_main` / `reader_page`）以外のプリセットが、`main` / `[role='main']` / `#main` / `#content` 以外の部分セレクタで文字のある要素に当たった |
| `fallback` | それ以外。難読化クラス（`sc-…`、`css-…`、CSS Modules）などで名前付きクラスが無いとき、HTML5 の意味タグと ARIA role の当たりだけで判断している |

### 観測のきまり

- **構造データ**: JSON-LD（`script[type=application/ld+json]`、`@graph` と入れ子の `@type` も拾う）、microdata（`itemscope` + `itemtype`、`itemprop`）、OpenGraph（`meta[property^=og:]`）。型は分類の手がかり（score +5）にだけ使い、DOM で当たらなければ `matched_nodes: 0`、`selector_used: "structured_data"` になる
- **Declarative Shadow DOM**: `<template shadowrootmode="open|closed">` の中身は見える文字として数える。ただの `<template>` は数えない
- **article**: 入れ子（コメントなど）と最上位を分けて数える
- **表**: `th` / `caption` / `thead` / `scope` があればデータ表。`role=presentation|none`、表を含む、見出しなしでセルにブロック要素、見出しなしで1行以下、のどれかならレイアウト表
- 見える文字に `script` / `style` / `noscript` / 通常の `template` は含めない

### まだ試していないもの

- JS 実行後の DOM（CSR は空殻として判定するだけで、描画はしない）
- `attachShadow()` で作られる命令的な Shadow DOM、iframe の中身
- Canvas / WebGL で描く文字
- RDFa（`vocab` / `typeof`）
- 実在サイトの保存 HTML による精度評価（今回の fixture はすべて手書き）
