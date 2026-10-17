# Aoi の子リポジトリ

Aoi のサブプロジェクトを独立させたリポジトリの登録です。親 myon-bioinformatics の `child-heads.json` と同じ形（`child-heads/1`）を、Aoi 直下に置きます。PythDRagoras・QueRyu・NagoyAction の親は Aoi です（myon-bioinformatics からは孫）。

| 子 | prefix | 登録した main |
|---|---|---|
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | `pythdragoras/` | `child-heads.json` の `sha` |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | `queryu/` | `child-heads.json` の `sha` |
| [NagoyAction](https://github.com/myon-bioinformatics/NagoyAction) | `nagoyaction/` | `child-heads.json` の `sha` |

- `child-heads.json`: 子ごとに `sha`（子の main）、`repository_id`、`optional` に次を書く。子は prefix の純粋な subtree で、除外するファイルはない（`not_in_parent` / `child_preamble` は受け付けない）。子の `.github/`、`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、README も Aoi の prefix の下に置く。Aoi では `pythdragoras/.github/` は動かず、`pythdragoras/conftest.py` は Aoi の pytest でも同じように `AOI_ROOT` を確かめる。
  - `subtree_prefix`: Aoi の中の場所。
  - `mirrored_from_parent`: prefix の下のパス → Aoi の原本のパス。共有するルートのファイルを子に通常のファイルとして置くとき（PythDRagoras の `aoi_paths.py` は Aoi 直下の `aoi_paths.py`）。Aoi の中でコピーの blob と mode が原本と違えば失敗（`--offline` でも）。QueRyu などほかの子でも同じ書き方で使う。
- Aoi と subtree 子の間では vendor lock を使わない（`vendor-consumers.json` は置かない）。
- `scripts/check_child_heads.py`: 形の確認、`mirrored_from_parent`、子の main と登録した `sha` のずれ（drift）、登録した `sha` の子の tree と Aoi の prefix の tree の差分（blob と mode、除外なし）。子ごとの取得の失敗（リポジトリがない、タイムアウトなど）はその子の `error` にして続ける。書き込みはしない。`--offline` で形と Aoi 側だけ。

```bash
python -S scripts/check_child_heads.py --fail-on-diff
```

`sha` の更新は PR で行い、自動マージはしない。

## subtree の同期（決定）

同期の方法は決まりました。Aoi 側で子ごとに一度だけ subtree add（join）をして履歴をつなぎ、そのあとは `git subtree pull` / `split` で同期します。Aoi と子の間では vendor lock を使いません。`aoi_paths.py` のような Aoi 固有のファイルは、子に通常のファイルとして置き、subtree で同期します。原本との一致は、`child-heads.json` の `mirrored_from_parent` を使って `check_child_heads.py` が確かめます。手順は PythDRagoras のものを子ごとに読み替えます。

PythDRagoras の main は `git filter-branch --subdirectory-filter pythdragoras` で切り出したので（git 2.47.3 の `git subtree split --prefix=pythdragoras` は Aoi の 585 コミット中 506 で止まり、10/4 の古い先頭 `f599f60d419f15cd5e9ff386d92b77b3f6467b4e` を返す。join 前は split が古い tree で止まる（[gh_identity#74](https://github.com/myon-bioinformatics/gh_identity/issues/74)））、Aoi の履歴とつながっていません。そのため Aoi に一度だけ join を入れます。

- join は2つのコミットです。`Squashed 'pythdragoras/' content from commit <sha>`（親なし、tree は PythDRagoras の `<sha>` と同じ、`git-subtree-dir: pythdragoras` / `git-subtree-split: <sha>`）と、それを2つ目の親にした、Aoi の tree を変えないマージ（`git-subtree-mainline:` も書く）。
- `<sha>` は PythDRagoras の main にあるコミットにします。`git subtree pull` / `split` は `<sha>` を手元に必要とし、PythDRagoras の main から取ってくるためです。PythDRagoras の PR を squash マージして main の sha が変わったら、その sha で join を入れ直します（tree は同じ）。
- join は2つ目の親として残す必要があります。**join を含む Aoi の PR は squash せず、merge commit で入れます**。squash すると2つ目の親が消え、`git subtree pull --squash` と `split` が止まります。
- join 以降は `git subtree` が join を起点にするので、join 以前に split が古く止まっていた範囲をたどりません。

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
- **Aoi → 子への push（同期）は、親リポジトリ myon-bioinformatics の `gh_ops.py` `subtree-push` で行います**（[myon-bioinformatics#98](https://github.com/myon-bioinformatics/myon-bioinformatics/pull/98)）。gh_identity は検索・存在確認・fetch など書き込みをしない操作に限定し、add/commit/push など重い書き込みは親の gh_ops が担います。tree の一致は上の `test` と `check_child_heads.py` で確かめます。
- `check_child_heads.py --fail-on-diff` は、登録した `sha` の tree と Aoi の `pythdragoras/` を比べます。
- Aoi の直下から `pytest pythdragoras/tests` のようにパスだけ渡すと、pytest は `pythdragoras/pyproject.toml` を設定ファイルに選びます（rootdir が `pythdragoras/`）。Aoi の設定で動かすときは `pytest -c pyproject.toml pythdragoras/tests`。引数なしの `pytest`（CI）は Aoi の設定のままです。

## QueRyu

- QueRyu の main `35a08024dc0040566068ba513074e3d8326897d4`（21 コミット）は、Aoi `85243d6d1285e3bf4667e1447308543c7d648ab7` から `git filter-branch --subdirectory-filter queryu` で切り出しました。tree `c995b928f46b297025d9cddaeee3df04b322405b` が Aoi の `queryu/` と一致することを確かめています。`git subtree split --prefix=queryu` は 3 コミットで止まり、tree `f5e3d18463fb7f4c431ee796d79d7a42ff1c772a`（10/3 時点）を返しました（PythDRagoras と同じ split の止まり（[gh_identity#74](https://github.com/myon-bioinformatics/gh_identity/issues/74)））。
- QueRyu #1/#2/#3/#4 を merge commit で取り込んだ main `e052cc3750cf14fd271187cee12c6ddddc11d7ab` に対し、一度だけの join を追加しました。親なし squash commit の tree はこの子の tree と同一で、Aoi の merge commit の第2親として保持します。PR は squash/rebase せず merge commit で入れてください。
- `queryu/` 全体（足場・CI・テスト・cache_core も含む）は登録した QueRyu tree と同一です。`mirrored_from_parent: {"aoi_paths.py": "aoi_paths.py"}` により原本との blob/mode 一致も検査します。
- 単独 QueRyu では Aoi 配下の BlueProbe を拒否します。物理的に `AOI_ROOT/queryu` にある subtree のテストだけは、逆に `AOI_ROOT/blueprobe` の正確な場所を要求します。Aoi 直下から対象を絞る場合は `pytest -c pyproject.toml queryu/tests` を使います。

QueRyu #5 の埋込み共有 aoi_layout 出自ガード修正は、初回joinの後に通常の subtree merge で取り込みました。登録先は `4a478d1d69b5aa0c577ce6a5882c1e35593cbf2f` です。単独運用の出自制限を保ち、Aoi内では正確なPythDRagorasミラーのバイト一致を実行時に確認します。

## NagoyAction

- NagoyAction の最初の 49 コミットは、Aoi `0a1751a60ac64708d679f22950aa2b14cf688efd` から `git filter-branch --subdirectory-filter nagoyaction` で切り出しました（先頭 `b35707b877a92fd088db06f15b87d0e72158fc27`、tree `1537879773093a5350a17ca657fbdf89f6a57e72` が Aoi の `nagoyaction/` と一致）。そのうえに子の足場（LICENSE・`.gitignore`・README の節、CI）を足した main `97ee776559ddebdc1ddf54330c98e3face099391` に対し、一度だけの join を入れました。親なし squash commit の tree はこの子の tree と同一で、Aoi の merge commit の第2親として残します。PR は squash/rebase せず merge commit で入れてください。
- `nagoyaction/` 全体（子の CI・LICENSE・`.gitignore` も含む）は登録した NagoyAction の tree と同一です。Aoi の原本を写したファイルはないので `mirrored_from_parent` は書きません。`min.py` は Aoi が提供し、子には置きません。
- NagoyAction の手順とテストは Aoi の直下（`cycles/`・`queryu/`・`sakanalytics/`・`blueprobe/`・`vendor/`・`scripts/`・`docs/`）を相対パスで使います。子の CI は Aoi を固定 SHA で checkout し、その `nagoyaction/` を子の tree に置き換えて（index の tree が子の tree と一致することを確かめて）、Aoi の設定で `pytest -c pyproject.toml nagoyaction/tests` を動かします。Aoi の中では `nagoyaction/.github/` は動きません。
- 同期は PythDRagoras の手順の `pythdragoras` を `nagoyaction`、リポジトリを NagoyAction に読み替えます。
