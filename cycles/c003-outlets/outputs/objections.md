# 異議あり — 命題の判定記録（自動生成）

判定基準は結果を見る前に命題ファイルに書いたもの（docs/propositions.md）。
命題ファイル SHA-256: `fe1b9dc9eaabdcb01b07c68361eb71f9b3b904a79d7f6e1ee53e7e63a6239240` / コード: `b126b0d`

判定は命題がその範囲で成り立つかどうかだけを示し、原因は示さない。

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 1 回（どれかの形に異議あり 1 回）、直近で元の命題に判例がない連続 0 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

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
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 12 | 12 | 1.00 [0.76, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |

## O15: どの単位でも、槽と管の中の合計は最初から 1 ulp も変わらない

- **判定: exit 4 待った！判断保留** — 対偶: n=0（min_n=10）、成立率の区間 0.00〜1.00
- もし: `（すべての単位）` ならば: `conservation_q == 0`
- 識別子: `[all] * => conservation_q==0`（指紋 `7c3f01901c7f68f4`）
- 強さ: 必ず（always, 基準 反例なし）/ 範囲: 全体 / 単位数: 338
- 見直す条件（反証）: 0 でない単位があれば、その方式は採らない
- 条件の数: 1（例外条件を増やしすぎていないかの目安）
- 共通評価軸（元の命題）: precision=1.000, recall=1.000, f1=1.000, accuracy=1.000, balanced_accuracy=None, mcc=None
- 合成seed評価: None (not_evaluated)
- 台帳: 評価 1 回、元の命題に異議あり 0 回（どれかの形に異議あり 0 回）、直近で元の命題に判例がない連続 1 回

| 形 | n | 成立 | 成立率 [95%区間] | 基準から（σ、片側 p） | 基準率 | lift | p | 判定不能 | 判定 | exit |
|---|---|---|---|---|---|---|---|---|---|---|
| 元の命題 | 338 | 338 | 1.00 [0.99, 1.00] | — | 1.00 | 1.00 | 1.000 | 0 | 支持 | 0 |
| 対偶 | 0 | 0 | - [0.00, 1.00] | — | 0.00 | - | 1.000 | 0 | 判断保留 | 4 |
