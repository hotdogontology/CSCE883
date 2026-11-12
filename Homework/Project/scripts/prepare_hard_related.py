"""Freeze grouped three-way data with threshold-related synthetic argument swaps.

The primary task pairs a coherent English statement/proof with a Lean
statement/proof from a related, different source. Source pairs are user-assumed
positives; swaps are constructed negatives, not human-certified fidelity labels.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random

import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer

from argument_data import FIELDS, canonical_signature, payload
from argument_model import tokens
from mine_related_proofs import graph_tokens, normalize

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'artifacts/argument-14b/data-v4/positive-pairs.jsonl'
DEPENDENCIES = ROOT / 'artifacts/relatedness-20261110/dependencies.jsonl'
OUT = ROOT / 'artifacts/hard-related-20261110/data'
REPORT = ROOT / 'reports/hard-related-20261110'
SEED = 884
THRESHOLD = .20
MAX_TOKENS = 4096


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def write(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_groups(rows):
    groups = sorted({r['group'] for r in rows})
    random.Random(SEED).shuffle(groups)
    n_validation = int(len(groups) * .15)
    n_test = int(len(groups) * .15)
    allocation = {g: ('validation' if i < n_validation else 'test' if i < n_validation + n_test else 'train')
                  for i, g in enumerate(groups)}
    return {name: [r for r in rows if allocation[r['group']] == name]
            for name in ['train', 'validation', 'test']}


def subset_permutation(scores, allowed):
    """Maximize coverage then similarity, using fixed points only as omissions.

    Because every source has one incoming and outgoing edge, the selected
    non-fixed points form disjoint cycles. The selected donor and anchor sets
    therefore coincide exactly, preserving both input marginals across labels.
    """
    n = len(scores)
    costs = np.where(allowed, -(n + 1 + scores), 1e9)
    np.fill_diagonal(costs, 0.)
    indices, donors = linear_sum_assignment(costs)
    selected = [(int(i), int(j)) for i, j in zip(indices, donors) if i != j]
    assert all(allowed[i, j] for i, j in selected)
    assert {i for i, j in selected} == {j for i, j in selected}
    return selected


def negative(anchor, donor, split, kind='bundle'):
    result = {**payload(anchor), 'id': anchor['id'] + '-hard-' + kind,
              'source_id': anchor['id'], 'group': anchor['group'], 'split': split,
              'label': False, 'label_scope': 'argument_fidelity',
              'label_source': 'synthetic_related_source_' + kind + '_swap',
              'label_assumption': 'Different related source assumed semantically mismatched; not independently reviewed.',
              'donor_id': donor['id'], 'donor_group': donor['group'],
              'pair_kind': 'related_' + kind + '_swap',
              'informal_proof': donor['informal_proof']}
    if kind == 'bundle':
        result['informal_statement'] = donor['informal_statement']
    return result


def positive(row, split):
    return {**payload(row), 'id': row['id'] + '-hard-positive', 'source_id': row['id'],
            'group': row['group'], 'split': split, 'label': True,
            'label_scope': 'argument_fidelity', 'label_source': 'user_assumed_corrected_ProofNet_argument_correspondence',
            'label_assumption': 'Source argument correspondence assumed by user; not independently audited.',
            'pair_kind': 'source_positive', 'lean_replay': 'compiled_Lean4.28'}


def validate_splits(splits, source_lookup, threshold=THRESHOLD):
    group_sets = []
    for split, rows in splits.items():
        assert len({r['id'] for r in rows}) == len(rows)
        yes = [r for r in rows if r['label']]
        no = [r for r in rows if not r['label']]
        assert len(yes) == len(no) > 0
        assert Counter((r['informal_statement'], r['informal_proof']) for r in yes) == Counter(
            (r['informal_statement'], r['informal_proof']) for r in no)
        assert Counter(tuple(r[k] for k in ['context', 'formal_statement', 'formal_proof']) for r in yes) == Counter(
            tuple(r[k] for k in ['context', 'formal_statement', 'formal_proof']) for r in no)
        for row in rows:
            assert row['split'] == split
            anchor = source_lookup[row['source_id']]
            assert row['group'] == anchor['group']
            assert all(row[k] == anchor[k] for k in ['context', 'formal_statement', 'formal_proof'])
            donor = anchor if row['label'] else source_lookup[row['donor_id']]
            assert row['informal_statement'] == donor['informal_statement']
            assert row['informal_proof'] == donor['informal_proof']
            if not row['label']:
                assert row['group'] != row['donor_group']
                assert row['relatedness_score'] >= threshold
        group_sets.append({r['group'] for r in rows})
    assert all(not a.intersection(b) for i, a in enumerate(group_sets) for b in group_sets[i+1:])
    proof_sets = [{r['informal_proof'] for r in rows} for rows in splits.values()]
    assert all(not a.intersection(b) for i, a in enumerate(proof_sets) for b in proof_sets[i+1:])


def main():
    if (OUT / 'manifest.json').exists():
        manifest = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
        assert manifest['builder_sha256'] == digest(Path(__file__)), 'Builder changed: preserve old dataset and use a fresh version.'
        assert all(digest(OUT/name) == expected for name, expected in manifest['files'].items())
        print(json.dumps({'status': 'already_frozen', 'splits': manifest['splits']}))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    sources = read(SOURCE)
    dependencies = {r['id']: r for r in read(DEPENDENCIES)}
    assert all(dependencies[r['id']]['status'] == 'compiled' for r in sources)
    source_lookup = {r['id']: r for r in sources}
    raw_splits = split_groups(sources)
    tokenizer = AutoTokenizer.from_pretrained(ROOT/'data/models/Qwen3-14B', local_files_only=True)
    exclusions = []
    eligible = {}
    # Exclude the whole family if any original pair exceeds the common context.
    for split, rows in raw_splits.items():
        lengths = {r['id']: len(tokens(tokenizer, r, training=True)[0]) for r in rows}
        too_long_groups = {r['group'] for r in rows if lengths[r['id']] > MAX_TOKENS}
        incomplete_groups = {r['group'] for r in rows if not all(
            dependencies[r['id']]['dependencies'][role]['complete'] for role in ['statement', 'proof'])}
        excluded_groups = too_long_groups | incomplete_groups
        eligible[split] = [r for r in rows if r['group'] not in excluded_groups]
        exclusions.extend({'source_id': r['id'], 'group': r['group'], 'split': split,
                           'reason': 'source_or_family_incomplete_dependency_expansion' if r['group'] in incomplete_groups
                                     else 'source_or_family_exceeds_4096', 'tokens': lengths[r['id']]}
                          for r in rows if r['group'] in excluded_groups)
    train = eligible['train']
    vectorizers = {field: TfidfVectorizer(analyzer='char', ngram_range=(3, 5), max_features=20000,
                                        sublinear_tf=True).fit([normalize(r, field) for r in train])
                   for field in ['informal_statement', 'formal_statement']}
    module_vectorizer = TfidfVectorizer(analyzer=lambda x: x, lowercase=False)
    module_vectorizer.fit([graph_tokens(dependencies[r['id']], 'proof', True) for r in train])
    manifest = {
        'scope': 'paired_English_Lean_argument_fidelity_with_synthetic_related_negatives',
        'seed': SEED, 'relatedness_threshold': THRESHOLD,
        'threshold_policy': 'Fixed 0.20 heuristic threshold before new split evaluation; no validation/test labels or model predictions used.',
        'relatedness': '.45 English statement char TF-IDF cosine + .45 normalized Lean statement char TF-IDF cosine + .10 mathlib proof-module TF-IDF cosine',
        'fit_policy': 'Vocabularies and IDF fit only on token-eligible training sources; graph uses compiled source constants, not model predictions.',
        'split_policy': 'Shuffle 335 precomputed exercise/shared-English-proof families with seed884; 70/15/15 by family, before token and similarity filtering.',
        'negative_policy': 'Swap complete English statement+proof bundles with a different related source in the same split. Labels are synthetic assumptions, not human-certified semantic differences.',
        'positive_policy': 'User-assumed corrected ProofNet argument correspondence; original Lean sides replay successfully under pinned Lean4.28.',
        'limits': ['Relatedness is a heuristic, not a calibrated semantic ontology.',
                   'Whole-bundle negatives can change conclusions as well as argument steps; they do not isolate subtle same-theorem route errors.',
                   'Distinct source IDs are not a proof of semantic inequivalence; some synthetic negatives may be mislabeled.',
                   'New test is held out from this training run; previous experiments inspected this public source corpus. It is not a pristine never-observed benchmark.',
                   'Similarity and token filtering change the eligible population; report coverage and original counts.'],
        'max_tokens': MAX_TOKENS, 'source_sha256': digest(SOURCE), 'dependency_sha256': digest(DEPENDENCIES),
        'builder_sha256': digest(Path(__file__)), 'splits': {}, 'core_diagnostic_used_in_construction': False,
        'source_revision': sources[0]['source_revision'], 'lean_replay': 'all365_compiled_Lean4.28',
    }
    result_splits = {}
    for split, rows in eligible.items():
        components = {}
        for field, vectorizer in vectorizers.items():
            matrix = vectorizer.transform([normalize(r, field) for r in rows])
            components[field] = (matrix @ matrix.T).toarray()
        modules = module_vectorizer.transform([graph_tokens(dependencies[r['id']], 'proof', True) for r in rows])
        components['proof_module'] = (modules @ modules.T).toarray()
        scores = .45*components['informal_statement'] + .45*components['formal_statement'] + .10*components['proof_module']
        allowed = np.array([[a['group'] != b['group'] and a['informal_proof'] != b['informal_proof'] and
                             canonical_signature(a['formal_statement']) != canonical_signature(b['formal_statement'])
                             for b in rows] for a in rows]) & (scores >= THRESHOLD)
        initial_edges = int(allowed.sum())
        rejected_edges = 0
        while True:
            assignment = subset_permutation(scores, allowed)
            oversized = [(i, j) for i, j in assignment
                         if len(tokens(tokenizer, negative(rows[i], rows[j], split), training=True)[0]) > MAX_TOKENS]
            if not oversized:
                break
            for i, j in oversized:
                allowed[i, j] = False
            rejected_edges += len(oversized)
        selected = {i for i, j in assignment}
        exclusions.extend({'source_id': row['id'], 'group': row['group'], 'split': split,
                           'reason': 'no_retained_threshold_permutation_edge'}
                          for i, row in enumerate(rows) if i not in selected)
        records = []
        details = []
        proof_only = []
        proof_only_skipped = []
        for i, j in assignment:
            anchor, donor = rows[i], rows[j]
            detail = {'anchor': anchor['id'], 'donor': donor['id'], 'anchor_group': anchor['group'],
                      'donor_group': donor['group'], 'score': float(scores[i, j]),
                      'components': {key: float(value[i, j]) for key, value in components.items()}}
            pos = positive(anchor, split)
            neg = negative(anchor, donor, split)
            neg['relatedness_score'] = detail['score']
            records.extend([pos, neg])
            details.append(detail)
            secondary = negative(anchor, donor, split, 'proof-only')
            secondary['relatedness_score'] = detail['score']
            if len(tokens(tokenizer, secondary, training=True)[0]) <= MAX_TOKENS:
                proof_only.extend([pos, secondary])
            else:
                proof_only_skipped.append(anchor['id'])
        assert records, 'No usable threshold-related cycles in ' + split
        # Deterministic interleaving is intentional; trainer shuffles with its own fixed seed.
        write(OUT/(split+'.jsonl'), records)
        write(OUT/(split+'-proof-only-diagnostic.jsonl'), proof_only)
        write(OUT/(split+'-assignment.jsonl'), details)
        result_splits[split] = records
        scored = [d['score'] for d in details]
        manifest['splits'][split] = {
            'allocated_sources': len(raw_splits[split]), 'allocated_families': len({r['group'] for r in raw_splits[split]}),
            'token_eligible_sources': len(rows), 'selected_sources': len(assignment),
            'rows': len(records), 'positives': len(assignment), 'negatives': len(assignment),
            'threshold_edges_before_token_check': initial_edges, 'rejected_over_budget_edges': rejected_edges,
            'minimum_relatedness': min(scored), 'mean_relatedness': float(np.mean(scored)),
            'maximum_relatedness': max(scored), 'exact_English_bundle_and_Lean_marginals': True,
            'max_training_tokens': max(len(tokens(tokenizer, r, training=True)[0]) for r in records),
            'proof_only_diagnostic_rows': len(proof_only), 'proof_only_skipped_anchors': proof_only_skipped,
        }
    validate_splits(result_splits, source_lookup)
    write(OUT/'excluded.jsonl', exclusions)
    write(OUT/'split-allocation.jsonl', [{'id': r['id'], 'group': r['group'], 'split': split}
                                       for split, rows in raw_splits.items() for r in rows])
    manifest['files'] = {p.name: digest(p) for p in sorted(OUT.glob('*.jsonl'))}
    manifest['validation'] = {'group_disjoint': True, 'English_proof_disjoint': True,
                              'balanced_labels': True, 'donors_within_split': True,
                              'exact_label_marginals': True, 'all_training_prompts_fit': True}
    text = json.dumps(manifest, indent=2) + '\n'
    (OUT/'manifest.json').write_text(text, encoding='utf-8')
    (REPORT/'dataset-manifest.json').write_text(text, encoding='utf-8')
    print(json.dumps({'status': 'frozen', 'splits': manifest['splits']}, indent=2))


if __name__ == '__main__':
    main()
