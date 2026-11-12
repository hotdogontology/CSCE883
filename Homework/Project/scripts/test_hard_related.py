"""Integrity checks for threshold-related synthetic argument datasets."""
from collections import Counter
import json
import unittest

import numpy as np

from prepare_hard_related import (OUT, SOURCE, THRESHOLD, negative, payload, read,
                                  split_groups, subset_permutation, validate_splits)


class ThresholdMatchingTests(unittest.TestCase):
    def test_cardinality_precedes_similarity_and_omits_isolated_source(self):
        scores = np.array([[0., .95, .20, 0.], [.95, 0., .20, 0.], [.20, .20, 0., 0.], [0., 0., 0., 0.]])
        allowed = scores >= .20
        assignment = subset_permutation(scores, allowed)
        self.assertEqual({i for i, j in assignment}, {0, 1, 2})
        self.assertEqual({j for i, j in assignment}, {0, 1, 2})
        self.assertTrue(all(i != j for i, j in assignment))

    def test_directed_edges_cannot_create_unmatched_donor(self):
        scores = np.ones((3, 3))
        allowed = np.array([[False, True, False], [True, False, True], [False, False, False]])
        self.assertEqual(set(subset_permutation(scores, allowed)), {(0, 1), (1, 0)})

    def test_family_allocation_preserves_shared_group(self):
        rows = [{'id': str(i), 'group': str(i // 2)} for i in range(40)]
        splits = split_groups(rows)
        self.assertEqual(splits, split_groups(rows))
        owners = {}
        for name, values in splits.items():
            for row in values:
                self.assertEqual(owners.setdefault(row['group'], name), name)
        self.assertEqual(sum(len(rows) for rows in splits.values()), 40)

    def test_negative_preserves_complete_sides_and_hides_metadata(self):
        anchor = dict(id='a', group='ga', informal_statement='statement A', informal_proof='argument A',
                      formal_statement='theorem a : True', formal_proof='by trivial', context='import Mathlib')
        donor = dict(anchor, id='b', group='gb', informal_statement='statement B', informal_proof='argument B')
        row = negative(anchor, donor, 'train')
        self.assertEqual(row['informal_statement'], 'statement B')
        self.assertEqual(row['informal_proof'], 'argument B')
        self.assertEqual(row['formal_proof'], anchor['formal_proof'])
        self.assertEqual(set(payload(row)), {'informal_statement', 'informal_proof', 'formal_statement', 'formal_proof', 'context'})
        self.assertNotIn('label', payload(row))
        self.assertNotIn('donor_id', payload(row))


@unittest.skipUnless((OUT/'manifest.json').exists(), 'Frozen data not yet built')
class FrozenDataTests(unittest.TestCase):
    def test_balanced_disjoint_and_source_faithful(self):
        lookup = {r['id']: r for r in read(SOURCE)}
        splits = {name: read(OUT/(name+'.jsonl')) for name in ['train', 'validation', 'test']}
        validate_splits(splits, lookup)

    def test_bad_label_marginal_is_detected(self):
        lookup = {r['id']: r for r in read(SOURCE)}
        splits = {name: read(OUT/(name+'.jsonl')) for name in ['train', 'validation', 'test']}
        splits['test'][0]['informal_proof'] = 'corrupted proof'
        with self.assertRaises(AssertionError):
            validate_splits(splits, lookup)

    def test_allocation_and_assignment_stay_in_split(self):
        allocation = read(OUT/'split-allocation.jsonl')
        owners = {r['id']: r['split'] for r in allocation}
        self.assertEqual(len(owners), 365)
        for split in ['train', 'validation', 'test']:
            for edge in read(OUT/(split+'-assignment.jsonl')):
                self.assertEqual(owners[edge['anchor']], split)
                self.assertEqual(owners[edge['donor']], split)
                self.assertGreaterEqual(edge['score'], THRESHOLD)
                self.assertNotEqual(edge['anchor_group'], edge['donor_group'])


if __name__ == '__main__':
    unittest.main()
