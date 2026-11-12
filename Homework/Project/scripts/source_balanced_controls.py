"""Secondary shortcut diagnostics; never report these as semantic accuracy."""
import json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'artifacts/source-balanced-20261112/data'
OUT = ROOT / 'reports/source-balanced-20261112'


def main():
    rows = {s: [json.loads(x) for x in (DATA / (s + '.jsonl')).read_text(encoding='utf-8').splitlines()]
            for s in ('train', 'validation', 'test')}
    results = {}
    for mode in ('source_only', 'length_only', 'english_only', 'lean_only', 'paired_lexical'):
        def features(records):
            if mode == 'source_only': return [[r['source'] == 'faithform'] for r in records]
            if mode == 'length_only': return [[len(r['input'][k]) for k in ('english', 'lean')] for r in records]
            if mode == 'paired_lexical': return [r['input']['english'] + '\n' + r['input']['lean'] for r in records]
            return [r['input'][mode.split('_')[0]] for r in records]
        if mode in ('source_only', 'length_only'):
            model = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=883)
        else:
            model = make_pipeline(TfidfVectorizer(analyzer='char', ngram_range=(3, 5)),
                                  LogisticRegression(C=1, random_state=883))
        model.fit(features(rows['train']), [r['label'] for r in rows['train']])
        results[mode] = {}
        for split in ('validation', 'test'):
            pred = model.predict(features(rows[split]))
            results[mode][split] = {'accuracy': accuracy_score([r['label'] for r in rows[split]], pred),
                                    'n': len(pred), 'predictions': [bool(x) for x in pred]}
    report = {'purpose': 'Shortcut diagnostics, not semantic correspondence performance',
              'warning': 'Tiny provisional convenience pilot; do not tune repeatedly against test', 'results': results}
    (OUT / 'shortcut-controls.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
