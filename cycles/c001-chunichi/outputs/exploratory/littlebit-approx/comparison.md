# littlebit-approx の探索

このファイルは探索の記録である。確かめの記録は `confirmation.md` に置く。
ファイルの登録区分は posthoc である。exploratory は探索であることの印であり、登録区分の第三の値ではない。
事前登録の証拠はこのファイルに付けていない。

## 観測

- 目的: `upper_half == False`
- 単位数: 156
- 人が書いた候補: 17
- 近似: littlebit_prune.littlebit、判定: rule_search.search
- rank=8、stages=2、seed=0（sign-tie-only）、als_iters=6
- 規則: `canonical-sign-of-F`。行列の形: 156 × 17（単位 × 候補条件）
- 要求した潜在パターン: 16
- 足した候補: 16、落とした潜在パターン: 0
- 符号が同数だった軸: 2
- ビット集合と既定の判定が一致: True
- 残差の平均エネルギー: 1.113361887687446
- 残差の手がかり: 80 / 156

落とした理由の内訳:

- （なし）

成立は前件が真かつ目的が真の単位数（tp）。反例は前件が真かつ目的が偽の単位数（fp）。


### 既存の候補だけ

| 順位 | MCC | 成立 | 反例 | 条件数 | 入った派生列 | 式 |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.820782681668 | 70 | 6 | 3 | — | [sim_p_upper < 0.4] または [rd < 50 かつ alloc_z_strat < -1] |
| 2 | 0.820782681668 | 70 | 6 | 4 | — | [sim_p_upper < 0.4 かつ rd < 50] または [rd < 50 かつ alloc_z_strat < -1] |
| 3 | 0.819149508429 | 64 | 1 | 3 | — | [rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] |
| 4 | 0.819149508429 | 64 | 1 | 4 | — | [sim_p_upper < 0.3 かつ rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] |
| 5 | 0.819149508429 | 64 | 1 | 4 | — | [sim_p_upper < 0.4 かつ rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] |
| 6 | 0.819149508429 | 64 | 1 | 4 | — | [sim_p_upper < 0.5 かつ rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] |
| 7 | 0.819149508429 | 64 | 1 | 4 | — | [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [sim_p_upper < 0.6 かつ rd < -50] |
| 8 | 0.815845917721 | 65 | 2 | 3 | — | [rd < -50] または [sim_p_upper < 0.6 かつ wins_vs_pythag < 0] |
| 9 | 0.815845917721 | 76 | 13 | 3 | — | [sim_p_upper < 0.5] または [alloc_z_strat < -1 かつ one_run_net < 0] |
| 10 | 0.815845917721 | 65 | 2 | 4 | — | [sim_p_upper < 0.3 かつ rd < -50] または [sim_p_upper < 0.6 かつ wins_vs_pythag < 0] |
| 11 | 0.815845917721 | 65 | 2 | 4 | — | [sim_p_upper < 0.4 かつ rd < -50] または [sim_p_upper < 0.6 かつ wins_vs_pythag < 0] |
| 12 | 0.815845917721 | 65 | 2 | 4 | — | [sim_p_upper < 0.5 かつ rd < -50] または [sim_p_upper < 0.6 かつ wins_vs_pythag < 0] |
| 13 | 0.815845917721 | 76 | 13 | 4 | — | [sim_p_upper < 0.5 かつ rd < 50] または [alloc_z_strat < -1 かつ one_run_net < 0] |
| 14 | 0.815845917721 | 65 | 2 | 4 | — | [sim_p_upper < 0.6 かつ rd < -50] または [sim_p_upper < 0.6 かつ wins_vs_pythag < 0] |
| 15 | 0.809356899351 | 73 | 10 | 2 | — | [sim_p_upper < 0.4] または [alloc_z_strat < -1] |
| 16 | 0.809356899351 | 73 | 10 | 3 | — | [alloc_z_strat < -1] または [sim_p_upper < 0.4 かつ rd < 50] |
| 17 | 0.809356899351 | 73 | 10 | 3 | — | [sim_p_upper < 0.4] または [wins_vs_pythag < 0 かつ alloc_z_strat < -1] |
| 18 | 0.809356899351 | 73 | 10 | 3 | — | [sim_p_upper < 0.5] または [rd < 50 かつ alloc_z_strat < -1] |
| 19 | 0.809356899351 | 73 | 10 | 4 | — | [sim_p_upper < 0.4 かつ rd < 50] または [wins_vs_pythag < 0 かつ alloc_z_strat < -1] |
| 20 | 0.809356899351 | 73 | 10 | 4 | — | [sim_p_upper < 0.5 かつ rd < 50] または [rd < 50 かつ alloc_z_strat < -1] |

### 既存の候補に派生候補を足したもの

| 順位 | MCC | 成立 | 反例 | 条件数 | 入った派生列 | 式 |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.820782681668 | 70 | 6 | 3 | — | [sim_p_upper < 0.4] または [rd < 50 かつ alloc_z_strat < -1] |
| 2 | 0.820782681668 | 70 | 6 | 4 | `littlebit_s0_k0` | [sim_p_upper < 0.4 かつ littlebit_s0_k0 == True] または [rd < 50 かつ alloc_z_strat < -1] |
| 3 | 0.820782681668 | 70 | 6 | 4 | — | [sim_p_upper < 0.4 かつ rd < 50] または [rd < 50 かつ alloc_z_strat < -1] |
| 4 | 0.819149508429 | 64 | 1 | 3 | — | [rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] |
| 5 | 0.819149508429 | 64 | 1 | 4 | — | [sim_p_upper < 0.3 かつ rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] |
| 6 | 0.819149508429 | 64 | 1 | 4 | `littlebit_s0_k4` | [sim_p_upper < 0.4 かつ littlebit_s0_k4 == True] または [sim_p_upper < 0.5 かつ one_run_net < 0] |
| 7 | 0.819149508429 | 64 | 1 | 4 | — | [sim_p_upper < 0.4 かつ rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] |
| 8 | 0.819149508429 | 64 | 1 | 4 | `littlebit_s0_k4` | [sim_p_upper < 0.5 かつ one_run_net < 0] または [sim_p_upper < 0.5 かつ littlebit_s0_k4 == True] |
| 9 | 0.819149508429 | 64 | 1 | 4 | — | [sim_p_upper < 0.5 かつ rd < -50] または [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] |
| 10 | 0.819149508429 | 64 | 1 | 4 | `littlebit_s0_k0` | [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < -50 かつ littlebit_s0_k0 == True] |
| 11 | 0.819149508429 | 64 | 1 | 4 | `littlebit_s0_k3` | [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < -50 かつ littlebit_s0_k3 == True] |
| 12 | 0.819149508429 | 64 | 1 | 4 | `littlebit_s1_k0` | [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [rd < -50 かつ littlebit_s1_k0 == True] |
| 13 | 0.819149508429 | 64 | 1 | 4 | — | [sim_p_upper < 0.5 かつ wins_vs_pythag < 0] または [sim_p_upper < 0.6 かつ rd < -50] |
| 14 | 0.815845917721 | 65 | 2 | 3 | — | [rd < -50] または [sim_p_upper < 0.6 かつ wins_vs_pythag < 0] |
| 15 | 0.815845917721 | 76 | 13 | 3 | `littlebit_s1_k2` | [sim_p_upper < 0.5] または [alloc_z_strat < -1 かつ littlebit_s1_k2 == True] |
| 16 | 0.815845917721 | 76 | 13 | 3 | — | [sim_p_upper < 0.5] または [alloc_z_strat < -1 かつ one_run_net < 0] |
| 17 | 0.815845917721 | 65 | 2 | 4 | — | [sim_p_upper < 0.3 かつ rd < -50] または [sim_p_upper < 0.6 かつ wins_vs_pythag < 0] |
| 18 | 0.815845917721 | 65 | 2 | 4 | — | [sim_p_upper < 0.4 かつ rd < -50] または [sim_p_upper < 0.6 かつ wins_vs_pythag < 0] |
| 19 | 0.815845917721 | 76 | 13 | 4 | `littlebit_s0_k0`, `littlebit_s1_k2` | [sim_p_upper < 0.5 かつ littlebit_s0_k0 == True] または [alloc_z_strat < -1 かつ littlebit_s1_k2 == True] |
| 20 | 0.815845917721 | 76 | 13 | 4 | `littlebit_s0_k0` | [sim_p_upper < 0.5 かつ littlebit_s0_k0 == True] または [alloc_z_strat < -1 かつ one_run_net < 0] |

### 球団年ごとの判定集合

既存最良式との比較。全単位のID、TP/FP/FN/TN集合、共通部分と両方向の差分は comparison.json の `unit_comparison` に保存する。
FP修正は既存FP→TN、FN修正は既存FN→TP。新規誤りと合わせて評価する。

| 順位 | 判定集合一致 | FP修正 | FN修正 | 新規FP | 新規FN |
|---:|---|---|---|---|---|
| 1 | True | — | — | — | — |
| 2 | True | — | — | — | — |
| 3 | True | — | — | — | — |
| 4 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | e-2012, t-2016 | — | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 5 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | e-2012, t-2016 | — | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 6 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | t-2016 | — | c-2015, d-2019, e-2023, g-2017, g-2022, m-2012, m-2019 |
| 7 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | e-2012, t-2016 | — | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 8 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | t-2016 | — | c-2015, d-2019, e-2023, g-2017, g-2022, m-2012, m-2019 |
| 9 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | e-2012, t-2016 | — | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 10 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | e-2012, t-2016 | — | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 11 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | e-2012, t-2016 | — | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 12 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | e-2012, t-2016 | — | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 13 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | e-2012, t-2016 | — | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 14 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | d-2014, e-2012, t-2016 | l-2022 | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 15 | False | — | c-2019, e-2012, h-2013, h-2021, l-2015, t-2016 | db-2019, g-2018, l-2012, m-2023, t-2019, t-2022, t-2025 | — |
| 16 | False | — | c-2019, e-2012, h-2013, h-2021, l-2015, t-2016 | db-2019, g-2018, l-2012, m-2023, t-2019, t-2022, t-2025 | — |
| 17 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | d-2014, e-2012, t-2016 | l-2022 | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 18 | False | db-2017, m-2013, m-2015, s-2012, t-2014 | d-2014, e-2012, t-2016 | l-2022 | c-2015, c-2021, d-2019, e-2023, g-2017, g-2022, m-2019, m-2022 |
| 19 | False | — | c-2019, e-2012, h-2013, h-2021, l-2015, t-2016 | db-2019, g-2018, l-2012, m-2023, t-2019, t-2022, t-2025 | — |
| 20 | False | — | c-2019, e-2012, h-2013, h-2021, l-2015, t-2016 | db-2019, g-2018, l-2012, m-2023, t-2019, t-2022, t-2025 | — |

上位20式中18式は既存上位式のいずれかと判定集合が一致する。
この比較は探索に使った同じ標本での記述であり、独立検証ではない。目的列を因子分解に渡さなくても、式の選択は目的列で採点される。
独立検証は未実施。式・変換・設定を固定し、未使用の球団年に適用して評価する必要がある。保存済みloading_unitsは標本内のマスクであり、新しい球団年への外挿器ではない。
`matching_baseline_top_ranks` は既存上位式との集合一致を示す。一致がなくても既存候補全体で表現不能という証明ではない。
同一判定の式は追加の識別能力を示さない。誤りの修正があっても新規誤りと相殺される場合は改善と扱わない。


### 上位に入った派生候補

- `littlebit_s0_k0` stage=0 pattern=0 sign=-1 n_loading=150 source=littlebit-approx rank=8 seed=0 registration=posthoc exploratory=True rule=canonical-sign-of-F
  - weight 1.5921236: rank_ra >= 3
  - weight 1.5577685: rd < 50
  - weight 1.3502817: sim_p_upper < 0.6
  - weight 1.2886966: sim_p_upper < 0.5
  - weight 1.2874928: rank_ra >= 4
  - weight 1.2760902: rd < 0
  - weight 1.2376281: wins_vs_pythag < 0
  - weight 1.1942708: sim_p_upper < 0.4
  - weight 1.1418035: rank_rf >= 4
  - weight 1.1063657: bat_d_r_runner < 0
  - weight 0.92389187: one_run_net < 0
  - weight 0.8423792: sim_p_upper < 0.3
  - weight 0.80378741: rank_rf >= 5
  - weight 0.75733069: rd < -50
  - weight 0.59664597: wins_vs_pythag < -2
  - weight 0.42181021: alloc_z_strat < -1
  - weight 0.34324393: wins_vs_pythag < -4

- `littlebit_s0_k4` stage=0 pattern=4 sign=-1 n_loading=89 source=littlebit-approx rank=8 seed=0 registration=posthoc exploratory=True rule=canonical-sign-of-F
  - weight 1.5921236: rank_ra >= 3
  - weight -1.5577685: rd < 50
  - weight -1.3502817: sim_p_upper < 0.6
  - weight -1.2886966: sim_p_upper < 0.5
  - weight 1.2874928: rank_ra >= 4
  - weight -1.2760902: rd < 0
  - weight 1.2376281: wins_vs_pythag < 0
  - weight -1.1942708: sim_p_upper < 0.4
  - weight 1.1418035: rank_rf >= 4
  - weight 1.1063657: bat_d_r_runner < 0
  - weight -0.92389187: one_run_net < 0
  - weight 0.8423792: sim_p_upper < 0.3
  - weight 0.80378741: rank_rf >= 5
  - weight 0.75733069: rd < -50
  - weight 0.59664597: wins_vs_pythag < -2
  - weight -0.42181021: alloc_z_strat < -1
  - weight 0.34324393: wins_vs_pythag < -4

- `littlebit_s0_k3` stage=0 pattern=3 sign=1 n_loading=78 source=littlebit-approx rank=8 seed=0 registration=posthoc exploratory=True rule=canonical-sign-of-F
  - weight -1.5921236: rank_ra >= 3
  - weight -1.5577685: rd < 50
  - weight 1.3502817: sim_p_upper < 0.6
  - weight 1.2886966: sim_p_upper < 0.5
  - weight -1.2874928: rank_ra >= 4
  - weight 1.2760902: rd < 0
  - weight -1.2376281: wins_vs_pythag < 0
  - weight 1.1942708: sim_p_upper < 0.4
  - weight -1.1418035: rank_rf >= 4
  - weight -1.1063657: bat_d_r_runner < 0
  - weight 0.92389187: one_run_net < 0
  - weight 0.8423792: sim_p_upper < 0.3
  - weight 0.80378741: rank_rf >= 5
  - weight 0.75733069: rd < -50
  - weight 0.59664597: wins_vs_pythag < -2
  - weight 0.42181021: alloc_z_strat < -1
  - weight 0.34324393: wins_vs_pythag < -4

- `littlebit_s1_k0` stage=1 pattern=0 sign=1 n_loading=85 source=littlebit-approx rank=8 seed=0 registration=posthoc exploratory=True rule=canonical-sign-of-F
  - weight -1.7968801: wins_vs_pythag < 0
  - weight -1.6193123: wins_vs_pythag < -2
  - weight -1.3553683: one_run_net < 0
  - weight 1.2994251: rd < 50
  - weight 1.2188358: bat_d_r_runner < 0
  - weight -1.151903: alloc_z_strat < -1
  - weight -1.0365883: rank_ra >= 3
  - weight -0.90837828: wins_vs_pythag < -4
  - weight 0.8397204: sim_p_upper < 0.6
  - weight 0.83940683: sim_p_upper < 0.3
  - weight 0.8181374: rank_rf >= 4
  - weight 0.71720377: rd < 0
  - weight 0.71661341: rd < -50
  - weight -0.57785491: rank_rf >= 5
  - weight 0.5648462: sim_p_upper < 0.4
  - weight 0.54922787: sim_p_upper < 0.5
  - weight 0.50044653: rank_ra >= 4

- `littlebit_s1_k2` stage=1 pattern=2 sign=-1 n_loading=94 source=littlebit-approx rank=8 seed=0 registration=posthoc exploratory=True rule=canonical-sign-of-F
  - weight -1.7968801: wins_vs_pythag < 0
  - weight -1.6193123: wins_vs_pythag < -2
  - weight 1.3553683: one_run_net < 0
  - weight 1.2994251: rd < 50
  - weight 1.2188358: bat_d_r_runner < 0
  - weight -1.151903: alloc_z_strat < -1
  - weight 1.0365883: rank_ra >= 3
  - weight 0.90837828: wins_vs_pythag < -4
  - weight -0.8397204: sim_p_upper < 0.6
  - weight -0.83940683: sim_p_upper < 0.3
  - weight 0.8181374: rank_rf >= 4
  - weight -0.71720377: rd < 0
  - weight -0.71661341: rd < -50
  - weight -0.57785491: rank_rf >= 5
  - weight -0.5648462: sim_p_upper < 0.4
  - weight -0.54922787: sim_p_upper < 0.5
  - weight -0.50044653: rank_ra >= 4

### 足した派生候補

| 列 | 段 | 軸 | 乗った単位 | 登録 |
|---|---:|---:|---:|---|
| `littlebit_s0_k0` | 0 | 0 | 150 | posthoc |
| `littlebit_s0_k1` | 0 | 1 | 83 | posthoc |
| `littlebit_s0_k2` | 0 | 2 | 83 | posthoc |
| `littlebit_s0_k3` | 0 | 3 | 78 | posthoc |
| `littlebit_s0_k4` | 0 | 4 | 89 | posthoc |
| `littlebit_s0_k5` | 0 | 5 | 84 | posthoc |
| `littlebit_s0_k6` | 0 | 6 | 82 | posthoc |
| `littlebit_s0_k7` | 0 | 7 | 87 | posthoc |
| `littlebit_s1_k0` | 1 | 0 | 85 | posthoc |
| `littlebit_s1_k1` | 1 | 1 | 76 | posthoc |
| `littlebit_s1_k2` | 1 | 2 | 94 | posthoc |
| `littlebit_s1_k3` | 1 | 3 | 75 | posthoc |
| `littlebit_s1_k4` | 1 | 4 | 89 | posthoc |
| `littlebit_s1_k5` | 1 | 5 | 75 | posthoc |
| `littlebit_s1_k6` | 1 | 6 | 83 | posthoc |
| `littlebit_s1_k7` | 1 | 7 | 84 | posthoc |

### 残差の手がかり

| 単位 | 球団年の残差エネルギー | 満たした候補の数 |
|---|---:|---:|
| d-2014 | 2.616752 | 8 |
| d-2015 | 2.380503 | 13 |
| c-2024 | 2.319796 | 10 |
| h-2013 | 2.251479 | 6 |
| l-2022 | 2.215461 | 7 |
| l-2017 | 2.173180 | 5 |
| f-2018 | 2.131827 | 5 |
| f-2019 | 2.124390 | 11 |
| t-2016 | 2.114899 | 10 |
| c-2022 | 2.074249 | 10 |
| e-2012 | 2.018446 | 7 |
| t-2021 | 2.011334 | 3 |
| t-2019 | 1.967210 | 7 |
| m-2021 | 1.960154 | 5 |
| c-2023 | 1.946714 | 7 |
| l-2015 | 1.942499 | 7 |
| g-2025 | 1.940036 | 4 |
| h-2012 | 1.925232 | 7 |
| l-2016 | 1.852316 | 11 |
| m-2012 | 1.844205 | 10 |
| m-2016 | 1.781785 | 4 |
| g-2019 | 1.747746 | 4 |
| s-2018 | 1.700922 | 5 |
| m-2024 | 1.700922 | 5 |
| db-2023 | 1.673172 | 4 |
| b-2013 | 1.650898 | 11 |
| l-2023 | 1.650898 | 11 |
| b-2024 | 1.650898 | 11 |
| t-2013 | 1.643414 | 6 |
| db-2022 | 1.628676 | 6 |
| db-2021 | 1.625134 | 12 |
| l-2024 | 1.621561 | 14 |
| s-2013 | 1.605806 | 14 |
| e-2022 | 1.586093 | 9 |
| g-2017 | 1.584272 | 6 |
| l-2014 | 1.582685 | 14 |
| db-2016 | 1.555349 | 5 |
| b-2025 | 1.555349 | 5 |
| c-2021 | 1.544299 | 10 |
| t-2022 | 1.534977 | 8 |
| h-2019 | 1.503524 | 3 |
| m-2019 | 1.499513 | 7 |
| e-2021 | 1.497406 | 5 |
| g-2021 | 1.497327 | 6 |
| m-2022 | 1.488467 | 8 |
| g-2015 | 1.477167 | 5 |
| l-2013 | 1.475960 | 4 |
| s-2019 | 1.472535 | 13 |
| m-2015 | 1.425641 | 8 |
| b-2018 | 1.420387 | 9 |
| g-2024 | 1.393734 | 4 |
| f-2023 | 1.391829 | 15 |
| f-2015 | 1.377214 | 3 |
| s-2014 | 1.371680 | 13 |
| s-2023 | 1.371680 | 13 |
| t-2012 | 1.361376 | 14 |
| e-2019 | 1.353997 | 5 |
| c-2012 | 1.334749 | 9 |
| b-2015 | 1.323623 | 13 |
| l-2012 | 1.320095 | 6 |
| db-2019 | 1.320095 | 6 |
| db-2013 | 1.297351 | 10 |
| g-2016 | 1.283196 | 4 |
| d-2016 | 1.268528 | 15 |
| c-2025 | 1.268528 | 15 |
| g-2014 | 1.267646 | 2 |
| f-2024 | 1.257160 | 2 |
| d-2019 | 1.253993 | 9 |
| h-2024 | 1.211960 | 3 |
| f-2025 | 1.211960 | 3 |
| g-2022 | 1.202847 | 8 |
| c-2013 | 1.200395 | 5 |
| m-2014 | 1.175315 | 11 |
| d-2021 | 1.174375 | 11 |
| db-2024 | 1.163624 | 5 |
| t-2018 | 1.159216 | 12 |
| h-2023 | 1.158694 | 5 |
| b-2017 | 1.150812 | 13 |
| d-2018 | 1.150812 | 13 |
| d-2022 | 1.113935 | 10 |

単位ごとの残差エネルギー全体は comparison.json の `residual_units` にある。

## 解釈

この節は、上の数をどう読むかである。次の年に成り立つという主張は、ここには書かない。

上位の式は、この表の上での Matthews 相関係数の順序である。因子の近似値そのものは、成立の証拠にしていない。成立と反例は、保存した 0/1 を既存のビット演算で数えた数である。

残差の手がかりは、候補条件の行列を因子が再構成しきれなかった球団年である。目的の真偽で選んだ一覧ではない。その単位を判例だと決めた一覧でもない。あとで判例を探すときの順番として残してある。

rank、stages、seed は、枝刈り側のコマンド既定（rank 8、stages 2）と seed 0 に固定してある。この並びを見たあとで動かした値ではない。符号の同点以外では、seed は軸の向きを変えない。

ここに並んだ式を命題ファイルへ移す作業は、この記録の外である。確かめは confirmation.md の手続きで行う。
