# Aoi の子リポジトリ

Aoi のサブプロジェクトを独立させたリポジトリの登録です。親 myon-bioinformatics の `child-heads.json` と同じ形（`child-heads/1`）を、Aoi 直下に置きます。PythDRagoras の親は Aoi です（myon-bioinformatics からは孫）。

| 子 | prefix | 登録した main |
|---|---|---|
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | `pythdragoras/` | `child-heads.json` の `sha` |

- `child-heads.json`: 子ごとに `sha`、`repository_id`、`optional` に次を書く。
  - `subtree_prefix`: Aoi の中の場所。
  - `not_in_parent`: 子だけに置くパス（`/` で終わればディレクトリ）。Aoi の prefix の下にあれば `excluded_in_parent` に出る。
  - `child_preamble`: 子の中身が「子だけの前書き + Aoi の中身」になっているファイル（PythDRagoras の `README.md`）。Aoi の中身で終わっていれば一致とみなす。本文は Aoi と同じに保ち、独立リポジトリとしての説明だけを子に足すため。
  - `mirrored_from_parent`: prefix の下のパス → Aoi の原本のパス。共有するルートのファイルを子に通常のファイルとして置くとき（PythDRagoras の `aoi_paths.py` は Aoi 直下の `aoi_paths.py`）。Aoi の中でコピーの blob と mode が原本と違えば失敗（`--offline` でも）。QueRyu などほかの子でも同じ書き方で使う。
- `vendor-consumers.json`（`vendor-consumers/1`）: 子が Aoi から vendor lock で取り込むファイルの topology。vendor する子がいなければ置かない（今はない）。置いた場合、`state: locked` の子の lock が登録した `sha` にない・読めないときは失敗。
- `scripts/check_child_heads.py`: 形の確認、`mirrored_from_parent`、子の main と登録した `sha` のずれ（drift）、登録した `sha` の子の tree と Aoi の prefix の tree の差分（blob と mode）、vendor lock の topology。子ごとの取得の失敗（リポジトリがない、タイムアウトなど）はその子の `error` にして続ける。書き込みはしない。`--offline` で形と Aoi 側だけ。

```bash
python -S scripts/check_child_heads.py --vendor-tools <myon-bioinformatics の checkout @ 1eda992> --fail-on-diff
```

`sha` の更新は PR で行い、自動マージはしない。

## subtree の同期

```bash
git subtree pull --prefix=pythdragoras https://github.com/myon-bioinformatics/PythDRagoras.git main --squash
```

`not_in_parent` のファイル（`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、`.github/`、`docs/ci/`）は取り込み後に Aoi 側で消す（BlueProbe と同じ）。

git 2.47.3 の `git subtree split --prefix=pythdragoras`（と、それを使う gh_identity の `split-preflight` / `subtree-sync-status`）は、Aoi の履歴の途中で止まって 10/4 の古い先頭 `f599f60d419f15cd5e9ff386d92b77b3f6467b4e`（25 コミット）を返します。PythDRagoras の main は `git filter-branch --subdirectory-filter pythdragoras` で切り出し、tree が Aoi の `pythdragoras/` と一致することを確かめています。`check_child_heads.py` の差分は tree で比べるので、この影響を受けません。
