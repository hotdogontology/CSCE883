import unittest
from collections import Counter
from argument_data import strip_comments,assignment,extract,payload,swapped_negatives,paired_too_long,trusted_signature,family_groups
from argument_model import messages


class ArgumentGuards(unittest.TestCase):
    def test_nested_comments_and_comment_markers_in_strings(self):
        self.assertEqual(strip_comments('def s := "-- /-" /- a /- nested -/ b -/\n-- x\ntheorem t : True := by trivial'),
            'def s := "-- /-"\n\ntheorem t : True := by trivial')

    def test_outer_assignment_not_binder_default(self):
        t='theorem x (n : Nat := 0) : n = n := by rfl'
        self.assertEqual(t[assignment(t):],':= by rfl')

    def test_corrected_target_not_admitted_original_or_refutation(self):
        text='import Mathlib\n/- English proof YES -/\ntheorem t : False := by sorry\ntheorem t_neg : True := by trivial\nnamespace X\ntheorem _root_.t_corrected : True := by trivial\nend X'
        result=extract(text,'t')
        self.assertEqual(result['formal_proof'],'by trivial')
        self.assertIn('import Mathlib',result['context'])
        self.assertNotIn('sorry',str(result));self.assertNotIn('t_neg',str(result));self.assertNotIn('English',str(result))

    def test_signature_aligns_unbracketed_type_let(self):
        template='theorem t : let x : Nat := 1; x = 1 := by sorry'
        code='theorem t_corrected : let x : Nat := 1; x = 1 := by rfl'
        split=assignment(code,trusted_signature(template))
        self.assertEqual(code[split+2:].strip(),'by rfl')

    def test_trusted_signature_accepts_plain_sorry_and_option_wrapper(self):
        template='set_option maxRecDepth 2048 in\ntheorem t : True := sorry'
        code='theorem t_corrected : True := by trivial'
        self.assertEqual(code[assignment(code,trusted_signature(template))+2:].strip(),'by trivial')

    def test_source_signature_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'trusted signature'):
            assignment('theorem t : False := by trivial','theorem t : True')

    def test_genuine_prefixed_helper_retained_and_obsolete_instance_removed(self):
        text='import Mathlib\ntheorem t_helper : True := by trivial\ninstance t : Nonempty Nat := by exact ⟨0⟩\ntheorem t_corrected : True := by exact t_helper'
        result=extract(text,'t','theorem t : True')
        self.assertIn('theorem t_helper',result['context'])
        self.assertNotIn('instance t :',result['context'])

    def test_context_dependency_on_removed_target_is_rejected(self):
        text='theorem t : True := by sorry\ndef dependent : True := t\ntheorem t_corrected : True := by trivial'
        with self.assertRaisesRegex(ValueError,'context depends'):
            extract(text,'t','theorem t : True')

    def test_qualified_dependency_on_removed_target_is_rejected(self):
        text='theorem t : True := by sorry\ndef dependent : True := _root_.t\ntheorem t_corrected : True := by trivial'
        with self.assertRaisesRegex(ValueError,'context depends'):
            extract(text,'t','theorem t : True')

    def test_family_parts_and_shared_proofs_are_grouped(self):
        rows=[{'id':'a','name':'Pugh_exercise_3_63a','informal_proof':'same proof'},
              {'id':'b','name':'Pugh_exercise_3_63b','informal_proof':'other proof'},
              {'id':'c','name':'Other_exercise_1','informal_proof':'same  proof'}]
        family_groups(rows)
        self.assertEqual(len({r['group'] for r in rows}),1)

    def test_payload_has_both_proof_bodies_and_no_labels(self):
        row=dict(informal_statement='S',informal_proof='English argument',formal_statement='T',
            formal_proof='by rfl',context='',label=True,label_source='assumption',commented_proof='leak')
        data=payload(row)
        self.assertIn('informal_proof',data);self.assertIn('formal_proof',data)
        self.assertNotIn('label',data);self.assertNotIn('commented_proof',data)
        self.assertIn('English argument',messages(row)[1]['content'])

    def test_swaps_leave_statements_and_lean_unchanged(self):
        rows=[dict(id=str(i),group=str(i),informal_proof='argument '+str(i),
            informal_statement='S'+str(i),formal_statement='T'+str(i),formal_proof='by rfl',context='',label=True) for i in range(3)]
        result=swapped_negatives(rows,'train')
        self.assertEqual(Counter(r['informal_proof'] for r in result[::2]),
                         Counter(r['informal_proof'] for r in result[1::2]))
        for pos,neg in zip(result[::2],result[1::2]):
            for k in ['informal_statement','formal_statement','formal_proof','context']:
                self.assertEqual(pos[k],neg[k])
            self.assertNotEqual(pos['informal_proof'],neg['informal_proof'])
            self.assertNotEqual(pos['group'],neg['donor_group'])

    def test_long_positive_excludes_its_negative_too(self):
        self.assertEqual(paired_too_long([{'group':'a'},{'group':'a'},{'group':'b'}],[101,2,3],100),{'a'})


if __name__=='__main__':unittest.main()
