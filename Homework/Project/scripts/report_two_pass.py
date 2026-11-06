"""Report available stage outputs; disagreements are not confirmed errors."""
import csv
import json
from pathlib import Path
from collections import Counter

from two_pass import ROOT, read, metadata


def report():
    out=ROOT/'artifacts/two-pass'
    stages={}
    for p in out.glob('*/run.json'):
        r=json.loads(p.read_text(encoding='utf-8'))
        stages[p.parent.name]={k:r.get(k) for k in ['status','rows','accuracy','predictions','status_counts','labeled_coverage','confusion']}
    comparison={}
    paths=[out/name/'predictions.jsonl' for name in ['untuned-herald','first-pass-herald']]
    if all(p.exists() for p in paths):
        a,b=[{r['id']:r for r in read(p)} for p in paths]
        counts=Counter()
        with (out/'herald-comparison.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f);w.writerow(['id','untuned','first_pass','comparison'])
            for identity in sorted(set(a)|set(b)):
                x,y=a.get(identity,{}).get('prediction'),b.get(identity,{}).get('prediction')
                kind='missing' if x is None or y is None else 'agree' if x==y else 'disagree'
                counts[kind]+=1;w.writerow([identity,x,y,kind])
        comparison=dict(counts)
    source=out/'data/external.jsonl'
    if source.exists():
        predictions={name:{r['id']:r for r in read(out/(name+'-external')/'predictions.jsonl')}
            for name in ['untuned','first-pass','second-pass']
            if (out/(name+'-external')/'predictions.jsonl').exists()}
        with (out/'external-comparison.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f);w.writerow(['id','untuned','first_pass','second_pass','label_status','scope_note'])
            for row in read(source):
                w.writerow([row['id'],*[predictions.get(n,{}).get(row['id'],{}).get('prediction')
                    for n in ['untuned','first-pass','second-pass']],row['label_status'],row['unit_note']])
    summary={'stages':stages,'herald_comparison':comparison,
        'interpretation':'Herald agreement/YES rates are not accuracy; external NO flags require source/context review.',
        'scope':'statement_fidelity_only'}
    metadata(out/'report.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':report()
