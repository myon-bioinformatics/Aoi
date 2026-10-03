# PythDRagoras（実装）

> 本当にその説明で十分か？

![PythDRagoras](../docs/images/pythdragoras.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

思想は [docs/PythDRagoras.md](../docs/PythDRagoras.md)。ここはその検証部分の実装。

| 関数 | 中身 |
|---|---|
| `apply_exclusions` | 分析から除くシーズンを適用する。理由のない除外は受け付けず、何を・なぜ除いたかを結果に残す |
| `cumulative_test` | 期待勝率からのずれの累積を z 値にする（固定指数・可変指数の両方） |
| `rank_test` | 順位が下位に偏る珍しさ。帰無仮説（各シーズン独立に一様）と、全球団の実際の記録との比較を並べる |
| `summary_markdown` | 検証記録。原因は書かない。競合仮説の状態を並べる |
| `propositions.py` | 命題・判例・異議あり（仕様は [docs/propositions.md](../docs/propositions.md)） |

## 命題と「異議あり」

説明を「もし A ならば B」の命題として書き、元の命題・対偶・逆・裏の4つの形で判定する。
判定の基準は、結果を見る前に言葉で宣言する（必ず / ほとんど 0.90 / 概ね 0.75 / 多くの場合 0.50）。

```text
判定（上から順に最初に当てはまるもの）
  n < min_n                      → 判断保留
  必ず かつ 反例なし / あり        → 支持 / 棄却
  区間の下限 ≥ 基準                → 支持
  区間が基準をまたぐ              → 判断保留
  区間の上限 < 基準 かつ 関係あり   → 修正（主張が強すぎる）
  区間の上限 < 基準 かつ 関係なし   → 棄却
```

反例が1件でもあれば、判定が「支持」でも **異議あり** として判例を並べる。支持された説明の中の反例こそが、説明が足りなくなる場所だからである。
除外したシーズンの判例は、統計からは外しても「除外中の判例」として必ず表示する。

外部の主張（記事・レポート・他のAI）は、観測ではなく claim として登録し、パイプラインで再現できるかを確かめる。

帰無仮説は各シーズンを独立とみなすため、前年からの戦力の持ち越しを無視し、珍しさを過大に見積もる。
そのため、同じ期間の全球団との比較（経験的基準）を必ず並べる。

```bash
uv run python pythdragoras/pythdragoras.py --season cycles/c001-chunichi/outputs/season.jsonl \
  --config cycles/c001-chunichi/analysis.toml --hypotheses cycles/c001-chunichi/hypotheses.toml \
  --propositions cycles/c001-chunichi/propositions.toml --claims cycles/c001-chunichi/claims.toml \
  --outdir cycles/c001-chunichi/outputs
```
