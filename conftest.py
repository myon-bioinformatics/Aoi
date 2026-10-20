"""Optional cross-repository integration with an explicit fail-closed mode."""
from importlib import import_module
import importlib.util
import os
import sys
from pathlib import Path

import pytest

import aoi_paths

# 子（queryu/ など）の conftest.py は Aoi の場所を AOI_ROOT で受け取る。Aoi の中ではここで入れる
os.environ.setdefault("AOI_ROOT", str(aoi_paths.resolve_aoi_root(anchor=Path(__file__))))


def _install_npb_teams():
    """QueRyu's ask holds no team table; Aoi passes the NPB one (aoi_npb.TEAMS)."""
    try:
        import ask
    except ImportError:
        return
    import aoi_npb
    ask.set_teams(aoi_npb.TEAMS)


_install_npb_teams()


@pytest.fixture(scope="session")
def aoi_root() -> Path:
    return aoi_paths.resolve_aoi_root(anchor=Path(__file__))


LAB_INTEGRATION_NODE_IDS = {
    'blueprobe/tests/test_blueprobe_html_source.py::test_optional_real_lab_extractor_reuses_all_calendar_rows',
    'blueprobe/tests/test_blueprobe_html_compare.py::test_real_saved_npb_fixture_coverage_and_css',
    'blueprobe/tests/test_blueprobe_html_source.py::test_verified_cache_real_lab_snapshot_replay',
}
_LAB_REPORTS = pytest.StashKey[dict[str, dict[str, str]]]()


def pytest_addoption(parser):
    parser.addoption(
        '--require-lab-integration', action='store_true',
        help='Require all real offline mcp-toolcall-lab regressions to pass without skips.',
    )


def pytest_configure(config):
    config.stash[_LAB_REPORTS] = {}


@pytest.fixture
def lab_html_snapshot(pytestconfig, no_network):
    module_name = 'mcp_toolcall_lab.adapters.html_snapshot'
    if pytestconfig.getoption('--require-lab-integration'):
        source_root = os.environ.get('AOI_LAB_SOURCE_ROOT')
        if not source_root:
            pytest.fail('--require-lab-integration requires AOI_LAB_SOURCE_ROOT', pytrace=False)
        modules = {}
        try:
            for name in ('html_snapshot', 'css_inspect'):
                modules[name] = import_module(f'mcp_toolcall_lab.adapters.{name}')
        except ImportError as exc:
            pytest.fail(f'--require-lab-integration requires the lab extractors: {exc}', pytrace=False)
        for name, module in modules.items():
            expected = (Path(source_root) / 'mcp_toolcall_lab' / 'adapters' / f'{name}.py').resolve()
            origin = getattr(module, '__file__', None)
            if origin is None or Path(origin).resolve() != expected:
                pytest.fail(f'{module.__name__} imported from {origin}; expected {expected}', pytrace=False)
        return modules['html_snapshot']
    return pytest.importorskip(module_name, reason='optional cross-repository integration')


@pytest.fixture
def lab_source_access(pytestconfig, lab_html_snapshot):
    module = import_module('mcp_toolcall_lab.source_access')
    if pytestconfig.getoption('--require-lab-integration'):
        expected = (Path(os.environ['AOI_LAB_SOURCE_ROOT']) / 'mcp_toolcall_lab' / 'source_access.py').resolve()
        origin = getattr(module, '__file__', None)
        if origin is None or Path(origin).resolve() != expected:
            pytest.fail(f'{module.__name__} imported from {origin}; expected {expected}', pytrace=False)
    return module


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if item.config.getoption('--require-lab-integration') and report.nodeid in LAB_INTEGRATION_NODE_IDS:
        phases = item.config.stash[_LAB_REPORTS].setdefault(report.nodeid, {})
        phases[report.when] = report.outcome


def pytest_sessionfinish(session, exitstatus):
    if not session.config.getoption('--require-lab-integration'):
        return
    reports = session.config.stash[_LAB_REPORTS]
    passed = {'setup': 'passed', 'call': 'passed', 'teardown': 'passed'}
    incomplete = sorted(node_id for node_id in LAB_INTEGRATION_NODE_IDS
                        if reports.get(node_id) != passed)
    if incomplete:
        # A skip, xfail, deselection, or an accidentally narrowed test command
        # must never turn the dedicated integration check green.
        if exitstatus == pytest.ExitCode.OK:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED
        terminal = session.config.pluginmanager.get_plugin('terminalreporter')
        if terminal is not None:
            terminal.write_sep('=', 'required lab integration tests did not pass')
            for node_id in incomplete:
                terminal.write_line(f'{node_id}: {reports.get(node_id, "not run")}')


class _DistinctBasenameModule(pytest.Module):
    """Import one test file under a path-derived module name."""

    def _getobj(self):
        path = self.path.resolve()
        root = Path(self.config.rootpath).resolve()
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        module_name = 'aoi_test_' + '_'.join(rel.with_suffix('').parts)
        cached = sys.modules.get(module_name)
        if cached is not None and Path(getattr(cached, '__file__', '') or '').resolve() == path:
            return cached
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(module_name, None)
            raise
        self.config.pluginmanager.consider_module(module)
        return module


_DISTINCT_BASENAMES = frozenset({
    # Pure subtrees ship the same basename. Pytest's default import mode loads
    # it once, then aborts when the next copy does not match.
    'test_no_sibling_imports.py',
    'test_vendor_lock.py',
})


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makemodule(module_path, parent):
    if module_path.name not in _DISTINCT_BASENAMES:
        return None
    return _DistinctBasenameModule.from_parent(parent, path=module_path)
