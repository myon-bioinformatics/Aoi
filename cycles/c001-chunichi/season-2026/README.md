# 2026年レギュラーシーズンの確定記録

10月3日時点の保存済み観測に、**10月4〜8日の9試合と、10月3日に未終了だった2試合の確定記録**を追加した別データセットです。2026年10月25日に残りの日付順で取得し直しました。**858試合、12球団×143試合**を確認し、試合から再集計した `G/W/L/T/RF/RA` の **72値すべて**が、10月15日保存の公式年次記録と一致します。

## ファイルと境界

- [observed/game_updates.jsonl](observed/game_updates.jsonl): 今回取得した11試合の解析結果。終了状態、球団、日付、URL、イニングと得点のみを対象とし、選手記録は追加していません。新規行では `1x` などの原表記を `*_inning_cells` に保持し、数値集計用 `*_inn` と分けています。
- [observed/games.jsonl](observed/games.jsonl): 2026年の確定レギュラーシーズン858試合。元の確定847行をそのまま保持し、新しい11行を合流します。交流戦を含み、オールスター・CS・日本シリーズ・中止・未終了を含みません。欠損の推測補完や143試合への切り詰めは行いません。
- [observed/annual_totals.json](observed/annual_totals.json): 2つの保存済み元ZIPの実年次行から取り出した12球団の成績と来歴。10月15日保存の公式ページ10種類を現行parserで再解析し、各ZIPの96カテゴリ行と一致、unknown 0を確認しました。年次ページを今回新規取得したという意味ではありません。元ZIP全体やHTMLはここには複製していません。
- [derived/team_totals.jsonl](derived/team_totals.jsonl): 試合行から作った年次集計。観測した年次表とは別ファイルです。
- [provenance/acquisition.jsonl](provenance/acquisition.jsonl): 今回取得した11試合と日程一覧のURL・取得時刻/日・HTTP状態・バイト数・SHA-256。日程一覧から選んだのは10月4〜8日の通常カードだけです。
- [provenance/reconciliation.json](provenance/reconciliation.json): 入力ハッシュ、追加/確定URL、件数、72値の照合結果。

元の [games_raw.json](../recovered-inputs/observed/games_raw.json) と公開済み原本ZIPはバイト変更していません。過去の進行中2行も原本側には残します。以前の原本のイニング表現を遡って改善したものではありません。既存の409列研究パネル、モデル出力、暫定レート報告、架空データは変更しておらず、研究の結論を更新するものではありません。QueRyuの `data/observations/npb_calendar/games.jsonl` に名前だけ変えて登録したものでもありません。

## オフライン再現

リポジトリ直下で、保存入力から派生ファイルを再生成できます。ネットワーク取得は行いません。

```sh
python scripts/reconcile_season_2026.py
python scripts/reconcile_season_2026.py --check
pytest -q tests/test_season_2026.py
```

照合は球団ごとの143試合、勝敗分と得失点、URL重複、終了状態、日付範囲、イニング合計を検査します。保存済み847試合を今回すべて公式ページから再取得した独立検証ではありません。年次合計一致だけでイニング単位の正しさや研究上の主張を保証しません。再取得した全文HTMLはこの変更の公開対象外です。

## 出典・利用条件

試合の出典は各行のNPB公式URL、年次値の出典と保存日時は `annual_totals.json` の `source_pages` を参照してください。元ZIPからの回収は保存バイトの同一性を検査したもので、出典の権利許諾を示しません。今回の公開指示はこの解析済みレギュラーシーズン更新に限られ、NPBからの再配布許諾やAoiのMITライセンスの原資料への適用を意味しません。[既存の公開範囲・未確認事項](../recovered-inputs/README.md#出典と公開範囲)を維持します。新しい全文HTML、ポストシーズン、私的データは含めません。
