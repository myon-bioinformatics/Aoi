"""Run six fresh-environment samples; writes only under build/experiment.

Requires uv and an existing compatible Python. Downloads locked packages.
Use a fresh checkout: existing sample directories are intentionally rejected.
"""
import json, os, pathlib, shutil, subprocess, sys, time
root=pathlib.Path(__file__).resolve().parents[2]
work=root/'build'/'experiment'
tests=['tests/test_blueprobe_accessible_names.py','tests/test_blueprobe_emoji_observations.py','tests/test_blueprobe_heading_observations.py','tests/test_blueprobe_snapshot_source.py','tests/test_web_observations.py','tests/test_accessible_iterative_walk.py']
work.mkdir(parents=True, exist_ok=True)
if any(work.glob('[1-6]-*')):
    raise SystemExit('Existing samples found; use a fresh checkout to preserve them.')
shutil.copyfile(pathlib.Path(__file__).with_name('receipt_plugin.py'), work/'receipt_plugin.py')
results=[]
def save():
    (work/'results.json').write_text(json.dumps({'source_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'python':sys.version,'uv':subprocess.check_output(['uv','--version'],text=True).strip(),'tests':tests,'samples':results},indent=2)+'\n')
def run(cmd, env, log):
    start=time.perf_counter()
    p=subprocess.run(cmd,cwd=root,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.write_text(p.stdout)
    return p.returncode,time.perf_counter()-start
def size(path):
    return sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not p.is_symlink())
for index, kind in enumerate(['full','nano','nano','full','full','nano']):
    d=work/f'{index+1}-{kind}'; d.mkdir()
    env=dict(os.environ, UV_CACHE_DIR=str(d/'cache'), UV_PROJECT_ENVIRONMENT=str(d/'venv'), UV_PYTHON_DOWNLOADS='never', PYTHONPATH=str(work), RECEIPT_PATH=str(d/'receipt.json'))
    cmd=['uv','sync','--locked','--python',sys.executable]
    if kind=='nano': cmd+=['--only-group','observation-test']
    rc,seconds=run(cmd,env,d/'install.log')
    row={'sample':index+1,'kind':kind,'install_seconds':seconds,'install_exit':rc}
    results.append(row)
    save()
    if rc: raise SystemExit(rc)
    py=str(d/'venv/bin/python')
    row['venv_regular_bytes']=size(d/'venv'); row['cache_regular_bytes']=size(d/'cache')
    row['packages']=json.loads(subprocess.check_output([py,'-c','import importlib.metadata as m,json;print(json.dumps(sorted((d.metadata["Name"],d.version) for d in m.distributions())))'],text=True))
    rc,seconds=run([py,'-m','pytest','-q','-p','receipt_plugin',*tests],env,d/'test.log')
    row.update(test_exit=rc,test_seconds=seconds,receipt=json.loads((d/'receipt.json').read_text()))
    checkrc,checksec=run(['uv','pip','check','--python',py,'--offline'],env,d/'check.log'); row['pip_check_exit']=checkrc
    save()
    print(row['sample'],kind,row['install_exit'],row['test_exit'],row['test_seconds'],flush=True)
    if rc or checkrc: raise SystemExit(rc or checkrc)

if not all(row['receipt'] == results[0]['receipt'] for row in results):
    raise SystemExit('Collection, external plugins or outcomes differ; inspect raw receipts.')
if len(results[0]['receipt']['nodeids']) != 49:
    raise SystemExit('Expected 49 selected tests; review the source and test selection.')
if any(phase[2] != 'passed' for row in results for phase in row['receipt']['phases']):
    raise SystemExit('A test phase did not pass; inspect raw receipts.')
