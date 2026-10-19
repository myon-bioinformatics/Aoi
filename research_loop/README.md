# research_loop（Aoi の研究ループ）

#48（大文字フォルダの削除）で消えた、自動の探索と HTML の観測を回す部品を戻したもの。
どれも Aoi の研究サイクル（`cycles/<cycle>/sets.toml`・`outputs/`）を前提にし、
複数のサブプロジェクト（SakAnalytics の測定、PythDRagoras の判定、DRAgoWing の HTML、QueRyu の ask）をつなぐ。
そのため、どれか1つのサブプロジェクトには置かず、Aoi 自身に置く。

| ファイル | 元の場所 | 中身 |
|---|---|---|
| `autonomous.py` | `NagoyAction/inbox/autonomous.py` | 決まった順の自動の種（登録済みの式 → `all`）。終わった仕事・止めた仕事は二度と出さない |
| `feedback.py` | `NagoyAction/inbox/feedback.py` | 近い球団年の組（測定）→ 既存の判定 → HTML → 観測した変化。同じ入力なら何も書かない |
| `exploration.py` | `PythDRagoras/logic/exploration.py` | 登録済みの集合だけで、再開できる上限つきの探索（取得・任意のコード・閾値の変更・正式な命題の編集はしない） |
| `neighbor_checks.py` | `PythDRagoras/logic/neighbor_checks.py` | 測った組に、既存の判定の反例が当たるかを見る（不明は不明のまま） |
| `dragowing_inspect.py` | `BlueProbe/reports/dragowing_inspect.py` | DRAgoWing の HTML に埋め込んだ観測（`report-data`）だけを読む。HTML を実行せず、URL も取らない |

`neighbors.py`（近い球団年の組を測る）は測定なので `sakanalytics/neighbors.py` に置いた。

## オフライン worker 接続（有効化は保留）

NagoyAction の `inbox/inbox.py worker` が `exploration.py` を読み、登録済み集合の
探索を1候補ずつ進める。期限、保存、再開、権限制御は子の実装を正本とする。
[worker の手順と制約](../nagoyaction/docs/worker.md) を参照。

`autonomous.py` による複数 seed の自動選択、feedback、HTML観測、LLM、質問受付の
`/explore`・`/stop` への接続は未導入。worker の停止は専用状態ディレクトリの
`STOP` ファイルで行う。質問受付は従来どおり独立して動作する。

テストは `tests/test_research_loop.py`（部品）と
`nagoyaction/tests/test_worker.py`（実際の部品を呼ぶ期限・中断再開・入力保護）。
Actions の再開判断は [worker-operations.md](worker-operations.md) を参照。
