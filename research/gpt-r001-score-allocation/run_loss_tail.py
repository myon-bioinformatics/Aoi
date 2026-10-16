"""Sequential tests -> analysis -> judgement; preserve actual child exit codes."""
import json
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent

def main():
    steps=[('tests',[sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_*.py']),
           ('analysis',[sys.executable,str(HERE/'loss_tail.py'),'analyze']),
           ('judgement',[sys.executable,str(HERE/'loss_tail.py'),'judge'])]
    records=[]
    for name,cmd in steps:
        result=subprocess.run(cmd,cwd=HERE.parents[1],text=True,capture_output=True)
        records.append(dict(stage=name,command=cmd,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))
        print(f'{name}: exit={result.returncode}',flush=True)
        if result.returncode and name!='judgement':
            break
    code=records[-1]['exit_code']
    out=HERE/'outputs';out.mkdir(exist_ok=True)
    (out/'loss_tail_sequential.json').write_text(json.dumps(dict(stages=records,exit_code=code),ensure_ascii=False,indent=2)+'\n')
    return code

if __name__=='__main__':
    sys.exit(main())
