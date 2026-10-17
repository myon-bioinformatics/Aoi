# Aoi の子リポジトリ

Aoi のサブプロジェクトを `git subtree` で独立させたリポジトリの登録です。親 myon-bioinformatics の `child-heads.json` / `vendor-consumers.json` と同じ形（`child-heads/1`、`vendor-consumers/1`）を、Aoi 直下に置きます。PythDRagoras と QueRyu の親は Aoi です（myon-bioinformatics からは孫）。

| 子 | prefix | 登録した main |
|---|---|---|
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | `pythdragoras/` | `child-heads.json` の `sha` |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | `queryu/` | `child-heads.json` の `sha` |

- `child-heads.json`: 子ごとに `sha`（子の main）、`repository_id`、`optional.subtree_prefix`、`optional.not_in_parent`（子だけに置くファイル。Aoi へ取り込まない）。
- `vendor-consumers.json`: 子が Aoi から vendor するファイルの topology。正確な commit / blob / SHA-256 は子の `vendor.lock.json` が持つ。
- `scripts/check_child_heads.py`: 形の確認、子の main と登録した `sha` のずれ（drift）、登録した `sha` の子の tree と Aoi の prefix の tree の差分、子の `vendor.lock.json` と登録の topology。書き込みはしない。`--offline` で形だけ。

```bash
python -S scripts/check_child_heads.py --vendor-tools <myon-bioinformatics の checkout @ 1eda992>
```

`sha` の更新は PR で行い、自動マージはしない。

## subtree の同期

```bash
git subtree pull --prefix=pythdragoras https://github.com/myon-bioinformatics/PythDRagoras.git main --squash
git subtree pull --prefix=queryu https://github.com/myon-bioinformatics/QueRyu.git main --squash
```

`not_in_parent` のファイル（`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、`.github/`、`docs/ci/`）は取り込み後に Aoi 側で消す（BlueProbe と同じ）。

git 2.47.3 の `git subtree split --prefix=pythdragoras`（と、それを使う gh_identity の `split-preflight` / `subtree-sync-status`）は、Aoi の履歴の途中で止まって 10/4 の古い先頭 `f599f60d419f15cd5e9ff386d92b77b3f6467b4e`（25 コミット）を返します。PythDRagoras の main は `git filter-branch --subdirectory-filter pythdragoras` で切り出し、tree が Aoi の `pythdragoras/` と一致することを確かめています。`check_child_heads.py` の差分は tree で比べるので、この影響を受けません。

QueRyu も同じで、`git subtree split --prefix=queryu` は 3 コミットで止まり、tree `f5e3d18463fb7f4c431ee796d79d7a42ff1c772a`（10/3 時点）を返します。QueRyu の main `35a08024dc0040566068ba513074e3d8326897d4`（21 コミット）は `git filter-branch --subdirectory-filter queryu` で Aoi `85243d6d1285e3bf4667e1447308543c7d648ab7` から切り出し、tree `c995b928f46b297025d9cddaeee3df04b322405b` が Aoi の `queryu/` と一致することを確かめています。
