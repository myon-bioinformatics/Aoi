"""Chromium defaults are independent of the runner's other installed browsers."""
from pathlib import Path

import pytest

from dragowing import chrome_pipe


@pytest.fixture
def browsers(monkeypatch, tmp_path):
    monkeypatch.setattr(chrome_pipe.sys, "platform", "linux")
    monkeypatch.delenv("CHROME", raising=False)
    monkeypatch.delenv("CHROMIUM", raising=False)
    monkeypatch.chdir(tmp_path)
    paths, searched = {}, []

    def which(name):
        searched.append(name)
        return paths.get(name)

    monkeypatch.setattr(chrome_pipe.shutil, "which", which)

    def install(*names):
        for name in names:
            executable = tmp_path / "bin" / name
            executable.parent.mkdir(exist_ok=True)
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(0o755)
            paths[name] = str(executable)
        return paths, searched

    return install


@pytest.mark.parametrize("available, expected", [
    (("google-chrome", "chromium", "chromium-browser"), "chromium"),
    (("google-chrome", "chromium-browser"), "chromium-browser"),
])
def test_default_search_is_chromium_only(browsers, available, expected):
    paths, searched = browsers(*available)
    assert chrome_pipe.find_chrome() == paths[expected]
    assert searched == (["chromium"] if expected == "chromium" else ["chromium", "chromium-browser"])


def test_chrome_only_install_does_not_hide_missing_chromium(browsers):
    _, searched = browsers("google-chrome", "google-chrome-stable", "chrome")
    with pytest.raises(RuntimeError, match="Chromium was not found on PATH.*Install Chromium.*CHROMIUM"):
        chrome_pipe.find_chrome()
    assert searched == ["chromium", "chromium-browser"]


@pytest.mark.parametrize("variable", ["CHROME", "CHROMIUM"])
def test_explicit_environment_override_accepts_legacy_chrome(browsers, monkeypatch, variable):
    paths, searched = browsers("google-chrome", "chromium")
    monkeypatch.setenv(variable, "google-chrome")
    assert chrome_pipe.find_chrome() == paths["google-chrome"]
    assert searched == ["google-chrome"]


def test_argument_precedes_environment_overrides(browsers, monkeypatch):
    paths, searched = browsers("google-chrome", "chromium")
    monkeypatch.setenv("CHROME", "/missing/chrome")
    monkeypatch.setenv("CHROMIUM", paths["chromium"])
    assert chrome_pipe.find_chrome(paths["google-chrome"]) == paths["google-chrome"]
    assert searched == []


def test_legacy_environment_precedence_is_preserved(browsers, monkeypatch):
    paths, searched = browsers("google-chrome", "chromium")
    monkeypatch.setenv("CHROME", paths["google-chrome"])
    monkeypatch.setenv("CHROMIUM", paths["chromium"])
    assert chrome_pipe.find_chrome() == paths["google-chrome"]
    assert searched == []
    monkeypatch.setenv("CHROME", "/missing/legacy-chrome")
    assert chrome_pipe.find_chrome() == paths["chromium"]
    assert searched == ["/missing/legacy-chrome"]


@pytest.mark.parametrize("override", ["argument", "CHROME", "CHROMIUM"])
def test_invalid_explicit_selection_does_not_fall_back_to_path(browsers, monkeypatch, override):
    _, searched = browsers("chromium", "google-chrome")
    argument = "missing-explicit-browser" if override == "argument" else None
    if argument is None:
        monkeypatch.setenv(override, "missing-explicit-browser")
    with pytest.raises(RuntimeError, match="not found or not executable: missing-explicit-browser"):
        chrome_pipe.find_chrome(argument)
    assert searched == ["missing-explicit-browser"]


def test_nonexecutable_default_alias_is_skipped(browsers):
    paths, searched = browsers("chromium", "chromium-browser")
    Path(paths["chromium"]).chmod(0o644)
    assert chrome_pipe.find_chrome() == paths["chromium-browser"]
    assert searched == ["chromium", "chromium-browser"]
