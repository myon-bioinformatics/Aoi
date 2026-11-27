"""Every documented child CLI exposes help without third-party packages."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from cli_args import run_cli  # noqa: E402


def test_child_readme_help():
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    children = {'blueprobe', 'queryu', 'nagoyaction', 'sakanalytics', 'pythdragoras', 'dragowing'}
    documented = set(re.findall(r'^python aoi\.py (\w+) --help$', readme, re.M))
    assert children <= documented
    for child in sorted(children):
        result = run_cli(
            ROOT / 'aoi.py', child, '--help',
            python_options=('-I', '-S'), encoding='utf-8', cwd=ROOT, timeout=30,
        )
        assert result.returncode == 0, (child, result.stderr)
        assert '--help' in result.stdout, (child, result.stdout)
