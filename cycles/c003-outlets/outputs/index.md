# 命題の一覧（自動生成）

命題ファイル SHA-256: `a183edbfc568a33b845685df87da053e276d0a4a101da871a377cb92bd61825e` / コード: `41ad024`

各形のセルは「終了コード・成立率（単位数）」。0 異議なし、1 例外あり、2 主張が強すぎる、3 不成立、4 判断保留、5 判定できない単位。
σ は、元の命題の成立数が強さの基準（概ね 0.75・多くの場合 0.5 など）から標準偏差いくつ分上（＋）か下（−）か。終了コードの判定（95% の区間、両側でおよそ ±2σ）とは別に、±1σ・±2σ・±3σ で読むための値。
判例と根拠は objections.md、規則は docs/propositions.md。

総合の終了コードの内訳: exit 0 異議なし 3件、exit 3 異議あり（不成立） 15件、exit 4 待った！判断保留 26件

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
| O15 | `[all] * => conservation_q==0` | 必ず | 0・1.00（1388） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O16 | `[where:independent==true, where:n>=2, where:valve_only==true] * => euler_ratio<=1.0` | 必ず | 0・1.00（100） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 | O5 |
| O17 | `[where:independent==true, where:n>=2, where:valve_only==true] h<=0.125 => so_rel<=0.005` | 必ず | 3・0.87（60） | — | 3・0.83（48） | 0・1.00（52） | 0・1.00（40） | — | **3** 異議あり（不成立） |  |
| O18 | `[where:independent==true, where:n>=2, where:valve_only==true] * => so_rel<=0.05` | 必ず | 3・0.80（100） | — | 3・0.00（20） | — | — | — | **3** 異議あり（不成立） | O3 |
| O19 | `[where:independent==true, where:valve_only==true] * => disc_gap<1e-09` | 必ず | 0・1.00（110） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O20 | `[where:gentle==true, where:joint==true] * => err_abs<1e-09` | 必ず | 3・0.00（30） | — | 3・0.00（30） | — | — | — | **3** 異議あり（不成立） | O10 |
| O21 | `[where:gentle==true, where:joint==true] n==1 => joint_ratio<=1.000001 & joint_ratio>=0.999999` | 必ず | 0・1.00（10） | — | 0・1.00（20） | 0・1.00（10） | 0・1.00（20） | — | **0** 異議なし |  |
| O22 | `[where:affine==true, where:gentle==true] * => err_abs<1e-09` | 必ず | 0・1.00（30） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O23 | `[where:chain==true] * => err_abs<1e-09` | 必ず | 3・0.00（50） | — | 3・0.00（50） | — | — | — | **3** 異議あり（不成立） |  |
| O24 | `[where:chain==true] * => first_err_abs<1e-09` | 必ず | 0・1.00（50） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O25 | `[where:chain==true, where:has_half==true] h<=0.03125 => chain_halving<=2.1 & chain_halving>=1.9` | 必ず | 0・1.00（10） | — | 4・1.00（9） | 3・0.48（21） | 3・0.45（20） | — | **4** 待った！判断保留 |  |
| O26 | `[where:native==true] * => err_abs<1e-09` | 必ず | 0・1.00（160） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O27 | `[where:chain2==true, where:independent==true] h<=0.03125 => chain_pred_rel<=0.05` | 必ず | 0・1.00（24） | — | 0・1.00（32） | 3・0.50（48） | 3・0.57（56） | — | **3** 異議あり（不成立） |  |
| O28 | `[where:fed==true, where:independent==true] * => err_abs<1e-09` | 必ず | 3・0.00（30） | — | 3・0.00（30） | — | — | — | **3** 異議あり（不成立） |  |
| O29 | `[where:fed==true, where:independent==true] * => fed_gap<1e-09` | 必ず | 0・1.00（30） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O30 | `[where:fed==true, where:uniform==true] * => err_abs<1e-09` | 必ず | 0・1.00（30） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O31 | `[where:chain2==true, where:uniform==true] * => err_abs<1e-09` | 必ず | 3・0.00（80） | — | 3・0.00（80） | — | — | — | **3** 異議あり（不成立） |  |
| O32 | `[where:chain2==true, where:uniform==true] h<=0.03125 => gain_vs_independent>=10` | 必ず | 0・1.00（24） | — | 4・1.00（6） | 3・0.32（74） | 3・0.11（56） | — | **4** 待った！判断保留 |  |
| O33 | `[where:chain2==true, where:has_half==true, where:uniform==true] h<=0.03125 => uniform_halving<=4.2 & uniform_halving>=3.8` | 必ず | 0・1.00（16） | — | 4・-（0） | 3・0.33（48） | 3・0.00（32） | — | **4** 待った！判断保留 |  |
| O34 | `[where:chain2==true, where:through==true] * => err_abs<1e-09` | 必ず | 0・1.00（80） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O35 | `[where:flow==true, where:from_pump==true] * => err_abs<1e-09` | 必ず | 0・1.00（30） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O36 | `[where:flow==true, where:from_pump==false] * => native_gap<1e-09` | 必ず | 0・1.00（80） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O37 | `[where:combo==true, where:uniform_in==true] * => err_abs<1e-09` | 必ず | 0・1.00（50） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O38 | `[where:combo==true, where:uniform_in==false] * => err_abs>=1e-09` | 必ず | 0・1.00（50） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| O39 | `[where:chain3==true, where:uniform_in==false] h<=0.03125 => chain3_pred_rel<=0.05` | 必ず | 3・0.00（12） | — | 3・0.68（38） | 4・0.00（2） | 3・0.93（28） | — | **3** 異議あり（不成立） |  |
| O40 | `[where:chain3==true, where:uniform_in==true] h<=0.03125 => gain_vs_end>=10` | 必ず | 0・1.00（12） | — | 0・1.00（11） | 3・0.41（29） | 3・0.39（28） | — | **3** 異議あり（不成立） |  |
| O41 | `[where:chain3==true, where:has_half==true, where:uniform_in==true] h<=0.03125 => flow_halving<=4.2 & flow_halving>=3.8` | 必ず | 4・1.00（8） | — | 4・1.00（5） | 3・0.42（19） | 3・0.31（16） | — | **4** 待った！判断保留 |  |
| O42 | `[where:ring==true, where:settled==false, where:uniform_in==true] h<=0.03125 => gain_vs_end>=10` | 必ず | 0・1.00（12） | — | 4・1.00（8） | 3・0.38（32） | 3・0.29（28） | — | **4** 待った！判断保留 |  |
| O43 | `[where:ring==true, where:settled==true, where:uniform_in==true] * => err_abs<1e-09` | 必ず | 3・0.97（40） | — | 4・0.00（1） | — | — | — | **3** 異議あり（不成立） |  |
| O44 | `[where:ring==true, where:settled==true, where:uniform_in==false] * => err_abs>=1e-09` | 必ず | 0・1.00（40） | — | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |

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
| **O16** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O17** | 0.867 | 1.000 | 0.929 | 0.920 | 0.917 | 0.850 | None (not_evaluated) |
| **O18** | 0.800 | 1.000 | 0.889 | 0.800 | 0.500 | None | None (not_evaluated) |
| **O19** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O20** | 0.000 | None | 0.000 | 0.000 | None | None | None (not_evaluated) |
| **O21** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | None (not_evaluated) |
| **O22** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O23** | 0.000 | None | 0.000 | 0.000 | None | None | None (not_evaluated) |
| **O24** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O25** | 1.000 | 0.476 | 0.645 | 0.633 | 0.738 | 0.463 | None (not_evaluated) |
| **O26** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O27** | 1.000 | 0.500 | 0.667 | 0.700 | 0.750 | 0.535 | None (not_evaluated) |
| **O28** | 0.000 | None | 0.000 | 0.000 | None | None | None (not_evaluated) |
| **O29** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O30** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O31** | 0.000 | None | 0.000 | 0.000 | None | None | None (not_evaluated) |
| **O32** | 1.000 | 0.324 | 0.490 | 0.375 | 0.662 | 0.186 | None (not_evaluated) |
| **O33** | 1.000 | 0.333 | 0.500 | 0.333 | None | None | None (not_evaluated) |
| **O34** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O35** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O36** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O37** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O38** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
| **O39** | 0.000 | 0.000 | 0.000 | 0.650 | 0.342 | -0.150 | None (not_evaluated) |
| **O40** | 1.000 | 0.414 | 0.585 | 0.575 | 0.707 | 0.403 | None (not_evaluated) |
| **O41** | 1.000 | 0.421 | 0.593 | 0.542 | 0.711 | 0.363 | None (not_evaluated) |
| **O42** | 1.000 | 0.375 | 0.545 | 0.500 | 0.688 | 0.327 | None (not_evaluated) |
| **O43** | 0.975 | 1.000 | 0.987 | 0.975 | 0.500 | None | None (not_evaluated) |
| **O44** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (not_evaluated) |
