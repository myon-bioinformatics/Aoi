> **独立リポジトリ**: このリポジトリは [Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクト `dragowing/` から独立したものです。
> 親は Aoi（Aoi の親は myon-bioinformatics）。tree は Aoi の `dragowing/` とまったく同じで（`.github/`、`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、`LICENSE`、この README も含む）、`git subtree` で同期します（下の「Aoi との同期」）。
> この README は Aoi の `dragowing/README.md` と同じファイルです。`../docs/` や `cycles/` への相対リンクは Aoi のリポジトリの中を指します。

## このリポジトリで動かす

サイクルデータ（`cycles/` の outputs）、PythDRagoras（`propositions` と `rule_search`）、QueRyu（`ask`）は Aoi に残します。コピーはせず、Aoi を固定 SHA で checkout して渡します。

```bash
git clone https://github.com/myon-bioinformatics/Aoi.git .test-deps/aoi
git -C .test-deps/aoi checkout a8dc4997f43236b24a23df56e21f143fa0e233d8   # .github/workflows/ci.yml の AOI_SHA
AOI_ROOT=$PWD/.test-deps/aoi \
  PYTHONPATH=$PWD/.test-deps/aoi/pythdragoras:$PWD/.test-deps/aoi/queryu/ask \
  uv run --locked pytest -q --junitxml=reports/junit.xml
```

- パスは Aoi の規約（`--root` / `AOI_ROOT`、`--cycle` / `AOI_RESEARCH_CYCLE`、`aoi_layout.py`）で解決します。
- `AOI_ROOT` が Aoi を指していない（`cycles/` がない）と、pytest は最初に止まって理由を出します。
- 実行時の依存は polars、numpy、markdown です。図はブラウザの plotly.js で、matplotlib も Python の plotly も入れません。HTTP は標準ライブラリの urllib だけです（httpx は使いません）。
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

## aoi_paths.py

`aoi_paths.py` は Aoi 直下の `aoi_paths.py` と同じ中身の通常のファイルです（blob `aa0d41f8b5a017b9b677ed0fecea327bdd5cd1af`、mode 100644。vendor lock は使いません）。Aoi では `dragowing/aoi_paths.py` になり、Aoi の `scripts/check_child_heads.py` が Aoi 直下の原本と blob と mode が同じかを確かめます（`child-heads.json` の `optional.mirrored_from_parent`）。直すときは Aoi の原本を直し、同じ中身をここに置きます。

`aoi_paths.py` をリポジトリ直下に置くのは、`aoi_layout.bind()` が上のディレクトリへ向かって `aoi_paths.py` を探すためです。

`LICENSE` は Aoi 直下の MIT LICENSE と同じ中身です（blob `4ec4989b801bf1a3df6184d21f79e6e7ed5931f6`、1061 bytes。Copyright (c) 2026 myon）。

## Aoi との同期

このリポジトリは Aoi の `dragowing/` の subtree です。除外するファイルはなく、Aoi の `dragowing/` の tree とこのリポジトリの tree は同じです。Aoi の中では `dragowing/.github/` は動かず（GitHub が読むのはリポジトリ直下の `.github/` だけ）、`dragowing/conftest.py` は Aoi の pytest でも同じように `AOI_ROOT` を確かめ、パッケージ登録は何もしません。

- 履歴は Aoi `a8dc4997f43236b24a23df56e21f143fa0e233d8`（main）の `dragowing/` から履歴を残して切り出しました（main `c789da2e30b33144f3110506f90f91ea579b9a6b`、切り出し時点の tree `70424b5a2768f43633766435cc9552f77c1b2ba7` は Aoi の `dragowing/` と同じ）。
- この履歴は Aoi の履歴とつながっていないので、Aoi に一度だけ join を入れます。`git-subtree-split:` にこのリポジトリの main のコミットを書いた squash コミット（tree はこのリポジトリと同じ）を、Aoi の tree を変えないマージの2つ目の親にします。join 以降は `git subtree` が join を起点にします。
- join は2つ目の親として残す必要があります。join を含む Aoi の PR は squash せず、merge commit で入れます（squash すると2つ目の親が消え、`git subtree pull` と `split` が止まります）。
- `git-subtree-split:` のコミットはこのリポジトリの main にある必要があります。この PR も squash せず、merge commit で入れてください（squash すると main の sha が変わり、`git-subtree-split:` に書く sha が main に残りません）。

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

---

# DRAgoWing

記録を、判定をやり直さずに置く。

四つの形の文字の表は [docs/forms.md](docs/forms.md)。HTML（軌跡、球団×年、条件の重なり、命題の一覧）は [docs/figures.md](docs/figures.md)。構想図は [docs/images/dragowing.webp](../docs/images/dragowing.webp)。

```bash
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing
```

`build/dragowing/index.html` と `propositions.html` ができる。`index.html` の軌跡と球団×年は Plotly の JSON 仕様とブラウザの plotly.js（jsDelivr の最新 dist）で描く。Python の `plotly` パッケージは使わない。`propositions.html` は一覧と Markdown の表で、Plotly は使わない。`index.html` に Plotly.js を埋め込むときは `--embed` を付ける。ページの文章は Markdown から HTML にしている。

PNG は任意である。`--png` を付けると Chrome 経由で書き出す。Chrome が無ければ HTML だけで、テストもそちらだけを見る。

## 既存 Markdown 実装との接続

[DRAgoWing reports ワークフロー](../.github/workflows/dragowing.yml) は、PR・main 更新・手動実行時に `myon-bioinformatics/markdown` の最新 main を一度チェックアウトしてから `dragowing/reports/build_reports.py` で研究文書を描画する。通常 pytest の docs-only スキップは維持し、文書だけの変更でもレポート生成は実行する。

ローカルでの例（出力先は空のディレクトリを指定）:

```sh
git clone https://github.com/myon-bioinformatics/markdown.git .deps/markdown
python -S dragowing/reports/build_reports.py --markdown-root .deps/markdown --output build/dragowing --previous-ref HEAD~1
```
