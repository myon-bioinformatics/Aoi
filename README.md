# PythDRagoras（実装）

> 本当にその説明で十分か？

思想は [docs/PythDRagoras.md](../docs/PythDRagoras.md)。ここはその検証部分の実装。

| 関数 | 中身 |
|---|---|
| `apply_exclusions` | 分析から除くシーズンを適用する。理由のない除外は受け付けず、何を・なぜ除いたかを結果に残す |
| `cumulative_test` | 期待勝率からのずれの累積を z 値にする（固定指数・可変指数の両方） |
| `rank_test` | 順位が下位に偏る珍しさ。帰無仮説（各シーズン独立に一様）と、全球団の実際の記録との比較を並べる |
| `summary_markdown` | 検証記録。原因は書かない。競合仮説の状態を並べる |

帰無仮説は各シーズンを独立とみなすため、前年からの戦力の持ち越しを無視し、珍しさを過大に見積もる。
そのため、同じ期間の全球団との比較（経験的基準）を必ず並べる。

```bash
uv run python pythdragoras/pythdragoras.py --season cycles/c001-chunichi/outputs/season.jsonl \
  --config cycles/c001-chunichi/analysis.toml --hypotheses cycles/c001-chunichi/hypotheses.toml \
  --outdir cycles/c001-chunichi/outputs
```
