# 波の減衰 0 → ε: 2026年を足した結果（探索・暫定）

`../wave_eps_trial.py` と `../wave_eps_sensitivity.py` を、2013〜2025年に **2026年（確定した 858 試合）を足して** 走らせた結果です。2013〜2025年の 156 単位の結果は `../wave_eps_trial_results/` と `../wave_eps_sensitivity_results/` に残してあり、ここでは上書きしていません。確定済みの出力（`outputs/season.jsonl` など）は変更していません。**ε の値は暫定の置き場所で、結論には使いません。扱いは今後決めます。**

2026年は、ε を考えたときに使っていない年です（ε の挙動を 2013〜2025年で見たあとに入った年）。ただし単位は 12 しかなく、減衰 0 の単位は 1 つなので、「確かめられた」とは書きません。見たのは「2013〜2025年で見た挙動と違うことが起きたか」だけです。

## 入力と対照

- 試合の表: [games_table_from_observed.py](../games_table_from_observed.py) で保存済みの観測から作ったもの（2013〜2025年は `recovered-inputs/observed/games_raw.json`、2026年は `season-2026/observed/games.jsonl`）。11,886 試合、168 球団年。作った表の球団年ごとの G/W/L/T/RF/RA は、確定済みの値（2013〜2025年 `outputs/season.jsonl` の 156 球団年、2026年 `season-2026/derived/team_totals.jsonl` の 12 球団年）と全部一致する（一致しなければ作らずに止まる）。試合そのものはコミットしていません（`wave_*` の派生値と集計だけ）
- 試験の対照（今のコード vs 確定済み `season.jsonl`、`--new-seasons 2026`）: 168 単位、2013〜2025年の 156 単位は違う行 0。2026年の 12 単位は確定済みの行がなく対照の外（`new_seasons_with_committed_rows` 0、`new_seasons_without_units` なし）。`wave_eps_trial_gate.json`・`wave_eps_sensitivity_gate.json` はどちらも pass
- 2013〜2025年の 156 単位の行は、`../wave_eps_trial_results/wave_eps_rows_<ε>.jsonl` と、3 つの ε のすべてで行の中身まで同じ（2026年を足しても動かない）
- 注意: `wave_eps_rows_<ε>.jsonl` の `committed_*` 列は、2026年の行では**確定済みの値ではなく、ε を入れない今のコードの値**（確定済みの行がないため）。2013〜2025年の行では、対照が通っているので同じ

## 置いたファイル

- `wave_eps_rows_0.001.jsonl` / `wave_eps_rows_1e-06.jsonl` / `wave_eps_rows_1e-09.jsonl`: **2026年の 12 単位だけ**の行（2013〜2025年の行は上の `../wave_eps_trial_results/` にあり、同じもの）
- `wave_eps_trial.md` / `wave_eps_trial_gate.json`: 168 単位全体の試験の要約と対照の関門
- `wave_eps_sensitivity.md` / `.json` / `wave_eps_boundary_membership.jsonl` / `wave_eps_sensitivity_gate.json`: 168 単位全体の感度（ε の格子 9 通りと、線の始まり・終わりを動かした 8 通り）
- `wave_eps_settle_coefficients.md` / `.json`: 落ち着く位置を「係数 × 10^n」（ε = a × 10^-n）で書いた表。`../wave_eps_trial_results/` の 156 単位の行に 2026年の行を足した 168 単位から（`../wave_eps_settle_coefficients.py`）

## 結果（要点）

- 2026年の 12 単位のうち、ε なしで減衰が 0 の単位は **1 つ（ヤクルト、2026-s）**。全体で 23 → 24。ε = 1e-3, 1e-6, 1e-9 のどれでも ε の波が選ばれ、`wave_limit_rank` が 2.7645 / 2.7637 / 2.7637、`wave_settle_x` が 1.262×10^3 / 1.262×10^6 / 1.262×10^9。
- 落ち着く位置の「係数」（`wave_settle_x` / 10^n、a = 1）は 1.2625 / 1.2619 / 1.2619。最小の ε の係数から言い当てた位置の外れは、絶対 0.545・相対 4.3×10^-4 で、2013〜2025年の 23 単位の範囲（絶対で最大 0.64、相対で最大 0.7%）の中。係数の範囲（0.077〜1.764）も、振れ幅の範囲も、2026年を足して広がらなかった（このヤクルトの係数 1.262、振れ幅 1.766）。
- 2026年のほかの 11 単位は、ε なしで減衰が 1〜13 で、ε を入れても選ばれる式は変わらない。動いたのは前半だけの当てはめ（`wave_limit_rank_h1`）が空欄だったヤクルトと巨人の 2 単位で、ε を入れると値が出る（巨人 1.770、ヤクルト 2.643。どちらの ε でも同じ値の範囲）。`wave_osc_base` は 2026年では動かなかった。
- ε = 1e-3 で選ばれる式が乗り換わるのは、2026年を足しても 2024年のソフトバンクだけ（1e-6 と 1e-9 は乗り換えなし）。**その入れ替わりの仕組みは特定できていないまま**で、2026年は材料を足していない。
- 感度（`wave_eps_sensitivity.md`）: ε の格子の行は、単位が 12 増えたぶん数が変わるだけで、乗り換える単位は前と同じ（0.1 で 2019年の西武、0.03・0.001・1e-12 で 2024年のソフトバンク）。2026年の単位は、どの ε でも乗り換えない。線の始まり・終わりを動かした 8 本のうち、2026-s が境界に残るのは 4 本（8 本すべてで残るのは前と同じ 4 単位で、2026-s は入らない）。10 試合から・順位確定日までの線の「残った単位の収束先のずれ」の最大は 0.095 → 0.142 に上がった（2026年の単位が入ったため）。

## 注意

- この結果は**野球の順位の線だけ**での話です。ε が野球以外の連続データ（主食価格の月次）でも使えるかは、[research/epsilon-generality](../../../../research/epsilon-generality/results/README.md) で別に見ています（境界の単位の割合は野球の約 14% に対し約 36% など、違った点もある）
- 単位は 12、減衰 0 は 1 つ。ε の挙動について、2013〜2025年に見たこと（落ち着く位置が 1/ε に比例し、係数が ε によらない）と**矛盾する材料は 2026年にはなかった**、までしか言えない
- 再現: 試合の表を作る → 試験 → 感度 → 係数、の順
  ```sh
  python cycles/c001-chunichi/exploratory/games_table_from_observed.py \
      --games-raw cycles/c001-chunichi/recovered-inputs/observed/games_raw.json --season-jsonl cycles/c001-chunichi/outputs/season.jsonl \
      --season-2026 cycles/c001-chunichi/season-2026/observed/games.jsonl --totals-2026 cycles/c001-chunichi/season-2026/derived/team_totals.jsonl --out games.jsonl
  uv run --locked python cycles/c001-chunichi/exploratory/wave_eps_trial.py --games games.jsonl --config cycles/c001-chunichi/analysis.toml \
      --committed cycles/c001-chunichi/outputs/season.jsonl --new-seasons 2026 --eps 1e-3 1e-6 1e-9 --outdir out_trial --repo .
  uv run --locked python cycles/c001-chunichi/exploratory/wave_eps_sensitivity.py --games games.jsonl --config cycles/c001-chunichi/analysis.toml \
      --committed cycles/c001-chunichi/outputs/season.jsonl --new-seasons 2026 --outdir out_sens --repo .
  ```
  試験は約 2 分、感度は約 11 分かかります（`season_trajectory` をそれぞれ 4 回、25 回走らせるため）。`wave_eps_rows_*.jsonl`（2026年の行）から係数の表までは、[tests/test_c001_wave_eps_settle_coefficients.py](../../../../tests/test_c001_wave_eps_settle_coefficients.py) が保存済みの行だけでバイト単位で再現できることを確かめています。
