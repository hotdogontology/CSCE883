"""Reproduce concrete extraction and split-integrity findings without model inference."""
from collections import defaultdict
import json
import re
import pandas as pd
from argument_data import ROOT,strip_comments
from two_pass import read,statement,metadata


def main():
    source=ROOT/'artifacts/argument-14b/data-v3'
    prepared={r['id']:r for r in read(source/'herald.jsonl')}
    original=pd.read_parquet(ROOT/'data/herald/data/train-00000-of-00001.parquet')
    bad=[]
    for row in original.to_dict('records'):
        identity=f'herald-{row["id"]}'
        expected=strip_comments(statement(row['formal_theorem']))
        actual=prepared[identity].get('formal_statement','')
        if re.sub(r'\s+','',expected)!=re.sub(r'\s+','',actual):bad.append(identity)
    positives={r['id']:r for r in read(source/'positive-pairs.jsonl')}
    dependencies={'proofnet-60':'Dummit_Foote_exercise_7_1_15_mul_comm',
        'proofnet-257':'Herstein_exercise_2_2_3_pow_central',
        'proofnet-185':'Artin_exercise_2_8_6_center_eq'}
    dangling=[]
    for identity,name in dependencies.items():
        context=positives[identity]['context']
        if name in context and not re.search(r'(?:lemma|theorem|def)\s+'+re.escape(name)+r'\b',context):
            dangling.append({'id':identity,'removed_helper_still_referenced':name})
    english=defaultdict(lambda:defaultdict(list))
    for split in ['train','validation']:
        for row in read(source/(split+'.jsonl')):
            if row['label']:english[row['informal_proof']][split].append(row['id'])
    duplicates=[dict(v) for v in english.values() if len(v)>1]
    result={'data_version':'argument-14b/data-v3','herald_signature_mismatch_count':len(bad),
        'herald_signature_mismatch_ids':bad,'dangling_context_examples':dangling,
        'malformed_ProofNet_target':'proofnet-289; first unbracketed := splits internal let in type',
        'exact_english_proof_cross_split_duplicates':duplicates,
        'limitation':'This reproduces specific integrity defects; it is not a full Lean elaboration or semantic audit.'}
    dest=ROOT/'reports/audit-20261109';dest.mkdir(parents=True,exist_ok=True)
    metadata(dest/'extraction-integrity.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='herald_signature_mismatch_ids'},indent=2))


if __name__=='__main__':main()
