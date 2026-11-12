"""Audited BF16 pilot, same-theorem diagnostic and Herald; no second-pass training."""
from collections import Counter, defaultdict
import csv
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from two_pass import ROOT, read, metadata, sha

BASE_OUT = ROOT / 'artifacts/argument-14b'
OUT = BASE_OUT / 'overnight-20261109'
DATA = BASE_OUT / 'data-v4'
BUDGET_DATA = OUT / 'budget-data'
CORE = BASE_OUT / 'core/test.jsonl'
CORE_MASKED = CORE.parent / 'test-formal-masked.jsonl'
DEST = ROOT / 'reports/argument-14b-overnight'
MANIFEST = ROOT / 'model-manifest-14b.json'
LOCK = BASE_OUT / 'gpu-driver.lock'
WORKER = BASE_OUT / 'active-worker.json'
PREDICTION_STAGES = ['untuned-validation', 'tuned-validation', 'untuned-core', 'tuned-core',
    'untuned-core-masked', 'tuned-core-masked', 'untuned-herald', 'tuned-herald']


def utc():
    return datetime.now(timezone.utc).isoformat()


def process_alive(pid):
    kernel = ctypes.windll.kernel32
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000, False, int(pid))
    if not handle:
        return False
    try:
        code = wintypes.DWORD()
        return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
    finally:
        kernel.CloseHandle(handle)


def acquire_lock():
    BASE_OUT.mkdir(parents=True, exist_ok=True)
    if WORKER.exists():
        old_worker = json.loads(WORKER.read_text(encoding='utf-8'))
        if process_alive(old_worker['pid']):
            raise RuntimeError('A previous experiment worker is still active; refusing duplicate GPU job')
        WORKER.unlink()
    if LOCK.exists():
        old = json.loads(LOCK.read_text(encoding='utf-8'))
        if process_alive(old['pid']):
            raise RuntimeError('An argument GPU driver is active; refusing duplicate job')
        LOCK.unlink()  # Exact task lock only, never recursive cleanup.
    for candidate in [BASE_OUT, ROOT / 'artifacts/two-pass', OUT]:
        job, pid_file = candidate / 'job.json', candidate / 'job.pid'
        if job.exists() and pid_file.exists():
            previous = json.loads(job.read_text(encoding='utf-8-sig'))
            pid = int(pid_file.read_text().strip())
            if previous.get('status') == 'running' and pid != os.getpid() and process_alive(pid):
                raise RuntimeError('Existing experiment driver is active: ' + str(candidate))
    with LOCK.open('x', encoding='utf-8') as output:
        json.dump({'pid': os.getpid(), 'started_utc': utc(), 'output': str(OUT)}, output)


def validate_hashes(root, manifest):
    for relative, expected in manifest.get('files', {}).items():
        if not isinstance(expected, str):
            raise ValueError('Expected path-to-SHA256 mapping in files')
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('Manifest path escapes dataset directory')
        if sha(path.read_bytes()) != expected:
            raise ValueError('Dataset file fingerprint mismatch: ' + relative)


def validate_core(rows):
    """Each side separately appears under both labels in every four-cell matrix."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['group']].append(row)
        if type(row.get('label')) is not bool:
            raise ValueError('Core labels must be booleans')
        for key in ['informal_statement', 'informal_proof', 'formal_statement', 'formal_proof', 'context']:
            if not isinstance(row.get(key), str) or (key != 'context' and not row[key].strip()):
                raise ValueError('Incomplete core argument evidence')
    if not grouped:
        raise ValueError('Core test is empty')
    for name, group in grouped.items():
        if len(group) != 4 or Counter(r['label'] for r in group) != {True: 2, False: 2}:
            raise ValueError('Core group is not a balanced four-cell matrix: ' + name)
        if len({r['informal_statement'] for r in group}) != 1 or len({r['formal_statement'] for r in group}) != 1:
            raise ValueError('Core theorem statements vary within matrix: ' + name)
        for fields in [('informal_statement', 'informal_proof'), ('formal_statement', 'formal_proof', 'context')]:
            side = defaultdict(list)
            for row in group:
                side[tuple(row[k] for k in fields)].append(row['label'])
            if len(side) != 2 or any(Counter(labels) != {True: 1, False: 1} for labels in side.values()):
                raise ValueError('One-sided core evidence predicts a label: ' + name)
    return len(grouped)


def readiness():
    integrity_path, data_path = DATA / 'integrity.json', DATA / 'manifest.json'
    core_path = CORE.parent / 'manifest.json'
    for path in [integrity_path, data_path, CORE, CORE_MASKED, core_path, MANIFEST]:
        if not path.exists():
            raise ValueError('Required readiness artifact missing: ' + str(path))
    integrity = json.loads(integrity_path.read_text(encoding='utf-8'))
    if integrity.get('ready_for_training') is not True:
        raise ValueError('Corrected data have not passed integrity checks')
    data_manifest = json.loads(data_path.read_text(encoding='utf-8'))
    for name in ['train.jsonl', 'validation.jsonl', 'herald.jsonl']:
        if name not in data_manifest.get('files', {}):
            raise ValueError('Required dataset fingerprint absent: ' + name)
    validate_hashes(DATA, data_manifest)
    core_manifest = json.loads(core_path.read_text(encoding='utf-8'))
    if core_manifest.get('ready_for_evaluation') is not True:
        raise ValueError('Constructed core test is not declared ready')
    if core_manifest.get('compiled') is not True and core_manifest.get('lean_build_status') != 'passed':
        raise ValueError('Core Lean build has not passed')
    validate_hashes(CORE.parent, core_manifest)
    for path in [CORE, CORE_MASKED]:
        expected = core_manifest.get('files', {}).get(path.name)
        if path == CORE:
            expected = expected or core_manifest.get('test_sha256')
        if not expected or sha(path.read_bytes()) != expected:
            raise ValueError('Core input fingerprint absent or changed: ' + path.name)
    groups = validate_core(read(CORE))
    original, masked = read(CORE), read(CORE_MASKED)
    if len(original) != len(masked) or [r['id'] for r in original] != [r['id'] for r in masked]:
        raise ValueError('Masked core must retain exactly the full core IDs/order')
    for a, b in zip(original, masked):
        if {k: v for k, v in a.items() if k != 'formal_proof'} != {k: v for k, v in b.items() if k != 'formal_proof'}:
            raise ValueError('Masked ablation changed more than formal proof evidence')
    model = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if model.get('repo_id') != 'Qwen/Qwen3-14B' or not model.get('download_complete'):
        raise ValueError('Pinned 14B model is not verified ready')
    if model['local_directory'] != 'data/models/Qwen3-14B':
        raise ValueError('Model manifest points at the wrong checkpoint')
    return {'data_manifest_sha256': sha(data_path.read_bytes()), 'integrity_sha256': sha(integrity_path.read_bytes()),
        'core_manifest_sha256': sha(core_path.read_bytes()), 'core_test_sha256': sha(CORE.read_bytes()),
        'core_masked_sha256': sha(CORE_MASKED.read_bytes()), 'core_theorem_groups': groups,
        'proofnet_local_lean_replay': data_manifest.get('lean_replay', 'not_run'), 'model_revision': model['revision']}


def export(state):
    DEST.mkdir(parents=True, exist_ok=True)
    result = {'observed_utc': utc(), 'job': state, 'quantization': None, 'dtype': 'BF16',
        'scope': 'proof-body pilot and constructed same-theorem argument diagnostic',
        'positive_labels': 'User-assumed corrected ProofNet argument matches',
        'training_negatives': 'Constructed cross-problem English proof swaps',
        'evaluation_roles': {'validation': 'cross-problem proof-consistency pilot; English-only shortcut exists',
            'core': 'constructed same-theorem 2x2 diagnostic; locally compiled, not human reviewed',
            'core-masked': 'formal-proof-withheld ablation; does not establish semantic accuracy',
            'herald': 'unlabeled deployment survey; no accuracy claim'}, 'runs': {}}
    for name in PREDICTION_STAGES:
        path = OUT / name / 'run.json'
        if path.exists():
            result['runs'][name] = json.loads(path.read_text(encoding='utf-8'))
    for name in ['probe-8192', 'probe-4096', 'probe-2048', 'fine-tuned']:
        path = OUT / name / ('training.json' if name == 'fine-tuned' else 'probe.json')
        if path.exists():
            result[name] = json.loads(path.read_text(encoding='utf-8'))
    metadata(DEST / 'latest.json', result)
    lines = ['# Overnight BF16 Qwen3-14B argument experiment', '', f"Observed UTC: {result['observed_utc']}",
        f"Job: {state['status']}; stage: {state.get('stage')}", '',
        'Both English and Lean proof bodies are inputs. No quantization or second-pass training.',
        'ProofNet positives are user-assumed; training swaps are a coarse proof-consistency pilot.',
        'The separate core crosses two valid routes for each theorem, with a formal-proof-masked control.',
        'Core material is constructed and is not independently human reviewed.', '',
        '| Model / corpus | Status | Rows | Accuracy |', '| --- | --- | ---: | ---: |']
    for name, run in result['runs'].items():
        accuracy = run.get('accuracy')
        lines.append(f"| {name} | {run['status']} | {run.get('rows', '')} | " +
            (f'{accuracy:.2%}' if accuracy is not None else 'unlabeled') + ' |')
    lines += ['', 'No Herald accuracy claim is possible without independent labels.',
        'Cross-problem pilot accuracy alone does not demonstrate proof-route matching.',
        'Compilation is distinct from independent semantic argument validation.']
    (DEST / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    a, b = [OUT / n / 'predictions.jsonl' for n in ['untuned-herald', 'tuned-herald']]
    if a.exists() and b.exists() and all(result['runs'].get(n, {}).get('status') == 'complete'
                                       for n in ['untuned-herald', 'tuned-herald']):
        left, right = [{r['id']: r for r in read(p)} for p in [a, b]]
        counts = Counter()
        with (OUT / 'herald-comparison.csv').open('w', encoding='utf-8', newline='') as output:
            writer = csv.writer(output); writer.writerow(['id', 'untuned', 'fine_tuned', 'comparison'])
            for identity in sorted(set(left) | set(right)):
                x, y = left.get(identity, {}).get('prediction'), right.get(identity, {}).get('prediction')
                kind = 'missing' if x is None or y is None else 'agreement' if x == y else 'disagreement'
                counts[kind] += 1; writer.writerow([identity, x, y, kind])
        metadata(DEST / 'herald-summary.json', dict(counts))
    metrics = []
    for name, run in result['runs'].items():
        if 'metrics' in run:
            for cls, score in run['metrics']['classes'].items():
                metrics.append({'run': name, 'class': cls, 'precision': score['precision'], 'recall': score['recall'],
                    'f1': score['f1-score'], 'support': score['support'], 'accuracy': run['accuracy'],
                    'macro_f1': run['metrics']['macro']['f1-score'], 'coverage': run['metrics']['coverage']})
    if metrics:
        with (DEST / 'classification-metrics.csv').open('w', encoding='utf-8', newline='') as output:
            writer = csv.DictWriter(output, fieldnames=list(metrics[0])); writer.writeheader(); writer.writerows(metrics)


def stage_fingerprint(args):
    options = dict(zip(args[1::2], args[2::2]))
    model = json.loads(MANIFEST.read_text(encoding='utf-8'))
    adapter = Path(options['--adapter']) if '--adapter' in options else None
    return {'action': args[0], 'input_sha256': sha(Path(options['--input']).read_bytes()),
        'prompt_sha256': sha((ROOT / 'prompts/argument-v1.txt').read_bytes()), 'base_revision': model['revision'],
        'model_manifest_sha256': sha(MANIFEST.read_bytes()), 'max_tokens': int(options['--max-tokens']),
        'adapter_sha256': sha((adapter / 'adapter_model.safetensors').read_bytes()) if adapter else None,
        'quantization': None, 'base_dtype': 'bfloat16', 'implementation_sha256': {
            name: sha((ROOT / 'scripts' / name).read_bytes()) for name in ['argument_model.py', 'argument_data.py']}}


def command(name, args, marker):
    expected = stage_fingerprint(args); provenance = marker.parent / 'stage-provenance.json'
    if provenance.exists():
        if json.loads(provenance.read_text(encoding='utf-8')) != expected:
            raise ValueError('Stage provenance changed; use fresh output: ' + name)
    elif marker.exists():
        raise ValueError('Existing stage lacks comparable provenance; refusing reuse: ' + name)
    if marker.exists():
        previous = json.loads(marker.read_text(encoding='utf-8')); recorded = previous.get('spec', previous)
        for key in ['input_sha256', 'prompt_sha256', 'base_revision', 'max_tokens']:
            if recorded.get(key) != expected[key]:
                raise ValueError('Marker disagrees with requested fingerprints: ' + name)
        if previous.get('status') == 'complete':
            if args[0] == 'train' and not (marker.parent / 'adapter/adapter_model.safetensors').exists():
                raise ValueError('Completed training lacks adapter')
            return
        if args[0] in ['train', 'probe']:
            raise RuntimeError('Interrupted training/probe needs a fresh stage directory: ' + name)
    # Training creates its own directory with exist_ok=False; do not pre-create it.
    metadata(OUT / (name + '.stage-provenance.json'), expected)
    with (OUT / (name + '.log')).open('a', encoding='utf-8') as log:
        worker = subprocess.Popen([sys.executable, str(ROOT / 'scripts/argument_model.py'), *args],
            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        metadata(WORKER, {'pid': worker.pid, 'driver_pid': os.getpid(), 'stage': name, 'started_utc': utc()})
        try:
            returncode = worker.wait()
        finally:
            if worker.poll() is not None and WORKER.exists() and json.loads(WORKER.read_text(encoding='utf-8'))['pid'] == worker.pid:
                WORKER.unlink()
    if marker.parent.exists():
        metadata(provenance, expected)
    if returncode:
        raise RuntimeError(f'{name} failed; inspect {name}.log')
    if not marker.exists() or json.loads(marker.read_text(encoding='utf-8')).get('status') != 'complete':
        raise RuntimeError('Child returned without a completed marker: ' + name)


def prepare_budget(budget):
    expected = {'source_manifest_sha256': sha((DATA / 'manifest.json').read_bytes()), 'max_tokens': budget,
        'preparer_sha256': sha((ROOT / 'scripts/prepare_argument_budget.py').read_bytes())}
    marker, provenance = BUDGET_DATA / 'manifest.json', OUT / 'budget-stage-provenance.json'
    if provenance.exists() and json.loads(provenance.read_text(encoding='utf-8')) != expected:
        raise ValueError('Budget-data provenance changed; use a fresh output directory')
    if marker.exists():
        if not provenance.exists():
            raise ValueError('Existing budget data lack comparable provenance')
    else:
        metadata(provenance, expected)
        with (OUT / 'prepare-budget.log').open('a', encoding='utf-8') as log:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/prepare_argument_budget.py'),
                '--source', str(DATA), '--output', str(BUDGET_DATA), '--max-tokens', str(budget)],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError('Budget-specific data preparation failed; see prepare-budget.log')
    info = json.loads(marker.read_text(encoding='utf-8'))
    if info.get('ready_for_training') is not True:
        raise ValueError('Budget-filtered dataset is not ready')
    validate_hashes(BUDGET_DATA, info)
    for name in ['train.jsonl', 'validation.jsonl']:
        if name not in info.get('files', {}):
            raise ValueError('Budget dataset missing required fingerprint')
    return {'manifest_sha256': sha(marker.read_bytes()), 'max_tokens': budget}


def main():
    acquire_lock(); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'job.pid').write_text(str(os.getpid()) + '\n', encoding='utf-8')
    state = {'status': 'running', 'stage': 'readiness_checks', 'started_utc': utc(), 'second_pass': False,
        'model': 'Qwen/Qwen3-14B', 'quantization': None, 'output_directory': OUT.relative_to(ROOT).as_posix(),
        'data_directory': DATA.relative_to(ROOT).as_posix()}
    awake = ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    def save():
        state['updated_utc'] = utc(); metadata(OUT / 'job.json', state); export(state)
    try:
        if not awake:
            raise RuntimeError('Cannot hold temporary Windows execution request')
        state['readiness'] = readiness()
        archived = BASE_OUT / 'job.json'
        if archived.exists():
            old = json.loads(archived.read_text(encoding='utf-8-sig'))
            if old.get('status') == 'held_for_audit':
                old.update(superseded_by=state['output_directory'],
                    hold_resolution='Corrected dataset readiness passed; historical run remains held.')
                metadata(archived, old)
        save()
        # The standalone 8192 probe exceeded the local resource/time budget on
        # Windows without compiled FlashAttention. Keep the failed artifact and
        # test smaller full-proof budgets, with no quantization/truncation.
        state['probe_budget_policy'] = '4096 then 2048; 8192 resource trial archived'
        for budget in [4096, 2048]:
            name = f'probe-{budget}'; state['stage'] = name; save()
            try:
                command(name, ['probe', '--input', str(DATA / 'train.jsonl'), '--output', str(OUT / name),
                    '--max-tokens', str(budget), '--model-manifest', str(MANIFEST)], OUT / name / 'probe.json')
                break
            except RuntimeError:
                path = OUT / name / 'probe.json'
                failure = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
                if 'out of memory' not in failure.get('error', '').lower():
                    raise
        else:
            raise RuntimeError('No unquantized budget fits; no quantized fallback allowed')
        state['max_tokens'] = budget; state['stage'] = 'prepare-budget-data'; save()
        state['budget_data'] = prepare_budget(budget); save()
        state['stage'] = 'english-only-control'; save()
        with (OUT / 'english-only-control.log').open('a', encoding='utf-8') as log:
            control = subprocess.run([sys.executable, str(ROOT / 'scripts/audit_argument_shortcuts.py'),
                '--data-dir', str(BUDGET_DATA), '--output', str(DEST / 'english-only-control.json')],
                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        if control.returncode:
            raise RuntimeError('English-only control failed; inspect english-only-control.log')
        steps = [('untuned-validation', 'predict', BUDGET_DATA / 'validation.jsonl', None),
            ('untuned-core', 'predict', CORE, None), ('untuned-core-masked', 'predict', CORE_MASKED, None),
            ('fine-tuned', 'train', BUDGET_DATA / 'train.jsonl', None),
            ('tuned-validation', 'predict', BUDGET_DATA / 'validation.jsonl', OUT / 'fine-tuned/adapter'),
            ('tuned-core', 'predict', CORE, OUT / 'fine-tuned/adapter'),
            ('tuned-core-masked', 'predict', CORE_MASKED, OUT / 'fine-tuned/adapter'),
            ('untuned-herald', 'predict', DATA / 'herald.jsonl', None),
            ('tuned-herald', 'predict', DATA / 'herald.jsonl', OUT / 'fine-tuned/adapter')]
        for name, action, input_path, adapter in steps:
            state['stage'] = name; save()
            args = [action, '--input', str(input_path), '--output', str(OUT / name),
                    '--max-tokens', str(budget), '--model-manifest', str(MANIFEST)]
            if adapter:
                args += ['--adapter', str(adapter)]
            command(name, args, OUT / name / ('training.json' if action == 'train' else 'run.json'))
            state.setdefault('completed_stages', []).append(name); save()
        state['status'] = 'complete'
    except BaseException as error:
        state.update(status='failed', error=repr(error)); raise
    finally:
        try:
            save()
        finally:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            if LOCK.exists() and json.loads(LOCK.read_text(encoding='utf-8'))['pid'] == os.getpid():
                LOCK.unlink()


if __name__ == '__main__':
    main()
