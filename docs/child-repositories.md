# Aoi の子リポジトリ

Aoi のサブプロジェクトを独立させたリポジトリの登録です。親 myon-bioinformatics の `child-heads.json` と同じ形（`child-heads/1`）を、Aoi 直下に置きます。BlueProbe・PythDRagoras・QueRyu・NagoyAction・SakAnalytics・DRAgoWing の親は Aoi です（myon-bioinformatics からは孫）。

| 子 | prefix | 登録した main |
|---|---|---|
| [BlueProbe](https://github.com/myon-bioinformatics/BlueProbe) | [`blueprobe/`](../blueprobe/) | `child-heads.json` の `sha` |
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | [`pythdragoras/`](../pythdragoras/) | `child-heads.json` の `sha` |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | [`queryu/`](../queryu/) | `child-heads.json` の `sha` |
| [NagoyAction](https://github.com/myon-bioinformatics/NagoyAction) | [`nagoyaction/`](../nagoyaction/) | `child-heads.json` の `sha` |
| [SakAnalytics](https://github.com/myon-bioinformatics/SakAnalytics) | [`sakanalytics/`](../sakanalytics/) | `child-heads.json` の `sha` |
| [DRAgoWing](https://github.com/myon-bioinformatics/DRAgoWing) | [`dragowing/`](../dragowing/) | `child-heads.json` の `sha` |

- `child-heads.json`: 子ごとに `sha`（子の main）、`repository_id`、`optional` に次を書く。子は prefix の純粋な subtree で、除外するファイルはない（`not_in_parent` / `child_preamble` は受け付けない）。子の `.github/`、`pyproject.toml`、`uv.lock`、`conftest.py`、`.gitignore`、README も Aoi の prefix の下に置く。Aoi では `pythdragoras/.github/` は動かず、`pythdragoras/conftest.py` は Aoi の pytest でも同じように `AOI_ROOT` を確かめる。
  - `subtree_prefix`: Aoi の中の場所。
  - `mirrored_from_parent`: checker が対応する任意の mirror 宣言。現在は登録していない。Aoi 固有の配置設定は親だけが持ち、子へ引数で渡す。
- Aoi と subtree 子の間では `vendor-consumers.json` を置かない。共有する stdlib-shrink の道具だけは Aoi が原本で、[`shared-tools.lock.json`](../shared-tools.lock.json)（`vendor-lock/1`）に path、sha256、source（Aoi）、consumer の子を1本ずつ書く。子はその lock のバイトを受け取る。subtree の tree 一致とは別の契約である。
- `scripts/check_child_heads.py`: 形の確認、`mirrored_from_parent`、子の main と登録した `sha` のずれ（drift）、登録した `sha` の子の tree と Aoi の prefix の tree の差分（blob と mode、除外なし）。子ごとの取得の失敗（リポジトリがない、タイムアウトなど）はその子の `error` にして続ける。書き込みはしない。`--offline` で形と Aoi 側だけ。

```bash
python -S scripts/check_child_heads.py --fail-on-diff
```

`sha` の更新は PR で行い、自動マージはしない。

2026-10-20: BlueProbe #30 の merge `50a2846d68fcba4acbe7e4abf7fb0130de07de89`（標準ライブラリの html.parser）と QueRyu #16 の merge `fcadaa9aaab30292703459758eae481d0f018f2d` を、squash なしの `git subtree pull --prefix=blueprobe` と `git subtree pull --prefix=queryu` で取り込みました。`blueprobe/` と `queryu/` の tree は登録した SHA の tree と同一です。各 merge commit の第2親は子の main の head です。

2026-10-20: 各子の open PR を子ごとの統合 PR（BlueProbe #29、QueRyu #15、PythDRagoras #15、DRAgoWing #8、SakAnalytics #9、NagoyAction #10）にまとめて merge し、6つの子すべてを `git subtree pull`（`--squash` なし）で取り込みました（BlueProbe `27f61b3b10c629ace49ad6c8a2dc9f09ad5e31f3`、QueRyu `0a83400f3a718901815e1d07d2e2d990976839b3`、PythDRagoras `b0f9c3a1ef255f7c0bc38bc7eeff86360403e69f`、DRAgoWing `cd8140ce695ede6add6817cced2ea5c8ee2e161f`、SakAnalytics `3cd2349b8a5d49f4e0de187aac2741566b3d731c`、NagoyAction `a1ee275410f49f7d0ce95c6ff4f16ae5bbc39028`）。各 merge commit の第2親は子の main の head です。

2026-10-19（2回目）: PythDRagoras・DRAgoWing・SakAnalytics の squash の join を、BlueProbe・QueRyu・NagoyAction と同じく、prefix を消してから `git subtree add`（`--squash` なし）で入れ直しました（PythDRagoras `cd21d7e295facfbc8101ea2d89f715da27fbd80a`、DRAgoWing `8d6163989fc2f4843412a03b465fee1cf9b3ac3c`、SakAnalytics `9a5bc4a048edfdaefbbe514fdde94eb0df4f2065`）。これで6つの子はすべて squash なしの subtree で、同期は `git subtree pull`（`--squash` なし）です。

2026-10-19: SakAnalytics へのリポジトリ名の変更に合わせて、6つの子の README を各子の main で直し、`git subtree pull` で Aoi に取り込みました（BlueProbe・QueRyu・NagoyAction は squash なし、PythDRagoras・DRAgoWing・SakAnalytics は join に合わせて `--squash`）。2026-10-18 に README を直接コピーしていたため、squash の3つは README が衝突し、子の版を採って解決しました（解決後の prefix の tree は子の main と同一）。`child-heads.json` の SakAnalytics のキーも新しい名前にしました。

2026-10-18: 子の README（各子の main）を Aoi の prefix にそのままコピーし、`pythdragoras/`・`sakanalytics/` に子と同じ `LICENSE` を置いて、5つの子の `sha` を各子の main（DRAgoWing `a060e79`、NagoyAction `9ee99dc`、PythDRagoras `7ea1438`、QueRyu `096bef9`、sakanalytics `887444d`）に更新しました。README と LICENSE だけの差分なので `git subtree pull` はしていません（tree は一致）。次の `git subtree pull --squash` は同じ変更を両側に持つ状態からの取り込みになります。

## subtree の同期（決定）

同期の方法は決まりました。Aoi 側で子ごとに一度だけ subtree add（join）をして履歴をつなぎ、そのあとは `git subtree pull` / `split` で同期します。Aoi と子の間では `vendor-consumers.json` を使いません。共有する stdlib-shrink の道具は `shared-tools.lock.json` で配ります。`aoi_paths.py` と `aoi_npb.py` は Aoi だけに置き、解決したパス・設定を子へ引数で渡します（[親のNPBコマンド](../cycles/c001-chunichi/npb-configuration.md)）。子のtreeは登録SHAと完全一致させます。手順は PythDRagoras のものを子ごとに読み替えます。

PythDRagoras の main は `git filter-branch --subdirectory-filter pythdragoras` で切り出したので（git 2.47.3 の `git subtree split --prefix=pythdragoras` は Aoi の 585 コミット中 506 で止まり、10/4 の古い先頭 `f599f60d419f15cd5e9ff386d92b77b3f6467b4e` を返す。join 前は split が古い tree で止まる（[gh_identity#74](https://github.com/myon-bioinformatics/gh_identity/issues/74)））、Aoi の履歴とつながっていません。そのため Aoi に一度だけ join を入れます。

- 2026-10-19 に、旧 `pythdragoras/` を消してから `git subtree add --prefix=pythdragoras https://github.com/myon-bioinformatics/PythDRagoras.git main`（`--squash` なし）で join を入れ直しました。merge commit の第2親は PythDRagoras main の head で、PythDRagoras の全履歴が Aoi につながります（BlueProbe #64・QueRyu #68・NagoyAction #69 と同じ。手組みの2親マージや squash 由来の join は使いません。以前の squash の join と `Squashed 'pythdragoras/' changes` のコミットは履歴に残りますが、起点にはしません）。
- 登録する `sha` は PythDRagoras の main にあるコミットにします。子の PR も squash せず merge commit で入れます。
- join は2つ目の親として残す必要があります。**join を含む Aoi の PR は squash せず、merge commit で入れます**。squash すると2つ目の親が消え、`git subtree pull` と `split` が止まります。
- join 以降は `git subtree` が join を起点にするので、join 以前に split が古く止まっていた範囲をたどりません。

子 → Aoi（Aoi の main から作ったブランチで）:

```bash
git subtree pull --prefix=pythdragoras https://github.com/myon-bioinformatics/PythDRagoras.git main
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

2026-10-20: Aoi の配置と NPB 固有の表・規則を子から外しました（案A）。QueRyu #17 `079d502`、DRAgoWing #9 `8eb7d9c`、PythDRagoras #16 `bd5690f`、SakAnalytics #10 `44f95f6`、NagoyAction #11 `1181e43` を、それぞれ squash なしの `git subtree pull` で取り込みました。子の `aoi_paths.py` の写しはなくなり、`child-heads.json` の `mirrored_from_parent` も外しました。Aoi の配置は直下の `aoi_paths.py`、NPB の設定（球団表・並び順・月の key・年間表の前提・CS 規則のプリセット）は直下の `aoi_npb.py` だけが持ち、子へ引数で渡します。`annual_scope.py` は Aoi の直下、`season_verify_2022.py` は `scripts/` に移しました。続けて QueRyu #18 `f1a91e5`、DRAgoWing #10 `360afbd`、PythDRagoras #17 `5fa7935`、SakAnalytics #11 `1630c83`（Aoi に埋め込まれたときは `AOI_ROOT` がなくても親の Aoi を使う conftest）も同じ方法で取り込みました。`pythdragoras/aoi_layout.py`・`sakanalytics/aoi_layout.py` は、ソースの SHA-256 を証跡で固定した CLI（littlebit、proposition_seed_audit）のためだけに残っています。

2026-10-20: QueRyu #16 の merge `fcadaa9aaab30292703459758eae481d0f018f2d` を、squash なしの `git subtree pull --prefix=queryu` で取り込みました。`pattern_postprocess` は `from blueprobe import detect_pattern, get_pattern` でパターンを読みます。`queryu/` の tree は登録した SHA の tree と同一です。

2026-10-20: QueRyu #14 の merge `b8b2983edde039f010be75e40944f750ccfd9ce7` を、squash なしの `git subtree pull --prefix=queryu` で取り込みました。`queryu/` の tree は登録した SHA の tree と同一です。この版は import 時に BlueProbe の `dom_patterns` を読むため、BlueProbe main `563d84488a57efd3bca2d89c97c0a72759ab8ee5` も同じ方法で `blueprobe/` に取り込みました。DRAgoWing・PythDRagoras・SakAnalytics は drift のみなので登録 SHA は変えていません。

- QueRyu の main `35a08024dc0040566068ba513074e3d8326897d4`（21 コミット）は、Aoi `85243d6d1285e3bf4667e1447308543c7d648ab7` から `git filter-branch --subdirectory-filter queryu` で切り出しました。tree `c995b928f46b297025d9cddaeee3df04b322405b` が Aoi の `queryu/` と一致することを確かめています。`git subtree split --prefix=queryu` は 3 コミットで止まり、tree `f5e3d18463fb7f4c431ee796d79d7a42ff1c772a`（10/3 時点）を返しました（PythDRagoras と同じ split の止まり（[gh_identity#74](https://github.com/myon-bioinformatics/gh_identity/issues/74)））。
- QueRyu の main `5ce256d77d64b33d4c71c2cbb84fe201f9637567`（#5–#8: 埋込み aoi_layout 出自ガード、stdlib cache core、README、emoji_data、cache_share）に対し、一度だけ `git subtree add` で join を入れました。merge commit の第2親は QueRyu main の head です（手組みの2親マージや squash 由来の join は使いません）。PR は squash/rebase せず merge commit で入れてください。
- `queryu/` 全体（足場・CI・テスト・cache_core も含む）は登録した QueRyu tree と同一です。`mirrored_from_parent: {"aoi_paths.py": "aoi_paths.py"}` により原本との blob/mode 一致も検査します。
- 単独 QueRyu では Aoi 配下の BlueProbe を拒否します。物理的に `AOI_ROOT/queryu` にある subtree のテストだけは、逆に `AOI_ROOT/blueprobe` の正確な場所を要求します。埋込み共有 `aoi_layout` は単独運用の出自制限を保ち、Aoi 内では正確な PythDRagoras ミラーのバイト一致を実行時に確認します。Aoi 直下から対象を絞る場合は `pytest -c pyproject.toml queryu/tests` を使います。

## NagoyAction

2026-10-20: main `c3889f69f59d46286c974164cf3e6e6d55d3796c`（#18: ルートの `scripts/shrink_module.py`・`scripts/shrink_polars.py`・`shrink/polars_min.py` の fork を消し、共有ツールは `vendor/aoi/` だけ）を、直前の subtree merge を残したまま squash なしの `git subtree pull --prefix=nagoyaction` で取り込みました。merge commit の第2親はこの SHA で、`nagoyaction/` の tree は登録した SHA の tree と同一です。

2026-10-20: main `60e301b8bbd43ec5b682397f8ff1d6be887b1596`（#17: `vendor-aoi` の `uses:` を full SHA に固定し、`localci.py --strict` で可変ピンを失敗にする）を、直前の subtree merge を残したまま squash なしの `git subtree pull --prefix=nagoyaction` で取り込みました。merge commit の第2親はこの SHA で、`nagoyaction/` の tree は登録した SHA の tree と同一です。

2026-10-20: main `c4cdf0d7d17a15380dac89fdd21f147efcef3be5`（#12: CI が Aoi main を実行時に解決する、#15: Aoi の polars shrink 道具を vendor、#16: ローカル CI のシャードと `polars_min` の collect 検査）を squash なしの `git subtree pull --prefix=nagoyaction` で取り込みました。merge commit の第2親はこの SHA で、`nagoyaction/` の tree は登録した SHA の tree と同一です。

2026-10-20: Aoi #77 の `show` を子の正本 NagoyAction #7 へ反映し、main `4ad09fdd7b3c1a69e103772b3a5dbf4ea4b28df8` を squash なしの subtree pull で取り込みました。子 #6 の共通 `.gitignore` も含め、prefix 全体の tree と登録 SHA を一致させています。Aoi #78 の3子の join 修復も保持しています。研究workerの自動実行は有効化していません。

- NagoyAction の最初の 49 コミットは、Aoi `0a1751a60ac64708d679f22950aa2b14cf688efd` から `git filter-branch --subdirectory-filter nagoyaction` で切り出しました（先頭 `b35707b877a92fd088db06f15b87d0e72158fc27`、tree `1537879773093a5350a17ca657fbdf89f6a57e72` が Aoi の `nagoyaction/` と一致）。そのうえに子の足場（LICENSE・`.gitignore`・README の節、CI）を足し、NagoyAction #1（README）と #2（Aoi #67 の fetch-guard の同期）を merge commit で取り込んだ main `a53df3f0fd9780ab55626e489ebb12851724731c` に対し、旧 `nagoyaction/` を消してから一度だけ `git subtree add`（`--squash` なし）で join を入れ直しました。merge commit の第2親は NagoyAction main の head で、NagoyAction の全履歴が Aoi につながります（手組みの2親マージや squash 由来の join は使いません。最初の squash の join `f575167` は履歴に残りますが、起点にはしません）。PR は squash/rebase せず merge commit で入れてください。
- `nagoyaction/` 全体（子の CI・LICENSE・`.gitignore` も含む）は登録した NagoyAction の tree と同一です。Aoi の原本を写したファイルはないので `mirrored_from_parent` は書きません。`min.py` は Aoi が提供し、子には置きません。
- NagoyAction の手順とテストは Aoi の直下（`cycles/`・`queryu/`・`sakanalytics/`・`blueprobe/`・`vendor/`・`scripts/`・`docs/`）を相対パスで使います。子の CI は Aoi の past-pattern snapshot を SHA で取得して検証データに使い、その `nagoyaction/` を子の tree に置き換えて（index の tree が子の tree と一致することを確かめて）、Aoi の設定で `pytest -c pyproject.toml nagoyaction/tests` を動かします。Aoi の中では `nagoyaction/.github/` は動きません。
- 同期は PythDRagoras の手順の `pythdragoras` を `nagoyaction`、リポジトリを NagoyAction に読み替えます。

## SakAnalytics

- リポジトリ名は 2026-10-19 に sakanalytics から SakAnalytics に変えました（旧 URL は GitHub がリダイレクト）。Aoi の prefix `sakanalytics/` と Python のモジュール名 `sakanalytics` は変えません。
- SakAnalytics の最初の 71 コミットは、Aoi `0a1751a60ac64708d679f22950aa2b14cf688efd` から `git filter-branch --subdirectory-filter sakanalytics` で切り出しました（先頭 `67c8781b0e606ab41f56f717c2a84efa67b98533`、tree `a54fc414f1959f7619619c0ae9398ff2fe8fbcbb` が Aoi の `sakanalytics/` と一致）。そのうえに子の足場（CI・`.gitignore`・`pyproject.toml`・`uv.lock`・`conftest.py`・`aoi_paths.py`・README の節・兄弟 import のテスト）を足しました。最初は `0bb7177ac0ec5240c468b6d2c58ca52e116c6d03` に対する手組みの squash の join（#59）でしたが、2026-10-19 に、旧 `sakanalytics/` を消してから main `9a5bc4a048edfdaefbbe514fdde94eb0df4f2065`（#4 の expected_total_games、#5 の README、#6 の依存の下限）に対して `git subtree add`（`--squash` なし）で join を入れ直しました。merge commit の第2親は SakAnalytics main の head です。PR は squash/rebase せず merge commit で入れてください。
- `sakanalytics/` 全体（子の CI・`.gitignore`・`pyproject.toml`・`uv.lock`・`conftest.py` も含む）は登録した SakAnalytics の tree と同一です。`mirrored_from_parent: {"aoi_paths.py": "aoi_paths.py"}` により原本との blob/mode 一致も検査します。`min.py` は Aoi が提供し、子には置きません。
- サイクルデータ（`cycles/`）と PythDRagoras（`propositions`）は Aoi に残します。子の CI は Aoi の past-pattern snapshot を SHA で取得して検証データに使い、`AOI_ROOT` と `PYTHONPATH` の `pythdragoras` を渡して pytest を動かします。Aoi の中では `sakanalytics/.github/` は動きません。`sakanalytics/conftest.py` は Aoi の pytest でも同じように `AOI_ROOT` を確かめます。
- 同期は PythDRagoras の手順の `pythdragoras` を `sakanalytics`、リポジトリを SakAnalytics に読み替えます（`--squash` なし）。

## DRAgoWing

2026-10-21: main `9e9376f1b7c0ec1dfbafd020a50769c8dc3d82cf`（#16: headless Chrome が D-Bus の応答待ちで `Browser.getVersion` に届かないのを止める）を squash なしの `git subtree pull --prefix=dragowing` で取り込みました。merge commit の第2親はこの SHA で、`dragowing/` の tree は登録した SHA の tree と同一です。

2026-10-21: DRAgoWing #15 の main `5487e25add5ec084c16d4a4e4ac8a734da2ba695` を squash なしの `git subtree pull` で取り込みました。`load_overlap(..., backend="stdlib")` の明示選択・一致検証・測定を含み、既定は native のままです。prefix tree と登録SHAは一致し、研究入力・holdout履歴・研究結果は変更していません。

2026-10-20: main `e7734b3d538ff49c00a0295d21553a160ff67467`（#13: Aoi の `fetch_module.py` と `numpy_min.py` を `vendor/aoi/` に置く。#14: `dragowing/.github/workflows/` の `uses:` を full SHA に固定）を、直前の subtree merge を残したまま squash なしの `git subtree pull --prefix=dragowing` で取り込みました。merge commit の第2親はこの SHA で、`dragowing/` の tree は登録した SHA の tree と同一です。

2026-10-20: main `ec0280afb8dfdfe9ae486a4337aa736e08ff9de8`（#12: Markdown を pure-Python wheel として取得し、`shrink/numpy_min.py` で `render_md` と `load_overlap` をインストール済みの markdown / numpy なしで動かす）を squash なしの `git subtree pull --prefix=dragowing` で取り込みました。merge commit の第2親はこの SHA で、`dragowing/` の tree は登録した SHA の tree と同一です。

- DRAgoWing の最初の 28 コミットは、Aoi `a8dc4997f43236b24a23df56e21f143fa0e233d8` から `git filter-branch --subdirectory-filter dragowing` で切り出しました（先頭 `c789da2e30b33144f3110506f90f91ea579b9a6b`、tree `70424b5a2768f43633766435cc9552f77c1b2ba7` が Aoi の `dragowing/` と一致）。そのうえに子の足場（CI・LICENSE・`.gitignore`・`pyproject.toml`・`uv.lock`・`conftest.py`・`aoi_paths.py`・README の節・兄弟 import のテスト、および単独実行のためのテスト修正）を足しました。最初は `4d798e1405e14d5cdd33e0c3f8fa87b29789b9cc` に対する手組みの squash の join（#61）でしたが、2026-10-19 に、旧 `dragowing/` を消してから main `8d6163989fc2f4843412a03b465fee1cf9b3ac3c`（#3 の `--svg`、#4 の README、#5 の依存の下限）に対して `git subtree add`（`--squash` なし）で join を入れ直しました。merge commit の第2親は DRAgoWing main の head です。PR は squash/rebase せず merge commit で入れてください。
- `dragowing/` 全体（子の CI・LICENSE・`.gitignore`・`pyproject.toml`・`uv.lock`・`conftest.py` も含む）は登録した DRAgoWing の tree と同一です。`mirrored_from_parent: {"aoi_paths.py": "aoi_paths.py"}` により原本との blob/mode 一致も検査します。`min.py` は Aoi が提供し、子には置きません。
- サイクルデータ（`cycles/`）、PythDRagoras（`propositions`・`rule_search`）、QueRyu（`ask`）は Aoi に残します。子の CI は Aoi の past-pattern snapshot を SHA で取得して検証データに使い、`AOI_ROOT` と `PYTHONPATH` の `pythdragoras` と `queryu/ask` を渡して pytest を動かします。子の CI に Chrome のジョブはなく、Aoi の CI の Chrome ジョブと DRAgoWing reports ワークフローが `dragowing/` のパスを使います。Aoi の中では `dragowing/.github/` は動きません。`dragowing/conftest.py` は Aoi の pytest でも同じように `AOI_ROOT` を確かめ、パッケージ登録は何もしません。`dragowing/tests/conftest.py` と共存します。
- 同期は PythDRagoras の手順の `pythdragoras` を `dragowing`、リポジトリを DRAgoWing に読み替えます（`--squash` なし）。

## BlueProbe

2026-10-20: main `f0763c4de0a2976bb243cd7d780c8b5ae0c22ba4`（#32: `social_timeline`・`ecommerce_product`・`forum_qa`・`dashboard_grid` のプリセットと `classify_document` / `--classify`。観測のみで変換はしない）を squash なしの `git subtree pull --prefix=blueprobe` で取り込みました。実行時の依存はありません。

2026-10-20: main `af8552e869491aa900ad1010330955fd6652d766`（#31: 再エクスポートの `dom_patterns.py` を削除し、DOM パターン API は `blueprobe.py` のみ）を squash なしの `git subtree pull --prefix=blueprobe` で取り込みました。実行時の依存はありません。

2026-10-20: main `50a2846d68fcba4acbe7e4abf7fb0130de07de89`（#30: 標準ライブラリの html.parser。DOM パターン表は `blueprobe.py` にあり、`dom_patterns.py` は再エクスポート）を squash なしの `git subtree pull --prefix=blueprobe` で取り込みました。実行時の依存はありません。

2026-10-20: main `563d84488a57efd3bca2d89c97c0a72759ab8ee5`（#26 の DOM パターン）を squash なしの `git subtree pull --prefix=blueprobe` で取り込みました。QueRyu の新しい `pattern_postprocess` が `load_source("dom_patterns")` を import 時に呼ぶためです。

- BlueProbe は Aoi の [`blueprobe/`](../blueprobe/) から独立したリポジトリです。親 myon-bioinformatics の `child-heads.json` への登録は廃止し、Aoi の `child-heads.json` に移しました。Aoi と子の間では vendor lock を使いません（`vendor/`・`vendor.lock.json` は子から除く）。main `596f334198b669546a32c432422acc2eb37afeee`（#21: Aoi 側にだけあった NPB 取得元の移植と vendor カタログの除去）に対し、一度だけの join を入れました。merge commit は第2親として join を残します。PR は squash/rebase せず merge commit で入れてください。
- `blueprobe/` 全体（子の CI・LICENSE・`.gitignore`・`pyproject.toml`・`uv.lock`・`conftest.py` も含む）は登録した BlueProbe の tree と同一です。Aoi の原本を写したファイルはないので `mirrored_from_parent` は書きません。`min.py` は Aoi が提供し、子には置きません。
- サイクルデータ（`cycles/`）の fixture と QueRyu 連携は Aoi に残します。子の CI は Aoi の past-pattern snapshot を SHA で取得して検証データに使い、`PYTHONPATH` の `queryu` を渡して pytest を動かします。Aoi の中では `blueprobe/.github/` は動きません。
- 同期は PythDRagoras の手順の `pythdragoras` を `blueprobe`、リポジトリを BlueProbe に読み替えます。
