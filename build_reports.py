"""Build Markdown reports and rendered/source comparisons using upstream markdown.py."""
import argparse
import difflib
import hashlib
import html
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from urllib.parse import urljoin

REPOSITORY = 'myon-bioinformatics/Aoi'


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True).stdout


def revision(root, ref):
    value = git(root, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
    if not re.fullmatch('[0-9a-f]{40}', value):
        raise ValueError('Expected Git SHA-1 commit')
    return value


class SourceLinks(HTMLParser):
    """Resolve relative URLs against the exact source commit; retain escaped text."""
    def __init__(self, base):
        super().__init__(convert_charrefs=False)
        self.base = base
        self.parts = []

    def handle_starttag(self, tag, attrs):
        out = []
        for name, value in attrs:
            if name in ('href', 'src') and value and not value.startswith('#'):
                value = urljoin(self.base, value)
            out.append(' ' + name + ('' if value is None else '="' + html.escape(value, quote=True) + '"'))
        self.parts.append('<' + tag + ''.join(out) + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        self.parts.append('</' + tag + '>')

    def handle_data(self, data):
        self.parts.append(data)

    def handle_entityref(self, name):
        self.parts.append('&' + name + ';')

    def handle_charref(self, name):
        self.parts.append('&#' + name + ';')


def render(md, text, path, sha):
    base = f'https://github.com/{REPOSITORY}/blob/{sha}/{path}'
    parser = SourceLinks(base)
    parser.feed(md.markdown_to_html(text))
    return ''.join(parser.parts)


def page(title, body, md):
    return ('<!doctype html><html lang="ja"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + html.escape(title) + '</title><style>' + md.default_stylesheet() + '''
body{margin:0;background:#f4f6fa;color:#182b43;font-family:system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:24px}article{background:white;padding:22px;border:1px solid #dde3eb;border-radius:8px;overflow-wrap:anywhere}pre,.scroll{overflow-x:auto}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}.pair>*{min-width:0}.old{border-top:5px solid #ad4c40}.new{border-top:5px solid #27715c}nav{margin-bottom:16px}table.diff{font-size:13px;white-space:pre}.diff_add{background:#d5f3df}.diff_sub{background:#f8d9d4}.diff_chg{background:#fff0b3}footer{overflow-wrap:anywhere;font-size:13px}h1{font-size:26px}@media(max-width:700px){main{padding:12px}.pair{grid-template-columns:1fr}article{padding:12px}}
</style><main>''' + body + '</main></html>')


def load_markdown(path):
    spec = importlib.util.spec_from_file_location('aoi_upstream_markdown', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def selected_paths(root, sha=None):
    if sha:
        paths = git(root, 'ls-tree', '-r', '--name-only', '-z', sha, '--', 'research/', 'dragowing/README.md').decode().split('\0')
        return {p for p in paths if p.endswith('.md')}
    return {p.relative_to(root).as_posix() for p in (root / 'research').rglob('*.md')} | {'dragowing/README.md'}


def build(root, upstream, output, previous_ref=None):
    root, upstream, output = root.resolve(), upstream.resolve(), output.resolve()
    # Output is an isolated build directory, never a source/repository parent.
    if output == root or output in root.parents or root / 'research' == output or output == root / 'dragowing':
        raise ValueError('Output must not overwrite source')
    source = upstream / 'markdown.py'
    license_path = upstream / 'LICENSE'
    if not source.is_file() or not license_path.is_file():
        raise ValueError('markdown.py and upstream LICENSE are required')
    current = revision(root, 'HEAD')
    upstream_sha = revision(upstream, 'HEAD')
    for path in [source, license_path]:
        if git(upstream, 'show', upstream_sha + ':' + path.name) != path.read_bytes():
            raise ValueError('Upstream checkout differs from its commit')
    md = load_markdown(source)
    previous = None
    previous_status = 'not_requested'
    if previous_ref and previous_ref != '0' * 40:
        try:
            previous = revision(root, previous_ref)
            previous_status = 'available'
        except subprocess.CalledProcessError:
            previous_status = 'unavailable'
    previous_paths = selected_paths(root, previous) if previous else set()
    paths = selected_paths(root) | previous_paths
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory must be empty; choose a fresh build path')
    output.mkdir(parents=True, exist_ok=True)
    manifest = dict(source_commit=current, markdown_repository='myon-bioinformatics/markdown',
                    markdown_commit=upstream_sha, markdown_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                    markdown_license_sha256=hashlib.sha256(license_path.read_bytes()).hexdigest(),
                    previous_commit=previous, previous_status=previous_status, documents=[])
    listings = []
    for path in sorted(paths):
        p = root / path
        new = p.read_text(encoding='utf-8') if p.is_file() else ''
        old = git(root, 'show', previous + ':' + path).decode() if previous and path in previous_paths else ''
        # Identity includes empty files: creation/deletion do not depend on content.
        present_old = bool(previous and path in previous_paths)
        status = ('current_only' if not previous else 'added' if not present_old else
                  'deleted' if not p.is_file() else 'unchanged' if old == new else 'modified')
        target = Path(path).with_suffix('.html')
        dest = output / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        home = os.path.relpath(output / 'index.html', dest.parent).replace(os.sep, '/')
        diff_name = target.stem + '.diff.html'
        body = '<nav><a href="' + html.escape(home) + '">一覧</a> · <a href="' + html.escape(diff_name) + '">変更比較</a></nav>'
        body += '<article>' + render(md, new, path, current) + '</article>'
        body += '<footer>source: ' + current + ' · markdown: ' + upstream_sha + '</footer>'
        dest.write_text(page(path, body, md), encoding='utf-8')
        compared = '<nav><a href="' + html.escape(home) + '">一覧</a> · <a href="' + target.name + '">現版</a></nav><h1>' + html.escape(path) + '</h1>'
        if previous:
            compared += '<p>状態: ' + status + '。同じMarkdown実装で両版を描画。色は旧版・新版の区別で、良否を示しません。</p><div class="pair">'
            compared += '<article class="old"><h2>旧版</h2>' + render(md, old, path, previous) + '</article>'
            compared += '<article class="new"><h2>新版</h2>' + render(md, new, path, current) + '</article></div>'
            compared += '<h2>Markdownソースの行差分</h2><p>追加・削除・変更を色と記号で表示。描画後の単語単位の差分は未実装。</p><div class="scroll">'
            compared += difflib.HtmlDiff(wrapcolumn=80).make_table(old.splitlines(), new.splitlines(), fromdesc='旧版', todesc='新版', context=True, numlines=3) + '</div>'
        else:
            compared += '<p>比較元: ' + previous_status + '。変更なしとは判定しません。</p><article>' + render(md, new, path, current) + '</article>'
        compared += '<footer>source: ' + current + ' · previous: ' + str(previous) + ' · markdown: ' + upstream_sha + '</footer>'
        dest.with_name(diff_name).write_text(page('変更比較 ' + path, compared, md), encoding='utf-8')
        listings.append('<li><a href="' + target.as_posix() + '">' + html.escape(path) + '</a> [' + status + '] <a href="' + target.with_name(diff_name).as_posix() + '">差分</a></li>')
        manifest['documents'].append(dict(path=path, status=status, sha256=hashlib.sha256(new.encode()).hexdigest() if p.is_file() else None))
    plot = root / 'research/gpt-r001-score-allocation/outputs/score_timing.html'
    plot_link = ''
    if plot.is_file():
        shutil.copyfile(plot, output / 'score_timing.html')
        plot_link = '<p><a href="score_timing.html">Plotly 得点時期レポート</a></p>'
    index = '<h1>Aoi / DRAgoWing 研究レポート</h1><p>既存研究文書をそのまま描画。主張・反例・留保は各文書を参照。</p>' + plot_link + '<ul>' + ''.join(listings) + '</ul>'
    index += '<footer>source: ' + current + '<br>markdown: ' + upstream_sha + '<br>比較元: ' + previous_status + '</footer>'
    (output / 'index.html').write_text(page('Aoi 研究レポート', index, md), encoding='utf-8')
    (output / 'build-provenance.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    snapshot = output / '_renderer'; snapshot.mkdir(exist_ok=True)
    shutil.copyfile(source, snapshot / 'markdown.py')
    shutil.copyfile(license_path, snapshot / 'LICENSE')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--markdown-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('build/dragowing'))
    parser.add_argument('--previous-ref')
    args = parser.parse_args()
    result = build(args.root, args.markdown_root, args.output, args.previous_ref)
    print(json.dumps({'documents':len(result['documents']), 'markdown_commit':result['markdown_commit'], 'previous_status':result['previous_status']}))


if __name__ == '__main__':
    main()
