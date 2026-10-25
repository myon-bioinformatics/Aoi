"""Chromium CI selection fails closed without changing legacy report identity."""
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def _selection_step(path, title, job_name):
    text = path.read_text(encoding="utf-8")
    text = text.split("\n  " + job_name + ":\n", 1)[1]
    marker = "      - name: " + title + "\n"
    block = text.split(marker, 1)[1].split("\n      - ", 1)[0]
    script = block.split("        run: |\n", 1)[1]
    return "\n".join(line.removeprefix("          ") for line in script.splitlines()) + "\n"


def _select(tmp_path, names, job_name):
    tmp_path.mkdir()
    binary = tmp_path / "bin"
    binary.mkdir()
    for name in names:
        path = binary / name
        path.write_text("#!/bin/sh\necho 'Chromium 123.4'\n", encoding="utf-8")
        path.chmod(0o755)
    output = tmp_path / "environment"
    env = {**os.environ, "PATH": str(binary), "GITHUB_ENV": str(output)}
    script = _selection_step(ROOT / ".github/workflows/ci.yml", "Select required Chromium without Chrome fallback", job_name)
    result = subprocess.run(["/bin/bash", "--noprofile", "--norc", "-c", script], env=env, capture_output=True, text=True)
    return result, output


def test_ci_prefers_chromium_and_records_selected_path(tmp_path):
    for job_name in ("test", "chrome-export"):
        work = tmp_path / job_name
        result, output = _select(work, ["google-chrome", "chromium", "chromium-browser"], job_name)
        assert result.returncode == 0, result.stderr
        assert "Chromium 123.4" in result.stdout
        assert output.read_text() == "CHROME=" + str(work / "bin/chromium") + "\nDRAGOWING_REQUIRE_CHROME=1\n"


def test_ci_accepts_chromium_alias(tmp_path):
    for job_name in ("test", "chrome-export"):
        work = tmp_path / job_name
        result, output = _select(work, ["chromium-browser"], job_name)
        assert result.returncode == 0, result.stderr
        assert output.read_text() == "CHROME=" + str(work / "bin/chromium-browser") + "\nDRAGOWING_REQUIRE_CHROME=1\n"


def test_ci_rejects_chrome_only_runner(tmp_path):
    for job_name in ("test", "chrome-export"):
        result, output = _select(tmp_path / job_name, ["google-chrome", "google-chrome-stable", "chrome"], job_name)
        assert result.returncode != 0
        assert "::error::Chromium is required:" in result.stdout
        assert not output.exists()


def test_offline_ci_keeps_isolation_and_report_contract():
    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    job = text.split("\n  chrome-export:\n", 1)[1].split("\n  failure-identity:\n", 1)[0]
    assert "runs-on: ubuntu-24.04" in job
    assert 'sudo unshare --net -- env CHROME="$CHROME" DRAGOWING_REQUIRE_CHROME=1' in job
    assert "--junitxml=build/test-results/chrome-export-3.14.xml" in job
    assert "name: junit-chrome-export-py3.14" in job
    assert "name: chrome-export-evidence" in job
    assert "name: Offline Chrome export (Python 3.14)" in job
    assert '"junit-chrome-export-py3.14/chrome-export-3.14.xml"' in text
    assert "needs: [changes, test, lab-integration, chrome-export]" in text


def test_diagnostics_use_chromium_by_default_with_manual_chrome_comparison():
    text = (ROOT / ".github/workflows/browser-startup-validation.yml").read_text(encoding="utf-8")
    assert "compare-chrome:\n" in text
    assert "type: boolean\n        required: false\n        default: false" in text
    assert "fromJSON(github.event_name == 'workflow_dispatch' && inputs.compare-chrome && '[\"chromium\",\"google-chrome\"]' || '[\"chromium\"]')" in text
    assert "Chromium is required:" in text
    assert "The requested Chrome comparison requires" in text
    assert text.count('--chrome "$CHROME"') == 3
    assert text.count('--runs 10 --timeout 30') == 2
    assert '--runs 3 --timeout 30' in text
    assert "DRAGOWING_REQUIRE_CHROME: '1'" in text
    assert "if: always()" in text
    assert "build/browser-startup/*.json" in text
    assert "build/browser-startup/diagnostic-exports/" in text


def test_python_matrix_pins_the_same_required_chromium_selection():
    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    job = text.split("\n  test:\n", 1)[1].split("\n  lab-integration:\n", 1)[0]
    assert "runs-on: ubuntu-24.04" in job
    assert "command -v chromium || command -v chromium-browser" in job
    assert "command -v google-chrome" not in job
    assert "CHROMIUM=%s" not in job
    assert "DRAGOWING_REQUIRE_CHROME=1" in job
    assert "from dragowing.plotly_cdn import fetch_plotly_js" in job
    assert "DRAGOWING_PINNED_PLOTLY_JS: ${{ github.workspace }}/build/test-assets/plotly.min.js" in job
