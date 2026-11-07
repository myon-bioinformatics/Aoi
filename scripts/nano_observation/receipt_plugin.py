import json, os
from pathlib import Path
DATA = {'nodeids': [], 'phases': [], 'plugins': []}
def pytest_collection_finish(session):
    DATA['nodeids'] = [item.nodeid for item in session.items]
    DATA['plugins'] = sorted((dist.project_name, dist.version) for plugin, dist in session.config.pluginmanager.list_plugin_distinfo())
    DATA['config'] = str(session.config.inipath.relative_to(session.config.rootpath))
def pytest_runtest_logreport(report):
    DATA['phases'].append([report.nodeid, report.when, report.outcome])
def pytest_sessionfinish(session, exitstatus):
    DATA['exitstatus'] = int(exitstatus)
    Path(os.environ['RECEIPT_PATH']).write_text(json.dumps(DATA, sort_keys=True))
