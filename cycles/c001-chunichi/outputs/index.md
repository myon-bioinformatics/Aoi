# 命題の一覧（自動生成）

命題ファイル SHA-256: `0074801d0ede337a76c98624e8d206912ad0ee42a89fecde9d8eb7646d52a35a` / コード: `3a7592dfed1833e84fd2f38d81ac1ad6ed834bbb`

各形のセルは「終了コード・成立率（単位数）」。0 異議なし、1 例外あり、2 主張が強すぎる、3 不成立、4 判断保留、5 判定できない単位。
σ は、元の命題の成立数が強さの基準（概ね 0.75・多くの場合 0.5 など）から標準偏差いくつ分上（＋）か下（−）か。終了コードの判定（95% の区間、両側でおよそ ±2σ）とは別に、±1σ・±2σ・±3σ で読むための値。
判例と根拠は objections.md、規則は docs/propositions.md。

総合の終了コードの内訳: exit 1 異議あり（例外あり） 16件、exit 2 異議あり（主張が強すぎる） 6件、exit 3 異議あり（不成立） 20件、exit 4 待った！判断保留 72件

| id | 識別子 | 強さ | 元の命題 | σ | 対偶 | 逆 | 裏 | きっかけ以外 | 総合 | 親 |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | `[all] rd>0 => upper_half==true` | 概ね | 4・0.84（73） | +1.69σ | 1・0.85（78） | 4・0.78（78） | 4・0.80（83） | — | **4** 待った！判断保留 |  |
| P2 | `[all] rank_pythag<=3 => rank<=3` | 概ね | 1・0.86（78） | +2.22σ | 1・0.86（78） | 1・0.86（78） | 1・0.86（78） | — | **1** 異議あり（例外あり） |  |
| P3 | `[all] rank_rf<=2 => rank<=3` | 概ね | 4・0.70（53） | -0.87σ | 4・0.79（78） | 2・0.47（78） | 2・0.60（103） | — | **4** 待った！判断保留 |  |
| P4 | `[all] rank_ra<=2 => rank<=3` | 概ね | 4・0.73（52） | -0.32σ | 4・0.82（78） | 2・0.49（78） | 2・0.62（104） | — | **4** 待った！判断保留 |  |
| P5 | `[all] rank_rf>=5 => upper_half==false` | 概ね | 4・0.85（52） | +1.60σ | 1・0.90（78） | 2・0.56（78） | 4・0.67（104） | — | **4** 待った！判断保留 |  |
| P6 | `[all] * => wins_vs_pythag<=5 & wins_vs_pythag>=-5` | ほとんど | 3・0.77（156） | -5.44σ | 3・0.00（36） | — | — | — | **3** 異議あり（不成立） |  |
| P9 | `[all] one_run_net>0 => wins_vs_pythag>0` | 概ね | 4・0.74（76） | -0.26σ | 4・0.76（82） | 4・0.76（74） | 4・0.78（80） | — | **4** 待った！判断保留 |  |
| P10 | `[all] blowout_net<0 => wins_vs_pythag>0` | 概ね | 2・0.61（76） | -2.91σ | 2・0.63（82） | 2・0.62（74） | 2・0.65（80） | — | **2** 異議あり（主張が強すぎる） |  |
| P11 | `[all] one_run_net>0 & rd<=20 & rd>=-20 => upper_half==true` | 多くの場合 | 1・0.90（20） | +3.58σ | 1・0.97（78） | 2・0.23（78） | 4・0.56（136） | — | **1** 異議あり（例外あり） |  |
| P7 | `[all] team=="d" => rank_gap<=1` | 概ね | 4・0.92（13） | +1.44σ | 4・0.88（8） | — | — | — | **4** 待った！判断保留 |  |
| P8 | `[all] team=="d" => wins_vs_pythag>=-3` | 概ね | 4・0.77（13） | +0.16σ | 1・0.91（33） | — | — | — | **4** 待った！判断保留 |  |
| P12 | `[all] alloc_z>=1 => alloc_z_next>0` | 多くの場合 | 4・0.54（28） | +0.38σ | 1・0.82（72） | 3・0.21（72） | 4・0.51（116） | — | **4** 待った！判断保留 |  |
| P13 | `[all] alloc_z_abs>=1 => alloc_same_sign==true` | 多くの場合 | 1・0.64（61） | +2.18σ | 1・0.78（99） | 1・0.68（57） | 1・0.81（95） | — | **1** 異議あり（例外あり） |  |
| P14 | `[all] team=="d" => alloc_net>=0` | 概ね | 3・0.38（13） | -3.04σ | 1・0.90（78） | — | — | — | **3** 異議あり（不成立） |  |
| P15 | `[where:rank_rf>=5] rank_ra<=2 => upper_half==true` | 概ね | 2・0.38（16） | -3.46σ | 4・0.77（44） | 4・0.75（8） | 1・0.94（36） | — | **2** 異議あり（主張が強すぎる） |  |
| P16 | `[where:rank_rf>=5] wins_vs_pythag>0 => upper_half==true` | 多くの場合 | 3・0.17（24） | -3.27σ | 4・0.55（44） | 4・0.50（8） | 1・0.86（28） | — | **3** 異議あり（不成立） |  |
| P17 | `[team=d, where:rank_rf>=5] * => rank_ra>=3` | 概ね | 4・0.64（11） | -0.87σ | 4・0.00（4） | — | — | — | **4** 待った！判断保留 |  |
| P18 | `[where:rank_ra<=2, where:rank_rf>=5] rd>0 => upper_half==true` | 概ね | 4・0.83（6） | +0.47σ | 4・0.90（10） | 4・0.83（6） | 4・0.90（10） | 判断保留・-（0） | **4** 待った！判断保留 | P15 |
| P19 | `[team=d, where:rank_rf>=5] * => rf_def_floor_minus_ceiling<0` | 概ね | 3・0.00（11） | -5.74σ | 3・0.00（11） | — | — | — | **3** 異議あり（不成立） |  |
| P20 | `[where:rank_rf>=5] * => rf_def_floor_minus_ceiling<0` | 多くの場合 | 3・0.23（52） | -3.88σ | 3・0.00（40） | — | — | — | **3** 異議あり（不成立） |  |
| P21 | `[where:rank_rf>=5] rf_def_floor_minus_ceiling<0 => upper_half==false` | 概ね | 4・0.75（12） | +0.00σ | 4・0.62（8） | 3・0.20（44） | 3・0.12（40） | — | **4** 待った！判断保留 |  |
| P22 | `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_freq_minus_size<0` | 概ね | 4・0.55（11） | -1.57σ | 4・0.00（5） | — | — | — | **4** 待った！判断保留 |  |
| P23 | `[seasons=2013-2025, where:rank_rf>=5] * => inn_freq_minus_size<0` | 多くの場合 | 1・0.73（48） | +3.18σ | 3・0.00（13） | — | — | — | **1** 異議あり（例外あり） |  |
| P24 | `[seasons=2013-2025, where:rank_rf>=5] inn_freq_minus_size<0 => upper_half==false` | 概ね | 4・0.89（35） | +1.85σ | 4・0.43（7） | 4・0.76（41） | 3・0.23（13） | — | **4** 待った！判断保留 |  |
| P25 | `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_freq_minus_size_6<0` | 概ね | 4・0.64（11） | -0.87σ | 4・0.00（4） | — | — | — | **4** 待った！判断保留 |  |
| P26 | `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_d_single_share>0` | 概ね | 4・0.91（11） | +1.22σ | 4・0.00（1） | — | — | — | **4** 待った！判断保留 |  |
| P27 | `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_d_big_share<0` | 概ね | 4・1.00（11） | +1.91σ | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| P28 | `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_dlog_size_home<0` | 概ね | 4・0.91（11） | +1.22σ | 4・0.00（1） | — | — | — | **4** 待った！判断保留 |  |
| P29 | `[team=d, seasons=2013-2025, where:rank_rf>=5] * => inn_dlog_size_away<0` | 概ね | 4・0.91（11） | +1.22σ | 4・0.00（1） | — | — | — | **4** 待った！判断保留 |  |
| P30 | `[seasons=2013-2025, where:rank_rf>=5, where:team!="d"] * => inn_d_big_share<0` | 多くの場合 | 1・0.76（37） | +3.12σ | 4・0.00（9） | — | — | — | **1** 異議あり（例外あり） |  |
| P31 | `[team=d, where:rank_rf>=5] * => bat_d_iso<0` | 概ね | 4・1.00（11） | +1.91σ | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| P32 | `[team=d, where:rank_rf>=5] * => bat_d_obp<0` | 概ね | 4・1.00（11） | +1.91σ | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| P33 | `[seasons=2013-2025] bat_d_iso<0 => inn_d_big_share<0` | 概ね | 4・0.66（76） | -1.85σ | 2・0.64（72） | 4・0.69（72） | 4・0.68（68） | — | **4** 待った！判断保留 |  |
| P34 | `[seasons=2013-2025] bat_d_obp<0 => inn_dlog_freq<0` | 概ね | 4・0.79（72） | +0.82σ | 4・0.80（76） | 4・0.84（68） | 4・0.85（72） | — | **4** 待った！判断保留 |  |
| P35 | `[seasons=2013-2025] bat_d_iso<0 => inn_d_big_share<0` | 多くの場合 | 1・0.66（76） | +2.75σ | 1・0.64（72） | 1・0.69（72） | 1・0.68（68） | — | **1** 異議あり（例外あり） | P33 |
| P36 | `[team=d, where:rank_rf>=5] * => rf_def_floor_minus_k67<0` | 概ね | 3・0.27（11） | -3.66σ | 4・0.00（8） | — | — | — | **3** 異議あり（不成立） | P19 |
| P37 | `[where:rank_rf>=5] * => rf_def_floor_minus_k67<0` | 多くの場合 | 4・0.40（52） | -1.39σ | 3・0.00（31） | — | — | — | **4** 待った！判断保留 | P20 |
| P38 | `[seasons=2013-2025] bat_d_bb_pa<0 => inn_dlog_size<0` | 概ね | 2・0.60（73） | -2.91σ | 2・0.64（81） | 4・0.70（63） | 4・0.73（71） | — | **2** 異議あり（主張が強すぎる） |  |
| P39 | `[seasons=2013-2025] bat_d_iso<0 => inn_dlog_size<0` | 概ね | 2・0.57（76） | -3.71σ | 2・0.59（81） | 4・0.68（63） | 4・0.71（68） | — | **2** 異議あり（主張が強すぎる） |  |
| P40 | `[team=d, where:rank_rf>=5] * => bat_d_walk_share<0` | 概ね | 4・0.82（11） | +0.52σ | 4・0.00（2） | — | — | — | **4** 待った！判断保留 |  |
| P41 | `[where:rank_rf>=5] bat_d_walk_share<0 => upper_half==false` | 概ね | 4・0.84（32） | +1.22σ | 4・0.38（8） | 3・0.61（44） | 3・0.15（20） | — | **4** 待った！判断保留 |  |
| P42 | `[where:rank_rf>=5] bat_d_iso<0 => upper_half==false` | 概ね | 4・0.87（45） | +1.81σ | 4・0.25（8） | 1・0.89（44） | 4・0.29（7） | — | **4** 待った！判断保留 |  |
| P43 | `[where:rank_rf>=5] bat_d_bb_pa<0 => upper_half==false` | 概ね | 4・0.85（40） | +1.46σ | 4・0.25（8） | 4・0.77（44） | 3・0.17（12） | — | **4** 待った！判断保留 |  |
| P44 | `[seasons=2013-2025] bat_d_walk_share<0 => inn_dlog_size<0` | 概ね | 2・0.56（71） | -3.63σ | 2・0.62（81） | 2・0.63（63） | 4・0.68（73） | — | **2** 異議あり（主張が強すぎる） |  |
| P45 | `[team=d, where:rank_rf>=5] * => bat_d_ibb_bb<0` | 概ね | 4・0.64（11） | -0.87σ | 4・0.00（4） | — | — | — | **4** 待った！判断保留 |  |
| P46 | `[team=d, where:rank_rf>=5] * => bat_d_r_runner<0` | 概ね | 4・1.00（11） | +1.91σ | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| P47 | `[where:rank_rf>=5, where:team!="d"] * => bat_d_r_runner<0` | 多くの場合 | 1・0.88（41） | +4.84σ | 4・0.00（5） | — | — | — | **1** 異議あり（例外あり） |  |
| P48 | `[seasons=2013-2025] bat_d_r_runner<0 => inn_dlog_size<0` | 概ね | 4・0.68（71） | -1.44σ | 4・0.72（81） | 4・0.76（63） | 4・0.79（73） | — | **4** 待った！判断保留 |  |
| P49 | `[where:rank_rf>=5] bat_d_r_runner<0 => upper_half==false` | 概ね | 4・0.87（47） | +1.94σ | 4・0.25（8） | 1・0.93（44） | 4・0.40（5） | — | **4** 待った！判断保留 |  |
| P50 | `[all] sim_p_upper>=0.5 => upper_half==true` | 概ね | 1・0.88（77） | +2.70σ | 1・0.88（78） | 1・0.87（78） | 1・0.87（79） | — | **1** 異議あり（例外あり） |  |
| P51 | `[team=d] * => sim_p_upper<0.5` | 概ね | 4・0.77（13） | +0.16σ | 4・0.00（3） | — | — | — | **4** 待った！判断保留 |  |
| P52 | `[all] ((alloc_z_strat<-1) \| (sim_p_upper<0.4)) => upper_half==false` | 概ね | 1・0.88（83） | +2.73σ | 1・0.87（78） | 1・0.94（78） | 1・0.93（73） | — | **1** 異議あり（例外あり） |  |
| P53 | `[where:rank<=4, where:rank>=3] pair34_net>0 => upper_half==true` | 概ね | 4・0.64（25） | -1.27σ | 4・0.65（26） | 4・0.62（26） | 4・0.63（27） | — | **4** 待った！判断保留 |  |
| P54 | `[where:rank<=4, where:rank>=3] half2_vs_pythag>0 => upper_half==true` | 多くの場合 | 4・0.58（24） | +0.82σ | 4・0.62（26） | 4・0.54（26） | 4・0.57（28） | — | **4** 待った！判断保留 |  |
| P55 | `[where:rank<=4, where:rank>=3] max_lose_streak_d<0 => upper_half==true` | 多くの場合 | 4・0.42（26） | -0.78σ | 4・0.42（26） | 4・0.42（26） | 4・0.42（26） | — | **4** 待った！判断保留 |  |
| P56 | `[where:rank<=4, where:rank>=3] sim_p_upper>=0.5 => upper_half==true` | 多くの場合 | 1・0.71（28） | +2.27σ | 1・0.69（26） | 1・0.77（26） | 1・0.75（24） | — | **1** 異議あり（例外あり） |  |
| P57 | `[where:rank<=4, where:rank>=3] pair34_vs_lower_wpct_diff>0 => upper_half==true` | 多くの場合 | 4・0.62（26） | +1.18σ | 4・0.62（26） | 4・0.62（26） | 4・0.62（26） | — | **4** 待った！判断保留 |  |
| P58 | `[where:rank<=4, where:rank>=3] pair34_vs_battle_wpct_diff>0 => upper_half==true` | 多くの場合 | 4・0.54（26） | +0.39σ | 4・0.54（26） | 4・0.54（26） | 4・0.54（26） | — | **4** 待った！判断保留 |  |
| P59 | `[where:rank<=4, where:rank>=3] pair34_focus_gap_diff>0 => upper_half==true` | 多くの場合 | 4・0.54（26） | +0.39σ | 4・0.54（26） | 4・0.54（26） | 4・0.54（26） | — | **4** 待った！判断保留 |  |
| P60 | `[all] alloc_z_strat<-1 => vs_lower_wpct_d<0` | 概ね | 4・0.75（28） | +0.00σ | 1・0.91（82） | 2・0.28（74） | 2・0.59（128） | — | **4** 待った！判断保留 |  |
| P61 | `[team=d] * => focus_gap<0` | 概ね | 3・0.15（13） | -4.96σ | 3・0.00（11） | — | — | — | **3** 異議あり（不成立） |  |
| P62 | `[seasons=2013-2025] inn_size_low_streak>=2 => upper_half==false` | 概ね | 0・1.00（16） | +2.31σ | 0・1.00（72） | 2・0.22（72） | 2・0.56（128） | — | **2** 異議あり（主張が強すぎる） |  |
| P63 | `[seasons=2013-2025, where:team!="d"] inn_size_low_streak>=2 => upper_half==false` | 概ね | 4・1.00（7） | +1.53σ | 0・1.00（72） | 2・0.12（60） | 2・0.58（125） | — | **4** 待った！判断保留 |  |
| P64 | `[all] rf_low_streak>=2 => upper_half==false` | 概ね | 4・0.85（26） | +1.13σ | 1・0.95（78） | 2・0.28（78） | 2・0.57（130） | — | **4** 待った！判断保留 |  |
| P65 | `[where:team!="d"] rf_low_streak>=2 => upper_half==false` | 概ね | 4・0.76（17） | +0.14σ | 1・0.95（77） | 2・0.20（66） | 2・0.58（126） | — | **4** 待った！判断保留 |  |
| P66 | `[where:rank<=4, where:rank>=3] pair34_opp_adj_mid_diff>0 => upper_half==true` | 多くの場合 | 4・0.58（26） | +0.78σ | 4・0.58（26） | 4・0.58（26） | 4・0.58（26） | — | **4** 待った！判断保留 |  |
| P67 | `[where:rank<=4, where:rank>=3] pair34_opp_adj_low_diff>0 => upper_half==true` | 多くの場合 | 4・0.58（26） | +0.78σ | 4・0.58（26） | 4・0.58（26） | 4・0.58（26） | — | **4** 待った！判断保留 |  |
| P68 | `[where:rank<=4, where:rank>=3] pair34_opp_adj_total_diff>0 => upper_half==true` | 多くの場合 | 4・0.62（26） | +1.18σ | 4・0.62（26） | 4・0.62（26） | 4・0.62（26） | — | **4** 待った！判断保留 |  |
| P69 | `[team=d] * => opp_adj_mid<0` | 概ね | 4・0.54（13） | -1.76σ | 4・0.00（6） | — | — | — | **4** 待った！判断保留 |  |
| P70 | `[team=d] * => opp_rf_gap_top<0` | 概ね | 3・0.31（13） | -3.68σ | 4・0.00（9） | — | — | — | **3** 異議あり（不成立） |  |
| P71 | `[team=d] * => opp_ra_gap_top<0` | 概ね | 3・0.31（13） | -3.68σ | 4・0.00（9） | — | — | — | **3** 異議あり（不成立） |  |
| P72 | `[all] opp_adj_top<0 => opp_top_rf_minus_ra<0` | 多くの場合 | 4・0.54（57） | +0.66σ | 1・0.67（79） | 4・0.40（77） | 4・0.54（99） | — | **4** 待った！判断保留 |  |
| P73 | `[all] opp_adj_top<0 => opp_conv_top<0` | 多くの場合 | 1・0.72（57） | +3.31σ | 1・0.80（81） | 4・0.55（75） | 1・0.66（99） | — | **1** 異議あり（例外あり） |  |
| P74 | `[team=d] * => opp_rf_gap_top_c<0` | 概ね | 3・0.46（13） | -2.40σ | 4・0.00（7） | — | — | — | **3** 異議あり（不成立） | P70 |
| P75 | `[team=d] * => opp_ra_gap_top_c<0` | 概ね | 3・0.31（13） | -3.68σ | 4・0.00（9） | — | — | — | **3** 異議あり（不成立） | P71 |
| P76 | `[where:rd>0, where:upper_half==false] * => opp_rf_gap_top_c<0` | 多くの場合 | 4・0.42（12） | -0.58σ | 4・0.00（7） | — | — | 判断保留・0.36（11） -0.90σ | **4** 待った！判断保留 | P74 |
| P77 | `[where:rank==4, where:sim_p_upper>=0.5] * => pair34_net<0` | 多くの場合 | 4・0.50（8） | +0.00σ | 4・0.00（4） | — | — | 判断保留・0.43（7） -0.38σ | **4** 待った！判断保留 | P53 |
| P78 | `[where:rank==4, where:sim_p_upper>=0.5] * => opp_conv_top<0` | 多くの場合 | 4・0.88（8） | +2.12σ | 4・0.00（1） | — | — | 判断保留・0.86（7） +1.89σ | **4** 待った！判断保留 | P73 |
| P79 | `[all] opp_rf_gap_top_c<0 => opp_ra_gap_top_c>0` | 多くの場合 | 1・0.66（79） | +2.81σ | 1・0.64（74） | 1・0.63（82） | 4・0.61（77） | — | **1** 異議あり（例外あり） |  |
| P80 | `[where:rd>0, where:upper_half==false] * => opp_env_gap_top_c<0` | 多くの場合 | 4・0.50（12） | +0.00σ | 4・0.00（6） | — | — | 判断保留・0.45（11） -0.30σ | **4** 待った！判断保留 | P76 |
| P81 | `[seasons=2013-2025] inn_dlog_size<0 => opp_env_gap_top_c<0` | 多くの場合 | 4・0.56（63） | +0.88σ | 4・0.59（69） | 4・0.47（75） | 4・0.51（81） | 判断保留・0.53（60） +0.52σ | **4** 待った！判断保留 |  |
| P82 | `[seasons=2013-2025] inn_dlog_size<0 => opp_env_gap_mid_c<0` | 多くの場合 | 4・0.49（63） | -0.13σ | 4・0.55（71） | 4・0.42（73） | 4・0.48（81） | — | **4** 待った！判断保留 |  |
| P83 | `[all] rank_ra<=2 => opp_env_gap_top_c<0` | 多くの場合 | 4・0.63（52） | +1.94σ | 1・0.75（76） | 4・0.41（80） | 4・0.55（104） | 判断保留・0.61（49） +1.57σ | **4** 待った！判断保留 |  |
| P84 | `[all] upper_half==true => opp_env_gap_top_c<0` | 多くの場合 | 4・0.51（78） | +0.23σ | 4・0.50（76） | 4・0.50（80） | 4・0.49（78） | — | **4** 待った！判断保留 |  |
| P85 | `[team=d] * => wl_rf_win_gap<0` | 概ね | 4・0.92（13） | +1.44σ | 4・0.00（1） | — | — | — | **4** 待った！判断保留 |  |
| P86 | `[team=d] * => wl_rf_loss_gap>0` | 概ね | 4・0.85（13） | +0.80σ | 4・0.00（2） | — | — | — | **4** 待った！判断保留 |  |
| P87 | `[team=d] * => wl_wpct_high_gap<0` | 概ね | 3・0.46（13） | -2.40σ | 4・0.00（7） | — | — | — | **3** 異議あり（不成立） |  |
| P88 | `[team=d] * => course_wpct_diff<0` | 概ね | 4・0.54（13） | -1.76σ | 4・0.00（6） | — | — | — | **4** 待った！判断保留 |  |
| P89 | `[team=d, where:upper_half==false] * => course_rank_h1<=3` | 多くの場合 | 3・0.17（12） | -2.31σ | 3・0.00（10） | — | — | — | **3** 異議あり（不成立） |  |
| P90 | `[where:team!="d", where:upper_half==false] * => course_rank_h1<=3` | 多くの場合 | 3・0.26（66） | -3.94σ | 3・0.00（49） | — | — | — | **3** 異議あり（不成立） |  |
| P91 | `[all] course_close_win_h1_d>0 => course_ra_d>0` | 多くの場合 | 4・0.46（78） | -0.68σ | 4・0.45（77） | 4・0.46（79） | 4・0.45（78） | — | **4** 待った！判断保留 |  |
| P92 | `[all] course_close_win_h1_d>0 => course_wpct_diff<0` | 多くの場合 | 4・0.49（78） | -0.23σ | 4・0.53（85） | 4・0.54（71） | 4・0.58（78） | — | **4** 待った！判断保留 |  |
| P93 | `[all] course_ra_h1_d<0 => course_ra_d>0` | 多くの場合 | 1・0.69（83） | +3.40σ | 1・0.66（77） | 1・0.72（79） | 1・0.70（73） | — | **1** 異議あり（例外あり） |  |
| P94 | `[all] half1_vs_pythag>0 => course_wpct_diff<0` | 多くの場合 | 4・0.58（86） | +1.51σ | 4・0.58（85） | 1・0.70（71） | 1・0.70（70） | — | **4** 待った！判断保留 |  |
| P95 | `[all] ((alloc_z_strat<-1) \| (opp_conv_top<-2) \| (sim_p_upper<0.4)) => upper_half==false` | 概ね | 4・0.81（93） | +1.26σ | 4・0.77（78） | 1・0.96（78） | 1・0.95（63） | 判断保留・0.80（92） +1.20σ | **4** 待った！判断保留 | P52 |
| P96 | `[all] ((alloc_z_strat<-1 & rd<50) \| (rd<-50) \| (sim_p_upper<0.5 & wins_vs_pythag<0)) => upper_half==false` | 概ね | 1・0.99（69） | +4.52σ | 1・0.99（78） | 1・0.87（78） | 1・0.89（87） | — | **1** 異議あり（例外あり） |  |
| P97 | `[team=d, where:upper_half==false] * => traj_rank_peak==true` | 多くの場合 | 4・0.67（12） | +1.15σ | 4・0.00（4） | — | — | — | **4** 待った！判断保留 |  |
| P98 | `[where:team!="d", where:upper_half==false] * => traj_rank_peak==true` | 多くの場合 | 1・0.79（66） | +4.68σ | 3・0.00（14） | — | — | — | **1** 異議あり（例外あり） |  |
| P99 | `[team=d] * => traj_wl_peak==true` | 多くの場合 | 4・0.31（13） | -1.39σ | 4・0.00（9） | — | — | — | **4** 待った！判断保留 |  |
| P100 | `[team=d, where:upper_half==false] * => traj_rank_end_slope<0` | 概ね | 3・0.50（12） | -2.00σ | 4・0.00（6） | — | — | — | **3** 異議あり（不成立） |  |
| P101 | `[where:team!="d", where:upper_half==false] * => traj_rank_end_slope<0` | 概ね | 3・0.53（66） | -4.12σ | 3・0.00（31） | — | — | — | **3** 異議あり（不成立） |  |
| P102 | `[team=d, where:upper_half==false] * => wave_settle_pct<0.5` | 多くの場合 | 4・0.67（12） | +1.15σ | 4・0.00（4） | — | — | — | **4** 待った！判断保留 |  |
| P103 | `[where:team!="d", where:upper_half==false] * => wave_settle_pct<0.5` | 多くの場合 | 3・0.38（66） | -1.97σ | 3・0.00（41） | — | — | — | **3** 異議あり（不成立） |  |
| P104 | `[team=d, where:upper_half==false] * => wave_limit_rank_h1>=3.5` | 多くの場合 | 4・1.00（6） | +2.45σ | 4・-（0） | — | — | — | **4** 待った！判断保留 |  |
| P105 | `[where:team!="d", where:upper_half==false] * => wave_limit_rank_h1>=3.5` | 多くの場合 | 1・0.78（58） | +4.20σ | 3・0.00（13） | — | — | — | **1** 異議あり（例外あり） |  |
| P106 | `[team=d] * => series_lost_pct>0.5` | 多くの場合 | 4・0.77（13） | +1.94σ | 4・0.00（3） | — | — | — | **4** 待った！判断保留 |  |
| P107 | `[where:team!="d"] * => series_lost_pct>0.5` | 多くの場合 | 4・0.52（143） | +0.59σ | 3・0.00（68） | — | — | — | **4** 待った！判断保留 |  |
| P108 | `[team=d] * => series_disp_pct<0.5` | 多くの場合 | 4・0.31（13） | -1.39σ | 4・0.00（9） | — | — | — | **4** 待った！判断保留 |  |
| P109 | `[where:team!="d"] * => series_disp_pct<0.5` | 多くの場合 | 4・0.49（143） | -0.25σ | 3・0.00（73） | — | — | — | **4** 待った！判断保留 |  |
| P110 | `[team=d] * => series_g1_minus_rest>0` | 多くの場合 | 4・0.69（13） | +1.39σ | 4・0.00（4） | — | — | — | **4** 待った！判断保留 |  |
| P111 | `[where:team!="d"] * => series_g1_minus_rest>0` | 多くの場合 | 4・0.53（143） | +0.75σ | 3・0.00（67） | — | — | — | **4** 待った！判断保留 |  |
| P112 | `[team=d, where:upper_half==false] * => clinch_out_left>=10` | 多くの場合 | 3・0.08（12） | -2.89σ | 3・0.00（11） | — | — | — | **3** 異議あり（不成立） |  |
| P113 | `[where:team!="d", where:upper_half==false] * => clinch_out_left>=10` | 多くの場合 | 3・0.29（66） | -3.45σ | 3・0.00（47） | — | — | — | **3** 異議あり（不成立） |  |
| P114 | `[where:traj_wl_peak==true, where:upper_half==true] * => traj_wl_peak_after_clinch==true` | 多くの場合 | 3・0.09（46） | -5.60σ | 3・0.00（42） | — | — | — | **3** 異議あり（不成立） |  |

## 全命題の共通評価軸

過小評価かどうか・元の支持判定にかかわらず同じ項目を表示する。分類指標は条件不成立を陰性予測とする診断で、逆命題を要求するものではない。
`None` は計算不能・未評価。欠けた値を0や不変に置き換えない。分母0などの理由はJSONのmetrics.none_reasons、seedの理由はseed_sensitivity.reasonを参照。
seed比較は命題定義・年・生成条件ごと。試したseed内の不変性であり、全seedの不変性・統計的有意性・因果は主張しない。

| 命題 | Precision | Recall | F1 | Accuracy | Balanced Accuracy | MCC | 合成seed評価 |
|---|---|---|---|---|---|---|---|
| **P1** | 0.836 | 0.782 | 0.808 | 0.814 | 0.814 | 0.629 | evaluated (8条件; 条件別に表示) |
| **P2** | 0.859 | 0.859 | 0.859 | 0.859 | 0.859 | 0.718 | evaluated (8条件; 条件別に表示) |
| **P3** | 0.698 | 0.474 | 0.565 | 0.635 | 0.635 | 0.284 | evaluated (8条件; 条件別に表示) |
| **P4** | 0.731 | 0.487 | 0.585 | 0.654 | 0.654 | 0.326 | evaluated (8条件; 条件別に表示) |
| **P5** | 0.846 | 0.564 | 0.677 | 0.731 | 0.731 | 0.490 | evaluated (8条件; 条件別に表示) |
| **P6** | 0.769 | 1.000 | 0.870 | 0.769 | 0.500 | None | evaluated (8条件; 条件別に表示) |
| **P9** | 0.737 | 0.757 | 0.747 | 0.756 | 0.756 | 0.512 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P10** | 0.605 | 0.622 | 0.613 | 0.628 | 0.628 | 0.256 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P11** | 0.900 | 0.231 | 0.367 | 0.603 | 0.603 | 0.307 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P7** | 0.923 | 0.081 | 0.149 | 0.122 | 0.478 | -0.035 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P8** | 0.769 | 0.081 | 0.147 | 0.256 | 0.495 | -0.014 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P12** | 0.536 | 0.208 | 0.300 | 0.514 | 0.514 | 0.035 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P13** | 0.639 | 0.684 | 0.661 | 0.744 | 0.731 | 0.456 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P14** | 0.385 | 0.064 | 0.110 | 0.481 | 0.481 | -0.070 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P15** | 0.375 | 0.750 | 0.500 | 0.769 | 0.761 | 0.409 | evaluated (8条件; 条件別に表示) |
| **P16** | 0.167 | 0.500 | 0.250 | 0.538 | 0.523 | 0.033 | evaluated (8条件; 条件別に表示) |
| **P17** | 0.636 | 1.000 | 0.778 | 0.636 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P18** | 0.833 | 0.833 | 0.833 | 0.875 | 0.867 | 0.733 | evaluated (8条件; 条件別に表示) |
| **P19** | 0.000 | None | 0.000 | 0.000 | None | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P20** | 0.231 | 1.000 | 0.375 | 0.231 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P21** | 0.750 | 0.205 | 0.321 | 0.269 | 0.415 | -0.146 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P22** | 0.545 | 1.000 | 0.706 | 0.545 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P23** | 0.729 | 1.000 | 0.843 | 0.729 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P24** | 0.886 | 0.756 | 0.816 | 0.708 | 0.592 | 0.147 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P25** | 0.636 | 1.000 | 0.778 | 0.636 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P26** | 0.909 | 1.000 | 0.952 | 0.909 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P27** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P28** | 0.909 | 1.000 | 0.952 | 0.909 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P29** | 0.909 | 1.000 | 0.952 | 0.909 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P30** | 0.757 | 1.000 | 0.862 | 0.757 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P31** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P32** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P33** | 0.658 | 0.694 | 0.676 | 0.667 | 0.667 | 0.334 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P34** | 0.792 | 0.838 | 0.814 | 0.819 | 0.820 | 0.640 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P35** | 0.658 | 0.694 | 0.676 | 0.667 | 0.667 | 0.334 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P36** | 0.273 | 1.000 | 0.429 | 0.273 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P37** | 0.404 | 1.000 | 0.575 | 0.404 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P38** | 0.603 | 0.698 | 0.647 | 0.667 | 0.670 | 0.338 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P39** | 0.566 | 0.683 | 0.619 | 0.632 | 0.638 | 0.273 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P40** | 0.818 | 1.000 | 0.900 | 0.818 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P41** | 0.844 | 0.614 | 0.711 | 0.577 | 0.494 | -0.008 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P42** | 0.867 | 0.886 | 0.876 | 0.788 | 0.568 | 0.144 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P43** | 0.850 | 0.773 | 0.810 | 0.692 | 0.511 | 0.019 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P44** | 0.563 | 0.635 | 0.597 | 0.625 | 0.626 | 0.250 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P45** | 0.636 | 1.000 | 0.778 | 0.636 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P46** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P47** | 0.878 | 1.000 | 0.935 | 0.878 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P48** | 0.676 | 0.762 | 0.716 | 0.736 | 0.739 | 0.474 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P49** | 0.872 | 0.932 | 0.901 | 0.827 | 0.591 | 0.223 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P50** | 0.883 | 0.872 | 0.877 | 0.878 | 0.878 | 0.756 | evaluated (6条件; 条件別に表示) |
| **P51** | 0.769 | 1.000 | 0.870 | 0.769 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P52** | 0.880 | 0.936 | 0.907 | 0.904 | 0.904 | 0.809 | evaluated (6条件; 条件別に表示) |
| **P53** | 0.640 | 0.615 | 0.627 | 0.635 | 0.635 | 0.269 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P54** | 0.583 | 0.538 | 0.560 | 0.577 | 0.577 | 0.154 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P55** | 0.423 | 0.423 | 0.423 | 0.423 | 0.423 | -0.154 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P56** | 0.714 | 0.769 | 0.741 | 0.731 | 0.731 | 0.463 | evaluated (6条件; 条件別に表示) |
| **P57** | 0.615 | 0.615 | 0.615 | 0.615 | 0.615 | 0.231 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P58** | 0.538 | 0.538 | 0.538 | 0.538 | 0.538 | 0.077 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P59** | 0.538 | 0.538 | 0.538 | 0.538 | 0.538 | 0.077 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P60** | 0.750 | 0.284 | 0.412 | 0.615 | 0.599 | 0.258 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P61** | 0.154 | 1.000 | 0.267 | 0.154 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P62** | 1.000 | 0.222 | 0.364 | 0.611 | 0.611 | 0.354 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P63** | 1.000 | 0.117 | 0.209 | 0.598 | 0.558 | 0.259 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P64** | 0.846 | 0.282 | 0.423 | 0.615 | 0.615 | 0.310 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P65** | 0.765 | 0.197 | 0.313 | 0.601 | 0.573 | 0.223 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P66** | 0.577 | 0.577 | 0.577 | 0.577 | 0.577 | 0.154 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P67** | 0.577 | 0.577 | 0.577 | 0.577 | 0.577 | 0.154 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P68** | 0.615 | 0.615 | 0.615 | 0.615 | 0.615 | 0.231 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P69** | 0.538 | 1.000 | 0.700 | 0.538 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P70** | 0.308 | 1.000 | 0.471 | 0.308 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P71** | 0.308 | 1.000 | 0.471 | 0.308 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P72** | 0.544 | 0.403 | 0.463 | 0.538 | 0.537 | 0.076 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P73** | 0.719 | 0.547 | 0.621 | 0.679 | 0.675 | 0.362 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P74** | 0.462 | 1.000 | 0.632 | 0.462 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P75** | 0.308 | 1.000 | 0.471 | 0.308 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P76** | 0.417 | 1.000 | 0.588 | 0.417 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P77** | 0.500 | 1.000 | 0.667 | 0.500 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P78** | 0.875 | 1.000 | 0.933 | 0.875 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P79** | 0.658 | 0.634 | 0.646 | 0.635 | 0.635 | 0.269 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P80** | 0.500 | 1.000 | 0.667 | 0.500 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P81** | 0.556 | 0.467 | 0.507 | 0.528 | 0.530 | 0.061 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P82** | 0.492 | 0.425 | 0.456 | 0.486 | 0.487 | -0.026 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P83** | 0.635 | 0.412 | 0.500 | 0.577 | 0.581 | 0.172 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P84** | 0.513 | 0.500 | 0.506 | 0.500 | 0.500 | 0.000 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P85** | 0.923 | 1.000 | 0.960 | 0.923 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P86** | 0.846 | 1.000 | 0.917 | 0.846 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P87** | 0.462 | 1.000 | 0.632 | 0.462 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P88** | 0.538 | 1.000 | 0.700 | 0.538 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P89** | 0.167 | 1.000 | 0.286 | 0.167 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P90** | 0.258 | 1.000 | 0.410 | 0.258 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P91** | 0.462 | 0.456 | 0.459 | 0.455 | 0.455 | -0.090 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P92** | 0.487 | 0.535 | 0.510 | 0.532 | 0.532 | 0.064 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P93** | 0.687 | 0.722 | 0.704 | 0.692 | 0.692 | 0.385 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P94** | 0.581 | 0.704 | 0.637 | 0.635 | 0.640 | 0.281 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P95** | 0.806 | 0.962 | 0.877 | 0.865 | 0.865 | 0.745 | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P96** | 0.986 | 0.872 | 0.925 | 0.929 | 0.929 | 0.865 | evaluated (6条件; 条件別に表示) |
| **P97** | 0.667 | 1.000 | 0.800 | 0.667 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P98** | 0.788 | 1.000 | 0.881 | 0.788 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P99** | 0.308 | 1.000 | 0.471 | 0.308 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P100** | 0.500 | 1.000 | 0.667 | 0.500 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P101** | 0.530 | 1.000 | 0.693 | 0.530 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P102** | 0.667 | 1.000 | 0.800 | 0.667 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P103** | 0.379 | 1.000 | 0.549 | 0.379 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P104** | 1.000 | 1.000 | 1.000 | 1.000 | None | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P105** | 0.776 | 1.000 | 0.874 | 0.776 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P106** | 0.769 | 1.000 | 0.870 | 0.769 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P107** | 0.524 | 1.000 | 0.688 | 0.524 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P108** | 0.308 | 1.000 | 0.471 | 0.308 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P109** | 0.490 | 1.000 | 0.657 | 0.490 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P110** | 0.692 | 1.000 | 0.818 | 0.692 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P111** | 0.531 | 1.000 | 0.694 | 0.531 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P112** | 0.083 | 1.000 | 0.154 | 0.083 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P113** | 0.288 | 1.000 | 0.447 | 0.288 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |
| **P114** | 0.087 | 1.000 | 0.160 | 0.087 | 0.500 | None | None (synthetic_inputs_or_identity_adapter_unavailable) |

### P1 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.236 [0.176, 0.361] | 0.284 [0.211, 0.435] | -0.647 [-0.796, -0.340] | 0.141 | False |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.832 [0.832, 0.832] | 1.000 [1.000, 1.000] | 0.814 [0.814, 0.814] | 0.000 | False |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 1.000 [1.000, 1.000] | 0.667 [0.667, 0.667] | 0.707 [0.707, 0.707] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.707 [-0.707, -0.707] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | 0.000 [0.000, 0.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 1.000 [1.000, 1.000] | 0.667 [0.667, 0.667] | 0.707 [0.707, 0.707] | 0.000 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.707 [-0.707, -0.707] | 0.000 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | 0.000 [0.000, 0.000] | None [None, None] | None | None |

### P2 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.171 [0.109, 0.332] | 0.173 [0.110, 0.336] | -0.667 [-0.792, -0.339] | 0.137 | False |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.935 [0.935, 0.953] | 0.946 [0.946, 0.964] | 0.881 [0.881, 0.917] | 0.017 | False |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -1.000 [-1.000, -1.000] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.500 [0.500, 0.500] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -1.000 [-1.000, -1.000] | 0.000 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.500 [0.500, 0.500] | 1.000 [1.000, 1.000] | None [None, None] | None | None |

### P3 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.184 [0.110, 0.355] | 0.125 [0.074, 0.241] | -0.453 [-0.559, -0.207] | 0.106 | False |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.895 [0.868, 0.912] | 0.607 [0.589, 0.619] | 0.566 [0.528, 0.591] | 0.019 | False |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 1.000 [1.000, 1.000] | 0.667 [0.667, 0.667] | 0.707 [0.707, 0.707] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.707 [-0.707, -0.707] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.500 [0.500, 0.500] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 1.000 [1.000, 1.000] | 0.667 [0.667, 0.667] | 0.707 [0.707, 0.707] | 0.000 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.707 [-0.707, -0.707] | 0.000 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.500 [0.500, 0.500] | 1.000 [1.000, 1.000] | None [None, None] | None | None |

### P4 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.158 [0.079, 0.377] | 0.107 [0.054, 0.256] | -0.490 [-0.603, -0.176] | 0.134 | False |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.868 [0.851, 0.899] | 0.589 [0.577, 0.610] | 0.528 [0.503, 0.572] | 0.021 | False |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 1.000 [1.000, 1.000] | 0.667 [0.667, 0.667] | 0.707 [0.707, 0.707] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.707 [-0.707, -0.707] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.500 [0.500, 0.500] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 1.000 [1.000, 1.000] | 0.667 [0.667, 0.667] | 0.707 [0.707, 0.707] | 0.000 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.707 [-0.707, -0.707] | 0.000 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.500 [0.500, 0.500] | 1.000 [1.000, 1.000] | None [None, None] | None | None |

### P5 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.343 [0.204, 0.389] | 0.220 [0.131, 0.250] | -0.217 [-0.408, -0.153] | 0.088 | False |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.657 [0.657, 0.685] | 0.423 [0.423, 0.440] | 0.217 [0.217, 0.255] | 0.019 | False |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | 0.000 [0.000, 0.000] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | 0.000 [0.000, 0.000] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | 0.000 [0.000, 0.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | 0.000 [0.000, 0.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | 0.000 [0.000, 0.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | 0.000 [0.000, 0.000] | None [None, None] | None | None |

### P6 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.177 [0.168, 0.190] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.226 [0.223, 0.232] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.554 [0.554, 0.554] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.333 [0.333, 0.333] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.167 [0.167, 0.167] | 1.000 [1.000, 1.000] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.333 [0.333, 0.333] | 1.000 [1.000, 1.000] | None [None, None] | None | None |

### P15 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.159 [0.045, 0.500] | 0.097 [0.030, 0.256] | -0.871 [-0.962, -0.610] | 0.122 | False |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.841 [0.773, 0.841] | 1.000 [1.000, 1.000] | 0.871 [0.817, 0.871] | 0.026 | False |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |

### P16 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.992 [0.985, 1.000] | 0.924 [0.756, 0.985] | 0.885 [0.587, 0.961] | 0.133 | False |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.905 [-0.905, -0.850] | 0.027 | False |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |

### P18 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"dataset": "skill-budget", "loss": 0.0, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.131 [0.024, 0.500] | 0.717 [0.500, 0.955] | -0.379 [-0.647, 0.000] | 0.235 | False |
| `{"dataset": "skill-budget", "loss": 0.4, "years": [2023, 2024, 2025, 2026]}` | 10 | 0.881 [0.810, 0.881] | 1.000 [1.000, 1.000] | 0.502 [0.402, 0.502] | 0.049 | False |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | None [None, None] | None [None, None] | None [None, None] | None | None |

### P50 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.912 [0.912, 0.912] | 0.738 [0.738, 0.738] | 0.679 [0.679, 0.679] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.173 [0.173, 0.173] | 0.155 [0.155, 0.155] | -0.587 [-0.587, -0.587] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.805 [0.805, 0.805] | 0.786 [0.786, 0.786] | 0.595 [0.595, 0.595] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.969 [0.930, 0.972] | 0.786 [0.750, 0.821] | 0.746 [0.735, 0.807] | 0.032 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.284 [0.237, 0.296] | 0.274 [0.226, 0.286] | -0.417 [-0.501, -0.393] | 0.046 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.910 [0.906, 0.929] | 0.940 [0.917, 0.964] | 0.869 [0.821, 0.871] | 0.023 | False |

### P52 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.688 [0.688, 0.688] | 0.762 [0.762, 0.762] | 0.419 [0.419, 0.419] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.521 [0.521, 0.521] | 0.738 [0.738, 0.738] | 0.065 [0.065, 0.065] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.948 [0.948, 0.948] | 0.869 [0.869, 0.869] | 0.824 [0.824, 0.824] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.865 [0.830, 0.868] | 0.929 [0.917, 0.940] | 0.775 [0.743, 0.800] | 0.023 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.600 [0.598, 0.647] | 0.750 [0.726, 0.786] | 0.258 [0.244, 0.366] | 0.054 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.988 [0.976, 1.000] | 0.976 [0.952, 0.988] | 0.964 [0.929, 0.988] | 0.024 | False |

### P56 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.778 [0.778, 0.778] | 0.250 [0.250, 0.250] | 0.243 [0.243, 0.243] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.500 [0.500, 0.500] | 0.250 [0.250, 0.250] | 0.000 [0.000, 0.000] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.593 [0.593, 0.593] | 0.571 [0.571, 0.571] | 0.179 [0.179, 0.179] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.929 [0.909, 1.000] | 0.357 [0.250, 0.464] | 0.405 [0.378, 0.495] | 0.050 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.467 [0.333, 0.500] | 0.250 [0.179, 0.357] | -0.040 [-0.202, 0.000] | 0.087 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.758 [0.724, 0.793] | 0.821 [0.750, 0.893] | 0.608 [0.465, 0.617] | 0.070 | False |

### P96 の条件別seed感度

各指標は中央値 [最小, 最大]。seedが1個だけなら安定性を評価しない。

| 条件 | seed数 | Precision | Recall | MCC | MCC標準偏差 | MCC符号反転 |
|---|---|---|---|---|---|---|
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.175 [-0.175, -0.175] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 1.000 [1.000, 1.000] | 0.286 [0.286, 0.286] | 0.408 [0.408, 0.408] | None | None |
| `{"conversion": 0.5, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 1 | 1.000 [1.000, 1.000] | 0.976 [0.976, 0.976] | 0.976 [0.976, 0.976] | None | None |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "aligned", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 0.824 [0.803, 0.826] | 0.667 [0.631, 0.679] | 0.534 [0.488, 0.544] | 0.025 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "reversed", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 1.000 [1.000, 1.000] | 0.357 [0.345, 0.357] | 0.466 [0.457, 0.466] | 0.004 | False |
| `{"conversion": 1.0, "dataset": "annual-score-witness", "profile": "same_totals", "years": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}` | 3 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.000 | False |
