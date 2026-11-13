"""Verify archived evidence; optionally restore it without overwriting changes."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verify-only', action='store_true')
    ap.add_argument('--destination', type=Path, default=ROOT)
    args = ap.parse_args()
    source = ROOT / 'reproducibility/evidence'
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
    dest = args.destination.resolve()
    by_sha = {}
    for row in manifest['files']:
        rel = PurePosixPath(row['path'])
        if rel.is_absolute() or '..' in rel.parts or ':' in row['path'] or '\\' in row['path'] or rel.parts[0] != 'artifacts':
            raise ValueError('Unsafe evidence path')
        by_sha.setdefault(row['sha256'], []).append(row)
    count = 0
    for archive in manifest['archives']:
        name = archive['path']
        if Path(name).name != name:
            raise ValueError('Unsafe archive path')
        path = source / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == archive['sha256'], name
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None, name
            for member in z.namelist():
                assert manifest['blobs'][member] == name
                payload = z.read(member)
                assert hashlib.sha256(payload).hexdigest() == member
                for row in by_sha[member]:
                    assert len(payload) == row['bytes']
                    count += 1
                    if args.verify_only:
                        continue
                    target = (dest / row['path']).resolve()
                    assert target.is_relative_to(dest)
                    if target.exists():
                        assert hashlib.sha256(target.read_bytes()).hexdigest() == member, f'Refusing to overwrite changed file: {target}'
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(payload)
    assert count == len(manifest['files'])
    print(f'Verified {count} file records; ' + ('no files restored.' if args.verify_only else f'restored to {dest}.'))

if __name__ == '__main__':
    main()
