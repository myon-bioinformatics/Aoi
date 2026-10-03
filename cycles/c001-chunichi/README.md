# サイクル1: 中日ドラゴンズ

GENESIS.md の「Note On Evidence」で予告した、問いを生んだ観測の再構築。

## 問い

- 観測: 中日ドラゴンズは長いあいだ、セ・リーグの下位に位置するシーズンが続いた（**取得したデータで数え直す**。記憶では書かない）
- 問い: 既存の指標（得失点・ピタゴラス期待勝率）は、この結果を十分に説明しているか
- 順位: 偏りがなければ、各シーズンの順位の期待値は1〜6のどれも同じはず。下位（4〜6位）がどれだけ続いているかを観測する。CS の有無は扱わない（リーグによって制度が異なり、後からできた制度でもあるため）

## 範囲と判断

| 項目 | 内容 | 記録場所 |
|---|---|---|
| 期間 | 2012〜2025年の公式戦（交流戦を含む） | `pipeline.toml` の `years` |
| 取得元 | npb.jp の月別公式戦カレンダー（最終スコアのみ） | `blueprobe/docs/npb_calendar.md` |
| 除外 | 2020年（理由は `analysis.toml`） | `outputs/exclusions.json` |
| 比較対象 | セ・リーグの6球団 | `analysis.toml` の `[focus]` |
| 保留 | イニング単位のデータ（逆転・前半/後半・連続無得点） | `hypotheses.toml` |

## 実行

```bash
python nagoyaction/nagoyaction.py doctor cycles/c001-chunichi/pipeline.toml
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml --receipt data/receipts/c001.jsonl
```

GitHub 上では Actions の「cycle c001 (chunichi)」を手動実行する。中身は同じコマンド。
取得は約126リクエスト（3秒間隔で約7分）で、2回目以降は進行中のシーズンだけを確認する。

## 成果物（`outputs/`、git で管理する）

| ファイル | 中身 |
|---|---|
| `observed.md` | 年ごとの取得結果、採用しなかった件数、未知の表記（数字は伏せる）、試合数の照合 |
| `season.jsonl` | チーム×シーズンの指標（派生値） |
| `cumulative.jsonl` | 期待勝率からのずれの累積と z 値 |
| `rank_test.jsonl` | 順位の偏りの検定（帰無仮説と全球団比較） |
| `exclusions.json` | 除外したシーズンと理由 |
| `summary.md` | 検証記録。観測した数だけを書き、原因は書かない |

生のページ（`data/raw/`）と1試合ごとの観測（`data/observations/`）は git に入れない。
