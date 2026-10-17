# CI の提案

`ci.yml.proposed` を `.github/workflows/ci.yml` として置く想定（このリポジトリの push 権限では workflow を書けないため、ここに置く）。

各リポジトリとの揃え方:

- **JUnit XML**: Aoi と同じく `pytest -q --junitxml=build/test-results/pytest-<python>.xml`、artifact 名 `junit-py<python>`、
  保持 14 日。集約は組織親リポジトリの `reusable-junit-identity.yml`（`.github/workflows/ci.yml` の workflow ピンと同じ SHA）
  - 他リポジトリの出力先は `reports/junit.xml`・`build/junit/`・`test-results/` などに分かれている。BlueProbe は出自の Aoi に合わせた
- **lint**: 調べた公開リポジトリに ruff などの lint 設定は見つからなかった。BlueProbe でも足さない（`python -m compileall` で構文だけ確かめる、Aoi と同じ）
- **vendor**: ルートの `vendor.lock.json`（`vendor/README.md` に背景・取り込まなかったものの一覧）
