# DRAgoWing

> Lay down the record without re-judging it.
>
> Renders baseball research records as Plotly.js HTML reports, proposition tables and optional headless-Chrome PNG/SVG exports without Python plotting libraries. Split out from Aoi's dragowing/ (git subtree).

![DRAgoWing](https://github.com/myon-bioinformatics/Aoi/raw/main/docs/images/dragowing.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

## Role in Aoi

**Visualization and reports.**

| Challenges | Approach | Outcomes & value |
|---|---|---|
| Records are scattered and hard to reproduce | 1. Read the records | Easy-to-read reports |
| Aggregated information is hard to summarize | 2. Render them as figures and tables | Sharing through HTML |
| Reports need continuous updating | 3. Convert them to HTML | Continuous report generation |

Topics: reports, HTML, visualization

## 概要

記録された結果（`season.jsonl` と `propositions.jsonl`）を、判定をやり直さずに図と表にする。あてはめ・平滑化・階級への丸めはしない。

四つの形の文字の表は [docs/forms.md](docs/forms.md)。HTML（軌跡、球団×年、条件の重なり、命題の一覧）は [docs/figures.md](docs/figures.md)。構想図は [docs/images/dragowing.webp](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/images/dragowing.webp)。

`build/dragowing/index.html` と `propositions.html` ができる。`index.html` の軌跡・球団×年・条件の重なり（マスの格子と内訳）は Plotly の JSON 仕様とブラウザの plotly.js（jsDelivr の最新 dist）で描く。Python の `plotly` パッケージは使わない。`propositions.html` は一覧と Markdown の表で、Plotly は使わない。`index.html` に Plotly.js を埋め込むときは `--embed` を付ける。ページの文章は Markdown から HTML にしている。

PNG / SVG は任意である。`--png` や `--svg` を付けると Chrome 経由で書き出す。Chrome が無ければ HTML だけで、テストもそちらだけを見る。

[Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクト [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) から独立したリポジトリです（下の「Aoi との関係」）。

## インストールと使い方

Python 3.11 以上と [uv](https://docs.astral.sh/uv/) を使います。実行時の依存は polars、numpy、markdown です。図はブラウザの plotly.js で、matplotlib も Python の plotly も入れません。HTTP は標準ライブラリの urllib だけです（httpx は使いません）。

```bash
git clone https://github.com/myon-bioinformatics/DRAgoWing.git
cd DRAgoWing
uv sync
```

```bash
python -m dragowing --results <DIR> --out build/dragowing [--id ID ...] [--column 列] [--cond col,op,値 ...] [--breakdown 列] [--breakdown-keep 値 ...] [--png] [--svg] [--embed]
```

- `--results` は `season.jsonl` と `propositions.jsonl` があるディレクトリ。`--id` で命題を絞り、`--column` で球団×年に置く数値列（既定 `wins_vs_pythag`）を選ぶ。
- `--cond` を繰り返すと、条件の重なりを B クラスを含め 2〜8 集合で描く（4 集合以上は格子）。`--breakdown` は重なりの内訳を分ける列（既定 `team`）、`--breakdown-keep` は「その他」にまとめず残す値。詳しくは [docs/figures.md](docs/figures.md)。
- 条件の重なり（`overlap.py`）は [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) の `propositions` と `rule_search` を、四つの形の表（`forms.py`）は [QueRyu](https://github.com/myon-bioinformatics/QueRyu) の `ask`（登録状態）を使います。動かすときはそれらを `PYTHONPATH` に入れます（下の「テスト」と同じ）。
- このディレクトリはパッケージ `dragowing` の中身なので、`python -m dragowing` はディレクトリ名が `dragowing` に見える親から実行します（下の「テスト」の例）。

## 重なり計算だけを軽量にする

`load_overlap(path, conds, backend="stdlib")` または `--overlap-backend stdlib` で、
NumPy・Polarsを読み込まない限定経路を選べます。既定は従来の `native` です。
対応入力・制限・比較測定は [docs/overlap-stdlib.md](docs/overlap-stdlib.md)。
HTMLのMarkdown、画像出力のChromeなどは引き続き必要です。

## 構成

| ファイル | 中身 |
|---|---|
| `cli.py`・`__main__.py` | `python -m dragowing --results DIR --out DIR` |
| `records.py` | 結果ディレクトリの JSONL を、記録の順のまま読む |
| `figures.py` | 記録された値の Plotly 図 JSON（data / layout） |
| `htmlout.py` | HTML。文章と表は Markdown から作る（Plotly は軌跡・球団×年・条件の重なり） |
| `venn.py` | 条件の重なり（2〜8 集合）の図。カルノー図の並びのマスの格子と、領域ごとの内訳の積み上げ棒。Plotly の JSON 仕様を返す（`venn_figures`） |
| `forms.py` | 四つの形の 2×2 と、条件の論理記号（[docs/forms.md](docs/forms.md)） |
| `overlap.py` | 条件集合と B クラスの重なり（マスクは rule_search のビット行列） |
| `plotly_cdn.py` | Plotly.js（jsDelivr） |
| `chrome_pipe.py`・`render.py`・`export.py` | 任意の Chrome（headless）での PNG / SVG の書き出し（[docs/export.md](docs/export.md)） |
| `html_tag_count.py` | ブラウザなしで HTML の要素を数える |
| `research_report.py`・`reports/` | 研究の集計図と、Markdown レポートの描画（Aoi のワークフローから呼ぶ） |
| `docs/` | `forms.md`・`figures.md`・`export.md` |
| `vendor/aoi/`・`vendor.lock.json` | Aoi の共有ツールのうち、このリポジトリが使う `fetch_module.py` と `numpy_min.py` |
| `tests/` | pytest |

## テスト

サイクルデータ（`cycles/` の outputs）、[PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras)（`propositions` と `rule_search`）、[QueRyu](https://github.com/myon-bioinformatics/QueRyu)（`ask`）は Aoi に残します。コピーはせず、Aoi の main を checkout して渡します。

```bash
git clone https://github.com/myon-bioinformatics/Aoi.git .test-deps/aoi
git -C .test-deps/aoi checkout main   # CI は実行時に main の SHA を解決して checkout する
AOI_ROOT=$PWD/.test-deps/aoi \
  PYTHONPATH=$PWD/.test-deps/aoi/pythdragoras:$PWD/.test-deps/aoi/queryu/ask \
  uv run --locked pytest -q --junitxml=reports/junit.xml
```

- DRAgoWing は Aoi の配置を知りません。`--results` と（必要なら）`--team-order` を明示で受け取ります。テストは `AOI_ROOT` の Aoi の `aoi_paths.py` でデータの場所を決めます。
- `AOI_ROOT` が Aoi を指していない（`cycles/` がない）と、pytest は最初に止まって理由を出します。
- このディレクトリはパッケージ `dragowing` の中身です（`__init__.py` は置かない。`export.py` と `cli.py` は `from .plotly_cdn` のような相対 import を使います）。テストは `from dragowing.xxx` と `python -m dragowing` を使います。pytest の `pythonpath` は `["."]` で、直下の `conftest.py` が、`dragowing` を同じディレクトリからまだ import できないときだけ、このディレクトリを `sys.modules["dragowing"]`（`__path__` はこのディレクトリ）に登録します。Aoi では親が pythonpath に入っていて同じディレクトリがすでに `dragowing` なので、この登録は何もしません。
- pytest の外で `python -m dragowing` を動かすときは、ディレクトリ名が `dragowing` ならその親から実行します。

```bash
# リポジトリの中から。checkout のディレクトリ名が dragowing のとき（Aoi の中の dragowing/ も同じ）
cd ..
AOI_ROOT=$PWD/dragowing/.test-deps/aoi \
  PYTHONPATH=$PWD/dragowing/.test-deps/aoi/pythdragoras:$PWD/dragowing/.test-deps/aoi/queryu/ask \
  uv run --project dragowing --locked python -m dragowing \
  --results "$PWD/dragowing/.test-deps/aoi/cycles/c001-chunichi/outputs" --out dragowing/build/dragowing
```

ディレクトリ名が `dragowing` でないとき（このリポジトリを `DRAgoWing` として clone したときなど）は、親に `dragowing` という名前で見せます。

```bash
mkdir -p /tmp/dragowing-run
ln -sfn "$PWD" /tmp/dragowing-run/dragowing
AOI_ROOT=$PWD/.test-deps/aoi \
  PYTHONPATH="/tmp/dragowing-run:$PWD/.test-deps/aoi/pythdragoras:$PWD/.test-deps/aoi/queryu/ask" \
  uv run --locked python -m dragowing \
  --results "$PWD/.test-deps/aoi/cycles/c001-chunichi/outputs" --out build/dragowing
```

- テストは、これに加えて `AOI_ROOT` の Aoi を使います。
  - `cycles/` の出力（`cycles/c001-chunichi/outputs`）。
  - PythDRagoras の `propositions` と `rule_search`（`PYTHONPATH` の `pythdragoras`。`overlap.py` は `pythdragoras` を辿る）。
  - QueRyu の `ask`（`PYTHONPATH` の `queryu/ask`。`forms.py` は `queryu` を辿る）。
  - これ以外に Aoi の兄弟サブプロジェクトと `scripts/` を使わないことは、`tests/test_no_sibling_imports.py` で確かめます（`propositions`、`rule_search`、`ask`、それに `queryu` と `pythdragoras` のパスが既知の例外です）。
- `reports/build_reports.py` は Aoi 側のツールです（Aoi の DRAgoWing reports ワークフローが `myon-bioinformatics/markdown` を checkout して呼び出します）。このリポジトリの CI ではそのワークフローを実行しません。
- Chrome のジョブはありません。Chrome が無いとき、Chrome を使うテストは skip します。

CI（`.github/workflows/ci.yml`）は Python 3.11–3.15 で pytest を動かします。`vendor.lock.json`（`vendor-lock/1`）は path、sha256、source（`myon-bioinformatics/Aoi`）で、写しは `vendor/aoi/` にあります。CI は Aoi の main を `git ls-remote` で解決し（`workflow_dispatch` の `aoi-ref` で上書きできる）、repository id `1402862784` を確かめてから写しと比べます。不一致は pull request では警告、main への push と schedule では失敗です。

## Aoi との関係

このリポジトリは [Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクト [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) から独立したものです。
親は Aoi（Aoi の親は [myon-bioinformatics](https://github.com/myon-bioinformatics/myon-bioinformatics)）。Aoi の [`child-heads.json`](https://github.com/myon-bioinformatics/Aoi/blob/main/child-heads.json) に登録され、tree は登録した時点の Aoi の `dragowing/` と同じです（`.github/`、`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、`LICENSE`、この README も含む）。`git subtree` で同期します（下の「Aoi との同期」。手順の全体は Aoi の [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md)）。
この README は Aoi の `dragowing/README.md` と同じファイルから始まっています。Aoi の中の文書・データへのリンクは、どちらで読んでも開けるように GitHub の URL で書いています。

### Aoi との同期

このリポジトリは Aoi の `dragowing/` の subtree です。除外するファイルはなく、Aoi の `dragowing/` の tree とこのリポジトリの tree は同じです。Aoi の中では `dragowing/.github/` は動かず（GitHub が読むのはリポジトリ直下の `.github/` だけ）、`dragowing/conftest.py` は Aoi の pytest でも同じように `AOI_ROOT` を確かめ、パッケージ登録は何もしません。

- 履歴は Aoi `a8dc4997f43236b24a23df56e21f143fa0e233d8`（main）の `dragowing/` から履歴を残して切り出しました（main `c789da2e30b33144f3110506f90f91ea579b9a6b`、切り出し時点の tree `70424b5a2768f43633766435cc9552f77c1b2ba7` は Aoi の `dragowing/` と同じ）。
- この履歴は Aoi の履歴とつながっていないので、Aoi に一度だけ join を入れます。`git-subtree-split:` にこのリポジトリの main のコミットを書いた squash コミット（tree はこのリポジトリと同じ）を、Aoi の tree を変えないマージの2つ目の親にします。join 以降は `git subtree` が join を起点にします。
- join は2つ目の親として残す必要があります。join を含む Aoi の PR は squash せず、merge commit で入れます（squash すると2つ目の親が消え、`git subtree pull` と `split` が止まります）。
- `git-subtree-split:` のコミットはこのリポジトリの main にある必要があります。このリポジトリの PR も squash せず、merge commit で入れてください（squash すると main の sha が変わり、`git-subtree-split:` に書く sha が main に残りません）。

子 → Aoi（Aoi の main から作ったブランチで）:

```bash
git subtree pull --prefix=dragowing https://github.com/myon-bioinformatics/DRAgoWing.git main --squash
test "$(git rev-parse HEAD:dragowing)" = "$(git rev-parse FETCH_HEAD^{tree})"   # Aoi 側に未同期の変更がないとき
```

Aoi → 子（Aoi の main で）:

```bash
git fetch https://github.com/myon-bioinformatics/DRAgoWing.git main   # split の起点のコミットを手元に置く
git subtree split --prefix=dragowing -b sync/dragowing
test "$(git rev-parse sync/dragowing^{tree})" = "$(git rev-parse HEAD:dragowing)"
git push https://github.com/myon-bioinformatics/DRAgoWing.git sync/dragowing:refs/heads/<新しいブランチ>
```

- push したブランチからこのリポジトリに PR を作ります。マージしたら、Aoi で「子 → Aoi」の pull をして、Aoi 側の起点をこのリポジトリの main に付け直します（squash マージでは split のコミットが main に残らないため）。
- Aoi の `scripts/check_child_heads.py --fail-on-diff` が、Aoi の `child-heads.json` に登録した sha の tree と Aoi の `dragowing/` を比べます。

## 関連サブプロジェクト

親の [Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクトは、それぞれ独立したリポジトリになっています。Aoi の中の場所（subtree）とあわせて載せます。一覧と登録の詳細は Aoi の [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md) です。

| リポジトリ | Aoi の中の場所 | 役割 |
|---|---|---|
| [BlueProbe](https://github.com/myon-bioinformatics/BlueProbe) | [`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe) | 観測と抽出（保存した HTML/CSS/DOM を読み、何があるかを記録する） |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | [`queryu/`](https://github.com/myon-bioinformatics/Aoi/tree/main/queryu) | 取得と観測データセットの作成（来歴つきのキャッシュ） |
| [SakAnalytics](https://github.com/myon-bioinformatics/SakAnalytics) | [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) | 観測データからの指標と統計（チーム×シーズンの指標、残り試合の見通し） |
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | [`pythdragoras/`](https://github.com/myon-bioinformatics/Aoi/tree/main/pythdragoras) | 説明の検証（命題・反例・異議あり） |
| [NagoyAction](https://github.com/myon-bioinformatics/NagoyAction) | [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) | パイプラインの実行と自動化（同じ定義をローカルと GitHub Actions で） |
| **DRAgoWing**（このリポジトリ） | [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) | 図とレポート（Plotly.js の HTML、四つの形の表） |

## ライセンス

MIT License（[LICENSE](LICENSE)）。`LICENSE` は Aoi 直下の MIT LICENSE と同じ中身です（blob `4ec4989b801bf1a3df6184d21f79e6e7ed5931f6`、1061 bytes。Copyright (c) 2026 myon）。

---

# Aoi の研究サイクル（中日・NPB）での使い方

Aoi のルートで、c001（中日）の出力から HTML を作る例。

```bash
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing \
  --team-order d,g,s,db,t,c,h,f,b,e,l,m   # 並び順は Aoi の設定（aoi_npb.py の TEAM_ORDER）
```

## 既存 Markdown 実装との接続

[DRAgoWing reports ワークフロー](https://github.com/myon-bioinformatics/Aoi/blob/main/.github/workflows/dragowing.yml) は、PR・main 更新・手動実行時に `myon-bioinformatics/markdown` の最新 main を一度チェックアウトしてから `dragowing/reports/build_reports.py` で研究文書を描画する。通常 pytest の docs-only スキップは維持し、文書だけの変更でもレポート生成は実行する。

ローカルでの例（出力先は空のディレクトリを指定）:

```sh
git clone https://github.com/myon-bioinformatics/markdown.git .deps/markdown
python -S dragowing/reports/build_reports.py --markdown-root .deps/markdown --output build/dragowing --previous-ref HEAD~1
```
