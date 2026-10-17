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

## 未接続

今の `nagoyaction/inbox/inbox.py` は「探索とローカル LLM の連携は main への最初の展開から外す」方針で、
これらを呼ばない。ここに戻したのはコードとテストだけで、受付（inbox）への接続はしていない。
つなぐかどうかは別に決める。

テストは `tests/test_research_loop.py`（#48 の前の `NagoyAction/tests/test_inbox.py` のうち、これらのモジュールに関わるもの）。
