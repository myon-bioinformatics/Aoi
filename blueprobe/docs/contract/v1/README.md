# BlueProbe 契約 v1

状態: **stable**（初版 1.0.0）

BlueProbe と、それを使う側（Aoi の QueRyu・SakAnalytics、各リポジトリ）とのあいだの互換面。
決め方は [web-ui contract/v1](https://github.com/myon-bioinformatics/web-ui/tree/main/contract/v1) に揃える。

## 安定性の約束

- v1 の中では、安定項目を**消さない・意味を変えない**
- 項目の追加は v1 のまま行ってよい（読む側は知らない項目を無視する）
- 削除・意味の変更・必須化は v2 として `docs/contract/v2/` を新しく作る
- パッチ番号は互換の目印に使わない。互換の単位は `v1` / `v2`

| 文書 | 対象 |
|---|---|
| [report.md](report.md) | 1ページを読んだ結果（records / counts / unknown）と集計行 |
| [snapshot.md](snapshot.md) | 保存済み本文の供給元と `html-snapshot/1` の記録 |
