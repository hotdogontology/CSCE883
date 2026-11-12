"""Rank within-split related proofs; create unlabeled balanced donor permutations."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import random

import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer

from argument_data import payload
from argument_model import tokens

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts/relatedness-20261110'
DATA = ROOT/'artifacts/argument-14b/overnight-20261109/budget-data'


def read(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def write(path, rows):
    with path.open('w',encoding='utf-8') as handle:
        for row in rows:handle.write(json.dumps(row,ensure_ascii=False)+'\n')


def normalize(row, field):
    return re.sub(r'\b(theorem|lemma)\s+[^\s(:{]+',r'\1 candidate',row[field])


def original_donors(rows):
    """Reconstruct the original seeded permutation without ambiguous text lookup."""
    order=list(rows);random.Random(883).shuffle(order)
    for shift in range(1,len(order)):
        donors={r['id']:order[(i+shift)%len(order)] for i,r in enumerate(order)}
        if all(r['group']!=donors[r['id']]['group'] and
               r['informal_proof']!=donors[r['id']]['informal_proof'] for r in order):
            return donors
    raise ValueError('Cannot reconstruct original donor permutation')


def graph_tokens(dependency, role, modules=False):
    if not dependency or dependency['status']!='compiled':return []
    values = dependency['dependencies'][role]['constants']
    if modules:
        return sorted({'.'.join(c['module'].split('.')[:3]) for c in values
                       if c['module'].startswith('Mathlib.') and not c['module'].startswith('Mathlib.Tactic.')})
    return sorted({c['name'] for c in values if c['module'].startswith('Mathlib.')})


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    deps = {r['id']:r for r in read(OUT/'dependencies.jsonl')}
    def eligible(row):
        dep=deps.get(row['id'],{})
        return dep.get('status')=='compiled' and all(dep['dependencies'][role]['complete'] for role in ['statement','proof'])
    splits = {name:[r for r in read(DATA/(name+'.jsonl')) if r['label'] and eligible(r)]
              for name in ['train','validation']}
    train=splits['train']
    vectorizers={}
    for field in ['informal_statement','formal_statement']:
        vectorizers[field]=TfidfVectorizer(analyzer='char',ngram_range=(3,5),max_features=20000,
                                          sublinear_tf=True).fit([normalize(r,field) for r in train])
    module_vectorizer=TfidfVectorizer(analyzer=lambda x:x,lowercase=False)
    module_vectorizer.fit([graph_tokens(deps.get(r['id']),'proof',True) for r in train])
    tokenizer=AutoTokenizer.from_pretrained(ROOT/'data/models/Qwen3-14B',local_files_only=True)
    summary={'scope':'UNLABELED hard-swap candidate mining; not trusted negatives or model accuracy',
             'ranking':'0.45 English statement char cosine +0.45 formal statement char cosine +0.10 proof-module cosine; heuristic, not calibrated relatedness',
             'fit_policy':'Training-only vocabularies/IDF; within-existing-split donors; no core inputs',
             'dependency_status':dict(Counter(r['status'] for r in deps.values())),
             'candidate_gate':'Successful Lean4.28 replay and complete local-helper dependency expansion required for both sources',
             'dependencies_sha256':hashlib.sha256((OUT/'dependencies.jsonl').read_bytes()).hexdigest(),
             'inputs_sha256':{name:hashlib.sha256((DATA/(name+'.jsonl')).read_bytes()).hexdigest() for name in splits},
             'splits':{}}
    neighbors=[]
    for split,rows in splits.items():
        matrices={field:vectorizers[field].transform([normalize(r,field) for r in rows]) for field in vectorizers}
        components={field:(m@m.T).toarray() for field,m in matrices.items()}
        m=module_vectorizer.transform([graph_tokens(deps.get(r['id']),'proof',True) for r in rows])
        components['proof_module']=(m@m.T).toarray()
        scores=.45*components['informal_statement']+.45*components['formal_statement']+.10*components['proof_module']
        allowed=np.array([[a['group']!=b['group'] and a['informal_proof']!=b['informal_proof']
                           for b in rows] for a in rows])
        def detail(i,j):
            return {'anchor':rows[i]['id'],'donor':rows[j]['id'],'split':split,
                    'heuristic_score':float(scores[i,j]),
                    'components':{k:float(v[i,j]) for k,v in components.items()},
                    'both_compiled':all(deps.get(rows[k]['id'],{}).get('status')=='compiled' for k in [i,j])}
        for i in range(len(rows)):
            js=[int(j) for j in np.argsort(-scores[i]) if allowed[i,j]][:5]
            neighbors.extend([dict(detail(i,j),rank=rank+1) for rank,j in enumerate(js)])
        # Maximize relatedness while using every proof exactly once as a donor.
        # Reject any over-budget selected edge and solve again, without truncation.
        rounds=0
        while True:
            indices,donors=linear_sum_assignment(np.where(allowed,-scores,1e6))
            if not all(allowed[i,j] for i,j in zip(indices,donors)):raise ValueError('No complete safe donor permutation')
            too_long=[]
            for i,j in zip(indices,donors):
                candidate=dict(rows[i],informal_proof=rows[j]['informal_proof'])
                bundle=dict(candidate,informal_statement=rows[j]['informal_statement'])
                if max(len(tokens(tokenizer,candidate)),len(tokens(tokenizer,bundle)))>4096:too_long.append((i,j))
            if not too_long:break
            for i,j in too_long:allowed[i,j]=False
            rounds+=1
            if rounds>len(rows)**2:raise ValueError('Token filtering failed to converge')
        candidates=[];assignment=[]
        for i,j in zip(indices,donors):
            original={**payload(rows[i]),'id':rows[i]['id']+'-related-control','group':rows[i]['group'],
                      'split':split,'pair_kind':'source_positive_control','label_status':'user_assumed_source_match'}
            candidate={**payload(rows[i]),'informal_proof':rows[j]['informal_proof'],
                       'id':rows[i]['id']+'-related-candidate','group':rows[i]['group'],'split':split,
                       'pair_kind':'related_swap_candidate','donor_id':rows[j]['id'],
                       'donor_group':rows[j]['group'],'label_status':'UNREVIEWED_NO_BINARY_LABEL'}
            bundle={**candidate,'informal_statement':rows[j]['informal_statement'],
                    'id':rows[i]['id']+'-related-bundle','pair_kind':'related_english_bundle_candidate'}
            candidates.extend([original,candidate,bundle]);assignment.append(detail(i,j))
        assert Counter(r['informal_proof'] for r in candidates if r['pair_kind']=='source_positive_control') == Counter(
            r['informal_proof'] for r in candidates if r['pair_kind']=='related_swap_candidate')
        assert Counter((r['informal_statement'],r['informal_proof']) for r in candidates if r['pair_kind']=='source_positive_control') == Counter(
            (r['informal_statement'],r['informal_proof']) for r in candidates if r['pair_kind']=='related_english_bundle_candidate')
        write(OUT/(split+'-candidates.jsonl'),candidates)
        write(OUT/(split+'-assignment.jsonl'),assignment)
        if split=='validation':
            report=ROOT/'reports/relatedness-20261110'
            report.mkdir(parents=True,exist_ok=True)
            ranked=sorted(assignment,key=lambda r:-r['heuristic_score'])
            selected=[ranked[i] for i in sorted(set(np.linspace(0,len(ranked)-1,6,dtype=int).tolist()))]
            lookup_rows={r['id']:r for r in rows}
            lines=['# Related-proof candidate review index', '',
                   'Six examples spanning the heuristic ranking. These are unreviewed candidates,',
                   'not asserted mismatches. Full paired payloads are in the ignored artifact',
                   '`artifacts/relatedness-20261110/validation-candidates.jsonl`. No model',
                   'predictions or labels were used to select this index.', '']
            for entry in selected:
                anchor=lookup_rows[entry['anchor']];donor=lookup_rows[entry['donor']]
                lines += ['## '+entry['anchor']+' / '+entry['donor'], '',
                          'Heuristic relatedness: '+str(round(entry['heuristic_score'],4))+'.', '',
                          '**Anchor English statement:** '+anchor['informal_statement'], '',
                          '**Donor English statement:** '+donor['informal_statement'], '',
                          '**Anchor English proof:** '+anchor['informal_proof'], '',
                          '**Donor English proof:** '+donor['informal_proof'], '',
                          '**Anchor Lean statement:**', '', '```lean',anchor['formal_statement'],'```','',
                          '**Donor Lean statement:**', '', '```lean',donor['formal_statement'],'```','']
            (report/'candidate-review.md').write_text('\n'.join(lines),encoding='utf-8')
        random_rows=read(DATA/(split+'.jsonl'))
        anchors={r['id']:i for i,r in enumerate(rows)}
        old_donors=original_donors([r for r in random_rows if r['label']])
        assert all(r['informal_proof']==old_donors[r['id'].removesuffix('-swapped')]['informal_proof']
                   for r in random_rows if not r['label'])
        old_scores=[scores[anchors[id],anchors[donor['id']]] for id,donor in old_donors.items()
                    if id in anchors and donor['id'] in anchors]
        summary['splits'][split]={'sources':len(rows),'candidate_rows':len(candidates),
                                  'token_reassignment_rounds':rounds,
                                  'all_prompts_within_4096':True,'exact_english_proof_marginals':True,
                                  'exact_english_bundle_marginals':True,
                                  'random_comparable_pairs':len(old_scores),
                                  'mean_random_relatedness':float(np.mean(old_scores)),
                                  'mean_mined_relatedness':float(np.mean([r['heuristic_score'] for r in assignment]))}
        print(split,summary['splits'][split],flush=True)
    write(OUT/'nearest-neighbors.jsonl',neighbors)
    # Persist a compact typed graph for inspection, preserving role-specific edges.
    nodes=[];edges=[];modules=set();constants={}
    for id,record in deps.items():
        if record['status']!='compiled':continue
        nodes.append({'id':id,'kind':'proofnet_proof'})
        for role in ['statement','proof']:
            for c in record['dependencies'][role]['constants']:
                key='constant:'+c['name'];module=c['module']
                if module=='LOCAL':key=id+':'+key
                constants[key]={'id':key,'kind':'declaration','name':c['name'],'module':module}
                edges.append({'from':id,'to':key,'kind':role+'_uses'})
                if module!='LOCAL':modules.add(module)
    for key,node in constants.items():
        if node['module']!='LOCAL':edges.append({'from':key,'to':'module:'+node['module'],'kind':'defined_in'})
    # Mathlib's file hierarchy is a subject hint; imports are a separate edge type.
    subjects=set()
    for module in sorted(list(modules)):
        if not module.startswith('Mathlib.'):continue
        subject='.'.join(module.split('.')[:2]);subjects.add(subject)
        edges.append({'from':'module:'+module,'to':'subject:'+subject,'kind':'in_subject_directory'})
        source=ROOT/'data/lean428/mathlib'/Path(*module.split('.')).with_suffix('.lean')
        if source.exists():
            for imported in re.findall(r'(?m)^\s*(?:public\s+)?import\s+(Mathlib\.[\w.]+)',source.read_text(encoding='utf-8')):
                modules.add(imported)
                edges.append({'from':'module:'+module,'to':'module:'+imported,'kind':'imports'})
    nodes.extend(constants.values());nodes.extend({'id':'module:'+m,'kind':'module'} for m in sorted(modules))
    nodes.extend({'id':'subject:'+s,'kind':'subject_directory'} for s in sorted(subjects))
    write(OUT/'ontology-nodes.jsonl',nodes);write(OUT/'ontology-edges.jsonl',edges)
    summary['graph']={'nodes':len(nodes),'edges':len(edges),'scope':'resolved constants/modules referenced by successful source replays plus direct imports and subject directories; not all mathlib'}
    (OUT/'mining-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
