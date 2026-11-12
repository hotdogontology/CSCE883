"""Scientific validity guards for source-isolated intermediary comparisons."""
import json
import unittest

from intermediary_model import (source_view, translation_messages, judge_messages,
                                 clean_generation, generation_finished, generation_key,
                                 pair_representations, requirements, summarize, output_budget)


def example():
    return {'id': 'SECRET_ID', 'label': False, 'donor_id': 'SECRET_DONOR',
            'informal_statement': 'ENGLISH_CLAIM', 'informal_proof': 'ENGLISH_PROOF',
            'context': 'FORMAL_CONTEXT', 'formal_statement': 'FORMAL_CLAIM',
            'formal_proof': 'FORMAL_PROOF'}


class IntermediaryGuards(unittest.TestCase):
    def test_english_generation_cannot_see_formal_branch_or_labels(self):
        row = example()
        text = json.dumps(translation_messages(source_view(row, 'english'), 'english', 'lean'))
        for forbidden in ['FORMAL_CONTEXT', 'FORMAL_CLAIM', 'FORMAL_PROOF', 'SECRET_ID', 'SECRET_DONOR']:
            self.assertNotIn(forbidden, text)
        self.assertIn('ENGLISH_PROOF', text)
        self.assertNotIn('"label"', text)

    def test_formal_generation_cannot_see_english_branch_or_labels(self):
        row = example()
        text = json.dumps(translation_messages(source_view(row, 'lean'), 'lean', 'english'))
        for forbidden in ['ENGLISH_CLAIM', 'ENGLISH_PROOF', 'SECRET_ID', 'SECRET_DONOR']:
            self.assertNotIn(forbidden, text)
        self.assertIn('FORMAL_PROOF', text)
        self.assertIn('FORMAL_CONTEXT', text)

    def test_dual_translations_and_judge_are_isolated(self):
        row = example()
        generated = {'english': {'text': 'TRANSLATION_N'}, 'lean': {'text': 'TRANSLATION_F'}}
        first, second, representation = pair_representations(row, 'verbose_lean', generated)
        text = json.dumps(judge_messages(first, second, representation))
        self.assertIn('TRANSLATION_N', text)
        self.assertIn('TRANSLATION_F', text)
        for value in row.values():
            if isinstance(value, str):
                self.assertNotIn(value, text)

    def test_single_translation_compares_against_correct_provided_view(self):
        row = example()
        generated = {'english': {'text': 'GENERATED_LEAN'}, 'lean': {'text': 'GENERATED_ENGLISH'}}
        first, second, language = pair_representations(row, 'nl_to_lean', generated)
        self.assertEqual(first, 'GENERATED_LEAN')
        self.assertEqual(second, source_view(row, 'lean'))
        first, second, language = pair_representations(row, 'lean_to_nl', generated)
        self.assertEqual(first, source_view(row, 'english'))
        self.assertEqual(second, 'GENERATED_ENGLISH')

    def test_cache_deduplicates_views_without_label_or_id(self):
        a = example()
        b = dict(a, id='ANOTHER_ID', label=True, formal_proof='OTHER_FORMAL_PROOF')
        first = translation_messages(source_view(a, 'english'), 'english', 'lean')
        second = translation_messages(source_view(b, 'english'), 'english', 'lean')
        self.assertEqual(generation_key(first, {'base': 'A'}), generation_key(second, {'base': 'A'}))
        self.assertNotEqual(generation_key(first, {'base': 'A'}), generation_key(first, {'base': 'B'}))

    def test_truncated_output_is_not_complete(self):
        self.assertFalse(generation_finished([1, 2, 3], {99}, 3))
        self.assertTrue(generation_finished([1, 2, 99], {99}, 3))
        self.assertFalse(generation_finished([], {99}, 3))

    def test_generation_budget_preserves_full_input_and_total_context_limit(self):
        self.assertEqual(output_budget(2000, 4096, 1536), 1536)
        self.assertEqual(output_budget(3500, 4096, 1536), 596)
        self.assertEqual(output_budget(3840, 4096, 1536), 256)
        self.assertLess(output_budget(3841, 4096, 1536), 256)
        self.assertEqual(output_budget(4500, 4096, 1536), 0)

    def test_admission_failure_not_semantic_negative(self):
        text, status = clean_generation('```lean\ntheorem t : True := by sorry\n```', 'lean')
        self.assertEqual(status, 'admitted_generation')
        self.assertEqual(clean_generation('TRANSLATION_FAILED', 'natural_lean')[1], 'untranslatable')
        self.assertEqual(clean_generation('UNTRANSLATABLE', 'english')[1], 'untranslatable')
        self.assertEqual(clean_generation('```lean\ntheorem t : True := by trivial\n```', 'lean')[1], 'generated')

    def test_actual_capitalized_dialect_declarations_are_allowed(self):
        self.assertEqual(clean_generation('import Natural\nTheorem. True. [candidate]\nProof. Therefore True.', 'natural_lean')[1], 'generated')
        self.assertEqual(clean_generation('import Verbose.English.All\nExample "title"\nConclusion: True\nProof:\n  trivial\nQED', 'verbose_lean')[1], 'generated')

    def test_dialect_requires_pinned_guide(self):
        with self.assertRaises(ValueError):
            translation_messages(source_view(example(), 'english'), 'english', 'verbose_lean')

    def test_missing_proof_does_not_become_negative(self):
        with self.assertRaises(ValueError):
            source_view(dict(example(), informal_proof=''), 'english')
        report = summarize([example()], [{'id': 'SECRET_ID', 'status': 'translation_failed', 'prediction': None}])
        self.assertEqual(report['coverage'], 0.)
        self.assertIsNone(report['accuracy'])

    def test_metrics_expose_abstention_and_mismatch_recall(self):
        rows = [{'id': 'A', 'label': False}, {'id': 'B', 'label': True}, {'id': 'C', 'label': False}]
        predictions = [{'id': 'A', 'status': 'predicted', 'prediction': False, 'yes_minus_no_logit': -4.},
                       {'id': 'B', 'status': 'predicted', 'prediction': True, 'yes_minus_no_logit': 4.},
                       {'id': 'C', 'status': 'translation_failed', 'prediction': None}]
        report = summarize(rows, predictions)
        self.assertAlmostEqual(report['coverage'], 2 / 3)
        self.assertEqual(report['metrics']['classes']['mismatch']['recall'], 1.)
        self.assertEqual(report['metrics']['confusion_matrix']['rows_true_columns_predicted'], [[1, 0], [0, 1]])


if __name__ == '__main__':
    unittest.main()
