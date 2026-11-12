from collections import Counter
from unittest import TestCase,main
from unittest.mock import patch
from prepare_argument_budget import select


class BudgetRegeneration(TestCase):
    def test_regenerated_negatives_have_equal_proof_marginals(self):
        rows=[{'id':str(i),'group':str(i),'informal_proof':p,'label':True} for i,p in enumerate(['a','bb','ccc'])]
        def fake_tokens(tokenizer,row,training):return [0]*(len(row['informal_proof'])+1),[1]
        with patch('prepare_argument_budget.tokens',side_effect=fake_tokens):
            result,detail=select(rows,None,5,'train')
        self.assertTrue(detail['english_proof_marginals_equal'])
        self.assertEqual(Counter(r['informal_proof'] for r in result if r['label']),
            Counter(r['informal_proof'] for r in result if not r['label']))

    def test_positive_long_family_is_removed_before_negatives(self):
        rows=[{'id':str(i),'group':str(i),'informal_proof':p,'label':True} for i,p in enumerate(['a','bb','verylong'])]
        def fake_tokens(tokenizer,row,training):return [0]*(len(row['informal_proof'])+1),[1]
        with patch('prepare_argument_budget.tokens',side_effect=fake_tokens):
            result,detail=select(rows,None,4,'train')
        self.assertEqual({r['group'] for r in result},{'0','1'})
        self.assertEqual(detail['rows'],4)


if __name__=='__main__':main()
