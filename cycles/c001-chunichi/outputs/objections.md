# 異議あり — 命題の判定記録（自動生成）

判定基準は結果を見る前に命題ファイルに書いたもの（docs/propositions.md）。
命題ファイル SHA-256: `19aa3bec6f20e6b87c90c1bea196578dcf6e2c352c11e29aadbbff3b549454f7` / コード: `7c7feff0002beb08f44749ead68f118295262743`

判定は命題がその範囲で成り立つかどうかだけを示し、原因は示さない。

## P1: 得失点差がプラスなら、上位半分（Aクラス）である

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 12 件: h-2013, d-2019, h-2021, l-2015, c-2022 ほか
- もし: `rd > 0` ならば: `upper_half == True`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 73 | 61 | 0.84 [0.73, 0.90] | 0.50 | 1.67 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 66 | 0.85 [0.75, 0.91] | 0.53 | 1.59 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 61 | 0.78 [0.68, 0.86] | 0.47 | 1.67 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 83 | 66 | 0.80 [0.70, 0.87] | 0.50 | 1.59 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 12 件（対偶の判例も同じ）

- ソフトバンク 2013: rd=98, upper_half=False, rank=4, rank_pythag=1, wins_vs_pythag=-8.37 / surprise=3
  - ソフトバンク 2013 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- 中日 2019 **(focus)**: rd=19, upper_half=False, rank=5, rank_pythag=2, wins_vs_pythag=-4.71 / surprise=3
  - 中日 2019 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- ソフトバンク 2021: rd=71, upper_half=False, rank=4, rank_pythag=1, wins_vs_pythag=-8.47 / surprise=3
  - ソフトバンク 2021 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- 西武 2015: rd=58, upper_half=False, rank=4, rank_pythag=2, wins_vs_pythag=-6.07 / surprise=2
  - 西武 2015 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- 広島 2022: rd=8, upper_half=False, rank=5, rank_pythag=3, wins_vs_pythag=-4.93 / surprise=2
  - 広島 2022 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- 楽天 2012: rd=24, upper_half=False, rank=4, rank_pythag=3, wins_vs_pythag=-3.07 / surprise=1
  - 楽天 2012 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- 広島 2015: rd=32, upper_half=False, rank=4, rank_pythag=3, wins_vs_pythag=-5.18 / surprise=1
  - 広島 2015 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- 巨人 2017: rd=32, upper_half=False, rank=4, rank_pythag=3, wins_vs_pythag=-1.94 / surprise=1
  - 巨人 2017 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- ロッテ 2019: rd=31, upper_half=False, rank=4, rank_pythag=3, wins_vs_pythag=-3.65 / surprise=1
  - ロッテ 2019 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- 巨人 2023: rd=16, upper_half=False, rank=4, rank_pythag=3, wins_vs_pythag=-1.50 / surprise=1
  - 巨人 2023 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3, H4
- ほか 2 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 17 件（裏の判例も同じ）

- 阪神 2015: rd=-85, upper_half=True, rank=3, rank_pythag=6, wins_vs_pythag=+10.25 / surprise=-3
  - 阪神 2015 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- 西武 2012: rd=-2, upper_half=True, rank=2, rank_pythag=4, wins_vs_pythag=+4.74 / surprise=-2
  - 西武 2012 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- DeNA 2019: rd=-15, upper_half=True, rank=2, rank_pythag=4, wins_vs_pythag=+2.59 / surprise=-2
  - DeNA 2019 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- 阪神 2019: rd=-28, upper_half=True, rank=3, rank_pythag=5, wins_vs_pythag=+3.68 / surprise=-2
  - 阪神 2019 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- DeNA 2022: rd=-37, upper_half=True, rank=2, rank_pythag=4, wins_vs_pythag=+7.13 / surprise=-2
  - DeNA 2022 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- 広島 2023: rd=-15, upper_half=True, rank=2, rank_pythag=4, wins_vs_pythag=+6.41 / surprise=-2
  - 広島 2023 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- ロッテ 2013: rd=-12, upper_half=True, rank=3, rank_pythag=4, wins_vs_pythag=+4.35 / surprise=-1
  - ロッテ 2013 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- 阪神 2014: rd=-15, upper_half=True, rank=2, rank_pythag=3, wins_vs_pythag=+5.12 / surprise=-1
  - 阪神 2014 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- ロッテ 2015: rd=-2, upper_half=True, rank=3, rank_pythag=4, wins_vs_pythag=+2.23 / surprise=-1
  - ロッテ 2015 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- DeNA 2016: rd=-16, upper_half=True, rank=3, rank_pythag=2, wins_vs_pythag=0.767 / surprise=1
  - DeNA 2016 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2, H3, H4
- ほか 7 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: rd=42, upper_half=False, rank=4, rank_pythag=2, wins_vs_pythag=-5.42
- 楽天 2020: rd=35, upper_half=False, rank=4, rank_pythag=2, wins_vs_pythag=-4.32

## P2: ピタゴラス期待勝率でリーグ3位以内なら、実際も3位以内である

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 11 件: h-2013, d-2019, h-2021, l-2015, c-2022 ほか
- もし: `rank_pythag <= 3` ならば: `rank <= 3`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 78 | 67 | 0.86 [0.76, 0.92] | 0.50 | 1.72 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 67 | 0.86 [0.76, 0.92] | 0.50 | 1.72 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 67 | 0.86 [0.76, 0.92] | 0.50 | 1.72 | 0.000 | 0 | 支持 | 1 |
| 裏 | 78 | 67 | 0.86 [0.76, 0.92] | 0.50 | 1.72 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 11 件（対偶の判例も同じ）

- ソフトバンク 2013: rank_pythag=1, rank=4, rd=98, wins_vs_pythag=-8.37 / surprise=3
  - ソフトバンク 2013 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- 中日 2019 **(focus)**: rank_pythag=2, rank=5, rd=19, wins_vs_pythag=-4.71 / surprise=3
  - 中日 2019 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- ソフトバンク 2021: rank_pythag=1, rank=4, rd=71, wins_vs_pythag=-8.47 / surprise=3
  - ソフトバンク 2021 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- 西武 2015: rank_pythag=2, rank=4, rd=58, wins_vs_pythag=-6.07 / surprise=2
  - 西武 2015 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- 広島 2022: rank_pythag=3, rank=5, rd=8, wins_vs_pythag=-4.93 / surprise=2
  - 広島 2022 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- 楽天 2012: rank_pythag=3, rank=4, rd=24, wins_vs_pythag=-3.07 / surprise=1
  - 楽天 2012 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- 広島 2015: rank_pythag=3, rank=4, rd=32, wins_vs_pythag=-5.18 / surprise=1
  - 広島 2015 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- 巨人 2017: rank_pythag=3, rank=4, rd=32, wins_vs_pythag=-1.94 / surprise=1
  - 巨人 2017 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- 広島 2019: rank_pythag=3, rank=4, rd=-10, wins_vs_pythag=+1.07 / surprise=1
  - 広島 2019 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- ロッテ 2019: rank_pythag=3, rank=4, rd=31, wins_vs_pythag=-3.65 / surprise=1
  - ロッテ 2019 は「rank_pythag <= 3」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2, H3, H4
- ほか 1 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 11 件（裏の判例も同じ）

- 阪神 2015: rank_pythag=6, rank=3, rd=-85, wins_vs_pythag=+10.25 / surprise=-3
  - 阪神 2015 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- 西武 2012: rank_pythag=4, rank=2, rd=-2, wins_vs_pythag=+4.74 / surprise=-2
  - 西武 2012 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- DeNA 2019: rank_pythag=4, rank=2, rd=-15, wins_vs_pythag=+2.59 / surprise=-2
  - DeNA 2019 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- ソフトバンク 2019: rank_pythag=4, rank=2, rd=18, wins_vs_pythag=+5.02 / surprise=-2
  - ソフトバンク 2019 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- 阪神 2019: rank_pythag=5, rank=3, rd=-28, wins_vs_pythag=+3.68 / surprise=-2
  - 阪神 2019 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- ロッテ 2021: rank_pythag=4, rank=2, rd=14, wins_vs_pythag=+3.62 / surprise=-2
  - ロッテ 2021 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- DeNA 2022: rank_pythag=4, rank=2, rd=-37, wins_vs_pythag=+7.13 / surprise=-2
  - DeNA 2022 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- 広島 2023: rank_pythag=4, rank=2, rd=-15, wins_vs_pythag=+6.41 / surprise=-2
  - 広島 2023 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- ロッテ 2013: rank_pythag=4, rank=3, rd=-12, wins_vs_pythag=+4.35 / surprise=-1
  - ロッテ 2013 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- ロッテ 2015: rank_pythag=4, rank=3, rd=-2, wins_vs_pythag=+2.23 / surprise=-1
  - ロッテ 2015 は「rank <= 3」を満たすのに「rank_pythag <= 3」を満たさない。なぜか？ → H2, H3, H4
- ほか 1 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: rank_pythag=2, rank=4, rd=42, wins_vs_pythag=-5.42
- 楽天 2020: rank_pythag=2, rank=4, rd=35, wins_vs_pythag=-4.32

## P3: 得点がリーグ2位以内なら、3位以内である

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 16 件: h-2013, h-2021, l-2015, c-2022, e-2023 ほか
- もし: `rank_rf <= 2` ならば: `rank <= 3`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 53 | 37 | 0.70 [0.56, 0.80] | 0.50 | 1.40 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 62 | 0.79 [0.69, 0.87] | 0.66 | 1.20 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 78 | 37 | 0.47 [0.37, 0.58] | 0.34 | 1.40 | 0.000 | 0 | 修正 | 2 |
| 裏 | 103 | 62 | 0.60 [0.51, 0.69] | 0.50 | 1.20 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 16 件（対偶の判例も同じ）

- ソフトバンク 2013: rank_rf=1, rank=4, rank_ra=3, rd=98 / surprise=3
  - ソフトバンク 2013 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- ソフトバンク 2021: rank_rf=2, rank=4, rank_ra=1, rd=71 / surprise=3
  - ソフトバンク 2021 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 西武 2015: rank_rf=2, rank=4, rank_ra=4, rd=58 / surprise=2
  - 西武 2015 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 広島 2022: rank_rf=2, rank=5, rank_ra=4, rd=8 / surprise=2
  - 広島 2022 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 楽天 2023: rank_rf=2, rank=4, rank_ra=6, rd=-43 / surprise=-2
  - 楽天 2023 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- DeNA 2013: rank_rf=1, rank=5, rank_ra=6, rd=-56 / surprise=1
  - DeNA 2013 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- ヤクルト 2014: rank_rf=1, rank=6, rank_ra=6, rd=-50 / surprise=1
  - ヤクルト 2014 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- DeNA 2015: rank_rf=2, rank=6, rank_ra=6, rd=-90 / surprise=1
  - DeNA 2015 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- ヤクルト 2016: rank_rf=2, rank=5, rank_ra=6, rd=-100 / surprise=-1
  - ヤクルト 2016 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- ロッテ 2019: rank_rf=2, rank=4, rank_ra=4, rd=31 / surprise=1
  - ロッテ 2019 は「rank_rf <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- ほか 6 件（propositions.jsonl を参照）

**異議あり（主張が強すぎる）** 逆に判例 41 件（裏の判例も同じ）

- 阪神 2015: rank_rf=6, rank=3, rank_ra=5, rd=-85 / surprise=-3
  - 阪神 2015 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- DeNA 2019: rank_rf=3, rank=2, rank_ra=5, rd=-15 / surprise=-2
  - DeNA 2019 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- ソフトバンク 2019: rank_rf=4, rank=2, rank_ra=1, rd=18 / surprise=-2
  - ソフトバンク 2019 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- 阪神 2019: rank_rf=6, rank=3, rank_ra=2, rd=-28 / surprise=-2
  - 阪神 2019 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- DeNA 2022: rank_rf=4, rank=2, rank_ra=3, rd=-37 / surprise=-2
  - DeNA 2022 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- 阪神 2022: rank_rf=5, rank=3, rank_ra=1, rd=61 / surprise=2
  - 阪神 2022 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- 広島 2023: rank_rf=5, rank=2, rank_ra=5, rd=-15 / surprise=-2
  - 広島 2023 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- ソフトバンク 2012: rank_rf=5, rank=3, rank_ra=1, rd=23 / surprise=1
  - ソフトバンク 2012 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- 西武 2013: rank_rf=4, rank=2, rank_ra=3, rd=8 / surprise=-1
  - 西武 2013 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- ロッテ 2013: rank_rf=3, rank=3, rank_ra=5, rd=-12 / surprise=-1
  - ロッテ 2013 は「rank <= 3」を満たすのに「rank_rf <= 2」を満たさない。なぜか？ → H2
- ほか 31 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: rank_rf=1, rank=4, rank_ra=4, rd=35
- 広島 2020: rank_rf=2, rank=5, rank_ra=5, rd=-6

## P4: 失点がリーグで2番目以内に少なければ、3位以内である

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 14 件: d-2019, h-2021, t-2018, c-2015, g-2017 ほか
- もし: `rank_ra <= 2` ならば: `rank <= 3`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 38 | 0.73 [0.60, 0.83] | 0.50 | 1.46 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 64 | 0.82 [0.72, 0.89] | 0.67 | 1.23 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 78 | 38 | 0.49 [0.38, 0.60] | 0.33 | 1.46 | 0.000 | 0 | 修正 | 2 |
| 裏 | 104 | 64 | 0.62 [0.52, 0.70] | 0.50 | 1.23 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 14 件（対偶の判例も同じ）

- 中日 2019 **(focus)**: rank_ra=1, rank=5, rank_rf=5, rd=19 / surprise=3
  - 中日 2019 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- ソフトバンク 2021: rank_ra=1, rank=4, rank_rf=2, rd=71 / surprise=3
  - ソフトバンク 2021 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 阪神 2018: rank_ra=2, rank=6, rank_rf=5, rd=-51 / surprise=2
  - 阪神 2018 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 広島 2015: rank_ra=2, rank=4, rank_rf=3, rd=32 / surprise=1
  - 広島 2015 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 巨人 2017: rank_ra=1, rank=4, rank_rf=4, rd=32 / surprise=1
  - 巨人 2017 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rank_ra=1, rank=5, rank_rf=6, rd=-73 / surprise=-1
  - 中日 2021 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 西武 2023: rank_ra=2, rank=5, rank_rf=6, rd=-30 / surprise=1
  - 西武 2023 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- オリックス 2024: rank_ra=2, rank=5, rank_rf=5, rd=-46 / surprise=1
  - オリックス 2024 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- オリックス 2013: rank_ra=1, rank=5, rank_rf=6, rd=-16 / surprise=0
  - オリックス 2013 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- 中日 2014 **(focus)**: rank_ra=2, rank=4, rank_rf=5, rd=-20 / surprise=0
  - 中日 2014 は「rank_ra <= 2」を満たすのに「rank <= 3」を満たさない。なぜか？ → H2
- ほか 4 件（propositions.jsonl を参照）

**異議あり（主張が強すぎる）** 逆に判例 40 件（裏の判例も同じ）

- 阪神 2015: rank_ra=5, rank=3, rank_rf=6, rd=-85 / surprise=-3
  - 阪神 2015 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- 西武 2012: rank_ra=5, rank=2, rank_rf=1, rd=-2 / surprise=-2
  - 西武 2012 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- DeNA 2019: rank_ra=5, rank=2, rank_rf=3, rd=-15 / surprise=-2
  - DeNA 2019 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- ロッテ 2021: rank_ra=5, rank=2, rank_rf=1, rd=14 / surprise=-2
  - ロッテ 2021 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- DeNA 2022: rank_ra=3, rank=2, rank_rf=4, rd=-37 / surprise=-2
  - DeNA 2022 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- 広島 2023: rank_ra=5, rank=2, rank_rf=5, rd=-15 / surprise=-2
  - 広島 2023 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- 西武 2013: rank_ra=3, rank=2, rank_rf=4, rd=8 / surprise=-1
  - 西武 2013 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- ロッテ 2013: rank_ra=5, rank=3, rank_rf=3, rd=-12 / surprise=-1
  - ロッテ 2013 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- 広島 2014: rank_ra=3, rank=3, rank_rf=2, rd=39 / surprise=1
  - 広島 2014 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- 阪神 2014: rank_ra=4, rank=2, rank_rf=3, rd=-15 / surprise=-1
  - 阪神 2014 は「rank <= 3」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- ほか 30 件（propositions.jsonl を参照）

## P5: 得点がリーグ5位以下なら、下位半分（Bクラス）である

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 8 件: t-2015, t-2019, t-2022, c-2023, h-2012 ほか
- もし: `rank_rf >= 5` ならば: `upper_half == False`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 44 | 0.85 [0.72, 0.92] | 0.50 | 1.69 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 70 | 0.90 [0.81, 0.95] | 0.67 | 1.35 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 44 | 0.56 [0.45, 0.67] | 0.33 | 1.69 | 0.000 | 0 | 修正 | 2 |
| 裏 | 104 | 70 | 0.67 [0.58, 0.76] | 0.50 | 1.35 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 8 件（対偶の判例も同じ）

- 阪神 2015: rank_rf=6, upper_half=True, rank=3, rank_ra=5, rd=-85 / surprise=-3
  - 阪神 2015 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2019: rank_rf=6, upper_half=True, rank=3, rank_ra=2, rd=-28 / surprise=-2
  - 阪神 2019 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2022: rank_rf=5, upper_half=True, rank=3, rank_ra=1, rd=61 / surprise=2
  - 阪神 2022 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 広島 2023: rank_rf=5, upper_half=True, rank=2, rank_ra=5, rd=-15 / surprise=-2
  - 広島 2023 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ソフトバンク 2012: rank_rf=5, upper_half=True, rank=3, rank_ra=1, rd=23 / surprise=1
  - ソフトバンク 2012 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2013: rank_rf=5, upper_half=True, rank=2, rank_ra=1, rd=43 / surprise=0
  - 阪神 2013 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2021: rank_rf=5, upper_half=True, rank=2, rank_ra=2, rd=33 / surprise=0
  - 阪神 2021 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2022: rank_rf=5, upper_half=True, rank=3, rank_ra=1, rd=16 / surprise=0
  - 西武 2022 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 34 件（裏の判例も同じ）

- ソフトバンク 2013: rank_rf=1, upper_half=False, rank=4, rank_ra=3, rd=98 / surprise=3
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- ソフトバンク 2021: rank_rf=2, upper_half=False, rank=4, rank_ra=1, rd=71 / surprise=3
  - ソフトバンク 2021 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 西武 2015: rank_rf=2, upper_half=False, rank=4, rank_ra=4, rd=58 / surprise=2
  - 西武 2015 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 広島 2022: rank_rf=2, upper_half=False, rank=5, rank_ra=4, rd=8 / surprise=2
  - 広島 2022 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 楽天 2023: rank_rf=2, upper_half=False, rank=4, rank_ra=6, rd=-43 / surprise=-2
  - 楽天 2023 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 楽天 2012: rank_rf=4, upper_half=False, rank=4, rank_ra=3, rd=24 / surprise=1
  - 楽天 2012 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- DeNA 2013: rank_rf=1, upper_half=False, rank=5, rank_ra=6, rd=-56 / surprise=1
  - DeNA 2013 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 西武 2014: rank_rf=4, upper_half=False, rank=5, rank_ra=4, rd=-26 / surprise=1
  - 西武 2014 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- ヤクルト 2014: rank_rf=1, upper_half=False, rank=6, rank_ra=6, rd=-50 / surprise=1
  - ヤクルト 2014 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 広島 2015: rank_rf=3, upper_half=False, rank=4, rank_ra=2, rd=32 / surprise=1
  - 広島 2015 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- ほか 24 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rank_rf=6, upper_half=True, rank=3, rank_ra=4, rd=-60
- ロッテ 2020: rank_rf=5, upper_half=True, rank=2, rank_ra=2, rd=-18

## P6: どのチーム・シーズンでも、実際の勝利数はピタゴラス期待勝利数の±5勝以内に収まる

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 36 件: t-2015, t-2022, s-2023, h-2021, d-2012 ほか
- もし: `（すべての単位）` ならば: `wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5`
- 強さ: ほとんど（almost_always, 基準 0.90）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 156 | 120 | 0.77 [0.70, 0.83] | 0.77 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 36 | 0 | 0.00 [0.00, 0.10] | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 36 件（対偶の判例も同じ）

- 阪神 2015: wins_vs_pythag=+10.25, rd=-85, rank=3, rank_pythag=6 / surprise=+10.25
  - 阪神 2015 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- 阪神 2022: wins_vs_pythag=-9.93, rd=61, rank=3, rank_pythag=1 / surprise=-9.93
  - 阪神 2022 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- ヤクルト 2023: wins_vs_pythag=-9.16, rd=-33, rank=5, rank_pythag=5 / surprise=-9.16
  - ヤクルト 2023 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- ソフトバンク 2021: wins_vs_pythag=-8.47, rd=71, rank=4, rank_pythag=1 / surprise=-8.47
  - ソフトバンク 2021 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- 中日 2012 **(focus)**: wins_vs_pythag=+8.45, rd=18, rank=2, rank_pythag=2 / surprise=+8.45
  - 中日 2012 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- ソフトバンク 2013: wins_vs_pythag=-8.37, rd=98, rank=4, rank_pythag=1 / surprise=-8.37
  - ソフトバンク 2013 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- 楽天 2024: wins_vs_pythag=+7.78, rd=-87, rank=4, rank_pythag=5 / surprise=+7.78
  - 楽天 2024 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- 中日 2024 **(focus)**: wins_vs_pythag=+7.56, rd=-105, rank=6, rank_pythag=6 / surprise=+7.56
  - 中日 2024 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- 巨人 2018: wins_vs_pythag=-7.25, rd=50, rank=3, rank_pythag=2 / surprise=-7.25
  - 巨人 2018 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- DeNA 2022: wins_vs_pythag=+7.13, rd=-37, rank=2, rank_pythag=4 / surprise=+7.13
  - DeNA 2022 は「（すべての単位）」を満たすのに「wins_vs_pythag >= -5 かつ wins_vs_pythag <= 5」を満たさない。なぜか？ → H3, H4, H5
- ほか 26 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: wins_vs_pythag=+9.35, rd=-60, rank=3, rank_pythag=5
- 西武 2020: wins_vs_pythag=+6.63, rd=-64, rank=3, rank_pythag=5
- DeNA 2020: wins_vs_pythag=-5.42, rd=42, rank=4, rank_pythag=2

## P9: 1点差の試合で勝ち越していれば、ピタゴラス期待勝利数を上回る

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 20 件: h-2024, f-2025, h-2025, t-2024, e-2012 ほか
- もし: `one_run_net > 0` ならば: `wins_vs_pythag > 0`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 1点差で勝ち越したチーム・シーズンのうち、期待勝利数を下回るものが4分の1を超える
- 注記: 1点差の勝敗とピタゴラスからのずれは計算上も連動しやすい。成り立っても「どうずれたか」の記述で、「なぜか」の説明ではない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 56 | 0.74 [0.63, 0.82] | 0.47 | 1.55 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 82 | 62 | 0.76 [0.65, 0.84] | 0.51 | 1.47 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 74 | 56 | 0.76 [0.65, 0.84] | 0.49 | 1.55 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 80 | 62 | 0.78 [0.67, 0.85] | 0.53 | 1.47 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 20 件（対偶の判例も同じ）

- ソフトバンク 2024: one_run_net=5, wins_vs_pythag=-5.88, rd=217, wpct_1run=0.571, blowout_net=27 / surprise=-5.88
  - ソフトバンク 2024 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- 日本ハム 2025: one_run_net=1, wins_vs_pythag=-5.30, rd=139, wpct_1run=0.509, blowout_net=18 / surprise=-5.30
  - 日本ハム 2025 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- ソフトバンク 2025: one_run_net=5, wins_vs_pythag=-3.92, rd=162, wpct_1run=0.553, blowout_net=15 / surprise=-3.92
  - ソフトバンク 2025 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- 阪神 2024: one_run_net=4, wins_vs_pythag=-3.47, rd=65, wpct_1run=0.540, blowout_net=7 / surprise=-3.47
  - 阪神 2024 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- 楽天 2012: one_run_net=5, wins_vs_pythag=-3.07, rd=24, wpct_1run=0.547, blowout_net=7 / surprise=-3.07
  - 楽天 2012 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- ソフトバンク 2016: one_run_net=5, wins_vs_pythag=-2.97, rd=158, wpct_1run=0.558, blowout_net=16 / surprise=-2.97
  - ソフトバンク 2016 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- 巨人 2024: one_run_net=4, wins_vs_pythag=-2.87, rd=81, wpct_1run=0.543, blowout_net=11 / surprise=-2.87
  - 巨人 2024 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- ソフトバンク 2023: one_run_net=2, wins_vs_pythag=-2.56, rd=29, wpct_1run=0.524, blowout_net=6 / surprise=-2.56
  - ソフトバンク 2023 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- 巨人 2015: one_run_net=1, wins_vs_pythag=-2.40, rd=46, wpct_1run=0.508, blowout_net=3 / surprise=-2.40
  - 巨人 2015 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- 阪神 2013: one_run_net=2, wins_vs_pythag=-2.40, rd=43, wpct_1run=0.523, blowout_net=16 / surprise=-2.40
  - 阪神 2013 は「one_run_net > 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H8
- ほか 10 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 18 件（裏の判例も同じ）

- DeNA 2022: one_run_net=-1, wins_vs_pythag=+7.13, rd=-37, wpct_1run=0.490, blowout_net=-4 / surprise=+7.13
  - DeNA 2022 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- 中日 2017 **(focus)**: one_run_net=-3, wins_vs_pythag=+5.29, rd=-136, wpct_1run=0.463, blowout_net=-22 / surprise=+5.29
  - 中日 2017 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- DeNA 2018: one_run_net=-1, wins_vs_pythag=+3.92, rd=-70, wpct_1run=0.486, blowout_net=-16 / surprise=+3.92
  - DeNA 2018 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ロッテ 2021: one_run_net=-3, wins_vs_pythag=+3.62, rd=14, wpct_1run=0.455, blowout_net=0 / surprise=+3.62
  - ロッテ 2021 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ヤクルト 2016: one_run_net=0, wins_vs_pythag=+3.04, rd=-100, wpct_1run=0.500, blowout_net=-11 / surprise=+3.04
  - ヤクルト 2016 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ロッテ 2017: one_run_net=-2, wins_vs_pythag=+2.42, rd=-168, wpct_1run=0.474, blowout_net=-21 / surprise=+2.42
  - ロッテ 2017 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ロッテ 2022: one_run_net=-12, wins_vs_pythag=+2.38, rd=-35, wpct_1run=0.375, blowout_net=-4 / surprise=+2.38
  - ロッテ 2022 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- オリックス 2016: one_run_net=-2, wins_vs_pythag=+2.19, rd=-136, wpct_1run=0.478, blowout_net=-16 / surprise=+2.19
  - オリックス 2016 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- 中日 2023 **(focus)**: one_run_net=-3, wins_vs_pythag=+2.18, rd=-108, wpct_1run=0.467, blowout_net=-16 / surprise=+2.18
  - 中日 2023 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- DeNA 2015: one_run_net=0, wins_vs_pythag=+1.52, rd=-90, wpct_1run=0.500, blowout_net=-12 / surprise=+1.52
  - DeNA 2015 は「wins_vs_pythag > 0」を満たすのに「one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ほか 8 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 巨人 2020: one_run_net=2, wins_vs_pythag=-0.811, rd=111, wpct_1run=0.533, blowout_net=17
- ソフトバンク 2020: one_run_net=1, wins_vs_pythag=-0.444, rd=142, wpct_1run=0.515, blowout_net=22
- 阪神 2020: one_run_net=5, wins_vs_pythag=-0.181, rd=34, wpct_1run=0.593, blowout_net=1

## P10: 4点以上差の試合で負け越していれば、ピタゴラス期待勝利数を上回る（大敗が失点を押し上げ、期待勝利数を下げる）

- **判定: exit 2 異議あり（主張が強すぎる）** — 元の命題: 判例 30 件: t-2012, s-2014, s-2017, c-2022, e-2018 ほか
- もし: `blowout_net < 0` ならば: `wins_vs_pythag > 0`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 4点以上差で負け越したチーム・シーズンのうち、期待勝利数を下回るものが4分の1を超える
- 注記: 得点・失点の「配分」の偏りを見る命題。大差の試合が少ない年は条件に入らない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 46 | 0.61 [0.49, 0.71] | 0.47 | 1.28 | 0.001 | 0 | 修正 | 2 |
| 対偶 | 82 | 52 | 0.63 [0.53, 0.73] | 0.51 | 1.24 | 0.001 | 0 | 修正 | 2 |
| 逆 | 74 | 46 | 0.62 [0.51, 0.72] | 0.49 | 1.28 | 0.001 | 0 | 修正 | 2 |
| 裏 | 80 | 52 | 0.65 [0.54, 0.75] | 0.53 | 1.24 | 0.001 | 0 | 修正 | 2 |

**異議あり（主張が強すぎる）** 元の命題に判例 30 件（対偶の判例も同じ）

- 阪神 2012: blowout_net=-3, wins_vs_pythag=-6.22, rd=-27, one_run_net=-8, rank=5 / surprise=-6.22
  - 阪神 2012 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- ヤクルト 2014: blowout_net=-6, wins_vs_pythag=-5.84, rd=-50, one_run_net=-2, rank=6 / surprise=-5.84
  - ヤクルト 2014 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- ヤクルト 2017: blowout_net=-19, wins_vs_pythag=-5.28, rd=-180, one_run_net=-13, rank=6 / surprise=-5.28
  - ヤクルト 2017 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- 広島 2022: blowout_net=-1, wins_vs_pythag=-4.93, rd=8, one_run_net=-7, rank=5 / surprise=-4.93
  - 広島 2022 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- 楽天 2018: blowout_net=-3, wins_vs_pythag=-4.70, rd=-63, one_run_net=-13, rank=6 / surprise=-4.70
  - 楽天 2018 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- 西武 2014: blowout_net=-9, wins_vs_pythag=-4.16, rd=-26, one_run_net=-16, rank=5 / surprise=-4.16
  - 西武 2014 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- ヤクルト 2019: blowout_net=-8, wins_vs_pythag=-3.85, rd=-83, one_run_net=-8, rank=6 / surprise=-3.85
  - ヤクルト 2019 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- 中日 2015 **(focus)**: blowout_net=-1, wins_vs_pythag=-3.47, rd=-31, one_run_net=-5, rank=5 / surprise=-3.47
  - 中日 2015 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- 中日 2016 **(focus)**: blowout_net=-6, wins_vs_pythag=-3.32, rd=-73, one_run_net=-7, rank=6 / surprise=-3.32
  - 中日 2016 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- DeNA 2021: blowout_net=-10, wins_vs_pythag=-3.13, rd=-65, one_run_net=-2, rank=6 / surprise=-3.13
  - DeNA 2021 は「blowout_net < 0」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H8
- ほか 20 件（propositions.jsonl を参照）

**異議あり（主張が強すぎる）** 逆に判例 28 件（裏の判例も同じ）

- 中日 2012 **(focus)**: blowout_net=0, wins_vs_pythag=+8.45, rd=18, one_run_net=11, rank=2 / surprise=+8.45
  - 中日 2012 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- 阪神 2021: blowout_net=2, wins_vs_pythag=+6.67, rd=33, one_run_net=11, rank=2 / surprise=+6.67
  - 阪神 2021 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- オリックス 2025: blowout_net=0, wins_vs_pythag=+6.13, rd=-17, one_run_net=2, rank=3 / surprise=+6.13
  - オリックス 2025 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- オリックス 2023: blowout_net=7, wins_vs_pythag=+5.69, rd=80, one_run_net=15, rank=1 / surprise=+5.69
  - オリックス 2023 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- 巨人 2014: blowout_net=1, wins_vs_pythag=+5.49, rd=44, one_run_net=5, rank=1 / surprise=+5.49
  - 巨人 2014 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- 巨人 2013: blowout_net=6, wins_vs_pythag=+5.45, rd=89, one_run_net=8, rank=1 / surprise=+5.45
  - 巨人 2013 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- ヤクルト 2018: blowout_net=3, wins_vs_pythag=+5.18, rd=-7, one_run_net=8, rank=2 / surprise=+5.18
  - ヤクルト 2018 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- 西武 2018: blowout_net=20, wins_vs_pythag=+5.18, rd=139, one_run_net=14, rank=1 / surprise=+5.18
  - 西武 2018 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- 広島 2018: blowout_net=6, wins_vs_pythag=+4.93, rd=70, one_run_net=7, rank=1 / surprise=+4.93
  - 広島 2018 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- 日本ハム 2015: blowout_net=1, wins_vs_pythag=+4.83, rd=34, one_run_net=8, rank=2 / surprise=+4.83
  - 日本ハム 2015 は「wins_vs_pythag > 0」を満たすのに「blowout_net < 0」を満たさない。なぜか？ → H8
- ほか 18 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- オリックス 2020: blowout_net=-8, wins_vs_pythag=-4.95, rd=-60, one_run_net=-14, rank=6
- 楽天 2020: blowout_net=-3, wins_vs_pythag=-4.32, rd=35, one_run_net=-4, rank=4
- ヤクルト 2020: blowout_net=-13, wins_vs_pythag=-2.60, rd=-121, one_run_net=-5, rank=6
- 広島 2020: blowout_net=-2, wins_vs_pythag=-1.44, rd=-6, one_run_net=-4, rank=5
- 日本ハム 2020: blowout_net=-1, wins_vs_pythag=-0.896, rd=-35, one_run_net=-3, rank=5

## P11: 得失点差が ±20 以内のチームの間では、1点差で勝ち越していれば上位半分（Aクラス）に入る

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 2 件: c-2019, e-2022
- もし: `rd >= -20 かつ rd <= 20 かつ one_run_net > 0` ならば: `upper_half == True`
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 得失点差が拮抗し1点差で勝ち越したチーム・シーズンの半数以上が下位半分
- 注記: 「得失点差が同程度でも勝率が違う」を、得失点差の幅を絞って比べる。±20 は「同程度」の目安として事前に決めた値
- 条件の数: 4（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 20 | 18 | 0.90 [0.70, 0.97] | 0.50 | 1.80 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 76 | 0.97 [0.91, 0.99] | 0.87 | 1.12 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 18 | 0.23 [0.15, 0.34] | 0.13 | 1.80 | 0.000 | 0 | 修正 | 2 |
| 裏 | 136 | 76 | 0.56 [0.47, 0.64] | 0.50 | 1.12 | 0.000 | 0 | 判断保留 | 4 |

**異議あり（例外あり）** 元の命題に判例 2 件（対偶の判例も同じ）

- 広島 2019: rd=-10, one_run_net=5, upper_half=False, rank=4, rank_pythag=3, wins_vs_pythag=+1.07 / surprise=1
  - 広島 2019 は「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H8
- 楽天 2022: rd=11, one_run_net=8, upper_half=False, rank=4, rank_pythag=4, wins_vs_pythag=-2.34 / surprise=0
  - 楽天 2022 は「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H8

**異議あり（主張が強すぎる）** 逆に判例 60 件（裏の判例も同じ）

- 阪神 2015: rd=-85, one_run_net=4, upper_half=True, rank=3, rank_pythag=6, wins_vs_pythag=+10.25 / surprise=-3
  - 阪神 2015 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- 阪神 2019: rd=-28, one_run_net=1, upper_half=True, rank=3, rank_pythag=5, wins_vs_pythag=+3.68 / surprise=-2
  - 阪神 2019 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ロッテ 2021: rd=14, one_run_net=-3, upper_half=True, rank=2, rank_pythag=4, wins_vs_pythag=+3.62 / surprise=-2
  - ロッテ 2021 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- DeNA 2022: rd=-37, one_run_net=-1, upper_half=True, rank=2, rank_pythag=4, wins_vs_pythag=+7.13 / surprise=-2
  - DeNA 2022 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- 阪神 2022: rd=61, one_run_net=-5, upper_half=True, rank=3, rank_pythag=1, wins_vs_pythag=-9.93 / surprise=2
  - 阪神 2022 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ソフトバンク 2012: rd=23, one_run_net=-3, upper_half=True, rank=3, rank_pythag=2, wins_vs_pythag=-2.15 / surprise=1
  - ソフトバンク 2012 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- 楽天 2013: rd=91, one_run_net=1, upper_half=True, rank=1, rank_pythag=2, wins_vs_pythag=+1.47 / surprise=-1
  - 楽天 2013 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- オリックス 2014: rd=116, one_run_net=-6, upper_half=True, rank=2, rank_pythag=1, wins_vs_pythag=-5.19 / surprise=1
  - オリックス 2014 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- 広島 2014: rd=39, one_run_net=-1, upper_half=True, rank=3, rank_pythag=2, wins_vs_pythag=-1.02 / surprise=1
  - 広島 2014 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ソフトバンク 2014: rd=85, one_run_net=6, upper_half=True, rank=1, rank_pythag=2, wins_vs_pythag=-0.465 / surprise=-1
  - ソフトバンク 2014 は「upper_half == True」を満たすのに「rd >= -20 かつ rd <= 20 かつ one_run_net > 0」を満たさない。なぜか？ → H3, H8
- ほか 50 件（propositions.jsonl を参照）

## P7: 中日の順位は、得失点から期待される順位より2つ以上は下回らない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2019
- もし: `team == d` ならば: `rank_gap <= 1`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 逆・裏は評価しない（理由: 条件が「中日であること」なので、逆（期待どおりなら中日である）は意味を持たない）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 12 | 0.92 [0.67, 0.99] | 0.95 | 0.97 | 0.865 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 7 | 0.88 [0.53, 0.98] | 0.92 | 0.95 | 0.865 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2019 **(focus)**: team=d, rank_gap=3, rank=5, rank_pythag=2, rd=19, wins_vs_pythag=-4.71 / surprise=3
  - 中日 2019 は「team == d」を満たすのに「rank_gap <= 1」を満たさない。なぜか？ → H3, H4, H5

## P8: 中日の勝利数は、ピタゴラス期待勝利数を3勝以上は下回らない（「運が悪かった」ではない）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 3 件: d-2019, d-2015, d-2016
- もし: `team == d` ならば: `wins_vs_pythag >= -3`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 逆・裏は評価しない（理由: 条件が「中日であること」なので、逆（期待どおりなら中日である）は意味を持たない）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 10 | 0.77 [0.50, 0.92] | 0.79 | 0.98 | 0.716 | 0 | 判断保留 | 4 |
| 対偶 | 33 | 30 | 0.91 [0.76, 0.97] | 0.92 | 0.99 | 0.716 | 0 | 支持 | 1 |

**待った！判断保留** 元の命題に判例 3 件（対偶の判例も同じ）

- 中日 2019 **(focus)**: team=d, wins_vs_pythag=-4.71, rank=5, rank_pythag=2, rd=19, wpct_1run=0.413 / surprise=-4.71
  - 中日 2019 は「team == d」を満たすのに「wins_vs_pythag >= -3」を満たさない。なぜか？ → H3, H4, H5
- 中日 2015 **(focus)**: team=d, wins_vs_pythag=-3.47, rank=5, rank_pythag=4, rd=-31, wpct_1run=0.444 / surprise=-3.47
  - 中日 2015 は「team == d」を満たすのに「wins_vs_pythag >= -3」を満たさない。なぜか？ → H3, H4, H5
- 中日 2016 **(focus)**: team=d, wins_vs_pythag=-3.32, rank=6, rank_pythag=5, rd=-73, wpct_1run=0.410 / surprise=-3.32
  - 中日 2016 は「team == d」を満たすのに「wins_vs_pythag >= -3」を満たさない。なぜか？ → H3, H4, H5

## P12: 配分効果がはっきりプラスのシーズン（alloc_z ≥ 1）の翌年も、配分効果はプラスである（配分はチームの特徴として続く）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 13 件: s-2022, t-2021, s-2012, s-2018, b-2019 ほか
- もし: `alloc_z >= 1` ならば: `alloc_z_next > 0`
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: alloc_z ≥ 1 のシーズンのうち、翌年の alloc_z が 0 以下になるものが半数以上
- 注記: 翌年のないシーズン（最終年、除外の前年）は判定できない単位として数える。同じチームでも選手は入れ替わる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 28 | 15 | 0.54 [0.36, 0.70] | 0.50 | 1.07 | 0.417 | 12 | 判断保留 | 4 |
| 対偶 | 72 | 59 | 0.82 [0.72, 0.89] | 0.81 | 1.02 | 0.417 | 12 | 支持 | 1 |
| 逆 | 72 | 15 | 0.21 [0.13, 0.32] | 0.19 | 1.07 | 0.417 | 12 | 棄却 | 3 |
| 裏 | 116 | 59 | 0.51 [0.42, 0.60] | 0.50 | 1.02 | 0.417 | 12 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 13 件（対偶の判例も同じ）

- ヤクルト 2022: alloc_z=+1.89, alloc_z_next=-2.53, wins_vs_pythag=+4.82 / surprise=-2.53
  - ヤクルト 2022 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- 阪神 2021: alloc_z=+1.67, alloc_z_next=-2.11, wins_vs_pythag=+6.67 / surprise=-2.11
  - 阪神 2021 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- ヤクルト 2012: alloc_z=+1.76, alloc_z_next=-1.73, wins_vs_pythag=+3.30 / surprise=-1.73
  - ヤクルト 2012 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- ヤクルト 2018: alloc_z=+1.25, alloc_z_next=-1.69, wins_vs_pythag=+5.18 / surprise=-1.69
  - ヤクルト 2018 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- オリックス 2019: alloc_z=+1.02, alloc_z_next=-1.61, wins_vs_pythag=+2.75 / surprise=-1.61
  - オリックス 2019 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- オリックス 2023: alloc_z=+2.56, alloc_z_next=-1.39, wins_vs_pythag=+5.69 / surprise=-1.39
  - オリックス 2023 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- 阪神 2015: alloc_z=+1.48, alloc_z_next=-0.672, wins_vs_pythag=+10.25 / surprise=-0.672
  - 阪神 2015 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- ソフトバンク 2019: alloc_z=+1.94, alloc_z_next=-0.268, wins_vs_pythag=+5.02 / surprise=-0.268
  - ソフトバンク 2019 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- DeNA 2023: alloc_z=+1.25, alloc_z_next=-0.180, wins_vs_pythag=0.975 / surprise=-0.180
  - DeNA 2023 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- ロッテ 2021: alloc_z=+1.13, alloc_z_next=-0.162, wins_vs_pythag=+3.62 / surprise=-0.162
  - ロッテ 2021 は「alloc_z >= 1」を満たすのに「alloc_z_next > 0」を満たさない。なぜか？ → H9
- ほか 3 件（propositions.jsonl を参照）

**異議あり（不成立）** 逆に判例 57 件（裏の判例も同じ）

- オリックス 2022: alloc_z=-0.237, alloc_z_next=+2.56, wins_vs_pythag=+1.15 / surprise=+2.56
  - オリックス 2022 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- 阪神 2013: alloc_z=-0.067, alloc_z_next=+2.50, wins_vs_pythag=-2.40 / surprise=+2.50
  - 阪神 2013 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- 西武 2019: alloc_z=0.997, alloc_z_next=+2.23, wins_vs_pythag=+3.55 / surprise=+2.23
  - 西武 2019 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- ソフトバンク 2016: alloc_z=0.197, alloc_z_next=+2.09, wins_vs_pythag=-2.97 / surprise=+2.09
  - ソフトバンク 2016 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- ソフトバンク 2018: alloc_z=-0.001, alloc_z_next=+1.94, wins_vs_pythag=0.164 / surprise=+1.94
  - ソフトバンク 2018 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- ヤクルト 2021: alloc_z=0.593, alloc_z_next=+1.89, wins_vs_pythag=+1.25 / surprise=+1.89
  - ヤクルト 2021 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- 楽天 2023: alloc_z=0.930, alloc_z_next=+1.84, wins_vs_pythag=+4.68 / surprise=+1.84
  - 楽天 2023 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- DeNA 2016: alloc_z=0.565, alloc_z_next=+1.73, wins_vs_pythag=0.767 / surprise=+1.73
  - DeNA 2016 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- オリックス 2024: alloc_z=-1.39, alloc_z_next=+1.73, wins_vs_pythag=-0.083 / surprise=+1.73
  - オリックス 2024 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- ロッテ 2012: alloc_z=-1.01, alloc_z_next=+1.65, wins_vs_pythag=-2.15 / surprise=+1.65
  - ロッテ 2012 は「alloc_z_next > 0」を満たすのに「alloc_z >= 1」を満たさない。なぜか？ → H9
- ほか 47 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 西武 2020: alloc_z=+2.23, alloc_z_next=-0.113, wins_vs_pythag=+6.63
- 中日 2020 **(focus)**: alloc_z=+1.39, alloc_z_next=-0.086, wins_vs_pythag=+9.35

## P13: 配分効果がはっきり出たシーズン（\|alloc_z\| ≥ 1）は、ホームとビジターで配分効果の符号がそろう

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 22 件: s-2023, t-2022, g-2013, h-2019, s-2017 ほか
- もし: `alloc_z_abs >= 1` ならば: `alloc_same_sign == True`
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: \|alloc_z\| ≥ 1 のシーズンの半数以上で、ホームとビジターの符号が逆
- 注記: ホームの勝ち試合は9回裏を行わない・サヨナラで打ち切られるため、ホームの配分効果は偏りやすい（R1 の限界を参照）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 61 | 39 | 0.64 [0.51, 0.75] | 0.37 | 1.75 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 99 | 77 | 0.78 [0.69, 0.85] | 0.61 | 1.28 | 0.000 | 0 | 支持 | 1 |
| 逆 | 57 | 39 | 0.68 [0.56, 0.79] | 0.39 | 1.75 | 0.000 | 0 | 支持 | 1 |
| 裏 | 95 | 77 | 0.81 [0.72, 0.88] | 0.63 | 1.28 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 22 件（対偶の判例も同じ）

- ヤクルト 2023: alloc_z_abs=+2.53, alloc_same_sign=False, alloc_net_home=+4.24, alloc_net_away=-18.70 / surprise=-2.53
  - ヤクルト 2023 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- 阪神 2022: alloc_z_abs=+2.11, alloc_same_sign=False, alloc_net_home=+2.46, alloc_net_away=-14.46 / surprise=-2.11
  - 阪神 2022 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- 巨人 2013: alloc_z_abs=+2.07, alloc_same_sign=False, alloc_net_home=+12.64, alloc_net_away=-1.51 / surprise=+2.07
  - 巨人 2013 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- ソフトバンク 2019: alloc_z_abs=+1.94, alloc_same_sign=False, alloc_net_home=+11.74, alloc_net_away=-0.577 / surprise=+1.94
  - ソフトバンク 2019 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- ヤクルト 2017: alloc_z_abs=+1.94, alloc_same_sign=False, alloc_net_home=+6.49, alloc_net_away=-14.72 / surprise=-1.94
  - ヤクルト 2017 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- DeNA 2017: alloc_z_abs=+1.73, alloc_same_sign=False, alloc_net_home=+10.07, alloc_net_away=-0.181 / surprise=+1.73
  - DeNA 2017 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- 西武 2024: alloc_z_abs=+1.68, alloc_same_sign=False, alloc_net_home=+1.14, alloc_net_away=-9.65 / surprise=-1.68
  - 西武 2024 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- 中日 2015 **(focus)**: alloc_z_abs=+1.65, alloc_same_sign=False, alloc_net_home=0.139, alloc_net_away=-10.92 / surprise=-1.65
  - 中日 2015 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- DeNA 2012: alloc_z_abs=+1.49, alloc_same_sign=False, alloc_net_home=+5.40, alloc_net_away=-13.46 / surprise=-1.49
  - DeNA 2012 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- 阪神 2015: alloc_z_abs=+1.48, alloc_same_sign=False, alloc_net_home=+13.14, alloc_net_away=-5.03 / surprise=+1.48
  - 阪神 2015 は「alloc_z_abs >= 1」を満たすのに「alloc_same_sign == True」を満たさない。なぜか？ → H9
- ほか 12 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 18 件（裏の判例も同じ）

- 楽天 2023: alloc_z_abs=0.930, alloc_same_sign=True, alloc_net_home=+4.04, alloc_net_away=+1.41 / surprise=0.930
  - 楽天 2023 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- 楽天 2019: alloc_z_abs=0.906, alloc_same_sign=True, alloc_net_home=-0.183, alloc_net_away=-5.29 / surprise=-0.906
  - 楽天 2019 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- 中日 2014 **(focus)**: alloc_z_abs=0.879, alloc_same_sign=True, alloc_net_home=-0.583, alloc_net_away=-3.76 / surprise=-0.879
  - 中日 2014 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- ロッテ 2023: alloc_z_abs=0.856, alloc_same_sign=True, alloc_net_home=+3.21, alloc_net_away=+1.70 / surprise=0.856
  - ロッテ 2023 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- DeNA 2021: alloc_z_abs=0.779, alloc_same_sign=True, alloc_net_home=-1.10, alloc_net_away=-3.57 / surprise=-0.779
  - DeNA 2021 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- 巨人 2021: alloc_z_abs=0.750, alloc_same_sign=True, alloc_net_home=-1.03, alloc_net_away=-3.21 / surprise=-0.750
  - 巨人 2021 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- 日本ハム 2012: alloc_z_abs=0.737, alloc_same_sign=True, alloc_net_home=-4.17, alloc_net_away=-0.736 / surprise=-0.737
  - 日本ハム 2012 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- ロッテ 2024: alloc_z_abs=0.710, alloc_same_sign=True, alloc_net_home=+1.07, alloc_net_away=+3.03 / surprise=0.710
  - ロッテ 2024 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- ロッテ 2025: alloc_z_abs=0.678, alloc_same_sign=True, alloc_net_home=-0.653, alloc_net_away=-3.30 / surprise=-0.678
  - ロッテ 2025 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- 楽天 2015: alloc_z_abs=0.652, alloc_same_sign=True, alloc_net_home=+2.41, alloc_net_away=+1.82 / surprise=0.652
  - 楽天 2015 は「alloc_same_sign == True」を満たすのに「alloc_z_abs >= 1」を満たさない。なぜか？ → H9
- ほか 8 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 阪神 2020: alloc_z_abs=+1.33, alloc_same_sign=False, alloc_net_home=+9.47, alloc_net_away=-4.03

## P14: 中日は、得点・失点の配分（どの試合で組み合わさったか）で勝ち越し数を失っていない（alloc_net ≥ 0）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 8 件: d-2015, d-2019, d-2016, d-2014, d-2023 ほか
- もし: `team == d` ならば: `alloc_net >= 0`
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 逆・裏は評価しない（理由: 条件が「中日であること」なので、逆（配分で損をしていなければ中日である）は意味を持たない）
- 見直す条件（反証）: 中日のシーズンのうち、配分で負け越し（alloc_net < 0）が4分の1を超える
- 注記: 成り立てば、CS 不出場の説明は配分ではなく、得点・失点の総量（とその原因）の側に寄る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 5 | 0.38 [0.18, 0.64] | 0.50 | 0.77 | 0.877 | 0 | 棄却 | 3 |
| 対偶 | 78 | 70 | 0.90 [0.81, 0.95] | 0.92 | 0.98 | 0.877 | 0 | 支持 | 1 |

**異議あり（不成立）** 元の命題に判例 8 件（対偶の判例も同じ）

- 中日 2015 **(focus)**: team=d, alloc_net=-9.29, rank=5, rd=-31, wins_vs_pythag=-3.47, alloc_z=-1.65 / surprise=-9.29
  - 中日 2015 は「team == d」を満たすのに「alloc_net >= 0」を満たさない。なぜか？ → H3, H9
- 中日 2019 **(focus)**: team=d, alloc_net=-7.43, rank=5, rd=19, wins_vs_pythag=-4.71, alloc_z=-1.30 / surprise=-7.43
  - 中日 2019 は「team == d」を満たすのに「alloc_net >= 0」を満たさない。なぜか？ → H3, H9
- 中日 2016 **(focus)**: team=d, alloc_net=-5.80, rank=6, rd=-73, wins_vs_pythag=-3.32, alloc_z=-1.02 / surprise=-5.80
  - 中日 2016 は「team == d」を満たすのに「alloc_net >= 0」を満たさない。なぜか？ → H3, H9
- 中日 2014 **(focus)**: team=d, alloc_net=-5.12, rank=4, rd=-20, wins_vs_pythag=-0.792, alloc_z=-0.879 / surprise=-5.12
  - 中日 2014 は「team == d」を満たすのに「alloc_net >= 0」を満たさない。なぜか？ → H3, H9
- 中日 2023 **(focus)**: team=d, alloc_net=-4.84, rank=6, rd=-108, wins_vs_pythag=+2.18, alloc_z=-0.869 / surprise=-4.84
  - 中日 2023 は「team == d」を満たすのに「alloc_net >= 0」を満たさない。なぜか？ → H3, H9
- 中日 2018 **(focus)**: team=d, alloc_net=-3.38, rank=5, rd=-56, wins_vs_pythag=-1.74, alloc_z=-0.581 / surprise=-3.38
  - 中日 2018 は「team == d」を満たすのに「alloc_net >= 0」を満たさない。なぜか？ → H3, H9
- 中日 2025 **(focus)**: team=d, alloc_net=-1.13, rank=4, rd=-60, wins_vs_pythag=+1.41, alloc_z=-0.204 / surprise=-1.13
  - 中日 2025 は「team == d」を満たすのに「alloc_net >= 0」を満たさない。なぜか？ → H3, H9
- 中日 2021 **(focus)**: team=d, alloc_net=-0.476, rank=5, rd=-73, wins_vs_pythag=+1.48, alloc_z=-0.086 / surprise=-0.476
  - 中日 2021 は「team == d」を満たすのに「alloc_net >= 0」を満たさない。なぜか？ → H3, H9
