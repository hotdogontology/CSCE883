"""Make a reproducible formal-proof-withheld control for the compiled core matrix."""
from two_pass import ROOT,read,write,sha,metadata
import json


def main():
    core=ROOT/'artifacts/argument-14b/core'
    rows=read(core/'test.jsonl')
    write(core/'test-formal-masked.jsonl',[dict(r,formal_proof='(Lean proof withheld for diagnostic ablation)') for r in rows])
    manifest=json.loads((core/'manifest.json').read_text(encoding='utf-8'))
    manifest['files']['test-formal-masked.jsonl']=sha((core/'test-formal-masked.jsonl').read_bytes())
    manifest['masked_diagnostic']='All other fields identical; Lean proof withheld; balanced complete matrices admit at most 50% deterministic one-side classification.'
    metadata(core/'manifest.json',manifest)
    print('Prepared formal-proof-masked diagnostic:',len(rows),'rows')


if __name__=='__main__':main()
