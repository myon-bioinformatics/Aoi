"""Every documented child CLI exposes help without third-party packages."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_child_readme_help():
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    children = {'blueprobe', 'queryu', 'nagoyaction', 'sakanalytics', 'pythdragoras', 'dragowing'}
    documented = set(re.findall(r'^python aoi\.py (\w+) --help$', readme, re.M))
    assert children <= documented
    for child in sorted(children):
        result = subprocess.run(
            [sys.executable, '-I', '-S', str(ROOT / 'aoi.py'), child, '--help'],
            capture_output=True, text=True, encoding='utf-8', cwd=ROOT, timeout=30,
        )
        assert result.returncode == 0, (child, result.stderr)
        assert '--help' in result.stdout, (child, result.stdout)
