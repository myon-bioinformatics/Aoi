# 命題の一覧（自動生成）

命題ファイル SHA-256: `fe1b9dc9eaabdcb01b07c68361eb71f9b3b904a79d7f6e1ee53e7e63a6239240` / コード: `b126b0d`

各形のセルは「終了コード・成立率（単位数）」。0 異議なし、1 例外あり、2 主張が強すぎる、3 不成立、4 判断保留、5 判定できない単位。
σ は、元の命題の成立数が強さの基準（概ね 0.75・多くの場合 0.5 など）から標準偏差いくつ分上（＋）か下（−）か。終了コードの判定（95% の区間、両側でおよそ ±2σ）とは別に、±1σ・±2σ・±3σ で読むための値。
判例と根拠は objections.md、規則は docs/propositions.md。

総合の終了コードの内訳: exit 0 異議なし 2件、exit 3 異議あり（不成立） 5件、exit 4 待った！判断保留 8件

| id | 識別子 | 強さ | 元の命題 | σ | 対偶 | 逆 | 裏 | きっかけ以外 | 総合 | 親 |
|---|---|---|---|---|---|---|---|---|---|---|
| O1 | `[where:independent==true, where:valve_only==true] n==1 => err_abs<1e-09` | 必ず | 0・1.00（10） | — | 0・1.00（100） | 0・1.00（10） | 0・1.00（100） | — | **0** 異議なし |  |
| O2 | `[where:independent==true, where:valve_only==true] n>=2 => err<-1e-09` | 必ず | 0・1.00（100） | — | 0・1.00（10） | 0・1.00（100） | 0・1.00（10） | — | **0** 異議なし |  |
| O6 | `[where:equal_split==true, where:independent==true, where:n>=2, where:valve_only==true] * => drop_from_fewer<0` | 必ず | 0・1.00（50） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O3 | `[where:independent==true, where:n>=2, where:valve_only==true] * => fo_rel<=0.05` | 必ず | 3・0.66（100） | — | 3・0.00（34） | — | — | — | **3** 異議あり（不成立） |  |
| O4 | `[where:independent==true, where:n>=2, where:valve_only==true] h<=0.03125 => fo_rel<=0.05` | 必ず | 0・1.00（30） | — | 0・1.00（34） | 3・0.45（66） | 3・0.49（70） | — | **3** 異議あり（不成立） |  |
| O5 | `[where:independent==true, where:n>=2, where:valve_only==true] * => ceil_ratio<=1.0` | 必ず | 3・0.98（100） | — | 4・0.00（2） | — | — | — | **3** 異議あり（不成立） |  |
| O7 | `[where:has_half==true, where:independent==true, where:n>=2, where:valve_only==true] h<=0.03125 => halving_ratio<=2.1 & halving_ratio>=1.9` | 必ず | 0・1.00（20） | — | 4・1.00（6） | 3・0.37（54） | 3・0.15（40） | — | **4** 待った！判断保留 |  |
| O8 | `[where:independent==true, where:n>=2, where:valve_only==true] h<=0.03125 => corr_gain>=10` | 必ず | 0・1.00（30） | — | 0・1.00（40） | 3・0.50（60） | 3・0.57（70） | — | **3** 異議あり（不成立） |  |
| O9 | `[where:joint==true, where:valve_only==true] * => err_abs<1e-09` | 必ず | 0・1.00（110） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O10 | `[where:joint==true, where:mixed==true] * => err_abs<1e-09` | 必ず | 3・0.10（30） | — | 3・0.00（27） | — | — | — | **3** 異議あり（不成立） |  |
| O11 | `[where:affine==true, where:mixed==true] * => err_abs<1e-09` | 必ず | 0・1.00（30） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O12 | `[where:pump_only==true] * => err_abs<1e-09` | 必ず | 0・1.00（16） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O13 | `[where:has_delay==true] * => src_same==true` | 必ず | 0・1.00（12） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O14 | `[where:has_delay==true] * => lag_err_steps==0` | 必ず | 0・1.00（12） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O15 | `[all] * => conservation_q==0` | 必ず | 0・1.00（338） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |

## 全命題の共通評価軸

過小評価かどうか・元の支持判定にかかわらず同じ項目を表示する。分類指標は条件不成立を陰性予測とする診断で、逆命題を要求するものではない。
`None` は計算不能・未評価。欠けた値を0や不変に置き換えない。分母0などの理由はJSONのmetrics.none_reasons、seedの理由はseed_sensitivity.reasonを参照。
seed比較は命題定義・年・生成条件ごと。試したseed内の不変性であり、全seedの不変性・統計的有意性・因果は主張しない。

| 命題 | Precision | Recall | F1 | Accuracy | Balanced Accuracy | MCC | 合成seed評価 |
|---|---|---|---|---|---|---|---|
| **O1** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | None (not_evaluated) |
| **O2** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | None (not_evaluated) |
| **O6** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O3** | 0.660 | 1.000 | 0.795 | 0.660 | 0.500 | None | None (not_evaluated) |
| **O4** | 1.000 | 0.455 | 0.625 | 0.640 | 0.727 | 0.470 | None (not_evaluated) |
| **O5** | 0.980 | 1.000 | 0.990 | 0.980 | 0.500 | None | None (not_evaluated) |
| **O7** | 1.000 | 0.370 | 0.541 | 0.433 | 0.685 | 0.236 | None (not_evaluated) |
| **O8** | 1.000 | 0.500 | 0.667 | 0.700 | 0.750 | 0.535 | None (not_evaluated) |
| **O9** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O10** | 0.100 | 1.000 | 0.182 | 0.100 | 0.500 | None | None (not_evaluated) |
| **O11** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O12** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O13** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O14** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O15** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
