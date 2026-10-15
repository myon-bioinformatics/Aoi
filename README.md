# SakAnalytics

> 数字は語る。だが、まだ語りきっていないことがある。

![SakAnalytics](../docs/images/sakanalytics.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

観測データセット（1試合1行: `key, date, home, away, hs, as`）から、チーム×シーズンの指標を作る。
測るだけで、除外や良し悪しの判断はしない（それは PythDRagoras と分析設定の仕事）。

チームの所属と表示名は分析設定の `[teams]` で明示的に与える。定義のないチームが現れたら、黙って捨てずにエラーにする。

主な列は `sakanalytics.py` の冒頭に一覧がある。順位（`rank`）は勝率から計算した派生値で、
公式の同率時の規定は再現しないため、同率には `rank_tie = true` の印をつける。

```bash
uv run python sakanalytics/sakanalytics.py --games data/observations/npb_calendar/games.jsonl \
  --config cycles/c001-chunichi/analysis.toml --out cycles/c001-chunichi/outputs/season.jsonl
```

## 年間チーム表と架空リーグ

`annual_audit.py` は公式の年成績から、整数項目・率の公表桁・表間の共通列・既存年表との一致を照合する。
`synthetic_league.py` は、リーグ全体の年成績を先に固定し、対戦容量を整数最大流で確認してから試合結果へ展開する。
主対象は2013〜2026年。既定は3条件×各1組の14年間で、全14年の年成績と試合集計が一致すれば合格とする。
過去年の網羅や生成件数の増加は要求しない。2013年以前は通常の解析・較正・合格判定から分けて参考保管する。
得失点が同じでも勝敗配分の違う例を作れる。生成例は実測件数に加算しない。
手順・生成族・完了条件は [c001の取得・架空検証記録](../cycles/c001-chunichi/annual-history-synthetic.md)。
