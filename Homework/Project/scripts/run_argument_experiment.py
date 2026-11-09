"""Sequential unquantized proof-body experiment; no pseudo-label second pass."""
from collections import Counter
import csv
import ctypes
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import time

from two_pass import ROOT,read,metadata

OUT=ROOT/'artifacts/argument-14b'
DATA=OUT/'data-v3'
DEST=ROOT/'reports/argument-14b'
MANIFEST=ROOT/'model-manifest-14b.json'


def export(state):
    DEST.mkdir(parents=True,exist_ok=True)
    result={'observed_utc':datetime.now(timezone.utc).isoformat(),'job':state,
        'scope':'proof_argument_correspondence','quantization':None,'dtype':'BF16',
        'positive_labels':'User-assumed corrected ProofNet argument matches',
        'negative_labels':'Constructed cross-problem English proof swaps',
        'limitation':'Swapped-proof validation does not establish detection of subtle same-theorem alternative arguments',
        'runs':{}}
    for name in ['untuned-validation','tuned-validation','untuned-herald','tuned-herald']:
        path=OUT/name/'run.json'
        if path.exists():result['runs'][name]=json.loads(path.read_text(encoding='utf-8'))
    for name in ['probe-8192','probe-4096','probe-2048','fine-tuned']:
        path=OUT/name/('training.json' if name=='fine-tuned' else 'probe.json')
        if path.exists():result[name]=json.loads(path.read_text(encoding='utf-8'))
    metadata(DEST/'latest.json',result)
    lines=['# Unquantized Qwen3-14B proof-argument experiment','',
        f"Observed UTC: {result['observed_utc']}",f"Job: {state['status']}; stage: {state.get('stage')}",'',
        'Both English and Lean proof bodies are inputs. BF16 model weights; no quantization.',
        'Positive correspondence assumed per user instruction; negatives are synthetic proof swaps.','',
        '| Model / corpus | Status | Rows | Accuracy |','| --- | --- | ---: | ---: |']
    for name,r in result['runs'].items():
        accuracy=r.get('accuracy')
        lines.append(f"| {name} | {r['status']} | {r.get('rows','')} | "+(f'{accuracy:.2%}' if accuracy is not None else 'unlabeled')+' |')
    lines+=['','No Herald accuracy claim is possible without independent labels.',
        'All token-budget and extraction failures are missing predictions, never negative labels.']
    (DEST/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    a,b=[OUT/n/'predictions.jsonl' for n in ['untuned-herald','tuned-herald']]
    if a.exists() and b.exists() and all(result['runs'].get(n,{}).get('status')=='complete' for n in ['untuned-herald','tuned-herald']):
        left,right=[{r['id']:r for r in read(p)} for p in [a,b]]
        counts=Counter()
        with (OUT/'herald-comparison.csv').open('w',encoding='utf-8',newline='') as f:
            writer=csv.writer(f);writer.writerow(['id','untuned','fine_tuned','comparison'])
            for identity in sorted(set(left)|set(right)):
                x,y=left.get(identity,{}).get('prediction'),right.get(identity,{}).get('prediction')
                kind='missing' if x is None or y is None else 'agreement' if x==y else 'disagreement'
                counts[kind]+=1;writer.writerow([identity,x,y,kind])
        metadata(DEST/'herald-summary.json',dict(counts))
    metrics=[]
    for name,r in result['runs'].items():
        if 'metrics' in r:
            for cls,m in r['metrics']['classes'].items():
                metrics.append({'model':name,'class':cls,'precision':m['precision'],'recall':m['recall'],
                    'f1':m['f1-score'],'support':m['support'],'accuracy':r['accuracy'],
                    'macro_f1':r['metrics']['macro']['f1-score'],'coverage':r['metrics']['coverage']})
    if metrics:
        with (DEST/'classification-metrics.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)


def command(name,args,marker):
    if marker.exists() and json.loads(marker.read_text(encoding='utf-8')).get('status')=='complete':return
    with (OUT/(name+'.log')).open('a',encoding='utf-8') as log:
        result=subprocess.run([sys.executable,str(ROOT/'scripts/argument_model.py'),*args],
            cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(f'{name} failed; inspect {name}.log')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    state={'status':'running','stage':'waiting_for_verified_download','started_utc':datetime.now(timezone.utc).isoformat(),
        'second_pass':False,'model':'Qwen/Qwen3-14B','scope':'argument_fidelity','quantization':None}
    awake=ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    if not awake:raise RuntimeError('Cannot hold temporary Windows execution request')
    def save():
        state['updated_utc']=datetime.now(timezone.utc).isoformat()
        metadata(OUT/'job.json',state);export(state)
    try:
        save()
        while True:
            if MANIFEST.exists() and json.loads(MANIFEST.read_text(encoding='utf-8')).get('download_complete'):break
            if time.time()-datetime.fromisoformat(state['started_utc']).timestamp()>8*3600:
                raise RuntimeError('Download not verified within eight hours; no training started')
            time.sleep(30)
        info=json.loads(MANIFEST.read_text(encoding='utf-8'))
        if info['repo_id']!='Qwen/Qwen3-14B':raise ValueError('Incorrect model manifest')
        # The already-running downloader predates the CLI local-directory fix.
        # Its hashes verify the 14B download; correct that metadata field only.
        if info['local_directory']!='data/models/Qwen3-14B':
            info['local_directory']='data/models/Qwen3-14B';metadata(MANIFEST,info)
        for budget in [8192,4096,2048]:
            name=f'probe-{budget}';state['stage']=name;save()
            try:
                command(name,['probe','--input',str(DATA/'train.jsonl'),'--output',str(OUT/name),
                    '--max-tokens',str(budget)],OUT/name/'probe.json')
                break
            except RuntimeError:
                failure=json.loads((OUT/name/'probe.json').read_text(encoding='utf-8'))
                if 'out of memory' not in failure.get('error','').lower():raise
        else:raise RuntimeError('No tested unquantized training budget fits; no quantized fallback allowed')
        state['max_tokens']=budget
        steps=[('untuned-validation','predict',DATA/'validation.jsonl',None),
            ('fine-tuned','train',DATA/'train.jsonl',None),
            ('tuned-validation','predict',DATA/'validation.jsonl',OUT/'fine-tuned/adapter'),
            ('untuned-herald','predict',DATA/'herald.jsonl',None),
            ('tuned-herald','predict',DATA/'herald.jsonl',OUT/'fine-tuned/adapter')]
        for name,action,input_path,adapter in steps:
            state['stage']=name;save()
            args=[action,'--input',str(input_path),'--output',str(OUT/name),'--max-tokens',str(budget)]
            if adapter:args+=['--adapter',str(adapter)]
            command(name,args,OUT/name/('training.json' if action=='train' else 'run.json'))
            state.setdefault('completed_stages',[]).append(name);save()
        state['status']='complete'
    except BaseException as error:
        state.update(status='failed',error=repr(error));raise
    finally:
        save();ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__=='__main__':main()
