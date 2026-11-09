"""Construct and compile held-out same-theorem two-route argument diagnostics.

This small suite is agent-authored, with declared route labels. Compilation
certifies formal validity; it does not independently certify the route labels.
No item in this suite is used for LoRA training or threshold selection.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'lean/ArgumentCore.lean'
DEST = ROOT / 'artifacts/argument-14b/core'
CONTEXT = 'import Mathlib\nopen scoped BigOperators'

CASES = [
    {
        'id': 'odd_sum',
        'family': 'finite_odd_sum',
        'statement': 'For every natural number n, the sum of the first n odd numbers, '
            'sum_{k=0}^{n-1} (2k+1), equals n squared. The sum is interpreted in the integers.',
        'english': {
            'A': 'Use induction on n. For n=0 the empty sum and 0 squared are both zero. '
                'Assume the sum of the first n odd numbers is n squared. Appending the next '
                'term 2n+1 gives n squared + 2n + 1 = (n+1) squared, completing the induction.',
            'B': 'For each k, rewrite 2k+1 as (k+1) squared minus k squared. The resulting '
                'sum telescopes: all intermediate squares cancel, leaving n squared minus '
                '0 squared, which is n squared.',
        },
        'routes': {'A': 'induction on the number of summands', 'B': 'telescoping consecutive square differences'},
    },
    {
        'id': 'consecutive_even',
        'family': 'consecutive_product_parity',
        'statement': 'For every natural number n, there is a natural number k such that '
            'n(n+1) = 2k; thus the product of two consecutive natural numbers is even.',
        'english': {
            'A': 'Induct on n, carrying an explicit witness k. At n=0 take k=0. '
                'If n(n+1)=2k, then (n+1)(n+2)=n(n+1)+2(n+1)=2(k+n+1). '
                'Hence k+n+1 is the witness for the successor.',
            'B': 'Split into the parity cases for n. If n=2m, use k=m(n+1), since '
                'n(n+1)=2m(n+1). If n=2m+1, then n+1=2(m+1), so use '
                'k=n(m+1). These witnesses cover every natural number n.',
        },
        'routes': {'A': 'inductively update an evenness witness', 'B': 'split n into even and odd forms'},
    },
    {
        'id': 'cubic_root',
        'family': 'real_polynomial_root_existence',
        'statement': 'There exists a real number x such that x cubed plus x equals 2.',
        'english': {
            'A': 'Take x=1. Direct substitution gives 1 cubed plus 1 = 2, '
                'so this explicit number witnesses the required existence.',
            'B': 'Consider the continuous real function f(x)=x cubed plus x on the '
                'closed interval [0,2]. Its endpoint values are f(0)=0 and f(2)=10, '
                'and 2 lies between them. By the intermediate value theorem, some '
                'x in [0,2] satisfies f(x)=2; that x witnesses the assertion.',
        },
        'routes': {'A': 'construct the numerical witness 1', 'B': 'obtain a witness by continuity and the intermediate value theorem'},
    },
    {
        'id': 'power_divisibility',
        'family': 'exponential_divisibility',
        'statement': 'For every natural number n, the integer 4 to the power n minus 1 '
            'is divisible by 3.',
        'english': {
            'A': 'Induct on n. The base case is 4 to the power 0 minus 1 = 0. '
                'For the induction step, if 4 to the power n minus 1 = 3k, then '
                '4 to the power (n+1) minus 1 = 4(4 to the power n minus 1)+3 '
                '= 3(4k+1). Thus divisibility is preserved at the successor.',
            'B': 'Use the finite geometric-series identity: 4 to the power n minus 1 '
                '= (4-1) times the sum of 4 to the power k for 0 <= k < n. '
                'This equals 3 times an integer sum, which supplies an explicit '
                'quotient and proves divisibility by 3.',
        },
        'routes': {'A': 'inductively update a divisibility witness', 'B': 'factor through a finite geometric sum'},
    },
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_route(source, identity, route):
    pattern = rf'-- BEGIN {identity} {route}\n(.*?)-- END {identity} {route}'
    match = re.search(pattern, source, re.S)
    if match is None:
        raise ValueError(f'Missing source block {identity}/{route}')
    block = match[1].strip()
    if '--' in block or '/-' in block:
        raise ValueError('Proof input unexpectedly contains a comment')
    # This authored suite has no assignments in theorem types. Enforce the exact
    # proof-introduction marker rather than use the corpus extractor being audited.
    statement, separator, body = block.partition(':= by')
    if not separator or not body.strip():
        raise ValueError('Malformed authored theorem block')
    normalized = re.sub(r'^theorem\s+[^\s(]+', 'theorem candidate', statement.strip(), count=1)
    declaration = re.match(r'^theorem\s+([^\s(]+)', statement)[1]
    if re.search(r'\b(?:sorry|admit|axiom)\b', block):
        raise ValueError('Admission in authored source')
    return {'formal_statement': normalized, 'formal_proof': 'by' + body,
            'source_declaration': 'ArgumentCore.' + declaration}


def compile_source():
    env = dict(os.environ)
    env['ELAN_HOME'] = 'C:/Users/tbelcher/.elan'
    lake = 'C:/Users/tbelcher/.elan/bin/lake.exe'
    version = subprocess.run([lake, 'env', 'lean', '--version'], cwd=ROOT/'lean',
        env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
    result = subprocess.run([lake, 'env', 'lean', 'ArgumentCore.lean'], cwd=ROOT/'lean',
        env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (DEST/'build.log').write_text(result.stdout + result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Core Lean source did not compile; inspect core/build.log')
    if 'sorryAx' in result.stdout or 'sorryAx' in result.stderr:
        raise RuntimeError('Axiom audit found an admitted dependency')
    axioms = {}
    for declaration, value in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", result.stdout):
        axioms[declaration] = [x.strip() for x in value.split(',') if x.strip()]
    expected = {f'ArgumentCore.{name}' for name in [
        'odd_sum_induction', 'odd_sum_telescoping', 'consecutive_even_induction',
        'consecutive_even_parity', 'cubic_root_explicit', 'cubic_root_ivt',
        'power_divisibility_induction', 'power_divisibility_geometric']}
    if set(axioms) != expected:
        raise RuntimeError('Did not capture all eight axiom reports')
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    if any(set(items)-allowed for items in axioms.values()):
        raise RuntimeError('Unexpected transitive axiom')
    return version.stdout.strip(), axioms


def replay_payloads(rows):
    """Compile the exact normalized inputs, not only the authored source file."""
    unique = {}
    for row in rows:
        unique[(row['formal_statement'], row['formal_proof'])] = row
    blocks = [CONTEXT]
    for i, row in enumerate(unique.values()):
        header = row['formal_statement'].replace('theorem candidate', f'theorem replay_{i}', 1)
        blocks.append(header + ' := ' + row['formal_proof'])
    path = DEST/'Replay.lean'
    path.write_text('\n\n'.join(blocks)+'\n', encoding='utf-8')
    env = dict(os.environ)
    env['ELAN_HOME'] = 'C:/Users/tbelcher/.elan'
    result = subprocess.run(['C:/Users/tbelcher/.elan/bin/lake.exe', 'env', 'lean', str(path)],
        cwd=ROOT/'lean', env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (DEST/'payload-replay.log').write_text(result.stdout+result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Normalized model payloads did not compile; inspect payload-replay.log')
    return digest(path.read_bytes())


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode('utf-8')
    version, axioms = compile_source()
    rows = []
    for case in CASES:
        formal = {route: parse_route(source, case['id'], route) for route in ['A', 'B']}
        assert formal['A']['formal_statement'] == formal['B']['formal_statement']
        for english_route in ['A', 'B']:
            for lean_route in ['A', 'B']:
                rows.append({
                    'id': f'core-{case["id"]}-E{english_route}-L{lean_route}',
                    'group': 'core-' + case['id'], 'source_family': case['family'],
                    'informal_statement': case['statement'],
                    'informal_proof': case['english'][english_route],
                    'formal_statement': formal[lean_route]['formal_statement'],
                    'formal_proof': formal[lean_route]['formal_proof'], 'context': CONTEXT,
                    'label': english_route == lean_route, 'label_scope': 'argument_fidelity',
                    'label_source': 'agent_constructed_same_theorem_two_route_matrix',
                    'label_assumption': 'At the declared route granularity, different explicit strategies are different arguments.',
                    'route_english': english_route, 'route_lean': lean_route,
                    'route_description_english': case['routes'][english_route],
                    'route_description_lean': case['routes'][lean_route],
                    'formal_source_declaration': formal[lean_route]['source_declaration'],
                    'source_file': 'lean/ArgumentCore.lean', 'source_file_sha256': digest(source_bytes),
                    'split': 'held_out_constructed_diagnostic', 'use_for_training': False,
                    'lean_replay': 'passed', 'transitive_axioms': axioms[formal[lean_route]['source_declaration']],
                    'human_argument_review': False,
                })
    # Verify exact duplicated one-sided evidence has opposing labels, without
    # relying on route metadata that the model never receives.
    for case in CASES:
        cells = [r for r in rows if r['group'] == 'core-' + case['id']]
        assert len({r['formal_statement'] for r in cells}) == 1
        assert len({r['context'] for r in cells}) == 1
        assert len({r['informal_statement'] for r in cells}) == 1
        assert Counter(r['label'] for r in cells) == Counter({True: 2, False: 2})
        for field in ['informal_proof', 'formal_proof']:
            for text in {r[field] for r in cells}:
                assert {r['label'] for r in cells if r[field] == text} == {True, False}
    target = DEST/'test.jsonl'
    target.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows), encoding='utf-8')
    replay_sha = replay_payloads(rows)
    manifest = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'ready_for_evaluation': True, 'compiled': True, 'lean_build_status': 'passed',
        'scope': 'same_theorem_argument_correspondence', 'rows': len(rows),
        'theorem_groups': len(CASES), 'route_proofs': len(axioms),
        'labels': {'match': 8, 'mismatch': 8}, 'use_for_training': False,
        'label_provenance': 'Agent-authored English arguments, explicit Lean proofs and route judgments; not human-audited.',
        'negative_policy': 'Cross two valid proof routes for one literally identical statement and context.',
        'limitations': [
            'Four elementary theorem groups; descriptive diagnostic only, not a representative benchmark.',
            'Agent-authored route labels have no independent human review.',
            'Imported supporting lemmas expose strategy-level granularity, not every kernel proof step.',
            'Public elementary mathematics may occur in model pretraining.',
            'Do not tune prompts, thresholds or adapters on these held-out cases.',
        ],
        'lean_version': version, 'lean_toolchain': (ROOT/'lean/lean-toolchain').read_text().strip(),
        'lake_manifest_sha256': digest((ROOT/'lean/lake-manifest.json').read_bytes()),
        'source_file': 'lean/ArgumentCore.lean', 'source_file_sha256': digest(source_bytes),
        'test_jsonl_sha256': digest(target.read_bytes()), 'files': {'test.jsonl': digest(target.read_bytes())},
        'payload_replay_compiled': True, 'payload_replay_sha256': replay_sha,
        'axioms': axioms,
    }
    (DEST/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'rows': len(rows), 'groups': len(CASES), 'compiled': True,
        'lean_version': version, 'destination': str(DEST)}))


if __name__ == '__main__':
    main()
