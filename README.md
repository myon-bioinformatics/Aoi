# SakAnalytics

> 数字は語る。だが、まだ語りきっていないことがある。

![SakAnalytics](https://github.com/myon-bioinformatics/Aoi/raw/main/docs/images/sakanalytics.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

## 概要

観測データセット（1試合1行: `key, date, home, away, hs, as`）から、チーム×シーズンの指標を作る。
測るだけで、除外や良し悪しの判断はしない（それは PythDRagoras と分析設定の仕事）。

チームの所属と表示名は分析設定の `[teams]` で明示的に与える。定義のないチームが現れたら、黙って捨てずにエラーにする。

主な列は `sakanalytics.py` の冒頭に一覧がある。順位（`rank`）は勝率から計算した派生値で、
公式の同率時の規定は再現しないため、同率には `rank_tie = true` の印をつける。

ほかに、残り試合・CS確率・優勝マジックの見通し（`season_simulator.py`、[SEASON_SIMULATOR.md](SEASON_SIMULATOR.md)）、年成績の照合（`annual_audit.py`）、架空リーグの生成（`synthetic_league.py`）がある。

[Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクト [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) から独立したリポジトリです（下の「Aoi との関係」）。

## インストールと使い方

Python 3.11 以上と [uv](https://docs.astral.sh/uv/) を使います。実行時の依存は polars だけです。ortools は任意で、`season-requirements.txt` を入れたときだけ exact の求解（`season_exact.py`）が動きます。

```bash
git clone https://github.com/myon-bioinformatics/SakAnalytics.git
cd SakAnalytics
uv sync
uv run python sakanalytics.py --help
uv run python sakanalytics.py --games <games.jsonl> --config <analysis.toml> --out <season.jsonl>
```

入力の `--games` は観測データセット（1試合1行: `key, date, home, away, hs, as`。[QueRyu](https://github.com/myon-bioinformatics/QueRyu) が作る形）、`--config` は `[teams]` を含む分析設定の TOML です。打撃・守備・得点表などの観測があれば、`--batting`・`--fielding`・`--linescore` で列を足します。

## 構成

| ファイル | 中身 |
|---|---|
| `sakanalytics.py` | CLI。チーム×シーズンの指標（主な列は冒頭に一覧） |
| `season_simulator.py`・`season_exact.py` | 残り試合の見通し（標準ライブラリ）と、任意の OR-Tools による確定判定（[SEASON_SIMULATOR.md](SEASON_SIMULATOR.md)・[SEASON_SIMULATOR_PLAN.md](SEASON_SIMULATOR_PLAN.md)） |
| `annual_audit.py` | 年間チーム表の照合（整数項目と公表桁） |
| `synthetic_league.py`・`league_laboratory.py` | 年成績を先に固定した架空リーグと、その実験 |
| `neighbors.py` | 結果を使わない記述的な近傍 |
| `proposition_seed_audit.py`・`synthetic_rule_discovery.py` | 命題の seed 感度と、架空データだけでの追跡（PythDRagoras を使う） |
| `aoi_layout.py` | 出力の証跡を固定した `proposition_seed_audit.py` の CLI だけが使う（下の「Aoi との関係」） |
| `tests/` | pytest |

## テスト

サイクルデータ（`cycles/`）と [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras)（`propositions`）は Aoi に残します。コピーはせず、Aoi を固定 SHA で checkout して渡します。

```bash
git clone https://github.com/myon-bioinformatics/Aoi.git .test-deps/aoi
git -C .test-deps/aoi checkout 0a1751a60ac64708d679f22950aa2b14cf688efd   # .github/workflows/ci.yml の AOI_SHA
AOI_ROOT=$PWD/.test-deps/aoi PYTHONPATH=$PWD/.test-deps/aoi/pythdragoras \
  uv run --locked pytest -q --junitxml=reports/junit.xml
```

- CLI は `--cycle-dir` などのパスを明示で受け取ります（`proposition_seed_audit.py` だけは下の理由で `aoi_layout.py` のまま）。テストは `AOI_ROOT` だけで Aoi を受け取り、データの場所は Aoi の `aoi_paths.py` に聞きます。
- `AOI_ROOT` が Aoi を指していない（`cycles/` がない）と、pytest は最初に止まって理由を出します。
- 実行時の依存は polars だけです。ortools は任意で、`season-requirements.txt` を入れたときだけ exact の求解が動き、無ければそのテストは skip します。
- テストは、これに加えて `AOI_ROOT` の Aoi を使います。
  - `cycles/` のサイクルデータ。
  - PythDRagoras の `propositions`: `proposition_seed_audit.py` と `synthetic_rule_discovery.py`（`PYTHONPATH` の `pythdragoras`）。
  - これ以外に Aoi の兄弟サブプロジェクトと `scripts/` を使わないことは、`tests/test_no_sibling_imports.py` で確かめます（`propositions` が既知の例外です）。

CI（`.github/workflows/ci.yml`）は Python 3.11–3.15 で同じことをします。

## Aoi との関係

このリポジトリは [Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクト [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) から独立したものです。
親は Aoi（Aoi の親は [myon-bioinformatics](https://github.com/myon-bioinformatics/myon-bioinformatics)）。Aoi の [`child-heads.json`](https://github.com/myon-bioinformatics/Aoi/blob/main/child-heads.json) に登録され、tree は登録した時点の Aoi の `sakanalytics/` と同じです（`.github/`、`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、この README も含む）。`git subtree` で同期します（下の「Aoi との同期」。手順の全体は Aoi の [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md)）。
この README は Aoi の `sakanalytics/README.md` と同じファイルから始まっています。Aoi の中の文書・データへのリンクは、どちらで読んでも開けるように GitHub の URL で書いています。

### aoi_layout.py

`aoi_paths.py` は Aoi 直下の 1 か所だけに置きます（このリポジトリには置きません）。`aoi_layout.py` は `proposition_seed_audit.py` の CLI が Aoi の `aoi_paths.py` を探すために残しています。このファイルは Aoi の `seed-evaluation.json`（`analysis_sha256`）でソースの SHA-256 を固定しているので、CLI を引数だけにする変更は、子の CI が読む Aoi の固定 SHA を上げるときにまとめて行います。

NPB 固有の前提（年間表の球団数・丸め方・対戦列、CS の規則のプリセット `npb_rules()`、2022 年の検証 `season_verify_2022.py`）は Aoi の `aoi_npb.py`・`scripts/` に置き、ここでは `AuditRules`・`Rules` として受け取ります。

### Aoi との同期

このリポジトリは Aoi の `sakanalytics/` の subtree です。除外するファイルはなく、Aoi の `sakanalytics/` の tree とこのリポジトリの tree は同じです。Aoi の中では `sakanalytics/.github/` は動かず（GitHub が読むのはリポジトリ直下の `.github/` だけ）、`sakanalytics/conftest.py` は Aoi の pytest でも同じように `AOI_ROOT` を確かめます。

- 履歴は Aoi `0a1751a60ac64708d679f22950aa2b14cf688efd`（main、#57 のマージコミット）の `sakanalytics/` から履歴を残して切り出しました（main `67c8781b0e606ab41f56f717c2a84efa67b98533`、切り出し時点の tree `a54fc414f1959f7619619c0ae9398ff2fe8fbcbb` は Aoi の `sakanalytics/` と同じ）。
- この履歴は Aoi の履歴とつながっていないので、Aoi に一度だけ join を入れます。`git-subtree-split:` にこのリポジトリの main のコミットを書いた squash コミット（tree はこのリポジトリと同じ）を、Aoi の tree を変えないマージの2つ目の親にします。join 以降は `git subtree` が join を起点にします。
- join は2つ目の親として残す必要があります。join を含む Aoi の PR は squash せず、merge commit で入れます（squash すると2つ目の親が消え、`git subtree pull` と `split` が止まります）。
- `git-subtree-split:` のコミットはこのリポジトリの main にある必要があります。このリポジトリの PR を squash マージして main の sha が変わったときは、Aoi で同じ tree の join を入れ直します。

子 → Aoi（Aoi の main から作ったブランチで）:

```bash
git subtree pull --prefix=sakanalytics https://github.com/myon-bioinformatics/SakAnalytics.git main --squash
test "$(git rev-parse HEAD:sakanalytics)" = "$(git rev-parse FETCH_HEAD^{tree})"   # Aoi 側に未同期の変更がないとき
```

Aoi → 子（Aoi の main で）:

```bash
git fetch https://github.com/myon-bioinformatics/SakAnalytics.git main   # split の起点のコミットを手元に置く
git subtree split --prefix=sakanalytics -b sync/sakanalytics
test "$(git rev-parse sync/sakanalytics^{tree})" = "$(git rev-parse HEAD:sakanalytics)"
git push https://github.com/myon-bioinformatics/SakAnalytics.git sync/sakanalytics:refs/heads/<新しいブランチ>
```

- push したブランチからこのリポジトリに PR を作ります。マージしたら、Aoi で「子 → Aoi」の pull をして、Aoi 側の起点をこのリポジトリの main に付け直します（squash マージでは split のコミットが main に残らないため）。
- Aoi の `scripts/check_child_heads.py --fail-on-diff` が、Aoi の `child-heads.json` に登録した sha の tree と Aoi の `sakanalytics/` を比べます。

## 関連サブプロジェクト

親の [Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクトは、それぞれ独立したリポジトリになっています。Aoi の中の場所（subtree）とあわせて載せます。一覧と登録の詳細は Aoi の [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md) です。

| リポジトリ | Aoi の中の場所 | 役割 |
|---|---|---|
| [BlueProbe](https://github.com/myon-bioinformatics/BlueProbe) | [`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe) | 観測と抽出（保存した HTML/CSS/DOM を読み、何があるかを記録する） |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | [`queryu/`](https://github.com/myon-bioinformatics/Aoi/tree/main/queryu) | 取得と観測データセットの作成（来歴つきのキャッシュ） |
| **SakAnalytics**（このリポジトリ） | [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) | 観測データからの指標と統計（チーム×シーズンの指標、残り試合の見通し） |
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | [`pythdragoras/`](https://github.com/myon-bioinformatics/Aoi/tree/main/pythdragoras) | 説明の検証（命題・反例・異議あり） |
| [NagoyAction](https://github.com/myon-bioinformatics/NagoyAction) | [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) | パイプラインの実行と自動化（同じ定義をローカルと GitHub Actions で） |
| [DRAgoWing](https://github.com/myon-bioinformatics/DRAgoWing) | [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) | 図とレポート（Plotly.js の HTML、四つの形の表） |

## ライセンス

MIT License（[LICENSE](LICENSE)）。Aoi の `LICENSE` と同じ内容です。

---

# 研究での使い方と列の詳細（中日・NPB）

以下は Aoi の研究サイクル（c001: 中日・NPB のデータ）での使い方と、研究から作った列の詳細です。コマンド例のパス（`sakanalytics/…`・`cycles/…`・`data/…`）は Aoi のルートからの場所です。

```bash
uv run python sakanalytics/sakanalytics.py --games data/observations/npb_calendar/games.jsonl \
  --config cycles/c001-chunichi/analysis.toml --out cycles/c001-chunichi/outputs/season.jsonl
```

## 優位・誤差と、研究から作った列（R32〜R34・R39）

どれも同じ年・同じリーグの他球団と比べた値で、1試合あたり。順位ではなく量で読むための列。
上の相手・下の相手は**最終順位**で決める（結果を知ったうえでの議論。[docs/propositions.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/propositions.md) の Groups Defined By The Final Outcome）。

| 列 | 中身 | 式 | 注意 |
|---|---|---|---|
| `rf_adv` | 得点の優位（プラスほど多く取った） | 得点／試合 − 他球団の得点／試合の平均 | `rf_def_total` と同じ量 |
| `ra_adv` | 失点の優位（プラスほど抑えた） | 他球団の失点／試合の平均 − 失点／試合 | |
| `run_balance` | 収支 | `rf_adv + ra_adv` | プラスなら、得点の不足を失点で補えた |
| `short_share` | 取り分（0〜1） | 不足 ÷（不足 + 優位）。不足 = max(0, −`rf_adv`)、優位 = `ra_adv` | 割る数が 0 の近くでも発散しない。打ち消せないなら 1、不足がなく優位が正なら 0、どちらもなければ空 |
| `rf_adv_z` / `ra_adv_z` | 優位 ÷ 全単位の優位の標準偏差 | | 物差しはチームの間の散らばり。年を足すと少し動く |
| `rf_zone` / `ra_zone` | 上の z の3区分 | z ≥ 1 → 1、z ≤ −1 → −1、その間 → 0 | R33 で広すぎた。誤差の区分（下）を優先 |
| `rf_sd_g` / `ra_sd_g` | 試合ごとの得点・失点の標準偏差 | | 試合ごとの値から作る（measure の段階） |
| `rf_adv_se` / `ra_adv_se` | 優位の誤差 | √（自分の sd² ÷ 試合数 + Σ 他球団の sd² ÷ 試合数 ÷ 他球団の数²） | 各チームの試合は独立とみなす |
| `rf_zone_se` / `ra_zone_se` | 誤差での3区分 | 優位 ≥ 誤差 → 1、≤ −誤差 → −1、その間 → 0 | 0 は「平均と区別できない」 |
| `rf_adv_t` / `ra_adv_t` | 優位が誤差の何倍か（連続値） | `rf_adv / rf_adv_se`、`ra_adv / ra_adv_se` | `*_zone_se` は \|t\| ≥ 1 で区切った同じ量 |
| `run_balance_t` | 収支が誤差の何倍か | `run_balance / √(rf_adv_se² + ra_adv_se²)` | 得点と失点の誤差は独立とみなす |
| `adv_shape_se` | 形（9通りの文字列） | `"<得点の区分>/<失点の区分>"`、それぞれ `-1`・`0`・`+1` | 例 `-1/+1` = 得点ははっきり足りず、失点ははっきり上回る |
| `bat_routes` | 打撃の経路の数（0〜2） | [`bat_d_bb_pa` ≥ 0] + [`bat_d_iso` ≥ 0] | 四死球／打席・ISO が他球団の平均以上なら1つ。どちらかが空なら空 |
| `vs_top_minus_lower` | 上の相手との勝率 − 下の相手との勝率 | `vs_top_wpct − vs_lower_wpct` | 上 = 最終順位の1・2位、下 = 4〜6位。最終順位で決めるので、A かどうかと算術でつながる面がある |

## A の線（R46・R50）

| 列 | 中身 | 式 | 注意 |
|---|---|---|---|
| `lg_lead_gap` / `lg_gap34` / `lg_rest_sd` | 1位 − 2位、3位 − 4位の勝率差、1位以外の勝率の標準偏差 | 勝率を高い順に並べた k 番目の値 | リーグごとの比較には使わない（ユーザーの方針） |
| `lg_line` | その年・そのリーグの A の線 | （3位の勝率 + 4位の勝率）÷ 2 | |
| `line_gap_pythag` | 点の差で見込む勝率の、A の線からの距離 | `pythag_fixed − lg_line` | 勝率 − A の線 = `line_gap_pythag` + `resid_fixed`（点の差より勝った分）の恒等式で分ける |
| `lg_rank_at_500` | 勝率 .500 が何位に当たるか（もう1つの線の引き方） | 勝率を高い順に並べ、.500 をはさむ2チームの間を直線でつないだ順位 | 3.5 より小さいほど .500 が上位寄り。全チームが .500 の片側なら空 |
| `lg_break_after` / `lg_break_gap` | 勝率のいちばん大きな隙間（データが自然に割れる所）が「k 位と k+1 位の間」の k と、その差 | 勝率を高い順に並べた隣どうしの差の最大 | 人が決めた区切りを使わない線。差が同じなら上位側 |
| `lg_tier` / `lg_tier_of_3rd` | 大きい隙間2つで分けた3つの塊（上から 1・2・3）のうち、自分の塊と3位の塊 | 隣どうしの差の大きい順に2つの切れ目 | 3位と同じ塊なら、A の線の下でも3位と勝率の近いまとまりにいた |
| `lg_bar` | 越えるべき高さ（R56） | 同じ年・同じリーグのほかの球団の勝率を高い順に並べた（球団数 ÷ 2）番目（6球団なら3番目） | ほかの球団だけで決まる外の高さ。勝率がこれを上回れば上位半分（同率は除く）。勝率 − lg_bar の符号は A・B と算術で一致する |
| `lg_bar_pythag` / `pbar_gap` | 点の差から見たその年の越えるべき高さ（R73） | ほかの球団の点の差で見込む勝率（`pythag_fixed`）を高い順に並べた（球団数 ÷ 2）番目。`pbar_gap` = 自分の点の差で見込む勝率 − それ | 固定の .500 と比べない（独走の1位がいる年と拮抗した年で高さが変わる）。マイナスなら点の差どおりでは届かない |
| `mix_lo` / `mix_hi` / `mix_zone` | A と B が混ざる帯（R53）と、自分がその下・中・上のどこか（−1・0・+1） | 自分の年を除いたほかの年（設定の `[[exclude]]` の年も除く）の全単位で、A の勝率の最低（mix_lo）と B の勝率の最高（mix_hi） | 1年抜きなので、その年のデータで線を決めていない。リーグはまとめる。端ちょうどは中（0）。ほかの年に A か B がなければ空 |
| `live_mix_lo` / `live_mix_hi` / `live_mix_zone` | 同じ帯を、A・B に効く試合だけの勝率（`live_wpct`）で引いたもの（R58） | `add_mix_zone(col="live_wpct", prefix="live_mix")` | 効かない試合（決まった後）を外した帯 |
| `rf_mix_*` / `bal_mix_*` / `vsl_mix_*` / `sim_mix_*`（`_lo`・`_hi`・`_zone`） | 同じ帯を、得点の優位（`rf_adv`）・収支（`run_balance`）・下の相手との勝率（`vs_lower_wpct`）・分布から見た A の確率（`sim_p_upper`、R67）の値で引いたもの（R66） | `add_mix_zone(col=..., prefix=...)`、1年抜き | 順位ではなく指標の値の線。−1 はほかの年のどの A よりも悪い値 |
| `rf_adv_bgap` / `run_balance_bgap` / `vs_lower_wpct_bgap` と `rfg_mix_*` / `balg_mix_*` / `vslg_mix_*` | 指標の、その年の高さ（ほかの球団の上位半分の最後の値）からの差と、その差で引いた帯（R74） | `add_bar_gaps` → `add_mix_zone` | 固定の 0・.500 と比べない。独走・拮抗の年の違いを持つ |
| `rf_state2` / `ra_state2` | 得点の優位・失点の優位の2本線の状態（`A`・`AB`・`B`、R67） | 同じ年・同じリーグの値を大きい順に並べ、2番目と3番目の真ん中・4番目と5番目の真ん中で分ける（`add_state2`） | 順位ではなく値の線。値のない球団があるリーグ年は空 |
| `fld_fpct` / `fld_e_g` / `fld_dp_g` / `fld_pb_g` / `fld_a_po` と `fld_d_*` | チーム守備成績の率（`--fielding`）: 守備率・失策/試合・併殺/試合・捕逸/試合・補殺/刺殺と、同じ年・同じリーグの他球団の平均との差 | `fielding_join`。試合数・守備機会・守備率の照合が合わなければ止まる | `fld_d_e_g` がマイナスなら、他球団より失策が少ない。原票の数は出さない |
| `ls_cov` / `ls_e_g` / `ls_opp_e_g` / `ls_e_net_g` / `ls_e_net_close` / `ls_e_net_win` / `ls_e_net_loss` / `ls_e_net_q4` | 試合ごとの得点表（`--linescore`）からの失策: 得点表のある試合の割合、自分・相手の失策／試合、（自分 − 相手）／試合を全試合・1点差・勝ち・負け・最後の区間で | `linescore_join`。日付とチームで結び、R が日程の得点と合わなければ止まる | 取得した年だけ埋まる（`ls_cov` = 0 の年は空）。マイナスなら相手より失策が少ない |
| `rank_fixed_x` / `rank_fixed_left` / `rank_fixed` | 最終順位が数の上で確かになった日の位置（0 = 開幕、1 = 最終日）・その日の残り試合・その順位（R57） | 各日の終わりに残りを全勝・全敗としたときの勝率の上限・下限から、ありうる最高と最低の順位が一致した日 | 直接対決を考えないので控えめ（遅く出ることはあっても早くは出ない）。最後まで同率なら空 |
| `live_g` / `live_wpct` / `live_rd_g` | A・B に効く試合（自分の入る・入れないが決まった日まで、その日を含む）の試合数・勝率・1試合あたりの点の差（R57） | `clinch_in_x` か `clinch_out_x` の日で区切る。決まらなければ全試合 | 区切りは R26 と同じ控えめな日付 |
| `dead_g` / `dead_wpct` / `dead_rd_g` | 決まった日より後の試合（A・B には効かない試合） | 同上の残り | なければ `dead_g` = 0、ほかは空 |
| `h2_live_g` / `h2_live_wpct` | 後半（自分の試合の後ろ半分）のうち、A・B に効く試合の数と勝率（R63） | 境は 試合数 ÷ 2 の切り捨て。効く試合は `live_*` と同じ区切り | 後半の下がりが決まった後の試合で起きたのかを分ける |
| `h1_rd_g` / `h1_wl_vs_upper` / `h1_wl_vs_lower` と `h2_live_*` の同じもの | 前半（全試合）と後半の効く試合だけの、1試合あたりの点の差、同じリーグの上位半分・下位半分の相手との勝 − 敗（R64） | 上位・下位は最終の勝率（同率は上位側） | 交流戦の相手は数えない |
| `lock_g` / `lock_x` | 順位表で、自分の側（上位半分か否か）が最後と同じになり、その後変わらなくなった日の消化試合数（N）と日付の位置（R60） | 各日の終わりの勝率の並び。勝率で自分より上の球団の数 + 1 ≤ 球団数 ÷ 2 なら上の側（同率は上位側） | 数の上の確定（`clinch_*`）ではなく、実際の順位表が落ち着いた時点 |
| `lg_set_lock_x` | そのリーグの上位半分の顔ぶれが最後と同じになり、その後変わらなくなった日の位置（R60） | 同上 | リーグで1つの値 |
| `q_wl_1`〜`q_wl_4` / `lone_down_n` | 自分の試合を消化順に4つに分けた区間の勝 − 敗と、そのリーグで自分だけが負け越した区間の数（R60） | 境は 試合数 × q ÷ 4 の切り捨て | 「ある期間に自分だけが減っていた」の記録。それ自体に意味は求めず、命題の材料にする |
| `pre_lock_wpct` / `post_lock_g` / `post_lock_wpct` | 順位表で最後の側に落ち着いた日まで（含む）の勝率と、その後の試合数・勝率（R61） | `lock_g` で区切る | 落ち着いた後も同じ向きで戦ったか、五分に戻したか |
| `q4_g` / `q4_rd_g` / `q4_one_run_net` / `q4_wl_vs_upper` / `q4_wl_vs_lower` | 4つ目の区間（自分の試合の最後の 1/4、境は 試合数 × 3 ÷ 4 の切り捨て）の試合数・1試合あたりの点の差・1点差の勝 − 敗・同じリーグの上位半分／下位半分の相手との勝 − 敗（R62） | 上位・下位は最終順位で決める（前提） | 交流戦の相手は上下どちらにも数えない |

## B に着く道筋の参考値（R45）

`path_offense`・`path_defense`・`path_convert`・`path_collapse`（当たるか）と、当たったものを `+` でつないだ `b_paths`（例 `offense+convert`、どれにも当たらなければ `none`）。**判定（命題の終了コード）には使わない参考値**で、規則はこれまでの研究で決めたものを固定して使う（値を見て変えない）。A の単位にも付く（道筋に当たりながら A に入った、と読む）。

| 道筋 | 規則 | 出どころ |
|---|---|---|
| `offense` 得点不足 | `rf_zone_se = −1`（得点の優位が誤差を超えてマイナス） | R35・R40 |
| `defense` 失点の劣り | `ra_zone_se = −1` | R40・R44 |
| `convert` 点の差を勝ちに変えられない | `wins_vs_pythag < −2` または `alloc_z_strat < −1` | R38・R44 |
| `collapse` 後半の崩れ | `course_fade ≥ 3` かつ `course_rf_d < 0` かつ `course_ra_d > 0` かつ `half2_vs_pythag < −2` | R43・R44 |

元の列が空なら、その道筋は空。どの道筋も判定できなければ `b_paths` は空。

どの列も「測る」だけで、良し悪しの判断はしない。どの研究でなぜ作ったかは `cycles/c001-chunichi/from-cycle-001/research/` の `R31`〜`R39`・`R45` にある（cycle-001/chunichi の branch 側の研究。正本の `research/` とは番号が別）。

## 年間チーム表と架空リーグ

`annual_audit.py` は公式の年成績から、整数項目・率の公表桁・表間の共通列・既存年表との一致を照合する。
`synthetic_league.py` は、リーグ全体の年成績を先に固定し、対戦容量を整数最大流で確認してから試合結果へ展開する。
主対象は2013〜2026年。既定は3条件×各1組の14年間で、全14年の年成績と試合集計が一致すれば合格とする。
過去年の網羅や生成件数の増加は要求しない。2013年以前は通常の解析・較正・合格判定から分けて参考保管する。
得失点が同じでも勝敗配分の違う例を作れる。生成例は実測件数に加算しない。
手順・生成族・完了条件は [c001の取得・架空検証記録](https://github.com/myon-bioinformatics/Aoi/blob/main/cycles/c001-chunichi/annual-history-synthetic.md)。

## 条件付き生成・能力予算・得点尺度の実験

`league_laboratory.py` は、得失点を固定して隠した勝敗を補完する実験、同じポイント予算で能力を配分する実験、
同じ整数スコアを6種類の分析単位で測る実験を実行する。年成績で先に検査し、代表例だけ試合へ展開する。
生成不能例・推奨条件の通過/不通過・修正/新規FP/FN・尺度間の順位変化を残し、次の命題の材料にする。

```bash
python -S sakanalytics/league_laboratory.py
```

設定は [league-laboratory.toml](https://github.com/myon-bioinformatics/Aoi/blob/main/cycles/c001-chunichi/league-laboratory.toml)、
観測と解釈は [R29](https://github.com/myon-bioinformatics/Aoi/blob/main/cycles/c001-chunichi/research/R29-league-laboratory.md)。
架空モデルの仮定下の探索で、既存命題・合格条件・実測スコアは変更しない。

## 全命題の共通評価軸とseed感度

PythDRagorasは全命題・評価した各形にPrecision / Recall / F1 / Accuracy /
Balanced Accuracy / MCCを付ける。分母0・定数予測などは`None`と理由を残し、正式判定には使わない。
合成入力がない命題もseed評価の項目を持ち、未評価は`None`。特定の再評価候補だけに限定しない。

```bash
python sakanalytics/proposition_seed_audit.py
# 年成績の証跡も同じ条件で作り直す場合だけ:
python sakanalytics/proposition_seed_audit.py --generate-plans
```

既存の年成績合成3系列と、能力予算のseed 0〜9・2023〜2026年・全28配分・減衰0/0.4を使う。
証跡は`cycles/c001-chunichi/outputs/exploratory/proposition-evaluation/`。
通常のc001 pipelineも`--seed-evaluation`で診断を読み、`outputs/index.md`へ全命題を並べる。
年・命題定義・生成条件が同じ群内だけでseedの振れを測り、条件変更の効果とは分ける。
合成入力は13命題に対応し、必要な列や実在球団への対応付けがない命題は未評価のままにする。
