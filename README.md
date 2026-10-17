> **独立リポジトリ**: このリポジトリは [Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクト `pythdragoras/` から独立したものです。
> 親は Aoi（Aoi の親は myon-bioinformatics）。Aoi の `pythdragoras/` とは `git subtree` で同期します（下の「Aoi との同期」）。
> 以下の本文は Aoi の `pythdragoras/README.md` と同じで、`../docs/` や `cycles/` への相対リンクは Aoi のリポジトリの中を指します。

## このリポジトリで動かす

サイクルデータ（`cycles/`）、`scripts/`、SakAnalytics は Aoi に残します。コピーはせず、Aoi を固定 SHA で checkout して渡します。

```bash
git clone https://github.com/myon-bioinformatics/Aoi.git .test-deps/aoi
git -C .test-deps/aoi checkout 85243d6d1285e3bf4667e1447308543c7d648ab7   # docs/ci/ci.yml.proposed の AOI_SHA
AOI_ROOT=$PWD/.test-deps/aoi PYTHONPATH=$PWD/.test-deps/aoi/sakanalytics \
  uv run pytest -q --junitxml=reports/junit.xml
```

- パスは Aoi の規約（PR #49）（`--root` / `AOI_ROOT`、`--cycle` / `AOI_RESEARCH_CYCLE`、`aoi_layout.py`）で解決します。
- `AOI_ROOT` が Aoi を指していないと、pytest は最初に止まって理由を出します。
- 依存は polars と numpy だけです（ortools は使っていません）。

## vendor

`vendor.lock.json`（vendor-lock/1）で固定し、親 myon-bioinformatics の `vendor_sync.py`（`1eda992aa6fa31a902e2c06428e53ab17e8fe3c1`）で検証します。共有するのは標準モジュールだけの単一ファイルだけです。

| ファイル | 取得元 |
|---|---|
| `aoi_paths.py` | Aoi `aoi_paths.py` @ `85243d6d1285e3bf4667e1447308543c7d648ab7` |
| `vendor/Aoi-LICENSE` | Aoi `LICENSE` @ 同上 |

`aoi_paths.py` をリポジトリ直下に置くのは、`aoi_layout.bind()` が上のディレクトリへ向かって `aoi_paths.py` を探すためです。

```bash
python -S vendor_sync.py check --manifest vendor.lock.json
```

## Aoi との同期

Aoi 側（`pythdragoras/` が subtree）:

```bash
git subtree pull --prefix=pythdragoras https://github.com/myon-bioinformatics/PythDRagoras.git main --squash
git subtree push --prefix=pythdragoras https://github.com/myon-bioinformatics/PythDRagoras.git <branch>
```

- 履歴は Aoi `85243d6d1285e3bf4667e1447308543c7d648ab7`（main、#51 のマージコミット）の `pythdragoras/` から切り出しました（75 コミット、先頭 `12522c890e64313005e2bb3cad07d90365d4cf60`、tree は Aoi の `pythdragoras/` と同じ `873bd0d947a99da043e314cb11762189540c6b98`）。初回は `070dc6430e57f9912661ef88db826462e1bc76bb` からの 72 コミットを push し、そのあと fast-forward で 3 コミットを足しています。
- git 2.47.3 の `git subtree split --prefix=pythdragoras` は Aoi の 585 コミット中 506 で止まり、10/4 の古い先頭（25 コミット、7 ファイル）を返したため、`git filter-branch --subdirectory-filter pythdragoras` で切り出しています。
- Aoi に取り込まないファイル: `pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、`.github/`、`docs/ci/`（Aoi 側の設定と二重になるため）。

---

# PythDRagoras（実装）

> 本当にその説明で十分か？

![PythDRagoras](../docs/images/pythdragoras.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

思想は [docs/PythDRagoras.md](../docs/PythDRagoras.md)。ここはその検証部分の実装。

| 関数 | 中身 |
|---|---|
| `apply_exclusions` | 分析から除くシーズンを適用する。理由のない除外は受け付けず、何を・なぜ除いたかを結果に残す |
| `cumulative_test` | 期待勝率からのずれの累積を z 値にする（固定指数・可変指数の両方） |
| `rank_test` | 順位が下位に偏る珍しさ。帰無仮説（各シーズン独立に一様）と、全球団の実際の記録との比較を並べる |
| `summary_markdown` | 検証記録。原因は書かない。競合仮説の状態を並べる |
| `propositions.py` | 命題・判例・異議あり（仕様は [docs/propositions.md](../docs/propositions.md)） |
| `littlebit_approx.py` | 候補の 0/1 行列から潜在パターンを条件候補にする（探索。判定は `rule_search.py`） |

## 命題と「異議あり」

説明を「もし A ならば B」の命題として書き、元の命題・対偶・逆・裏の4つの形で判定する。
判定の基準は、結果を見る前に言葉で宣言する（必ず / ほとんど 0.90 / 概ね 0.75 / 多くの場合 0.50）。

```text
判定（上から順に最初に当てはまるもの）
  n < min_n                      → 判断保留
  必ず かつ 反例なし / あり        → 支持 / 棄却
  区間の下限 ≥ 基準                → 支持
  区間が基準をまたぐ              → 判断保留
  区間の上限 < 基準 かつ 関係あり   → 修正（主張が強すぎる）
  区間の上限 < 基準 かつ 関係なし   → 棄却
```

反例が1件でもあれば、判定が「支持」でも **異議あり** として判例を並べる。支持された説明の中の反例こそが、説明が足りなくなる場所だからである。
除外したシーズンの判例は、統計からは外しても「除外中の判例」として必ず表示する。

外部の主張（記事・レポート・他のAI）は、観測ではなく claim として登録し、パイプラインで再現できるかを確かめる。

## 潜在パターンを条件候補にする

`littlebit_approx.py` は、人が書いた候補条件のマスクを単位 × 条件の 0/1 行列にして、LittleBit 式（`littlebit_prune.littlebit`）で分解する。各潜在軸を「この単位はパターンに乗るか」という 1 本の条件にして `search` に渡す。成立と反例の数え方は `search` のビット演算のままである。目的の列は因子に渡さない。足した条件には `source=littlebit-approx`、rank、seed、元の条件と重み、`posthoc=true` を付ける。登録区分は `registration_audit.classify` に従い、この作り方では posthoc になる。

手順と、落とす軸・残差の手がかりの規則は [docs/littlebit-approx.md](docs/littlebit-approx.md)。c001 での並びは `cycles/c001-chunichi/outputs/exploratory/littlebit-approx/` に置く。確かめの記録は `confirmation.md` に置く。

帰無仮説は各シーズンを独立とみなすため、前年からの戦力の持ち越しを無視し、珍しさを過大に見積もる。
そのため、同じ期間の全球団との比較（経験的基準）を必ず並べる。

```bash
uv run python pythdragoras/pythdragoras.py --season cycles/c001-chunichi/outputs/season.jsonl \
  --config cycles/c001-chunichi/analysis.toml --hypotheses cycles/c001-chunichi/hypotheses.toml \
  --propositions cycles/c001-chunichi/propositions.toml --claims cycles/c001-chunichi/claims.toml \
  --outdir cycles/c001-chunichi/outputs
```

## 年単位から始める差分探索（season_sensitivity.py）

先に年成績の指標・重み・境界を動かし、変化と安定性を調べる。
有望な候補や説明の破れる年が見えてから、次節の試合単位へ進む。
このCLIは標準ライブラリだけで動作し、SciPyを必要としない。

```bash
python -S pythdragoras/season_sensitivity.py \
  --season cycles/c001-chunichi/outputs/season.jsonl \
  --additional-season cycles/c001-chunichi/references/season-2026-central-summary.jsonl \
  --config cycles/c001-chunichi/season_sensitivity.toml \
  --out cycles/c001-chunichi/outputs/season_sensitivity.json \
  --markdown cycles/c001-chunichi/outputs/season_sensitivity.md
```

`x + weight × y >= threshold` を設定し、片方を固定した感度曲線を計算する。
条件付き確率・MCC・基準との差、有限差分の傾き・変化・格子上の極値・最大値の区間・台形面積を出す。
閾値の移動では、境界を越えたチーム×年だけ混同行列の件数を更新する。
滑らかな関数の微分や極値を推定したとは扱わない。計算式と候補条件はTOMLに保存する。

年をまたいで同じ球団が含まれるため、独立標本の有意差検定は行わない。
1年の全球団を外して選び直す検証と、2026を選択から分離した照合を残す。
欠損した列・検証年・指標が外れるチーム×年も列挙し、中日の年次推移は欠年をつながない。
期待する6球団の不足、重複した球団×年、順位同率の未定義な扱いはエラーにする。
候補は探索的な関連であり、原因・CS出場確率・命題の支持を自動判定しない。

初回の結果・定義・読み方は [年単位の探索記録](../cycles/c001-chunichi/research/R27-season-sensitivity.md)、
年別表は [実測結果](../cycles/c001-chunichi/outputs/season_sensitivity.md)。
2026は既知の結果を含む回顧的照合であり、完全な盲検ではない。
通常の年表に2026を取り込んだ後は補助入力を外す。

## 次段階: 試合ごとの得失点変更（score_sensitivity.py）

NNUEの「変更箇所だけ更新する」考え方を参考に、試合の寄与を引いて新しい寄与を足す。
ニューラルネットや学習済み重みは使わない。対象は SakAnalytics と同じ試合原票。
RF・RA・W・L・T を差分更新し、派生値だけを再評価するため、各変更の更新量は試合数によらない。
探索全体は、対象試合数 × ステップ数 × 2軸に比例する。

```bash
uv run python pythdragoras/score_sensitivity.py \
  --games data/observations/npb_calendar/games.jsonl \
  --config cycles/c001-chunichi/analysis.toml \
  --max-step 3 --out cycles/c001-chunichi/outputs/score_sensitivity.json
```

`--team` で任意の設定済みチームを選べる。既定は `[focus].team`。

| 出力 | 意味 |
|---|---|
| `baseline` | 変更前の得失点、勝敗、勝率、指数1.83の期待勝率・期待勝利数 |
| `curve` | 各試合の得点を0〜3点増やす、または失点を0〜3点減らした結果。常に一方の軸だけ変更 |
| `delta` | 同じシーズンの基準値との差 |
| `timeline` | 日付・key順に1試合ずつ適用した途中経過、当該変更の差分、基準との差分 |
| `changed_runs` | 実際に変更した得失点の合計。失点は0で止める |
| `candidates` | 探索年の各試合1点改善で、変更1点あたりの勝ち越し増加が大きい順の命題候補 |

候補条件は既定で「探索年が3年以上あり、すべての探索年で勝ち越しが増加」。
`--min-seasons` で指定し、選択条件とともに結果に残す。2点・3点の結果を見て選択条件を変えない。
`[[exclude]]` は理由付きで適用し、`[confirm].seasons` は曲線を出すが候補の選択・順位には使わない。
候補は `propositions.toml` に自動登録しない。独立した年での検証と、人による命題の具体化が必要。

たとえば0対1の敗戦は、RFを1点増やすと引き分け、2点増やすと勝利となる。
増えた点数と勝利数の関係には段差があるため、期待勝率の滑らかな変化と実際の勝敗変化を両方残す。
全試合が引き分けなら勝率は未定義（null）、双方の総得点が0なら期待勝率もnullとする。

これは**最終スコアを変更する感度分析**であり、得点改善を実現する戦術・選手能力の因果効果ではない。
相手の同一試合の得失点も対になるが、全球団の順位は再計算しない。
イニング・延長・サヨナラ・その後の采配は再現せず、Aクラス確率も推定しない。
`timeline` は変更の適用順であり、将来の成績予測や実際のシーズン途中成績ではない。
入力範囲はユーザーが用意した原票そのもの。シーズン完結性は自動保証しないため、未完了年を含めるときは明示的に除外または検証用年に設定する。

検証: ランダムな80試合について、RF/RA両軸・4ステップの**各編集時点**を独立した全件再計算と照合。
引き分け、0失点、チームの向き、重複・不正原票、除外、検証用年からの選択漏洩、CLIも検証する。
