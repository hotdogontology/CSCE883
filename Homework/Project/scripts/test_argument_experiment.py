import unittest
from collections import Counter
from argument_data import strip_comments,assignment,extract,payload,swapped_negatives,paired_too_long
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
