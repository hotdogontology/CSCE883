"""Replay isolated ProofNet positives and export resolved type/proof dependencies."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts/relatedness-20261110'


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def replay_code(row, helper):
    # Keep scoped `set_option ... in` immediately adjacent to its theorem.
    return (row['context']+'\n\n'+row['formal_statement']+' := '+row['formal_proof']+
            '\n\n'+helper+'\n\n#proof_dependencies '+row['extracted_declaration']+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args()
    base = ROOT/'data/lean428'
    setup = json.loads((base/'setup.json').read_text())
    if setup['status'] != 'complete': raise ValueError('Lean4.28 environment not ready')
    work = base/'mathlib'
    lake = base/'lean-4.28.0-windows/bin/lake.exe'
    env = dict(os.environ)
    env['PATH'] = str(lake.parent)+os.pathsep+r'C:\Program Files\Git\cmd'+os.pathsep+env['PATH']
    env['GIT_CONFIG_COUNT']='1';env['GIT_CONFIG_KEY_0']='safe.directory'
    env['GIT_CONFIG_VALUE_0']=base.as_posix()+'/*'
    # Resolve Lean's dependency search path once; launch lean directly for each row.
    search = subprocess.check_output([str(lake),'env',sys.executable,'-c',
                                      "import os; print(os.environ['LEAN_PATH'])"],cwd=work,env=env,text=True).strip()
    env['LEAN_PATH'] = search
    helper = (ROOT/'lean/ProofDependencies.lean').read_text(encoding='utf-8')
    helper = re.sub(r'^import Lean\s*', '', helper)
    sources = read(ROOT/'artifacts/argument-14b/data-v4/positive-pairs.jsonl')
    if args.limit: sources = sources[:args.limit]
    (OUT/'replay').mkdir(parents=True,exist_ok=True)
    fingerprint = hashlib.sha256((helper+setup['mathlib_revision']).encode()).hexdigest()

    def run(row):
        target = OUT/'replay'/row['id']
        cached = target.with_suffix('.json')
        code = replay_code(row,helper)
        digest = hashlib.sha256((fingerprint+code).encode()).hexdigest()
        if cached.exists():
            data = json.loads(cached.read_text(encoding='utf-8'))
            if data.get('fingerprint')==digest:return data
            legacy = row['context']+'\n\n'+helper+'\n\n'+row['formal_statement']+' := '+row['formal_proof']
            legacy += '\n\n#proof_dependencies '+row['extracted_declaration']+'\n'
            legacy_digest=hashlib.sha256((fingerprint+legacy).encode()).hexdigest()
            if data.get('status')=='compiled' and data.get('fingerprint')==legacy_digest:
                return data  # An already successful replay with exactly these source/helper versions.
        target.with_suffix('.lean').write_text(code,encoding='utf-8')
        started = time.perf_counter()
        result = {'id':row['id'],'group':row['group'],'fingerprint':digest,
                  'source_sha256':row['source_file_sha256'],'mathlib_revision':setup['mathlib_revision']}
        try:
            proc = subprocess.run([str(lake.parent/'lean.exe'),str(target.with_suffix('.lean'))],
                                  cwd=work,env=env,capture_output=True,text=True,encoding='utf-8',
                                  errors='replace',timeout=args.timeout)
            log = proc.stdout+'\n'+proc.stderr
            target.with_suffix('.log').write_text(log,encoding='utf-8')
            lines = [s.removeprefix('PROOF_DEPENDENCIES ') for s in proc.stdout.splitlines()
                     if s.startswith('PROOF_DEPENDENCIES ')]
            if proc.returncode==0 and len(lines)==1:
                result.update(status='compiled',dependencies=json.loads(lines[0]))
            else:result.update(status='compile_failed',returncode=proc.returncode)
        except subprocess.TimeoutExpired:
            result['status']='timeout'
        result['seconds']=time.perf_counter()-started
        cached.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return result

    results=[]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for future in as_completed([executor.submit(run,row) for row in sources]):
            results.append(future.result())
            if len(results)%10==0:print('replayed',len(results),'/',len(sources),flush=True)
    results.sort(key=lambda r:int(r['id'].split('-')[-1]))
    with (OUT/'dependencies.jsonl').open('w',encoding='utf-8') as handle:
        for result in results:handle.write(json.dumps(result,ensure_ascii=False)+'\n')
    summary={'rows':len(results),'status_counts':{s:sum(r['status']==s for r in results)
             for s in sorted({r['status'] for r in results})},'mathlib_revision':setup['mathlib_revision'],
             'policy':'Isolated extracted target + retained helper context; successful elaboration required; no argument labels established.'}
    (OUT/'replay-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
