# イニング指標辞書

`inning_features.py` が生成する64数値項目。独立した64仮説という意味ではなく、分子・分母・相補的な率を含む。

共通キー：`year`、`team`、`league`、`venue`（その球団がhome/away、またはall）、`role`（off=攻撃、def=相手の攻撃）、`window`（all=全実施回、first6=双方が6回まで実施した試合の1–6回）。defのhomeも「その球団がホーム」で、打っている相手はビジター。交流戦を含む。

G=対象試合数、I=実施した自軍攻撃回数（defでは相手）、R=総得点、S=得点回数。得点した試合数をG+とする。率は0–1、回数・点数は数値。CSV空欄は分母0による未定義で、0とは区別する。

| 列 | 定義・分母 |
| --- | --- |
| games, innings, runs, scoring_innings | G, I, R, S |
| innings_per_game, runs_per_game, runs_per_inning | I/G, R/G, R/I |
| score_rate, zero_rate | S/I, (I−S)/I |
| single_run_inning_rate, two_run_inning_rate, big_inning_rate | 1点、2点、3点以上の回数/I |
| runs_per_scoring_inning | R/S |
| single_share_scoring | 1点の回数/S |
| extra_runs_per_game | (R−S)/G。得点回の最初の1点を除く得点/試合 |
| scoring_innings_per_game | S/G |
| scoring_innings_variance | 試合ごとの得点回数の母分散（Gで割る） |
| zero_scoring_game_rate, one_scoring_game_rate | 得点回が0回、1回の試合数/G |
| multi_scoring_game_rate, threeplus_scoring_game_rate | 得点回が2回以上、3回以上の試合数/G |
| scored_games | G+ |
| one_scoring_given_scored | 得点回が1回の試合数/G+ |
| mean_max_zero_run | 各試合の最長連続無得点回数の平均 |
| mean_max_scoring_run | 各試合の最長連続得点回数の平均 |
| mean_leading_zeros, mean_trailing_zeros | 最初の得点まで、最後の得点後の無得点回数の平均。無得点試合は全実施回数 |
| mean_scoring_clusters | 各試合の連続得点区間数の平均（例：0,1,1,0,2なら2区間） |
| mean_max_inning_runs | 各試合で最も得点した回の得点の平均 |
| zero_run_ge6_game_rate | 6回以上連続無得点があった試合数/G |
| consecutive_scoring_game_rate | 2回以上連続得点した試合数/G |
| mean_first_scoring_inning_given_scored, mean_last_scoring_inning_given_scored | 最初、最後に得点した回の番号の平均（G+のみ） |
| mean_max_inning_share_given_scored | 各得点試合の最大回得点/試合得点を平均 |
| mean_inning_run_hhi_given_scored | 各得点試合のΣ(各回得点/試合得点)²を平均。大きいほど少数回への集中 |
| transition_from_0_n, transition_from_1_n | 次の自軍攻撃回が実施された無得点回、得点回の数。試合末尾を除く |
| transition_00_n, transition_01_n, transition_10_n, transition_11_n | 隣接する自軍攻撃回の無得点/得点の組合せ数。相手の攻撃を間に挟む |
| transition_00_rate, transition_01_rate | 上記00,01 / transition_from_0_n |
| transition_10_rate, transition_11_rate | 上記10,11 / transition_from_1_n |
| first3_eligible_games, first6_eligible_games | 少なくとも自軍攻撃が3回、6回実施された試合数 |
| first3_scoreless_rate, first6_scoreless_rate | 対応する先頭3回、6回がすべて0の試合数 / eligible_games |
| early_innings, middle_innings, late_innings, extra_innings | 1–3回、4–6回、7–9回、10回以降の実施回数 |
| early_score_rate, middle_score_rate, late_score_rate, extra_score_rate | 対応する時間帯の得点回数/実施回数 |
| early_runs_per_inning, middle_runs_per_inning, late_runs_per_inning, extra_runs_per_inning | 対応する時間帯の得点/実施回数 |
| zero_games_uniform_expected | 下記参照モデルでの無得点試合数の期待値 |
| zero_game_rate_uniform_expected | 同期待値/G |
| zero_game_rate_excess_uniform | 観測無得点試合率−参照期待率 |

## 集中の参照モデル

同じ年・球団・home/away・攻守・windowのI枠に、S個の得点印を一様に配置する。n回実施した試合が無得点になる確率は `C(I−S,n)/C(I,n)`。実際には巨大な組合せを作らず積で計算する。各試合のこの確率の合計が期待無得点試合数となる。allではhome/away別の期待数を足してからGで割る。

得点印の交換可能性を仮定した参照であり、日々の投手・打者・相手・天候・イニング・試合展開の差は保存しない。標準誤差やp値は計算していない。差が小さくても全てランダムとは言えず、差が大きくても戦略・能力・運とは確定しない。回別得点の大きさの集中を測るHHIとは別の量。

## 集約と比較

- `team_year_metrics.csv.gz`：156球団年×3主催区分×2攻守×2window=1,872行。各行は総数から計算。
- `group_summary.csv`：上記の球団年単純平均。chunichi、other_cl（中日以外のセ5球団）、cl、npb。all/without2020、3主催区分、2攻守、2window。カウント列も「平均の球団年のカウント」であり合計ではない。未定義値は平均対象外。全て未定義なら空欄。
- `chunichi_peer_differences.csv.gz`：同年・主催区分・攻守・windowごとに中日−他セ5球団平均。各指標の有効比較先数peer_nも保存。比較先を見て指標を削除しない。
- ローカルの`data/observations/r001_inning_features/team_game_features.csv`：44,112行の試合×球団×攻守派生特徴、URL付き。生イニング配列は再掲しない。共有ZIPから再生成可能。

多くの指標は得点頻度・実施回数・得点総数と機械的に連動する。無得点連続やHHI単独から「つながりの能力」を測ったと解釈しない。サヨナラ回の途中終了はCSVで区別できず、実施した1回として数える。試合間の連続無得点記録は今回扱わない。
