# Web観測をPython／Nodeへの置き換え検証に渡す

まず保存済みの実観測を整理する。新しいブラウザ巡回・絵文字移動・HTML取得は作らない。
取得と操作はbrowser-test-kitと既存Flutterの収集処理、保存物の完全性・215ルートの
網羅確認はFlutterの既存`python/check_web_observations.py`に残す。

```sh
python -S web_observations.py /path/to/saved-pages --source-root /path/to/flutter_navigation_basic > observed.json
```

`/path/to/saved-pages`は取得済みアーティファクトを展開した実在するディレクトリに、
`/path/to/flutter_navigation_basic`はソースの実在するディレクトリに置き換える。
最初の位置引数は観測ディレクトリであり、`saved-pages`というサブコマンドではない。
その配下の`web-observation.json`を再帰的に読む。ソース一覧が不要なら
`--source-root`は省略できる。

追加依存、Flutter、Dart SDK、Xcode、Android SDK、ブラウザは不要。
`flutter-web-observation/1`と隣接する`exploration.json`を読み、BlueProbe既存の
`records / counts / unknown`契約に沿った`web-portability-observations/1`を出す。

- `raw`に観測の原文、`derived`にラベル・表示座標・viewport・操作履歴・収集結果を残す。
- 欠けた操作履歴は`null`と件数で残す。座標の不正、空の観測、異なる申告ビルドSHAの混在を隠さない。
- ソース一覧はDart／Kotlin／Swiftのファイルと主要なビルド設定のパス、サイズ、SHA-256。
  生成物ディレクトリを除くがテストのソースも含む。本文を実行・変換・importしない。
  ファイルのハッシュは、そのファイルと描画ルートの対応や実行時の版を証明しない。
- 終了0は解析の完了。アプリの合格ではない。無効な記録は終了2。
  producerが失敗した記録も保持し、`producer_failed_or_incomplete`に数える。

この段階では、座標は収集時のviewport上の矩形であって、別端末でのクリック先保証ではない。
`reported_build_sha`もproducerの申告値であり、独立した実行コードの証明ではない。
スクリーンショットのバイト検証も既存producer検証器で行う。

## 完了条件を段階ごとに置く

| 検査 | 実行するもの | この段階で分かる範囲 |
|---|---|---|
| 保存観測の解析 | このCLI | 記録された構造・座標・操作と、足りない情報 |
| 置き換え先の入出力 | xprobeの`contract_probe.py`に明示したPython／Nodeコマンド | 同じ入力に対し、各実装が明示した期待結果を満たすか |
| 現在のWeb画面 | 既存browser-test-kit／Flutterの実ブラウザ収集 | 対象版・viewport・操作条件での実際の描画と動作 |
| OS権限・ネイティブ連携 | 対象プラットフォームの専用検査 | 実行した能力だけ。Webの合格から推測しない |

Webで閉じる機能は、その機能の入力・期待する出力・状態遷移・対象ルート・版を
明示した契約に落とす。保存観測は候補の発見に使い、期待結果を自動で丸写しして正解にしない。
PythonとNodeが同じ誤答を返しても、期待結果に反すれば失敗にする。

**未実装／未観測:** バックエンドのrequest/response本文と状態遷移、ソースからルートへの
対応、元のビルドとのソース対応、OS副作用、アプリ全体のPython／Node実装。
これらは`unobserved`にも残す。バックエンドの再現には順序付きI/O契約が必要であり、
ログの再表示だけを独立したバックエンド実装として扱わない。
Dart↔Kotlin／Swiftの可逆変換や完全な意味解析はこのCLIには含めない。

最初の実データ検証では、既存の保存済み215ページ、2,895個のコントロール矩形、645操作を
解析した。これはその保存観測の読取検証であり、現在のソースやネイティブ機能の合格数ではない。
