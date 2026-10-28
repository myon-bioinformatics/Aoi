# 軌跡・球団×年・条件の重なり・命題の一覧

`python -m dragowing` は、`cycles/c001-chunichi/outputs` にすでにある JSONL だけを読む。NPB の取得はしない。判定（`evaluate`）は呼ばない。数を丸めて階級に入れない。回帰、平滑化、あてはめの線は描かない。

```bash
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --id P1
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --column wins_vs_pythag
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --cond 'rd,>,0' --cond 'rank_ra,<=,2'
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --embed
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --team-order d,g,s   # 球団×年の上からの並び。省略すると記号順
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --png --svg
```

`--cond` の値は JSON である（`0`、`true`、`"d"`）。省略すると、`propositions.jsonl` の `if` をファイルの順に見て、`season.jsonl` にある列の原子を 2 個取り、そこに B クラス（`upper_half == false`）を足す。集合は 2 個か 3 個である。`--cond` を繰り返すと B クラスを足して 2〜8 個まで使える（4 集合以上は格子で読む。下の「条件の重なり」）。重なりの内訳は `--breakdown 列`（既定 `team`）と `--breakdown-keep 値`（繰り返せる）で選ぶ。

既定では、`index.html` が jsDelivr の Plotly.js（`https://cdn.jsdelivr.net/npm/plotly.js-dist-min/plotly.min.js`、SRI なし）を読む。`propositions.html` は Plotly を読まない。出力先へ `plotly.min.js` はコピーしない。Python パッケージ `plotly` は依存に置かない。

`--embed` を付けると、`index.html` に Plotly.js を埋め込む。`propositions.html` は埋め込まない。

| ファイル | 中身 |
|---|---|
| `index.html` | 軌跡、球団×年、条件の重なり（格子と内訳）、領域の件数と単位の表 |
| `propositions.html` | 先頭の一覧と、命題ごとの 2×2、論理記号、反例の表 |

ページの見出し、一覧、2×2、反例の表、論理記号の囲みは Markdown で書き、Python-Markdown で HTML にする。数は変換のあとにもファイルの値のまま残す。丸めない。

文字だけの 2×2 は [forms.md](forms.md) の `dragowing/forms.py` のままである。

文字は図もページも `figures.FONT`（`Meiryo, メイリオ, sans-serif`）で揃える。フォントファイルは同梱しないので、メイリオが入っていない環境（Mac・iPhone・Linux、`--png` / `--svg` を書き出す Chrome も含む）では OS 既定の sans-serif で表示される。字形を完全に揃えたいときは、見る側にメイリオを入れる。

PNG / SVG が要るときだけ `--png` / `--svg` を付ける。Chrome もそのときだけ要る（`--chrome` または `CHROME` 環境変数）。Chrome が無いと HTML は書いたうえで終了コード 2 になる。テストは Chrome も使わない。

`sets.jsonl` はこの結果に無い。条件式のハッセ図（提案の C6）は出していない。成立率をここで新しく計算して色を塗ることもしていない。

配布契約は web-ui の単一ファイルを `vendor.lock.json` の正確なコミットと
ファイルハッシュで固定して共用する。版・URL・期待 SHA-256・SRI・8 MiB の上限・
取得と検証はそこで管理し、DRAgoWing は重複定義しない。
`--embed` は固定 URL の bytes をハッシュ照合してから UTF-8 に変換し、
HTML raw-text 終端を検査して埋め込む。HTTP エラー・取得失敗・サイズ超過・
CDN 内容不一致・改変はエラーで停止し、成功 bytes だけをプロセス内キャッシュに置く。
版更新は upstream の契約更新と lock 更新を一組で行う。

web-ui の `remote_scripts` / `remote_script_tag` / `fetch_plotly_js` を共用する。
`plotly_figure` は `ui-panel` と inline 初期化を返すため、既存の
`application/json` 図形ブロック・ID・CSS・DRAgoWing 初期化は維持する。
PNG/SVG API と CLI `--png` は `export_draw` と同じ CDN 契約の Plotly.js を一時ディレクトリへコピーして使う。

## 観測

図に書いてあるのは、記録の列名と値と、次の表示規則だけである。

### 一覧と四つの形（提案 C1）と記号（C2）と反例の表（C7）と 1 ページ（C8）

`propositions.html` の先頭は一覧である。1 行が 1 命題で、ID、`statement`、四つの形それぞれの `hold`、反例（`n - hold`）、`rate` を置く。ID は同じページの節へのリンクである。`rate` はファイルの数のまま置く。ここでは計算し直さない。形が無い、または `n` と `hold` から数が決まらないときは `不明` である。

その下は命題 1 件につき 1 節である。節の見出しの印は `registration_status` と同じ三つのどれかである。

| 記録 | 表示 |
|---|---|
| `posthoc` が true | 事後構成 |
| `preregistered` が true、または事前登録の記録がある | 事前登録 |
| それ以外 | 不明 |

2×2 のマスは [forms.md](forms.md) と同じく `n` と `hold` から数える。Markdown の表にする。Plotly の表にはしない。二つの形が食い違うマスは `不一致` である。空で決まらないマスは `不明` である。四つの形はもう一つの 2×2 で、`hold/n（反例 n-hold）` と、記録に `rate` があるときのその数である。`rate` はファイルの数をそのまま置く。パーセントにはしない。

論理記号の行は `render_logic` の文字列である。`>` を `<=` に書き換えない。

反例は形ごとに 1 つの表で、1 行が `counterexamples` の 1 要素である。元と対偶、逆と裏が同じ単位の並びなら 1 表にまとめ、文でそう書く。並びが違うときだけ両方を出し、見出しに `不一致` と書く。表は `<details>` に入れ、初めは畳んである。並びは記録の順で、`|surprise|` の降順、同点は `season`、次に `team` である。行数は配列の長さである。2×2 の反例数は `n - hold` である。列は記録にある `unit`、`season`、`team`、`team_name`、`focus`、`surprise`、`question`、`values`、`context` である。`excluded_counterexamples` と `held_out` も同じ列で別節に置く。空の前件で ¬P 行に置く 0 は `0（前件が空）` と書く。`values` と `context` は JSON の文字のまま置く。

`statement` を節に出すときは、フィールド名 `statement:` を付けて記録の文として置く。

### 軌跡（提案 C3）

`season.jsonl` の各行を 1 点にする。横は `rank_rf`（得点順位）、縦は `rank_ra`（失点順位）。数値は記録の整数のまま、軸は 1 が原点側である。

点の色は `upper_half` である。`true` を A、`false` を B と書く。`null` は B にしない。

線は、同じ `league` と `team` の行を `season` の昇順で結んだものである。点と点の間に新しい値は置かない。線の形は直線の分だけである。

パネルは記録の `league` ごと（この結果では C と P）である。順位はリーグの中の数なので、パネルを分けてある。

### 球団×年（提案 C4）

図の題は「球団 × 年」である。行のラベルは `team` の記号だけである（`d`、`g`、`s`、`db`、`t`、`c`、`h`、`f`、`b`、`e`、`l`、`m`）。球団名は軸に書かない。上からこの順で、中日 `d` が最上段である。この並びに無い記号は、その後へ記号順で置く。同じ記号が二つのリーグにあるときは `league:team` にして行を分けたままにする。列は `season` の昇順である。既定の列は `wins_vs_pythag`。`--column` で、どの行にも数値（または null）としてある列へ替えられる。文字列の列は拒否する。

色は、そのマスの列の値である（`sigma_band` ではない）。図の近くに `zmin` と `zmax` を置く。マスに書く文字は `A` か `B` の一字だけである。`upper_half == true` を A、`false` を B とする。null のマスには文字を置かない。数はマスに書かない。行が無いマスの値は null のままで、0 にはしない。

ホバーに出すのは `team`、`team_name`、`season`、`class`（A または B）、`rank`（その行に列があるとき）、その列の値である。値と `rank` は記録の数のまま出す。`upper_half` というフィールド名はホバーに出さない。

### 条件の重なり（提案 C5）

条件ごとに `pythdragoras/rule_search.py` の `_mask` と `_masks_to_matrix` でビット行列を作る。件数は、その bool 行列で領域（入っている / 入っていないの組み合わせ）を数えた整数である。null の比較は真に数えない。これは `_mask` が null を立てないのと同じである。

円は描かない。件数は領域の表の整数である。下の表の `unit` は `team-season`（例: `d-2012`）で、`team_name` と条件の列の値は `season.jsonl` のその行である。

B は `upper_half == false` という集合の表示名である。

集合は B クラスを含めて 2〜8 個（`overlap.MAX_SETS`）。領域は 2^n 個で、件数 0 の領域も 0 のまま置く。

**格子**（`dragowing/venn.py` の `grid_figure`、図の ID は `overlap_grid`）。面積を件数に合わせた円や楕円は、あてはめになるので使わない。2^n 個の領域を 1 マスずつ、カルノー図の並びの格子に置く。

- 行は前半 n÷2 個（切り捨て）の集合、列は残りの集合。軸の並びはグレイ符号で、先頭の集合が入る側から（4 集合なら 10, 11, 01, 00）。隣のマスは 1 つの集合だけ違う。軸のラベルは、集合の番号順に入る(1)・入らない(0)を並べた文字。
- マスの数は件数で、丸めない。色は件数（一つの色相の薄い→濃い）。数はマスに書き、色の凡例は置かない。
- 集合は枠で示す。行の集合は横長、列の集合は縦長の長方形で、ラベル `S1`…`Sn` と凡例（条件式）で対応する。格子の並びの性質で、集合の入る範囲が離れた帯になることがある（5 集合以上）。その場合は帯ごとに枠を描く。
- 枠は格子の外へはみ出して描くため、図形は paper 座標にしている（軸の座標だと格子の外が切れる）。

**内訳**（`breakdown_figure`、図の ID は `overlap_breakdown`）。件数が 1 以上の領域を 1 行にした横の積み上げ棒で、長さが件数。`unit` の列（`team`、`team_name`、`league`、`season`、`upper_half`。CLI の `--breakdown`、既定は `team`）の値で色を分ける。

- 行は件数の降順（同数は領域の並びの順）。行のラベルは領域の桁と括弧の件数。件数 0 の領域は棒にせず、数を図の題に書く（格子とページの表には出ている）。
- 色は値の昇順で固定の順に割り当てる（件数の順位では塗り替えない）。色を付ける値は 7 個までで、超えた値は灰色の「その他」にまとめ、中身（値と件数）はホバーに出す。`--breakdown-keep d` のように値を指定すると、件数にかかわらず別の色で残す。
- 図の題と `layout.meta`（`by`、`folded`、`empty_regions`、領域ごとの値別の件数）に、まとめたこと・省いたことを書く。

Python から呼ぶときは、Plotly の JSON 仕様（`data` と `layout`）を返すだけで、`plotly` パッケージも numpy も要らない。仕様は JSON なので、ブラウザの `Plotly.newPlot(id, spec.data, spec.layout)` へそのまま渡せる（Node からも同じ）。

```python
from dragowing.overlap import finalize_conditions, load_overlap, parse_cond
from dragowing.records import read_jsonl
from dragowing.venn import venn_figures
from dragowing.htmlout import figure_block, standalone

rows = read_jsonl("season.jsonl")
conds = finalize_conditions([parse_cond(t) for t in ("rd,>,0", "rank_ra,<=,2", "rank_rf,<=,3")], [], rows)  # + B = 4 集合
figs = venn_figures(load_overlap("season.jsonl", conds, backend="stdlib"), by="team", keep=("d",))
page = standalone("重なり", figure_block(figs["overlap_grid"], "g") + figure_block(figs["overlap_breakdown"], "b"), plotly=True)
```

## 解釈

このページは、保存された数と文字列をマスと点と表に移したものである。

2×2 の数が大きいことを、その命題が正しいことや、次の年も成り立つこととしては読まない。`不明` は「事前登録ではなかった」という意味ではなく、機械的な記録が無い、という表示である。詳しくは [forms.md](forms.md) の解釈と同じである。

軌跡の線は、記録された点の順をつないだものである。傾きを傾向や予測としては読まない。A と B は `upper_half` の表示名で、色が付いている理由の説明ではない。

`wins_vs_pythag` の色は、その数の大小を見やすくしたものである。正や負を、勝ち越しや失敗の判断としては読まない。マスの A と B はクラスの表示名である。ホバーの `rank` は記録された順位で、このページは順位を計算し直さない。

重なりの表は、選んだ条件式が記録の上でどこで同時に真だったかの件数である。式を採用したことや、次に使う規則であることは示さない。

格子の並びや枠の入れ子は、集合どうしの近さや因果を示さない。色の濃さは件数の大小を見やすくしたもので、濃い領域が重要という意味ではない。内訳の色は値の昇順に割り当てただけで、値の良し悪しを表さない。「その他」にまとめたことは件数の話で、その値が重要でないことは示さない。

反例の表の `question` は、保存されている問いの文である。このページはその問いに答えない。

候補 ID（`もしかして`）は出さない。問い合わせ側は [ask.md](../../queryu/docs/ask.md)。
