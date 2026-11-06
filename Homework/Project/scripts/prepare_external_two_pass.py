"""Build an unlabeled, source-pinned statement screening pilot from inspected files."""
import hashlib
import json
from pathlib import Path
import re

from two_pass import ROOT, write, metadata


def uncomment(text):
    # Sources selected here have no nested comments in the retained context.
    return re.sub(r'/\-.*?\-/', '', text, flags=re.S)


def main():
    root=ROOT/'data/external-two-pass'
    rows=[]
    for name in ['Imo2024P1','Imo2023P1','Imo2022P2']:
        path=f'Compfiles/{name}.lean'
        text=(root/'compfiles'/path).read_text(encoding='utf-8')
        tree=json.loads((root/'compfiles/tree.json').read_text(encoding='utf-8'))
        natural=re.search(r'/\-!\s*(.*?)\-/',text,re.S).group(1).strip()
        start=text.index('\nproblem ')+1
        formal=text[start:text.index(':= by',start)].strip().replace('problem ','theorem ',1)
        solution=re.search(r'determine (\w+) : (.*?)\n\nproblem',text,re.S).group(0).split('\n\nproblem')[0]
        context=solution.replace('determine ','def ',1)
        if name=='Imo2023P1':
            context=text[text.index('abbrev ConsecutiveFactors'):text.index('snip begin')]+context
        if name=='Imo2022P2':
            context=text[text.index('abbrev PosReal'):text.index('snip begin')]+context
        rows.append({'id':name,'name':name,'informal_statement':natural,
            'formal_statement':formal,'context':'import Mathlib\nnamespace '+name+'\n'+context,
            'source_url':f'https://github.com/dwrensha/compfiles/blob/{tree["revision"]}/{path}',
            'source_revision':tree['revision'],'label_scope':'statement_fidelity',
            'label_status':'unreviewed_external_candidate','unit_note':
            'Published determine-all question versus proposed solution-set theorem; a NO can reflect question/answer scope.'})
    tree=json.loads((root/'math/tree.json').read_text(encoding='utf-8'))
    matching=(root/'math/preprints/Entropy-and-Face-Dimension-of-the-Perfect-Matching-Polytope-September-23-2026/main.txt').read_text(encoding='utf-8')
    binpacking=(root/'math/binpacking.txt').read_text(encoding='utf-8')
    cases=[('openai-binary-counting','BinaryMatching','deterministic_approximate_counting',
        matching[matching.index('For the algorithmic problem'):matching.index('The factor512')],
        'lean/OAI/Computability/MatchingCount/BinarySolve.lean',
        'Theorem 1.2; PDF text extraction loses superscript formatting: the approximation factor is 512^n.'),
        ('openai-matching-entropy','MatchingEntropy','entropy_main',
        matching[matching.index('Throughout, a graph'):matching.index('In particular,H')],
        'lean/OAI/Combinatorics/PerfectMatching/Main.lean',
        'Theorem 1.1 versus catalogued entropy_main; version/strength alignment needs review. PDF fractions may be flattened.'),
        ('openai-binpacking-results','BinPackingGap','main_results',
        binpacking[binpacking.index('An instance of bin packing'):binpacking.index('1.3 Related')]
            if '1.3 Related' in binpacking else binpacking[:6500],
        'lean/OAI/Computability/BinPacking/Main.lean',
        'Results section versus aggregate main_results; formal theorem includes additional guarantees and construction details.')]
    for identity, comparator, declaration, english, source, note in cases:
        text=(root/'math'/source).read_text(encoding='utf-8')
        start=text.rindex('theorem '+declaration)
        end=text.index(':=',start)
        formal=text[start:end].strip()
        # Comparator definitions provide compact context only, never its admitted theorem body.
        context=(root/f'math/lean/ComparatorChallenges/{comparator}.lean').read_text(encoding='utf-8')
        context=uncomment(context[:context.index('theorem '+declaration)])
        rows.append({'id':identity,'name':identity,'informal_statement':english,
            'formal_statement':formal,'context':context,
            'source_url':f'https://github.com/openai/math/blob/{tree["revision"]}/{source}',
            'source_revision':tree['revision'],'label_scope':'statement_fidelity',
            'label_status':'unreviewed_external_candidate','unit_note':note,
            'lean_verification':'not_run'})
    write(ROOT/'artifacts/two-pass/data/external.jsonl',rows)
    metadata(ROOT/'external-two-pass-manifest.json',{'purpose':'qualitative statement screening, not labeled accuracy test',
        'pretraining_overlap':'unknown','herald_contest_exclusion':'name/import heuristic only',
        'cases':[{k:r[k] for k in ['id','source_url','source_revision','unit_note']} for r in rows],
        'local_sources':[{ 'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in root.rglob('*') if p.is_file() and p.name!='tree.json'],
        'independent_semantic_review':False,'lean_replay':False})
    print('Prepared',len(rows),'unlabeled external cases')


if __name__=='__main__':main()
