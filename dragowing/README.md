# DRAgoWing

記録を、判定をやり直さずに置く。

四つの形の文字の表は [docs/forms.md](docs/forms.md)。HTML（軌跡、球団×年、条件の重なり、命題の一覧）は [docs/figures.md](docs/figures.md)。構想図は [docs/images/dragowing.webp](../docs/images/dragowing.webp)。

```bash
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing
```

`build/dragowing/index.html` と `propositions.html` ができる。`index.html` の軌跡と球団×年は Plotly の JSON 仕様とブラウザの plotly.js（CDN `plotly-latest`）で描く。Python の `plotly` パッケージは使わない。`propositions.html` は一覧と Markdown の表で、Plotly は使わない。`index.html` に Plotly.js を埋め込むときは `--embed` を付ける。ページの文章は Markdown から HTML にしている。

PNG は任意である。`uv sync --extra png` のあと `--png` を付ける。kaleido と Chrome が要る。付けなければ HTML だけで、テストもそちらだけを見る。
