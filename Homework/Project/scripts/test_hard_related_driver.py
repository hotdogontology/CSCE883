"""Checks for stage provenance and honest partial-coverage reporting."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_hard_related_experiment as driver


class DriverTests(unittest.TestCase):
    def test_failed_generations_are_not_negative_predictions(self):
        rows = [{'id': 'a', 'label': True}, {'id': 'b', 'label': False}, {'id': 'c', 'label': False}]
        predictions = [{'id': 'a', 'prediction': True, 'status': 'predicted', 'yes_minus_no_logit': 2.},
                       {'id': 'b', 'prediction': False, 'status': 'predicted', 'yes_minus_no_logit': -1.},
                       {'id': 'c', 'prediction': None, 'status': 'translation_failed'}]
        result = driver.metrics(rows, predictions)
        self.assertAlmostEqual(result['coverage'], 2 / 3)
        self.assertEqual(result['accuracy'], 1.)
        self.assertEqual(result['confusion_matrix'], [[1, 0], [0, 1]])
        self.assertEqual(result['auroc_match'], 1.)
        self.assertEqual(result['class_coverage']['mismatch'], {'expected': 2, 'scored': 1})

    def test_no_scored_rows_is_reported_without_inventing_accuracy(self):
        result = driver.metrics([{'id': 'a', 'label': True}],
                                [{'id': 'a', 'prediction': None, 'status': 'translation_failed'}])
        self.assertEqual(result['coverage'], 0)
        self.assertIsNone(result['accuracy'])

    def test_missing_predictions_are_rejected(self):
        with self.assertRaises(ValueError):
            driver.metrics([{'id': 'a', 'label': True}], [])

    def test_unscored_duplicate_predictions_are_rejected(self):
        with self.assertRaises(ValueError):
            driver.metrics([{'id': 'a', 'label': True}, {'id': 'b', 'label': False}],
                           [{'id': 'a', 'prediction': None}, {'id': 'a', 'prediction': None}])

    def test_frozen_input_changes_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'x.jsonl').write_text('original')
            config = {'stages': [], 'inputs': {'x.jsonl': driver.digest(root / 'x.jsonl')}}
            with patch.object(driver, 'ROOT', root):
                driver.validate_queue(config)
                (root / 'x.jsonl').write_text('changed')
                with self.assertRaises(ValueError):
                    driver.validate_queue(config)

    def test_forward_dependencies_are_rejected(self):
        with self.assertRaises(ValueError):
            driver.validate_queue({'stages': [{'name': 'tuned', 'depends_on': ['train']}], 'inputs': {}})


if __name__ == '__main__':
    unittest.main()
