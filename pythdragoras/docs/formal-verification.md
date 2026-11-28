# ビット規則の形式検証

`formal/RuleSoundness.lean` は、`core/bitwise_surrogate.py` の規則の意味と、
「成立し得ない」「含意する」「同時には成立しない」という判定の根拠を形式化します。
実行時の依存は増やしません。共通の Python ラッパーと Lean 専用 CI は
[親リポジトリ](https://github.com/myon-bioinformatics/myon-bioinformatics/blob/27dedd9651efc816fa88d8922adb5f242725df69/lean_verify.py)
で管理し、このリポジトリは固有の証明と Python 側の接続テストを管理します。

## 規則のモデル

規則は、必須特徴 `required`、禁止特徴 `forbidden`、正の OR 節のリスト `clauses` です。
行 `row` が規則を満たす条件 `Holds` は、次の三つの積です。

1. 必須特徴がすべて真。
2. 禁止特徴がすべて偽。
3. 各 OR 節に少なくとも一つ真の特徴がある。

Lean では特徴を任意の型、特徴集合と行を述語として表します。
したがって証明は小さなビット幅に限定されません。Python では特徴集合を非負整数の
ビットで表し、この対応を独立した集合の解釈と比較します。

| 証明 | 内容 | Python の接続先 |
| --- | --- | --- |
| `PythDRagoras.satisfiable_iff` | 充足する全割当の存在と、必須・禁止の無衝突かつ各節に許可特徴があることの同値 | `satisfiable` |
| `PythDRagoras.unsatisfiable_rejects_all` | 条件を満たさない規則はどの全割当でも成立しない | `satisfiable` の否定判定 |
| `PythDRagoras.forced_true` | 必須特徴と、許可特徴が一つだけの OR 節はその特徴を真に強制する | `implies` の `forced` 計算 |
| `PythDRagoras.implication_checks_sound` | 必須特徴・禁止特徴・OR 節の包含検査に通れば含意が成り立つ | `implies` の通常分岐 |
| `PythDRagoras.reported_implication_sound` | 充足不能な前件の分岐も含め、含意の肯定判定が正しい | `implies` |
| `PythDRagoras.combined_rule_iff` | 必須・禁止の和集合と節の連結が、元の二規則の積に相当する | `_both` |
| `PythDRagoras.exclusive_sound` | 結合した規則が充足不能なら二規則は同時に成立しない | `rule_relation` の `exclusive` の根拠 |

例えば「特徴 65 または 511」が必須で、65 が禁止なら、511 が必ず真です。
この場合の含意は単なる必須ビットの包含だけでは検出できず、許可特徴が一つ残る節の
処理が必要になります。証明と接続テストはこの分岐も対象にします。

## Python 実装との接続

`tests/test_formal_bridge.py` は実際の `BitwiseSymbolicSurrogate`、`satisfiable`、
`implies`、`_both`、`witness`、`rule_relation` を呼びます。
期待値は、実装のマスク演算や分岐を再利用しない特徴集合の真理表で計算します。

- 2 特徴の 112 規則を 4 全割当ですべて検査。
- 12,544 組の規則について、含意・同時成立・排他性・返された witness を検査。
- 特徴番号を 65・511 へ移し、無関係な特徴 127 を加えて機械語幅を超える整数も検査。
- 許可特徴が一つ残る OR 節の含意と、その逆の反例を明示的に検査。
- `None` の判定を偽に取り違えず、未確定数として残す境界も確認。

これらは有限の検査です。Lean の数学モデルと Python の全実行を形式的に同一視するものではありません。
Lean 未導入でも、接続テストは標準ライブラリだけで単独実行できます。

```sh
python -S -m unittest discover -s tests -p test_formal_bridge.py -v
```

## Lean 専用の検証

`formal/lean-toolchain` で `leanprover/lean4:v4.36.0` に固定しています。
Lean に同梱された `Std` だけを使い、Mathlib は不要です。
親リポジトリを隣の `myon-bioinformatics` に配置した場合、次のように全宣言を監査できます。

```sh
python -S ../myon-bioinformatics/lean_verify.py \
  --cwd formal --required --json-output build/lean-verification.json \
  --theorem PythDRagoras.satisfiable_iff \
  --theorem PythDRagoras.unsatisfiable_rejects_all \
  --theorem PythDRagoras.forced_true \
  --theorem PythDRagoras.implication_checks_sound \
  --theorem PythDRagoras.reported_implication_sound \
  --theorem PythDRagoras.combined_rule_iff \
  --theorem PythDRagoras.exclusive_sound \
  RuleSoundness.lean
```

共通 CI は未導入を `unverified`、証明や公理の監査の失敗を `failed` と記録し、
どちらも専用レーンの失敗にします。通常の Python テストは Lean を実行しません。

## 証明の境界

対象は **全特徴の真偽が決まった割当**と、AND・NOT・正の OR 節を組み合わせる限定された規則です。
一般の DNF、`None` を含む三値論理の全挙動、文字列からの規則生成、統計的判定、
ビット演算の機械実装、Python の witness 構成アルゴリズムそのものは今回の証明範囲外です。
含意検査の証明は肯定判定の健全性を対象とし、検査の完全性は主張しません。

また、特徴同士にはデータ上の関係がある場合があります。
マスクでの共通割当が存在しても、実際の列値からその割当を作れるとは限りません。
従来どおり `overlap` の witness と実測行の存在を区別し、形式検証の成功から
実データでの支持・因果関係・未知の入力への精度を結論しません。
