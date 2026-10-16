# DRAgoWing

記録を、判定をやり直さずに置く。

四つの形の文字の表は [docs/forms.md](docs/forms.md)。HTML の図（軌跡、球団×年、条件の重なり、反例カード）は [docs/figures.md](docs/figures.md)。構想図は [docs/images/dragowing.webp](../docs/images/dragowing.webp)。

```bash
python -m dragowing --results cycles/c001-chunichi/outputs --out build/dragowing
```

`build/dragowing/index.html` と `propositions.html` と、共有の `plotly.min.js` ができる。ブラウザで開く。ネットワークには出さない。図のライブラリは Plotly で、Plotly.js は出力先に1つだけ置く。各 HTML に埋め込むときは `--embed` を付ける。ページの文章は Markdown から HTML にしている。

PNG は任意である。`uv sync --extra png` のあと `--png` を付ける。kaleido と Chrome が要る。付けなければ HTML だけで、テストもそちらだけを見る。
