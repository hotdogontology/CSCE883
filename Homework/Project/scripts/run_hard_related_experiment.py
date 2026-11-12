"""Run the frozen related-proof experiment sequentially with resumable stage checks."""
import argparse
from collections import Counter
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from run_argument_experiment import acquire_lock, process_alive, LOCK, WORKER

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/hard-related-20261110'
REPORT = ROOT / 'reports/hard-related-20261110'


def utc():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temp.replace(path)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(2**20), b''):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(stage):
    files = {str(path): digest(ROOT / path) for path in stage['fingerprint_files']}
    for directory in stage.get('fingerprint_directories', []):
        for path in sorted((ROOT / directory).glob('*.json')):
            files[path.relative_to(ROOT).as_posix()] = digest(path)
    return {'command': stage['command'], 'files': files}


def validate_queue(config):
    names = [s['name'] for s in config['stages']]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate stage names')
    seen = set()
    for stage in config['stages']:
        if not set(stage.get('depends_on', [])) <= seen:
            raise ValueError('Stage dependencies must precede their consumer')
        seen.add(stage['name'])
        if not stage['command'][0].startswith('scripts/'):
            raise ValueError('Only local project scripts may be queued')
        for name in ['marker', 'output']:
            if not (ROOT / stage[name]).resolve().is_relative_to(OUT.resolve()):
                raise ValueError('Stage output must stay in this experiment directory')
        if not (ROOT / stage['command'][0]).is_file():
            raise ValueError('Missing stage implementation: ' + stage['command'][0])
    for path, expected in config['inputs'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('Frozen input changed: ' + path)


def metrics(rows, predictions):
    from classification_metrics import evaluate
    from sklearn.metrics import confusion_matrix, roc_auc_score, average_precision_score
    truth = {r['id']: r['label'] for r in rows}
    selected = [p for p in predictions if p['id'] in truth]
    if (len(truth) != len(rows) or len(selected) != len(rows) or
            len({p['id'] for p in selected}) != len(selected)):
        raise ValueError('Incomplete or duplicate evaluation predictions')
    scored = [p for p in selected if type(p.get('prediction')) is bool]
    class_coverage = {name: {'expected': sum(r['label'] == value for r in rows),
                            'scored': sum(truth[p['id']] == value for p in scored)}
                      for value, name in [(False, 'mismatch'), (True, 'match')]}
    if not scored:
        return {'coverage': 0, 'scored': 0, 'total': len(rows), 'accuracy': None,
                'class_coverage': class_coverage,
                'status_counts': dict(Counter(p.get('status') for p in selected))}
    result = evaluate(rows, selected)
    y = [truth[p['id']] for p in scored]
    result['confusion_matrix_order'] = ['mismatch', 'match']
    result['confusion_matrix'] = confusion_matrix(y, [p['prediction'] for p in scored], labels=[False, True]).tolist()
    result['false_acceptances'] = sum(not truth[p['id']] and p['prediction'] for p in scored)
    result['status_counts'] = dict(Counter(p.get('status') for p in selected))
    result['class_coverage'] = class_coverage
    if len(set(y)) == 2:
        scores = [p.get('yes_minus_no_logit', p.get('yes_no_logit_margin', p.get('yes_score_uncalibrated'))) for p in scored]
        if all(s is not None for s in scores):
            result['auroc_match'] = float(roc_auc_score(y, scores))
            result['average_precision_mismatch'] = float(average_precision_score([not v for v in y], [-s for s in scores]))
    return result


def export(config, state):
    report = {'observed_utc': utc(), 'job': state, 'label_policy': config['label_policy'],
              'quantization': None, 'base_dtype': 'bfloat16', 'results': {}}
    compile_ledger = OUT / 'compilation/compilation.jsonl'
    compile_marker = OUT / 'compilation/summary.json'
    compiled = None
    if compile_ledger.exists() and compile_marker.exists():
        compiled = {r['cache_key']: r for r in read(compile_ledger)}
    for stage in config['stages']:
        marker = ROOT / stage['marker']
        if not marker.exists():
            continue
        value = json.loads(marker.read_text(encoding='utf-8'))
        entry = {'worker_status': value.get('status')}
        predictions = ROOT / stage['output'] / 'predictions.jsonl'
        if value.get('status') == 'complete' and predictions.exists():
            observed = read(predictions)
            entry['evaluations'] = {name: metrics(read(ROOT / path), observed)
                                    for name, path in stage.get('evaluation_sets', {}).items()}
            if compiled is not None and stage['name'] in ['nl_to_lean', 'verbose_lean', 'natural_lean']:
                qualified = []
                for prediction in observed:
                    result = dict(prediction)
                    generations = result.get('generations', {})
                    if not generations or not all(compiled.get(g['cache_key'], {}).get('status') == 'compiled'
                                                  for g in generations.values()):
                        result.update(prediction=None, status='generated_code_not_compiler_verified')
                    qualified.append(result)
                entry['compiler_qualified_evaluations'] = {
                    name: metrics(read(ROOT / path), qualified) for name, path in stage.get('evaluation_sets', {}).items()}
                entry['compiler_qualified_scope'] = 'Generated code compiled; source-argument preservation still unverified'
        elif stage['name'] == 'fine-tuned':
            entry['training'] = value
        elif stage['name'] == 'compilation':
            entry['compilation'] = value
        report['results'][stage['name']] = entry
    save(REPORT / 'latest.json', report)
    lines = ['# Related-proof and intermediary experiment', '',
             'Job: ' + state['status'] + '; current stage: ' + state.get('stage', 'none') + '.', '',
             'Both English and Lean arguments are compared. Source positives are user-assumed;',
             'related swaps are synthetic negatives. Scores do not certify subtle semantic fidelity.',
             'The old 16-case core is a previously inspected diagnostic, not a new blind test.',
             'Generation failures are abstentions; accuracy is conditional on scored examples.',
             'Generated code is compiler-unchecked unless a separate compilation report exists.', '',
             '| Model / architecture | Evaluation | Coverage | Accuracy | Mismatch F1 | False acceptance |',
             '| --- | --- | ---: | ---: | ---: | ---: |']
    for name, value in report['results'].items():
        comparisons = list(value.get('evaluations', {}).items())
        comparisons += [(split + ' (generated code compiled)', score)
                        for split, score in value.get('compiler_qualified_evaluations', {}).items()]
        for split, score in comparisons:
            accuracy = score.get('accuracy')
            f1 = score.get('classes', {}).get('mismatch', {}).get('f1-score')
            lines.append(f"| {name} | {split} | {score['scored']}/{score['total']} | " +
                         (f'{accuracy:.2%}' if accuracy is not None else 'unscored') + ' | ' +
                         (f'{f1:.4f}' if f1 is not None else 'n/a') + ' | ' + str(score.get('false_acceptances', 'n/a')) + ' |')
    lines += ['', 'See latest.json for both classes, confusion matrices, ranking metrics and status.',
              'Raw prompts, generations, predictions, adapters and logs remain ignored local artifacts.']
    compilation = report['results'].get('compilation', {}).get('compilation')
    if compilation:
        lines += ['', 'Generated-code compiler outcomes (not source-faithfulness labels):', '']
        lines += ['- ' + target + ': ' + json.dumps(counts) for target, counts in compilation.get('by_target', {}).items()]
    (REPORT / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', type=Path, default=OUT / 'queue.json')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.queue.read_text(encoding='utf-8'))
    validate_queue(config)
    if args.validate_only:
        print(json.dumps({'status': 'validated', 'stages': len(config['stages'])}))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    state = {'status': 'running', 'pid': os.getpid(), 'started_utc': utc(),
             'queue_sha256': digest(args.queue), 'stages': {}}
    acquire_lock()
    awake = ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    (OUT / 'job.pid').write_text(str(os.getpid()), encoding='utf-8')
    child = None
    try:
        for stage in config['stages']:
            name = stage['name']
            state['stage'] = name
            blocked = [dep for dep in stage.get('depends_on', []) if state['stages'].get(dep, {}).get('status') != 'complete']
            if blocked:
                state['stages'][name] = {'status': 'blocked_dependency', 'dependencies': blocked}
                save(OUT / 'job.json', state)
                continue
            try:
                validate_queue(config)
                expected = fingerprint(stage)
                provenance = OUT / (name + '.provenance.json')
                marker = ROOT / stage['marker']
                if provenance.exists() and json.loads(provenance.read_text(encoding='utf-8')) != expected:
                    raise ValueError('Stage inputs or implementation changed: use a new output directory')
                if marker.exists() and not provenance.exists():
                    raise ValueError('Existing output has no verified provenance')
                if marker.exists() and json.loads(marker.read_text(encoding='utf-8')).get('status') == 'complete':
                    state['stages'][name] = {'status': 'complete', 'reused': True}
                else:
                    gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], text=True)
                    if int(gpu.strip().splitlines()[0]) > 5000:
                        raise RuntimeError('GPU memory occupied; refusing overlapping model workers')
                    save(provenance, expected)
                    state['stages'][name] = {'status': 'running', 'started_utc': utc()}
                    save(OUT / 'job.json', state)
                    export(config, state)
                    with (OUT / (name + '.log')).open('a', encoding='utf-8') as log:
                        child = subprocess.Popen([sys.executable, *stage['command']], cwd=ROOT,
                                                 stdout=log, stderr=subprocess.STDOUT)
                        save(WORKER, {'pid': child.pid, 'parent_pid': os.getpid(), 'stage': name, 'output': str(OUT)})
                        state['stages'][name]['worker_pid'] = child.pid
                        save(OUT / 'job.json', state)
                        deadline = time.monotonic() + stage.get('timeout_seconds', 12 * 3600)
                        while child.poll() is None:
                            state['heartbeat_utc'] = utc()
                            save(OUT / 'job.json', state)
                            if time.monotonic() > deadline:
                                child.terminate()
                                child.wait(timeout=60)
                                raise TimeoutError('Stage exceeded recorded time budget')
                            time.sleep(15)
                        code = child.returncode
                    WORKER.unlink(missing_ok=True)
                    child = None
                    if code != 0:
                        raise RuntimeError(f'Worker exit {code}; see {name}.log')
                    if not marker.exists() or json.loads(marker.read_text(encoding='utf-8')).get('status') != 'complete':
                        raise RuntimeError('Worker did not publish completed result')
                    state['stages'][name].update(status='complete', finished_utc=utc())
            except Exception as exc:
                state['stages'][name] = {'status': 'failed', 'error': repr(exc), 'finished_utc': utc()}
            finally:
                if child is not None:
                    if child.poll() is None:
                        child.terminate()
                        try:
                            child.wait(timeout=30)
                        except subprocess.TimeoutExpired:
                            child.kill()
                            child.wait(timeout=30)
                    child = None
                    WORKER.unlink(missing_ok=True)
            save(OUT / 'job.json', state)
            export(config, state)
        state['status'] = 'complete' if all(s['status'] == 'complete' for s in state['stages'].values()) else 'complete_with_failures'
        state['finished_utc'] = utc()
        state['stage'] = 'finished'
    except BaseException as exc:
        state.update(status='failed', error=repr(exc), finished_utc=utc())
        raise
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=60)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        WORKER.unlink(missing_ok=True)
        LOCK.unlink(missing_ok=True)
        if awake:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        save(OUT / 'job.json', state)
        export(config, state)


if __name__ == '__main__':
    main()
