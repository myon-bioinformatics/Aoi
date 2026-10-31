# 回収入力の分類と復元先

2026-10-25に回収した保存ファイルを、**実観測・年次派生・架空シナリオに分けて保存**します。元の2つのZIPと試合JSONはバイトを変更していません。年次JSONLは既存の同一ファイルを参照し、架空シナリオは別ZIPに隔離します。元HTMLは含めません。

- 実観測: [元ZIP](observed/source-archives/aoi_supplement_share.zip)、[games_raw.json](observed/games_raw.json)
- 年次派生: [元ZIP](derived-annual/source-archives/c001-v2-ghi-gated-37640078444.zip)、[既存の同一season.jsonl](../from-cycle-001/outputs/season.jsonl)
- 架空のみ: [分離ZIP](synthetic/aoi-synthetic-examples-only-20261025.zip)

出典と再配布条件は末尾の注意を確認してください。原資料へのMITライセンス付与や、NPBによる公開許諾を示すものではありません。

## 実観測・年次派生・架空データの区別

| ファイル | 分類 | 確認した内容 |
| --- | --- | --- |
| `aoi_supplement_share.zip` 内の `data/part2/games_raw.json` | 実試合ページ由来の解析済み観測 | JSON配列12,574件。2013-03-29〜2026-10-03。元HTMLは入っていない。 |
| `c001-v2-ghi-gated-37640078444.zip` 内の `v1/season.jsonl` / `v2/season.jsonl` | 実観測を入力とした年次派生パネル | 2012〜2025年 ×12球団の168行、各409列。両ファイルはバイト一致。モデル・シミュレーションの派生列も含む。 |
| 同ZIP内の `v2/fetched/npb_game_linescore.jsonl` | 取得来歴 | URL・日時・状態・バイト数・SHA-256の858行。試合スコア本体ではない。 |
| `aoi_primary_2013_2026.zip` / `aoi_annual_history_1950_2026.zip` | 実年次記録と架空実験の混在パッケージ | `data/synthetic/` 配下の `*.games.jsonl` は架空シナリオ。実試合の入力に混ぜない。元ZIP全体を「実データ」または「全て架空」と呼ばない。 |

`season.jsonl` の入力球団年は架空の試合表ではありません。ただし全409列が観測値という意味ではなく、`pythag_*`、`sim_*`、`wave_*` などの計算・モデル出力を含みます。保存済み入力からの下流再判定であり、元HTMLの独立再検証を示しません。

ハッシュ・バイト数・分類の機械可読版は [manifest.json](manifest.json) にあります。ハッシュ一致は保存バイトの同一性であり、データの完全性や研究上の結論を保証しません。

## 既存の年次ファイルを重複させない

回収した年次パネルは、既存の [from-cycle-001/outputs/season.jsonl](../from-cycle-001/outputs/season.jsonl) と完全に一致します。

- SHA-256: `20466c46628f4657233ef6289c628f076a0c665a2129594f5651d29a0d05d350`
- 別の正本 [outputs/season.jsonl](../outputs/season.jsonl) は `8ddba36adfbd06db5c7510f91953184233801c596f87d4fe9bd66fc1b9573a93`。回収版で上書きしません。
- 既存の [PR #126](https://github.com/myon-bioinformatics/Aoi/pull/126) は、この2系統の年次ファイルと取得来歴などをまとめたアーカイブです。確認したheadは `3d234170e151463c296545907deda2fbcf45086a`。この変更ではそのPRやアーカイブを変更しません。

補足ZIPの保存済み `team_season_summary.csv` と回収した年次パネルは、共通する2013〜2025年の156球団年で `G/W/L/T/RF/RA` の936値が一致しました。これは保存済み集計どうしの照合です。今回、新たに試合行から年次値を作り直した結果ではありません。

## 架空シナリオを混ぜない

分離ZIPは元の混在パッケージ2つから `data/synthetic/` 配下330ファイルだけを取り出したものです。162個の `*.games.jsonl` に110,016件の架空試合を含みます。新しいデータ生成や数値変更はしていません。ZIP内MANIFESTに全メンバーの元ZIP・元パス・SHA-256を保持しています。

実年次成績から得た平均得点の校正情報は実験設定に残りますが、実測の試合行・年次行は分離ZIPに含めません。

元ZIPごとのディレクトリを保つため、同名パスも混ざりません。元の混在ZIP全体は重複保存していません。これらの元ZIPにある年次ページのHTML.gzは回収済みですが、公開対象から除外しています。合成件数を実測標本数に加えず、架空表の成績をNPBの実試合結果として利用しません。

## 試合JSONの境界

- `games_raw.json` は終了試合だけの表ではありません。final 12,111件、中止389件、noGame 72件、取得時点の進行中2件を含みます。ポストシーズン・オールスターも入っています。
- 420件で片方または両方の球団IDがnullです。日付・URLは保持されており、URL重複はありません。欠損を架空値で埋めません。
- 2026年は2026-10-03取得時点の暫定記録です。現在の確定記録に更新したものではありません。 原本を変更せず、残りのレギュラーシーズンを照合した[別の2026年確定データセット](../season-2026/README.md)を追加しました。
- `data/observations/npb_calendar/games.jsonl` と、その再構築に必要な試合ページの元HTMLキャッシュ（npb_calendar / linescore）は回収できていません。ファイル名だけを変えて互換入力として使いません。QueRyu向けの変換には、正規シーズンの選別、球団ID・状態・イニング・サヨナラ表記などの対応を別途検証する必要があります。
- 元ZIP内のREADME・スクリプトは当時の記録です。絶対パスや旧取得手順を含むため、そのまま実行する手順として扱いません。今回、ネットワーク再取得や同梱スクリプトの実行はしていません。

## 保存ZIPから作業用コピーを復元

リポジトリ直下で次を実行すると、元ZIPを変更せず、選んだ2ファイルだけをgit管理外 `data/recovered-inputs/` に復元します。既存ファイルの不一致では停止します。これはデータのコピー手順であり、利用条件や再配布権限を新たに付与するものではありません。

[stdlib-only検査helper](../../../scripts/recovered_zip.py) は、読み込むZIPの全メンバーを先に検査します。絶対パス、`.` / `..` / 空要素、バックスラッシュ、Windowsのdrive・ADS・予約名、NUL等の制御文字、名前の重複・別名、ファイルとディレクトリの衝突、symlink・device等の特殊型を拒否し、安全な名前への書き換えはしません。Unix型ビット未指定の通常ファイルと、末尾 `/` の空ディレクトリは受け入れます。CIは公開する3つのZIP（架空専用ZIPを含む）と架空MANIFESTの元パスを同じ条件で検証します。このhelperは展開器ではなく、以下も固定の出力先にだけコピーします。`extract()` / `extractall()` は使いません。

```python
import hashlib
import io
import json
from pathlib import Path

from scripts.recovered_zip import validated_zip

catalog = json.loads(Path("cycles/c001-chunichi/recovered-inputs/manifest.json").read_text())
root = Path("data/recovered-inputs")
targets = [
    (catalog["archives"][0], "data/part2/games_raw.json", root / "observed/games_raw.json"),
    (catalog["archives"][1], "v2/season.jsonl", root / "derived-annual/season.jsonl"),
]
for archive, member, output in targets:
    source = Path(archive["repository_path"])
    content = source.read_bytes()
    if len(content) != archive["bytes"] or hashlib.sha256(content).hexdigest() != archive["sha256"]:
        raise ValueError(f"Archive mismatch: {source.name}")
    with validated_zip(io.BytesIO(content)) as saved:
        payload = saved.read(member)
    expected = archive["selected_member"]
    if len(payload) != expected["bytes"] or hashlib.sha256(payload).hexdigest() != expected["sha256"]:
        raise ValueError(f"Member mismatch: {member}")
    if output.is_symlink() or any(parent.is_symlink() for parent in output.parents):
        raise ValueError(f"Refusing symlink output path: {output}")
    if output.exists() and output.read_bytes() != payload:
        raise ValueError(f"Refusing to overwrite different data: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    print(output)
```

実観測と年次派生を別ディレクトリに保持します。架空シナリオのファイルはこの復元対象に含めません。復元したファイルは既存pipelineへ自動登録されません。出力先と親ディレクトリの既存symlinkも拒否しますが、他プロセスによる同時のパス差し替えを防ぐ展開sandboxではありません。自分が管理する作業ディレクトリで実行してください。

## 出典と公開範囲

補足ZIPのREADMEはGrok側で2026-10-03に作成したNPBページ由来の解析結果と記載しています。元の35メンバーは同梱MANIFESTのSHA-256・バイト数と一致しました。c001 ZIPでは年次パネルが同梱input-manifestのハッシュとも一致しています。出典ページの一例は [NPB 2013-03-29の試合結果](https://npb.jp/bis/2013/games/s2013032900160.html) です。

当該NPBページのフッターには掲載情報などの二次利用・無断転載を禁じる表示があり、回収ZIP内には別の再配布ライセンスがありません。数値的な事実と保護される表現・編集物の扱いは同じとは限りませんが、今回の確認だけで原本一式の公開権限を確定しません。AoiのMITライセンスを第三者の元資料への許諾として扱いません。

上記の未確認事項を明記したうえで、提供者から公開する指示を受けて保存したものです。この指示はNPBからの権利許諾を意味しません。利用・再配布の可否は目的・範囲・適用条件ごとに別途確認してください。

[従来のデータ転載の境界](../research/PR3_FOLLOWUP.md) は過去の研究引き継ぎ時点の記録として保持します。今回の保存は、この回収パッケージに限る公開指示によるものです。他の入力や将来の取得データを一括で公開する方針変更ではありません。
