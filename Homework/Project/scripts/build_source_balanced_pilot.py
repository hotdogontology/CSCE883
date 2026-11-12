"""Reproducible small source-balanced pilot; explicit provisional semantic review.

No validity flag is automatically converted to a correspondence label.
"""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from argument_data import strip_comments

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/source-balanced-20261112/data'
REPORT = ROOT / 'reports/source-balanced-20261112'
# Fixed row references into the archived first100 response, reviewed 2026-11-12.
# All labels are model/agent review, not independent human annotations.
REVIEWS = {
  14: (False, 'Assumes the asserted total=sum as a hypothesis, rather than establishing the counting claim.'),
  15: (False, 'Assumes the asserted total=product as a hypothesis; this changes the obligation to a tautology.'),
  16: (True, 'Preserves the explicit local arithmetic calculation 2+1=3; book interpretation remains supplied by English context.'),
  18: (True, 'Four hypotheses preserve each reader reading each collection; the union conclusion covers both readers for every book.'),
  28: (True, 'Preserves the explicit local calculation 9+5=14; color interpretation is supplied by source context.'),
  30: (True, 'Preserves 14-3=11; natural subtraction agrees with the nonnegative counts in this local step.'),
  32: (False, 'Adds total=red+blue+yellow as a premise, assuming the claim instead of deriving the total.'),
  33: (False, 'Adds the claimed total=red+blue-yellow as a premise; does not establish the original counting relation.'),
  38: (False, 'Assumes the total-count formula it was asked to establish, leaving only identity of premise and conclusion.'),
  41: (False, 'Replaces a claim about total animals with expression=itself; removes the connection to the total.'),
  42: (True, 'Preserves the source total via its dependency counts: 10+15+36+12=73. Local arithmetic fidelity, not full story certification.'),
  52: (True, 'Preserves x=12 as a hypothesis and 3*x=36 as conclusion, representing the stated substitution/calculation.'),
  54: (False, 'Omits the observation that five fries remain and universally asserts the resulting equation for arbitrary x.'),
  55: (False, 'Changes an equation about the given initial quantity into existence of some real quantity satisfying an equation.'),
  56: (True, 'Preserves the preceding equation as a hypothesis and the add-one inference as conclusion.'),
  58: (True, 'Preserves the one-third equation as hypothesis and multiplication-by-three conclusion.'),
}
SPLITS = {'gsm8k-201': 'train', 'gsm8k-202': 'train',
          'gsm8k-203': 'validation', 'gsm8k-204': 'test'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def clean(code):
    code = strip_comments(code)
    # Rename the target declaration consistently, including self-references.
    names = re.findall(r'(?m)^(?:theorem|lemma)\s+([^\s(:{]+)', code)
    if names:
        code = re.sub(r'(?<![\w.])' + re.escape(names[-1]) + r'(?![\w.])', 'target', code)
    return '\n'.join(x for x in code.splitlines() if x.strip())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    path = ROOT / 'data/faithform-label-audit/Faithform-LLMs-first100.json'
    source_bytes = path.read_bytes()
    source = json.loads(source_bytes)['rows']
    rows = []
    for index, (label, reason) in REVIEWS.items():
        r = source[index]['row']
        blocks = re.findall(r'```(?:lean4?|Lean4?)?\s*\n(.*?)```', r['autoformalizer_output'], re.S)
        assert blocks, f'No committed code block: {index}'
        deps = ast.literal_eval(r['dependencies_content'])
        english = 'Context:\n' + '\n'.join(deps) + '\nStep:\n' + r['step_content']
        rows.append({'id': f'faithform-llms-row-{index}', 'source': 'faithform',
                     'group': 'faithform:' + r['problem_id'], 'split': SPLITS[r['problem_id']],
                     'label': label, 'scope': 'local_inference_translation',
                     'input': {'english': english, 'lean': clean(blocks[-1])},
                     'provenance': {'status': 'agent_reviewed_provisional', 'reason': reason,
                                    'source_row': index, 'source_sha256': digest(source_bytes),
                                    'problem_id': r['problem_id'], 'node_id': r['node_id'],
                                    'upstream_proof_result': r['proof_result'],
                                    'is_perturbed': r['is_perturbed'],
                                    'formal_proof_body': 'placeholder; assess local inference translation, not proof route'}})
    hashes = {'faithform_first100': digest(source_bytes)}
    all_pn = {}
    for split in ('train', 'validation', 'test'):
        p = ROOT / f'artifacts/hard-related-20261110/data/{split}.jsonl'
        raw = p.read_bytes(); hashes['proofnet_' + split] = digest(raw)
        all_pn[split] = [json.loads(x) for x in raw.decode('utf-8').splitlines()]
    # Verify inherited splits isolate donor and recipient source families.
    seen = {}
    for split, inherited in all_pn.items():
        for r in inherited:
            for g in [r['group'], r.get('donor_group', r['group'])]:
                assert g not in seen or seen[g] == split, ('Inherited donor leakage', g)
                seen[g] = split
    for split, inherited in all_pn.items():
        quota = sum(r['split'] == split and r['label'] for r in rows if r['source'] == 'faithform')
        pairs = {}
        for r in inherited:
            pairs.setdefault(r['group'], {})[r['label']] = r
        candidates = [v for v in pairs.values() if len(v) == 2]
        # Prefer shorter complete pairs to reduce the length gap, without truncation.
        candidates.sort(key=lambda pair: (sum(len(str(pair[b].get(k, ''))) for b in (True, False)
                            for k in ('informal_proof', 'formal_proof')), pair[True]['id']))
        for pair in candidates[:quota]:
            for label in (True, False):
                r = pair[label]
                english = r['informal_statement'] + '\nProof:\n' + r['informal_proof']
                lean = r['context'] + '\n' + r['formal_statement'] + ' := ' + r['formal_proof']
                rows.append({'id': r['id'], 'source': 'proofnet', 'group': r['group'],
                             'split': split, 'label': label, 'scope': 'full_argument_correspondence',
                             'input': {'english': english, 'lean': clean(lean)},
                             'provenance': {'status': r['label_source'],
                                            'reason': r.get('label_assumption', 'Related-problem English bundle swap; constructed mismatch, not human gold.'),
                                            'donor_group': r.get('donor_group'), 'source_id': r['source_id']}})
    seen, input_splits = {}, {}
    for r in rows:
        assert set(r['input']) == {'english', 'lean'}
        for g in [r['group'], r['provenance'].get('donor_group')]:
            if g:
                assert g not in seen or seen[g] == r['split']
                seen[g] = r['split']
        h = digest(json.dumps(r['input'], sort_keys=True).encode())
        assert h not in input_splits or input_splits[h] == r['split'], 'Duplicate input across splits'
        input_splits[h] = r['split']
    for split in ('train', 'validation', 'test'):
        selected = sorted([r for r in rows if r['split'] == split], key=lambda r: digest(r['id'].encode()))
        counts = Counter((r['source'], r['label']) for r in selected)
        assert len(counts) == 4 and len(set(counts.values())) == 1, counts
        (OUT / (split + '.jsonl')).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in selected), encoding='utf-8')
    manifest = {'rows': len(rows), 'input_hashes': hashes,
                'counts': {s: dict(Counter(r['source'] + ':' + str(r['label']) for r in rows if r['split'] == s))
                           for s in ('train', 'validation', 'test')},
                'faithform_review': 'agent provisional, not independent human gold',
                'limitations': ['Four Faithform source problems, ordered convenience sample',
                               'Source balanced, but local inference vs full-proof scope differs',
                               'ProofNet full-proof positives assumed; related swaps constructed',
                               'No formal proof replay or human review in this build']}
    (REPORT / 'dataset-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    review = ['# Source-balanced pilot review', '', 'Provisional agent review; labels are not human gold.', '']
    for r in rows:
        review += [f"## {r['id']} ({r['split']}; {'MATCH' if r['label'] else 'MISMATCH'})",
                   '', r['provenance']['reason'], '', '```text', r['input']['english'], '```',
                   '', '```lean', r['input']['lean'], '```', '']
    (REPORT / 'review.md').write_text('\n'.join(review), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
