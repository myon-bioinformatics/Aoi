# 異議あり — 命題の判定記録（自動生成）

判定基準は結果を見る前に命題ファイルに書いたもの（docs/propositions.md）。
命題ファイル SHA-256: `16c9c1f873aa81d049ecdf1ce51f75227cf44fc64b419fc389f61501e5a101a3` / コード: `e997caaeb38113f8e2ae7ef664098fb18ebd7334`

判定は命題がその範囲で成り立つかどうかだけを示し、原因は示さない。

## 命題の系譜

- P15 → **P18**: P15 の判例 10件（低得点・失点2番目以内なのに B クラス）を見て、得失点差がプラスかどうかで分かれているように見えたため、前件に rd > 0 を加えた。結果を見てから作ったので、確かめには新しいデータ（2026年以降、または未取得の年）を使う
- P19 → **P36**: 天井の帯を k ≥ 6（幅の上限なし）から k = 6〜7（床と同じ幅2）に変えた。R3 の比較は、得点の量で比べると天井が大きく出る作りだったため（R3 の自分への異議）
- P20 → **P37**: P36 と同じ変更（天井の帯を k = 6〜7 にして幅をそろえた）
- P23 → **P155**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P26 → **P156**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P27 → **P157**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P28 → **P158**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P29 → **P159**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P30 → **P160**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P31 → **P161**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P32 → **P162**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P33 → **P35**: 強さを usually（0.75）から more_often_than_not（0.50）に下げた。P33 は成立率 0.66・lift 1.32・p < 0.001 で、関係はあるが「概ね」に届かなかった。同じデータでの言い直しで、確かめではない
- P46 → **P163**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P47 → **P164**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P52 → **P95**: 式1が取りこぼした 2014年の道筋（R17、強い相手との試合で点の差どおりに勝てていない）を3つ目の組として足した。閾値 −2 は中日 2014 の −2.57 を見て決めた
- P53 → **P77**: 3位と4位すべてから、2014年と同じ状況（4位で、分布の見込みが 0.5 以上）に絞り、結論を「直接対決で負け越し」にした。2014年は作るきっかけなので held-out から除く
- P70 → **P74**: 見込みの式が相手のグループで偏っていた（R16 の自分への異議）ので、同じ年・同じリーグの全球団の平均を引いた値に変えた。R16 の読み直しを見た後の言い直し
  - P74 → **P76**: 中日だけから、2019年と同じ状況（得失点差がプラスなのに B クラス）のチーム・シーズン全体に広げた。2019年は作るきっかけなので held-out から除く
    - P76 → **P80**: 結論を「得点の差が負」から「試合全体の点が少ない（env < 0）」に変えた（2019年の得点 −57・失点 +13 の鏡の形から）
- P71 → **P75**: P74 と同じ変更（平均を引いた値）
- P73 → **P78**: 全球団から、2014年と同じ状況（4位で、分布の見込みが 0.5 以上）に絞った。2014年は作るきっかけなので held-out から除く
- P98 → **P165**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P104 → **P169**: 範囲の「B クラス」を「もし」に移し、中日だけで逆・裏を見られるようにした（R41 と同じ立て直し）
- P105 → **P166**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
  - P166 → **P168**: 範囲から「中日以外」を外し、中日を含めた全体で4つの形を見る
- P115 → **P126**: 上位半分を順位（3位以内）ではなく、1試合あたりの優位の符号で決める。R31 で、失点3位でも優位がほぼ 0 か負の単位が4つあった
  - P126 → **P134**: 優位の符号ではなく、0 から1標準偏差以上離れた単位だけで読む（R32 で 0 の近くの単位が出入りした）
    - P134 → **P139**: 幅の物差しを、チームの間の散らばり（R33、広すぎた）から、その年の平均の誤差（試合ごとの点の散らばり）にする
- P116 → **P172**: R27 の種: P116 の判例（大きさは上位なのに B）の多くは得点も上位だった。失点がはっきり劣る単位を除く条件を足す
- P118 → **P127**: 失点だけ上位の範囲を、順位ではなく優位の符号で決める（R31）
- P123 → **P128**: 失点だけ上位の範囲を、順位ではなく優位の符号で決める（R31）
  - P128 → **P135**: 失点だけ優位の範囲を、符号ではなく1標準偏差以上の離れで決める
    - P135 → **P140**: 幅の物差しを、その年の平均の誤差にする
- P141 → **P167**: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ
- P143 → **P144**: 範囲を、失点 +1 の形だけから、得点 −1 の形すべて（失点 −1・0・+1）に広げた。R37 で阪神 2015・巨人 2016 も同じ向きに外れていた

## P1: 得失点差がプラスなら、上位半分（Aクラス）である

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 12 件: h-2013, d-2019, h-2021, l-2015, c-2022 ほか
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[all] rd>0 => upper_half==true`（指紋 `43d21396576b5a67`）
- 兄弟（範囲と結論が同じ、条件が違う）: P11, P50, P152, P153, P154, P177, P178, P179, P180, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 73 | 61 | 0.84 [0.73, 0.90] | +1.69σ（0.055） | 0.50 | 1.67 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 66 | 0.85 [0.75, 0.91] | +1.96σ（0.029） | 0.53 | 1.59 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 61 | 0.78 [0.68, 0.86] | +0.65σ（0.306） | 0.47 | 1.67 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 83 | 66 | 0.80 [0.70, 0.87] | +0.95σ（0.207） | 0.50 | 1.59 | 0.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 78 | 67 | 0.86 [0.76, 0.92] | +2.22σ（0.014） | 0.50 | 1.72 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 67 | 0.86 [0.76, 0.92] | +2.22σ（0.014） | 0.50 | 1.72 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 67 | 0.86 [0.76, 0.92] | +2.22σ（0.014） | 0.50 | 1.72 | 0.000 | 0 | 支持 | 1 |
| 裏 | 78 | 67 | 0.86 [0.76, 0.92] | +2.22σ（0.014） | 0.50 | 1.72 | 0.000 | 0 | 支持 | 1 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 53 | 37 | 0.70 [0.56, 0.80] | -0.87σ（0.234） | 0.50 | 1.40 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 62 | 0.79 [0.69, 0.87] | +0.92σ（0.219） | 0.66 | 1.20 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 78 | 37 | 0.47 [0.37, 0.58] | -5.62σ（0.000） | 0.34 | 1.40 | 0.000 | 0 | 修正 | 2 |
| 裏 | 103 | 62 | 0.60 [0.51, 0.69] | -3.47σ（0.001） | 0.50 | 1.20 | 0.000 | 0 | 修正 | 2 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 38 | 0.73 [0.60, 0.83] | -0.32σ（0.426） | 0.50 | 1.46 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 64 | 0.82 [0.72, 0.89] | +1.44σ（0.092） | 0.67 | 1.23 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 78 | 38 | 0.49 [0.38, 0.60] | -5.36σ（0.000） | 0.33 | 1.46 | 0.000 | 0 | 修正 | 2 |
| 裏 | 104 | 64 | 0.62 [0.52, 0.70] | -3.17σ（0.002） | 0.50 | 1.23 | 0.000 | 0 | 修正 | 2 |

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
- 兄弟（範囲と結論が同じ、条件が違う）: P52, P64, P95, P96, P115, P126, P138, P147, P148, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 44 | 0.85 [0.72, 0.92] | +1.60σ（0.070） | 0.50 | 1.69 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 70 | 0.90 [0.81, 0.95] | +3.01σ（0.001） | 0.67 | 1.35 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 44 | 0.56 [0.45, 0.67] | -3.79σ（0.000） | 0.33 | 1.69 | 0.000 | 0 | 修正 | 2 |
| 裏 | 104 | 70 | 0.67 [0.58, 0.76] | -1.81σ（0.048） | 0.50 | 1.35 | 0.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 156 | 120 | 0.77 [0.70, 0.83] | -5.44σ（0.000） | 0.77 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 36 | 0 | 0.00 [0.00, 0.10] | -18.00σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 56 | 0.74 [0.63, 0.82] | -0.26σ（0.439） | 0.47 | 1.55 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 82 | 62 | 0.76 [0.65, 0.84] | +0.13σ（0.509） | 0.51 | 1.47 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 74 | 56 | 0.76 [0.65, 0.84] | +0.13σ（0.509） | 0.49 | 1.55 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 80 | 62 | 0.78 [0.67, 0.85] | +0.52σ（0.356） | 0.53 | 1.47 | 0.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 46 | 0.61 [0.49, 0.71] | -2.91σ（0.004） | 0.47 | 1.28 | 0.001 | 0 | 修正 | 2 |
| 対偶 | 82 | 52 | 0.63 [0.53, 0.73] | -2.42σ（0.013） | 0.51 | 1.24 | 0.001 | 0 | 修正 | 2 |
| 逆 | 74 | 46 | 0.62 [0.51, 0.72] | -2.55σ（0.010） | 0.49 | 1.28 | 0.001 | 0 | 修正 | 2 |
| 裏 | 80 | 52 | 0.65 [0.54, 0.75] | -2.07σ（0.029） | 0.53 | 1.24 | 0.001 | 0 | 修正 | 2 |

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
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P50, P152, P153, P154, P177, P178, P179, P180, P182
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 得失点差が拮抗し1点差で勝ち越したチーム・シーズンの半数以上が下位半分
- 注記: 「得失点差が同程度でも勝率が違う」を、得失点差の幅を絞って比べる。±20 は「同程度」の目安として事前に決めた値
- 条件の数: 4（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 20 | 18 | 0.90 [0.70, 0.97] | +3.58σ（0.000） | 0.50 | 1.80 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 76 | 0.97 [0.91, 0.99] | +8.38σ（0.000） | 0.87 | 1.12 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 18 | 0.23 [0.15, 0.34] | -4.76σ（0.000） | 0.13 | 1.80 | 0.000 | 0 | 修正 | 2 |
| 裏 | 136 | 76 | 0.56 [0.47, 0.64] | +1.37σ（0.099） | 0.50 | 1.12 | 0.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 12 | 0.92 [0.67, 0.99] | +1.44σ（0.127） | 0.95 | 0.97 | 0.865 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 7 | 0.88 [0.53, 0.98] | +0.82σ（0.367） | 0.92 | 0.95 | 0.865 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 10 | 0.77 [0.50, 0.92] | +0.16σ（0.584） | 0.79 | 0.98 | 0.716 | 0 | 判断保留 | 4 |
| 対偶 | 33 | 30 | 0.91 [0.76, 0.97] | +2.11σ（0.021） | 0.92 | 0.99 | 0.716 | 0 | 支持 | 1 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 28 | 15 | 0.54 [0.36, 0.70] | +0.38σ（0.425） | 0.50 | 1.07 | 0.417 | 12 | 判断保留 | 4 |
| 対偶 | 72 | 59 | 0.82 [0.72, 0.89] | +5.42σ（0.000） | 0.81 | 1.02 | 0.417 | 12 | 支持 | 1 |
| 逆 | 72 | 15 | 0.21 [0.13, 0.32] | -4.95σ（0.000） | 0.19 | 1.07 | 0.417 | 12 | 棄却 | 3 |
| 裏 | 116 | 59 | 0.51 [0.42, 0.60] | +0.19σ（0.463） | 0.50 | 1.02 | 0.417 | 12 | 判断保留 | 4 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 61 | 39 | 0.64 [0.51, 0.75] | +2.18σ（0.020） | 0.37 | 1.75 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 99 | 77 | 0.78 [0.69, 0.85] | +5.53σ（0.000） | 0.61 | 1.28 | 0.000 | 0 | 支持 | 1 |
| 逆 | 57 | 39 | 0.68 [0.56, 0.79] | +2.78σ（0.004） | 0.39 | 1.75 | 0.000 | 0 | 支持 | 1 |
| 裏 | 95 | 77 | 0.81 [0.72, 0.88] | +6.05σ（0.000） | 0.63 | 1.28 | 0.000 | 0 | 支持 | 1 |

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
- 台帳: 評価 32 回、元の命題に異議あり 32 回（どれかの形に異議あり 32 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 5 | 0.38 [0.18, 0.64] | -3.04σ（0.006） | 0.50 | 0.77 | 0.877 | 0 | 棄却 | 3 |
| 対偶 | 78 | 70 | 0.90 [0.81, 0.95] | +3.01σ（0.001） | 0.92 | 0.98 | 0.877 | 0 | 支持 | 1 |

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
- 台帳: 評価 31 回、元の命題に異議あり 31 回（どれかの形に異議あり 31 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 6 | 0.38 [0.18, 0.61] | -3.46σ（0.002） | 0.15 | 2.44 | 0.007 | 0 | 修正 | 2 |
| 対偶 | 44 | 34 | 0.77 [0.63, 0.87] | +0.35σ（0.442） | 0.69 | 1.12 | 0.007 | 0 | 判断保留 | 4 |
| 逆 | 8 | 6 | 0.75 [0.41, 0.93] | +0.00σ（0.679） | 0.31 | 2.44 | 0.007 | 0 | 判断保留 | 4 |
| 裏 | 36 | 34 | 0.94 [0.82, 0.98] | +2.69σ（0.003） | 0.85 | 1.12 | 0.007 | 0 | 支持 | 1 |

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
- 台帳: 評価 31 回、元の命題に異議あり 31 回（どれかの形に異議あり 31 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 24 | 4 | 0.17 [0.07, 0.36] | -3.27σ（0.001） | 0.15 | 1.08 | 0.556 | 0 | 棄却 | 3 |
| 対偶 | 44 | 24 | 0.55 [0.40, 0.68] | +0.60σ（0.326） | 0.54 | 1.01 | 0.556 | 0 | 判断保留 | 4 |
| 逆 | 8 | 4 | 0.50 [0.22, 0.78] | +0.00σ（0.637） | 0.46 | 1.08 | 0.556 | 0 | 判断保留 | 4 |
| 裏 | 28 | 24 | 0.86 [0.69, 0.94] | +3.78σ（0.000） | 0.85 | 1.01 | 0.556 | 0 | 支持 | 1 |

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
- 台帳: 評価 31 回、元の命題に異議あり 31 回（どれかの形に異議あり 31 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 7 | 0.64 [0.35, 0.85] | -0.87σ（0.287） | 0.64 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | -3.46σ（0.004） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 31 回、元の命題に異議あり 31 回（どれかの形に異議あり 31 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 6 | 5 | 0.83 [0.44, 0.97] | +0.47σ（0.534） | 0.38 | 2.22 | 0.008 | 0 | 判断保留 | 4 |
| 対偶 | 10 | 9 | 0.90 [0.60, 0.98] | +1.10σ（0.244） | 0.62 | 1.44 | 0.008 | 0 | 判断保留 | 4 |
| 逆 | 6 | 5 | 0.83 [0.44, 0.97] | +0.47σ（0.534） | 0.38 | 2.22 | 0.008 | 0 | 判断保留 | 4 |
| 裏 | 10 | 9 | 0.90 [0.60, 0.98] | +1.10σ（0.244） | 0.62 | 1.44 | 0.008 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 30 回、元の命題に異議あり 30 回（どれかの形に異議あり 30 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 0 | 0.00 [0.00, 0.26] | -5.74σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 11 | 0 | 0.00 [0.00, 0.26] | -5.74σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

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
- 台帳: 評価 30 回、元の命題に異議あり 30 回（どれかの形に異議あり 30 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 12 | 0.23 [0.14, 0.36] | -3.88σ（0.000） | 0.23 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 40 | 0 | 0.00 [0.00, 0.09] | -6.32σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

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
- 台帳: 評価 30 回、元の命題に異議あり 30 回（どれかの形に異議あり 30 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 9 | 0.75 [0.47, 0.91] | +0.00σ（0.649） | 0.85 | 0.89 | 0.928 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 5 | 0.62 [0.31, 0.86] | -0.82σ（0.321） | 0.77 | 0.81 | 0.928 | 0 | 判断保留 | 4 |
| 逆 | 44 | 9 | 0.20 [0.11, 0.35] | -8.36σ（0.000） | 0.23 | 0.89 | 0.928 | 0 | 棄却 | 3 |
| 裏 | 40 | 5 | 0.12 [0.05, 0.26] | -9.13σ（0.000） | 0.15 | 0.81 | 0.928 | 0 | 棄却 | 3 |

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
- 台帳: 評価 29 回、元の命題に異議あり 29 回（どれかの形に異議あり 29 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 6 | 0.55 [0.28, 0.79] | -1.57σ（0.115） | 0.55 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 5 | 0 | 0.00 [0.00, 0.43] | -3.87σ（0.001） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 29 回、元の命題に異議あり 29 回（どれかの形に異議あり 29 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 35 | 0.73 [0.59, 0.83] | +3.18σ（0.001） | 0.73 | 1.00 | 1.000 | 0 | 支持 | 1 |
| 対偶 | 13 | 0 | 0.00 [0.00, 0.23] | -3.61σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

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
- 台帳: 評価 29 回、元の命題に異議あり 29 回（どれかの形に異議あり 29 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 35 | 31 | 0.89 [0.74, 0.95] | +1.85σ（0.041） | 0.85 | 1.04 | 0.278 | 0 | 判断保留 | 4 |
| 対偶 | 7 | 3 | 0.43 [0.16, 0.75] | -1.96σ（0.071） | 0.27 | 1.58 | 0.278 | 0 | 判断保留 | 4 |
| 逆 | 41 | 31 | 0.76 [0.61, 0.86] | +0.09σ（0.548） | 0.73 | 1.04 | 0.278 | 0 | 判断保留 | 4 |
| 裏 | 13 | 3 | 0.23 [0.08, 0.50] | -4.32σ（0.000） | 0.15 | 1.58 | 0.278 | 0 | 棄却 | 3 |

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
- 台帳: 評価 29 回、元の命題に異議あり 29 回（どれかの形に異議あり 29 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 7 | 0.64 [0.35, 0.85] | -0.87σ（0.287） | 0.64 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | -3.46σ（0.004） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 28 回、元の命題に異議あり 28 回（どれかの形に異議あり 28 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.91 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 28 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 28 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | +1.91σ（0.042） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## P28: 得点がリーグ5位以下だったシーズンの中日は、ホームの試合で得点した回の大きさが他球団（ホーム同士）より小さい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2014
- もし: `（すべての単位）` ならば: `inn_dlog_size_home < 0`
- 識別子: `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_dlog_size_home<0`（指紋 `982ba976095d3ed6`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、ホームの大きさが他球団以上
- 注記: 球場の係数ではない。ホーム同士で比べるだけ。P29 と片方だけ成り立つなら、主催区分の問題として扱う（原因は特定しない）
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 28 回、元の命題に異議あり 28 回（どれかの形に異議あり 28 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.91 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 28 回、元の命題に異議あり 28 回（どれかの形に異議あり 28 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.91 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 28 回、元の命題に異議あり 28 回（どれかの形に異議あり 28 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 37 | 28 | 0.76 [0.60, 0.87] | +3.12σ（0.001） | 0.76 | 1.00 | 1.000 | 0 | 支持 | 1 |
| 対偶 | 9 | 0 | 0.00 [0.00, 0.30] | -3.00σ（0.002） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 27 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 27 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | +1.91σ（0.042） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## P32: 得点がリーグ5位以下だったシーズンの中日は、出塁率が他球団より低い

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `（すべての単位）` ならば: `bat_d_obp < 0`
- 識別子: `[team=d, where:rank_rf>=5] * => bat_d_obp<0`（指紋 `c0b8da141e31af81`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 11
- 見直す条件（反証）: 中日の低得点のシーズンの4分の1を超えて、出塁率が他球団以上
- 注記: P31 と組で読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 27 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 27 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | +1.91σ（0.042） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## P33: ISO が同じ年・同じリーグの他球団より低ければ、得点した回のうち3点以上の回の割合も他球団より少ない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 26 件: t-2023, m-2022, c-2022, s-2016, m-2016 ほか
- もし: `bat_d_iso < 0` ならば: `inn_d_big_share < 0`
- 識別子: `[seasons=2013-2025] bat_d_iso<0 => inn_d_big_share<0`（指紋 `3a4203e6412ef7e6`）
- 兄弟（範囲と結論が同じ、条件が違う）: P35
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: ISO が低いチーム・シーズンの4分の1を超えて、3点以上の回の割合が他球団以上
- 注記: 成り立たなければ、ISO と大量点の回を結ぶ見方そのものを弱める（中日の R5 の結果を長打で説明できなくなる）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 27 回、元の命題に異議あり 27 回（どれかの形に異議あり 27 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 50 | 0.66 [0.55, 0.75] | -1.85σ（0.046） | 0.50 | 1.32 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 72 | 46 | 0.64 [0.52, 0.74] | -2.18σ（0.024） | 0.47 | 1.35 | 0.000 | 0 | 修正 | 2 |
| 逆 | 72 | 50 | 0.69 [0.58, 0.79] | -1.09σ（0.170） | 0.53 | 1.32 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 68 | 46 | 0.68 [0.56, 0.78] | -1.40σ（0.106） | 0.50 | 1.35 | 0.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 27 回、元の命題に異議あり 27 回（どれかの形に異議あり 27 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 72 | 57 | 0.79 [0.68, 0.87] | +0.82σ（0.252） | 0.47 | 1.68 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 76 | 61 | 0.80 [0.70, 0.88] | +1.06σ（0.178） | 0.50 | 1.61 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 68 | 57 | 0.84 [0.73, 0.91] | +1.68σ（0.057） | 0.50 | 1.68 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 72 | 61 | 0.85 [0.75, 0.91] | +1.91σ（0.034） | 0.53 | 1.61 | 0.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 26 回、元の命題に異議あり 26 回（どれかの形に異議あり 26 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 50 | 0.66 [0.55, 0.75] | +2.75σ（0.004） | 0.50 | 1.32 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 72 | 46 | 0.64 [0.52, 0.74] | +2.36σ（0.012） | 0.47 | 1.35 | 0.000 | 0 | 支持 | 1 |
| 逆 | 72 | 50 | 0.69 [0.58, 0.79] | +3.30σ（0.001） | 0.53 | 1.32 | 0.000 | 0 | 支持 | 1 |
| 裏 | 68 | 46 | 0.68 [0.56, 0.78] | +2.91σ（0.002） | 0.50 | 1.35 | 0.000 | 0 | 支持 | 1 |

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
- 台帳: 評価 26 回、元の命題に異議あり 26 回（どれかの形に異議あり 26 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 3 | 0.27 [0.10, 0.57] | -3.66σ（0.001） | 0.27 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 8 | 0 | 0.00 [0.00, 0.32] | -4.90σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 26 回、元の命題に異議あり 26 回（どれかの形に異議あり 26 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 21 | 0.40 [0.28, 0.54] | -1.39σ（0.106） | 0.40 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 31 | 0 | 0.00 [0.00, 0.11] | -5.57σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

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
- 台帳: 評価 26 回、元の命題に異議あり 26 回（どれかの形に異議あり 26 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 73 | 44 | 0.60 [0.49, 0.71] | -2.91σ（0.004） | 0.44 | 1.38 | 0.000 | 0 | 修正 | 2 |
| 対偶 | 81 | 52 | 0.64 [0.53, 0.74] | -2.25σ（0.020） | 0.49 | 1.30 | 0.000 | 0 | 修正 | 2 |
| 逆 | 63 | 44 | 0.70 [0.58, 0.80] | -0.95σ（0.209） | 0.51 | 1.38 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 71 | 52 | 0.73 [0.62, 0.82] | -0.34σ（0.410） | 0.56 | 1.30 | 0.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 26 回、元の命題に異議あり 26 回（どれかの形に異議あり 26 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 76 | 43 | 0.57 [0.45, 0.67] | -3.71σ（0.000） | 0.44 | 1.29 | 0.001 | 0 | 修正 | 2 |
| 対偶 | 81 | 48 | 0.59 [0.48, 0.69] | -3.27σ（0.001） | 0.47 | 1.25 | 0.001 | 0 | 修正 | 2 |
| 逆 | 63 | 43 | 0.68 [0.56, 0.78] | -1.24σ（0.138） | 0.53 | 1.29 | 0.001 | 0 | 判断保留 | 4 |
| 裏 | 68 | 48 | 0.71 [0.59, 0.80] | -0.84σ（0.238） | 0.56 | 1.25 | 0.001 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 25 回、元の命題に異議あり 25 回（どれかの形に異議あり 25 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 9 | 0.82 [0.52, 0.95] | +0.52σ（0.455） | 0.82 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 2 | 0 | 0.00 [0.00, 0.66] | -2.45σ（0.062） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 25 回、元の命題に異議あり 25 回（どれかの形に異議あり 25 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 32 | 27 | 0.84 [0.68, 0.93] | +1.22σ（0.153） | 0.85 | 1.00 | 0.668 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 3 | 0.38 [0.14, 0.69] | -2.45σ（0.027） | 0.38 | 0.97 | 0.668 | 0 | 判断保留 | 4 |
| 逆 | 44 | 27 | 0.61 [0.47, 0.74] | -2.09σ（0.032） | 0.62 | 1.00 | 0.668 | 0 | 棄却 | 3 |
| 裏 | 20 | 3 | 0.15 [0.05, 0.36] | -6.20σ（0.000） | 0.15 | 0.97 | 0.668 | 0 | 棄却 | 3 |

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
- 台帳: 評価 25 回、元の命題に異議あり 25 回（どれかの形に異議あり 25 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 45 | 39 | 0.87 [0.74, 0.94] | +1.81σ（0.045） | 0.85 | 1.02 | 0.291 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 2 | 0.25 [0.07, 0.59] | -3.27σ（0.004） | 0.13 | 1.86 | 0.291 | 0 | 判断保留 | 4 |
| 逆 | 44 | 39 | 0.89 [0.76, 0.95] | +2.09σ（0.021） | 0.87 | 1.02 | 0.291 | 0 | 支持 | 1 |
| 裏 | 7 | 2 | 0.29 [0.08, 0.64] | -2.84σ（0.013） | 0.15 | 1.86 | 0.291 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 25 回、元の命題に異議あり 25 回（どれかの形に異議あり 25 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 40 | 34 | 0.85 [0.71, 0.93] | +1.46σ（0.096） | 0.85 | 1.00 | 0.601 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 2 | 0.25 [0.07, 0.59] | -3.27σ（0.004） | 0.23 | 1.08 | 0.601 | 0 | 判断保留 | 4 |
| 逆 | 44 | 34 | 0.77 [0.63, 0.87] | +0.35σ（0.442） | 0.77 | 1.00 | 0.601 | 0 | 判断保留 | 4 |
| 裏 | 12 | 2 | 0.17 [0.05, 0.45] | -4.67σ（0.000） | 0.15 | 1.08 | 0.601 | 0 | 棄却 | 3 |

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
- 台帳: 評価 25 回、元の命題に異議あり 25 回（どれかの形に異議あり 25 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 71 | 40 | 0.56 [0.45, 0.67] | -3.63σ（0.000） | 0.44 | 1.29 | 0.002 | 0 | 修正 | 2 |
| 対偶 | 81 | 50 | 0.62 [0.51, 0.72] | -2.76σ（0.006） | 0.51 | 1.22 | 0.002 | 0 | 修正 | 2 |
| 逆 | 63 | 40 | 0.63 [0.51, 0.74] | -2.11σ（0.028） | 0.49 | 1.29 | 0.002 | 0 | 修正 | 2 |
| 裏 | 73 | 50 | 0.68 [0.57, 0.78] | -1.28σ（0.126） | 0.56 | 1.22 | 0.002 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 25 回、元の命題に異議あり 25 回（どれかの形に異議あり 25 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 7 | 0.64 [0.35, 0.85] | -0.87σ（0.287） | 0.64 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | -3.46σ（0.004） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 24 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 24 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | +1.91σ（0.042） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## P47: 得点がリーグ5位以下のチーム・シーズン（中日を除く）では、走者1人あたりの得点が他球団より少ない

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 5 件: t-2021, m-2014, db-2018, c-2023, f-2022
- もし: `（すべての単位）` ならば: `bat_d_r_runner < 0`
- 識別子: `[where:rank_rf>=5, where:team!="d"] * => bat_d_r_runner<0`（指紋 `603eea1d2eb73341`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '>=', 'value': 5}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 41
- 見直す条件（反証）: 中日以外の低得点のチーム・シーズンの半数以上で、走者1人あたりの得点が他球団以上
- 注記: P46 と成立率を並べ、中日固有かを見る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 24 回、元の命題に異議あり 24 回（どれかの形に異議あり 24 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 41 | 36 | 0.88 [0.74, 0.95] | +4.84σ（0.000） | 0.88 | 1.00 | 1.000 | 0 | 支持 | 1 |
| 対偶 | 5 | 0 | 0.00 [0.00, 0.43] | -2.24σ（0.031） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 24 回、元の命題に異議あり 24 回（どれかの形に異議あり 24 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 71 | 48 | 0.68 [0.56, 0.77] | -1.44σ（0.099） | 0.44 | 1.55 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 81 | 58 | 0.72 [0.61, 0.80] | -0.71σ（0.277） | 0.51 | 1.41 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 63 | 48 | 0.76 [0.64, 0.85] | +0.22σ（0.481） | 0.49 | 1.55 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 73 | 58 | 0.79 [0.69, 0.87] | +0.88σ（0.232） | 0.56 | 1.41 | 0.000 | 0 | 判断保留 | 4 |

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
- 台帳: 評価 24 回、元の命題に異議あり 24 回（どれかの形に異議あり 24 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 47 | 41 | 0.87 [0.75, 0.94] | +1.94σ（0.032） | 0.85 | 1.03 | 0.164 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 2 | 0.25 [0.07, 0.59] | -3.27σ（0.004） | 0.10 | 2.60 | 0.164 | 0 | 判断保留 | 4 |
| 逆 | 44 | 41 | 0.93 [0.82, 0.98] | +2.79σ（0.002） | 0.90 | 1.03 | 0.164 | 0 | 支持 | 1 |
| 裏 | 5 | 2 | 0.40 [0.12, 0.77] | -1.81σ（0.104） | 0.15 | 2.60 | 0.164 | 0 | 判断保留 | 4 |

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
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P152, P153, P154, P177, P178, P179, P180, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 確率 0.5 以上のチーム・シーズンの4分の1を超えて B クラス
- 注記: この作り直しが順位をどれだけ言い当てるか。成り立たなければ、R10 の他の読みも弱める
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 24 回、元の命題に異議あり 24 回（どれかの形に異議あり 24 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 77 | 68 | 0.88 [0.79, 0.94] | +2.70σ（0.003） | 0.50 | 1.77 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 69 | 0.88 [0.80, 0.94] | +2.75σ（0.003） | 0.51 | 1.75 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 68 | 0.87 [0.78, 0.93] | +2.48σ（0.006） | 0.49 | 1.77 | 0.000 | 0 | 支持 | 1 |
| 裏 | 79 | 69 | 0.87 [0.78, 0.93] | +2.53σ（0.005） | 0.50 | 1.75 | 0.000 | 0 | 支持 | 1 |

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
- 台帳: 評価 24 回、元の命題に異議あり 24 回（どれかの形に異議あり 24 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 10 | 0.77 [0.50, 0.92] | +0.16σ（0.584） | 0.77 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 3 | 0 | 0.00 [0.00, 0.56] | -3.00σ（0.016） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

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
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P64, P95, P96, P115, P126, P138, P147, P148, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 2026年以降のデータで、この前件を満たすチーム・シーズンの4分の1を超えて A クラス、または B クラスの4分の1を超えて前件を満たさない
- 注記: 探索（R11）で見つけた式。作るきっかけと同じデータでの判定は確かめではない。逆（B クラス ⇒ 前件）が「なぜ B クラスか」の説明の網羅性にあたる
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 24 回、元の命題に異議あり 24 回（どれかの形に異議あり 24 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 83 | 73 | 0.88 [0.79, 0.93] | +2.73σ（0.003） | 0.50 | 1.76 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 68 | 0.87 [0.78, 0.93] | +2.48σ（0.006） | 0.47 | 1.86 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 73 | 0.94 [0.86, 0.97] | +3.79σ（0.000） | 0.53 | 1.76 | 0.000 | 0 | 支持 | 1 |
| 裏 | 73 | 68 | 0.93 [0.85, 0.97] | +3.58σ（0.000） | 0.50 | 1.86 | 0.000 | 0 | 支持 | 1 |

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

## P53: 3位と4位のチームの間では、直接対決で勝ち越したほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 9 件: c-2015, t-2016, g-2017, db-2018, e-2012 ほか
- もし: `pair34_net > 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] pair34_net>0 => upper_half==true`（指紋 `59e83bdc34c8d35a`）
- 兄弟（範囲と結論が同じ、条件が違う）: P54, P55, P56, P57, P58, P59, P66, P67, P68
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。境目は直接対決では決まっていない
- 注記: 直接対決は順位を決める勝ち負けの一部。成り立っても記述であって、なぜ勝てたかの説明ではない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 23 回、元の命題に異議あり 23 回（どれかの形に異議あり 23 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 25 | 16 | 0.64 [0.45, 0.80] | -1.27σ（0.149） | 0.50 | 1.28 | 0.047 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 17 | 0.65 [0.46, 0.81] | -1.13σ（0.180） | 0.52 | 1.26 | 0.047 | 0 | 判断保留 | 4 |
| 逆 | 26 | 16 | 0.62 [0.43, 0.78] | -1.59σ（0.091） | 0.48 | 1.28 | 0.047 | 0 | 判断保留 | 4 |
| 裏 | 27 | 17 | 0.63 [0.44, 0.78] | -1.44σ（0.113） | 0.50 | 1.26 | 0.047 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 9 件（対偶の判例も同じ）

- 広島 2015: pair34_net=7, upper_half=False, sim_p_upper=0.786, alloc_z_strat=-1.47, vs_near_net=1, half2_vs_pythag=+1.86 / surprise=7
  - 広島 2015 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 阪神 2016: pair34_net=6, upper_half=False, sim_p_upper=0.438, alloc_z_strat=-0.594, vs_near_net=6, half2_vs_pythag=-1.95 / surprise=6
  - 阪神 2016 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2017: pair34_net=6, upper_half=False, sim_p_upper=0.844, alloc_z_strat=-1.17, vs_near_net=9, half2_vs_pythag=-2.31 / surprise=6
  - 巨人 2017 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- DeNA 2018: pair34_net=6, upper_half=False, sim_p_upper=0.291, alloc_z_strat=0.207, vs_near_net=11, half2_vs_pythag=+2.27 / surprise=6
  - DeNA 2018 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2012: pair34_net=4, upper_half=False, sim_p_upper=0.425, alloc_z_strat=0.135, vs_near_net=-1, half2_vs_pythag=-3.08 / surprise=4
  - 楽天 2012 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2023: pair34_net=4, upper_half=False, sim_p_upper=0.319, alloc_z_strat=0.951, vs_near_net=0, half2_vs_pythag=+2.68 / surprise=4
  - 楽天 2023 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ロッテ 2019: pair34_net=3, upper_half=False, sim_p_upper=0.666, alloc_z_strat=-1.56, vs_near_net=6, half2_vs_pythag=-2.37 / surprise=3
  - ロッテ 2019 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2023: pair34_net=3, upper_half=False, sim_p_upper=0.738, alloc_z_strat=-0.914, vs_near_net=12, half2_vs_pythag=-3.31 / surprise=3
  - 巨人 2023 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2024: pair34_net=3, upper_half=False, sim_p_upper=0.324, alloc_z_strat=0.465, vs_near_net=8, half2_vs_pythag=+1.79 / surprise=3
  - 広島 2024 は「pair34_net > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9

**待った！判断保留** 逆に判例 10 件（裏の判例も同じ）

- 阪神 2015: pair34_net=-7, upper_half=True, sim_p_upper=0.234, alloc_z_strat=+1.44, vs_near_net=-14, half2_vs_pythag=0.884 / surprise=-7
  - 阪神 2015 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2016: pair34_net=-6, upper_half=True, sim_p_upper=0.560, alloc_z_strat=0.700, vs_near_net=-2, half2_vs_pythag=+2.81 / surprise=-6
  - DeNA 2016 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2017: pair34_net=-6, upper_half=True, sim_p_upper=0.317, alloc_z_strat=+1.71, vs_near_net=-10, half2_vs_pythag=+3.31 / surprise=-6
  - DeNA 2017 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2018: pair34_net=-6, upper_half=True, sim_p_upper=0.817, alloc_z_strat=-1.75, vs_near_net=-8, half2_vs_pythag=-1.52 / surprise=-6
  - 巨人 2018 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2012: pair34_net=-4, upper_half=True, sim_p_upper=0.669, alloc_z_strat=-0.755, vs_near_net=-2, half2_vs_pythag=-3.80 / surprise=-4
  - ソフトバンク 2012 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2023: pair34_net=-4, upper_half=True, sim_p_upper=0.682, alloc_z_strat=-0.183, vs_near_net=-4, half2_vs_pythag=-4.89 / surprise=-4
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- 楽天 2019: pair34_net=-3, upper_half=True, sim_p_upper=0.726, alloc_z_strat=-0.950, vs_near_net=-4, half2_vs_pythag=-4.11 / surprise=-3
  - 楽天 2019 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2023: pair34_net=-3, upper_half=True, sim_p_upper=0.554, alloc_z_strat=+1.27, vs_near_net=-7, half2_vs_pythag=0.569 / surprise=-3
  - DeNA 2023 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2024: pair34_net=-3, upper_half=True, sim_p_upper=0.626, alloc_z_strat=-0.205, vs_near_net=-5, half2_vs_pythag=-2.25 / surprise=-3
  - DeNA 2024 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2021: pair34_net=0, upper_half=True, sim_p_upper=0.696, alloc_z_strat=-0.738, vs_near_net=-4, half2_vs_pythag=-2.26 / surprise=0
  - 巨人 2021 は「upper_half == True」を満たすのに「pair34_net > 0」を満たさない。なぜか？ → H3, H9

## P54: 3位と4位のチームの間では、後半に期待勝利数を上回ったほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 10 件: e-2025, e-2024, d-2013, e-2023, db-2018 ほか
- もし: `half2_vs_pythag > 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] half2_vs_pythag>0 => upper_half==true`（指紋 `5870e30294457a9e`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P55, P56, P57, P58, P59, P66, P67, P68
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。後半の上振れは境目を分けない
- 注記: P53・P55・P56 と兄弟。P56（分布だけ）より強く分けるかを見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 23 回、元の命題に異議あり 23 回（どれかの形に異議あり 23 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 24 | 14 | 0.58 [0.39, 0.76] | +0.82σ（0.271） | 0.50 | 1.17 | 0.202 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.54 | 1.14 | 0.202 | 0 | 判断保留 | 4 |
| 逆 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.46 | 1.17 | 0.202 | 0 | 判断保留 | 4 |
| 裏 | 28 | 16 | 0.57 [0.39, 0.73] | +0.76σ（0.286） | 0.50 | 1.14 | 0.202 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 10 件（対偶の判例も同じ）

- 楽天 2025: half2_vs_pythag=+3.37, upper_half=False, half1_vs_pythag=+3.70, sim_p_upper=0.145, pair34_net=-5 / surprise=+3.37
  - 楽天 2025 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2024: half2_vs_pythag=+3.13, upper_half=False, half1_vs_pythag=+4.70, sim_p_upper=0.104, pair34_net=-2 / surprise=+3.13
  - 楽天 2024 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2013 **(focus)**: half2_vs_pythag=+2.85, upper_half=False, half1_vs_pythag=-1.02, sim_p_upper=0.112, pair34_net=-2 / surprise=+2.85
  - 中日 2013 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2023: half2_vs_pythag=+2.68, upper_half=False, half1_vs_pythag=+2.19, sim_p_upper=0.319, pair34_net=4 / surprise=+2.68
  - 楽天 2023 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- DeNA 2018: half2_vs_pythag=+2.27, upper_half=False, half1_vs_pythag=+1.69, sim_p_upper=0.291, pair34_net=6 / surprise=+2.27
  - DeNA 2018 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 広島 2015: half2_vs_pythag=+1.86, upper_half=False, half1_vs_pythag=-6.54, sim_p_upper=0.786, pair34_net=7 / surprise=+1.86
  - 広島 2015 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 広島 2024: half2_vs_pythag=+1.79, upper_half=False, half1_vs_pythag=-3.18, sim_p_upper=0.324, pair34_net=3 / surprise=+1.79
  - 広島 2024 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 広島 2021: half2_vs_pythag=+1.54, upper_half=False, half1_vs_pythag=-1.35, sim_p_upper=0.272, pair34_net=0 / surprise=+1.54
  - 広島 2021 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ロッテ 2014: half2_vs_pythag=+1.43, upper_half=False, half1_vs_pythag=+2.85, sim_p_upper=0.093, pair34_net=-2 / surprise=+1.43
  - ロッテ 2014 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2014 **(focus)**: half2_vs_pythag=0.388, upper_half=False, half1_vs_pythag=-0.940, sim_p_upper=0.543, pair34_net=-4 / surprise=0.388
  - 中日 2014 は「half2_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3

**待った！判断保留** 逆に判例 12 件（裏の判例も同じ）

- ソフトバンク 2023: half2_vs_pythag=-4.89, upper_half=True, half1_vs_pythag=+2.34, sim_p_upper=0.682, pair34_net=-4 / surprise=-4.89
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- 楽天 2019: half2_vs_pythag=-4.11, upper_half=True, half1_vs_pythag=+1.81, sim_p_upper=0.726, pair34_net=-3 / surprise=-4.11
  - 楽天 2019 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- ソフトバンク 2012: half2_vs_pythag=-3.80, upper_half=True, half1_vs_pythag=+1.28, sim_p_upper=0.669, pair34_net=-4 / surprise=-3.80
  - ソフトバンク 2012 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- 広島 2014: half2_vs_pythag=-3.62, upper_half=True, half1_vs_pythag=+2.63, sim_p_upper=0.813, pair34_net=4 / surprise=-3.62
  - 広島 2014 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- 阪神 2022: half2_vs_pythag=-3.50, upper_half=True, half1_vs_pythag=-6.35, sim_p_upper=0.832, pair34_net=4 / surprise=-3.50
  - 阪神 2022 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- 巨人 2021: half2_vs_pythag=-2.26, upper_half=True, half1_vs_pythag=0.749, sim_p_upper=0.696, pair34_net=0 / surprise=-2.26
  - 巨人 2021 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- DeNA 2024: half2_vs_pythag=-2.25, upper_half=True, half1_vs_pythag=+1.00, sim_p_upper=0.626, pair34_net=-3 / surprise=-2.25
  - DeNA 2024 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- 広島 2013: half2_vs_pythag=-2.00, upper_half=True, half1_vs_pythag=0.793, sim_p_upper=0.601, pair34_net=2 / surprise=-2.00
  - 広島 2013 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- 巨人 2018: half2_vs_pythag=-1.52, upper_half=True, half1_vs_pythag=-5.74, sim_p_upper=0.817, pair34_net=-6 / surprise=-1.52
  - 巨人 2018 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- 楽天 2021: half2_vs_pythag=-1.33, upper_half=True, half1_vs_pythag=0.530, sim_p_upper=0.631, pair34_net=1 / surprise=-1.33
  - 楽天 2021 は「upper_half == True」を満たすのに「half2_vs_pythag > 0」を満たさない。なぜか？ → H3
- ほか 2 件（propositions.jsonl を参照）

## P55: 3位と4位のチームの間では、最長連敗が他球団平均より短いほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 15 件: e-2023, m-2019, e-2012, g-2023, d-2013 ほか
- もし: `max_lose_streak_d < 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] max_lose_streak_d<0 => upper_half==true`（指紋 `717702cdd34004c7`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P54, P56, P57, P58, P59, P66, P67, P68
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。連敗の長さは境目を分けない
- 注記: P56（分布だけ）より強く分けるかを見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 23 回、元の命題に異議あり 23 回（どれかの形に異議あり 23 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 11 | 0.42 [0.26, 0.61] | -0.78σ（0.279） | 0.50 | 0.85 | 0.918 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 11 | 0.42 [0.26, 0.61] | -0.78σ（0.279） | 0.50 | 0.85 | 0.918 | 0 | 判断保留 | 4 |
| 逆 | 26 | 11 | 0.42 [0.26, 0.61] | -0.78σ（0.279） | 0.50 | 0.85 | 0.918 | 0 | 判断保留 | 4 |
| 裏 | 26 | 11 | 0.42 [0.26, 0.61] | -0.78σ（0.279） | 0.50 | 0.85 | 0.918 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 15 件（対偶の判例も同じ）

- 楽天 2023: max_lose_streak_d=-3.80, upper_half=False, max_lose_streak=5, max_win_streak=8, sim_p_upper=0.319 / surprise=-3.80
  - 楽天 2023 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ロッテ 2019: max_lose_streak_d=-2.00, upper_half=False, max_lose_streak=5, max_win_streak=4, sim_p_upper=0.666 / surprise=-2.00
  - ロッテ 2019 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2012: max_lose_streak_d=-1.60, upper_half=False, max_lose_streak=5, max_win_streak=6, sim_p_upper=0.425 / surprise=-1.60
  - 楽天 2012 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 巨人 2023: max_lose_streak_d=-1.60, upper_half=False, max_lose_streak=5, max_win_streak=6, sim_p_upper=0.738 / surprise=-1.60
  - 巨人 2023 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2013 **(focus)**: max_lose_streak_d=-1.20, upper_half=False, max_lose_streak=5, max_win_streak=5, sim_p_upper=0.112 / surprise=-1.20
  - 中日 2013 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2022: max_lose_streak_d=-1.20, upper_half=False, max_lose_streak=5, max_win_streak=10, sim_p_upper=0.329 / surprise=-1.20
  - 楽天 2022 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2025 **(focus)**: max_lose_streak_d=-1.20, upper_half=False, max_lose_streak=5, max_win_streak=7, sim_p_upper=0.177 / surprise=-1.20
  - 中日 2025 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ソフトバンク 2013: max_lose_streak_d=-1.00, upper_half=False, max_lose_streak=5, max_win_streak=5, sim_p_upper=0.885 / surprise=-1.00
  - ソフトバンク 2013 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2014 **(focus)**: max_lose_streak_d=-1.00, upper_half=False, max_lose_streak=6, max_win_streak=4, sim_p_upper=0.543 / surprise=-1.00
  - 中日 2014 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- DeNA 2018: max_lose_streak_d=-1.00, upper_half=False, max_lose_streak=5, max_win_streak=8, sim_p_upper=0.291 / surprise=-1.00
  - DeNA 2018 は「max_lose_streak_d < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ほか 5 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 15 件（裏の判例も同じ）

- ソフトバンク 2023: max_lose_streak_d=+4.60, upper_half=True, max_lose_streak=12, max_win_streak=5, sim_p_upper=0.682 / surprise=+4.60
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- ヤクルト 2012: max_lose_streak_d=+4.00, upper_half=True, max_lose_streak=10, max_win_streak=6, sim_p_upper=0.399 / surprise=+4.00
  - ヤクルト 2012 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- DeNA 2024: max_lose_streak_d=+3.00, upper_half=True, max_lose_streak=9, max_win_streak=7, sim_p_upper=0.626 / surprise=+3.00
  - DeNA 2024 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- 阪神 2022: max_lose_streak_d=+2.80, upper_half=True, max_lose_streak=9, max_win_streak=6, sim_p_upper=0.832 / surprise=+2.80
  - 阪神 2022 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- 広島 2014: max_lose_streak_d=+2.60, upper_half=True, max_lose_streak=9, max_win_streak=6, sim_p_upper=0.813 / surprise=+2.60
  - 広島 2014 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- 楽天 2021: max_lose_streak_d=+2.40, upper_half=True, max_lose_streak=7, max_win_streak=6, sim_p_upper=0.631 / surprise=+2.40
  - 楽天 2021 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- 日本ハム 2014: max_lose_streak_d=+1.80, upper_half=True, max_lose_streak=7, max_win_streak=5, sim_p_upper=0.740 / surprise=+1.80
  - 日本ハム 2014 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- 巨人 2021: max_lose_streak_d=+1.60, upper_half=True, max_lose_streak=7, max_win_streak=8, sim_p_upper=0.696 / surprise=+1.60
  - 巨人 2021 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- 西武 2022: max_lose_streak_d=+1.20, upper_half=True, max_lose_streak=7, max_win_streak=5, sim_p_upper=0.526 / surprise=+1.20
  - 西武 2022 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- ロッテ 2024: max_lose_streak_d=0.600, upper_half=True, max_lose_streak=7, max_win_streak=8, sim_p_upper=0.651 / surprise=0.600
  - ロッテ 2024 は「upper_half == True」を満たすのに「max_lose_streak_d < 0」を満たさない。なぜか？ → H3
- ほか 5 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: max_lose_streak_d=-1.60, upper_half=False, max_lose_streak=4, max_win_streak=5, sim_p_upper=0.705

## P56: 3位と4位のチームの間では、得点・失点の分布から見た A クラスの見込みが 0.5 以上なら3位

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 8 件: h-2013, g-2017, h-2021, c-2015, g-2023 ほか
- もし: `sim_p_upper >= 0.5` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] sim_p_upper>=0.5 => upper_half==true`（指紋 `5cf54bfdfd0df0e3`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P54, P55, P57, P58, P59, P66, P67, P68
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。境目では分布だけでは分けられない
- 注記: 比べるための基準。P53〜P55 がこれより強く分けるなら、分布の外の情報を足している
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 23 回、元の命題に異議あり 23 回（どれかの形に異議あり 23 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 28 | 20 | 0.71 [0.53, 0.85] | +2.27σ（0.018） | 0.50 | 1.43 | 0.001 | 0 | 支持 | 1 |
| 対偶 | 26 | 18 | 0.69 [0.50, 0.83] | +1.96σ（0.038） | 0.46 | 1.50 | 0.001 | 0 | 支持 | 1 |
| 逆 | 26 | 20 | 0.77 [0.58, 0.89] | +2.75σ（0.005） | 0.54 | 1.43 | 0.001 | 0 | 支持 | 1 |
| 裏 | 24 | 18 | 0.75 [0.55, 0.88] | +2.45σ（0.011） | 0.50 | 1.50 | 0.001 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 8 件（対偶の判例も同じ）

- ソフトバンク 2013: sim_p_upper=0.885, upper_half=False, rd=98, alloc_z_strat=-2.21, pair34_net=-6 / surprise=0.885
  - ソフトバンク 2013 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 巨人 2017: sim_p_upper=0.844, upper_half=False, rd=32, alloc_z_strat=-1.17, pair34_net=6 / surprise=0.844
  - 巨人 2017 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- ソフトバンク 2021: sim_p_upper=0.833, upper_half=False, rd=71, alloc_z_strat=-2.48, pair34_net=-1 / surprise=0.833
  - ソフトバンク 2021 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 広島 2015: sim_p_upper=0.786, upper_half=False, rd=32, alloc_z_strat=-1.47, pair34_net=7 / surprise=0.786
  - 広島 2015 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 巨人 2023: sim_p_upper=0.738, upper_half=False, rd=16, alloc_z_strat=-0.914, pair34_net=3 / surprise=0.738
  - 巨人 2023 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 西武 2015: sim_p_upper=0.680, upper_half=False, rd=58, alloc_z_strat=-1.04, pair34_net=-2 / surprise=0.680
  - 西武 2015 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- ロッテ 2019: sim_p_upper=0.666, upper_half=False, rd=31, alloc_z_strat=-1.56, pair34_net=3 / surprise=0.666
  - ロッテ 2019 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 中日 2014 **(focus)**: sim_p_upper=0.543, upper_half=False, rd=-20, alloc_z_strat=-0.752, pair34_net=-4 / surprise=0.543
  - 中日 2014 は「sim_p_upper >= 0.5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3

**異議あり（例外あり）** 逆に判例 6 件（裏の判例も同じ）

- 阪神 2019: sim_p_upper=0.424, upper_half=True, rd=-28, alloc_z_strat=0.651, pair34_net=1 / surprise=0.424
  - 阪神 2019 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H2, H3
- ヤクルト 2012: sim_p_upper=0.399, upper_half=True, rd=-15, alloc_z_strat=+1.53, pair34_net=2 / surprise=0.399
  - ヤクルト 2012 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H2, H3
- DeNA 2017: sim_p_upper=0.317, upper_half=True, rd=-1, alloc_z_strat=+1.71, pair34_net=-6 / surprise=0.317
  - DeNA 2017 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H2, H3
- ロッテ 2015: sim_p_upper=0.262, upper_half=True, rd=-2, alloc_z_strat=+1.33, pair34_net=2 / surprise=0.262
  - ロッテ 2015 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H2, H3
- 阪神 2015: sim_p_upper=0.234, upper_half=True, rd=-85, alloc_z_strat=+1.44, pair34_net=-7 / surprise=0.234
  - 阪神 2015 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H2, H3
- ロッテ 2013: sim_p_upper=0.222, upper_half=True, rd=-12, alloc_z_strat=+1.64, pair34_net=6 / surprise=0.222
  - ロッテ 2013 は「upper_half == True」を満たすのに「sim_p_upper >= 0.5」を満たさない。なぜか？ → H2, H3

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: sim_p_upper=0.840, upper_half=False, rd=42, alloc_z_strat=-2.18, pair34_net=-6
- 楽天 2020: sim_p_upper=0.705, upper_half=False, rd=35, alloc_z_strat=-0.656, pair34_net=-2

## P57: 3位と4位のチームの間では、下位の相手との勝率が相手チームより高いほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 10 件: l-2015, g-2023, c-2021, c-2012, c-2019 ほか
- もし: `pair34_vs_lower_wpct_diff > 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] pair34_vs_lower_wpct_diff>0 => upper_half==true`（指紋 `fbe402419b8b10c1`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P54, P55, P56, P58, P59, P66, P67, P68
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）
- 注記: R12 の平均（.556 対 .523）を見た後に作った命題。同じデータでの判定は確かめではない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 22 回、元の命題に異議あり 22 回（どれかの形に異議あり 22 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.50 | 1.23 | 0.082 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.50 | 1.23 | 0.082 | 0 | 判断保留 | 4 |
| 逆 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.50 | 1.23 | 0.082 | 0 | 判断保留 | 4 |
| 裏 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.50 | 1.23 | 0.082 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 10 件（対偶の判例も同じ）

- 西武 2015: pair34_vs_lower_wpct_diff=0.106, upper_half=False, vs_lower_wpct=0.660, sim_p_upper=0.680, alloc_z_strat=-1.04 / surprise=0.106
  - 西武 2015 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2023: pair34_vs_lower_wpct_diff=0.091, upper_half=False, vs_lower_wpct=0.653, sim_p_upper=0.738, alloc_z_strat=-0.914 / surprise=0.091
  - 巨人 2023 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2021: pair34_vs_lower_wpct_diff=0.077, upper_half=False, vs_lower_wpct=0.609, sim_p_upper=0.272, alloc_z_strat=0.385 / surprise=0.077
  - 広島 2021 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2012: pair34_vs_lower_wpct_diff=0.047, upper_half=False, vs_lower_wpct=0.591, sim_p_upper=0.347, alloc_z_strat=-0.429 / surprise=0.047
  - 広島 2012 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2019: pair34_vs_lower_wpct_diff=0.046, upper_half=False, vs_lower_wpct=0.560, sim_p_upper=0.487, alloc_z_strat=0.232 / surprise=0.046
  - 広島 2019 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2017: pair34_vs_lower_wpct_diff=0.043, upper_half=False, vs_lower_wpct=0.620, sim_p_upper=0.844, alloc_z_strat=-1.17 / surprise=0.043
  - 巨人 2017 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 阪神 2016: pair34_vs_lower_wpct_diff=0.037, upper_half=False, vs_lower_wpct=0.531, sim_p_upper=0.438, alloc_z_strat=-0.594 / surprise=0.037
  - 阪神 2016 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2022: pair34_vs_lower_wpct_diff=0.037, upper_half=False, vs_lower_wpct=0.571, sim_p_upper=0.329, alloc_z_strat=0.284 / surprise=0.037
  - 楽天 2022 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2022: pair34_vs_lower_wpct_diff=0.020, upper_half=False, vs_lower_wpct=0.520, sim_p_upper=0.279, alloc_z_strat=0.669 / surprise=0.020
  - 巨人 2022 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2023: pair34_vs_lower_wpct_diff=0.010, upper_half=False, vs_lower_wpct=0.510, sim_p_upper=0.319, alloc_z_strat=0.951 / surprise=0.010
  - 楽天 2023 は「pair34_vs_lower_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9

**待った！判断保留** 逆に判例 10 件（裏の判例も同じ）

- ロッテ 2015: pair34_vs_lower_wpct_diff=-0.106, upper_half=True, vs_lower_wpct=0.554, sim_p_upper=0.262, alloc_z_strat=+1.33 / surprise=-0.106
  - ロッテ 2015 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2023: pair34_vs_lower_wpct_diff=-0.091, upper_half=True, vs_lower_wpct=0.562, sim_p_upper=0.554, alloc_z_strat=+1.27 / surprise=-0.091
  - DeNA 2023 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2021: pair34_vs_lower_wpct_diff=-0.077, upper_half=True, vs_lower_wpct=0.531, sim_p_upper=0.696, alloc_z_strat=-0.738 / surprise=-0.077
  - 巨人 2021 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- ヤクルト 2012: pair34_vs_lower_wpct_diff=-0.047, upper_half=True, vs_lower_wpct=0.544, sim_p_upper=0.399, alloc_z_strat=+1.53 / surprise=-0.047
  - ヤクルト 2012 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 阪神 2019: pair34_vs_lower_wpct_diff=-0.046, upper_half=True, vs_lower_wpct=0.514, sim_p_upper=0.424, alloc_z_strat=0.651 / surprise=-0.046
  - 阪神 2019 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2017: pair34_vs_lower_wpct_diff=-0.043, upper_half=True, vs_lower_wpct=0.577, sim_p_upper=0.317, alloc_z_strat=+1.71 / surprise=-0.043
  - DeNA 2017 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2016: pair34_vs_lower_wpct_diff=-0.037, upper_half=True, vs_lower_wpct=0.493, sim_p_upper=0.560, alloc_z_strat=0.700 / surprise=-0.037
  - DeNA 2016 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 西武 2022: pair34_vs_lower_wpct_diff=-0.037, upper_half=True, vs_lower_wpct=0.534, sim_p_upper=0.526, alloc_z_strat=0.357 / surprise=-0.037
  - 西武 2022 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 阪神 2022: pair34_vs_lower_wpct_diff=-0.020, upper_half=True, vs_lower_wpct=0.500, sim_p_upper=0.832, alloc_z_strat=-2.14 / surprise=-0.020
  - 阪神 2022 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2023: pair34_vs_lower_wpct_diff=-0.010, upper_half=True, vs_lower_wpct=0.500, sim_p_upper=0.682, alloc_z_strat=-0.183 / surprise=-0.010
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「pair34_vs_lower_wpct_diff > 0」を満たさない。なぜか？ → H3, H9

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: pair34_vs_lower_wpct_diff=0.010, upper_half=False, vs_lower_wpct=0.488, sim_p_upper=0.705, alloc_z_strat=-0.656

## P58: 3位と4位のチームの間では、3位を争う相手（3〜5位）との勝率が相手チームより高いほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 12 件: g-2023, t-2016, db-2018, c-2021, m-2019 ほか
- もし: `pair34_vs_battle_wpct_diff > 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] pair34_vs_battle_wpct_diff>0 => upper_half==true`（指紋 `ab0098dbc830e0d6`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P54, P55, P56, P57, P59, P66, P67, P68
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。争う相手に勝っておくことは境目を分けない
- 注記: ユーザーの見方から。P56（分布だけ、lift 1.43）より大きな lift なら、分布の外の情報を足している
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 22 回、元の命題に異議あり 22 回（どれかの形に異議あり 22 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.50 | 1.08 | 0.391 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.50 | 1.08 | 0.391 | 0 | 判断保留 | 4 |
| 逆 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.50 | 1.08 | 0.391 | 0 | 判断保留 | 4 |
| 裏 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.50 | 1.08 | 0.391 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 12 件（対偶の判例も同じ）

- 巨人 2023: pair34_vs_battle_wpct_diff=0.110, upper_half=False, vs_battle_wpct=0.620, vs_top_wpct=0.286, sim_p_upper=0.738 / surprise=0.110
  - 巨人 2023 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 阪神 2016: pair34_vs_battle_wpct_diff=0.093, upper_half=False, vs_battle_wpct=0.562, vs_top_wpct=0.327, sim_p_upper=0.438 / surprise=0.093
  - 阪神 2016 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- DeNA 2018: pair34_vs_battle_wpct_diff=0.091, upper_half=False, vs_battle_wpct=0.612, vs_top_wpct=0.429, sim_p_upper=0.291 / surprise=0.091
  - DeNA 2018 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2021: pair34_vs_battle_wpct_diff=0.075, upper_half=False, vs_battle_wpct=0.553, vs_top_wpct=0.435, sim_p_upper=0.272 / surprise=0.075
  - 広島 2021 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ロッテ 2019: pair34_vs_battle_wpct_diff=0.073, upper_half=False, vs_battle_wpct=0.562, vs_top_wpct=0.510, sim_p_upper=0.666 / surprise=0.073
  - ロッテ 2019 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2019: pair34_vs_battle_wpct_diff=0.071, upper_half=False, vs_battle_wpct=0.540, vs_top_wpct=0.521, sim_p_upper=0.487 / surprise=0.071
  - 広島 2019 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2017: pair34_vs_battle_wpct_diff=0.070, upper_half=False, vs_battle_wpct=0.592, vs_top_wpct=0.417, sim_p_upper=0.844 / surprise=0.070
  - 巨人 2017 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2024: pair34_vs_battle_wpct_diff=0.060, upper_half=False, vs_battle_wpct=0.580, vs_top_wpct=0.457, sim_p_upper=0.324 / surprise=0.060
  - 広島 2024 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2021: pair34_vs_battle_wpct_diff=0.052, upper_half=False, vs_battle_wpct=0.575, vs_top_wpct=0.500, sim_p_upper=0.833 / surprise=0.052
  - ソフトバンク 2021 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2023: pair34_vs_battle_wpct_diff=0.031, upper_half=False, vs_battle_wpct=0.500, vs_top_wpct=0.440, sim_p_upper=0.319 / surprise=0.031
  - 楽天 2023 は「pair34_vs_battle_wpct_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ほか 2 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 12 件（裏の判例も同じ）

- DeNA 2023: pair34_vs_battle_wpct_diff=-0.110, upper_half=True, vs_battle_wpct=0.510, vs_top_wpct=0.449, sim_p_upper=0.554 / surprise=-0.110
  - DeNA 2023 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2016: pair34_vs_battle_wpct_diff=-0.093, upper_half=True, vs_battle_wpct=0.469, vs_top_wpct=0.531, sim_p_upper=0.560 / surprise=-0.093
  - DeNA 2016 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2018: pair34_vs_battle_wpct_diff=-0.091, upper_half=True, vs_battle_wpct=0.521, vs_top_wpct=0.375, sim_p_upper=0.817 / surprise=-0.091
  - 巨人 2018 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2021: pair34_vs_battle_wpct_diff=-0.075, upper_half=True, vs_battle_wpct=0.478, vs_top_wpct=0.455, sim_p_upper=0.696 / surprise=-0.075
  - 巨人 2021 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 楽天 2019: pair34_vs_battle_wpct_diff=-0.073, upper_half=True, vs_battle_wpct=0.489, vs_top_wpct=0.520, sim_p_upper=0.726 / surprise=-0.073
  - 楽天 2019 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 阪神 2019: pair34_vs_battle_wpct_diff=-0.071, upper_half=True, vs_battle_wpct=0.469, vs_top_wpct=0.531, sim_p_upper=0.424 / surprise=-0.071
  - 阪神 2019 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2017: pair34_vs_battle_wpct_diff=-0.070, upper_half=True, vs_battle_wpct=0.522, vs_top_wpct=0.469, sim_p_upper=0.317 / surprise=-0.070
  - DeNA 2017 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2024: pair34_vs_battle_wpct_diff=-0.060, upper_half=True, vs_battle_wpct=0.520, vs_top_wpct=0.396, sim_p_upper=0.626 / surprise=-0.060
  - DeNA 2024 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- 楽天 2021: pair34_vs_battle_wpct_diff=-0.052, upper_half=True, vs_battle_wpct=0.523, vs_top_wpct=0.432, sim_p_upper=0.631 / surprise=-0.052
  - 楽天 2021 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2023: pair34_vs_battle_wpct_diff=-0.031, upper_half=True, vs_battle_wpct=0.469, vs_top_wpct=0.479, sim_p_upper=0.682 / surprise=-0.031
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「pair34_vs_battle_wpct_diff > 0」を満たさない。なぜか？ → H3, H9
- ほか 2 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: pair34_vs_battle_wpct_diff=0.010, upper_half=False, vs_battle_wpct=0.488, vs_top_wpct=0.511, sim_p_upper=0.705

## P59: 3位と4位のチームの間では、争う相手への重点（争う相手との勝率 − 上の相手との勝率）が相手チームより大きいほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 12 件: t-2016, g-2023, c-2012, g-2017, c-2021 ほか
- もし: `pair34_focus_gap_diff > 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] pair34_focus_gap_diff>0 => upper_half==true`（指紋 `cee51c112590aab8`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P54, P55, P56, P57, P58, P66, P67, P68
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。重点の置き方は境目を分けない
- 注記: ユーザーの見方（1・2位には最悪負けてもいい）をそのまま指標にしたもの
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 22 回、元の命題に異議あり 22 回（どれかの形に異議あり 22 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.50 | 1.08 | 0.391 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.50 | 1.08 | 0.391 | 0 | 判断保留 | 4 |
| 逆 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.50 | 1.08 | 0.391 | 0 | 判断保留 | 4 |
| 裏 | 26 | 14 | 0.54 [0.35, 0.71] | +0.39σ（0.423） | 0.50 | 1.08 | 0.391 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 12 件（対偶の判例も同じ）

- 阪神 2016: pair34_focus_gap_diff=0.297, upper_half=False, focus_gap=0.236, vs_battle_wpct=0.562, vs_top_wpct=0.327 / surprise=0.297
  - 阪神 2016 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2023: pair34_focus_gap_diff=0.273, upper_half=False, focus_gap=0.334, vs_battle_wpct=0.620, vs_top_wpct=0.286 / surprise=0.273
  - 巨人 2023 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2012: pair34_focus_gap_diff=0.124, upper_half=False, focus_gap=0.121, vs_battle_wpct=0.455, vs_top_wpct=0.333 / surprise=0.124
  - 広島 2012 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2017: pair34_focus_gap_diff=0.123, upper_half=False, focus_gap=0.175, vs_battle_wpct=0.592, vs_top_wpct=0.417 / surprise=0.123
  - 巨人 2017 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2021: pair34_focus_gap_diff=0.095, upper_half=False, focus_gap=0.118, vs_battle_wpct=0.553, vs_top_wpct=0.435 / surprise=0.095
  - 広島 2021 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2012: pair34_focus_gap_diff=0.089, upper_half=False, focus_gap=-0.011, vs_battle_wpct=0.489, vs_top_wpct=0.500 / surprise=0.089
  - 楽天 2012 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 西武 2015: pair34_focus_gap_diff=0.087, upper_half=False, focus_gap=0.218, vs_battle_wpct=0.531, vs_top_wpct=0.312 / surprise=0.087
  - 西武 2015 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ロッテ 2019: pair34_focus_gap_diff=0.083, upper_half=False, focus_gap=0.052, vs_battle_wpct=0.562, vs_top_wpct=0.510 / surprise=0.083
  - ロッテ 2019 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2019: pair34_focus_gap_diff=0.080, upper_half=False, focus_gap=0.019, vs_battle_wpct=0.540, vs_top_wpct=0.521 / surprise=0.080
  - 広島 2019 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2023: pair34_focus_gap_diff=0.070, upper_half=False, focus_gap=0.060, vs_battle_wpct=0.500, vs_top_wpct=0.440 / surprise=0.070
  - 楽天 2023 は「pair34_focus_gap_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ほか 2 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 12 件（裏の判例も同じ）

- DeNA 2016: pair34_focus_gap_diff=-0.297, upper_half=True, focus_gap=-0.061, vs_battle_wpct=0.469, vs_top_wpct=0.531 / surprise=-0.297
  - DeNA 2016 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2023: pair34_focus_gap_diff=-0.273, upper_half=True, focus_gap=0.061, vs_battle_wpct=0.510, vs_top_wpct=0.449 / surprise=-0.273
  - DeNA 2023 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- ヤクルト 2012: pair34_focus_gap_diff=-0.124, upper_half=True, focus_gap=-0.003, vs_battle_wpct=0.533, vs_top_wpct=0.537 / surprise=-0.124
  - ヤクルト 2012 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2017: pair34_focus_gap_diff=-0.123, upper_half=True, focus_gap=0.052, vs_battle_wpct=0.522, vs_top_wpct=0.469 / surprise=-0.123
  - DeNA 2017 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2021: pair34_focus_gap_diff=-0.095, upper_half=True, focus_gap=0.024, vs_battle_wpct=0.478, vs_top_wpct=0.455 / surprise=-0.095
  - 巨人 2021 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2012: pair34_focus_gap_diff=-0.089, upper_half=True, focus_gap=-0.100, vs_battle_wpct=0.465, vs_top_wpct=0.565 / surprise=-0.089
  - ソフトバンク 2012 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- ロッテ 2015: pair34_focus_gap_diff=-0.087, upper_half=True, focus_gap=0.131, vs_battle_wpct=0.571, vs_top_wpct=0.440 / surprise=-0.087
  - ロッテ 2015 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- 楽天 2019: pair34_focus_gap_diff=-0.083, upper_half=True, focus_gap=-0.031, vs_battle_wpct=0.489, vs_top_wpct=0.520 / surprise=-0.083
  - 楽天 2019 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- 阪神 2019: pair34_focus_gap_diff=-0.080, upper_half=True, focus_gap=-0.061, vs_battle_wpct=0.469, vs_top_wpct=0.531 / surprise=-0.080
  - 阪神 2019 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2023: pair34_focus_gap_diff=-0.070, upper_half=True, focus_gap=-0.010, vs_battle_wpct=0.469, vs_top_wpct=0.479 / surprise=-0.070
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「pair34_focus_gap_diff > 0」を満たさない。なぜか？ → H3, H9
- ほか 2 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: pair34_focus_gap_diff=0.031, upper_half=False, focus_gap=-0.022, vs_battle_wpct=0.488, vs_top_wpct=0.511

## P60: 得点と失点の組み合わせ方がランダムな基準より不利（alloc_z_strat < −1）なら、下位の相手との勝率が他球団平均より低い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 7 件: l-2015, l-2023, t-2025, g-2017, h-2022 ほか
- もし: `alloc_z_strat < -1` ならば: `vs_lower_wpct_d < 0`
- 識別子: `[all] alloc_z_strat<-1 => vs_lower_wpct_d<0`（指紋 `c63e5dbb054a6801`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 組み合わせ方が不利なチーム・シーズンの4分の1を超えて、下位の相手との勝率が他球団平均以上
- 注記: 下位からの取りこぼしが、R1 の「基準より不利」を別の名前で見ているだけかを確かめる。4つの形すべてで成り立てば、ほぼ同じもの
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 22 回、元の命題に異議あり 22 回（どれかの形に異議あり 22 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 28 | 21 | 0.75 [0.57, 0.87] | +0.00σ（0.600） | 0.47 | 1.58 | 0.001 | 0 | 判断保留 | 4 |
| 対偶 | 82 | 75 | 0.91 [0.83, 0.96] | +3.44σ（0.000） | 0.82 | 1.11 | 0.001 | 0 | 支持 | 1 |
| 逆 | 74 | 21 | 0.28 [0.19, 0.40] | -9.26σ（0.000） | 0.18 | 1.58 | 0.001 | 0 | 修正 | 2 |
| 裏 | 128 | 75 | 0.59 [0.50, 0.67] | -4.29σ（0.000） | 0.53 | 1.11 | 0.001 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 7 件（対偶の判例も同じ）

- 西武 2015: alloc_z_strat=-1.04, vs_lower_wpct_d=0.127, vs_lower_wpct=0.660, rank=4 / surprise=0.127
  - 西武 2015 は「alloc_z_strat < -1」を満たすのに「vs_lower_wpct_d < 0」を満たさない。なぜか？ → H9
- 西武 2023: alloc_z_strat=-1.37, vs_lower_wpct_d=0.093, vs_lower_wpct=0.612, rank=5 / surprise=0.093
  - 西武 2023 は「alloc_z_strat < -1」を満たすのに「vs_lower_wpct_d < 0」を満たさない。なぜか？ → H9
- 阪神 2025: alloc_z_strat=-1.53, vs_lower_wpct_d=0.080, vs_lower_wpct=0.622, rank=1 / surprise=0.080
  - 阪神 2025 は「alloc_z_strat < -1」を満たすのに「vs_lower_wpct_d < 0」を満たさない。なぜか？ → H9
- 巨人 2017: alloc_z_strat=-1.17, vs_lower_wpct_d=0.069, vs_lower_wpct=0.620, rank=4 / surprise=0.069
  - 巨人 2017 は「alloc_z_strat < -1」を満たすのに「vs_lower_wpct_d < 0」を満たさない。なぜか？ → H9
- ソフトバンク 2022: alloc_z_strat=-1.10, vs_lower_wpct_d=0.059, vs_lower_wpct=0.581, rank=1 / surprise=0.059
  - ソフトバンク 2022 は「alloc_z_strat < -1」を満たすのに「vs_lower_wpct_d < 0」を満たさない。なぜか？ → H9
- 巨人 2018: alloc_z_strat=-1.75, vs_lower_wpct_d=0.045, vs_lower_wpct=0.569, rank=3 / surprise=0.045
  - 巨人 2018 は「alloc_z_strat < -1」を満たすのに「vs_lower_wpct_d < 0」を満たさない。なぜか？ → H9
- ソフトバンク 2021: alloc_z_strat=-2.48, vs_lower_wpct_d=0.011, vs_lower_wpct=0.537, rank=4 / surprise=0.011
  - ソフトバンク 2021 は「alloc_z_strat < -1」を満たすのに「vs_lower_wpct_d < 0」を満たさない。なぜか？ → H9

**異議あり（主張が強すぎる）** 逆に判例 53 件（裏の判例も同じ）

- 楽天 2015: alloc_z_strat=0.749, vs_lower_wpct_d=-0.265, vs_lower_wpct=0.333, rank=6 / surprise=-0.265
  - 楽天 2015 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- ロッテ 2025: alloc_z_strat=-0.694, vs_lower_wpct_d=-0.197, vs_lower_wpct=0.396, rank=6 / surprise=-0.197
  - ロッテ 2025 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- 中日 2023 **(focus)**: alloc_z_strat=-0.769, vs_lower_wpct_d=-0.177, vs_lower_wpct=0.408, rank=6 / surprise=-0.177
  - 中日 2023 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- 中日 2016 **(focus)**: alloc_z_strat=-0.968, vs_lower_wpct_d=-0.169, vs_lower_wpct=0.400, rank=6 / surprise=-0.169
  - 中日 2016 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- 中日 2021 **(focus)**: alloc_z_strat=-0.295, vs_lower_wpct_d=-0.159, vs_lower_wpct=0.413, rank=5 / surprise=-0.159
  - 中日 2021 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- 日本ハム 2022: alloc_z_strat=-0.620, vs_lower_wpct_d=-0.159, vs_lower_wpct=0.400, rank=6 / surprise=-0.159
  - 日本ハム 2022 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- ロッテ 2018: alloc_z_strat=-0.042, vs_lower_wpct_d=-0.139, vs_lower_wpct=0.449, rank=5 / surprise=-0.139
  - ロッテ 2018 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- 広島 2025: alloc_z_strat=-0.818, vs_lower_wpct_d=-0.129, vs_lower_wpct=0.447, rank=5 / surprise=-0.129
  - 広島 2025 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- ヤクルト 2024: alloc_z_strat=-0.903, vs_lower_wpct_d=-0.120, vs_lower_wpct=0.438, rank=5 / surprise=-0.120
  - ヤクルト 2024 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- オリックス 2017: alloc_z_strat=-0.091, vs_lower_wpct_d=-0.113, vs_lower_wpct=0.480, rank=4 / surprise=-0.113
  - オリックス 2017 は「vs_lower_wpct_d < 0」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H9
- ほか 43 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: alloc_z_strat=-2.18, vs_lower_wpct_d=0.043, vs_lower_wpct=0.578, rank=4

## P61: 中日は、3位を争う相手との勝率が、上の相手（1・2位）との勝率より低い

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 11 件: d-2024, d-2012, d-2021, d-2014, d-2022 ほか
- もし: `（すべての単位）` ならば: `focus_gap < 0`
- 識別子: `[team=d] * => focus_gap<0`（指紋 `f3c2c579a125c243`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日のシーズンの4分の1を超えて、争う相手との勝率のほうが高い
- 注記: 成り立たなければ「中日は争う相手に負けていた」という見方を弱める
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 22 回、元の命題に異議あり 22 回（どれかの形に異議あり 22 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 2 | 0.15 [0.04, 0.42] | -4.96σ（0.000） | 0.15 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 11 | 0 | 0.00 [0.00, 0.26] | -5.74σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 11 件（対偶の判例も同じ）

- 中日 2024 **(focus)**: focus_gap=0.173, vs_battle_wpct=0.521, vs_top_wpct=0.348, rank=6 / surprise=0.173
  - 中日 2024 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2012 **(focus)**: focus_gap=0.115, vs_battle_wpct=0.591, vs_top_wpct=0.476, rank=2 / surprise=0.115
  - 中日 2012 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2021 **(focus)**: focus_gap=0.110, vs_battle_wpct=0.467, vs_top_wpct=0.357, rank=5 / surprise=0.110
  - 中日 2021 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2014 **(focus)**: focus_gap=0.106, vs_battle_wpct=0.511, vs_top_wpct=0.404, rank=4 / surprise=0.106
  - 中日 2014 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2022 **(focus)**: focus_gap=0.103, vs_battle_wpct=0.520, vs_top_wpct=0.417, rank=6 / surprise=0.103
  - 中日 2022 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2015 **(focus)**: focus_gap=0.052, vs_battle_wpct=0.490, vs_top_wpct=0.438, rank=5 / surprise=0.052
  - 中日 2015 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2019 **(focus)**: focus_gap=0.041, vs_battle_wpct=0.490, vs_top_wpct=0.449, rank=5 / surprise=0.041
  - 中日 2019 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2025 **(focus)**: focus_gap=0.029, vs_battle_wpct=0.449, vs_top_wpct=0.420, rank=4 / surprise=0.029
  - 中日 2025 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2017 **(focus)**: focus_gap=0.029, vs_battle_wpct=0.383, vs_top_wpct=0.354, rank=5 / surprise=0.029
  - 中日 2017 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- 中日 2016 **(focus)**: focus_gap=0.002, vs_battle_wpct=0.419, vs_top_wpct=0.417, rank=6 / surprise=0.002
  - 中日 2016 は「（すべての単位）」を満たすのに「focus_gap < 0」を満たさない。なぜか？ → H3, H9
- ほか 1 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: focus_gap=0.097, vs_battle_wpct=0.532, vs_top_wpct=0.435, rank=3

## P62: 得点した回の大きさが2年以上続けてリーグ下位2位以内なら、B クラス

- **判定: exit 2 異議あり（主張が強すぎる）**（仮: 元の命題と対偶まで） — 逆: 判例 56 件: b-2013, d-2013, s-2013, b-2015, e-2015 ほか
- もし: `inn_size_low_streak >= 2` ならば: `upper_half == False`
- 識別子: `[seasons=2013-2025] inn_size_low_streak>=2 => upper_half==false`（指紋 `0fcce9a33c3def67`）
- 兄弟（範囲と結論が同じ、条件が違う）: P117, P173
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: 続けて低いチーム・シーズンの4分の1を超えて A クラス
- 注記: 中日の値（10年続けて）を見た後に作った条件。P63（中日を除く）が確かめの役割
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 21 回、元の命題に異議あり 0 回（どれかの形に異議あり 21 回）、直近で元の命題に判例がない連続 21 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 16 | 1.00 [0.81, 1.00] | +2.31σ（0.010） | 0.50 | 2.00 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 72 | 72 | 1.00 [0.95, 1.00] | +4.90σ（0.000） | 0.89 | 1.12 | 0.000 | 0 | 支持 | 0 |
| 逆 | 72 | 16 | 0.22 [0.14, 0.33] | -10.34σ（0.000） | 0.11 | 2.00 | 0.000 | 0 | 修正 | 2 |
| 裏 | 128 | 72 | 0.56 [0.48, 0.65] | -4.90σ（0.000） | 0.50 | 1.12 | 0.000 | 0 | 修正 | 2 |

**異議あり（主張が強すぎる）** 逆に判例 56 件（裏の判例も同じ）

- オリックス 2013: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.044, rank=5, sim_p_upper=0.305 / surprise=1
  - オリックス 2013 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 中日 2013 **(focus)**: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.072, rank=4, sim_p_upper=0.112 / surprise=1
  - 中日 2013 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- ヤクルト 2013: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=-0.021, rank=6, sim_p_upper=0.154 / surprise=1
  - ヤクルト 2013 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- オリックス 2015: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=0.014, rank=5, sim_p_upper=0.314 / surprise=1
  - オリックス 2015 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 楽天 2015: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.156, rank=6, sim_p_upper=0.003 / surprise=1
  - 楽天 2015 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 西武 2016: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=-0.069, rank=4, sim_p_upper=0.384 / surprise=1
  - 西武 2016 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 中日 2017 **(focus)**: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.136, rank=5, sim_p_upper=0.020 / surprise=1
  - 中日 2017 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 日本ハム 2017: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=-0.052, rank=5, sim_p_upper=0.026 / surprise=1
  - 日本ハム 2017 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- ロッテ 2017: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.060, rank=6, sim_p_upper=0.002 / surprise=1
  - ロッテ 2017 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- ヤクルト 2017: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=-0.014, rank=6, sim_p_upper=0.000 / surprise=1
  - ヤクルト 2017 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- ほか 46 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: inn_size_low_streak=4, upper_half=True, inn_size_rank=1, inn_dlog_size=-0.096, rank=3, sim_p_upper=0.371

## P63: 中日以外で、得点した回の大きさが2年以上続けてリーグ下位2位以内なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: n=7（min_n=10）、成立率の区間 0.65〜1.00
- もし: `inn_size_low_streak >= 2` ならば: `upper_half == False`
- 識別子: `[seasons=2013-2025, where:team!="d"] inn_size_low_streak>=2 => upper_half==false`（指紋 `3ad97a1dcfc02a61`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025', 'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 132
- 見直す条件（反証）: 中日以外の続けて低いチーム・シーズンの4分の1を超えて A クラス
- 注記: 該当する単位が少ない（数単位）見込み。判断保留は正しい結果としてありうる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 21 回、元の命題に異議あり 0 回（どれかの形に異議あり 21 回）、直近で元の命題に判例がない連続 21 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 7 | 7 | 1.00 [0.65, 1.00] | +1.53σ（0.133） | 0.45 | 2.20 | 0.003 | 0 | 判断保留 | 4 |
| 対偶 | 72 | 72 | 1.00 [0.95, 1.00] | +4.90σ（0.000） | 0.95 | 1.06 | 0.003 | 0 | 支持 | 0 |
| 逆 | 60 | 7 | 0.12 [0.06, 0.22] | -11.33σ（0.000） | 0.05 | 2.20 | 0.003 | 0 | 修正 | 2 |
| 裏 | 125 | 72 | 0.58 [0.49, 0.66] | -4.49σ（0.000） | 0.55 | 1.06 | 0.003 | 0 | 修正 | 2 |

**異議あり（主張が強すぎる）** 逆に判例 53 件（裏の判例も同じ）

- オリックス 2013: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.044, rank=5 / surprise=1
  - オリックス 2013 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- ヤクルト 2013: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=-0.021, rank=6 / surprise=1
  - ヤクルト 2013 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- オリックス 2015: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=0.014, rank=5 / surprise=1
  - オリックス 2015 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 楽天 2015: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.156, rank=6 / surprise=1
  - 楽天 2015 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 西武 2016: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=-0.069, rank=4 / surprise=1
  - 西武 2016 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 日本ハム 2017: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=-0.052, rank=5 / surprise=1
  - 日本ハム 2017 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- ロッテ 2017: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.060, rank=6 / surprise=1
  - ロッテ 2017 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- ヤクルト 2017: inn_size_low_streak=1, upper_half=False, inn_size_rank=2, inn_dlog_size=-0.014, rank=6 / surprise=1
  - ヤクルト 2017 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- DeNA 2018: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.072, rank=4 / surprise=1
  - DeNA 2018 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 楽天 2018: inn_size_low_streak=1, upper_half=False, inn_size_rank=1, inn_dlog_size=-0.096, rank=6 / surprise=1
  - 楽天 2018 は「upper_half == False」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- ほか 43 件（propositions.jsonl を参照）

## P64: 得点が2年以上続けてリーグ5位以下なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: t-2013, t-2019, l-2022, t-2022
- もし: `rf_low_streak >= 2` ならば: `upper_half == False`
- 識別子: `[all] rf_low_streak>=2 => upper_half==false`（指紋 `79cfb4c532f3825c`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P95, P96, P115, P126, P138, P147, P148, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 続けて得点が5位以下のチーム・シーズンの4分の1を超えて A クラス
- 注記: P5（得点5位以下 ⇒ B）に「続けて」を足したもの。P5 と兄弟
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 21 回、元の命題に異議あり 21 回（どれかの形に異議あり 21 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 22 | 0.85 [0.66, 0.94] | +1.13σ（0.184） | 0.50 | 1.69 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 74 | 0.95 [0.88, 0.98] | +4.05σ（0.000） | 0.83 | 1.14 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 22 | 0.28 [0.19, 0.39] | -9.54σ（0.000） | 0.17 | 1.69 | 0.000 | 0 | 修正 | 2 |
| 裏 | 130 | 74 | 0.57 [0.48, 0.65] | -4.76σ（0.000） | 0.50 | 1.14 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 阪神 2013: rf_low_streak=2, upper_half=True, rank_rf=5, rank_ra=1, rank=2, sim_p_upper=0.858 / surprise=2
  - 阪神 2013 は「rf_low_streak >= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2019: rf_low_streak=2, upper_half=True, rank_rf=6, rank_ra=2, rank=3, sim_p_upper=0.424 / surprise=2
  - 阪神 2019 は「rf_low_streak >= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2022: rf_low_streak=2, upper_half=True, rank_rf=5, rank_ra=1, rank=3, sim_p_upper=0.526 / surprise=2
  - 西武 2022 は「rf_low_streak >= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2022: rf_low_streak=2, upper_half=True, rank_rf=5, rank_ra=1, rank=3, sim_p_upper=0.832 / surprise=2
  - 阪神 2022 は「rf_low_streak >= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 56 件（裏の判例も同じ）

- オリックス 2012: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=6, rank=6, sim_p_upper=0.046 / surprise=1
  - オリックス 2012 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- DeNA 2012: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=6, rank=6, sim_p_upper=0.011 / surprise=1
  - DeNA 2012 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 阪神 2012: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=3, rank=5, sim_p_upper=0.312 / surprise=1
  - 阪神 2012 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 中日 2013 **(focus)**: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=4, rank=4, sim_p_upper=0.112 / surprise=1
  - 中日 2013 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 日本ハム 2013: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=6, rank=6, sim_p_upper=0.021 / surprise=1
  - 日本ハム 2013 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- DeNA 2014: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=5, rank=5, sim_p_upper=0.222 / surprise=1
  - DeNA 2014 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 楽天 2014: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=5, rank=6, sim_p_upper=0.074 / surprise=1
  - 楽天 2014 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- ロッテ 2014: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=6, rank=4, sim_p_upper=0.093 / surprise=1
  - ロッテ 2014 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- オリックス 2015: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=2, rank=5, sim_p_upper=0.314 / surprise=1
  - オリックス 2015 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 日本ハム 2017: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=4, rank=5, sim_p_upper=0.026 / surprise=1
  - 日本ハム 2017 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- ほか 46 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rf_low_streak=2, upper_half=True, rank_rf=6, rank_ra=4, rank=3, sim_p_upper=0.371

## P65: 中日以外で、得点が2年以上続けてリーグ5位以下なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: t-2013, t-2019, l-2022, t-2022
- もし: `rf_low_streak >= 2` ならば: `upper_half == False`
- 識別子: `[where:team!="d"] rf_low_streak>=2 => upper_half==false`（指紋 `75e8c9a6e5eb720b`）
- 兄弟（範囲と結論が同じ、条件が違う）: P167
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 143
- 見直す条件（反証）: 中日以外の続けて得点が5位以下のチーム・シーズンの4分の1を超えて A クラス
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 21 回、元の命題に異議あり 21 回（どれかの形に異議あり 21 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 13 | 0.76 [0.53, 0.90] | +0.14σ（0.574） | 0.46 | 1.66 | 0.007 | 0 | 判断保留 | 4 |
| 対偶 | 77 | 73 | 0.95 [0.87, 0.98] | +4.01σ（0.000） | 0.88 | 1.08 | 0.007 | 0 | 支持 | 1 |
| 逆 | 66 | 13 | 0.20 [0.12, 0.31] | -10.38σ（0.000） | 0.12 | 1.66 | 0.007 | 0 | 修正 | 2 |
| 裏 | 126 | 73 | 0.58 [0.49, 0.66] | -4.42σ（0.000） | 0.54 | 1.08 | 0.007 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 阪神 2013: rf_low_streak=2, upper_half=True, rank_rf=5, rank_ra=1, rank=2 / surprise=2
  - 阪神 2013 は「rf_low_streak >= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2019: rf_low_streak=2, upper_half=True, rank_rf=6, rank_ra=2, rank=3 / surprise=2
  - 阪神 2019 は「rf_low_streak >= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2022: rf_low_streak=2, upper_half=True, rank_rf=5, rank_ra=1, rank=3 / surprise=2
  - 西武 2022 は「rf_low_streak >= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2022: rf_low_streak=2, upper_half=True, rank_rf=5, rank_ra=1, rank=3 / surprise=2
  - 阪神 2022 は「rf_low_streak >= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 53 件（裏の判例も同じ）

- オリックス 2012: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=6, rank=6 / surprise=1
  - オリックス 2012 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- DeNA 2012: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=6, rank=6 / surprise=1
  - DeNA 2012 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 阪神 2012: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=3, rank=5 / surprise=1
  - 阪神 2012 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 日本ハム 2013: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=6, rank=6 / surprise=1
  - 日本ハム 2013 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- DeNA 2014: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=5, rank=5 / surprise=1
  - DeNA 2014 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 楽天 2014: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=5, rank=6 / surprise=1
  - 楽天 2014 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- ロッテ 2014: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=6, rank=4 / surprise=1
  - ロッテ 2014 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- オリックス 2015: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=2, rank=5 / surprise=1
  - オリックス 2015 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- 日本ハム 2017: rf_low_streak=1, upper_half=False, rank_rf=5, rank_ra=4, rank=5 / surprise=1
  - 日本ハム 2017 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- ロッテ 2017: rf_low_streak=1, upper_half=False, rank_rf=6, rank_ra=6, rank=6 / surprise=1
  - ロッテ 2017 は「upper_half == False」を満たすのに「rf_low_streak >= 2」を満たさない。なぜか？ → H2
- ほか 43 件（propositions.jsonl を参照）

## P66: 3位と4位のチームの間では、中位の相手（強さの順で3・4番目）に対して見込みより多く勝ったほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 11 件: g-2022, c-2024, e-2023, t-2016, c-2021 ほか
- もし: `pair34_opp_adj_mid_diff > 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] pair34_opp_adj_mid_diff>0 => upper_half==true`（指紋 `f8ad438120930b09`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P54, P55, P56, P57, P58, P59, P67, P68
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。相手の強さを差し引いても、争う相手に勝っておくことは境目を分けない
- 注記: R13 の P58（相手の強さを差し引いていない版）の作り直し。P56（lift 1.43）と比べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 20 回、元の命題に異議あり 20 回（どれかの形に異議あり 20 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 15 | 0.58 [0.39, 0.74] | +0.78σ（0.279） | 0.50 | 1.15 | 0.203 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 15 | 0.58 [0.39, 0.74] | +0.78σ（0.279） | 0.50 | 1.15 | 0.203 | 0 | 判断保留 | 4 |
| 逆 | 26 | 15 | 0.58 [0.39, 0.74] | +0.78σ（0.279） | 0.50 | 1.15 | 0.203 | 0 | 判断保留 | 4 |
| 裏 | 26 | 15 | 0.58 [0.39, 0.74] | +0.78σ（0.279） | 0.50 | 1.15 | 0.203 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 11 件（対偶の判例も同じ）

- 巨人 2022: pair34_opp_adj_mid_diff=+7.25, upper_half=False, opp_adj_mid=0.723, opp_adj_top=+2.12, opp_adj_low=-0.402, sim_p_upper=0.279 / surprise=+7.25
  - 巨人 2022 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2024: pair34_opp_adj_mid_diff=+5.79, upper_half=False, opp_adj_mid=+5.20, opp_adj_top=0.576, opp_adj_low=-7.62, sim_p_upper=0.324 / surprise=+5.79
  - 広島 2024 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2023: pair34_opp_adj_mid_diff=+3.26, upper_half=False, opp_adj_mid=+2.13, opp_adj_top=+4.76, opp_adj_low=-2.23, sim_p_upper=0.319 / surprise=+3.26
  - 楽天 2023 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 阪神 2016: pair34_opp_adj_mid_diff=+3.06, upper_half=False, opp_adj_mid=-1.54, opp_adj_top=+2.21, opp_adj_low=-0.676, sim_p_upper=0.438 / surprise=+3.06
  - 阪神 2016 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2021: pair34_opp_adj_mid_diff=+1.86, upper_half=False, opp_adj_mid=+3.51, opp_adj_top=0.014, opp_adj_low=+1.83, sim_p_upper=0.272 / surprise=+1.86
  - 広島 2021 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2021: pair34_opp_adj_mid_diff=+1.80, upper_half=False, opp_adj_mid=0.064, opp_adj_top=-0.528, opp_adj_low=-4.54, sim_p_upper=0.833 / surprise=+1.80
  - ソフトバンク 2021 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 中日 2025 **(focus)**: pair34_opp_adj_mid_diff=+1.53, upper_half=False, opp_adj_mid=-1.63, opp_adj_top=+3.70, opp_adj_low=-0.817, sim_p_upper=0.177 / surprise=+1.53
  - 中日 2025 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2017: pair34_opp_adj_mid_diff=+1.52, upper_half=False, opp_adj_mid=0.974, opp_adj_top=-1.17, opp_adj_low=+1.49, sim_p_upper=0.844 / surprise=+1.52
  - 巨人 2017 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 中日 2014 **(focus)**: pair34_opp_adj_mid_diff=0.945, upper_half=False, opp_adj_mid=+1.78, opp_adj_top=-4.58, opp_adj_low=-1.15, sim_p_upper=0.543 / surprise=0.945
  - 中日 2014 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ロッテ 2014: pair34_opp_adj_mid_diff=0.334, upper_half=False, opp_adj_mid=+1.58, opp_adj_top=+4.55, opp_adj_low=-2.65, sim_p_upper=0.093 / surprise=0.334
  - ロッテ 2014 は「pair34_opp_adj_mid_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ほか 1 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 11 件（裏の判例も同じ）

- 阪神 2022: pair34_opp_adj_mid_diff=-7.25, upper_half=True, opp_adj_mid=-6.53, opp_adj_top=-5.07, opp_adj_low=-2.71, sim_p_upper=0.832 / surprise=-7.25
  - 阪神 2022 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2024: pair34_opp_adj_mid_diff=-5.79, upper_half=True, opp_adj_mid=-0.594, opp_adj_top=-3.07, opp_adj_low=0.094, sim_p_upper=0.626 / surprise=-5.79
  - DeNA 2024 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2023: pair34_opp_adj_mid_diff=-3.26, upper_half=True, opp_adj_mid=-1.14, opp_adj_top=-0.299, opp_adj_low=-4.02, sim_p_upper=0.682 / surprise=-3.26
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2016: pair34_opp_adj_mid_diff=-3.06, upper_half=True, opp_adj_mid=-4.61, opp_adj_top=+6.78, opp_adj_low=-1.26, sim_p_upper=0.560 / surprise=-3.06
  - DeNA 2016 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2021: pair34_opp_adj_mid_diff=-1.86, upper_half=True, opp_adj_mid=+1.66, opp_adj_top=0.011, opp_adj_low=-3.48, sim_p_upper=0.696 / surprise=-1.86
  - 巨人 2021 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- 楽天 2021: pair34_opp_adj_mid_diff=-1.80, upper_half=True, opp_adj_mid=-1.74, opp_adj_top=+2.12, opp_adj_low=-1.03, sim_p_upper=0.631 / surprise=-1.80
  - 楽天 2021 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2025: pair34_opp_adj_mid_diff=-1.53, upper_half=True, opp_adj_mid=-3.15, opp_adj_top=+3.44, opp_adj_low=+2.80, sim_p_upper=0.750 / surprise=-1.53
  - 巨人 2025 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2017: pair34_opp_adj_mid_diff=-1.52, upper_half=True, opp_adj_mid=-0.542, opp_adj_top=+2.72, opp_adj_low=0.757, sim_p_upper=0.317 / surprise=-1.52
  - DeNA 2017 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- 広島 2014: pair34_opp_adj_mid_diff=-0.945, upper_half=True, opp_adj_mid=0.832, opp_adj_top=0.056, opp_adj_low=+2.33, sim_p_upper=0.813 / surprise=-0.945
  - 広島 2014 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- 日本ハム 2014: pair34_opp_adj_mid_diff=-0.334, upper_half=True, opp_adj_mid=+1.24, opp_adj_top=+1.89, opp_adj_low=-1.25, sim_p_upper=0.740 / surprise=-0.334
  - 日本ハム 2014 は「upper_half == True」を満たすのに「pair34_opp_adj_mid_diff > 0」を満たさない。なぜか？ → H3, H9
- ほか 1 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: pair34_opp_adj_mid_diff=0.225, upper_half=False, opp_adj_mid=-3.16, opp_adj_top=+1.00, opp_adj_low=-2.92, sim_p_upper=0.840

## P67: 3位と4位のチームの間では、最も弱い相手に対して見込みより多く勝ったほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 11 件: c-2012, c-2021, l-2015, e-2025, e-2022 ほか
- もし: `pair34_opp_adj_low_diff > 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] pair34_opp_adj_low_diff>0 => upper_half==true`（指紋 `0d956ca476fb7a99`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P54, P55, P56, P57, P58, P59, P66, P68
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。弱い相手からの取りこぼしは境目を分けない
- 注記: R12・R13 の「下位の相手との勝率」の、相手の強さを差し引いた版
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 20 回、元の命題に異議あり 20 回（どれかの形に異議あり 20 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 15 | 0.58 [0.39, 0.74] | +0.78σ（0.279） | 0.50 | 1.15 | 0.203 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 15 | 0.58 [0.39, 0.74] | +0.78σ（0.279） | 0.50 | 1.15 | 0.203 | 0 | 判断保留 | 4 |
| 逆 | 26 | 15 | 0.58 [0.39, 0.74] | +0.78σ（0.279） | 0.50 | 1.15 | 0.203 | 0 | 判断保留 | 4 |
| 裏 | 26 | 15 | 0.58 [0.39, 0.74] | +0.78σ（0.279） | 0.50 | 1.15 | 0.203 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 11 件（対偶の判例も同じ）

- 広島 2012: pair34_opp_adj_low_diff=+7.18, upper_half=False, opp_adj_low=+4.96, opp_adj_mid=-6.55, sim_p_upper=0.347 / surprise=+7.18
  - 広島 2012 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 広島 2021: pair34_opp_adj_low_diff=+5.31, upper_half=False, opp_adj_low=+1.83, opp_adj_mid=+3.51, sim_p_upper=0.272 / surprise=+5.31
  - 広島 2021 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 西武 2015: pair34_opp_adj_low_diff=+4.95, upper_half=False, opp_adj_low=+3.07, opp_adj_mid=-9.01, sim_p_upper=0.680 / surprise=+4.95
  - 西武 2015 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2025: pair34_opp_adj_low_diff=+3.73, upper_half=False, opp_adj_low=+3.29, opp_adj_mid=-1.68, sim_p_upper=0.145 / surprise=+3.73
  - 楽天 2025 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2022: pair34_opp_adj_low_diff=+3.20, upper_half=False, opp_adj_low=+2.86, opp_adj_mid=-3.51, sim_p_upper=0.329 / surprise=+3.20
  - 楽天 2022 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2022: pair34_opp_adj_low_diff=+2.31, upper_half=False, opp_adj_low=-0.402, opp_adj_mid=0.723, sim_p_upper=0.279 / surprise=+2.31
  - 巨人 2022 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2023: pair34_opp_adj_low_diff=+1.79, upper_half=False, opp_adj_low=-2.23, opp_adj_mid=+2.13, sim_p_upper=0.319 / surprise=+1.79
  - 楽天 2023 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 楽天 2012: pair34_opp_adj_low_diff=+1.04, upper_half=False, opp_adj_low=+1.25, opp_adj_mid=-5.03, sim_p_upper=0.425 / surprise=+1.04
  - 楽天 2012 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- DeNA 2018: pair34_opp_adj_low_diff=0.841, upper_half=False, opp_adj_low=-5.75, opp_adj_mid=+1.53, sim_p_upper=0.291 / surprise=0.841
  - DeNA 2018 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- 巨人 2017: pair34_opp_adj_low_diff=0.728, upper_half=False, opp_adj_low=+1.49, opp_adj_mid=0.974, sim_p_upper=0.844 / surprise=0.728
  - 巨人 2017 は「pair34_opp_adj_low_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3, H9
- ほか 1 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 11 件（裏の判例も同じ）

- ヤクルト 2012: pair34_opp_adj_low_diff=-7.18, upper_half=True, opp_adj_low=-2.22, opp_adj_mid=0.445, sim_p_upper=0.399 / surprise=-7.18
  - ヤクルト 2012 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2021: pair34_opp_adj_low_diff=-5.31, upper_half=True, opp_adj_low=-3.48, opp_adj_mid=+1.66, sim_p_upper=0.696 / surprise=-5.31
  - 巨人 2021 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- ロッテ 2015: pair34_opp_adj_low_diff=-4.95, upper_half=True, opp_adj_low=-1.89, opp_adj_mid=0.738, sim_p_upper=0.262 / surprise=-4.95
  - ロッテ 2015 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- オリックス 2025: pair34_opp_adj_low_diff=-3.73, upper_half=True, opp_adj_low=-0.440, opp_adj_mid=+3.60, sim_p_upper=0.575 / surprise=-3.73
  - オリックス 2025 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- 西武 2022: pair34_opp_adj_low_diff=-3.20, upper_half=True, opp_adj_low=-0.347, opp_adj_mid=-0.015, sim_p_upper=0.526 / surprise=-3.20
  - 西武 2022 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- 阪神 2022: pair34_opp_adj_low_diff=-2.31, upper_half=True, opp_adj_low=-2.71, opp_adj_mid=-6.53, sim_p_upper=0.832 / surprise=-2.31
  - 阪神 2022 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2023: pair34_opp_adj_low_diff=-1.79, upper_half=True, opp_adj_low=-4.02, opp_adj_mid=-1.14, sim_p_upper=0.682 / surprise=-1.79
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2012: pair34_opp_adj_low_diff=-1.04, upper_half=True, opp_adj_low=0.213, opp_adj_mid=-2.50, sim_p_upper=0.669 / surprise=-1.04
  - ソフトバンク 2012 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- 巨人 2018: pair34_opp_adj_low_diff=-0.841, upper_half=True, opp_adj_low=-6.59, opp_adj_mid=+6.65, sim_p_upper=0.817 / surprise=-0.841
  - 巨人 2018 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- DeNA 2017: pair34_opp_adj_low_diff=-0.728, upper_half=True, opp_adj_low=0.757, opp_adj_mid=-0.542, sim_p_upper=0.317 / surprise=-0.728
  - DeNA 2017 は「upper_half == True」を満たすのに「pair34_opp_adj_low_diff > 0」を満たさない。なぜか？ → H3, H9
- ほか 1 件（propositions.jsonl を参照）

## P68: 3位と4位のチームの間では、リーグ内の相手すべてに対して見込みより多く勝ったほうが3位

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 10 件: g-2022, e-2023, db-2018, c-2021, d-2013 ほか
- もし: `pair34_opp_adj_total_diff > 0` ならば: `upper_half == True`
- 識別子: `[where:rank<=4, where:rank>=3] pair34_opp_adj_total_diff>0 => upper_half==true`（指紋 `513d849d09520cde`）
- 兄弟（範囲と結論が同じ、条件が違う）: P53, P54, P55, P56, P57, P58, P59, P66, P67
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '>=', 'value': 3}, {'col': 'rank', 'op': '<=', 'value': 4}]} / 単位数: 52
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）
- 注記: wins_vs_pythag とかなり重なる指標。相手ごとに見込みを変えた分だけ違う
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 20 回、元の命題に異議あり 20 回（どれかの形に異議あり 20 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.50 | 1.23 | 0.082 | 0 | 判断保留 | 4 |
| 対偶 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.50 | 1.23 | 0.082 | 0 | 判断保留 | 4 |
| 逆 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.50 | 1.23 | 0.082 | 0 | 判断保留 | 4 |
| 裏 | 26 | 16 | 0.62 [0.43, 0.78] | +1.18σ（0.163） | 0.50 | 1.23 | 0.082 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 10 件（対偶の判例も同じ）

- 巨人 2022: pair34_opp_adj_total_diff=+16.75, upper_half=False, opp_adj_total=+2.44, wins_vs_pythag=+2.61, sim_p_upper=0.279 / surprise=+16.75
  - 巨人 2022 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2023: pair34_opp_adj_total_diff=+10.11, upper_half=False, opp_adj_total=+4.66, wins_vs_pythag=+4.68, sim_p_upper=0.319 / surprise=+10.11
  - 楽天 2023 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- DeNA 2018: pair34_opp_adj_total_diff=+9.98, upper_half=False, opp_adj_total=+2.85, wins_vs_pythag=+3.92, sim_p_upper=0.291 / surprise=+9.98
  - DeNA 2018 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 広島 2021: pair34_opp_adj_total_diff=+7.17, upper_half=False, opp_adj_total=+5.36, wins_vs_pythag=0.845, sim_p_upper=0.272 / surprise=+7.17
  - 広島 2021 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2013 **(focus)**: pair34_opp_adj_total_diff=+3.13, upper_half=False, opp_adj_total=+1.34, wins_vs_pythag=+1.84, sim_p_upper=0.112 / surprise=+3.13
  - 中日 2013 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 広島 2024: pair34_opp_adj_total_diff=+1.73, upper_half=False, opp_adj_total=-1.84, wins_vs_pythag=-0.394, sim_p_upper=0.324 / surprise=+1.73
  - 広島 2024 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ロッテ 2014: pair34_opp_adj_total_diff=+1.59, upper_half=False, opp_adj_total=+3.48, wins_vs_pythag=+4.29, sim_p_upper=0.093 / surprise=+1.59
  - ロッテ 2014 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2025: pair34_opp_adj_total_diff=+1.35, upper_half=False, opp_adj_total=+5.85, wins_vs_pythag=+7.06, sim_p_upper=0.145 / surprise=+1.35
  - 楽天 2025 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ロッテ 2019: pair34_opp_adj_total_diff=+1.22, upper_half=False, opp_adj_total=-1.32, wins_vs_pythag=-3.65, sim_p_upper=0.666 / surprise=+1.22
  - ロッテ 2019 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 広島 2019: pair34_opp_adj_total_diff=0.014, upper_half=False, opp_adj_total=+5.05, wins_vs_pythag=+1.07, sim_p_upper=0.487 / surprise=0.014
  - 広島 2019 は「pair34_opp_adj_total_diff > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3

**待った！判断保留** 逆に判例 10 件（裏の判例も同じ）

- 阪神 2022: pair34_opp_adj_total_diff=-16.75, upper_half=True, opp_adj_total=-14.31, wins_vs_pythag=-9.93, sim_p_upper=0.832 / surprise=-16.75
  - 阪神 2022 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- ソフトバンク 2023: pair34_opp_adj_total_diff=-10.11, upper_half=True, opp_adj_total=-5.45, wins_vs_pythag=-2.56, sim_p_upper=0.682 / surprise=-10.11
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- 巨人 2018: pair34_opp_adj_total_diff=-9.98, upper_half=True, opp_adj_total=-7.14, wins_vs_pythag=-7.25, sim_p_upper=0.817 / surprise=-9.98
  - 巨人 2018 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- 巨人 2021: pair34_opp_adj_total_diff=-7.17, upper_half=True, opp_adj_total=-1.81, wins_vs_pythag=-1.63, sim_p_upper=0.696 / surprise=-7.17
  - 巨人 2021 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- 広島 2013: pair34_opp_adj_total_diff=-3.13, upper_half=True, opp_adj_total=-1.78, wins_vs_pythag=-1.85, sim_p_upper=0.601 / surprise=-3.13
  - 広島 2013 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- DeNA 2024: pair34_opp_adj_total_diff=-1.73, upper_half=True, opp_adj_total=-3.57, wins_vs_pythag=-1.37, sim_p_upper=0.626 / surprise=-1.73
  - DeNA 2024 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- 日本ハム 2014: pair34_opp_adj_total_diff=-1.59, upper_half=True, opp_adj_total=+1.88, wins_vs_pythag=-0.164, sim_p_upper=0.740 / surprise=-1.59
  - 日本ハム 2014 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- オリックス 2025: pair34_opp_adj_total_diff=-1.35, upper_half=True, opp_adj_total=+4.50, wins_vs_pythag=+6.13, sim_p_upper=0.575 / surprise=-1.35
  - オリックス 2025 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- 楽天 2019: pair34_opp_adj_total_diff=-1.22, upper_half=True, opp_adj_total=-2.54, wins_vs_pythag=-2.34, sim_p_upper=0.726 / surprise=-1.22
  - 楽天 2019 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3
- 阪神 2019: pair34_opp_adj_total_diff=-0.014, upper_half=True, opp_adj_total=+5.04, wins_vs_pythag=+3.68, sim_p_upper=0.424 / surprise=-0.014
  - 阪神 2019 は「upper_half == True」を満たすのに「pair34_opp_adj_total_diff > 0」を満たさない。なぜか？ → H3

## P69: 中日は、中位の相手（強さの順で3・4番目）に対して見込みより勝てていない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: d-2024, d-2022, d-2014, d-2021, d-2016 ほか
- もし: `（すべての単位）` ならば: `opp_adj_mid < 0`
- 識別子: `[team=d] * => opp_adj_mid<0`（指紋 `7b6ffad351a67c9d`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日のシーズンの4分の1を超えて、中位の相手に見込み以上に勝っている
- 注記: R13 の P61（相手の強さを差し引いていない版、不成立）の作り直し
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 20 回、元の命題に異議あり 20 回（どれかの形に異議あり 20 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 7 | 0.54 [0.29, 0.77] | -1.76σ（0.080） | 0.54 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 6 | 0 | 0.00 [0.00, 0.39] | -4.24σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- 中日 2024 **(focus)**: opp_adj_mid=+7.52, opp_adj_top=-0.357, opp_adj_low=+2.10, opp_adj_total=+9.26, rank=6 / surprise=+7.52
  - 中日 2024 は「（すべての単位）」を満たすのに「opp_adj_mid < 0」を満たさない。なぜか？ → H3, H9
- 中日 2022 **(focus)**: opp_adj_mid=+6.18, opp_adj_top=+8.14, opp_adj_low=-6.79, opp_adj_total=+7.53, rank=6 / surprise=+6.18
  - 中日 2022 は「（すべての単位）」を満たすのに「opp_adj_mid < 0」を満たさない。なぜか？ → H3, H9
- 中日 2014 **(focus)**: opp_adj_mid=+1.78, opp_adj_top=-4.58, opp_adj_low=-1.15, opp_adj_total=-3.96, rank=4 / surprise=+1.78
  - 中日 2014 は「（すべての単位）」を満たすのに「opp_adj_mid < 0」を満たさない。なぜか？ → H3, H9
- 中日 2021 **(focus)**: opp_adj_mid=+1.65, opp_adj_top=-1.40, opp_adj_low=-1.71, opp_adj_total=-1.47, rank=5 / surprise=+1.65
  - 中日 2021 は「（すべての単位）」を満たすのに「opp_adj_mid < 0」を満たさない。なぜか？ → H3, H9
- 中日 2016 **(focus)**: opp_adj_mid=+1.50, opp_adj_top=-0.892, opp_adj_low=-4.71, opp_adj_total=-4.10, rank=6 / surprise=+1.50
  - 中日 2016 は「（すべての単位）」を満たすのに「opp_adj_mid < 0」を満たさない。なぜか？ → H3, H9
- 中日 2018 **(focus)**: opp_adj_mid=0.929, opp_adj_top=0.606, opp_adj_low=-2.87, opp_adj_total=-1.33, rank=5 / surprise=0.929
  - 中日 2018 は「（すべての単位）」を満たすのに「opp_adj_mid < 0」を満たさない。なぜか？ → H3, H9

## P70: 中日は、強い相手（自分との試合を除いた強さで上位2チーム）に対して、見込みより得点が少ない

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 9 件: d-2012, d-2017, d-2025, d-2015, d-2016 ほか
- もし: `（すべての単位）` ならば: `opp_rf_gap_top < 0`
- 識別子: `[team=d] * => opp_rf_gap_top<0`（指紋 `7bddb94c701f5bf0`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日のシーズンの4分の1を超えて、強い相手に見込み以上に得点している
- 注記: 基準に中日自身の得点力が入っているので、「もともと得点が少ない」は差し引かれている。P71 と組で読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 19 回、元の命題に異議あり 19 回（どれかの形に異議あり 19 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 4 | 0.31 [0.13, 0.58] | -3.68σ（0.001） | 0.31 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 9 | 0 | 0.00 [0.00, 0.30] | -5.20σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 9 件（対偶の判例も同じ）

- 中日 2012 **(focus)**: opp_rf_gap_top=+26.19, opp_ra_gap_top=+33.20, opp_conv_top=-0.869, opp_adj_top=+7.89, rank=2 / surprise=+26.19
  - 中日 2012 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2017 **(focus)**: opp_rf_gap_top=+24.00, opp_ra_gap_top=+8.68, opp_conv_top=-0.239, opp_adj_top=+3.73, rank=5 / surprise=+24.00
  - 中日 2017 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2025 **(focus)**: opp_rf_gap_top=+22.17, opp_ra_gap_top=-4.90, opp_conv_top=0.509, opp_adj_top=+3.70, rank=4 / surprise=+22.17
  - 中日 2025 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2015 **(focus)**: opp_rf_gap_top=+18.40, opp_ra_gap_top=+30.31, opp_conv_top=0.096, opp_adj_top=+6.49, rank=5 / surprise=+18.40
  - 中日 2015 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2016 **(focus)**: opp_rf_gap_top=+12.29, opp_ra_gap_top=-17.62, opp_conv_top=-2.22, opp_adj_top=-0.892, rank=6 / surprise=+12.29
  - 中日 2016 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2023 **(focus)**: opp_rf_gap_top=+12.11, opp_ra_gap_top=+20.78, opp_conv_top=-0.037, opp_adj_top=+4.87, rank=6 / surprise=+12.11
  - 中日 2023 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2013 **(focus)**: opp_rf_gap_top=+11.11, opp_ra_gap_top=+23.21, opp_conv_top=-0.219, opp_adj_top=+3.55, rank=4 / surprise=+11.11
  - 中日 2013 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2022 **(focus)**: opp_rf_gap_top=+8.16, opp_ra_gap_top=+25.15, opp_conv_top=+4.33, opp_adj_top=+8.14, rank=6 / surprise=+8.16
  - 中日 2022 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2024 **(focus)**: opp_rf_gap_top=+3.97, opp_ra_gap_top=-22.39, opp_conv_top=0.788, opp_adj_top=-0.357, rank=6 / surprise=+3.97
  - 中日 2024 は「（すべての単位）」を満たすのに「opp_rf_gap_top < 0」を満たさない。なぜか？ → H2, H5, H6

## P71: 中日は、強い相手（自分との試合を除いた強さで上位2チーム）に対して、見込みより失点が多い

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 9 件: d-2012, d-2021, d-2015, d-2019, d-2022 ほか
- もし: `（すべての単位）` ならば: `opp_ra_gap_top < 0`
- 識別子: `[team=d] * => opp_ra_gap_top<0`（指紋 `eb8480c855c2ada0`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日のシーズンの4分の1を超えて、強い相手に見込み以下の失点に抑えている
- 注記: P70 と組で読む。片方だけ成り立つなら、強い相手との差はその側にある
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 19 回、元の命題に異議あり 19 回（どれかの形に異議あり 19 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 4 | 0.31 [0.13, 0.58] | -3.68σ（0.001） | 0.31 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 9 | 0 | 0.00 [0.00, 0.30] | -5.20σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 9 件（対偶の判例も同じ）

- 中日 2012 **(focus)**: opp_ra_gap_top=+33.20, opp_rf_gap_top=+26.19, opp_conv_top=-0.869, opp_adj_top=+7.89, rank=2 / surprise=+33.20
  - 中日 2012 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: opp_ra_gap_top=+32.91, opp_rf_gap_top=-28.07, opp_conv_top=-1.97, opp_adj_top=-1.40, rank=5 / surprise=+32.91
  - 中日 2021 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2
- 中日 2015 **(focus)**: opp_ra_gap_top=+30.31, opp_rf_gap_top=+18.40, opp_conv_top=0.096, opp_adj_top=+6.49, rank=5 / surprise=+30.31
  - 中日 2015 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: opp_ra_gap_top=+28.07, opp_rf_gap_top=-50.63, opp_conv_top=-0.813, opp_adj_top=-3.70, rank=5 / surprise=+28.07
  - 中日 2019 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2
- 中日 2022 **(focus)**: opp_ra_gap_top=+25.15, opp_rf_gap_top=+8.16, opp_conv_top=+4.33, opp_adj_top=+8.14, rank=6 / surprise=+25.15
  - 中日 2022 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2
- 中日 2013 **(focus)**: opp_ra_gap_top=+23.21, opp_rf_gap_top=+11.11, opp_conv_top=-0.219, opp_adj_top=+3.55, rank=4 / surprise=+23.21
  - 中日 2013 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2
- 中日 2023 **(focus)**: opp_ra_gap_top=+20.78, opp_rf_gap_top=+12.11, opp_conv_top=-0.037, opp_adj_top=+4.87, rank=6 / surprise=+20.78
  - 中日 2023 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2
- 中日 2017 **(focus)**: opp_ra_gap_top=+8.68, opp_rf_gap_top=+24.00, opp_conv_top=-0.239, opp_adj_top=+3.73, rank=5 / surprise=+8.68
  - 中日 2017 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2
- 中日 2014 **(focus)**: opp_ra_gap_top=+3.48, opp_rf_gap_top=-19.86, opp_conv_top=-2.57, opp_adj_top=-4.58, rank=4 / surprise=+3.48
  - 中日 2014 は「（すべての単位）」を満たすのに「opp_ra_gap_top < 0」を満たさない。なぜか？ → H2

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: opp_ra_gap_top=+49.92, opp_rf_gap_top=-5.15, opp_conv_top=+3.76, opp_adj_top=+8.38, rank=3

## P72: 強い相手に見込みより負けたチーム・シーズンでは、その差は失点の側より得点の側で大きい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 26 件: db-2013, s-2021, l-2017, e-2022, e-2018 ほか
- もし: `opp_adj_top < 0` ならば: `opp_top_rf_minus_ra < 0`
- 識別子: `[all] opp_adj_top<0 => opp_top_rf_minus_ra<0`（指紋 `93a1a3ff831bb3fc`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 強い相手に見込みより負けたチーム・シーズンの半数以上で、失点の側の差のほうが大きい
- 注記: 全球団での一般の形。中日（P70・P71）がこの一般の形と同じかを見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 19 回、元の命題に異議あり 19 回（どれかの形に異議あり 19 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 57 | 31 | 0.54 [0.42, 0.67] | +0.66σ（0.298） | 0.49 | 1.10 | 0.216 | 0 | 判断保留 | 4 |
| 対偶 | 79 | 53 | 0.67 [0.56, 0.76] | +3.04σ（0.002） | 0.63 | 1.06 | 0.216 | 0 | 支持 | 1 |
| 逆 | 77 | 31 | 0.40 [0.30, 0.51] | -1.71σ（0.055） | 0.37 | 1.10 | 0.216 | 0 | 判断保留 | 4 |
| 裏 | 99 | 53 | 0.54 [0.44, 0.63] | +0.70σ（0.273） | 0.51 | 1.06 | 0.216 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 26 件（対偶の判例も同じ）

- DeNA 2013: opp_adj_top=-0.806, opp_top_rf_minus_ra=+89.95, opp_rf_gap_top=+40.29, opp_ra_gap_top=-49.65, opp_conv_top=-1.57 / surprise=+89.95
  - DeNA 2013 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- ヤクルト 2021: opp_adj_top=-5.46, opp_top_rf_minus_ra=+84.95, opp_rf_gap_top=+28.53, opp_ra_gap_top=-56.41, opp_conv_top=-2.51 / surprise=+84.95
  - ヤクルト 2021 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- 西武 2017: opp_adj_top=-0.286, opp_top_rf_minus_ra=+79.41, opp_rf_gap_top=+33.30, opp_ra_gap_top=-46.12, opp_conv_top=0.616 / surprise=+79.41
  - 西武 2017 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- 楽天 2022: opp_adj_top=-0.027, opp_top_rf_minus_ra=+74.36, opp_rf_gap_top=+31.12, opp_ra_gap_top=-43.23, opp_conv_top=0.888 / surprise=+74.36
  - 楽天 2022 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- 楽天 2018: opp_adj_top=-5.43, opp_top_rf_minus_ra=+73.43, opp_rf_gap_top=+17.75, opp_ra_gap_top=-55.68, opp_conv_top=-2.43 / surprise=+73.43
  - 楽天 2018 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- ロッテ 2018: opp_adj_top=-0.080, opp_top_rf_minus_ra=+62.10, opp_rf_gap_top=+46.48, opp_ra_gap_top=-15.62, opp_conv_top=-3.99 / surprise=+62.10
  - ロッテ 2018 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- 巨人 2018: opp_adj_top=-7.19, opp_top_rf_minus_ra=+59.85, opp_rf_gap_top=+22.56, opp_ra_gap_top=-37.29, opp_conv_top=-5.84 / surprise=+59.85
  - 巨人 2018 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- DeNA 2012: opp_adj_top=-1.85, opp_top_rf_minus_ra=+53.92, opp_rf_gap_top=+21.95, opp_ra_gap_top=-31.97, opp_conv_top=-2.75 / surprise=+53.92
  - DeNA 2012 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- ソフトバンク 2021: opp_adj_top=-0.528, opp_top_rf_minus_ra=+39.92, opp_rf_gap_top=+31.99, opp_ra_gap_top=-7.92, opp_conv_top=-2.93 / surprise=+39.92
  - ソフトバンク 2021 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- ロッテ 2012: opp_adj_top=-1.15, opp_top_rf_minus_ra=+39.48, opp_rf_gap_top=+22.58, opp_ra_gap_top=-16.90, opp_conv_top=-2.01 / surprise=+39.48
  - ロッテ 2012 は「opp_adj_top < 0」を満たすのに「opp_top_rf_minus_ra < 0」を満たさない。なぜか？ → H2, H5
- ほか 16 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 46 件（裏の判例も同じ）

- ロッテ 2014: opp_adj_top=+4.55, opp_top_rf_minus_ra=-94.15, opp_rf_gap_top=-30.43, opp_ra_gap_top=+63.72, opp_conv_top=+2.10 / surprise=-94.15
  - ロッテ 2014 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- 広島 2021: opp_adj_top=0.014, opp_top_rf_minus_ra=-64.01, opp_rf_gap_top=-29.35, opp_ra_gap_top=+34.67, opp_conv_top=-0.028 / surprise=-64.01
  - 広島 2021 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- オリックス 2013: opp_adj_top=0.585, opp_top_rf_minus_ra=-54.64, opp_rf_gap_top=-31.77, opp_ra_gap_top=+22.87, opp_conv_top=+2.28 / surprise=-54.64
  - オリックス 2013 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- 広島 2015: opp_adj_top=+3.24, opp_top_rf_minus_ra=-52.78, opp_rf_gap_top=-5.56, opp_ra_gap_top=+47.22, opp_conv_top=-3.81 / surprise=-52.78
  - 広島 2015 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- 広島 2019: opp_adj_top=+7.29, opp_top_rf_minus_ra=-52.56, opp_rf_gap_top=-13.39, opp_ra_gap_top=+39.17, opp_conv_top=+4.37 / surprise=-52.56
  - 広島 2019 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- 巨人 2024: opp_adj_top=+2.48, opp_top_rf_minus_ra=-46.62, opp_rf_gap_top=-17.75, opp_ra_gap_top=+28.86, opp_conv_top=+1.29 / surprise=-46.62
  - 巨人 2024 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- DeNA 2018: opp_adj_top=+7.07, opp_top_rf_minus_ra=-42.07, opp_rf_gap_top=0.897, opp_ra_gap_top=+42.97, opp_conv_top=+2.28 / surprise=-42.07
  - DeNA 2018 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- 巨人 2019: opp_adj_top=+1.53, opp_top_rf_minus_ra=-39.79, opp_rf_gap_top=-5.89, opp_ra_gap_top=+33.89, opp_conv_top=-1.93 / surprise=-39.79
  - 巨人 2019 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- 阪神 2014: opp_adj_top=+2.35, opp_top_rf_minus_ra=-38.86, opp_rf_gap_top=-25.49, opp_ra_gap_top=+13.37, opp_conv_top=+4.01 / surprise=-38.86
  - 阪神 2014 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- オリックス 2021: opp_adj_top=0.498, opp_top_rf_minus_ra=-37.63, opp_rf_gap_top=-25.88, opp_ra_gap_top=+11.76, opp_conv_top=+2.08 / surprise=-37.63
  - オリックス 2021 は「opp_top_rf_minus_ra < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H2, H5
- ほか 36 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 阪神 2020: opp_adj_top=-2.00, opp_top_rf_minus_ra=+8.64, opp_rf_gap_top=-10.05, opp_ra_gap_top=-18.69, opp_conv_top=+1.40
- 日本ハム 2020: opp_adj_top=-3.46, opp_top_rf_minus_ra=0.951, opp_rf_gap_top=-26.23, opp_ra_gap_top=-27.18, opp_conv_top=+1.76

## P73: 強い相手に見込みより負けたチーム・シーズンでは、点の差では説明できない負けもある（opp_conv_top < 0）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 16 件: db-2023, g-2015, b-2018, m-2016, l-2014 ほか
- もし: `opp_adj_top < 0` ならば: `opp_conv_top < 0`
- 識別子: `[all] opp_adj_top<0 => opp_conv_top<0`（指紋 `f8a28c4d0985db0c`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 強い相手に見込みより負けたチーム・シーズンの半数以上で、点の差どおり以上に勝っている
- 注記: 点の差を勝ち負けに変える部分（R1 の組み合わせ方と近い）が、強い相手との差にどれだけ入っているかを見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 19 回、元の命題に異議あり 19 回（どれかの形に異議あり 19 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 57 | 41 | 0.72 [0.59, 0.82] | +3.31σ（0.001） | 0.48 | 1.50 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 81 | 65 | 0.80 [0.70, 0.87] | +5.44σ（0.000） | 0.63 | 1.26 | 0.000 | 0 | 支持 | 1 |
| 逆 | 75 | 41 | 0.55 [0.43, 0.65] | +0.81σ（0.244） | 0.37 | 1.50 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 99 | 65 | 0.66 [0.56, 0.74] | +3.12σ（0.001） | 0.52 | 1.26 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 16 件（対偶の判例も同じ）

- DeNA 2023: opp_adj_top=-1.50, opp_conv_top=+4.09, opp_rf_gap_top=-37.95, opp_ra_gap_top=-3.82, alloc_z_strat=+1.27 / surprise=+4.09
  - DeNA 2023 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- 巨人 2015: opp_adj_top=-4.06, opp_conv_top=+3.53, opp_rf_gap_top=-62.44, opp_ra_gap_top=+16.20, alloc_z_strat=0.257 / surprise=+3.53
  - 巨人 2015 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- オリックス 2018: opp_adj_top=-3.60, opp_conv_top=+2.25, opp_rf_gap_top=-33.83, opp_ra_gap_top=-21.03, alloc_z_strat=-0.847 / surprise=+2.25
  - オリックス 2018 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- ロッテ 2016: opp_adj_top=-3.63, opp_conv_top=+2.25, opp_rf_gap_top=-16.75, opp_ra_gap_top=-42.02, alloc_z_strat=0.415 / surprise=+2.25
  - ロッテ 2016 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- 西武 2014: opp_adj_top=-0.745, opp_conv_top=+2.21, opp_rf_gap_top=-21.46, opp_ra_gap_top=-5.21, alloc_z_strat=-0.938 / surprise=+2.21
  - 西武 2014 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- 西武 2023: opp_adj_top=-3.21, opp_conv_top=+2.16, opp_rf_gap_top=-19.10, opp_ra_gap_top=-21.13, alloc_z_strat=-1.37 / surprise=+2.16
  - 西武 2023 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- 広島 2012: opp_adj_top=-0.621, opp_conv_top=+1.32, opp_rf_gap_top=-7.73, opp_ra_gap_top=-3.99, alloc_z_strat=-0.429 / surprise=+1.32
  - 広島 2012 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- 楽天 2022: opp_adj_top=-0.027, opp_conv_top=0.888, opp_rf_gap_top=+31.12, opp_ra_gap_top=-43.23, alloc_z_strat=0.284 / surprise=0.888
  - 楽天 2022 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- オリックス 2014: opp_adj_top=-4.28, opp_conv_top=0.867, opp_rf_gap_top=-23.90, opp_ra_gap_top=-18.29, alloc_z_strat=-0.632 / surprise=0.867
  - オリックス 2014 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- 中日 2024 **(focus)**: opp_adj_top=-0.357, opp_conv_top=0.788, opp_rf_gap_top=+3.97, opp_ra_gap_top=-22.39, alloc_z_strat=0.459 / surprise=0.788
  - 中日 2024 は「opp_adj_top < 0」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9
- ほか 6 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 34 件（裏の判例も同じ）

- 広島 2015: opp_adj_top=+3.24, opp_conv_top=-3.81, opp_rf_gap_top=-5.56, opp_ra_gap_top=+47.22, alloc_z_strat=-1.47 / surprise=-3.81
  - 広島 2015 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- 西武 2016: opp_adj_top=+2.51, opp_conv_top=-3.57, opp_rf_gap_top=+28.21, opp_ra_gap_top=+24.77, alloc_z_strat=-1.51 / surprise=-3.57
  - 西武 2016 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- 楽天 2019: opp_adj_top=+1.55, opp_conv_top=-3.07, opp_rf_gap_top=+39.46, opp_ra_gap_top=+10.03, alloc_z_strat=-0.950 / surprise=-3.07
  - 楽天 2019 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- 日本ハム 2019: opp_adj_top=0.741, opp_conv_top=-2.71, opp_rf_gap_top=+44.24, opp_ra_gap_top=-14.42, alloc_z_strat=-0.391 / surprise=-2.71
  - 日本ハム 2019 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- 日本ハム 2016: opp_adj_top=+5.93, opp_conv_top=-2.51, opp_rf_gap_top=+39.03, opp_ra_gap_top=+35.94, alloc_z_strat=0.528 / surprise=-2.51
  - 日本ハム 2016 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- ロッテ 2017: opp_adj_top=+1.40, opp_conv_top=-2.42, opp_rf_gap_top=+8.84, opp_ra_gap_top=+33.00, alloc_z_strat=-0.300 / surprise=-2.42
  - ロッテ 2017 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- 日本ハム 2014: opp_adj_top=+1.89, opp_conv_top=-2.29, opp_rf_gap_top=+13.33, opp_ra_gap_top=+21.34, alloc_z_strat=-0.215 / surprise=-2.29
  - 日本ハム 2014 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- ソフトバンク 2018: opp_adj_top=+2.61, opp_conv_top=-2.25, opp_rf_gap_top=+34.71, opp_ra_gap_top=+11.24, alloc_z_strat=-0.039 / surprise=-2.25
  - ソフトバンク 2018 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- 巨人 2019: opp_adj_top=+1.53, opp_conv_top=-1.93, opp_rf_gap_top=-5.89, opp_ra_gap_top=+33.89, alloc_z_strat=-0.240 / surprise=-1.93
  - 巨人 2019 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- ロッテ 2015: opp_adj_top=+3.74, opp_conv_top=-1.88, opp_rf_gap_top=+10.73, opp_ra_gap_top=+41.92, alloc_z_strat=+1.33 / surprise=-1.88
  - ロッテ 2015 は「opp_conv_top < 0」を満たすのに「opp_adj_top < 0」を満たさない。なぜか？ → H3, H9
- ほか 24 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 日本ハム 2020: opp_adj_top=-3.46, opp_conv_top=+1.76, opp_rf_gap_top=-26.23, opp_ra_gap_top=-27.18, alloc_z_strat=-0.772
- 阪神 2020: opp_adj_top=-2.00, opp_conv_top=+1.40, opp_rf_gap_top=-10.05, opp_ra_gap_top=-18.69, alloc_z_strat=+1.05

## P74: 中日は、強い相手に対して、得点が見込みより（同じ年・同じリーグの全球団の平均と比べて）少ない

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 7 件: d-2012, d-2025, d-2013, d-2015, d-2017 ほか
- もし: `（すべての単位）` ならば: `opp_rf_gap_top_c < 0`
- 識別子: `[team=d] * => opp_rf_gap_top_c<0`（指紋 `060afe0a89a3002e`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 親: P70（変更: 見込みの式が相手のグループで偏っていた（R16 の自分への異議）ので、同じ年・同じリーグの全球団の平均を引いた値に変えた。R16 の読み直しを見た後の言い直し）
- 見直す条件（反証）: 中日のシーズンの4分の1を超えて、平均を引いた得点の差が 0 以上
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 17 回、元の命題に異議あり 17 回（どれかの形に異議あり 17 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 6 | 0.46 [0.23, 0.71] | -2.40σ（0.024） | 0.46 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 7 | 0 | 0.00 [0.00, 0.35] | -4.58σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 7 件（対偶の判例も同じ）

- 中日 2012 **(focus)**: opp_rf_gap_top_c=+21.56, opp_ra_gap_top_c=+20.99, opp_env_gap_top_c=0.569, opp_adj_top=+7.89, rank=2 / surprise=+21.56
  - 中日 2012 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2025 **(focus)**: opp_rf_gap_top_c=+20.69, opp_ra_gap_top_c=-0.900, opp_env_gap_top_c=+21.59, opp_adj_top=+3.70, rank=4 / surprise=+20.69
  - 中日 2025 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2013 **(focus)**: opp_rf_gap_top_c=+17.07, opp_ra_gap_top_c=+12.01, opp_env_gap_top_c=+5.06, opp_adj_top=+3.55, rank=4 / surprise=+17.07
  - 中日 2013 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2015 **(focus)**: opp_rf_gap_top_c=+16.85, opp_ra_gap_top_c=+14.71, opp_env_gap_top_c=+2.14, opp_adj_top=+6.49, rank=5 / surprise=+16.85
  - 中日 2015 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2017 **(focus)**: opp_rf_gap_top_c=+6.45, opp_ra_gap_top_c=+5.10, opp_env_gap_top_c=+1.36, opp_adj_top=+3.73, rank=5 / surprise=+6.45
  - 中日 2017 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2024 **(focus)**: opp_rf_gap_top_c=+5.74, opp_ra_gap_top_c=-23.83, opp_env_gap_top_c=+29.57, opp_adj_top=-0.357, rank=6 / surprise=+5.74
  - 中日 2024 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H2, H5, H6
- 中日 2023 **(focus)**: opp_rf_gap_top_c=+4.16, opp_ra_gap_top_c=+14.47, opp_env_gap_top_c=-10.31, opp_adj_top=+4.87, rank=6 / surprise=+4.16
  - 中日 2023 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H2, H5, H6

## P75: 中日は、強い相手に対して、失点が見込みより（同じ年・同じリーグの全球団の平均と比べて）多い

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 9 件: d-2021, d-2022, d-2012, d-2015, d-2023 ほか
- もし: `（すべての単位）` ならば: `opp_ra_gap_top_c < 0`
- 識別子: `[team=d] * => opp_ra_gap_top_c<0`（指紋 `75599a09f83038f3`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 親: P71（変更: P74 と同じ変更（平均を引いた値））
- 見直す条件（反証）: 中日のシーズンの4分の1を超えて、平均を引いた失点の差が 0 以上
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 17 回、元の命題に異議あり 17 回（どれかの形に異議あり 17 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 4 | 0.31 [0.13, 0.58] | -3.68σ（0.001） | 0.31 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 9 | 0 | 0.00 [0.00, 0.30] | -5.20σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 9 件（対偶の判例も同じ）

- 中日 2021 **(focus)**: opp_ra_gap_top_c=+33.55, opp_rf_gap_top_c=-29.28, opp_env_gap_top_c=-62.82, opp_adj_top=-1.40, rank=5 / surprise=+33.55
  - 中日 2021 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2
- 中日 2022 **(focus)**: opp_ra_gap_top_c=+29.50, opp_rf_gap_top_c=-4.60, opp_env_gap_top_c=-34.10, opp_adj_top=+8.14, rank=6 / surprise=+29.50
  - 中日 2022 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2
- 中日 2012 **(focus)**: opp_ra_gap_top_c=+20.99, opp_rf_gap_top_c=+21.56, opp_env_gap_top_c=0.569, opp_adj_top=+7.89, rank=2 / surprise=+20.99
  - 中日 2012 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2
- 中日 2015 **(focus)**: opp_ra_gap_top_c=+14.71, opp_rf_gap_top_c=+16.85, opp_env_gap_top_c=+2.14, opp_adj_top=+6.49, rank=5 / surprise=+14.71
  - 中日 2015 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2
- 中日 2023 **(focus)**: opp_ra_gap_top_c=+14.47, opp_rf_gap_top_c=+4.16, opp_env_gap_top_c=-10.31, opp_adj_top=+4.87, rank=6 / surprise=+14.47
  - 中日 2023 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: opp_ra_gap_top_c=+13.07, opp_rf_gap_top_c=-57.34, opp_env_gap_top_c=-70.42, opp_adj_top=-3.70, rank=5 / surprise=+13.07
  - 中日 2019 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2
- 中日 2013 **(focus)**: opp_ra_gap_top_c=+12.01, opp_rf_gap_top_c=+17.07, opp_env_gap_top_c=+5.06, opp_adj_top=+3.55, rank=4 / surprise=+12.01
  - 中日 2013 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2
- 中日 2017 **(focus)**: opp_ra_gap_top_c=+5.10, opp_rf_gap_top_c=+6.45, opp_env_gap_top_c=+1.36, opp_adj_top=+3.73, rank=5 / surprise=+5.10
  - 中日 2017 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2
- 中日 2018 **(focus)**: opp_ra_gap_top_c=+2.04, opp_rf_gap_top_c=-13.55, opp_env_gap_top_c=-15.59, opp_adj_top=0.606, rank=5 / surprise=+2.04
  - 中日 2018 は「（すべての単位）」を満たすのに「opp_ra_gap_top_c < 0」を満たさない。なぜか？ → H2

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: opp_ra_gap_top_c=+47.09, opp_rf_gap_top_c=-7.24, opp_env_gap_top_c=-54.34, opp_adj_top=+8.38, rank=3

## P76: 得失点差がプラスなのに B クラスだったチームは、強い相手から（平均と比べて）得点できていない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 7 件: h-2013, h-2021, e-2022, l-2016, m-2019 ほか
- もし: `（すべての単位）` ならば: `opp_rf_gap_top_c < 0`
- 識別子: `[where:rd>0, where:upper_half==false] * => opp_rf_gap_top_c<0`（指紋 `2f4e9983d6f91430`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rd', 'op': '>', 'value': 0}, {'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 12
- 親: P74（変更: 中日だけから、2019年と同じ状況（得失点差がプラスなのに B クラス）のチーム・シーズン全体に広げた。2019年は作るきっかけなので held-out から除く）
- 見直す条件（反証）: held-out（中日 2019 を除く）で、得点の差が負のチーム・シーズンが半数以下
- 注記: 2019年の道筋。2014年の道筋（P77・P78）と両方成り立つ必要はない
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 17 回、元の命題に異議あり 17 回（どれかの形に異議あり 17 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 5 | 0.42 [0.19, 0.68] | -0.58σ（0.387） | 0.42 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 7 | 0 | 0.00 [0.00, 0.35] | -2.65σ（0.008） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 7 件（対偶の判例も同じ）

- ソフトバンク 2013: opp_rf_gap_top_c=+47.56, opp_ra_gap_top_c=-18.67, opp_env_gap_top_c=+66.22, opp_adj_top=+3.37, sim_p_upper=0.885 / surprise=+47.56
  - ソフトバンク 2013 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3, H5
- ソフトバンク 2021: opp_rf_gap_top_c=+31.91, opp_ra_gap_top_c=-13.27, opp_env_gap_top_c=+45.18, opp_adj_top=-0.528, sim_p_upper=0.833 / surprise=+31.91
  - ソフトバンク 2021 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3, H5
- 楽天 2022: opp_rf_gap_top_c=+21.55, opp_ra_gap_top_c=-39.92, opp_env_gap_top_c=+61.47, opp_adj_top=-0.027, sim_p_upper=0.329 / surprise=+21.55
  - 楽天 2022 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3, H5
- 西武 2016: opp_rf_gap_top_c=+20.08, opp_ra_gap_top_c=+23.78, opp_env_gap_top_c=-3.70, opp_adj_top=+2.51, sim_p_upper=0.384 / surprise=+20.08
  - 西武 2016 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3, H5
- ロッテ 2019: opp_rf_gap_top_c=+18.81, opp_ra_gap_top_c=-4.97, opp_env_gap_top_c=+23.78, opp_adj_top=+7.48, sim_p_upper=0.666 / surprise=+18.81
  - ロッテ 2019 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3, H5
- 広島 2022: opp_rf_gap_top_c=+18.80, opp_ra_gap_top_c=-7.54, opp_env_gap_top_c=+26.34, opp_adj_top=+1.05, sim_p_upper=0.319 / surprise=+18.80
  - 広島 2022 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3, H5
- 西武 2015: opp_rf_gap_top_c=+14.29, opp_ra_gap_top_c=+1.17, opp_env_gap_top_c=+13.11, opp_adj_top=-0.110, sim_p_upper=0.680 / surprise=+14.29
  - 西武 2015 は「（すべての単位）」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3, H5

**きっかけ以外での判定**（作り直しのきっかけ d-2019 を除く）: n=11 成立=4 成立率=0.36 [0.15, 0.65] → **判断保留** / 判例: h-2013, h-2021, e-2022, l-2016, m-2019, c-2022, l-2015

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: opp_rf_gap_top_c=+30.41, opp_ra_gap_top_c=-2.71, opp_env_gap_top_c=+33.12, opp_adj_top=+1.00, sim_p_upper=0.840
- 楽天 2020: opp_rf_gap_top_c=+21.49, opp_ra_gap_top_c=-1.94, opp_env_gap_top_c=+23.43, opp_adj_top=+4.08, sim_p_upper=0.705

## P77: 4位で、得点・失点の分布から見た A クラスの見込みが 0.5 以上だったチームは、3位との直接対決で負け越している

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: c-2015, g-2017, m-2019, g-2023
- もし: `（すべての単位）` ならば: `pair34_net < 0`
- 識別子: `[where:rank==4, where:sim_p_upper>=0.5] * => pair34_net<0`（指紋 `fa3304ecfe62d142`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '==', 'value': 4}, {'col': 'sim_p_upper', 'op': '>=', 'value': 0.5}]} / 単位数: 8
- 親: P53（変更: 3位と4位すべてから、2014年と同じ状況（4位で、分布の見込みが 0.5 以上）に絞り、結論を「直接対決で負け越し」にした。2014年は作るきっかけなので held-out から除く）
- 見直す条件（反証）: held-out（中日 2014 を除く）で、直接対決で負け越したチームが半数以下
- 注記: 2014年の道筋その1
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 17 回、元の命題に異議あり 17 回（どれかの形に異議あり 17 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 8 | 4 | 0.50 [0.22, 0.78] | +0.00σ（0.637） | 0.50 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | -2.00σ（0.062） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 広島 2015: pair34_net=7, sim_p_upper=0.786, opp_conv_top=-3.81, opp_adj_top=+3.24, vs_lower_wpct=0.388 / surprise=7
  - 広島 2015 は「（すべての単位）」を満たすのに「pair34_net < 0」を満たさない。なぜか？ → H3, H9
- 巨人 2017: pair34_net=6, sim_p_upper=0.844, opp_conv_top=-1.49, opp_adj_top=-1.17, vs_lower_wpct=0.620 / surprise=6
  - 巨人 2017 は「（すべての単位）」を満たすのに「pair34_net < 0」を満たさない。なぜか？ → H3, H9
- ロッテ 2019: pair34_net=3, sim_p_upper=0.666, opp_conv_top=+2.54, opp_adj_top=+7.48, vs_lower_wpct=0.469 / surprise=3
  - ロッテ 2019 は「（すべての単位）」を満たすのに「pair34_net < 0」を満たさない。なぜか？ → H3, H9
- 巨人 2023: pair34_net=3, sim_p_upper=0.738, opp_conv_top=-3.65, opp_adj_top=-1.85, vs_lower_wpct=0.653 / surprise=3
  - 巨人 2023 は「（すべての単位）」を満たすのに「pair34_net < 0」を満たさない。なぜか？ → H3, H9

**きっかけ以外での判定**（作り直しのきっかけ d-2014 を除く）: n=7 成立=3 成立率=0.43 [0.16, 0.75] → **判断保留** / 判例: c-2015, g-2017, m-2019, g-2023

## P78: 4位で、得点・失点の分布から見た A クラスの見込みが 0.5 以上だったチームは、強い相手との試合で点の差どおりに勝てていない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: m-2019
- もし: `（すべての単位）` ならば: `opp_conv_top < 0`
- 識別子: `[where:rank==4, where:sim_p_upper>=0.5] * => opp_conv_top<0`（指紋 `d1472747f653df69`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rank', 'op': '==', 'value': 4}, {'col': 'sim_p_upper', 'op': '>=', 'value': 0.5}]} / 単位数: 8
- 親: P73（変更: 全球団から、2014年と同じ状況（4位で、分布の見込みが 0.5 以上）に絞った。2014年は作るきっかけなので held-out から除く）
- 見直す条件（反証）: held-out（中日 2014 を除く）で、点の差どおり以上に勝っていたチームが半数以上
- 注記: 2014年の道筋その2
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 17 回、元の命題に異議あり 17 回（どれかの形に異議あり 17 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 8 | 7 | 0.88 [0.53, 0.98] | +2.12σ（0.035） | 0.88 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.00σ（0.500） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- ロッテ 2019: opp_conv_top=+2.54, sim_p_upper=0.666, pair34_net=3, opp_adj_top=+7.48, alloc_z_strat=-1.56 / surprise=+2.54
  - ロッテ 2019 は「（すべての単位）」を満たすのに「opp_conv_top < 0」を満たさない。なぜか？ → H3, H9

**きっかけ以外での判定**（作り直しのきっかけ d-2014 を除く）: n=7 成立=6 成立率=0.86 [0.49, 0.97] → **判断保留** / 判例: m-2019

## P79: 強い相手に対して得点が（平均と比べて）見込みより少なければ、失点も見込みより少ない（鏡の形）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 27 件: b-2018, db-2023, f-2017, h-2019, h-2024 ほか
- もし: `opp_rf_gap_top_c < 0` ならば: `opp_ra_gap_top_c > 0`
- 識別子: `[all] opp_rf_gap_top_c<0 => opp_ra_gap_top_c>0`（指紋 `15ba1e891532908e`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）。鏡の形は中日の数年に偶然出たもので、全球団の連動ではない
- 注記: 中日の 2019・2021・2022年で見た形を全球団で確かめる。成り立てば、連動の正体は試合全体の点の多さ（env）の側
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 17 回、元の命題に異議あり 17 回（どれかの形に異議あり 17 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 79 | 52 | 0.66 [0.55, 0.75] | +2.81σ（0.003） | 0.53 | 1.25 | 0.001 | 0 | 支持 | 1 |
| 対偶 | 74 | 47 | 0.64 [0.52, 0.74] | +2.32σ（0.013） | 0.49 | 1.29 | 0.001 | 0 | 支持 | 1 |
| 逆 | 82 | 52 | 0.63 [0.53, 0.73] | +2.43σ（0.010） | 0.51 | 1.25 | 0.001 | 0 | 支持 | 1 |
| 裏 | 77 | 47 | 0.61 [0.50, 0.71] | +1.94σ（0.034） | 0.47 | 1.29 | 0.001 | 0 | 判断保留 | 4 |

**異議あり（例外あり）** 元の命題に判例 27 件（対偶の判例も同じ）

- オリックス 2018: opp_rf_gap_top_c=-45.75, opp_ra_gap_top_c=-9.19, opp_net_gap_top_c=-54.94 / surprise=-36.55
  - オリックス 2018 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- DeNA 2023: opp_rf_gap_top_c=-45.90, opp_ra_gap_top_c=-10.12, opp_net_gap_top_c=-56.02 / surprise=-35.78
  - DeNA 2023 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- 日本ハム 2017: opp_rf_gap_top_c=-28.20, opp_ra_gap_top_c=-1.07, opp_net_gap_top_c=-29.26 / surprise=-27.13
  - 日本ハム 2017 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- ソフトバンク 2019: opp_rf_gap_top_c=-24.34, opp_ra_gap_top_c=-0.278, opp_net_gap_top_c=-24.61 / surprise=-24.06
  - ソフトバンク 2019 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- ソフトバンク 2024: opp_rf_gap_top_c=-4.72, opp_ra_gap_top_c=-26.61, opp_net_gap_top_c=-31.33 / surprise=+21.89
  - ソフトバンク 2024 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- ヤクルト 2018: opp_rf_gap_top_c=-11.81, opp_ra_gap_top_c=-31.43, opp_net_gap_top_c=-43.24 / surprise=+19.62
  - ヤクルト 2018 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- ロッテ 2016: opp_rf_gap_top_c=-24.89, opp_ra_gap_top_c=-43.00, opp_net_gap_top_c=-67.89 / surprise=+18.11
  - ロッテ 2016 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- ロッテ 2024: opp_rf_gap_top_c=-37.24, opp_ra_gap_top_c=-19.26, opp_net_gap_top_c=-56.51 / surprise=-17.98
  - ロッテ 2024 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- 中日 2014 **(focus)**: opp_rf_gap_top_c=-16.71, opp_ra_gap_top_c=-1.45, opp_net_gap_top_c=-18.16 / surprise=-15.26
  - 中日 2014 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- 西武 2013: opp_rf_gap_top_c=-5.92, opp_ra_gap_top_c=-19.75, opp_net_gap_top_c=-25.67 / surprise=+13.82
  - 西武 2013 は「opp_rf_gap_top_c < 0」を満たすのに「opp_ra_gap_top_c > 0」を満たさない。なぜか？ → H3
- ほか 17 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 30 件（裏の判例も同じ）

- 広島 2018: opp_rf_gap_top_c=+42.80, opp_ra_gap_top_c=+7.94, opp_net_gap_top_c=+50.73 / surprise=+34.86
  - 広島 2018 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- 広島 2023: opp_rf_gap_top_c=+34.56, opp_ra_gap_top_c=+1.10, opp_net_gap_top_c=+35.66 / surprise=+33.46
  - 広島 2023 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- ロッテ 2017: opp_rf_gap_top_c=+1.29, opp_ra_gap_top_c=+34.31, opp_net_gap_top_c=+35.60 / surprise=-33.03
  - ロッテ 2017 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- 阪神 2023: opp_rf_gap_top_c=+19.72, opp_ra_gap_top_c=0.138, opp_net_gap_top_c=+19.86 / surprise=+19.58
  - 阪神 2023 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- DeNA 2016: opp_rf_gap_top_c=+37.45, opp_ra_gap_top_c=+19.64, opp_net_gap_top_c=+57.09 / surprise=+17.80
  - DeNA 2016 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- 楽天 2025: opp_rf_gap_top_c=+3.99, opp_ra_gap_top_c=+20.06, opp_net_gap_top_c=+24.05 / surprise=-16.07
  - 楽天 2025 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- ロッテ 2013: opp_rf_gap_top_c=0.205, opp_ra_gap_top_c=+15.97, opp_net_gap_top_c=+16.18 / surprise=-15.77
  - ロッテ 2013 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- 西武 2015: opp_rf_gap_top_c=+14.29, opp_ra_gap_top_c=+1.17, opp_net_gap_top_c=+15.46 / surprise=+13.11
  - 西武 2015 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- DeNA 2022: opp_rf_gap_top_c=+3.31, opp_ra_gap_top_c=+15.55, opp_net_gap_top_c=+18.86 / surprise=-12.23
  - DeNA 2022 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- 日本ハム 2023: opp_rf_gap_top_c=+12.24, opp_ra_gap_top_c=0.263, opp_net_gap_top_c=+12.51 / surprise=+11.98
  - 日本ハム 2023 は「opp_ra_gap_top_c > 0」を満たすのに「opp_rf_gap_top_c < 0」を満たさない。なぜか？ → H3
- ほか 20 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 阪神 2020: opp_rf_gap_top_c=-12.14, opp_ra_gap_top_c=-21.52, opp_net_gap_top_c=-33.66
- 広島 2020: opp_rf_gap_top_c=-18.10, opp_ra_gap_top_c=-13.91, opp_net_gap_top_c=-32.02
- 日本ハム 2020: opp_rf_gap_top_c=-48.01, opp_ra_gap_top_c=-47.83, opp_net_gap_top_c=-95.84
- 巨人 2020: opp_rf_gap_top_c=-4.37, opp_ra_gap_top_c=-4.44, opp_net_gap_top_c=-8.80

## P80: 得失点差がプラスなのに B クラスだったチームは、強い相手との試合全体の点が（平均と比べて）少ない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: h-2013, e-2022, h-2021, c-2022, m-2019 ほか
- もし: `（すべての単位）` ならば: `opp_env_gap_top_c < 0`
- 識別子: `[where:rd>0, where:upper_half==false] * => opp_env_gap_top_c<0`（指紋 `0311e10a084c2178`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'rd', 'op': '>', 'value': 0}, {'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 12
- 親: P76（変更: 結論を「得点の差が負」から「試合全体の点が少ない（env < 0）」に変えた（2019年の得点 −57・失点 +13 の鏡の形から））
- 見直す条件（反証）: held-out（中日 2019 を除く）で、試合全体の点が少なかったチームが半数以下
- 注記: 2019年の道筋を、鏡の形（env）で言い直したもの。P76 と並べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 17 回、元の命題に異議あり 17 回（どれかの形に異議あり 17 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 6 | 0.50 [0.25, 0.75] | +0.00σ（0.613） | 0.50 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 6 | 0 | 0.00 [0.00, 0.39] | -2.45σ（0.016） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- ソフトバンク 2013: opp_env_gap_top_c=+66.22, opp_rf_gap_top_c=+47.56, opp_ra_gap_top_c=-18.67, opp_net_gap_top_c=+28.89 / surprise=+66.22
  - ソフトバンク 2013 は「（すべての単位）」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 楽天 2022: opp_env_gap_top_c=+61.47, opp_rf_gap_top_c=+21.55, opp_ra_gap_top_c=-39.92, opp_net_gap_top_c=-18.37 / surprise=+61.47
  - 楽天 2022 は「（すべての単位）」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ソフトバンク 2021: opp_env_gap_top_c=+45.18, opp_rf_gap_top_c=+31.91, opp_ra_gap_top_c=-13.27, opp_net_gap_top_c=+18.63 / surprise=+45.18
  - ソフトバンク 2021 は「（すべての単位）」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 広島 2022: opp_env_gap_top_c=+26.34, opp_rf_gap_top_c=+18.80, opp_ra_gap_top_c=-7.54, opp_net_gap_top_c=+11.26 / surprise=+26.34
  - 広島 2022 は「（すべての単位）」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ロッテ 2019: opp_env_gap_top_c=+23.78, opp_rf_gap_top_c=+18.81, opp_ra_gap_top_c=-4.97, opp_net_gap_top_c=+13.84 / surprise=+23.78
  - ロッテ 2019 は「（すべての単位）」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 西武 2015: opp_env_gap_top_c=+13.11, opp_rf_gap_top_c=+14.29, opp_ra_gap_top_c=+1.17, opp_net_gap_top_c=+15.46 / surprise=+13.11
  - 西武 2015 は「（すべての単位）」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3

**きっかけ以外での判定**（作り直しのきっかけ d-2019 を除く）: n=11 成立=5 成立率=0.45 [0.21, 0.72] → **判断保留** / 判例: h-2013, e-2022, h-2021, c-2022, m-2019, l-2015

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: opp_env_gap_top_c=+33.12, opp_rf_gap_top_c=+30.41, opp_ra_gap_top_c=-2.71, opp_net_gap_top_c=+27.70
- 楽天 2020: opp_env_gap_top_c=+23.43, opp_rf_gap_top_c=+21.49, opp_ra_gap_top_c=-1.94, opp_net_gap_top_c=+19.54

## P81: 得点した回の大きさがリーグ平均より小さいチームは、強い相手との試合全体の点が（同じ年・同じリーグの平均と比べて）少ない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 28 件: db-2015, e-2018, t-2015, db-2014, m-2018 ほか
- もし: `inn_dlog_size < 0` ならば: `opp_env_gap_top_c < 0`
- 識別子: `[seasons=2013-2025] inn_dlog_size<0 => opp_env_gap_top_c<0`（指紋 `d0599ac003a908b7`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: 作るきっかけ（中日 2019・2021・2022）を除いた判定で、試合全体の点が少なかった単位が半数以下
- 注記: P82（中位の相手）と並べて、強い相手に限った結びつきかを読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 16 回、元の命題に異議あり 16 回（どれかの形に異議あり 16 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 63 | 35 | 0.56 [0.43, 0.67] | +0.88σ（0.225） | 0.52 | 1.07 | 0.285 | 0 | 判断保留 | 4 |
| 対偶 | 69 | 41 | 0.59 [0.48, 0.70] | +1.57σ（0.074） | 0.56 | 1.06 | 0.285 | 0 | 判断保留 | 4 |
| 逆 | 75 | 35 | 0.47 [0.36, 0.58] | -0.58σ（0.322） | 0.44 | 1.07 | 0.285 | 0 | 判断保留 | 4 |
| 裏 | 81 | 41 | 0.51 [0.40, 0.61] | +0.11σ（0.500） | 0.48 | 1.06 | 0.285 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 28 件（対偶の判例も同じ）

- DeNA 2015: inn_dlog_size=-0.012, opp_env_gap_top_c=+56.76, opp_rf_gap_top_c=+39.22, opp_ra_gap_top_c=-17.54, rank_ra=6 / surprise=+56.76
  - DeNA 2015 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 楽天 2018: inn_dlog_size=-0.096, opp_env_gap_top_c=+49.68, opp_rf_gap_top_c=+5.83, opp_ra_gap_top_c=-43.84, rank_ra=3 / surprise=+49.68
  - 楽天 2018 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 阪神 2015: inn_dlog_size=-0.036, opp_env_gap_top_c=+39.34, opp_rf_gap_top_c=+18.78, opp_ra_gap_top_c=-20.55, rank_ra=5 / surprise=+39.34
  - 阪神 2015 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- DeNA 2014: inn_dlog_size=-0.017, opp_env_gap_top_c=+38.56, opp_rf_gap_top_c=+24.23, opp_ra_gap_top_c=-14.34, rank_ra=5 / surprise=+38.56
  - DeNA 2014 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ロッテ 2018: inn_dlog_size=-0.056, opp_env_gap_top_c=+38.35, opp_rf_gap_top_c=+34.57, opp_ra_gap_top_c=-3.78, rank_ra=5 / surprise=+38.35
  - ロッテ 2018 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ヤクルト 2014: inn_dlog_size=-0.020, opp_env_gap_top_c=+35.52, opp_rf_gap_top_c=+18.64, opp_ra_gap_top_c=-16.88, rank_ra=6 / surprise=+35.52
  - ヤクルト 2014 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ヤクルト 2025: inn_dlog_size=-0.041, opp_env_gap_top_c=+34.38, opp_rf_gap_top_c=+10.78, opp_ra_gap_top_c=-23.59, rank_ra=6 / surprise=+34.38
  - ヤクルト 2025 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 広島 2023: inn_dlog_size=-0.015, opp_env_gap_top_c=+33.46, opp_rf_gap_top_c=+34.56, opp_ra_gap_top_c=+1.10, rank_ra=5 / surprise=+33.46
  - 広島 2023 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 中日 2024 **(focus)**: inn_dlog_size=-0.092, opp_env_gap_top_c=+29.57, opp_rf_gap_top_c=+5.74, opp_ra_gap_top_c=-23.83, rank_ra=4 / surprise=+29.57
  - 中日 2024 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ヤクルト 2023: inn_dlog_size=-0.002, opp_env_gap_top_c=+23.13, opp_rf_gap_top_c=+5.79, opp_ra_gap_top_c=-17.34, rank_ra=6 / surprise=+23.13
  - ヤクルト 2023 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ほか 18 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 40 件（裏の判例も同じ）

- 巨人 2015: inn_dlog_size=0.003, opp_env_gap_top_c=-64.58, opp_rf_gap_top_c=-63.99, opp_ra_gap_top_c=0.595, rank_ra=1 / surprise=-64.58
  - 巨人 2015 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- DeNA 2025: inn_dlog_size=0.034, opp_env_gap_top_c=-44.75, opp_rf_gap_top_c=-38.03, opp_ra_gap_top_c=+6.72, rank_ra=2 / surprise=-44.75
  - DeNA 2025 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 巨人 2024: inn_dlog_size=0.115, opp_env_gap_top_c=-43.41, opp_rf_gap_top_c=-15.99, opp_ra_gap_top_c=+27.42, rank_ra=1 / surprise=-43.41
  - 巨人 2024 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- ロッテ 2015: inn_dlog_size=0.034, opp_env_gap_top_c=-39.61, opp_rf_gap_top_c=-9.74, opp_ra_gap_top_c=+29.87, rank_ra=3 / surprise=-39.61
  - ロッテ 2015 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 広島 2015: inn_dlog_size=0.003, opp_env_gap_top_c=-38.72, opp_rf_gap_top_c=-7.11, opp_ra_gap_top_c=+31.61, rank_ra=2 / surprise=-38.72
  - 広島 2015 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 阪神 2018: inn_dlog_size=0.010, opp_env_gap_top_c=-36.63, opp_rf_gap_top_c=-27.25, opp_ra_gap_top_c=+9.38, rank_ra=2 / surprise=-36.63
  - 阪神 2018 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- DeNA 2023: inn_dlog_size=0.045, opp_env_gap_top_c=-35.78, opp_rf_gap_top_c=-45.90, opp_ra_gap_top_c=-10.12, rank_ra=2 / surprise=-35.78
  - DeNA 2023 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 巨人 2017: inn_dlog_size=0.004, opp_env_gap_top_c=-35.12, opp_rf_gap_top_c=-26.14, opp_ra_gap_top_c=+8.98, rank_ra=1 / surprise=-35.12
  - 巨人 2017 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- ロッテ 2022: inn_dlog_size=0.030, opp_env_gap_top_c=-33.67, opp_rf_gap_top_c=-15.59, opp_ra_gap_top_c=+18.09, rank_ra=6 / surprise=-33.67
  - ロッテ 2022 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- オリックス 2021: inn_dlog_size=0.012, opp_env_gap_top_c=-32.37, opp_rf_gap_top_c=-25.96, opp_ra_gap_top_c=+6.41, rank_ra=2 / surprise=-32.37
  - オリックス 2021 は「opp_env_gap_top_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- ほか 30 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ d-2019, d-2021, d-2022 を除く）: n=60 成立=32 成立率=0.53 [0.41, 0.65] → **判断保留** / 判例: db-2015, e-2018, t-2015, db-2014, m-2018, s-2014, s-2025, c-2023, d-2024, s-2023

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: inn_dlog_size=-0.025, opp_env_gap_top_c=+33.12, opp_rf_gap_top_c=+30.41, opp_ra_gap_top_c=-2.71, rank_ra=3
- 西武 2020: inn_dlog_size=-0.035, opp_env_gap_top_c=+28.10, opp_rf_gap_top_c=+14.42, opp_ra_gap_top_c=-13.68, rank_ra=6

## P82: 得点した回の大きさがリーグ平均より小さいチームは、中位の相手との試合全体の点も（平均と比べて）少ない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 32 件: s-2013, g-2023, c-2021, b-2019, s-2014 ほか
- もし: `inn_dlog_size < 0` ならば: `opp_env_gap_mid_c < 0`
- 識別子: `[seasons=2013-2025] inn_dlog_size<0 => opp_env_gap_mid_c<0`（指紋 `7ab72a310be8db04`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）
- 注記: P81 の対照。P81 だけ成り立てば強い相手に限った結びつき、両方なら相手の強さに関係のない結びつき
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 16 回、元の命題に異議あり 16 回（どれかの形に異議あり 16 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 63 | 31 | 0.49 [0.37, 0.61] | -0.13σ（0.500） | 0.51 | 0.97 | 0.685 | 0 | 判断保留 | 4 |
| 対偶 | 71 | 39 | 0.55 [0.43, 0.66] | +0.83σ（0.238） | 0.56 | 0.98 | 0.685 | 0 | 判断保留 | 4 |
| 逆 | 73 | 31 | 0.42 [0.32, 0.54] | -1.29σ（0.121） | 0.44 | 0.97 | 0.685 | 0 | 判断保留 | 4 |
| 裏 | 81 | 39 | 0.48 [0.38, 0.59] | -0.33σ（0.412） | 0.49 | 0.98 | 0.685 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 32 件（対偶の判例も同じ）

- ヤクルト 2013: inn_dlog_size=-0.021, opp_env_gap_mid_c=+78.07, opp_rf_gap_mid_c=+33.03, opp_ra_gap_mid_c=-45.03, opp_env_gap_top_c=-52.78 / surprise=+78.07
  - ヤクルト 2013 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- 巨人 2023: inn_dlog_size=-0.019, opp_env_gap_mid_c=+49.37, opp_rf_gap_mid_c=+14.93, opp_ra_gap_mid_c=-34.44, opp_env_gap_top_c=-30.08 / surprise=+49.37
  - 巨人 2023 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- 広島 2021: inn_dlog_size=-0.002, opp_env_gap_mid_c=+44.79, opp_rf_gap_mid_c=+33.70, opp_ra_gap_mid_c=-11.09, opp_env_gap_top_c=-65.85 / surprise=+44.79
  - 広島 2021 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- オリックス 2019: inn_dlog_size=-0.035, opp_env_gap_mid_c=+40.66, opp_rf_gap_mid_c=+12.95, opp_ra_gap_mid_c=-27.71, opp_env_gap_top_c=-41.10 / surprise=+40.66
  - オリックス 2019 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- ヤクルト 2014: inn_dlog_size=-0.020, opp_env_gap_mid_c=+38.28, opp_rf_gap_mid_c=+21.49, opp_ra_gap_mid_c=-16.78, opp_env_gap_top_c=+35.52 / surprise=+38.28
  - ヤクルト 2014 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- 西武 2013: inn_dlog_size=-0.030, opp_env_gap_mid_c=+32.87, opp_rf_gap_mid_c=+40.79, opp_ra_gap_mid_c=+7.93, opp_env_gap_top_c=+13.82 / surprise=+32.87
  - 西武 2013 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- オリックス 2017: inn_dlog_size=-0.007, opp_env_gap_mid_c=+32.73, opp_rf_gap_mid_c=+17.08, opp_ra_gap_mid_c=-15.64, opp_env_gap_top_c=-16.74 / surprise=+32.73
  - オリックス 2017 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- DeNA 2016: inn_dlog_size=-0.002, opp_env_gap_mid_c=+27.93, opp_rf_gap_mid_c=-4.43, opp_ra_gap_mid_c=-32.36, opp_env_gap_top_c=+17.80 / surprise=+27.93
  - DeNA 2016 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- ヤクルト 2023: inn_dlog_size=-0.002, opp_env_gap_mid_c=+26.69, opp_rf_gap_mid_c=+23.10, opp_ra_gap_mid_c=-3.59, opp_env_gap_top_c=+23.13 / surprise=+26.69
  - ヤクルト 2023 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- 西武 2022: inn_dlog_size=-0.045, opp_env_gap_mid_c=+24.54, opp_rf_gap_mid_c=+13.19, opp_ra_gap_mid_c=-11.35, opp_env_gap_top_c=-37.68 / surprise=+24.54
  - 西武 2022 は「inn_dlog_size < 0」を満たすのに「opp_env_gap_mid_c < 0」を満たさない。なぜか？ → H3
- ほか 22 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 42 件（裏の判例も同じ）

- 日本ハム 2019: inn_dlog_size=0.031, opp_env_gap_mid_c=-73.55, opp_rf_gap_mid_c=-30.71, opp_ra_gap_mid_c=+42.84, opp_env_gap_top_c=+36.42 / surprise=-73.55
  - 日本ハム 2019 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- ソフトバンク 2013: inn_dlog_size=0.026, opp_env_gap_mid_c=-68.70, opp_rf_gap_mid_c=-49.86, opp_ra_gap_mid_c=+18.85, opp_env_gap_top_c=+66.22 / surprise=-68.70
  - ソフトバンク 2013 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 阪神 2023: inn_dlog_size=0.071, opp_env_gap_mid_c=-47.05, opp_rf_gap_mid_c=-17.25, opp_ra_gap_mid_c=+29.80, opp_env_gap_top_c=+19.58 / surprise=-47.05
  - 阪神 2023 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 日本ハム 2018: inn_dlog_size=0.008, opp_env_gap_mid_c=-43.70, opp_rf_gap_mid_c=-42.81, opp_ra_gap_mid_c=0.896, opp_env_gap_top_c=-31.85 / surprise=-43.70
  - 日本ハム 2018 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- DeNA 2013: inn_dlog_size=0.033, opp_env_gap_mid_c=-41.93, opp_rf_gap_mid_c=-13.27, opp_ra_gap_mid_c=+28.66, opp_env_gap_top_c=+107.12 / surprise=-41.93
  - DeNA 2013 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- ロッテ 2019: inn_dlog_size=0.007, opp_env_gap_mid_c=-41.13, opp_rf_gap_mid_c=-2.57, opp_ra_gap_mid_c=+38.56, opp_env_gap_top_c=+23.78 / surprise=-41.13
  - ロッテ 2019 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 巨人 2022: inn_dlog_size=0.050, opp_env_gap_mid_c=-39.52, opp_rf_gap_mid_c=-20.89, opp_ra_gap_mid_c=+18.63, opp_env_gap_top_c=+43.93 / surprise=-39.52
  - 巨人 2022 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- ヤクルト 2021: inn_dlog_size=0.066, opp_env_gap_mid_c=-38.15, opp_rf_gap_mid_c=-15.95, opp_ra_gap_mid_c=+22.20, opp_env_gap_top_c=+83.11 / surprise=-38.15
  - ヤクルト 2021 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 広島 2025: inn_dlog_size=0.031, opp_env_gap_mid_c=-37.22, opp_rf_gap_mid_c=+3.91, opp_ra_gap_mid_c=+41.13, opp_env_gap_top_c=-9.24 / surprise=-37.22
  - 広島 2025 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- 広島 2013: inn_dlog_size=0.009, opp_env_gap_mid_c=-36.08, opp_rf_gap_mid_c=-20.55, opp_ra_gap_mid_c=+15.53, opp_env_gap_top_c=-29.40 / surprise=-36.08
  - 広島 2013 は「opp_env_gap_mid_c < 0」を満たすのに「inn_dlog_size < 0」を満たさない。なぜか？ → H3
- ほか 32 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: inn_dlog_size=-0.004, opp_env_gap_mid_c=+24.80, opp_rf_gap_mid_c=-31.57, opp_ra_gap_mid_c=-56.38, opp_env_gap_top_c=-34.75
- 中日 2020 **(focus)**: inn_dlog_size=-0.096, opp_env_gap_mid_c=+21.69, opp_rf_gap_mid_c=-27.12, opp_ra_gap_mid_c=-48.80, opp_env_gap_top_c=-54.34

## P83: 失点がリーグ2位以内のチームは、強い相手との試合全体の点が（平均と比べて）少ない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 19 件: g-2018, h-2021, t-2017, h-2017, h-2024 ほか
- もし: `rank_ra <= 2` ならば: `opp_env_gap_top_c < 0`
- 識別子: `[all] rank_ra<=2 => opp_env_gap_top_c<0`（指紋 `f703ed88ab92854a`）
- 兄弟（範囲と結論が同じ、条件が違う）: P84
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 作るきっかけ（中日 2019・2021・2022）を除いた判定で、試合全体の点が少なかった単位が半数以下
- 注記: 成り立っても、投手の起用の結果か、掛け算の見込みの式の偏りかは分けられない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 16 回、元の命題に異議あり 16 回（どれかの形に異議あり 16 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 33 | 0.63 [0.50, 0.75] | +1.94σ（0.035） | 0.51 | 1.24 | 0.023 | 0 | 判断保留 | 4 |
| 対偶 | 76 | 57 | 0.75 [0.64, 0.83] | +4.36σ（0.000） | 0.67 | 1.12 | 0.023 | 0 | 支持 | 1 |
| 逆 | 80 | 33 | 0.41 [0.31, 0.52] | -1.57σ（0.073） | 0.33 | 1.24 | 0.023 | 0 | 判断保留 | 4 |
| 裏 | 104 | 57 | 0.55 [0.45, 0.64] | +0.98σ（0.189） | 0.49 | 1.13 | 0.023 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 19 件（対偶の判例も同じ）

- 巨人 2018: rank_ra=1, opp_env_gap_top_c=+49.83, opp_rf_gap_top_c=+15.74, opp_ra_gap_top_c=-34.09, upper_half=True / surprise=+49.83
  - 巨人 2018 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ソフトバンク 2021: rank_ra=1, opp_env_gap_top_c=+45.18, opp_rf_gap_top_c=+31.91, opp_ra_gap_top_c=-13.27, upper_half=False / surprise=+45.18
  - ソフトバンク 2021 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 阪神 2017: rank_ra=2, opp_env_gap_top_c=+44.98, opp_rf_gap_top_c=+9.90, opp_ra_gap_top_c=-35.08, upper_half=True / surprise=+44.98
  - 阪神 2017 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ソフトバンク 2017: rank_ra=1, opp_env_gap_top_c=+31.18, opp_rf_gap_top_c=+25.10, opp_ra_gap_top_c=-6.08, upper_half=True / surprise=+31.18
  - ソフトバンク 2017 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ソフトバンク 2024: rank_ra=1, opp_env_gap_top_c=+21.89, opp_rf_gap_top_c=-4.72, opp_ra_gap_top_c=-26.61, upper_half=True / surprise=+21.89
  - ソフトバンク 2024 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ソフトバンク 2015: rank_ra=1, opp_env_gap_top_c=+21.39, opp_rf_gap_top_c=+12.26, opp_ra_gap_top_c=-9.13, upper_half=True / surprise=+21.39
  - ソフトバンク 2015 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 阪神 2023: rank_ra=1, opp_env_gap_top_c=+19.58, opp_rf_gap_top_c=+19.72, opp_ra_gap_top_c=0.138, upper_half=True / surprise=+19.58
  - 阪神 2023 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 広島 2024: rank_ra=2, opp_env_gap_top_c=+18.90, opp_rf_gap_top_c=+2.17, opp_ra_gap_top_c=-16.72, upper_half=False / surprise=+18.90
  - 広島 2024 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 巨人 2016: rank_ra=2, opp_env_gap_top_c=+18.06, opp_rf_gap_top_c=+3.27, opp_ra_gap_top_c=-14.79, upper_half=True / surprise=+18.06
  - 巨人 2016 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ソフトバンク 2014: rank_ra=2, opp_env_gap_top_c=+13.36, opp_rf_gap_top_c=+11.02, opp_ra_gap_top_c=-2.34, upper_half=True / surprise=+13.36
  - ソフトバンク 2014 は「rank_ra <= 2」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ほか 9 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 47 件（裏の判例も同じ）

- ロッテ 2014: rank_ra=6, opp_env_gap_top_c=-76.25, opp_rf_gap_top_c=-20.90, opp_ra_gap_top_c=+55.35, upper_half=False / surprise=-76.25
  - ロッテ 2014 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- ヤクルト 2017: rank_ra=6, opp_env_gap_top_c=-70.26, opp_rf_gap_top_c=-29.45, opp_ra_gap_top_c=+40.81, upper_half=False / surprise=-70.26
  - ヤクルト 2017 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- 広島 2021: rank_ra=5, opp_env_gap_top_c=-65.85, opp_rf_gap_top_c=-30.55, opp_ra_gap_top_c=+35.30, upper_half=False / surprise=-65.85
  - 広島 2021 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- 阪神 2012: rank_ra=3, opp_env_gap_top_c=-61.47, opp_rf_gap_top_c=-45.79, opp_ra_gap_top_c=+15.68, upper_half=False / surprise=-61.47
  - 阪神 2012 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- ヤクルト 2013: rank_ra=5, opp_env_gap_top_c=-52.78, opp_rf_gap_top_c=-25.77, opp_ra_gap_top_c=+27.01, upper_half=False / surprise=-52.78
  - ヤクルト 2013 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- DeNA 2018: rank_ra=3, opp_env_gap_top_c=-52.09, opp_rf_gap_top_c=-5.92, opp_ra_gap_top_c=+46.17, upper_half=False / surprise=-52.09
  - DeNA 2018 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- 楽天 2012: rank_ra=3, opp_env_gap_top_c=-45.47, opp_rf_gap_top_c=-16.26, opp_ra_gap_top_c=+29.22, upper_half=False / surprise=-45.47
  - 楽天 2012 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- 西武 2024: rank_ra=3, opp_env_gap_top_c=-45.01, opp_rf_gap_top_c=-1.89, opp_ra_gap_top_c=+43.12, upper_half=False / surprise=-45.01
  - 西武 2024 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- 広島 2019: rank_ra=4, opp_env_gap_top_c=-44.27, opp_rf_gap_top_c=-20.10, opp_ra_gap_top_c=+24.17, upper_half=False / surprise=-44.27
  - 広島 2019 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- オリックス 2019: rank_ra=5, opp_env_gap_top_c=-41.10, opp_rf_gap_top_c=-17.65, opp_ra_gap_top_c=+23.45, upper_half=False / surprise=-41.10
  - オリックス 2019 は「opp_env_gap_top_c < 0」を満たすのに「rank_ra <= 2」を満たさない。なぜか？ → H3
- ほか 37 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ d-2019, d-2021, d-2022 を除く）: n=49 成立=30 成立率=0.61 [0.47, 0.74] → **判断保留** / 判例: g-2018, h-2021, t-2017, h-2017, h-2024, h-2015, t-2023, c-2024, g-2016, h-2014

**除外中の判例**（統計からは除いたが、判例としては残す）

- 阪神 2020: rank_ra=2, opp_env_gap_top_c=+9.38, opp_rf_gap_top_c=-12.14, opp_ra_gap_top_c=-21.52, upper_half=True
- 巨人 2020: rank_ra=1, opp_env_gap_top_c=0.071, opp_rf_gap_top_c=-4.37, opp_ra_gap_top_c=-4.44, upper_half=True

## P84: A クラスのチームは、強い相手（3位を争う相手）との試合全体の点が（平均と比べて）少ない

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 38 件: s-2021, l-2017, g-2018, m-2021, db-2019 ほか
- もし: `upper_half == True` ならば: `opp_env_gap_top_c < 0`
- 識別子: `[all] upper_half==true => opp_env_gap_top_c<0`（指紋 `2d3a3b233df4a7dc`）
- 兄弟（範囲と結論が同じ、条件が違う）: P83
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）
- 注記: 上位どうしの試合が投手戦に寄るか。上位を狙った起用（作為）と矛盾しないかを見るが、起用そのものはこのデータでは分けられない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 16 回、元の命題に異議あり 16 回（どれかの形に異議あり 16 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 78 | 40 | 0.51 [0.40, 0.62] | +0.23σ（0.455） | 0.51 | 1.00 | 0.564 | 0 | 判断保留 | 4 |
| 対偶 | 76 | 38 | 0.50 [0.39, 0.61] | +0.00σ（0.546） | 0.50 | 1.00 | 0.564 | 0 | 判断保留 | 4 |
| 逆 | 80 | 40 | 0.50 [0.39, 0.61] | +0.00σ（0.544） | 0.50 | 1.00 | 0.564 | 0 | 判断保留 | 4 |
| 裏 | 78 | 38 | 0.49 [0.38, 0.60] | -0.23σ（0.455） | 0.49 | 1.00 | 0.564 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 38 件（対偶の判例も同じ）

- ヤクルト 2021: upper_half=True, opp_env_gap_top_c=+83.11, rank=1, opp_rf_gap_top_c=+27.32, opp_ra_gap_top_c=-55.78, opp_adj_top=-5.46 / surprise=+83.11
  - ヤクルト 2021 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 西武 2017: upper_half=True, opp_env_gap_top_c=+70.55, rank=2, opp_rf_gap_top_c=+25.75, opp_ra_gap_top_c=-44.80, opp_adj_top=-0.286 / surprise=+70.55
  - 西武 2017 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 巨人 2018: upper_half=True, opp_env_gap_top_c=+49.83, rank=3, opp_rf_gap_top_c=+15.74, opp_ra_gap_top_c=-34.09, opp_adj_top=-7.19 / surprise=+49.83
  - 巨人 2018 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ロッテ 2021: upper_half=True, opp_env_gap_top_c=+48.67, rank=2, opp_rf_gap_top_c=+19.75, opp_ra_gap_top_c=-28.92, opp_adj_top=0.417 / surprise=+48.67
  - ロッテ 2021 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- DeNA 2019: upper_half=True, opp_env_gap_top_c=+48.43, rank=2, opp_rf_gap_top_c=+28.49, opp_ra_gap_top_c=-19.94, opp_adj_top=+3.26 / surprise=+48.43
  - DeNA 2019 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 西武 2012: upper_half=True, opp_env_gap_top_c=+47.88, rank=2, opp_rf_gap_top_c=+18.43, opp_ra_gap_top_c=-29.44, opp_adj_top=+3.59 / surprise=+47.88
  - 西武 2012 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 巨人 2021: upper_half=True, opp_env_gap_top_c=+45.42, rank=3, opp_rf_gap_top_c=+28.17, opp_ra_gap_top_c=-17.25, opp_adj_top=0.011 / surprise=+45.42
  - 巨人 2021 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 阪神 2017: upper_half=True, opp_env_gap_top_c=+44.98, rank=2, opp_rf_gap_top_c=+9.90, opp_ra_gap_top_c=-35.08, opp_adj_top=0.709 / surprise=+44.98
  - 阪神 2017 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 阪神 2015: upper_half=True, opp_env_gap_top_c=+39.34, rank=3, opp_rf_gap_top_c=+18.78, opp_ra_gap_top_c=-20.55, opp_adj_top=+2.27 / surprise=+39.34
  - 阪神 2015 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- 広島 2017: upper_half=True, opp_env_gap_top_c=+36.38, rank=1, opp_rf_gap_top_c=+35.87, opp_ra_gap_top_c=-0.512, opp_adj_top=+5.20 / surprise=+36.38
  - 広島 2017 は「upper_half == True」を満たすのに「opp_env_gap_top_c < 0」を満たさない。なぜか？ → H3
- ほか 28 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 40 件（裏の判例も同じ）

- ロッテ 2014: upper_half=False, opp_env_gap_top_c=-76.25, rank=4, opp_rf_gap_top_c=-20.90, opp_ra_gap_top_c=+55.35, opp_adj_top=+4.55 / surprise=-76.25
  - ロッテ 2014 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2019 **(focus)**: upper_half=False, opp_env_gap_top_c=-70.42, rank=5, opp_rf_gap_top_c=-57.34, opp_ra_gap_top_c=+13.07, opp_adj_top=-3.70 / surprise=-70.42
  - 中日 2019 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ヤクルト 2017: upper_half=False, opp_env_gap_top_c=-70.26, rank=6, opp_rf_gap_top_c=-29.45, opp_ra_gap_top_c=+40.81, opp_adj_top=-0.496 / surprise=-70.26
  - ヤクルト 2017 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- オリックス 2013: upper_half=False, opp_env_gap_top_c=-67.91, rank=5, opp_rf_gap_top_c=-43.33, opp_ra_gap_top_c=+24.58, opp_adj_top=0.585 / surprise=-67.91
  - オリックス 2013 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 広島 2021: upper_half=False, opp_env_gap_top_c=-65.85, rank=4, opp_rf_gap_top_c=-30.55, opp_ra_gap_top_c=+35.30, opp_adj_top=0.014 / surprise=-65.85
  - 広島 2021 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2021 **(focus)**: upper_half=False, opp_env_gap_top_c=-62.82, rank=5, opp_rf_gap_top_c=-29.28, opp_ra_gap_top_c=+33.55, opp_adj_top=-1.40 / surprise=-62.82
  - 中日 2021 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 阪神 2012: upper_half=False, opp_env_gap_top_c=-61.47, rank=5, opp_rf_gap_top_c=-45.79, opp_ra_gap_top_c=+15.68, opp_adj_top=-5.79 / surprise=-61.47
  - 阪神 2012 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ヤクルト 2013: upper_half=False, opp_env_gap_top_c=-52.78, rank=6, opp_rf_gap_top_c=-25.77, opp_ra_gap_top_c=+27.01, opp_adj_top=-1.97 / surprise=-52.78
  - ヤクルト 2013 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- DeNA 2018: upper_half=False, opp_env_gap_top_c=-52.09, rank=4, opp_rf_gap_top_c=-5.92, opp_ra_gap_top_c=+46.17, opp_adj_top=+7.07 / surprise=-52.09
  - DeNA 2018 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2012: upper_half=False, opp_env_gap_top_c=-45.47, rank=4, opp_rf_gap_top_c=-16.26, opp_ra_gap_top_c=+29.22, opp_adj_top=+4.50 / surprise=-45.47
  - 楽天 2012 は「opp_env_gap_top_c < 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ほか 30 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 西武 2020: upper_half=True, opp_env_gap_top_c=+28.10, rank=3, opp_rf_gap_top_c=+14.42, opp_ra_gap_top_c=-13.68, opp_adj_top=+6.26
- 阪神 2020: upper_half=True, opp_env_gap_top_c=+9.38, rank=2, opp_rf_gap_top_c=-12.14, opp_ra_gap_top_c=-21.52, opp_adj_top=-2.00
- 巨人 2020: upper_half=True, opp_env_gap_top_c=0.071, rank=1, opp_rf_gap_top_c=-4.37, opp_ra_gap_top_c=-4.44, opp_adj_top=0.998

## P85: 中日は、勝ち試合の得点が、自分の得点・失点の分布から見込まれるより少ない（勝つときは投手戦で勝っている）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2021
- もし: `（すべての単位）` ならば: `wl_rf_win_gap < 0`
- 識別子: `[team=d] * => wl_rf_win_gap<0`（指紋 `2eb739fb8cf900f3`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日の13年のうち4分の1を超えて、勝ち試合の得点が見込み以上
- 注記: 見込みからのずれは全球団に出うる。中日の傾向と言うのは、中日の13年の平均が12球団の中で端から2番目以内のとき（R20 の読み方）
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 12 | 0.92 [0.67, 0.99] | +1.44σ（0.127） | 0.92 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2021 **(focus)**: wl_rf_win_gap=0.063, wl_rf_win=+4.60, wl_rf_win_exp=+4.54, wl_rf_loss_gap=0.037, rank=5 / surprise=0.063
  - 中日 2021 は「（すべての単位）」を満たすのに「wl_rf_win_gap < 0」を満たさない。なぜか？ → H8

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: wl_rf_win_gap=0.074, wl_rf_win=+5.02, wl_rf_win_exp=+4.94, wl_rf_loss_gap=-0.302, rank=3

## P86: 中日は、負け試合の得点が、自分の得点・失点の分布から見込まれるより多い（点を取っても負けている）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: d-2012, d-2013
- もし: `（すべての単位）` ならば: `wl_rf_loss_gap > 0`
- 識別子: `[team=d] * => wl_rf_loss_gap>0`（指紋 `6a7ec804cfd4d926`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日の13年のうち4分の1を超えて、負け試合の得点が見込み以下
- 注記: P85 と同じ量の表と裏になりやすい（1試合の中で得点と失点が一緒に動くと両方起きる）
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 11 | 0.85 [0.58, 0.96] | +0.80σ（0.333） | 0.85 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 2 | 0 | 0.00 [0.00, 0.66] | -2.45σ（0.062） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- 中日 2012 **(focus)**: wl_rf_loss_gap=-0.229, wl_rf_loss=+1.49, wl_rf_loss_exp=+1.72, wl_rf_win_gap=-0.334, rank=2 / surprise=-0.229
  - 中日 2012 は「（すべての単位）」を満たすのに「wl_rf_loss_gap > 0」を満たさない。なぜか？ → H8
- 中日 2013 **(focus)**: wl_rf_loss_gap=-0.117, wl_rf_loss=+2.00, wl_rf_loss_exp=+2.12, wl_rf_win_gap=-0.179, rank=4 / surprise=-0.117
  - 中日 2013 は「（すべての単位）」を満たすのに「wl_rf_loss_gap > 0」を満たさない。なぜか？ → H8

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: wl_rf_loss_gap=-0.302, wl_rf_loss=+2.09, wl_rf_loss_exp=+2.39, wl_rf_win_gap=0.074, rank=3

## P87: 中日は、両チームの合計得点がリーグの中央値より多い試合の勝率が、見込みより低い（点の多い試合を制せない）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 7 件: d-2021, d-2013, d-2012, d-2024, d-2025 ほか
- もし: `（すべての単位）` ならば: `wl_wpct_high_gap < 0`
- 識別子: `[team=d] * => wl_wpct_high_gap<0`（指紋 `6d0cbde3062c6d46`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日の13年のうち4分の1を超えて、点の多い試合の勝率が見込み以上
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 6 | 0.46 [0.23, 0.71] | -2.40σ（0.024） | 0.46 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 7 | 0 | 0.00 [0.00, 0.35] | -4.58σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 7 件（対偶の判例も同じ）

- 中日 2021 **(focus)**: wl_wpct_high_gap=0.059, wl_wpct_high=0.512, wl_wpct_low=0.400, wl_wpct_low_gap=-0.037, rank=5 / surprise=0.059
  - 中日 2021 は「（すべての単位）」を満たすのに「wl_wpct_high_gap < 0」を満たさない。なぜか？ → H8
- 中日 2013 **(focus)**: wl_wpct_high_gap=0.045, wl_wpct_high=0.482, wl_wpct_low=0.435, wl_wpct_low_gap=0.012, rank=4 / surprise=0.045
  - 中日 2013 は「（すべての単位）」を満たすのに「wl_wpct_high_gap < 0」を満たさない。なぜか？ → H8
- 中日 2012 **(focus)**: wl_wpct_high_gap=0.037, wl_wpct_high=0.500, wl_wpct_low=0.628, wl_wpct_low_gap=0.027, rank=2 / surprise=0.037
  - 中日 2012 は「（すべての単位）」を満たすのに「wl_wpct_high_gap < 0」を満たさない。なぜか？ → H8
- 中日 2024 **(focus)**: wl_wpct_high_gap=0.030, wl_wpct_high=0.345, wl_wpct_low=0.512, wl_wpct_low_gap=-0.001, rank=6 / surprise=0.030
  - 中日 2024 は「（すべての単位）」を満たすのに「wl_wpct_high_gap < 0」を満たさない。なぜか？ → H8
- 中日 2025 **(focus)**: wl_wpct_high_gap=0.019, wl_wpct_high=0.417, wl_wpct_low=0.469, wl_wpct_low_gap=-0.017, rank=4 / surprise=0.019
  - 中日 2025 は「（すべての単位）」を満たすのに「wl_wpct_high_gap < 0」を満たさない。なぜか？ → H8
- 中日 2022 **(focus)**: wl_wpct_high_gap=0.009, wl_wpct_high=0.383, wl_wpct_low=0.511, wl_wpct_low_gap=0.020, rank=6 / surprise=0.009
  - 中日 2022 は「（すべての単位）」を満たすのに「wl_wpct_high_gap < 0」を満たさない。なぜか？ → H8
- 中日 2014 **(focus)**: wl_wpct_high_gap=0.001, wl_wpct_high=0.493, wl_wpct_low=0.466, wl_wpct_low_gap=-0.029, rank=4 / surprise=0.001
  - 中日 2014 は「（すべての単位）」を満たすのに「wl_wpct_high_gap < 0」を満たさない。なぜか？ → H8

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: wl_wpct_high_gap=0.026, wl_wpct_high=0.341, wl_wpct_low=0.634, wl_wpct_low_gap=0.029, rank=3

## P88: 中日は、後半の勝率が前半より低い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: d-2022, d-2019, d-2013, d-2023, d-2012 ほか
- もし: `（すべての単位）` ならば: `course_wpct_diff < 0`
- 識別子: `[team=d] * => course_wpct_diff<0`（指紋 `cde4a2a8ca257b4c`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日の後半の勝率が前半より低い年が13年中7年以下
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 7 | 0.54 [0.29, 0.77] | -1.76σ（0.080） | 0.54 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 6 | 0 | 0.00 [0.00, 0.39] | -4.24σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- 中日 2022 **(focus)**: course_wpct_diff=0.092, course_wpct_h1=0.423, course_wpct_h2=0.514, course_rank_h1=6, rank=6 / surprise=0.092
  - 中日 2022 は「（すべての単位）」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H6
- 中日 2019 **(focus)**: course_wpct_diff=0.064, course_wpct_h1=0.451, course_wpct_h2=0.514, course_rank_h1=5, rank=5 / surprise=0.064
  - 中日 2019 は「（すべての単位）」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H6
- 中日 2013 **(focus)**: course_wpct_diff=0.063, course_wpct_h1=0.423, course_wpct_h2=0.486, course_rank_h1=4, rank=4 / surprise=0.063
  - 中日 2013 は「（すべての単位）」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H6
- 中日 2023 **(focus)**: course_wpct_diff=0.012, course_wpct_h1=0.400, course_wpct_h2=0.412, course_rank_h1=5, rank=6 / surprise=0.012
  - 中日 2023 は「（すべての単位）」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H6
- 中日 2012 **(focus)**: course_wpct_diff=0.010, course_wpct_h1=0.581, course_wpct_h2=0.591, course_rank_h1=2, rank=2 / surprise=0.010
  - 中日 2012 は「（すべての単位）」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H6
- 中日 2018 **(focus)**: course_wpct_diff=0.008, course_wpct_h1=0.443, course_wpct_h2=0.451, course_rank_h1=6, rank=5 / surprise=0.008
  - 中日 2018 は「（すべての単位）」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: course_wpct_diff=0.112, course_wpct_h1=0.464, course_wpct_h2=0.576, course_rank_h1=4, rank=3

## P89: 中日の B クラスの年は、前半の勝率ではリーグ3位以内にいた（前半は上位にいて、後半に落ちた）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 10 件: d-2015, d-2017, d-2018, d-2021, d-2023 ほか
- もし: `（すべての単位）` ならば: `course_rank_h1 <= 3`
- 識別子: `[team=d, where:upper_half==false] * => course_rank_h1<=3`（指紋 `b67ff3b207430ee0`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd', 'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 12
- 見直す条件（反証）: 中日の B クラスの年のうち、前半3位以内が半数以下
- 注記: P90（中日以外の B クラス）の率より 0.2 以上高ければ、中日の B クラスは前半は上位にいて後半に落ちる形に寄っている
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 2 | 0.17 [0.05, 0.45] | -2.31σ（0.019） | 0.17 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 10 | 0 | 0.00 [0.00, 0.28] | -3.16σ（0.001） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 10 件（対偶の判例も同じ）

- 中日 2015 **(focus)**: course_rank_h1=6, course_rank_q1=3, course_rank_q3=6, rank=5, course_wpct_diff=-0.022 / surprise=-1
  - 中日 2015 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2017 **(focus)**: course_rank_h1=4, course_rank_q1=6, course_rank_q3=5, rank=5, course_wpct_diff=-0.056 / surprise=1
  - 中日 2017 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2018 **(focus)**: course_rank_h1=6, course_rank_q1=5, course_rank_q3=5, rank=5, course_wpct_diff=0.008 / surprise=-1
  - 中日 2018 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2021 **(focus)**: course_rank_h1=4, course_rank_q1=5, course_rank_q3=4, rank=5, course_wpct_diff=-0.030 / surprise=1
  - 中日 2021 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2023 **(focus)**: course_rank_h1=5, course_rank_q1=6, course_rank_q3=6, rank=6, course_wpct_diff=0.012 / surprise=1
  - 中日 2023 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2024 **(focus)**: course_rank_h1=5, course_rank_q1=6, course_rank_q3=5, rank=6, course_wpct_diff=-0.033 / surprise=1
  - 中日 2024 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2025 **(focus)**: course_rank_h1=5, course_rank_q1=5, course_rank_q3=5, rank=4, course_wpct_diff=-0.033 / surprise=-1
  - 中日 2025 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2013 **(focus)**: course_rank_h1=4, course_rank_q1=6, course_rank_q3=4, rank=4, course_wpct_diff=0.063 / surprise=0
  - 中日 2013 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2019 **(focus)**: course_rank_h1=5, course_rank_q1=5, course_rank_q3=5, rank=5, course_wpct_diff=0.064 / surprise=0
  - 中日 2019 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 中日 2022 **(focus)**: course_rank_h1=6, course_rank_q1=4, course_rank_q3=6, rank=6, course_wpct_diff=0.092 / surprise=0
  - 中日 2022 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6

## P90: 中日以外の B クラスのチームは、前半の勝率ではリーグ3位以内にいた

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 49 件: l-2021, f-2023, b-2013, db-2014, s-2014 ほか
- もし: `（すべての単位）` ならば: `course_rank_h1 <= 3`
- 識別子: `[where:team!="d", where:upper_half==false] * => course_rank_h1<=3`（指紋 `5ae64a63d334bc38`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 66
- 見直す条件（反証）: （基準の命題。P89 と率を比べるために置く）
- 注記: P89 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 66 | 17 | 0.26 [0.17, 0.37] | -3.94σ（0.000） | 0.26 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 49 | 0 | 0.00 [0.00, 0.07] | -7.00σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 49 件（対偶の判例も同じ）

- 西武 2021: course_rank_h1=4, course_rank_q1=4, course_rank_q3=5, rank=6, course_wpct_diff=-0.112 / surprise=2
  - 西武 2021 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 日本ハム 2023: course_rank_h1=4, course_rank_q1=5, course_rank_q3=6, rank=6, course_wpct_diff=-0.085 / surprise=2
  - 日本ハム 2023 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- オリックス 2013: course_rank_h1=6, course_rank_q1=5, course_rank_q3=6, rank=5, course_wpct_diff=0.007 / surprise=-1
  - オリックス 2013 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- DeNA 2014: course_rank_h1=6, course_rank_q1=5, course_rank_q3=5, rank=5, course_wpct_diff=0.112 / surprise=-1
  - DeNA 2014 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- ヤクルト 2014: course_rank_h1=5, course_rank_q1=6, course_rank_q3=6, rank=6, course_wpct_diff=-0.006 / surprise=1
  - ヤクルト 2014 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- オリックス 2015: course_rank_h1=6, course_rank_q1=6, course_rank_q3=6, rank=5, course_wpct_diff=0.065 / surprise=-1
  - オリックス 2015 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 楽天 2015: course_rank_h1=5, course_rank_q1=5, course_rank_q3=5, rank=6, course_wpct_diff=-0.140 / surprise=1
  - 楽天 2015 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- ヤクルト 2016: course_rank_h1=6, course_rank_q1=5, course_rank_q3=5, rank=5, course_wpct_diff=0.044 / surprise=-1
  - ヤクルト 2016 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- 巨人 2017: course_rank_h1=5, course_rank_q1=3, course_rank_q3=4, rank=4, course_wpct_diff=0.158 / surprise=-1
  - 巨人 2017 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- オリックス 2018: course_rank_h1=5, course_rank_q1=4, course_rank_q3=5, rank=4, course_wpct_diff=-0.086 / surprise=-1
  - オリックス 2018 は「（すべての単位）」を満たすのに「course_rank_h1 <= 3」を満たさない。なぜか？ → H1, H6
- ほか 39 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 日本ハム 2020: course_rank_h1=4, course_rank_q1=5, course_rank_q3=5, rank=5, course_wpct_diff=-0.095
- オリックス 2020: course_rank_h1=6, course_rank_q1=6, course_rank_q3=6, rank=6, course_wpct_diff=0.117
- 広島 2020: course_rank_h1=5, course_rank_q1=5, course_rank_q3=5, rank=5, course_wpct_diff=0.074
- ヤクルト 2020: course_rank_h1=6, course_rank_q1=2, course_rank_q3=6, rank=6, course_wpct_diff=-0.127

## P91: 前半の勝ちが（他球団より）接戦に偏ったチームは、後半に失点が増える（他球団と比べて）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 42 件: d-2022, db-2021, m-2015, db-2022, h-2012 ほか
- もし: `course_close_win_h1_d > 0` ならば: `course_ra_d > 0`
- 識別子: `[all] course_close_win_h1_d>0 => course_ra_d>0`（指紋 `f91eb617270eb2ae`）
- 兄弟（範囲と結論が同じ、条件が違う）: P93, P170
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）
- 注記: 投手の負担の見立て。P93（前半の失点が少なかったことからの戻り）と並べて読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 78 | 36 | 0.46 [0.36, 0.57] | -0.68σ（0.286） | 0.51 | 0.91 | 0.900 | 0 | 判断保留 | 4 |
| 対偶 | 77 | 35 | 0.45 [0.35, 0.57] | -0.80σ（0.247） | 0.50 | 0.91 | 0.900 | 0 | 判断保留 | 4 |
| 逆 | 79 | 36 | 0.46 [0.35, 0.57] | -0.79σ（0.250） | 0.50 | 0.91 | 0.900 | 0 | 判断保留 | 4 |
| 裏 | 78 | 35 | 0.45 [0.34, 0.56] | -0.91σ（0.214） | 0.49 | 0.91 | 0.900 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 42 件（対偶の判例も同じ）

- 中日 2022 **(focus)**: course_close_win_h1_d=0.120, course_ra_d=-1.18, course_close_win_h1=0.633, course_ra_h1_d=0.335, course_wpct_diff=0.092, rank_ra=2 / surprise=-1.18
  - 中日 2022 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- DeNA 2021: course_close_win_h1_d=0.003, course_ra_d=-1.09, course_close_win_h1=0.478, course_ra_h1_d=+1.21, course_wpct_diff=0.106, rank_ra=6 / surprise=-1.09
  - DeNA 2021 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- ロッテ 2015: course_close_win_h1_d=0.051, course_ra_d=-1.01, course_close_win_h1=0.500, course_ra_h1_d=0.524, course_wpct_diff=0.014, rank_ra=3 / surprise=-1.01
  - ロッテ 2015 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- DeNA 2022: course_close_win_h1_d=0.087, course_ra_d=-1.00, course_close_win_h1=0.606, course_ra_h1_d=0.572, course_wpct_diff=0.107, rank_ra=3 / surprise=-1.00
  - DeNA 2022 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- ソフトバンク 2012: course_close_win_h1_d=0.063, course_ra_d=-0.969, course_close_win_h1=0.613, course_ra_h1_d=0.044, course_wpct_diff=0.076, rank_ra=1 / surprise=-0.969
  - ソフトバンク 2012 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- ロッテ 2017: course_close_win_h1_d=0.061, course_ra_d=-0.960, course_close_win_h1=0.545, course_ra_h1_d=+1.14, course_wpct_diff=0.136, rank_ra=6 / surprise=-0.960
  - ロッテ 2017 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- オリックス 2016: course_close_win_h1_d=0.203, course_ra_d=-0.939, course_close_win_h1=0.692, course_ra_h1_d=0.997, course_wpct_diff=0.083, rank_ra=5 / surprise=-0.939
  - オリックス 2016 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- DeNA 2014: course_close_win_h1_d=0.124, course_ra_d=-0.914, course_close_win_h1=0.533, course_ra_h1_d=0.508, course_wpct_diff=0.112, rank_ra=5 / surprise=-0.914
  - DeNA 2014 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- 巨人 2017: course_close_win_h1_d=0.013, course_ra_d=-0.859, course_close_win_h1=0.484, course_ra_h1_d=-0.158, course_wpct_diff=0.158, rank_ra=1 / surprise=-0.859
  - 巨人 2017 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- オリックス 2013: course_close_win_h1_d=0.095, course_ra_d=-0.850, course_close_win_h1=0.515, course_ra_h1_d=0.142, course_wpct_diff=0.007, rank_ra=1 / surprise=-0.850
  - オリックス 2013 は「course_close_win_h1_d > 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H3, H6
- ほか 32 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 43 件（裏の判例も同じ）

- DeNA 2016: course_close_win_h1_d=-0.032, course_ra_d=+1.41, course_close_win_h1=0.469, course_ra_h1_d=-0.589, course_wpct_diff=0.043, rank_ra=5 / surprise=+1.41
  - DeNA 2016 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- ヤクルト 2022: course_close_win_h1_d=-0.053, course_ra_d=+1.28, course_close_win_h1=0.489, course_ra_h1_d=-0.307, course_wpct_diff=-0.193, rank_ra=5 / surprise=+1.28
  - ヤクルト 2022 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 巨人 2021: course_close_win_h1_d=-0.071, course_ra_d=+1.02, course_close_win_h1=0.417, course_ra_h1_d=-0.546, course_wpct_diff=-0.187, rank_ra=4 / surprise=+1.02
  - 巨人 2021 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 西武 2013: course_close_win_h1_d=-0.057, course_ra_d=0.833, course_close_win_h1=0.389, course_ra_h1_d=-0.425, course_wpct_diff=0.044, rank_ra=3 / surprise=0.833
  - 西武 2013 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 広島 2024: course_close_win_h1_d=-0.066, course_ra_d=0.752, course_close_win_h1=0.486, course_ra_h1_d=-0.718, course_wpct_diff=-0.116, rank_ra=2 / surprise=0.752
  - 広島 2024 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 日本ハム 2023: course_close_win_h1_d=-0.094, course_ra_d=0.688, course_close_win_h1=0.455, course_ra_h1_d=-0.346, course_wpct_diff=-0.085, rank_ra=3 / surprise=0.688
  - 日本ハム 2023 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- ロッテ 2016: course_close_win_h1_d=-0.013, course_ra_d=0.662, course_close_win_h1=0.512, course_ra_h1_d=-0.254, course_wpct_diff=-0.143, rank_ra=3 / surprise=0.662
  - ロッテ 2016 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 楽天 2014: course_close_win_h1_d=-0.149, course_ra_d=0.614, course_close_win_h1=0.276, course_ra_h1_d=-0.003, course_wpct_diff=0.083, rank_ra=5 / surprise=0.614
  - 楽天 2014 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 西武 2017: course_close_win_h1_d=-0.172, course_ra_d=0.611, course_close_win_h1=0.351, course_ra_h1_d=-0.380, course_wpct_diff=0.055, rank_ra=3 / surprise=0.611
  - 西武 2017 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 広島 2025: course_close_win_h1_d=-0.099, course_ra_d=0.553, course_close_win_h1=0.457, course_ra_h1_d=-0.014, course_wpct_diff=-0.172, rank_ra=5 / surprise=0.553
  - 広島 2025 は「course_ra_d > 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- ほか 33 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: course_close_win_h1_d=0.169, course_ra_d=-0.830, course_close_win_h1=0.606, course_ra_h1_d=0.267, course_wpct_diff=-0.111, rank_ra=2
- ヤクルト 2020: course_close_win_h1_d=0.082, course_ra_d=-0.787, course_close_win_h1=0.458, course_ra_h1_d=+1.35, course_wpct_diff=-0.127, rank_ra=6

## P92: 前半の勝ちが（他球団より）接戦に偏ったチームは、後半の勝率が前半より下がる

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 40 件: c-2021, s-2025, e-2023, g-2017, m-2017 ほか
- もし: `course_close_win_h1_d > 0` ならば: `course_wpct_diff < 0`
- 識別子: `[all] course_close_win_h1_d>0 => course_wpct_diff<0`（指紋 `6b996f06deab176f`）
- 兄弟（範囲と結論が同じ、条件が違う）: P94
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）
- 注記: P94（前半の出来すぎからの戻り）と並べて読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 78 | 38 | 0.49 [0.38, 0.60] | -0.23σ（0.455） | 0.46 | 1.07 | 0.260 | 0 | 判断保留 | 4 |
| 対偶 | 85 | 45 | 0.53 [0.42, 0.63] | +0.54σ（0.332） | 0.50 | 1.06 | 0.260 | 0 | 判断保留 | 4 |
| 逆 | 71 | 38 | 0.54 [0.42, 0.65] | +0.59σ（0.318） | 0.50 | 1.07 | 0.260 | 0 | 判断保留 | 4 |
| 裏 | 78 | 45 | 0.58 [0.47, 0.68] | +1.36σ（0.106） | 0.54 | 1.06 | 0.260 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 40 件（対偶の判例も同じ）

- 広島 2021: course_close_win_h1_d=0.055, course_wpct_diff=0.209, course_close_win_h1=0.522, half1_vs_pythag=-1.35, course_ra_d=-0.534, rank=4 / surprise=0.209
  - 広島 2021 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- ヤクルト 2025: course_close_win_h1_d=0.038, course_wpct_diff=0.208, course_close_win_h1=0.571, half1_vs_pythag=0.280, course_ra_d=-0.714, rank=6 / surprise=0.208
  - ヤクルト 2025 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- 楽天 2023: course_close_win_h1_d=0.023, course_wpct_diff=0.163, course_close_win_h1=0.552, half1_vs_pythag=+2.19, course_ra_d=-0.628, rank=4 / surprise=0.163
  - 楽天 2023 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- 巨人 2017: course_close_win_h1_d=0.013, course_wpct_diff=0.158, course_close_win_h1=0.484, half1_vs_pythag=+1.34, course_ra_d=-0.859, rank=4 / surprise=0.158
  - 巨人 2017 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- ロッテ 2017: course_close_win_h1_d=0.061, course_wpct_diff=0.136, course_close_win_h1=0.545, half1_vs_pythag=0.990, course_ra_d=-0.960, rank=6 / surprise=0.136
  - ロッテ 2017 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- 日本ハム 2021: course_close_win_h1_d=0.060, course_wpct_diff=0.136, course_close_win_h1=0.500, half1_vs_pythag=0.575, course_ra_d=-0.798, rank=5 / surprise=0.136
  - 日本ハム 2021 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- 巨人 2024: course_close_win_h1_d=0.041, course_wpct_diff=0.129, course_close_win_h1=0.576, half1_vs_pythag=-1.40, course_ra_d=-0.654, rank=1 / surprise=0.129
  - 巨人 2024 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- ソフトバンク 2018: course_close_win_h1_d=0.056, course_wpct_diff=0.113, course_close_win_h1=0.459, half1_vs_pythag=0.403, course_ra_d=-0.395, rank=2 / surprise=0.113
  - ソフトバンク 2018 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- DeNA 2014: course_close_win_h1_d=0.124, course_wpct_diff=0.112, course_close_win_h1=0.533, half1_vs_pythag=+3.26, course_ra_d=-0.914, rank=5 / surprise=0.112
  - DeNA 2014 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- DeNA 2022: course_close_win_h1_d=0.087, course_wpct_diff=0.107, course_close_win_h1=0.606, half1_vs_pythag=+2.65, course_ra_d=-1.00, rank=2 / surprise=0.107
  - DeNA 2022 は「course_close_win_h1_d > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H3, H6
- ほか 30 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 33 件（裏の判例も同じ）

- 楽天 2017: course_close_win_h1_d=-0.019, course_wpct_diff=-0.214, course_close_win_h1=0.478, half1_vs_pythag=+1.29, course_ra_d=0.480, rank=3 / surprise=-0.214
  - 楽天 2017 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- ソフトバンク 2016: course_close_win_h1_d=-0.041, course_wpct_diff=-0.205, course_close_win_h1=0.489, half1_vs_pythag=+2.89, course_ra_d=0.288, rank=2 / surprise=-0.205
  - ソフトバンク 2016 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- ヤクルト 2022: course_close_win_h1_d=-0.053, course_wpct_diff=-0.193, course_close_win_h1=0.489, half1_vs_pythag=+3.83, course_ra_d=+1.28, rank=1 / surprise=-0.193
  - ヤクルト 2022 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 巨人 2021: course_close_win_h1_d=-0.071, course_wpct_diff=-0.187, course_close_win_h1=0.417, half1_vs_pythag=0.749, course_ra_d=+1.02, rank=3 / surprise=-0.187
  - 巨人 2021 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 広島 2025: course_close_win_h1_d=-0.099, course_wpct_diff=-0.172, course_close_win_h1=0.457, half1_vs_pythag=-1.22, course_ra_d=0.553, rank=5 / surprise=-0.172
  - 広島 2025 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- ロッテ 2016: course_close_win_h1_d=-0.013, course_wpct_diff=-0.143, course_close_win_h1=0.512, half1_vs_pythag=0.839, course_ra_d=0.662, rank=3 / surprise=-0.143
  - ロッテ 2016 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 西武 2015: course_close_win_h1_d=-0.044, course_wpct_diff=-0.131, course_close_win_h1=0.421, half1_vs_pythag=0.952, course_ra_d=0.194, rank=4 / surprise=-0.131
  - 西武 2015 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- オリックス 2014: course_close_win_h1_d=-0.027, course_wpct_diff=-0.125, course_close_win_h1=0.378, half1_vs_pythag=-0.886, course_ra_d=0.181, rank=2 / surprise=-0.125
  - オリックス 2014 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- 広島 2024: course_close_win_h1_d=-0.066, course_wpct_diff=-0.116, course_close_win_h1=0.486, half1_vs_pythag=-3.18, course_ra_d=0.752, rank=4 / surprise=-0.116
  - 広島 2024 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- ソフトバンク 2024: course_close_win_h1_d=-0.078, course_wpct_diff=-0.109, course_close_win_h1=0.458, half1_vs_pythag=-3.05, course_ra_d=0.514, rank=1 / surprise=-0.109
  - ソフトバンク 2024 は「course_wpct_diff < 0」を満たすのに「course_close_win_h1_d > 0」を満たさない。なぜか？ → H3, H6
- ほか 23 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: course_close_win_h1_d=0.040, course_wpct_diff=0.112, course_close_win_h1=0.423, half1_vs_pythag=+3.26, course_ra_d=0.093, rank=3
- 西武 2020: course_close_win_h1_d=0.042, course_wpct_diff=0.103, course_close_win_h1=0.500, half1_vs_pythag=-1.43, course_ra_d=0.370, rank=3

## P93: 前半の失点が他球団より少なかったチームは、後半に失点が増える（他球団と比べて）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 26 件: h-2025, g-2017, g-2024, c-2016, c-2013 ほか
- もし: `course_ra_h1_d < 0` ならば: `course_ra_d > 0`
- 識別子: `[all] course_ra_h1_d<0 => course_ra_d>0`（指紋 `3c0a4996189b7b29`）
- 兄弟（範囲と結論が同じ、条件が違う）: P91, P170
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）
- 注記: P91 の対照（前半の水準からの戻り）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 83 | 57 | 0.69 [0.58, 0.78] | +3.40σ（0.000） | 0.51 | 1.36 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 77 | 51 | 0.66 [0.55, 0.76] | +2.85σ（0.003） | 0.47 | 1.42 | 0.000 | 0 | 支持 | 1 |
| 逆 | 79 | 57 | 0.72 [0.61, 0.81] | +3.94σ（0.000） | 0.53 | 1.36 | 0.000 | 0 | 支持 | 1 |
| 裏 | 73 | 51 | 0.70 [0.59, 0.79] | +3.39σ（0.000） | 0.49 | 1.42 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 26 件（対偶の判例も同じ）

- ソフトバンク 2025: course_ra_h1_d=-0.163, course_ra_d=-1.14, course_close_win_h1_d=-0.097, rank_ra=1 / surprise=-1.14
  - ソフトバンク 2025 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- 巨人 2017: course_ra_h1_d=-0.158, course_ra_d=-0.859, course_close_win_h1_d=0.013, rank_ra=1 / surprise=-0.859
  - 巨人 2017 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- 巨人 2024: course_ra_h1_d=-0.330, course_ra_d=-0.654, course_close_win_h1_d=0.041, rank_ra=1 / surprise=-0.654
  - 巨人 2024 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- 広島 2016: course_ra_h1_d=-0.369, course_ra_d=-0.542, course_close_win_h1_d=-0.145, rank_ra=1 / surprise=-0.542
  - 広島 2016 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- 広島 2013: course_ra_h1_d=-0.039, course_ra_d=-0.458, course_close_win_h1_d=0.067, rank_ra=3 / surprise=-0.458
  - 広島 2013 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- 阪神 2019: course_ra_h1_d=-0.132, course_ra_d=-0.398, course_close_win_h1_d=0.133, rank_ra=2 / surprise=-0.398
  - 阪神 2019 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- 中日 2019 **(focus)**: course_ra_h1_d=-0.318, course_ra_d=-0.396, course_close_win_h1_d=0.025, rank_ra=1 / surprise=-0.396
  - 中日 2019 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- オリックス 2023: course_ra_h1_d=-0.380, course_ra_d=-0.378, course_close_win_h1_d=-0.113, rank_ra=1 / surprise=-0.378
  - オリックス 2023 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- 広島 2015: course_ra_h1_d=-0.166, course_ra_d=-0.345, course_close_win_h1_d=-0.175, rank_ra=2 / surprise=-0.345
  - 広島 2015 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- 西武 2023: course_ra_h1_d=-0.093, course_ra_d=-0.332, course_close_win_h1_d=0.064, rank_ra=2 / surprise=-0.332
  - 西武 2023 は「course_ra_h1_d < 0」を満たすのに「course_ra_d > 0」を満たさない。なぜか？ → H6
- ほか 16 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 22 件（裏の判例も同じ）

- 中日 2017 **(focus)**: course_ra_h1_d=0.028, course_ra_d=0.755, course_close_win_h1_d=0.168, rank_ra=5 / surprise=0.755
  - 中日 2017 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- ヤクルト 2017: course_ra_h1_d=0.299, course_ra_d=0.718, course_close_win_h1_d=0.032, rank_ra=6 / surprise=0.718
  - ヤクルト 2017 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- オリックス 2012: course_ra_h1_d=0.061, course_ra_d=0.597, course_close_win_h1_d=0.013, rank_ra=6 / surprise=0.597
  - オリックス 2012 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- 西武 2021: course_ra_h1_d=0.217, course_ra_d=0.569, course_close_win_h1_d=0.039, rank_ra=6 / surprise=0.569
  - 西武 2021 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- DeNA 2012: course_ra_h1_d=0.689, course_ra_d=0.539, course_close_win_h1_d=0.064, rank_ra=6 / surprise=0.539
  - DeNA 2012 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- 楽天 2025: course_ra_h1_d=0.158, course_ra_d=0.506, course_close_win_h1_d=0.057, rank_ra=5 / surprise=0.506
  - 楽天 2025 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- DeNA 2015: course_ra_h1_d=0.459, course_ra_d=0.480, course_close_win_h1_d=0.092, rank_ra=6 / surprise=0.480
  - DeNA 2015 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- ヤクルト 2024: course_ra_h1_d=0.583, course_ra_d=0.450, course_close_win_h1_d=-0.090, rank_ra=6 / surprise=0.450
  - ヤクルト 2024 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- 巨人 2022: course_ra_h1_d=0.335, course_ra_d=0.384, course_close_win_h1_d=0.041, rank_ra=6 / surprise=0.384
  - 巨人 2022 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- オリックス 2017: course_ra_h1_d=0.059, course_ra_d=0.371, course_close_win_h1_d=0.243, rank_ra=5 / surprise=0.371
  - オリックス 2017 は「course_ra_d > 0」を満たすのに「course_ra_h1_d < 0」を満たさない。なぜか？ → H6
- ほか 12 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ソフトバンク 2020: course_ra_h1_d=-0.913, course_ra_d=-0.270, course_close_win_h1_d=-0.009, rank_ra=1
- 阪神 2020: course_ra_h1_d=-0.233, course_ra_d=-0.207, course_close_win_h1_d=-0.054, rank_ra=2

## P94: 前半に得失点からの見込みより多く勝っていたチームは、後半の勝率が前半より下がる

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 36 件: s-2025, e-2023, g-2017, m-2017, f-2021 ほか
- もし: `half1_vs_pythag > 0` ならば: `course_wpct_diff < 0`
- 識別子: `[all] half1_vs_pythag>0 => course_wpct_diff<0`（指紋 `29f4473163e711e5`）
- 兄弟（範囲と結論が同じ、条件が違う）: P92
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: lift が 1 に近い（Fisher の p ≥ 0.05）
- 注記: P92 の対照（前半の出来すぎからの戻り）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 86 | 50 | 0.58 [0.48, 0.68] | +1.51σ（0.080） | 0.46 | 1.28 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 85 | 49 | 0.58 [0.47, 0.68] | +1.41σ（0.096） | 0.45 | 1.28 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 71 | 50 | 0.70 [0.59, 0.80] | +3.44σ（0.000） | 0.55 | 1.28 | 0.000 | 0 | 支持 | 1 |
| 裏 | 70 | 49 | 0.70 [0.58, 0.79] | +3.35σ（0.001） | 0.54 | 1.28 | 0.000 | 0 | 支持 | 1 |

**待った！判断保留** 元の命題に判例 36 件（対偶の判例も同じ）

- ヤクルト 2025: half1_vs_pythag=0.280, course_wpct_diff=0.208, half2_vs_pythag=+3.74, course_close_win_h1_d=0.038 / surprise=0.208
  - ヤクルト 2025 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- 楽天 2023: half1_vs_pythag=+2.19, course_wpct_diff=0.163, half2_vs_pythag=+2.68, course_close_win_h1_d=0.023 / surprise=0.163
  - 楽天 2023 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- 巨人 2017: half1_vs_pythag=+1.34, course_wpct_diff=0.158, half2_vs_pythag=-2.31, course_close_win_h1_d=0.013 / surprise=0.158
  - 巨人 2017 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- ロッテ 2017: half1_vs_pythag=0.990, course_wpct_diff=0.136, half2_vs_pythag=0.940, course_close_win_h1_d=0.061 / surprise=0.136
  - ロッテ 2017 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- 日本ハム 2021: half1_vs_pythag=0.575, course_wpct_diff=0.136, half2_vs_pythag=-0.444, course_close_win_h1_d=0.060 / surprise=0.136
  - 日本ハム 2021 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- ソフトバンク 2018: half1_vs_pythag=0.403, course_wpct_diff=0.113, half2_vs_pythag=0.365, course_close_win_h1_d=0.056 / surprise=0.113
  - ソフトバンク 2018 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- 西武 2012: half1_vs_pythag=0.610, course_wpct_diff=0.113, half2_vs_pythag=+4.05, course_close_win_h1_d=-0.018 / surprise=0.113
  - 西武 2012 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- DeNA 2014: half1_vs_pythag=+3.26, course_wpct_diff=0.112, half2_vs_pythag=-1.70, course_close_win_h1_d=0.124 / surprise=0.112
  - DeNA 2014 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- DeNA 2022: half1_vs_pythag=+2.65, course_wpct_diff=0.107, half2_vs_pythag=+4.06, course_close_win_h1_d=0.087 / surprise=0.107
  - DeNA 2022 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- 広島 2013: half1_vs_pythag=0.793, course_wpct_diff=0.106, half2_vs_pythag=-2.00, course_close_win_h1_d=0.067 / surprise=0.106
  - 広島 2013 は「half1_vs_pythag > 0」を満たすのに「course_wpct_diff < 0」を満たさない。なぜか？ → H2, H6
- ほか 26 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 21 件（裏の判例も同じ）

- 広島 2025: half1_vs_pythag=-1.22, course_wpct_diff=-0.172, half2_vs_pythag=-1.75, course_close_win_h1_d=-0.099 / surprise=-0.172
  - 広島 2025 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- ヤクルト 2017: half1_vs_pythag=-0.668, course_wpct_diff=-0.161, half2_vs_pythag=-4.98, course_close_win_h1_d=0.032 / surprise=-0.161
  - ヤクルト 2017 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- オリックス 2014: half1_vs_pythag=-0.886, course_wpct_diff=-0.125, half2_vs_pythag=-4.41, course_close_win_h1_d=-0.027 / surprise=-0.125
  - オリックス 2014 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- 広島 2024: half1_vs_pythag=-3.18, course_wpct_diff=-0.116, half2_vs_pythag=+1.79, course_close_win_h1_d=-0.066 / surprise=-0.116
  - 広島 2024 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- ソフトバンク 2024: half1_vs_pythag=-3.05, course_wpct_diff=-0.109, half2_vs_pythag=-2.44, course_close_win_h1_d=-0.078 / surprise=-0.109
  - ソフトバンク 2024 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- ソフトバンク 2014: half1_vs_pythag=-1.83, course_wpct_diff=-0.087, half2_vs_pythag=+1.61, course_close_win_h1_d=0.034 / surprise=-0.087
  - ソフトバンク 2014 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- 日本ハム 2023: half1_vs_pythag=-3.50, course_wpct_diff=-0.085, half2_vs_pythag=-3.53, course_close_win_h1_d=-0.094 / surprise=-0.085
  - 日本ハム 2023 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- ソフトバンク 2021: half1_vs_pythag=-3.35, course_wpct_diff=-0.065, half2_vs_pythag=-4.89, course_close_win_h1_d=-0.020 / surprise=-0.065
  - ソフトバンク 2021 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- ソフトバンク 2022: half1_vs_pythag=-2.39, course_wpct_diff=-0.064, half2_vs_pythag=-2.76, course_close_win_h1_d=-0.149 / surprise=-0.064
  - ソフトバンク 2022 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- 阪神 2012: half1_vs_pythag=-1.96, course_wpct_diff=-0.059, half2_vs_pythag=-4.13, course_close_win_h1_d=0.048 / surprise=-0.059
  - 阪神 2012 は「course_wpct_diff < 0」を満たすのに「half1_vs_pythag > 0」を満たさない。なぜか？ → H2, H6
- ほか 11 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: half1_vs_pythag=+3.26, course_wpct_diff=0.112, half2_vs_pythag=+6.09, course_close_win_h1_d=0.040
- ソフトバンク 2020: half1_vs_pythag=0.950, course_wpct_diff=0.063, half2_vs_pythag=-1.47, course_close_win_h1_d=-0.009

## P95: 得点・失点の分布から見た A クラスの見込みが4割未満、または組み合わせ方が基準より不利（alloc_z_strat < −1）、または強い相手との試合で点の差どおりに勝てていない（opp_conv_top < −2）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 18 件: g-2018, t-2022, t-2014, e-2019, g-2012 ほか
- もし: `（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）` ならば: `upper_half == False`
- 識別子: `[all] ((alloc_z_strat<-1) | (opp_conv_top<-2) | (sim_p_upper<0.4)) => upper_half==false`（指紋 `2705568c057ad20f`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P96, P115, P126, P138, P147, P148, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 親: P52（変更: 式1が取りこぼした 2014年の道筋（R17、強い相手との試合で点の差どおりに勝てていない）を3つ目の組として足した。閾値 −2 は中日 2014 の −2.57 を見て決めた）
- 見直す条件（反証）: 中日 2014 を除いて、P52 より Matthews 相関が上がらない（B クラスの取りこぼしの減りより、A クラスの誤りの増えが大きい）
- 注記: 言いにくいが確実に選ぶ式の候補。P52 と並べて読む。原因ではなく、どこで勝ちを落としたかの説明
- 条件の数: 4（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 15 回、元の命題に異議あり 15 回（どれかの形に異議あり 15 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 93 | 75 | 0.81 [0.71, 0.87] | +1.26σ（0.126） | 0.50 | 1.61 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 60 | 0.77 [0.66, 0.85] | +0.39σ（0.405） | 0.40 | 1.90 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 78 | 75 | 0.96 [0.89, 0.99] | +4.31σ（0.000） | 0.60 | 1.61 | 0.000 | 0 | 支持 | 1 |
| 裏 | 63 | 60 | 0.95 [0.87, 0.98] | +3.71σ（0.000） | 0.50 | 1.90 | 0.000 | 0 | 支持 | 1 |

**待った！判断保留** 元の命題に判例 18 件（対偶の判例も同じ）

- 巨人 2018: sim_p_upper=0.817, alloc_z_strat=-1.75, opp_conv_top=-5.84, upper_half=True, rank=3, rd=50 / surprise=-5.84
  - 巨人 2018 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 阪神 2022: sim_p_upper=0.832, alloc_z_strat=-2.14, opp_conv_top=-5.18, upper_half=True, rank=3, rd=61 / surprise=-5.18
  - 阪神 2022 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 阪神 2014: sim_p_upper=0.293, alloc_z_strat=+2.46, opp_conv_top=+4.01, upper_half=True, rank=2, rd=-15 / surprise=+4.01
  - 阪神 2014 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 楽天 2019: sim_p_upper=0.726, alloc_z_strat=-0.950, opp_conv_top=-3.07, upper_half=True, rank=3, rd=36 / surprise=-3.07
  - 楽天 2019 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 巨人 2012: sim_p_upper=1.000, alloc_z_strat=+1.43, opp_conv_top=-2.56, upper_half=True, rank=1, rd=180 / surprise=-2.56
  - 巨人 2012 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 日本ハム 2016: sim_p_upper=0.995, alloc_z_strat=0.528, opp_conv_top=-2.51, upper_half=True, rank=1, rd=152 / surprise=-2.51
  - 日本ハム 2016 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- ヤクルト 2021: sim_p_upper=0.958, alloc_z_strat=0.733, opp_conv_top=-2.51, upper_half=True, rank=1, rd=94 / surprise=-2.51
  - ヤクルト 2021 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 日本ハム 2012: sim_p_upper=0.942, alloc_z_strat=-0.890, opp_conv_top=-2.45, upper_half=True, rank=1, rd=60 / surprise=-2.45
  - 日本ハム 2012 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- 日本ハム 2014: sim_p_upper=0.740, alloc_z_strat=-0.215, opp_conv_top=-2.29, upper_half=True, rank=3, rd=24 / surprise=-2.29
  - 日本ハム 2014 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- ソフトバンク 2018: sim_p_upper=0.971, alloc_z_strat=-0.039, opp_conv_top=-2.25, upper_half=True, rank=2, rd=106 / surprise=-2.25
  - ソフトバンク 2018 は「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9
- ほか 8 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 3 件（裏の判例も同じ）

- 広島 2019: sim_p_upper=0.487, alloc_z_strat=0.232, opp_conv_top=+4.37, upper_half=False, rank=4, rd=-10 / surprise=+4.37
  - 広島 2019 は「upper_half == False」を満たすのに「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たさない。なぜか？ → H2, H3, H9
- 楽天 2012: sim_p_upper=0.425, alloc_z_strat=0.135, opp_conv_top=+1.69, upper_half=False, rank=4, rd=24 / surprise=+1.69
  - 楽天 2012 は「upper_half == False」を満たすのに「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たさない。なぜか？ → H2, H3, H9
- 阪神 2016: sim_p_upper=0.438, alloc_z_strat=-0.594, opp_conv_top=-0.285, upper_half=False, rank=4, rd=-40 / surprise=-0.285
  - 阪神 2016 は「upper_half == False」を満たすのに「（[sim_p_upper < 0.4] または [alloc_z_strat < -1] または [opp_conv_top < -2]）」を満たさない。なぜか？ → H2, H3, H9

**きっかけ以外での判定**（作り直しのきっかけ d-2014 を除く）: n=92 成立=74 成立率=0.80 [0.71, 0.87] → **判断保留** / 判例: g-2018, t-2022, t-2014, e-2019, g-2012, f-2016, s-2021, f-2012, f-2014, h-2018

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: sim_p_upper=0.371, alloc_z_strat=+1.36, opp_conv_top=+3.76, upper_half=True, rank=3, rd=-60
- 西武 2020: sim_p_upper=0.200, alloc_z_strat=+2.26, opp_conv_top=+1.88, upper_half=True, rank=3, rd=-64

## P96: 得失点差が −50 未満、または分布から見た A クラスの見込みが5割未満で期待勝利数を下回った、または得失点差が +50 未満で組み合わせ方が基準より不利なら、B クラス（誤りのほとんどない式）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 1 件: t-2015
- もし: `（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）` ならば: `upper_half == False`
- 識別子: `[all] ((alloc_z_strat<-1 & rd<50) | (rd<-50) | (sim_p_upper<0.5 & wins_vs_pythag<0)) => upper_half==false`（指紋 `bdb05c59ec6f9d12`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P115, P126, P138, P147, P148, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 2026年（R18）で、この式に当たるのに A クラスのチームが出る（学習データでは156単位中1）
- 注記: R21 の探索の1位（結果を見た後の式）。P52（取りこぼしが少ない）と並べる、言い当て方の違う式。同じデータでの成績は良く見えやすい
- 条件の数: 6（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 14 回、元の命題に異議あり 14 回（どれかの形に異議あり 14 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 69 | 68 | 0.99 [0.92, 1.00] | +4.52σ（0.000） | 0.50 | 1.97 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 77 | 0.99 [0.93, 1.00] | +4.84σ（0.000） | 0.56 | 1.77 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 68 | 0.87 [0.78, 0.93] | +2.48σ（0.006） | 0.44 | 1.97 | 0.000 | 0 | 支持 | 1 |
| 裏 | 87 | 77 | 0.89 [0.80, 0.94] | +2.91σ（0.001） | 0.50 | 1.77 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 1 件（対偶の判例も同じ）

- 阪神 2015: rd=-85, sim_p_upper=0.234, wins_vs_pythag=+10.25, alloc_z_strat=+1.44, upper_half=True, rank=3 / surprise=-85
  - 阪神 2015 は「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2, H3, H9

**異議あり（例外あり）** 逆に判例 10 件（裏の判例も同じ）

- ソフトバンク 2013: rd=98, sim_p_upper=0.885, wins_vs_pythag=-8.37, alloc_z_strat=-2.21, upper_half=False, rank=4 / surprise=98
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- ソフトバンク 2021: rd=71, sim_p_upper=0.833, wins_vs_pythag=-8.47, alloc_z_strat=-2.48, upper_half=False, rank=4 / surprise=71
  - ソフトバンク 2021 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 西武 2015: rd=58, sim_p_upper=0.680, wins_vs_pythag=-6.07, alloc_z_strat=-1.04, upper_half=False, rank=4 / surprise=58
  - 西武 2015 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 楽天 2023: rd=-43, sim_p_upper=0.319, wins_vs_pythag=+4.68, alloc_z_strat=0.951, upper_half=False, rank=4 / surprise=-43
  - 楽天 2023 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 巨人 2022: rd=-41, sim_p_upper=0.279, wins_vs_pythag=+2.61, alloc_z_strat=0.669, upper_half=False, rank=4 / surprise=-41
  - 巨人 2022 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- ロッテ 2022: rd=-35, sim_p_upper=0.337, wins_vs_pythag=+2.38, alloc_z_strat=-0.219, upper_half=False, rank=5 / surprise=-35
  - ロッテ 2022 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 広島 2021: rd=-32, sim_p_upper=0.272, wins_vs_pythag=0.845, alloc_z_strat=0.385, upper_half=False, rank=4 / surprise=-32
  - 広島 2021 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 中日 2014 **(focus)**: rd=-20, sim_p_upper=0.543, wins_vs_pythag=-0.792, alloc_z_strat=-0.752, upper_half=False, rank=4 / surprise=-20
  - 中日 2014 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 巨人 2023: rd=16, sim_p_upper=0.738, wins_vs_pythag=-1.50, alloc_z_strat=-0.914, upper_half=False, rank=4 / surprise=16
  - 巨人 2023 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9
- 広島 2019: rd=-10, sim_p_upper=0.487, wins_vs_pythag=+1.07, alloc_z_strat=0.232, upper_half=False, rank=4 / surprise=-10
  - 広島 2019 は「upper_half == False」を満たすのに「（[rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < 50 かつ alloc_z_strat < -1]）」を満たさない。なぜか？ → H2, H3, H9

**除外中の判例**（統計からは除いたが、判例としては残す）

- 西武 2020: rd=-64, sim_p_upper=0.200, wins_vs_pythag=+6.63, alloc_z_strat=+2.26, upper_half=True, rank=3
- 中日 2020 **(focus)**: rd=-60, sim_p_upper=0.371, wins_vs_pythag=+9.35, alloc_z_strat=+1.36, upper_half=True, rank=3
- 阪神 2020: rd=34, sim_p_upper=0.464, wins_vs_pythag=-0.181, alloc_z_strat=+1.05, upper_half=True, rank=2

## P97: 中日の B クラスの年は、順位の高さの線（3次式でならしたもの）に山がある（上がってから下がる）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: d-2015, d-2018, d-2022, d-2025
- もし: `（すべての単位）` ならば: `traj_rank_peak == True`
- 識別子: `[team=d, where:upper_half==false] * => traj_rank_peak==true`（指紋 `005c9c87c0994d34`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd', 'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 12
- 見直す条件（反証）: 中日の B クラスの年の山の数が、力が一定のときの見込みの範囲（trajectory_expectation.jsonl で P ≥ 0.05）
- 注記: 山があること自体は力が一定でも起きる。基準と比べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 13 回、元の命題に異議あり 13 回（どれかの形に異議あり 13 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 8 | 0.67 [0.39, 0.86] | +1.15σ（0.194） | 0.67 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | -2.00σ（0.062） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 中日 2015 **(focus)**: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.735, traj_rank_end_slope=+7.38, rank=5
  - 中日 2015 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 中日 2018 **(focus)**: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.665, traj_rank_end_slope=+5.15, rank=5
  - 中日 2018 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 中日 2022 **(focus)**: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.760, traj_rank_end_slope=+6.23, rank=6
  - 中日 2022 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 中日 2025 **(focus)**: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.730, traj_rank_end_slope=+2.77, rank=4
  - 中日 2025 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6

## P98: 中日以外の B クラスのチームは、順位の高さの線に山がある

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 14 件: t-2012, db-2013, e-2014, e-2015, l-2016 ほか
- もし: `（すべての単位）` ならば: `traj_rank_peak == True`
- 識別子: `[where:team!="d", where:upper_half==false] * => traj_rank_peak==true`（指紋 `278cf7178bc42e34`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 66
- 見直す条件（反証）: （基準の命題。P97 と率を比べるために置く）
- 注記: P97 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 13 回、元の命題に異議あり 13 回（どれかの形に異議あり 13 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 66 | 52 | 0.79 [0.67, 0.87] | +4.68σ（0.000） | 0.79 | 1.00 | 1.000 | 0 | 支持 | 1 |
| 対偶 | 14 | 0 | 0.00 [0.00, 0.22] | -3.74σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（例外あり）** 元の命題に判例 14 件（対偶の判例も同じ）

- 阪神 2012: traj_rank_peak=False, traj_rank_shape=fall, traj_rank_peak_base=0.765, traj_rank_end_slope=-0.447, rank=5
  - 阪神 2012 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- DeNA 2013: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.735, traj_rank_end_slope=+2.18, rank=5
  - DeNA 2013 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 楽天 2014: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.725, traj_rank_end_slope=+7.87, rank=6
  - 楽天 2014 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 楽天 2015: traj_rank_peak=False, traj_rank_shape=fall, traj_rank_peak_base=0.665, traj_rank_end_slope=-7.49, rank=6
  - 楽天 2015 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 西武 2016: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.760, traj_rank_end_slope=+5.81, rank=4
  - 西武 2016 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- ヤクルト 2016: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.685, traj_rank_end_slope=+3.97, rank=5
  - ヤクルト 2016 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- ヤクルト 2017: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.520, traj_rank_end_slope=+1.68, rank=6
  - ヤクルト 2017 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 阪神 2018: traj_rank_peak=False, traj_rank_shape=fall, traj_rank_peak_base=0.645, traj_rank_end_slope=-9.26, rank=6
  - 阪神 2018 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- ヤクルト 2019: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.680, traj_rank_end_slope=+1.45, rank=6
  - ヤクルト 2019 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 広島 2021: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.795, traj_rank_end_slope=+9.13, rank=4
  - 広島 2021 は「（すべての単位）」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- ほか 4 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- オリックス 2020: traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.645, traj_rank_end_slope=+1.45, rank=6
- 楽天 2020: traj_rank_peak=False, traj_rank_shape=fall, traj_rank_peak_base=0.750, traj_rank_end_slope=-2.56, rank=4

## P99: 中日は、貯金の線（3次式でならしたもの）に山がある（貯金を増やしてから減らす）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 9 件: d-2012, d-2013, d-2015, d-2019, d-2021 ほか
- もし: `（すべての単位）` ならば: `traj_wl_peak == True`
- 識別子: `[team=d] * => traj_wl_peak==true`（指紋 `48749683d6c52002`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日の山の数が、力が一定のときの見込みの範囲（trajectory_expectation.jsonl で P ≥ 0.05）
- 注記: 順位はほかのチームでも動くので、自分の力の線として貯金も見る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 13 回、元の命題に異議あり 13 回（どれかの形に異議あり 13 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 4 | 0.31 [0.13, 0.58] | -1.39σ（0.133） | 0.31 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 9 | 0 | 0.00 [0.00, 0.30] | -3.00σ（0.002） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 9 件（対偶の判例も同じ）

- 中日 2012 **(focus)**: traj_wl_peak=False, traj_wl_shape=rise, traj_wl_peak_base=0.340, traj_wl_end_slope=+28.30, rank=2
  - 中日 2012 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6
- 中日 2013 **(focus)**: traj_wl_peak=False, traj_wl_shape=fall, traj_wl_peak_base=0.585, traj_wl_end_slope=-1.02, rank=4
  - 中日 2013 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6
- 中日 2015 **(focus)**: traj_wl_peak=False, traj_wl_shape=valley, traj_wl_peak_base=0.490, traj_wl_end_slope=+13.11, rank=5
  - 中日 2015 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6
- 中日 2019 **(focus)**: traj_wl_peak=False, traj_wl_shape=valley, traj_wl_peak_base=0.735, traj_wl_end_slope=+36.08, rank=5
  - 中日 2019 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6
- 中日 2021 **(focus)**: traj_wl_peak=False, traj_wl_shape=fall, traj_wl_peak_base=0.340, traj_wl_end_slope=-18.45, rank=5
  - 中日 2021 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6
- 中日 2022 **(focus)**: traj_wl_peak=False, traj_wl_shape=valley, traj_wl_peak_base=0.650, traj_wl_end_slope=+38.42, rank=6
  - 中日 2022 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6
- 中日 2023 **(focus)**: traj_wl_peak=False, traj_wl_shape=fall, traj_wl_peak_base=0.280, traj_wl_end_slope=-21.87, rank=6
  - 中日 2023 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6
- 中日 2024 **(focus)**: traj_wl_peak=False, traj_wl_shape=fall, traj_wl_peak_base=0.500, traj_wl_end_slope=-21.34, rank=6
  - 中日 2024 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6
- 中日 2025 **(focus)**: traj_wl_peak=False, traj_wl_shape=fall, traj_wl_peak_base=0.510, traj_wl_end_slope=-23.69, rank=4
  - 中日 2025 は「（すべての単位）」を満たすのに「traj_wl_peak == True」を満たさない。なぜか？ → H6

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: traj_wl_peak=False, traj_wl_shape=valley, traj_wl_peak_base=0.595, traj_wl_end_slope=+19.02, rank=3

## P100: 中日の B クラスの年は、最後の日の順位の高さの傾きが負（下がりながらシーズンを終える）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 6 件: d-2015, d-2022, d-2018, d-2016, d-2025 ほか
- もし: `（すべての単位）` ならば: `traj_rank_end_slope < 0`
- 識別子: `[team=d, where:upper_half==false] * => traj_rank_end_slope<0`（指紋 `83edaae8a86269e3`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 12
- 見直す条件（反証）: P101（中日以外の B クラス）との率の差が 0.2 未満
- 注記: B クラスで終わるチームは、力が一定でも下がりながら終わりやすい。P101 と比べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 13 回、元の命題に異議あり 13 回（どれかの形に異議あり 13 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 6 | 0.50 [0.25, 0.75] | -2.00σ（0.054） | 0.50 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 6 | 0 | 0.00 [0.00, 0.39] | -4.24σ（0.000） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 6 件（対偶の判例も同じ）

- 中日 2015 **(focus)**: traj_rank_end_slope=+7.38, traj_rank_shape=valley, traj_rank_peak_x=-, rank=5 / surprise=+7.38
  - 中日 2015 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 中日 2022 **(focus)**: traj_rank_end_slope=+6.23, traj_rank_shape=valley, traj_rank_peak_x=-, rank=6 / surprise=+6.23
  - 中日 2022 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 中日 2018 **(focus)**: traj_rank_end_slope=+5.15, traj_rank_shape=valley, traj_rank_peak_x=-, rank=5 / surprise=+5.15
  - 中日 2018 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 中日 2016 **(focus)**: traj_rank_end_slope=+4.97, traj_rank_shape=peak-valley, traj_rank_peak_x=0.252, rank=6 / surprise=+4.97
  - 中日 2016 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 中日 2025 **(focus)**: traj_rank_end_slope=+2.77, traj_rank_shape=valley, traj_rank_peak_x=-, rank=4 / surprise=+2.77
  - 中日 2025 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 中日 2023 **(focus)**: traj_rank_end_slope=+2.46, traj_rank_shape=peak-valley, traj_rank_peak_x=0.298, rank=6 / surprise=+2.46
  - 中日 2023 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6

## P101: 中日以外の B クラスのチームは、最後の日の順位の高さの傾きが負

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 31 件: e-2012, c-2019, m-2019, db-2018, b-2018 ほか
- もし: `（すべての単位）` ならば: `traj_rank_end_slope < 0`
- 識別子: `[where:team!="d", where:upper_half==false] * => traj_rank_end_slope<0`（指紋 `82161c014d75b092`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 66
- 見直す条件（反証）: （基準の命題。P100 と率を比べるために置く）
- 注記: P100 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 13 回、元の命題に異議あり 13 回（どれかの形に異議あり 13 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 66 | 35 | 0.53 [0.41, 0.65] | -4.12σ（0.000） | 0.53 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 31 | 0 | 0.00 [0.00, 0.11] | -9.64σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 31 件（対偶の判例も同じ）

- 楽天 2012: traj_rank_end_slope=+14.97, traj_rank_shape=peak-valley, traj_rank_peak_x=0.350, rank=4 / surprise=+14.97
  - 楽天 2012 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 広島 2019: traj_rank_end_slope=+14.20, traj_rank_shape=peak-valley, traj_rank_peak_x=0.402, rank=4 / surprise=+14.20
  - 広島 2019 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- ロッテ 2019: traj_rank_end_slope=+13.30, traj_rank_shape=peak-valley, traj_rank_peak_x=0.286, rank=4 / surprise=+13.30
  - ロッテ 2019 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- DeNA 2018: traj_rank_end_slope=+13.11, traj_rank_shape=peak-valley, traj_rank_peak_x=0.107, rank=4 / surprise=+13.11
  - DeNA 2018 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- オリックス 2018: traj_rank_end_slope=+10.39, traj_rank_shape=peak-valley, traj_rank_peak_x=0.358, rank=4 / surprise=+10.39
  - オリックス 2018 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 西武 2025: traj_rank_end_slope=+9.95, traj_rank_shape=peak-valley, traj_rank_peak_x=0.301, rank=5 / surprise=+9.95
  - 西武 2025 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 広島 2021: traj_rank_end_slope=+9.13, traj_rank_shape=valley, traj_rank_peak_x=-, rank=4 / surprise=+9.13
  - 広島 2021 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 日本ハム 2023: traj_rank_end_slope=+8.44, traj_rank_shape=peak-valley, traj_rank_peak_x=0.355, rank=6 / surprise=+8.44
  - 日本ハム 2023 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 巨人 2022: traj_rank_end_slope=+8.07, traj_rank_shape=peak-valley, traj_rank_peak_x=0.171, rank=4 / surprise=+8.07
  - 巨人 2022 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- 楽天 2014: traj_rank_end_slope=+7.87, traj_rank_shape=valley, traj_rank_peak_x=-, rank=6 / surprise=+7.87
  - 楽天 2014 は「（すべての単位）」を満たすのに「traj_rank_end_slope < 0」を満たさない。なぜか？ → H6
- ほか 21 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ヤクルト 2020: traj_rank_end_slope=+15.28, traj_rank_shape=peak-valley, traj_rank_peak_x=0.099, rank=6
- オリックス 2020: traj_rank_end_slope=+1.45, traj_rank_shape=valley, traj_rank_peak_x=-, rank=6

## P102: 中日の B クラスの年は、順位が決まった位置（波のゆれの幅が半順位を下回る位置）が、力が一定のときの半分より早い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: d-2016, d-2015, d-2013, d-2017
- もし: `（すべての単位）` ならば: `wave_settle_pct < 0.5`
- 識別子: `[team=d, where:upper_half==false] * => wave_settle_pct<0.5`（指紋 `0577611af51d40b7`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd', 'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 12
- 見直す条件（反証）: 中日の B クラスの年のうち、力が一定のときより早く決まった年が半数以下
- 注記: P103（中日以外の B クラス）と並べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 12 回、元の命題に異議あり 12 回（どれかの形に異議あり 12 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 8 | 0.67 [0.39, 0.86] | +1.15σ（0.194） | 0.67 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | -2.00σ（0.062） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 中日 2016 **(focus)**: wave_settle_pct=0.805, wave_limit_rank=+5.60, wave_decay=+1.00, wave_period=+2.00, rank=6 / surprise=+2.06
  - 中日 2016 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 中日 2015 **(focus)**: wave_settle_pct=0.795, wave_limit_rank=+4.92, wave_decay=+2.00, wave_period=+2.00, rank=5 / surprise=+1.15
  - 中日 2015 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 中日 2013 **(focus)**: wave_settle_pct=0.615, wave_limit_rank=+3.95, wave_decay=+3.00, wave_period=+1.00, rank=4 / surprise=0.568
  - 中日 2013 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 中日 2017 **(focus)**: wave_settle_pct=0.845, wave_limit_rank=+4.91, wave_decay=+2.00, wave_period=0.750, rank=5 / surprise=0.567
  - 中日 2017 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6

## P103: 中日以外の B クラスのチームは、順位が決まった位置が、力が一定のときの半分より早い

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 41 件: f-2019, c-2012, e-2012, c-2015, db-2015 ほか
- もし: `（すべての単位）` ならば: `wave_settle_pct < 0.5`
- 識別子: `[where:team!="d", where:upper_half==false] * => wave_settle_pct<0.5`（指紋 `83f8fa66f43dd4fa`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 66
- 見直す条件（反証）: （基準の命題。P102 と率を比べるために置く）
- 注記: P102 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 12 回、元の命題に異議あり 12 回（どれかの形に異議あり 12 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 66 | 25 | 0.38 [0.27, 0.50] | -1.97σ（0.032） | 0.38 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 41 | 0 | 0.00 [0.00, 0.09] | -6.40σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 41 件（対偶の判例も同じ）

- 日本ハム 2019: wave_settle_pct=0.890, wave_limit_rank=+5.65, wave_decay=+1.00, wave_period=+2.00, rank=5 / surprise=+2.34
  - 日本ハム 2019 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 広島 2012: wave_settle_pct=0.915, wave_limit_rank=+3.98, wave_decay=0.500, wave_period=0.750, rank=4 / surprise=+2.07
  - 広島 2012 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 楽天 2012: wave_settle_pct=0.735, wave_limit_rank=+3.88, wave_decay=0.500, wave_period=0.750, rank=4 / surprise=+2.02
  - 楽天 2012 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 広島 2015: wave_settle_pct=0.785, wave_limit_rank=+4.38, wave_decay=+1.00, wave_period=+2.00, rank=4 / surprise=+1.30
  - 広島 2015 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- DeNA 2015: wave_settle_pct=0.790, wave_limit_rank=+5.34, wave_decay=+2.00, wave_period=+2.00, rank=6 / surprise=+1.29
  - DeNA 2015 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 広島 2021: wave_settle_pct=0.775, wave_limit_rank=+3.92, wave_decay=+2.00, wave_period=+2.00, rank=4 / surprise=+1.21
  - 広島 2021 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 楽天 2014: wave_settle_pct=0.790, wave_limit_rank=+4.46, wave_decay=+2.00, wave_period=+2.00, rank=6 / surprise=+1.20
  - 楽天 2014 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 日本ハム 2023: wave_settle_pct=0.840, wave_limit_rank=+5.37, wave_decay=+1.00, wave_period=+1.00, rank=6 / surprise=+1.20
  - 日本ハム 2023 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 日本ハム 2013: wave_settle_pct=0.790, wave_limit_rank=+5.27, wave_decay=0.500, wave_period=0.333, rank=6 / surprise=+1.08
  - 日本ハム 2013 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- 楽天 2022: wave_settle_pct=0.650, wave_limit_rank=+4.08, wave_decay=+3.00, wave_period=+2.00, rank=4 / surprise=0.943
  - 楽天 2022 は「（すべての単位）」を満たすのに「wave_settle_pct < 0.5」を満たさない。なぜか？ → H1, H6
- ほか 31 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- DeNA 2020: wave_settle_pct=0.845, wave_limit_rank=+7.17, wave_decay=0.500, wave_period=-, rank=4
- ヤクルト 2020: wave_settle_pct=0.880, wave_limit_rank=+5.80, wave_decay=+5.00, wave_period=+1.00, rank=6
- 楽天 2020: wave_settle_pct=0.605, wave_limit_rank=+3.63, wave_decay=+5.00, wave_period=+2.00, rank=4

## P104: 中日の B クラスの年は、前半の線だけから当てた波の行き先が、もう4位以下

- **判定: exit 4 待った！判断保留** — 元の命題: n=6（min_n=10）、成立率の区間 0.61〜1.00
- もし: `（すべての単位）` ならば: `wave_limit_rank_h1 >= 3.5`
- 識別子: `[team=d, where:upper_half==false] * => wave_limit_rank_h1>=3.5`（指紋 `1a1b75af4bda0937`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd', 'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 12
- 見直す条件（反証）: 中日の B クラスの年のうち、前半の行き先が4位以下だった年が半数以下
- 注記: 減衰しない波が選ばれた年は行き先が空（判定不能）。P105 と並べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 12 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 12 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 6 | 6 | 1.00 [0.61, 1.00] | +2.45σ（0.016） | 1.00 | 1.00 | 1.000 | 6 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 6 | 判断保留 | 4 |

## P105: 中日以外の B クラスのチームは、前半の線だけから当てた波の行き先が、もう4位以下

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 13 件: h-2013, db-2018, c-2022, f-2019, t-2018 ほか
- もし: `（すべての単位）` ならば: `wave_limit_rank_h1 >= 3.5`
- 識別子: `[where:team!="d", where:upper_half==false] * => wave_limit_rank_h1>=3.5`（指紋 `8ca683a18ebf206a`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 66
- 見直す条件（反証）: （基準の命題。P104 と率を比べるために置く）
- 注記: P104 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 12 回、元の命題に異議あり 12 回（どれかの形に異議あり 12 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 58 | 45 | 0.78 [0.65, 0.86] | +4.20σ（0.000） | 0.78 | 1.00 | 1.000 | 8 | 支持 | 1 |
| 対偶 | 13 | 0 | 0.00 [0.00, 0.23] | -3.61σ（0.000） | 0.00 | - | 1.000 | 8 | 棄却 | 3 |

**異議あり（例外あり）** 元の命題に判例 13 件（対偶の判例も同じ）

- ソフトバンク 2013: wave_limit_rank_h1=+3.46, wave_limit_rank=+3.50, course_rank_h1=3, rank=4 / surprise=+3.46
  - ソフトバンク 2013 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- DeNA 2018: wave_limit_rank_h1=+3.36, wave_limit_rank=+4.21, course_rank_h1=4, rank=4 / surprise=+3.36
  - DeNA 2018 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 広島 2022: wave_limit_rank_h1=+3.16, wave_limit_rank=-, course_rank_h1=3, rank=5 / surprise=+3.16
  - 広島 2022 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 日本ハム 2019: wave_limit_rank_h1=+3.13, wave_limit_rank=+5.65, course_rank_h1=3, rank=5 / surprise=+3.13
  - 日本ハム 2019 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 阪神 2018: wave_limit_rank_h1=+2.99, wave_limit_rank=+5.09, course_rank_h1=2, rank=6 / surprise=+2.99
  - 阪神 2018 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 広島 2025: wave_limit_rank_h1=+2.90, wave_limit_rank=+4.27, course_rank_h1=2, rank=5 / surprise=+2.90
  - 広島 2025 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 巨人 2022: wave_limit_rank_h1=+1.90, wave_limit_rank=-, course_rank_h1=2, rank=4 / surprise=+1.90
  - 巨人 2022 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 楽天 2022: wave_limit_rank_h1=+1.87, wave_limit_rank=+4.08, course_rank_h1=2, rank=4 / surprise=+1.87
  - 楽天 2022 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- DeNA 2015: wave_limit_rank_h1=+1.84, wave_limit_rank=+5.34, course_rank_h1=3, rank=6 / surprise=+1.84
  - DeNA 2015 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 楽天 2016: wave_limit_rank_h1=+1.43, wave_limit_rank=+4.36, course_rank_h1=5, rank=5 / surprise=+1.43
  - 楽天 2016 は「（すべての単位）」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- ほか 3 件（propositions.jsonl を参照）

## P106: 中日は、負け越したカードが、力が一定（その年の勝率）のときより多い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 3 件: d-2017, d-2023, d-2015
- もし: `（すべての単位）` ならば: `series_lost_pct > 0.5`
- 識別子: `[team=d] * => series_lost_pct>0.5`（指紋 `6eaa5a012bad6075`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日の年のうち、力が一定のときより多くのカードを負け越した年が半数以下
- 注記: 見立て「3連戦で2敗を引き当て続ける」。P107 と並べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 11 回、元の命題に異議あり 11 回（どれかの形に異議あり 11 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 10 | 0.77 [0.50, 0.92] | +1.94σ（0.046） | 0.77 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 3 | 0 | 0.00 [0.00, 0.56] | -1.73σ（0.125） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 3 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: series_lost_pct=0.388, series_disp=0.949, series3_w1=15, series3_w1_exp=+14.08, rank=5 / surprise=0.521
  - 中日 2017 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- 中日 2023 **(focus)**: series_lost_pct=0.285, series_disp=+1.01, series3_w1=9, series3_w1_exp=+13.06, rank=6 / surprise=0.510
  - 中日 2023 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- 中日 2015 **(focus)**: series_lost_pct=0.458, series_disp=+1.17, series3_w1=13, series3_w1_exp=+14.24, rank=5 / surprise=0.500
  - 中日 2015 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8

## P107: 中日以外のチームは、負け越したカードが、力が一定のときより多い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 68 件: s-2017, l-2024, s-2023, f-2023, s-2019 ほか
- もし: `（すべての単位）` ならば: `series_lost_pct > 0.5`
- 識別子: `[where:team!="d"] * => series_lost_pct>0.5`（指紋 `badcb073c3f75db5`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 143
- 見直す条件（反証）: （基準の命題。P106 と率を比べるために置く）
- 注記: P106 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 11 回、元の命題に異議あり 11 回（どれかの形に異議あり 11 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 143 | 75 | 0.52 [0.44, 0.60] | +0.59σ（0.308） | 0.52 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 68 | 0 | 0.00 [0.00, 0.05] | -8.25σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 68 件（対偶の判例も同じ）

- ヤクルト 2017: series_lost_pct=0.405, series_disp=0.848, rank=6 / surprise=0.708
  - ヤクルト 2017 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- 西武 2024: series_lost_pct=0.343, series_disp=+1.19, rank=6 / surprise=0.620
  - 西武 2024 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- ヤクルト 2023: series_lost_pct=0.323, series_disp=+1.18, rank=5 / surprise=0.553
  - ヤクルト 2023 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- 日本ハム 2023: series_lost_pct=0.410, series_disp=0.883, rank=6 / surprise=0.540
  - 日本ハム 2023 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- ヤクルト 2019: series_lost_pct=0.253, series_disp=0.957, rank=6 / surprise=0.531
  - ヤクルト 2019 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- 楽天 2018: series_lost_pct=0.445, series_disp=+1.07, rank=6 / surprise=0.529
  - 楽天 2018 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- オリックス 2015: series_lost_pct=0.338, series_disp=0.857, rank=5 / surprise=0.520
  - オリックス 2015 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- DeNA 2012: series_lost_pct=0.140, series_disp=+1.02, rank=6 / surprise=0.510
  - DeNA 2012 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- 日本ハム 2022: series_lost_pct=0.372, series_disp=+1.05, rank=6 / surprise=0.510
  - 日本ハム 2022 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- 日本ハム 2017: series_lost_pct=0.388, series_disp=+1.14, rank=5 / surprise=0.509
  - 日本ハム 2017 は「（すべての単位）」を満たすのに「series_lost_pct > 0.5」を満たさない。なぜか？ → H8
- ほか 58 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- オリックス 2020: series_lost_pct=0.133, series_disp=+1.08, rank=6
- 日本ハム 2020: series_lost_pct=0.412, series_disp=0.823, rank=5
- DeNA 2020: series_lost_pct=0.333, series_disp=0.971, rank=4
- 楽天 2020: series_lost_pct=0.312, series_disp=0.897, rank=4
- ロッテ 2020: series_lost_pct=0.420, series_disp=+1.05, rank=2
- 阪神 2020: series_lost_pct=0.328, series_disp=0.900, rank=2

## P108: 中日は、カードごとの勝ち数の散らばりが、力が一定のときより小さい（1勝2敗・2勝1敗に寄る）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 9 件: d-2012, d-2015, d-2022, d-2019, d-2013 ほか
- もし: `（すべての単位）` ならば: `series_disp_pct < 0.5`
- 識別子: `[team=d] * => series_disp_pct<0.5`（指紋 `4ef5659e3ce01d31`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日の年のうち、散らばりが力が一定のときより小さかった年が半数以下
- 注記: 決まった並び順（ローテーションなど）があるときの形。P109 と並べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 11 回、元の命題に異議あり 11 回（どれかの形に異議あり 11 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 4 | 0.31 [0.13, 0.58] | -1.39σ（0.133） | 0.31 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 9 | 0 | 0.00 [0.00, 0.30] | -3.00σ（0.002） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 9 件（対偶の判例も同じ）

- 中日 2012 **(focus)**: series_disp_pct=0.890, series_lost_pct=0.897, series3_w1=6, series3_w2=11, rank=2 / surprise=+1.21
  - 中日 2012 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 中日 2015 **(focus)**: series_disp_pct=0.845, series_lost_pct=0.458, series3_w1=13, series3_w2=11, rank=5 / surprise=+1.17
  - 中日 2015 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 中日 2022 **(focus)**: series_disp_pct=0.685, series_lost_pct=0.578, series3_w1=14, series3_w2=13, rank=6 / surprise=+1.09
  - 中日 2022 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 中日 2019 **(focus)**: series_disp_pct=0.670, series_lost_pct=0.805, series3_w1=16, series3_w2=8, rank=5 / surprise=+1.07
  - 中日 2019 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 中日 2013 **(focus)**: series_disp_pct=0.690, series_lost_pct=0.635, series3_w1=15, series3_w2=11, rank=4 / surprise=+1.06
  - 中日 2013 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 中日 2018 **(focus)**: series_disp_pct=0.505, series_lost_pct=0.623, series3_w1=17, series3_w2=13, rank=5 / surprise=+1.02
  - 中日 2018 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 中日 2023 **(focus)**: series_disp_pct=0.500, series_lost_pct=0.285, series3_w1=9, series3_w2=14, rank=6 / surprise=+1.01
  - 中日 2023 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 中日 2021 **(focus)**: series_disp_pct=0.545, series_lost_pct=0.595, series3_w1=12, series3_w2=6, rank=5 / surprise=+1.01
  - 中日 2021 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 中日 2014 **(focus)**: series_disp_pct=0.515, series_lost_pct=0.672, series3_w1=15, series3_w2=9, rank=4 / surprise=0.993
  - 中日 2014 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: series_disp_pct=0.950, series_lost_pct=0.568, series3_w1=8, series3_w2=13, rank=3

## P109: 中日以外のチームは、カードごとの勝ち数の散らばりが、力が一定のときより小さい

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 73 件: c-2022, h-2025, t-2022, l-2017, g-2013 ほか
- もし: `（すべての単位）` ならば: `series_disp_pct < 0.5`
- 識別子: `[where:team!="d"] * => series_disp_pct<0.5`（指紋 `817c95d8596903ef`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 143
- 見直す条件（反証）: （基準の命題。P108 と率を比べるために置く）
- 注記: P108 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 11 回、元の命題に異議あり 11 回（どれかの形に異議あり 11 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 143 | 70 | 0.49 [0.41, 0.57] | -0.25σ（0.434） | 0.49 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 73 | 0 | 0.00 [0.00, 0.05] | -8.54σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 73 件（対偶の判例も同じ）

- 広島 2022: series_disp_pct=+1.00, series_lost_pct=0.305, rank=5 / surprise=+1.54
  - 広島 2022 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- ソフトバンク 2025: series_disp_pct=+1.00, series_lost_pct=0.367, rank=1 / surprise=+1.44
  - ソフトバンク 2025 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 阪神 2022: series_disp_pct=+1.00, series_lost_pct=0.380, rank=3 / surprise=+1.43
  - 阪神 2022 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 西武 2017: series_disp_pct=0.980, series_lost_pct=0.688, rank=2 / surprise=+1.38
  - 西武 2017 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 巨人 2013: series_disp_pct=0.975, series_lost_pct=0.723, rank=1 / surprise=+1.37
  - 巨人 2013 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- オリックス 2017: series_disp_pct=0.980, series_lost_pct=0.593, rank=4 / surprise=+1.37
  - オリックス 2017 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 巨人 2016: series_disp_pct=0.955, series_lost_pct=0.507, rank=2 / surprise=+1.33
  - 巨人 2016 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- ソフトバンク 2022: series_disp_pct=0.985, series_lost_pct=0.725, rank=1 / surprise=+1.31
  - ソフトバンク 2022 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- DeNA 2015: series_disp_pct=0.930, series_lost_pct=0.647, rank=6 / surprise=+1.25
  - DeNA 2015 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- 楽天 2015: series_disp_pct=0.910, series_lost_pct=0.522, rank=6 / surprise=+1.24
  - 楽天 2015 は「（すべての単位）」を満たすのに「series_disp_pct < 0.5」を満たさない。なぜか？ → H8
- ほか 63 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 巨人 2020: series_disp_pct=0.755, series_lost_pct=0.517, rank=1
- ソフトバンク 2020: series_disp_pct=0.700, series_lost_pct=0.815, rank=1
- オリックス 2020: series_disp_pct=0.615, series_lost_pct=0.133, rank=6
- ロッテ 2020: series_disp_pct=0.530, series_lost_pct=0.420, rank=2

## P110: 中日は、カードの1試合目の勝率が、2試合目以降より高い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: d-2013, d-2014, d-2022, d-2025
- もし: `（すべての単位）` ならば: `series_g1_minus_rest > 0`
- 識別子: `[team=d] * => series_g1_minus_rest>0`（指紋 `ca77f1308529fd95`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd'} / 単位数: 13
- 見直す条件（反証）: 中日の年のうち、1試合目の勝率のほうが高かった年が半数以下
- 注記: 並び順のいちばん単純な現れ方。P111 と並べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 11 回、元の命題に異議あり 11 回（どれかの形に異議あり 11 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 9 | 0.69 [0.42, 0.87] | +1.39σ（0.133） | 0.69 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 4 | 0 | 0.00 [0.00, 0.49] | -2.00σ（0.062） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 中日 2013 **(focus)**: series_g1_minus_rest=-0.126, series_disp=+1.06, rank=4 / surprise=-0.126
  - 中日 2013 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- 中日 2014 **(focus)**: series_g1_minus_rest=-0.106, series_disp=0.993, rank=4 / surprise=-0.106
  - 中日 2014 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- 中日 2022 **(focus)**: series_g1_minus_rest=-0.094, series_disp=+1.09, rank=6 / surprise=-0.094
  - 中日 2022 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- 中日 2025 **(focus)**: series_g1_minus_rest=-0.092, series_disp=0.840, rank=4 / surprise=-0.092
  - 中日 2025 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: series_g1_minus_rest=-0.034, series_disp=+1.29, rank=3

## P111: 中日以外のチームは、カードの1試合目の勝率が、2試合目以降より高い

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 67 件: e-2022, h-2021, l-2013, s-2019, l-2024 ほか
- もし: `（すべての単位）` ならば: `series_g1_minus_rest > 0`
- 識別子: `[where:team!="d"] * => series_g1_minus_rest>0`（指紋 `6fca590af5cb4c53`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 143
- 見直す条件（反証）: （基準の命題。P110 と率を比べるために置く）
- 注記: P110 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 11 回、元の命題に異議あり 11 回（どれかの形に異議あり 11 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 143 | 76 | 0.53 [0.45, 0.61] | +0.75σ（0.252） | 0.53 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 67 | 0 | 0.00 [0.00, 0.05] | -8.19σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 67 件（対偶の判例も同じ）

- 楽天 2022: series_g1_minus_rest=-0.267, series_disp=0.949, rank=4 / surprise=-0.267
  - 楽天 2022 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- ソフトバンク 2021: series_g1_minus_rest=-0.228, series_disp=+1.12, rank=4 / surprise=-0.228
  - ソフトバンク 2021 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- 西武 2013: series_g1_minus_rest=-0.170, series_disp=0.866, rank=2 / surprise=-0.170
  - 西武 2013 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- ヤクルト 2019: series_g1_minus_rest=-0.156, series_disp=0.957, rank=6 / surprise=-0.156
  - ヤクルト 2019 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- 西武 2024: series_g1_minus_rest=-0.155, series_disp=+1.19, rank=6 / surprise=-0.155
  - 西武 2024 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- オリックス 2024: series_g1_minus_rest=-0.144, series_disp=+1.01, rank=5 / surprise=-0.144
  - オリックス 2024 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- 阪神 2023: series_g1_minus_rest=-0.144, series_disp=+1.07, rank=1 / surprise=-0.144
  - 阪神 2023 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- 楽天 2017: series_g1_minus_rest=-0.142, series_disp=+1.20, rank=3 / surprise=-0.142
  - 楽天 2017 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- ロッテ 2025: series_g1_minus_rest=-0.139, series_disp=0.903, rank=6 / surprise=-0.139
  - ロッテ 2025 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- DeNA 2013: series_g1_minus_rest=-0.130, series_disp=0.702, rank=5 / surprise=-0.130
  - DeNA 2013 は「（すべての単位）」を満たすのに「series_g1_minus_rest > 0」を満たさない。なぜか？ → H8
- ほか 57 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ヤクルト 2020: series_g1_minus_rest=-0.206, series_disp=0.779, rank=6
- 楽天 2020: series_g1_minus_rest=-0.079, series_disp=0.897, rank=4
- 日本ハム 2020: series_g1_minus_rest=-0.062, series_disp=0.823, rank=5

## P112: 中日の B クラスの年は、B クラスが（数の上で）確定した日に、残り試合が10以上あった

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 11 件: d-2022, d-2019, d-2013, d-2014, d-2016 ほか
- もし: `（すべての単位）` ならば: `clinch_out_left >= 10`
- 識別子: `[team=d, where:upper_half==false] * => clinch_out_left>=10`（指紋 `429925d00124742e`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd', 'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 12
- 見直す条件（反証）: 中日の B クラスの年のうち、残り10試合以上で確定した年が半数以下
- 注記: 確定の日は控えめ（直接対決の残りを考えない）。P113 と並べて読む
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 1 | 0.08 [0.01, 0.35] | -2.89σ（0.003） | 0.08 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 11 | 0 | 0.00 [0.00, 0.26] | -3.32σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 11 件（対偶の判例も同じ）

- 中日 2022 **(focus)**: clinch_out_left=4, decided_x=0.995, rank=6 / surprise=0.969
  - 中日 2022 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2019 **(focus)**: clinch_out_left=4, decided_x=+1.00, rank=5 / surprise=0.968
  - 中日 2019 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2013 **(focus)**: clinch_out_left=6, decided_x=0.933, rank=4 / surprise=0.933
  - 中日 2013 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2014 **(focus)**: clinch_out_left=5, decided_x=0.959, rank=4 / surprise=0.927
  - 中日 2014 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2016 **(focus)**: clinch_out_left=7, decided_x=0.937, rank=6 / surprise=0.926
  - 中日 2016 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2018 **(focus)**: clinch_out_left=3, decided_x=0.980, rank=5 / surprise=0.924
  - 中日 2018 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2024 **(focus)**: clinch_out_left=7, decided_x=0.979, rank=6 / surprise=0.921
  - 中日 2024 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2025 **(focus)**: clinch_out_left=8, decided_x=0.926, rank=4 / surprise=0.921
  - 中日 2025 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2015 **(focus)**: clinch_out_left=7, decided_x=+1.00, rank=5 / surprise=0.918
  - 中日 2015 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 中日 2021 **(focus)**: clinch_out_left=6, decided_x=0.959, rank=5 / surprise=0.914
  - 中日 2021 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- ほか 1 件（propositions.jsonl を参照）

## P113: 中日以外の B クラスのチームは、B クラスが確定した日に、残り試合が10以上あった

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 47 件: c-2015, c-2019, e-2023, l-2015, g-2022 ほか
- もし: `（すべての単位）` ならば: `clinch_out_left >= 10`
- 識別子: `[where:team!="d", where:upper_half==false] * => clinch_out_left>=10`（指紋 `2aab4168b858ed24`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}, {'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 66
- 見直す条件（反証）: （基準の命題。P112 と率を比べるために置く）
- 注記: P112 の比べる相手
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 66 | 19 | 0.29 [0.19, 0.41] | -3.45σ（0.000） | 0.29 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 47 | 0 | 0.00 [0.00, 0.08] | -6.86σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 47 件（対偶の判例も同じ）

- 広島 2015: clinch_out_left=0, decided_x=+1.00, rank=4 / surprise=+1.00
  - 広島 2015 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 広島 2019: clinch_out_left=0, decided_x=+1.00, rank=4 / surprise=+1.00
  - 広島 2019 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 楽天 2023: clinch_out_left=0, decided_x=+1.00, rank=4 / surprise=+1.00
  - 楽天 2023 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 西武 2015: clinch_out_left=0, decided_x=0.995, rank=4 / surprise=0.995
  - 西武 2015 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 巨人 2022: clinch_out_left=0, decided_x=0.995, rank=4 / surprise=0.995
  - 巨人 2022 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 楽天 2022: clinch_out_left=1, decided_x=0.990, rank=4 / surprise=0.990
  - 楽天 2022 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 広島 2022: clinch_out_left=1, decided_x=0.995, rank=5 / surprise=0.984
  - 広島 2022 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- DeNA 2018: clinch_out_left=1, decided_x=0.980, rank=4 / surprise=0.980
  - DeNA 2018 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 広島 2024: clinch_out_left=2, decided_x=0.979, rank=4 / surprise=0.979
  - 広島 2024 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- 楽天 2012: clinch_out_left=4, decided_x=0.974, rank=4 / surprise=0.974
  - 楽天 2012 は「（すべての単位）」を満たすのに「clinch_out_left >= 10」を満たさない。なぜか？ → H1
- ほか 37 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: clinch_out_left=2, decided_x=0.972, rank=4
- 日本ハム 2020: clinch_out_left=3, decided_x=0.972, rank=5
- DeNA 2020: clinch_out_left=2, decided_x=0.939, rank=4
- 広島 2020: clinch_out_left=4, decided_x=0.939, rank=5

## P114: A クラスで貯金の線に山があるチームは、その山が A クラスの確定より後にある（決まった後に落とす）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 42 件: l-2012, g-2016, h-2019, db-2017, t-2014 ほか
- もし: `（すべての単位）` ならば: `traj_wl_peak_after_clinch == True`
- 識別子: `[where:traj_wl_peak==true, where:upper_half==true] * => traj_wl_peak_after_clinch==true`（指紋 `47d019b7e86d9b23`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': True}, {'col': 'traj_wl_peak', 'op': '==', 'value': True}]} / 単位数: 46
- 見直す条件（反証）: 確定後の山の数が、力が一定のときの見込みの範囲（trajectory_expectation.jsonl で P ≥ 0.05）
- 注記: R22・R25 の「A クラスの貯金の山は見込みより多い」が、決まった後の試合から来ているかを見る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 46 | 4 | 0.09 [0.03, 0.20] | -5.60σ（0.000） | 0.09 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 42 | 0 | 0.00 [0.00, 0.08] | -6.48σ（0.000） | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 42 件（対偶の判例も同じ）

- 西武 2012: traj_wl_peak_after_clinch=False, clinch_in_x=0.969, traj_wl_peak_after_clinch_base=0.020, rank=2 / surprise=0.927
  - 西武 2012 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- 巨人 2016: traj_wl_peak_after_clinch=False, clinch_in_x=0.932, traj_wl_peak_after_clinch_base=0.040, rank=2 / surprise=0.913
  - 巨人 2016 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- ソフトバンク 2019: traj_wl_peak_after_clinch=False, clinch_in_x=0.946, traj_wl_peak_after_clinch_base=0.045, rank=2 / surprise=0.881
  - ソフトバンク 2019 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- DeNA 2017: traj_wl_peak_after_clinch=False, clinch_in_x=0.953, traj_wl_peak_after_clinch_base=0.025, rank=3 / surprise=0.847
  - DeNA 2017 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- 阪神 2014: traj_wl_peak_after_clinch=False, clinch_in_x=0.948, traj_wl_peak_after_clinch_base=0.020, rank=2 / surprise=0.831
  - 阪神 2014 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- DeNA 2019: traj_wl_peak_after_clinch=False, clinch_in_x=0.968, traj_wl_peak_after_clinch_base=0.015, rank=2 / surprise=0.821
  - DeNA 2019 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- 巨人 2019: traj_wl_peak_after_clinch=False, clinch_in_x=0.919, traj_wl_peak_after_clinch_base=0.065, rank=1 / surprise=0.816
  - 巨人 2019 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- 広島 2023: traj_wl_peak_after_clinch=False, clinch_in_x=0.952, traj_wl_peak_after_clinch_base=0.015, rank=2 / surprise=0.812
  - 広島 2023 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- ソフトバンク 2014: traj_wl_peak_after_clinch=False, clinch_in_x=0.839, traj_wl_peak_after_clinch_base=0.125, rank=1 / surprise=0.800
  - ソフトバンク 2014 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- 阪神 2022: traj_wl_peak_after_clinch=False, clinch_in_x=0.995, traj_wl_peak_after_clinch_base=0.000, rank=3 / surprise=0.778
  - 阪神 2022 は「（すべての単位）」を満たすのに「traj_wl_peak_after_clinch == True」を満たさない。なぜか？ → H6
- ほか 32 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 巨人 2020: traj_wl_peak_after_clinch=False, clinch_in_x=0.851, traj_wl_peak_after_clinch_base=0.125, rank=1
- ロッテ 2020: traj_wl_peak_after_clinch=False, clinch_in_x=0.972, traj_wl_peak_after_clinch_base=0.015, rank=2

## P115: 得点も失点もリーグ上位半分（3位以内）に入らないなら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: t-2015, m-2023, c-2023, g-2021
- もし: `rank_rf >= 4 かつ rank_ra >= 4` ならば: `upper_half == False`
- 識別子: `[all] rank_ra>=4 & rank_rf>=4 => upper_half==false`（指紋 `5b650488a6bfb0d9`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P126, P138, P147, P148, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 得点も失点も4位以下のチーム・シーズンの4分の1を超えて A クラス
- 注記: 十分の向きの命題。逆（B クラスなら、得点も失点も4位以下）の判例が、得点か失点のどちらかは上位なのに B になった道筋の種になる
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 35 | 31 | 0.89 [0.74, 0.95] | +1.85σ（0.041） | 0.50 | 1.77 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 74 | 0.95 [0.88, 0.98] | +4.05σ（0.000） | 0.78 | 1.22 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 31 | 0.40 [0.30, 0.51] | -7.19σ（0.000） | 0.22 | 1.77 | 0.000 | 0 | 修正 | 2 |
| 裏 | 121 | 74 | 0.61 [0.52, 0.69] | -3.52σ（0.001） | 0.50 | 1.22 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 阪神 2015: rank_rf=6, rank_ra=5, upper_half=True, rank=3, rd=-85, sim_p_upper=0.234 / surprise=-85
  - 阪神 2015 は「rank_rf >= 4 かつ rank_ra >= 4」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2023: rank_rf=4, rank_ra=5, upper_half=True, rank=2, rd=-19, sim_p_upper=0.444 / surprise=-19
  - ロッテ 2023 は「rank_rf >= 4 かつ rank_ra >= 4」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 広島 2023: rank_rf=5, rank_ra=5, upper_half=True, rank=2, rd=-15, sim_p_upper=0.553 / surprise=-15
  - 広島 2023 は「rank_rf >= 4 かつ rank_ra >= 4」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 巨人 2021: rank_rf=4, rank_ra=4, upper_half=True, rank=3, rd=11, sim_p_upper=0.696 / surprise=11
  - 巨人 2021 は「rank_rf >= 4 かつ rank_ra >= 4」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 47 件（裏の判例も同じ）

- 西武 2024: rank_rf=6, rank_ra=3, upper_half=False, rank=6, rd=-135, sim_p_upper=0.004 / surprise=-135
  - 西武 2024 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- 中日 2023 **(focus)**: rank_rf=6, rank_ra=3, upper_half=False, rank=6, rd=-108, sim_p_upper=0.031 / surprise=-108
  - 中日 2023 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- ヤクルト 2013: rank_rf=3, rank_ra=5, upper_half=False, rank=6, rd=-105, sim_p_upper=0.154 / surprise=-105
  - ヤクルト 2013 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- ヤクルト 2016: rank_rf=2, rank_ra=6, upper_half=False, rank=5, rd=-100, sim_p_upper=0.175 / surprise=-100
  - ヤクルト 2016 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- ソフトバンク 2013: rank_rf=1, rank_ra=3, upper_half=False, rank=4, rd=98, sim_p_upper=0.885 / surprise=98
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- DeNA 2015: rank_rf=2, rank_ra=6, upper_half=False, rank=6, rd=-90, sim_p_upper=0.046 / surprise=-90
  - DeNA 2015 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- ヤクルト 2019: rank_rf=2, rank_ra=6, upper_half=False, rank=6, rd=-83, sim_p_upper=0.138 / surprise=-83
  - ヤクルト 2019 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- 中日 2022 **(focus)**: rank_rf=6, rank_ra=2, upper_half=False, rank=6, rd=-81, sim_p_upper=0.113 / surprise=-81
  - 中日 2022 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rank_rf=6, rank_ra=1, upper_half=False, rank=5, rd=-73, sim_p_upper=0.087 / surprise=-73
  - 中日 2021 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- ソフトバンク 2021: rank_rf=2, rank_ra=1, upper_half=False, rank=4, rd=71, sim_p_upper=0.833 / surprise=71
  - ソフトバンク 2021 は「upper_half == False」を満たすのに「rank_rf >= 4 かつ rank_ra >= 4」を満たさない。なぜか？ → H2
- ほか 37 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 西武 2020: rank_rf=4, rank_ra=6, upper_half=True, rank=3, rd=-64, sim_p_upper=0.200
- 中日 2020 **(focus)**: rank_rf=6, rank_ra=4, upper_half=True, rank=3, rd=-60, sim_p_upper=0.371

## P116: 得点した回の大きさがリーグ上位2位以内なら、A クラス（P62 の鏡）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 15 件: c-2022, l-2015, e-2022, s-2019, db-2021 ほか
- もし: `inn_size_rank >= 5` ならば: `upper_half == True`
- 識別子: `[seasons=2013-2025] inn_size_rank>=5 => upper_half==true`（指紋 `e0ae033c8a12c47a`）
- 兄弟（範囲と結論が同じ、条件が違う）: P172
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: 大きさが上位2位以内のチーム・シーズンの4分の1を超えて B クラス
- 注記: inn_size_rank は小さいほうが 1（6球団なので 5・6 が上位2位）。大きさの軸が上にも下にも効く（対称）か、下だけの床かを見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 33 | 0.69 [0.55, 0.80] | -1.00σ（0.200） | 0.50 | 1.38 | 0.001 | 0 | 判断保留 | 4 |
| 対偶 | 72 | 57 | 0.79 [0.68, 0.87] | +0.82σ（0.252） | 0.67 | 1.19 | 0.001 | 0 | 判断保留 | 4 |
| 逆 | 72 | 33 | 0.46 [0.35, 0.57] | -5.72σ（0.000） | 0.33 | 1.38 | 0.001 | 0 | 修正 | 2 |
| 裏 | 96 | 57 | 0.59 [0.49, 0.69] | -3.54σ（0.001） | 0.50 | 1.19 | 0.001 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 15 件（対偶の判例も同じ）

- 広島 2022: inn_size_rank=6, upper_half=False, rank=5, rank_rf=2, sim_p_upper=0.319 / surprise=0.103
  - 広島 2022 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 西武 2015: inn_size_rank=6, upper_half=False, rank=4, rank_rf=2, sim_p_upper=0.680 / surprise=0.066
  - 西武 2015 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 楽天 2022: inn_size_rank=6, upper_half=False, rank=4, rank_rf=2, sim_p_upper=0.329 / surprise=0.063
  - 楽天 2022 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- ヤクルト 2019: inn_size_rank=6, upper_half=False, rank=6, rank_rf=2, sim_p_upper=0.138 / surprise=0.054
  - ヤクルト 2019 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- DeNA 2021: inn_size_rank=5, upper_half=False, rank=6, rank_rf=2, sim_p_upper=0.105 / surprise=0.053
  - DeNA 2021 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 巨人 2022: inn_size_rank=5, upper_half=False, rank=4, rank_rf=3, sim_p_upper=0.279 / surprise=0.050
  - 巨人 2022 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 楽天 2014: inn_size_rank=6, upper_half=False, rank=6, rank_rf=6, sim_p_upper=0.074 / surprise=0.049
  - 楽天 2014 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- ソフトバンク 2021: inn_size_rank=6, upper_half=False, rank=4, rank_rf=2, sim_p_upper=0.833 / surprise=0.044
  - ソフトバンク 2021 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 楽天 2016: inn_size_rank=5, upper_half=False, rank=5, rank_rf=5, sim_p_upper=0.033 / surprise=0.034
  - 楽天 2016 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- DeNA 2013: inn_size_rank=6, upper_half=False, rank=5, rank_rf=1, sim_p_upper=0.302 / surprise=0.033
  - DeNA 2013 は「inn_size_rank >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- ほか 5 件（propositions.jsonl を参照）

**異議あり（主張が強すぎる）** 逆に判例 39 件（裏の判例も同じ）

- ソフトバンク 2019: inn_size_rank=1, upper_half=True, rank=2, rank_rf=4, sim_p_upper=0.527 / surprise=-0.103
  - ソフトバンク 2019 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- オリックス 2022: inn_size_rank=1, upper_half=True, rank=1, rank_rf=4, sim_p_upper=0.855 / surprise=-0.079
  - オリックス 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- DeNA 2022: inn_size_rank=2, upper_half=True, rank=2, rank_rf=4, sim_p_upper=0.618 / surprise=-0.067
  - DeNA 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- ロッテ 2023: inn_size_rank=2, upper_half=True, rank=2, rank_rf=4, sim_p_upper=0.444 / surprise=-0.054
  - ロッテ 2023 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- 巨人 2016: inn_size_rank=1, upper_half=True, rank=2, rank_rf=4, sim_p_upper=0.698 / surprise=-0.050
  - 巨人 2016 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- 西武 2022: inn_size_rank=2, upper_half=True, rank=3, rank_rf=5, sim_p_upper=0.526 / surprise=-0.045
  - 西武 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- ヤクルト 2022: inn_size_rank=4, upper_half=True, rank=1, rank_rf=1, sim_p_upper=0.852 / surprise=0.039
  - ヤクルト 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- 阪神 2015: inn_size_rank=1, upper_half=True, rank=3, rank_rf=6, sim_p_upper=0.234 / surprise=-0.036
  - 阪神 2015 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- 広島 2018: inn_size_rank=4, upper_half=True, rank=1, rank_rf=1, sim_p_upper=0.942 / surprise=0.034
  - 広島 2018 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- 阪神 2022: inn_size_rank=3, upper_half=True, rank=3, rank_rf=5, sim_p_upper=0.832 / surprise=0.031
  - 阪神 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5」を満たさない。なぜか？ → H5
- ほか 29 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 広島 2020: inn_size_rank=6, upper_half=False, rank=5, rank_rf=2, sim_p_upper=0.353
- 楽天 2020: inn_size_rank=6, upper_half=False, rank=4, rank_rf=1, sim_p_upper=0.705
- 日本ハム 2020: inn_size_rank=5, upper_half=False, rank=5, rank_rf=3, sim_p_upper=0.416

## P117: 得点した回の大きさがその年リーグ下位2位以内なら、B クラス（続けてでなく1年だけ）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 10 件: h-2019, b-2022, db-2022, m-2023, g-2016 ほか
- もし: `inn_size_rank <= 2` ならば: `upper_half == False`
- 識別子: `[seasons=2013-2025] inn_size_rank<=2 => upper_half==false`（指紋 `ac07929a7d84077c`）
- 兄弟（範囲と結論が同じ、条件が違う）: P62, P173
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: （P62 と率を比べるための命題）
- 注記: P62（2年以上続けて）と率を比べ、続いていることが効いているかを見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 38 | 0.79 [0.66, 0.88] | +0.67σ（0.316） | 0.50 | 1.58 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 72 | 62 | 0.86 [0.76, 0.92] | +2.18σ（0.016） | 0.67 | 1.29 | 0.000 | 0 | 支持 | 1 |
| 逆 | 72 | 38 | 0.53 [0.41, 0.64] | -4.35σ（0.000） | 0.33 | 1.58 | 0.000 | 0 | 修正 | 2 |
| 裏 | 96 | 62 | 0.65 [0.55, 0.73] | -2.36σ（0.015） | 0.50 | 1.29 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 10 件（対偶の判例も同じ）

- ソフトバンク 2019: inn_size_rank=1, upper_half=True, inn_size_low_streak=1, rank=2, rank_rf=4, sim_p_upper=0.527 / surprise=-0.103
  - ソフトバンク 2019 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- オリックス 2022: inn_size_rank=1, upper_half=True, inn_size_low_streak=1, rank=1, rank_rf=4, sim_p_upper=0.855 / surprise=-0.079
  - オリックス 2022 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- DeNA 2022: inn_size_rank=2, upper_half=True, inn_size_low_streak=1, rank=2, rank_rf=4, sim_p_upper=0.618 / surprise=-0.067
  - DeNA 2022 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- ロッテ 2023: inn_size_rank=2, upper_half=True, inn_size_low_streak=1, rank=2, rank_rf=4, sim_p_upper=0.444 / surprise=-0.054
  - ロッテ 2023 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 巨人 2016: inn_size_rank=1, upper_half=True, inn_size_low_streak=1, rank=2, rank_rf=4, sim_p_upper=0.698 / surprise=-0.050
  - 巨人 2016 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 西武 2022: inn_size_rank=2, upper_half=True, inn_size_low_streak=1, rank=3, rank_rf=5, sim_p_upper=0.526 / surprise=-0.045
  - 西武 2022 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 阪神 2015: inn_size_rank=1, upper_half=True, inn_size_low_streak=1, rank=3, rank_rf=6, sim_p_upper=0.234 / surprise=-0.036
  - 阪神 2015 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 西武 2013: inn_size_rank=2, upper_half=True, inn_size_low_streak=1, rank=2, rank_rf=4, sim_p_upper=0.689 / surprise=-0.030
  - 西武 2013 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- ソフトバンク 2014: inn_size_rank=2, upper_half=True, inn_size_low_streak=1, rank=1, rank_rf=1, sim_p_upper=0.950 / surprise=-0.019
  - ソフトバンク 2014 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6
- 楽天 2021: inn_size_rank=2, upper_half=True, inn_size_low_streak=1, rank=3, rank_rf=4, sim_p_upper=0.631 / surprise=-0.015
  - 楽天 2021 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5, H6

**異議あり（主張が強すぎる）** 逆に判例 34 件（裏の判例も同じ）

- 広島 2022: inn_size_rank=6, upper_half=False, inn_size_low_streak=0, rank=5, rank_rf=2, sim_p_upper=0.319 / surprise=0.103
  - 広島 2022 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- 西武 2015: inn_size_rank=6, upper_half=False, inn_size_low_streak=0, rank=4, rank_rf=2, sim_p_upper=0.680 / surprise=0.066
  - 西武 2015 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- 楽天 2022: inn_size_rank=6, upper_half=False, inn_size_low_streak=0, rank=4, rank_rf=2, sim_p_upper=0.329 / surprise=0.063
  - 楽天 2022 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- ヤクルト 2019: inn_size_rank=6, upper_half=False, inn_size_low_streak=0, rank=6, rank_rf=2, sim_p_upper=0.138 / surprise=0.054
  - ヤクルト 2019 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- DeNA 2021: inn_size_rank=5, upper_half=False, inn_size_low_streak=0, rank=6, rank_rf=2, sim_p_upper=0.105 / surprise=0.053
  - DeNA 2021 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- 巨人 2022: inn_size_rank=5, upper_half=False, inn_size_low_streak=0, rank=4, rank_rf=3, sim_p_upper=0.279 / surprise=0.050
  - 巨人 2022 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- 楽天 2014: inn_size_rank=6, upper_half=False, inn_size_low_streak=0, rank=6, rank_rf=6, sim_p_upper=0.074 / surprise=0.049
  - 楽天 2014 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- ソフトバンク 2021: inn_size_rank=6, upper_half=False, inn_size_low_streak=0, rank=4, rank_rf=2, sim_p_upper=0.833 / surprise=0.044
  - ソフトバンク 2021 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- 楽天 2016: inn_size_rank=5, upper_half=False, inn_size_low_streak=0, rank=5, rank_rf=5, sim_p_upper=0.033 / surprise=0.034
  - 楽天 2016 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- DeNA 2013: inn_size_rank=6, upper_half=False, inn_size_low_streak=0, rank=5, rank_rf=1, sim_p_upper=0.302 / surprise=0.033
  - DeNA 2013 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5, H6
- ほか 24 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: inn_size_rank=1, upper_half=True, inn_size_low_streak=4, rank=3, rank_rf=6, sim_p_upper=0.371
- 西武 2020: inn_size_rank=1, upper_half=True, inn_size_low_streak=1, rank=3, rank_rf=4, sim_p_upper=0.200

## P118: 失点だけが上位半分（失点3位以内・得点4位以下）のチームは、得点が5位以下なら B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: t-2022, t-2013, t-2021, t-2019, h-2012 ほか
- もし: `rank_rf >= 5` ならば: `upper_half == False`
- 識別子: `[where:rank_ra<=3, where:rank_rf>=4] rank_rf>=5 => upper_half==false`（指紋 `9a0ad0383775b6a7`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_ra', 'op': '<=', 'value': 3}, {'col': 'rank_rf', 'op': '>=', 'value': 4}]} / 単位数: 43
- 見直す条件（反証）: きっかけの中日6単位を除いて、得点5位以下の単位の4分の1を超えて A クラス
- 注記: 中日の6単位（得点5・6位）を見た後の条件。きっかけ以外で読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 20 | 0.77 [0.58, 0.89] | +0.23σ（0.515） | 0.53 | 1.44 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 20 | 14 | 0.70 [0.48, 0.85] | -0.52σ（0.383） | 0.40 | 1.77 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 23 | 20 | 0.87 [0.68, 0.95] | +1.32σ（0.137） | 0.60 | 1.44 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 17 | 14 | 0.82 [0.59, 0.94] | +0.70σ（0.353） | 0.47 | 1.77 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- 阪神 2022: rank_rf=5, upper_half=True, rank=3, rank_ra=1, rd=61, sim_p_upper=0.832 / surprise=61
  - 阪神 2022 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2013: rank_rf=5, upper_half=True, rank=2, rank_ra=1, rd=43, sim_p_upper=0.858 / surprise=43
  - 阪神 2013 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2021: rank_rf=5, upper_half=True, rank=2, rank_ra=2, rd=33, sim_p_upper=0.891 / surprise=33
  - 阪神 2021 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2019: rank_rf=6, upper_half=True, rank=3, rank_ra=2, rd=-28, sim_p_upper=0.424 / surprise=-28
  - 阪神 2019 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ソフトバンク 2012: rank_rf=5, upper_half=True, rank=3, rank_ra=1, rd=23, sim_p_upper=0.669 / surprise=23
  - ソフトバンク 2012 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2022: rank_rf=5, upper_half=True, rank=3, rank_ra=1, rd=16, sim_p_upper=0.526 / surprise=16
  - 西武 2022 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**待った！判断保留** 逆に判例 3 件（裏の判例も同じ）

- 巨人 2017: rank_rf=4, upper_half=False, rank=4, rank_ra=1, rd=32, sim_p_upper=0.844 / surprise=32
  - 巨人 2017 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- オリックス 2018: rank_rf=4, upper_half=False, rank=4, rank_ra=1, rd=-27, sim_p_upper=0.330 / surprise=-27
  - オリックス 2018 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 楽天 2012: rank_rf=4, upper_half=False, rank=4, rank_ra=3, rd=24, sim_p_upper=0.425 / surprise=24
  - 楽天 2012 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2

**きっかけ以外での判定**（作り直しのきっかけ d-2014, d-2015, d-2019, d-2021, d-2022, d-2023 を除く）: n=20 成立=14 成立率=0.70 [0.48, 0.85] → **判断保留** / 判例: t-2022, t-2013, t-2021, t-2019, h-2012, l-2022

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: rank_rf=5, upper_half=True, rank=2, rank_ra=2, rd=-18, sim_p_upper=0.561

## P119: 得点だけが上位半分（得点3位以内・失点4位以下）のチームは、失点が5位以下なら B クラス（P118 の鏡）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 13 件: l-2018, l-2019, s-2022, f-2015, db-2024 ほか
- もし: `rank_ra >= 5` ならば: `upper_half == False`
- 識別子: `[where:rank_ra>=4, where:rank_rf<=3] rank_ra>=5 => upper_half==false`（指紋 `661afc308b616172`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '<=', 'value': 3}, {'col': 'rank_ra', 'op': '>=', 'value': 4}]} / 単位数: 41
- 見直す条件（反証）: 失点5位以下の単位の4分の1を超えて A クラス
- 注記: P118 と対称か（弱い側の深さが効くのは失点の側でも同じか）を見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 26 | 13 | 0.50 [0.32, 0.68] | -2.94σ（0.005） | 0.51 | 0.98 | 0.701 | 0 | 棄却 | 3 |
| 対偶 | 20 | 7 | 0.35 [0.18, 0.57] | -4.13σ（0.000） | 0.37 | 0.96 | 0.701 | 0 | 棄却 | 3 |
| 逆 | 21 | 13 | 0.62 [0.41, 0.79] | -1.39σ（0.130） | 0.63 | 0.98 | 0.701 | 0 | 判断保留 | 4 |
| 裏 | 15 | 7 | 0.47 [0.25, 0.70] | -2.53σ（0.017） | 0.49 | 0.96 | 0.701 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 13 件（対偶の判例も同じ）

- 西武 2018: rank_ra=6, upper_half=True, rank=1, rank_rf=1, rd=139, sim_p_upper=0.990 / surprise=139
  - 西武 2018 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2019: rank_ra=6, upper_half=True, rank=1, rank_rf=1, rd=61, sim_p_upper=0.824 / surprise=61
  - 西武 2019 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ヤクルト 2022: rank_ra=5, upper_half=True, rank=1, rank_rf=1, rd=53, sim_p_upper=0.852 / surprise=53
  - ヤクルト 2022 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 日本ハム 2015: rank_ra=5, upper_half=True, rank=2, rank_rf=3, rd=34, sim_p_upper=0.753 / surprise=34
  - 日本ハム 2015 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- DeNA 2024: rank_ra=5, upper_half=True, rank=3, rank_rf=1, rd=19, sim_p_upper=0.626 / surprise=19
  - DeNA 2024 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- DeNA 2016: rank_ra=5, upper_half=True, rank=3, rank_rf=3, rd=-16, sim_p_upper=0.560 / surprise=-16
  - DeNA 2016 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ヤクルト 2012: rank_ra=5, upper_half=True, rank=3, rank_rf=2, rd=-15, sim_p_upper=0.399 / surprise=-15
  - ヤクルト 2012 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- DeNA 2019: rank_ra=5, upper_half=True, rank=2, rank_rf=3, rd=-15, sim_p_upper=0.426 / surprise=-15
  - DeNA 2019 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2021: rank_ra=5, upper_half=True, rank=2, rank_rf=1, rd=14, sim_p_upper=0.550 / surprise=14
  - ロッテ 2021 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2013: rank_ra=5, upper_half=True, rank=3, rank_rf=3, rd=-12, sim_p_upper=0.222 / surprise=-12
  - ロッテ 2013 は「rank_ra >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ほか 3 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 8 件（裏の判例も同じ）

- 西武 2015: rank_ra=4, upper_half=False, rank=4, rank_rf=2, rd=58, sim_p_upper=0.680 / surprise=58
  - 西武 2015 は「upper_half == False」を満たすのに「rank_ra >= 5」を満たさない。なぜか？ → H2
- ロッテ 2019: rank_ra=4, upper_half=False, rank=4, rank_rf=2, rd=31, sim_p_upper=0.666 / surprise=31
  - ロッテ 2019 は「upper_half == False」を満たすのに「rank_ra >= 5」を満たさない。なぜか？ → H2
- 広島 2012: rank_ra=4, upper_half=False, rank=4, rank_rf=3, rd=-27, sim_p_upper=0.347 / surprise=-27
  - 広島 2012 は「upper_half == False」を満たすのに「rank_ra >= 5」を満たさない。なぜか？ → H2
- 巨人 2023: rank_ra=4, upper_half=False, rank=4, rank_rf=3, rd=16, sim_p_upper=0.738 / surprise=16
  - 巨人 2023 は「upper_half == False」を満たすのに「rank_ra >= 5」を満たさない。なぜか？ → H2
- 楽天 2022: rank_ra=4, upper_half=False, rank=4, rank_rf=2, rd=11, sim_p_upper=0.329 / surprise=11
  - 楽天 2022 は「upper_half == False」を満たすのに「rank_ra >= 5」を満たさない。なぜか？ → H2
- 広島 2022: rank_ra=4, upper_half=False, rank=5, rank_rf=2, rd=8, sim_p_upper=0.319 / surprise=8
  - 広島 2022 は「upper_half == False」を満たすのに「rank_ra >= 5」を満たさない。なぜか？ → H2
- ロッテ 2012: rank_ra=4, upper_half=False, rank=5, rank_rf=3, rd=-3, sim_p_upper=0.464 / surprise=-3
  - ロッテ 2012 は「upper_half == False」を満たすのに「rank_ra >= 5」を満たさない。なぜか？ → H2
- 西武 2016: rank_ra=4, upper_half=False, rank=4, rank_rf=2, rd=1, sim_p_upper=0.384 / surprise=1
  - 西武 2016 は「upper_half == False」を満たすのに「rank_ra >= 5」を満たさない。なぜか？ → H2

## P120: 失点だけが上位半分のチームは、得点した回の大きさが下位2位以内なら B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 7 件: h-2019, b-2022, db-2022, g-2016, l-2022 ほか
- もし: `inn_size_rank <= 2` ならば: `upper_half == False`
- 識別子: `[seasons=2013-2025, where:rank_ra<=3, where:rank_rf>=4] inn_size_rank<=2 => upper_half==false`（指紋 `ecd0af94b2f85356`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025', 'where': [{'col': 'rank_ra', 'op': '<=', 'value': 3}, {'col': 'rank_rf', 'op': '>=', 'value': 4}]} / 単位数: 39
- 見直す条件（反証）: きっかけの中日6単位を除いて、大きさ下位2位以内の単位の4分の1を超えて A クラス
- 注記: 得点の量（P118）と、点の入り方（回の大きさ）のどちらが、片側だけ上位のチームを分けるかを比べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 22 | 15 | 0.68 [0.47, 0.84] | -0.74σ（0.301） | 0.54 | 1.27 | 0.042 | 0 | 判断保留 | 4 |
| 対偶 | 18 | 11 | 0.61 [0.39, 0.80] | -1.36σ（0.139） | 0.44 | 1.40 | 0.042 | 0 | 判断保留 | 4 |
| 逆 | 21 | 15 | 0.71 [0.50, 0.86] | -0.38σ（0.433） | 0.56 | 1.27 | 0.042 | 0 | 判断保留 | 4 |
| 裏 | 17 | 11 | 0.65 [0.41, 0.83] | -0.98σ（0.235） | 0.46 | 1.40 | 0.042 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 7 件（対偶の判例も同じ）

- ソフトバンク 2019: inn_size_rank=1, upper_half=True, rank=2, rank_rf=4, inn_size_low_streak=1, sim_p_upper=0.527 / surprise=-0.103
  - ソフトバンク 2019 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- オリックス 2022: inn_size_rank=1, upper_half=True, rank=1, rank_rf=4, inn_size_low_streak=1, sim_p_upper=0.855 / surprise=-0.079
  - オリックス 2022 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- DeNA 2022: inn_size_rank=2, upper_half=True, rank=2, rank_rf=4, inn_size_low_streak=1, sim_p_upper=0.618 / surprise=-0.067
  - DeNA 2022 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 巨人 2016: inn_size_rank=1, upper_half=True, rank=2, rank_rf=4, inn_size_low_streak=1, sim_p_upper=0.698 / surprise=-0.050
  - 巨人 2016 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 西武 2022: inn_size_rank=2, upper_half=True, rank=3, rank_rf=5, inn_size_low_streak=1, sim_p_upper=0.526 / surprise=-0.045
  - 西武 2022 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 西武 2013: inn_size_rank=2, upper_half=True, rank=2, rank_rf=4, inn_size_low_streak=1, sim_p_upper=0.689 / surprise=-0.030
  - 西武 2013 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 楽天 2021: inn_size_rank=2, upper_half=True, rank=3, rank_rf=4, inn_size_low_streak=1, sim_p_upper=0.631 / surprise=-0.015
  - 楽天 2021 は「inn_size_rank <= 2」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5

**待った！判断保留** 逆に判例 6 件（裏の判例も同じ）

- 日本ハム 2019: inn_size_rank=5, upper_half=False, rank=5, rank_rf=5, inn_size_low_streak=0, sim_p_upper=0.242 / surprise=0.031
  - 日本ハム 2019 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5
- 広島 2024: inn_size_rank=3, upper_half=False, rank=4, rank_rf=5, inn_size_low_streak=0, sim_p_upper=0.324 / surprise=-0.028
  - 広島 2024 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5
- オリックス 2018: inn_size_rank=3, upper_half=False, rank=4, rank_rf=4, inn_size_low_streak=0, sim_p_upper=0.330 / surprise=-0.015
  - オリックス 2018 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5
- 阪神 2018: inn_size_rank=3, upper_half=False, rank=6, rank_rf=5, inn_size_low_streak=0, sim_p_upper=0.092 / surprise=0.010
  - 阪神 2018 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5
- 西武 2023: inn_size_rank=3, upper_half=False, rank=5, rank_rf=6, inn_size_low_streak=0, sim_p_upper=0.357 / surprise=-0.004
  - 西武 2023 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5
- 巨人 2017: inn_size_rank=4, upper_half=False, rank=4, rank_rf=4, inn_size_low_streak=0, sim_p_upper=0.844 / surprise=0.004
  - 巨人 2017 は「upper_half == False」を満たすのに「inn_size_rank <= 2」を満たさない。なぜか？ → H5

**きっかけ以外での判定**（作り直しのきっかけ d-2014, d-2015, d-2019, d-2021, d-2022, d-2023 を除く）: n=16 成立=9 成立率=0.56 [0.33, 0.77] → **判断保留** / 判例: h-2019, b-2022, db-2022, g-2016, l-2022, l-2013, e-2021

## P121: 失点だけが上位半分で得点が5位以下のチームは、得失点差がプラスなら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2019
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[where:rank_ra<=3, where:rank_rf>=5] rd>0 => upper_half==true`（指紋 `5f87c601c0a50708`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_ra', 'op': '<=', 'value': 3}, {'col': 'rank_rf', 'op': '>=', 'value': 5}]} / 単位数: 26
- 見直す条件（反証）: 2026年以降、この範囲で得失点差プラスなのに B クラスの単位が出る（中日 2019年に続く判例）
- 注記: R28 の記述（判例は中日 2019年だけ）を見た後に作った。同じデータでは確かめにならず、きっかけ以外の単位はほぼ残らない。確かめは 2026年以降（analysis.toml の [confirm]）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 6 | 5 | 0.83 [0.44, 0.97] | +0.47σ（0.534） | 0.23 | 3.61 | 0.001 | 0 | 判断保留 | 4 |
| 対偶 | 20 | 19 | 0.95 [0.76, 0.99] | +2.07σ（0.024） | 0.77 | 1.23 | 0.001 | 0 | 支持 | 1 |
| 逆 | 6 | 5 | 0.83 [0.44, 0.97] | +0.47σ（0.534） | 0.23 | 3.61 | 0.001 | 0 | 判断保留 | 4 |
| 裏 | 20 | 19 | 0.95 [0.76, 0.99] | +2.07σ（0.024） | 0.77 | 1.23 | 0.001 | 0 | 支持 | 1 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2019 **(focus)**: rd=19, upper_half=False, rank=5, rank_ra=1, rank_rf=5, wins_vs_pythag=-4.71, sim_p_upper=0.627 / surprise=19
  - 中日 2019 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 阪神 2019: rd=-28, upper_half=True, rank=3, rank_ra=2, rank_rf=6, wins_vs_pythag=+3.68, sim_p_upper=0.424 / surprise=-28
  - 阪神 2019 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2

**きっかけ以外での判定**（作り直しのきっかけ t-2013, t-2021, t-2022, h-2012, l-2022, d-2019 を除く）: n=0 成立=0 成立率=- [0.00, 1.00] → **判断保留** / 判例なし

## P122: 得点だけが上位半分（得点3位以内・失点4位以下）のチームは、得失点差がプラスなら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: l-2015, m-2019, g-2023, e-2022, c-2022 ほか
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[where:rank_ra>=4, where:rank_rf<=3] rd>0 => upper_half==true`（指紋 `100214fdc4f6f6ba`）
- 兄弟（範囲と結論が同じ、条件が違う）: P124
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '<=', 'value': 3}, {'col': 'rank_ra', 'op': '>=', 'value': 4}]} / 単位数: 41
- 見直す条件（反証）: 得失点差プラスの単位の4分の1を超えて B クラス
- 注記: P121 の鏡（得点の側）。この範囲の得失点差と順位の組はまだ見ていない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 10 | 0.62 [0.39, 0.82] | -1.15σ（0.190） | 0.49 | 1.28 | 0.139 | 0 | 判断保留 | 4 |
| 対偶 | 21 | 15 | 0.71 [0.50, 0.86] | -0.38σ（0.433） | 0.61 | 1.17 | 0.139 | 0 | 判断保留 | 4 |
| 逆 | 20 | 10 | 0.50 [0.30, 0.70] | -2.58σ（0.014） | 0.39 | 1.28 | 0.139 | 0 | 棄却 | 3 |
| 裏 | 25 | 15 | 0.60 [0.41, 0.77] | -1.73σ（0.071） | 0.51 | 1.17 | 0.139 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- 西武 2015: rd=58, upper_half=False, rank=4, rank_rf=2, rank_ra=4, wins_vs_pythag=-6.07, sim_p_upper=0.680 / surprise=58
  - 西武 2015 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- ロッテ 2019: rd=31, upper_half=False, rank=4, rank_rf=2, rank_ra=4, wins_vs_pythag=-3.65, sim_p_upper=0.666 / surprise=31
  - ロッテ 2019 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 巨人 2023: rd=16, upper_half=False, rank=4, rank_rf=3, rank_ra=4, wins_vs_pythag=-1.50, sim_p_upper=0.738 / surprise=16
  - 巨人 2023 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 楽天 2022: rd=11, upper_half=False, rank=4, rank_rf=2, rank_ra=4, wins_vs_pythag=-2.34, sim_p_upper=0.329 / surprise=11
  - 楽天 2022 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 広島 2022: rd=8, upper_half=False, rank=5, rank_rf=2, rank_ra=4, wins_vs_pythag=-4.93, sim_p_upper=0.319 / surprise=8
  - 広島 2022 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 西武 2016: rd=1, upper_half=False, rank=4, rank_rf=2, rank_ra=4, wins_vs_pythag=-6.10, sim_p_upper=0.384 / surprise=1
  - 西武 2016 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**異議あり（不成立）** 逆に判例 10 件（裏の判例も同じ）

- オリックス 2025: rd=-17, upper_half=True, rank=3, rank_rf=3, rank_ra=4, wins_vs_pythag=+6.13, sim_p_upper=0.575 / surprise=-17
  - オリックス 2025 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- DeNA 2016: rd=-16, upper_half=True, rank=3, rank_rf=3, rank_ra=5, wins_vs_pythag=0.767, sim_p_upper=0.560 / surprise=-16
  - DeNA 2016 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- ヤクルト 2012: rd=-15, upper_half=True, rank=3, rank_rf=2, rank_ra=5, wins_vs_pythag=+3.30, sim_p_upper=0.399 / surprise=-15
  - ヤクルト 2012 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- 阪神 2014: rd=-15, upper_half=True, rank=2, rank_rf=3, rank_ra=4, wins_vs_pythag=+5.12, sim_p_upper=0.293 / surprise=-15
  - 阪神 2014 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- DeNA 2019: rd=-15, upper_half=True, rank=2, rank_rf=3, rank_ra=5, wins_vs_pythag=+2.59, sim_p_upper=0.426 / surprise=-15
  - DeNA 2019 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- ロッテ 2013: rd=-12, upper_half=True, rank=3, rank_rf=3, rank_ra=5, wins_vs_pythag=+4.35, sim_p_upper=0.222 / surprise=-12
  - ロッテ 2013 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- ヤクルト 2018: rd=-7, upper_half=True, rank=2, rank_rf=2, rank_ra=6, wins_vs_pythag=+5.18, sim_p_upper=0.675 / surprise=-7
  - ヤクルト 2018 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- 西武 2012: rd=-2, upper_half=True, rank=2, rank_rf=1, rank_ra=5, wins_vs_pythag=+4.74, sim_p_upper=0.467 / surprise=-2
  - 西武 2012 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- ロッテ 2024: rd=-2, upper_half=True, rank=3, rank_rf=3, rank_ra=5, wins_vs_pythag=+2.75, sim_p_upper=0.651 / surprise=-2
  - ロッテ 2024 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- DeNA 2017: rd=-1, upper_half=True, rank=3, rank_rf=2, rank_ra=4, wins_vs_pythag=+4.11, sim_p_upper=0.317 / surprise=-1
  - DeNA 2017 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: rd=35, upper_half=False, rank=4, rank_rf=1, rank_ra=4, wins_vs_pythag=-4.32, sim_p_upper=0.705

## P123: 失点だけが上位半分（失点3位以内・得点4位以下）のチームは、得失点差がプラスなら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 3 件: g-2017, e-2012, d-2019
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[where:rank_ra<=3, where:rank_rf>=4] rd>0 => upper_half==true`（指紋 `213b1a6b6d580d4f`）
- 兄弟（範囲と結論が同じ、条件が違う）: P125
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_ra', 'op': '<=', 'value': 3}, {'col': 'rank_rf', 'op': '>=', 'value': 4}]} / 単位数: 43
- 見直す条件（反証）: きっかけの6単位を除いて、得失点差プラスの単位の4分の1を超えて B クラス
- 注記: P121 の範囲を得点4位まで広げた形。得点4位の17単位は見ていないので、きっかけ以外はその部分で読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 19 | 16 | 0.84 [0.62, 0.94] | +0.93σ（0.263） | 0.47 | 1.81 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 23 | 20 | 0.87 [0.68, 0.95] | +1.32σ（0.137） | 0.56 | 1.56 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 20 | 16 | 0.80 [0.58, 0.92] | +0.52σ（0.415） | 0.44 | 1.81 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 24 | 20 | 0.83 [0.64, 0.93] | +0.94σ（0.247） | 0.53 | 1.56 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 3 件（対偶の判例も同じ）

- 巨人 2017: rd=32, upper_half=False, rank=4, rank_ra=1, rank_rf=4, wins_vs_pythag=-1.94, sim_p_upper=0.844 / surprise=32
  - 巨人 2017 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 楽天 2012: rd=24, upper_half=False, rank=4, rank_ra=3, rank_rf=4, wins_vs_pythag=-3.07, sim_p_upper=0.425 / surprise=24
  - 楽天 2012 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: rd=19, upper_half=False, rank=5, rank_ra=1, rank_rf=5, wins_vs_pythag=-4.71, sim_p_upper=0.627 / surprise=19
  - 中日 2019 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**待った！判断保留** 逆に判例 4 件（裏の判例も同じ）

- DeNA 2022: rd=-37, upper_half=True, rank=2, rank_ra=3, rank_rf=4, wins_vs_pythag=+7.13, sim_p_upper=0.618 / surprise=-37
  - DeNA 2022 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- 阪神 2019: rd=-28, upper_half=True, rank=3, rank_ra=2, rank_rf=6, wins_vs_pythag=+3.68, sim_p_upper=0.424 / surprise=-28
  - 阪神 2019 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- 巨人 2016: rd=-24, upper_half=True, rank=2, rank_ra=2, rank_rf=4, wins_vs_pythag=+3.89, sim_p_upper=0.698 / surprise=-24
  - 巨人 2016 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- ロッテ 2015: rd=-2, upper_half=True, rank=3, rank_ra=3, rank_rf=4, wins_vs_pythag=+2.23, sim_p_upper=0.262 / surprise=-2
  - ロッテ 2015 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2

**きっかけ以外での判定**（作り直しのきっかけ t-2013, t-2021, t-2022, h-2012, l-2022, d-2019 を除く）: n=13 成立=11 成立率=0.85 [0.58, 0.96] → **判断保留** / 判例: g-2017, e-2012

## P124: 得点だけが上位半分のチームは、点の差から見込まれるより多く勝っていれば A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 6 件: e-2023, s-2016, g-2022, m-2022, db-2015 ほか
- もし: `wins_vs_pythag > 0` ならば: `upper_half == True`
- 識別子: `[where:rank_ra>=4, where:rank_rf<=3] wins_vs_pythag>0 => upper_half==true`（指紋 `412955a6842c100e`）
- 兄弟（範囲と結論が同じ、条件が違う）: P122
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_rf', 'op': '<=', 'value': 3}, {'col': 'rank_ra', 'op': '>=', 'value': 4}]} / 単位数: 41
- 見直す条件（反証）: きっかけの16単位を除いて、見込みより多く勝った単位の4分の1を超えて B クラス
- 注記: wins_vs_pythag は勝ち数と、得点・失点から見込まれる勝ち数（固定指数）の差。きっかけ以外の25単位で読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 23 | 17 | 0.74 [0.54, 0.87] | -0.12σ（0.532） | 0.49 | 1.52 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 21 | 15 | 0.71 [0.50, 0.86] | -0.38σ（0.433） | 0.44 | 1.63 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 20 | 17 | 0.85 [0.64, 0.95] | +1.03σ（0.225） | 0.56 | 1.52 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 18 | 15 | 0.83 [0.61, 0.94] | +0.82σ（0.306） | 0.51 | 1.63 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 6 件（対偶の判例も同じ）

- 楽天 2023: wins_vs_pythag=+4.68, upper_half=False, rank=4, rd=-43, rank_rf=2, rank_ra=6, one_run_net=6 / surprise=+4.68
  - 楽天 2023 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ヤクルト 2016: wins_vs_pythag=+3.04, upper_half=False, rank=5, rd=-100, rank_rf=2, rank_ra=6, one_run_net=0 / surprise=+3.04
  - ヤクルト 2016 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 巨人 2022: wins_vs_pythag=+2.61, upper_half=False, rank=4, rd=-41, rank_rf=3, rank_ra=6, one_run_net=4 / surprise=+2.61
  - 巨人 2022 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- ロッテ 2022: wins_vs_pythag=+2.38, upper_half=False, rank=5, rd=-35, rank_rf=3, rank_ra=6, one_run_net=-12 / surprise=+2.38
  - ロッテ 2022 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- DeNA 2015: wins_vs_pythag=+1.52, upper_half=False, rank=6, rd=-90, rank_rf=2, rank_ra=6, one_run_net=0 / surprise=+1.52
  - DeNA 2015 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 広島 2021: wins_vs_pythag=0.845, upper_half=False, rank=4, rd=-32, rank_rf=3, rank_ra=5, one_run_net=-2 / surprise=0.845
  - 広島 2021 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3

**待った！判断保留** 逆に判例 3 件（裏の判例も同じ）

- ソフトバンク 2023: wins_vs_pythag=-2.56, upper_half=True, rank=3, rd=29, rank_rf=1, rank_ra=4, one_run_net=2 / surprise=-2.56
  - ソフトバンク 2023 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- DeNA 2024: wins_vs_pythag=-1.37, upper_half=True, rank=3, rd=19, rank_rf=1, rank_ra=5, one_run_net=-5 / surprise=-1.37
  - DeNA 2024 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- ヤクルト 2015: wins_vs_pythag=-1.10, upper_half=True, rank=1, rd=56, rank_rf=1, rank_ra=4, one_run_net=2 / surprise=-1.10
  - ヤクルト 2015 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3

**きっかけ以外での判定**（作り直しのきっかけ b-2025, c-2022, db-2016, db-2017, db-2019, e-2022, g-2023, l-2012, l-2015, l-2016, m-2013, m-2019, m-2024, s-2012, s-2018, t-2014 を除く）: n=13 成立=7 成立率=0.54 [0.29, 0.77] → **判断保留** / 判例: e-2023, s-2016, g-2022, m-2022, db-2015, c-2021

## P125: 失点だけが上位半分のチームは、点の差から見込まれるより多く勝っていれば A クラス（P124 の鏡）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 5 件: d-2022, db-2018, d-2023, d-2021, l-2025
- もし: `wins_vs_pythag > 0` ならば: `upper_half == True`
- 識別子: `[where:rank_ra<=3, where:rank_rf>=4] wins_vs_pythag>0 => upper_half==true`（指紋 `47dce11519f6107a`）
- 兄弟（範囲と結論が同じ、条件が違う）: P123
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rank_ra', 'op': '<=', 'value': 3}, {'col': 'rank_rf', 'op': '>=', 'value': 4}]} / 単位数: 43
- 見直す条件（反証）: （P124 と率を比べるための命題）
- 注記: R28 で見た26単位（得点5・6位）を除き、得点4位の17単位で読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 10 回、元の命題に異議あり 10 回（どれかの形に異議あり 10 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 12 | 0.71 [0.47, 0.87] | -0.42σ（0.426） | 0.47 | 1.52 | 0.012 | 0 | 判断保留 | 4 |
| 対偶 | 23 | 18 | 0.78 [0.58, 0.90] | +0.36σ（0.468） | 0.60 | 1.29 | 0.012 | 0 | 判断保留 | 4 |
| 逆 | 20 | 12 | 0.60 [0.39, 0.78] | -1.55σ（0.102） | 0.40 | 1.52 | 0.012 | 0 | 判断保留 | 4 |
| 裏 | 26 | 18 | 0.69 [0.50, 0.83] | -0.68σ（0.315） | 0.53 | 1.29 | 0.012 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 5 件（対偶の判例も同じ）

- 中日 2022 **(focus)**: wins_vs_pythag=+6.93, upper_half=False, rank=6, rd=-81, rank_rf=6, rank_ra=2, one_run_net=2 / surprise=+6.93
  - 中日 2022 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- DeNA 2018: wins_vs_pythag=+3.92, upper_half=False, rank=4, rd=-70, rank_rf=6, rank_ra=3, one_run_net=-1 / surprise=+3.92
  - DeNA 2018 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2023 **(focus)**: wins_vs_pythag=+2.18, upper_half=False, rank=6, rd=-108, rank_rf=6, rank_ra=3, one_run_net=-3 / surprise=+2.18
  - 中日 2023 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2021 **(focus)**: wins_vs_pythag=+1.48, upper_half=False, rank=5, rd=-73, rank_rf=6, rank_ra=1, one_run_net=-2 / surprise=+1.48
  - 中日 2021 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 西武 2025: wins_vs_pythag=+1.03, upper_half=False, rank=5, rd=-55, rank_rf=6, rank_ra=3, one_run_net=4 / surprise=+1.03
  - 西武 2025 は「wins_vs_pythag > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3

**待った！判断保留** 逆に判例 8 件（裏の判例も同じ）

- 阪神 2022: wins_vs_pythag=-9.93, upper_half=True, rank=3, rd=61, rank_rf=5, rank_ra=1, one_run_net=-5 / surprise=-9.93
  - 阪神 2022 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- 巨人 2024: wins_vs_pythag=-2.87, upper_half=True, rank=1, rd=81, rank_rf=4, rank_ra=1, one_run_net=4 / surprise=-2.87
  - 巨人 2024 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- 巨人 2015: wins_vs_pythag=-2.40, upper_half=True, rank=2, rd=46, rank_rf=4, rank_ra=1, one_run_net=1 / surprise=-2.40
  - 巨人 2015 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- 阪神 2013: wins_vs_pythag=-2.40, upper_half=True, rank=2, rd=43, rank_rf=5, rank_ra=1, one_run_net=2 / surprise=-2.40
  - 阪神 2013 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- ソフトバンク 2012: wins_vs_pythag=-2.15, upper_half=True, rank=3, rd=23, rank_rf=5, rank_ra=1, one_run_net=-3 / surprise=-2.15
  - ソフトバンク 2012 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- 広島 2013: wins_vs_pythag=-1.85, upper_half=True, rank=3, rd=3, rank_rf=4, rank_ra=3, one_run_net=-1 / surprise=-1.85
  - 広島 2013 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- 楽天 2021: wins_vs_pythag=-0.817, upper_half=True, rank=3, rd=25, rank_rf=4, rank_ra=3, one_run_net=2 / surprise=-0.817
  - 楽天 2021 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3
- 西武 2022: wins_vs_pythag=-0.247, upper_half=True, rank=3, rd=16, rank_rf=5, rank_ra=1, one_run_net=-3 / surprise=-0.247
  - 西武 2022 は「upper_half == True」を満たすのに「wins_vs_pythag > 0」を満たさない。なぜか？ → H3

**きっかけ以外での判定**（作り直しのきっかけ b-2013, b-2015, b-2024, c-2024, d-2014, d-2015, d-2019, d-2021, d-2022, d-2023, db-2018, e-2018, f-2019, f-2023, h-2012, l-2022, l-2023, l-2024, l-2025, t-2012, t-2013, t-2016, t-2018, t-2019, t-2021, t-2022 を除く）: n=10 成立=10 成立率=1.00 [0.72, 1.00] → **判断保留** / 判例なし

## P126: 得点も失点も、1試合あたりで他球団の平均を上回っていない（優位がない）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 7 件: t-2015, db-2022, db-2019, c-2023, m-2013 ほか
- もし: `rf_adv <= 0 かつ ra_adv <= 0` ならば: `upper_half == False`
- 識別子: `[all] ra_adv<=0 & rf_adv<=0 => upper_half==false`（指紋 `2dc6e335fd5e67d9`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P115, P138, P147, P148, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 親: P115（変更: 上位半分を順位（3位以内）ではなく、1試合あたりの優位の符号で決める。R31 で、失点3位でも優位がほぼ 0 か負の単位が4つあった）
- 見直す条件（反証）: 優位のないチーム・シーズンの4分の1を超えて A クラス
- 注記: P115 の対偶（A なら一方は3位以内）が、量で決めても保たれるかを見る
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 37 | 30 | 0.81 [0.66, 0.91] | +0.85σ（0.259） | 0.50 | 1.62 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 71 | 0.91 [0.83, 0.96] | +3.27σ（0.000） | 0.76 | 1.19 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 30 | 0.38 [0.28, 0.50] | -7.45σ（0.000） | 0.24 | 1.62 | 0.000 | 0 | 修正 | 2 |
| 裏 | 119 | 71 | 0.60 [0.51, 0.68] | -3.86σ（0.000） | 0.50 | 1.19 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 7 件（対偶の判例も同じ）

- 阪神 2015: rf_adv=-0.315, ra_adv=-0.298, upper_half=True, rank=3, rank_rf=6, rank_ra=5, run_balance=-0.613 / surprise=-85
  - 阪神 2015 は「rf_adv <= 0 かつ ra_adv <= 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- DeNA 2022: rf_adv=-0.192, ra_adv=-0.067, upper_half=True, rank=2, rank_rf=4, rank_ra=3, run_balance=-0.259 / surprise=-37
  - DeNA 2022 は「rf_adv <= 0 かつ ra_adv <= 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- DeNA 2019: rf_adv=-0.043, ra_adv=-0.045, upper_half=True, rank=2, rank_rf=3, rank_ra=5, run_balance=-0.088 / surprise=-15
  - DeNA 2019 は「rf_adv <= 0 かつ ra_adv <= 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 広島 2023: rf_adv=-0.080, ra_adv=-0.067, upper_half=True, rank=2, rank_rf=5, rank_ra=5, run_balance=-0.147 / surprise=-15
  - 広島 2023 は「rf_adv <= 0 かつ ra_adv <= 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2013: rf_adv=-0.062, ra_adv=-0.175, upper_half=True, rank=3, rank_rf=3, rank_ra=5, run_balance=-0.237 / surprise=-12
  - ロッテ 2013 は「rf_adv <= 0 かつ ra_adv <= 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2015: rf_adv=-0.103, ra_adv=-0.014, upper_half=True, rank=3, rank_rf=4, rank_ra=3, run_balance=-0.117 / surprise=-2
  - ロッテ 2015 は「rf_adv <= 0 かつ ra_adv <= 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2016: rf_adv=-0.004, ra_adv=-0.080, upper_half=True, rank=3, rank_rf=4, rank_ra=3, run_balance=-0.084 / surprise=1
  - ロッテ 2016 は「rf_adv <= 0 かつ ra_adv <= 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 48 件（裏の判例も同じ）

- 中日 2023 **(focus)**: rf_adv=-0.944, ra_adv=0.017, upper_half=False, rank=6, rank_rf=6, rank_ra=3, run_balance=-0.927 / surprise=-108
  - 中日 2023 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- ヤクルト 2013: rf_adv=0.061, ra_adv=-0.799, upper_half=False, rank=6, rank_rf=3, rank_ra=5, run_balance=-0.737 / surprise=-105
  - ヤクルト 2013 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- ヤクルト 2016: rf_adv=0.264, ra_adv=-1.01, upper_half=False, rank=5, rank_rf=2, rank_ra=6, run_balance=-0.747 / surprise=-100
  - ヤクルト 2016 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- ソフトバンク 2013: rf_adv=0.671, ra_adv=0.008, upper_half=False, rank=4, rank_rf=1, rank_ra=3, run_balance=0.679 / surprise=98
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- DeNA 2015: rf_adv=0.046, ra_adv=-0.701, upper_half=False, rank=6, rank_rf=2, rank_ra=6, run_balance=-0.655 / surprise=-90
  - DeNA 2015 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- 楽天 2024: rf_adv=0.106, ra_adv=-0.828, upper_half=False, rank=4, rank_rf=4, rank_ra=6, run_balance=-0.722 / surprise=-87
  - 楽天 2024 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- ヤクルト 2019: rf_adv=0.460, ra_adv=-1.12, upper_half=False, rank=6, rank_rf=2, rank_ra=6, run_balance=-0.659 / surprise=-83
  - ヤクルト 2019 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- 中日 2022 **(focus)**: rf_adv=-0.888, ra_adv=0.260, upper_half=False, rank=6, rank_rf=6, rank_ra=2, run_balance=-0.628 / surprise=-81
  - 中日 2022 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- 中日 2016 **(focus)**: rf_adv=-0.524, ra_adv=0.004, upper_half=False, rank=6, rank_rf=6, rank_ra=4, run_balance=-0.520 / surprise=-73
  - 中日 2016 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rf_adv=-1.13, ra_adv=0.564, upper_half=False, rank=5, rank_rf=6, rank_ra=1, run_balance=-0.568 / surprise=-73
  - 中日 2021 は「upper_half == False」を満たすのに「rf_adv <= 0 かつ ra_adv <= 0」を満たさない。なぜか？ → H2
- ほか 38 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 西武 2020: rf_adv=-0.148, ra_adv=-0.492, upper_half=True, rank=3, rank_rf=4, rank_ra=6, run_balance=-0.640

## P127: 失点だけに優位がある（失点の優位 > 0、得点の優位 ≤ 0）チームは、得点が5位以下なら B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 5 件: t-2022, t-2013, t-2019, h-2012, l-2022
- もし: `rank_rf >= 5` ならば: `upper_half == False`
- 識別子: `[where:ra_adv>0, where:rf_adv<=0] rank_rf>=5 => upper_half==false`（指紋 `618458cc73e3a64c`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'ra_adv', 'op': '>', 'value': 0}, {'col': 'rf_adv', 'op': '<=', 'value': 0}]} / 単位数: 42
- 親: P118（変更: 失点だけ上位の範囲を、順位ではなく優位の符号で決める（R31））
- 見直す条件（反証）: きっかけの中日6単位を除いて、4分の1を超えて A クラス
- 注記: P118 と同じく中日の6単位を見た後の条件。きっかけ以外で読む
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 25 | 20 | 0.80 [0.61, 0.91] | +0.58σ（0.378） | 0.57 | 1.40 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 18 | 13 | 0.72 [0.49, 0.88] | -0.27σ（0.481） | 0.40 | 1.78 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 24 | 20 | 0.83 [0.64, 0.93] | +0.94σ（0.247） | 0.60 | 1.40 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 17 | 13 | 0.76 [0.53, 0.90] | +0.14σ（0.574） | 0.43 | 1.78 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 5 件（対偶の判例も同じ）

- 阪神 2022: rank_rf=5, upper_half=True, rank=3, rank_ra=1, ra_adv=0.822, rf_adv=-0.259 / surprise=61
  - 阪神 2022 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2013: rank_rf=5, upper_half=True, rank=2, rank_ra=1, ra_adv=0.818, rf_adv=-0.322 / surprise=43
  - 阪神 2013 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2019: rank_rf=6, upper_half=True, rank=3, rank_ra=2, ra_adv=0.333, rf_adv=-0.530 / surprise=-28
  - 阪神 2019 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ソフトバンク 2012: rank_rf=5, upper_half=True, rank=3, rank_ra=1, ra_adv=0.440, rf_adv=-0.276 / surprise=23
  - ソフトバンク 2012 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2022: rank_rf=5, upper_half=True, rank=3, rank_ra=1, ra_adv=0.393, rf_adv=-0.310 / surprise=16
  - 西武 2022 は「rank_rf >= 5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**待った！判断保留** 逆に判例 4 件（裏の判例も同じ）

- 巨人 2017: rank_rf=4, upper_half=False, rank=4, rank_ra=1, ra_adv=0.590, rf_adv=-0.283 / surprise=32
  - 巨人 2017 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 広島 2012: rank_rf=3, upper_half=False, rank=4, rank_ra=4, ra_adv=0.017, rf_adv=-0.214 / surprise=-27
  - 広島 2012 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- オリックス 2018: rank_rf=4, upper_half=False, rank=4, rank_ra=1, ra_adv=0.285, rf_adv=-0.601 / surprise=-27
  - オリックス 2018 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2
- 広島 2019: rank_rf=4, upper_half=False, rank=4, rank_ra=4, ra_adv=0.039, rf_adv=-0.085 / surprise=-10
  - 広島 2019 は「upper_half == False」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2

**きっかけ以外での判定**（作り直しのきっかけ d-2014, d-2015, d-2019, d-2021, d-2022, d-2023 を除く）: n=19 成立=14 成立率=0.74 [0.51, 0.88] → **判断保留** / 判例: t-2022, t-2013, t-2019, h-2012, l-2022

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rank_rf=6, upper_half=True, rank=3, rank_ra=4, ra_adv=0.047, rf_adv=-0.647
- ロッテ 2020: rank_rf=5, upper_half=True, rank=2, rank_ra=2, ra_adv=0.148, rf_adv=-0.328

## P128: 失点だけに優位があるチームは、得失点差がプラスなら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: g-2017, d-2019
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[where:ra_adv>0, where:rf_adv<=0] rd>0 => upper_half==true`（指紋 `74fa0f8a119240d1`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'ra_adv', 'op': '>', 'value': 0}, {'col': 'rf_adv', 'op': '<=', 'value': 0}]} / 単位数: 42
- 親: P123（変更: 失点だけ上位の範囲を、順位ではなく優位の符号で決める（R31））
- 見直す条件（反証）: きっかけの6単位を除いて、得失点差プラスの単位の4分の1を超えて B クラス
- 注記: P123 の範囲を量で決め直した形
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 15 | 0.88 [0.66, 0.97] | +1.26σ（0.164） | 0.43 | 2.06 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 24 | 22 | 0.92 [0.74, 0.98] | +1.89σ（0.040） | 0.60 | 1.54 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 18 | 15 | 0.83 [0.61, 0.94] | +0.82σ（0.306） | 0.40 | 2.06 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 25 | 22 | 0.88 [0.70, 0.96] | +1.50σ（0.096） | 0.57 | 1.54 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- 巨人 2017: rd=32, upper_half=False, rank=4, rank_ra=1, rank_rf=4, wins_vs_pythag=-1.94 / surprise=32
  - 巨人 2017 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: rd=19, upper_half=False, rank=5, rank_ra=1, rank_rf=5, wins_vs_pythag=-4.71 / surprise=19
  - 中日 2019 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**待った！判断保留** 逆に判例 3 件（裏の判例も同じ）

- 阪神 2019: rd=-28, upper_half=True, rank=3, rank_ra=2, rank_rf=6, wins_vs_pythag=+3.68 / surprise=-28
  - 阪神 2019 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- 巨人 2016: rd=-24, upper_half=True, rank=2, rank_ra=2, rank_rf=4, wins_vs_pythag=+3.89 / surprise=-24
  - 巨人 2016 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2
- 阪神 2014: rd=-15, upper_half=True, rank=2, rank_ra=4, rank_rf=3, wins_vs_pythag=+5.12 / surprise=-15
  - 阪神 2014 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2

**きっかけ以外での判定**（作り直しのきっかけ t-2013, t-2021, t-2022, h-2012, l-2022, d-2019 を除く）: n=12 成立=11 成立率=0.92 [0.65, 0.99] → **判断保留** / 判例: g-2017

## P129: 中日以外で、失点だけに優位がある B クラスは、得点した回の大きさが2年以上続けて下位2位以内なら、得点の不足が大きい（1試合 0.6点を超える）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: t-2016
- もし: `inn_size_low_streak >= 2` ならば: `rf_adv < -0.6`
- 識別子: `[seasons=2013-2025, where:ra_adv>0, where:rf_adv<=0, where:team!="d", where:upper_half==false] inn_size_low_streak>=2 => rf_adv<-0.6`（指紋 `b814d7b7333d08dc`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025', 'where': [{'col': 'team', 'op': '!=', 'value': 'd'}, {'col': 'ra_adv', 'op': '>', 'value': 0}, {'col': 'rf_adv', 'op': '<=', 'value': 0}, {'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 14
- 見直す条件（反証）: 続けて低い単位の4分の1を超えて、不足が 0.6 以下
- 注記: R31 の中日の2つの層（届きかけた年 −0.25〜−0.32、届かなかった年 −0.89〜−1.13）の間をとって 0.6 を境にした（中日を見た後の境）。分ける条件は中日以外で探す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 2 | 1 | 0.50 [0.09, 0.91] | -0.82σ（0.438） | 0.36 | 1.40 | 0.604 | 0 | 判断保留 | 4 |
| 対偶 | 9 | 8 | 0.89 [0.57, 0.98] | +0.96σ（0.300） | 0.86 | 1.04 | 0.604 | 0 | 判断保留 | 4 |
| 逆 | 5 | 1 | 0.20 [0.04, 0.62] | -2.84σ（0.016） | 0.14 | 1.40 | 0.604 | 0 | 判断保留 | 4 |
| 裏 | 12 | 8 | 0.67 [0.39, 0.86] | -0.67σ（0.351） | 0.64 | 1.04 | 0.604 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 阪神 2016: inn_size_low_streak=2, rf_adv=-0.474, rank=4, inn_size_rank=2, ra_adv=0.231, run_balance=-0.243 / surprise=-0.474
  - 阪神 2016 は「inn_size_low_streak >= 2」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H5, H6

**待った！判断保留** 逆に判例 4 件（裏の判例も同じ）

- 楽天 2018: inn_size_low_streak=1, rf_adv=-0.752, rank=6, inn_size_rank=1, ra_adv=0.134, run_balance=-0.618 / surprise=-0.752
  - 楽天 2018 は「rf_adv < -0.6」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- 日本ハム 2021: inn_size_low_streak=1, rf_adv=-0.674, rank=5, inn_size_rank=1, ra_adv=0.117, run_balance=-0.557 / surprise=-0.674
  - 日本ハム 2021 は「rf_adv < -0.6」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- オリックス 2024: inn_size_low_streak=1, rf_adv=-0.649, rank=5, inn_size_rank=1, ra_adv=0.271, run_balance=-0.378 / surprise=-0.649
  - オリックス 2024 は「rf_adv < -0.6」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6
- オリックス 2018: inn_size_low_streak=0, rf_adv=-0.601, rank=4, inn_size_rank=3, ra_adv=0.285, run_balance=-0.316 / surprise=-0.601
  - オリックス 2018 は「rf_adv < -0.6」を満たすのに「inn_size_low_streak >= 2」を満たさない。なぜか？ → H5, H6

## P130: 中日以外で、失点だけに優位がある B クラスは、四死球と長打がどちらも他球団より少なければ、得点の不足が大きい（1試合 0.6点を超える）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 6 件: b-2013, l-2023, f-2019, c-2024, t-2012 ほか
- もし: `bat_d_bb_pa < 0 かつ bat_d_iso < 0` ならば: `rf_adv < -0.6`
- 識別子: `[where:ra_adv>0, where:rf_adv<=0, where:team!="d", where:upper_half==false] bat_d_bb_pa<0 & bat_d_iso<0 => rf_adv<-0.6`（指紋 `2ffabd164a495b85`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}, {'col': 'ra_adv', 'op': '>', 'value': 0}, {'col': 'rf_adv', 'op': '<=', 'value': 0}, {'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 16
- 見直す条件（反証）: 四死球も長打も少ない単位の4分の1を超えて、不足が 0.6 以下
- 注記: R6〜R9 の「中日は四死球と長打がそれぞれ別々に少ない」を、届かなかった層を分ける条件として中日以外で試す。境 0.6 は P129 と同じ
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 5 | 0.45 [0.21, 0.72] | -2.26σ（0.034） | 0.31 | 1.45 | 0.106 | 0 | 棄却 | 3 |
| 対偶 | 11 | 5 | 0.45 [0.21, 0.72] | -2.26σ（0.034） | 0.31 | 1.45 | 0.106 | 0 | 棄却 | 3 |
| 逆 | 5 | 5 | 1.00 [0.57, 1.00] | +1.29σ（0.237） | 0.69 | 1.45 | 0.106 | 0 | 判断保留 | 4 |
| 裏 | 5 | 5 | 1.00 [0.57, 1.00] | +1.29σ（0.237） | 0.69 | 1.45 | 0.106 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 6 件（対偶の判例も同じ）

- オリックス 2013: bat_d_bb_pa=-0.005, bat_d_iso=-0.005, rf_adv=-0.554, rank=5, bat_d_avg=-0.007, ra_adv=0.283, run_balance=-0.271 / surprise=-0.554
  - オリックス 2013 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 西武 2023: bat_d_bb_pa=-0.009, bat_d_iso=-0.008, rf_adv=-0.491, rank=5, bat_d_avg=-0.009, ra_adv=0.260, run_balance=-0.231 / surprise=-0.491
  - 西武 2023 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 日本ハム 2019: bat_d_bb_pa=-0.000, bat_d_iso=-0.031, rf_adv=-0.473, rank=5, bat_d_avg=-0.000, ra_adv=0.217, run_balance=-0.256 / surprise=-0.473
  - 日本ハム 2019 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 広島 2024: bat_d_bb_pa=-0.019, bat_d_iso=-0.023, rf_adv=-0.382, rank=4, bat_d_avg=-0.008, ra_adv=0.340, run_balance=-0.042 / surprise=-0.382
  - 広島 2024 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 阪神 2012: bat_d_bb_pa=-0.002, bat_d_iso=-0.017, rf_adv=-0.347, rank=5, bat_d_avg=-0.009, ra_adv=0.150, run_balance=-0.197 / surprise=-0.347
  - 阪神 2012 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 広島 2019: bat_d_bb_pa=-0.001, bat_d_iso=-0.002, rf_adv=-0.085, rank=4, bat_d_avg=0.002, ra_adv=0.039, run_balance=-0.046 / surprise=-0.085
  - 広島 2019 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7

## P131: 中日以外で、得点に不足があり失点だけに優位がある B クラスは、不足が優位の 1.5〜2.5 倍（取り分 0.6〜0.714）に入る

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 8 件: c-2012, l-2025, t-2018, f-2021, e-2018 ほか
- もし: `（すべての単位）` ならば: `short_share >= 0.6 かつ short_share <= 0.7143`
- 識別子: `[where:ra_adv>0, where:rf_adv<0, where:team!="d", where:upper_half==false] * => short_share<=0.7143 & short_share>=0.6`（指紋 `729eb6aab5a6cc1f`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}, {'col': 'ra_adv', 'op': '>', 'value': 0}, {'col': 'rf_adv', 'op': '<', 'value': 0}, {'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 16
- 見直す条件（反証）: 半分以下しか、この範囲に入らない
- 注記: R31 で順位の範囲で見た分布（中央値 2.18、最頻の区間 2.25）を見た後の命題。同じデータでは確かめにならない。2026年で確かめる（[confirm]）。比 r と取り分 s は s = r ÷ (1 + r)
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 9 回、元の命題に異議あり 9 回（どれかの形に異議あり 9 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 8 | 0.50 [0.28, 0.72] | +0.00σ（0.598） | 0.50 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 0 | 0.00 [0.00, 0.32] | -2.83σ（0.004） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 8 件（対偶の判例も同じ）

- 広島 2012: short_share=0.928, rf_adv=-0.214, ra_adv=0.017, run_balance=-0.197, rank=4 / surprise=0.928
  - 広島 2012 は「（すべての単位）」を満たすのに「short_share >= 0.6 かつ short_share <= 0.7143」を満たさない。なぜか？ → H2
- 西武 2025: short_share=0.861, rf_adv=-0.613, ra_adv=0.099, run_balance=-0.513, rank=5 / surprise=0.861
  - 西武 2025 は「（すべての単位）」を満たすのに「short_share >= 0.6 かつ short_share <= 0.7143」を満たさない。なぜか？ → H2
- 阪神 2018: short_share=0.860, rf_adv=-0.404, ra_adv=0.066, run_balance=-0.338, rank=6 / surprise=0.860
  - 阪神 2018 は「（すべての単位）」を満たすのに「short_share >= 0.6 かつ short_share <= 0.7143」を満たさない。なぜか？ → H2
- 日本ハム 2021: short_share=0.852, rf_adv=-0.674, ra_adv=0.117, run_balance=-0.557, rank=5 / surprise=0.852
  - 日本ハム 2021 は「（すべての単位）」を満たすのに「short_share >= 0.6 かつ short_share <= 0.7143」を満たさない。なぜか？ → H2
- 楽天 2018: short_share=0.849, rf_adv=-0.752, ra_adv=0.134, run_balance=-0.618, rank=6 / surprise=0.849
  - 楽天 2018 は「（すべての単位）」を満たすのに「short_share >= 0.6 かつ short_share <= 0.7143」を満たさない。なぜか？ → H2
- オリックス 2015: short_share=0.803, rf_adv=-0.456, ra_adv=0.112, run_balance=-0.344, rank=5 / surprise=0.803
  - オリックス 2015 は「（すべての単位）」を満たすのに「short_share >= 0.6 かつ short_share <= 0.7143」を満たさない。なぜか？ → H2
- 広島 2024: short_share=0.529, rf_adv=-0.382, ra_adv=0.340, run_balance=-0.042, rank=4 / surprise=0.529
  - 広島 2024 は「（すべての単位）」を満たすのに「short_share >= 0.6 かつ short_share <= 0.7143」を満たさない。なぜか？ → H2
- 巨人 2017: short_share=0.324, rf_adv=-0.283, ra_adv=0.590, run_balance=0.308, rank=4 / surprise=0.324
  - 巨人 2017 は「（すべての単位）」を満たすのに「short_share >= 0.6 かつ short_share <= 0.7143」を満たさない。なぜか？ → H2

## P132: B クラスで、得点の不足が1試合 0.6点を超えるなら、四死球も長打も他球団より少ない（必要の向き）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: s-2017, m-2018
- もし: `rf_adv < -0.6` ならば: `bat_d_bb_pa < 0 かつ bat_d_iso < 0`
- 識別子: `[where:upper_half==false] rf_adv<-0.6 => bat_d_bb_pa<0 & bat_d_iso<0`（指紋 `352c653735998cc9`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 78
- 見直す条件（反証）: きっかけの5単位を除いて、不足が 0.6 を超える B の4分の1を超えて、四死球か長打の少なくとも一方が他球団以上
- 注記: R32 の P130 の逆（5中5）を、失点だけ優位の範囲から B クラス全体に広げた。中日を含む。きっかけ以外で読む
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 15 | 0.88 [0.66, 0.97] | +1.26σ（0.164） | 0.49 | 1.81 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 40 | 38 | 0.95 [0.83, 0.99] | +2.92σ（0.001） | 0.78 | 1.21 | 0.000 | 0 | 支持 | 1 |
| 逆 | 38 | 15 | 0.39 [0.26, 0.55] | -5.06σ（0.000） | 0.22 | 1.81 | 0.000 | 0 | 修正 | 2 |
| 裏 | 61 | 38 | 0.62 [0.50, 0.73] | -2.29σ（0.019） | 0.51 | 1.21 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- ヤクルト 2017: rf_adv=-0.811, bat_d_bb_pa=0.004, bat_d_iso=-0.028, rank=6, bat_d_avg=-0.020, rank_ra=6, ra_adv=-0.660 / surprise=-0.811
  - ヤクルト 2017 は「rf_adv < -0.6」を満たすのに「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たさない。なぜか？ → H6, H7
- ロッテ 2018: rf_adv=-0.635, bat_d_bb_pa=0.010, bat_d_iso=-0.042, rank=5, bat_d_avg=-0.008, rank_ra=5, ra_adv=-0.243 / surprise=-0.635
  - ロッテ 2018 は「rf_adv < -0.6」を満たすのに「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たさない。なぜか？ → H6, H7

**異議あり（主張が強すぎる）** 逆に判例 23 件（裏の判例も同じ）

- オリックス 2013: rf_adv=-0.554, bat_d_bb_pa=-0.005, bat_d_iso=-0.005, rank=5, bat_d_avg=-0.007, rank_ra=1, ra_adv=0.283 / surprise=-0.554
  - オリックス 2013 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 中日 2016 **(focus)**: rf_adv=-0.524, bat_d_bb_pa=-0.005, bat_d_iso=-0.022, rank=6, bat_d_avg=-0.009, rank_ra=4, ra_adv=0.004 / surprise=-0.524
  - 中日 2016 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 西武 2023: rf_adv=-0.491, bat_d_bb_pa=-0.009, bat_d_iso=-0.008, rank=5, bat_d_avg=-0.009, rank_ra=2, ra_adv=0.260 / surprise=-0.491
  - 西武 2023 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 日本ハム 2019: rf_adv=-0.473, bat_d_bb_pa=-0.000, bat_d_iso=-0.031, rank=5, bat_d_avg=-0.000, rank_ra=3, ra_adv=0.217 / surprise=-0.473
  - 日本ハム 2019 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 中日 2025 **(focus)**: rf_adv=-0.473, bat_d_bb_pa=-0.008, bat_d_iso=-0.005, rank=4, bat_d_avg=-0.012, rank_ra=4, ra_adv=0.021 / surprise=-0.473
  - 中日 2025 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 広島 2024: rf_adv=-0.382, bat_d_bb_pa=-0.019, bat_d_iso=-0.023, rank=4, bat_d_avg=-0.008, rank_ra=2, ra_adv=0.340 / surprise=-0.382
  - 広島 2024 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 日本ハム 2013: rf_adv=-0.379, bat_d_bb_pa=-0.001, bat_d_iso=-0.004, rank=6, bat_d_avg=-0.007, rank_ra=6, ra_adv=-0.342 / surprise=-0.379
  - 日本ハム 2013 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- ロッテ 2025: rf_adv=-0.352, bat_d_bb_pa=-0.007, bat_d_iso=-0.012, rank=6, bat_d_avg=-0.007, rank_ra=6, ra_adv=-0.639 / surprise=-0.352
  - ロッテ 2025 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 阪神 2012: rf_adv=-0.347, bat_d_bb_pa=-0.002, bat_d_iso=-0.017, rank=5, bat_d_avg=-0.009, rank_ra=3, ra_adv=0.150 / surprise=-0.347
  - 阪神 2012 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 楽天 2016: rf_adv=-0.331, bat_d_bb_pa=-0.007, bat_d_iso=-0.005, rank=5, bat_d_avg=-0.003, rank_ra=6, ra_adv=-0.684 / surprise=-0.331
  - 楽天 2016 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- ほか 13 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ e-2018, b-2018, l-2025, b-2024, f-2021 を除く）: n=12 成立=10 成立率=0.83 [0.55, 0.95] → **判断保留** / 判例: s-2017, m-2018

## P133: 得点の不足が1試合 0.6点を超えるなら、四死球も長打も他球団より少ない（A クラスも含む全体）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: s-2017, m-2018
- もし: `rf_adv < -0.6` ならば: `bat_d_bb_pa < 0 かつ bat_d_iso < 0`
- 識別子: `[all] rf_adv<-0.6 => bat_d_bb_pa<0 & bat_d_iso<0`（指紋 `22bc73f4411fa77a`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: きっかけの5単位を除いて、不足が 0.6 を超える単位の4分の1を超えて、どちらか一方が他球団以上
- 注記: B クラスに限るか（P132）、不足の大きさそのものの形か（P133）を比べる
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 15 | 0.88 [0.66, 0.97] | +1.26σ（0.164） | 0.29 | 3.06 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 111 | 109 | 0.98 [0.94, 1.00] | +5.64σ（0.000） | 0.89 | 1.10 | 0.000 | 0 | 支持 | 1 |
| 逆 | 45 | 15 | 0.33 [0.21, 0.48] | -6.45σ（0.000） | 0.11 | 3.06 | 0.000 | 0 | 修正 | 2 |
| 裏 | 139 | 109 | 0.78 [0.71, 0.84] | +0.93σ（0.204） | 0.71 | 1.10 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- ヤクルト 2017: rf_adv=-0.811, bat_d_bb_pa=0.004, bat_d_iso=-0.028, rank=6, bat_d_avg=-0.020, upper_half=False / surprise=-0.811
  - ヤクルト 2017 は「rf_adv < -0.6」を満たすのに「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たさない。なぜか？ → H6, H7
- ロッテ 2018: rf_adv=-0.635, bat_d_bb_pa=0.010, bat_d_iso=-0.042, rank=5, bat_d_avg=-0.008, upper_half=False / surprise=-0.635
  - ロッテ 2018 は「rf_adv < -0.6」を満たすのに「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たさない。なぜか？ → H6, H7

**異議あり（主張が強すぎる）** 逆に判例 30 件（裏の判例も同じ）

- オリックス 2013: rf_adv=-0.554, bat_d_bb_pa=-0.005, bat_d_iso=-0.005, rank=5, bat_d_avg=-0.007, upper_half=False / surprise=-0.554
  - オリックス 2013 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 阪神 2019: rf_adv=-0.530, bat_d_bb_pa=-0.005, bat_d_iso=-0.034, rank=3, bat_d_avg=-0.002, upper_half=True / surprise=-0.530
  - 阪神 2019 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 中日 2016 **(focus)**: rf_adv=-0.524, bat_d_bb_pa=-0.005, bat_d_iso=-0.022, rank=6, bat_d_avg=-0.009, upper_half=False / surprise=-0.524
  - 中日 2016 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 西武 2023: rf_adv=-0.491, bat_d_bb_pa=-0.009, bat_d_iso=-0.008, rank=5, bat_d_avg=-0.009, upper_half=False / surprise=-0.491
  - 西武 2023 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 日本ハム 2019: rf_adv=-0.473, bat_d_bb_pa=-0.000, bat_d_iso=-0.031, rank=5, bat_d_avg=-0.000, upper_half=False / surprise=-0.473
  - 日本ハム 2019 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 中日 2025 **(focus)**: rf_adv=-0.473, bat_d_bb_pa=-0.008, bat_d_iso=-0.005, rank=4, bat_d_avg=-0.012, upper_half=False / surprise=-0.473
  - 中日 2025 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 広島 2024: rf_adv=-0.382, bat_d_bb_pa=-0.019, bat_d_iso=-0.023, rank=4, bat_d_avg=-0.008, upper_half=False / surprise=-0.382
  - 広島 2024 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 日本ハム 2013: rf_adv=-0.379, bat_d_bb_pa=-0.001, bat_d_iso=-0.004, rank=6, bat_d_avg=-0.007, upper_half=False / surprise=-0.379
  - 日本ハム 2013 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- ロッテ 2025: rf_adv=-0.352, bat_d_bb_pa=-0.007, bat_d_iso=-0.012, rank=6, bat_d_avg=-0.007, upper_half=False / surprise=-0.352
  - ロッテ 2025 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- 阪神 2012: rf_adv=-0.347, bat_d_bb_pa=-0.002, bat_d_iso=-0.017, rank=5, bat_d_avg=-0.009, upper_half=False / surprise=-0.347
  - 阪神 2012 は「bat_d_bb_pa < 0 かつ bat_d_iso < 0」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H6, H7
- ほか 20 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ e-2018, b-2018, l-2025, b-2024, f-2021 を除く）: n=12 成立=10 成立率=0.83 [0.55, 0.95] → **判断保留** / 判例: s-2017, m-2018

## P134: 0 の近く（\|z\| < 1）を除いて、得点にも失点にも、はっきりした優位がない（どちらも z ≤ −1）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: n=3（min_n=10）、成立率の区間 0.44〜1.00
- もし: `rf_zone == -1 かつ ra_zone == -1` ならば: `upper_half == False`
- 識別子: `[where:ra_zone!=0, where:rf_zone!=0] ra_zone==-1 & rf_zone==-1 => upper_half==false`（指紋 `668f7cea6ac56920`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rf_zone', 'op': '!=', 'value': 0}, {'col': 'ra_zone', 'op': '!=', 'value': 0}]} / 単位数: 15
- 親: P126（変更: 優位の符号ではなく、0 から1標準偏差以上離れた単位だけで読む（R32 で 0 の近くの単位が出入りした））
- 見直す条件（反証）: はっきりした優位がない単位の4分の1を超えて A クラス
- 注記: 対偶（A なら、どちらかにはっきりした優位がある）を P126 の対偶 0.91 と並べる
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 3 | 3 | 1.00 [0.44, 1.00] | +1.00σ（0.422） | 0.40 | 2.50 | 0.044 | 0 | 判断保留 | 4 |
| 対偶 | 9 | 9 | 1.00 [0.70, 1.00] | +1.73σ（0.075） | 0.80 | 1.25 | 0.044 | 0 | 判断保留 | 4 |
| 逆 | 6 | 3 | 0.50 [0.19, 0.81] | -1.41σ（0.169） | 0.20 | 2.50 | 0.044 | 0 | 判断保留 | 4 |
| 裏 | 12 | 9 | 0.75 [0.47, 0.91] | +0.00σ（0.649） | 0.60 | 1.25 | 0.044 | 0 | 判断保留 | 4 |

**待った！判断保留** 逆に判例 3 件（裏の判例も同じ）

- 中日 2021 **(focus)**: rf_zone=-1, ra_zone=1, upper_half=False, rank=5, rf_adv=-1.13, ra_adv=0.564, run_balance=-0.568 / surprise=-73
  - 中日 2021 は「upper_half == False」を満たすのに「rf_zone == -1 かつ ra_zone == -1」を満たさない。なぜか？ → H2
- DeNA 2013: rf_zone=1, ra_zone=-1, upper_half=False, rank=5, rf_adv=0.503, ra_adv=-0.832, run_balance=-0.329 / surprise=-56
  - DeNA 2013 は「upper_half == False」を満たすのに「rf_zone == -1 かつ ra_zone == -1」を満たさない。なぜか？ → H2
- ヤクルト 2014: rf_zone=1, ra_zone=-1, upper_half=False, rank=6, rf_adv=0.490, ra_adv=-0.826, run_balance=-0.336 / surprise=-50
  - ヤクルト 2014 は「upper_half == False」を満たすのに「rf_zone == -1 かつ ra_zone == -1」を満たさない。なぜか？ → H2

## P135: 失点にだけはっきりした優位がある（失点 z ≥ 1、得点 z ≤ −1）チームは、得失点差がプラスなら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[where:ra_zone==1, where:rf_zone==-1] rd>0 => upper_half==true`（指紋 `17cdfc38b2b966c0`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'ra_zone', 'op': '==', 'value': 1}, {'col': 'rf_zone', 'op': '==', 'value': -1}]} / 単位数: 1
- 親: P128（変更: 失点だけ優位の範囲を、符号ではなく1標準偏差以上の離れで決める）
- 見直す条件（反証）: きっかけの6単位を除いて、得失点差プラスの単位の4分の1を超えて B クラス
- 注記: 範囲の単位は少なくなる見込み。判断保留は正しい結果としてありうる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 1 | 1.00 [0.21, 1.00] | +0.58σ（0.750） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |
| 裏 | 1 | 1 | 1.00 [0.21, 1.00] | +0.58σ（0.750） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |

**きっかけ以外での判定**（作り直しのきっかけ t-2013, t-2021, t-2022, h-2012, l-2022, d-2019 を除く）: n=0 成立=0 成立率=- [0.00, 1.00] → **判断保留** / 判例なし

## P136: 四死球が他球団以上なら、得点の不足は1試合 0.6点以下

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 2 件: s-2017, m-2018
- もし: `bat_d_bb_pa >= 0` ならば: `rf_adv >= -0.6`
- 識別子: `[all] bat_d_bb_pa>=0 => rf_adv>=-0.6`（指紋 `893ef4f49bf3395c`）
- 兄弟（範囲と結論が同じ、条件が違う）: P137
- 強さ: ほとんど（almost_always, 基準 0.90）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 四死球が他球団以上の単位の1割を超えて、不足が 0.6 を超える
- 注記: P133 の対偶を経路ごとに分けた（四死球の経路）。判例は R33 で見た2単位（長打だけ少ない）になると分かっている。P137 と率・単位の数を比べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 77 | 75 | 0.97 [0.91, 0.99] | +2.17σ（0.014） | 0.89 | 1.09 | 0.001 | 0 | 支持 | 1 |
| 対偶 | 17 | 15 | 0.88 [0.66, 0.97] | -0.24σ（0.518） | 0.51 | 1.74 | 0.001 | 0 | 判断保留 | 4 |
| 逆 | 139 | 75 | 0.54 [0.46, 0.62] | -14.16σ（0.000） | 0.49 | 1.09 | 0.001 | 0 | 修正 | 2 |
| 裏 | 79 | 15 | 0.19 [0.12, 0.29] | -21.04σ（0.000） | 0.11 | 1.74 | 0.001 | 0 | 修正 | 2 |

**異議あり（例外あり）** 元の命題に判例 2 件（対偶の判例も同じ）

- ヤクルト 2017: bat_d_bb_pa=0.004, rf_adv=-0.811, bat_d_iso=-0.028, rank=6, upper_half=False / surprise=-0.811
  - ヤクルト 2017 は「bat_d_bb_pa >= 0」を満たすのに「rf_adv >= -0.6」を満たさない。なぜか？ → H6, H7
- ロッテ 2018: bat_d_bb_pa=0.010, rf_adv=-0.635, bat_d_iso=-0.042, rank=5, upper_half=False / surprise=-0.635
  - ロッテ 2018 は「bat_d_bb_pa >= 0」を満たすのに「rf_adv >= -0.6」を満たさない。なぜか？ → H6, H7

**異議あり（主張が強すぎる）** 逆に判例 64 件（裏の判例も同じ）

- ソフトバンク 2013: bat_d_bb_pa=-0.007, rf_adv=0.671, bat_d_iso=0.025, rank=4, upper_half=False / surprise=0.671
  - ソフトバンク 2013 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- ソフトバンク 2018: bat_d_bb_pa=-0.015, rf_adv=0.632, bat_d_iso=0.050, rank=2, upper_half=True / surprise=0.632
  - ソフトバンク 2018 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- オリックス 2013: bat_d_bb_pa=-0.005, rf_adv=-0.554, bat_d_iso=-0.005, rank=5, upper_half=False / surprise=-0.554
  - オリックス 2013 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- 阪神 2019: bat_d_bb_pa=-0.005, rf_adv=-0.530, bat_d_iso=-0.034, rank=3, upper_half=True / surprise=-0.530
  - 阪神 2019 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- 中日 2016 **(focus)**: bat_d_bb_pa=-0.005, rf_adv=-0.524, bat_d_iso=-0.022, rank=6, upper_half=False / surprise=-0.524
  - 中日 2016 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- DeNA 2024: bat_d_bb_pa=-0.002, rf_adv=0.516, bat_d_iso=0.027, rank=3, upper_half=True / surprise=0.516
  - DeNA 2024 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- DeNA 2013: bat_d_bb_pa=-0.008, rf_adv=0.503, bat_d_iso=0.009, rank=5, upper_half=False / surprise=0.503
  - DeNA 2013 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- 西武 2023: bat_d_bb_pa=-0.009, rf_adv=-0.491, bat_d_iso=-0.008, rank=5, upper_half=False / surprise=-0.491
  - 西武 2023 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- ヤクルト 2014: bat_d_bb_pa=-0.005, rf_adv=0.490, bat_d_iso=0.007, rank=6, upper_half=False / surprise=0.490
  - ヤクルト 2014 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- 日本ハム 2019: bat_d_bb_pa=-0.000, rf_adv=-0.473, bat_d_iso=-0.031, rank=5, upper_half=False / surprise=-0.473
  - 日本ハム 2019 は「rf_adv >= -0.6」を満たすのに「bat_d_bb_pa >= 0」を満たさない。なぜか？ → H6, H7
- ほか 54 件（propositions.jsonl を参照）

## P137: 長打（ISO）が他球団以上なら、得点の不足は1試合 0.6点以下

- **判定: exit 4 待った！判断保留** — 対偶: n=17（min_n=10）、成立率の区間 0.82〜1.00
- もし: `bat_d_iso >= 0` ならば: `rf_adv >= -0.6`
- 識別子: `[all] bat_d_iso>=0 => rf_adv>=-0.6`（指紋 `e3974fbb9c6c2f5c`）
- 兄弟（範囲と結論が同じ、条件が違う）: P136
- 強さ: ほとんど（almost_always, 基準 0.90）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 長打が他球団以上の単位の1割を超えて、不足が 0.6 を超える
- 注記: P133 の対偶を経路ごとに分けた（長打の経路）。判例が 0 になると分かっている
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 75 | 75 | 1.00 [0.95, 1.00] | +2.89σ（0.000） | 0.89 | 1.12 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 17 | 17 | 1.00 [0.82, 1.00] | +1.37σ（0.167） | 0.52 | 1.93 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 139 | 75 | 0.54 [0.46, 0.62] | -14.16σ（0.000） | 0.48 | 1.12 | 0.000 | 0 | 修正 | 2 |
| 裏 | 81 | 17 | 0.21 [0.14, 0.31] | -20.70σ（0.000） | 0.11 | 1.93 | 0.000 | 0 | 修正 | 2 |

**異議あり（主張が強すぎる）** 逆に判例 64 件（裏の判例も同じ）

- オリックス 2013: bat_d_iso=-0.005, rf_adv=-0.554, bat_d_bb_pa=-0.005, rank=5, upper_half=False / surprise=-0.554
  - オリックス 2013 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- 日本ハム 2017: bat_d_iso=-0.025, rf_adv=-0.540, bat_d_bb_pa=0.003, rank=5, upper_half=False / surprise=-0.540
  - 日本ハム 2017 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- 阪神 2019: bat_d_iso=-0.034, rf_adv=-0.530, bat_d_bb_pa=-0.005, rank=3, upper_half=True / surprise=-0.530
  - 阪神 2019 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- 中日 2016 **(focus)**: bat_d_iso=-0.022, rf_adv=-0.524, bat_d_bb_pa=-0.005, rank=6, upper_half=False / surprise=-0.524
  - 中日 2016 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- 西武 2023: bat_d_iso=-0.008, rf_adv=-0.491, bat_d_bb_pa=-0.009, rank=5, upper_half=False / surprise=-0.491
  - 西武 2023 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- 阪神 2016: bat_d_iso=-0.023, rf_adv=-0.474, bat_d_bb_pa=0.001, rank=4, upper_half=False / surprise=-0.474
  - 阪神 2016 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- 日本ハム 2019: bat_d_iso=-0.031, rf_adv=-0.473, bat_d_bb_pa=-0.000, rank=5, upper_half=False / surprise=-0.473
  - 日本ハム 2019 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- 中日 2025 **(focus)**: bat_d_iso=-0.005, rf_adv=-0.473, bat_d_bb_pa=-0.008, rank=4, upper_half=False / surprise=-0.473
  - 中日 2025 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- オリックス 2015: bat_d_iso=-0.017, rf_adv=-0.456, bat_d_bb_pa=0.000, rank=5, upper_half=False / surprise=-0.456
  - オリックス 2015 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- 阪神 2023: bat_d_iso=-0.016, rf_adv=0.441, bat_d_bb_pa=0.023, rank=1, upper_half=True / surprise=0.441
  - 阪神 2023 は「rf_adv >= -0.6」を満たすのに「bat_d_iso >= 0」を満たさない。なぜか？ → H6, H7
- ほか 54 件（propositions.jsonl を参照）

## P138: 得点の不足が1試合 0.6点を超えるなら、必ず B クラス

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 61 件: h-2013, b-2013, f-2017, d-2016, db-2013 ほか
- もし: `rf_adv < -0.6` ならば: `upper_half == False`
- 識別子: `[all] rf_adv<-0.6 => upper_half==false`（指紋 `283ec921c3253ea2`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P115, P126, P147, P148, P149, P150, P151, P181
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 不足が 0.6 を超えて A クラスの単位が1つでも出る
- 注記: R33 で 17中17 を見た後の命題。同じデータでは確かめにならない。2026年で確かめる（[confirm]）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 17 | 1.00 [0.82, 1.00] | — | 0.50 | 2.00 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 78 | 78 | 1.00 [0.95, 1.00] | — | 0.89 | 1.12 | 0.000 | 0 | 支持 | 0 |
| 逆 | 78 | 17 | 0.22 [0.14, 0.32] | — | 0.11 | 2.00 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 139 | 78 | 0.56 [0.48, 0.64] | — | 0.50 | 1.12 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 61 件（裏の判例も同じ）

- ソフトバンク 2013: rf_adv=0.671, upper_half=False, rank=4, ra_adv=0.008, run_balance=0.679 / surprise=0.671
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- オリックス 2013: rf_adv=-0.554, upper_half=False, rank=5, ra_adv=0.283, run_balance=-0.271 / surprise=-0.554
  - オリックス 2013 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- 日本ハム 2017: rf_adv=-0.540, upper_half=False, rank=5, ra_adv=-0.229, run_balance=-0.769 / surprise=-0.540
  - 日本ハム 2017 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- 中日 2016 **(focus)**: rf_adv=-0.524, upper_half=False, rank=6, ra_adv=0.004, run_balance=-0.520 / surprise=-0.524
  - 中日 2016 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- DeNA 2013: rf_adv=0.503, upper_half=False, rank=5, ra_adv=-0.832, run_balance=-0.329 / surprise=0.503
  - DeNA 2013 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- 西武 2023: rf_adv=-0.491, upper_half=False, rank=5, ra_adv=0.260, run_balance=-0.231 / surprise=-0.491
  - 西武 2023 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- ヤクルト 2014: rf_adv=0.490, upper_half=False, rank=6, ra_adv=-0.826, run_balance=-0.336 / surprise=0.490
  - ヤクルト 2014 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- 西武 2015: rf_adv=0.484, upper_half=False, rank=4, ra_adv=-0.098, run_balance=0.386 / surprise=0.484
  - 西武 2015 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- 阪神 2016: rf_adv=-0.474, upper_half=False, rank=4, ra_adv=0.231, run_balance=-0.243 / surprise=-0.474
  - 阪神 2016 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- 日本ハム 2019: rf_adv=-0.473, upper_half=False, rank=5, ra_adv=0.217, run_balance=-0.256 / surprise=-0.473
  - 日本ハム 2019 は「upper_half == False」を満たすのに「rf_adv < -0.6」を満たさない。なぜか？ → H2
- ほか 51 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rf_adv=-0.647, upper_half=True, rank=3, ra_adv=0.047, run_balance=-0.600

## P139: 得点にも失点にも、誤差1つ分を超える優位がない（どちらも誤差1つ分以上の劣位）なら、B クラス（誤差の幅で 0 の近くを除く）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: t-2015
- もし: `rf_zone_se == -1 かつ ra_zone_se == -1` ならば: `upper_half == False`
- 識別子: `[where:ra_zone_se!=0, where:rf_zone_se!=0] ra_zone_se==-1 & rf_zone_se==-1 => upper_half==false`（指紋 `fdb9fc276e49b469`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rf_zone_se', 'op': '!=', 'value': 0}, {'col': 'ra_zone_se', 'op': '!=', 'value': 0}]} / 単位数: 53
- 親: P134（変更: 幅の物差しを、チームの間の散らばり（R33、広すぎた）から、その年の平均の誤差（試合ごとの点の散らばり）にする）
- 見直す条件（反証）: はっきりした優位がない単位の4分の1を超えて A クラス
- 注記: 対偶（A なら、どちらかに誤差を超える優位）を P126 の対偶 0.91 と並べる
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 12 | 0.92 [0.67, 0.99] | +1.44σ（0.127） | 0.49 | 1.88 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 27 | 26 | 0.96 [0.82, 0.99] | +2.56σ（0.004） | 0.75 | 1.28 | 0.000 | 0 | 支持 | 1 |
| 逆 | 26 | 12 | 0.46 [0.29, 0.65] | -3.40σ（0.002） | 0.25 | 1.88 | 0.000 | 0 | 修正 | 2 |
| 裏 | 40 | 26 | 0.65 [0.50, 0.78] | -1.46σ（0.103） | 0.51 | 1.28 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 阪神 2015: rf_zone_se=-1, ra_zone_se=-1, upper_half=True, rank=3, rf_adv=-0.315, ra_adv=-0.298, rf_adv_se=0.227, ra_adv_se=0.282 / surprise=-85
  - 阪神 2015 は「rf_zone_se == -1 かつ ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 14 件（裏の判例も同じ）

- ヤクルト 2016: rf_zone_se=1, ra_zone_se=-1, upper_half=False, rank=5, rf_adv=0.264, ra_adv=-1.01, rf_adv_se=0.258, ra_adv_se=0.281 / surprise=-100
  - ヤクルト 2016 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- ヤクルト 2019: rf_zone_se=1, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=0.460, ra_adv=-1.12, rf_adv_se=0.285, ra_adv_se=0.302 / surprise=-83
  - ヤクルト 2019 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- 中日 2021 **(focus)**: rf_zone_se=-1, ra_zone_se=1, upper_half=False, rank=5, rf_adv=-1.13, ra_adv=0.564, rf_adv_se=0.225, ra_adv_se=0.254 / surprise=-73
  - 中日 2021 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- DeNA 2013: rf_zone_se=1, ra_zone_se=-1, upper_half=False, rank=5, rf_adv=0.503, ra_adv=-0.832, rf_adv_se=0.296, ra_adv_se=0.304 / surprise=-56
  - DeNA 2013 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- ヤクルト 2014: rf_zone_se=1, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=0.490, ra_adv=-0.826, rf_adv_se=0.294, ra_adv_se=0.305 / surprise=-50
  - ヤクルト 2014 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- ヤクルト 2024: rf_zone_se=1, ra_zone_se=-1, upper_half=False, rank=5, rf_adv=0.382, ra_adv=-0.810, rf_adv_se=0.224, ra_adv_se=0.237 / surprise=-50
  - ヤクルト 2024 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- オリックス 2024: rf_zone_se=-1, ra_zone_se=1, upper_half=False, rank=5, rf_adv=-0.649, ra_adv=0.271, rf_adv_se=0.219, ra_adv_se=0.252 / surprise=-46
  - オリックス 2024 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- 巨人 2017: rf_zone_se=-1, ra_zone_se=1, upper_half=False, rank=4, rf_adv=-0.283, ra_adv=0.590, rf_adv_se=0.244, ra_adv_se=0.270 / surprise=32
  - 巨人 2017 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- 西武 2023: rf_zone_se=-1, ra_zone_se=1, upper_half=False, rank=5, rf_adv=-0.491, ra_adv=0.260, rf_adv_se=0.215, ra_adv_se=0.232 / surprise=-30
  - 西武 2023 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- オリックス 2018: rf_zone_se=-1, ra_zone_se=1, upper_half=False, rank=4, rf_adv=-0.601, ra_adv=0.285, rf_adv_se=0.256, ra_adv_se=0.268 / surprise=-27
  - オリックス 2018 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == -1」を満たさない。なぜか？ → H2
- ほか 4 件（propositions.jsonl を参照）

## P140: 失点にだけ誤差を超える優位がある（失点 +、得点 −、どちらも誤差1つ分以上）チームは、得失点差がプラスなら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: g-2017, d-2019
- もし: `rd > 0` ならば: `upper_half == True`
- 識別子: `[where:ra_zone_se==1, where:rf_zone_se==-1] rd>0 => upper_half==true`（指紋 `41af5caf89c31c1d`）
- 兄弟（範囲と結論が同じ、条件が違う）: P143
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'ra_zone_se', 'op': '==', 'value': 1}, {'col': 'rf_zone_se', 'op': '==', 'value': -1}]} / 単位数: 14
- 親: P135（変更: 幅の物差しを、その年の平均の誤差にする）
- 見直す条件（反証）: きっかけの6単位を除いて、得失点差プラスの単位の4分の1を超えて B クラス
- 注記: P128（符号、きっかけ以外 0.92）と並べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 7 | 5 | 0.71 [0.36, 0.92] | -0.22σ（0.555） | 0.43 | 1.67 | 0.051 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 6 | 0.75 [0.41, 0.93] | +0.00σ（0.679） | 0.50 | 1.50 | 0.051 | 0 | 判断保留 | 4 |
| 逆 | 6 | 5 | 0.83 [0.44, 0.97] | +0.47σ（0.534） | 0.50 | 1.67 | 0.051 | 0 | 判断保留 | 4 |
| 裏 | 7 | 6 | 0.86 [0.49, 0.97] | +0.65σ（0.445） | 0.57 | 1.50 | 0.051 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- 巨人 2017: rd=32, upper_half=False, rank=4, rf_adv=-0.283, ra_adv=0.590, wins_vs_pythag=-1.94 / surprise=32
  - 巨人 2017 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: rd=19, upper_half=False, rank=5, rf_adv=-0.320, ra_adv=0.517, wins_vs_pythag=-4.71 / surprise=19
  - 中日 2019 は「rd > 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 阪神 2019: rd=-28, upper_half=True, rank=3, rf_adv=-0.530, ra_adv=0.333, wins_vs_pythag=+3.68 / surprise=-28
  - 阪神 2019 は「upper_half == True」を満たすのに「rd > 0」を満たさない。なぜか？ → H2

**きっかけ以外での判定**（作り直しのきっかけ t-2013, t-2021, t-2022, h-2012, l-2022, d-2019 を除く）: n=3 成立=2 成立率=0.67 [0.21, 0.94] → **判断保留** / 判例: g-2017

## P141: 中日以外で、得点の不足が誤差を超え（得点 −1）、失点の優位が誤差の内側（失点 0）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: g-2016
- もし: `（すべての単位）` ならば: `upper_half == False`
- 識別子: `[where:ra_zone_se==0, where:rf_zone_se==-1, where:team!="d"] * => upper_half==false`（指紋 `5fa6667ba8deb458`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}, {'col': 'rf_zone_se', 'op': '==', 'value': -1}, {'col': 'ra_zone_se', 'op': '==', 'value': 0}]} / 単位数: 17
- 見直す条件（反証）: この範囲の単位の4分の1を超えて A クラス
- 注記: 中日の 2013〜2016・2022〜2025年はこの区分（R34）。中日の形が、得点ははっきり足りず失点は平均と区別できないチームに共通かを見る
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 16 | 0.94 [0.73, 0.99] | +1.82σ（0.050） | 0.94 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 巨人 2016: upper_half=True, rank=2, rf_adv=-0.365, ra_adv=0.256, rank_ra=2, rank_rf=4 / surprise=-0.109
  - 巨人 2016 は「（すべての単位）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: upper_half=True, rank=2, rf_adv=-0.328, ra_adv=0.148, rank_ra=2, rank_rf=5

## P142: 中日以外で、得点の不足が誤差を超え、失点の優位も誤差を超えている（得点 −1・失点 +1）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 5 件: t-2013, t-2019, h-2012, h-2019, l-2022
- もし: `（すべての単位）` ならば: `upper_half == False`
- 識別子: `[where:ra_zone_se==1, where:rf_zone_se==-1, where:team!="d"] * => upper_half==false`（指紋 `0a876ef32bd80a6b`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}, {'col': 'rf_zone_se', 'op': '==', 'value': -1}, {'col': 'ra_zone_se', 'op': '==', 'value': 1}]} / 単位数: 11
- 見直す条件（反証）: （P141 と率を比べるための命題）
- 注記: 中日の 2012・2019・2021年の区分。P140 の範囲から中日を除いたもの（P140 の得失点差プラスの単位は見ている）
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 6 | 0.55 [0.28, 0.79] | +0.30σ（0.500） | 0.55 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 5 | 0 | 0.00 [0.00, 0.43] | -2.24σ（0.031） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 5 件（対偶の判例も同じ）

- 阪神 2013: upper_half=True, rank=2, rf_adv=-0.322, ra_adv=0.818, rd=43 / surprise=0.496
  - 阪神 2013 は「（すべての単位）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2019: upper_half=True, rank=3, rf_adv=-0.530, ra_adv=0.333, rd=-28 / surprise=-0.197
  - 阪神 2019 は「（すべての単位）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ソフトバンク 2012: upper_half=True, rank=3, rf_adv=-0.276, ra_adv=0.440, rd=23 / surprise=0.164
  - ソフトバンク 2012 は「（すべての単位）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ソフトバンク 2019: upper_half=True, rank=2, rf_adv=-0.288, ra_adv=0.401, rd=18 / surprise=0.113
  - ソフトバンク 2019 は「（すべての単位）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2022: upper_half=True, rank=3, rf_adv=-0.310, ra_adv=0.393, rd=16 / surprise=0.083
  - 西武 2022 は「（すべての単位）」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

## P143: 得点の不足も失点の優位も誤差を超えている（得点 −1・失点 +1）チームは、上の相手（1・2位）との勝率が .47 以上なら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: n=6（min_n=10）、成立率の区間 0.61〜1.00
- もし: `vs_top_wpct >= 0.47` ならば: `upper_half == True`
- 識別子: `[where:ra_zone_se==1, where:rf_zone_se==-1] vs_top_wpct>=0.47 => upper_half==true`（指紋 `2f165b794cb74a39`）
- 兄弟（範囲と結論が同じ、条件が違う）: P140
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rf_zone_se', 'op': '==', 'value': -1}, {'col': 'ra_zone_se', 'op': '==', 'value': 1}]} / 単位数: 14
- 見直す条件（反証）: 2026年以降、この形で上の相手に .47 以上なのに B、または .47 未満なのに A の単位が続く
- 注記: R36 で、同じ形の A 5単位（.48〜.57）と B 6単位（.34〜.46）を分けた唯一の指標。境は見た後。上の相手は最終順位で決めるので、A かどうかと算術でつながる面がある
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 6 | 6 | 1.00 [0.61, 1.00] | +1.41σ（0.178） | 0.43 | 2.33 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 8 | 8 | 1.00 [0.68, 1.00] | +1.63σ（0.100） | 0.57 | 1.75 | 0.000 | 0 | 判断保留 | 4 |
| 逆 | 6 | 6 | 1.00 [0.61, 1.00] | +1.41σ（0.178） | 0.43 | 2.33 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 8 | 8 | 1.00 [0.68, 1.00] | +1.63σ（0.100） | 0.57 | 1.75 | 0.000 | 0 | 判断保留 | 4 |

## P144: 得点の不足が誤差を超えている（得点 −1）チームは、上の相手（1・2位）との勝率が .47 以上なら A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: n=7（min_n=10）、成立率の区間 0.65〜1.00
- もし: `vs_top_wpct >= 0.47` ならば: `upper_half == True`
- 識別子: `[where:rf_zone_se==-1] vs_top_wpct>=0.47 => upper_half==true`（指紋 `9ceb281ff95c3791`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rf_zone_se', 'op': '==', 'value': -1}]} / 単位数: 52
- 親: P143（変更: 範囲を、失点 +1 の形だけから、得点 −1 の形すべて（失点 −1・0・+1）に広げた。R37 で阪神 2015・巨人 2016 も同じ向きに外れていた）
- 見直す条件（反証）: 2026年以降、得点がはっきり足りず上の相手に .47 以上なのに B の単位が出る
- 注記: 上の相手は最終順位で決める（docs/propositions.md の Groups Defined By The Final Outcome）。A かどうかと算術でつながる面がある。境は見た後
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 7 | 7 | 1.00 [0.65, 1.00] | +1.53σ（0.133） | 0.15 | 6.50 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 44 | 44 | 1.00 [0.92, 1.00] | +3.83σ（0.000） | 0.87 | 1.16 | 0.000 | 0 | 支持 | 0 |
| 逆 | 8 | 7 | 0.88 [0.53, 0.98] | +0.82σ（0.367） | 0.13 | 6.50 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 45 | 44 | 0.98 [0.88, 1.00] | +3.53σ（0.000） | 0.85 | 1.16 | 0.000 | 0 | 支持 | 1 |

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 阪神 2015: vs_top_wpct=0.440, upper_half=True, rank=3, ra_zone_se=-1, rd=-85, wins_vs_pythag=+10.25 / surprise=0.440
  - 阪神 2015 は「upper_half == True」を満たすのに「vs_top_wpct >= 0.47」を満たさない。なぜか？ → H3

## P145: 得失点差がプラスでも、得点・失点の組み合わせ方が基準より1標準偏差を超えて不利なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: t-2022, g-2018, t-2025, h-2022
- もし: `alloc_z_strat < -1` ならば: `upper_half == False`
- 識別子: `[where:rd>0] alloc_z_strat<-1 => upper_half==false`（指紋 `b77eb16d54b35f44`）
- 兄弟（範囲と結論が同じ、条件が違う）: P146
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rd', 'op': '>', 'value': 0}]} / 単位数: 73
- 見直す条件（反証）: 得失点差プラスで組み合わせ方 < −1 の単位の4分の1を超えて A クラス
- 注記: R38 で得失点差プラスの B の 10/12 が A の25%より下だった指標。境は R11 と同じ −1。組み合わせ方は勝ち数と一部算術でつながる（R1）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 8 | 0.67 [0.39, 0.86] | -0.67σ（0.351） | 0.16 | 4.06 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 61 | 57 | 0.93 [0.84, 0.97] | +3.33σ（0.000） | 0.84 | 1.12 | 0.000 | 0 | 支持 | 1 |
| 逆 | 12 | 8 | 0.67 [0.39, 0.86] | -0.67σ（0.351） | 0.16 | 4.06 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 61 | 57 | 0.93 [0.84, 0.97] | +3.33σ（0.000） | 0.84 | 1.12 | 0.000 | 0 | 支持 | 1 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- 阪神 2022: alloc_z_strat=-2.14, upper_half=True, rank=3, rd=61, wins_vs_pythag=-9.93, one_run_net=-5 / surprise=-2.14
  - 阪神 2022 は「alloc_z_strat < -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H3
- 巨人 2018: alloc_z_strat=-1.75, upper_half=True, rank=3, rd=50, wins_vs_pythag=-7.25, one_run_net=-12 / surprise=-1.75
  - 巨人 2018 は「alloc_z_strat < -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H3
- 阪神 2025: alloc_z_strat=-1.53, upper_half=True, rank=1, rd=144, wins_vs_pythag=-5.62, one_run_net=-3 / surprise=-1.53
  - 阪神 2025 は「alloc_z_strat < -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H3
- ソフトバンク 2022: alloc_z_strat=-1.10, upper_half=True, rank=1, rd=84, wins_vs_pythag=-5.01, one_run_net=0 / surprise=-1.10
  - ソフトバンク 2022 は「alloc_z_strat < -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H3

**待った！判断保留** 逆に判例 4 件（裏の判例も同じ）

- 巨人 2023: alloc_z_strat=-0.914, upper_half=False, rank=4, rd=16, wins_vs_pythag=-1.50, one_run_net=0 / surprise=-0.914
  - 巨人 2023 は「upper_half == False」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H3
- 広島 2022: alloc_z_strat=-0.293, upper_half=False, rank=5, rd=8, wins_vs_pythag=-4.93, one_run_net=-7 / surprise=-0.293
  - 広島 2022 は「upper_half == False」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H3
- 楽天 2022: alloc_z_strat=0.284, upper_half=False, rank=4, rd=11, wins_vs_pythag=-2.34, one_run_net=8 / surprise=0.284
  - 楽天 2022 は「upper_half == False」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H3
- 楽天 2012: alloc_z_strat=0.135, upper_half=False, rank=4, rd=24, wins_vs_pythag=-3.07, one_run_net=5 / surprise=0.135
  - 楽天 2012 は「upper_half == False」を満たすのに「alloc_z_strat < -1」を満たさない。なぜか？ → H3

## P146: 得失点差がプラスでも、下の相手（4〜6位）に勝ち越せない（.500 未満）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: e-2019
- もし: `vs_lower_wpct < 0.5` ならば: `upper_half == False`
- 識別子: `[where:rd>0] vs_lower_wpct<0.5 => upper_half==false`（指紋 `61a3d07fdf417639`）
- 兄弟（範囲と結論が同じ、条件が違う）: P145
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'rd', 'op': '>', 'value': 0}]} / 単位数: 73
- 見直す条件（反証）: 得失点差プラスで下の相手に .500 未満の単位の4分の1を超えて A クラス
- 注記: R38 で得失点差プラスの B の 8/12 が A の25%（.54）より下だった指標。境は五分。下の相手は最終順位で決める（docs/propositions.md の前提）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 7 | 6 | 0.86 [0.49, 0.97] | +0.65σ（0.445） | 0.16 | 5.21 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 61 | 60 | 0.98 [0.91, 1.00] | +4.21σ（0.000） | 0.90 | 1.09 | 0.000 | 0 | 支持 | 1 |
| 逆 | 12 | 6 | 0.50 [0.25, 0.75] | -2.00σ（0.054） | 0.10 | 5.21 | 0.000 | 0 | 修正 | 2 |
| 裏 | 66 | 60 | 0.91 [0.82, 0.96] | +2.98σ（0.001） | 0.84 | 1.09 | 0.000 | 0 | 支持 | 1 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 楽天 2019: vs_lower_wpct=0.493, upper_half=True, rank=3, rd=36, vs_top_wpct=0.520, alloc_z_strat=-0.950 / surprise=0.493
  - 楽天 2019 は「vs_lower_wpct < 0.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H3

**異議あり（主張が強すぎる）** 逆に判例 6 件（裏の判例も同じ）

- 西武 2015: vs_lower_wpct=0.660, upper_half=False, rank=4, rd=58, vs_top_wpct=0.312, alloc_z_strat=-1.04 / surprise=0.660
  - 西武 2015 は「upper_half == False」を満たすのに「vs_lower_wpct < 0.5」を満たさない。なぜか？ → H3
- 巨人 2023: vs_lower_wpct=0.653, upper_half=False, rank=4, rd=16, vs_top_wpct=0.286, alloc_z_strat=-0.914 / surprise=0.653
  - 巨人 2023 は「upper_half == False」を満たすのに「vs_lower_wpct < 0.5」を満たさない。なぜか？ → H3
- 巨人 2017: vs_lower_wpct=0.620, upper_half=False, rank=4, rd=32, vs_top_wpct=0.417, alloc_z_strat=-1.17 / surprise=0.620
  - 巨人 2017 は「upper_half == False」を満たすのに「vs_lower_wpct < 0.5」を満たさない。なぜか？ → H3
- 楽天 2022: vs_lower_wpct=0.571, upper_half=False, rank=4, rd=11, vs_top_wpct=0.469, alloc_z_strat=0.284 / surprise=0.571
  - 楽天 2022 は「upper_half == False」を満たすのに「vs_lower_wpct < 0.5」を満たさない。なぜか？ → H3
- ソフトバンク 2021: vs_lower_wpct=0.537, upper_half=False, rank=4, rd=71, vs_top_wpct=0.500, alloc_z_strat=-2.48 / surprise=0.537
  - ソフトバンク 2021 は「upper_half == False」を満たすのに「vs_lower_wpct < 0.5」を満たさない。なぜか？ → H3
- 楽天 2012: vs_lower_wpct=0.500, upper_half=False, rank=4, rd=24, vs_top_wpct=0.500, alloc_z_strat=0.135 / surprise=0.500
  - 楽天 2012 は「upper_half == False」を満たすのに「vs_lower_wpct < 0.5」を満たさない。なぜか？ → H3

## P147: 得点の不足が誤差を超えている（得点 −1）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 8 件: t-2019, g-2016, t-2015, l-2022, h-2012 ほか
- もし: `rf_zone_se == -1` ならば: `upper_half == False`
- 識別子: `[all] rf_zone_se==-1 => upper_half==false`（指紋 `87e483d8d2733c8c`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P115, P126, P138, P148, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 得点 −1 の単位の4分の1を超えて A クラス
- 注記: 元の命題の率は R35〜R37 からほぼ分かっている。読みたいのは逆（B なら得点ははっきり足りない）で、P148 の逆と比べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 52 | 44 | 0.85 [0.72, 0.92] | +1.60σ（0.070） | 0.50 | 1.69 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 70 | 0.90 [0.81, 0.95] | +3.01σ（0.001） | 0.67 | 1.35 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 44 | 0.56 [0.45, 0.67] | -3.79σ（0.000） | 0.33 | 1.69 | 0.000 | 0 | 修正 | 2 |
| 裏 | 104 | 70 | 0.67 [0.58, 0.76] | -1.81σ（0.048） | 0.50 | 1.35 | 0.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 8 件（対偶の判例も同じ）

- 阪神 2019: rf_zone_se=-1, upper_half=True, rank=3, adv_shape_se=-1/+1, run_balance_t=-0.520 / surprise=-2.05
  - 阪神 2019 は「rf_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 巨人 2016: rf_zone_se=-1, upper_half=True, rank=2, adv_shape_se=-1/0, run_balance_t=-0.308 / surprise=-1.54
  - 巨人 2016 は「rf_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2015: rf_zone_se=-1, upper_half=True, rank=3, adv_shape_se=-1/-1, run_balance_t=-1.69 / surprise=-1.39
  - 阪神 2015 は「rf_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2022: rf_zone_se=-1, upper_half=True, rank=3, adv_shape_se=-1/+1, run_balance_t=0.263 / surprise=-1.37
  - 西武 2022 は「rf_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ソフトバンク 2012: rf_zone_se=-1, upper_half=True, rank=3, adv_shape_se=-1/+1, run_balance_t=0.482 / surprise=-1.16
  - ソフトバンク 2012 は「rf_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2013: rf_zone_se=-1, upper_half=True, rank=2, adv_shape_se=-1/+1, run_balance_t=+1.28 / surprise=-1.14
  - 阪神 2013 は「rf_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 中日 2012 **(focus)**: rf_zone_se=-1, upper_half=True, rank=2, adv_shape_se=-1/+1, run_balance_t=0.530 / surprise=-1.12
  - 中日 2012 は「rf_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ソフトバンク 2019: rf_zone_se=-1, upper_half=True, rank=2, adv_shape_se=-1/+1, run_balance_t=0.303 / surprise=-1.08
  - ソフトバンク 2019 は「rf_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 34 件（裏の判例も同じ）

- ソフトバンク 2013: rf_zone_se=1, upper_half=False, rank=4, adv_shape_se=+1/0, run_balance_t=+1.75 / surprise=+2.34
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- ヤクルト 2024: rf_zone_se=1, upper_half=False, rank=5, adv_shape_se=+1/-1, run_balance_t=-1.31 / surprise=+1.71
  - ヤクルト 2024 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- DeNA 2013: rf_zone_se=1, upper_half=False, rank=5, adv_shape_se=+1/-1, run_balance_t=-0.777 / surprise=+1.70
  - DeNA 2013 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- ヤクルト 2014: rf_zone_se=1, upper_half=False, rank=6, adv_shape_se=+1/-1, run_balance_t=-0.793 / surprise=+1.66
  - ヤクルト 2014 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- ヤクルト 2019: rf_zone_se=1, upper_half=False, rank=6, adv_shape_se=+1/-1, run_balance_t=-1.58 / surprise=+1.61
  - ヤクルト 2019 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- 西武 2015: rf_zone_se=1, upper_half=False, rank=4, adv_shape_se=+1/0, run_balance_t=0.918 / surprise=+1.53
  - 西武 2015 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- 西武 2016: rf_zone_se=1, upper_half=False, rank=4, adv_shape_se=+1/-1, run_balance_t=-0.231 / surprise=+1.15
  - 西武 2016 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- ヤクルト 2016: rf_zone_se=1, upper_half=False, rank=5, adv_shape_se=+1/-1, run_balance_t=-1.96 / surprise=+1.02
  - ヤクルト 2016 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- ヤクルト 2023: rf_zone_se=0, upper_half=False, rank=5, adv_shape_se=0/-1, run_balance_t=-0.804 / surprise=0.987
  - ヤクルト 2023 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- 楽天 2022: rf_zone_se=0, upper_half=False, rank=4, adv_shape_se=0/0, run_balance_t=0.109 / surprise=0.953
  - 楽天 2022 は「upper_half == False」を満たすのに「rf_zone_se == -1」を満たさない。なぜか？ → H2
- ほか 24 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rf_zone_se=-1, upper_half=True, rank=3, adv_shape_se=-1/0, run_balance_t=-1.39
- ロッテ 2020: rf_zone_se=-1, upper_half=True, rank=2, adv_shape_se=-1/0, run_balance_t=-0.443

## P148: 失点の優位が誤差を超えて負けている（失点 −1）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 10 件: l-2019, s-2012, l-2018, db-2024, b-2025 ほか
- もし: `ra_zone_se == -1` ならば: `upper_half == False`
- 識別子: `[all] ra_zone_se==-1 => upper_half==false`（指紋 `b7486b886a6ce7d8`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P115, P126, P138, P147, P149, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 失点 −1 の単位の4分の1を超えて A クラス
- 注記: P147 の鏡（失点の側）。逆（B なら失点ははっきり劣る）を P147 の逆と比べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 43 | 33 | 0.77 [0.62, 0.87] | +0.26σ（0.477） | 0.50 | 1.53 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 68 | 0.87 [0.78, 0.93] | +2.48σ（0.006） | 0.72 | 1.20 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 33 | 0.42 [0.32, 0.53] | -6.67σ（0.000） | 0.28 | 1.53 | 0.000 | 0 | 修正 | 2 |
| 裏 | 113 | 68 | 0.60 [0.51, 0.69] | -3.64σ（0.000） | 0.50 | 1.20 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 10 件（対偶の判例も同じ）

- 西武 2019: ra_zone_se=-1, upper_half=True, rank=1, adv_shape_se=+1/-1, run_balance_t=+1.13 / surprise=-2.34
  - 西武 2019 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ヤクルト 2012: ra_zone_se=-1, upper_half=True, rank=3, adv_shape_se=+1/-1, run_balance_t=-0.259 / surprise=-1.89
  - ヤクルト 2012 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2018: ra_zone_se=-1, upper_half=True, rank=1, adv_shape_se=+1/-1, run_balance_t=+2.57 / surprise=-1.56
  - 西武 2018 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- DeNA 2024: ra_zone_se=-1, upper_half=True, rank=3, adv_shape_se=+1/-1, run_balance_t=0.420 / surprise=-1.46
  - DeNA 2024 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- オリックス 2025: ra_zone_se=-1, upper_half=True, rank=3, adv_shape_se=0/-1, run_balance_t=-0.528 / surprise=-1.34
  - オリックス 2025 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2021: ra_zone_se=-1, upper_half=True, rank=2, adv_shape_se=+1/-1, run_balance_t=0.192 / surprise=-1.29
  - ロッテ 2021 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 西武 2012: ra_zone_se=-1, upper_half=True, rank=2, adv_shape_se=+1/-1, run_balance_t=-0.132 / surprise=-1.24
  - 西武 2012 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ヤクルト 2022: ra_zone_se=-1, upper_half=True, rank=1, adv_shape_se=+1/-1, run_balance_t=+1.19 / surprise=-1.14
  - ヤクルト 2022 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- 阪神 2015: ra_zone_se=-1, upper_half=True, rank=3, adv_shape_se=-1/-1, run_balance_t=-1.69 / surprise=-1.06
  - 阪神 2015 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2023: ra_zone_se=-1, upper_half=True, rank=2, adv_shape_se=0/-1, run_balance_t=-0.422 / surprise=-1.00
  - ロッテ 2023 は「ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 45 件（裏の判例も同じ）

- 中日 2021 **(focus)**: ra_zone_se=1, upper_half=False, rank=5, adv_shape_se=-1/+1, run_balance_t=-1.68 / surprise=+2.22
  - 中日 2021 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- 巨人 2017: ra_zone_se=1, upper_half=False, rank=4, adv_shape_se=-1/+1, run_balance_t=0.847 / surprise=+2.19
  - 巨人 2017 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- 中日 2019 **(focus)**: ra_zone_se=1, upper_half=False, rank=5, adv_shape_se=-1/+1, run_balance_t=0.545 / surprise=+2.07
  - 中日 2019 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- 広島 2024: ra_zone_se=1, upper_half=False, rank=4, adv_shape_se=-1/+1, run_balance_t=-0.126 / surprise=+1.50
  - 広島 2024 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- 広島 2015: ra_zone_se=1, upper_half=False, rank=4, adv_shape_se=0/+1, run_balance_t=+1.05 / surprise=+1.39
  - 広島 2015 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- ソフトバンク 2021: ra_zone_se=1, upper_half=False, rank=4, adv_shape_se=0/+1, run_balance_t=+1.50 / surprise=+1.22
  - ソフトバンク 2021 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- 西武 2023: ra_zone_se=1, upper_half=False, rank=5, adv_shape_se=-1/+1, run_balance_t=-0.729 / surprise=+1.12
  - 西武 2023 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- オリックス 2024: ra_zone_se=1, upper_half=False, rank=5, adv_shape_se=-1/+1, run_balance_t=-1.13 / surprise=+1.08
  - オリックス 2024 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- オリックス 2018: ra_zone_se=1, upper_half=False, rank=4, adv_shape_se=-1/+1, run_balance_t=-0.852 / surprise=+1.06
  - オリックス 2018 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- オリックス 2013: ra_zone_se=1, upper_half=False, rank=5, adv_shape_se=-1/+1, run_balance_t=-0.715 / surprise=+1.03
  - オリックス 2013 は「upper_half == False」を満たすのに「ra_zone_se == -1」を満たさない。なぜか？ → H2
- ほか 35 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 西武 2020: ra_zone_se=-1, upper_half=True, rank=3, adv_shape_se=0/-1, run_balance_t=-1.57

## P149: 得点も失点もはっきり劣る（形 -1/-1）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: t-2015
- もし: `adv_shape_se == -1/-1` ならば: `upper_half == False`
- 識別子: `[all] adv_shape_se=="-1/-1" => upper_half==false`（指紋 `46ee815a9e4806bc`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P115, P126, P138, P147, P148, P150, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: この形の4分の1を超えて A クラス
- 注記: 見ている（13中12）。形ごとの表をそろえるために置く
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 12 | 0.92 [0.67, 0.99] | +1.44σ（0.127） | 0.50 | 1.85 | 0.001 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 77 | 0.99 [0.93, 1.00] | +4.84σ（0.000） | 0.92 | 1.08 | 0.001 | 0 | 支持 | 1 |
| 逆 | 78 | 12 | 0.15 [0.09, 0.25] | -12.16σ（0.000） | 0.08 | 1.85 | 0.001 | 0 | 修正 | 2 |
| 裏 | 143 | 77 | 0.54 [0.46, 0.62] | -5.84σ（0.000） | 0.50 | 1.08 | 0.001 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 阪神 2015: adv_shape_se=-1/-1, upper_half=True, rank=3, rf_adv_t=-1.39, ra_adv_t=-1.06 / surprise=-1.69
  - 阪神 2015 は「adv_shape_se == -1/-1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 66 件（裏の判例も同じ）

- 西武 2024: adv_shape_se=-1/0, upper_half=False, rank=6, rf_adv_t=-4.96, ra_adv_t=-0.159 / surprise=-3.41
  - 西武 2024 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- ヤクルト 2025: adv_shape_se=0/-1, upper_half=False, rank=6, rf_adv_t=-0.621, ra_adv_t=-3.34 / surprise=-2.91
  - ヤクルト 2025 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- 中日 2024 **(focus)**: adv_shape_se=-1/0, upper_half=False, rank=6, rf_adv_t=-3.48, ra_adv_t=-0.593 / surprise=-2.65
  - 中日 2024 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- 中日 2023 **(focus)**: adv_shape_se=-1/0, upper_half=False, rank=6, rf_adv_t=-4.14, ra_adv_t=0.063 / surprise=-2.64
  - 中日 2023 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- ロッテ 2018: adv_shape_se=-1/0, upper_half=False, rank=5, rf_adv_t=-2.48, ra_adv_t=-0.913 / surprise=-2.37
  - ロッテ 2018 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- オリックス 2019: adv_shape_se=-1/0, upper_half=False, rank=6, rf_adv_t=-2.29, ra_adv_t=-0.783 / surprise=-2.16
  - オリックス 2019 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- 日本ハム 2017: adv_shape_se=-1/0, upper_half=False, rank=5, rf_adv_t=-2.13, ra_adv_t=-0.904 / surprise=-2.14
  - 日本ハム 2017 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- ロッテ 2014: adv_shape_se=0/-1, upper_half=False, rank=4, rf_adv_t=-0.674, ra_adv_t=-2.11 / surprise=-2.03
  - ロッテ 2014 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- ヤクルト 2016: adv_shape_se=+1/-1, upper_half=False, rank=5, rf_adv_t=+1.02, ra_adv_t=-3.59 / surprise=-1.96
  - ヤクルト 2016 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- DeNA 2015: adv_shape_se=0/-1, upper_half=False, rank=6, rf_adv_t=0.204, ra_adv_t=-2.82 / surprise=-1.95
  - DeNA 2015 は「upper_half == False」を満たすのに「adv_shape_se == -1/-1」を満たさない。なぜか？ → H2
- ほか 56 件（propositions.jsonl を参照）

## P150: 得点ははっきり足りず、失点は平均と区別できない（形 -1/0）なら、B クラス

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 1 件: g-2016
- もし: `adv_shape_se == -1/0` ならば: `upper_half == False`
- 識別子: `[all] adv_shape_se=="-1/0" => upper_half==false`（指紋 `585834e7dca94dc7`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P115, P126, P138, P147, P148, P149, P151, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: この形の4分の1を超えて A クラス
- 注記: 中日を含めた P141。見ている。P151（鏡 0/-1）と比べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 25 | 24 | 0.96 [0.80, 0.99] | +2.42σ（0.007） | 0.50 | 1.92 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 77 | 0.99 [0.93, 1.00] | +4.84σ（0.000） | 0.84 | 1.18 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 24 | 0.31 [0.22, 0.42] | -9.02σ（0.000） | 0.16 | 1.92 | 0.000 | 0 | 修正 | 2 |
| 裏 | 131 | 77 | 0.59 [0.50, 0.67] | -4.29σ（0.000） | 0.50 | 1.18 | 0.000 | 0 | 修正 | 2 |

**異議あり（例外あり）** 元の命題に判例 1 件（対偶の判例も同じ）

- 巨人 2016: adv_shape_se=-1/0, upper_half=True, rank=2, rf_adv_t=-1.54, ra_adv_t=0.970, bat_routes=1 / surprise=-0.308
  - 巨人 2016 は「adv_shape_se == -1/0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 54 件（裏の判例も同じ）

- ヤクルト 2017: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-3.02, ra_adv_t=-2.46, bat_routes=1 / surprise=-3.87
  - ヤクルト 2017 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- ロッテ 2017: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-3.19, ra_adv_t=-2.27, bat_routes=0 / surprise=-3.80
  - ロッテ 2017 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- 楽天 2015: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-3.86, ra_adv_t=-1.55, bat_routes=0 / surprise=-3.71
  - 楽天 2015 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- DeNA 2012: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-1.10, ra_adv_t=-3.62, bat_routes=0 / surprise=-3.45
  - DeNA 2012 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- オリックス 2016: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-2.86, ra_adv_t=-1.75, bat_routes=0 / surprise=-3.18
  - オリックス 2016 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- 中日 2017 **(focus)**: adv_shape_se=-1/-1, upper_half=False, rank=5, rf_adv_t=-3.14, ra_adv_t=-1.41, bat_routes=0 / surprise=-3.03
  - 中日 2017 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- ヤクルト 2025: adv_shape_se=0/-1, upper_half=False, rank=6, rf_adv_t=-0.621, ra_adv_t=-3.34, bat_routes=1 / surprise=-2.91
  - ヤクルト 2025 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- ロッテ 2025: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-1.47, ra_adv_t=-2.53, bat_routes=0 / surprise=-2.85
  - ロッテ 2025 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- 楽天 2016: adv_shape_se=-1/-1, upper_half=False, rank=5, rf_adv_t=-1.17, ra_adv_t=-2.30, bat_routes=0 / surprise=-2.47
  - 楽天 2016 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- オリックス 2012: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-1.55, ra_adv_t=-1.44, bat_routes=2 / surprise=-2.10
  - オリックス 2012 は「upper_half == False」を満たすのに「adv_shape_se == -1/0」を満たさない。なぜか？ → H2
- ほか 44 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: adv_shape_se=-1/0, upper_half=True, rank=3, rf_adv_t=-2.51, ra_adv_t=0.134, bat_routes=0
- ロッテ 2020: adv_shape_se=-1/0, upper_half=True, rank=2, rf_adv_t=-1.15, ra_adv_t=0.511, bat_routes=1

## P151: 得点は平均と区別できず、失点ははっきり劣る（形 0/-1）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: b-2025, m-2023
- もし: `adv_shape_se == 0/-1` ならば: `upper_half == False`
- 識別子: `[all] adv_shape_se=="0/-1" => upper_half==false`（指紋 `643e7bcb6148d3b6`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P115, P126, P138, P147, P148, P149, P150, P181
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: この形の4分の1を超えて A クラス
- 注記: P150 の鏡。まだ見ていない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 15 | 0.88 [0.66, 0.97] | +1.26σ（0.164） | 0.50 | 1.76 | 0.001 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 76 | 0.97 [0.91, 0.99] | +4.58σ（0.000） | 0.89 | 1.09 | 0.001 | 0 | 支持 | 1 |
| 逆 | 78 | 15 | 0.19 [0.12, 0.29] | -11.37σ（0.000） | 0.11 | 1.76 | 0.001 | 0 | 修正 | 2 |
| 裏 | 139 | 76 | 0.55 [0.46, 0.63] | -5.53σ（0.000） | 0.50 | 1.09 | 0.001 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- オリックス 2025: adv_shape_se=0/-1, upper_half=True, rank=3, rf_adv_t=0.623, ra_adv_t=-1.34 / surprise=-0.528
  - オリックス 2025 は「adv_shape_se == 0/-1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2
- ロッテ 2023: adv_shape_se=0/-1, upper_half=True, rank=2, rf_adv_t=0.419, ra_adv_t=-1.00 / surprise=-0.422
  - ロッテ 2023 は「adv_shape_se == 0/-1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 63 件（裏の判例も同じ）

- ヤクルト 2017: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-3.02, ra_adv_t=-2.46 / surprise=-3.87
  - ヤクルト 2017 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- ロッテ 2017: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-3.19, ra_adv_t=-2.27 / surprise=-3.80
  - ロッテ 2017 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- 楽天 2015: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-3.86, ra_adv_t=-1.55 / surprise=-3.71
  - 楽天 2015 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- DeNA 2012: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-1.10, ra_adv_t=-3.62 / surprise=-3.45
  - DeNA 2012 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- 西武 2024: adv_shape_se=-1/0, upper_half=False, rank=6, rf_adv_t=-4.96, ra_adv_t=-0.159 / surprise=-3.41
  - 西武 2024 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- オリックス 2016: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-2.86, ra_adv_t=-1.75 / surprise=-3.18
  - オリックス 2016 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- 中日 2017 **(focus)**: adv_shape_se=-1/-1, upper_half=False, rank=5, rf_adv_t=-3.14, ra_adv_t=-1.41 / surprise=-3.03
  - 中日 2017 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- ロッテ 2025: adv_shape_se=-1/-1, upper_half=False, rank=6, rf_adv_t=-1.47, ra_adv_t=-2.53 / surprise=-2.85
  - ロッテ 2025 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- 中日 2024 **(focus)**: adv_shape_se=-1/0, upper_half=False, rank=6, rf_adv_t=-3.48, ra_adv_t=-0.593 / surprise=-2.65
  - 中日 2024 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- 中日 2023 **(focus)**: adv_shape_se=-1/0, upper_half=False, rank=6, rf_adv_t=-4.14, ra_adv_t=0.063 / surprise=-2.64
  - 中日 2023 は「upper_half == False」を満たすのに「adv_shape_se == 0/-1」を満たさない。なぜか？ → H2
- ほか 53 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 西武 2020: adv_shape_se=0/-1, upper_half=True, rank=3, rf_adv_t=-0.542, ra_adv_t=-1.63

## P152: 得点も失点もはっきり上回る（形 +1/+1）なら、A クラス

- **判定: exit 2 異議あり（主張が強すぎる）**（仮: 元の命題と対偶まで） — 逆: 判例 65 件: l-2018, l-2017, b-2014, g-2013, b-2023 ほか
- もし: `adv_shape_se == +1/+1` ならば: `upper_half == True`
- 識別子: `[all] adv_shape_se=="+1/+1" => upper_half==true`（指紋 `ead60eba821d66dc`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P50, P153, P154, P177, P178, P179, P180, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: この形の4分の1を超えて B クラス
- 注記: まだ見ていない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 13 | 13 | 1.00 [0.77, 1.00] | +2.08σ（0.024） | 0.50 | 2.00 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 78 | 78 | 1.00 [0.95, 1.00] | +5.10σ（0.000） | 0.92 | 1.09 | 0.000 | 0 | 支持 | 0 |
| 逆 | 78 | 13 | 0.17 [0.10, 0.26] | -11.90σ（0.000） | 0.08 | 2.00 | 0.000 | 0 | 修正 | 2 |
| 裏 | 143 | 78 | 0.55 [0.46, 0.62] | -5.65σ（0.000） | 0.50 | 1.09 | 0.000 | 0 | 修正 | 2 |

**異議あり（主張が強すぎる）** 逆に判例 65 件（裏の判例も同じ）

- 西武 2018: adv_shape_se=+1/-1, upper_half=True, rank=1, rf_adv_t=+5.07, ra_adv_t=-1.56 / surprise=+2.57
  - 西武 2018 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- 西武 2017: adv_shape_se=+1/0, upper_half=True, rank=2, rf_adv_t=+3.22, ra_adv_t=0.251 / surprise=+2.51
  - 西武 2017 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- オリックス 2014: adv_shape_se=0/+1, upper_half=True, rank=2, rf_adv_t=0.212, ra_adv_t=+3.47 / surprise=+2.47
  - オリックス 2014 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- 巨人 2013: adv_shape_se=0/+1, upper_half=True, rank=1, rf_adv_t=0.813, ra_adv_t=+2.46 / surprise=+2.28
  - 巨人 2013 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- オリックス 2023: adv_shape_se=0/+1, upper_half=True, rank=1, rf_adv_t=0.505, ra_adv_t=+2.43 / surprise=+2.06
  - オリックス 2023 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- ヤクルト 2021: adv_shape_se=+1/0, upper_half=True, rank=1, rf_adv_t=+2.40, ra_adv_t=0.430 / surprise=+2.05
  - ヤクルト 2021 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- 巨人 2024: adv_shape_se=0/+1, upper_half=True, rank=1, rf_adv_t=0.050, ra_adv_t=+3.04 / surprise=+2.02
  - 巨人 2024 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- ソフトバンク 2018: adv_shape_se=+1/0, upper_half=True, rank=2, rf_adv_t=+2.22, ra_adv_t=0.579 / surprise=+1.97
  - ソフトバンク 2018 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- ソフトバンク 2022: adv_shape_se=+1/0, upper_half=True, rank=1, rf_adv_t=+1.66, ra_adv_t=0.776 / surprise=+1.74
  - ソフトバンク 2022 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- 広島 2018: adv_shape_se=+1/0, upper_half=True, rank=1, rf_adv_t=+2.85, ra_adv_t=-0.466 / surprise=+1.72
  - 広島 2018 は「upper_half == True」を満たすのに「adv_shape_se == +1/+1」を満たさない。なぜか？ → H2
- ほか 55 件（propositions.jsonl を参照）

## P153: 得点ははっきり上回り、失点は平均と区別できない（形 +1/0）なら、A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: h-2013, l-2015
- もし: `adv_shape_se == +1/0` ならば: `upper_half == True`
- 識別子: `[all] adv_shape_se=="+1/0" => upper_half==true`（指紋 `ddfa02810fe5226d`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P50, P152, P154, P177, P178, P179, P180, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: この形の4分の1を超えて B クラス
- 注記: まだ見ていない。P154（鏡 0/+1）と比べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 15 | 13 | 0.87 [0.62, 0.96] | +1.04σ（0.236） | 0.50 | 1.73 | 0.002 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 76 | 0.97 [0.91, 0.99] | +4.58σ（0.000） | 0.90 | 1.08 | 0.002 | 0 | 支持 | 1 |
| 逆 | 78 | 13 | 0.17 [0.10, 0.26] | -11.90σ（0.000） | 0.10 | 1.73 | 0.002 | 0 | 修正 | 2 |
| 裏 | 141 | 76 | 0.54 [0.46, 0.62] | -5.79σ（0.000） | 0.50 | 1.08 | 0.002 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- ソフトバンク 2013: adv_shape_se=+1/0, upper_half=False, rank=4, rf_adv_t=+2.34, ra_adv_t=0.032 / surprise=+1.75
  - ソフトバンク 2013 は「adv_shape_se == +1/0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 西武 2015: adv_shape_se=+1/0, upper_half=False, rank=4, rf_adv_t=+1.53, ra_adv_t=-0.352 / surprise=0.918
  - 西武 2015 は「adv_shape_se == +1/0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 65 件（裏の判例も同じ）

- ソフトバンク 2024: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+3.67, ra_adv_t=+3.49 / surprise=+5.03
  - ソフトバンク 2024 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- 巨人 2012: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+2.66, ra_adv_t=+4.58 / surprise=+4.85
  - 巨人 2012 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- 広島 2017: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+4.84, ra_adv_t=+1.10 / surprise=+4.32
  - 広島 2017 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- 広島 2016: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+3.59, ra_adv_t=+2.45 / surprise=+4.30
  - 広島 2016 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- 阪神 2025: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+1.45, ra_adv_t=+4.57 / surprise=+4.23
  - 阪神 2025 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- ソフトバンク 2025: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+2.11, ra_adv_t=+3.18 / surprise=+3.67
  - ソフトバンク 2025 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- ソフトバンク 2015: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+2.49, ra_adv_t=+2.42 / surprise=+3.48
  - ソフトバンク 2015 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- 日本ハム 2016: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+1.09, ra_adv_t=+3.79 / surprise=+3.30
  - 日本ハム 2016 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- ソフトバンク 2016: adv_shape_se=+1/+1, upper_half=True, rank=2, rf_adv_t=+1.53, ra_adv_t=+3.37 / surprise=+3.29
  - ソフトバンク 2016 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- 日本ハム 2025: adv_shape_se=+1/+1, upper_half=True, rank=2, rf_adv_t=+2.02, ra_adv_t=+2.63 / surprise=+3.22
  - 日本ハム 2025 は「upper_half == True」を満たすのに「adv_shape_se == +1/0」を満たさない。なぜか？ → H2
- ほか 55 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: adv_shape_se=+1/0, upper_half=False, rank=4, rf_adv_t=+1.82, ra_adv_t=-0.940

## P154: 得点は平均と区別できず、失点ははっきり上回る（形 0/+1）なら、A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: h-2021, c-2015
- もし: `adv_shape_se == 0/+1` ならば: `upper_half == True`
- 識別子: `[all] adv_shape_se=="0/+1" => upper_half==true`（指紋 `7f1ed22826a69037`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P50, P152, P153, P177, P178, P179, P180, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: この形の4分の1を超えて B クラス
- 注記: まだ見ていない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 19 | 17 | 0.89 [0.69, 0.97] | +1.46σ（0.111） | 0.50 | 1.79 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 76 | 0.97 [0.91, 0.99] | +4.58σ（0.000） | 0.88 | 1.11 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 17 | 0.22 [0.14, 0.32] | -10.85σ（0.000） | 0.12 | 1.79 | 0.000 | 0 | 修正 | 2 |
| 裏 | 137 | 76 | 0.55 [0.47, 0.64] | -5.28σ（0.000） | 0.50 | 1.11 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- ソフトバンク 2021: adv_shape_se=0/+1, upper_half=False, rank=4, rf_adv_t=0.915, ra_adv_t=+1.22 / surprise=+1.50
  - ソフトバンク 2021 は「adv_shape_se == 0/+1」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2
- 広島 2015: adv_shape_se=0/+1, upper_half=False, rank=4, rf_adv_t=0.115, ra_adv_t=+1.39 / surprise=+1.05
  - 広島 2015 は「adv_shape_se == 0/+1」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 61 件（裏の判例も同じ）

- ソフトバンク 2024: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+3.67, ra_adv_t=+3.49 / surprise=+5.03
  - ソフトバンク 2024 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- 巨人 2012: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+2.66, ra_adv_t=+4.58 / surprise=+4.85
  - 巨人 2012 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- 広島 2017: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+4.84, ra_adv_t=+1.10 / surprise=+4.32
  - 広島 2017 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- 広島 2016: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+3.59, ra_adv_t=+2.45 / surprise=+4.30
  - 広島 2016 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- 阪神 2025: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+1.45, ra_adv_t=+4.57 / surprise=+4.23
  - 阪神 2025 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- ソフトバンク 2025: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+2.11, ra_adv_t=+3.18 / surprise=+3.67
  - ソフトバンク 2025 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- ソフトバンク 2015: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+2.49, ra_adv_t=+2.42 / surprise=+3.48
  - ソフトバンク 2015 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- 日本ハム 2016: adv_shape_se=+1/+1, upper_half=True, rank=1, rf_adv_t=+1.09, ra_adv_t=+3.79 / surprise=+3.30
  - 日本ハム 2016 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- ソフトバンク 2016: adv_shape_se=+1/+1, upper_half=True, rank=2, rf_adv_t=+1.53, ra_adv_t=+3.37 / surprise=+3.29
  - ソフトバンク 2016 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- 日本ハム 2025: adv_shape_se=+1/+1, upper_half=True, rank=2, rf_adv_t=+2.02, ra_adv_t=+2.63 / surprise=+3.22
  - 日本ハム 2025 は「upper_half == True」を満たすのに「adv_shape_se == 0/+1」を満たさない。なぜか？ → H2
- ほか 51 件（propositions.jsonl を参照）

## P155: 得点がリーグ5位以下のチーム・シーズンでは、得点する回の頻度の不足が、得点した回の大きさの不足より大きい（条件を「もし」に移した形）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 13 件: d-2017, f-2023, d-2022, db-2018, d-2013 ほか
- もし: `rank_rf >= 5` ならば: `inn_freq_minus_size < 0`
- 識別子: `[seasons=2013-2025] rank_rf>=5 => inn_freq_minus_size<0`（指紋 `417299378b37b89b`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 親: P23（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P23 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 35 | 0.73 [0.59, 0.83] | +3.18σ（0.001） | 0.45 | 1.62 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 79 | 66 | 0.84 [0.74, 0.90] | +5.96σ（0.000） | 0.67 | 1.25 | 0.000 | 0 | 支持 | 1 |
| 逆 | 65 | 35 | 0.54 [0.42, 0.65] | +0.62σ（0.310） | 0.33 | 1.62 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 96 | 66 | 0.69 [0.59, 0.77] | +3.67σ（0.000） | 0.55 | 1.25 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 13 件（対偶の判例も同じ）

- 中日 2017 **(focus)**: rank_rf=5, inn_freq_minus_size=0.089, rank=5, inn_dlog_freq=-0.047, inn_dlog_size=-0.136 / surprise=0.089
  - 中日 2017 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2023: rank_rf=5, inn_freq_minus_size=0.065, rank=6, inn_dlog_freq=-0.003, inn_dlog_size=-0.068 / surprise=0.065
  - 日本ハム 2023 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2022 **(focus)**: rank_rf=6, inn_freq_minus_size=0.049, rank=6, inn_dlog_freq=-0.107, inn_dlog_size=-0.156 / surprise=0.049
  - 中日 2022 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2018: rank_rf=6, inn_freq_minus_size=0.043, rank=4, inn_dlog_freq=-0.029, inn_dlog_size=-0.072 / surprise=0.043
  - DeNA 2018 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2013 **(focus)**: rank_rf=6, inn_freq_minus_size=0.043, rank=4, inn_dlog_freq=-0.029, inn_dlog_size=-0.072 / surprise=0.043
  - 中日 2013 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2019 **(focus)**: rank_rf=5, inn_freq_minus_size=0.040, rank=5, inn_dlog_freq=-0.012, inn_dlog_size=-0.052 / surprise=0.040
  - 中日 2019 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2015: rank_rf=6, inn_freq_minus_size=0.038, rank=6, inn_dlog_freq=-0.117, inn_dlog_size=-0.156 / surprise=0.038
  - 楽天 2015 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 広島 2023: rank_rf=5, inn_freq_minus_size=0.023, rank=2, inn_dlog_freq=0.008, inn_dlog_size=-0.015 / surprise=0.023
  - 広島 2023 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- 中日 2025 **(focus)**: rank_rf=6, inn_freq_minus_size=0.018, rank=4, inn_dlog_freq=-0.068, inn_dlog_size=-0.087 / surprise=0.018
  - 中日 2025 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2024: rank_rf=5, inn_freq_minus_size=0.010, rank=5, inn_dlog_freq=-0.089, inn_dlog_size=-0.098 / surprise=0.010
  - オリックス 2024 は「rank_rf >= 5」を満たすのに「inn_freq_minus_size < 0」を満たさない。なぜか？ → H5, H6
- ほか 3 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 30 件（裏の判例も同じ）

- 巨人 2024: rank_rf=4, inn_freq_minus_size=-0.217, rank=1, inn_dlog_freq=-0.103, inn_dlog_size=0.115 / surprise=-0.217
  - 巨人 2024 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ロッテ 2016: rank_rf=4, inn_freq_minus_size=-0.150, rank=3, inn_dlog_freq=-0.077, inn_dlog_size=0.073 / surprise=-0.150
  - ロッテ 2016 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- オリックス 2025: rank_rf=3, inn_freq_minus_size=-0.134, rank=3, inn_dlog_freq=-0.043, inn_dlog_size=0.091 / surprise=-0.134
  - オリックス 2025 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 広島 2022: rank_rf=2, inn_freq_minus_size=-0.134, rank=5, inn_dlog_freq=-0.030, inn_dlog_size=0.103 / surprise=-0.134
  - 広島 2022 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- オリックス 2018: rank_rf=4, inn_freq_minus_size=-0.120, rank=4, inn_dlog_freq=-0.135, inn_dlog_size=-0.015 / surprise=-0.120
  - オリックス 2018 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 巨人 2018: rank_rf=3, inn_freq_minus_size=-0.111, rank=3, inn_dlog_freq=-0.054, inn_dlog_size=0.057 / surprise=-0.111
  - 巨人 2018 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- DeNA 2019: rank_rf=3, inn_freq_minus_size=-0.090, rank=2, inn_dlog_freq=-0.047, inn_dlog_size=0.043 / surprise=-0.090
  - DeNA 2019 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- オリックス 2023: rank_rf=3, inn_freq_minus_size=-0.085, rank=1, inn_dlog_freq=-0.023, inn_dlog_size=0.062 / surprise=-0.085
  - オリックス 2023 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 阪神 2014: rank_rf=3, inn_freq_minus_size=-0.085, rank=2, inn_dlog_freq=-0.046, inn_dlog_size=0.039 / surprise=-0.085
  - 阪神 2014 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ロッテ 2015: rank_rf=4, inn_freq_minus_size=-0.072, rank=3, inn_dlog_freq=-0.038, inn_dlog_size=0.034 / surprise=-0.072
  - ロッテ 2015 は「inn_freq_minus_size < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ほか 20 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: rank_rf=6, inn_freq_minus_size=0.031, rank=3, inn_dlog_freq=-0.065, inn_dlog_size=-0.096

## P156: 得点がリーグ5位以下だったシーズンの中日は、得点した回のうち1点の回の割合が他球団より多い（条件を「もし」に移した形）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2015
- もし: `rank_rf >= 5` ならば: `inn_d_single_share > 0`
- 識別子: `[team=d, seasons=2013-2025] rank_rf>=5 => inn_d_single_share>0`（指紋 `094067c41970bf6f`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025'} / 単位数: 12
- 親: P26（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P26 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.92 | 0.99 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.08 | 0.00 | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.92 | 0.99 | 1.000 | 0 | 判断保留 | 4 |
| 裏 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.08 | 0.00 | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2015 **(focus)**: rank_rf=5, inn_d_single_share=-0.008, inn_d_big_share=-0.015, inn_dlog_size=-0.028, rank=5 / surprise=-0.008
  - 中日 2015 は「rank_rf >= 5」を満たすのに「inn_d_single_share > 0」を満たさない。なぜか？ → H5, H6

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 中日 2018 **(focus)**: rank_rf=4, inn_d_single_share=0.053, inn_d_big_share=-0.018, inn_dlog_size=-0.065, rank=5 / surprise=0.053
  - 中日 2018 は「inn_d_single_share > 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6

## P157: 得点がリーグ5位以下だったシーズンの中日は、得点した回のうち3点以上の回の割合が他球団より少ない（条件を「もし」に移した形）

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `rank_rf >= 5` ならば: `inn_d_big_share < 0`
- 識別子: `[team=d, seasons=2013-2025] rank_rf>=5 => inn_d_big_share<0`（指紋 `48ec33a54c3b8c8e`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025'} / 単位数: 12
- 親: P27（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P27 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | +1.91σ（0.042） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.08 | - | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 12 | 11 | 0.92 [0.65, 0.99] | +1.33σ（0.158） | 0.92 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 裏 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 中日 2018 **(focus)**: rank_rf=4, inn_d_big_share=-0.018, inn_d_single_share=0.053, inn_dlog_size=-0.065, rank=5 / surprise=-0.018
  - 中日 2018 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6

## P158: 得点がリーグ5位以下だったシーズンの中日は、ホームの試合で得点した回の大きさが他球団（ホーム同士）より小さい（条件を「もし」に移した形）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2014
- もし: `rank_rf >= 5` ならば: `inn_dlog_size_home < 0`
- 識別子: `[team=d, seasons=2013-2025] rank_rf>=5 => inn_dlog_size_home<0`（指紋 `e88908bc62636f29`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025'} / 単位数: 12
- 親: P28（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P28 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.92 | 0.99 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.08 | 0.00 | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.92 | 0.99 | 1.000 | 0 | 判断保留 | 4 |
| 裏 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.08 | 0.00 | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2014 **(focus)**: rank_rf=5, inn_dlog_size_home=0.009, inn_dlog_size_away=-0.055, inn_dlog_size=-0.024, inn_dlog_freq_home=-0.117 / surprise=0.009
  - 中日 2014 は「rank_rf >= 5」を満たすのに「inn_dlog_size_home < 0」を満たさない。なぜか？ → H5, H6

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 中日 2018 **(focus)**: rank_rf=4, inn_dlog_size_home=-0.094, inn_dlog_size_away=-0.030, inn_dlog_size=-0.065, inn_dlog_freq_home=-0.006 / surprise=-0.094
  - 中日 2018 は「inn_dlog_size_home < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6

## P159: 得点がリーグ5位以下だったシーズンの中日は、ビジターの試合で得点した回の大きさが他球団（ビジター同士）より小さい（条件を「もし」に移した形）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: d-2016
- もし: `rank_rf >= 5` ならば: `inn_dlog_size_away < 0`
- 識別子: `[team=d, seasons=2013-2025] rank_rf>=5 => inn_dlog_size_away<0`（指紋 `86dc84f8475a2e8f`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd', 'seasons': '2013-2025'} / 単位数: 12
- 親: P29（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P29 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.92 | 0.99 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.08 | 0.00 | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 11 | 10 | 0.91 [0.62, 0.98] | +1.22σ（0.197） | 0.92 | 0.99 | 1.000 | 0 | 判断保留 | 4 |
| 裏 | 1 | 0 | 0.00 [0.00, 0.79] | -1.73σ（0.250） | 0.08 | 0.00 | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 中日 2016 **(focus)**: rank_rf=6, inn_dlog_size_away=0.037, inn_dlog_size_home=-0.002, inn_dlog_size=0.018, inn_dlog_freq_away=-0.052 / surprise=0.037
  - 中日 2016 は「rank_rf >= 5」を満たすのに「inn_dlog_size_away < 0」を満たさない。なぜか？ → H5, H6

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 中日 2018 **(focus)**: rank_rf=4, inn_dlog_size_away=-0.030, inn_dlog_size_home=-0.094, inn_dlog_size=-0.065, inn_dlog_freq_away=0.052 / surprise=-0.030
  - 中日 2018 は「inn_dlog_size_away < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6

## P160: 得点がリーグ5位以下のチーム・シーズン（中日を除く）では、得点した回のうち3点以上の回の割合が他球団より少ない（条件を「もし」に移した形）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 9 件: e-2014, e-2016, m-2025, f-2019, l-2024 ほか
- もし: `rank_rf >= 5` ならば: `inn_d_big_share < 0`
- 識別子: `[seasons=2013-2025, where:team!="d"] rank_rf>=5 => inn_d_big_share<0`（指紋 `be27866f59d53db8`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'seasons': '2013-2025', 'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 132
- 親: P30（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P30 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 37 | 28 | 0.76 [0.60, 0.87] | +3.12σ（0.001） | 0.45 | 1.66 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 72 | 63 | 0.88 [0.78, 0.93] | +6.36σ（0.000） | 0.72 | 1.22 | 0.000 | 0 | 支持 | 1 |
| 逆 | 60 | 28 | 0.47 [0.35, 0.59] | -0.52σ（0.349） | 0.28 | 1.66 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 95 | 63 | 0.66 [0.56, 0.75] | +3.18σ（0.001） | 0.55 | 1.22 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 9 件（対偶の判例も同じ）

- 楽天 2014: rank_rf=6, inn_d_big_share=0.034, inn_d_single_share=-0.040, inn_dlog_size=0.049, rank=6 / surprise=0.034
  - 楽天 2014 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 楽天 2016: rank_rf=5, inn_d_big_share=0.022, inn_d_single_share=-0.010, inn_dlog_size=0.034, rank=5 / surprise=0.022
  - 楽天 2016 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2025: rank_rf=5, inn_d_big_share=0.019, inn_d_single_share=0.000, inn_dlog_size=0.018, rank=6 / surprise=0.019
  - ロッテ 2025 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2019: rank_rf=5, inn_d_big_share=0.011, inn_d_single_share=-0.011, inn_dlog_size=0.031, rank=5 / surprise=0.011
  - 日本ハム 2019 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 西武 2024: rank_rf=6, inn_d_big_share=0.010, inn_d_single_share=0.026, inn_dlog_size=-0.032, rank=6 / surprise=0.010
  - 西武 2024 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 西武 2021: rank_rf=5, inn_d_big_share=0.008, inn_d_single_share=-0.010, inn_dlog_size=0.015, rank=6 / surprise=0.008
  - 西武 2021 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 阪神 2022: rank_rf=5, inn_d_big_share=0.006, inn_d_single_share=-0.048, inn_dlog_size=0.031, rank=3 / surprise=0.006
  - 阪神 2022 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- 阪神 2013: rank_rf=5, inn_d_big_share=0.002, inn_d_single_share=0.013, inn_dlog_size=0.024, rank=2 / surprise=0.002
  - 阪神 2013 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6
- オリックス 2015: rank_rf=5, inn_d_big_share=0.001, inn_d_single_share=-0.004, inn_dlog_size=0.014, rank=5 / surprise=0.001
  - オリックス 2015 は「rank_rf >= 5」を満たすのに「inn_d_big_share < 0」を満たさない。なぜか？ → H5, H6

**待った！判断保留** 逆に判例 32 件（裏の判例も同じ）

- オリックス 2022: rank_rf=4, inn_d_big_share=-0.045, inn_d_single_share=0.009, inn_dlog_size=-0.079, rank=1 / surprise=-0.045
  - オリックス 2022 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 楽天 2025: rank_rf=4, inn_d_big_share=-0.039, inn_d_single_share=0.057, inn_dlog_size=-0.102, rank=4 / surprise=-0.039
  - 楽天 2025 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 西武 2016: rank_rf=2, inn_d_big_share=-0.036, inn_d_single_share=0.055, inn_dlog_size=-0.069, rank=4 / surprise=-0.036
  - 西武 2016 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ソフトバンク 2014: rank_rf=1, inn_d_big_share=-0.036, inn_d_single_share=0.007, inn_dlog_size=-0.019, rank=1 / surprise=-0.036
  - ソフトバンク 2014 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 巨人 2016: rank_rf=4, inn_d_big_share=-0.034, inn_d_single_share=0.027, inn_dlog_size=-0.050, rank=2 / surprise=-0.034
  - 巨人 2016 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ヤクルト 2024: rank_rf=2, inn_d_big_share=-0.029, inn_d_single_share=0.030, inn_dlog_size=-0.057, rank=5 / surprise=-0.029
  - ヤクルト 2024 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ヤクルト 2014: rank_rf=1, inn_d_big_share=-0.026, inn_d_single_share=0.010, inn_dlog_size=-0.020, rank=6 / surprise=-0.026
  - ヤクルト 2014 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ソフトバンク 2019: rank_rf=4, inn_d_big_share=-0.025, inn_d_single_share=0.081, inn_dlog_size=-0.103, rank=2 / surprise=-0.025
  - ソフトバンク 2019 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 楽天 2019: rank_rf=3, inn_d_big_share=-0.022, inn_d_single_share=-0.005, inn_dlog_size=-0.008, rank=3 / surprise=-0.022
  - 楽天 2019 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- DeNA 2022: rank_rf=4, inn_d_big_share=-0.022, inn_d_single_share=0.043, inn_dlog_size=-0.067, rank=2 / surprise=-0.022
  - DeNA 2022 は「inn_d_big_share < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ほか 22 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: rank_rf=5, inn_d_big_share=0.022, inn_d_single_share=0.011, inn_dlog_size=-0.004, rank=2
- ヤクルト 2020: rank_rf=5, inn_d_big_share=0.020, inn_d_single_share=-0.021, inn_dlog_size=0.009, rank=6

## P161: 得点がリーグ5位以下だったシーズンの中日は、ISO（長打率 − 打率）が他球団より低い（条件を「もし」に移した形）

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `rank_rf >= 5` ならば: `bat_d_iso < 0`
- 識別子: `[team=d] rank_rf>=5 => bat_d_iso<0`（指紋 `684b7a1cde4dfb19`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 親: P31（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P31 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | +1.91σ（0.042） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.15 | - | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 13 | 11 | 0.85 [0.58, 0.96] | +0.80σ（0.333） | 0.85 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 裏 | 2 | 0 | 0.00 [0.00, 0.66] | -2.45σ（0.062） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 逆に判例 2 件（裏の判例も同じ）

- 中日 2018 **(focus)**: rank_rf=4, bat_d_iso=-0.030, bat_d_obp=-0.007, bat_d_hr_pa=-0.009, bat_d_bb_pa=-0.017, rank=5 / surprise=-0.030
  - 中日 2018 は「bat_d_iso < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2, H6
- 中日 2012 **(focus)**: rank_rf=4, bat_d_iso=-0.007, bat_d_obp=0.001, bat_d_hr_pa=-0.001, bat_d_bb_pa=0.000, rank=2 / surprise=-0.007
  - 中日 2012 は「bat_d_iso < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2, H6

## P162: 得点がリーグ5位以下だったシーズンの中日は、出塁率が他球団より低い（条件を「もし」に移した形）

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `rank_rf >= 5` ならば: `bat_d_obp < 0`
- 識別子: `[team=d] rank_rf>=5 => bat_d_obp<0`（指紋 `edb2ae2b701f9c59`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 親: P32（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P32 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | +1.91σ（0.042） | 0.92 | 1.08 | 0.154 | 0 | 判断保留 | 4 |
| 対偶 | 1 | 1 | 1.00 [0.21, 1.00] | +0.58σ（0.750） | 0.15 | 6.50 | 0.154 | 0 | 判断保留 | 4 |
| 逆 | 12 | 11 | 0.92 [0.65, 0.99] | +1.33σ（0.158） | 0.85 | 1.08 | 0.154 | 0 | 判断保留 | 4 |
| 裏 | 2 | 1 | 0.50 [0.09, 0.91] | -0.82σ（0.438） | 0.08 | 6.50 | 0.154 | 0 | 判断保留 | 4 |

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 中日 2018 **(focus)**: rank_rf=4, bat_d_obp=-0.007, bat_d_iso=-0.030, bat_d_avg=0.007, bat_d_bb_pa=-0.017, rank=5 / surprise=-0.007
  - 中日 2018 は「bat_d_obp < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H2, H5

## P163: 得点がリーグ5位以下だったシーズンの中日は、走者1人あたりの得点が他球団より少ない（条件を「もし」に移した形）

- **判定: exit 4 待った！判断保留** — 元の命題: n=11（min_n=10）、成立率の区間 0.74〜1.00
- もし: `rank_rf >= 5` ならば: `bat_d_r_runner < 0`
- 識別子: `[team=d] rank_rf>=5 => bat_d_r_runner<0`（指紋 `81ae80184b8d08b0`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'team': 'd'} / 単位数: 13
- 親: P46（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P46 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 11 | 1.00 [0.74, 1.00] | +1.91σ（0.042） | 1.00 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.15 | - | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 13 | 11 | 0.85 [0.58, 0.96] | +0.80σ（0.333） | 0.85 | 1.00 | 1.000 | 0 | 判断保留 | 4 |
| 裏 | 2 | 0 | 0.00 [0.00, 0.66] | -2.45σ（0.062） | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**待った！判断保留** 逆に判例 2 件（裏の判例も同じ）

- 中日 2012 **(focus)**: rank_rf=4, bat_d_r_runner=-0.024, bat_d_r_ab=-0.008, bat_d_r_pa=-0.007, bat_d_obp=0.001, bat_d_iso=-0.007 / surprise=-0.024
  - 中日 2012 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 中日 2018 **(focus)**: rank_rf=4, bat_d_r_runner=-0.005, bat_d_r_ab=-0.007, bat_d_r_pa=-0.004, bat_d_obp=-0.007, bat_d_iso=-0.030 / surprise=-0.005
  - 中日 2018 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6

## P164: 得点がリーグ5位以下のチーム・シーズン（中日を除く）では、走者1人あたりの得点が他球団より少ない（条件を「もし」に移した形）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 5 件: t-2021, m-2014, db-2018, c-2023, f-2022
- もし: `rank_rf >= 5` ならば: `bat_d_r_runner < 0`
- 識別子: `[where:team!="d"] rank_rf>=5 => bat_d_r_runner<0`（指紋 `6aa697208a2edb09`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 143
- 親: P47（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P47 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 41 | 36 | 0.88 [0.74, 0.95] | +4.84σ（0.000） | 0.45 | 1.96 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 79 | 74 | 0.94 [0.86, 0.97] | +7.76σ（0.000） | 0.71 | 1.31 | 0.000 | 0 | 支持 | 1 |
| 逆 | 64 | 36 | 0.56 [0.44, 0.68] | +1.00σ（0.191） | 0.29 | 1.96 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 102 | 74 | 0.73 [0.63, 0.80] | +4.55σ（0.000） | 0.55 | 1.31 | 0.000 | 0 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 5 件（対偶の判例も同じ）

- 阪神 2021: rank_rf=5, bat_d_r_runner=0.009, bat_d_r_ab=0.001, bat_d_obp=-0.005, bat_d_iso=-0.001 / surprise=0.009
  - 阪神 2021 は「rank_rf >= 5」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- ロッテ 2014: rank_rf=5, bat_d_r_runner=0.005, bat_d_r_ab=-0.007, bat_d_obp=-0.017, bat_d_iso=0.006 / surprise=0.005
  - ロッテ 2014 は「rank_rf >= 5」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- DeNA 2018: rank_rf=6, bat_d_r_runner=0.005, bat_d_r_ab=-0.013, bat_d_obp=-0.028, bat_d_iso=0.029 / surprise=0.005
  - DeNA 2018 は「rank_rf >= 5」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- 広島 2023: rank_rf=5, bat_d_r_runner=0.003, bat_d_r_ab=-0.001, bat_d_obp=-0.002, bat_d_iso=-0.009 / surprise=0.003
  - 広島 2023 は「rank_rf >= 5」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6
- 日本ハム 2022: rank_rf=6, bat_d_r_runner=0.002, bat_d_r_ab=-0.009, bat_d_obp=-0.021, bat_d_iso=0.004 / surprise=0.002
  - 日本ハム 2022 は「rank_rf >= 5」を満たすのに「bat_d_r_runner < 0」を満たさない。なぜか？ → H5, H6

**待った！判断保留** 逆に判例 28 件（裏の判例も同じ）

- 楽天 2025: rank_rf=4, bat_d_r_runner=-0.032, bat_d_r_ab=-0.009, bat_d_obp=0.003, bat_d_iso=-0.025 / surprise=-0.032
  - 楽天 2025 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 楽天 2021: rank_rf=4, bat_d_r_runner=-0.023, bat_d_r_ab=-0.000, bat_d_obp=0.016, bat_d_iso=-0.008 / surprise=-0.023
  - 楽天 2021 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- オリックス 2022: rank_rf=4, bat_d_r_runner=-0.020, bat_d_r_ab=-0.003, bat_d_obp=0.009, bat_d_iso=-0.005 / surprise=-0.020
  - オリックス 2022 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 巨人 2017: rank_rf=4, bat_d_r_runner=-0.020, bat_d_r_ab=-0.007, bat_d_obp=0.000, bat_d_iso=-0.003 / surprise=-0.020
  - 巨人 2017 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- オリックス 2018: rank_rf=4, bat_d_r_runner=-0.019, bat_d_r_ab=-0.016, bat_d_obp=-0.020, bat_d_iso=-0.027 / surprise=-0.019
  - オリックス 2018 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- オリックス 2017: rank_rf=4, bat_d_r_runner=-0.018, bat_d_r_ab=-0.009, bat_d_obp=-0.004, bat_d_iso=-0.008 / surprise=-0.018
  - オリックス 2017 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 日本ハム 2018: rank_rf=3, bat_d_r_runner=-0.018, bat_d_r_ab=-0.003, bat_d_obp=0.006, bat_d_iso=-0.003 / surprise=-0.018
  - 日本ハム 2018 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 楽天 2019: rank_rf=3, bat_d_r_runner=-0.013, bat_d_r_ab=0.001, bat_d_obp=0.009, bat_d_iso=-0.001 / surprise=-0.013
  - 楽天 2019 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- 巨人 2025: rank_rf=3, bat_d_r_runner=-0.013, bat_d_r_ab=0.000, bat_d_obp=0.013, bat_d_iso=0.003 / surprise=-0.013
  - 巨人 2025 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- DeNA 2022: rank_rf=4, bat_d_r_runner=-0.012, bat_d_r_ab=-0.004, bat_d_obp=0.001, bat_d_iso=0.006 / surprise=-0.012
  - DeNA 2022 は「bat_d_r_runner < 0」を満たすのに「rank_rf >= 5」を満たさない。なぜか？ → H5, H6
- ほか 18 件（propositions.jsonl を参照）

## P165: 中日以外の B クラスのチームは、順位の高さの線に山がある（条件を「もし」に移した形）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 14 件: t-2012, db-2013, e-2014, e-2015, l-2016 ほか
- もし: `upper_half == False` ならば: `traj_rank_peak == True`
- 識別子: `[where:team!="d"] upper_half==false => traj_rank_peak==true`（指紋 `e2ccc4b6fbb0bf94`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 143
- 親: P98（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P98 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 66 | 52 | 0.79 [0.67, 0.87] | +4.68σ（0.000） | 0.76 | 1.03 | 0.320 | 0 | 支持 | 1 |
| 対偶 | 34 | 20 | 0.59 [0.42, 0.74] | +1.03σ（0.196） | 0.54 | 1.09 | 0.320 | 0 | 判断保留 | 4 |
| 逆 | 109 | 52 | 0.48 [0.39, 0.57] | -0.48σ（0.351） | 0.46 | 1.03 | 0.320 | 0 | 判断保留 | 4 |
| 裏 | 77 | 20 | 0.26 [0.17, 0.37] | -4.22σ（0.000） | 0.24 | 1.09 | 0.320 | 0 | 棄却 | 3 |

**異議あり（例外あり）** 元の命題に判例 14 件（対偶の判例も同じ）

- 阪神 2012: upper_half=False, traj_rank_peak=False, traj_rank_shape=fall, traj_rank_peak_base=0.765, traj_rank_end_slope=-0.447, rank=5
  - 阪神 2012 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- DeNA 2013: upper_half=False, traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.735, traj_rank_end_slope=+2.18, rank=5
  - DeNA 2013 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 楽天 2014: upper_half=False, traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.725, traj_rank_end_slope=+7.87, rank=6
  - 楽天 2014 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 楽天 2015: upper_half=False, traj_rank_peak=False, traj_rank_shape=fall, traj_rank_peak_base=0.665, traj_rank_end_slope=-7.49, rank=6
  - 楽天 2015 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 西武 2016: upper_half=False, traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.760, traj_rank_end_slope=+5.81, rank=4
  - 西武 2016 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- ヤクルト 2016: upper_half=False, traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.685, traj_rank_end_slope=+3.97, rank=5
  - ヤクルト 2016 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- ヤクルト 2017: upper_half=False, traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.520, traj_rank_end_slope=+1.68, rank=6
  - ヤクルト 2017 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 阪神 2018: upper_half=False, traj_rank_peak=False, traj_rank_shape=fall, traj_rank_peak_base=0.645, traj_rank_end_slope=-9.26, rank=6
  - 阪神 2018 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- ヤクルト 2019: upper_half=False, traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.680, traj_rank_end_slope=+1.45, rank=6
  - ヤクルト 2019 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- 広島 2021: upper_half=False, traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.795, traj_rank_end_slope=+9.13, rank=4
  - 広島 2021 は「upper_half == False」を満たすのに「traj_rank_peak == True」を満たさない。なぜか？ → H1, H6
- ほか 4 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 57 件（裏の判例も同じ）

- 巨人 2016: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.755, traj_rank_end_slope=-0.073, rank=2 / surprise=0.992
  - 巨人 2016 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ヤクルト 2015: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.790, traj_rank_end_slope=-2.75, rank=1 / surprise=0.951
  - ヤクルト 2015 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- オリックス 2023: upper_half=True, traj_rank_peak=True, traj_rank_shape=peak, traj_rank_peak_base=0.690, traj_rank_end_slope=-0.162, rank=1 / surprise=0.940
  - オリックス 2023 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- DeNA 2022: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.745, traj_rank_end_slope=-5.84, rank=2 / surprise=0.908
  - DeNA 2022 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ソフトバンク 2014: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.725, traj_rank_end_slope=-2.20, rank=1 / surprise=0.892
  - ソフトバンク 2014 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 日本ハム 2015: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.780, traj_rank_end_slope=-0.455, rank=2 / surprise=0.872
  - 日本ハム 2015 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 西武 2012: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.770, traj_rank_end_slope=-9.74, rank=2 / surprise=0.872
  - 西武 2012 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 広島 2023: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.765, traj_rank_end_slope=-5.03, rank=2 / surprise=0.856
  - 広島 2023 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ソフトバンク 2025: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.775, traj_rank_end_slope=-8.77, rank=1 / surprise=0.850
  - ソフトバンク 2025 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ヤクルト 2018: upper_half=True, traj_rank_peak=True, traj_rank_shape=valley-peak, traj_rank_peak_base=0.835, traj_rank_end_slope=-11.99, rank=2 / surprise=0.839
  - ヤクルト 2018 は「traj_rank_peak == True」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ほか 47 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- オリックス 2020: upper_half=False, traj_rank_peak=False, traj_rank_shape=valley, traj_rank_peak_base=0.645, traj_rank_end_slope=+1.45, rank=6
- 楽天 2020: upper_half=False, traj_rank_peak=False, traj_rank_shape=fall, traj_rank_peak_base=0.750, traj_rank_end_slope=-2.56, rank=4

## P166: 中日以外の B クラスのチームは、前半の線だけから当てた波の行き先が、もう4位以下（条件を「もし」に移した形）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 13 件: h-2013, db-2018, c-2022, f-2019, t-2018 ほか
- もし: `upper_half == False` ならば: `wave_limit_rank_h1 >= 3.5`
- 識別子: `[where:team!="d"] upper_half==false => wave_limit_rank_h1>=3.5`（指紋 `00685ca8c15a8121`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 143
- 親: P105（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P105 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 58 | 45 | 0.78 [0.65, 0.86] | +4.20σ（0.000） | 0.47 | 1.66 | 0.000 | 25 | 支持 | 1 |
| 対偶 | 63 | 50 | 0.79 [0.68, 0.88] | +4.66σ（0.000） | 0.51 | 1.56 | 0.000 | 25 | 支持 | 1 |
| 逆 | 55 | 45 | 0.82 [0.70, 0.90] | +4.72σ（0.000） | 0.49 | 1.66 | 0.000 | 25 | 支持 | 1 |
| 裏 | 60 | 50 | 0.83 [0.72, 0.91] | +5.16σ（0.000） | 0.53 | 1.56 | 0.000 | 25 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 13 件（対偶の判例も同じ）

- ソフトバンク 2013: upper_half=False, wave_limit_rank_h1=+3.46, wave_limit_rank=+3.50, course_rank_h1=3, rank=4 / surprise=+3.46
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- DeNA 2018: upper_half=False, wave_limit_rank_h1=+3.36, wave_limit_rank=+4.21, course_rank_h1=4, rank=4 / surprise=+3.36
  - DeNA 2018 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 広島 2022: upper_half=False, wave_limit_rank_h1=+3.16, wave_limit_rank=-, course_rank_h1=3, rank=5 / surprise=+3.16
  - 広島 2022 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 日本ハム 2019: upper_half=False, wave_limit_rank_h1=+3.13, wave_limit_rank=+5.65, course_rank_h1=3, rank=5 / surprise=+3.13
  - 日本ハム 2019 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 阪神 2018: upper_half=False, wave_limit_rank_h1=+2.99, wave_limit_rank=+5.09, course_rank_h1=2, rank=6 / surprise=+2.99
  - 阪神 2018 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 広島 2025: upper_half=False, wave_limit_rank_h1=+2.90, wave_limit_rank=+4.27, course_rank_h1=2, rank=5 / surprise=+2.90
  - 広島 2025 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 巨人 2022: upper_half=False, wave_limit_rank_h1=+1.90, wave_limit_rank=-, course_rank_h1=2, rank=4 / surprise=+1.90
  - 巨人 2022 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 楽天 2022: upper_half=False, wave_limit_rank_h1=+1.87, wave_limit_rank=+4.08, course_rank_h1=2, rank=4 / surprise=+1.87
  - 楽天 2022 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- DeNA 2015: upper_half=False, wave_limit_rank_h1=+1.84, wave_limit_rank=+5.34, course_rank_h1=3, rank=6 / surprise=+1.84
  - DeNA 2015 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 楽天 2016: upper_half=False, wave_limit_rank_h1=+1.43, wave_limit_rank=+4.36, course_rank_h1=5, rank=5 / surprise=+1.43
  - 楽天 2016 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- ほか 3 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 10 件（裏の判例も同じ）

- DeNA 2022: upper_half=True, wave_limit_rank_h1=+4.96, wave_limit_rank=+1.64, course_rank_h1=4, rank=2 / surprise=+4.96
  - DeNA 2022 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- DeNA 2019: upper_half=True, wave_limit_rank_h1=+4.59, wave_limit_rank=+2.62, course_rank_h1=4, rank=2 / surprise=+4.59
  - DeNA 2019 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ロッテ 2015: upper_half=True, wave_limit_rank_h1=+4.22, wave_limit_rank=+3.57, course_rank_h1=4, rank=3 / surprise=+4.22
  - ロッテ 2015 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ヤクルト 2018: upper_half=True, wave_limit_rank_h1=+4.08, wave_limit_rank=+2.30, course_rank_h1=2, rank=2 / surprise=+4.08
  - ヤクルト 2018 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ソフトバンク 2012: upper_half=True, wave_limit_rank_h1=+4.03, wave_limit_rank=+2.16, course_rank_h1=5, rank=3 / surprise=+4.03
  - ソフトバンク 2012 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 阪神 2014: upper_half=True, wave_limit_rank_h1=+3.97, wave_limit_rank=+2.67, course_rank_h1=4, rank=2 / surprise=+3.97
  - 阪神 2014 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ヤクルト 2015: upper_half=True, wave_limit_rank_h1=+3.83, wave_limit_rank=-, course_rank_h1=4, rank=1 / surprise=+3.83
  - ヤクルト 2015 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 広島 2013: upper_half=True, wave_limit_rank_h1=+3.80, wave_limit_rank=+3.21, course_rank_h1=3, rank=3 / surprise=+3.80
  - 広島 2013 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ソフトバンク 2025: upper_half=True, wave_limit_rank_h1=+3.65, wave_limit_rank=0.771, course_rank_h1=3, rank=1 / surprise=+3.65
  - ソフトバンク 2025 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 西武 2019: upper_half=True, wave_limit_rank_h1=+3.59, wave_limit_rank=+1.67, course_rank_h1=4, rank=1 / surprise=+3.59
  - 西武 2019 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6

## P167: 中日以外で、得点の不足が誤差を超え（得点 −1）、失点の優位が誤差の内側（失点 0）なら、B クラス（条件を「もし」に移した形）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: g-2016
- もし: `rf_zone_se == -1 かつ ra_zone_se == 0` ならば: `upper_half == False`
- 識別子: `[where:team!="d"] ra_zone_se==0 & rf_zone_se==-1 => upper_half==false`（指紋 `453bbd9f46af68ad`）
- 兄弟（範囲と結論が同じ、条件が違う）: P65
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'team', 'op': '!=', 'value': 'd'}]} / 単位数: 143
- 親: P141（変更: 範囲（where）に書いていた条件を「もし」に移し、逆・裏を見られるようにした。元の命題の単位は親と同じ）
- 注記: R41。親 P141 の元の命題・判例と同じ。読むのは逆・裏
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 17 | 16 | 0.94 [0.73, 0.99] | +1.82σ（0.050） | 0.46 | 2.04 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 77 | 76 | 0.99 [0.93, 1.00] | +4.80σ（0.000） | 0.88 | 1.12 | 0.000 | 0 | 支持 | 1 |
| 逆 | 66 | 16 | 0.24 [0.16, 0.36] | -9.52σ（0.000） | 0.12 | 2.04 | 0.000 | 0 | 修正 | 2 |
| 裏 | 126 | 76 | 0.60 [0.52, 0.68] | -3.81σ（0.000） | 0.54 | 1.12 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 巨人 2016: rf_zone_se=-1, ra_zone_se=0, upper_half=True, rank=2, rf_adv=-0.365, ra_adv=0.256, rank_ra=2, rank_rf=4 / surprise=-0.109
  - 巨人 2016 は「rf_zone_se == -1 かつ ra_zone_se == 0」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 50 件（裏の判例も同じ）

- ヤクルト 2017: rf_zone_se=-1, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=-0.811, ra_adv=-0.660, rank_ra=6, rank_rf=6 / surprise=-1.47
  - ヤクルト 2017 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- ロッテ 2017: rf_zone_se=-1, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=-0.792, ra_adv=-0.657, rank_ra=6, rank_rf=6 / surprise=-1.45
  - ロッテ 2017 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- 楽天 2015: rf_zone_se=-1, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=-0.926, ra_adv=-0.425, rank_ra=6, rank_rf=6 / surprise=-1.35
  - 楽天 2015 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- オリックス 2016: rf_zone_se=-1, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=-0.709, ra_adv=-0.524, rank_ra=5, rank_rf=6 / surprise=-1.23
  - オリックス 2016 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- DeNA 2012: rf_zone_se=-1, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=-0.256, ra_adv=-0.958, rank_ra=6, rank_rf=5 / surprise=-1.21
  - DeNA 2012 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- 楽天 2016: rf_zone_se=-1, ra_zone_se=-1, upper_half=False, rank=5, rf_adv=-0.331, ra_adv=-0.684, rank_ra=6, rank_rf=5 / surprise=-1.02
  - 楽天 2016 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- ロッテ 2025: rf_zone_se=-1, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=-0.352, ra_adv=-0.639, rank_ra=6, rank_rf=5 / surprise=-0.992
  - ロッテ 2025 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- ヤクルト 2025: rf_zone_se=0, ra_zone_se=-1, upper_half=False, rank=6, rf_adv=-0.137, ra_adv=-0.827, rank_ra=6, rank_rf=4 / surprise=-0.964
  - ヤクルト 2025 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- ロッテ 2014: rf_zone_se=0, ra_zone_se=-1, upper_half=False, rank=4, rf_adv=-0.176, ra_adv=-0.621, rank_ra=6, rank_rf=5 / surprise=-0.797
  - ロッテ 2014 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- ヤクルト 2016: rf_zone_se=1, ra_zone_se=-1, upper_half=False, rank=5, rf_adv=0.264, ra_adv=-1.01, rank_ra=6, rank_rf=2 / surprise=-0.747
  - ヤクルト 2016 は「upper_half == False」を満たすのに「rf_zone_se == -1 かつ ra_zone_se == 0」を満たさない。なぜか？ → H2
- ほか 40 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- ロッテ 2020: rf_zone_se=-1, ra_zone_se=0, upper_half=True, rank=2, rf_adv=-0.328, ra_adv=0.148, rank_ra=2, rank_rf=5

## P168: B クラスなら、前半の線だけから当てた波の行き先が、もう4位以下（中日を含む全体）

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 13 件: h-2013, db-2018, c-2022, f-2019, t-2018 ほか
- もし: `upper_half == False` ならば: `wave_limit_rank_h1 >= 3.5`
- 識別子: `[all] upper_half==false => wave_limit_rank_h1>=3.5`（指紋 `86f06a2ce2abff99`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 親: P166（変更: 範囲から「中日以外」を外し、中日を含めた全体で4つの形を見る）
- 見直す条件（反証）: B クラスの単位の半分以下しか、前半の行き先が4位以下にならない
- 注記: 減衰しない波が選ばれた年は行き先が空で、判定できない単位（exit 5 の対象）として数える
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 64 | 51 | 0.80 [0.68, 0.88] | +4.75σ（0.000） | 0.50 | 1.61 | 0.000 | 31 | 支持 | 1 |
| 対偶 | 63 | 50 | 0.79 [0.68, 0.88] | +4.66σ（0.000） | 0.49 | 1.63 | 0.000 | 31 | 支持 | 1 |
| 逆 | 62 | 51 | 0.82 [0.71, 0.90] | +5.08σ（0.000） | 0.51 | 1.61 | 0.000 | 31 | 支持 | 1 |
| 裏 | 61 | 50 | 0.82 [0.71, 0.90] | +4.99σ（0.000） | 0.50 | 1.63 | 0.000 | 31 | 支持 | 1 |

**異議あり（例外あり）** 元の命題に判例 13 件（対偶の判例も同じ）

- ソフトバンク 2013: upper_half=False, wave_limit_rank_h1=+3.46, wave_limit_rank=+3.50, course_rank_h1=3, rank=4 / surprise=+3.46
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- DeNA 2018: upper_half=False, wave_limit_rank_h1=+3.36, wave_limit_rank=+4.21, course_rank_h1=4, rank=4 / surprise=+3.36
  - DeNA 2018 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 広島 2022: upper_half=False, wave_limit_rank_h1=+3.16, wave_limit_rank=-, course_rank_h1=3, rank=5 / surprise=+3.16
  - 広島 2022 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 日本ハム 2019: upper_half=False, wave_limit_rank_h1=+3.13, wave_limit_rank=+5.65, course_rank_h1=3, rank=5 / surprise=+3.13
  - 日本ハム 2019 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 阪神 2018: upper_half=False, wave_limit_rank_h1=+2.99, wave_limit_rank=+5.09, course_rank_h1=2, rank=6 / surprise=+2.99
  - 阪神 2018 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 広島 2025: upper_half=False, wave_limit_rank_h1=+2.90, wave_limit_rank=+4.27, course_rank_h1=2, rank=5 / surprise=+2.90
  - 広島 2025 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 巨人 2022: upper_half=False, wave_limit_rank_h1=+1.90, wave_limit_rank=-, course_rank_h1=2, rank=4 / surprise=+1.90
  - 巨人 2022 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 楽天 2022: upper_half=False, wave_limit_rank_h1=+1.87, wave_limit_rank=+4.08, course_rank_h1=2, rank=4 / surprise=+1.87
  - 楽天 2022 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- DeNA 2015: upper_half=False, wave_limit_rank_h1=+1.84, wave_limit_rank=+5.34, course_rank_h1=3, rank=6 / surprise=+1.84
  - DeNA 2015 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- 楽天 2016: upper_half=False, wave_limit_rank_h1=+1.43, wave_limit_rank=+4.36, course_rank_h1=5, rank=5 / surprise=+1.43
  - 楽天 2016 は「upper_half == False」を満たすのに「wave_limit_rank_h1 >= 3.5」を満たさない。なぜか？ → H1, H6
- ほか 3 件（propositions.jsonl を参照）

**異議あり（例外あり）** 逆に判例 11 件（裏の判例も同じ）

- DeNA 2022: upper_half=True, wave_limit_rank_h1=+4.96, wave_limit_rank=+1.64, course_rank_h1=4, rank=2 / surprise=+4.96
  - DeNA 2022 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- DeNA 2019: upper_half=True, wave_limit_rank_h1=+4.59, wave_limit_rank=+2.62, course_rank_h1=4, rank=2 / surprise=+4.59
  - DeNA 2019 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ロッテ 2015: upper_half=True, wave_limit_rank_h1=+4.22, wave_limit_rank=+3.57, course_rank_h1=4, rank=3 / surprise=+4.22
  - ロッテ 2015 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ヤクルト 2018: upper_half=True, wave_limit_rank_h1=+4.08, wave_limit_rank=+2.30, course_rank_h1=2, rank=2 / surprise=+4.08
  - ヤクルト 2018 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ソフトバンク 2012: upper_half=True, wave_limit_rank_h1=+4.03, wave_limit_rank=+2.16, course_rank_h1=5, rank=3 / surprise=+4.03
  - ソフトバンク 2012 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 阪神 2014: upper_half=True, wave_limit_rank_h1=+3.97, wave_limit_rank=+2.67, course_rank_h1=4, rank=2 / surprise=+3.97
  - 阪神 2014 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 中日 2012 **(focus)**: upper_half=True, wave_limit_rank_h1=+3.86, wave_limit_rank=+1.85, course_rank_h1=2, rank=2 / surprise=+3.86
  - 中日 2012 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ヤクルト 2015: upper_half=True, wave_limit_rank_h1=+3.83, wave_limit_rank=-, course_rank_h1=4, rank=1 / surprise=+3.83
  - ヤクルト 2015 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- 広島 2013: upper_half=True, wave_limit_rank_h1=+3.80, wave_limit_rank=+3.21, course_rank_h1=3, rank=3 / surprise=+3.80
  - 広島 2013 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ソフトバンク 2025: upper_half=True, wave_limit_rank_h1=+3.65, wave_limit_rank=0.771, course_rank_h1=3, rank=1 / surprise=+3.65
  - ソフトバンク 2025 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6
- ほか 1 件（propositions.jsonl を参照）

## P169: 中日は、B クラスの年なら、前半の線だけから当てた波の行き先が、もう4位以下

- **判定: exit 4 待った！判断保留** — 元の命題: n=6（min_n=10）、成立率の区間 0.61〜1.00
- もし: `upper_half == False` ならば: `wave_limit_rank_h1 >= 3.5`
- 識別子: `[team=d] upper_half==false => wave_limit_rank_h1>=3.5`（指紋 `ae1cdf9893b1d675`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'team': 'd'} / 単位数: 13
- 親: P104（変更: 範囲の「B クラス」を「もし」に移し、中日だけで逆・裏を見られるようにした（R41 と同じ立て直し））
- 見直す条件（反証）: 中日の B の年の半分以下しか、前半の行き先が4位以下にならない
- 注記: 中日の A は 2012年だけなので、対偶・裏は単位が少ない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 6 | 6 | 1.00 [0.61, 1.00] | +2.45σ（0.016） | 1.00 | 1.00 | 1.000 | 6 | 判断保留 | 4 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.14 | - | 1.000 | 6 | 判断保留 | 4 |
| 逆 | 7 | 6 | 0.86 [0.49, 0.97] | +1.89σ（0.062） | 0.86 | 1.00 | 1.000 | 6 | 判断保留 | 4 |
| 裏 | 1 | 0 | 0.00 [0.00, 0.79] | -1.00σ（0.500） | 0.00 | - | 1.000 | 6 | 判断保留 | 4 |

**待った！判断保留** 逆に判例 1 件（裏の判例も同じ）

- 中日 2012 **(focus)**: upper_half=True, wave_limit_rank_h1=+3.86, wave_limit_rank=+1.85, course_rank_h1=2, rank=2 / surprise=+3.86
  - 中日 2012 は「wave_limit_rank_h1 >= 3.5」を満たすのに「upper_half == False」を満たさない。なぜか？ → H1, H6

## P170: 前半の順位より3つ以上下で終わった（course_fade ≥ 3）なら、後半の失点が前半より（他球団と比べて）増えている

- **判定: exit 4 待った！判断保留** — 元の命題: n=7（min_n=10）、成立率の区間 0.65〜1.00
- もし: `course_fade >= 3` ならば: `course_ra_d > 0`
- 識別子: `[all] course_fade>=3 => course_ra_d>0`（指紋 `5ecbe48ab694b91b`）
- 兄弟（範囲と結論が同じ、条件が違う）: P91, P93
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 大きく落ちた単位の半分以下しか、後半の失点が増えていない
- 注記: 開いた問い5（投手の負担は後半に効くか）の、投手の記録なしでできる部分。P171（得点の側）と率を比べる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 7 | 7 | 1.00 [0.65, 1.00] | +2.65σ（0.008） | 0.51 | 1.97 | 0.007 | 0 | 判断保留 | 4 |
| 対偶 | 77 | 77 | 1.00 [0.95, 1.00] | +8.77σ（0.000） | 0.96 | 1.05 | 0.007 | 0 | 支持 | 0 |
| 逆 | 79 | 7 | 0.09 [0.04, 0.17] | -7.31σ（0.000） | 0.04 | 1.97 | 0.007 | 0 | 修正 | 2 |
| 裏 | 149 | 77 | 0.52 [0.44, 0.60] | +0.41σ（0.372） | 0.49 | 1.05 | 0.007 | 0 | 判断保留 | 4 |

**異議あり（主張が強すぎる）** 逆に判例 72 件（裏の判例も同じ）

- DeNA 2016: course_fade=0, course_ra_d=+1.41, rank=3, course_rank_h1=3, course_rf_d=0.902, half2_vs_pythag=+2.81 / surprise=+1.41
  - DeNA 2016 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- ヤクルト 2022: course_fade=0, course_ra_d=+1.28, rank=1, course_rank_h1=1, course_rf_d=-0.440, half2_vs_pythag=0.535 / surprise=+1.28
  - ヤクルト 2022 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 西武 2025: course_fade=1, course_ra_d=+1.03, rank=5, course_rank_h1=4, course_rf_d=-0.087, half2_vs_pythag=-1.52 / surprise=+1.03
  - 西武 2025 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 巨人 2021: course_fade=1, course_ra_d=+1.02, rank=3, course_rank_h1=2, course_rf_d=-0.569, half2_vs_pythag=-2.26 / surprise=+1.02
  - 巨人 2021 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 楽天 2015: course_fade=1, course_ra_d=0.979, rank=6, course_rank_h1=5, course_rf_d=0.136, half2_vs_pythag=0.308 / surprise=0.979
  - 楽天 2015 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 巨人 2013: course_fade=0, course_ra_d=0.942, rank=1, course_rank_h1=1, course_rf_d=-0.239, half2_vs_pythag=+5.12 / surprise=0.942
  - 巨人 2013 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- ロッテ 2018: course_fade=2, course_ra_d=0.925, rank=5, course_rank_h1=3, course_rf_d=-0.746, half2_vs_pythag=-2.15 / surprise=0.925
  - ロッテ 2018 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 西武 2013: course_fade=-1, course_ra_d=0.833, rank=2, course_rank_h1=3, course_rf_d=0.147, half2_vs_pythag=+5.93 / surprise=0.833
  - 西武 2013 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 楽天 2022: course_fade=2, course_ra_d=0.805, rank=4, course_rank_h1=2, course_rf_d=0.365, half2_vs_pythag=-3.05 / surprise=0.805
  - 楽天 2022 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- オリックス 2019: course_fade=0, course_ra_d=0.794, rank=6, course_rank_h1=6, course_rf_d=0.915, half2_vs_pythag=0.507 / surprise=0.794
  - オリックス 2019 は「course_ra_d > 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- ほか 62 件（propositions.jsonl を参照）

## P171: 前半の順位より3つ以上下で終わったなら、後半の得点が前半より（他球団と比べて）減っている

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 1 件: t-2018
- もし: `course_fade >= 3` ならば: `course_rf_d < 0`
- 識別子: `[all] course_fade>=3 => course_rf_d<0`（指紋 `8f520edd17b2c2f2`）
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 大きく落ちた単位の半分以下しか、後半の得点が減っていない
- 注記: P170 の鏡（得点の側）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 7 | 6 | 0.86 [0.49, 0.97] | +1.89σ（0.062） | 0.46 | 1.88 | 0.035 | 0 | 判断保留 | 4 |
| 対偶 | 85 | 84 | 0.99 [0.94, 1.00] | +9.00σ（0.000） | 0.96 | 1.03 | 0.035 | 0 | 支持 | 1 |
| 逆 | 71 | 6 | 0.08 [0.04, 0.17] | -7.00σ（0.000） | 0.04 | 1.88 | 0.035 | 0 | 修正 | 2 |
| 裏 | 149 | 84 | 0.56 [0.48, 0.64] | +1.56σ（0.070） | 0.54 | 1.03 | 0.035 | 0 | 判断保留 | 4 |

**待った！判断保留** 元の命題に判例 1 件（対偶の判例も同じ）

- 阪神 2018: course_fade=4, course_rf_d=0.249, rank=6, course_rank_h1=2, course_ra_d=0.524, half2_vs_pythag=-4.87 / surprise=0.249
  - 阪神 2018 は「course_fade >= 3」を満たすのに「course_rf_d < 0」を満たさない。なぜか？ → H6

**異議あり（主張が強すぎる）** 逆に判例 65 件（裏の判例も同じ）

- 楽天 2017: course_fade=2, course_rf_d=-1.52, rank=3, course_rank_h1=1, course_ra_d=0.480, half2_vs_pythag=0.142 / surprise=-1.52
  - 楽天 2017 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 広島 2015: course_fade=0, course_rf_d=-1.19, rank=4, course_rank_h1=4, course_ra_d=-0.345, half2_vs_pythag=+1.86 / surprise=-1.19
  - 広島 2015 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- ソフトバンク 2014: course_fade=-1, course_rf_d=-0.975, rank=1, course_rank_h1=2, course_ra_d=0.281, half2_vs_pythag=+1.61 / surprise=-0.975
  - ソフトバンク 2014 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 阪神 2021: course_fade=1, course_rf_d=-0.954, rank=2, course_rank_h1=1, course_ra_d=0.499, half2_vs_pythag=+4.02 / surprise=-0.954
  - 阪神 2021 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- ロッテ 2016: course_fade=1, course_rf_d=-0.848, rank=3, course_rank_h1=2, course_ra_d=0.662, half2_vs_pythag=+1.46 / surprise=-0.848
  - ロッテ 2016 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- オリックス 2025: course_fade=1, course_rf_d=-0.836, rank=3, course_rank_h1=2, course_ra_d=-0.248, half2_vs_pythag=+2.71 / surprise=-0.836
  - オリックス 2025 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- オリックス 2023: course_fade=0, course_rf_d=-0.799, rank=1, course_rank_h1=1, course_ra_d=-0.378, half2_vs_pythag=+5.96 / surprise=-0.799
  - オリックス 2023 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- ヤクルト 2016: course_fade=-1, course_rf_d=-0.779, rank=5, course_rank_h1=6, course_ra_d=-0.515, half2_vs_pythag=+3.68 / surprise=-0.779
  - ヤクルト 2016 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- 楽天 2019: course_fade=2, course_rf_d=-0.772, rank=3, course_rank_h1=1, course_ra_d=-0.693, half2_vs_pythag=-4.11 / surprise=-0.772
  - 楽天 2019 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- ロッテ 2018: course_fade=2, course_rf_d=-0.746, rank=5, course_rank_h1=3, course_ra_d=0.925, half2_vs_pythag=-2.15 / surprise=-0.746
  - ロッテ 2018 は「course_rf_d < 0」を満たすのに「course_fade >= 3」を満たさない。なぜか？ → H6
- ほか 55 件（propositions.jsonl を参照）

## P172: 得点した回の大きさがリーグ上位2位以内で、失点がはっきり劣ってはいない（失点の区分 ≥ 0）なら、A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 7 件: c-2022, l-2015, e-2022, h-2021, f-2019 ほか
- もし: `inn_size_rank >= 5 かつ ra_zone_se >= 0` ならば: `upper_half == True`
- 識別子: `[seasons=2013-2025] inn_size_rank>=5 & ra_zone_se>=0 => upper_half==true`（指紋 `e033fbafbc7acc20`）
- 兄弟（範囲と結論が同じ、条件が違う）: P116
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 親: P116（変更: R27 の種: P116 の判例（大きさは上位なのに B）の多くは得点も上位だった。失点がはっきり劣る単位を除く条件を足す）
- 見直す条件（反証）: この条件の単位の4分の1を超えて B クラス
- 注記: P173 と並べる。P116 は 0.69
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 37 | 30 | 0.81 [0.66, 0.91] | +0.85σ（0.259） | 0.50 | 1.62 | 0.000 | 0 | 判断保留 | 4 |
| 対偶 | 72 | 65 | 0.90 [0.81, 0.95] | +2.99σ（0.001） | 0.74 | 1.21 | 0.000 | 0 | 支持 | 1 |
| 逆 | 72 | 30 | 0.42 [0.31, 0.53] | -6.53σ（0.000） | 0.26 | 1.62 | 0.000 | 0 | 修正 | 2 |
| 裏 | 107 | 65 | 0.61 [0.51, 0.69] | -3.40σ（0.001） | 0.50 | 1.21 | 0.000 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 7 件（対偶の判例も同じ）

- 広島 2022: inn_size_rank=6, ra_zone_se=0, upper_half=False, rank=5, ra_adv_t=-0.611, rank_rf=2 / surprise=0.103
  - 広島 2022 は「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 西武 2015: inn_size_rank=6, ra_zone_se=0, upper_half=False, rank=4, ra_adv_t=-0.352, rank_rf=2 / surprise=0.066
  - 西武 2015 は「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 楽天 2022: inn_size_rank=6, ra_zone_se=0, upper_half=False, rank=4, ra_adv_t=-0.939, rank_rf=2 / surprise=0.063
  - 楽天 2022 は「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- ソフトバンク 2021: inn_size_rank=6, ra_zone_se=1, upper_half=False, rank=4, ra_adv_t=+1.22, rank_rf=2 / surprise=0.044
  - ソフトバンク 2021 は「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 日本ハム 2019: inn_size_rank=5, ra_zone_se=0, upper_half=False, rank=5, ra_adv_t=0.800, rank_rf=5 / surprise=0.031
  - 日本ハム 2019 は「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- ソフトバンク 2013: inn_size_rank=5, ra_zone_se=0, upper_half=False, rank=4, ra_adv_t=0.032, rank_rf=1 / surprise=0.026
  - ソフトバンク 2013 は「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5
- 広島 2015: inn_size_rank=5, ra_zone_se=1, upper_half=False, rank=4, ra_adv_t=+1.39, rank_rf=3 / surprise=0.003
  - 広島 2015 は「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H5

**異議あり（主張が強すぎる）** 逆に判例 42 件（裏の判例も同じ）

- 西武 2018: inn_size_rank=6, ra_zone_se=-1, upper_half=True, rank=1, ra_adv_t=-1.56, rank_rf=1 / surprise=0.136
  - 西武 2018 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- 西武 2019: inn_size_rank=6, ra_zone_se=-1, upper_half=True, rank=1, ra_adv_t=-2.34, rank_rf=1 / surprise=0.109
  - 西武 2019 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- ソフトバンク 2019: inn_size_rank=1, ra_zone_se=1, upper_half=True, rank=2, ra_adv_t=+1.53, rank_rf=4 / surprise=-0.103
  - ソフトバンク 2019 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- オリックス 2025: inn_size_rank=6, ra_zone_se=-1, upper_half=True, rank=3, ra_adv_t=-1.34, rank_rf=3 / surprise=0.091
  - オリックス 2025 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- オリックス 2022: inn_size_rank=1, ra_zone_se=1, upper_half=True, rank=1, ra_adv_t=+1.28, rank_rf=4 / surprise=-0.079
  - オリックス 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- DeNA 2022: inn_size_rank=2, ra_zone_se=0, upper_half=True, rank=2, ra_adv_t=-0.223, rank_rf=4 / surprise=-0.067
  - DeNA 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- ロッテ 2023: inn_size_rank=2, ra_zone_se=-1, upper_half=True, rank=2, ra_adv_t=-1.00, rank_rf=4 / surprise=-0.054
  - ロッテ 2023 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- 巨人 2016: inn_size_rank=1, ra_zone_se=0, upper_half=True, rank=2, ra_adv_t=0.970, rank_rf=4 / surprise=-0.050
  - 巨人 2016 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- 西武 2022: inn_size_rank=2, ra_zone_se=1, upper_half=True, rank=3, ra_adv_t=+1.81, rank_rf=5 / surprise=-0.045
  - 西武 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- ヤクルト 2022: inn_size_rank=4, ra_zone_se=-1, upper_half=True, rank=1, ra_adv_t=-1.14, rank_rf=1 / surprise=0.039
  - ヤクルト 2022 は「upper_half == True」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se >= 0」を満たさない。なぜか？ → H5
- ほか 32 件（propositions.jsonl を参照）

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: inn_size_rank=6, ra_zone_se=0, upper_half=False, rank=4, ra_adv_t=-0.940, rank_rf=1

## P173: 得点した回の大きさがリーグ上位2位以内でも、失点がはっきり劣る（失点 −1）なら、B クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 3 件: l-2019, l-2018, b-2025
- もし: `inn_size_rank >= 5 かつ ra_zone_se == -1` ならば: `upper_half == False`
- 識別子: `[seasons=2013-2025] inn_size_rank>=5 & ra_zone_se==-1 => upper_half==false`（指紋 `849b2b03b6af386b`）
- 兄弟（範囲と結論が同じ、条件が違う）: P62, P117
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'seasons': '2013-2025'} / 単位数: 144
- 見直す条件（反証）: この条件の単位の4分の1を超えて A クラス
- 注記: P172 の裏の側を、命題として立てたもの
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 11 | 8 | 0.73 [0.43, 0.90] | -0.17σ（0.545） | 0.50 | 1.45 | 0.104 | 0 | 判断保留 | 4 |
| 対偶 | 72 | 69 | 0.96 [0.88, 0.99] | +4.08σ（0.000） | 0.92 | 1.04 | 0.104 | 0 | 支持 | 1 |
| 逆 | 72 | 8 | 0.11 [0.06, 0.20] | -12.52σ（0.000） | 0.08 | 1.45 | 0.104 | 0 | 棄却 | 3 |
| 裏 | 133 | 69 | 0.52 [0.43, 0.60] | -6.16σ（0.000） | 0.50 | 1.04 | 0.104 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 3 件（対偶の判例も同じ）

- 西武 2019: inn_size_rank=6, ra_zone_se=-1, upper_half=True, rank=1, inn_dlog_size=0.109, rank_rf=1 / surprise=-2.34
  - 西武 2019 は「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- 西武 2018: inn_size_rank=6, ra_zone_se=-1, upper_half=True, rank=1, inn_dlog_size=0.136, rank_rf=1 / surprise=-1.56
  - 西武 2018 は「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5
- オリックス 2025: inn_size_rank=6, ra_zone_se=-1, upper_half=True, rank=3, inn_dlog_size=0.091, rank_rf=3 / surprise=-1.34
  - オリックス 2025 は「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H5

**異議あり（不成立）** 逆に判例 64 件（裏の判例も同じ）

- ヤクルト 2024: inn_size_rank=2, ra_zone_se=-1, upper_half=False, rank=5, inn_dlog_size=-0.057, rank_rf=2 / surprise=-3.42
  - ヤクルト 2024 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- ヤクルト 2025: inn_size_rank=2, ra_zone_se=-1, upper_half=False, rank=6, inn_dlog_size=-0.041, rank_rf=4 / surprise=-3.34
  - ヤクルト 2025 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- DeNA 2015: inn_size_rank=3, ra_zone_se=-1, upper_half=False, rank=6, inn_dlog_size=-0.012, rank_rf=2 / surprise=-2.82
  - DeNA 2015 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- 楽天 2024: inn_size_rank=4, ra_zone_se=-1, upper_half=False, rank=4, inn_dlog_size=0.008, rank_rf=4 / surprise=-2.76
  - 楽天 2024 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- ヤクルト 2014: inn_size_rank=2, ra_zone_se=-1, upper_half=False, rank=6, inn_dlog_size=-0.020, rank_rf=1 / surprise=-2.71
  - ヤクルト 2014 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- ヤクルト 2013: inn_size_rank=2, ra_zone_se=-1, upper_half=False, rank=6, inn_dlog_size=-0.021, rank_rf=3 / surprise=-2.64
  - ヤクルト 2013 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- ロッテ 2025: inn_size_rank=4, ra_zone_se=-1, upper_half=False, rank=6, inn_dlog_size=0.018, rank_rf=5 / surprise=-2.53
  - ロッテ 2025 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- ヤクルト 2017: inn_size_rank=2, ra_zone_se=-1, upper_half=False, rank=6, inn_dlog_size=-0.014, rank_rf=6 / surprise=-2.46
  - ヤクルト 2017 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- ロッテ 2017: inn_size_rank=1, ra_zone_se=-1, upper_half=False, rank=6, inn_dlog_size=-0.060, rank_rf=6 / surprise=-2.27
  - ロッテ 2017 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- 中日 2021 **(focus)**: inn_size_rank=1, ra_zone_se=1, upper_half=False, rank=5, inn_dlog_size=-0.136, rank_rf=6 / surprise=+2.22
  - 中日 2021 は「upper_half == False」を満たすのに「inn_size_rank >= 5 かつ ra_zone_se == -1」を満たさない。なぜか？ → H5
- ほか 54 件（propositions.jsonl を参照）

## P174: 1位が抜けた年（1位と2位の勝率差 .050 以上）の B クラスは、どの道筋にも当たらない

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 34 件: d-2016, s-2016, t-2016, e-2023, f-2023 ほか
- もし: `lg_lead_gap >= 0.05` ならば: `b_paths == none`
- 識別子: `[where:upper_half==false] lg_lead_gap>=0.05 => b_paths=="none"`（指紋 `57858164f3675fcf`）
- 兄弟（範囲と結論が同じ、条件が違う）: P175
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 78
- 見直す条件（反証）: （P175 と率を比べるための命題。率そのものは低い見込み）
- 注記: 読むのは率の比べ（P175 との差）と、逆（道筋のない B なら1位が抜けた年）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 36 | 2 | 0.06 [0.02, 0.18] | -5.33σ（0.000） | 0.05 | 1.08 | 0.632 | 0 | 棄却 | 3 |
| 対偶 | 74 | 40 | 0.54 [0.43, 0.65] | +0.70σ（0.281） | 0.54 | 1.00 | 0.632 | 0 | 判断保留 | 4 |
| 逆 | 4 | 2 | 0.50 [0.15, 0.85] | +0.00σ（0.688） | 0.46 | 1.08 | 0.632 | 0 | 判断保留 | 4 |
| 裏 | 42 | 40 | 0.95 [0.84, 0.99] | +5.86σ（0.000） | 0.95 | 1.00 | 0.632 | 0 | 支持 | 1 |

**異議あり（不成立）** 元の命題に判例 34 件（対偶の判例も同じ）

- 中日 2016 **(focus)**: lg_lead_gap=0.124, b_paths=offense+convert+collapse, rank=6, league=C, lg_gap34=0.036, lg_rest_sd=0.037 / surprise=0.124
  - 中日 2016 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ヤクルト 2016: lg_lead_gap=0.124, b_paths=defense, rank=5, league=C, lg_gap34=0.036, lg_rest_sd=0.037 / surprise=0.124
  - ヤクルト 2016 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 阪神 2016: lg_lead_gap=0.124, b_paths=offense, rank=4, league=C, lg_gap34=0.036, lg_rest_sd=0.037 / surprise=0.124
  - 阪神 2016 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 楽天 2023: lg_lead_gap=0.111, b_paths=defense, rank=4, league=P, lg_gap34=0.011, lg_rest_sd=0.037 / surprise=0.111
  - 楽天 2023 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 日本ハム 2023: lg_lead_gap=0.111, b_paths=offense+convert, rank=6, league=P, lg_gap34=0.011, lg_rest_sd=0.037 / surprise=0.111
  - 日本ハム 2023 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 西武 2023: lg_lead_gap=0.111, b_paths=offense+convert, rank=5, league=P, lg_gap34=0.011, lg_rest_sd=0.037 / surprise=0.111
  - 西武 2023 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- オリックス 2024: lg_lead_gap=0.094, b_paths=offense+convert, rank=5, league=P, lg_gap34=0.036, lg_rest_sd=0.078 / surprise=0.094
  - オリックス 2024 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 楽天 2024: lg_lead_gap=0.094, b_paths=defense, rank=4, league=P, lg_gap34=0.036, lg_rest_sd=0.078 / surprise=0.094
  - 楽天 2024 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 西武 2024: lg_lead_gap=0.094, b_paths=offense+convert, rank=6, league=P, lg_gap34=0.036, lg_rest_sd=0.078 / surprise=0.094
  - 西武 2024 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 広島 2025: lg_lead_gap=0.093, b_paths=defense+convert, rank=5, league=C, lg_gap34=0.057, lg_rest_sd=0.045 / surprise=0.093
  - 広島 2025 は「lg_lead_gap >= 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ほか 24 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 2 件（裏の判例も同じ）

- 中日 2018 **(focus)**: lg_lead_gap=0.050, b_paths=none, rank=5, league=C, lg_gap34=0.010, lg_rest_sd=0.037 / surprise=0.050
  - 中日 2018 は「b_paths == none」を満たすのに「lg_lead_gap >= 0.05」を満たさない。なぜか？ → H1
- 広島 2019: lg_lead_gap=0.039, b_paths=none, rank=4, league=C, lg_gap34=0.004, lg_rest_sd=0.037 / surprise=0.039
  - 広島 2019 は「b_paths == none」を満たすのに「lg_lead_gap >= 0.05」を満たさない。なぜか？ → H1

**除外中の判例**（統計からは除いたが、判例としては残す）

- オリックス 2020: lg_lead_gap=0.122, b_paths=offense+convert, rank=6, league=P, lg_gap34=0.009, lg_rest_sd=0.046
- 楽天 2020: lg_lead_gap=0.122, b_paths=convert, rank=4, league=P, lg_gap34=0.009, lg_rest_sd=0.046
- 日本ハム 2020: lg_lead_gap=0.122, b_paths=defense, rank=5, league=P, lg_gap34=0.009, lg_rest_sd=0.046
- 広島 2020: lg_lead_gap=0.067, b_paths=defense, rank=5, league=C, lg_gap34=0.031, lg_rest_sd=0.063
- DeNA 2020: lg_lead_gap=0.067, b_paths=convert, rank=4, league=C, lg_gap34=0.031, lg_rest_sd=0.063
- ヤクルト 2020: lg_lead_gap=0.067, b_paths=defense+convert, rank=6, league=C, lg_gap34=0.031, lg_rest_sd=0.063

## P175: 1位が抜けていない年（1位と2位の勝率差 .050 未満）の B クラスは、どの道筋にも当たらない

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 40 件: db-2018, t-2018, d-2014, db-2014, s-2014 ほか
- もし: `lg_lead_gap < 0.05` ならば: `b_paths == none`
- 識別子: `[where:upper_half==false] lg_lead_gap<0.05 => b_paths=="none"`（指紋 `31781ca690a48ade`）
- 兄弟（範囲と結論が同じ、条件が違う）: P174
- 強さ: 多くの場合（more_often_than_not, 基準 0.50）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 78
- 見直す条件（反証）: （P174 と率を比べるための命題）
- 注記: P174 の比べる相手
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 42 | 2 | 0.05 [0.01, 0.16] | -5.86σ（0.000） | 0.05 | 0.93 | 0.748 | 0 | 棄却 | 3 |
| 対偶 | 74 | 34 | 0.46 [0.35, 0.57] | -0.70σ（0.281） | 0.46 | 1.00 | 0.748 | 0 | 判断保留 | 4 |
| 逆 | 4 | 2 | 0.50 [0.15, 0.85] | +0.00σ（0.688） | 0.54 | 0.93 | 0.748 | 0 | 判断保留 | 4 |
| 裏 | 36 | 34 | 0.94 [0.82, 0.98] | +5.33σ（0.000） | 0.95 | 1.00 | 0.748 | 0 | 支持 | 1 |

**異議あり（不成立）** 元の命題に判例 40 件（対偶の判例も同じ）

- DeNA 2018: lg_lead_gap=0.050, b_paths=offense, rank=4, league=C, lg_gap34=0.010, lg_rest_sd=0.037 / surprise=0.050
  - DeNA 2018 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 阪神 2018: lg_lead_gap=0.050, b_paths=offense+convert, rank=6, league=C, lg_gap34=0.010, lg_rest_sd=0.037 / surprise=0.050
  - 阪神 2018 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 中日 2014 **(focus)**: lg_lead_gap=0.049, b_paths=offense, rank=4, league=C, lg_gap34=0.043, lg_rest_sd=0.041 / surprise=0.049
  - 中日 2014 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- DeNA 2014: lg_lead_gap=0.049, b_paths=offense, rank=5, league=C, lg_gap34=0.043, lg_rest_sd=0.041 / surprise=0.049
  - DeNA 2014 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ヤクルト 2014: lg_lead_gap=0.049, b_paths=defense+convert, rank=6, league=C, lg_gap34=0.043, lg_rest_sd=0.041 / surprise=0.049
  - ヤクルト 2014 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- オリックス 2018: lg_lead_gap=0.047, b_paths=offense, rank=4, league=P, lg_gap34=0.058, lg_rest_sd=0.070 / surprise=0.047
  - オリックス 2018 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 楽天 2018: lg_lead_gap=0.047, b_paths=offense+convert, rank=6, league=P, lg_gap34=0.058, lg_rest_sd=0.070 / surprise=0.047
  - 楽天 2018 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ロッテ 2018: lg_lead_gap=0.047, b_paths=offense, rank=5, league=P, lg_gap34=0.058, lg_rest_sd=0.070 / surprise=0.047
  - ロッテ 2018 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 中日 2019 **(focus)**: lg_lead_gap=0.039, b_paths=offense+convert, rank=5, league=C, lg_gap34=0.004, lg_rest_sd=0.037 / surprise=0.039
  - 中日 2019 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ヤクルト 2019: lg_lead_gap=0.039, b_paths=defense+convert, rank=6, league=C, lg_gap34=0.004, lg_rest_sd=0.037 / surprise=0.039
  - ヤクルト 2019 は「lg_lead_gap < 0.05」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ほか 30 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 2 件（裏の判例も同じ）

- 巨人 2023: lg_lead_gap=0.084, b_paths=none, rank=4, league=C, lg_gap34=0.025, lg_rest_sd=0.064 / surprise=0.084
  - 巨人 2023 は「b_paths == none」を満たすのに「lg_lead_gap < 0.05」を満たさない。なぜか？ → H1
- 広島 2012: lg_lead_gap=0.081, b_paths=none, rank=4, league=C, lg_gap34=0.049, lg_rest_sd=0.089 / surprise=0.081
  - 広島 2012 は「b_paths == none」を満たすのに「lg_lead_gap < 0.05」を満たさない。なぜか？ → H1

## P176: どの道筋にも当たらない B クラスは、3位と4位の勝率差が .020 未満の年にいる（A と B の境が近い）

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 2 件: c-2012, g-2023
- もし: `b_paths == none` ならば: `lg_gap34 < 0.02`
- 識別子: `[where:upper_half==false] b_paths=="none" => lg_gap34<0.02`（指紋 `c6d9784a6d7fc471`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: {'where': [{'col': 'upper_half', 'op': '==', 'value': False}]} / 単位数: 78
- 見直す条件（反証）: 道筋のない B の4分の1を超えて、3位と4位の差が .020 以上
- 注記: 単位は4つで判断保留の見込み。逆（境が近い年の B は道筋がない）も見る
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 4 | 2 | 0.50 [0.15, 0.85] | -1.15σ（0.262） | 0.46 | 1.08 | 0.632 | 0 | 判断保留 | 4 |
| 対偶 | 42 | 40 | 0.95 [0.84, 0.99] | +3.03σ（0.001） | 0.95 | 1.00 | 0.632 | 0 | 支持 | 1 |
| 逆 | 36 | 2 | 0.06 [0.02, 0.18] | -9.62σ（0.000） | 0.05 | 1.08 | 0.632 | 0 | 棄却 | 3 |
| 裏 | 74 | 40 | 0.54 [0.43, 0.65] | -4.16σ（0.000） | 0.54 | 1.00 | 0.632 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 2 件（対偶の判例も同じ）

- 広島 2012: b_paths=none, lg_gap34=0.049, rank=4, league=C, lg_lead_gap=0.081, lg_rest_sd=0.089 / surprise=0.049
  - 広島 2012 は「b_paths == none」を満たすのに「lg_gap34 < 0.02」を満たさない。なぜか？ → H1
- 巨人 2023: b_paths=none, lg_gap34=0.025, rank=4, league=C, lg_lead_gap=0.084, lg_rest_sd=0.064 / surprise=0.025
  - 巨人 2023 は「b_paths == none」を満たすのに「lg_gap34 < 0.02」を満たさない。なぜか？ → H1

**異議あり（不成立）** 逆に判例 34 件（裏の判例も同じ）

- 広島 2021: b_paths=defense, lg_gap34=0.015, rank=4, league=C, lg_lead_gap=0.005, lg_rest_sd=0.061 / surprise=0.015
  - 広島 2021 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 中日 2021 **(focus)**: b_paths=offense, lg_gap34=0.015, rank=5, league=C, lg_lead_gap=0.005, lg_rest_sd=0.061 / surprise=0.015
  - 中日 2021 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- DeNA 2021: b_paths=defense+convert, lg_gap34=0.015, rank=6, league=C, lg_lead_gap=0.005, lg_rest_sd=0.061 / surprise=0.015
  - DeNA 2021 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 中日 2017 **(focus)**: b_paths=offense+defense, lg_gap34=0.015, rank=5, league=C, lg_lead_gap=0.072, lg_rest_sd=0.098 / surprise=0.015
  - 中日 2017 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 巨人 2017: b_paths=offense+convert, lg_gap34=0.015, rank=4, league=C, lg_lead_gap=0.072, lg_rest_sd=0.098 / surprise=0.015
  - 巨人 2017 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ヤクルト 2017: b_paths=offense+defense+convert, lg_gap34=0.015, rank=6, league=C, lg_lead_gap=0.072, lg_rest_sd=0.098 / surprise=0.015
  - ヤクルト 2017 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 広島 2024: b_paths=offense, lg_gap34=0.014, rank=4, league=C, lg_lead_gap=0.026, lg_rest_sd=0.041 / surprise=0.014
  - 広島 2024 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- 中日 2024 **(focus)**: b_paths=offense, lg_gap34=0.014, rank=6, league=C, lg_lead_gap=0.026, lg_rest_sd=0.041 / surprise=0.014
  - 中日 2024 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ヤクルト 2024: b_paths=defense, lg_gap34=0.014, rank=5, league=C, lg_lead_gap=0.026, lg_rest_sd=0.041 / surprise=0.014
  - ヤクルト 2024 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- オリックス 2019: b_paths=offense, lg_gap34=0.014, rank=6, league=P, lg_lead_gap=0.013, lg_rest_sd=0.039 / surprise=0.014
  - オリックス 2019 は「lg_gap34 < 0.02」を満たすのに「b_paths == none」を満たさない。なぜか？ → H1
- ほか 24 件（propositions.jsonl を参照）

## P177: 点の差から見込まれるより5勝以上多く勝てば、A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 5 件: e-2024, d-2024, e-2025, d-2022, d-2017
- もし: `wins_vs_pythag >= 5` ならば: `upper_half == True`
- 識別子: `[all] wins_vs_pythag>=5 => upper_half==true`（指紋 `7b61084cee78732b`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P50, P152, P153, P154, P178, P179, P180, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: きっかけ以外で、5勝以上多く勝った単位の4分の1を超えて B
- 注記: R49。中日 2022年（+6.9 で B）は判例になると分かっている。wins_vs_pythag は勝ち数を含むので A かどうかと一部算術でつながる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 18 | 13 | 0.72 [0.49, 0.88] | -0.27σ（0.481） | 0.50 | 1.44 | 0.039 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 73 | 0.94 [0.86, 0.97] | +3.79σ（0.000） | 0.88 | 1.06 | 0.039 | 0 | 支持 | 1 |
| 逆 | 78 | 13 | 0.17 [0.10, 0.26] | -11.90σ（0.000） | 0.12 | 1.44 | 0.039 | 0 | 修正 | 2 |
| 裏 | 138 | 73 | 0.53 [0.45, 0.61] | -6.00σ（0.000） | 0.50 | 1.06 | 0.039 | 0 | 修正 | 2 |

**待った！判断保留** 元の命題に判例 5 件（対偶の判例も同じ）

- 楽天 2024: wins_vs_pythag=+7.78, upper_half=False, rank=4, rd=-87, alloc_z_strat=+1.88, one_run_net=3 / surprise=+7.78
  - 楽天 2024 は「wins_vs_pythag >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2024 **(focus)**: wins_vs_pythag=+7.56, upper_half=False, rank=6, rd=-105, alloc_z_strat=0.459, one_run_net=10 / surprise=+7.56
  - 中日 2024 は「wins_vs_pythag >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2025: wins_vs_pythag=+7.06, upper_half=False, rank=4, rd=-80, alloc_z_strat=+1.24, one_run_net=12 / surprise=+7.06
  - 楽天 2025 は「wins_vs_pythag >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2022 **(focus)**: wins_vs_pythag=+6.93, upper_half=False, rank=6, rd=-81, alloc_z_strat=0.719, one_run_net=2 / surprise=+6.93
  - 中日 2022 は「wins_vs_pythag >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2017 **(focus)**: wins_vs_pythag=+5.29, upper_half=False, rank=5, rd=-136, alloc_z_strat=0.233, one_run_net=-3 / surprise=+5.29
  - 中日 2017 は「wins_vs_pythag >= 5」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3

**異議あり（主張が強すぎる）** 逆に判例 65 件（裏の判例も同じ）

- 阪神 2022: wins_vs_pythag=-9.93, upper_half=True, rank=3, rd=61, alloc_z_strat=-2.14, one_run_net=-5 / surprise=-9.93
  - 阪神 2022 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- 巨人 2018: wins_vs_pythag=-7.25, upper_half=True, rank=3, rd=50, alloc_z_strat=-1.75, one_run_net=-12 / surprise=-7.25
  - 巨人 2018 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- ソフトバンク 2024: wins_vs_pythag=-5.88, upper_half=True, rank=1, rd=217, alloc_z_strat=0.285, one_run_net=5 / surprise=-5.88
  - ソフトバンク 2024 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- 阪神 2025: wins_vs_pythag=-5.62, upper_half=True, rank=1, rd=144, alloc_z_strat=-1.53, one_run_net=-3 / surprise=-5.62
  - 阪神 2025 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- 日本ハム 2025: wins_vs_pythag=-5.30, upper_half=True, rank=2, rd=139, alloc_z_strat=0.957, one_run_net=1 / surprise=-5.30
  - 日本ハム 2025 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- オリックス 2014: wins_vs_pythag=-5.19, upper_half=True, rank=2, rd=116, alloc_z_strat=-0.632, one_run_net=-6 / surprise=-5.19
  - オリックス 2014 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- ソフトバンク 2022: wins_vs_pythag=-5.01, upper_half=True, rank=1, rd=84, alloc_z_strat=-1.10, one_run_net=0 / surprise=-5.01
  - ソフトバンク 2022 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- 広島 2018: wins_vs_pythag=+4.93, upper_half=True, rank=1, rd=70, alloc_z_strat=+1.46, one_run_net=7 / surprise=+4.93
  - 広島 2018 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- 日本ハム 2015: wins_vs_pythag=+4.83, upper_half=True, rank=2, rd=34, alloc_z_strat=+1.32, one_run_net=8 / surprise=+4.83
  - 日本ハム 2015 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- ヤクルト 2022: wins_vs_pythag=+4.82, upper_half=True, rank=1, rd=53, alloc_z_strat=+1.89, one_run_net=8 / surprise=+4.82
  - ヤクルト 2022 は「upper_half == True」を満たすのに「wins_vs_pythag >= 5」を満たさない。なぜか？ → H3
- ほか 55 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ t-2015 を除く）: n=17 成立=12 成立率=0.71 [0.47, 0.87] → **判断保留** / 判例: e-2024, d-2024, e-2025, d-2022, d-2017

## P178: 得点・失点の組み合わせ方が基準より1標準偏差以上有利なら、A クラス

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 3 件: e-2024, e-2025, b-2019
- もし: `alloc_z_strat >= 1` ならば: `upper_half == True`
- 識別子: `[all] alloc_z_strat>=1 => upper_half==true`（指紋 `e5eb40764a993e0e`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P50, P152, P153, P154, P177, P179, P180, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: きっかけ以外で、組み合わせ方 ≥ 1 の単位の4分の1を超えて B
- 注記: R49。P52 の「組み合わせ方 < −1 ⇒ B」の鏡の側
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 31 | 28 | 0.90 [0.75, 0.97] | +1.97σ（0.031） | 0.50 | 1.81 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 75 | 0.96 [0.89, 0.99] | +4.31σ（0.000） | 0.80 | 1.20 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 28 | 0.36 [0.26, 0.47] | -7.98σ（0.000） | 0.20 | 1.81 | 0.000 | 0 | 修正 | 2 |
| 裏 | 125 | 75 | 0.60 [0.51, 0.68] | -3.87σ（0.000） | 0.50 | 1.20 | 0.000 | 0 | 修正 | 2 |

**異議あり（例外あり）** 元の命題に判例 3 件（対偶の判例も同じ）

- 楽天 2024: alloc_z_strat=+1.88, upper_half=False, rank=4, rd=-87, wins_vs_pythag=+7.78 / surprise=+1.88
  - 楽天 2024 は「alloc_z_strat >= 1」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2025: alloc_z_strat=+1.24, upper_half=False, rank=4, rd=-80, wins_vs_pythag=+7.06 / surprise=+1.24
  - 楽天 2025 は「alloc_z_strat >= 1」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- オリックス 2019: alloc_z_strat=+1.08, upper_half=False, rank=6, rd=-93, wins_vs_pythag=+2.75 / surprise=+1.08
  - オリックス 2019 は「alloc_z_strat >= 1」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3

**異議あり（主張が強すぎる）** 逆に判例 50 件（裏の判例も同じ）

- 阪神 2022: alloc_z_strat=-2.14, upper_half=True, rank=3, rd=61, wins_vs_pythag=-9.93 / surprise=-2.14
  - 阪神 2022 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- 巨人 2018: alloc_z_strat=-1.75, upper_half=True, rank=3, rd=50, wins_vs_pythag=-7.25 / surprise=-1.75
  - 巨人 2018 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- 阪神 2025: alloc_z_strat=-1.53, upper_half=True, rank=1, rd=144, wins_vs_pythag=-5.62 / surprise=-1.53
  - 阪神 2025 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- ソフトバンク 2022: alloc_z_strat=-1.10, upper_half=True, rank=1, rd=84, wins_vs_pythag=-5.01 / surprise=-1.10
  - ソフトバンク 2022 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- 西武 2017: alloc_z_strat=-0.997, upper_half=True, rank=2, rd=130, wins_vs_pythag=-4.21 / surprise=-0.997
  - 西武 2017 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- 楽天 2013: alloc_z_strat=0.970, upper_half=True, rank=1, rd=91, wins_vs_pythag=+1.47 / surprise=0.970
  - 楽天 2013 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- 日本ハム 2025: alloc_z_strat=0.957, upper_half=True, rank=2, rd=139, wins_vs_pythag=-5.30 / surprise=0.957
  - 日本ハム 2025 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- 楽天 2019: alloc_z_strat=-0.950, upper_half=True, rank=3, rd=36, wins_vs_pythag=-2.34 / surprise=-0.950
  - 楽天 2019 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- 日本ハム 2018: alloc_z_strat=0.910, upper_half=True, rank=3, rd=3, wins_vs_pythag=+3.67 / surprise=0.910
  - 日本ハム 2018 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- 日本ハム 2012: alloc_z_strat=-0.890, upper_half=True, rank=1, rd=60, wins_vs_pythag=-0.083 / surprise=-0.890
  - 日本ハム 2012 は「upper_half == True」を満たすのに「alloc_z_strat >= 1」を満たさない。なぜか？ → H3
- ほか 40 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ t-2015 を除く）: n=30 成立=27 成立率=0.90 [0.74, 0.97] → **判断保留** / 判例: e-2024, e-2025, b-2019

## P179: 中位の相手との試合で、点の差から見込まれるより3勝以上多く勝てば、A クラス

- **判定: exit 4 待った！判断保留** — 元の命題: 判例 4 件: m-2017, e-2015, d-2023, e-2023
- もし: `opp_conv_mid >= 3` ならば: `upper_half == True`
- 識別子: `[all] opp_conv_mid>=3 => upper_half==true`（指紋 `b54daa8b824c738c`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P50, P152, P153, P154, P177, P178, P180, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: きっかけ以外で、中位の相手から3勝以上多く勝った単位の4分の1を超えて B
- 注記: R49。中位の相手は最終順位で決める（docs/propositions.md の前提）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 15 | 11 | 0.73 [0.48, 0.89] | -0.15σ（0.539） | 0.50 | 1.47 | 0.050 | 0 | 判断保留 | 4 |
| 対偶 | 78 | 74 | 0.95 [0.88, 0.98] | +4.05σ（0.000） | 0.90 | 1.05 | 0.050 | 0 | 支持 | 1 |
| 逆 | 78 | 11 | 0.14 [0.08, 0.24] | -12.42σ（0.000） | 0.10 | 1.47 | 0.050 | 0 | 棄却 | 3 |
| 裏 | 141 | 74 | 0.52 [0.44, 0.61] | -6.17σ（0.000） | 0.50 | 1.05 | 0.050 | 0 | 棄却 | 3 |

**待った！判断保留** 元の命題に判例 4 件（対偶の判例も同じ）

- ロッテ 2017: opp_conv_mid=+3.88, upper_half=False, rank=6, rd=-168, opp_conv_top=-2.42, opp_conv_low=+1.04 / surprise=+3.88
  - ロッテ 2017 は「opp_conv_mid >= 3」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2015: opp_conv_mid=+3.40, upper_half=False, rank=6, rd=-149, opp_conv_top=0.168, opp_conv_low=-0.063 / surprise=+3.40
  - 楽天 2015 は「opp_conv_mid >= 3」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 中日 2023 **(focus)**: opp_conv_mid=+3.31, upper_half=False, rank=6, rd=-108, opp_conv_top=-0.037, opp_conv_low=-0.949 / surprise=+3.31
  - 中日 2023 は「opp_conv_mid >= 3」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3
- 楽天 2023: opp_conv_mid=+3.14, upper_half=False, rank=4, rd=-43, opp_conv_top=-0.450, opp_conv_low=-1.02 / surprise=+3.14
  - 楽天 2023 は「opp_conv_mid >= 3」を満たすのに「upper_half == True」を満たさない。なぜか？ → H3

**異議あり（不成立）** 逆に判例 67 件（裏の判例も同じ）

- 西武 2017: opp_conv_mid=-4.29, upper_half=True, rank=2, rd=130, opp_conv_top=0.616, opp_conv_low=-0.586 / surprise=-4.29
  - 西武 2017 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- ソフトバンク 2024: opp_conv_mid=-4.14, upper_half=True, rank=1, rd=217, opp_conv_top=-1.06, opp_conv_low=-0.989 / surprise=-4.14
  - ソフトバンク 2024 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- 阪神 2022: opp_conv_mid=-2.84, upper_half=True, rank=3, rd=61, opp_conv_top=-5.18, opp_conv_low=-2.09 / surprise=-2.84
  - 阪神 2022 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- 巨人 2015: opp_conv_mid=-2.79, upper_half=True, rank=2, rd=46, opp_conv_top=+3.53, opp_conv_low=+1.07 / surprise=-2.79
  - 巨人 2015 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- 西武 2019: opp_conv_mid=+2.76, upper_half=True, rank=1, rd=61, opp_conv_top=+1.21, opp_conv_low=0.714 / surprise=+2.76
  - 西武 2019 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- 楽天 2017: opp_conv_mid=+2.75, upper_half=True, rank=3, rd=57, opp_conv_top=-1.75, opp_conv_low=-1.48 / surprise=+2.75
  - 楽天 2017 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- 広島 2023: opp_conv_mid=+2.64, upper_half=True, rank=2, rd=-15, opp_conv_top=0.595, opp_conv_low=+1.68 / surprise=+2.64
  - 広島 2023 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- ソフトバンク 2017: opp_conv_mid=+2.60, upper_half=True, rank=1, rd=155, opp_conv_top=+1.13, opp_conv_low=+3.01 / surprise=+2.60
  - ソフトバンク 2017 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- ヤクルト 2018: opp_conv_mid=+2.59, upper_half=True, rank=2, rd=-7, opp_conv_top=-1.17, opp_conv_low=+1.79 / surprise=+2.59
  - ヤクルト 2018 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- オリックス 2025: opp_conv_mid=-2.58, upper_half=True, rank=3, rd=-17, opp_conv_top=+2.49, opp_conv_low=+3.12 / surprise=-2.58
  - オリックス 2025 は「upper_half == True」を満たすのに「opp_conv_mid >= 3」を満たさない。なぜか？ → H3
- ほか 57 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ t-2015 を除く）: n=14 成立=10 成立率=0.71 [0.45, 0.88] → **判断保留** / 判例: m-2017, e-2015, d-2023, e-2023

## P180: 点の差どおりに勝てば A の線（3位と4位の勝率の中間）に届く（line_gap_pythag ≥ 0）なら、A クラス

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 11 件: h-2021, h-2013, l-2015, c-2015, c-2022 ほか
- もし: `line_gap_pythag >= 0` ならば: `upper_half == True`
- 識別子: `[all] line_gap_pythag>=0 => upper_half==true`（指紋 `d49be6cb37c59033`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P50, P152, P153, P154, P177, P178, P179, P182
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 点の差どおりで線に届くチームの4分の1を超えて B
- 注記: 勝率 − 線 = line_gap_pythag + resid_fixed の恒等式のうち、前の項だけで言う命題。逆の判例（線に届かないのに A）は、点の差より勝って線を越えたチーム。線は最終順位で決める（前提）
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 3 回、元の命題に異議あり 3 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 74 | 63 | 0.85 [0.75, 0.91] | +2.01σ（0.025） | 0.50 | 1.70 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 67 | 0.86 [0.76, 0.92] | +2.22σ（0.014） | 0.53 | 1.63 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 63 | 0.81 [0.71, 0.88] | +1.18σ（0.147） | 0.47 | 1.70 | 0.000 | 0 | 判断保留 | 4 |
| 裏 | 82 | 67 | 0.82 [0.72, 0.89] | +1.40σ（0.098） | 0.50 | 1.63 | 0.000 | 0 | 判断保留 | 4 |

**異議あり（例外あり）** 元の命題に判例 11 件（対偶の判例も同じ）

- ソフトバンク 2021: line_gap_pythag=0.058, upper_half=False, rank=4, lg_line=0.504, pythag_fixed=0.561, resid_fixed=-0.069, wins_vs_pythag=-8.47 / surprise=0.058
  - ソフトバンク 2021 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- ソフトバンク 2013: line_gap_pythag=0.055, upper_half=False, rank=4, lg_line=0.518, pythag_fixed=0.573, resid_fixed=-0.059, wins_vs_pythag=-8.37 / surprise=0.055
  - ソフトバンク 2013 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 西武 2015: line_gap_pythag=0.037, upper_half=False, rank=4, lg_line=0.507, pythag_fixed=0.544, resid_fixed=-0.044, wins_vs_pythag=-6.07 / surprise=0.037
  - 西武 2015 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 広島 2015: line_gap_pythag=0.035, upper_half=False, rank=4, lg_line=0.495, pythag_fixed=0.530, resid_fixed=-0.037, wins_vs_pythag=-5.18 / surprise=0.035
  - 広島 2015 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 広島 2022: line_gap_pythag=0.019, upper_half=False, rank=5, lg_line=0.487, pythag_fixed=0.507, resid_fixed=-0.035, wins_vs_pythag=-4.93 / surprise=0.019
  - 広島 2022 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 楽天 2012: line_gap_pythag=0.019, upper_half=False, rank=4, lg_line=0.504, pythag_fixed=0.523, resid_fixed=-0.023, wins_vs_pythag=-3.07 / surprise=0.019
  - 楽天 2012 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- ロッテ 2019: line_gap_pythag=0.019, upper_half=False, rank=4, lg_line=0.504, pythag_fixed=0.523, resid_fixed=-0.026, wins_vs_pythag=-3.65 / surprise=0.019
  - ロッテ 2019 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 西武 2016: line_gap_pythag=0.015, upper_half=False, rank=4, lg_line=0.486, pythag_fixed=0.501, resid_fixed=-0.044, wins_vs_pythag=-6.10 / surprise=0.015
  - 西武 2016 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 中日 2019 **(focus)**: line_gap_pythag=0.014, upper_half=False, rank=5, lg_line=0.502, pythag_fixed=0.516, resid_fixed=-0.033, wins_vs_pythag=-4.71 / surprise=0.014
  - 中日 2019 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- 巨人 2017: line_gap_pythag=0.006, upper_half=False, rank=4, lg_line=0.522, pythag_fixed=0.528, resid_fixed=-0.014, wins_vs_pythag=-1.94 / surprise=0.006
  - 巨人 2017 は「line_gap_pythag >= 0」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2, H3
- ほか 1 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 15 件（裏の判例も同じ）

- 阪神 2015: line_gap_pythag=-0.071, upper_half=True, rank=3, lg_line=0.495, pythag_fixed=0.424, resid_fixed=0.073, wins_vs_pythag=+10.25 / surprise=-0.071
  - 阪神 2015 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- 広島 2023: line_gap_pythag=-0.030, upper_half=True, rank=2, lg_line=0.516, pythag_fixed=0.486, resid_fixed=0.046, wins_vs_pythag=+6.41 / surprise=-0.030
  - 広島 2023 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- ロッテ 2013: line_gap_pythag=-0.027, upper_half=True, rank=3, lg_line=0.518, pythag_fixed=0.491, resid_fixed=0.031, wins_vs_pythag=+4.35 / surprise=-0.027
  - ロッテ 2013 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- 阪神 2019: line_gap_pythag=-0.025, upper_half=True, rank=3, lg_line=0.502, pythag_fixed=0.477, resid_fixed=0.027, wins_vs_pythag=+3.68 / surprise=-0.025
  - 阪神 2019 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- DeNA 2017: line_gap_pythag=-0.022, upper_half=True, rank=3, lg_line=0.522, pythag_fixed=0.499, resid_fixed=0.030, wins_vs_pythag=+4.11 / surprise=-0.022
  - DeNA 2017 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- DeNA 2022: line_gap_pythag=-0.020, upper_half=True, rank=2, lg_line=0.487, pythag_fixed=0.467, resid_fixed=0.051, wins_vs_pythag=+7.13 / surprise=-0.020
  - DeNA 2022 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- ロッテ 2023: line_gap_pythag=-0.019, upper_half=True, rank=2, lg_line=0.502, pythag_fixed=0.483, resid_fixed=0.024, wins_vs_pythag=+3.33 / surprise=-0.019
  - ロッテ 2023 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- オリックス 2025: line_gap_pythag=-0.017, upper_half=True, rank=3, lg_line=0.502, pythag_fixed=0.485, resid_fixed=0.044, wins_vs_pythag=+6.13 / surprise=-0.017
  - オリックス 2025 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- DeNA 2019: line_gap_pythag=-0.013, upper_half=True, rank=2, lg_line=0.502, pythag_fixed=0.489, resid_fixed=0.019, wins_vs_pythag=+2.59 / surprise=-0.013
  - DeNA 2019 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- 阪神 2014: line_gap_pythag=-0.011, upper_half=True, rank=2, lg_line=0.500, pythag_fixed=0.489, resid_fixed=0.036, wins_vs_pythag=+5.12 / surprise=-0.011
  - 阪神 2014 は「upper_half == True」を満たすのに「line_gap_pythag >= 0」を満たさない。なぜか？ → H2, H3
- ほか 5 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ t-2015 を除く）: n=74 成立=63 成立率=0.85 [0.75, 0.91] → **支持** / 判例: h-2021, h-2013, l-2015, c-2015, c-2022, e-2012, m-2019, l-2016, d-2019, g-2017

**除外中の判例**（統計からは除いたが、判例としては残す）

- 楽天 2020: line_gap_pythag=0.034, upper_half=False, rank=4, lg_line=0.496, pythag_fixed=0.530, resid_fixed=-0.039, wins_vs_pythag=-4.32
- DeNA 2020: line_gap_pythag=0.032, upper_half=False, rank=4, lg_line=0.506, pythag_fixed=0.539, resid_fixed=-0.048, wins_vs_pythag=-5.42

## P181: ほかの年の A の最低勝率より下（A と B が混ざる帯の下、mix_zone = −1）なら、B クラス

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 1 件: g-2018
- もし: `mix_zone == -1` ならば: `upper_half == False`
- 識別子: `[all] mix_zone==-1 => upper_half==false`（指紋 `36fd04fa07c1ec21`）
- 兄弟（範囲と結論が同じ、条件が違う）: P5, P52, P64, P95, P96, P115, P126, P138, P147, P148, P149, P150, P151
- 強さ: ほとんど（almost_always, 基準 0.90）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 帯の下の単位の10分の1を超えて A
- 注記: R53。帯は自分の年を除いて引く（1年抜き）。きっかけの巨人 2018年は帯の下端そのもの。勝率と順位の算術のつながりが強いので、通っても説明ではない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 65 | 64 | 0.98 [0.92, 1.00] | +2.27σ（0.009） | 0.50 | 1.97 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 77 | 0.99 [0.93, 1.00] | +2.57σ（0.003） | 0.58 | 1.69 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 64 | 0.82 [0.72, 0.89] | -2.34σ（0.022） | 0.42 | 1.97 | 0.000 | 0 | 修正 | 2 |
| 裏 | 91 | 77 | 0.85 [0.76, 0.91] | -1.71σ（0.068） | 0.50 | 1.69 | 0.000 | 0 | 判断保留 | 4 |

**異議あり（例外あり）** 元の命題に判例 1 件（対偶の判例も同じ）

- 巨人 2018: mix_zone=-1, upper_half=True, wpct=0.486, mix_lo=0.489, mix_hi=0.514, rank=3 / surprise=-1
  - 巨人 2018 は「mix_zone == -1」を満たすのに「upper_half == False」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 14 件（裏の判例も同じ）

- 巨人 2017: mix_zone=1, upper_half=False, wpct=0.514, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=1
  - 巨人 2017 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- 楽天 2012: mix_zone=0, upper_half=False, wpct=0.500, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - 楽天 2012 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- ソフトバンク 2013: mix_zone=0, upper_half=False, wpct=0.514, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - ソフトバンク 2013 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- 広島 2015: mix_zone=0, upper_half=False, wpct=0.493, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - 広島 2015 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- 西武 2015: mix_zone=0, upper_half=False, wpct=0.500, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - 西武 2015 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- 広島 2019: mix_zone=0, upper_half=False, wpct=0.500, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - 広島 2019 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- ロッテ 2019: mix_zone=0, upper_half=False, wpct=0.496, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - ロッテ 2019 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- ソフトバンク 2021: mix_zone=0, upper_half=False, wpct=0.492, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - ソフトバンク 2021 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- 楽天 2022: mix_zone=0, upper_half=False, wpct=0.493, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - 楽天 2022 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- 巨人 2022: mix_zone=0, upper_half=False, wpct=0.486, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=0
  - 巨人 2022 は「upper_half == False」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2
- ほか 4 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ g-2018 を除く）: n=64 成立=64 成立率=1.00 [0.94, 1.00] → **支持** / 判例なし

## P182: ほかの年の B の最高勝率より上（帯の上、mix_zone = +1）なら、A クラス

- **判定: exit 1 異議あり（例外あり）** — 元の命題: 判例 1 件: g-2017
- もし: `mix_zone == 1` ならば: `upper_half == True`
- 識別子: `[all] mix_zone==1 => upper_half==true`（指紋 `2d66229977ee4cb5`）
- 兄弟（範囲と結論が同じ、条件が違う）: P1, P11, P50, P152, P153, P154, P177, P178, P179, P180
- 強さ: ほとんど（almost_always, 基準 0.90）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 帯の上の単位の10分の1を超えて B
- 注記: R53。P181 の鏡の側。きっかけの巨人 2017年は帯の上端そのもの
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 60 | 59 | 0.98 [0.91, 1.00] | +2.15σ（0.014） | 0.50 | 1.97 | 0.000 | 0 | 支持 | 1 |
| 対偶 | 78 | 77 | 0.99 [0.93, 1.00] | +2.57σ（0.003） | 0.62 | 1.60 | 0.000 | 0 | 支持 | 1 |
| 逆 | 78 | 59 | 0.76 [0.65, 0.84] | -4.23σ（0.000） | 0.38 | 1.97 | 0.000 | 0 | 修正 | 2 |
| 裏 | 96 | 77 | 0.80 [0.71, 0.87] | -3.20σ（0.003） | 0.50 | 1.60 | 0.000 | 0 | 修正 | 2 |

**異議あり（例外あり）** 元の命題に判例 1 件（対偶の判例も同じ）

- 巨人 2017: mix_zone=1, upper_half=False, wpct=0.514, mix_lo=0.486, mix_hi=0.514, rank=4 / surprise=1
  - 巨人 2017 は「mix_zone == 1」を満たすのに「upper_half == True」を満たさない。なぜか？ → H2

**異議あり（主張が強すぎる）** 逆に判例 19 件（裏の判例も同じ）

- 巨人 2018: mix_zone=-1, upper_half=True, wpct=0.486, mix_lo=0.489, mix_hi=0.514, rank=3 / surprise=-1
  - 巨人 2018 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- ソフトバンク 2012: mix_zone=0, upper_half=True, wpct=0.508, mix_lo=0.486, mix_hi=0.514, rank=3 / surprise=0
  - ソフトバンク 2012 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- ヤクルト 2012: mix_zone=0, upper_half=True, wpct=0.511, mix_lo=0.486, mix_hi=0.514, rank=3 / surprise=0
  - ヤクルト 2012 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- 広島 2013: mix_zone=0, upper_half=True, wpct=0.489, mix_lo=0.486, mix_hi=0.514, rank=3 / surprise=0
  - 広島 2013 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- ロッテ 2015: mix_zone=0, upper_half=True, wpct=0.514, mix_lo=0.486, mix_hi=0.514, rank=3 / surprise=0
  - ロッテ 2015 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- 阪神 2015: mix_zone=0, upper_half=True, wpct=0.496, mix_lo=0.486, mix_hi=0.514, rank=3 / surprise=0
  - 阪神 2015 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- DeNA 2016: mix_zone=0, upper_half=True, wpct=0.493, mix_lo=0.486, mix_hi=0.514, rank=3 / surprise=0
  - DeNA 2016 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- 巨人 2016: mix_zone=0, upper_half=True, wpct=0.507, mix_lo=0.486, mix_hi=0.514, rank=2 / surprise=0
  - 巨人 2016 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- ロッテ 2016: mix_zone=0, upper_half=True, wpct=0.514, mix_lo=0.486, mix_hi=0.514, rank=3 / surprise=0
  - ロッテ 2016 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- DeNA 2019: mix_zone=0, upper_half=True, wpct=0.507, mix_lo=0.486, mix_hi=0.514, rank=2 / surprise=0
  - DeNA 2019 は「upper_half == True」を満たすのに「mix_zone == 1」を満たさない。なぜか？ → H2
- ほか 9 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ g-2017 を除く）: n=59 成立=59 成立率=1.00 [0.94, 1.00] → **支持** / 判例なし

## P183: 収支がプラスなのに点の差を勝ちに変えられない（path_convert）なら、A と B が混ざる帯の中に落ちる

- **判定: exit 2 異議あり（主張が強すぎる）** — 元の命題: 判例 18 件: t-2013, b-2014, g-2015, h-2016, g-2017 ほか
- もし: `run_balance > 0 かつ path_convert == True` ならば: `mix_zone == 0`
- 識別子: `[all] path_convert==true & run_balance>0 => mix_zone==0`（指紋 `244cd7a1264c48c0`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: きっかけ以外で、収支プラス・変えられない単位の4分の1を超えて帯の外
- 注記: R54。帯は1年抜き（R53）。path_convert の規則は R45 で決めたもの（wins_vs_pythag < −2 か alloc_z_strat < −1）を使い、値を見て変えない
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 29 | 11 | 0.38 [0.23, 0.56] | -4.61σ（0.000） | 0.20 | 1.91 | 0.010 | 0 | 修正 | 2 |
| 対偶 | 125 | 107 | 0.86 [0.78, 0.91] | +2.74σ（0.003） | 0.81 | 1.05 | 0.010 | 0 | 支持 | 1 |
| 逆 | 31 | 11 | 0.35 [0.21, 0.53] | -5.08σ（0.000） | 0.19 | 1.91 | 0.010 | 0 | 修正 | 2 |
| 裏 | 127 | 107 | 0.84 [0.77, 0.90] | +2.41σ（0.008） | 0.80 | 1.05 | 0.010 | 0 | 支持 | 1 |

**異議あり（主張が強すぎる）** 元の命題に判例 18 件（対偶の判例も同じ）

- 阪神 2013: run_balance=0.496, path_convert=True, mix_zone=1, wins_vs_pythag=-2.40, one_run_net=2, alloc_z_strat=-0.050, wpct=0.521, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - 阪神 2013 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- オリックス 2014: run_balance=0.886, path_convert=True, mix_zone=1, wins_vs_pythag=-5.19, one_run_net=-6, alloc_z_strat=-0.632, wpct=0.563, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - オリックス 2014 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- 巨人 2015: run_balance=0.487, path_convert=True, mix_zone=1, wins_vs_pythag=-2.40, one_run_net=1, alloc_z_strat=0.257, wpct=0.528, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - 巨人 2015 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- ソフトバンク 2016: run_balance=+1.23, path_convert=True, mix_zone=1, wins_vs_pythag=-2.97, one_run_net=5, alloc_z_strat=0.181, wpct=0.606, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - ソフトバンク 2016 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- 巨人 2017: run_balance=0.308, path_convert=True, mix_zone=1, wins_vs_pythag=-1.94, one_run_net=-14, alloc_z_strat=-1.17, wpct=0.514, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - 巨人 2017 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- 西武 2017: run_balance=+1.05, path_convert=True, mix_zone=1, wins_vs_pythag=-4.21, one_run_net=-6, alloc_z_strat=-0.997, wpct=0.564, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - 西武 2017 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- 巨人 2018: run_balance=0.509, path_convert=True, mix_zone=-1, wins_vs_pythag=-7.25, one_run_net=-12, alloc_z_strat=-1.75, wpct=0.486, mix_lo=0.489, mix_hi=0.514 / surprise=True
  - 巨人 2018 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- 中日 2019 **(focus)**: run_balance=0.197, path_convert=True, mix_zone=-1, wins_vs_pythag=-4.71, one_run_net=-8, alloc_z_strat=-1.34, wpct=0.482, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - 中日 2019 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- 巨人 2019: run_balance=0.793, path_convert=True, mix_zone=1, wins_vs_pythag=-2.86, one_run_net=-1, alloc_z_strat=-0.240, wpct=0.546, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - 巨人 2019 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- 広島 2022: run_balance=0.119, path_convert=True, mix_zone=-1, wins_vs_pythag=-4.93, one_run_net=-7, alloc_z_strat=-0.293, wpct=0.471, mix_lo=0.486, mix_hi=0.514 / surprise=True
  - 広島 2022 は「run_balance > 0 かつ path_convert == True」を満たすのに「mix_zone == 0」を満たさない。なぜか？ → H2, H3
- ほか 8 件（propositions.jsonl を参照）

**異議あり（主張が強すぎる）** 逆に判例 20 件（裏の判例も同じ）

- ヤクルト 2012: run_balance=-0.097, path_convert=False, mix_zone=0, wins_vs_pythag=+3.30, one_run_net=8, alloc_z_strat=+1.53, wpct=0.511, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - ヤクルト 2012 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- 広島 2013: run_balance=0.162, path_convert=False, mix_zone=0, wins_vs_pythag=-1.85, one_run_net=-1, alloc_z_strat=-0.024, wpct=0.489, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - 広島 2013 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- ロッテ 2015: run_balance=-0.117, path_convert=False, mix_zone=0, wins_vs_pythag=+2.23, one_run_net=6, alloc_z_strat=+1.33, wpct=0.514, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - ロッテ 2015 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- 阪神 2015: run_balance=-0.613, path_convert=False, mix_zone=0, wins_vs_pythag=+10.25, one_run_net=4, alloc_z_strat=+1.44, wpct=0.496, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - 阪神 2015 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- DeNA 2016: run_balance=-0.042, path_convert=False, mix_zone=0, wins_vs_pythag=0.767, one_run_net=8, alloc_z_strat=0.700, wpct=0.493, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - DeNA 2016 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- 巨人 2016: run_balance=-0.109, path_convert=False, mix_zone=0, wins_vs_pythag=+3.89, one_run_net=5, alloc_z_strat=0.612, wpct=0.507, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - 巨人 2016 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- ロッテ 2016: run_balance=-0.084, path_convert=False, mix_zone=0, wins_vs_pythag=+1.89, one_run_net=3, alloc_z_strat=0.415, wpct=0.514, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - ロッテ 2016 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- 広島 2019: run_balance=-0.046, path_convert=False, mix_zone=0, wins_vs_pythag=+1.07, one_run_net=5, alloc_z_strat=0.232, wpct=0.500, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - 広島 2019 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- DeNA 2019: run_balance=-0.088, path_convert=False, mix_zone=0, wins_vs_pythag=+2.59, one_run_net=6, alloc_z_strat=0.858, wpct=0.507, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - DeNA 2019 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- 阪神 2019: run_balance=-0.197, path_convert=False, mix_zone=0, wins_vs_pythag=+3.68, one_run_net=1, alloc_z_strat=0.651, wpct=0.504, mix_lo=0.486, mix_hi=0.514 / surprise=False
  - 阪神 2019 は「mix_zone == 0」を満たすのに「run_balance > 0 かつ path_convert == True」を満たさない。なぜか？ → H2, H3
- ほか 10 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ g-2017, g-2018 を除く）: n=27 成立=11 成立率=0.41 [0.25, 0.59] → **修正** / 判例: t-2013, b-2014, g-2015, h-2016, l-2017, d-2019, g-2019, c-2022, h-2022, g-2024

## P184: 収支がマイナスなら、点の差より勝っても（resid_fixed > 0）、A と B が混ざる帯の下にいる

- **判定: exit 2 異議あり（主張が強すぎる）** — 元の命題: 判例 22 件: t-2015, db-2022, c-2023, b-2025, t-2014 ほか
- もし: `run_balance < 0 かつ resid_fixed > 0` ならば: `mix_zone == -1`
- 識別子: `[all] resid_fixed>0 & run_balance<0 => mix_zone==-1`（指紋 `f64dcd1c8c5dab3f`）
- 強さ: 概ね（usually, 基準 0.75）/ 範囲: 全体 / 単位数: 156
- 見直す条件（反証）: 収支マイナス・点の差より勝った単位の4分の1を超えて帯の中か上
- 注記: R54。P183 の鏡の側（中日の B の年の形、R51 の区画）。きっかけは巨人の2単位だが、この命題の範囲には入らない（どちらも収支プラス）
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 26 | 0.54 [0.40, 0.67] | -3.33σ（0.001） | 0.42 | 1.30 | 0.027 | 0 | 修正 | 2 |
| 対偶 | 91 | 69 | 0.76 [0.66, 0.83] | +0.18σ（0.484） | 0.69 | 1.10 | 0.027 | 0 | 判断保留 | 4 |
| 逆 | 65 | 26 | 0.40 [0.29, 0.52] | -6.52σ（0.000） | 0.31 | 1.30 | 0.027 | 0 | 修正 | 2 |
| 裏 | 108 | 69 | 0.64 [0.54, 0.72] | -2.67σ（0.007） | 0.58 | 1.10 | 0.027 | 0 | 修正 | 2 |

**異議あり（主張が強すぎる）** 元の命題に判例 22 件（対偶の判例も同じ）

- 阪神 2015: run_balance=-0.613, resid_fixed=0.073, mix_zone=0, wins_vs_pythag=+10.25, wpct=0.496, mix_lo=0.486 / surprise=0.073
  - 阪神 2015 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- DeNA 2022: run_balance=-0.259, resid_fixed=0.051, mix_zone=1, wins_vs_pythag=+7.13, wpct=0.518, mix_lo=0.486 / surprise=0.051
  - DeNA 2022 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- 広島 2023: run_balance=-0.147, resid_fixed=0.046, mix_zone=1, wins_vs_pythag=+6.41, wpct=0.532, mix_lo=0.486 / surprise=0.046
  - 広島 2023 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- オリックス 2025: run_balance=-0.194, resid_fixed=0.044, mix_zone=1, wins_vs_pythag=+6.13, wpct=0.529, mix_lo=0.486 / surprise=0.044
  - オリックス 2025 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- 阪神 2014: run_balance=-0.044, resid_fixed=0.036, mix_zone=1, wins_vs_pythag=+5.12, wpct=0.524, mix_lo=0.486 / surprise=0.036
  - 阪神 2014 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- 西武 2012: run_balance=-0.044, resid_fixed=0.035, mix_zone=1, wins_vs_pythag=+4.74, wpct=0.533, mix_lo=0.486 / surprise=0.035
  - 西武 2012 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- 楽天 2023: run_balance=-0.340, resid_fixed=0.033, mix_zone=0, wins_vs_pythag=+4.68, wpct=0.496, mix_lo=0.486 / surprise=0.033
  - 楽天 2023 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- ロッテ 2013: run_balance=-0.237, resid_fixed=0.031, mix_zone=1, wins_vs_pythag=+4.35, wpct=0.521, mix_lo=0.486 / surprise=0.031
  - ロッテ 2013 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- 巨人 2016: run_balance=-0.109, resid_fixed=0.028, mix_zone=0, wins_vs_pythag=+3.89, wpct=0.507, mix_lo=0.486 / surprise=0.028
  - 巨人 2016 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- 阪神 2019: run_balance=-0.197, resid_fixed=0.027, mix_zone=0, wins_vs_pythag=+3.68, wpct=0.504, mix_lo=0.486 / surprise=0.027
  - 阪神 2019 は「run_balance < 0 かつ resid_fixed > 0」を満たすのに「mix_zone == -1」を満たさない。なぜか？ → H2, H3
- ほか 12 件（propositions.jsonl を参照）

**異議あり（主張が強すぎる）** 逆に判例 39 件（裏の判例も同じ）

- ヤクルト 2023: run_balance=-0.298, resid_fixed=-0.065, mix_zone=-1, wins_vs_pythag=-9.16, wpct=0.407, mix_lo=0.486 / surprise=-0.065
  - ヤクルト 2023 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- 巨人 2018: run_balance=0.509, resid_fixed=-0.053, mix_zone=-1, wins_vs_pythag=-7.25, wpct=0.486, mix_lo=0.489 / surprise=-0.053
  - 巨人 2018 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- 阪神 2012: run_balance=-0.197, resid_fixed=-0.048, mix_zone=-1, wins_vs_pythag=-6.22, wpct=0.423, mix_lo=0.486 / surprise=-0.048
  - 阪神 2012 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- 日本ハム 2023: run_balance=-0.248, resid_fixed=-0.047, mix_zone=-1, wins_vs_pythag=-6.67, wpct=0.423, mix_lo=0.486 / surprise=-0.047
  - 日本ハム 2023 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- 西武 2016: run_balance=-0.084, resid_fixed=-0.044, mix_zone=-1, wins_vs_pythag=-6.10, wpct=0.457, mix_lo=0.486 / surprise=-0.044
  - 西武 2016 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- オリックス 2015: run_balance=-0.344, resid_fixed=-0.043, mix_zone=-1, wins_vs_pythag=-6.00, wpct=0.433, mix_lo=0.486 / surprise=-0.043
  - オリックス 2015 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- ヤクルト 2014: run_balance=-0.336, resid_fixed=-0.041, mix_zone=-1, wins_vs_pythag=-5.84, wpct=0.426, mix_lo=0.486 / surprise=-0.041
  - ヤクルト 2014 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- ヤクルト 2017: run_balance=-1.47, resid_fixed=-0.037, mix_zone=-1, wins_vs_pythag=-5.28, wpct=0.319, mix_lo=0.486 / surprise=-0.037
  - ヤクルト 2017 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- 広島 2022: run_balance=0.119, resid_fixed=-0.035, mix_zone=-1, wins_vs_pythag=-4.93, wpct=0.471, mix_lo=0.486 / surprise=-0.035
  - 広島 2022 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- 楽天 2018: run_balance=-0.618, resid_fixed=-0.034, mix_zone=-1, wins_vs_pythag=-4.70, wpct=0.414, mix_lo=0.489 / surprise=-0.034
  - 楽天 2018 は「mix_zone == -1」を満たすのに「run_balance < 0 かつ resid_fixed > 0」を満たさない。なぜか？ → H2, H3
- ほか 29 件（propositions.jsonl を参照）

**きっかけ以外での判定**（作り直しのきっかけ g-2017, g-2018 を除く）: n=48 成立=26 成立率=0.54 [0.40, 0.67] → **修正** / 判例: t-2015, db-2022, c-2023, b-2025, t-2014, l-2012, e-2023, m-2013, g-2016, t-2019

**除外中の判例**（統計からは除いたが、判例としては残す）

- 中日 2020 **(focus)**: run_balance=-0.600, resid_fixed=0.081, mix_zone=1, wins_vs_pythag=+9.35, wpct=0.522, mix_lo=0.486
- 西武 2020: run_balance=-0.640, resid_fixed=0.057, mix_zone=0, wins_vs_pythag=+6.63, wpct=0.500, mix_lo=0.486
- ロッテ 2020: run_balance=-0.180, resid_fixed=0.030, mix_zone=0, wins_vs_pythag=+3.55, wpct=0.513, mix_lo=0.486
