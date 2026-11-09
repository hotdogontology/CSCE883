"""Class-specific metrics on frozen labeled validation pairs; no model inference."""
import csv
from pathlib import Path

from two_pass import ROOT, read, metadata


def evaluate(truth_rows, predictions):
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report
    truth={r['id']:r['label'] for r in truth_rows}
    if len(truth)!=len(truth_rows) or len({r['id'] for r in predictions})!=len(predictions):
        raise ValueError('Duplicate IDs')
    if set(truth)!={r['id'] for r in predictions}:
        raise ValueError('Prediction IDs do not match frozen validation')
    valid=[r for r in predictions if type(r.get('prediction')) is bool]
    if not valid:
        raise ValueError('No scored examples')
    y=[truth[r['id']] for r in valid];z=[r['prediction'] for r in valid]
    report=classification_report(y,z,labels=[False,True],target_names=['mismatch','match'],
        output_dict=True,zero_division=0)
    return {'accuracy':accuracy_score(y,z),'balanced_accuracy':balanced_accuracy_score(y,z),
        'coverage':len(valid)/len(truth),'scored':len(valid),'total':len(truth),
        'classes':{k:report[k] for k in ['mismatch','match']},
        'macro':report['macro avg'],'weighted':report['weighted avg'],
        'zero_denominator_policy':'report precision/recall/F1 as zero when undefined'}


def main():
    out=ROOT/'artifacts/two-pass';dest=ROOT/'reports/two-pass';dest.mkdir(parents=True,exist_ok=True)
    truth=read(out/'data/proofnet-validation.jsonl')
    results={name:evaluate(truth,read(out/(name+'-validation')/'predictions.jsonl'))
        for name in ['untuned','first-pass','second-pass']}
    metadata(dest/'classification-metrics.json',{'scope':'statement_fidelity',
        'source':'frozen ProofNet validation; not Herald or external ground truth',
        'positive_label_convention':'Both classes reported one-versus-rest; mismatch means NO.',
        'models':results})
    with (dest/'classification-metrics.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['model','class','support','precision','recall','f1',
            'accuracy','balanced_accuracy','macro_f1','coverage']);w.writeheader()
        for name,r in results.items():
            for cls,m in r['classes'].items():
                w.writerow(dict(model=name,**{'class':cls},support=m['support'],precision=m['precision'],
                    recall=m['recall'],f1=m['f1-score'],accuracy=r['accuracy'],
                    balanced_accuracy=r['balanced_accuracy'],macro_f1=r['macro']['f1-score'],coverage=r['coverage']))
    print((dest/'classification-metrics.csv').read_text())


if __name__=='__main__':main()
