# 2026年の確かめ（R18）の部分実行: 結果（探索）

[research/R18-confirmation-2026.md](../../research/R18-confirmation-2026.md) に事前登録した手順のうち、**試合の記録だけから作れる列で `[confirm].detail` の命題を 2026年の 12 単位に当てた**結果です。`../r18_partial_confirmation.py` が作りました。**正規の `outputs/confirmation.md` の代わりではなく、そのファイルは変更していません**（正規の手順 = `pipeline.toml` の `years` を 2012-2026 にして取得から走らせる実行は、していません）。

## 何をして、何が足りないか

- 入力: [games_table_from_observed.py](../games_table_from_observed.py) で保存済みの観測（2013〜2025年は `recovered-inputs/observed/games_raw.json`、2026年は `season-2026/observed/games.jsonl` の確定した 858 試合）から作った試合の表。球団年ごとの G/W/L/T/RF/RA は確定済みの値と全部一致する
- その表から sakanalytics を走らせ、2026年の 12 単位の行を作った（`r18_partial_panel_2026.jsonl`、318 列）。**確定済みの season.jsonl にあって、この表にない 72 列（`inn_*` = イニング集計、`bat_*` = チーム打撃）は、2026年の単位では空にした**。その列を使う命題は判定不能になる
- 2012年の試合は入力にない。`rf_low_streak` など「何年続いているか」の値が、2013年から数え始めた値になる違いがありうる（2026年の判定に使う「2年以上」では結果が変わらない）
- **先に対照**: 同じ処理を確定済み season.jsonl の 156 単位（2012〜2025年、2020年を除く）に当てて、R18 に登録された学習データの数（P52 の逆の判例 5・判例 10・B 78・A 78、P64 の前件 26 のうち B 22、P79 の前件 79 のうち成立 52、P51 の中日 13 年中 10 など）が全部再現できなければ、2026年の結果を出さずに止まる。再現できた
- 読み方は R18 の登録のまま。単位が 12 しかないので統計の判定はせず、「確かめられた」とは書かない

## 結果（要点）

| 命題 | 2026年の 12 単位 | 読み |
|---|---|---|
| **P52**（式1） | 成立 6（B クラス 6 球団すべて）、どちらも当たらない 6（A クラス 6 球団すべて）。**判例 0、逆の判例 0**（期待値は 0.77 件、0.38 件） | 登録した読み方では**「学習データと矛盾しない」**（逆の判例 2 件以上でも、判例 3 件以上でもない）。中日は前件の一部を先に知っていた弱い単位 |
| P50 | 成立 6（A クラス 6 球団すべて）、どちらも当たらない 6。判例 0、逆の判例 0（期待値 0.69 件、0.77 件） | 記録のみ。P52 と並べて読む |
| P64 | 前件に当たる単位は 1（広島、B クラス、成立）。判例なし（学習データの率なら前件に当たる単位は 2 前後） | 記録のみ |
| P62（式2） | 12 単位とも判定不能 | R18 が先に書いたとおり（2026年のイニング単位の集計が手元にない）。データが足されたときに判定する |
| P78・P76・P80（式3） | 範囲に入る単位なし（4位で分布の見込み 0.5 以上のチームがない／得失点差がプラスなのに B クラスのチームがない） | R18 の期待値 0〜2 の下限 |
| P79（式4、鏡） | 前件に当たる 6 単位（学習データの率なら 6 前後）のうち成立 3（オリックス・中日・楽天）、判例 3（日本ハム・巨人・西武） | 成立が半分を**超えない（ちょうど半分）**。R18 の読み方どおり、単位が少ないので鏡の形は取り下げない |
| P51 | 中日の分布の見込みは 0.5 未満（成立） | 弱い単位（中日は前件の一部を先に知っていた） |

要点: **登録した読み方に当てる限り、P52 の 2026年の結果は学習データと矛盾しない。判例も逆の判例も出なかった**。P79 は半分ちょうどで、2026年の材料としては中立。

## 限界

- 12 単位、しかも A・B は全球団すでに知られていた。期待どおりでも「確かめられた」とは書かない
- 中日は前件の一部を先に知っていた（P52・P51 は弱い単位）
- 部分実行: イニング・打撃の列がなく、2012年の試合がない。正規の実行でどう変わるかは、その実行を待つ。P62 など、ここで判定不能だった命題は、正規の実行でも 2026年のイニング集計がなければ判定不能のまま
- 試合の表から行を作る手順は 1 ビットまで同じには再現されない（`alloc_*_opp` などで 1e-15 前後の違いが出る。groupby の順による）。判定は閾値との比較で、この大きさでは変わらない。保存済みの 2026年の行からの再現（`--panel`）は、結果がバイト単位で同じになる

## 置いたファイル

- `r18_partial_confirmation.md` / `.json`: 結果（命題ごとの学習データ側・2026年の数、期待値、読み、単位ごとの状態、空にした列）
- `r18_partial_panel_2026.jsonl`: 2026年の 12 単位の行（sakanalytics が試合の表から作ったもの、318 列）

## 再現

```sh
python cycles/c001-chunichi/exploratory/games_table_from_observed.py \
    --games-raw cycles/c001-chunichi/recovered-inputs/observed/games_raw.json --season-jsonl cycles/c001-chunichi/outputs/season.jsonl \
    --season-2026 cycles/c001-chunichi/season-2026/observed/games.jsonl --totals-2026 cycles/c001-chunichi/season-2026/derived/team_totals.jsonl --out games.jsonl
uv run --locked python cycles/c001-chunichi/exploratory/r18_partial_confirmation.py --games games.jsonl \
    --config cycles/c001-chunichi/analysis.toml --propositions cycles/c001-chunichi/propositions.toml \
    --committed cycles/c001-chunichi/outputs/season.jsonl --out-md r18.md --out-json r18.json --out-panel-2026 panel.jsonl --repo .   # 約 1 分
# 保存済みの 2026年の行から読み方だけ当て直す（数秒）: --games の代わりに --panel r18_partial_panel_2026.jsonl
```

保存済みの行からの再現は [tests/test_c001_r18_partial_confirmation.py](../../../../tests/test_c001_r18_partial_confirmation.py) が、結果のバイト単位の一致と、学習データ側の数が登録と違うときに止まることを確かめています。
