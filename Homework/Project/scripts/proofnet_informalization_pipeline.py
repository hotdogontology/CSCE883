"""Fresh ProofNet-supervised informalizer, unchanged English judge, held-out tests."""
import argparse
import gc
import json
from pathlib import Path
import informalization_pipeline as pipeline
from two_pass import ROOT, read, write, metadata

OUT=ROOT/'artifacts/informalization-proofnet-14b-20261113'
REPORT=ROOT/'reports'/OUT.name
SPLITS=ROOT/'artifacts/hard-related-20261110/data'

def prepare():
    from transformers import AutoTokenizer
    source=ROOT/'artifacts/argument-14b/data-v4/positive-pairs.jsonl'
    originals=read(source)
    allocation={r['id']:r for r in read(SPLITS/'split-allocation.jsonl')}
    tok=AutoTokenizer.from_pretrained(ROOT/json.loads(pipeline.MANIFEST.read_text())['local_directory'],local_files_only=True)
    dest=OUT/'data';dest.mkdir(parents=True,exist_ok=False)
    pools={'train':[],'validation':[]};excluded=[]
    for r in originals:
        a=allocation.get(r['id'])
        if a is None: raise ValueError('Missing family allocation '+r['id'])
        if a['split']=='test':continue
        p,t=pipeline.encode(tok,r)
        reason='total_over_2048' if len(p)+len(t)>2048 else 'target_over_1024' if len(t)>1024 else None
        if reason:
            excluded.append({'id':r['id'],'split':a['split'],'reason':reason});continue
        pools[a['split']].append({**r,'split':a['split'],'group':a['group']})
    test=read(SPLITS/'test.jsonl')
    for r in test:
        assert allocation[r['source_id']]['split']=='test'
        if len(pipeline.prefix(tok,pipeline.TRANSLATE,pipeline.lean_input(r)))>8192:
            raise ValueError('Test input too long; no truncation')
    # Check paired source texts across train/validation/test as well as family IDs.
    groups=[{r['group'] for r in rows} for rows in [pools['train'],pools['validation'],test]]
    for i in range(3):
        for j in range(i):assert not groups[i]&groups[j]
    for field in ['formal_proof','informal_proof']:
        sets=[{pipeline.norm(r[field]) for r in rows} for rows in [pools['train'],pools['validation'],test]]
        for i in range(3):
            for j in range(i):assert not sets[i]&sets[j],('duplicate',field)
    for split,rows in {**pools,'test':test}.items():write(dest/(split+'.jsonl'),rows)
    write(dest/'excluded.jsonl',excluded)
    spec={'source':str(source.relative_to(ROOT)),'source_sha256':pipeline.digest(source.read_bytes()),
          'allocation_sha256':pipeline.digest((SPLITS/'split-allocation.jsonl').read_bytes()),
          'counts':{**{s:len(v) for s,v in pools.items()},'test':len(test)},
          'excluded':len(excluded),'files':{p.name:pipeline.digest(p.read_bytes()) for p in dest.glob('*.jsonl')},
          'supervision':'Original corrected ProofNet English proofs paired with existing Lean proof bodies; no swapped negatives in translation training.',
          'label_policy':'Original argument correspondence assumed per project policy; related-swap test negatives are synthetic.',
          'split_policy':'Reuse frozen related-proof family allocation (70/15/15 before filtering); all eligible original training pairs, not only swap-selected anchors.',
          'settings':'Fresh base Qwen3-14B, BF16 rank16 LoRA, one epoch lr1e-4 accumulation8; total2048/target1024, no truncation; original base English judge.',
          'limitation':'Training set size differs from Herald; dataset-only causal comparison is not claimed. Test corpus has been examined in previous experiments.'}
    metadata(dest/'manifest.json',spec);REPORT.mkdir(parents=True,exist_ok=True)
    metadata(REPORT/'data-manifest.json',spec)
    print(json.dumps(spec['counts']),flush=True)

def run():
    pipeline.OUT=OUT
    pipeline.run()
    truth={r['id']:r for r in read(OUT/'data/test.jsonl')}
    generations={r['id']:r for r in read(OUT/'generated.jsonl')}
    scored=[];abstentions=[]
    for r in read(OUT/'judgments.jsonl'):
        if r['match'] is None or generations[r['id']]['hit_generation_limit']:
            abstentions.append(r['id']);continue
        scored.append((truth[r['id']]['label'],r['match']))
    tp=sum(not t and not p for t,p in scored);fn=sum(not t and p for t,p in scored)
    fp=sum(t and not p for t,p in scored);tn=sum(t and p for t,p in scored)
    precision=tp/(tp+fp) if tp+fp else 0;recall=tp/(tp+fn) if tp+fn else 0
    metrics={'scored':len(scored),'total':len(truth),'abstentions':abstentions,
             'accuracy':(tp+tn)/len(scored) if scored else None,
             'mismatch_precision':precision,'mismatch_recall':recall,
             'mismatch_f1':2*precision*recall/(precision+recall) if precision+recall else 0,
             'confusion_matrix_rows_truth_columns_predicted_mismatch_match':[[tp,fn],[fp,tn]],
             'scope':'Conditional on completed nontruncated generation and judgment; assumed positive and synthetic negative labels.'}
    metadata(OUT/'classification-metrics.json',metrics);metadata(REPORT/'classification-metrics.json',metrics)
    for name in ['job.json','validation-loss.json','judgments.jsonl']:
        (REPORT/name).write_bytes((OUT/name).read_bytes())
    print(json.dumps(metrics),flush=True)
    # Repeat the two external cases using the newly trained adapter, retaining the Herald run.
    import torch
    gc.collect();torch.cuda.empty_cache()
    import openai_informalization_cases as external
    external.OUT=ROOT/'artifacts/openai-proofnet-informalization-20261113'
    external.ADAPTER=OUT/'adapter'
    external.prepare();external.run()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','run']);a=p.parse_args()
    prepare() if a.command=='prepare' else run()
