# littlebit-approx

候補条件のマスクから潜在パターンを作り、PythDRagoras の条件候補に足す。共通識別子は `littlebit-approx`。

成否の判定は [rule_search.py](../rule_search.py) のビット演算である。因子の計算は [littlebit_prune.py](../littlebit_prune.py) の `littlebit`（低ランク、符号による二値、行スケール・列スケール・潜在スケール、残差の段）を使う。公式の LittleBit カーネルは使わない。

## 行列

`indicator_matrix` は単位 × 候補条件の 0/1 行列である。列 j は `search` がすでに作っているマスク（`_mask`）と同じである。目的の列（B クラスの `upper_half` など）は、この行列に入れない。`derive` は target を受け取らない。

行を `search` と揃える作業（除外、目的や候補が空の行を落とすこと）は、呼び出す側が `search` と同じ表を渡す。

## 載るかどうか

`littlebit` の各段、各潜在軸 k について、単位側の因子を `F[:, k]` とする。`littlebit` の定義では、これは行スケール h、符号二値 Us、潜在スケール l の積である。列側は符号二値 Vs と列スケール g である。

軸の符号 s は +1 または -1 である。

- `np.sign(F[:, k])` の和が正なら s = +1
- 和が負なら s = -1
- 和が 0（正と負が同数）のときだけ seed を使う。seed から作った乱数の最初の 1 ビットが 0 なら、最初の非ゼロ成分が正になる向き、1 なら負になる向きを s とする

単位 i がパターン k に乗るのは `s * F[i, k] > 0` のときである。0 ちょうどは乗らない。これは因子の符号であり、.040 や .060 のような境界をデータに合わせて刻む手続きではない。

列 j の重みは `w_j = s * g_j * Vs[j, k]` である。再構成のその軸の寄与は `(s * F[:, k])` と `w` の積に戻る（s を両側に掛けると s² = 1 で元の積になる）。重みは、束ねた元の条件との算術的なつながりとして候補に残す。

列スケール g は、その段の中では条件ごとに一つである。潜在軸ごとの違いは、符号 `Vs[j, k]` と単位側の `F[:, k]` に出る。同じ段では、重みの絶対値は軸が違っても一致し、符号の並びが軸を分ける。

既定は rank=8、stages=2、seed=0、交互最小二乗は `littlebit` の既定 6 回である。rank と stages は枝刈りコマンドの既定と同じで、探索結果の MCC を見てから選んだ値ではない。同点以外では seed は軸を変えず、記録にだけ残る。

## 条件にしなかった軸

人が書いた候補は消さない。要求した `rank * stages` 本のうち、次の軸は新しい条件にしない。

| 理由 | 内容 |
|---|---|
| `zero-factor` | F の列が全部 0 |
| `constant-mask` | 乗る単位が 0 か、全員 |
| `duplicate-mask` | すでに足したパターンと同じ 0/1 |
| `rank-shortfall` | SVD の成分が rank に足りない |
| `no-units` / `no-candidates` | 行列が空 |

足した数と落とした数の和は、要求した本数と一致する。設定（rank、stages、seed）と、この二つの数は、比較の記録に残す。

## 出どころ

各派生候補は次を持つ。

- `source` = `littlebit-approx`
- `rank`、`seed`、`stage`、`pattern`
- `bundle`: 元の条件（`col`、`op`、`value`）と `weight`
- `posthoc` = true、`exploratory` = true
- `registration`: [registration_audit.py](../registration_audit.py) の `classify` の結果

この作り方は結果を見たあとの条件なので、`classify` は posthoc を返す。`exploratory` は探索であることの印であり、posthoc / preregistered / unknown に次の値を足すものではない。事前登録にするには、[registration-metadata-audit.md](../../docs/registration-metadata-audit.md) のとおり、評価より前に記録した証拠が要る。ここにはその証拠を付けない。

`search` は `col`、`op`、`value` だけでマスクを作り、並べる鍵もその三つだけを見る。上の記録が付いていても、成立・反例の数は変わらない。

## 残差

残差エネルギーは、条件行列と再構成の差の二乗を、単位ごとに足したものである。全単位の平均より大きい単位を、判例を探す手がかり（`lead`）にする。平均ちょうどは手がかりにしない。目的の列の真偽では分けない。

手がかりは「この球団年は候補の並びを因子が再構成しきれなかった」という記録である。その単位を判例だと決めた一覧は、[propositions.md](../../docs/propositions.md) の判定で別に残す。

## c001 の並び

c001 では、既存の候補だけを `search` に渡した上位と、派生候補を足して `search` に渡した上位を並べ、`cycles/c001-chunichi/outputs/exploratory/littlebit-approx/` に書く。観測と解釈は [comparison.md](../../cycles/c001-chunichi/outputs/exploratory/littlebit-approx/comparison.md) で節を分けている。機械向けの全体は同じディレクトリの `comparison.json` である。

確かめの記録は [confirmation.md](../../cycles/c001-chunichi/outputs/confirmation.md) に置く。候補ファイルは [rule_candidates.toml](../../cycles/c001-chunichi/rule_candidates.toml)。再生成は次である。

```bash
uv run python pythdragoras/littlebit_approx.py
```
