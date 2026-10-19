# NagoyAction

> 研究を、続けられる仕組みに。

![NagoyAction](https://github.com/myon-bioinformatics/Aoi/raw/main/docs/images/nagoyaction.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

## 概要

パイプラインを TOML に一度だけ書き、**ローカルでも GitHub Actions でも同じコマンド**で動かす。
データを外に出せない案件では、同じ定義をローカルで実行すればよい。

- `doctor`：Python の版、必須ツール（例: git, uv）、任意ツール（例: gh）、オフライン実行に必要な成果物の有無を確認する（`-v` / `--verbose` で詳細情報、`--json` で JSON 出力、改善案を表示）。足りなければ終了コード1で、実行前に止まる
- `show`：パイプラインの構造（変数・ステップ・コマンド・出力・ネットワーク要求）を表示する（`--json` で JSON 出力）
- `run`：doctor のあと手順を順に実行し、`--receipt` に受領記録（JSONL）を残す。失敗した手順で止まる
- 手順はシェルを通さず、引数の配列で実行する
- 標準ライブラリだけ（Python 3.11+）。このファイル1つをコピーすれば他のリポジトリでも使える

[Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクト [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) から独立したリポジトリ（下の「Aoi との関係」）。

## インストールと使い方

インストールは要らない。Python 3.11 以上の標準ライブラリだけで動く。

```bash
python nagoyaction.py doctor <pipeline.toml>            # 実行前の確認（-v / --verbose / --json も可）
python nagoyaction.py show   <pipeline.toml>            # パイプライン構造の表示（--json も可）
python nagoyaction.py run    <pipeline.toml>            # 実行
python nagoyaction.py run    <pipeline.toml> --offline  # 取得しない
python nagoyaction.py run    <pipeline.toml> --dry-run  # 何をするかだけ表示
```

パイプラインの TOML は `name`・`root`・`[requires]`（Python の版・ツール）・`[[step]]`（`name`・引数の配列 `run`・`network`・`outputs`）で書く。例は `pipelines/research.toml`・`pipelines/inbox.toml`。

GitHub Actions のワークフローは、このコマンドを呼ぶだけにする（例: `.github/workflows/cycle-c001.yml`）。
組織共通の再利用ワークフロー（actionlint など）は `myon-bioinformatics/myon-bioinformatics` のものを使う。
他のリポジトリから共有モジュールを取り込むときは、同リポジトリの `vendor_sync.py`（SHA 固定）を使う。

## 構成

| ファイル | 中身 |
|---|---|
| `nagoyaction.py` | パイプラインの事前確認（`doctor`）と実行（`run`） |
| `pipelines/` | パイプラインの定義（`research.toml`・`inbox.toml`） |
| `linkcheck.py` | Markdown のリンクと画像の参照先を確かめる（下の「リンク確認」） |
| `inbox/inbox.py`・`docs/inbox.md` | 質問受付 |
| `research_digest.py`・`docs/research-digest.md` | 研究記録（R*.md）と命題の判定の索引（ネットワーク・LLM 不要） |
| `publication_gate.py`・`ghi_execution.py`・`PUBLICATION.md` | 公開前の証跡の確認（オフライン）と、実行中の GitHub Actions の照合 |
| `annual_history_report.py` | 年間の監査結果と架空のモデル検証の結果を分けて並べる |
| `containers/` | ローカル LLM のコンテナ（未接続。下の「ローカル LLM のコンテナ」） |
| `tests/` | pytest（Aoi の中で動かす。下の「テスト」） |

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

## テスト

手順やテストは Aoi の直下（`cycles/`・`queryu/`・`sakanalytics/`・`blueprobe/`・`vendor/`・`scripts/`・`docs/`）を相対パスで使う。単独ではテストしない。CI は Aoi を固定 SHA で checkout し、その `nagoyaction/` をこのリポジトリの tree に置き換えて、Aoi の設定で `nagoyaction/tests` を動かす（`.github/workflows/ci.yml` の `AOI_SHA`）。

```sh
git clone https://github.com/myon-bioinformatics/Aoi.git ../Aoi
git -C ../Aoi checkout 0a1751a60ac64708d679f22950aa2b14cf688efd
rm -rf ../Aoi/nagoyaction && mkdir ../Aoi/nagoyaction && git archive HEAD | tar -x -C ../Aoi/nagoyaction
git -C ../Aoi add -A nagoyaction
cd ../Aoi && uv run --locked pytest -q -c pyproject.toml nagoyaction/tests
```

CI は Python 3.11–3.15 で同じことをする。

## Aoi との関係

[Aoi](https://github.com/myon-bioinformatics/Aoi) の [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) から独立したリポジトリ。直接の親は Aoi で、`nagoyaction/` との差分は Aoi 側で確かめる。
最初の 49 コミットは Aoi `0a1751a60ac64708d679f22950aa2b14cf688efd` の `nagoyaction/` を `git filter-branch --subdirectory-filter nagoyaction` で履歴ごと切り出したもの（先頭 `b35707b877a92fd088db06f15b87d0e72158fc27`、tree `1537879773093a5350a17ca657fbdf89f6a57e72`）。
Aoi の [`child-heads.json`](https://github.com/myon-bioinformatics/Aoi/blob/main/child-heads.json) に登録されている（手順の全体は Aoi の [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md)）。

- `min.py` はここには置かない（Aoi が提供する）
- Aoi との同期: Aoi 側で一度だけ `git subtree add` をして履歴をつなぎ、そのあとは subtree で同期する。Aoi と NagoyAction の間では vendor lock を使わない
- この README のコマンド例の `nagoyaction/…`・`cycles/…` は、Aoi のルートから見た場所を指す（Aoi の中の文書へのリンクは GitHub の URL で書く）

## 関連サブプロジェクト

親の [Aoi](https://github.com/myon-bioinformatics/Aoi) のサブプロジェクトは、それぞれ独立したリポジトリになっています。Aoi の中の場所（subtree）とあわせて載せます。一覧と登録の詳細は Aoi の [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md) です。

| リポジトリ | Aoi の中の場所 | 役割 |
|---|---|---|
| [BlueProbe](https://github.com/myon-bioinformatics/BlueProbe) | [`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe) | 観測と抽出（保存した HTML/CSS/DOM を読み、何があるかを記録する） |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | [`queryu/`](https://github.com/myon-bioinformatics/Aoi/tree/main/queryu) | 取得と観測データセットの作成（来歴つきのキャッシュ） |
| [sakanalytics](https://github.com/myon-bioinformatics/sakanalytics) | [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) | 観測データからの指標と統計（チーム×シーズンの指標、残り試合の見通し） |
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | [`pythdragoras/`](https://github.com/myon-bioinformatics/Aoi/tree/main/pythdragoras) | 説明の検証（命題・反例・異議あり） |
| **NagoyAction**（このリポジトリ） | [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) | パイプラインの実行と自動化（同じ定義をローカルと GitHub Actions で） |
| [DRAgoWing](https://github.com/myon-bioinformatics/DRAgoWing) | [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) | 図とレポート（Plotly.js の HTML、四つの形の表） |

## ライセンス

MIT License（[LICENSE](LICENSE)）。Aoi の `LICENSE` と同じ内容です。

---

# Aoi の研究サイクル（中日・NPB）での使い方

Aoi のルートで、c001（中日）のパイプラインを動かす例。

```bash
python nagoyaction/nagoyaction.py doctor cycles/c001-chunichi/pipeline.toml            # 実行前の確認
python nagoyaction/nagoyaction.py show   cycles/c001-chunichi/pipeline.toml            # 構造の表示
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml            # 実行
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml --offline  # 取得しない
python nagoyaction/nagoyaction.py run    cycles/c001-chunichi/pipeline.toml --dry-run  # 何をするかだけ表示
```
