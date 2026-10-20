# DOM 構造パターン・プリセット設計

実装は [`blueprobe.py`](../blueprobe.py)。[`dom_patterns.py`](../dom_patterns.py) は同じ関数を再公開する。

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
import dom_patterns

matches = dom_patterns.detect_pattern(html)
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
