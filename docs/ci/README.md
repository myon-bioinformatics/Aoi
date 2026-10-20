# CI

実行定義は `.github/workflows/ci.yml`。

- **Aoi**: 実行時に `git ls-remote https://github.com/myon-bioinformatics/Aoi refs/heads/main` で main の SHA を解決し、公開ページの repository id を照合してから `.test-deps/aoi` に checkout する。解決した SHA はジョブサマリに残す。`workflow_dispatch` の `aoi_ref` で ref を上書きできる。コミット SHA はファイルに固定しない。
- **mcp-toolcall-lab**: `LAB_SHA` は README が固定スナップショットとして扱う意図的な fixture pin。この照合はどのイベントでも失敗にする。
- **ソースハッシュ**: 浮動のソースハッシュ照合を足す場合、`pull_request` では報告のみ、`main` への push と `schedule` では失敗にする。Aoi のソースハッシュは記録しない。
- **JUnit XML**: `pytest -q --junitxml=reports/junit.xml`、artifact 名 `junit-py<python>`、保持 14 日。集約は組織親の `reusable-junit-identity.yml`。
- **lint**: ruff は足さない。`python -m compileall` で構文だけ確かめる。
- **実行時**: 標準ライブラリのみ。依存の上限は置かない。
