# littlebit-approx（探索）

このディレクトリは c001 の探索記録である。確かめの記録は [confirmation.md](../../confirmation.md) に置く。命題ファイルや `rules.jsonl` とは別に置く。

- [comparison.md](comparison.md) は、既存候補だけの `search` と、派生候補を足した `search` の並びである。観測と解釈は節を分けてある。
- [comparison.json](comparison.json) は同じ並びの機械向け記録である。残差の単位はこちらに全部ある。
- 規則は [littlebit-approx.md](../../../../../pythdragoras/docs/littlebit-approx.md)。

再生成:

```bash
uv run python pythdragoras/littlebit_approx.py
```

rank、stages、seed はコマンドの既定（8、2、0）のまま使う。
