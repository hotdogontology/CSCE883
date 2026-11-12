"""Install isolated, workspace-local Lean/mathlib 4.28 for archived ProofNet replay."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/lean428'
GIT = r'C:\Program Files\Git\cmd\git.exe'
LEAN_SHA256 = 'faa0a8213ec81035d1ff3745d6d28e55b9d80de63fb9cd33380cd51b23cfc1aa'
MATHLIB_REV = '8f9d9cff6bd728b17a24e163c9402775d9e6a365'


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    state = {'status': 'starting', 'scope': 'isolated archived ProofNet environment', 'version': '4.28.0'}
    def save(stage):
        state['stage'] = stage
        (BASE/'setup.json').write_text(json.dumps(state, indent=2)+'\n', encoding='utf-8')
        print(stage, flush=True)
    try:
        save('release_metadata')
        response = requests.get('https://api.github.com/repos/leanprover/lean4/releases/tags/v4.28.0', timeout=60)
        response.raise_for_status()
        asset = next(a for a in response.json()['assets'] if a['name']=='lean-4.28.0-windows.zip')
        archive = BASE / asset['name']
        if not archive.exists():
            save('download_lean')
            with requests.get(asset['browser_download_url'], stream=True, timeout=120) as r:
                r.raise_for_status()
                with archive.with_suffix('.partial').open('wb') as handle:
                    for chunk in r.iter_content(8*1024*1024): handle.write(chunk)
            archive.with_suffix('.partial').replace(archive)
        digest = hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest()
        if digest != LEAN_SHA256 or 'sha256:'+digest != asset['digest']:
            raise ValueError('Pinned/official Lean digest mismatch')
        state['lean_sha256'] = digest
        lean = BASE/'lean-4.28.0-windows'
        if not (lean/'bin/lake.exe').exists():
            save('extract_lean')
            with zipfile.ZipFile(archive) as z:
                for member in z.infolist():
                    target = (BASE/member.filename).resolve()
                    if not target.is_relative_to(BASE.resolve()): raise ValueError('Unsafe archive path')
                z.extractall(BASE)
        env = dict(os.environ)
        env['PATH'] = str(lean/'bin')+os.pathsep+str(Path(GIT).parent)+os.pathsep+env['PATH']
        env['GIT_CONFIG_COUNT']='1'
        env['GIT_CONFIG_KEY_0']='safe.directory'
        env['GIT_CONFIG_VALUE_0']=BASE.as_posix()+'/*'
        env['GIT_TERMINAL_PROMPT']='0'
        mathlib = BASE/'mathlib'
        if not (mathlib/'.git').exists():
            save('clone_mathlib')
            subprocess.run([GIT,'clone','--depth','1','--branch','v4.28.0',
                            'https://github.com/leanprover-community/mathlib4.git',str(mathlib)],
                           env=env,check=True)
        state['mathlib_revision']=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=mathlib,env=env,text=True).strip()
        if state['mathlib_revision'] != MATHLIB_REV: raise ValueError('Mathlib tag differs from pinned revision')
        state['lean_version']=subprocess.check_output([str(lean/'bin/lean.exe'),'--version'],env=env,text=True).strip()
        save('lake_dependencies_and_cache')
        subprocess.run([str(lean/'bin/lake.exe'),'exe','cache','get'],cwd=mathlib,env=env,check=True)
        state['status']='complete'
        save('complete')
    except BaseException as exc:
        state['status']='failed';state['error']=str(exc);save(state.get('stage','unknown'));raise


if __name__=='__main__':main()
