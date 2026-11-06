"""Fetch pinned public source snapshots; preserve labels and record checksums."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('proofnet-verified', 'marcusm117/ProofNet-Verified',
     '14879cb23e078d122adecd9578dd26a7304f753b', 'statement correspondence'),
    ('faithsieve', 'TropicalFatFish/anonymous-faithsieve',
     '7df6da7fd7661d69fe875673f06770d260e4fd12', 'proof correctness / first-error location'),
]


def main():
    manifest = {'downloaded_utc': datetime.now(timezone.utc).isoformat(),
                'usage': 'reserved reference/evaluation candidates; no training split assigned',
                'local_lean_replay': False, 'argument_fidelity_labels_imported': False,
                'sources': []}
    for name, repo, rev, target in SOURCES:
        url = f'https://codeload.github.com/{repo}/zip/{rev}'
        req = urllib.request.Request(url, headers={'User-Agent': 'CSCE883-research'})
        payload = urllib.request.urlopen(req, timeout=120).read()
        dest = ROOT / 'data' / name / rev
        dest.mkdir(parents=True, exist_ok=True)
        (dest / 'source.zip').write_bytes(payload)
        records = []
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                relative = Path(*Path(member.filename).parts[1:])
                output = (dest / 'source' / relative).resolve()
                if not output.is_relative_to((dest / 'source').resolve()):
                    raise ValueError('Unsafe archive path')
                data = archive.read(member)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(data)
                record = {'path': relative.as_posix(), 'bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest()}
                if relative.suffix == '.jsonl':
                    rows = [json.loads(line) for line in data.decode('utf-8-sig').splitlines() if line.strip()]
                    record.update(rows=len(rows), fields=sorted(set().union(*(r.keys() for r in rows))))
                    if rows and 'first_error_step' in rows[0]:
                        record['correctness_counts'] = dict(Counter(
                            'correct' if r['first_error_step'] == 'correct' else 'contains_error' for r in rows))
                records.append(record)
        source = {'name': name, 'repository': 'https://github.com/' + repo,
                  'revision': rev, 'url': url, 'local_directory': dest.relative_to(ROOT).as_posix(),
                  'published_target': target, 'archive_bytes': len(payload),
                  'archive_sha256': hashlib.sha256(payload).hexdigest(), 'files': records}
        manifest['sources'].append(source)
        print(json.dumps({'name': name, 'files': len(records), 'bytes': len(payload),
                          'jsonl': [r for r in records if 'rows' in r]}), flush=True)
    (ROOT / 'verified-data-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
