"""Find exact surface-signature duplicates as leads for same-theorem route pairs."""
from collections import defaultdict
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def main():
    rows=read(ROOT/'artifacts/argument-14b/data-v4/positive-pairs.jsonl')
    splits={r['id']:split for split in ['train','validation'] for r in read(
        ROOT/'artifacts/argument-14b/overnight-20261109/budget-data'/(split+'.jsonl')) if r['label']}
    groups=defaultdict(list)
    for row in rows:
        signature=re.sub(r'\b(theorem|lemma)\s+[^\s(:{]+',r'\1 candidate',row['formal_statement'])
        groups[re.sub(r'\s+',' ',signature).strip()].append(row)
    duplicates=[{'surface_signature':signature,
                 'sources':[{'id':r['id'],'group':r['group'],'split':splits.get(r['id'],'excluded_by_budget'),
                             'english_statement':r['informal_statement']} for r in members],
                 'different_english_proofs':len({r['informal_proof'] for r in members})>1,
                 'crosses_train_validation':{'train','validation'}.issubset({splits.get(r['id']) for r in members})}
                for signature,members in groups.items() if len(members)>1]
    report={'policy':'Exact whitespace/name-normalized source signature only. Not alpha/definitional equivalence; context resolution and proof-route review still required.',
            'source_rows':len(rows),'duplicate_signature_groups':len(duplicates),
            'cross_split_groups':sum(g['crosses_train_validation'] for g in duplicates),'groups':duplicates}
    out=ROOT/'reports/relatedness-20261110/same-theorem-leads.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
