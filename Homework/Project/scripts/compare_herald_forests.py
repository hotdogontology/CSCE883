"""Compare forest/Qwen predictions on identical unlabeled Herald IDs."""
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def main():
    forest=ROOT/'artifacts/random-forest-herald-20261110'
    models={}
    for name in ['english_only','both_languages']:
        rows=read(forest/(name+'-survey.jsonl'))
        models['forest_'+name]={r['id']:r['prediction'] for r in rows}
        assert len(models['forest_'+name])==len(rows)
    for name in ['untuned','tuned']:
        rows=[r for r in read(ROOT/'artifacts/argument-14b/overnight-20261109'/
                              (name+'-herald')/'predictions.jsonl') if r['status']=='predicted']
        models['qwen_'+name]={r['id']:r['prediction'] for r in rows}
        assert len(models['qwen_'+name])==len(rows)
    ids=set(next(iter(models.values())))
    assert len(ids)==44537 and all(set(model)==ids for model in models.values())
    old=json.loads((ROOT/'reports/random-forest-20261110/metrics.json').read_text())
    metadata=json.loads((forest/'metrics.json').read_text())
    for name in old['models']:
        for split in ['validation','same_theorem_diagnostic']:
            assert old['models'][name][split]==metadata['models'][name][split]
    report={'scope':'Matched-coverage unlabeled Herald survey: no model accuracy or truth labels',
            'rows':len(ids),'excluded_to_match_qwen_context_limit':16,
            'frozen_forest_metrics_reproduced':True,'source_fingerprints':{
                key:value for key,value in metadata.items() if key.endswith('sha256')},
            'models':{},'pairwise':{}}
    for name,predictions in models.items():
        yes=sum(predictions.values())
        report['models'][name]={'yes':yes,'no':len(ids)-yes,'yes_fraction':yes/len(ids)}
    for left,right in combinations(models,2):
        cross=Counter(('YES' if models[left][id] else 'NO')+' / '+('YES' if models[right][id] else 'NO') for id in ids)
        agree=sum(models[left][id]==models[right][id] for id in ids)
        report['pairwise'][left+' vs '+right]={'agree':agree,'disagree':len(ids)-agree,
                                                'agreement_fraction':agree/len(ids),'crosstab_left_right':dict(sorted(cross.items()))}
    out=ROOT/'reports/random-forest-herald-20261110'
    out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
