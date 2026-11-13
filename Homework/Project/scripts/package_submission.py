"""Package committed project deliverables, with file hashes and Git revision."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]

def main():
    git = shutil.which('git') or 'C:/Program Files/Git/cmd/git.exe'
    base = [git, '-c', f'safe.directory={REPO.as_posix()}', '-C', str(REPO)]
    prefix = ROOT.relative_to(REPO).as_posix() + '/'
    paths = subprocess.check_output(base + ['ls-files', '-z', '--', prefix]).decode().split('\0')
    revision = subprocess.check_output(base + ['rev-parse', 'HEAD']).decode().strip()
    dest = ROOT / 'submission'
    dest.mkdir(exist_ok=True)
    records = []
    with zipfile.ZipFile(dest / 'CSCE883-final-project.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in sorted(filter(None, paths)):
            p = REPO / name
            rel = p.relative_to(ROOT)
            if any(x in rel.parts for x in ('.git', '.venv', '__pycache__', 'build', 'submission')):
                continue
            assert not p.name.startswith('.env') or p.name in ('.env.example', '.env.sample'), 'Credential path rejected'
            assert p.suffix.lower() not in {'.safetensors', '.gguf', '.pt', '.pth', '.ckpt', '.bin'}, 'Weight/binary path rejected'
            data = p.read_bytes()
            z.writestr('Project/' + rel.as_posix(), data)
            records.append({'path': rel.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        manifest = {'repository': 'https://github.com/hotdogontology/CSCE883', 'commit': revision, 'files': records}
        z.writestr('SUBMISSION-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    with zipfile.ZipFile(dest / 'CSCE883-final-project.zip') as z:
        assert z.testzip() is None
        for r in records:
            assert hashlib.sha256(z.read('Project/' + r['path'])).hexdigest() == r['sha256']
    print(f'Packaged and verified {len(records)} files at commit {revision}.')
    print(dest / 'CSCE883-final-project.zip')

if __name__ == '__main__':
    main()
