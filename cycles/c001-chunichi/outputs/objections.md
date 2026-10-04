# 異議あり — 命題の判定記録（自動生成）

判定基準は結果を見る前に命題ファイルに書いたもの（docs/propositions.md）。
命題ファイル SHA-256: `9a031111ad04aa81adb8888f3452c60da99c365455f0c7546a8052de04661fe2` / コード: `a24c7c15c40be239511785e483dec1b34f2f767d`

判定は命題がその範囲で成り立つかどうかだけを示し、原因は示さない。

## 命題の系譜

- P15 → **P18**: P15 の判例 10件（低得点・失点2番目以内なのに B クラス）を見て、得失点差がプラスかどうかで分かれているように見えたため、前件に rd > 0 を加えた。結果を見てから作ったので、確かめには新しいデータ（2026年以降、または未取得の年）を使う
- P19 → **P36**: 天井の帯を k ≥ 6（幅の上限なし）から k = 6〜7（床と同じ幅2）に変えた。R3 の比較は、得点の量で比べると天井が大きく出る作りだったため（R3 の自分への異議）
- P20 → **P37**: P36 と同じ変更（天井の帯を k = 6〜7 にして幅をそろえた）
- P33 → **P35**: 強さを usually（0.75）から more_often_than_not（0.50）に下げた。P33 は成立率 0.66・lift 1.32・p < 0.001 で、関係はあるが「概ね」に届かなかった。同じデータでの言い直しで、確かめではない

## P1: 得失点差がプラスなら、上位半分（Aクラス）である

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 12 件: h-2013, d-2019, h-2021, l-2015, c-2022 ほか
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[all] rd>0 => upper_half==true`（指紋 `43d21396576b5a67`）
- 兄弟（範囲と結論が同じ、条件が違う）: P11, P50
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] rank_pythag<=3 => rank<=3`（指紋 `cb8d5b9daa5a65a0`）
- 兄弟（範囲と結論が同じ、条件が違う）: P3, P4
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] rank_rf<=2 => rank<=3`（指紋 `c1faf71742892560`）
- 兄弟（範囲と結論が同じ、条件が違う）: P2, P4
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] rank_ra<=2 => rank<=3`（指紋 `7a49cb7ef73a9684`）
- 兄弟（範囲と結論が同じ、条件が違う）: P2, P3
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] rank_rf>=5 => upper_half==false`（指紋 `b7529d85063bb804`）
- 兄弟（範囲と結論が同じ、条件が違う）: P52
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] * => wins_vs_pythag<=5 & wins_vs_pythag>=-5`（指紋 `3e727c30258ae3df`）
- 強さ: ほとんど（almost_always, 基準 0.90）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] one_run_net>0 => wins_vs_pythag>0`（指紋 `5d9252ea58c645eb`）
- 兄弟（範囲と結論が同じ、条件が違う）: P10
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 1点差で勝ち越したチーム・シーズンのうち、期待勝利数を下回るものが4分の1を超える
- 注記: 1点差の勝敗とピタゴラスからのずれは計算上も連動しやすい。成り立っても「どうずれたか」の記述で、「なぜか」の説明ではない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] blowout_net<0 => wins_vs_pythag>0`（指紋 `4bbf5fd32d3ae838`）
- 兄弟（範囲と結論が同じ、条件が違う）: P9
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 4点以上差で負け越したチーム・シーズンのうち、期待勝利数を下回るものが4分の1を超える
- 注記: 得点・失点の「配分」の偏りを見る命題。大差の試合が少ない年は条件に入らない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] one_run_net>0 & rd<=20 & rd>=-20 => upper_half==true`（指紋 `46eaae2a798cd858`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P50
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 得失点差が拮抗し1点差で勝ち越したチーム・シーズンの半数以上が下位半分
- 注記: 「得失点差が同程度でも勝率が違う」を、得失点差の幅を絞って比べる。±20 は「同程度」の目安として事前に決めた値
- 条件の数: 4（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] team=="d" => rank_gap<=1`（指紋 `c92edd20dc677142`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 逆・裏は評価しない（理由: 条件が「中日であること」なので、逆（期待どおりなら中日である）は意味を持たない）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] team=="d" => wins_vs_pythag>=-3`（指紋 `39baba6201c36f03`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 逆・裏は評価しない（理由: 条件が「中日であること」なので、逆（期待どおりなら中日である）は意味を持たない）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] alloc_z>=1 => alloc_z_next>0`（指紋 `75f1f90d99bf2ba6`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: alloc_z ≥ 1 のシーズンのうち、翌年の alloc_z が 0 以下になるものが半数以上
- 注記: 翌年のないシーズン（最終年、除外の前年）は判定できない単位として数える。同じチームでも選手は入れ替わる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] alloc_z_abs>=1 => alloc_same_sign==true`（指紋 `a7e653c60b61baf3`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: \|alloc_z\| ≥ 1 のシーズンの半数以上で、ホームとビジターの符号が逆
- 注記: ホームの勝ち試合は9回裏を行わない・サヨナラで打ち切られるため、ホームの配分効果は偏りやすい（R1 の限界を参照）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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
- 識別子: `[all] team=="d" => alloc_net>=0`（指紋 `9d6de68e3af493db`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 逆・裏は評価しない（理由: 条件が「中日であること」なので、逆（配分で損をしていなければ中日である）は意味を持たない）
- 見直す条件（反証）: 中日のシーズンのうち、配分で負け越し（alloc_net < 0）が4分の1を超える
- 注記: 成り立てば、CS 不出場の説明は配分ではなく、得点・失点の総量（とその原因）の側に寄る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

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

## P15: 得点がリーグ5位以下のチームの間では、失点がリーグで2番目以内に少なければ A クラス

- **判定: exit 2 異議あり（主張が強すぎる）** — 元の命題: 判例 10 件: d-2019, t-2018, d-2021, l-2023, b-2024 ほか
- もし: `rank_ra <= 2` ならば: `upper_half == True`
- 識別子: `[where:rank_rf>=5] rank_ra<=2 => upper_half==true`（指紋 `b9a676014f04e4b2`）
- 兄弟（範囲と結論が同じ、条件が違う）: P16
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 見直す条件（反証）: 低得点で失点が2番目以内に少ないチーム・シーズンのうち、B クラスが4分の1を超える
- 注記: 逆（A クラスなら失点が2番目以内）は、低得点の A クラスが失点の少なさで届いたかを見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 6 | 0.38 [0.18, 0.61] | 0.15 | 2.44 | 0.007 | 0 | 修正 | 2 |
| 対偶 | 44 | 34 | 0.77 [0.63, 0.87] | 0.69 | 1.12 | 0.007 | 0 | 判断保留 | 4 |
| 逆 | 8 | 6 | 0.75 [0.41, 0.93] | 0.31 | 2.44 | 0.007 | 0 | 判断保留 | 4 |
| 裏 | 36 | 34 | 0.94 [0.82, 0.98] | 0.85 | 1.12 | 0.007 | 0 | 支持 | 1 |

**異議あり（主張が強すぎる）** 元の命題に判例 10 件（対偶の判例も同じ）

- 中日 2019 **(focus)**: rank_ra=1, upper_half=False, rank=5, rank_rf=5, rd=19, rank_rd=2, wins_vs_pythag=-4.71 / surprise=3
  - 中日 2019 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 阪神 2018: rank_ra=2, upper_half=False, rank=6, rank_rf=5, rd=-51, rank_rd=4, wins_vs_pythag=-3.05 / surprise=2
  - 阪神 2018 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rank_ra=1, upper_half=False, rank=5, rank_rf=6, rd=-73, rank_rd=6, wins_vs_pythag=+1.48 / surprise=-1
  - 中日 2021 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 西武 2023: rank_ra=2, upper_half=False, rank=5, rank_rf=6, rd=-30, rank_rd=4, wins_vs_pythag=-1.67 / surprise=1
  - 西武 2023 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- オリックス 2024: rank_ra=2, upper_half=False, rank=5, rank_rf=5, rd=-46, rank_rd=4, wins_vs_pythag=-0.083 / surprise=1
  - オリックス 2024 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- オリックス 2013: rank_ra=1, upper_half=False, rank=5, rank_rf=6, rd=-16, rank_rd=5, wins_vs_pythag=-1.55 / surprise=0
  - オリックス 2013 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 中日 2014 **(focus)**: rank_ra=2, upper_half=False, rank=4, rank_rf=5, rd=-20, rank_rd=4, wins_vs_pythag=-0.792 / surprise=0
  - 中日 2014 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- オリックス 2015: rank_ra=2, upper_half=False, rank=5, rank_rf=5, rd=-29, rank_rd=5, wins_vs_pythag=-6.00 / surprise=0
  - オリックス 2015 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 中日 2022 **(focus)**: rank_ra=2, upper_half=False, rank=6, rank_rf=6, rd=-81, rank_rd=6, wins_vs_pythag=+6.93 / surprise=0
  - 中日 2022 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 広島 2024: rank_ra=2, upper_half=False, rank=4, rank_rf=5, rd=-4, rank_rd=4, wins_vs_pythag=-0.394 / surprise=0
  - 広島 2024 は「rank_ra <= 2」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**待った！判断保留** 逆に判例 2 件（裏の判例も同じ）

- 阪神 2015: rank_ra=5, upper_half=True, rank=3, rank_rf=6, rd=-85, rank_rd=5, wins_vs_pythag=+10.25 / surprise=-3
  - 阪神 2015 は「upper_half == True」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2
- 広島 2023: rank_ra=5, upper_half=True, rank=2, rank_rf=5, rd=-15, rank_rd=4, wins_vs_pythag=+6.41 / surprise=-2
  - 広島 2023 は「upper_half == True」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H2

## P16: 得点がリーグ5位以下のチームの間では、ピタゴラス期待勝利数を上回れば A クラス

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 20 件: d-2024, d-2022, d-2017, e-2015, m-2014 ほか
- もし: `wins_vs_pythag > 0` ならば: `upper_half == True`
- 識別子: `[where:rank_rf>=5] wins_vs_pythag>0 => upper_half==true`（指紋 `1f85b035a8106fcc`）
- 兄弟（範囲と結論が同じ、条件が違う）: P15
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 見直す条件（反証）: 低得点で期待以上に勝ったチーム・シーズンの半数以上が B クラス
- 注記: 逆（A クラスなら期待以上）が成り立つなら、低得点の A クラスは得失点で説明しにくい部分で届いた。R1 ではその部分は翌年に続かなかった
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 24 | 4 | 0.17 [0.07, 0.36] | 0.15 | 1.08 | 0.556 | 0 | 棄却 | 3 |
| 対偶 | 44 | 24 | 0.55 [0.40, 0.68] | 0.54 | 1.01 | 0.556 | 0 | 判断保留 | 4 |
| 逆 | 8 | 4 | 0.50 [0.22, 0.78] | 0.46 | 1.08 | 0.556 | 0 | 判断保留 | 4 |
| 裏 | 28 | 24 | 0.86 [0.69, 0.94] | 0.85 | 1.01 | 0.556 | 0 | 支持 | 1 |

**異議あり（不成立）** 元の命題に判例 20 件（対偶の判例も同じ）

- 中日 2024 **(focus)**: wins_vs_pythag=+7.56, upper_half=False, rank=6, rank_ra=4, rd=-105, one_run_net=10, alloc_net_strat=+2.48 / surprise=+7.56
  - 中日 2024 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 中日 2022 **(focus)**: wins_vs_pythag=+6.93, upper_half=False, rank=6, rank_ra=2, rd=-81, one_run_net=2, alloc_net_strat=+4.02 / surprise=+6.93
  - 中日 2022 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 中日 2017 **(focus)**: wins_vs_pythag=+5.29, upper_half=False, rank=5, rank_ra=5, rd=-136, one_run_net=-3, alloc_net_strat=+1.31 / surprise=+5.29
  - 中日 2017 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2015: wins_vs_pythag=+4.49, upper_half=False, rank=6, rank_ra=6, rd=-149, one_run_net=1, alloc_net_strat=+4.23 / surprise=+4.49
  - 楽天 2015 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ロッテ 2014: wins_vs_pythag=+4.29, upper_half=False, rank=4, rank_ra=6, rd=-86, one_run_net=8, alloc_net_strat=+3.12 / surprise=+4.29
  - ロッテ 2014 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- DeNA 2018: wins_vs_pythag=+3.92, upper_half=False, rank=4, rank_ra=3, rd=-70, one_run_net=-1, alloc_net_strat=+1.20 / surprise=+3.92
  - DeNA 2018 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2016: wins_vs_pythag=+3.68, upper_half=False, rank=5, rank_ra=6, rd=-110, one_run_net=2, alloc_net_strat=+4.26 / surprise=+3.68
  - 楽天 2016 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- オリックス 2019: wins_vs_pythag=+2.75, upper_half=False, rank=6, rank_ra=5, rd=-93, one_run_net=6, alloc_net_strat=+6.17 / surprise=+2.75
  - オリックス 2019 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ロッテ 2017: wins_vs_pythag=+2.42, upper_half=False, rank=6, rank_ra=6, rd=-168, one_run_net=-2, alloc_net_strat=-1.72 / surprise=+2.42
  - ロッテ 2017 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- オリックス 2016: wins_vs_pythag=+2.19, upper_half=False, rank=6, rank_ra=5, rd=-136, one_run_net=-2, alloc_net_strat=-1.01 / surprise=+2.19
  - オリックス 2016 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ほか 10 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 4 件（裏の判例も同じ）

- 阪神 2022: wins_vs_pythag=-9.93, upper_half=True, rank=3, rank_ra=1, rd=61, one_run_net=-5, alloc_net_strat=-12.01 / surprise=-9.93
  - 阪神 2022 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H9
- 阪神 2013: wins_vs_pythag=-2.40, upper_half=True, rank=2, rank_ra=1, rd=43, one_run_net=2, alloc_net_strat=-0.292 / surprise=-2.40
  - 阪神 2013 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2012: wins_vs_pythag=-2.15, upper_half=True, rank=3, rank_ra=1, rd=23, one_run_net=-3, alloc_net_strat=-4.19 / surprise=-2.15
  - ソフトバンク 2012 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H9
- 西武 2022: wins_vs_pythag=-0.247, upper_half=True, rank=3, rank_ra=1, rd=16, one_run_net=-3, alloc_net_strat=+1.98 / surprise=-0.247
  - 西武 2022 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3, H9

## P17: 得点がリーグ5位以下だったシーズンの中日は、失点がリーグで2番目以内に少なくない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: d-2014, d-2022, d-2019, d-2021
- もし: `（すべての単位）` ならば: `rank_ra >= 3`
- 識別子: `[team=d, where:rank_rf>=5] * => rank_ra>=3`（指紋 `0948926dd405f0a5`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、失点が2番目以内に少ない
- 注記: 成り立てば「失点でも補えなかった」。成り立たなければ、失点は少なかったのに届かなかった年があり、得点の不足の大きさに戻る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 7 | 0.64 [0.35, 0.85] | 0.64 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 中日 2014 **(focus)**: rank_ra=2, rank=4, rank_rf=5, rd=-20, RA=590 / surprise=2
  - 中日 2014 は「（すべての単位）」を満たすのに「rank_ra >= 3」を満たさない。なぜか？ → H2
- 中日 2022 **(focus)**: rank_ra=2, rank=6, rank_rf=6, rd=-81, RA=495 / surprise=2
  - 中日 2022 は「（すべての単位）」を満たすのに「rank_ra >= 3」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: rank_ra=1, rank=5, rank_rf=5, rd=19, RA=544 / surprise=1
  - 中日 2019 は「（すべての単位）」を満たすのに「rank_ra >= 3」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rank_ra=1, rank=5, rank_rf=6, rd=-73, RA=478 / surprise=1
  - 中日 2021 は「（すべての単位）」を満たすのに「rank_ra >= 3」を満たさない。なぜか？ → H2

## P18: 得点がリーグ5位以下で失点が2番目以内に少ないチームの間では、得失点差がプラスなら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2019
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[where:rank_ra<=2, where:rank_rf>=5] rd>0 => upper_half==true`（指紋 `d497ab4e1cb399ee`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}, {'col': 'rank_ra', 'op': '<=', 'value': 2}]} / 単位数: 16
- 親: P15（変更: P15 の判例 10件（低得点・失点2番目以内なのに B クラス）を見て、得失点差がプラスかどうかで分かれているように見えたため、前件に rd > 0 を加えた。結果を見てから作ったので、確かめには新しいデータ（2026年以降、または未取得の年）を使う）
- 見直す条件（反証）: 新しいデータで、この範囲かつ rd > 0 のチーム・シーズンの4分の1を超えて B クラス
- 注記: motivated_by に作るきっかけの16単位すべてを入れたので、今のデータでの held-out は0単位（判断保留が正しい）。失点の少なさは、得点の不足を上回ったときにだけ順位に届く、という見方の確かめ
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 6 | 5 | 0.83 [0.44, 0.97] | 0.38 | 2.22 | 0.008 | 0 | 判断保留 | 4 |
| 対偶 | 10 | 9 | 0.90 [0.60, 0.98] | 0.62 | 1.44 | 0.008 | 0 | 判断保留 | 4 |
| 逆 | 6 | 5 | 0.83 [0.44, 0.97] | 0.38 | 2.22 | 0.008 | 0 | 判断保留 | 4 |
| 裏 | 10 | 9 | 0.90 [0.60, 0.98] | 0.62 | 1.44 | 0.008 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2019 **(focus)**: rd=19, upper_half=False, rank=5, RF=563, RA=544, rank_rd=2, wins_vs_pythag=-4.71 / surprise=3
  - 中日 2019 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 阪神 2019: rd=-28, upper_half=True, rank=3, RF=538, RA=566, rank_rd=5, wins_vs_pythag=+3.68 / surprise=-2
  - 阪神 2019 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2

**きっかけ以外での判定**（作り直しのきっかけ d-2019, t-2018, d-2021, l-2023, b-2024, b-2013, d-2014, b-2015, d-2022, c-2024, t-2022, t-2013, t-2021, h-2012, l-2022, t-2019 を除く）: n=0 成立=0 成立率=- [0.00, 1.00] → **判断保留** / 判例なし

## P19: 得点がリーグ5位以下だったシーズンの中日は、床（0〜2点に抑えられる試合）の不足が、天井（6点以上）の不足より大きい

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 11 件: d-2017, d-2021, d-2014, d-2015, d-2022 ほか
- もし: `（すべての単位）` ならば: `rf_def_floor_minus_ceiling < 0`
- 識別子: `[team=d, where:rank_rf>=5] * => rf_def_floor_minus_ceiling<0`（指紋 `30df121361f9d2a3`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、天井の不足のほうが大きい
- 注記: 成り立てば「抑え込まれる試合が多い」。成り立たなければ「大量点が出ない」側を調べる
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 0 | 0.00 [0.00, 0.26] | 0.00 | - | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 11 | 0 | 0.00 [0.00, 0.26] | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 11 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: rf_def_floor_minus_ceiling=0.481, rank=5, rf_def_floor=0.038, rf_def_mid=-0.288, rf_def_ceiling=-0.443, rf_def_total=-0.694 / surprise=0.481
  - 中日 2017 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rf_def_floor_minus_ceiling=0.341, rank=5, rf_def_floor=-0.175, rf_def_mid=-0.441, rf_def_ceiling=-0.516, rf_def_total=-1.13 / surprise=0.341
  - 中日 2021 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2014 **(focus)**: rf_def_floor_minus_ceiling=0.261, rank=4, rf_def_floor=-0.025, rf_def_mid=-0.007, rf_def_ceiling=-0.286, rf_def_total=-0.318 / surprise=0.261
  - 中日 2014 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2015 **(focus)**: rf_def_floor_minus_ceiling=0.213, rank=5, rf_def_floor=-0.004, rf_def_mid=-0.027, rf_def_ceiling=-0.217, rf_def_total=-0.248 / surprise=0.213
  - 中日 2015 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2022 **(focus)**: rf_def_floor_minus_ceiling=0.197, rank=6, rf_def_floor=-0.178, rf_def_mid=-0.336, rf_def_ceiling=-0.375, rf_def_total=-0.888 / surprise=0.197
  - 中日 2022 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2024 **(focus)**: rf_def_floor_minus_ceiling=0.165, rank=6, rf_def_floor=-0.101, rf_def_mid=-0.368, rf_def_ceiling=-0.266, rf_def_total=-0.734 / surprise=0.165
  - 中日 2024 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2013 **(focus)**: rf_def_floor_minus_ceiling=0.156, rank=4, rf_def_floor=-0.036, rf_def_mid=-0.136, rf_def_ceiling=-0.192, rf_def_total=-0.364 / surprise=0.156
  - 中日 2013 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2025 **(focus)**: rf_def_floor_minus_ceiling=0.133, rank=4, rf_def_floor=-0.090, rf_def_mid=-0.161, rf_def_ceiling=-0.222, rf_def_total=-0.473 / surprise=0.133
  - 中日 2025 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: rf_def_floor_minus_ceiling=0.129, rank=5, rf_def_floor=-0.022, rf_def_mid=-0.147, rf_def_ceiling=-0.151, rf_def_total=-0.320 / surprise=0.129
  - 中日 2019 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2023 **(focus)**: rf_def_floor_minus_ceiling=0.103, rank=6, rf_def_floor=-0.200, rf_def_mid=-0.441, rf_def_ceiling=-0.303, rf_def_total=-0.944 / surprise=0.103
  - 中日 2023 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- ほか 1 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rf_def_floor_minus_ceiling=0.420, rank=3, rf_def_floor=-0.023, rf_def_mid=-0.180, rf_def_ceiling=-0.443, rf_def_total=-0.647

## P20: 得点がリーグ5位以下のチーム・シーズンでは、床の不足が天井の不足より大きい

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 40 件: d-2017, e-2015, d-2021, b-2016, b-2019 ほか
- もし: `（すべての単位）` ならば: `rf_def_floor_minus_ceiling < 0`
- 識別子: `[where:rank_rf>=5] * => rf_def_floor_minus_ceiling<0`（指紋 `1ca2a6db7ee62f2e`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 見直す条件（反証）: 低得点のチーム・シーズンの半数以上で、天井の不足のほうが大きい
- 注記: P19 と成立率を並べ、中日の形が低得点のチームの中で特別かを見る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 12 | 0.23 [0.14, 0.36] | 0.23 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 40 | 0 | 0.00 [0.00, 0.09] | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 40 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: rf_def_floor_minus_ceiling=0.481, rank=5, rf_def_floor=0.038, rf_def_ceiling=-0.443, rf_def_total=-0.694 / surprise=0.481
  - 中日 2017 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 楽天 2015: rf_def_floor_minus_ceiling=0.438, rank=6, rf_def_floor=-0.081, rf_def_ceiling=-0.519, rf_def_total=-0.926 / surprise=0.438
  - 楽天 2015 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rf_def_floor_minus_ceiling=0.341, rank=5, rf_def_floor=-0.175, rf_def_ceiling=-0.516, rf_def_total=-1.13 / surprise=0.341
  - 中日 2021 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- オリックス 2016: rf_def_floor_minus_ceiling=0.331, rank=6, rf_def_floor=-0.053, rf_def_ceiling=-0.385, rf_def_total=-0.709 / surprise=0.331
  - オリックス 2016 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- オリックス 2019: rf_def_floor_minus_ceiling=0.313, rank=6, rf_def_floor=-0.025, rf_def_ceiling=-0.338, rf_def_total=-0.607 / surprise=0.313
  - オリックス 2019 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- ロッテ 2017: rf_def_floor_minus_ceiling=0.312, rank=6, rf_def_floor=-0.099, rf_def_ceiling=-0.411, rf_def_total=-0.792 / surprise=0.312
  - ロッテ 2017 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- ロッテ 2018: rf_def_floor_minus_ceiling=0.287, rank=5, rf_def_floor=-0.024, rf_def_ceiling=-0.310, rf_def_total=-0.635 / surprise=0.287
  - ロッテ 2018 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- DeNA 2018: rf_def_floor_minus_ceiling=0.283, rank=4, rf_def_floor=-0.045, rf_def_ceiling=-0.327, rf_def_total=-0.446 / surprise=0.283
  - DeNA 2018 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2014 **(focus)**: rf_def_floor_minus_ceiling=0.261, rank=4, rf_def_floor=-0.025, rf_def_ceiling=-0.286, rf_def_total=-0.318 / surprise=0.261
  - 中日 2014 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 広島 2023: rf_def_floor_minus_ceiling=0.246, rank=2, rf_def_floor=0.052, rf_def_ceiling=-0.194, rf_def_total=-0.080 / surprise=0.246
  - 広島 2023 は「（すべての単位）」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- ほか 30 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rf_def_floor_minus_ceiling=0.420, rank=3, rf_def_floor=-0.023, rf_def_ceiling=-0.443, rf_def_total=-0.647
- オリックス 2020: rf_def_floor_minus_ceiling=0.108, rank=6, rf_def_floor=-0.130, rf_def_ceiling=-0.238, rf_def_total=-0.518
- ロッテ 2020: rf_def_floor_minus_ceiling=0.068, rank=2, rf_def_floor=-0.100, rf_def_ceiling=-0.168, rf_def_total=-0.328
- ヤクルト 2020: rf_def_floor_minus_ceiling=0.030, rank=6, rf_def_floor=-0.063, rf_def_ceiling=-0.093, rf_def_total=-0.257

## P21: 得点がリーグ5位以下のチームの間では、床の不足が天井の不足より大きい形なら B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 3 件: t-2022, h-2012, t-2013
- もし: `rf_def_floor_minus_ceiling < 0` ならば: `upper_half == False`
- 識別子: `[where:rank_rf>=5] rf_def_floor_minus_ceiling<0 => upper_half==false`（指紋 `0fd629213cbc0c8e`）
- 兄弟（範囲と結論が同じ、条件が違う）: P41, P42, P43, P49
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。不足の形は順位と関係しない
- 注記: 低得点のチームはもともと大半が B クラスなので、成立率より lift と p を読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 9 | 0.75 [0.47, 0.91] | 0.85 | 0.89 | 0.928 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 5 | 0.62 [0.31, 0.86] | 0.77 | 0.81 | 0.928 | 0 | 判断保留 | 4 |
| 逆 | 44 | 9 | 0.20 [0.11, 0.35] | 0.23 | 0.89 | 0.928 | 0 | 棄却 | 3 |
| 裏 | 40 | 5 | 0.12 [0.05, 0.26] | 0.15 | 0.81 | 0.928 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 3 件（対偶の判例も同じ）

- 阪神 2022: rf_def_floor_minus_ceiling=-0.063, upper_half=True, rank=3, rank_ra=1, rd=61, rf_def_total=-0.259 / surprise=2
  - 阪神 2022 は「rf_def_floor_minus_ceiling < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ソフトバンク 2012: rf_def_floor_minus_ceiling=-0.067, upper_half=True, rank=3, rank_ra=1, rd=23, rf_def_total=-0.276 / surprise=1
  - ソフトバンク 2012 は「rf_def_floor_minus_ceiling < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2013: rf_def_floor_minus_ceiling=-0.103, upper_half=True, rank=2, rank_ra=1, rd=43, rf_def_total=-0.322 / surprise=0
  - 阪神 2013 は「rf_def_floor_minus_ceiling < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（不成立）** 逆に判例 35 件（裏の判例も同じ）

- 中日 2019 **(focus)**: rf_def_floor_minus_ceiling=0.129, upper_half=False, rank=5, rank_ra=1, rd=19, rf_def_total=-0.320 / surprise=3
  - 中日 2019 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- ロッテ 2014: rf_def_floor_minus_ceiling=0.047, upper_half=False, rank=4, rank_ra=6, rd=-86, rf_def_total=-0.176 / surprise=-2
  - ロッテ 2014 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- DeNA 2018: rf_def_floor_minus_ceiling=0.283, upper_half=False, rank=4, rank_ra=3, rd=-70, rf_def_total=-0.446 / surprise=-2
  - DeNA 2018 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 日本ハム 2023: rf_def_floor_minus_ceiling=0.045, upper_half=False, rank=6, rank_ra=3, rd=-32, rf_def_total=-0.248 / surprise=2
  - 日本ハム 2023 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2013 **(focus)**: rf_def_floor_minus_ceiling=0.156, upper_half=False, rank=4, rank_ra=4, rd=-73, rf_def_total=-0.364 / surprise=-1
  - 中日 2013 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- DeNA 2014: rf_def_floor_minus_ceiling=0.078, upper_half=False, rank=5, rank_ra=5, rd=-56, rf_def_total=-0.335 / surprise=-1
  - DeNA 2014 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2015 **(focus)**: rf_def_floor_minus_ceiling=0.213, upper_half=False, rank=5, rank_ra=3, rd=-31, rf_def_total=-0.248 / surprise=1
  - 中日 2015 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 中日 2016 **(focus)**: rf_def_floor_minus_ceiling=0.025, upper_half=False, rank=6, rank_ra=4, rd=-73, rf_def_total=-0.524 / surprise=1
  - 中日 2016 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- 楽天 2018: rf_def_floor_minus_ceiling=0.245, upper_half=False, rank=6, rank_ra=3, rd=-63, rf_def_total=-0.752 / surprise=1
  - 楽天 2018 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- ロッテ 2018: rf_def_floor_minus_ceiling=0.287, upper_half=False, rank=5, rank_ra=5, rd=-94, rf_def_total=-0.635 / surprise=-1
  - ロッテ 2018 は「upper_half == False」を満たすのに「rf_def_floor_minus_ceiling < 0」を満たさない。なぜか？ → H2
- ほか 25 件（propositions.jsonl を参照）

## P22: 得点がリーグ5位以下だったシーズンの中日は、得点する回の頻度の不足が、得点した回の大きさの不足より大きい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 5 件: d-2017, d-2022, d-2013, d-2019, d-2025
- もし: `（すべての単位）` ならば: `inn_freq_minus_size < 0`
- 識別子: `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_freq_minus_size<0`（指紋 `82a06ac8994a73de`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、大きさの不足のほうが大きい
- 注記: 成り立てば「点が入る回が少ない」。成り立たなければ「入っても1点で止まる」側を調べる
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 6 | 0.55 [0.28, 0.79] | 0.55 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 5 | 0 | 0.00 [0.00, 0.43] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 5 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: inn_freq_minus_size=0.089, rank=5, inn_dlog_freq=-0.047, inn_dlog_size=-0.136, inn_dlog_rpi=-0.183 / surprise=0.089
  - 中日 2017 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2022 **(focus)**: inn_freq_minus_size=0.049, rank=6, inn_dlog_freq=-0.107, inn_dlog_size=-0.156, inn_dlog_rpi=-0.263 / surprise=0.049
  - 中日 2022 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2013 **(focus)**: inn_freq_minus_size=0.043, rank=4, inn_dlog_freq=-0.029, inn_dlog_size=-0.072, inn_dlog_rpi=-0.101 / surprise=0.043
  - 中日 2013 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2019 **(focus)**: inn_freq_minus_size=0.040, rank=5, inn_dlog_freq=-0.012, inn_dlog_size=-0.052, inn_dlog_rpi=-0.063 / surprise=0.040
  - 中日 2019 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2025 **(focus)**: inn_freq_minus_size=0.018, rank=4, inn_dlog_freq=-0.068, inn_dlog_size=-0.087, inn_dlog_rpi=-0.155 / surprise=0.018
  - 中日 2025 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: inn_freq_minus_size=0.031, rank=3, inn_dlog_freq=-0.065, inn_dlog_size=-0.096, inn_dlog_rpi=-0.161

## P23: 得点がリーグ5位以下のチーム・シーズンでは、得点する回の頻度の不足が、得点した回の大きさの不足より大きい

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 13 件: d-2017, f-2023, d-2022, db-2018, d-2013 ほか
- もし: `（すべての単位）` ならば: `inn_freq_minus_size < 0`
- 識別子: `[seasons=2013-2025, where:rank_rf>=5] * => inn_freq_minus_size<0`（指紋 `05c8055d2de1c4da`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 48
- 見直す条件（反証）: 低得点のチーム・シーズンの半数以上で、大きさの不足のほうが大きい
- 注記: P22 と成立率を並べ、中日の形が低得点のチームの中で特別かを見る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 35 | 0.73 [0.59, 0.83] | 0.73 | 1.00 | 1.000 | 0 | 支持 | 1 |
| 対偶 | 13 | 0 | 0.00 [0.00, 0.23] | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（例外あり）** 元の命題に判例 13 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: inn_freq_minus_size=0.089, rank=5, inn_dlog_freq=-0.047, inn_dlog_size=-0.136 / surprise=0.089
  - 中日 2017 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2023: inn_freq_minus_size=0.065, rank=6, inn_dlog_freq=-0.003, inn_dlog_size=-0.068 / surprise=0.065
  - 日本ハム 2023 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2022 **(focus)**: inn_freq_minus_size=0.049, rank=6, inn_dlog_freq=-0.107, inn_dlog_size=-0.156 / surprise=0.049
  - 中日 2022 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2018: inn_freq_minus_size=0.043, rank=4, inn_dlog_freq=-0.029, inn_dlog_size=-0.072 / surprise=0.043
  - DeNA 2018 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2013 **(focus)**: inn_freq_minus_size=0.043, rank=4, inn_dlog_freq=-0.029, inn_dlog_size=-0.072 / surprise=0.043
  - 中日 2013 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2019 **(focus)**: inn_freq_minus_size=0.040, rank=5, inn_dlog_freq=-0.012, inn_dlog_size=-0.052 / surprise=0.040
  - 中日 2019 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2015: inn_freq_minus_size=0.038, rank=6, inn_dlog_freq=-0.117, inn_dlog_size=-0.156 / surprise=0.038
  - 楽天 2015 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 広島 2023: inn_freq_minus_size=0.023, rank=2, inn_dlog_freq=0.008, inn_dlog_size=-0.015 / surprise=0.023
  - 広島 2023 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2025 **(focus)**: inn_freq_minus_size=0.018, rank=4, inn_dlog_freq=-0.068, inn_dlog_size=-0.087 / surprise=0.018
  - 中日 2025 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2024: inn_freq_minus_size=0.010, rank=5, inn_dlog_freq=-0.089, inn_dlog_size=-0.098 / surprise=0.010
  - オリックス 2024 は「（すべての単位）」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- ほか 3 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: inn_freq_minus_size=0.031, rank=3, inn_dlog_freq=-0.065, inn_dlog_size=-0.096

## P24: 得点がリーグ5位以下のチームの間では、得点する回の頻度の不足が大きい形なら B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: t-2015, t-2019, t-2022, t-2013
- もし: `inn_freq_minus_size < 0` ならば: `upper_half == False`
- 識別子: `[seasons=2013-2025, where:rank_rf>=5] inn_freq_minus_size<0 => upper_half==false`（指紋 `948cdd3811232de9`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 48
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。形は順位と関係しない
- 注記: 低得点のチームはもともと大半が B クラスなので、成立率より lift と p を読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 35 | 31 | 0.89 [0.74, 0.95] | 0.85 | 1.04 | 0.278 | 0 | 判断保留 | 4 |
| 対偶 | 7 | 3 | 0.43 [0.16, 0.75] | 0.27 | 1.58 | 0.278 | 0 | 判断保留 | 4 |
| 逆 | 41 | 31 | 0.76 [0.61, 0.86] | 0.73 | 1.04 | 0.278 | 0 | 判断保留 | 4 |
| 裏 | 13 | 3 | 0.23 [0.08, 0.50] | 0.15 | 1.58 | 0.278 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 阪神 2015: inn_freq_minus_size=-0.016, upper_half=True, rank=3, rank_ra=5, rd=-85, inn_dlog_rpi=-0.088 / surprise=-3
  - 阪神 2015 は「inn_freq_minus_size < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 阪神 2019: inn_freq_minus_size=-0.079, upper_half=True, rank=3, rank_ra=2, rd=-28, inn_dlog_rpi=-0.140 / surprise=-2
  - 阪神 2019 は「inn_freq_minus_size < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 阪神 2022: inn_freq_minus_size=-0.125, upper_half=True, rank=3, rank_ra=1, rd=61, inn_dlog_rpi=-0.064 / surprise=2
  - 阪神 2022 は「inn_freq_minus_size < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 阪神 2013: inn_freq_minus_size=-0.134, upper_half=True, rank=2, rank_ra=1, rd=43, inn_dlog_rpi=-0.085 / surprise=0
  - 阪神 2013 は「inn_freq_minus_size < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6

**待った！判断保留** 逆に判例 10 件（裏の判例も同じ）

- 中日 2019 **(focus)**: inn_freq_minus_size=0.040, upper_half=False, rank=5, rank_ra=1, rd=19, inn_dlog_rpi=-0.063 / surprise=3
  - 中日 2019 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2018: inn_freq_minus_size=0.043, upper_half=False, rank=4, rank_ra=3, rd=-70, inn_dlog_rpi=-0.100 / surprise=-2
  - DeNA 2018 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2023: inn_freq_minus_size=0.065, upper_half=False, rank=6, rank_ra=3, rd=-32, inn_dlog_rpi=-0.071 / surprise=2
  - 日本ハム 2023 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2013 **(focus)**: inn_freq_minus_size=0.043, upper_half=False, rank=4, rank_ra=4, rd=-73, inn_dlog_rpi=-0.101 / surprise=-1
  - 中日 2013 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2024: inn_freq_minus_size=0.010, upper_half=False, rank=5, rank_ra=2, rd=-46, inn_dlog_rpi=-0.187 / surprise=1
  - オリックス 2024 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2025 **(focus)**: inn_freq_minus_size=0.018, upper_half=False, rank=4, rank_ra=4, rd=-60, inn_dlog_rpi=-0.155 / surprise=-1
  - 中日 2025 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 西武 2025: inn_freq_minus_size=0.001, upper_half=False, rank=5, rank_ra=3, rd=-55, inn_dlog_rpi=-0.194 / surprise=1
  - 西武 2025 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2015: inn_freq_minus_size=0.038, upper_half=False, rank=6, rank_ra=6, rd=-149, inn_dlog_rpi=-0.273 / surprise=0
  - 楽天 2015 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2017 **(focus)**: inn_freq_minus_size=0.089, upper_half=False, rank=5, rank_ra=5, rd=-136, inn_dlog_rpi=-0.183 / surprise=0
  - 中日 2017 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2022 **(focus)**: inn_freq_minus_size=0.049, upper_half=False, rank=6, rank_ra=2, rd=-81, inn_dlog_rpi=-0.263 / surprise=0
  - 中日 2022 は「upper_half == False」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: inn_freq_minus_size=-0.069, upper_half=True, rank=2, rank_ra=2, rd=-18, inn_dlog_rpi=-0.077

## P25: P22 を、双方が6回まで攻撃した試合の1〜6回だけで見ても、頻度の不足が大きさの不足より大きい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: d-2017, d-2019, d-2022, d-2025
- もし: `（すべての単位）` ならば: `inn_freq_minus_size_6 < 0`
- 識別子: `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_freq_minus_size_6<0`（指紋 `a595b298bbd4138f`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: P22 と判定が食い違う（9回裏の省略・延長の扱いが結果を左右している）
- 注記: 9回裏の省略・サヨナラの途中終了の影響を小さくした比較。補正ではない
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 7 | 0.64 [0.35, 0.85] | 0.64 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: inn_freq_minus_size_6=0.144, inn_dlog_freq_6=-0.020, inn_dlog_size_6=-0.163, inn_freq_minus_size=0.089 / surprise=0.144
  - 中日 2017 は「（すべての単位）」を満たすのに「inn_freq_minus_size_6 < 0」を満たさない。なぜか？ → H5, H6
- 中日 2019 **(focus)**: inn_freq_minus_size_6=0.043, inn_dlog_freq_6=0.003, inn_dlog_size_6=-0.040, inn_freq_minus_size=0.040 / surprise=0.043
  - 中日 2019 は「（すべての単位）」を満たすのに「inn_freq_minus_size_6 < 0」を満たさない。なぜか？ → H5, H6
- 中日 2022 **(focus)**: inn_freq_minus_size_6=0.041, inn_dlog_freq_6=-0.141, inn_dlog_size_6=-0.182, inn_freq_minus_size=0.049 / surprise=0.041
  - 中日 2022 は「（すべての単位）」を満たすのに「inn_freq_minus_size_6 < 0」を満たさない。なぜか？ → H5, H6
- 中日 2025 **(focus)**: inn_freq_minus_size_6=0.034, inn_dlog_freq_6=-0.093, inn_dlog_size_6=-0.127, inn_freq_minus_size=0.018 / surprise=0.034
  - 中日 2025 は「（すべての単位）」を満たすのに「inn_freq_minus_size_6 < 0」を満たさない。なぜか？ → H5, H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: inn_freq_minus_size_6=0.030, inn_dlog_freq_6=-0.067, inn_dlog_size_6=-0.097, inn_freq_minus_size=0.031

## P26: 得点がリーグ5位以下だったシーズンの中日は、得点した回のうち1点の回の割合が他球団より多い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2015
- もし: `（すべての単位）` ならば: `inn_d_single_share > 0`
- 識別子: `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_d_single_share>0`（指紋 `988b565d9c44d836`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、1点の回の割合が他球団以下
- 注記: P27 と組で読む。片方だけ成り立つなら、大きさの不足はその側に集中している
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 5 回、元の命題に異議あり 5 回（どれかの形に異議あり 5 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | 0.91 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2015 **(focus)**: inn_d_single_share=-0.008, inn_d_big_share=-0.015, inn_dlog_size=-0.028, rank=5 / surprise=-0.008
  - 中日 2015 は「（すべての単位）」を満たすのに「inn_d_single_share > 0」を満たさない。なぜか？ → H5, H6

## P27: 得点がリーグ5位以下だったシーズンの中日は、得点した回のうち3点以上の回の割合が他球団より少ない

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `（すべての単位）` ならば: `inn_d_big_share < 0`
- 識別子: `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_d_big_share<0`（指紋 `899ff74649bd67f2`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、3点以上の回の割合が他球団以上
- 注記: P30（中日以外の低得点のチーム）と成立率を並べ、中日固有かを見る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 5 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 5 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## P28: 得点がリーグ5位以下だったシーズンの中日は、ホームの試合で得点した回の大きさが他球団（ホーム同士）より小さい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2014
- もし: `（すべての単位）` ならば: `inn_dlog_size_home < 0`
- 識別子: `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_dlog_size_home<0`（指紋 `982ba976095d3ed6`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、ホームの大きさが他球団以上
- 注記: 球場の係数ではない。ホーム同士で比べるだけ。P29 と片方だけ成り立つなら、主催区分の問題として扱う（原因は特定しない）
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 5 回、元の命題に異議あり 5 回（どれかの形に異議あり 5 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | 0.91 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2014 **(focus)**: inn_dlog_size_home=0.009, inn_dlog_size_away=-0.055, inn_dlog_size=-0.024, inn_dlog_freq_home=-0.117 / surprise=0.009
  - 中日 2014 は「（すべての単位）」を満たすのに「inn_dlog_size_home < 0」を満たさない。なぜか？ → H5, H6

## P29: 得点がリーグ5位以下だったシーズンの中日は、ビジターの試合で得点した回の大きさが他球団（ビジター同士）より小さい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2016
- もし: `（すべての単位）` ならば: `inn_dlog_size_away < 0`
- 識別子: `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_dlog_size_away<0`（指紋 `a826d28bc87ede56`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、ビジターの大きさが他球団以上
- 注記: P28 と組で読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 5 回、元の命題に異議あり 5 回（どれかの形に異議あり 5 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | 0.91 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2016 **(focus)**: inn_dlog_size_away=0.037, inn_dlog_size_home=-0.002, inn_dlog_size=0.018, inn_dlog_freq_away=-0.052 / surprise=0.037
  - 中日 2016 は「（すべての単位）」を満たすのに「inn_dlog_size_away < 0」を満たさない。なぜか？ → H5, H6

## P30: 得点がリーグ5位以下のチーム・シーズン（中日を除く）では、得点した回のうち3点以上の回の割合が他球団より少ない

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 9 件: e-2014, e-2016, m-2025, f-2019, l-2024 ほか
- もし: `（すべての単位）` ならば: `inn_d_big_share < 0`
- 識別子: `[seasons=2013-2025, where:rank_rf>=5, where:team!="d"] * => inn_d_big_share<0`（指紋 `e72b9ea879f71acf`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 37
- 見直す条件（反証）: 中日以外の低得点のチーム・シーズンの半数以上で、3点以上の回の割合が他球団以上
- 注記: P27 と同じくらい成り立つなら、3点以上の回の少なさは低得点のチームに共通
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 5 回、元の命題に異議あり 5 回（どれかの形に異議あり 5 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 37 | 28 | 0.76 [0.60, 0.87] | 0.76 | 1.00 | 1.000 | 0 | 支持 | 1 |
| 対偶 | 9 | 0 | 0.00 [0.00, 0.30] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（例外あり）** 元の命題に判例 9 件（対偶の判例も同じ）

- 楽天 2014: inn_d_big_share=0.034, inn_d_single_share=-0.040, inn_dlog_size=0.049, rank=6 / surprise=0.034
  - 楽天 2014 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2016: inn_d_big_share=0.022, inn_d_single_share=-0.010, inn_dlog_size=0.034, rank=5 / surprise=0.022
  - 楽天 2016 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2025: inn_d_big_share=0.019, inn_d_single_share=0.000, inn_dlog_size=0.018, rank=6 / surprise=0.019
  - ロッテ 2025 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2019: inn_d_big_share=0.011, inn_d_single_share=-0.011, inn_dlog_size=0.031, rank=5 / surprise=0.011
  - 日本ハム 2019 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 西武 2024: inn_d_big_share=0.010, inn_d_single_share=0.026, inn_dlog_size=-0.032, rank=6 / surprise=0.010
  - 西武 2024 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 西武 2021: inn_d_big_share=0.008, inn_d_single_share=-0.010, inn_dlog_size=0.015, rank=6 / surprise=0.008
  - 西武 2021 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 阪神 2022: inn_d_big_share=0.006, inn_d_single_share=-0.048, inn_dlog_size=0.031, rank=3 / surprise=0.006
  - 阪神 2022 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 阪神 2013: inn_d_big_share=0.002, inn_d_single_share=0.013, inn_dlog_size=0.024, rank=2 / surprise=0.002
  - 阪神 2013 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2015: inn_d_big_share=0.001, inn_d_single_share=-0.004, inn_dlog_size=0.014, rank=5 / surprise=0.001
  - オリックス 2015 は「（すべての単位）」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: inn_d_big_share=0.022, inn_d_single_share=0.011, inn_dlog_size=-0.004, rank=2
- ヤクルト 2020: inn_d_big_share=0.020, inn_d_single_share=-0.021, inn_dlog_size=0.009, rank=6

## P31: 得点がリーグ5位以下だったシーズンの中日は、ISO（長打率 − 打率）が他球団より低い

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `（すべての単位）` ならば: `bat_d_iso < 0`
- 識別子: `[team=d, where:rank_rf>=5] * => bat_d_iso<0`（指紋 `7515ccfadec138d8`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、ISO が他球団以上
- 注記: P32 と組で読む。片方だけ成り立つなら、不足はその側に寄る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## P32: 得点がリーグ5位以下だったシーズンの中日は、出塁率が他球団より低い

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `（すべての単位）` ならば: `bat_d_obp < 0`
- 識別子: `[team=d, where:rank_rf>=5] * => bat_d_obp<0`（指紋 `c0b8da141e31af81`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、出塁率が他球団以上
- 注記: P31 と組で読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## P33: ISO が同じ年・同じリーグの他球団より低ければ、得点した回のうち3点以上の回の割合も他球団より少ない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 26 件: t-2023, m-2022, c-2022, s-2016, m-2016 ほか
- もし: `bat_d_iso < 0` ならば: `inn_d_big_share < 0`
- 識別子: `[seasons=2013-2025] bat_d_iso<0 => inn_d_big_share<0`（指紋 `3a4203e6412ef7e6`）
- 兄弟（範囲と結論が同じ、条件が違う）: P35
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: ISO が低いチーム・シーズンの4分の1を超えて、3点以上の回の割合が他球団以上
- 注記: 成り立たなければ、ISO と大量点の回を結ぶ見方そのものを弱める（中日の R5 の結果を長打で説明できなくなる）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 50 | 0.66 [0.55, 0.75] | 0.50 | 1.32 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 72 | 46 | 0.64 [0.52, 0.74] | 0.47 | 1.35 | 0.000 | 0 | 修正 | 2 |
| 逆 | 72 | 50 | 0.69 [0.58, 0.79] | 0.53 | 1.32 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 68 | 46 | 0.68 [0.56, 0.78] | 0.50 | 1.35 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 26 件（対偶の判例も同じ）

- 阪神 2023: bat_d_iso=-0.016, inn_d_big_share=0.076, bat_d_obp=0.020, inn_dlog_size=0.071, rank=1 / surprise=0.076
  - 阪神 2023 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ロッテ 2022: bat_d_iso=-0.009, inn_d_big_share=0.052, bat_d_obp=-0.007, inn_dlog_size=0.030, rank=5 / surprise=0.052
  - ロッテ 2022 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 広島 2022: bat_d_iso=-0.017, inn_d_big_share=0.047, bat_d_obp=0.001, inn_dlog_size=0.103, rank=5 / surprise=0.047
  - 広島 2022 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ヤクルト 2016: bat_d_iso=-0.004, inn_d_big_share=0.043, bat_d_obp=0.015, inn_dlog_size=0.021, rank=5 / surprise=0.043
  - ヤクルト 2016 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ロッテ 2016: bat_d_iso=-0.010, inn_d_big_share=0.036, bat_d_obp=-0.005, inn_dlog_size=0.073, rank=3 / surprise=0.036
  - ロッテ 2016 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 楽天 2014: bat_d_iso=-0.024, inn_d_big_share=0.034, bat_d_obp=-0.001, inn_dlog_size=0.049, rank=6 / surprise=0.034
  - 楽天 2014 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 巨人 2017: bat_d_iso=-0.003, inn_d_big_share=0.030, bat_d_obp=0.000, inn_dlog_size=0.004, rank=4 / surprise=0.030
  - 巨人 2017 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 楽天 2013: bat_d_iso=-0.003, inn_d_big_share=0.027, bat_d_obp=0.008, inn_dlog_size=0.043, rank=1 / surprise=0.027
  - 楽天 2013 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 阪神 2024: bat_d_iso=-0.013, inn_d_big_share=0.027, bat_d_obp=0.011, inn_dlog_size=0.044, rank=2 / surprise=0.027
  - 阪神 2024 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ヤクルト 2018: bat_d_iso=-0.004, inn_d_big_share=0.024, bat_d_obp=0.020, inn_dlog_size=0.036, rank=2 / surprise=0.024
  - ヤクルト 2018 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ほか 16 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 22 件（裏の判例も同じ）

- 西武 2016: bat_d_iso=0.019, inn_d_big_share=-0.036, bat_d_obp=0.005, inn_dlog_size=-0.069, rank=4 / surprise=-0.036
  - 西武 2016 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 巨人 2016: bat_d_iso=0.009, inn_d_big_share=-0.034, bat_d_obp=-0.011, inn_dlog_size=-0.050, rank=2 / surprise=-0.034
  - 巨人 2016 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ヤクルト 2024: bat_d_iso=0.012, inn_d_big_share=-0.029, bat_d_obp=0.008, inn_dlog_size=-0.057, rank=5 / surprise=-0.029
  - ヤクルト 2024 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2018: bat_d_iso=0.029, inn_d_big_share=-0.027, bat_d_obp=-0.028, inn_dlog_size=-0.072, rank=4 / surprise=-0.027
  - DeNA 2018 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ヤクルト 2014: bat_d_iso=0.007, inn_d_big_share=-0.026, bat_d_obp=0.013, inn_dlog_size=-0.020, rank=6 / surprise=-0.026
  - ヤクルト 2014 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ソフトバンク 2019: bat_d_iso=0.023, inn_d_big_share=-0.025, bat_d_obp=-0.016, inn_dlog_size=-0.103, rank=2 / surprise=-0.025
  - ソフトバンク 2019 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2022: bat_d_iso=0.006, inn_d_big_share=-0.022, bat_d_obp=0.001, inn_dlog_size=-0.067, rank=2 / surprise=-0.022
  - DeNA 2022 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 西武 2022: bat_d_iso=0.012, inn_d_big_share=-0.022, bat_d_obp=-0.014, inn_dlog_size=-0.045, rank=3 / surprise=-0.022
  - 西武 2022 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 広島 2015: bat_d_iso=0.014, inn_d_big_share=-0.019, bat_d_obp=-0.002, inn_dlog_size=0.003, rank=4 / surprise=-0.019
  - 広島 2015 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2014: bat_d_iso=0.003, inn_d_big_share=-0.018, bat_d_obp=-0.014, inn_dlog_size=-0.017, rank=5 / surprise=-0.018
  - DeNA 2014 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ほか 12 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: bat_d_iso=-0.013, inn_d_big_share=0.022, bat_d_obp=0.004, inn_dlog_size=-0.004, rank=2
- ヤクルト 2020: bat_d_iso=-0.004, inn_d_big_share=0.020, bat_d_obp=-0.003, inn_dlog_size=0.009, rank=6
- 阪神 2020: bat_d_iso=-0.001, inn_d_big_share=0.018, bat_d_obp=-0.003, inn_dlog_size=0.023, rank=2

## P34: 出塁率が同じ年・同じリーグの他球団より低ければ、得点する回の頻度も他球団より低い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 15 件: f-2024, h-2019, f-2014, db-2017, b-2021 ほか
- もし: `bat_d_obp < 0` ならば: `inn_dlog_freq < 0`
- 識別子: `[seasons=2013-2025] bat_d_obp<0 => inn_dlog_freq<0`（指紋 `110dc7e378cb3acc`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: 出塁率が低いチーム・シーズンの4分の1を超えて、得点する回の頻度が他球団以上
- 注記: P33 と対で、出塁 ↔ 頻度、長打 ↔ 大きさ、という対応が成り立つかを見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 72 | 57 | 0.79 [0.68, 0.87] | 0.47 | 1.68 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 76 | 61 | 0.80 [0.70, 0.88] | 0.50 | 1.61 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 68 | 57 | 0.84 [0.73, 0.91] | 0.50 | 1.68 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 72 | 61 | 0.85 [0.75, 0.91] | 0.53 | 1.61 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 15 件（対偶の判例も同じ）

- 日本ハム 2024: bat_d_obp=-0.001, inn_dlog_freq=0.135, bat_d_iso=0.020, rank=2 / surprise=0.135
  - 日本ハム 2024 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- ソフトバンク 2019: bat_d_obp=-0.016, inn_dlog_freq=0.049, bat_d_iso=0.023, rank=2 / surprise=0.049
  - ソフトバンク 2019 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- 日本ハム 2014: bat_d_obp=-0.009, inn_dlog_freq=0.047, bat_d_iso=0.007, rank=3 / surprise=0.047
  - 日本ハム 2014 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- DeNA 2017: bat_d_obp=-0.008, inn_dlog_freq=0.035, bat_d_iso=0.015, rank=3 / surprise=0.035
  - DeNA 2017 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- オリックス 2021: bat_d_obp=-0.004, inn_dlog_freq=0.033, bat_d_iso=0.006, rank=1 / surprise=0.033
  - オリックス 2021 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- DeNA 2016: bat_d_obp=-0.012, inn_dlog_freq=0.031, bat_d_iso=0.012, rank=3 / surprise=0.031
  - DeNA 2016 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- DeNA 2015: bat_d_obp=-0.009, inn_dlog_freq=0.029, bat_d_iso=0.016, rank=6 / surprise=0.029
  - DeNA 2015 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- ソフトバンク 2021: bat_d_obp=-0.001, inn_dlog_freq=0.025, bat_d_iso=0.015, rank=4 / surprise=0.025
  - ソフトバンク 2021 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- 巨人 2021: bat_d_obp=-0.006, inn_dlog_freq=0.023, bat_d_iso=0.029, rank=3 / surprise=0.023
  - 巨人 2021 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- 中日 2018 **(focus)**: bat_d_obp=-0.007, inn_dlog_freq=0.020, bat_d_iso=-0.030, rank=5 / surprise=0.020
  - 中日 2018 は「bat_d_obp < 0」を満たすのに「inn_dlog_freq < 0」を満たさない。なぜか？ → H5
- ほか 5 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 11 件（裏の判例も同じ）

- 阪神 2013: bat_d_obp=0.004, inn_dlog_freq=-0.109, bat_d_iso=-0.022, rank=2 / surprise=-0.109
  - 阪神 2013 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- 巨人 2024: bat_d_obp=0.006, inn_dlog_freq=-0.103, bat_d_iso=0.008, rank=1 / surprise=-0.103
  - 巨人 2024 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- 巨人 2017: bat_d_obp=0.000, inn_dlog_freq=-0.057, bat_d_iso=-0.003, rank=4 / surprise=-0.057
  - 巨人 2017 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- 阪神 2015: bat_d_obp=0.004, inn_dlog_freq=-0.052, bat_d_iso=-0.016, rank=3 / surprise=-0.052
  - 阪神 2015 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- 阪神 2014: bat_d_obp=0.007, inn_dlog_freq=-0.046, bat_d_iso=-0.019, rank=2 / surprise=-0.046
  - 阪神 2014 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- オリックス 2025: bat_d_obp=0.008, inn_dlog_freq=-0.043, bat_d_iso=0.005, rank=3 / surprise=-0.043
  - オリックス 2025 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- 広島 2022: bat_d_obp=0.001, inn_dlog_freq=-0.030, bat_d_iso=-0.017, rank=5 / surprise=-0.030
  - 広島 2022 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- 日本ハム 2018: bat_d_obp=0.006, inn_dlog_freq=-0.026, bat_d_iso=-0.003, rank=3 / surprise=-0.026
  - 日本ハム 2018 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- オリックス 2023: bat_d_obp=0.002, inn_dlog_freq=-0.023, bat_d_iso=0.007, rank=1 / surprise=-0.023
  - オリックス 2023 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- 巨人 2025: bat_d_obp=0.013, inn_dlog_freq=-0.017, bat_d_iso=0.003, rank=3 / surprise=-0.017
  - 巨人 2025 は「inn_dlog_freq < 0」を満たすのに「bat_d_obp < 0」を満たさない。なぜか？ → H5
- ほか 1 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ソフトバンク 2020: bat_d_obp=-0.006, inn_dlog_freq=0.106, bat_d_iso=0.025, rank=1
- 西武 2020: bat_d_obp=-0.012, inn_dlog_freq=0.006, bat_d_iso=0.006, rank=3

## P35: ISO が同じ年・同じリーグの他球団より低ければ、得点した回のうち3点以上の回の割合も他球団より少ないことが多い

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 26 件: t-2023, m-2022, c-2022, s-2016, m-2016 ほか
- もし: `bat_d_iso < 0` ならば: `inn_d_big_share < 0`
- 識別子: `[seasons=2013-2025] bat_d_iso<0 => inn_d_big_share<0`（指紋 `3a4203e6412ef7e6`）
- 兄弟（範囲と結論が同じ、条件が違う）: P33
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 親: P33（変更: 強さを usually（0.75）から more_often_than_not（0.50）に下げた。P33 は成立率 0.66・lift 1.32・p < 0.001 で、関係はあるが「概ね」に届かなかった。同じデータでの言い直しで、確かめではない）
- 見直す条件（反証）: ISO が低いチーム・シーズンの半数以上で、3点以上の回の割合が他球団以上
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 3 回、元の命題に異議あり 3 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 50 | 0.66 [0.55, 0.75] | 0.50 | 1.32 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 72 | 46 | 0.64 [0.52, 0.74] | 0.47 | 1.35 | 0.000 | 0 | 支持 | 1 |
| 逆 | 72 | 50 | 0.69 [0.58, 0.79] | 0.53 | 1.32 | 0.000 | 0 | 支持 | 1 |
| 裏 | 68 | 46 | 0.68 [0.56, 0.78] | 0.50 | 1.35 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 26 件（対偶の判例も同じ）

- 阪神 2023: bat_d_iso=-0.016, inn_d_big_share=0.076, bat_d_obp=0.020, inn_dlog_size=0.071, rank=1 / surprise=0.076
  - 阪神 2023 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ロッテ 2022: bat_d_iso=-0.009, inn_d_big_share=0.052, bat_d_obp=-0.007, inn_dlog_size=0.030, rank=5 / surprise=0.052
  - ロッテ 2022 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 広島 2022: bat_d_iso=-0.017, inn_d_big_share=0.047, bat_d_obp=0.001, inn_dlog_size=0.103, rank=5 / surprise=0.047
  - 広島 2022 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ヤクルト 2016: bat_d_iso=-0.004, inn_d_big_share=0.043, bat_d_obp=0.015, inn_dlog_size=0.021, rank=5 / surprise=0.043
  - ヤクルト 2016 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ロッテ 2016: bat_d_iso=-0.010, inn_d_big_share=0.036, bat_d_obp=-0.005, inn_dlog_size=0.073, rank=3 / surprise=0.036
  - ロッテ 2016 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 楽天 2014: bat_d_iso=-0.024, inn_d_big_share=0.034, bat_d_obp=-0.001, inn_dlog_size=0.049, rank=6 / surprise=0.034
  - 楽天 2014 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 巨人 2017: bat_d_iso=-0.003, inn_d_big_share=0.030, bat_d_obp=0.000, inn_dlog_size=0.004, rank=4 / surprise=0.030
  - 巨人 2017 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 楽天 2013: bat_d_iso=-0.003, inn_d_big_share=0.027, bat_d_obp=0.008, inn_dlog_size=0.043, rank=1 / surprise=0.027
  - 楽天 2013 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- 阪神 2024: bat_d_iso=-0.013, inn_d_big_share=0.027, bat_d_obp=0.011, inn_dlog_size=0.044, rank=2 / surprise=0.027
  - 阪神 2024 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ヤクルト 2018: bat_d_iso=-0.004, inn_d_big_share=0.024, bat_d_obp=0.020, inn_dlog_size=0.036, rank=2 / surprise=0.024
  - ヤクルト 2018 は「bat_d_iso < 0」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H6
- ほか 16 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 22 件（裏の判例も同じ）

- 西武 2016: bat_d_iso=0.019, inn_d_big_share=-0.036, bat_d_obp=0.005, inn_dlog_size=-0.069, rank=4 / surprise=-0.036
  - 西武 2016 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 巨人 2016: bat_d_iso=0.009, inn_d_big_share=-0.034, bat_d_obp=-0.011, inn_dlog_size=-0.050, rank=2 / surprise=-0.034
  - 巨人 2016 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ヤクルト 2024: bat_d_iso=0.012, inn_d_big_share=-0.029, bat_d_obp=0.008, inn_dlog_size=-0.057, rank=5 / surprise=-0.029
  - ヤクルト 2024 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2018: bat_d_iso=0.029, inn_d_big_share=-0.027, bat_d_obp=-0.028, inn_dlog_size=-0.072, rank=4 / surprise=-0.027
  - DeNA 2018 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ヤクルト 2014: bat_d_iso=0.007, inn_d_big_share=-0.026, bat_d_obp=0.013, inn_dlog_size=-0.020, rank=6 / surprise=-0.026
  - ヤクルト 2014 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ソフトバンク 2019: bat_d_iso=0.023, inn_d_big_share=-0.025, bat_d_obp=-0.016, inn_dlog_size=-0.103, rank=2 / surprise=-0.025
  - ソフトバンク 2019 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2022: bat_d_iso=0.006, inn_d_big_share=-0.022, bat_d_obp=0.001, inn_dlog_size=-0.067, rank=2 / surprise=-0.022
  - DeNA 2022 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 西武 2022: bat_d_iso=0.012, inn_d_big_share=-0.022, bat_d_obp=-0.014, inn_dlog_size=-0.045, rank=3 / surprise=-0.022
  - 西武 2022 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 広島 2015: bat_d_iso=0.014, inn_d_big_share=-0.019, bat_d_obp=-0.002, inn_dlog_size=0.003, rank=4 / surprise=-0.019
  - 広島 2015 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2014: bat_d_iso=0.003, inn_d_big_share=-0.018, bat_d_obp=-0.014, inn_dlog_size=-0.017, rank=5 / surprise=-0.018
  - DeNA 2014 は「inn_d_big_share < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ほか 12 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: bat_d_iso=-0.013, inn_d_big_share=0.022, bat_d_obp=0.004, inn_dlog_size=-0.004, rank=2
- ヤクルト 2020: bat_d_iso=-0.004, inn_d_big_share=0.020, bat_d_obp=-0.003, inn_dlog_size=0.009, rank=6
- 阪神 2020: bat_d_iso=-0.001, inn_d_big_share=0.018, bat_d_obp=-0.003, inn_dlog_size=0.023, rank=2

## P36: 得点がリーグ5位以下だったシーズンの中日は、床（k = 1〜2）の不足が、同じ幅の天井側（k = 6〜7）の不足より大きい

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 8 件: d-2017, d-2013, d-2015, d-2021, d-2024 ほか
- もし: `（すべての単位）` ならば: `rf_def_floor_minus_k67 < 0`
- 識別子: `[team=d, where:rank_rf>=5] * => rf_def_floor_minus_k67<0`（指紋 `571be9cd79e6babb`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 親: P19（変更: 天井の帯を k ≥ 6（幅の上限なし）から k = 6〜7（床と同じ幅2）に変えた。R3 の比較は、得点の量で比べると天井が大きく出る作りだったため（R3 の自分への異議））
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、k = 6〜7 の不足のほうが大きい
- 注記: P19 と同じく不成立なら、R3 の読みは帯の幅の作りのせいではなかった
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 3 回、元の命題に異議あり 3 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 3 | 0.27 [0.10, 0.57] | 0.27 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 8 | 0 | 0.00 [0.00, 0.32] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 8 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: rf_def_floor_minus_k67=0.196, rf_def_floor=0.038, rf_def_k67=-0.158, rf_def_total=-0.694, rank=5 / surprise=0.196
  - 中日 2017 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2013 **(focus)**: rf_def_floor_minus_k67=0.097, rf_def_floor=-0.036, rf_def_k67=-0.133, rf_def_total=-0.364, rank=4 / surprise=0.097
  - 中日 2013 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2015 **(focus)**: rf_def_floor_minus_k67=0.095, rf_def_floor=-0.004, rf_def_k67=-0.099, rf_def_total=-0.248, rank=5 / surprise=0.095
  - 中日 2015 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rf_def_floor_minus_k67=0.048, rf_def_floor=-0.175, rf_def_k67=-0.222, rf_def_total=-1.13, rank=5 / surprise=0.048
  - 中日 2021 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2024 **(focus)**: rf_def_floor_minus_k67=0.048, rf_def_floor=-0.101, rf_def_k67=-0.148, rf_def_total=-0.734, rank=6 / surprise=0.048
  - 中日 2024 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: rf_def_floor_minus_k67=0.042, rf_def_floor=-0.022, rf_def_k67=-0.064, rf_def_total=-0.320, rank=5 / surprise=0.042
  - 中日 2019 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2025 **(focus)**: rf_def_floor_minus_k67=0.027, rf_def_floor=-0.090, rf_def_k67=-0.116, rf_def_total=-0.473, rank=4 / surprise=0.027
  - 中日 2025 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2014 **(focus)**: rf_def_floor_minus_k67=0.003, rf_def_floor=-0.025, rf_def_k67=-0.028, rf_def_total=-0.318, rank=4 / surprise=0.003
  - 中日 2014 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rf_def_floor_minus_k67=0.168, rf_def_floor=-0.023, rf_def_k67=-0.192, rf_def_total=-0.647, rank=3

## P37: 得点がリーグ5位以下のチーム・シーズンでは、床（k = 1〜2）の不足が、同じ幅の天井側（k = 6〜7）の不足より大きい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 31 件: d-2017, b-2019, e-2015, b-2016, l-2022 ほか
- もし: `（すべての単位）` ならば: `rf_def_floor_minus_k67 < 0`
- 識別子: `[where:rank_rf>=5] * => rf_def_floor_minus_k67<0`（指紋 `4077c7f9dc15c0e0`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 親: P20（変更: P36 と同じ変更（天井の帯を k = 6〜7 にして幅をそろえた））
- 見直す条件（反証）: 低得点のチーム・シーズンの半数以上で、k = 6〜7 の不足のほうが大きい
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 3 回、元の命題に異議あり 3 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 21 | 0.40 [0.28, 0.54] | 0.40 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 31 | 0 | 0.00 [0.00, 0.11] | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 31 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: rf_def_floor_minus_k67=0.196, rf_def_floor=0.038, rf_def_k67=-0.158, rank=5 / surprise=0.196
  - 中日 2017 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- オリックス 2019: rf_def_floor_minus_k67=0.169, rf_def_floor=-0.025, rf_def_k67=-0.194, rank=6 / surprise=0.169
  - オリックス 2019 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 楽天 2015: rf_def_floor_minus_k67=0.165, rf_def_floor=-0.081, rf_def_k67=-0.246, rank=6 / surprise=0.165
  - 楽天 2015 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- オリックス 2016: rf_def_floor_minus_k67=0.157, rf_def_floor=-0.053, rf_def_k67=-0.210, rank=6 / surprise=0.157
  - オリックス 2016 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 西武 2022: rf_def_floor_minus_k67=0.144, rf_def_floor=0.011, rf_def_k67=-0.133, rank=3 / surprise=0.144
  - 西武 2022 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- ロッテ 2018: rf_def_floor_minus_k67=0.106, rf_def_floor=-0.024, rf_def_k67=-0.130, rank=5 / surprise=0.106
  - ロッテ 2018 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 西武 2025: rf_def_floor_minus_k67=0.105, rf_def_floor=-0.041, rf_def_k67=-0.145, rank=5 / surprise=0.105
  - 西武 2025 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2013 **(focus)**: rf_def_floor_minus_k67=0.097, rf_def_floor=-0.036, rf_def_k67=-0.133, rank=4 / surprise=0.097
  - 中日 2013 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- 中日 2015 **(focus)**: rf_def_floor_minus_k67=0.095, rf_def_floor=-0.004, rf_def_k67=-0.099, rank=5 / surprise=0.095
  - 中日 2015 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- ロッテ 2017: rf_def_floor_minus_k67=0.091, rf_def_floor=-0.099, rf_def_k67=-0.190, rank=6 / surprise=0.091
  - ロッテ 2017 は「（すべての単位）」を満たすのに「rf_def_floor_minus_k67 < 0」を満たさない。なぜか？ → H2
- ほか 21 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rf_def_floor_minus_k67=0.168, rf_def_floor=-0.023, rf_def_k67=-0.192, rank=3

## P38: 四死球／打席が同じ年・同じリーグの他球団より少なければ、得点した回の大きさも他球団より小さい

- **判定: exit 2 異議あり（主張が強すぎる）** — 元の命題: 判例 29 件: c-2022, b-2025, m-2016, b-2023, g-2018 ほか
- もし: `bat_d_bb_pa < 0` ならば: `inn_dlog_size < 0`
- 識別子: `[seasons=2013-2025] bat_d_bb_pa<0 => inn_dlog_size<0`（指紋 `e65ac9488f39797c`）
- 兄弟（範囲と結論が同じ、条件が違う）: P39, P44, P48
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: 四死球が少ないチーム・シーズンの4分の1を超えて、得点した回の大きさが他球団以上
- 注記: R6 の自分への異議から（同じデータを見た後に作った）。P39 と並べて読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 3 回、元の命題に異議あり 3 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 73 | 44 | 0.60 [0.49, 0.71] | 0.44 | 1.38 | 0.000 | 0 | 修正 | 2 |
| 対偶 | 81 | 52 | 0.64 [0.53, 0.74] | 0.49 | 1.30 | 0.000 | 0 | 修正 | 2 |
| 逆 | 63 | 44 | 0.70 [0.58, 0.80] | 0.51 | 1.38 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 71 | 52 | 0.73 [0.62, 0.82] | 0.56 | 1.30 | 0.000 | 0 | 判断保留 | 4 |

**異議あり（主張が強すぎる）** 元の命題に判例 29 件（対偶の判例も同じ）

- 広島 2022: bat_d_bb_pa=-0.010, inn_dlog_size=0.103, bat_d_iso=-0.017, bat_d_obp=0.001, rank=5 / surprise=0.103
  - 広島 2022 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2025: bat_d_bb_pa=-0.002, inn_dlog_size=0.091, bat_d_iso=0.005, bat_d_obp=0.008, rank=3 / surprise=0.091
  - オリックス 2025 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2016: bat_d_bb_pa=-0.001, inn_dlog_size=0.073, bat_d_iso=-0.010, bat_d_obp=-0.005, rank=3 / surprise=0.073
  - ロッテ 2016 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2023: bat_d_bb_pa=-0.011, inn_dlog_size=0.062, bat_d_iso=0.007, bat_d_obp=0.002, rank=1 / surprise=0.062
  - オリックス 2023 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 巨人 2018: bat_d_bb_pa=-0.007, inn_dlog_size=0.057, bat_d_iso=0.007, bat_d_obp=-0.006, rank=3 / surprise=0.057
  - 巨人 2018 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2021: bat_d_bb_pa=-0.003, inn_dlog_size=0.053, bat_d_iso=0.014, bat_d_obp=0.006, rank=6 / surprise=0.053
  - DeNA 2021 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2023: bat_d_bb_pa=-0.005, inn_dlog_size=0.045, bat_d_iso=0.005, bat_d_obp=-0.001, rank=3 / surprise=0.045
  - DeNA 2023 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ソフトバンク 2021: bat_d_bb_pa=-0.009, inn_dlog_size=0.044, bat_d_iso=0.015, bat_d_obp=-0.001, rank=4 / surprise=0.044
  - ソフトバンク 2021 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2019: bat_d_bb_pa=-0.004, inn_dlog_size=0.043, bat_d_iso=0.015, bat_d_obp=-0.010, rank=2 / surprise=0.043
  - DeNA 2019 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ソフトバンク 2022: bat_d_bb_pa=-0.005, inn_dlog_size=0.040, bat_d_iso=0.004, bat_d_obp=0.013, rank=1 / surprise=0.040
  - ソフトバンク 2022 は「bat_d_bb_pa < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ほか 19 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 19 件（裏の判例も同じ）

- 楽天 2025: bat_d_bb_pa=0.007, inn_dlog_size=-0.102, bat_d_iso=-0.025, bat_d_obp=0.003, rank=4 / surprise=-0.102
  - 楽天 2025 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2022: bat_d_bb_pa=0.003, inn_dlog_size=-0.079, bat_d_iso=-0.005, bat_d_obp=0.009, rank=1 / surprise=-0.079
  - オリックス 2022 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- 中日 2013 **(focus)**: bat_d_bb_pa=0.001, inn_dlog_size=-0.072, bat_d_iso=-0.008, bat_d_obp=-0.009, rank=4 / surprise=-0.072
  - 中日 2013 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- 西武 2016: bat_d_bb_pa=0.002, inn_dlog_size=-0.069, bat_d_iso=0.019, bat_d_obp=0.005, rank=4 / surprise=-0.069
  - 西武 2016 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- ヤクルト 2024: bat_d_bb_pa=0.013, inn_dlog_size=-0.057, bat_d_iso=0.012, bat_d_obp=0.008, rank=5 / surprise=-0.057
  - ヤクルト 2024 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2018: bat_d_bb_pa=0.010, inn_dlog_size=-0.056, bat_d_iso=-0.042, bat_d_obp=-0.000, rank=5 / surprise=-0.056
  - ロッテ 2018 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2023: bat_d_bb_pa=0.006, inn_dlog_size=-0.054, bat_d_iso=0.002, bat_d_obp=0.003, rank=2 / surprise=-0.054
  - ロッテ 2023 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2017: bat_d_bb_pa=0.003, inn_dlog_size=-0.052, bat_d_iso=-0.025, bat_d_obp=-0.008, rank=5 / surprise=-0.052
  - 日本ハム 2017 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- ヤクルト 2025: bat_d_bb_pa=0.003, inn_dlog_size=-0.041, bat_d_iso=-0.002, bat_d_obp=-0.006, rank=6 / surprise=-0.041
  - ヤクルト 2025 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- 阪神 2015: bat_d_bb_pa=0.009, inn_dlog_size=-0.036, bat_d_iso=-0.016, bat_d_obp=0.004, rank=3 / surprise=-0.036
  - 阪神 2015 は「inn_dlog_size < 0」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5, H6
- ほか 9 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 広島 2020: bat_d_bb_pa=-0.001, inn_dlog_size=0.086, bat_d_iso=0.004, bat_d_obp=0.009, rank=5

## P39: ISO が同じ年・同じリーグの他球団より低ければ、得点した回の大きさも他球団より小さい

- **判定: exit 2 異議あり（主張が強すぎる）** — 元の命題: 判例 33 件: c-2022, m-2016, t-2023, e-2022, e-2014 ほか
- もし: `bat_d_iso < 0` ならば: `inn_dlog_size < 0`
- 識別子: `[seasons=2013-2025] bat_d_iso<0 => inn_dlog_size<0`（指紋 `8df99c64432529af`）
- 兄弟（範囲と結論が同じ、条件が違う）: P38, P44, P48
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: ISO が低いチーム・シーズンの4分の1を超えて、得点した回の大きさが他球団以上
- 注記: R6 の自分への異議から（同じデータを見た後に作った）。P38 と並べて読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 3 回、元の命題に異議あり 3 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 43 | 0.57 [0.45, 0.67] | 0.44 | 1.29 | 0.001 | 0 | 修正 | 2 |
| 対偶 | 81 | 48 | 0.59 [0.48, 0.69] | 0.47 | 1.25 | 0.001 | 0 | 修正 | 2 |
| 逆 | 63 | 43 | 0.68 [0.56, 0.78] | 0.53 | 1.29 | 0.001 | 0 | 判断保留 | 4 |
| 裏 | 68 | 48 | 0.71 [0.59, 0.80] | 0.56 | 1.25 | 0.001 | 0 | 判断保留 | 4 |

**異議あり（主張が強すぎる）** 元の命題に判例 33 件（対偶の判例も同じ）

- 広島 2022: bat_d_iso=-0.017, inn_dlog_size=0.103, bat_d_bb_pa=-0.010, bat_d_obp=0.001, rank=5 / surprise=0.103
  - 広島 2022 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- ロッテ 2016: bat_d_iso=-0.010, inn_dlog_size=0.073, bat_d_bb_pa=-0.001, bat_d_obp=-0.005, rank=3 / surprise=0.073
  - ロッテ 2016 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- 阪神 2023: bat_d_iso=-0.016, inn_dlog_size=0.071, bat_d_bb_pa=0.023, bat_d_obp=0.020, rank=1 / surprise=0.071
  - 阪神 2023 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- 楽天 2022: bat_d_iso=-0.005, inn_dlog_size=0.063, bat_d_bb_pa=0.021, bat_d_obp=0.019, rank=4 / surprise=0.063
  - 楽天 2022 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- 楽天 2014: bat_d_iso=-0.024, inn_dlog_size=0.049, bat_d_bb_pa=0.003, bat_d_obp=-0.001, rank=6 / surprise=0.049
  - 楽天 2014 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- ソフトバンク 2023: bat_d_iso=-0.001, inn_dlog_size=0.048, bat_d_bb_pa=0.007, bat_d_obp=0.012, rank=3 / surprise=0.048
  - ソフトバンク 2023 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- 阪神 2024: bat_d_iso=-0.013, inn_dlog_size=0.044, bat_d_bb_pa=0.018, bat_d_obp=0.011, rank=2 / surprise=0.044
  - 阪神 2024 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- 楽天 2013: bat_d_iso=-0.003, inn_dlog_size=0.043, bat_d_bb_pa=0.004, bat_d_obp=0.008, rank=1 / surprise=0.043
  - 楽天 2013 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- 阪神 2014: bat_d_iso=-0.019, inn_dlog_size=0.039, bat_d_bb_pa=0.009, bat_d_obp=0.007, rank=2 / surprise=0.039
  - 阪神 2014 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- ヤクルト 2018: bat_d_iso=-0.004, inn_dlog_size=0.036, bat_d_bb_pa=0.015, bat_d_obp=0.020, rank=2 / surprise=0.036
  - ヤクルト 2018 は「bat_d_iso < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H6
- ほか 23 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 20 件（裏の判例も同じ）

- ソフトバンク 2019: bat_d_iso=0.023, inn_dlog_size=-0.103, bat_d_bb_pa=-0.021, bat_d_obp=-0.016, rank=2 / surprise=-0.103
  - ソフトバンク 2019 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2018: bat_d_iso=0.029, inn_dlog_size=-0.072, bat_d_bb_pa=-0.023, bat_d_obp=-0.028, rank=4 / surprise=-0.072
  - DeNA 2018 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 西武 2016: bat_d_iso=0.019, inn_dlog_size=-0.069, bat_d_bb_pa=0.002, bat_d_obp=0.005, rank=4 / surprise=-0.069
  - 西武 2016 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2022: bat_d_iso=0.006, inn_dlog_size=-0.067, bat_d_bb_pa=-0.003, bat_d_obp=0.001, rank=2 / surprise=-0.067
  - DeNA 2022 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ヤクルト 2024: bat_d_iso=0.012, inn_dlog_size=-0.057, bat_d_bb_pa=0.013, bat_d_obp=0.008, rank=5 / surprise=-0.057
  - ヤクルト 2024 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ロッテ 2023: bat_d_iso=0.002, inn_dlog_size=-0.054, bat_d_bb_pa=0.006, bat_d_obp=0.003, rank=2 / surprise=-0.054
  - ロッテ 2023 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 巨人 2016: bat_d_iso=0.009, inn_dlog_size=-0.050, bat_d_bb_pa=-0.012, bat_d_obp=-0.011, rank=2 / surprise=-0.050
  - 巨人 2016 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 西武 2022: bat_d_iso=0.012, inn_dlog_size=-0.045, bat_d_bb_pa=-0.003, bat_d_obp=-0.014, rank=3 / surprise=-0.045
  - 西武 2022 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 西武 2014: bat_d_iso=0.016, inn_dlog_size=-0.030, bat_d_bb_pa=0.013, bat_d_obp=0.001, rank=5 / surprise=-0.030
  - 西武 2014 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ヤクルト 2013: bat_d_iso=0.003, inn_dlog_size=-0.021, bat_d_bb_pa=0.007, bat_d_obp=0.004, rank=6 / surprise=-0.021
  - ヤクルト 2013 は「inn_dlog_size < 0」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- ほか 10 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 日本ハム 2020: bat_d_iso=-0.020, inn_dlog_size=0.026, bat_d_bb_pa=0.003, bat_d_obp=0.006, rank=5
- 阪神 2020: bat_d_iso=-0.001, inn_dlog_size=0.023, bat_d_bb_pa=0.006, bat_d_obp=-0.003, rank=2
- ヤクルト 2020: bat_d_iso=-0.004, inn_dlog_size=0.009, bat_d_bb_pa=0.013, bat_d_obp=-0.003, rank=6

## P40: 得点がリーグ5位以下だったシーズンの中日は、出塁のうち四死球による割合が他球団より低い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: d-2014, d-2013
- もし: `（すべての単位）` ならば: `bat_d_walk_share < 0`
- 識別子: `[team=d, where:rank_rf>=5] * => bat_d_walk_share<0`（指紋 `1e71d224f7df384e`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、四死球による出塁の割合が他球団以上
- 注記: R6 の数字から向きはある程度予想できる。他の低得点のチームとの差は summary で並べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 9 | 0.82 [0.52, 0.95] | 0.82 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 2 | 0 | 0.00 [0.00, 0.66] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- 中日 2014 **(focus)**: bat_d_walk_share=0.012, bat_d_avg=-0.007, bat_d_bb_pa=0.002, bat_d_obp=-0.005, rank=4 / surprise=0.012
  - 中日 2014 は「（すべての単位）」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- 中日 2013 **(focus)**: bat_d_walk_share=0.011, bat_d_avg=-0.011, bat_d_bb_pa=0.001, bat_d_obp=-0.009, rank=4 / surprise=0.011
  - 中日 2013 は「（すべての単位）」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5

## P41: 得点がリーグ5位以下のチームの間では、出塁のうち四死球による割合が他球団より低ければ B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 5 件: t-2019, t-2022, c-2023, h-2012, t-2021
- もし: `bat_d_walk_share < 0` ならば: `upper_half == False`
- 識別子: `[where:rank_rf>=5] bat_d_walk_share<0 => upper_half==false`（指紋 `7e039ef8076017d3`）
- 兄弟（範囲と結論が同じ、条件が違う）: P21, P42, P43, P49
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。低得点のチームの中では、出塁の中身は順位を分けない
- 注記: 中日だけの命題では作れない逆・裏を、低得点のチームどうしの比較で作る。成立率より lift と p を読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 32 | 27 | 0.84 [0.68, 0.93] | 0.85 | 1.00 | 0.668 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 3 | 0.38 [0.14, 0.69] | 0.38 | 0.97 | 0.668 | 0 | 判断保留 | 4 |
| 逆 | 44 | 27 | 0.61 [0.47, 0.74] | 0.62 | 1.00 | 0.668 | 0 | 棄却 | 3 |
| 裏 | 20 | 3 | 0.15 [0.05, 0.36] | 0.15 | 0.97 | 0.668 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 5 件（対偶の判例も同じ）

- 阪神 2019: bat_d_walk_share=-0.009, upper_half=True, bat_d_avg=-0.002, rank_ra=2, rd=-28 / surprise=-2
  - 阪神 2019 は「bat_d_walk_share < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 阪神 2022: bat_d_walk_share=-0.003, upper_half=True, bat_d_avg=-0.006, rank_ra=1, rd=61 / surprise=2
  - 阪神 2022 は「bat_d_walk_share < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 広島 2023: bat_d_walk_share=-0.019, upper_half=True, bat_d_avg=0.002, rank_ra=5, rd=-15 / surprise=-2
  - 広島 2023 は「bat_d_walk_share < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- ソフトバンク 2012: bat_d_walk_share=-0.032, upper_half=True, bat_d_avg=0.001, rank_ra=1, rd=23 / surprise=1
  - ソフトバンク 2012 は「bat_d_walk_share < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 阪神 2021: bat_d_walk_share=-0.001, upper_half=True, bat_d_avg=-0.004, rank_ra=2, rd=33 / surprise=0
  - 阪神 2021 は「bat_d_walk_share < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5

**異議あり（不成立）** 逆に判例 17 件（裏の判例も同じ）

- 阪神 2018: bat_d_walk_share=0.028, upper_half=False, bat_d_avg=-0.008, rank_ra=2, rd=-51 / surprise=2
  - 阪神 2018 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- 中日 2013 **(focus)**: bat_d_walk_share=0.011, upper_half=False, bat_d_avg=-0.011, rank_ra=4, rd=-73 / surprise=-1
  - 中日 2013 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- 楽天 2014: bat_d_walk_share=0.009, upper_half=False, bat_d_avg=-0.003, rank_ra=5, rd=-55 / surprise=1
  - 楽天 2014 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- ロッテ 2018: bat_d_walk_share=0.033, upper_half=False, bat_d_avg=-0.008, rank_ra=5, rd=-94 / surprise=-1
  - ロッテ 2018 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- 日本ハム 2021: bat_d_walk_share=0.010, upper_half=False, bat_d_avg=-0.012, rank_ra=4, rd=-61 / surprise=-1
  - 日本ハム 2021 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- オリックス 2012: bat_d_walk_share=0.010, upper_half=False, bat_d_avg=-0.013, rank_ra=6, rd=-82 / surprise=0
  - オリックス 2012 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- DeNA 2012: bat_d_walk_share=0.001, upper_half=False, bat_d_avg=-0.013, rank_ra=6, rd=-149 / surprise=0
  - DeNA 2012 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- 阪神 2012: bat_d_walk_share=0.002, upper_half=False, bat_d_avg=-0.009, rank_ra=3, rd=-27 / surprise=0
  - 阪神 2012 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- 日本ハム 2013: bat_d_walk_share=0.005, upper_half=False, bat_d_avg=-0.007, rank_ra=6, rd=-70 / surprise=0
  - 日本ハム 2013 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- 中日 2014 **(focus)**: bat_d_walk_share=0.012, upper_half=False, bat_d_avg=-0.007, rank_ra=2, rd=-20 / surprise=0
  - 中日 2014 は「upper_half == False」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5
- ほか 7 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: bat_d_walk_share=-0.019, upper_half=True, bat_d_avg=-0.002, rank_ra=4, rd=-60

## P42: 得点がリーグ5位以下のチームの間では、ISO が他球団より低ければ B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: t-2015, t-2019, t-2022, c-2023, t-2013 ほか
- もし: `bat_d_iso < 0` ならば: `upper_half == False`
- 識別子: `[where:rank_rf>=5] bat_d_iso<0 => upper_half==false`（指紋 `d3ac24ce4131bf22`）
- 兄弟（範囲と結論が同じ、条件が違う）: P21, P41, P43, P49
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。低得点のチームの中では、長打の不足は順位を分けない
- 注記: P41・P43 と兄弟（範囲と結論が同じ）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 45 | 39 | 0.87 [0.74, 0.94] | 0.85 | 1.02 | 0.291 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 2 | 0.25 [0.07, 0.59] | 0.13 | 1.86 | 0.291 | 0 | 判断保留 | 4 |
| 逆 | 44 | 39 | 0.89 [0.76, 0.95] | 0.87 | 1.02 | 0.291 | 0 | 支持 | 1 |
| 裏 | 7 | 2 | 0.29 [0.08, 0.64] | 0.15 | 1.86 | 0.291 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- 阪神 2015: bat_d_iso=-0.016, upper_half=True, bat_d_obp=0.004, rank_ra=5, rd=-85 / surprise=-3
  - 阪神 2015 は「bat_d_iso < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H6
- 阪神 2019: bat_d_iso=-0.034, upper_half=True, bat_d_obp=-0.005, rank_ra=2, rd=-28 / surprise=-2
  - 阪神 2019 は「bat_d_iso < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H6
- 阪神 2022: bat_d_iso=-0.034, upper_half=True, bat_d_obp=-0.008, rank_ra=1, rd=61 / surprise=2
  - 阪神 2022 は「bat_d_iso < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H6
- 広島 2023: bat_d_iso=-0.009, upper_half=True, bat_d_obp=-0.002, rank_ra=5, rd=-15 / surprise=-2
  - 広島 2023 は「bat_d_iso < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H6
- 阪神 2013: bat_d_iso=-0.022, upper_half=True, bat_d_obp=0.004, rank_ra=1, rd=43 / surprise=0
  - 阪神 2013 は「bat_d_iso < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H6
- 阪神 2021: bat_d_iso=-0.001, upper_half=True, bat_d_obp=-0.005, rank_ra=2, rd=33 / surprise=0
  - 阪神 2021 は「bat_d_iso < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H6

**異議あり（例外あり）** 逆に判例 5 件（裏の判例も同じ）

- ロッテ 2014: bat_d_iso=0.006, upper_half=False, bat_d_obp=-0.017, rank_ra=6, rd=-86 / surprise=-2
  - ロッテ 2014 は「upper_half == False」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2018: bat_d_iso=0.029, upper_half=False, bat_d_obp=-0.028, rank_ra=3, rd=-70 / surprise=-2
  - DeNA 2018 は「upper_half == False」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- DeNA 2014: bat_d_iso=0.003, upper_half=False, bat_d_obp=-0.014, rank_ra=5, rd=-56 / surprise=-1
  - DeNA 2014 は「upper_half == False」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- オリックス 2012: bat_d_iso=0.001, upper_half=False, bat_d_obp=-0.012, rank_ra=6, rd=-82 / surprise=0
  - オリックス 2012 は「upper_half == False」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6
- 日本ハム 2022: bat_d_iso=0.004, upper_half=False, bat_d_obp=-0.021, rank_ra=5, rd=-71 / surprise=0
  - 日本ハム 2022 は「upper_half == False」を満たすのに「bat_d_iso < 0」を満たさない。なぜか？ → H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: bat_d_iso=-0.035, upper_half=True, bat_d_obp=-0.008, rank_ra=4, rd=-60
- ロッテ 2020: bat_d_iso=-0.013, upper_half=True, bat_d_obp=0.004, rank_ra=2, rd=-18

## P43: 得点がリーグ5位以下のチームの間では、四死球／打席が他球団より少なければ B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: t-2019, t-2022, c-2023, h-2012, t-2021 ほか
- もし: `bat_d_bb_pa < 0` ならば: `upper_half == False`
- 識別子: `[where:rank_rf>=5] bat_d_bb_pa<0 => upper_half==false`（指紋 `333ed1013e91c299`）
- 兄弟（範囲と結論が同じ、条件が違う）: P21, P41, P42, P49
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。低得点のチームの中では、四死球の少なさは順位を分けない
- 注記: P41・P42 と兄弟
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 40 | 34 | 0.85 [0.71, 0.93] | 0.85 | 1.00 | 0.601 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 2 | 0.25 [0.07, 0.59] | 0.23 | 1.08 | 0.601 | 0 | 判断保留 | 4 |
| 逆 | 44 | 34 | 0.77 [0.63, 0.87] | 0.77 | 1.00 | 0.601 | 0 | 判断保留 | 4 |
| 裏 | 12 | 2 | 0.17 [0.05, 0.45] | 0.15 | 1.08 | 0.601 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- 阪神 2019: bat_d_bb_pa=-0.005, upper_half=True, bat_d_iso=-0.034, rank_ra=2, rd=-28 / surprise=-2
  - 阪神 2019 は「bat_d_bb_pa < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 阪神 2022: bat_d_bb_pa=-0.003, upper_half=True, bat_d_iso=-0.034, rank_ra=1, rd=61 / surprise=2
  - 阪神 2022 は「bat_d_bb_pa < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 広島 2023: bat_d_bb_pa=-0.006, upper_half=True, bat_d_iso=-0.009, rank_ra=5, rd=-15 / surprise=-2
  - 広島 2023 は「bat_d_bb_pa < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- ソフトバンク 2012: bat_d_bb_pa=-0.011, upper_half=True, bat_d_iso=0.002, rank_ra=1, rd=23 / surprise=1
  - ソフトバンク 2012 は「bat_d_bb_pa < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 阪神 2021: bat_d_bb_pa=-0.002, upper_half=True, bat_d_iso=-0.001, rank_ra=2, rd=33 / surprise=0
  - 阪神 2021 は「bat_d_bb_pa < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 西武 2022: bat_d_bb_pa=-0.003, upper_half=True, bat_d_iso=0.012, rank_ra=1, rd=16 / surprise=0
  - 西武 2022 は「bat_d_bb_pa < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5

**待った！判断保留** 逆に判例 10 件（裏の判例も同じ）

- 阪神 2018: bat_d_bb_pa=0.008, upper_half=False, bat_d_iso=-0.037, rank_ra=2, rd=-51 / surprise=2
  - 阪神 2018 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- 中日 2013 **(focus)**: bat_d_bb_pa=0.001, upper_half=False, bat_d_iso=-0.008, rank_ra=4, rd=-73 / surprise=-1
  - 中日 2013 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- 楽天 2014: bat_d_bb_pa=0.003, upper_half=False, bat_d_iso=-0.024, rank_ra=5, rd=-55 / surprise=1
  - 楽天 2014 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- ロッテ 2018: bat_d_bb_pa=0.010, upper_half=False, bat_d_iso=-0.042, rank_ra=5, rd=-94 / surprise=-1
  - ロッテ 2018 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- オリックス 2012: bat_d_bb_pa=0.000, upper_half=False, bat_d_iso=0.001, rank_ra=6, rd=-82 / surprise=0
  - オリックス 2012 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- 中日 2014 **(focus)**: bat_d_bb_pa=0.002, upper_half=False, bat_d_iso=-0.025, rank_ra=2, rd=-20 / surprise=0
  - 中日 2014 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- オリックス 2015: bat_d_bb_pa=0.000, upper_half=False, bat_d_iso=-0.017, rank_ra=2, rd=-29 / surprise=0
  - オリックス 2015 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- 阪神 2016: bat_d_bb_pa=0.001, upper_half=False, bat_d_iso=-0.023, rank_ra=3, rd=-40 / surprise=0
  - 阪神 2016 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- 日本ハム 2017: bat_d_bb_pa=0.003, upper_half=False, bat_d_iso=-0.025, rank_ra=4, rd=-87 / surprise=0
  - 日本ハム 2017 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5
- ヤクルト 2017: bat_d_bb_pa=0.004, upper_half=False, bat_d_iso=-0.028, rank_ra=6, rd=-180 / surprise=0
  - ヤクルト 2017 は「upper_half == False」を満たすのに「bat_d_bb_pa < 0」を満たさない。なぜか？ → H5

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: bat_d_bb_pa=-0.009, upper_half=True, bat_d_iso=-0.035, rank_ra=4, rd=-60

## P44: 出塁のうち四死球による割合が同じ年・同じリーグの他球団より低ければ、得点した回の大きさも他球団より小さい

- **判定: exit 2 異議あり（主張が強すぎる）** — 元の命題: 判例 31 件: c-2022, l-2017, b-2025, s-2015, b-2023 ほか
- もし: `bat_d_walk_share < 0` ならば: `inn_dlog_size < 0`
- 識別子: `[seasons=2013-2025] bat_d_walk_share<0 => inn_dlog_size<0`（指紋 `f7668e4a836b5f8c`）
- 兄弟（範囲と結論が同じ、条件が違う）: P38, P39, P48
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: 四死球による出塁の割合が低いチーム・シーズンの4分の1を超えて、得点した回の大きさが他球団以上
- 注記: P38（四死球／打席）・P39（ISO）と兄弟。P38 より明らかに弱ければ、効くのは割合ではなく数
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 71 | 40 | 0.56 [0.45, 0.67] | 0.44 | 1.29 | 0.002 | 0 | 修正 | 2 |
| 対偶 | 81 | 50 | 0.62 [0.51, 0.72] | 0.51 | 1.22 | 0.002 | 0 | 修正 | 2 |
| 逆 | 63 | 40 | 0.63 [0.51, 0.74] | 0.49 | 1.29 | 0.002 | 0 | 修正 | 2 |
| 裏 | 73 | 50 | 0.68 [0.57, 0.78] | 0.56 | 1.22 | 0.002 | 0 | 判断保留 | 4 |

**異議あり（主張が強すぎる）** 元の命題に判例 31 件（対偶の判例も同じ）

- 広島 2022: bat_d_walk_share=-0.034, inn_dlog_size=0.103, bat_d_bb_pa=-0.010, bat_d_avg=0.010, rank=5 / surprise=0.103
  - 広島 2022 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 西武 2017: bat_d_walk_share=-0.005, inn_dlog_size=0.096, bat_d_bb_pa=0.004, bat_d_avg=0.016, rank=2 / surprise=0.096
  - 西武 2017 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2025: bat_d_walk_share=-0.013, inn_dlog_size=0.091, bat_d_bb_pa=-0.002, bat_d_avg=0.010, rank=3 / surprise=0.091
  - オリックス 2025 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ヤクルト 2015: bat_d_walk_share=-0.006, inn_dlog_size=0.069, bat_d_bb_pa=0.001, bat_d_avg=0.010, rank=1 / surprise=0.069
  - ヤクルト 2015 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2023: bat_d_walk_share=-0.037, inn_dlog_size=0.062, bat_d_bb_pa=-0.011, bat_d_avg=0.011, rank=1 / surprise=0.062
  - オリックス 2023 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 巨人 2018: bat_d_walk_share=-0.015, inn_dlog_size=0.057, bat_d_bb_pa=-0.007, bat_d_avg=-0.002, rank=3 / surprise=0.057
  - 巨人 2018 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2021: bat_d_walk_share=-0.013, inn_dlog_size=0.053, bat_d_bb_pa=-0.003, bat_d_avg=0.009, rank=6 / surprise=0.053
  - DeNA 2021 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2023: bat_d_walk_share=-0.014, inn_dlog_size=0.045, bat_d_bb_pa=-0.005, bat_d_avg=0.003, rank=3 / surprise=0.045
  - DeNA 2023 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ソフトバンク 2021: bat_d_walk_share=-0.028, inn_dlog_size=0.044, bat_d_bb_pa=-0.009, bat_d_avg=0.007, rank=4 / surprise=0.044
  - ソフトバンク 2021 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2019: bat_d_walk_share=-0.004, inn_dlog_size=0.043, bat_d_bb_pa=-0.004, bat_d_avg=-0.007, rank=2 / surprise=0.043
  - DeNA 2019 は「bat_d_walk_share < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ほか 21 件（propositions.jsonl を参照）

**異議あり（主張が強すぎる）** 逆に判例 23 件（裏の判例も同じ）

- 楽天 2015: bat_d_walk_share=0.010, inn_dlog_size=-0.156, bat_d_bb_pa=-0.002, bat_d_avg=-0.018, rank=6 / surprise=-0.156
  - 楽天 2015 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2025: bat_d_walk_share=0.021, inn_dlog_size=-0.102, bat_d_bb_pa=0.007, bat_d_avg=-0.002, rank=4 / surprise=-0.102
  - 楽天 2025 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2022: bat_d_walk_share=0.001, inn_dlog_size=-0.079, bat_d_bb_pa=0.003, bat_d_avg=0.008, rank=1 / surprise=-0.079
  - オリックス 2022 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- 中日 2013 **(focus)**: bat_d_walk_share=0.011, inn_dlog_size=-0.072, bat_d_bb_pa=0.001, bat_d_avg=-0.011, rank=4 / surprise=-0.072
  - 中日 2013 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2021: bat_d_walk_share=0.010, inn_dlog_size=-0.067, bat_d_bb_pa=-0.000, bat_d_avg=-0.012, rank=5 / surprise=-0.067
  - 日本ハム 2021 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- ヤクルト 2024: bat_d_walk_share=0.038, inn_dlog_size=-0.057, bat_d_bb_pa=0.013, bat_d_avg=-0.002, rank=5 / surprise=-0.057
  - ヤクルト 2024 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2018: bat_d_walk_share=0.033, inn_dlog_size=-0.056, bat_d_bb_pa=0.010, bat_d_avg=-0.008, rank=5 / surprise=-0.056
  - ロッテ 2018 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2023: bat_d_walk_share=0.017, inn_dlog_size=-0.054, bat_d_bb_pa=0.006, bat_d_avg=-0.002, rank=2 / surprise=-0.054
  - ロッテ 2023 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2017: bat_d_walk_share=0.014, inn_dlog_size=-0.052, bat_d_bb_pa=0.003, bat_d_avg=-0.010, rank=5 / surprise=-0.052
  - 日本ハム 2017 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- 西武 2022: bat_d_walk_share=0.003, inn_dlog_size=-0.045, bat_d_bb_pa=-0.003, bat_d_avg=-0.013, rank=3 / surprise=-0.045
  - 西武 2022 は「inn_dlog_size < 0」を満たすのに「bat_d_walk_share < 0」を満たさない。なぜか？ → H5, H6
- ほか 13 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 広島 2020: bat_d_walk_share=-0.010, inn_dlog_size=0.086, bat_d_bb_pa=-0.001, bat_d_avg=0.010, rank=5

## P45: 得点がリーグ5位以下だったシーズンの中日は、四球のうち故意四球の割合が他球団より低い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: d-2019, d-2025, d-2021, d-2015
- もし: `（すべての単位）` ならば: `bat_d_ibb_bb < 0`
- 識別子: `[team=d, where:rank_rf>=5] * => bat_d_ibb_bb<0`（指紋 `c3c1f67b77a85cfd`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、故意四球の割合が他球団以上
- 注記: 勝負を避けられない（打者が怖がられていない）という読みの確かめ。成り立たなければこの読みは使わない
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 7 | 0.64 [0.35, 0.85] | 0.64 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 中日 2019 **(focus)**: bat_d_ibb_bb=0.034, bat_d_iso=-0.025, bat_d_bb_pa=-0.025, rank=5 / surprise=0.034
  - 中日 2019 は「（すべての単位）」を満たすのに「bat_d_ibb_bb < 0」を満たさない。なぜか？ → H6
- 中日 2025 **(focus)**: bat_d_ibb_bb=0.030, bat_d_iso=-0.005, bat_d_bb_pa=-0.008, rank=4 / surprise=0.030
  - 中日 2025 は「（すべての単位）」を満たすのに「bat_d_ibb_bb < 0」を満たさない。なぜか？ → H6
- 中日 2021 **(focus)**: bat_d_ibb_bb=0.029, bat_d_iso=-0.046, bat_d_bb_pa=-0.019, rank=5 / surprise=0.029
  - 中日 2021 は「（すべての単位）」を満たすのに「bat_d_ibb_bb < 0」を満たさない。なぜか？ → H6
- 中日 2015 **(focus)**: bat_d_ibb_bb=0.007, bat_d_iso=-0.024, bat_d_bb_pa=-0.006, rank=5 / surprise=0.007
  - 中日 2015 は「（すべての単位）」を満たすのに「bat_d_ibb_bb < 0」を満たさない。なぜか？ → H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: bat_d_ibb_bb=0.005, bat_d_iso=-0.035, bat_d_bb_pa=-0.009, rank=3

## P46: 得点がリーグ5位以下だったシーズンの中日は、走者1人あたりの得点が他球団より少ない

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `（すべての単位）` ならば: `bat_d_r_runner < 0`
- 識別子: `[team=d, where:rank_rf>=5] * => bat_d_r_runner<0`（指紋 `d2a5ec9973ae3359`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、走者1人あたりの得点が他球団以上
- 注記: 成り立たなければ「そもそも走者が少ない」側に戻る。本塁打が多いと機械的に高くなる指標
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## P47: 得点がリーグ5位以下のチーム・シーズン（中日を除く）では、走者1人あたりの得点が他球団より少ない

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 5 件: t-2021, m-2014, db-2018, c-2023, f-2022
- もし: `（すべての単位）` ならば: `bat_d_r_runner < 0`
- 識別子: `[where:rank_rf>=5, where:team!="d"] * => bat_d_r_runner<0`（指紋 `603eea1d2eb73341`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 41
- 見直す条件（反証）: 中日以外の低得点のチーム・シーズンの半数以上で、走者1人あたりの得点が他球団以上
- 注記: P46 と成立率を並べ、中日固有かを見る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 41 | 36 | 0.88 [0.74, 0.95] | 0.88 | 1.00 | 1.000 | 0 | 支持 | 1 |
| 対偶 | 5 | 0 | 0.00 [0.00, 0.43] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（例外あり）** 元の命題に判例 5 件（対偶の判例も同じ）

- 阪神 2021: bat_d_r_runner=0.009, bat_d_r_ab=0.001, bat_d_obp=-0.005, bat_d_iso=-0.001 / surprise=0.009
  - 阪神 2021 は「（すべての単位）」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2014: bat_d_r_runner=0.005, bat_d_r_ab=-0.007, bat_d_obp=-0.017, bat_d_iso=0.006 / surprise=0.005
  - ロッテ 2014 は「（すべての単位）」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2018: bat_d_r_runner=0.005, bat_d_r_ab=-0.013, bat_d_obp=-0.028, bat_d_iso=0.029 / surprise=0.005
  - DeNA 2018 は「（すべての単位）」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- 広島 2023: bat_d_r_runner=0.003, bat_d_r_ab=-0.001, bat_d_obp=-0.002, bat_d_iso=-0.009 / surprise=0.003
  - 広島 2023 は「（すべての単位）」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2022: bat_d_r_runner=0.002, bat_d_r_ab=-0.009, bat_d_obp=-0.021, bat_d_iso=0.004 / surprise=0.002
  - 日本ハム 2022 は「（すべての単位）」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6

## P48: 走者1人あたりの得点が同じ年・同じリーグの他球団より少なければ、得点した回の大きさも他球団より小さい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 23 件: g-2024, e-2022, e-2014, t-2014, s-2018 ほか
- もし: `bat_d_r_runner < 0` ならば: `inn_dlog_size < 0`
- 識別子: `[seasons=2013-2025] bat_d_r_runner<0 => inn_dlog_size<0`（指紋 `43ed4cd37db8b0fc`）
- 兄弟（範囲と結論が同じ、条件が違う）: P38, P39, P44
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: 走者1人あたりの得点が少ないチーム・シーズンの4分の1を超えて、得点した回の大きさが他球団以上
- 注記: P38・P39・P44 と兄弟。それらより明らかに強ければ、まとめて「走者を返す効率」として見るほうがよい
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 71 | 48 | 0.68 [0.56, 0.77] | 0.44 | 1.55 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 81 | 58 | 0.72 [0.61, 0.80] | 0.51 | 1.41 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 63 | 48 | 0.76 [0.64, 0.85] | 0.49 | 1.55 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 73 | 58 | 0.79 [0.69, 0.87] | 0.56 | 1.41 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 23 件（対偶の判例も同じ）

- 巨人 2024: bat_d_r_runner=-0.005, inn_dlog_size=0.115, bat_d_iso=0.008, bat_d_bb_pa=0.005 / surprise=0.115
  - 巨人 2024 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2022: bat_d_r_runner=-0.006, inn_dlog_size=0.063, bat_d_iso=-0.005, bat_d_bb_pa=0.021 / surprise=0.063
  - 楽天 2022 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2014: bat_d_r_runner=-0.018, inn_dlog_size=0.049, bat_d_iso=-0.024, bat_d_bb_pa=0.003 / surprise=0.049
  - 楽天 2014 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 阪神 2014: bat_d_r_runner=-0.011, inn_dlog_size=0.039, bat_d_iso=-0.019, bat_d_bb_pa=0.009 / surprise=0.039
  - 阪神 2014 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ヤクルト 2018: bat_d_r_runner=-0.003, inn_dlog_size=0.036, bat_d_iso=-0.004, bat_d_bb_pa=0.015 / surprise=0.036
  - ヤクルト 2018 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2016: bat_d_r_runner=-0.016, inn_dlog_size=0.034, bat_d_iso=-0.005, bat_d_bb_pa=-0.007 / surprise=0.034
  - 楽天 2016 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 巨人 2025: bat_d_r_runner=-0.013, inn_dlog_size=0.034, bat_d_iso=0.003, bat_d_bb_pa=0.006 / surprise=0.034
  - 巨人 2025 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 広島 2025: bat_d_r_runner=-0.009, inn_dlog_size=0.031, bat_d_iso=-0.013, bat_d_bb_pa=-0.011 / surprise=0.031
  - 広島 2025 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 阪神 2022: bat_d_r_runner=-0.011, inn_dlog_size=0.031, bat_d_iso=-0.034, bat_d_bb_pa=-0.003 / surprise=0.031
  - 阪神 2022 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2019: bat_d_r_runner=-0.035, inn_dlog_size=0.031, bat_d_iso=-0.031, bat_d_bb_pa=-0.000 / surprise=0.031
  - 日本ハム 2019 は「bat_d_r_runner < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H5, H6
- ほか 13 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 15 件（裏の判例も同じ）

- ソフトバンク 2019: bat_d_r_runner=0.005, inn_dlog_size=-0.103, bat_d_iso=0.023, bat_d_bb_pa=-0.021 / surprise=-0.103
  - ソフトバンク 2019 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2018: bat_d_r_runner=0.005, inn_dlog_size=-0.072, bat_d_iso=0.029, bat_d_bb_pa=-0.023 / surprise=-0.072
  - DeNA 2018 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- 西武 2016: bat_d_r_runner=0.012, inn_dlog_size=-0.069, bat_d_iso=0.019, bat_d_bb_pa=0.002 / surprise=-0.069
  - 西武 2016 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- ヤクルト 2024: bat_d_r_runner=0.027, inn_dlog_size=-0.057, bat_d_iso=0.012, bat_d_bb_pa=0.013 / surprise=-0.057
  - ヤクルト 2024 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2023: bat_d_r_runner=0.002, inn_dlog_size=-0.054, bat_d_iso=0.002, bat_d_bb_pa=0.006 / surprise=-0.054
  - ロッテ 2023 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- ヤクルト 2014: bat_d_r_runner=0.016, inn_dlog_size=-0.020, bat_d_iso=0.007, bat_d_bb_pa=-0.005 / surprise=-0.020
  - ヤクルト 2014 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- 巨人 2023: bat_d_r_runner=0.011, inn_dlog_size=-0.019, bat_d_iso=0.039, bat_d_bb_pa=-0.007 / surprise=-0.019
  - 巨人 2023 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- 広島 2023: bat_d_r_runner=0.003, inn_dlog_size=-0.015, bat_d_iso=-0.009, bat_d_bb_pa=-0.006 / surprise=-0.015
  - 広島 2023 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2014: bat_d_r_runner=0.005, inn_dlog_size=-0.013, bat_d_iso=0.006, bat_d_bb_pa=-0.013 / surprise=-0.013
  - ロッテ 2014 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2015: bat_d_r_runner=0.017, inn_dlog_size=-0.012, bat_d_iso=0.016, bat_d_bb_pa=-0.012 / surprise=-0.012
  - DeNA 2015 は「inn_dlog_size < 0」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- ほか 5 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 日本ハム 2020: bat_d_r_runner=-0.010, inn_dlog_size=0.026, bat_d_iso=-0.020, bat_d_bb_pa=0.003
- ヤクルト 2020: bat_d_r_runner=-0.022, inn_dlog_size=0.009, bat_d_iso=-0.004, bat_d_bb_pa=0.013

## P49: 得点がリーグ5位以下のチームの間では、走者1人あたりの得点が他球団より少なければ B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: t-2015, t-2019, t-2022, h-2012, t-2013 ほか
- もし: `bat_d_r_runner < 0` ならば: `upper_half == False`
- 識別子: `[where:rank_rf>=5] bat_d_r_runner<0 => upper_half==false`（指紋 `0adb6e0d7d35c2e2`）
- 兄弟（範囲と結論が同じ、条件が違う）: P21, P41, P42, P43
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。低得点のチームの中では、得点の効率は順位を分けない
- 注記: P41〜P43 と兄弟。成立率より lift と p を読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 47 | 41 | 0.87 [0.75, 0.94] | 0.85 | 1.03 | 0.164 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 2 | 0.25 [0.07, 0.59] | 0.10 | 2.60 | 0.164 | 0 | 判断保留 | 4 |
| 逆 | 44 | 41 | 0.93 [0.82, 0.98] | 0.90 | 1.03 | 0.164 | 0 | 支持 | 1 |
| 裏 | 5 | 2 | 0.40 [0.12, 0.77] | 0.15 | 2.60 | 0.164 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- 阪神 2015: bat_d_r_runner=-0.030, upper_half=True, rank_ra=5, rd=-85 / surprise=-3
  - 阪神 2015 は「bat_d_r_runner < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 阪神 2019: bat_d_r_runner=-0.037, upper_half=True, rank_ra=2, rd=-28 / surprise=-2
  - 阪神 2019 は「bat_d_r_runner < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 阪神 2022: bat_d_r_runner=-0.011, upper_half=True, rank_ra=1, rd=61 / surprise=2
  - 阪神 2022 は「bat_d_r_runner < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- ソフトバンク 2012: bat_d_r_runner=-0.014, upper_half=True, rank_ra=1, rd=23 / surprise=1
  - ソフトバンク 2012 は「bat_d_r_runner < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 阪神 2013: bat_d_r_runner=-0.032, upper_half=True, rank_ra=1, rd=43 / surprise=0
  - 阪神 2013 は「bat_d_r_runner < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 西武 2022: bat_d_r_runner=-0.007, upper_half=True, rank_ra=1, rd=16 / surprise=0
  - 西武 2022 は「bat_d_r_runner < 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6

**異議あり（例外あり）** 逆に判例 3 件（裏の判例も同じ）

- ロッテ 2014: bat_d_r_runner=0.005, upper_half=False, rank_ra=6, rd=-86 / surprise=-2
  - ロッテ 2014 は「upper_half == False」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2018: bat_d_r_runner=0.005, upper_half=False, rank_ra=3, rd=-70 / surprise=-2
  - DeNA 2018 は「upper_half == False」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2022: bat_d_r_runner=0.002, upper_half=False, rank_ra=5, rd=-71 / surprise=0
  - 日本ハム 2022 は「upper_half == False」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: bat_d_r_runner=-0.039, upper_half=True, rank_ra=4, rd=-60
- ロッテ 2020: bat_d_r_runner=-0.029, upper_half=True, rank_ra=2, rd=-18

## P50: 得点・失点の分布だけからシーズンを作り直したときに A クラスに入る確率が 0.5 以上なら、実際も A クラス

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 9 件: h-2013, d-2019, h-2021, l-2015, c-2015 ほか
- もし: `sim_p_upper >= 0.5` ならば: `upper_half == True`
- 識別子: `[all] sim_p_upper>=0.5 => upper_half==true`（指紋 `afed9548b83675bb`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 確率 0.5 以上のチーム・シーズンの4分の1を超えて B クラス
- 注記: この作り直しが順位をどれだけ言い当てるか。成り立たなければ、R10 の他の読みも弱める
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 77 | 68 | 0.88 [0.79, 0.94] | 0.50 | 1.77 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 69 | 0.88 [0.80, 0.94] | 0.51 | 1.75 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 68 | 0.87 [0.78, 0.93] | 0.49 | 1.77 | 0.000 | 0 | 支持 | 1 |
| 裏 | 79 | 69 | 0.87 [0.78, 0.93] | 0.50 | 1.75 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 9 件（対偶の判例も同じ）

- ソフトバンク 2013: sim_p_upper=0.885, upper_half=False, rank=4, rd=98, wins_vs_pythag=-8.37 / surprise=3
  - ソフトバンク 2013 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4
- 中日 2019 **(focus)**: sim_p_upper=0.627, upper_half=False, rank=5, rd=19, wins_vs_pythag=-4.71 / surprise=3
  - 中日 2019 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4
- ソフトバンク 2021: sim_p_upper=0.833, upper_half=False, rank=4, rd=71, wins_vs_pythag=-8.47 / surprise=3
  - ソフトバンク 2021 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4
- 西武 2015: sim_p_upper=0.680, upper_half=False, rank=4, rd=58, wins_vs_pythag=-6.07 / surprise=2
  - 西武 2015 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4
- 広島 2015: sim_p_upper=0.786, upper_half=False, rank=4, rd=32, wins_vs_pythag=-5.18 / surprise=1
  - 広島 2015 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4
- 巨人 2017: sim_p_upper=0.844, upper_half=False, rank=4, rd=32, wins_vs_pythag=-1.94 / surprise=1
  - 巨人 2017 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4
- ロッテ 2019: sim_p_upper=0.666, upper_half=False, rank=4, rd=31, wins_vs_pythag=-3.65 / surprise=1
  - ロッテ 2019 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4
- 巨人 2023: sim_p_upper=0.738, upper_half=False, rank=4, rd=16, wins_vs_pythag=-1.50 / surprise=1
  - 巨人 2023 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4
- 中日 2014 **(focus)**: sim_p_upper=0.543, upper_half=False, rank=4, rd=-20, wins_vs_pythag=-0.792 / surprise=0
  - 中日 2014 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H4

**異議あり（例外あり）** 逆に判例 10 件（裏の判例も同じ）

- 阪神 2015: sim_p_upper=0.234, upper_half=True, rank=3, rd=-85, wins_vs_pythag=+10.25 / surprise=-3
  - 阪神 2015 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- 西武 2012: sim_p_upper=0.467, upper_half=True, rank=2, rd=-2, wins_vs_pythag=+4.74 / surprise=-2
  - 西武 2012 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- DeNA 2019: sim_p_upper=0.426, upper_half=True, rank=2, rd=-15, wins_vs_pythag=+2.59 / surprise=-2
  - DeNA 2019 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- 阪神 2019: sim_p_upper=0.424, upper_half=True, rank=3, rd=-28, wins_vs_pythag=+3.68 / surprise=-2
  - 阪神 2019 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- ロッテ 2013: sim_p_upper=0.222, upper_half=True, rank=3, rd=-12, wins_vs_pythag=+4.35 / surprise=-1
  - ロッテ 2013 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- 阪神 2014: sim_p_upper=0.293, upper_half=True, rank=2, rd=-15, wins_vs_pythag=+5.12 / surprise=-1
  - 阪神 2014 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- ロッテ 2015: sim_p_upper=0.262, upper_half=True, rank=3, rd=-2, wins_vs_pythag=+2.23 / surprise=-1
  - ロッテ 2015 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- DeNA 2017: sim_p_upper=0.317, upper_half=True, rank=3, rd=-1, wins_vs_pythag=+4.11 / surprise=-1
  - DeNA 2017 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- ロッテ 2023: sim_p_upper=0.444, upper_half=True, rank=2, rd=-19, wins_vs_pythag=+3.33 / surprise=-1
  - ロッテ 2023 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4
- ヤクルト 2012: sim_p_upper=0.399, upper_half=True, rank=3, rd=-15, wins_vs_pythag=+3.30 / surprise=0
  - ヤクルト 2012 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H3, H4

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: sim_p_upper=0.840, upper_half=False, rank=4, rd=42, wins_vs_pythag=-5.42
- 楽天 2020: sim_p_upper=0.705, upper_half=False, rank=4, rd=35, wins_vs_pythag=-4.32

## P51: 中日は、得点・失点の分布だけからシーズンを作り直すと、A クラスに入る確率が 0.5 未満

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 3 件: d-2012, d-2019, d-2014
- もし: `（すべての単位）` ならば: `sim_p_upper < 0.5`
- 識別子: `[team=d] * => sim_p_upper<0.5`（指紋 `fa987a138cd397d7`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日のシーズンの4分の1を超えて、作り直しで A クラスに入る確率が 0.5 以上
- 注記: 中日の各年が、得点・失点の分布の時点で B クラス寄りだったか。チーム全体の比較は outputs/rank_expectation.jsonl
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 10 | 0.77 [0.50, 0.92] | 0.77 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 3 | 0 | 0.00 [0.00, 0.56] | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 3 件（対偶の判例も同じ）

- 中日 2012 **(focus)**: sim_p_upper=0.939, rank=2, rd=18, rank_rf=4, rank_ra=2 / surprise=0.939
  - 中日 2012 は「（すべての単位）」を満たすのに「sim_p_upper < 0.5」を満たさない。なぜか？ → H2, H3
- 中日 2019 **(focus)**: sim_p_upper=0.627, rank=5, rd=19, rank_rf=5, rank_ra=1 / surprise=0.627
  - 中日 2019 は「（すべての単位）」を満たすのに「sim_p_upper < 0.5」を満たさない。なぜか？ → H2, H3
- 中日 2014 **(focus)**: sim_p_upper=0.543, rank=4, rd=-20, rank_rf=5, rank_ra=2 / surprise=0.543
  - 中日 2014 は「（すべての単位）」を満たすのに「sim_p_upper < 0.5」を満たさない。なぜか？ → H2, H3

## P52: 得点・失点の分布から見た A クラスの確率が4割未満、または得点と失点の組み合わせ方が偶然の範囲を超えて不利（alloc_z_strat < −1）なら、B クラス

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 10 件: t-2015, t-2022, m-2013, t-2014, m-2015 ほか
- もし: `（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）` ならば: `upper_half == False`
- 識別子: `[all] ((alloc_z_strat<-1) | (sim_p_upper<0.4)) => upper_half==false`（指紋 `9b39490e840f2e44`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 2026年以降のデータで、この前件を満たすチーム・シーズンの4分の1を超えて A クラス、または B クラスの4分の1を超えて前件を満たさない
- 注記: 探索（R11）で見つけた式。作るきっかけと同じデータでの判定は確かめではない。逆（B クラス ⇒ 前件）が「なぜ B クラスか」の説明の網羅性にあたる
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 83 | 73 | 0.88 [0.79, 0.93] | 0.50 | 1.76 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 68 | 0.87 [0.78, 0.93] | 0.47 | 1.86 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 73 | 0.94 [0.86, 0.97] | 0.53 | 1.76 | 0.000 | 0 | 支持 | 1 |
| 裏 | 73 | 68 | 0.93 [0.85, 0.97] | 0.50 | 1.86 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 10 件（対偶の判例も同じ）

- 阪神 2015: sim_p_upper=0.234, alloc_z_strat=+1.44, upper_half=True, rank=3, rd=-85, wins_vs_pythag=+10.25 / surprise=-3
  - 阪神 2015 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 阪神 2022: sim_p_upper=0.832, alloc_z_strat=-2.14, upper_half=True, rank=3, rd=61, wins_vs_pythag=-9.93 / surprise=2
  - 阪神 2022 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- ロッテ 2013: sim_p_upper=0.222, alloc_z_strat=+1.64, upper_half=True, rank=3, rd=-12, wins_vs_pythag=+4.35 / surprise=-1
  - ロッテ 2013 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 阪神 2014: sim_p_upper=0.293, alloc_z_strat=+2.46, upper_half=True, rank=2, rd=-15, wins_vs_pythag=+5.12 / surprise=-1
  - 阪神 2014 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- ロッテ 2015: sim_p_upper=0.262, alloc_z_strat=+1.33, upper_half=True, rank=3, rd=-2, wins_vs_pythag=+2.23 / surprise=-1
  - ロッテ 2015 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- DeNA 2017: sim_p_upper=0.317, alloc_z_strat=+1.71, upper_half=True, rank=3, rd=-1, wins_vs_pythag=+4.11 / surprise=-1
  - DeNA 2017 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 巨人 2018: sim_p_upper=0.817, alloc_z_strat=-1.75, upper_half=True, rank=3, rd=50, wins_vs_pythag=-7.25 / surprise=1
  - 巨人 2018 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- ヤクルト 2012: sim_p_upper=0.399, alloc_z_strat=+1.53, upper_half=True, rank=3, rd=-15, wins_vs_pythag=+3.30 / surprise=0
  - ヤクルト 2012 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- ソフトバンク 2022: sim_p_upper=0.928, alloc_z_strat=-1.10, upper_half=True, rank=1, rd=84, wins_vs_pythag=-5.01 / surprise=0
  - ソフトバンク 2022 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 阪神 2025: sim_p_upper=1.000, alloc_z_strat=-1.53, upper_half=True, rank=1, rd=144, wins_vs_pythag=-5.62 / surprise=0
  - 阪神 2025 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9

**異議あり（例外あり）** 逆に判例 5 件（裏の判例も同じ）

- 楽天 2012: sim_p_upper=0.425, alloc_z_strat=0.135, upper_half=False, rank=4, rd=24, wins_vs_pythag=-3.07 / surprise=1
  - 楽天 2012 は「upper_half == False」を満たすのに「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 広島 2019: sim_p_upper=0.487, alloc_z_strat=0.232, upper_half=False, rank=4, rd=-10, wins_vs_pythag=+1.07 / surprise=1
  - 広島 2019 は「upper_half == False」を満たすのに「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 巨人 2023: sim_p_upper=0.738, alloc_z_strat=-0.914, upper_half=False, rank=4, rd=16, wins_vs_pythag=-1.50 / surprise=1
  - 巨人 2023 は「upper_half == False」を満たすのに「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 中日 2014 **(focus)**: sim_p_upper=0.543, alloc_z_strat=-0.752, upper_half=False, rank=4, rd=-20, wins_vs_pythag=-0.792 / surprise=0
  - 中日 2014 は「upper_half == False」を満たすのに「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 阪神 2016: sim_p_upper=0.438, alloc_z_strat=-0.594, upper_half=False, rank=4, rd=-40, wins_vs_pythag=-1.13 / surprise=0
  - 阪神 2016 は「upper_half == False」を満たすのに「（[sim_p_upper < 0.4] または [alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: sim_p_upper=0.371, alloc_z_strat=+1.36, upper_half=True, rank=3, rd=-60, wins_vs_pythag=+9.35
- 西武 2020: sim_p_upper=0.200, alloc_z_strat=+2.26, upper_half=True, rank=3, rd=-64, wins_vs_pythag=+6.63
