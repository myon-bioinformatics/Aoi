"""Real Chrome tests are optional locally and mandatory in their CI job."""
import os

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
