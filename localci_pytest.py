"""pytest plugin: shard one round, and monkeypatch seeded input substitution.

  pytest -p localci_pytest --localci-repeat 10 --localci-round 3 --localci-seed 7

`--localci-round` を省略すると絞らない。`--localci-seed` があるときは
`localci.substitute` が固定値ではなく seed からの値を返す。
"""

from __future__ import annotations

import os
import random

import pytest

import localci


def pytest_addoption(parser):
    parser.addoption("--localci-repeat", type=int, default=None)
    parser.addoption("--localci-round", type=int, default=None)
    parser.addoption("--localci-seed", default=None)
    parser.addoption("--localci-activate", action="store_true")


def pytest_configure(config):
    raw = config.getoption("localci_seed")
    if raw is None or raw == "":
        return
    seed = int(raw)
    mp = pytest.MonkeyPatch()
    config._localci_monkeypatch = mp
    mp.setattr(localci, "_active_rng", random.Random(seed))


def pytest_unconfigure(config):
    mp = getattr(config, "_localci_monkeypatch", None)
    if mp is not None:
        mp.undo()


def pytest_collection_modifyitems(config, items):
    repeat = config.getoption("localci_repeat")
    round_no = config.getoption("localci_round")
    raw_seed = config.getoption("localci_seed")
    if not repeat or round_no is None or raw_seed is None or raw_seed == "":
        return
    ids = [item.nodeid for item in items]
    chosen = localci.shard_for_round(ids, int(repeat), int(round_no), int(raw_seed))
    order = {node: index for index, node in enumerate(chosen)}
    selected = [item for item in items if item.nodeid in order]
    selected.sort(key=lambda item: order[item.nodeid])
    deselected = [item for item in items if item.nodeid not in order]
    items[:] = selected
    if deselected:
        config.hook.pytest_deselected(items=deselected)


def pytest_runtest_teardown(item, nextitem):
    del item, nextitem
    log = os.environ.get("LOCALCI_INPUT_LOG", "")
    notes = localci.take_substitutions()
    if not log or not notes:
        return
    with open(log, "a", encoding="utf-8") as fh:
        for note in notes:
            fixed = str(note["fixed"]).replace("\t", " ").replace("\n", " ")
            value = str(note["value"]).replace("\t", " ").replace("\n", " ")
            fh.write(f"{note['name']}\t{fixed}\t{value}\n")
