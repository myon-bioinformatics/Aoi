# SakAnalytics

> 数字は語る。だが、まだ語りきっていないことがある。

![SakAnalytics](../docs/images/sakanalytics.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

観測データセット（1試合1行: `key, date, home, away, hs, as`）から、チーム×シーズンの指標を作る。
測るだけで、除外や良し悪しの判断はしない（それは PythDRagoras と分析設定の仕事）。

チームの所属と表示名は分析設定の `[teams]` で明示的に与える。定義のないチームが現れたら、黙って捨てずにエラーにする。

主な列は `sakanalytics.py` の冒頭に一覧がある。順位（`rank`）は勝率から計算した派生値で、
公式の同率時の規定は再現しないため、同率には `rank_tie = true` の印をつける。

```bash
uv run python sakanalytics/sakanalytics.py --games data/observations/npb_calendar/games.jsonl \
  --config cycles/c001-chunichi/analysis.toml --out cycles/c001-chunichi/outputs/season.jsonl
```

## 優位・誤差と、研究から作った列（R32〜R34・R39）

どれも同じ年・同じリーグの他球団と比べた値で、1試合あたり。順位ではなく量で読むための列。
上の相手・下の相手は**最終順位**で決める（結果を知ったうえでの議論。[docs/propositions.md](../docs/propositions.md) の Groups Defined By The Final Outcome）。

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

## B に着く道筋の参考値（R45）

`path_offense`・`path_defense`・`path_convert`・`path_collapse`（当たるか）と、当たったものを `+` でつないだ `b_paths`（例 `offense+convert`、どれにも当たらなければ `none`）。**判定（命題の終了コード）には使わない参考値**で、規則はこれまでの研究で決めたものを固定して使う（値を見て変えない）。A の単位にも付く（道筋に当たりながら A に入った、と読む）。

| 道筋 | 規則 | 出どころ |
|---|---|---|
| `offense` 得点不足 | `rf_zone_se = −1`（得点の優位が誤差を超えてマイナス） | R35・R40 |
| `defense` 失点の劣り | `ra_zone_se = −1` | R40・R44 |
| `convert` 点の差を勝ちに変えられない | `wins_vs_pythag < −2` または `alloc_z_strat < −1` | R38・R44 |
| `collapse` 後半の崩れ | `course_fade ≥ 3` かつ `course_rf_d < 0` かつ `course_ra_d > 0` かつ `half2_vs_pythag < −2` | R43・R44 |

元の列が空なら、その道筋は空。どの道筋も判定できなければ `b_paths` は空。

どの列も「測る」だけで、良し悪しの判断はしない。どの研究でなぜ作ったかは `cycles/c001-chunichi/research/R31`〜`R39` にある。
