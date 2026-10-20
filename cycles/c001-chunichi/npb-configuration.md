# 親AoiのNPB設定と呼び出し

`aoi_npb.py` が球団名・表示順・カレンダーの月キー・年間監査規則・確認済みCS規則を持つ。`aoi_paths.py` が結果ref・サイクル・結果パスを解決する。子の汎用APIには、これらを明示して渡す。

Aoiのルートから実行する。下記は再実行用の手順であり、この統合では取得・研究の再計算・成果の再生成は実行していない。

```sh
# QueRyu: NPB球団表、サイクル、結果パスを渡して保存済み結果へ問い合わせる
python -S aoi_paths.py ask "中日が判例の命題" --json
# --results DIR / --cycle-dir DIR で明示できる。結果refが未配置なら別の結果へ代替しない。

# QueRyu: 月キーを共通設定から渡す。--plan は取得も観測ファイルの更新もしない
uv run --locked python aoi_npb.py calendar --years 2013-2026 \
  --cache data/raw/npb_calendar --plan

# DRAgoWing: 中日を先頭にしたNPB球団順を渡す。保存済み結果を読むだけ
uv run --locked python aoi_npb.py draw --results cycles/c001-chunichi/outputs --out build/dragowing

# SakAnalytics: NPBのリーグ数・球団数・率・対戦列の監査規則を渡す
python -S aoi_npb.py annual-audit \
  --observations data/observations/npb_team_annual/records.jsonl --years 2013-2026 \
  --baseline cycles/c001-chunichi/outputs/season.jsonl \
  --out build/annual-audit.json --annual-out build/annual.jsonl
```

各wrapperは子の終了コードを返す。明示的な子CLI引数はNPB既定値より優先される。別用途では子CLI/APIを直接使い、その用途の設定を渡せる。外部CLIで使う設定だけを書き出す場合は `python -S aoi_npb.py teams --out build/teams.json` または `python -S aoi_npb.py annual-audit-rules --out build/rules.json` を使う。

NPB年間キャッシュの選択・照合は親の `annual_scope.py`、2022年の検証は `scripts/season_verify_2022.py` に移動した。NagoyActionのinboxは親の球団表を読み、キャッシュ指紋にも `aoi_npb.py` を含める。年間集約も同じ親監査規則を使う。

研究記録R28・R29のコマンドは当時の記録として保持する。現在のAPIで再実行するときは、`sakanalytics/synthetic_rule_discovery.py` の `discover` / `evaluate` に `--cycle-dir cycles/c001-chunichi`（または明示的な `--propositions`）を追加し、`sakanalytics/league_laboratory.py` にも `--cycle-dir cycles/c001-chunichi` を渡す。研究を再実行するときの判断と、この設定統合は別である。

親で対象を絞ってテストするときは、子のpyprojectを選ばせず `uv run --locked pytest -c pyproject.toml pythdragoras/tests` のように親の設定を明示する。親conftestが `AOI_ROOT` とNPB球団表を渡す。単独子リポジトリのテストでは `AOI_ROOT` を呼び出し側が渡す。

旧 `pythdragoras/aoi_layout.py`・`sakanalytics/aoi_layout.py` は、ソースSHAが凍結済み証跡に記録されたCLIのために維持する。研究入力・holdout履歴・結果は更新しない。`source-divergence.json` は既存の出自監査に沿って、原成果を再生成せず現在のCLIソースとの差だけを記録する。自律workerの有効化やスケジュールの追加は行わない。
