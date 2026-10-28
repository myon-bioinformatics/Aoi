# Browser.getVersion 起動診断（検証専用）

`python scripts/diagnose_dragowing_browser.py` は、Chrome / Chromium の選択と、選択済みの実行ファイルが CDP に応答するまでの問題を分けて記録する。標準ライブラリだけで動き、研究データは読まない。既存の `Chrome`、`RenderSession`、`export_draw` を使う検証用モジュールであり、本番の起動引数、再試行、タイムアウト、ブラウザ選択は変更しない。

通常の画像テストと異なり、ブラウザ不在を skip しない。指定した実行ファイル・JS がない、バージョン取得に失敗した、1 回でも試行が失敗した場合は終了コード 1。引数の構文や上限値の誤りは argparse の終了コード 2。

## 起動だけを比べる

Aoi のルートから、使用する実行ファイルの絶対パスを必ず渡す。

```sh
python -S scripts/diagnose_dragowing_browser.py \
  --chrome /usr/bin/google-chrome --runs 5 --timeout 30 \
  --output build/browser-validation/chrome-startup.json

python -S scripts/diagnose_dragowing_browser.py \
  --chrome /usr/bin/chromium --runs 5 --timeout 30 \
  --output build/browser-validation/chromium-startup.json
```

- `--chrome` は必須。環境変数 `CHROME` / `CHROMIUM` や PATH の候補へ切り替えない。
- 指定したパスで起動する。シンボリックリンクの実体は別途記録するが、実体パスに置き換えて起動しない。ラッパーが自身の名前・位置に依存する場合の挙動を保つ。
- `--version` は最初に 1 回だけ別プロセスで取得する。その成否と CDP の成否は別に記録し、`--version` が失敗しても起動試行は続ける。
- 各試行は新しいブラウザと一時プロファイルで `Browser.getVersion` の応答を待ち、閉じる。ページ描画、Plotly.js の取得、既存ユーザープロファイルの利用は行わない。
- 各試行を独立した観測として残す。失敗を自動再試行して成功に置き換えることはしない。
- 通常の cleanup 後にプロセス・reader・プロファイル・pipe が残る、または thread / fd 数が増える場合、後続試行を止める。残りは `unattempted_runs`、理由は `stopped_early_reason` に記録する。資源漏れを増やさず、正常終了に見せかけない。所有が確認できる生存ブラウザは、通常 cleanup の証拠を保存した後で kill / wait と best-effort close を行い、結果を `recovery` に分けて残す。未追跡の fd を推測して閉じることはしない。

`--timeout` の既定値は 30 秒。CDP 呼び出し、`--version`、描画時の各段階の上限であり、試行全体の wall-clock 上限ではない。既存の Chrome cleanup の待ち時間は別にかかる。起動成功後にブラウザを使い回す本番挙動とは違い、起動試行ごとに fresh process を測る。

## 任意: 同一ブラウザで 3 図 × PNG / SVG

信頼できるローカルの Plotly.js を事前に用意し、`--plotly-js` と `--evidence-dir` を両方指定する。このコマンドは JS をダウンロードせず、環境変数で指定された別の JS にもフォールバックしない。

```sh
python -S scripts/diagnose_dragowing_browser.py \
  --chrome /usr/bin/google-chrome --runs 3 --timeout 30 \
  --plotly-js /absolute/path/to/plotly.min.js \
  --evidence-dir build/browser-validation/chrome-images \
  --output build/browser-validation/chrome-render.json
```

各試行は一つの `RenderSession(offline=True)` に診断用 Chrome を渡す。固定の人工データから異なる 3 図を作り、既存の Plotly 設定・`export_draw` で PNG / SVG を各 1 回出力する。6 出力が同じ PID を使い、各出力後に page target 集合が元に戻ることを確認する。

PNG は署名・寸法（400 × 300）・チャンク CRC・画像データの展開を検査し、3 図の PNG hash が異なることを確認する。SVG は XML として解析し、SVG root、人工のタイトルと凡例があることを確認する。画像バイトのブラウザ間一致は求めない。画像は `run-001/figure-0.png` などに保存される。再実行には新しい evidence directory を使い、以前の画像を今回の成功と取り違えない。

JS の実体パス、サイズ、SHA-256 を JSON に残す。同じ bundle・Python・OS・タイムアウト・試行数で Chrome / Chromium を別々に実行すると比較しやすい。CDP の offline は描画ページのネットワークを無効にするもので、OS 全体のネットワーク分離ではない。検証のために権限制限やプロセス起動制限を迂回しない。

## JSON とログの読み方

`--output -` は標準出力へ JSON だけを書く。ファイルを指定した場合は JSON を保存し、標準出力に CDP product、成功 / 失敗数、readiness の最小 / 最大秒数、失敗段階を 1 行で出す。

主なフィールド:

- `schema_version`: この JSON 形式の版（現在 1）。`created_at` は UTC。
- `runtime`: Python 版、OS platform、CPU architecture、kernel release。ホスト名や環境変数は含まない。
- `chrome.requested_path` / `executable_path` / `resolved_path`: 指定値、実際の起動パス、シンボリックリンクを解決した実体パス。
- `chrome.version`: `--version` の出力、終了コード、所要時間、失敗情報。失敗しても trial の CDP 応答は別に確認する。
- `preflight_failure`: 実行ファイル・JS・出力先などの事前検査失敗。
- `trials[].cdp_product` / `cdp_protocol_version`: 最初の `Browser.getVersion` が返した識別情報。別の追加 readiness probe は行わない。
- `readiness_elapsed_seconds`: 起動開始から最初の `Browser.getVersion` の成功 / 失敗まで。起動 cleanup を含めない。spawn 前に失敗した場合は null。
- `readiness_transport`: 最初の readiness request の `sending_request` / `waiting_reply` / `response_received`、送信所要時間、受信 message 数。既存の send / receive に同じ引数・deadline を渡して観測するだけで、message の本文は記録しない。pipe への書込完了はブラウザが読んだ証明ではない。
- `wait_observations`: 最初の readiness request 送信直後と応答 / 失敗時（cleanup 前）の最大 2 snapshot。経過秒、UTC 時刻、観測自身の所要秒を残す。Linux の所有する未回収の子 PID について state、`wchan`、minor / major fault、user / system CPU tick、I/O の `read_bytes` / `write_bytes` だけを読む。同じ PID の 2 点の差が起動中の増分であり、I/O rate を直接測った値ではない。読めない項目は null。`wchan=0` も待機場所が特定できた意味ではない。
- `wait_observations[].pipes`: 所有する親側 CDP pipe と子の fd 3 / 4 の pipe inode、一致有無、`FIONREAD` による親 endpoint の未読 byte 数。pipe 以外のリンク先は捨て、通信内容は読まない。request の未読量は未消費の要求、response の未読量はその時点で kernel pipe に残る量であり、reader が取り込んだ部分 frame は含まない。0 byte / 0 complete message でも「一切受信していない」とは断定しない。最初の snapshot は exec helper の fd remap より前の場合があるため、初回の不一致だけで transport の欠陥とはしない。snapshot 内の各値も原子的な同時観測ではない。
- `wait_observations[].kernel_stack`: readiness が失敗した終端 snapshot だけで、自分が起動した未回収の子の `/proc/PID/stack` を 1 回読む。通常の送信直後・成功時には読まない。`symbols` は出現順の最大 32 関数名だけで、アドレス・offset・module 注釈・未知形式の行は保存しない。`status` は `ok` / `empty` / `unparseable` / `permission_denied` / `unavailable` / `invalid_encoding` / `not_running` / `unsupported`。読めない場合の `symbols` は null、読めても空・解釈不能の場合は空配列。`truncated` は byte / frame 上限による省略、`omitted_lines` は未知形式の行数であり、空や取得不能を「待機なし」と解釈しない。
- `render_elapsed_seconds` / `renders`: 描画全体と各画像の所要時間、hash、サイズ、PID、出力パス、残った page 数。起動だけの実行では描画時間は null。
- `close_elapsed_seconds`: 正常時・例外時に既存 cleanup が使った時間の合計。重複した idempotent close も含む。
- `failure`: 最初の失敗段階、例外型、bounded message、`last_cdp_method`（最後に呼んだ CDP method で、画像検証エラーなどでは失敗した操作そのものとは限らない）、失敗時の process / reader / resource / stderr snapshot。`readiness`、`session_setup`、`render.figure-0.png` などを区別する。
- `failure.process`: snapshot 時点の PID、running / exited / not_started、returncode。Linux では `/proc/<pid>/stat` の state 文字も記録する。EOF とプロセス終了には競合があるため、EOF 時の running だけではハングと断定しない。
- `cleanup`: 既存 cleanup 後のプロファイル削除、reader 終了、プロセス状態、pipe / stderr の解放。保持した reader / process の参照で確認する。
- `resources_before` / `resources_after` / `resource_delta`: Python thread 数と、利用可能なら `/proc/self/fd` の個数。fd の内容やリンク先は読まない。未対応環境の fd 数は null。
- `cleanup_failure` / `cleanup_complete`: 最初の起動・描画エラーを上書きせずに cleanup の異常も記録する。
- `passed_runs` / `failed_runs` / `unattempted_runs`: 試行結果と未実施分。試行が全て成功しても `--version` の失敗があれば全体の `ok` は false。

`stderr_tail` はファイル末尾へ seek して最大 4096 bytes だけ読む。production の例外メッセージ生成も、検証用 subclass では同じ bounded reader を通す。`Chrome.start()` が例外時に stderr と一時プロファイルを消す前に snapshot を取る。終了処理後のメッセージは capture 対象外。

wait snapshot も検証用 subclass 内だけで行う。追加 thread / sleep / CDP request / browser 起動はなく、送信後の観測は既存の deadline 内で実行する。応答・失敗までの readiness 時間は終端 snapshot の追加処理前に記録する。proc 読出しはファイルごと最大 4096 文字（wchan は 128 文字）、FD は所有する 2 endpoint と子の 3 / 4 に限定する。終了・permission 不足・未対応の場合は取得不能を null とし、ptrace、security 設定、元の起動引数や timeout を変更しない。実行ファイルの事前 hash / 全読出しも追加しない。D state や fault 増分だけで原因のファイルを特定したとは扱わない。

stack の読出しは最大 4096 bytes + 超過検出用 1 byte で、切れた末尾の行は捨てる。これはデータ量の上限であり、proc 内部の待機に厳密な wall-clock 上限を付けるものではない。既存の 8 秒の応答判定が失敗した後にだけ実行し、追加時間は終端 `sample_duration_seconds` に含める。cleanup 開始はその分遅くなる。Linux 6.17 の [proc_pid_stack](https://github.com/torvalds/linux/blob/v6.17/fs/proc/base.c) は既存の capability と ptrace access check を要求するため、所有する子でも拒否され得る。取得不能を記録して終わり、sudo / capability / ptrace / security 設定の変更や権限を変えた再試行は行わない。従来の offline job の実行方法も変更しない。

stack は主プロセスの一時点だけで、state / wchan / pipe と原子的に同時ではなく、他の Chromium thread の stack でもない。OS のメモリ・ファイル page の待機と HTML ページ読込みを区別する。待機経路が見えても特定のファイル・device・browser build の欠陥まで確定する証拠にはならない。アクセス拒否や再現しない場合は、その限界を残す。

任意の argv / 環境変数、`/proc/*/cmdline` / `environ`、ユーザーのページや研究データは集めない。ログ中の credential・URL・environment・argument に見える文字列は伏せ、長さを制限する。ただし任意の実行ファイルが出す内容を完全に秘密判定できるわけではない。信頼する実行ファイルだけを指定し、外部に共有する前に診断 JSON を確認する。

この結果は原因確定ではなく観測である。例えば process singleton socket の EPERM は実行環境の制限を示すが、別環境での断続的な `Browser.getVersion` timeout の原因まで示さない。Chrome の成功と Chromium の失敗が 1 回だけあっても、製品差と断定せず、環境・bundle・試行位置と合わせて読む。

## ブラウザなしの回帰テスト

```sh
.venv/bin/python -m pytest -c pyproject.toml -q \
  tests/test_dragowing_browser_diagnostics.py \
  dragowing/tests/test_chrome_pipe.py \
  tests/test_dragowing_browser_transport.py \
  tests/test_dragowing_browser_resources.py
```

新しいテストは deterministic な CDP peer を POSIX pipe で動かし、実 Chrome / Chromium やダウンロードを必要としない。起動成功、応答なし、途中終了、不正 JSON、spawn 失敗、`--version` 失敗、実行ファイル / JS 不在、不正 timeout、symlink 名の維持、同一 PID の 6 出力、ready / capture 失敗、stderr の bounded read、cleanup 失敗による後続停止を確認する。実ブラウザの成否は別の CI 実測として扱う。


## CI の比較条件

Aoi の `.github/workflows/browser-startup-validation.yml` は `ubuntu-24.04` / Python 3.14 で、既定では `chromium` のみを検証する。手動実行の `compare-chrome` を有効にした場合だけ `google-chrome` の互換性比較ジョブを追加する。同一系統の実行ファイル名の別名（`google-chrome-stable`、`chromium-browser`）は検索するが、系統間フォールバックはしない。必要なブラウザがなければ明示的なエラーで失敗する。

各ジョブは依存関係とローカル Plotly.js を準備した後、次の順で測る。

1. fresh profile の起動を 10 回。
2. ブラウザを明示・必須化した Aoi の全 pytest suite。
3. fresh profile の起動をもう 10 回。
4. 3 つの独立した session で、それぞれ 3 図 × PNG / SVG を検証。

JSON、JUnit、人工図の画像を artifact に 14 日間保存する。先行の診断・テストが失敗しても、準備とブラウザ選択が成功しジョブがキャンセルされていなければ後段の測定も行う。実際の製品・版・bundle hash は各結果で確認する。通常の runner user / network のまま測り、この追加ジョブは namespace、権限、security 設定を変更しない。本番のブラウザ選択や既存のネットワーク分離 CI も変更しない。

## 別に確認した resource cleanup の問題

`test_dragowing_browser_resources.py` は 2 件の既存不具合を deterministic に再現する strict xfail テストである。

- 2 本目の `os.pipe()` が EMFILE を返したとき、先に確保した pipe pair が未追跡のまま残る。
- pipe fd が 1024 以上になると `select.select` が拒否し、`close()` も同じ ValueError を繰り返して cleanup に到達しない。

両テストとも検証用に確保した資源はテスト側で回収する。strict xfail は健康な状態の assertion を残すためのもので、予想外に成功した場合は失敗になり、修正後には該当マーカーを外す必要がある。これらは別に確認した欠陥であり、元の断続的な `Browser.getVersion` timeout の根本原因と確定したわけではない。この検証 PR は本番 transport の修正を含まない。

検証コードは Aoi の `scripts/`・`tests/`・`docs/` に置き、`dragowing/` subtree は登録済みの内容を保つ。DRAgoWing の配布物・子リポジトリの同期は、この診断専用 PR には含めない。

## Chromium への統一

通常の offline export CI も Chromium を明示的に選択する。既存の `chrome-export` job ID、JUnit / artifact 名は集計との互換性のため保つ。OS のネットワーク分離、起動引数、タイムアウト、再試行は変更しない。診断も同じ選択済み実行ファイルで前後 10 回の起動と 3 session × 6 画像を測定する。実行ファイル・CDP の版、Plotly.js の hash、段階別時間と cleanup を合わせて確認する。

本番ライブラリの既定選択は DRAgoWing の原本で変更してから、通常の subtree 同期と配布物生成で Aoi に取り込む。この Aoi 側 CI 変更だけでは、まだ取り込まれていない DRAgoWing や既存の配布物が変わったとは扱わない。Chromium への統一は元の 30 秒 timeout の修正完了を意味せず、2 件の cleanup 不具合も別件として残す。

## 最初の実ブラウザ起動を、通常 / offline の同条件で観測する

`first-start-context` は通常ユーザー・通常ネットワークの `normal` と、既存 offline CI と同じ `sudo unshare --net --` の `offline` を、それぞれ独立した新しい runner job で実行する。どちらも Ubuntu 24.04 / Python 3.14、同じ依存・Plotly.js 準備、同じ Chromium 選択と次の module 順序を使う。

1. `dragowing/tests/test_chrome_pipe.py`
2. `dragowing/tests/test_render.py`
3. `dragowing/tests/test_export.py`
4. `dragowing/tests/test_plotly_cdn.py`

最初の実 Chromium は既存の `test_stalled_dbus_does_not_block_browser_get_version` で起動する。先に full browser の診断・描画・warmup を実行しない。通常の選択段階での `--version` と synthetic pipe peer は両方に残す。そのため `first_in_pytest` は「この pytest の最初の実ブラウザ起動」であり、OS / ディスク cache が完全に cold であるという意味ではない。後続の fresh profile は `subsequent_in_pytest` として分け、最初の失敗を後続成功で置き換えない。別 job の既存 10 回事前起動つき全 suite は、warmup のある別条件として読む。

追加するのは Aoi 専用の opt-in plugin だけで、元のテスト・本番 subtree は編集しない。

```sh
.venv/bin/python -m pytest -c pyproject.toml -q \
  -p scripts.observe_dragowing_startup \
  --browser-startup-evidence=build/startup-context/actual-tests.json \
  dragowing/tests/test_chrome_pipe.py dragowing/tests/test_render.py \
  dragowing/tests/test_export.py dragowing/tests/test_plotly_cdn.py
```

plugin は `chrome_executable` fixture を使う実ブラウザテストだけで `RenderSession` に診断用 subclass を渡す。起動引数・環境生成・通信・deadline・cleanup は既存処理に委譲する。追加起動、追加 CDP probe、`--version`、retry は行わない。既存の launch=8 と全体 <8 秒の assertion も変更せず、JSON の書込はテストの teardown 後に行う。観測用の小さな Python 処理の追加はあるので、元の必須 offline job は変更せず独立した baseline として残す。

`actual-tests.json` には各 test の pytest setup / call / teardown outcome、起動順序、実際の timeout、最初の readiness の時間・送信/待機段階、CDP product、bounded / redacted stderr、cleanup を保存する。意図的に CDP error を起こすテストもあるため、`failure` があることだけで test failure や startup failure と判定しない。pytest outcome、readiness phase、last CDP method を併せて読む。二度目の `Browser.getVersion` は最初の readiness 計測を上書きしない。

runtime は Python / OS、uid / euid、network namespace inode、interface 数、loopback の有無だけを追加する。任意の environment、argv、ネットワークアドレス、ページ内容は収集しない。namespace inode は別 runner 間の共通 ID ではなく、interface 数も単独で isolation の完全な証明ではない。normal と offline の差はユーザーとネットワーク分離を合わせた条件差であり、単独の原因を切り分けた実験ではない。

JSON、JUnit、人工画像は成功 / 失敗の両方で `browser-first-start-{normal,offline}-py3.14` artifact に 14 日間保存する。8 秒や元の 30 秒 timeout の解消を示す修正ではなく、失敗した位置と条件を残す診断である。既存の失敗記録は保持し、transport / cleanup の修正や timeout 延長には進まない。

## 2026-10-28: head 7a613a6 の成功・失敗比較

対象は PR #122、[startup run 40486652453](https://github.com/myon-bioinformatics/Aoi/actions/runs/40486652453) と [CI run 40486653033](https://github.com/myon-bioinformatics/Aoi/actions/runs/40486653033)。以下は保存 JSON と実ジョブログの観測であり、修正後の成功を示す表ではない。

|条件|Browser.getVersion まで|送信時間|終端 state / wchan|major fault 増分|read_bytes 増分|終端 request 未読量|
|---|---:|---:|---|---:|---:|---:|
|normal 初回・8秒失敗|8.001813秒|0.000027797秒|D / folio_wait_bit_common|271|26,521,600|51 bytes|
|offline 初回・8秒失敗|8.001502秒|0.000023655秒|D / folio_wait_bit_common|1,085|129,302,528|51 bytes|
|成功ジョブ before.json 初回|11.161142秒|0.000041298秒|R / 0|1,859|163,250,176|0 bytes|
|成功ジョブ after.json 先頭|0.262038秒|0.000045225秒|R / 0|0|0|0 bytes|

出典 artifact: normal `12724803971`、offline `12725586774`、成功ジョブ `12726326049`。別 runner 間の比較であり、同一ホストの制御実験ではない。read_bytes は親 PID のカウンタで、子孫の全 I/O 量やストレージ latency の直接計測ではない。

### 確認済み

- 初回失敗の request_sent snapshot は起動開始から normal 0.000820秒、offline 0.000654秒。Popen と reader 開始、要求の pipe 書込みまでが8秒を消費したわけではない。Popen の返却は実行ファイル全体のロード完了を意味しない。
- 両失敗の終端では CDP の親子 pipe inode は一致し、要求51 bytesが未消費、response pipe は0 bytes、完成 message受信数は0。主な待ちは要求送信後・最初の CDP 応答前にある。reader 内の部分 frame量は測っていない。
- offline の kernel stack は `folio_wait_bit_common → filemap_fault → ... → exc_page_fault`。ファイル-backed page fault待ちが失敗時に存在する。normal の stack は permission_denied だが、D state と同じ wchan は取得済み。
- 同じブラウザ版の成功初回にも多数のmajor faultと読み込みがあり、11.161秒を要した。後続は0.222秒程度、suite後は0.242〜0.280秒。成功ジョブは診断起動10回をsuiteの前に実施しており、初回8秒テストの成功証拠にはならない。
- Python 3.11通常CIは画像生成前の `RenderSession.__enter__ → Chrome.start → Browser.getVersion` で30秒失敗。PlotlyのJS実行やPNG/SVG生成がタイムアウトしたわけではない。通常CIには当時wait snapshotがなく、同じpage fault原因とまでは確認できない。
- 成功経路にもno-bus.sockへの接続失敗ログが出る。これだけでD-Bus待ちを原因と断定できない。

### 未解明と今回の変更

待っているファイル、page cache / runnerストレージの状態、待機時間の内訳、Python 3.11失敗との共通原因は未特定。D stateの1点観測だけで8秒全体が同じwaitだったとは言わない。根本修正の根拠がないためproduction transportは変更しない。

検証専用の `spawn_elapsed_seconds` を追加し、既存 `_spawn` の所要時間を成功・失敗とも記録する。これはPython exec helperをPopenして親側pipeを設定するまでで、helperのexec完了やChromium内の初期化完了ではない。追加プロセス、追加CDP要求、再試行、事前ファイル読出し、timeout延長はない。

通常CIのPython 3.11〜3.15にも既存のopt-in observerを有効化し、`browser-observation-py<version>` artifactへ実テストのsnapshotを保存する。Plotly用fixtureはchrome_executableに依存するため、この画像出力テストも観測対象になる。normal/offline専用ジョブの順序・条件・8秒assertは維持する。研究データ・事前宣言・判定条件は変更しない。

ローカル検証（2026-10-28、Python 3.12.14）: 診断・pipeの対象テストは79 passed / 2 deselected。除外2件は実子PIDのproc情報・fd linkを読めることを前提とし、本環境では取得不能。同じ2件が変更前headでも失敗することを確認した。render/export/CDNを含む実行は101 passed / 11 skipped / 上記2 failed。Chromium本体が本環境にないため実画像出力、normal/offline初回、Python 3.11実ブラウザの再検証はGitHub CIが必要で、ローカル成功とは報告しない。

## 91aadb9 のCI再検証（2026-10-28）

`eb01906` と同一treeをGitHub接続経由で反映したheadが `91aadb97b8350f2b68ce72e1ab521284ad615747`。Draftは維持。

- [初回専用run 40619953090](https://github.com/myon-bioinformatics/Aoi/actions/runs/40619953090): normalは1 failed / 44 passed / 1 skipped、offlineは2 failed / 43 passed / 1 skipped。どちらも8秒のstalled_dbusテストでBrowser.getVersionを待って失敗。offlineは次の静的SVGテストも30秒のBrowser.getVersion待ちで失敗した。
- normal初回: spawn 0.000631秒、readiness 8.002050秒、送信 0.000031537秒。終端D / folio_wait_bit_common、major fault 1,477、read_bytes 148,111,360。要求は消費済み（0 bytes）で、前回の未消費51 bytesとは異なる。全失敗を「要求を読む前」と一般化できない。
- offline初回: spawn 0.000419秒、readiness 8.001454秒、送信 0.000024467秒。終端D / folio_wait_bit_common、major fault 265、read_bytes 25,567,232、要求未消費51 bytes。kernel stackは再びfilemap_fault。次の静的SVGテストもspawn 0.000460秒、readiness 30.001123秒、D / filemap_faultで、要求は消費済み。
- [通常CI run 40619953498](https://github.com/myon-bioinformatics/Aoi/actions/runs/40619953498): Python 3.11〜3.15は各3,148 passed / 39 skipped / 2 xfailed、失敗は各1件の依存調査一覧のstale検査のみ。既存offline画像出力、actionlintも成功。
- Python 3.11の `test_export_draw_plotly_three_figures_in_one_session` はsetup/call/teardownすべてpassed。保存artifact `12787446644` ではspawn 0.000580秒、readiness 19.907795秒、failureなし。今回の成功だけで起動遅延が解消したとはいえない。
- normal証拠artifact `12787490101`、offline証拠artifact `12786467854`。ファイルI/O待ちの関与は再確認できたが、待っているファイル・ストレージ・Python版との因果関係は未確定。

一覧staleは追加回帰テストによる `pytest.mark.parametrize` / `pytest.raises` の使用数各+1が原因。`survey_third_party.py --json`で生成メタデータだけ再生成し、関連テスト8件成功。研究データ・依存パッケージ・判定条件は変更しない。

事前診断付きStartup and exportジョブも完了。suiteは同じ一覧staleの1 failed / 3,148 passedのみ。診断はsuite前10/10成功（readiness 0.227〜17.611秒）、suite後10/10成功（0.238〜0.287秒）、3セッション×3図×PNG/SVGの出力も3/3成功（readiness 0.239〜0.255秒）。この成功は初回8秒失敗を取り消すものではない。
