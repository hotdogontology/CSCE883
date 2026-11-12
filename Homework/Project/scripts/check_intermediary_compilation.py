"""Replay generated proof intermediaries, separately from semantic judgments.

This is a conservative command screen plus pinned Lean elaboration, not an OS
sandbox or a proof of source correspondence. It never changes generation caches.
"""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

from argument_data import strip_comments

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/intermediary-sources'
SCHEMA = 1
IMPORT_ROOTS = {'Init', 'Std', 'Mathlib', 'Batteries', 'Aesop', 'Natural', 'Verbose'}


def screen(code):
    clean = strip_comments(code)
    if re.search(r'\b(sorry|admit|axiom|constant|opaque)\b', clean, re.I):
        return 'rejected_admission_or_opaque_declaration'
    # Generated translations need proof syntax, not executable extensions.
    # Block metaprogramming, foreign functions, and command evaluation even if
    # located inside a namespace or inside a proof's tactic block.
    if re.search(r'#\s*(eval!?|compile|check_failure)|\b(run_tac|run_elab|elab|macro|syntax|initialize|builtin_initialize|unsafe|extern|implemented_by|native_decide)\b', clean):
        return 'rejected_executable_extension'
    if re.search(r'\b(IO|System|Lean\.Elab|Lean\.Meta)\s*[.\[]', clean):
        return 'rejected_runtime_access'
    for match in re.finditer(r'^\s*(?:public\s+|private\s+)?import\s+([^\r\n]+)', clean, re.M):
        for module in match.group(1).split():
            if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*', module) or module.split('.')[0] not in IMPORT_ROOTS:
                return 'rejected_import'
    if not re.search(r'\b(theorem|lemma|example|Theorem|Lemma|Example|Exercise)\b', clean):
        return 'no_proof_declaration'
    return None


def environment(target):
    if target == 'english':
        return {'status': 'not_applicable'}
    if target == 'lean':
        root = ROOT / 'data/lean428'
        state_path = root / 'setup.json'
        if not state_path.exists() or json.loads(state_path.read_text())['status'] != 'complete':
            return {'status': 'not_checked', 'reason': 'Lean4.28 environment unavailable'}
        lean = root / 'lean-4.28.0-windows/bin/lean.exe'
        lake = lean.with_name('lake.exe')
        workdir = root / 'mathlib'
        env = dict(os.environ)
        env['PATH'] = str(lean.parent) + os.pathsep + env['PATH']
        lean_path = subprocess.check_output([str(lake), 'env', sys.executable, '-c',
            'import os;print(os.environ.get("LEAN_PATH",""))'], cwd=workdir, env=env,
            text=True, timeout=60).strip()
        return {'status': 'ready', 'lean_executable': str(lean), 'source': str(workdir),
                'lean_path': lean_path, 'version': '4.28.0',
                'environment_sha256': hashlib.sha256(state_path.read_bytes()).hexdigest()}
    name = {'verbose_lean': 'verbose-lean4', 'natural_lean': 'natural_lean'}.get(target)
    if not name:
        return {'status': 'not_checked', 'reason': 'unknown target dialect'}
    path = BASE / (name + '-setup.json')
    state = json.loads(path.read_text()) if path.exists() else {}
    if state.get('status') != 'complete':
        return {'status': 'not_checked', 'reason': 'matching dialect build is not complete',
                'setup_state': state.get('status', 'absent')}
    return {'status': 'ready', **{k: state[k] for k in ['lean_executable', 'source', 'lean_path', 'version', 'revision']},
            'environment_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def replay(record, config, output, timeout):
    result = {'cache_key': record['cache_key'], 'target': record.get('target'),
              'generation_status': record.get('status'), 'schema': SCHEMA,
              'semantic_correspondence': 'not_established_by_compilation'}
    if record.get('target') == 'english':
        return dict(result, status='not_applicable')
    if record.get('status') != 'generated':
        return dict(result, status='not_checked', reason='generation did not complete successfully')
    code = record.get('text', '')
    result['source_sha256'] = hashlib.sha256(code.encode()).hexdigest()
    rejected = screen(code)
    if rejected:
        return dict(result, status=rejected)
    if config['status'] != 'ready':
        return dict(result, status='not_checked', reason=config.get('reason'))
    result['environment'] = {k: config[k] for k in ['version', 'environment_sha256']}
    source = output / 'sources' / (record['cache_key'] + '.lean')
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(code, encoding='utf-8')
    env = dict(os.environ)
    # Do not propagate project/service credentials to generated-code processes.
    for key in list(env):
        if any(fragment in key.upper() for fragment in ['TOKEN', 'SECRET', 'API_KEY', 'PASSWORD']):
            del env[key]
    env['LEAN_PATH'] = config['lean_path']
    env['PATH'] = str(Path(config['lean_executable']).parent) + os.pathsep + env['PATH']
    start = time.monotonic()
    try:
        process = subprocess.run([config['lean_executable'], '-T', '300000', '-M', '4096',
                                  str(source.resolve())], cwd=config['source'], env=env,
                                 capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        log = process.stdout + process.stderr
        result['returncode'] = process.returncode
        if re.search(r'\bsorryAx\b|declaration uses .sorry.|\buses sorry\b', log):
            result['status'] = 'admitted_after_elaboration'
        else:
            result['status'] = 'compiled' if process.returncode == 0 else 'compile_failed'
    except subprocess.TimeoutExpired as error:
        result['status'] = 'timeout'
        log = str(error)
    except OSError as error:
        result['status'] = 'execution_failed'
        log = str(error)
    result['seconds'] = round(time.monotonic() - start, 3)
    (output / 'logs').mkdir(exist_ok=True)
    (output / 'logs' / (record['cache_key'] + '.log')).write_text(log, encoding='utf-8')
    result['log_excerpt'] = log[-1500:]
    # No full axiom closure audit is claimed; source admissions and compiler
    # sorry warnings are screened, and only pinned library imports are allowed.
    result['axiom_policy'] = 'source_admissions_and_sorry_warnings_screened; transitive_axioms_not_audited'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=60)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    records = [json.loads(path.read_text(encoding='utf-8')) for path in sorted(args.cache_dir.glob('*.json'))]
    configs = {target: environment(target) for target in {r.get('target') for r in records}}
    ledger = args.output / 'compilation.jsonl'
    rows = []
    with ledger.open('w', encoding='utf-8') as handle:
        for record in records:
            row = replay(record, configs[record.get('target')], args.output, args.timeout)
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')
            handle.flush()
            rows.append(row)
    summary = {'status': 'complete', 'schema': SCHEMA, 'records': len(rows),
               'status_counts': dict(Counter(r['status'] for r in rows)),
               'by_target': {target: dict(Counter(r['status'] for r in rows if r['target'] == target)) for target in configs},
               'environment_status': configs,
               'compilation_does_not_establish_source_argument_preservation': True}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'records': len(rows), 'status_counts': summary['status_counts']}), flush=True)


if __name__ == '__main__':
    main()
