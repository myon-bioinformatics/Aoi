"""Parent vendor_dispatch verify job stays beside the existing vendor-lock check."""
import re
import pytest
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".github/workflows/ci.yml").is_file())
CI = ROOT / ".github/workflows/ci.yml"
SETUP_NODE = "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0"
SETUP_PYTHON = "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0"
SETUP_UV = "astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2"


def _job(text: str, name: str) -> str:
    match = re.search(rf"\n  {re.escape(name)}:\n", text)
    assert match, name
    rest = text[match.end():]
    nxt = re.search(r"\n  [A-Za-z0-9-]+:\n", rest)
    body = rest[: nxt.start()] if nxt else rest
    return text[match.start(): match.start() + len(match.group(0)) + len(body)]


def test_vendor_lock_check_stays_on_python_s():
    text = CI.read_text(encoding="utf-8")
    job = _job(text, "vendor-lock")
    assert "python -S scripts/check_vendor_lock.py --aoi .test-deps/aoi" in job
    assert "python -S scripts/check_vendor_lock.py --aoi .test-deps/aoi --warn" in job
    assert "vendor_dispatch.py" not in job
    assert "--record" not in job


def test_vendor_dispatch_verifies_the_lock_without_record():
    text = CI.read_text(encoding="utf-8")
    assert "python -m pytest" not in text
    assert 'uv run --locked --python "${{ matrix.python }}" pytest' in text
    job = _job(text, "vendor-dispatch")
    assert "needs: changes" in job
    assert "actions/checkout@v7" in job
    assert SETUP_NODE in job
    assert SETUP_PYTHON in job
    assert SETUP_UV in job
    assert 'node-version: "24"' in job
    assert 'python-version: "3.12"' in job
    assert "git ls-remote https://github.com/myon-bioinformatics/myon-bioinformatics refs/heads/main" in job
    assert 'PARENT_REPOSITORY_ID: "638801160"' in job
    assert "python -S" not in job
    assert "python .test-deps/parent/pilot/vendor_dispatch.py --manifest vendor.lock.json" in job
    assert "--record" not in job
    assert "repository: myon-bioinformatics/myon-bioinformatics" not in job


def _assert_required_managed_chromium(job):
    install = 'python3 scripts/install_ci_chromium.py --destination "$RUNNER_TEMP/dragowing-chromium"'
    selection = 'chromium="$RUNNER_TEMP/dragowing-chromium/chrome-linux/chrome"'
    assert install in job and selection in job
    assert job.index(install) < job.index(selection) < job.index('"$chromium" --version')
    assert 'command -v chromium' not in job
    assert 'Chromium 156.0.8078.0' in job
    assert 'exit 1' in job
    assert 'continue-on-error' not in job
    assert 'command -v google-chrome' not in job
    assert 'Installed Chromium version does not match the reviewed snapshot.' in job
    assert 'DRAGOWING_REQUIRE_CHROME=1' in job
    assert 'DRAGOWING_PINNED_PLOTLY_JS: ${{ github.workspace }}/build/test-assets/plotly.min.js' in job
    assert 'from plotly_cdn import fetch_plotly_js' in job
    assert 'CHROMIUM=%s' not in job
    assert '"$chromium" --version' in job
    assert '>> "$GITHUB_ENV"' in job


def test_python_matrix_requires_chromium_without_implicit_chrome_fallback():
    _assert_required_managed_chromium(_job(CI.read_text(encoding="utf-8"), "test"))


@pytest.mark.parametrize("old,new", [
    ("python3 scripts/install_ci_chromium.py", "python3 missing-installer.py"),
    ('chromium="$RUNNER_TEMP/dragowing-chromium/chrome-linux/chrome"', 'chromium=/usr/bin/chromium'),
    ('Chromium 156.0.8078.0', 'Chromium 155.0.8059.0'),
    ('DRAGOWING_REQUIRE_CHROME=1', 'DRAGOWING_REQUIRE_CHROME=0'),
    ('shell: bash', 'continue-on-error: true\n        shell: bash'),
    ('test -x "$chromium"', 'command -v google-chrome'),
])
def test_managed_chromium_contract_rejects_missing_or_weakened_setup(old, new):
    job = _job(CI.read_text(encoding="utf-8"), "test")
    assert old in job
    with pytest.raises(AssertionError):
        _assert_required_managed_chromium(job.replace(old, new))
