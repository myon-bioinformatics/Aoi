# サイクル3: 出口の数（刻みで進める計算のずれ）

1 つの槽から出口が何本か出ているとき、刻み dt で進める計算の「残り」は、厳密な答えからどれだけ外れるか。
出典は [FluidFullSpeedSimulation](https://github.com/myon-bioinformatics/FluidFullSpeedSimulation) の E29 🚿 `outlet-count`。
野球（[サイクル1](../c001-chunichi/README.md)）とも米価（[サイクル2](../c002-gohantrust/README.md)）とも違い、**答えが式で分かっている**題材。
説明を命題にして、どこで成り立たなくなるかを判例で見る手順は同じ（[docs/propositions.md](../../docs/propositions.md)）。

## 進め方

1. 命題を書いて固定する（[`propositions.toml`](propositions.toml)。単位を作る前のコミット）
2. 単位を作る（FluidFullSpeedSimulation のエンジンで計算）
3. 別実装で検算する（エンジンを使わない素の漸化式）
4. PythDRagoras で 4 つの形を判定し、判例を並べる
5. 報告を書く。結果を見て出た着想は「未検討」に置くだけで、その場では走らせない

## 状況

事前登録を固定しただけ。単位はまだ作っていない。
