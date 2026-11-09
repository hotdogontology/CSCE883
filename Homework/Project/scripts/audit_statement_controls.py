"""Post-hoc CPU audit of saved statement results; no inference or threshold retuning."""
from collections import Counter,defaultdict
import json
from sklearn.metrics import accuracy_score,balanced_accuracy_score,classification_report,roc_auc_score,average_precision_score
from two_pass import ROOT,read,metadata


def main():
    out=ROOT/'artifacts/two-pass'
    train=read(out/'data/proofnet-train.jsonl');validation=read(out/'data/proofnet-validation.jsonl')
    def rule(row,absence_is_match):
        absent='noncomputable section' not in row['context']
        return absent if absence_is_match else not absent
    direction=max([True,False],key=lambda v:sum(rule(r,v)==r['label'] for r in train))
    truth=[r['label'] for r in validation];predicted=[rule(r,direction) for r in validation]
    report=classification_report(truth,predicted,labels=[False,True],target_names=['mismatch','match'],output_dict=True,zero_division=0)
    models={};groups=defaultdict(list)
    for row in validation:groups[row['group']].append(row)
    for name in ['untuned','first-pass','second-pass']:
        predictions={r['id']:r for r in read(out/(name+'-validation')/'predictions.jsonl')}
        scores=[predictions[r['id']]['yes_score_uncalibrated'] for r in validation]
        strata={}
        for suffix in ['original','corrected']:
            rows=[r for r in validation if r['id'].endswith('-'+suffix)]
            strata[suffix]={'rows':len(rows),'correct':sum(predictions[r['id']]['prediction']==r['label'] for r in rows)}
        contrast=[rows for rows in groups.values() if len(rows)==2 and {r['label'] for r in rows}=={True,False}]
        models[name]={'strata':strata,'AUROC':roc_auc_score(truth,scores),
            'mismatch_average_precision':average_precision_score([not x for x in truth],[1-x for x in scores]),
            'both_members_correct':sum(all(predictions[r['id']]['prediction']==r['label'] for r in rows) for rows in contrast),
            'contrast_pairs':len(contrast)}
    result={'interpretation':'Post-hoc audit controls. Feature selected after inspecting artifacts; rule direction fitted on training only.',
        'context_rule':{'absence_noncomputable_section_means_match':direction,
            'train_accuracy':sum(rule(r,direction)==r['label'] for r in train)/len(train),
            'validation_accuracy':accuracy_score(truth,predicted),
            'validation_balanced_accuracy':balanced_accuracy_score(truth,predicted),'report':report},
        'validation_rows':len(validation),'validation_source_groups':len(groups),
        'group_sizes':dict(Counter(len(rows) for rows in groups.values())),
        'models':models,'warning':'Observed scores remain correct; neither cue usage by the LLM nor broad generalization is established.'}
    dest=ROOT/'reports/audit-20261109';dest.mkdir(parents=True,exist_ok=True)
    metadata(dest/'statement-controls.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
