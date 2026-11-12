"""Checks for generated-code replay admission policy and actual pinned compilers."""
import tempfile
import unittest
from pathlib import Path
from check_intermediary_compilation import environment, replay, screen


class CompilationTests(unittest.TestCase):
    def test_admissions(self):
        for source in ['theorem bad : False := by sorry', 'Axiom. False.',
                       'axiom hidden : False\ntheorem bad : False := hidden']:
            self.assertEqual(screen(source), 'rejected_admission_or_opaque_declaration')

    def test_no_executable_extensions(self):
        self.assertEqual(screen('#eval IO.println "hello"\nexample : True := by trivial'),
                         'rejected_executable_extension')
        self.assertEqual(screen('example : True := by run_tac pure (); trivial'),
                         'rejected_executable_extension')

    def test_import_whitelist(self):
        self.assertEqual(screen('import PrivateProject\nexample : True := by trivial'), 'rejected_import')
        self.assertIsNone(screen('import Mathlib\n-- no sorry here\nexample : True := by trivial'))

    def test_failed_generation_not_compiled(self):
        with tempfile.TemporaryDirectory() as directory:
            result = replay({'cache_key': 'test', 'target': 'lean', 'status': 'generation_truncated'},
                            {'status': 'ready'}, Path(directory), 10)
            self.assertEqual(result['status'], 'not_checked')

    def test_local_lean(self):
        config = environment('lean')
        if config['status'] != 'ready': self.skipTest('Lean4.28 unavailable')
        with tempfile.TemporaryDirectory() as directory:
            result = replay({'cache_key': 'test', 'target': 'lean', 'status': 'generated',
                             'text': 'import Mathlib\ntheorem candidate : (2 : Nat) + 3 = 5 := by decide\n'},
                            config, Path(directory), 60)
            self.assertEqual(result['status'], 'compiled', result)

    def test_local_natural(self):
        config = environment('natural_lean')
        if config['status'] != 'ready': self.skipTest('Natural Lean unavailable')
        with tempfile.TemporaryDirectory() as directory:
            result = replay({'cache_key': 'test', 'target': 'natural_lean', 'status': 'generated',
                             'text': 'import Natural\nTheorem. For all x : Nat, x = x. [candidate]\nProof. Let x : Nat. Therefore x = x.\n'},
                            config, Path(directory), 60)
            self.assertEqual(result['status'], 'compiled', result)


if __name__ == '__main__':
    unittest.main()
