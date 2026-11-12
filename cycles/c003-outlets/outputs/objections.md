# 異議あり — 命題の判定記録（自動生成）

判定基準は結果を見る前に命題ファイルに書いたもの（docs/propositions.md）。
命題ファイル SHA-256: `b8f15568dfa2cbf514166c5524458a4aa68383c6c9e09883d46326febb8353a5` / コード: `09ec9e7`

判定は命題がその範囲で成り立つかどうかだけを示し、原因は示さない。

## 命題の系譜

- O3 → **O18**: 1 次の式を 2 次の式に置き直した（O3 の判例 34 件を受けて）。5 % と範囲は同じ
- O5 → **O16**: 頭打ちを 1 次の見積もり t·dt·K²/2 から、n → ∞ の厳密な形に置き直した（O5 の判例 2 件を受けて）
- O10 → **O20**: 範囲を、厳密な残りが最初の量の 6 割ほど残る条件（gentle）に替えた。O10 は残りが 2.7 % で、割合のずれが大きく出ていた
- O39 → **O45**: 予想の式を、段ごとの足し算から G_eff = G − (dt/2)·(D + G²) に替えた（1 つ飛ばしで引かれる項が入る）。単位は別の組
- O41 → **O47**: 問いは同じ。当たる単位が 8 件で判断保留だったので、別の組（chain3b、刻み 1/256 を足した）で問い直す
- O52 → **O56**: O55 と同じ替え方
- O53 → **O55**: 境目を係数の比 \|a1/b2\| から、その刻みと時刻での 2 つの式の予想の比に替えた（end の 2 次の項を入れた）。単位は別の組で、粗い刻みは使わない

## O1: 弁だけの槽を今の方式で進めるとき、出口が 1 本なら残りは厳密である

- **判定: exit 0 異議なし**（逆・裏まで）
- もし: `n == 1` ならば: `err_abs < 1e-09`
- 識別子: `[where:independent==true, where:valve_only==true] n==1 => err_abs<1e-09`（指紋 `dfd56b381be1fad0`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}]} / 単位数: 110
- 見直す条件（反証）: 出口 1 本で 1e-9 以上ずれる単位が 1 つでもあれば、弁 1 本の厳密さ（1 − e^(−dt/τ)）の前提を見直す
- 注記: 逆（厳密なら 1 本）は「2 本以上なら必ずずれる」と同じことを別の向きから問う
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=1.000, mcc=1.000
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 10 | 10 | 1.00 [0.72, 1.00] | — | 0.09 | 11.00 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 100 | 100 | 1.00 [0.96, 1.00] | — | 0.91 | 1.10 | 0.000 | 0 | 支持 | 0 |
| 逆 | 10 | 10 | 1.00 [0.72, 1.00] | — | 0.09 | 11.00 | 0.000 | 0 | 支持 | 0 |
| 裏 | 100 | 100 | 1.00 [0.96, 1.00] | — | 0.91 | 1.10 | 0.000 | 0 | 支持 | 0 |

## O2: 弁だけの槽を今の方式で進めるとき、出口が 2 本以上なら残りは厳密な答えより少ない（速く空く）

- **判定: exit 0 異議なし**（逆・裏まで）
- もし: `n >= 2` ならば: `err < -1e-09`
- 識別子: `[where:independent==true, where:valve_only==true] n>=2 => err<-1e-09`（指紋 `51b70927f0660365`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}]} / 単位数: 110
- 見直す条件（反証）: 2 本以上で残りが多い（遅く空く）か、ずれない単位があれば、取りすぎの説明（互いの取り分を知らずに取る）を見直す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=1.000, mcc=1.000
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 100 | 100 | 1.00 [0.96, 1.00] | — | 0.91 | 1.10 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 10 | 10 | 1.00 [0.72, 1.00] | — | 0.09 | 11.00 | 0.000 | 0 | 支持 | 0 |
| 逆 | 100 | 100 | 1.00 [0.96, 1.00] | — | 0.91 | 1.10 | 0.000 | 0 | 支持 | 0 |
| 裏 | 10 | 10 | 1.00 [0.72, 1.00] | — | 0.09 | 11.00 | 0.000 | 0 | 支持 | 0 |

## O6: 弁だけの槽を今の方式で進めるとき、合計の速さと刻みが同じなら、出口を増やすほど残りは少なくなる

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `drop_from_fewer < 0`
- 識別子: `[where:equal_split==true, where:independent==true, where:n>=2, where:valve_only==true] * => drop_from_fewer<0`（指紋 `abc9778b58f262c1`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'equal_split', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}]} / 単位数: 50
- 見直す条件（反証）: 本数を増やして残りが増える（か変わらない）組があれば、(1 − 1/n) の単調さを見直す
- 注記: drop_from_fewer = この単位の err − 同じ刻みで 1 つ少ない本数（1→2→3→4→8→16 の並び）の err。単位どうしの比べを列にしたもの
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 50 | 50 | 1.00 [0.93, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O3: 弁だけの槽を今の方式で進めるとき、2 本以上なら、ずれは 1 次の式 −t·dt·(K² − Σk_i²)/2 と 5 % 以内で合う

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 34 件: valve-skew-n2-independent-10, valve-eq-n2-independent-10, valve-skew-n3-independent-10, valve-skew-n2-independent-7, valve-eq-n2-independent-7 ほか
- もし: `（すべての単位）` ならば: `fo_rel <= 0.05`
- 識別子: `[where:independent==true, where:n>=2, where:valve_only==true] * => fo_rel<=0.05`（指紋 `83fa93d44de1cdbe`）
- 兄弟（範囲と結論が同じ、条件が違う）: O4
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}]} / 単位数: 100
- 見直す条件（反証）: 5 % を超える単位があれば、1 次の式が使える刻みの範囲を条件として持つ命題（O4）に譲る
- 注記: 刻みの条件を付けない強い主張。粗い刻みで破れると見込んで書いている（どこで止まるかを判例で見るため）
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.660, recall=1.000, f1=0.795, accuracy=0.660, balanced_accuracy=0.500, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 100 | 66 | 0.66 [0.56, 0.75] | — | 0.66 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 34 | 0 | 0.00 [0.00, 0.10] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 34 件（対偶の判例も同じ）

- 弁 偏り 2 本 independent h=0.74 10: fo_rel=0.193, h=0.740, n=2, equal_split=False, err=-0.485, err_pred=-0.407 / surprise=0.193
  - 弁 偏り 2 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 2 本 independent h=0.74 10: fo_rel=0.190, h=0.740, n=2, equal_split=True, err=-0.489, err_pred=-0.411 / surprise=0.190
  - 弁 2 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 3 本 independent h=0.74 10: fo_rel=0.150, h=0.740, n=3, equal_split=False, err=-0.609, err_pred=-0.529 / surprise=0.150
  - 弁 偏り 3 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 2 本 independent h=0.5 7: fo_rel=0.144, h=0.500, n=2, equal_split=False, err=-0.283, err_pred=-0.248 / surprise=0.144
  - 弁 偏り 2 本 independent h=0.5 7 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 2 本 independent h=0.5 7: fo_rel=0.143, h=0.500, n=2, equal_split=True, err=-0.286, err_pred=-0.250 / surprise=0.143
  - 弁 2 本 independent h=0.5 7 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 3 本 independent h=0.74 10: fo_rel=0.140, h=0.740, n=3, equal_split=True, err=-0.625, err_pred=-0.548 / surprise=0.140
  - 弁 3 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 3 本 independent h=0.5 7: fo_rel=0.128, h=0.500, n=3, equal_split=False, err=-0.363, err_pred=-0.322 / surprise=0.128
  - 弁 偏り 3 本 independent h=0.5 7 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 3 本 independent h=0.5 7: fo_rel=0.123, h=0.500, n=3, equal_split=True, err=-0.374, err_pred=-0.333 / surprise=0.123
  - 弁 3 本 independent h=0.5 7 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 4 本 independent h=0.74 10: fo_rel=0.121, h=0.740, n=4, equal_split=False, err=-0.673, err_pred=-0.601 / surprise=0.121
  - 弁 偏り 4 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 4 本 independent h=0.5 7: fo_rel=0.116, h=0.500, n=4, equal_split=False, err=-0.408, err_pred=-0.366 / surprise=0.116
  - 弁 偏り 4 本 independent h=0.5 7 は「（すべての単位）」を満たすのに「fo_rel <= 0.05」を満たさない。なぜか？
- ほか 24 件（propositions.jsonl を参照）

## O4: 弁だけの槽を今の方式で進めるとき、2 本以上で刻みが時定数の 1/32 以下なら、ずれは 1 次の式と 5 % 以内で合う

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 36 件: valve-skew-n8-independent-6, valve-eq-n8-independent-6, valve-skew-n16-independent-10, valve-eq-n16-independent-10, valve-skew-n16-independent-6 ほか
- もし: `h <= 0.03125` ならば: `fo_rel <= 0.05`
- 識別子: `[where:independent==true, where:n>=2, where:valve_only==true] h<=0.03125 => fo_rel<=0.05`（指紋 `962ebf6a13fa998a`）
- 兄弟（範囲と結論が同じ、条件が違う）: O3
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}]} / 単位数: 100
- 見直す条件（反証）: h ≤ 1/32 で 5 % を超える単位があれば、境（1/32）か式を見直す
- 注記: 逆（5 % 以内なら h ≤ 1/32）の判例は、もっと粗い刻みでも 1 次の式が使える単位を示す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.455, f1=0.625, accuracy=0.640, balanced_accuracy=0.727, mcc=0.470
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 30 | 1.00 [0.89, 1.00] | — | 0.66 | 1.52 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 34 | 34 | 1.00 [0.90, 1.00] | — | 0.70 | 1.43 | 0.000 | 0 | 支持 | 0 |
| 逆 | 66 | 30 | 0.45 [0.34, 0.57] | — | 0.30 | 1.52 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 70 | 34 | 0.49 [0.37, 0.60] | — | 0.34 | 1.43 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 36 件（裏の判例も同じ）

- 弁 偏り 8 本 independent h=0.25 6: h=0.250, fo_rel=0.049, n=8, equal_split=False, err=-0.223, err_pred=-0.213 / surprise=0.049
  - 弁 偏り 8 本 independent h=0.25 6 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 8 本 independent h=0.25 6: h=0.250, fo_rel=0.048, n=8, equal_split=True, err=-0.229, err_pred=-0.219 / surprise=0.048
  - 弁 8 本 independent h=0.25 6 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 16 本 independent h=0.74 10: h=0.740, fo_rel=0.047, n=16, equal_split=False, err=-0.802, err_pred=-0.766 / surprise=0.047
  - 弁 偏り 16 本 independent h=0.74 10 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 16 本 independent h=0.74 10: h=0.740, fo_rel=0.045, n=16, equal_split=True, err=-0.805, err_pred=-0.770 / surprise=0.045
  - 弁 16 本 independent h=0.74 10 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 16 本 independent h=0.25 6: h=0.250, fo_rel=0.045, n=16, equal_split=False, err=-0.243, err_pred=-0.233 / surprise=0.045
  - 弁 偏り 16 本 independent h=0.25 6 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 16 本 independent h=0.25 6: h=0.250, fo_rel=0.044, n=16, equal_split=True, err=-0.245, err_pred=-0.234 / surprise=0.044
  - 弁 16 本 independent h=0.25 6 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 2 本 independent h=0.125 5: h=0.125, fo_rel=0.033, n=2, equal_split=False, err=-0.064, err_pred=-0.062 / surprise=0.033
  - 弁 偏り 2 本 independent h=0.125 5 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 2 本 independent h=0.125 5: h=0.125, fo_rel=0.032, n=2, equal_split=True, err=-0.065, err_pred=-0.062 / surprise=0.032
  - 弁 2 本 independent h=0.125 5 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 3 本 independent h=0.125 5: h=0.125, fo_rel=0.029, n=3, equal_split=False, err=-0.083, err_pred=-0.081 / surprise=0.029
  - 弁 偏り 3 本 independent h=0.125 5 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 3 本 independent h=0.125 5: h=0.125, fo_rel=0.029, n=3, equal_split=True, err=-0.086, err_pred=-0.083 / surprise=0.029
  - 弁 3 本 independent h=0.125 5 は「fo_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 26 件（propositions.jsonl を参照）

## O5: 弁だけの槽を今の方式で進めるとき、2 本以上でも、ずれの大きさは頭打ち t·dt·K²/2 を超えない

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 2 件: valve-eq-n16-independent-7, valve-skew-n16-independent-7
- もし: `（すべての単位）` ならば: `ceil_ratio <= 1.0`
- 識別子: `[where:independent==true, where:n>=2, where:valve_only==true] * => ceil_ratio<=1.0`（指紋 `04bc4d24116dee01`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}]} / 単位数: 100
- 見直す条件（反証）: 頭打ちを超える単位があれば、頭打ちは 1 次の見積もりにすぎないと書き直す
- 注記: ceil_ratio = \|err\| / (t·dt·K²/2)。頭打ちは n → ∞ の 1 次の項。高次の項で超えるかどうかは見ていない
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.980, recall=1.000, f1=0.990, accuracy=0.980, balanced_accuracy=0.500, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 100 | 98 | 0.98 [0.93, 0.99] | — | 0.98 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 2 | 0 | 0.00 [0.00, 0.66] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 2 件（対偶の判例も同じ）

- 弁 16 本 independent h=0.5 7: ceil_ratio=+1.02, h=0.500, n=16, equal_split=True, err=-0.509 / surprise=+1.02
  - 弁 16 本 independent h=0.5 7 は「（すべての単位）」を満たすのに「ceil_ratio <= 1.0」を満たさない。なぜか？
- 弁 偏り 16 本 independent h=0.5 7: ceil_ratio=+1.01, h=0.500, n=16, equal_split=False, err=-0.507 / surprise=+1.01
  - 弁 偏り 16 本 independent h=0.5 7 は「（すべての単位）」を満たすのに「ceil_ratio <= 1.0」を満たさない。なぜか？

## O7: 弁だけの槽を今の方式で進めるとき、2 本以上で刻みが 1/32 以下なら、刻みを半分にするとずれも半分になる（比 1.9〜2.1）

- **判定: exit 4 待った！判断保留** — 対偶: n=6（min_n=10）、成立率の区間 0.61〜1.00
- もし: `h <= 0.03125` ならば: `halving_ratio >= 1.9 かつ halving_ratio <= 2.1`
- 識別子: `[where:has_half==true, where:independent==true, where:n>=2, where:valve_only==true] h<=0.03125 => halving_ratio<=2.1 & halving_ratio>=1.9`（指紋 `c40c408b8f558e6e`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}, {'col': 'has_half', 'op': '==', 'value': True}]} / 単位数: 60
- 見直す条件（反証）: 細かい刻みで比が 1.9〜2.1 を外れる単位があれば、1 次という読みを見直す
- 注記: halving_ratio = この単位の err / 同じ組で刻みが半分の単位の err。半分の刻みの単位がある組だけ（has_half）
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.370, f1=0.541, accuracy=0.433, balanced_accuracy=0.685, mcc=0.236
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 20 | 20 | 1.00 [0.84, 1.00] | — | 0.90 | 1.11 | 0.077 | 0 | 支持 | 0 |
| 対偶 | 6 | 6 | 1.00 [0.61, 1.00] | — | 0.67 | 1.50 | 0.077 | 0 | 判断保留 | 4 |
| 逆 | 54 | 20 | 0.37 [0.25, 0.50] | — | 0.33 | 1.11 | 0.077 | 0 | 棄却 | 3 |
| 裏 | 40 | 6 | 0.15 [0.07, 0.29] | — | 0.10 | 1.50 | 0.077 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 34 件（裏の判例も同じ）

- 弁 偏り 8 本 independent h=0.5 7: h=0.500, halving_ratio=+2.09, n=8, equal_split=False, err=-0.468 / surprise=+2.09
  - 弁 偏り 8 本 independent h=0.5 7 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 8 本 independent h=0.5 7: h=0.500, halving_ratio=+2.09, n=8, equal_split=True, err=-0.479 / surprise=+2.09
  - 弁 8 本 independent h=0.5 7 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 16 本 independent h=0.5 7: h=0.500, halving_ratio=+2.08, n=16, equal_split=False, err=-0.507 / surprise=+2.08
  - 弁 偏り 16 本 independent h=0.5 7 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 16 本 independent h=0.5 7: h=0.500, halving_ratio=+2.08, n=16, equal_split=True, err=-0.509 / surprise=+2.08
  - 弁 16 本 independent h=0.5 7 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 2 本 independent h=0.25 6: h=0.250, halving_ratio=+2.07, n=2, equal_split=False, err=-0.132 / surprise=+2.07
  - 弁 偏り 2 本 independent h=0.25 6 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 2 本 independent h=0.25 6: h=0.250, halving_ratio=+2.07, n=2, equal_split=True, err=-0.133 / surprise=+2.07
  - 弁 2 本 independent h=0.25 6 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 3 本 independent h=0.25 6: h=0.250, halving_ratio=+2.06, n=3, equal_split=False, err=-0.171 / surprise=+2.06
  - 弁 偏り 3 本 independent h=0.25 6 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 3 本 independent h=0.25 6: h=0.250, halving_ratio=+2.06, n=3, equal_split=True, err=-0.176 / surprise=+2.06
  - 弁 3 本 independent h=0.25 6 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 4 本 independent h=0.25 6: h=0.250, halving_ratio=+2.06, n=4, equal_split=False, err=-0.193 / surprise=+2.06
  - 弁 偏り 4 本 independent h=0.25 6 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 4 本 independent h=0.25 6: h=0.250, halving_ratio=+2.05, n=4, equal_split=True, err=-0.198 / surprise=+2.05
  - 弁 4 本 independent h=0.25 6 は「halving_ratio >= 1.9 かつ halving_ratio <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 24 件（propositions.jsonl を参照）

## O8: 弁だけの槽を今の方式で進めるとき、2 本以上で刻みが 1/32 以下なら、1 次の式で残りを直すとずれは 1/10 以下になる

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 30 件: valve-skew-n2-independent-9, valve-eq-n2-independent-9, valve-skew-n3-independent-9, valve-eq-n3-independent-9, valve-skew-n4-independent-9 ほか
- もし: `h <= 0.03125` ならば: `corr_gain >= 10`
- 識別子: `[where:independent==true, where:n>=2, where:valve_only==true] h<=0.03125 => corr_gain>=10`（指紋 `b3c9140b5deb7af1`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}]} / 単位数: 100
- 見直す条件（反証）: 直しても 1/10 にならない単位があれば、(1 − 1/n) を補正の変数として式に入れる案は弱いと書く
- 注記: corr_gain = \|err\| / \|直した後の err\|。直し方: 残りに e^(+t·dt·(K² − Σk_i²)/2) を掛ける。分母が 0 のときは ε = 1e-15 に置き、ログに残す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.500, f1=0.667, accuracy=0.700, balanced_accuracy=0.750, mcc=0.535
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 30 | 1.00 [0.89, 1.00] | — | 0.60 | 1.67 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 40 | 40 | 1.00 [0.91, 1.00] | — | 0.70 | 1.43 | 0.000 | 0 | 支持 | 0 |
| 逆 | 60 | 30 | 0.50 [0.38, 0.62] | — | 0.30 | 1.67 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 70 | 40 | 0.57 [0.45, 0.68] | — | 0.40 | 1.43 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 30 件（裏の判例も同じ）

- 弁 偏り 2 本 independent h=0.0478 9: h=0.048, corr_gain=+41.27, n=2, equal_split=False, err=-0.024 / surprise=+41.27
  - 弁 偏り 2 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 2 本 independent h=0.0478 9: h=0.048, corr_gain=+41.26, n=2, equal_split=True, err=-0.024 / surprise=+41.26
  - 弁 2 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 3 本 independent h=0.0478 9: h=0.048, corr_gain=+37.22, n=3, equal_split=False, err=-0.031 / surprise=+37.22
  - 弁 偏り 3 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 3 本 independent h=0.0478 9: h=0.048, corr_gain=+36.95, n=3, equal_split=True, err=-0.032 / surprise=+36.95
  - 弁 3 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 4 本 independent h=0.0478 9: h=0.048, corr_gain=+35.38, n=4, equal_split=False, err=-0.035 / surprise=+35.38
  - 弁 偏り 4 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 4 本 independent h=0.0478 9: h=0.048, corr_gain=+35.11, n=4, equal_split=True, err=-0.036 / surprise=+35.11
  - 弁 4 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 8 本 independent h=0.0478 9: h=0.048, corr_gain=+33.05, n=8, equal_split=False, err=-0.041 / surprise=+33.05
  - 弁 偏り 8 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 8 本 independent h=0.0478 9: h=0.048, corr_gain=+32.66, n=8, equal_split=True, err=-0.042 / surprise=+32.66
  - 弁 8 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 偏り 16 本 independent h=0.0478 9: h=0.048, corr_gain=+31.63, n=16, equal_split=False, err=-0.045 / surprise=+31.63
  - 弁 偏り 16 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 弁 16 本 independent h=0.0478 9: h=0.048, corr_gain=+31.55, n=16, equal_split=True, err=-0.045 / surprise=+31.55
  - 弁 16 本 independent h=0.0478 9 は「corr_gain >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 20 件（propositions.jsonl を参照）

## O9: 弁だけの槽は、弁をまとめて取る方式（joint）なら、何本でもどの刻みでも残りは厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:joint==true, where:valve_only==true] * => err_abs<1e-09`（指紋 `b01b87a7e9480bb0`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'joint', 'op': '==', 'value': True}]} / 単位数: 110
- 見直す条件（反証）: joint で 1e-9 以上ずれる単位があれば、まとめ方（合計の割合を速さの比で分ける）を見直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 110 | 110 | 1.00 [0.97, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O10: 弁とポンプが混ざる槽でも、弁をまとめて取る方式（joint）なら残りは厳密である

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 27 件: mixed-eq-n1-joint-7, mixed-eq-n2-joint-7, mixed-eq-n4-joint-7, mixed-eq-n1-joint-8, mixed-eq-n2-joint-8 ほか
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:joint==true, where:mixed==true] * => err_abs<1e-09`（指紋 `13164ed62d24248a`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'mixed', 'op': '==', 'value': True}, {'col': 'joint', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: ずれる単位があれば、弁だけをまとめても足りない（ポンプとの取り合いが残る）と書き、affine（O11）を見る
- 注記: 破れると見込んで書いている。弁をまとめても、ポンプはステップ最初の量を知らずに一定量を取るため
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.100, recall=1.000, f1=0.182, accuracy=0.100, balanced_accuracy=0.500, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 8 回（どれかの形に異議あり 8 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 3 | 0.10 [0.03, 0.26] | — | 0.10 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 27 | 0 | 0.00 [0.00, 0.12] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 27 件（対偶の判例も同じ）

- 弁+ポンプ 1 本 joint h=0.5 7: err_abs=+1.00, h=0.500, n=1, err=-1.00 / surprise=-1.00
  - 弁+ポンプ 1 本 joint h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 2 本 joint h=0.5 7: err_abs=+1.00, h=0.500, n=2, err=-1.00 / surprise=-1.00
  - 弁+ポンプ 2 本 joint h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 4 本 joint h=0.5 7: err_abs=+1.00, h=0.500, n=4, err=-1.00 / surprise=-1.00
  - 弁+ポンプ 4 本 joint h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 1 本 joint h=0.343 8: err_abs=+1.00, h=0.343, n=1, err=-1.00 / surprise=-1.00
  - 弁+ポンプ 1 本 joint h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 2 本 joint h=0.343 8: err_abs=+1.00, h=0.343, n=2, err=-1.00 / surprise=-1.00
  - 弁+ポンプ 2 本 joint h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 4 本 joint h=0.343 8: err_abs=+1.00, h=0.343, n=4, err=-1.00 / surprise=-1.00
  - 弁+ポンプ 4 本 joint h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 1 本 joint h=0.25 6: err_abs=0.516, h=0.250, n=1, err=-0.516 / surprise=-0.516
  - 弁+ポンプ 1 本 joint h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 2 本 joint h=0.25 6: err_abs=0.516, h=0.250, n=2, err=-0.516 / surprise=-0.516
  - 弁+ポンプ 2 本 joint h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 4 本 joint h=0.25 6: err_abs=0.516, h=0.250, n=4, err=-0.516 / surprise=-0.516
  - 弁+ポンプ 4 本 joint h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+ポンプ 1 本 joint h=0.125 5: err_abs=0.253, h=0.125, n=1, err=-0.253 / surprise=-0.253
  - 弁+ポンプ 1 本 joint h=0.125 5 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ほか 17 件（propositions.jsonl を参照）

## O11: 弁とポンプが混ざる槽は、1 ステップを厳密に解く方式（affine）なら、何本でもどの刻みでも残りは厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:affine==true, where:mixed==true] * => err_abs<1e-09`（指紋 `ed17f478c2abe289`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'mixed', 'op': '==', 'value': True}, {'col': 'affine', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: ずれる単位があれば、dV/dt = −K·V − q の 1 ステップの解の入れ方を見直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 30 | 1.00 [0.89, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O12: ポンプだけの槽は、何本に分けても、槽が途中で足りなくなっても、残りは厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:pump_only==true] * => err_abs<1e-09`（指紋 `d05448e5e01cd2e7`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'pump_only', 'op': '==', 'value': True}]} / 単位数: 16
- 見直す条件（反証）: ずれる単位があれば、足りない槽を分け合う処理か、足りているあいだの切り捨てを見直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 16 | 1.00 [0.81, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O13: 出口に遅れの管があっても、槽の残りは遅れのない同じ組と 1 ulp も違わない

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `src_same == True`
- 識別子: `[where:has_delay==true] * => src_same==true`（指紋 `85e7966045fca641`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'has_delay', 'op': '==', 'value': True}]} / 単位数: 12
- 見直す条件（反証）: 違う単位があれば、遅れは届く時刻だけを変えるという前提を見直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 12 | 1.00 [0.76, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O14: 遅れの管を通った量が届くのは、出てからちょうど遅れのステップ数の後である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `lag_err_steps == 0`
- 識別子: `[where:has_delay==true] * => lag_err_steps==0`（指紋 `1d6a881fd85b2ada`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'has_delay', 'op': '==', 'value': True}]} / 単位数: 12
- 見直す条件（反証）: 1 ステップでもずれる単位があれば、遅れの管の数え方を見直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 8 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 12 | 1.00 [0.76, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O15: どの単位でも、槽と管の中の合計は最初から 1 ulp も変わらない

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `conservation_q == 0`
- 識別子: `[all] * => conservation_q==0`（指紋 `7c3f01901c7f68f4`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: 全体 / 単位数: 2890
- 見直す条件（反証）: 0 でない単位があれば、その方式は採らない
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 8 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 5 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 2890 | 2890 | 1.00 [1.00, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O16: 弁だけの槽を今の方式で進めるとき、2 本以上でも、ずれの大きさは出口を無限に細かく分けたときの形 (1 − K·dt)^N を超えない

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `euler_ratio <= 1.0`
- 識別子: `[where:independent==true, where:n>=2, where:valve_only==true] * => euler_ratio<=1.0`（指紋 `23571f99b09322c0`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}]} / 単位数: 100
- 親: O5（変更: 頭打ちを 1 次の見積もり t·dt·K²/2 から、n → ∞ の厳密な形に置き直した（O5 の判例 2 件を受けて））
- 見直す条件（反証）: 超える単位があれば、1 − e^(−x) ≤ x から導いた上限の出し方を見直す
- 注記: 1 − e^(−x) ≤ x なので 1 ステップの残り 1 − Σ(1 − e^(−k_i·dt)) ≥ 1 − K·dt。紙の上では必ず成り立つはずの命題
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 100 | 100 | 1.00 [0.96, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O17: 弁だけの槽を今の方式で進めるとき、2 本以上で刻みが時定数の 1/8 以下なら、ずれは 2 次の式と 0.5 % 以内で合う

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 8 件: valve-eq-n16-independent-5, valve-skew-n16-independent-5, valve-eq-n8-independent-5, valve-skew-n8-independent-5, valve-eq-n4-independent-5 ほか
- もし: `h <= 0.125` ならば: `so_rel <= 0.005`
- 識別子: `[where:independent==true, where:n>=2, where:valve_only==true] h<=0.125 => so_rel<=0.005`（指紋 `7ef9af97e0d0648b`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}]} / 単位数: 100
- 見直す条件（反証）: h ≤ 1/8 で 0.5 % を超える単位があれば、2 次の項の導き方か境を見直す
- 注記: 2 次の式は ln(1 ステップの残り) を dt の 3 次まで展開したもの。係数はデータに当てはめていない
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.867, recall=1.000, f1=0.929, accuracy=0.920, balanced_accuracy=0.917, mcc=0.850
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 60 | 52 | 0.87 [0.76, 0.93] | — | 0.52 | 1.67 | 0.000 | 0 | 棄却 | 3 |
| 対偶 | 48 | 40 | 0.83 [0.70, 0.91] | — | 0.40 | 2.08 | 0.000 | 0 | 棄却 | 3 |
| 逆 | 52 | 52 | 1.00 [0.93, 1.00] | — | 0.60 | 1.67 | 0.000 | 0 | 支持 | 0 |
| 裏 | 40 | 40 | 1.00 [0.91, 1.00] | — | 0.48 | 2.08 | 0.000 | 0 | 支持 | 0 |

**異議あり（不成立）** 元の命題に判例 8 件（対偶の判例も同じ）

- 弁 16 本 independent h=0.125 5: h=0.125, so_rel=0.007, n=16, equal_split=True, err=-0.120 / surprise=0.007
  - 弁 16 本 independent h=0.125 5 は「h <= 0.125」を満たすのに「so_rel <= 0.005」を満たさない。なぜか？
- 弁 偏り 16 本 independent h=0.125 5: h=0.125, so_rel=0.007, n=16, equal_split=False, err=-0.119 / surprise=0.007
  - 弁 偏り 16 本 independent h=0.125 5 は「h <= 0.125」を満たすのに「so_rel <= 0.005」を満たさない。なぜか？
- 弁 8 本 independent h=0.125 5: h=0.125, so_rel=0.007, n=8, equal_split=True, err=-0.112 / surprise=0.007
  - 弁 8 本 independent h=0.125 5 は「h <= 0.125」を満たすのに「so_rel <= 0.005」を満たさない。なぜか？
- 弁 偏り 8 本 independent h=0.125 5: h=0.125, so_rel=0.006, n=8, equal_split=False, err=-0.109 / surprise=0.006
  - 弁 偏り 8 本 independent h=0.125 5 は「h <= 0.125」を満たすのに「so_rel <= 0.005」を満たさない。なぜか？
- 弁 4 本 independent h=0.125 5: h=0.125, so_rel=0.006, n=4, equal_split=True, err=-0.096 / surprise=0.006
  - 弁 4 本 independent h=0.125 5 は「h <= 0.125」を満たすのに「so_rel <= 0.005」を満たさない。なぜか？
- 弁 偏り 4 本 independent h=0.125 5: h=0.125, so_rel=0.006, n=4, equal_split=False, err=-0.094 / surprise=0.006
  - 弁 偏り 4 本 independent h=0.125 5 は「h <= 0.125」を満たすのに「so_rel <= 0.005」を満たさない。なぜか？
- 弁 3 本 independent h=0.125 5: h=0.125, so_rel=0.005, n=3, equal_split=True, err=-0.086 / surprise=0.005
  - 弁 3 本 independent h=0.125 5 は「h <= 0.125」を満たすのに「so_rel <= 0.005」を満たさない。なぜか？
- 弁 偏り 3 本 independent h=0.125 5: h=0.125, so_rel=0.005, n=3, equal_split=False, err=-0.083 / surprise=0.005
  - 弁 偏り 3 本 independent h=0.125 5 は「h <= 0.125」を満たすのに「so_rel <= 0.005」を満たさない。なぜか？

## O18: 弁だけの槽を今の方式で進めるとき、2 本以上なら、ずれは 2 次の式と 5 % 以内で合う（刻みの条件なし）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 20 件: valve-eq-n16-independent-10, valve-skew-n16-independent-10, valve-eq-n8-independent-10, valve-skew-n8-independent-10, valve-eq-n4-independent-10 ほか
- もし: `（すべての単位）` ならば: `so_rel <= 0.05`
- 識別子: `[where:independent==true, where:n>=2, where:valve_only==true] * => so_rel<=0.05`（指紋 `165df5a4a891d864`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}, {'col': 'n', 'op': '>=', 'value': 2}]} / 単位数: 100
- 親: O3（変更: 1 次の式を 2 次の式に置き直した（O3 の判例 34 件を受けて）。5 % と範囲は同じ）
- 見直す条件（反証）: 5 % を超える単位があれば、2 次でも粗い刻みには足りないと書く
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.800, recall=1.000, f1=0.889, accuracy=0.800, balanced_accuracy=0.500, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 100 | 80 | 0.80 [0.71, 0.87] | — | 0.80 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 20 | 0 | 0.00 [0.00, 0.16] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 20 件（対偶の判例も同じ）

- 弁 16 本 independent h=0.74 10: so_rel=0.184, h=0.740, n=16, equal_split=True, err=-0.805 / surprise=0.184
  - 弁 16 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 16 本 independent h=0.74 10: so_rel=0.184, h=0.740, n=16, equal_split=False, err=-0.802 / surprise=0.184
  - 弁 偏り 16 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 8 本 independent h=0.74 10: so_rel=0.181, h=0.740, n=8, equal_split=True, err=-0.768 / surprise=0.181
  - 弁 8 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 8 本 independent h=0.74 10: so_rel=0.179, h=0.740, n=8, equal_split=False, err=-0.754 / surprise=0.179
  - 弁 偏り 8 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 4 本 independent h=0.74 10: so_rel=0.170, h=0.740, n=4, equal_split=True, err=-0.686 / surprise=0.170
  - 弁 4 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 4 本 independent h=0.74 10: so_rel=0.169, h=0.740, n=4, equal_split=False, err=-0.673 / surprise=0.169
  - 弁 偏り 4 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 3 本 independent h=0.74 10: so_rel=0.160, h=0.740, n=3, equal_split=True, err=-0.625 / surprise=0.160
  - 弁 3 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 3 本 independent h=0.74 10: so_rel=0.159, h=0.740, n=3, equal_split=False, err=-0.609 / surprise=0.159
  - 弁 偏り 3 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 2 本 independent h=0.74 10: so_rel=0.136, h=0.740, n=2, equal_split=True, err=-0.489 / surprise=0.136
  - 弁 2 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- 弁 偏り 2 本 independent h=0.74 10: so_rel=0.136, h=0.740, n=2, equal_split=False, err=-0.485 / surprise=0.136
  - 弁 偏り 2 本 independent h=0.74 10 は「（すべての単位）」を満たすのに「so_rel <= 0.05」を満たさない。なぜか？
- ほか 10 件（propositions.jsonl を参照）

## O19: 弁だけの槽を今の方式で進めるとき、残りは離散の閉じた式 (1 − Σ(1 − e^(−k_i·dt)))^N と一致する（何本でも、どの刻みでも）

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `disc_gap < 1e-09`
- 識別子: `[where:independent==true, where:valve_only==true] * => disc_gap<1e-09`（指紋 `79954362332ed0f7`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'valve_only', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}]} / 単位数: 110
- 見直す条件（反証）: 合わない単位があれば、エンジンの 1 ステップの取り方の説明（どの弁もステップ最初の量を見る）を見直す
- 注記: 1 次・2 次の式はこの閉じた式の近似。ずれの説明そのものを問う命題
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 110 | 110 | 1.00 [0.97, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O20: 弁と弱いポンプが混ざる槽で、厳密な残りが大きいときなら、弁をまとめて取る方式（joint）で残りは厳密である

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 30 件: gentle-eq-n1-joint-10, gentle-eq-n2-joint-10, gentle-eq-n4-joint-10, gentle-eq-n1-joint-7, gentle-eq-n2-joint-7 ほか
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:gentle==true, where:joint==true] * => err_abs<1e-09`（指紋 `754c42277f55486f`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'gentle', 'op': '==', 'value': True}, {'col': 'joint', 'op': '==', 'value': True}]} / 単位数: 30
- 親: O10（変更: 範囲を、厳密な残りが最初の量の 6 割ほど残る条件（gentle）に替えた。O10 は残りが 2.7 % で、割合のずれが大きく出ていた）
- 見直す条件（反証）: ずれる単位があれば、joint が足りないのは残りの小ささのせいではないと書く
- 注記: 破れると見込んで書いている
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.000, recall=None, f1=0.000, accuracy=0.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 0 | 0.00 [0.00, 0.11] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 30 | 0 | 0.00 [0.00, 0.11] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 30 件（対偶の判例も同じ）

- 弁+弱いポンプ 1 本 joint h=0.74 10: err_abs=0.007, h=0.740, n=1, err=-0.007 / surprise=-0.007
  - 弁+弱いポンプ 1 本 joint h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 2 本 joint h=0.74 10: err_abs=0.007, h=0.740, n=2, err=-0.007 / surprise=-0.007
  - 弁+弱いポンプ 2 本 joint h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 4 本 joint h=0.74 10: err_abs=0.007, h=0.740, n=4, err=-0.007 / surprise=-0.007
  - 弁+弱いポンプ 4 本 joint h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 1 本 joint h=0.5 7: err_abs=0.003, h=0.500, n=1, err=-0.003 / surprise=-0.003
  - 弁+弱いポンプ 1 本 joint h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 2 本 joint h=0.5 7: err_abs=0.003, h=0.500, n=2, err=-0.003 / surprise=-0.003
  - 弁+弱いポンプ 2 本 joint h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 4 本 joint h=0.5 7: err_abs=0.003, h=0.500, n=4, err=-0.003 / surprise=-0.003
  - 弁+弱いポンプ 4 本 joint h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 1 本 joint h=0.25 6: err_abs=0.001, h=0.250, n=1, err=-0.001 / surprise=-0.001
  - 弁+弱いポンプ 1 本 joint h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 2 本 joint h=0.25 6: err_abs=0.001, h=0.250, n=2, err=-0.001 / surprise=-0.001
  - 弁+弱いポンプ 2 本 joint h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 4 本 joint h=0.25 6: err_abs=0.001, h=0.250, n=4, err=-0.001 / surprise=-0.001
  - 弁+弱いポンプ 4 本 joint h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 弁+弱いポンプ 1 本 joint h=0.343 8: err_abs=0.001, h=0.343, n=1, err=-0.001 / surprise=-0.001
  - 弁+弱いポンプ 1 本 joint h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ほか 20 件（propositions.jsonl を参照）

## O21: 弁と弱いポンプが混ざる槽では、弁が 1 本なら joint のずれは今の方式と同じである

- **判定: exit 0 異議なし**（逆・裏まで）
- もし: `n == 1` ならば: `joint_ratio >= 0.999999 かつ joint_ratio <= 1.000001`
- 識別子: `[where:gentle==true, where:joint==true] n==1 => joint_ratio<=1.000001 & joint_ratio>=0.999999`（指紋 `e8cd3deb4c5e91ea`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'gentle', 'op': '==', 'value': True}, {'col': 'joint', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: 弁 1 本で joint が違う値になれば、joint の定義（弁どうしだけをまとめる）を見直す
- 注記: 第1弾の判例（joint でずれが半分ほどになった）を見て作った命題。逆（同じなら 1 本）の判例が無ければ、弁が 2 本以上のとき joint は必ず値を変える
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=1.000, mcc=1.000
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 10 | 10 | 1.00 [0.72, 1.00] | — | 0.33 | 3.00 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 20 | 20 | 1.00 [0.84, 1.00] | — | 0.67 | 1.50 | 0.000 | 0 | 支持 | 0 |
| 逆 | 10 | 10 | 1.00 [0.72, 1.00] | — | 0.33 | 3.00 | 0.000 | 0 | 支持 | 0 |
| 裏 | 20 | 20 | 1.00 [0.84, 1.00] | — | 0.67 | 1.50 | 0.000 | 0 | 支持 | 0 |

## O22: 弁と弱いポンプが混ざる槽は、1 ステップを厳密に解く方式（affine）なら残りは厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:affine==true, where:gentle==true] * => err_abs<1e-09`（指紋 `3768d894d8ec37aa`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'gentle', 'op': '==', 'value': True}, {'col': 'affine', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: ずれる単位があれば、O11 の支持は範囲（残りが小さい条件）に寄っていたと書く
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 30 | 1.00 [0.89, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O23: 槽が 2 段つながるとき、出口が 1 本ずつなら 2 段目の量も厳密である

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 50 件: chain-r0.25-10, chain-r0.25-7, chain-r0.5-10, chain-r0.25-8, chain-r0.75-10 ほか
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:chain==true] * => err_abs<1e-09`（指紋 `fda61d2f761172a2`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain', 'op': '==', 'value': True}]} / 単位数: 50
- 見直す条件（反証）: ずれる単位があれば、出口の数とは別のずれ（上の槽から入ってくる量を同じステップの中で知らない）があると書く
- 注記: 破れると見込んで書いている。直す方式（joint・affine）は 1 つの槽の出口どうしを揃えるだけで、槽と槽のあいだには届かない
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.000, recall=None, f1=0.000, accuracy=0.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 7 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 50 | 0 | 0.00 [0.00, 0.07] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 50 | 0 | 0.00 [0.00, 0.07] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 50 件（対偶の判例も同じ）

- 2 段 τ2/τ=0.25 h=0.74 10: err_abs=+2.69, h=0.740, tau2_ratio=0.250, err=+2.69 / surprise=+2.69
  - 2 段 τ2/τ=0.25 h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.25 h=0.5 7: err_abs=+1.51, h=0.500, tau2_ratio=0.250, err=+1.51 / surprise=+1.51
  - 2 段 τ2/τ=0.25 h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.5 h=0.74 10: err_abs=+1.10, h=0.740, tau2_ratio=0.500, err=+1.10 / surprise=+1.10
  - 2 段 τ2/τ=0.5 h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.25 h=0.343 8: err_abs=0.910, h=0.343, tau2_ratio=0.250, err=0.910 / surprise=0.910
  - 2 段 τ2/τ=0.25 h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.75 h=0.74 10: err_abs=0.671, h=0.740, tau2_ratio=0.750, err=0.671 / surprise=0.671
  - 2 段 τ2/τ=0.75 h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.5 h=0.5 7: err_abs=0.649, h=0.500, tau2_ratio=0.500, err=0.649 / surprise=0.649
  - 2 段 τ2/τ=0.5 h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.25 h=0.25 6: err_abs=0.615, h=0.250, tau2_ratio=0.250, err=0.615 / surprise=0.615
  - 2 段 τ2/τ=0.25 h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.5 h=0.343 8: err_abs=0.409, h=0.343, tau2_ratio=0.500, err=0.409 / surprise=0.409
  - 2 段 τ2/τ=0.5 h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.75 h=0.5 7: err_abs=0.409, h=0.500, tau2_ratio=0.750, err=0.409 / surprise=0.409
  - 2 段 τ2/τ=0.75 h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.5 h=0.25 6: err_abs=0.284, h=0.250, tau2_ratio=0.500, err=0.284 / surprise=0.284
  - 2 段 τ2/τ=0.5 h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ほか 40 件（propositions.jsonl を参照）

## O24: 槽が 2 段つながるとき、1 段目（入ってくる管のない槽）の量は厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `first_err_abs < 1e-09`
- 識別子: `[where:chain==true] * => first_err_abs<1e-09`（指紋 `2023bfd7a1973a66`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain', 'op': '==', 'value': True}]} / 単位数: 50
- 見直す条件（反証）: ずれる単位があれば、O1（出口 1 本なら厳密）を見直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 50 | 50 | 1.00 [0.93, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O25: 槽が 2 段つながるとき、刻みが時定数の 1/32 以下なら、刻みを半分にすると 2 段目のずれも半分になる（比 1.9〜2.1）

- **判定: exit 4 待った！判断保留** — 対偶: n=9（min_n=10）、成立率の区間 0.70〜1.00
- もし: `h <= 0.03125` ならば: `chain_halving >= 1.9 かつ chain_halving <= 2.1`
- 識別子: `[where:chain==true, where:has_half==true] h<=0.03125 => chain_halving<=2.1 & chain_halving>=1.9`（指紋 `0220548b6a317dcf`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain', 'op': '==', 'value': True}, {'col': 'has_half', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: 比が外れる単位があれば、槽と槽のあいだのずれは 1 次ではないと書く
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.476, f1=0.645, accuracy=0.633, balanced_accuracy=0.738, mcc=0.463
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 7 回、元の命題に異議あり 0 回（どれかの形に異議あり 7 回）、直近で元の命題に判例がない連続 7 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 10 | 10 | 1.00 [0.72, 1.00] | — | 0.70 | 1.43 | 0.012 | 0 | 支持 | 0 |
| 対偶 | 9 | 9 | 1.00 [0.70, 1.00] | — | 0.67 | 1.50 | 0.012 | 0 | 判断保留 | 4 |
| 逆 | 21 | 10 | 0.48 [0.28, 0.68] | — | 0.33 | 1.43 | 0.012 | 0 | 棄却 | 3 |
| 裏 | 20 | 9 | 0.45 [0.26, 0.66] | — | 0.30 | 1.50 | 0.012 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 11 件（裏の判例も同じ）

- 2 段 τ2/τ=2 h=0.25 6: h=0.250, chain_halving=+2.06, tau2_ratio=+2.00, err=0.067 / surprise=+2.06
  - 2 段 τ2/τ=2 h=0.25 6 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.5 h=0.125 5: h=0.125, chain_halving=+2.06, tau2_ratio=0.500, err=0.133 / surprise=+2.06
  - 2 段 τ2/τ=0.5 h=0.125 5 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.25 h=0.0625 4: h=0.062, chain_halving=+2.05, tau2_ratio=0.250, err=0.132 / surprise=+2.05
  - 2 段 τ2/τ=0.25 h=0.0625 4 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=4 h=0.25 6: h=0.250, chain_halving=+2.05, tau2_ratio=+4.00, err=0.033 / surprise=+2.05
  - 2 段 τ2/τ=4 h=0.25 6 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.75 h=0.125 5: h=0.125, chain_halving=+2.05, tau2_ratio=0.750, err=0.088 / surprise=+2.05
  - 2 段 τ2/τ=0.75 h=0.125 5 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.5 h=0.0625 4: h=0.062, chain_halving=+2.03, tau2_ratio=0.500, err=0.064 / surprise=+2.03
  - 2 段 τ2/τ=0.5 h=0.0625 4 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=2 h=0.125 5: h=0.125, chain_halving=+2.03, tau2_ratio=+2.00, err=0.032 / surprise=+2.03
  - 2 段 τ2/τ=2 h=0.125 5 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=4 h=0.125 5: h=0.125, chain_halving=+2.03, tau2_ratio=+4.00, err=0.016 / surprise=+2.03
  - 2 段 τ2/τ=4 h=0.125 5 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.75 h=0.0625 4: h=0.062, chain_halving=+2.02, tau2_ratio=0.750, err=0.043 / surprise=+2.02
  - 2 段 τ2/τ=0.75 h=0.0625 4 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=2 h=0.0625 4: h=0.062, chain_halving=+2.02, tau2_ratio=+2.00, err=0.016 / surprise=+2.02
  - 2 段 τ2/τ=2 h=0.0625 4 は「chain_halving >= 1.9 かつ chain_halving <= 2.1」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 1 件（propositions.jsonl を参照）

## O26: エンジンの既定の取り方（槽ごとに 1 ステップを厳密に解く）なら、弁だけの槽も、弁とポンプが混ざる槽も、残りは厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:native==true] * => err_abs<1e-09`（指紋 `04e0ae43a7ea2912`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'native', 'op': '==', 'value': True}]} / 単位数: 160
- 見直す条件（反証）: ずれる単位があれば、エンジンへの入れ方が affine（O11・O22）と違っていると書き、エンジンを見直す
- 注記: O9・O11・O22 は単位を作るスクリプトが足した法則で確かめた。これはエンジン本体に入った実装を同じ条件で確かめ直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 160 | 160 | 1.00 [0.98, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O27: 槽が 2 段つながるとき、刻みが時定数の 1/32 以下なら、2 段目のずれは dt/(2·τ2) と 5 % 以内で合う（1 段目の速さにも時刻にもよらない）

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 24 件: chain2-r8-s3-independent-6, chain2-r8-s1-independent-6, chain2-r0.333-s1-independent-4, chain2-r0.333-s3-independent-4, chain2-r1.5-s3-independent-5 ほか
- もし: `h <= 0.03125` ならば: `chain_pred_rel <= 0.05`
- 識別子: `[where:chain2==true, where:independent==true] h<=0.03125 => chain_pred_rel<=0.05`（指紋 `73892278f4a77f76`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain2', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}]} / 単位数: 80
- 見直す条件（反証）: 外れる単位があれば、半ステップぶん減りそこねるという説明は足りない（時刻か 1 段目の速さが効く）と書く
- 注記: O23 の判例（t ≈ 2τ、τ2/τ = 1/4〜4）を見て作った命題。別の τ2 と別の時刻の単位だけで確かめる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.500, f1=0.667, accuracy=0.700, balanced_accuracy=0.750, mcc=0.535
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 24 | 24 | 1.00 [0.86, 1.00] | — | 0.60 | 1.67 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 32 | 32 | 1.00 [0.89, 1.00] | — | 0.70 | 1.43 | 0.000 | 0 | 支持 | 0 |
| 逆 | 48 | 24 | 0.50 [0.36, 0.64] | — | 0.30 | 1.67 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 56 | 32 | 0.57 [0.44, 0.69] | — | 0.40 | 1.43 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 24 件（裏の判例も同じ）

- 2 段 τ2/τ=8 t=3τ independent h=0.25 6: h=0.250, chain_pred_rel=0.048, tau2_ratio=+8.00, span_ratio=+3.00, err=0.016 / surprise=0.048
  - 2 段 τ2/τ=8 t=3τ independent h=0.25 6 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=8 t=1τ independent h=0.25 6: h=0.250, chain_pred_rel=0.048, tau2_ratio=+8.00, span_ratio=+1.00, err=0.016 / surprise=0.048
  - 2 段 τ2/τ=8 t=1τ independent h=0.25 6 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=1τ independent h=0.0625 4: h=0.062, chain_pred_rel=0.043, tau2_ratio=0.333, span_ratio=+1.00, err=0.098 / surprise=0.043
  - 2 段 τ2/τ=0.333 t=1τ independent h=0.0625 4 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ independent h=0.0625 4: h=0.062, chain_pred_rel=0.043, tau2_ratio=0.333, span_ratio=+3.00, err=0.098 / surprise=0.043
  - 2 段 τ2/τ=0.333 t=3τ independent h=0.0625 4 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=3τ independent h=0.125 5: h=0.125, chain_pred_rel=0.036, tau2_ratio=+1.50, span_ratio=+3.00, err=0.043 / surprise=0.036
  - 2 段 τ2/τ=1.5 t=3τ independent h=0.125 5 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=1τ independent h=0.125 5: h=0.125, chain_pred_rel=0.036, tau2_ratio=+1.50, span_ratio=+1.00, err=0.043 / surprise=0.036
  - 2 段 τ2/τ=1.5 t=1τ independent h=0.125 5 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ independent h=0.0478 9: h=0.048, chain_pred_rel=0.032, tau2_ratio=0.333, span_ratio=+3.00, err=0.074 / surprise=0.032
  - 2 段 τ2/τ=0.333 t=3τ independent h=0.0478 9 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=1τ independent h=0.0478 9: h=0.048, chain_pred_rel=0.032, tau2_ratio=0.333, span_ratio=+1.00, err=0.074 / surprise=0.032
  - 2 段 τ2/τ=0.333 t=1τ independent h=0.0478 9 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=3 t=1τ independent h=0.125 5: h=0.125, chain_pred_rel=0.028, tau2_ratio=+3.00, span_ratio=+1.00, err=0.021 / surprise=0.028
  - 2 段 τ2/τ=3 t=1τ independent h=0.125 5 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=3 t=3τ independent h=0.125 5: h=0.125, chain_pred_rel=0.028, tau2_ratio=+3.00, span_ratio=+3.00, err=0.021 / surprise=0.028
  - 2 段 τ2/τ=3 t=3τ independent h=0.125 5 は「chain_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 14 件（propositions.jsonl を参照）

## O28: ポンプから入って弁 1 本から出る槽は、今のエンジンで厳密である

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 30 件: fed-r0.25-independent-10, fed-r0.25-independent-7, fed-r0.25-independent-8, fed-r0.25-independent-6, fed-r1-independent-10 ほか
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:fed==true, where:independent==true] * => err_abs<1e-09`（指紋 `c9aece9f64c74d2e`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'fed', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: ずれる単位があれば、槽と槽のあいだのずれは上が弁でもポンプでも起きると書く
- 注記: 破れると見込んで書いている
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.000, recall=None, f1=0.000, accuracy=0.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 0 | 0.00 [0.00, 0.11] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 30 | 0 | 0.00 [0.00, 0.11] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 30 件（対偶の判例も同じ）

- ポンプ → 槽 τ2/τ=0.25 independent h=0.74 10: err_abs=+2.12, h=0.740, tau2_ratio=0.250, err=+2.12 / surprise=+2.12
  - ポンプ → 槽 τ2/τ=0.25 independent h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=0.25 independent h=0.5 7: err_abs=+1.31, h=0.500, tau2_ratio=0.250, err=+1.31 / surprise=+1.31
  - ポンプ → 槽 τ2/τ=0.25 independent h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=0.25 independent h=0.343 8: err_abs=0.838, h=0.343, tau2_ratio=0.250, err=0.838 / surprise=0.838
  - ポンプ → 槽 τ2/τ=0.25 independent h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=0.25 independent h=0.25 6: err_abs=0.582, h=0.250, tau2_ratio=0.250, err=0.582 / surprise=0.582
  - ポンプ → 槽 τ2/τ=0.25 independent h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=1 independent h=0.74 10: err_abs=0.415, h=0.740, tau2_ratio=+1.00, err=0.415 / surprise=0.415
  - ポンプ → 槽 τ2/τ=1 independent h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=1 independent h=0.5 7: err_abs=0.271, h=0.500, tau2_ratio=+1.00, err=0.271 / surprise=0.271
  - ポンプ → 槽 τ2/τ=1 independent h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=0.25 independent h=0.125 5: err_abs=0.271, h=0.125, tau2_ratio=0.250, err=0.271 / surprise=0.271
  - ポンプ → 槽 τ2/τ=0.25 independent h=0.125 5 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=1 independent h=0.343 8: err_abs=0.181, h=0.343, tau2_ratio=+1.00, err=0.181 / surprise=0.181
  - ポンプ → 槽 τ2/τ=1 independent h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=1 independent h=0.25 6: err_abs=0.130, h=0.250, tau2_ratio=+1.00, err=0.130 / surprise=0.130
  - ポンプ → 槽 τ2/τ=1 independent h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ポンプ → 槽 τ2/τ=0.25 independent h=0.0625 4: err_abs=0.130, h=0.062, tau2_ratio=0.250, err=0.130 / surprise=0.130
  - ポンプ → 槽 τ2/τ=0.25 independent h=0.0625 4 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ほか 20 件（propositions.jsonl を参照）

## O29: ポンプから入って弁 1 本から出る槽のずれは、閉じた式 x/(1 − e^(−x)) − 1（x = dt/τ2）と一致する

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `fed_gap < 1e-09`
- 識別子: `[where:fed==true, where:independent==true] * => fed_gap<1e-09`（指紋 `749f5406d4e2b8f9`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'fed', 'op': '==', 'value': True}, {'col': 'independent', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: 合わない単位があれば、1 ステップの取り方の説明（入った量はステップの終わりに足される）を見直す
- 注記: 紙の上で導いた式。時刻によらない（どの時刻でも同じ割合だけ多い）
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 30 | 1.00 [0.89, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O30: ポンプから入る槽は、入る量が一定の速さで入ると見なす方式（uniform）なら厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:fed==true, where:uniform==true] * => err_abs<1e-09`（指紋 `ce1591f2dd739d9d`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'fed', 'op': '==', 'value': True}, {'col': 'uniform', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: ずれる単位があれば、uniform の式を見直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 30 | 1.00 [0.89, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O31: 槽が 2 段つながるときも、uniform なら 2 段目は厳密である

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 80 件: chain2-r0.333-s1-uniform-10, chain2-r0.333-s3-uniform-10, chain2-r0.333-s1-uniform-7, chain2-r0.333-s3-uniform-7, chain2-r1.5-s3-uniform-10 ほか
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:chain2==true, where:uniform==true] * => err_abs<1e-09`（指紋 `0b62b12d45597dc3`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain2', 'op': '==', 'value': True}, {'col': 'uniform', 'op': '==', 'value': True}]} / 単位数: 80
- 見直す条件（反証）: ずれる単位があれば、上の槽から入る量は 1 ステップのあいだ一定ではない（減りながら入る）と書く
- 注記: 破れると見込んで書いている
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.000, recall=None, f1=0.000, accuracy=0.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 6 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 80 | 0 | 0.00 [0.00, 0.05] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 80 | 0 | 0.00 [0.00, 0.05] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 80 件（対偶の判例も同じ）

- 2 段 τ2/τ=0.333 t=1τ uniform h=0.74 10: err_abs=0.139, h=0.740, tau2_ratio=0.333, span_ratio=+1.00, err=0.139 / surprise=0.139
  - 2 段 τ2/τ=0.333 t=1τ uniform h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ uniform h=0.74 10: err_abs=0.139, h=0.740, tau2_ratio=0.333, span_ratio=+3.00, err=0.139 / surprise=0.139
  - 2 段 τ2/τ=0.333 t=3τ uniform h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=1τ uniform h=0.5 7: err_abs=0.063, h=0.500, tau2_ratio=0.333, span_ratio=+1.00, err=0.063 / surprise=0.063
  - 2 段 τ2/τ=0.333 t=1τ uniform h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ uniform h=0.5 7: err_abs=0.063, h=0.500, tau2_ratio=0.333, span_ratio=+3.00, err=0.063 / surprise=0.063
  - 2 段 τ2/τ=0.333 t=3τ uniform h=0.5 7 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=3τ uniform h=0.74 10: err_abs=0.031, h=0.740, tau2_ratio=+1.50, span_ratio=+3.00, err=0.031 / surprise=0.031
  - 2 段 τ2/τ=1.5 t=3τ uniform h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=1τ uniform h=0.74 10: err_abs=0.031, h=0.740, tau2_ratio=+1.50, span_ratio=+1.00, err=0.031 / surprise=0.031
  - 2 段 τ2/τ=1.5 t=1τ uniform h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=1τ uniform h=0.343 8: err_abs=0.030, h=0.343, tau2_ratio=0.333, span_ratio=+1.00, err=0.030 / surprise=0.030
  - 2 段 τ2/τ=0.333 t=1τ uniform h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ uniform h=0.343 8: err_abs=0.030, h=0.343, tau2_ratio=0.333, span_ratio=+3.00, err=0.030 / surprise=0.030
  - 2 段 τ2/τ=0.333 t=3τ uniform h=0.343 8 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=1τ uniform h=0.25 6: err_abs=0.016, h=0.250, tau2_ratio=0.333, span_ratio=+1.00, err=0.016 / surprise=0.016
  - 2 段 τ2/τ=0.333 t=1τ uniform h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ uniform h=0.25 6: err_abs=0.016, h=0.250, tau2_ratio=0.333, span_ratio=+3.00, err=0.016 / surprise=0.016
  - 2 段 τ2/τ=0.333 t=3τ uniform h=0.25 6 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？
- ほか 70 件（propositions.jsonl を参照）

## O32: 槽が 2 段つながるとき、刻みが時定数の 1/32 以下なら、uniform は今のエンジンよりずれを 1/10 以下にする

- **判定: exit 4 待った！判断保留** — 対偶: n=6（min_n=10）、成立率の区間 0.61〜1.00
- もし: `h <= 0.03125` ならば: `gain_vs_independent >= 10`
- 識別子: `[where:chain2==true, where:uniform==true] h<=0.03125 => gain_vs_independent>=10`（指紋 `6d0b4acab4e3522a`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain2', 'op': '==', 'value': True}, {'col': 'uniform', 'op': '==', 'value': True}]} / 単位数: 80
- 見直す条件（反証）: 1/10 にならない単位があれば、uniform は槽と槽のあいだのずれの直し方として弱いと書く
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.324, f1=0.490, accuracy=0.375, balanced_accuracy=0.662, mcc=0.186
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 24 | 24 | 1.00 [0.86, 1.00] | — | 0.93 | 1.08 | 0.108 | 0 | 支持 | 0 |
| 対偶 | 6 | 6 | 1.00 [0.61, 1.00] | — | 0.70 | 1.43 | 0.108 | 0 | 判断保留 | 4 |
| 逆 | 74 | 24 | 0.32 [0.23, 0.44] | — | 0.30 | 1.08 | 0.108 | 0 | 棄却 | 3 |
| 裏 | 56 | 6 | 0.11 [0.05, 0.21] | — | 0.07 | 1.43 | 0.108 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 50 件（裏の判例も同じ）

- 2 段 τ2/τ=0.333 t=1τ uniform h=0.0478 9: h=0.048, gain_vs_independent=+129.59, tau2_ratio=0.333, span_ratio=+1.00, err=0.001 / surprise=+129.59
  - 2 段 τ2/τ=0.333 t=1τ uniform h=0.0478 9 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ uniform h=0.0478 9: h=0.048, gain_vs_independent=+129.59, tau2_ratio=0.333, span_ratio=+3.00, err=0.001 / surprise=+129.59
  - 2 段 τ2/τ=0.333 t=3τ uniform h=0.0478 9 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=3τ uniform h=0.0478 9: h=0.048, gain_vs_independent=+127.20, tau2_ratio=+1.50, span_ratio=+3.00, err=0.000 / surprise=+127.20
  - 2 段 τ2/τ=1.5 t=3τ uniform h=0.0478 9 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=1τ uniform h=0.0478 9: h=0.048, gain_vs_independent=+127.20, tau2_ratio=+1.50, span_ratio=+1.00, err=0.000 / surprise=+127.20
  - 2 段 τ2/τ=1.5 t=1τ uniform h=0.0478 9 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=3 t=1τ uniform h=0.0478 9: h=0.048, gain_vs_independent=+126.86, tau2_ratio=+3.00, span_ratio=+1.00, err=0.000 / surprise=+126.86
  - 2 段 τ2/τ=3 t=1τ uniform h=0.0478 9 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=3 t=3τ uniform h=0.0478 9: h=0.048, gain_vs_independent=+126.86, tau2_ratio=+3.00, span_ratio=+3.00, err=0.000 / surprise=+126.86
  - 2 段 τ2/τ=3 t=3τ uniform h=0.0478 9 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=8 t=1τ uniform h=0.0478 9: h=0.048, gain_vs_independent=+126.65, tau2_ratio=+8.00, span_ratio=+1.00, err=0.000 / surprise=+126.65
  - 2 段 τ2/τ=8 t=1τ uniform h=0.0478 9 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=8 t=3τ uniform h=0.0478 9: h=0.048, gain_vs_independent=+126.65, tau2_ratio=+8.00, span_ratio=+3.00, err=0.000 / surprise=+126.65
  - 2 段 τ2/τ=8 t=3τ uniform h=0.0478 9 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ uniform h=0.0625 4: h=0.062, gain_vs_independent=+100.08, tau2_ratio=0.333, span_ratio=+3.00, err=0.001 / surprise=+100.08
  - 2 段 τ2/τ=0.333 t=3τ uniform h=0.0625 4 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=1τ uniform h=0.0625 4: h=0.062, gain_vs_independent=+100.08, tau2_ratio=0.333, span_ratio=+1.00, err=0.001 / surprise=+100.08
  - 2 段 τ2/τ=0.333 t=1τ uniform h=0.0625 4 は「gain_vs_independent >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 40 件（propositions.jsonl を参照）

## O33: 槽が 2 段つながるとき、刻みが時定数の 1/32 以下なら、uniform のずれは刻みを半分にすると 1/4 になる（比 3.8〜4.2）

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `h <= 0.03125` ならば: `uniform_halving >= 3.8 かつ uniform_halving <= 4.2`
- 識別子: `[where:chain2==true, where:has_half==true, where:uniform==true] h<=0.03125 => uniform_halving<=4.2 & uniform_halving>=3.8`（指紋 `aed81e2a0a55dbbb`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain2', 'op': '==', 'value': True}, {'col': 'uniform', 'op': '==', 'value': True}, {'col': 'has_half', 'op': '==', 'value': True}]} / 単位数: 48
- 見直す条件（反証）: 比が外れる単位があれば、uniform の残りのずれは 2 次ではないと書く
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.333, f1=0.500, accuracy=0.333, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 6 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 16 | 1.00 [0.81, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.67 | - | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 48 | 16 | 0.33 [0.22, 0.47] | — | 0.33 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 裏 | 32 | 0 | 0.00 [0.00, 0.11] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 32 件（裏の判例も同じ）

- 2 段 τ2/τ=0.333 t=3τ uniform h=0.5 7: h=0.500, uniform_halving=+4.03, tau2_ratio=0.333, span_ratio=+3.00, err=0.063 / surprise=+4.03
  - 2 段 τ2/τ=0.333 t=3τ uniform h=0.5 7 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=1τ uniform h=0.5 7: h=0.500, uniform_halving=+4.03, tau2_ratio=0.333, span_ratio=+1.00, err=0.063 / surprise=+4.03
  - 2 段 τ2/τ=0.333 t=1τ uniform h=0.5 7 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=1τ uniform h=0.5 7: h=0.500, uniform_halving=+4.02, tau2_ratio=+1.50, span_ratio=+1.00, err=0.014 / surprise=+4.02
  - 2 段 τ2/τ=1.5 t=1τ uniform h=0.5 7 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=3τ uniform h=0.5 7: h=0.500, uniform_halving=+4.02, tau2_ratio=+1.50, span_ratio=+3.00, err=0.014 / surprise=+4.02
  - 2 段 τ2/τ=1.5 t=3τ uniform h=0.5 7 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=3τ uniform h=0.25 6: h=0.250, uniform_halving=+4.01, tau2_ratio=0.333, span_ratio=+3.00, err=0.016 / surprise=+4.01
  - 2 段 τ2/τ=0.333 t=3τ uniform h=0.25 6 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=0.333 t=1τ uniform h=0.25 6: h=0.250, uniform_halving=+4.01, tau2_ratio=0.333, span_ratio=+1.00, err=0.016 / surprise=+4.01
  - 2 段 τ2/τ=0.333 t=1τ uniform h=0.25 6 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=1τ uniform h=0.25 6: h=0.250, uniform_halving=+4.00, tau2_ratio=+1.50, span_ratio=+1.00, err=0.003 / surprise=+4.00
  - 2 段 τ2/τ=1.5 t=1τ uniform h=0.25 6 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=1.5 t=3τ uniform h=0.25 6: h=0.250, uniform_halving=+4.00, tau2_ratio=+1.50, span_ratio=+3.00, err=0.003 / surprise=+4.00
  - 2 段 τ2/τ=1.5 t=3τ uniform h=0.25 6 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=3 t=3τ uniform h=0.5 7: h=0.500, uniform_halving=+4.00, tau2_ratio=+3.00, span_ratio=+3.00, err=0.007 / surprise=+4.00
  - 2 段 τ2/τ=3 t=3τ uniform h=0.5 7 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ2/τ=3 t=1τ uniform h=0.5 7: h=0.500, uniform_halving=+4.00, tau2_ratio=+3.00, span_ratio=+1.00, err=0.007 / surprise=+4.00
  - 2 段 τ2/τ=3 t=1τ uniform h=0.5 7 は「uniform_halving >= 3.8 かつ uniform_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 22 件（propositions.jsonl を参照）

## O34: 槽が 2 段つながるとき、2 段を 1 ステップぶん厳密に解く方式（through）なら 2 段目は厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:chain2==true, where:through==true] * => err_abs<1e-09`（指紋 `9c141c09a1f75fee`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain2', 'op': '==', 'value': True}, {'col': 'through', 'op': '==', 'value': True}]} / 単位数: 80
- 見直す条件（反証）: ずれる単位があれば、2 段の閉じた式の入れ方を見直す
- 注記: through は上の槽の量と速さを知っている前提の式で、上がポンプや何本もの管のときにはそのまま使えない
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 6 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 6 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 80 | 80 | 1.00 [0.95, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O35: エンジンに入れた uniform で、ポンプから入って弁 1 本から出る槽は厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:flow==true, where:from_pump==true] * => err_abs<1e-09`（指紋 `369fa5e4e0f29c72`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'flow', 'op': '==', 'value': True}, {'col': 'from_pump', 'op': '==', 'value': True}]} / 単位数: 30
- 見直す条件（反証）: ずれる単位があれば、エンジンへの入れ方（先に全部の管の量を決め、後から弁を増やす）を見直す
- 注記: O30 は整数の漸化式で確かめた。これはエンジン本体の実装を同じ条件で確かめ直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 30 | 30 | 1.00 [0.89, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O36: エンジンに入れた uniform で、2 段の槽の 2 段目は、第3弾の整数の漸化式（uniform）と同じずれになる

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `native_gap < 1e-09`
- 識別子: `[where:flow==true, where:from_pump==false] * => native_gap<1e-09`（指紋 `bc220c9245f81a53`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'flow', 'op': '==', 'value': True}, {'col': 'from_pump', 'op': '==', 'value': False}]} / 単位数: 80
- 見直す条件（反証）: 違う単位があれば、エンジンの実装と第3弾の式のどちらかが違うものを計算している
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 80 | 80 | 1.00 [0.95, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O37: 入るポンプ・何本もの弁・出るポンプがある槽は、エンジンに入れた uniform なら厳密である

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:combo==true, where:uniform_in==true] * => err_abs<1e-09`（指紋 `76b53505a6021050`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'combo', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}]} / 単位数: 50
- 見直す条件（反証）: ずれる単位があれば、弁の合計 = V·Φ + (I − P)·(1 − Φ/L) の式か、その入れ方を見直す
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 50 | 50 | 1.00 [0.93, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O38: 入るポンプ・何本もの弁・出るポンプがある槽は、今までの入る量の扱い（end）では厳密でない

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs >= 1e-09`
- 識別子: `[where:combo==true, where:uniform_in==false] * => err_abs>=1e-09`（指紋 `9a0c523cf14c9ec0`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'combo', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': False}]} / 単位数: 50
- 見直す条件（反証）: 厳密な単位があれば、入る量のずれは出るポンプや弁の本数と打ち消し合うことがあると書く
- 注記: O28（ポンプから入る槽は今のエンジンでずれる）を、弁が何本もあって出るポンプもある槽に広げた向き
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 50 | 50 | 1.00 [0.93, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O39: 槽が 3 段つながるとき、今までの入る量の扱い（end）で、刻みが時定数の 1/32 以下なら、3 段目のずれは dt/(2·τ2) + dt/(2·τ3) と 5 % 以内で合う

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 12 件: chain3-r3-r5-end-3, chain3-r3-r5-end-2, chain3-r3-r5-end-1, chain3-r0.333-r3-end-3, chain3-r0.333-r3-end-2 ほか
- もし: `h <= 0.03125` ならば: `chain3_pred_rel <= 0.05`
- 識別子: `[where:chain3==true, where:uniform_in==false] h<=0.03125 => chain3_pred_rel<=0.05`（指紋 `9c4b8cc89d690953`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': False}]} / 単位数: 40
- 見直す条件（反証）: 外れる単位があれば、ずれは段ごとに足し算で積み上がるという読みを見直す
- 注記: O27 の説明（入った量が半ステップぶん減りそこねる）を 3 段に延ばした予想。3 段目の中身は 2 段目と 3 段目を通ってきたので、両方の分だけ多い
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.000, recall=0.000, f1=0.000, accuracy=0.650, balanced_accuracy=0.342, mcc=-0.150
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 0 | 0.00 [0.00, 0.24] | — | 0.05 | 0.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 38 | 26 | 0.68 [0.53, 0.81] | — | 0.70 | 0.98 | 1.000 | 0 | 棄却 | 3 |
| 逆 | 2 | 0 | 0.00 [0.00, 0.66] | — | 0.30 | 0.00 | 1.000 | 0 | 判断保留 | 4 |
| 裏 | 28 | 26 | 0.93 [0.77, 0.98] | — | 0.95 | 0.98 | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 12 件（対偶の判例も同じ）

- 3 段 τ2/τ=3 τ3/τ=5 end h=0.03125 3: h=0.031, chain3_pred_rel=+1.66, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.005 / surprise=+1.66
  - 3 段 τ2/τ=3 τ3/τ=5 end h=0.03125 3 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 end h=0.015625 2: h=0.016, chain3_pred_rel=+1.65, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.003 / surprise=+1.65
  - 3 段 τ2/τ=3 τ3/τ=5 end h=0.015625 2 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 end h=0.0078125 1: h=0.008, chain3_pred_rel=+1.65, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.001 / surprise=+1.65
  - 3 段 τ2/τ=3 τ3/τ=5 end h=0.0078125 1 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=0.333 τ3/τ=3 end h=0.03125 3: h=0.031, chain3_pred_rel=0.906, tau2_ratio=0.333, tau3_ratio=+3.00, err=0.005 / surprise=0.906
  - 3 段 τ2/τ=0.333 τ3/τ=3 end h=0.03125 3 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=0.333 τ3/τ=3 end h=0.015625 2: h=0.016, chain3_pred_rel=0.906, tau2_ratio=0.333, tau3_ratio=+3.00, err=0.002 / surprise=0.906
  - 3 段 τ2/τ=0.333 τ3/τ=3 end h=0.015625 2 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=0.333 τ3/τ=3 end h=0.0078125 1: h=0.008, chain3_pred_rel=0.906, tau2_ratio=0.333, tau3_ratio=+3.00, err=0.001 / surprise=0.906
  - 3 段 τ2/τ=0.333 τ3/τ=3 end h=0.0078125 1 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 end h=0.0078125 1: h=0.008, chain3_pred_rel=0.258, tau2_ratio=0.500, tau3_ratio=0.333, err=0.015 / surprise=0.258
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 end h=0.0078125 1 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 end h=0.015625 2: h=0.016, chain3_pred_rel=0.252, tau2_ratio=0.500, tau3_ratio=0.333, err=0.029 / surprise=0.252
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 end h=0.015625 2 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 end h=0.03125 3: h=0.031, chain3_pred_rel=0.242, tau2_ratio=0.500, tau3_ratio=0.333, err=0.059 / surprise=0.242
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 end h=0.03125 3 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- 3 段 τ2/τ=2 τ3/τ=0.5 end h=0.0078125 1: h=0.008, chain3_pred_rel=0.200, tau2_ratio=+2.00, tau3_ratio=0.500, err=0.008 / surprise=0.200
  - 3 段 τ2/τ=2 τ3/τ=0.5 end h=0.0078125 1 は「h <= 0.03125」を満たすのに「chain3_pred_rel <= 0.05」を満たさない。なぜか？
- ほか 2 件（propositions.jsonl を参照）

**待った！判断保留** 逆に判例 2 件（裏の判例も同じ）

- 3 段 τ2/τ=2 τ3/τ=0.5 end h=0.74 10: h=0.740, chain3_pred_rel=0.040, tau2_ratio=+2.00, tau3_ratio=0.500, err=0.962 / surprise=0.040
  - 3 段 τ2/τ=2 τ3/τ=0.5 end h=0.74 10 は「chain3_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 end h=0.343 8: h=0.343, chain3_pred_rel=0.011, tau2_ratio=0.500, tau3_ratio=0.333, err=0.867 / surprise=0.011
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 end h=0.343 8 は「chain3_pred_rel <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？

## O40: 槽が 3 段つながるとき、刻みが時定数の 1/32 以下なら、エンジンに入れた uniform は 3 段目のずれを end の 1/10 以下にする

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 17 件: chain3-r3-r5-uniform_in-9, chain3-r3-r5-uniform_in-4, chain3-r3-r5-uniform_in-5, chain3-r2-r0.5-uniform_in-9, chain3-r3-r5-uniform_in-6 ほか
- もし: `h <= 0.03125` ならば: `gain_vs_end >= 10`
- 識別子: `[where:chain3==true, where:uniform_in==true] h<=0.03125 => gain_vs_end>=10`（指紋 `f11ee64fb0987772`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}]} / 単位数: 40
- 見直す条件（反証）: 1/10 にならない単位があれば、増やした分を下の槽の入る量に数えない入れ方が 3 段では足りないと書く
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.414, f1=0.585, accuracy=0.575, balanced_accuracy=0.707, mcc=0.403
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 12 | 1.00 [0.76, 1.00] | — | 0.72 | 1.38 | 0.009 | 0 | 支持 | 0 |
| 対偶 | 11 | 11 | 1.00 [0.74, 1.00] | — | 0.70 | 1.43 | 0.009 | 0 | 支持 | 0 |
| 逆 | 29 | 12 | 0.41 [0.26, 0.59] | — | 0.30 | 1.38 | 0.009 | 0 | 棄却 | 3 |
| 裏 | 28 | 11 | 0.39 [0.24, 0.58] | — | 0.28 | 1.43 | 0.009 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 17 件（裏の判例も同じ）

- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.0478 9: h=0.048, gain_vs_end=+347.36, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.000 / surprise=+347.36
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.0625 4: h=0.062, gain_vs_end=+264.77, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.000 / surprise=+264.77
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.0625 4 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.125 5: h=0.125, gain_vs_end=+134.20, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.000 / surprise=+134.20
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.125 5 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.0478 9: h=0.048, gain_vs_end=+84.18, tau2_ratio=+2.00, tau3_ratio=0.500, err=0.001 / surprise=+84.18
  - 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.25 6: h=0.250, gain_vs_end=+68.94, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.001 / surprise=+68.94
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.25 6 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.0625 4: h=0.062, gain_vs_end=+64.20, tau2_ratio=+2.00, tau3_ratio=0.500, err=0.001 / surprise=+64.20
  - 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.0625 4 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.343 8: h=0.343, gain_vs_end=+53.81, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.001 / surprise=+53.81
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.343 8 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.5 7: h=0.500, gain_vs_end=+36.37, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.003 / surprise=+36.37
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.5 7 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.0478 9: h=0.048, gain_vs_end=+33.39, tau2_ratio=0.500, tau3_ratio=0.333, err=0.003 / surprise=+33.39
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.125 5: h=0.125, gain_vs_end=+32.37, tau2_ratio=+2.00, tau3_ratio=0.500, err=0.004 / surprise=+32.37
  - 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.125 5 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 7 件（propositions.jsonl を参照）

## O41: 槽が 3 段つながるとき、刻みが時定数の 1/32 以下なら、エンジンに入れた uniform のずれは刻みを半分にすると 1/4 になる（比 3.8〜4.2）

- **判定: exit 4 待った！判断保留** — 元の命題: n=8（min_n=10）、成立率の区間 0.68〜1.00
- もし: `h <= 0.03125` ならば: `flow_halving >= 3.8 かつ flow_halving <= 4.2`
- 識別子: `[where:chain3==true, where:has_half==true, where:uniform_in==true] h<=0.03125 => flow_halving<=4.2 & flow_halving>=3.8`（指紋 `568bb12a1097c1c9`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}, {'col': 'has_half', 'op': '==', 'value': True}]} / 単位数: 24
- 見直す条件（反証）: 比が外れる単位があれば、3 段では uniform の残りのずれは 2 次ではないと書く
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.421, f1=0.593, accuracy=0.542, balanced_accuracy=0.711, mcc=0.363
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 8 | 8 | 1.00 [0.68, 1.00] | — | 0.79 | 1.26 | 0.103 | 0 | 判断保留 | 4 |
| 対偶 | 5 | 5 | 1.00 [0.57, 1.00] | — | 0.67 | 1.50 | 0.103 | 0 | 判断保留 | 4 |
| 逆 | 19 | 8 | 0.42 [0.23, 0.64] | — | 0.33 | 1.26 | 0.103 | 0 | 棄却 | 3 |
| 裏 | 16 | 5 | 0.31 [0.14, 0.56] | — | 0.21 | 1.50 | 0.103 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 11 件（裏の判例も同じ）

- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.25 6: h=0.250, flow_halving=+4.17, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.001 / surprise=+4.17
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.25 6 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.25 6: h=0.250, flow_halving=+4.09, tau2_ratio=+2.00, tau3_ratio=0.500, err=0.016 / surprise=+4.09
  - 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.25 6 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.125 5: h=0.125, flow_halving=+4.08, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.000 / surprise=+4.08
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.125 5 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.125 5: h=0.125, flow_halving=+4.04, tau2_ratio=+2.00, tau3_ratio=0.500, err=0.004 / surprise=+4.04
  - 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.125 5 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.0625 4: h=0.062, flow_halving=+4.04, tau2_ratio=+3.00, tau3_ratio=+5.00, err=-0.000 / surprise=+4.04
  - 3 段 τ2/τ=3 τ3/τ=5 uniform_in h=0.0625 4 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.0625 4: h=0.062, flow_halving=+4.02, tau2_ratio=+2.00, tau3_ratio=0.500, err=0.001 / surprise=+4.02
  - 3 段 τ2/τ=2 τ3/τ=0.5 uniform_in h=0.0625 4 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.0625 4: h=0.062, flow_halving=+3.99, tau2_ratio=0.500, tau3_ratio=0.333, err=0.005 / surprise=+3.99
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.0625 4 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.5 7: h=0.500, flow_halving=+3.98, tau2_ratio=0.500, tau3_ratio=0.333, err=0.295 / surprise=+3.98
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.5 7 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.125 5: h=0.125, flow_halving=+3.97, tau2_ratio=0.500, tau3_ratio=0.333, err=0.019 / surprise=+3.97
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.125 5 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.25 6: h=0.250, flow_halving=+3.96, tau2_ratio=0.500, tau3_ratio=0.333, err=0.074 / surprise=+3.96
  - 3 段 τ2/τ=0.5 τ3/τ=0.333 uniform_in h=0.25 6 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 1 件（propositions.jsonl を参照）

## O42: 2 つの槽が輪になっていて行き渡る途中のとき、刻みが時定数の 1/32 以下なら、エンジンに入れた uniform はずれを end の 1/10 以下にする

- **判定: exit 4 待った！判断保留** — 対偶: n=8（min_n=10）、成立率の区間 0.68〜1.00
- もし: `h <= 0.03125` ならば: `gain_vs_end >= 10`
- 識別子: `[where:ring==true, where:settled==false, where:uniform_in==true] h<=0.03125 => gain_vs_end>=10`（指紋 `c6505c5665ebb115`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'ring', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}, {'col': 'settled', 'op': '==', 'value': False}]} / 単位数: 40
- 見直す条件（反証）: 1/10 にならない単位があれば、輪（入る量が自分の出した量に戻ってくる）では uniform の効きが弱いと書く
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.375, f1=0.545, accuracy=0.500, balanced_accuracy=0.688, mcc=0.327
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 12 | 1.00 [0.76, 1.00] | — | 0.80 | 1.25 | 0.040 | 0 | 支持 | 0 |
| 対偶 | 8 | 8 | 1.00 [0.68, 1.00] | — | 0.70 | 1.43 | 0.040 | 0 | 判断保留 | 4 |
| 逆 | 32 | 12 | 0.38 [0.23, 0.55] | — | 0.30 | 1.25 | 0.040 | 0 | 棄却 | 3 |
| 裏 | 28 | 8 | 0.29 [0.15, 0.47] | — | 0.20 | 1.43 | 0.040 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 20 件（裏の判例も同じ）

- 輪 τ2/τ=0.25 t=2T uniform_in h=0.0478 9: h=0.048, gain_vs_end=+252.55, tau2_ratio=0.250, err=-0.000 / surprise=+252.55
  - 輪 τ2/τ=0.25 t=2T uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=0.5 t=2T uniform_in h=0.0478 9: h=0.048, gain_vs_end=+206.25, tau2_ratio=0.500, err=-0.000 / surprise=+206.25
  - 輪 τ2/τ=0.5 t=2T uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=0.25 t=2T uniform_in h=0.0625 4: h=0.062, gain_vs_end=+184.14, tau2_ratio=0.250, err=-0.001 / surprise=+184.14
  - 輪 τ2/τ=0.25 t=2T uniform_in h=0.0625 4 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=0.5 t=2T uniform_in h=0.0625 4: h=0.062, gain_vs_end=+158.39, tau2_ratio=0.500, err=-0.000 / surprise=+158.39
  - 輪 τ2/τ=0.5 t=2T uniform_in h=0.0625 4 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=0.25 t=2T uniform_in h=0.125 5: h=0.125, gain_vs_end=+81.41, tau2_ratio=0.250, err=-0.002 / surprise=+81.41
  - 輪 τ2/τ=0.25 t=2T uniform_in h=0.125 5 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=0.5 t=2T uniform_in h=0.125 5: h=0.125, gain_vs_end=+68.86, tau2_ratio=0.500, err=-0.001 / surprise=+68.86
  - 輪 τ2/τ=0.5 t=2T uniform_in h=0.125 5 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=0.25 t=2T uniform_in h=0.25 6: h=0.250, gain_vs_end=+41.50, tau2_ratio=0.250, err=-0.009 / surprise=+41.50
  - 輪 τ2/τ=0.25 t=2T uniform_in h=0.25 6 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=2 t=2T uniform_in h=0.0478 9: h=0.048, gain_vs_end=+34.99, tau2_ratio=+2.00, err=-0.000 / surprise=+34.99
  - 輪 τ2/τ=2 t=2T uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=0.5 t=2T uniform_in h=0.25 6: h=0.250, gain_vs_end=+33.56, tau2_ratio=0.500, err=-0.004 / surprise=+33.56
  - 輪 τ2/τ=0.5 t=2T uniform_in h=0.25 6 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 輪 τ2/τ=4 t=2T uniform_in h=0.0478 9: h=0.048, gain_vs_end=+31.04, tau2_ratio=+4.00, err=-0.000 / surprise=+31.04
  - 輪 τ2/τ=4 t=2T uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 10 件（propositions.jsonl を参照）

## O43: 2 つの槽が輪になっているとき、エンジンに入れた uniform なら、行き渡った後の槽の量は厳密である（滞在時間の比どおり）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 1 件: ring-r0.25-s40-uniform_in-10
- もし: `（すべての単位）` ならば: `err_abs < 1e-09`
- 識別子: `[where:ring==true, where:settled==true, where:uniform_in==true] * => err_abs<1e-09`（指紋 `8e4d2ca5728ebe89`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'ring', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}, {'col': 'settled', 'op': '==', 'value': True}]} / 単位数: 40
- 見直す条件（反証）: ずれる単位があれば、行き渡った後でも uniform は厳密な取り分を出さないと書く
- 注記: 行き渡った後は入る量が一定になるので、uniform の前提（一定の速さで入る）が成り立つはず、という予想
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.975, recall=1.000, f1=0.987, accuracy=0.975, balanced_accuracy=0.500, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 4 回（どれかの形に異議あり 4 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 40 | 39 | 0.97 [0.87, 1.00] | — | 0.97 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 対偶 | 1 | 0 | 0.00 [0.00, 0.79] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

**異議あり（不成立）** 元の命題に判例 1 件（対偶の判例も同じ）

- 輪 τ2/τ=0.25 t=40T uniform_in h=0.74 10: err_abs=0.000, h=0.740, tau2_ratio=0.250, err=-0.000 / surprise=-0.000
  - 輪 τ2/τ=0.25 t=40T uniform_in h=0.74 10 は「（すべての単位）」を満たすのに「err_abs < 1e-09」を満たさない。なぜか？

## O44: 2 つの槽が輪になっているとき、今までの入る量の扱い（end）では、行き渡った後の槽の量は厳密でない

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `err_abs >= 1e-09`
- 識別子: `[where:ring==true, where:settled==true, where:uniform_in==false] * => err_abs>=1e-09`（指紋 `3205cd875c2c84b3`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'ring', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': False}, {'col': 'settled', 'op': '==', 'value': True}]} / 単位数: 40
- 見直す条件（反証）: 厳密な単位があれば、輪では 2 つの槽のずれが打ち消し合うことがあると書く
- 注記: FluidFullSpeedSimulation の 🪙 金（E27）で、離散の定常が連続の式から刻みの 1 次だけ外れていたのと同じ向き
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 4 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 4 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 40 | 40 | 1.00 [0.91, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O45: 槽が 3 段つながるとき、今までの入る量の扱い（end）で、刻みが時定数の 1/32 以下なら、3 段目のずれは G_eff の式と合う（差は目安 (dt/2)·(k2 + k3) の 5 % 以内）

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 41 件: chain3b-r6-r0.2-s3-end-4, chain3b-r0.4-r2.5-s3-end-7, chain3b-r4-r1.5-s1-end-9, chain3b-r1.5-r4-s1-end-4, chain3b-r1.5-r4-s3-end-8 ほか
- もし: `h <= 0.03125` ならば: `stage_fit <= 0.05`
- 識別子: `[where:chain3b==true, where:uniform_in==false] h<=0.03125 => stage_fit<=0.05`（指紋 `a7c25656efd5fb0f`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain3b', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': False}]} / 単位数: 132
- 親: O39（変更: 予想の式を、段ごとの足し算から G_eff = G − (dt/2)·(D + G²) に替えた（1 つ飛ばしで引かれる項が入る）。単位は別の組）
- 見直す条件（反証）: 外れる単位があれば、1 ステップを連続の式に読み替える導き方（dt の 1 次まで）を見直す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.539, f1=0.701, accuracy=0.689, balanced_accuracy=0.770, mcc=0.525
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 3 回、元の命題に異議あり 0 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 3 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 48 | 1.00 [0.93, 1.00] | — | 0.67 | 1.48 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 43 | 43 | 1.00 [0.92, 1.00] | — | 0.64 | 1.57 | 0.000 | 0 | 支持 | 0 |
| 逆 | 89 | 48 | 0.54 [0.44, 0.64] | — | 0.36 | 1.48 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 84 | 43 | 0.51 [0.41, 0.62] | — | 0.33 | 1.57 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 41 件（裏の判例も同じ）

- 3 段 τ比 6・0.2-s3 end h=0.0625 4: h=0.062, stage_fit=0.049, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+3.00, err=0.167 / surprise=0.049
  - 3 段 τ比 6・0.2-s3 end h=0.0625 4 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s3 end h=0.5 7: h=0.500, stage_fit=0.048, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+3.00, err=0.183 / surprise=0.048
  - 3 段 τ比 0.4・2.5-s3 end h=0.5 7 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1 end h=0.0478 9: h=0.048, stage_fit=0.048, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.00, err=-0.018 / surprise=0.048
  - 3 段 τ比 4・1.5-s1 end h=0.0478 9 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s1 end h=0.0625 4: h=0.062, stage_fit=0.048, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.00, err=-0.037 / surprise=0.048
  - 3 段 τ比 1.5・4-s1 end h=0.0625 4 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s3 end h=0.343 8: h=0.343, stage_fit=0.044, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+3.00, err=0.027 / surprise=0.044
  - 3 段 τ比 1.5・4-s3 end h=0.343 8 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.25・0.75-s3 end h=0.343 8: h=0.343, stage_fit=0.044, tau2_ratio=0.250, tau3_ratio=0.750, span_ratio=+3.00, err=0.478 / surprise=0.044
  - 3 段 τ比 0.25・0.75-s3 end h=0.343 8 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.25・0.75-s3 end h=0.25 6: h=0.250, stage_fit=0.038, tau2_ratio=0.250, tau3_ratio=0.750, span_ratio=+3.00, err=0.320 / surprise=0.038
  - 3 段 τ比 0.25・0.75-s3 end h=0.25 6 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 6・0.2-s3 end h=0.0478 9: h=0.048, stage_fit=0.037, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+3.00, err=0.126 / surprise=0.037
  - 3 段 τ比 6・0.2-s3 end h=0.0478 9 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s1 end h=0.0478 9: h=0.048, stage_fit=0.036, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.00, err=-0.028 / surprise=0.036
  - 3 段 τ比 1.5・4-s1 end h=0.0478 9 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.25・0.75-s3 end h=0.74 10: h=0.740, stage_fit=0.035, tau2_ratio=0.250, tau3_ratio=0.750, span_ratio=+3.00, err=+1.44 / surprise=0.035
  - 3 段 τ比 0.25・0.75-s3 end h=0.74 10 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 31 件（propositions.jsonl を参照）

## O46: 槽が 3 段つながるとき、刻みが時定数の 1/32 以下なら、3 段目のずれの向き（多いか少ないか）は G_eff の式の向きと同じである

- **判定: exit 4 待った！判断保留** — 対偶: n=3（min_n=10）、成立率の区間 0.44〜1.00
- もし: `h <= 0.03125` ならば: `sign_ok == True`
- 識別子: `[where:chain3b==true, where:uniform_in==false] h<=0.03125 => sign_ok==true`（指紋 `c642abefc0e4da4c`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain3b', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': False}]} / 単位数: 132
- 見直す条件（反証）: 向きが違う単位があれば、式の予想が 0 に近い組（2 つの項が打ち消し合う所）では向きまでは当たらないと書く
- 注記: O39 の判例に、ずれが少ない側（向きが逆）の組があったことを受けた命題
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.372, f1=0.542, accuracy=0.386, balanced_accuracy=0.686, mcc=0.115
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 3 回、元の命題に異議あり 0 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 3 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 48 | 1.00 [0.93, 1.00] | — | 0.98 | 1.02 | 0.254 | 0 | 支持 | 0 |
| 対偶 | 3 | 3 | 1.00 [0.44, 1.00] | — | 0.64 | 1.57 | 0.254 | 0 | 判断保留 | 4 |
| 逆 | 129 | 48 | 0.37 [0.29, 0.46] | — | 0.36 | 1.02 | 0.254 | 0 | 棄却 | 3 |
| 裏 | 84 | 3 | 0.04 [0.01, 0.10] | — | 0.02 | 1.57 | 0.254 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 81 件（裏の判例も同じ）

- 3 段 τ比 0.25・0.75-s1 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=0.250, tau3_ratio=0.750, span_ratio=+1.00, err=0.033
  - 3 段 τ比 0.25・0.75-s1 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.25・0.75-s3 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=0.250, tau3_ratio=0.750, span_ratio=+3.00, err=0.069
  - 3 段 τ比 0.25・0.75-s3 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.00, err=-0.016
  - 3 段 τ比 0.4・2.5-s1 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s3 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+3.00, err=0.020
  - 3 段 τ比 0.4・2.5-s3 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.75・0.25-s1 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=0.750, tau3_ratio=0.250, span_ratio=+1.00, err=0.121
  - 3 段 τ比 0.75・0.25-s1 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.75・0.25-s3 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=0.750, tau3_ratio=0.250, span_ratio=+3.00, err=0.159
  - 3 段 τ比 0.75・0.25-s3 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s1 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.00, err=-0.037
  - 3 段 τ比 1.5・4-s1 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s3 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+3.00, err=0.005
  - 3 段 τ比 1.5・4-s3 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.00, err=-0.024
  - 3 段 τ比 4・1.5-s1 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s3 end h=0.0625 4: h=0.062, sign_ok=True, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+3.00, err=0.018
  - 3 段 τ比 4・1.5-s3 end h=0.0625 4 は「sign_ok == True」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 71 件（propositions.jsonl を参照）

## O49: 槽が 4 段つながるとき、今までの入る量の扱い（end）で、刻みが時定数の 1/32 以下なら、4 段目のずれは G_eff の式と合う（差は目安 (dt/2)·(k2 + k3 + k4) の 5 % 以内）

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 13 件: chain4-r2-r0.5-r3-end-5, chain4-r0.5-r0.333-r0.25-end-5, chain4-r0.333-r3-r0.5-end-6, chain4-r3-r5-r2-end-5, chain4-r2-r0.5-r3-end-4 ほか
- もし: `h <= 0.03125` ならば: `stage_fit <= 0.05`
- 識別子: `[where:chain4==true] h<=0.03125 => stage_fit<=0.05`（指紋 `31e3bd5b2cf17b9b`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain4', 'op': '==', 'value': True}]} / 単位数: 44
- 見直す条件（反証）: 外れる単位があれば、G_eff の式は 3 段までしか当たらないと書く
- 注記: 同じ式を、導くときに考えていない段数で確かめる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.552, f1=0.711, accuracy=0.705, balanced_accuracy=0.776, mcc=0.544
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 3 回、元の命題に異議あり 0 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 3 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 16 | 1.00 [0.81, 1.00] | — | 0.66 | 1.52 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 15 | 15 | 1.00 [0.80, 1.00] | — | 0.64 | 1.57 | 0.000 | 0 | 支持 | 0 |
| 逆 | 29 | 16 | 0.55 [0.38, 0.72] | — | 0.36 | 1.52 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 28 | 15 | 0.54 [0.36, 0.70] | — | 0.34 | 1.57 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 13 件（裏の判例も同じ）

- 4 段 τ比 2・0.5・3 end h=0.125 5: h=0.125, stage_fit=0.039, tau2_ratio=+2.00, tau3_ratio=0.500, tau4_ratio=+3.00, err=-0.071 / surprise=0.039
  - 4 段 τ比 2・0.5・3 end h=0.125 5 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 0.5・0.333・0.25 end h=0.125 5: h=0.125, stage_fit=0.036, tau2_ratio=0.500, tau3_ratio=0.333, tau4_ratio=0.250, err=0.361 / surprise=0.036
  - 4 段 τ比 0.5・0.333・0.25 end h=0.125 5 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 0.333・3・0.5 end h=0.25 6: h=0.250, stage_fit=0.033, tau2_ratio=0.333, tau3_ratio=+3.00, tau4_ratio=0.500, err=0.150 / surprise=0.033
  - 4 段 τ比 0.333・3・0.5 end h=0.25 6 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 3・5・2 end h=0.125 5: h=0.125, stage_fit=0.027, tau2_ratio=+3.00, tau3_ratio=+5.00, tau4_ratio=+2.00, err=-0.102 / surprise=0.027
  - 4 段 τ比 3・5・2 end h=0.125 5 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 2・0.5・3 end h=0.0625 4: h=0.062, stage_fit=0.019, tau2_ratio=+2.00, tau3_ratio=0.500, tau4_ratio=+3.00, err=-0.034 / surprise=0.019
  - 4 段 τ比 2・0.5・3 end h=0.0625 4 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 0.5・0.333・0.25 end h=0.0625 4: h=0.062, stage_fit=0.016, tau2_ratio=0.500, tau3_ratio=0.333, tau4_ratio=0.250, err=0.169 / surprise=0.016
  - 4 段 τ比 0.5・0.333・0.25 end h=0.0625 4 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 2・0.5・3 end h=0.0478 9: h=0.048, stage_fit=0.014, tau2_ratio=+2.00, tau3_ratio=0.500, tau4_ratio=+3.00, err=-0.025 / surprise=0.014
  - 4 段 τ比 2・0.5・3 end h=0.0478 9 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 3・5・2 end h=0.0625 4: h=0.062, stage_fit=0.014, tau2_ratio=+3.00, tau3_ratio=+5.00, tau4_ratio=+2.00, err=-0.050 / surprise=0.014
  - 4 段 τ比 3・5・2 end h=0.0625 4 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 0.5・0.333・0.25 end h=0.0478 9: h=0.048, stage_fit=0.012, tau2_ratio=0.500, tau3_ratio=0.333, tau4_ratio=0.250, err=0.128 / surprise=0.012
  - 4 段 τ比 0.5・0.333・0.25 end h=0.0478 9 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 4 段 τ比 3・5・2 end h=0.0478 9: h=0.048, stage_fit=0.011, tau2_ratio=+3.00, tau3_ratio=+5.00, tau4_ratio=+2.00, err=-0.037 / surprise=0.011
  - 4 段 τ比 3・5・2 end h=0.0478 9 は「stage_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 3 件（propositions.jsonl を参照）

## O47: 槽が 3 段つながるとき、刻みが時定数の 1/32 以下なら、エンジンの uniform のずれは刻みを半分にすると 1/4 になる（比 3.8〜4.2）

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 26 件: chain3b-r1.5-r4-s1-uniform_in-4, chain3b-r6-r0.2-s3-uniform_in-5, chain3b-r6-r0.2-s1-uniform_in-4, chain3b-r0.75-r0.25-s1-uniform_in-6, chain3b-r4-r1.5-s1-uniform_in-7 ほか
- もし: `h <= 0.03125` ならば: `flow_halving >= 3.8 かつ flow_halving <= 4.2`
- 識別子: `[where:chain3b==true, where:has_half==true, where:uniform_in==true] h<=0.03125 => flow_halving<=4.2 & flow_halving>=3.8`（指紋 `125138b6dee2d012`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain3b', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}, {'col': 'has_half', 'op': '==', 'value': True}]} / 単位数: 84
- 親: O41（変更: 問いは同じ。当たる単位が 8 件で判断保留だったので、別の組（chain3b、刻み 1/256 を足した）で問い直す）
- 見直す条件（反証）: 比が外れる単位があれば、3 段では uniform の残りのずれは 2 次ではないと書く
- 条件の数: 3（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.581, f1=0.735, accuracy=0.690, balanced_accuracy=0.790, mcc=0.516
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 3 回、元の命題に異議あり 0 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 3 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 36 | 36 | 1.00 [0.90, 1.00] | — | 0.74 | 1.35 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 22 | 22 | 1.00 [0.85, 1.00] | — | 0.57 | 1.75 | 0.000 | 0 | 支持 | 0 |
| 逆 | 62 | 36 | 0.58 [0.46, 0.70] | — | 0.43 | 1.35 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 48 | 22 | 0.46 [0.33, 0.60] | — | 0.26 | 1.75 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 26 件（裏の判例も同じ）

- 3 段 τ比 1.5・4-s1 uniform_in h=0.0625 4: h=0.062, flow_halving=+4.17, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.00, err=-0.000 / surprise=+4.17
  - 3 段 τ比 1.5・4-s1 uniform_in h=0.0625 4 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 6・0.2-s3 uniform_in h=0.125 5: h=0.125, flow_halving=+4.15, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+3.00, err=0.003 / surprise=+4.15
  - 3 段 τ比 6・0.2-s3 uniform_in h=0.125 5 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 6・0.2-s1 uniform_in h=0.0625 4: h=0.062, flow_halving=+4.14, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+1.00, err=0.003 / surprise=+4.14
  - 3 段 τ比 6・0.2-s1 uniform_in h=0.0625 4 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.75・0.25-s1 uniform_in h=0.25 6: h=0.250, flow_halving=+4.13, tau2_ratio=0.750, tau3_ratio=0.250, span_ratio=+1.00, err=0.098 / surprise=+4.13
  - 3 段 τ比 0.75・0.25-s1 uniform_in h=0.25 6 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1 uniform_in h=0.5 7: h=0.500, flow_halving=+4.12, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.00, err=0.021 / surprise=+4.12
  - 3 段 τ比 4・1.5-s1 uniform_in h=0.5 7 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.75・0.25-s3 uniform_in h=0.25 6: h=0.250, flow_halving=+4.09, tau2_ratio=0.750, tau3_ratio=0.250, span_ratio=+3.00, err=0.058 / surprise=+4.09
  - 3 段 τ比 0.75・0.25-s3 uniform_in h=0.25 6 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 6・0.2-s3 uniform_in h=0.0625 4: h=0.062, flow_halving=+4.07, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+3.00, err=0.001 / surprise=+4.07
  - 3 段 τ比 6・0.2-s3 uniform_in h=0.0625 4 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.75・0.25-s1 uniform_in h=0.125 5: h=0.125, flow_halving=+4.06, tau2_ratio=0.750, tau3_ratio=0.250, span_ratio=+1.00, err=0.024 / surprise=+4.06
  - 3 段 τ比 0.75・0.25-s1 uniform_in h=0.125 5 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1 uniform_in h=0.25 6: h=0.250, flow_halving=+4.05, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.00, err=0.005 / surprise=+4.05
  - 3 段 τ比 4・1.5-s1 uniform_in h=0.25 6 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s3 uniform_in h=0.5 7: h=0.500, flow_halving=+4.05, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+3.00, err=0.011 / surprise=+4.05
  - 3 段 τ比 4・1.5-s3 uniform_in h=0.5 7 は「flow_halving >= 3.8 かつ flow_halving <= 4.2」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 16 件（propositions.jsonl を参照）

## O48: 槽が 3 段つながるとき、刻みが時定数の 1/32 以下なら、エンジンの uniform は 3 段目のずれを end の 1/10 以下にする（別の組で）

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 50 件: chain3b-r1.5-r4-s1-uniform_in-9, chain3b-r1.5-r4-s1-uniform_in-4, chain3b-r6-r0.2-s3-uniform_in-9, chain3b-r6-r0.2-s3-uniform_in-4, chain3b-r1.5-r4-s1-uniform_in-5 ほか
- もし: `h <= 0.03125` ならば: `gain_vs_end >= 10`
- 識別子: `[where:chain3b==true, where:uniform_in==true] h<=0.03125 => gain_vs_end>=10`（指紋 `6d8c481df3dd23bd`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'chain3b', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}]} / 単位数: 132
- 見直す条件（反証）: 1/10 にならない単位があれば、O40 の支持は第4弾の 4 組に寄っていたと書く
- 注記: O40 と同じ問いを、別の時定数と別の時刻で確かめる。end のずれが 0 に近い組（O46 の所）では比が小さく出うる
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.490, f1=0.658, accuracy=0.621, balanced_accuracy=0.745, mcc=0.445
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 3 回、元の命題に異議あり 0 回（どれかの形に異議あり 3 回）、直近で元の命題に判例がない連続 3 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 48 | 48 | 1.00 [0.93, 1.00] | — | 0.74 | 1.35 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 34 | 34 | 1.00 [0.90, 1.00] | — | 0.64 | 1.57 | 0.000 | 0 | 支持 | 0 |
| 逆 | 98 | 48 | 0.49 [0.39, 0.59] | — | 0.36 | 1.35 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 84 | 34 | 0.40 [0.31, 0.51] | — | 0.26 | 1.57 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 50 件（裏の判例も同じ）

- 3 段 τ比 1.5・4-s1 uniform_in h=0.0478 9: h=0.048, gain_vs_end=+719.00, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.00, err=-0.000 / surprise=+719.00
  - 3 段 τ比 1.5・4-s1 uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s1 uniform_in h=0.0625 4: h=0.062, gain_vs_end=+536.93, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.00, err=-0.000 / surprise=+536.93
  - 3 段 τ比 1.5・4-s1 uniform_in h=0.0625 4 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 6・0.2-s3 uniform_in h=0.0478 9: h=0.048, gain_vs_end=+355.32, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+3.00, err=0.000 / surprise=+355.32
  - 3 段 τ比 6・0.2-s3 uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 6・0.2-s3 uniform_in h=0.0625 4: h=0.062, gain_vs_end=+271.38, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+3.00, err=0.001 / surprise=+271.38
  - 3 段 τ比 6・0.2-s3 uniform_in h=0.0625 4 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s1 uniform_in h=0.125 5: h=0.125, gain_vs_end=+256.29, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.00, err=-0.000 / surprise=+256.29
  - 3 段 τ比 1.5・4-s1 uniform_in h=0.125 5 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 6・0.2-s3 uniform_in h=0.125 5: h=0.125, gain_vs_end=+137.70, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+3.00, err=0.003 / surprise=+137.70
  - 3 段 τ比 6・0.2-s3 uniform_in h=0.125 5 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s3 uniform_in h=0.0478 9: h=0.048, gain_vs_end=+134.42, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+3.00, err=0.000 / surprise=+134.42
  - 3 段 τ比 4・1.5-s3 uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s1 uniform_in h=0.25 6: h=0.250, gain_vs_end=+118.72, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.00, err=-0.001 / surprise=+118.72
  - 3 段 τ比 1.5・4-s1 uniform_in h=0.25 6 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s3 uniform_in h=0.0625 4: h=0.062, gain_vs_end=+102.20, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+3.00, err=0.000 / surprise=+102.20
  - 3 段 τ比 4・1.5-s3 uniform_in h=0.0625 4 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1 uniform_in h=0.0478 9: h=0.048, gain_vs_end=+97.82, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.00, err=0.000 / surprise=+97.82
  - 3 段 τ比 4・1.5-s1 uniform_in h=0.0478 9 は「gain_vs_end >= 10」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 40 件（propositions.jsonl を参照）

## O50: 槽が 2 段つながるとき、刻みが時定数の 1/32 以下なら、エンジンの uniform の 2 段目のずれは k1·k2·dt²/12 と 5 % 以内で合う

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `h <= 0.03125` ならば: `uni_fit2 <= 0.05`
- 識別子: `[where:edge2==true] h<=0.03125 => uni_fit2<=0.05`（指紋 `ade77e5c12582fc8`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'edge2', 'op': '==', 'value': True}]} / 単位数: 44
- 見直す条件（反証）: 外れる単位があれば、uniform の 1 ステップを連続の式に読み替えた展開（dt の 2 次まで）を見直す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.364, f1=0.533, accuracy=0.364, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 2 回、元の命題に異議あり 0 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 2 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 16 | 16 | 1.00 [0.81, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.64 | - | 1.000 | 0 | 判断保留 | 4 |
| 逆 | 44 | 16 | 0.36 [0.24, 0.51] | — | 0.36 | 1.00 | 1.000 | 0 | 棄却 | 3 |
| 裏 | 28 | 0 | 0.00 [0.00, 0.12] | — | 0.00 | - | 1.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 28 件（裏の判例も同じ）

- 2 段 τ比 0.2 uniform_in h=0.74 10: h=0.740, uni_fit2=0.042, tau2_ratio=0.200, err=0.219 / surprise=0.042
  - 2 段 τ比 0.2 uniform_in h=0.74 10 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 0.6 uniform_in h=0.74 10: h=0.740, uni_fit2=0.027, tau2_ratio=0.600, err=0.078 / surprise=0.027
  - 2 段 τ比 0.6 uniform_in h=0.74 10 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 0.2 uniform_in h=0.5 7: h=0.500, uni_fit2=0.022, tau2_ratio=0.200, err=0.102 / surprise=0.022
  - 2 段 τ比 0.2 uniform_in h=0.5 7 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 1.25 uniform_in h=0.74 10: h=0.740, uni_fit2=0.014, tau2_ratio=+1.25, err=0.037 / surprise=0.014
  - 2 段 τ比 1.25 uniform_in h=0.74 10 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 0.6 uniform_in h=0.5 7: h=0.500, uni_fit2=0.012, tau2_ratio=0.600, err=0.035 / surprise=0.012
  - 2 段 τ比 0.6 uniform_in h=0.5 7 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 0.2 uniform_in h=0.343 8: h=0.343, uni_fit2=0.011, tau2_ratio=0.200, err=0.048 / surprise=0.011
  - 2 段 τ比 0.2 uniform_in h=0.343 8 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 1.25 uniform_in h=0.5 7: h=0.500, uni_fit2=0.007, tau2_ratio=+1.25, err=0.017 / surprise=0.007
  - 2 段 τ比 1.25 uniform_in h=0.5 7 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 0.2 uniform_in h=0.25 6: h=0.250, uni_fit2=0.006, tau2_ratio=0.200, err=0.026 / surprise=0.006
  - 2 段 τ比 0.2 uniform_in h=0.25 6 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 0.6 uniform_in h=0.343 8: h=0.343, uni_fit2=0.006, tau2_ratio=0.600, err=0.016 / surprise=0.006
  - 2 段 τ比 0.6 uniform_in h=0.343 8 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 2 段 τ比 1.25 uniform_in h=0.343 8: h=0.343, uni_fit2=0.003, tau2_ratio=+1.25, err=0.008 / surprise=0.003
  - 2 段 τ比 1.25 uniform_in h=0.343 8 は「uni_fit2 <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 18 件（propositions.jsonl を参照）

## O51: 槽が 3 段つながるとき、刻みが時定数の 1/32 以下なら、エンジンの uniform の 3 段目のずれは G_eff(uniform) の式と合う（差は目安 (dt·k_max)²/12 の 5 % 以内）

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 126 件: edge3-r0.4-r2.5-s1.33277-uniform_in-5, edge3-r0.4-r2.5-s1.38717-uniform_in-5, edge3-r0.4-r2.5-s1.42797-uniform_in-5, edge3-r1.5-r4-s1.92306-uniform_in-8, edge3-r1.5-r4-s2.16344-uniform_in-8 ほか
- もし: `h <= 0.03125` ならば: `uni_fit <= 0.05`
- 識別子: `[where:edge3==true, where:uniform_in==true] h<=0.03125 => uni_fit<=0.05`（指紋 `ce64274468430251`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'edge3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}]} / 単位数: 330
- 見直す条件（反証）: 外れる単位があれば、H の 2 つ先の槽への項を見直す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.488, f1=0.656, accuracy=0.618, balanced_accuracy=0.744, mcc=0.442
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 2 回、元の命題に異議あり 0 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 2 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 120 | 120 | 1.00 [0.97, 1.00] | — | 0.75 | 1.34 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 84 | 84 | 1.00 [0.96, 1.00] | — | 0.64 | 1.57 | 0.000 | 0 | 支持 | 0 |
| 逆 | 246 | 120 | 0.49 [0.43, 0.55] | — | 0.36 | 1.34 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 210 | 84 | 0.40 [0.34, 0.47] | — | 0.25 | 1.57 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 126 件（裏の判例も同じ）

- 3 段 τ比 0.4・2.5-s1.33277 uniform_in h=0.125 5: h=0.125, uni_fit=0.050, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.33, err=0.003 / surprise=0.050
  - 3 段 τ比 0.4・2.5-s1.33277 uniform_in h=0.125 5 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.38717 uniform_in h=0.125 5: h=0.125, uni_fit=0.050, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.39, err=0.003 / surprise=0.050
  - 3 段 τ比 0.4・2.5-s1.38717 uniform_in h=0.125 5 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.42797 uniform_in h=0.125 5: h=0.125, uni_fit=0.050, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.43, err=0.003 / surprise=0.050
  - 3 段 τ比 0.4・2.5-s1.42797 uniform_in h=0.125 5 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s1.92306 uniform_in h=0.343 8: h=0.343, uni_fit=0.049, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.92, err=0.003 / surprise=0.049
  - 3 段 τ比 1.5・4-s1.92306 uniform_in h=0.343 8 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.16344 uniform_in h=0.343 8: h=0.343, uni_fit=0.049, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.16, err=0.003 / surprise=0.049
  - 3 段 τ比 1.5・4-s2.16344 uniform_in h=0.343 8 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.49596 uniform_in h=0.125 5: h=0.125, uni_fit=0.048, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.50, err=0.003 / surprise=0.048
  - 3 段 τ比 0.4・2.5-s1.49596 uniform_in h=0.125 5 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.63196 uniform_in h=0.125 5: h=0.125, uni_fit=0.047, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.63, err=0.003 / surprise=0.047
  - 3 段 τ比 0.4・2.5-s1.63196 uniform_in h=0.125 5 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.25・0.75-s2 uniform_in h=0.0478 9: h=0.048, uni_fit=0.044, tau2_ratio=0.250, tau3_ratio=0.750, span_ratio=+2.00, err=0.003 / surprise=0.044
  - 3 段 τ比 0.25・0.75-s2 uniform_in h=0.0478 9 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.28364 uniform_in h=0.343 8: h=0.343, uni_fit=0.043, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.28, err=0.003 / surprise=0.043
  - 3 段 τ比 1.5・4-s2.28364 uniform_in h=0.343 8 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.35575 uniform_in h=0.343 8: h=0.343, uni_fit=0.043, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.36, err=0.003 / surprise=0.043
  - 3 段 τ比 1.5・4-s2.35575 uniform_in h=0.343 8 は「uni_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 116 件（propositions.jsonl を参照）

## O52: 槽が 3 段つながるとき、刻みが式から出した境目の半分以下なら、uniform のずれは end より小さい

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 8 件: edge3-r6-r0.2-s1-uniform_in-10, edge3-r4-r1.5-s1.60859-uniform_in-5, edge3-r4-r1.5-s1.6559-uniform_in-5, edge3-r4-r1.5-s1.54551-uniform_in-8, edge3-r4-r1.5-s1.60859-uniform_in-8 ほか
- もし: `h_ratio <= 0.5` ならば: `gain_vs_end > 1.0`
- 識別子: `[where:edge3==true, where:uniform_in==true] h_ratio<=0.5 => gain_vs_end>1.0`（指紋 `36ae80870c3fc127`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'edge3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}]} / 単位数: 330
- 見直す条件（反証）: 境目の半分以下で uniform のほうが大きい単位があれば、境目の式（1 次と 2 次の項だけで比べる）は粗い刻みで足りないと書く
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.968, recall=0.809, f1=0.882, accuracy=0.803, balanced_accuracy=0.776, mcc=0.375
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 250 | 242 | 0.97 [0.94, 0.98] | — | 0.91 | 1.07 | 0.000 | 0 | 棄却 | 3 |
| 対偶 | 31 | 23 | 0.74 [0.57, 0.86] | — | 0.24 | 3.06 | 0.000 | 0 | 棄却 | 3 |
| 逆 | 299 | 242 | 0.81 [0.76, 0.85] | — | 0.76 | 1.07 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 80 | 23 | 0.29 [0.20, 0.39] | — | 0.09 | 3.06 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 8 件（対偶の判例も同じ）

- 3 段 τ比 6・0.2-s1 uniform_in h=0.74 10: h_ratio=0.469, gain_vs_end=0.718, h=0.740, h_star=+1.58, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+1.00, err=+1.39 / surprise=0.718
  - 3 段 τ比 6・0.2-s1 uniform_in h=0.74 10 は「h_ratio <= 0.5」を満たすのに「gain_vs_end > 1.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.60859 uniform_in h=0.125 5: h_ratio=0.408, gain_vs_end=0.571, h=0.125, h_star=0.307, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.61, err=0.001 / surprise=0.571
  - 3 段 τ比 4・1.5-s1.60859 uniform_in h=0.125 5 は「h_ratio <= 0.5」を満たすのに「gain_vs_end > 1.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.6559 uniform_in h=0.125 5: h_ratio=0.408, gain_vs_end=0.571, h=0.125, h_star=0.307, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.66, err=0.001 / surprise=0.571
  - 3 段 τ比 4・1.5-s1.6559 uniform_in h=0.125 5 は「h_ratio <= 0.5」を満たすのに「gain_vs_end > 1.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.54551 uniform_in h=0.343 8: h_ratio=0.399, gain_vs_end=0.548, h=0.343, h_star=0.859, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.55, err=0.007 / surprise=0.548
  - 3 段 τ比 4・1.5-s1.54551 uniform_in h=0.343 8 は「h_ratio <= 0.5」を満たすのに「gain_vs_end > 1.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.60859 uniform_in h=0.343 8: h_ratio=0.399, gain_vs_end=0.548, h=0.343, h_star=0.859, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.61, err=0.007 / surprise=0.548
  - 3 段 τ比 4・1.5-s1.60859 uniform_in h=0.343 8 は「h_ratio <= 0.5」を満たすのに「gain_vs_end > 1.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.6559 uniform_in h=0.343 8: h_ratio=0.399, gain_vs_end=0.548, h=0.343, h_star=0.859, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.66, err=0.007 / surprise=0.548
  - 3 段 τ比 4・1.5-s1.6559 uniform_in h=0.343 8 は「h_ratio <= 0.5」を満たすのに「gain_vs_end > 1.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.73476 uniform_in h=0.343 8: h_ratio=0.399, gain_vs_end=0.548, h=0.343, h_star=0.859, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.73, err=0.007 / surprise=0.548
  - 3 段 τ比 4・1.5-s1.73476 uniform_in h=0.343 8 は「h_ratio <= 0.5」を満たすのに「gain_vs_end > 1.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.60859 uniform_in h=0.03125 3: h_ratio=0.290, gain_vs_end=0.453, h=0.031, h_star=0.108, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.61, err=0.000 / surprise=0.453
  - 3 段 τ比 4・1.5-s1.60859 uniform_in h=0.03125 3 は「h_ratio <= 0.5」を満たすのに「gain_vs_end > 1.0」を満たさない。なぜか？

**異議あり（不成立）** 逆に判例 57 件（裏の判例も同じ）

- 3 段 τ比 1.5・4-s1.92306 uniform_in h=0.74 10: h_ratio=0.655, gain_vs_end=+6.53, h=0.740, h_star=+1.13, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+1.92, err=0.011 / surprise=+6.53
  - 3 段 τ比 1.5・4-s1.92306 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.16344 uniform_in h=0.74 10: h_ratio=0.655, gain_vs_end=+6.53, h=0.740, h_star=+1.13, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.16, err=0.011 / surprise=+6.53
  - 3 段 τ比 1.5・4-s2.16344 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.28364 uniform_in h=0.74 10: h_ratio=0.655, gain_vs_end=+6.53, h=0.740, h_star=+1.13, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.28, err=0.011 / surprise=+6.53
  - 3 段 τ比 1.5・4-s2.28364 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.35575 uniform_in h=0.74 10: h_ratio=0.655, gain_vs_end=+6.53, h=0.740, h_star=+1.13, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.36, err=0.011 / surprise=+6.53
  - 3 段 τ比 1.5・4-s2.35575 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.4519 uniform_in h=0.74 10: h_ratio=0.655, gain_vs_end=+6.53, h=0.740, h_star=+1.13, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.45, err=0.011 / surprise=+6.53
  - 3 段 τ比 1.5・4-s2.4519 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.52402 uniform_in h=0.74 10: h_ratio=0.655, gain_vs_end=+6.53, h=0.740, h_star=+1.13, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.52, err=0.011 / surprise=+6.53
  - 3 段 τ比 1.5・4-s2.52402 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.26164 uniform_in h=0.74 10: h_ratio=+1.14, gain_vs_end=+5.21, h=0.740, h_star=0.648, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.26, err=0.037 / surprise=+5.21
  - 3 段 τ比 4・1.5-s1.26164 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.41935 uniform_in h=0.74 10: h_ratio=+1.14, gain_vs_end=+5.21, h=0.740, h_star=0.648, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.42, err=0.037 / surprise=+5.21
  - 3 段 τ比 4・1.5-s1.41935 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.4982 uniform_in h=0.74 10: h_ratio=+1.14, gain_vs_end=+5.21, h=0.740, h_star=0.648, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.50, err=0.037 / surprise=+5.21
  - 3 段 τ比 4・1.5-s1.4982 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.54551 uniform_in h=0.74 10: h_ratio=+1.14, gain_vs_end=+5.21, h=0.740, h_star=0.648, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.55, err=0.037 / surprise=+5.21
  - 3 段 τ比 4・1.5-s1.54551 uniform_in h=0.74 10 は「gain_vs_end > 1.0」を満たすのに「h_ratio <= 0.5」を満たさない。なぜか？
- ほか 47 件（propositions.jsonl を参照）

## O53: 槽が 3 段つながるとき、刻みが式から出した境目の 2 倍以上なら、uniform のずれは end より大きい

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 18 件: edge3-r0.25-r0.75-s1-uniform_in-10, edge3-r1.5-r4-s2.28364-uniform_in-8, edge3-r1.5-r4-s2.35575-uniform_in-8, edge3-r1.5-r4-s2.4519-uniform_in-8, edge3-r1.5-r4-s2.52402-uniform_in-8 ほか
- もし: `h_ratio >= 2.0` ならば: `gain_vs_end < 1.0`
- 識別子: `[where:edge3==true, where:uniform_in==true] h_ratio>=2.0 => gain_vs_end<1.0`（指紋 `56cdc704683eb104`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'edge3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}]} / 単位数: 330
- 見直す条件（反証）: 境目の 2 倍以上で uniform のほうが小さい単位があれば、境目の式は上側では当たらないと書く
- 注記: 逆（uniform のほうが大きいなら、刻みは境目の 2 倍以上）の判例は、境目の近く（1/2〜2 倍）で大きくなった単位を示す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.357, recall=0.323, f1=0.339, accuracy=0.882, balanced_accuracy=0.631, mcc=0.275
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 2 回、元の命題に異議あり 2 回（どれかの形に異議あり 2 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 28 | 10 | 0.36 [0.21, 0.54] | — | 0.09 | 3.80 | 0.000 | 0 | 棄却 | 3 |
| 対偶 | 299 | 281 | 0.94 [0.91, 0.96] | — | 0.92 | 1.03 | 0.000 | 0 | 棄却 | 3 |
| 逆 | 31 | 10 | 0.32 [0.19, 0.50] | — | 0.08 | 3.80 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 302 | 281 | 0.93 [0.90, 0.95] | — | 0.91 | 1.03 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 18 件（対偶の判例も同じ）

- 3 段 τ比 0.25・0.75-s1 uniform_in h=0.74 10: h_ratio=+4.70, gain_vs_end=+2.60, h=0.740, h_star=0.157, tau2_ratio=0.250, tau3_ratio=0.750, span_ratio=+1.00, err=0.385 / surprise=+2.60
  - 3 段 τ比 0.25・0.75-s1 uniform_in h=0.74 10 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.28364 uniform_in h=0.343 8: h_ratio=+23.44, gain_vs_end=+2.20, h=0.343, h_star=0.015, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.28, err=0.003 / surprise=+2.20
  - 3 段 τ比 1.5・4-s2.28364 uniform_in h=0.343 8 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.35575 uniform_in h=0.343 8: h_ratio=+23.44, gain_vs_end=+2.20, h=0.343, h_star=0.015, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.36, err=0.003 / surprise=+2.20
  - 3 段 τ比 1.5・4-s2.35575 uniform_in h=0.343 8 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.4519 uniform_in h=0.343 8: h_ratio=+23.44, gain_vs_end=+2.20, h=0.343, h_star=0.015, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.45, err=0.003 / surprise=+2.20
  - 3 段 τ比 1.5・4-s2.4519 uniform_in h=0.343 8 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.52402 uniform_in h=0.343 8: h_ratio=+23.44, gain_vs_end=+2.20, h=0.343, h_star=0.015, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.52, err=0.003 / surprise=+2.20
  - 3 段 τ比 1.5・4-s2.52402 uniform_in h=0.343 8 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.22397 uniform_in h=0.74 10: h_ratio=+3.53, gain_vs_end=+1.22, h=0.740, h_star=0.210, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.22, err=0.075 / surprise=+1.22
  - 3 段 τ比 0.4・2.5-s1.22397 uniform_in h=0.74 10 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.29197 uniform_in h=0.74 10: h_ratio=+3.53, gain_vs_end=+1.22, h=0.740, h_star=0.210, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.29, err=0.075 / surprise=+1.22
  - 3 段 τ比 0.4・2.5-s1.29197 uniform_in h=0.74 10 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.33277 uniform_in h=0.74 10: h_ratio=+3.53, gain_vs_end=+1.22, h=0.740, h_star=0.210, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.33, err=0.075 / surprise=+1.22
  - 3 段 τ比 0.4・2.5-s1.33277 uniform_in h=0.74 10 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.38717 uniform_in h=0.74 10: h_ratio=+3.53, gain_vs_end=+1.22, h=0.740, h_star=0.210, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.39, err=0.075 / surprise=+1.22
  - 3 段 τ比 0.4・2.5-s1.38717 uniform_in h=0.74 10 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- 3 段 τ比 0.4・2.5-s1.42797 uniform_in h=0.74 10: h_ratio=+3.53, gain_vs_end=+1.22, h=0.740, h_star=0.210, tau2_ratio=0.400, tau3_ratio=+2.50, span_ratio=+1.43, err=0.075 / surprise=+1.22
  - 3 段 τ比 0.4・2.5-s1.42797 uniform_in h=0.74 10 は「h_ratio >= 2.0」を満たすのに「gain_vs_end < 1.0」を満たさない。なぜか？
- ほか 8 件（propositions.jsonl を参照）

**異議あり（不成立）** 逆に判例 21 件（裏の判例も同じ）

- 3 段 τ比 1.5・4-s2.28364 uniform_in h=0.5 7: h_ratio=+1.09, gain_vs_end=0.963, h=0.500, h_star=0.458, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.28, err=0.007 / surprise=0.963
  - 3 段 τ比 1.5・4-s2.28364 uniform_in h=0.5 7 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.35575 uniform_in h=0.5 7: h_ratio=+1.09, gain_vs_end=0.963, h=0.500, h_star=0.458, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.36, err=0.007 / surprise=0.963
  - 3 段 τ比 1.5・4-s2.35575 uniform_in h=0.5 7 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.4519 uniform_in h=0.5 7: h_ratio=+1.09, gain_vs_end=0.963, h=0.500, h_star=0.458, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.45, err=0.007 / surprise=0.963
  - 3 段 τ比 1.5・4-s2.4519 uniform_in h=0.5 7 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.52402 uniform_in h=0.5 7: h_ratio=+1.09, gain_vs_end=0.963, h=0.500, h_star=0.458, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.52, err=0.007 / surprise=0.963
  - 3 段 τ比 1.5・4-s2.52402 uniform_in h=0.5 7 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 1.5・4-s2.64421 uniform_in h=0.5 7: h_ratio=+1.09, gain_vs_end=0.963, h=0.500, h_star=0.458, tau2_ratio=+1.50, tau3_ratio=+4.00, span_ratio=+2.64, err=0.007 / surprise=0.963
  - 3 段 τ比 1.5・4-s2.64421 uniform_in h=0.5 7 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 0.25・0.75-s1 uniform_in h=0.5 7: h_ratio=+1.26, gain_vs_end=0.726, h=0.500, h_star=0.396, tau2_ratio=0.250, tau3_ratio=0.750, span_ratio=+1.00, err=0.214 / surprise=0.726
  - 3 段 τ比 0.25・0.75-s1 uniform_in h=0.5 7 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 6・0.2-s1 uniform_in h=0.74 10: h_ratio=0.469, gain_vs_end=0.718, h=0.740, h_star=+1.58, tau2_ratio=+6.00, tau3_ratio=0.200, span_ratio=+1.00, err=+1.39 / surprise=0.718
  - 3 段 τ比 6・0.2-s1 uniform_in h=0.74 10 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.60859 uniform_in h=0.125 5: h_ratio=0.408, gain_vs_end=0.571, h=0.125, h_star=0.307, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.61, err=0.001 / surprise=0.571
  - 3 段 τ比 4・1.5-s1.60859 uniform_in h=0.125 5 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.6559 uniform_in h=0.125 5: h_ratio=0.408, gain_vs_end=0.571, h=0.125, h_star=0.307, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.66, err=0.001 / surprise=0.571
  - 3 段 τ比 4・1.5-s1.6559 uniform_in h=0.125 5 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- 3 段 τ比 4・1.5-s1.54551 uniform_in h=0.343 8: h_ratio=0.399, gain_vs_end=0.548, h=0.343, h_star=0.859, tau2_ratio=+4.00, tau3_ratio=+1.50, span_ratio=+1.55, err=0.007 / surprise=0.548
  - 3 段 τ比 4・1.5-s1.54551 uniform_in h=0.343 8 は「gain_vs_end < 1.0」を満たすのに「h_ratio >= 2.0」を満たさない。なぜか？
- ほか 11 件（propositions.jsonl を参照）

## O54: 槽が 3 段つながるとき、刻みが時定数の 1/32 以下なら、end の 3 段目のずれは 2 次までの式 G + dt·H1 + dt²·H2 と合う（差は目安 (dt·k_max)²/12 の 5 % 以内）

- **判定: exit 3 異議あり（不成立）** — 元の命題: 判例 6 件: cross3-r3-r1.25-n31-end-1, cross3-r3-r1.25-n42-end-1, cross3-r3-r1.25-n43-end-1, cross3-r3-r1.25-n44-end-1, cross3-r3-r1.25-n45-end-1 ほか
- もし: `h <= 0.03125` ならば: `end2_fit <= 0.05`
- 識別子: `[where:cross3==true, where:uniform_in==false] h<=0.03125 => end2_fit<=0.05`（指紋 `f3765fd6c2bb8754`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'cross3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': False}]} / 単位数: 245
- 見直す条件（反証）: 外れる単位があれば、H2 の展開を見直す
- 注記: 0 を横切る近くの単位で確かめるので、1 次の項だけの式（O45）より厳しい
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=0.957, recall=0.779, f1=0.859, accuracy=0.820, balanced_accuracy=0.848, mcc=0.644
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 140 | 134 | 0.96 [0.91, 0.98] | — | 0.70 | 1.36 | 0.000 | 0 | 棄却 | 3 |
| 対偶 | 73 | 67 | 0.92 [0.83, 0.96] | — | 0.43 | 2.14 | 0.000 | 0 | 棄却 | 3 |
| 逆 | 172 | 134 | 0.78 [0.71, 0.83] | — | 0.57 | 1.36 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 105 | 67 | 0.64 [0.54, 0.72] | — | 0.30 | 2.14 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 元の命題に判例 6 件（対偶の判例も同じ）

- 3 段 τ比 3・1.25-n31 end h=0.03125 1: h=0.031, end2_fit=0.096, tau2_ratio=+3.00, tau3_ratio=+1.25, span_ratio=0.969, err=-0.009 / surprise=0.096
  - 3 段 τ比 3・1.25-n31 end h=0.03125 1 は「h <= 0.03125」を満たすのに「end2_fit <= 0.05」を満たさない。なぜか？
- 3 段 τ比 3・1.25-n42 end h=0.03125 1: h=0.031, end2_fit=0.064, tau2_ratio=+3.00, tau3_ratio=+1.25, span_ratio=+1.31, err=-0.001 / surprise=0.064
  - 3 段 τ比 3・1.25-n42 end h=0.03125 1 は「h <= 0.03125」を満たすのに「end2_fit <= 0.05」を満たさない。なぜか？
- 3 段 τ比 3・1.25-n43 end h=0.03125 1: h=0.031, end2_fit=0.062, tau2_ratio=+3.00, tau3_ratio=+1.25, span_ratio=+1.34, err=-0.000 / surprise=0.062
  - 3 段 τ比 3・1.25-n43 end h=0.03125 1 は「h <= 0.03125」を満たすのに「end2_fit <= 0.05」を満たさない。なぜか？
- 3 段 τ比 3・1.25-n44 end h=0.03125 1: h=0.031, end2_fit=0.060, tau2_ratio=+3.00, tau3_ratio=+1.25, span_ratio=+1.38, err=0.000 / surprise=0.060
  - 3 段 τ比 3・1.25-n44 end h=0.03125 1 は「h <= 0.03125」を満たすのに「end2_fit <= 0.05」を満たさない。なぜか？
- 3 段 τ比 3・1.25-n45 end h=0.03125 1: h=0.031, end2_fit=0.058, tau2_ratio=+3.00, tau3_ratio=+1.25, span_ratio=+1.41, err=0.001 / surprise=0.058
  - 3 段 τ比 3・1.25-n45 end h=0.03125 1 は「h <= 0.03125」を満たすのに「end2_fit <= 0.05」を満たさない。なぜか？
- 3 段 τ比 3・1.25-n46 end h=0.03125 1: h=0.031, end2_fit=0.056, tau2_ratio=+3.00, tau3_ratio=+1.25, span_ratio=+1.44, err=0.001 / surprise=0.056
  - 3 段 τ比 3・1.25-n46 end h=0.03125 1 は「h <= 0.03125」を満たすのに「end2_fit <= 0.05」を満たさない。なぜか？

**異議あり（不成立）** 逆に判例 38 件（裏の判例も同じ）

- 3 段 τ比 5・2-n29 end h=0.0478 1: h=0.048, end2_fit=0.049, tau2_ratio=+5.00, tau3_ratio=+2.00, span_ratio=+1.39, err=-0.010 / surprise=0.049
  - 3 段 τ比 5・2-n29 end h=0.0478 1 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.3・2-n23 end h=0.0625 2: h=0.062, end2_fit=0.049, tau2_ratio=0.300, tau3_ratio=+2.00, span_ratio=+1.44, err=0.009 / surprise=0.049
  - 3 段 τ比 0.3・2-n23 end h=0.0625 2 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.6・2.5-n31 end h=0.0478 1: h=0.048, end2_fit=0.049, tau2_ratio=0.600, tau3_ratio=+2.50, span_ratio=+1.48, err=-0.001 / surprise=0.049
  - 3 段 τ比 0.6・2.5-n31 end h=0.0478 1 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.5・3-n23 end h=0.0625 2: h=0.062, end2_fit=0.048, tau2_ratio=0.500, tau3_ratio=+3.00, span_ratio=+1.44, err=-0.004 / surprise=0.048
  - 3 段 τ比 0.5・3-n23 end h=0.0625 2 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.6・2.5-n32 end h=0.0478 1: h=0.048, end2_fit=0.047, tau2_ratio=0.600, tau3_ratio=+2.50, span_ratio=+1.53, err=0.000 / surprise=0.047
  - 3 段 τ比 0.6・2.5-n32 end h=0.0478 1 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.5・3-n23 end h=0.0478 1: h=0.048, end2_fit=0.047, tau2_ratio=0.500, tau3_ratio=+3.00, span_ratio=+1.10, err=-0.013 / surprise=0.047
  - 3 段 τ比 0.5・3-n23 end h=0.0478 1 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.5・3-n24 end h=0.0625 1: h=0.062, end2_fit=0.047, tau2_ratio=0.500, tau3_ratio=+3.00, span_ratio=+1.50, err=-0.002 / surprise=0.047
  - 3 段 τ比 0.5・3-n24 end h=0.0625 1 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.6・2.5-n33 end h=0.0478 1: h=0.048, end2_fit=0.046, tau2_ratio=0.600, tau3_ratio=+2.50, span_ratio=+1.58, err=0.001 / surprise=0.046
  - 3 段 τ比 0.6・2.5-n33 end h=0.0478 1 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.5・3-n25 end h=0.0625 1: h=0.062, end2_fit=0.045, tau2_ratio=0.500, tau3_ratio=+3.00, span_ratio=+1.56, err=-0.001 / surprise=0.045
  - 3 段 τ比 0.5・3-n25 end h=0.0625 1 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- 3 段 τ比 0.6・2.5-n34 end h=0.0478 2: h=0.048, end2_fit=0.045, tau2_ratio=0.600, tau3_ratio=+2.50, span_ratio=+1.63, err=0.002 / surprise=0.045
  - 3 段 τ比 0.6・2.5-n34 end h=0.0478 2 は「end2_fit <= 0.05」を満たすのに「h <= 0.03125」を満たさない。なぜか？
- ほか 28 件（propositions.jsonl を参照）

## O55: 槽が 3 段つながるとき、式が「uniform のずれは end の 1.25 倍以上」と言う単位では、uniform のずれは実際に end より大きい

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 4 件: cross3-r0.3-r2-n10-uniform_in-1, cross3-r0.3-r2-n145-uniform_in-1, cross3-r0.6-r2.5-n49-uniform_in-1, cross3-r0.3-r2-n19-uniform_in-1
- もし: `pred_margin >= 1.25` ならば: `gain_vs_end < 1.0`
- 識別子: `[where:cross3==true, where:uniform_in==true] pred_margin>=1.25 => gain_vs_end<1.0`（指紋 `b121395fc4eadbf6`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'cross3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}]} / 単位数: 245
- 親: O53（変更: 境目を係数の比 \|a1/b2\| から、その刻みと時刻での 2 つの式の予想の比に替えた（end の 2 次の項を入れた）。単位は別の組で、粗い刻みは使わない）
- 見直す条件（反証）: uniform のほうが小さい単位があれば、2 次までの式でも境目は出ないと書く
- 注記: 逆（uniform のほうが大きいなら、式の比は 1.25 以上）の判例は、式が言い切れなかった単位（比が 0.8〜1.25）を示す
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.826, f1=0.905, accuracy=0.984, balanced_accuracy=0.913, mcc=0.901
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 1 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 19 | 19 | 1.00 [0.83, 1.00] | — | 0.09 | 10.65 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 222 | 222 | 1.00 [0.98, 1.00] | — | 0.92 | 1.08 | 0.000 | 0 | 支持 | 0 |
| 逆 | 23 | 19 | 0.83 [0.63, 0.93] | — | 0.08 | 10.65 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 226 | 222 | 0.98 [0.96, 0.99] | — | 0.91 | 1.08 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 4 件（裏の判例も同じ）

- 3 段 τ比 0.3・2-n10 uniform_in h=0.125 1: pred_margin=0.924, gain_vs_end=0.969, h=0.125, tau2_ratio=0.300, tau3_ratio=+2.00, span_ratio=+1.25, err=0.006 / surprise=0.969
  - 3 段 τ比 0.3・2-n10 uniform_in h=0.125 1 は「gain_vs_end < 1.0」を満たすのに「pred_margin >= 1.25」を満たさない。なぜか？
- 3 段 τ比 0.3・2-n145 uniform_in h=0.0078125 1: pred_margin=+1.15, gain_vs_end=0.892, h=0.008, tau2_ratio=0.300, tau3_ratio=+2.00, span_ratio=+1.13, err=0.000 / surprise=0.892
  - 3 段 τ比 0.3・2-n145 uniform_in h=0.0078125 1 は「gain_vs_end < 1.0」を満たすのに「pred_margin >= 1.25」を満たさない。なぜか？
- 3 段 τ比 0.6・2.5-n49 uniform_in h=0.03125 1: pred_margin=+1.14, gain_vs_end=0.847, h=0.031, tau2_ratio=0.600, tau3_ratio=+2.50, span_ratio=+1.53, err=0.000 / surprise=0.847
  - 3 段 τ比 0.6・2.5-n49 uniform_in h=0.03125 1 は「gain_vs_end < 1.0」を満たすのに「pred_margin >= 1.25」を満たさない。なぜか？
- 3 段 τ比 0.3・2-n19 uniform_in h=0.0625 1: pred_margin=+1.15, gain_vs_end=0.807, h=0.062, tau2_ratio=0.300, tau3_ratio=+2.00, span_ratio=+1.19, err=0.002 / surprise=0.807
  - 3 段 τ比 0.3・2-n19 uniform_in h=0.0625 1 は「gain_vs_end < 1.0」を満たすのに「pred_margin >= 1.25」を満たさない。なぜか？

## O56: 槽が 3 段つながるとき、式が「uniform のずれは end の 0.8 倍以下」と言う単位では、uniform のずれは実際に end より小さい

- **判定: exit 3 異議あり（不成立）**（仮: 元の命題と対偶まで） — 逆: 判例 8 件: cross3-r0.6-r2.5-n24-uniform_in-1, cross3-r3-r1.25-n11-uniform_in-1, cross3-r0.5-r3-n50-uniform_in-1, cross3-r0.6-r2.5-n12-uniform_in-1, cross3-r0.3-r2-n290-uniform_in-1 ほか
- もし: `pred_margin <= 0.8` ならば: `gain_vs_end > 1.0`
- 識別子: `[where:cross3==true, where:uniform_in==true] pred_margin<=0.8 => gain_vs_end>1.0`（指紋 `5ea6bd8678f7d14d`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: {'where': [{'col': 'cross3', 'op': '==', 'value': True}, {'col': 'uniform_in', 'op': '==', 'value': True}]} / 単位数: 245
- 親: O52（変更: O55 と同じ替え方）
- 見直す条件（反証）: uniform のほうが大きい単位があれば、2 次までの式でも境目は出ないと書く
- 条件の数: 2（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=0.964, f1=0.982, accuracy=0.967, balanced_accuracy=0.982, mcc=0.846
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 1 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 214 | 214 | 1.00 [0.98, 1.00] | — | 0.91 | 1.10 | 0.000 | 0 | 支持 | 0 |
| 対偶 | 23 | 23 | 1.00 [0.86, 1.00] | — | 0.13 | 7.90 | 0.000 | 0 | 支持 | 0 |
| 逆 | 222 | 214 | 0.96 [0.93, 0.98] | — | 0.87 | 1.10 | 0.000 | 0 | 棄却 | 3 |
| 裏 | 31 | 23 | 0.74 [0.57, 0.86] | — | 0.09 | 7.90 | 0.000 | 0 | 棄却 | 3 |

**異議あり（不成立）** 逆に判例 8 件（裏の判例も同じ）

- 3 段 τ比 0.6・2.5-n24 uniform_in h=0.0625 1: pred_margin=0.815, gain_vs_end=+1.37, h=0.062, tau2_ratio=0.600, tau3_ratio=+2.50, span_ratio=+1.50, err=0.001 / surprise=+1.37
  - 3 段 τ比 0.6・2.5-n24 uniform_in h=0.0625 1 は「gain_vs_end > 1.0」を満たすのに「pred_margin <= 0.8」を満たさない。なぜか？
- 3 段 τ比 3・1.25-n11 uniform_in h=0.125 1: pred_margin=0.886, gain_vs_end=+1.32, h=0.125, tau2_ratio=+3.00, tau3_ratio=+1.25, span_ratio=+1.38, err=0.002 / surprise=+1.32
  - 3 段 τ比 3・1.25-n11 uniform_in h=0.125 1 は「gain_vs_end > 1.0」を満たすのに「pred_margin <= 0.8」を満たさない。なぜか？
- 3 段 τ比 0.5・3-n50 uniform_in h=0.03125 1: pred_margin=0.817, gain_vs_end=+1.30, h=0.031, tau2_ratio=0.500, tau3_ratio=+3.00, span_ratio=+1.56, err=0.000 / surprise=+1.30
  - 3 段 τ比 0.5・3-n50 uniform_in h=0.03125 1 は「gain_vs_end > 1.0」を満たすのに「pred_margin <= 0.8」を満たさない。なぜか？
- 3 段 τ比 0.6・2.5-n12 uniform_in h=0.125 1: pred_margin=+1.06, gain_vs_end=+1.23, h=0.125, tau2_ratio=0.600, tau3_ratio=+2.50, span_ratio=+1.50, err=0.002 / surprise=+1.23
  - 3 段 τ比 0.6・2.5-n12 uniform_in h=0.125 1 は「gain_vs_end > 1.0」を満たすのに「pred_margin <= 0.8」を満たさない。なぜか？
- 3 段 τ比 0.3・2-n290 uniform_in h=0.00390625 1: pred_margin=0.857, gain_vs_end=+1.18, h=0.004, tau2_ratio=0.300, tau3_ratio=+2.00, span_ratio=+1.13, err=0.000 / surprise=+1.18
  - 3 段 τ比 0.3・2-n290 uniform_in h=0.00390625 1 は「gain_vs_end > 1.0」を満たすのに「pred_margin <= 0.8」を満たさない。なぜか？
- 3 段 τ比 0.3・2-n36 uniform_in h=0.03125 1: pred_margin=0.971, gain_vs_end=+1.13, h=0.031, tau2_ratio=0.300, tau3_ratio=+2.00, span_ratio=+1.12, err=0.000 / surprise=+1.13
  - 3 段 τ比 0.3・2-n36 uniform_in h=0.03125 1 は「gain_vs_end > 1.0」を満たすのに「pred_margin <= 0.8」を満たさない。なぜか？
- 3 段 τ比 0.5・3-n25 uniform_in h=0.0625 1: pred_margin=+1.08, gain_vs_end=+1.07, h=0.062, tau2_ratio=0.500, tau3_ratio=+3.00, span_ratio=+1.56, err=0.001 / surprise=+1.07
  - 3 段 τ比 0.5・3-n25 uniform_in h=0.0625 1 は「gain_vs_end > 1.0」を満たすのに「pred_margin <= 0.8」を満たさない。なぜか？
- 3 段 τ比 0.5・3-n51 uniform_in h=0.03125 1: pred_margin=0.939, gain_vs_end=+1.04, h=0.031, tau2_ratio=0.500, tau3_ratio=+3.00, span_ratio=+1.59, err=0.000 / surprise=+1.04
  - 3 段 τ比 0.5・3-n51 uniform_in h=0.03125 1 は「gain_vs_end > 1.0」を満たすのに「pred_margin <= 0.8」を満たさない。なぜか？
