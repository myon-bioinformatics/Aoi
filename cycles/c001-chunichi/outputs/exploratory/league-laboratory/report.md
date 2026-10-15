# 3方向のリーグ実験

記録: 2026-10-15

合成データによる探索の記録。実測件数に加えず、命題・合格条件を変更しない。
係数は仮定であり、潜在的な「真の攻撃力・守備力」が同定されたという意味ではない。

## ① 勝敗を隠した条件付き補完

- 提案 144 件: {'feasible': 141, 'infeasible-in-declared-family': 3}
- 各リーグ6球団。得失点・対戦数・引分数と指定球団の勝利数を固定し、他球団の勝利数を補完する。
- 総勝利数で残りを絞ってから整数最大流で判定する。有限回の偏りを持つ乱数提案であり、全解列挙や一様抽出ではない。
- 通過/不通過/重複を全件残す。生成不能は宣言した生成族内の判定であり、野球全体の不可能性ではない。

## ② 能力予算と変換の損失

- 全配分の年次スキャン 616 件。実現可能 616 件。
- 各球団の攻撃/守備/変換への配分合計は 6 ポイント。費用と得点の単位を混ぜない。
- 得点率は対戦相手の守備を含む指数モデル。変換能力の残存率(1−loss)を勝敗オッズへ適用する。
- lossは計算するたびに失われる量ではなく、宣言した能力効果の減衰率。W−ピタゴラス期待勝利数も別欄に残す。
- 全配分を年成績で先に検査し、攻撃偏重・守備偏重・変換偏重・均衡型だけ試合へ展開して費用を抑える。
- 同じ配分を14年間続けた架空C1の順位列・上位回数・最長下位連続年数もskill_pathsに残す。

## ③ 得点の物差し

| スコア | raw差 | log1p差 | sqrt差 | relative差 |
|---|---:|---:|---:|---:|
| 3-4 | -1.000000 | -0.223144 | -0.267949 | -0.125000 |
| 6-7 | -1.000000 | -0.133531 | -0.196262 | -0.071429 |

公式の整数スコアを保存したまま、試合ごとに変換してから年平均を作る。
raw/0.97倍/ln(1+x)/sqrt(x)/min(x,4)/(相手との合計+1)で規格化、の6尺度。
集計はmath.fsumで試合順への依存を避け、小数12桁へ丸める。丸め誤差だけの順位・閾値分割を避けるためである。
allowedは変換後の失点で、小さいほどよい。relativeは相手依存の指標で、独立した能力量ではない。
ピタゴラス式や既存命題の値は補正で置換しない。別ID LAB-G01〜06の探索候補として比較する。

## 固定した閾値の評価

生成系列ごとに、発見seed・2013〜2022年・loss=0だけで「変換後平均差と閾値の比較 ⇒ 下位半分」を選ぶ。
比較方向(<または>=)も探索対象で、逆向きに選ばれる場合もそのまま残す。異なる生成系列への転用結果も保存する。
その後、後年・別seed・変換損失変更へ固定して適用する。尺度の採否を評価結果から自動で選び直さない。

| 系列 | 評価 | 尺度 | n | MCC | TP | FP | FN | TN |
|---|---|---|---:|---:|---:|---:|---:|---:|
| masked-wins | discovery | raw | 468 | 0.196581 | 140 | 94 | 94 | 140 |
| masked-wins | discovery | linear_097 | 468 | 0.196581 | 140 | 94 | 94 | 140 |
| masked-wins | discovery | log1p | 468 | 0.713822 | 213 | 47 | 21 | 187 |
| masked-wins | discovery | sqrt | 468 | 0.668648 | 204 | 48 | 30 | 186 |
| masked-wins | discovery | capped4 | 468 | 0.743899 | 221 | 49 | 13 | 185 |
| masked-wins | discovery | relative | 468 | 0.746321 | 214 | 40 | 20 | 194 |
| masked-wins | seed-holdout | raw | 186 | 0.247312 | 58 | 35 | 35 | 58 |
| masked-wins | seed-holdout | linear_097 | 186 | 0.247312 | 58 | 35 | 35 | 58 |
| masked-wins | seed-holdout | log1p | 186 | 0.716714 | 86 | 20 | 7 | 73 |
| masked-wins | seed-holdout | sqrt | 186 | 0.681370 | 83 | 20 | 10 | 73 |
| masked-wins | seed-holdout | capped4 | 186 | 0.743714 | 89 | 21 | 4 | 72 |
| masked-wins | seed-holdout | relative | 186 | 0.796851 | 86 | 12 | 7 | 81 |
| masked-wins | witness-shift | raw | 186 | 0.247312 | 58 | 35 | 35 | 58 |
| masked-wins | witness-shift | linear_097 | 186 | 0.247312 | 58 | 35 | 35 | 58 |
| masked-wins | witness-shift | log1p | 186 | 0.765588 | 90 | 20 | 3 | 73 |
| masked-wins | witness-shift | sqrt | 186 | 0.774996 | 90 | 19 | 3 | 74 |
| masked-wins | witness-shift | capped4 | 186 | 0.693649 | 88 | 25 | 5 | 68 |
| masked-wins | witness-shift | relative | 186 | 0.815748 | 91 | 16 | 2 | 77 |
| masked-wins | year-holdout | raw | 192 | 0.187500 | 57 | 39 | 39 | 57 |
| masked-wins | year-holdout | linear_097 | 192 | 0.187500 | 57 | 39 | 39 | 57 |
| masked-wins | year-holdout | log1p | 192 | 0.691261 | 86 | 20 | 10 | 76 |
| masked-wins | year-holdout | sqrt | 192 | 0.667973 | 83 | 19 | 13 | 77 |
| masked-wins | year-holdout | capped4 | 192 | 0.727699 | 93 | 25 | 3 | 71 |
| masked-wins | year-holdout | relative | 192 | 0.761450 | 87 | 14 | 9 | 82 |
| skill-budget | discovery | raw | 240 | 0.557802 | 103 | 37 | 17 | 83 |
| skill-budget | discovery | linear_097 | 240 | 0.557802 | 103 | 37 | 17 | 83 |
| skill-budget | discovery | log1p | 240 | 0.512989 | 120 | 70 | 0 | 50 |
| skill-budget | discovery | sqrt | 240 | 0.519462 | 120 | 69 | 0 | 51 |
| skill-budget | discovery | capped4 | 240 | 0.458991 | 116 | 70 | 4 | 50 |
| skill-budget | discovery | relative | 240 | 0.485768 | 117 | 68 | 3 | 52 |
| skill-budget | loss-shift | raw | 96 | -0.845154 | 8 | 48 | 40 | 0 |
| skill-budget | loss-shift | linear_097 | 96 | -0.845154 | 8 | 48 | 40 | 0 |
| skill-budget | loss-shift | log1p | 96 | -0.512989 | 28 | 48 | 20 | 0 |
| skill-budget | loss-shift | sqrt | 96 | -0.512989 | 28 | 48 | 20 | 0 |
| skill-budget | loss-shift | capped4 | 96 | -0.529150 | 27 | 48 | 21 | 0 |
| skill-budget | loss-shift | relative | 96 | -0.529150 | 27 | 48 | 21 | 0 |
| skill-budget | seed-holdout | raw | 96 | 0.845154 | 48 | 8 | 0 | 40 |
| skill-budget | seed-holdout | linear_097 | 96 | 0.845154 | 48 | 8 | 0 | 40 |
| skill-budget | seed-holdout | log1p | 96 | 0.512989 | 48 | 28 | 0 | 20 |
| skill-budget | seed-holdout | sqrt | 96 | 0.529150 | 48 | 27 | 0 | 21 |
| skill-budget | seed-holdout | capped4 | 96 | 0.512989 | 48 | 28 | 0 | 20 |
| skill-budget | seed-holdout | relative | 96 | 0.512500 | 47 | 26 | 1 | 22 |
| skill-budget | witness-shift | raw | 96 | 0.845154 | 48 | 8 | 0 | 40 |
| skill-budget | witness-shift | linear_097 | 96 | 0.845154 | 48 | 8 | 0 | 40 |
| skill-budget | witness-shift | log1p | 96 | 0.577350 | 48 | 24 | 0 | 24 |
| skill-budget | witness-shift | sqrt | 96 | 0.593391 | 48 | 23 | 0 | 25 |
| skill-budget | witness-shift | capped4 | 96 | 0.674200 | 48 | 18 | 0 | 30 |
| skill-budget | witness-shift | relative | 96 | 0.561310 | 48 | 25 | 0 | 23 |
| skill-budget | year-holdout | raw | 96 | 0.380319 | 37 | 19 | 11 | 29 |
| skill-budget | year-holdout | linear_097 | 96 | 0.380319 | 37 | 19 | 11 | 29 |
| skill-budget | year-holdout | log1p | 96 | 0.496743 | 48 | 29 | 0 | 19 |
| skill-budget | year-holdout | sqrt | 96 | 0.478755 | 47 | 28 | 1 | 20 |
| skill-budget | year-holdout | capped4 | 96 | 0.297409 | 43 | 31 | 5 | 17 |
| skill-budget | year-holdout | relative | 96 | 0.346977 | 44 | 30 | 4 | 18 |

成立=TP。0.97倍は閾値も同じ単位へ換算する対照で、全群でrawと判定集合が一致することを必須にした。
各候補の修正/新規FP・FNのID集合、登録済みP2/P3/P4/P5の補助評価をresults.jsonへ保存する。
全判定集合はclassifications.jsonl.gz、生成条件と試合ハッシュはcases.jsonl.gz、変換前後の値はobservations.jsonl.gzにある。

## 発見側で固定した候補

| 発見系列 | 候補 | 尺度 | 比較 | 閾値 | 発見MCC |
|---|---|---|---|---:|---:|
| masked-wins | LAB-G01 | raw | < | -0.144000000 | 0.196581 |
| masked-wins | LAB-G02 | linear_097 | < | -0.139680000 | 0.196581 |
| masked-wins | LAB-G03 | log1p | < | -0.001804814 | 0.713822 |
| masked-wins | LAB-G04 | sqrt | < | -0.007585426 | 0.668648 |
| masked-wins | LAB-G05 | capped4 | < | 0.028000000 | 0.743899 |
| masked-wins | LAB-G06 | relative | < | -0.003811693 | 0.746321 |
| skill-budget | LAB-G01 | raw | >= | 0.392000000 | 0.557802 |
| skill-budget | LAB-G02 | linear_097 | >= | 0.380240000 | 0.557802 |
| skill-budget | LAB-G03 | log1p | >= | -0.134416092 | 0.512989 |
| skill-budget | LAB-G04 | sqrt | >= | -0.146106134 | 0.519462 |
| skill-budget | LAB-G05 | capped4 | >= | -0.196000000 | 0.458991 |
| skill-budget | LAB-G06 | relative | >= | -0.045636346 | 0.485768 |

## 尺度で変わった順位（別seed評価）

| 系列 | 尺度 | 攻撃順位が変化 | 失点抑制順位が変化 | 差分順位が変化 |
|---|---|---:|---:|---:|
| masked-wins | raw | 0 | 0 | 0 |
| masked-wins | linear_097 | 0 | 0 | 0 |
| masked-wins | log1p | 143 | 156 | 141 |
| masked-wins | sqrt | 126 | 156 | 137 |
| masked-wins | capped4 | 134 | 156 | 137 |
| masked-wins | relative | 135 | 139 | 138 |
| skill-budget | raw | 0 | 0 | 0 |
| skill-budget | linear_097 | 0 | 0 | 0 |
| skill-budget | log1p | 36 | 46 | 43 |
| skill-budget | sqrt | 30 | 45 | 37 |
| skill-budget | capped4 | 40 | 62 | 59 |
| skill-budget | relative | 42 | 55 | 51 |

## 適用範囲と次の問い

- 2013〜2026年をすべて生成する。各年は独立した架空モデルで、14年連続の組織特性をまだモデル化していない。
- 同リーグ25試合×5相手を既定とする。交流戦・公式日程・公式の同率順位/CS開催規則は再現しない。2020年も架空モデルに含む。
- 真の順位ラベルは元スコアから固定する。補正に合わせて正解ラベルや既存閾値を変更しない。
- witness-shiftはW/L/RF/RAを保ったまま共通得点を集中させる極端な対照。勝敗から組み立てた試合の配分に識別力が依存していないか調べる。
- 最初の試行後に系列別学習・比較方向の探索を追加した事後的設計で、設計中に評価年も閲覧している。未閲覧年での事前登録検証ではない。
- 攻撃/守備の尺度間の順位が入れ替わる球団と、既存条件の通過/不通過を次の命題の材料にする。
- 平均値だけでは非線形変換後の平均を復元できない。実測への適用には試合スコアが必要。
- 実測への適用状態: not-run: raw game scores not supplied。
- 合成データのholdoutは生成仮定内の比較であり、現実の独立確認・因果説明を意味しない。
