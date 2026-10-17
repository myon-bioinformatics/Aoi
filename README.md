# NagoyAction

> 研究を、続けられる仕組みに。

![NagoyAction](../docs/images/nagoyaction.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

パイプラインを TOML に一度だけ書き、**ローカルでも GitHub Actions でも同じコマンド**で動かす。
データを外に出せない案件では、同じ定義をローカルで実行すればよい。

## このリポジトリについて

[Aoi](https://github.com/myon-bioinformatics/Aoi) の `nagoyaction/` から独立したリポジトリ。直接の親は Aoi で、`nagoyaction/` との差分は Aoi 側で確かめる。
最初の 49 コミットは Aoi `0a1751a60ac64708d679f22950aa2b14cf688efd` の `nagoyaction/` を `git filter-branch --subdirectory-filter nagoyaction` で履歴ごと切り出したもの（先頭 `b35707b877a92fd088db06f15b87d0e72158fc27`、tree `1537879773093a5350a17ca657fbdf89f6a57e72`）。

- 手順やテストは Aoi の直下（`cycles/`・`queryu/`・`sakanalytics/`・`blueprobe/`・`vendor/`・`scripts/`・`docs/`）を相対パスで使う。単独ではテストしない。CI は Aoi を固定 SHA で checkout し、その `nagoyaction/` をこのリポジトリの tree に置き換えて、Aoi の設定で `nagoyaction/tests` を動かす
- `min.py` はここには置かない（Aoi が提供する）
- Aoi との同期: Aoi 側で一度だけ `git subtree add` をして履歴をつなぎ、そのあとは subtree で同期する。Aoi と NagoyAction の間では vendor lock を使わない
- この README のリンクのうち `../` で始まるものと、コマンド例の `nagoyaction/…`・`cycles/…` は Aoi の中の場所を指す

```sh
git clone https://github.com/myon-bioinformatics/Aoi.git ../Aoi
git -C ../Aoi checkout 0a1751a60ac64708d679f22950aa2b14cf688efd
rm -rf ../Aoi/nagoyaction && mkdir ../Aoi/nagoyaction && git archive HEAD | tar -x -C ../Aoi/nagoyaction
git -C ../Aoi add -A nagoyaction
cd ../Aoi && uv run --locked pytest -q -c pyproject.toml nagoyaction/tests
```

```bash
python nagoyaction/nagoyaction.py doctor cycles/c001-chunichi/pipeline.toml            # 実行前の確認
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml            # 実行
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml --offline  # 取得しない
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml --dry-run  # 何をするかだけ表示
```

- `doctor`：Python の版、必須ツール（例: git, uv）、任意ツール（例: gh）、オフライン実行に必要な成果物の有無を確認する。足りなければ終了コード1で、実行前に止まる
- `run`：doctor のあと手順を順に実行し、`--receipt` に受領記録（JSONL）を残す。失敗した手順で止まる
- 手順はシェルを通さず、引数の配列で実行する
- 標準ライブラリだけ（Python 3.11+）。このファイル1つをコピーすれば他のリポジトリでも使える

GitHub Actions のワークフローは、このコマンドを呼ぶだけにする（例: `.github/workflows/cycle-c001.yml`）。
組織共通の再利用ワークフロー（actionlint など）は `myon-bioinformatics/myon-bioinformatics` のものを使う。
他のリポジトリから共有モジュールを取り込むときは、同リポジトリの `vendor_sync.py`（SHA 固定）を使う。

## リンク確認（`linkcheck.py`）

```bash
python nagoyaction/linkcheck.py                                    # push 前: git 登録済み・大文字小文字一致で照合
python nagoyaction/linkcheck.py --remote OWNER/REPO --ref BRANCH   # push 後: そのブランチに実在するか（gh api）
python nagoyaction/linkcheck.py --external                         # http(s) も確認（404/410 だけ失敗）
```

GitHub は大文字小文字を区別するので、手元で開けても GitHub では 404 になることがある（例: `genesis.md` と `GENESIS.md`）。
`git add` を忘れたファイルも、手元にはあるが GitHub にはないので失敗にする。CI では両方を実行する。

## ローカル LLM のコンテナ（未接続）

`containers/llama.py` と `containers/llama.compose.yml` は、#48 で消えた `NagoyAction/containers/` を戻したもの。
公式の llama.cpp server イメージ（digest 固定）と、SHA-256 で確かめたモデルを使い、127.0.0.1 だけで待ち受ける。
今の `pipelines/inbox.toml` と `inbox/inbox.py` からは呼ばない（ローカル LLM の連携は main への最初の展開から外してある）。
テストは `tests/test_llama_container.py`（ネットワークなし）。
