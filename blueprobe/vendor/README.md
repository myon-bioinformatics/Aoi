# vendor/

myon-bioinformatics の公開・非アーカイブのリポジトリにある `vendor/` 配下から、
**単一ファイル・標準ライブラリのみ**の Python モジュールを、使う・使わないに関わらず置いている。
取り込み元（リポジトリ・コミット SHA・パス）とバイト列はルートの [`vendor.lock.json`](../vendor.lock.json)（`vendor-lock/1`）で固定する。編集せず、更新は lock を書き換えて取り込み直す。
本来の置き場（上流）があるものは上流から、上流から消えたものは vendor していたリポジトリから取った。
BlueProbe 本体はこれらを import しない（`pythonpath` にも入れていない）。

## 取り込まなかったもの

| ファイル | 見つけた所 | 理由 |
|---|---|---|
| `LINENotifyAPI_Template.py` | Ironmate | 標準ライブラリ以外: requests |
| `__init__.py` | Ironmate | パッケージ用の空ファイル（モジュールではない） |
| `audio_any2any_gui.py` | audio_any2any_gui | 標準ライブラリ以外: FreeSimpleGUI, PySimpleGUI |
| `convert_img_fmt_to_webp(CUI).py` | Ironmate | 標準ライブラリ以外: PIL |
| `convert_img_fmt_to_webp(GUI).py` | Ironmate | 標準ライブラリ以外: PIL, PySimpleGUI |
| `cumlative_usage.py` | Ironmate | 標準ライブラリ以外: matplotlib, numpy, scipy |
| `github_api_template.py` | Ironmate | 標準ライブラリ以外: requests |
| `html_snapshot.py` | myon-bioinformatics.github.io | css_inspect への相対 import（複数ファイルのパッケージ） |
| `image_ext_converter_gui.py` | image_ext_converter_gui | 標準ライブラリ以外: FreeSimpleGUI, PIL, PySimpleGUI, pillow_avif, pillow_heif |
| `niconico_search_api_template.py` | Ironmate | 標準ライブラリ以外: requests |
| `oci-cost-analysis.py` | Ironmate | 標準ライブラリ以外: pandas |
| `python3nmap_gui.py` | Ironmate | 標準ライブラリ以外: FreeSimpleGUI, nmap3 |
| `qiita_api_template.py` | Ironmate | 標準ライブラリ以外: requests |
| `repository_metadata_generator.py` | Err-o-RoadRunner | repository_metadata_contract に依存（単一ファイルで完結しない） |
| `scapy_gui.py` | Ironmate | 標準ライブラリ以外: FreeSimpleGUI, PySimpleGUI, fastapi, scapy, uvicorn |
| `vendor_catalog.py` | Ironmate | vendor_sync に依存 |
| `vendor_stage.py` | Ironmate | vendor_sync に依存 |
| `video2audio_gui.py` | video2audio_gui | 標準ライブラリ以外: FreeSimpleGUI, PySimpleGUI |
| `video_to_image_gui.py` | video_to_image_gui | 標準ライブラリ以外: FreeSimpleGUI, PySimpleGUI |
| `web_ui.py` | web-ui | css/・js/ の資産と組で使う複数ファイル構成 |
| `xprobe_pytest.py` | nvd_nist_known_vulns | 標準ライブラリ以外: pytest |
| `main.py` | Ironmate | アプリ内部の HTTP サーバのつなぎ（独立モジュールではない） |
| `ci_status.py` | Ironmate（上流 myon-bioinformatics） | 読み取り専用の CI 状態は `gh_ops.py` と重複。`vendor/gh_identity.py` を相対パスで読む前提 |
| `gh_workflow.py` | Ironmate（上流 myon-bioinformatics） | GitHub Actions 操作は `gh_ops.py`（親の正規ツール）と重複。gh CLI と隣の gh_identity 前提 |
| `check_png.py` | Err-o-RoadRunner（上流 browser-test-kit） | PNG 検証は `browser_evidence.py` と重複 |
| `git_inspector.py` | myon-bioinformatics | gh_identity に吸収済み（c26198f, #62）。親の版は gh_identity の `git_*` への互換 shim のみ。旧い完全版（Ironmate・browser-test-kit・ascii_artist など）は古いコピー |
| `repository_metadata_contract.py` | Err-o-RoadRunner（本来 Ironmate） | 上流から削除済み（Ironmate c05cb13, #81）。gh_identity の `repository_metadata_v1` / v2 が後継 |
| `python_artifact_provenance.py` | ascii_artist（本来 Ironmate） | 上流から削除済み（Ironmate c05cb13, #81） |
| `vendor_sync.py` | myon-bioinformatics | 親リポジトリの vendoring ツール群（`vendor_*.py`）の中核。BlueProbe の対象外 |
| `gh_ops.py` | myon-bioinformatics | 親リポジトリの正規ツール（parent-owned）。PR 読み取り等は gh_identity へ委譲中 |
