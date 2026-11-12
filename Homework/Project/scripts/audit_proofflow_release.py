"""Download pinned ProofFlow JSON artifacts and inventory unlabeled proof pairs.

Never deserialize upstream pickles or infer fidelity labels from compilation.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import hashlib
import json
import urllib.request
import urllib.parse
import time

ROOT = Path(__file__).resolve().parents[1]
REV = '97f1b7be82380733fb0380973c164e40645ae9da'
BASE = ROOT / 'data/proofflow' / REV
REPORT = ROOT / 'reports/proofflow32'


def fetch(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=90) as response:
                return response.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    tree = json.loads(fetch(f'https://api.github.com/repos/Huawei-AI4Math/ProofFlow/git/trees/{REV}?recursive=1'))
    assert not tree.get('truncated'), 'Incomplete upstream tree'
    entries = [x for x in tree['tree'] if x['path'].endswith('.json') and
               (x['path'].startswith('benchmark_results/output_pickle/') or
                x['path'] == 'data/benchmark_0409.json')]

    def download(entry):
        rel = entry['path']
        target = BASE / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            raw = fetch(f'https://raw.githubusercontent.com/Huawei-AI4Math/ProofFlow/{REV}/' + urllib.parse.quote(rel))
            json.loads(raw)
            target.write_bytes(raw)
        raw = target.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert blob == entry['sha'], f'Upstream hash mismatch: {rel}'
        return rel, json.loads(raw), hashlib.sha256(raw).hexdigest()

    records, manifest, schemas = [], [], Counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        for index, (rel, obj, digest) in enumerate(pool.map(download, entries), 1):
            manifest.append({'path': rel, 'sha256': digest})
            if isinstance(obj, dict):
                schemas[tuple(sorted(obj))] += 1
                result = obj.get('Lean_results') or {}
                code = result.get('lean_code') if isinstance(result, dict) else None
                if code and obj.get('original_proof'):
                    records.append({'id': rel, 'source_group': Path(rel).stem,
                                    'english_statement': obj.get('original_theorem'),
                                    'english_proof': obj['original_proof'], 'lean_code': code,
                                    'reported_lean_pass': result.get('lean_pass'),
                                    'reported_lean_verify': result.get('lean_verify'),
                                    'label': None, 'label_status': 'unknown_argument_fidelity',
                                    'source_revision': REV, 'source_sha256': digest})
            if index % 50 == 0:
                print(f'Audited {index}/{len(entries)} JSON files', flush=True)
    (BASE / 'pairs-unlabeled.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    audit = {'revision': REV, 'files': len(manifest), 'extracted_pairs': len(records),
             'source_groups': len({r['source_group'] for r in records}),
             'reported_lean_pass': dict(Counter(str(r['reported_lean_pass']) for r in records)),
             'schemas': [{'keys': list(k), 'count': v} for k, v in schemas.items()],
             'label_policy': 'All semantic correspondence labels unknown; compilation is not fidelity.',
             'files_manifest': manifest}
    (REPORT / 'release-audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in audit.items() if k not in ('files_manifest', 'schemas')}), flush=True)


if __name__ == '__main__':
    main()
