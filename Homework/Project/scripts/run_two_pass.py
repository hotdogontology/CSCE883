"""Sequential, resumable job driver; no simultaneous GPU jobs."""
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/two-pass'
DATA = OUT / 'data'
FIRST = OUT / 'first-pass-statement-v2/adapter'


def main():
    steps = []
    def predict(name, source, adapter=None):
        cmd=['predict','--input',str(source),'--output',str(OUT/name)]
        if adapter: cmd += ['--adapter',str(adapter)]
        steps.append((name,cmd,OUT/name/'run.json'))
    predict('untuned-validation',DATA/'proofnet-validation.jsonl')
    predict('first-pass-validation',DATA/'proofnet-validation.jsonl',FIRST)
    predict('untuned-herald',DATA/'herald.jsonl')
    predict('first-pass-herald',DATA/'herald.jsonl',FIRST)
    steps.append(('consensus',['consensus','--input',str(DATA/'herald.jsonl'),
        '--untuned',str(OUT/'untuned-herald/predictions.jsonl'),
        '--first-pass',str(OUT/'first-pass-herald/predictions.jsonl'),
        '--output',str(OUT/'consensus')],OUT/'consensus/summary.json'))
    steps.append(('second-pass-training',['train','--input',str(OUT/'consensus/train.jsonl'),
        '--output',str(OUT/'second-pass-statement'),'--epochs','1'],OUT/'second-pass-statement/training.json'))
    second=OUT/'second-pass-statement/adapter'
    predict('second-pass-validation',DATA/'proofnet-validation.jsonl',second)
    for name, adapter in [('untuned',None),('first-pass',FIRST),('second-pass',second)]:
        predict(name+'-external',DATA/'external.jsonl',adapter)
    status={'status':'running','stages':[],'scope':'statement_fidelity',
        'script_sha256':__import__('hashlib').sha256((ROOT/'scripts/two_pass.py').read_bytes()).hexdigest()}
    try:
        for name,cmd,marker in steps:
            status['current_stage']=name
            status['updated_utc']=datetime.now(timezone.utc).isoformat()
            (OUT/'job.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
            if marker.exists():
                previous=json.loads(marker.read_text(encoding='utf-8'))
                if previous.get('status')=='complete' or name=='consensus':
                    status['stages'].append({'name':name,'status':'previously_complete'})
                    continue
                if 'training' in name:
                    raise RuntimeError('Interrupted training needs explicit recovery into a fresh output directory')
            with (OUT/(name+'.log')).open('a',encoding='utf-8') as log:
                result=subprocess.run([sys.executable,str(ROOT/'scripts/two_pass.py'),*cmd],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError(f'{name} failed: see {name}.log')
            status['stages'].append({'name':name,'status':'complete'})
            subprocess.run([sys.executable,str(ROOT/'scripts/report_two_pass.py')],cwd=ROOT,check=True,
                stdout=subprocess.DEVNULL)
        status['status']='complete'
    except BaseException as error:
        status.update(status='failed',error=repr(error))
        raise
    finally:
        status['updated_utc']=datetime.now(timezone.utc).isoformat()
        (OUT/'job.json').write_text(json.dumps(status,indent=2),encoding='utf-8')


if __name__=='__main__':main()
