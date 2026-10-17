# Aoi の子リポジトリ

Aoi のサブプロジェクトを独立させたリポジトリの登録です。親 myon-bioinformatics の `child-heads.json` と同じ形（`child-heads/1`）を、Aoi 直下に置きます。PythDRagoras と QueRyu の親は Aoi です（myon-bioinformatics からは孫）。

| 子 | prefix | 登録した main |
|---|---|---|
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | `pythdragoras/` | `child-heads.json` の `sha` |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | `queryu/` | `child-heads.json` の `sha` |

- `child-heads.json`: 子ごとに `sha`、`repository_id`、`optional` に次を書く。
  - `subtree_prefix`: Aoi の中の場所。
  - `not_in_parent`: 子だけに置くパス（`/` で終わればディレクトリ）。Aoi の prefix の下にあれば `excluded_in_parent` に出る。
  - `child_preamble`: 子の中身が「子だけの前書き + Aoi の中身」になっているファイル（PythDRagoras の `README.md`）。Aoi の中身で終わっていれば一致とみなす。本文は Aoi と同じに保ち、独立リポジトリとしての説明だけを子に足すため。
  - `mirrored_from_parent`: prefix の下のパス → Aoi の原本のパス。共有するルートのファイルを子に通常のファイルとして置くとき（PythDRagoras の `aoi_paths.py` は Aoi 直下の `aoi_paths.py`）。Aoi の中でコピーの blob と mode が原本と違えば失敗（`--offline` でも）。QueRyu などほかの子でも同じ書き方で使う。
- `vendor-consumers.json`（`vendor-consumers/1`）: Aoi と子の間では vendor lock を使わないので、置かない。check_child_heads.py は、置いた場合の形の確認だけを残している。
- `scripts/mirrored_root_files.py`: 子の prefix の下のコピー（既定は `aoi_paths.py`、ほかは `mirrored_from_parent`）が、Aoi 直下の原本と同じ git blob（と実行ビット）かを確かめる。コピーがまだない子（subtree add の前）は `absent` として飛ばす。`tests/test_mirrored_root_files.py` が pytest で回す。`mirrored_from_parent` はコピーがないと失敗にするので、subtree add のあとに書く。
- `scripts/check_child_heads.py`: 形の確認、`mirrored_from_parent`、子の main と登録した `sha` のずれ（drift）、登録した `sha` の子の tree と Aoi の prefix の tree の差分（blob と mode）、vendor lock の topology。子ごとの取得の失敗（リポジトリがない、タイムアウトなど）はその子の `error` にして続ける。書き込みはしない。`--offline` で形と Aoi 側だけ。

```bash
python -S scripts/check_child_heads.py --vendor-tools <myon-bioinformatics の checkout @ 1eda992> --fail-on-diff
```

`sha` の更新は PR で行い、自動マージはしない。

## 同期の方法（決定）

- Aoi 側で、子ごとに一度だけ `git subtree add` をして、Aoi と子の履歴をつなぐ。そのあとは `git subtree pull` / `git subtree push` で同期する。
- Aoi と子の間では vendor lock を使わない。`aoi_paths.py` のような Aoi 固有のファイルは、子に通常のファイルとして置き、subtree で同期する。原本との一致は `scripts/mirrored_root_files.py` で確かめる。
- 一度だけの `git subtree add` はまだ行っていない。gh_identity #77（push の経路の修正）を待つ。それまでは gh_identity の `subtree-sync --write` を Aoi に使わない。古い tree を push するおそれがある（gh_identity #74）。

```bash
git subtree pull --prefix=pythdragoras https://github.com/myon-bioinformatics/PythDRagoras.git main --squash
git subtree pull --prefix=queryu https://github.com/myon-bioinformatics/QueRyu.git main --squash
```

`not_in_parent` のファイル（`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、`.github/`）は、取り込んだあと Aoi 側で消す（BlueProbe と同じ）。

git 2.47.3 の `git subtree split --prefix=pythdragoras`（と、それを使う gh_identity の `split-preflight` / `subtree-sync-status`）は、Aoi の履歴の途中で止まって 10/4 の古い先頭 `f599f60d419f15cd5e9ff386d92b77b3f6467b4e`（25 コミット）を返します。PythDRagoras の main は `git filter-branch --subdirectory-filter pythdragoras` で切り出し、tree が Aoi の `pythdragoras/` と一致することを確かめています。`check_child_heads.py` の差分は tree で比べるので、この影響を受けません。

QueRyu も同じです。`git subtree split --prefix=queryu` は 3 コミットで止まり、tree `f5e3d18463fb7f4c431ee796d79d7a42ff1c772a`（10/3 時点）を返します。QueRyu の main `35a08024dc0040566068ba513074e3d8326897d4`（21 コミット）は、Aoi `85243d6d1285e3bf4667e1447308543c7d648ab7` から `git filter-branch --subdirectory-filter queryu` で切り出しました。tree `c995b928f46b297025d9cddaeee3df04b322405b` が Aoi の `queryu/` と一致することを確かめています。
