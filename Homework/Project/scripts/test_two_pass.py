import argparse
import json
from pathlib import Path
import tempfile
import unittest

from two_pass import messages, statement, consensus, write, read


class SafetyTests(unittest.TestCase):
    def test_evidence_excludes_label_and_rationale(self):
        row=dict(informal_statement='English',formal_statement='Lean',context='',label=True,
                 reasoning='answer YES',informal_proof='unused')
        payload=json.loads(messages(row)[1]['content'])
        self.assertEqual(set(payload),{'informal_statement','formal_statement','context'})

    def test_template_removal_keeps_local_assignment(self):
        self.assertEqual(statement('theorem t : let x := 1; x = 1 := by sorry'),
                         'theorem t : let x := 1; x = 1')

    def test_consensus_excludes_disagreement_missing_and_reserved(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)
            rows=[{'id':str(i),'pseudo_train_eligible':i!=3} for i in range(5)]
            write(p/'input.jsonl',rows)
            write(p/'a.jsonl',[{'id':str(i),'prediction':v} for i,v in enumerate([True,False,True,True,None])])
            write(p/'b.jsonl',[{'id':str(i),'prediction':v} for i,v in enumerate([True,False,False,True,False])])
            consensus(argparse.Namespace(input=p/'input.jsonl',untuned=p/'a.jsonl',first_pass=p/'b.jsonl',output=p/'out'))
            kept=read(p/'out/train.jsonl')
            self.assertEqual([r['id'] for r in kept],['0','1'])
            self.assertEqual([r['label'] for r in kept],[True,False])
            self.assertEqual(read(p/'input.jsonl'),rows)


if __name__=='__main__':unittest.main()
