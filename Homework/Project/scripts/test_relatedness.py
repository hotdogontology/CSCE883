"""Guard against metadata leakage, loss of input separation and fake graph coverage."""
import unittest

from mine_related_proofs import graph_tokens, normalize, original_donors
from argument_data import swapped_negatives
from random_forest_argument import FIELDS, texts
from extract_proof_dependencies import replay_code


class RelatednessGuards(unittest.TestCase):
    def test_original_donor_reconstruction_handles_shared_proofs(self):
        rows=[{'id':str(i),'group':group,'informal_proof':proof,'label':True}
              for i,(group,proof) in enumerate([('A','same'),('A','same'),('B','other'),('C','third')])]
        donors=original_donors(rows)
        negatives=[r for r in swapped_negatives(rows,'train') if not r['label']]
        self.assertEqual({r['id'].removesuffix('-swapped'):r['informal_proof'] for r in negatives},
                         {id:donor['informal_proof'] for id,donor in donors.items()})

    def test_scoped_option_stays_attached_to_target(self):
        row={'context':'import Mathlib\nset_option maxHeartbeats 800000 in',
             'formal_statement':'theorem target : True','formal_proof':'by trivial',
             'extracted_declaration':'target'}
        code=replay_code(row,'namespace ExportHelper\nend ExportHelper')
        self.assertIn('800000 in\n\ntheorem target',code)
        self.assertLess(code.index('by trivial'),code.index('namespace ExportHelper'))

    def test_classifier_features_ignore_labels_and_source_names(self):
        a=dict(informal_statement='Claim',informal_proof='Argument',
               formal_statement='theorem Source_exercise_1 (n : Nat) : n = n',formal_proof='by rfl',
               label=True,id='source',route_english='A')
        b=dict(a,formal_statement='theorem Other_exercise_9 (n : Nat) : n = n',
               label=False,id='different',route_english='B')
        self.assertEqual(texts([a],FIELDS),texts([b],FIELDS))

    def test_failed_compilation_never_supplies_dependencies(self):
        self.assertEqual(graph_tokens({'status':'compile_failed'},'proof'),[])
        self.assertEqual(graph_tokens(None,'statement'),[])

    def test_statement_and_proof_dependencies_remain_distinct(self):
        row={'status':'compiled','dependencies':{
            'statement':{'constants':[{'name':'Group','module':'Mathlib.Algebra.Group.Defs'}]},
            'proof':{'constants':[{'name':'helper','module':'LOCAL'},
                                   {'name':'induction','module':'Mathlib.GroupTheory.Basic'},
                                   {'name':'tactic','module':'Mathlib.Tactic.Basic'}]}}}
        self.assertEqual(graph_tokens(row,'statement'),['Group'])
        self.assertNotIn('helper',graph_tokens(row,'proof'))
        self.assertEqual(graph_tokens(row,'proof',True),['Mathlib.GroupTheory.Basic'])

    def test_normalization_keeps_mathematical_claim(self):
        self.assertEqual(normalize({'formal_statement':'theorem source (n : Nat) : n = n'},'formal_statement'),
                         'theorem candidate (n : Nat) : n = n')


if __name__=='__main__':unittest.main()
