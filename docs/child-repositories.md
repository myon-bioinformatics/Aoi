# Aoi の子リポジトリ

Aoi のサブプロジェクトを独立させたリポジトリの登録です。親 myon-bioinformatics の `child-heads.json` と同じ形（`child-heads/1`）を、Aoi 直下に置きます。PythDRagoras と QueRyu の親は Aoi です（myon-bioinformatics からは孫）。

| 子 | prefix | 登録した main |
|---|---|---|
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | `pythdragoras/` | `child-heads.json` の `sha` |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | `queryu/` | `child-heads.json` の `sha` |

- `child-heads.json`: 子ごとに `sha`（子の main）、`repository_id`、`optional` に次を書く。子は prefix の純粋な subtree で、除外するファイルはない（`not_in_parent` / `child_preamble` は受け付けない）。子の `.github/`、`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、README も Aoi の prefix の下に置く。Aoi では `pythdragoras/.github/` は動かず、`pythdragoras/conftest.py` は Aoi の pytest でも同じように `AOI_ROOT` を確かめる。
  - `subtree_prefix`: Aoi の中の場所。
  - `mirrored_from_parent`: prefix の下のパス → Aoi の原本のパス。共有するルートのファイルを子に通常のファイルとして置くとき（PythDRagoras の `aoi_paths.py` は Aoi 直下の `aoi_paths.py`）。Aoi の中でコピーの blob と mode が原本と違えば失敗（`--offline` でも）。QueRyu などほかの子でも同じ書き方で使う。
- `vendor-consumers.json`（`vendor-consumers/1`）: Aoi と子の間では vendor lock を使わないので、置かない。check_child_heads.py には、置いた場合の確認（`state: locked` の子の lock が登録した `sha` にない・読めないときは失敗）だけが残っている。
- `scripts/mirrored_root_files.py`: 子の prefix の下のコピー（既定は `aoi_paths.py`、ほかは `mirrored_from_parent`）が、Aoi 直下の原本と同じ git blob（と実行ビット）かを確かめる。コピーがまだない子（subtree add の前）は `absent` として飛ばす。`tests/test_mirrored_root_files.py` が子ごとに pytest で回す。`mirrored_from_parent` はコピーがないと `check_child_heads.py` で失敗になるので、subtree add のあとに書く。
- `scripts/check_child_heads.py`: 形の確認、`mirrored_from_parent`、子の main と登録した `sha` のずれ（drift）、登録した `sha` の子の tree と Aoi の prefix の tree の差分（blob と mode、除外なし）、vendor lock の topology。子ごとの取得の失敗（リポジトリがない、タイムアウトなど）はその子の `error` にして続ける。書き込みはしない。`--offline` で形と Aoi 側だけ。

```bash
python -S scripts/check_child_heads.py --vendor-tools <myon-bioinformatics の checkout @ 1eda992> --fail-on-diff
```

`sha` の更新は PR で行い、自動マージはしない。

## subtree の同期（決定）

同期の方法は決まりました。Aoi 側で子ごとに一度だけ subtree add（join）をして履歴をつなぎ、そのあとは `git subtree pull` / `split` で同期します。Aoi と子の間では vendor lock を使いません。`aoi_paths.py` のような Aoi 固有のファイルは、子に通常のファイルとして置き、subtree で同期します。手順は PythDRagoras のものを子ごとに読み替えます。

PythDRagoras の main は `git filter-branch --subdirectory-filter pythdragoras` で切り出したので（git 2.47.3 の `git subtree split --prefix=pythdragoras` は Aoi の 585 コミット中 506 で止まり、10/4 の古い先頭 `f599f60d419f15cd5e9ff386d92b77b3f6467b4e` を返す。[gh_identity#74](https://github.com/myon-bioinformatics/gh_identity/issues/74)）、Aoi の履歴とつながっていません。そのため Aoi に一度だけ join を入れます。

- join は2つのコミットです。`Squashed 'pythdragoras/' content from commit <sha>`（親なし、tree は PythDRagoras の `<sha>` と同じ、`git-subtree-dir: pythdragoras` / `git-subtree-split: <sha>`）と、それを2つ目の親にした、Aoi の tree を変えないマージ（`git-subtree-mainline:` も書く）。
- `<sha>` は PythDRagoras の main にあるコミットにします。`git subtree pull` / `split` は `<sha>` を手元に必要とし、PythDRagoras の main から取ってくるためです。PythDRagoras の PR を squash マージして main の sha が変わったら、その sha で join を入れ直します（tree は同じ）。
- join は2つ目の親として残す必要があります。**join を含む Aoi の PR は squash せず、merge commit で入れます**。squash すると2つ目の親が消え、`git subtree pull --squash` と `split` が止まります。
- join 以降は `git subtree` が join を起点にするので、#74 の止まる範囲をたどりません。

子 → Aoi（Aoi の main から作ったブランチで）:

```bash
git subtree pull --prefix=pythdragoras https://github.com/myon-bioinformatics/PythDRagoras.git main --squash
test "$(git rev-parse HEAD:pythdragoras)" = "$(git rev-parse FETCH_HEAD^{tree})"   # Aoi 側に未同期の変更がないとき
```

Aoi → 子（Aoi の main で）:

```bash
git fetch https://github.com/myon-bioinformatics/PythDRagoras.git main   # split の起点のコミットを手元に置く
git subtree split --prefix=pythdragoras -b sync/pythdragoras
test "$(git rev-parse sync/pythdragoras^{tree})" = "$(git rev-parse HEAD:pythdragoras)"
git push https://github.com/myon-bioinformatics/PythDRagoras.git sync/pythdragoras:refs/heads/<新しいブランチ>
```

- push したブランチから PythDRagoras に PR を作ります。マージしたら、Aoi で「子 → Aoi」の pull をして、起点を PythDRagoras の main に付け直します（squash マージでは split のコミットが main に残らないため）。
- **gh_identity#74 が直るまで、Aoi に対して gh_identity の `subtree-sync --write` は使いません。** `--write` なしの計画だけにし、tree の一致は上の `test` で手で確かめます。
- `check_child_heads.py --fail-on-diff` は、登録した `sha` の tree と Aoi の `pythdragoras/` を比べます。
- Aoi の直下から `pytest pythdragoras/tests` のようにパスだけ渡すと、pytest は `pythdragoras/pyproject.toml` を設定ファイルに選びます（rootdir が `pythdragoras/`）。Aoi の設定で動かすときは `pytest -c pyproject.toml pythdragoras/tests`。引数なしの `pytest`（CI）は Aoi の設定のままです。

## QueRyu

- QueRyu の main `35a08024dc0040566068ba513074e3d8326897d4`（21 コミット）は、Aoi `85243d6d1285e3bf4667e1447308543c7d648ab7` から `git filter-branch --subdirectory-filter queryu` で切り出しました。tree `c995b928f46b297025d9cddaeee3df04b322405b` が Aoi の `queryu/` と一致することを確かめています。`git subtree split --prefix=queryu` は 3 コミットで止まり、tree `f5e3d18463fb7f4c431ee796d79d7a42ff1c772a`（10/3 時点）を返しました（gh_identity#74 と同じ）。
- そのため、Aoi の履歴とはまだつながっていません。上の手順で Aoi に一度だけ join（`--prefix=queryu`）を入れますが、まだ行っていません。gh_identity#77（push の経路の修正）を待ちます。
- join のあとは `queryu/aoi_paths.py` が Aoi に入ります。そのときに `child-heads.json` の QueRyu に `mirrored_from_parent: {"aoi_paths.py": "aoi_paths.py"}` を書きます。それまでは `tests/test_mirrored_root_files.py` が skip します。
