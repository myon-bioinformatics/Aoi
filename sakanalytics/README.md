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

## 条件付き生成・能力予算・得点尺度の実験

`league_laboratory.py` は、得失点を固定して隠した勝敗を補完する実験、同じポイント予算で能力を配分する実験、
同じ整数スコアを6種類の分析単位で測る実験を実行する。年成績で先に検査し、代表例だけ試合へ展開する。
生成不能例・推奨条件の通過/不通過・修正/新規FP/FN・尺度間の順位変化を残し、次の命題の材料にする。

```bash
python -S sakanalytics/league_laboratory.py
```

設定は [league-laboratory.toml](../cycles/c001-chunichi/league-laboratory.toml)、
観測と解釈は [R29](../cycles/c001-chunichi/research/R29-league-laboratory.md)。
架空モデルの仮定下の探索で、既存命題・合格条件・実測スコアは変更しない。

## 全命題の共通評価軸とseed感度

PythDRagorasは全命題・評価した各形にPrecision / Recall / F1 / Accuracy /
Balanced Accuracy / MCCを付ける。分母0・定数予測などは`None`と理由を残し、正式判定には使わない。
合成入力がない命題もseed評価の項目を持ち、未評価は`None`。特定の再評価候補だけに限定しない。

```bash
python sakanalytics/proposition_seed_audit.py
# 年成績の証跡も同じ条件で作り直す場合だけ:
python sakanalytics/proposition_seed_audit.py --generate-plans
```

既存の年成績合成3系列と、能力予算のseed 0〜9・2023〜2026年・全28配分・減衰0/0.4を使う。
証跡は`cycles/c001-chunichi/outputs/exploratory/proposition-evaluation/`。
通常のc001 pipelineも`--seed-evaluation`で診断を読み、`outputs/index.md`へ全命題を並べる。
年・命題定義・生成条件が同じ群内だけでseedの振れを測り、条件変更の効果とは分ける。
合成入力は13命題に対応し、必要な列や実在球団への対応付けがない命題は未評価のままにする。
