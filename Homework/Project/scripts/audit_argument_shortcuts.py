"""CPU-only diagnostic: can English-side lexical coherence solve proof swaps?"""
import json
import argparse
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report,balanced_accuracy_score
from argument_data import ROOT
from two_pass import read,metadata


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=ROOT/'artifacts/argument-14b/data-v3')
    parser.add_argument('--output',type=Path,default=ROOT/'reports/audit-20261109/english-only-shortcut.json')
    args=parser.parse_args();source=args.data_dir
    train=read(source/'train.jsonl');validation=read(source/'validation.jsonl')
    vectorizer=TfidfVectorizer(ngram_range=(1,1),stop_words='english',sublinear_tf=True)
    vectorizer.fit([r['informal_statement'] for r in train]+[r['informal_proof'] for r in train])
    def scores(rows):
        statements=vectorizer.transform([r['informal_statement'] for r in rows])
        proofs=vectorizer.transform([r['informal_proof'] for r in rows])
        return np.asarray(statements.multiply(proofs).sum(axis=1)).ravel()
    y=np.array([r['label'] for r in train]);s=scores(train)
    values=np.unique(s);thresholds=np.concatenate(([-1e-9],(values[:-1]+values[1:])/2,[1.000001]))
    # Balanced train pairs make accuracy the same as balanced accuracy.
    best=max(thresholds,key=lambda t:np.mean((s>=t)==y))
    target=np.array([r['label'] for r in validation]);prediction=scores(validation)>=best
    report=classification_report(target,prediction,labels=[False,True],target_names=['mismatch','match'],
        output_dict=True,zero_division=0)
    result={'diagnostic':'English-only TF-IDF cosine between statement and proof; no Lean fields read',
        'data_version':str(source),'threshold_selection':'maximize training accuracy only',
        'threshold':float(best),'train_accuracy':float(np.mean((s>=best)==y)),
        'validation':report,'validation_balanced_accuracy':balanced_accuracy_score(target,prediction),
        'interpretation':'Shortcut diagnostic, not a correspondence model or independently reviewed accuracy.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    metadata(args.output,result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
