"""Finish dependency replay, mine unlabeled candidates and survey frozen classifiers."""
from collections import Counter
import ctypes
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/relatedness-20261110'
REPORT=ROOT/'reports/relatedness-20261110'


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def main():
    OUT.mkdir(parents=True,exist_ok=True);REPORT.mkdir(parents=True,exist_ok=True)
    state={'status':'running','training':False,'labels':'Unreviewed candidates; no accuracy claims'}
    def stage(name):
        state['stage']=name
        (OUT/'job.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
        print(name,flush=True)
    def run(name, command):
        stage(name)
        with (OUT/(name+'.log')).open('w',encoding='utf-8') as log:
            subprocess.run([sys.executable,*command],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    awake=ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:
        stage('waiting_for_initial_full_replay')
        deadline=time.monotonic()+3600
        while True:
            marker=OUT/'replay-summary.json'
            if marker.exists() and json.loads(marker.read_text())['rows']==365:break
            if time.monotonic()>deadline:raise TimeoutError('Initial replay not complete within one hour')
            time.sleep(10)
        # Reuses successful exact-version cached replays, fixes scoped-option insertion failures.
        run('replay_final',['scripts/extract_proof_dependencies.py','--workers','6'])
        run('mine',['scripts/mine_related_proofs.py'])
        run('forest',['scripts/random_forest_argument.py','--candidate-file',str(OUT/'validation-candidates.jsonl'),
                      '--output-dir',str(REPORT/'forest')])
        # Verify extending the RF runner did not change its frozen original comparisons.
        old=json.loads((ROOT/'reports/random-forest-20261110/metrics.json').read_text())
        forest=json.loads((REPORT/'forest/metrics.json').read_text())
        for model in old['models']:
            for split in ['validation','same_theorem_diagnostic']:
                if old['models'][model][split]!=forest['models'][model][split]:
                    raise ValueError('Random forest frozen-result regression')
        gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True)
        if int(gpu.strip().splitlines()[0])>5000:raise RuntimeError('GPU busy; stop before loading Qwen')
        for name in ['untuned','tuned']:
            command=['scripts/argument_model.py','predict','--input',str(OUT/'validation-candidates.jsonl'),
                     '--output',str(OUT/name),'--max-tokens','4096']
            if name=='tuned':command+=['--adapter',str(ROOT/'artifacts/argument-14b/overnight-20261109/fine-tuned/adapter')]
            run(name,command)
        stage('aggregate')
        candidates=read(OUT/'validation-candidates.jsonl');by_id={r['id']:r for r in candidates}
        aggregate={'scope':'Descriptive survey of UNLABELED related swaps; no candidate accuracy computed',
                   'replay':json.loads((OUT/'replay-summary.json').read_text()),
                   'mining':json.loads((OUT/'mining-summary.json').read_text()),
                   'environment':json.loads((ROOT/'data/lean428/setup.json').read_text()),
                   'models':{}}
        for name in ['untuned','tuned']:
            predictions=read(OUT/name/'predictions.jsonl')
            counts={}
            for kind in sorted({r['pair_kind'] for r in candidates}):
                subset=[p for p in predictions if by_id[p['id']]['pair_kind']==kind]
                counts[kind]={'rows':len(subset),'status_counts':dict(Counter(p['status'] for p in subset)),
                              'yes_count':sum(p['prediction'] is True for p in subset),
                              'no_count':sum(p['prediction'] is False for p in subset)}
            # Original control payloads must reproduce their previous frozen predictions.
            previous={p['id']:p for p in read(ROOT/'artifacts/argument-14b/overnight-20261109'/
                                             (name+'-validation')/'predictions.jsonl')}
            for prediction in predictions:
                if by_id[prediction['id']]['pair_kind']=='source_positive_control':
                    source=prediction['id'].removesuffix('-related-control')
                    if prediction['prediction']!=previous[source]['prediction']:
                        raise ValueError('Qwen source-control prediction regression: '+prediction['id'])
            aggregate['models'][name]=counts
        for name,metrics in forest['models'].items():aggregate['models']['forest_'+name]=metrics['candidate_survey']
        (REPORT/'summary.json').write_text(json.dumps(aggregate,indent=2)+'\n',encoding='utf-8')
        state['status']='complete';stage('complete')
    except BaseException as exc:
        state['status']='failed';state['error']=repr(exc);stage(state.get('stage','unknown'));raise
    finally:
        if awake:ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


if __name__=='__main__':main()
