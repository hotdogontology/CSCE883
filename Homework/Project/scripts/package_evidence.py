"""Archive text experiment evidence, deduplicated by SHA-256; never weights."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'reproducibility/evidence'
EXT = {'.json', '.jsonl', '.csv', '.log', '.txt', '.lean', '.yaml', '.yml'}

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    if (DEST / 'manifest.json').exists():
        raise SystemExit('Evidence already frozen; choose a new destination for a new snapshot.')
    files, blobs = [], {}
    for p in sorted((ROOT / 'artifacts').rglob('*')):
        if not p.is_file() or p.suffix.lower() not in EXT:
            continue
        if any(x in p.parts for x in ('.git', '__pycache__')) or p.name.startswith('.env'):
            continue
        with p.open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        files.append({'path': p.relative_to(ROOT).as_posix(), 'sha256': digest, 'bytes': p.stat().st_size})
        blobs.setdefault(digest, p)
    archives, locations = [], {}
    groups, group, size = [], [], 0
    for sha, p in blobs.items():
        if group and size + p.stat().st_size > 64 * 2**20:
            groups.append(group); group, size = [], 0
        group.append((sha, p)); size += p.stat().st_size
    if group:
        groups.append(group)
    for i, group in enumerate(groups, 1):
        path = DEST / f'evidence-{i:02d}.zip'
        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for sha, p in group:
                z.write(p, sha)
                locations[sha] = path.name
        if path.stat().st_size > 45 * 2**20:
            raise RuntimeError(f'Archive too large for planned Git distribution: {path.name}')
        archives.append({'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
    manifest = {'format': 1, 'scope': 'All text artifacts, including historical/superseded preparations. Use paper snapshot paths to identify reported runs; do not pool historical runs.',
                'excluded': 'Weights, binary estimators, environments, caches, and source-corpus downloads. Exact experimental input splits and text outputs are included.',
                'files': files, 'blobs': locations, 'archives': archives}
    (DEST / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(files), 'unique_blobs': len(blobs), 'archives': len(archives),
                      'compressed_MiB': sum(a['bytes'] for a in archives) / 2**20}))

if __name__ == '__main__':
    main()
