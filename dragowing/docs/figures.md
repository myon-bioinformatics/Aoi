# 軌跡・球団×年・条件の重なり・反例カード

`python -m dragowing` は、`cycles/c001-chunichi/outputs` にすでにある JSONL だけを読む。NPB の取得はしない。判定（`evaluate`）は呼ばない。数を丸めて階級に入れない。回帰、平滑化、あてはめの線は描かない。

```bash
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --id P1
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --column wins_vs_pythag
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --cond 'rd,>,0' --cond 'rank_ra,<=,2'
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing --embed
```

`--cond` の値は JSON である（`0`、`true`、`"d"`）。省略すると、`propositions.jsonl` の `if` をファイルの順に見て、`season.jsonl` にある列の原子を 2 個取り、そこに B クラス（`upper_half == false`）を足す。集合は 2 個か 3 個である。

既定の出力は、HTML と、その隣に置く `plotly.min.js` である。`plotly.min.js` は、インストールされた Plotly の `package_data/plotly.min.js` を出力ディレクトリへコピーしたものである。HTML はそれを `src="plotly.min.js"` で読む。Plotly.js を各 HTML に埋め込まない。ブラウザはネットワークに出さない。

`--embed` を付けると、各 HTML に Plotly.js を埋め込む。そのファイルだけを別の場所へ移しても図が出る。`plotly.min.js` は書かない。

| ファイル | 中身 |
|---|---|
| `index.html` | 軌跡、球団×年、条件の重なりと単位の表 |
| `propositions.html` | 命題ごとの 2×2、論理記号、反例カード |
| `plotly.min.js` | 共有の Plotly.js。`--embed` のときは無い |

ページの見出し、カードの見出し、論理記号の囲みは Markdown で書き、Python-Markdown で HTML にする。記録の数と `data-json` は、変換のあとにもファイルの値のまま残す。

文字だけの 2×2 は [forms.md](forms.md) の `dragowing/forms.py` のままである。

PNG が要るときだけ、依存の extra `png`（kaleido）を入れて `--png` を付ける。Chrome もそのときだけ要る。extra が無いと HTML は書いたうえで終了コード 2 になる。テストは kaleido も Chrome も使わない。

`sets.jsonl` はこの結果に無い。条件式のハッセ図（提案の C6）は出していない。成立率をここで新しく計算して色を塗ることもしていない。

## 観測

図に書いてあるのは、記録の列名と値と、次の表示規則だけである。

### 四つの形（提案 C1）と記号（C2）とカード（C7）と 1 ページ（C8）

`propositions.html` は命題 1 件につき 1 節である。節の見出しの印は `registration_status` と同じ三つのどれかである。

| 記録 | 表示 |
|---|---|
| `posthoc` が true | 事後構成 |
| `preregistered` が true、または事前登録の記録がある | 事前登録 |
| それ以外 | 不明 |

2×2 のマスは [forms.md](forms.md) と同じく `n` と `hold` から数える。二つの形が食い違うマスは `不一致` である。空で決まらないマスは `不明` である。四つの形のマスは `hold/n（反例 n-hold）` と、記録に `rate` があるときのその数である。`rate` はファイルの数をそのまま置く。パーセントにはしない。

論理記号の行は `render_logic` の文字列である。`>` を `<=` に書き換えない。

カードは `forms[].counterexamples` の要素 1 個につき 1 枚である。枚数は配列の長さである。2×2 の反例数は `n - hold` である。この結果では両方の数が一致しているが、配列が短い保存なら枚数は配列の長さのままである。カードに載せるのは `unit`、`season`、`team`、`team_name`、`focus`、`values`、`context`、`question` の、記録にあるものだけである。`question` の文は記録の文である。

`statement` を節に出すときは、フィールド名 `statement:` を付けて記録の文として置く。

### 軌跡（提案 C3）

`season.jsonl` の各行を 1 点にする。横は `rank_rf`（得点順位）、縦は `rank_ra`（失点順位）。数値は記録の整数のまま、軸は 1 が原点側である。

点の色は `upper_half` である。`true` を A、`false` を B と書く。`null` は B にしない。

線は、同じ `league` と `team` の行を `season` の昇順で結んだものである。点と点の間に新しい値は置かない。線の形は直線の分だけである。

パネルは記録の `league` ごと（この結果では C と P）である。順位はリーグの中の数なので、パネルを分けてある。

### 球団×年（提案 C4）

図の題は「球団 × 年」である。行のラベルは `team` の記号だけである（`d`、`g`、`s`、`db`、`t`、`c`、`h`、`f`、`b`、`e`、`l`、`m`）。球団名は軸に書かない。上からこの順で、中日 `d` が最上段である。この並びに無い記号は、その後へ記号順で置く。同じ記号が二つのリーグにあるときは `league:team` にして行を分けたままにする。列は `season` の昇順である。既定の列は `wins_vs_pythag`。`--column` で、どの行にも数値（または null）としてある列へ替えられる。文字列の列は拒否する。

色は、そのマスの列の値である。マスに書く文字は `A` か `B` の一字だけである。`upper_half == true` を A、`false` を B とする。null のマスには文字を置かない。数はマスに書かない。行が無いマスの値は null のままで、0 にはしない。

ホバーに出すのは `team`、`team_name`、`season`、`class`（A または B）、`rank`（その行に列があるとき）、その列の値である。値と `rank` は記録の数のまま出す。`upper_half` というフィールド名はホバーに出さない。

### 条件の重なり（提案 C5）

条件ごとに `pythdragoras/rule_search.py` の `_mask` と `_masks_to_matrix` でビット行列を作る。件数は、その bool 行列で領域（入っている / 入っていないの組み合わせ）を数えた整数である。null の比較は真に数えない。これは `_mask` が null を立てないのと同じである。

円は 2 個か 3 個である。円の面積は件数に合わせていない。件数は円の中の整数と、下の表の行である。表の `unit` は `team-season`（例: `d-2012`）で、`team_name` と条件の列の値は `season.jsonl` のその行である。

B は `upper_half == false` という集合の表示名である。

## 解釈

このページは、保存された数と文字列をマスと点とカードに移したものである。

2×2 の数が大きいことを、その命題が正しいことや、次の年も成り立つこととしては読まない。`不明` は「事前登録ではなかった」という意味ではなく、機械的な記録が無い、という表示である。詳しくは [forms.md](forms.md) の解釈と同じである。

軌跡の線は、記録された点の順をつないだものである。傾きを傾向や予測としては読まない。A と B は `upper_half` の表示名で、色が付いている理由の説明ではない。

`wins_vs_pythag` の色は、その数の大小を見やすくしたものである。正や負を、勝ち越しや失敗の判断としては読まない。マスの A と B はクラスの表示名である。ホバーの `rank` は記録された順位で、このページは順位を計算し直さない。

重なりの図は、選んだ条件式が記録の上でどこで同時に真だったかの件数である。式を採用したことや、次に使う規則であることは示さない。円の大きさでは件数を比べない。

カードの `question` は、保存されている問いの文である。このページはその問いに答えない。

候補 ID（`もしかして`）は出さない。問い合わせ側は [ask.md](../../queryu/docs/ask.md)。
