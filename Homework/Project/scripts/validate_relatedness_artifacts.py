"""Verify generated graph references, split isolation and exact swap provenance."""
from collections import Counter
import json
from pathlib import Path

from argument_data import payload

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/relatedness-20261110'
DATA=ROOT/'artifacts/argument-14b/overnight-20261109/budget-data'


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def main():
    source={name:{r['id']:r for r in read(DATA/(name+'.jsonl')) if r['label']}
            for name in ['train','validation']}
    assert not {r['group'] for r in source['train'].values()} & {r['group'] for r in source['validation'].values()}
    dependency={r['id']:r for r in read(OUT/'dependencies.jsonl')}
    for split in source:
        rows=read(OUT/(split+'-candidates.jsonl'))
        assert len({r['id'] for r in rows})==len(rows)
        controls=[r for r in rows if r['pair_kind']=='source_positive_control']
        swaps=[r for r in rows if r['pair_kind']=='related_swap_candidate']
        bundles=[r for r in rows if r['pair_kind']=='related_english_bundle_candidate']
        assert len(controls)==len(swaps)==len(bundles)
        assert Counter(r['informal_proof'] for r in controls)==Counter(r['informal_proof'] for r in swaps)
        assert Counter((r['informal_statement'],r['informal_proof']) for r in controls)==Counter(
            (r['informal_statement'],r['informal_proof']) for r in bundles)
        for row in rows:
            assert 'label' not in row
            assert row['split']==split
            anchor_id=row['id'].split('-related-')[0]
            anchor=source[split][anchor_id]
            assert dependency[anchor_id]['status']=='compiled'
            if row['pair_kind']=='source_positive_control':
                assert payload(row)==payload(anchor)
                continue
            donor=source[split][row['donor_id']]
            assert dependency[donor['id']]['status']=='compiled'
            assert anchor['group']!=donor['group']
            assert anchor['informal_proof']!=donor['informal_proof']
            expected=dict(payload(anchor),informal_proof=donor['informal_proof'])
            if row['pair_kind']=='related_english_bundle_candidate':
                expected['informal_statement']=donor['informal_statement']
            assert payload(row)==expected
        print(split,':',len(rows),'unlabeled rows; exact provenance and marginals pass')
    nodes=read(OUT/'ontology-nodes.jsonl');edges=read(OUT/'ontology-edges.jsonl')
    identifiers={r['id'] for r in nodes}
    assert len(identifiers)==len(nodes)
    assert all(e['from'] in identifiers and e['to'] in identifiers for e in edges)
    print('Graph:',len(nodes),'unique nodes,',len(edges),'valid typed edges')


if __name__=='__main__':main()
