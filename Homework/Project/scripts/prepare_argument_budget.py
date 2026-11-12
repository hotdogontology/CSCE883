"""Regenerate within-split proof negatives after length filtering, preserving marginals."""
import argparse
from collections import Counter
import json
from pathlib import Path

from argument_data import swapped_negatives
from argument_model import tokens
from two_pass import ROOT,read,write,metadata,sha


def select(rows,tokenizer,budget,split):
    positive=[r for r in rows if r['label'] is True]
    original_count=len(positive);excluded=[]
    # Remove entire source-family groups when any source proof does not fit.
    long_groups={r['group'] for r in positive if len(tokens(tokenizer,r,True)[0])>budget}
    excluded.extend({'id':r['id'],'reason':'positive_family_exceeds_budget'} for r in positive if r['group'] in long_groups)
    positive=[r for r in positive if r['group'] not in long_groups]
    rounds=0
    while True:
        rounds+=1
        if len(positive)<2:raise ValueError('Too few source proofs remain for balanced negatives')
        pairs=swapped_negatives(positive,split)
        bad_groups={r['group'] for r in pairs if len(tokens(tokenizer,r,True)[0])>budget}
        if not bad_groups:break
        excluded.extend({'id':r['id'],'reason':'regenerated_negative_family_exceeds_budget'}
            for r in positive if r['group'] in bad_groups)
        positive=[r for r in positive if r['group'] not in bad_groups]
    yes=Counter(r['informal_proof'] for r in pairs if r['label'])
    no=Counter(r['informal_proof'] for r in pairs if not r['label'])
    assert yes==no
    assert Counter(r['label'] for r in pairs)=={True:len(positive),False:len(positive)}
    assert all(len(tokens(tokenizer,r,True)[0])<=budget for r in pairs)
    return pairs,{'original_positive_count':original_count,'retained_positive_count':len(positive),
        'rows':len(pairs),'groups':len({r['group'] for r in pairs}),'rounds':rounds,'excluded':excluded,
        'english_proof_marginals_equal':True,'class_balance_equal':True}


def main():
    from transformers import AutoTokenizer
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-tokens',type=int,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    tokenizer=AutoTokenizer.from_pretrained(ROOT/'data/models/Qwen3-14B',local_files_only=True)
    details={};split_groups={}
    for split in ['train','validation']:
        pairs,detail=select(read(args.source/(split+'.jsonl')),tokenizer,args.max_tokens,split)
        write(args.output/(split+'.jsonl'),pairs);details[split]=detail
        split_groups[split]={r['group'] for r in pairs}
    assert not split_groups['train']&split_groups['validation']
    metadata(args.output/'manifest.json',{'ready_for_training':True,'token_budget':args.max_tokens,
        'label_scope':'cross_problem_proof_consistency_pilot','details':details,
        'source_manifest_sha256':sha((args.source/'manifest.json').read_bytes()),
        'files':{f.name:sha(f.read_bytes()) for f in args.output.glob('*.jsonl')}})
    print(json.dumps({split:{k:v for k,v in d.items() if k!='excluded'} for split,d in details.items()},indent=2))


if __name__=='__main__':main()
