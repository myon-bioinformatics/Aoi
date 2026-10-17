"""Real Chrome tests are optional locally and mandatory in their CI job."""
import os
import importlib.util

import pytest

from dragowing.chrome_pipe import find_chrome


@pytest.fixture
def chrome_executable():
    try:
        return find_chrome()
    except RuntimeError as exc:
        if os.environ.get("DRAGOWING_REQUIRE_CHROME") == "1":
            pytest.fail(str(exc), pytrace=False)
        pytest.skip(str(exc))


@pytest.fixture
def plotly_chrome_executable(chrome_executable):
    if importlib.util.find_spec("plotly") is None:
        reason = "Plotly image export requires the optional export extra"
        if os.environ.get("DRAGOWING_REQUIRE_CHROME") == "1":
            pytest.fail(reason, pytrace=False)
        pytest.skip(reason)
    return chrome_executable
