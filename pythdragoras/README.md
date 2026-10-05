# PythDRagoras（実装）

> 本当にその説明で十分か？

![PythDRagoras](../docs/images/pythdragoras.webp)

*イメージ図（構想を共有するための図。実際のデータ・HTML構造ではない）*

思想は [docs/PythDRagoras.md](../docs/PythDRagoras.md)。ここはその検証部分の実装。

| 関数 | 中身 |
|---|---|
| `apply_exclusions` | 分析から除くシーズンを適用する。理由のない除外は受け付けず、何を・なぜ除いたかを結果に残す |
| `cumulative_test` | 期待勝率からのずれの累積を z 値にする（固定指数・可変指数の両方） |
| `rank_test` | 順位が下位に偏る珍しさ。帰無仮説（各シーズン独立に一様）と、全球団の実際の記録との比較を並べる |
| `summary_markdown` | 検証記録。原因は書かない。競合仮説の状態を並べる |
| `propositions.py` | 命題・判例・異議あり（仕様は [docs/propositions.md](../docs/propositions.md)） |

## 命題と「異議あり」

説明を「もし A ならば B」の命題として書き、元の命題・対偶・逆・裏の4つの形で判定する。
判定の基準は、結果を見る前に言葉で宣言する（必ず / ほとんど 0.90 / 概ね 0.75 / 多くの場合 0.50）。

```text
判定（上から順に最初に当てはまるもの）
  n < min_n                      → 判断保留
  必ず かつ 反例なし / あり        → 支持 / 棄却
  区間の下限 ≥ 基準                → 支持
  区間が基準をまたぐ              → 判断保留
  区間の上限 < 基準 かつ 関係あり   → 修正（主張が強すぎる）
  区間の上限 < 基準 かつ 関係なし   → 棄却
```

反例が1件でもあれば、判定が「支持」でも **異議あり** として判例を並べる。支持された説明の中の反例こそが、説明が足りなくなる場所だからである。
除外したシーズンの判例は、統計からは外しても「除外中の判例」として必ず表示する。

元の命題と逆の判定を並べた「読み」（十分条件だけ・必要条件だけ・同値に近い など、番号 0〜6）と、判例から取った次の命題の種（**絞る** = 元の命題の判例、**道筋** = 逆の判例）を `next.md`・`next.jsonl` に書く。読みは判定ではなく、終了コードを変えない（[docs/propositions.md](../docs/propositions.md) の Reading The Original And The Converse Together）。

```bash
uv run python pythdragoras/propositions.py next cycles/c001-chunichi/outputs/propositions.jsonl --reading 1 2
```

## 命題の集合（`sets.py`、R48）

登録した命題の条件を集合として名前で呼び（`from` に命題の id、`part` に if・then・where）、集合の式（`&` かつ、`|` または、`~` でない）を命題として判定する。式は「かつ」の組を「または」で並べた形に直して、4つの形・終了コード・判例を命題と同じ規則で出す。

- 焦点の球団の後件に当たる単位（中日の B の年など）のうち、式に入るものの数（**覆い**）を出す
- **通る** = 元の命題の形に判例がなく（終了コード 0）、焦点の後件の単位をすべて覆う。逆は求めない
- 1つ通っても正解とは書かない。別々の命題から組んだ式が複数通ることを求める
- 結果は `sets.md`（人が読む）・`sets.jsonl`（機械向け）・`sets.junit.xml`（JUnit 形式のテスト報告）に書く。通らなかった式は failure として、**止まった理由**（判例・覆えなかった焦点の単位）を残す。止まり方は、足りる指標・足りない指標を見つける材料（R49）
- 集合は登録済みの命題の条件だけから作る（新しい条件をここで書かない）。式は計算の前に `sets.toml` に書く

```bash
uv run python pythdragoras/sets.py --season cycles/c001-chunichi/outputs/season.jsonl --config cycles/c001-chunichi/analysis.toml \
  --propositions cycles/c001-chunichi/propositions.toml --sets cycles/c001-chunichi/sets.toml --outdir cycles/c001-chunichi/outputs --report-only
```

外部の主張（記事・レポート・他のAI）は、観測ではなく claim として登録し、パイプラインで再現できるかを確かめる。

帰無仮説は各シーズンを独立とみなすため、前年からの戦力の持ち越しを無視し、珍しさを過大に見積もる。
そのため、同じ期間の全球団との比較（経験的基準）を必ず並べる。

```bash
uv run python pythdragoras/pythdragoras.py --season cycles/c001-chunichi/outputs/season.jsonl \
  --config cycles/c001-chunichi/analysis.toml --hypotheses cycles/c001-chunichi/hypotheses.toml \
  --propositions cycles/c001-chunichi/propositions.toml --claims cycles/c001-chunichi/claims.toml \
  --outdir cycles/c001-chunichi/outputs
```
