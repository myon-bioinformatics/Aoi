"""テストでは球団表を fixtures/teams.json から入れる（本番は呼び出し側が ask.set_teams / --teams で渡す）。"""
import json
from pathlib import Path

import pytest

TEAMS = json.loads((Path(__file__).with_name("fixtures") / "teams.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _ask_teams():
    import ask
    before = dict(ask.TEAMS)
    ask.set_teams(TEAMS)
    yield
    ask.set_teams(before)
