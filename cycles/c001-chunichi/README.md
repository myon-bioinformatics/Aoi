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
| 命題 | 得失点・ピタゴラス・得点/失点順位と順位の関係、中日についての命題（P1〜P8、事前登録） | `propositions.toml` |
| 外部の主張 | 外部レポートの数値（C1〜C8）と解釈（C9, C10） | `claims.toml`、`references/` |

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
| `objections.md` | 命題ごとの判定と「異議あり」（判例の一覧、除外中の判例） |
| `propositions.jsonl` | 同じ内容の機械向け形式（命題ファイルの SHA-256 とコードの版つき） |
| `claims.json` | 外部の主張の再現結果 |

生のページ（`data/raw/`）と1試合ごとの観測（`data/observations/`）は git に入れない。
