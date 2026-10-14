# vendor/

myon-bioinformatics の公開・非アーカイブのリポジトリにある `vendor/` 配下から、
**単一ファイル・標準ライブラリのみ**の Python モジュールを、使う・使わないに関わらず置いている。
各ファイルの先頭に取り込み元（リポジトリ・コミット SHA・パス）を書いた。編集せず、更新は取り込み直す。
上流のリポジトリがあるものは上流から、ないものは vendor していたリポジトリから取った。
BlueProbe 本体はこれらを import しない（`pythonpath` にも入れていない）。

| ファイル | 取り込み元 | パス | コミット |
|---|---|---|---|
| `ascii_artist.py` | [ascii_artist](https://github.com/myon-bioinformatics/ascii_artist) | `ascii_artist.py` | `20a192da70e6` |
| `browser_evidence.py` | [Ironmate](https://github.com/myon-bioinformatics/Ironmate) | `vendor/browser_evidence.py` | `9643e2eae1c6` |
| `check_evidence.py` | [Err-o-RoadRunner](https://github.com/myon-bioinformatics/Err-o-RoadRunner) | `vendor/check_evidence.py` | `13c089742514` |
| `check_png.py` | [Err-o-RoadRunner](https://github.com/myon-bioinformatics/Err-o-RoadRunner) | `vendor/check_png.py` | `13c089742514` |
| `ci_status.py` | [Ironmate](https://github.com/myon-bioinformatics/Ironmate) | `vendor/ci_status.py` | `9643e2eae1c6` |
| `cli_args.py` | [cli_args](https://github.com/myon-bioinformatics/cli_args) | `cli_args.py` | `6317485625ac` |
| `gh_identity.py` | [gh_identity](https://github.com/myon-bioinformatics/gh_identity) | `gh_identity.py` | `c6b52a29d8cd` |
| `gh_ops.py` | [Err-o-RoadRunner](https://github.com/myon-bioinformatics/Err-o-RoadRunner) | `vendor/gh_ops.py` | `13c089742514` |
| `gh_workflow.py` | [Ironmate](https://github.com/myon-bioinformatics/Ironmate) | `vendor/gh_workflow.py` | `9643e2eae1c6` |
| `git_inspector.py` | [Ironmate](https://github.com/myon-bioinformatics/Ironmate) | `vendor/git_inspector.py` | `9643e2eae1c6` |
| `github_public_resolver.py` | [ascii_artist](https://github.com/myon-bioinformatics/ascii_artist) | `vendor/github_public_resolver.py` | `20a192da70e6` |
| `jsonl_digest.py` | [Err-o-RoadRunner](https://github.com/myon-bioinformatics/Err-o-RoadRunner) | `vendor/jsonl_digest.py` | `13c089742514` |
| `main.py` | [Ironmate](https://github.com/myon-bioinformatics/Ironmate) | `vendor/main.py` | `9643e2eae1c6` |
| `markdown.py` | [markdown](https://github.com/myon-bioinformatics/markdown) | `markdown.py` | `aa5bccfcaf11` |
| `nvd_nist_known_vulns.py` | [nvd_nist_known_vulns](https://github.com/myon-bioinformatics/nvd_nist_known_vulns) | `nvd_nist_known_vulns.py` | `cc85b8263c15` |
| `python_artifact_provenance.py` | [ascii_artist](https://github.com/myon-bioinformatics/ascii_artist) | `vendor/python_artifact_provenance.py` | `20a192da70e6` |
| `repository_metadata_contract.py` | [Err-o-RoadRunner](https://github.com/myon-bioinformatics/Err-o-RoadRunner) | `vendor/repository_metadata_contract.py` | `13c089742514` |
| `vendor_sync.py` | [Ironmate](https://github.com/myon-bioinformatics/Ironmate) | `vendor/vendor_sync.py` | `9643e2eae1c6` |
| `xprobe.py` | [xprobe](https://github.com/myon-bioinformatics/xprobe) | `xprobe.py` | `db770a438b7f` |
| `yourself.py` | [yourself](https://github.com/myon-bioinformatics/yourself) | `yourself.py` | `0da9a5b19eb0` |

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
