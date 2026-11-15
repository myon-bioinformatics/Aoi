"""The optional self-test environment must stay independent of Aoi research deps."""
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "tools" / "localci-env"


def test_localci_profile_has_only_the_pinned_test_runner():
    config = tomllib.loads((PROFILE / "pyproject.toml").read_text(encoding="utf-8"))
    assert config["project"]["dependencies"] == ["pytest==9.1.1"]
    assert config["project"]["requires-python"] == ">=3.11"
    assert config["tool"]["uv"]["package"] is False


def test_localci_lock_contains_only_pytest_closure():
    lock = tomllib.loads((PROFILE / "uv.lock").read_text(encoding="utf-8"))
    packages = {p["name"]: p for p in lock["package"]}
    assert set(packages) == {
        "nagoyaction-localci-tests", "pytest", "pluggy", "packaging",
        "iniconfig", "pygments", "colorama",
    }
    assert packages["pytest"]["version"] == "9.1.1"
    for name, package in packages.items():
        if name == "nagoyaction-localci-tests":
            continue
        assert package["source"] == {"registry": "https://pypi.org/simple"}
        assert package["wheels"]
        assert all(wheel["hash"].startswith("sha256:") for wheel in package["wheels"])


def test_localci_profile_does_not_become_repository_default():
    assert not (ROOT / "pyproject.toml").exists()
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "tools/localci-env" not in workflow
    assert "python localci.py run --repeat 10 --seed" in workflow
