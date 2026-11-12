"""Frozen-split lexical random-forest baseline; no LLM embeddings or test fitting."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import sklearn
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'artifacts/argument-14b/overnight-20261109/budget-data'
CORE = ROOT / 'artifacts/argument-14b/core/test.jsonl'
OUT = ROOT / 'reports/random-forest-20261110'
FIELDS = ['informal_statement', 'informal_proof', 'formal_statement', 'formal_proof']


def read(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def texts(rows, fields):
    # Hide source exercise names; IDs, labels, route metadata and context never enter features.
    return [[re.sub(r'\b(theorem|lemma)\s+[^\s(:{]+', r'\1 candidate', row[field])
             for field in fields] for row in rows]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-file', type=Path)
    parser.add_argument('--survey-file', type=Path)
    parser.add_argument('--survey-allowlist', type=Path, help='Qwen predictions: retain status=predicted IDs for matched coverage')
    parser.add_argument('--output-dir', type=Path, default=OUT)
    args = parser.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    train = read(DATA / 'train.jsonl')
    validation = read(DATA / 'validation.jsonl')
    core = read(CORE)
    result = {'seed': 883, 'sklearn': sklearn.__version__,
              'policy': 'All vocabulary/SVD/classifier fitting uses training only; fixed hyperparameters; threshold 0.5; no test tuning.',
              'limitations': 'Synthetic cross-problem labels; small unreviewed core; lexical baseline, not semantic proof verification.',
              'input_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [DATA/'train.jsonl', DATA/'validation.jsonl', CORE]}, 'models': {}}
    for name, fields in [('english_only', FIELDS[:2]), ('both_languages', FIELDS)]:
        train_text = texts(train, fields)
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 5), max_features=12000,
                                     sublinear_tf=True, min_df=2)
        fitted = vectorizer.fit_transform([s for row in train_text for s in row])
        svd = TruncatedSVD(n_components=32, random_state=883).fit(fitted)

        def features(rows):
            content = texts(rows, fields)
            matrices = [vectorizer.transform([row[i] for row in content]) for i in range(len(fields))]
            components = [svd.transform(m) for m in matrices]
            columns = components + [np.log1p(np.array([[len(t) for t in row] for row in content]))]
            for i in range(len(fields)):
                for j in range(i):
                    columns.append(np.asarray(matrices[i].multiply(matrices[j]).sum(axis=1)))
                    columns.append(np.abs(components[i] - components[j]))
                    columns.append(components[i] * components[j])
            return np.hstack(columns)

        model = RandomForestClassifier(n_estimators=400, min_samples_leaf=2,
                                       max_features='sqrt', class_weight='balanced',
                                       random_state=883, n_jobs=4)
        model.fit(features(train), [r['label'] for r in train])
        reports = {}
        for split, rows in [('validation', validation), ('same_theorem_diagnostic', core)]:
            probability = model.predict_proba(features(rows))[:, list(model.classes_).index(True)]
            prediction = probability >= 0.5
            target = [r['label'] for r in rows]
            reports[split] = {'n': len(rows), 'accuracy': accuracy_score(target, prediction),
                              'balanced_accuracy': balanced_accuracy_score(target, prediction),
                              'auroc': roc_auc_score(target, probability),
                              'classification': classification_report(target, prediction, output_dict=True, zero_division=0)}
            with (output / f'{name}-{split}.jsonl').open('w', encoding='utf-8') as handle:
                for row, score, answer in zip(rows, probability, prediction):
                    handle.write(json.dumps({'id': row['id'], 'label': row['label'],
                                             'match_score': float(score), 'prediction': bool(answer)}) + '\n')
        if args.candidate_file:
            candidates = read(args.candidate_file)
            probability = model.predict_proba(features(candidates))[:, list(model.classes_).index(True)]
            result['candidate_sha256'] = hashlib.sha256(args.candidate_file.read_bytes()).hexdigest()
            with (output / f'{name}-candidates.jsonl').open('w', encoding='utf-8') as handle:
                for row, score in zip(candidates, probability):
                    handle.write(json.dumps({'id': row['id'], 'pair_kind': row['pair_kind'],
                                             'match_score': float(score), 'prediction': bool(score >= .5)})+'\n')
            reports['candidate_survey'] = {
                kind: {'rows': sum(r['pair_kind']==kind for r in candidates),
                       'yes_count': sum(bool(p>=.5) for r,p in zip(candidates,probability) if r['pair_kind']==kind)}
                for kind in sorted({r['pair_kind'] for r in candidates})}
            reports['candidate_survey']['accuracy'] = None  # Unreviewed candidates have no binary labels.
            if name=='english_only':
                controls=sorted(float(p) for r,p in zip(candidates,probability) if r['pair_kind']=='source_positive_control')
                bundles=sorted(float(p) for r,p in zip(candidates,probability) if r['pair_kind']=='related_english_bundle_candidate')
                if len(controls)!=len(bundles) or not np.allclose(controls,bundles,atol=1e-12,rtol=0):
                    raise ValueError('English-only bundle permutation invariant violated')
                reports['candidate_survey']['english_bundle_control_scores_identical_as_multisets']=True
        if args.survey_file:
            survey = read(args.survey_file)
            result['survey_sha256'] = hashlib.sha256(args.survey_file.read_bytes()).hexdigest()
            if args.survey_allowlist:
                allowed = {r['id'] for r in read(args.survey_allowlist) if r['status']=='predicted'}
                result['survey_allowlist_sha256'] = hashlib.sha256(args.survey_allowlist.read_bytes()).hexdigest()
                survey = [r for r in survey if r['id'] in allowed]
                if {r['id'] for r in survey} != allowed: raise ValueError('Survey coverage differs from allowlist')
            counts = {'rows': len(survey), 'yes_count': 0, 'no_count': 0, 'accuracy': None}
            with (output / f'{name}-survey.jsonl').open('w', encoding='utf-8') as handle:
                for start in range(0,len(survey),128):
                    batch=survey[start:start+128]
                    scores=model.predict_proba(features(batch))[:,list(model.classes_).index(True)]
                    for row,score in zip(batch,scores):
                        answer=bool(score>=.5)
                        counts['yes_count']+=int(answer);counts['no_count']+=int(not answer)
                        handle.write(json.dumps({'id':row['id'],'match_score':float(score),'prediction':answer})+'\n')
                    if start%1024==0:
                        progress={'model':name,'completed':start+len(batch),'total':len(survey)}
                        (output/(name+'-progress.json')).write_text(json.dumps(progress)+'\n',encoding='utf-8')
                        print(json.dumps(progress),flush=True)
            reports['unlabeled_survey']=counts
        result['models'][name] = reports
    result['code_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output / 'metrics.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
