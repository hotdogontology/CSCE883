"""Extract proof-body inputs, preserving assumed versus constructed label provenance."""
import json
import random
import re
import zipfile
from pathlib import Path

from two_pass import ROOT, sha, read, write, metadata, statement

SEED=883
FIELDS=('informal_statement','informal_proof','formal_statement','formal_proof','context')
COMMAND=re.compile(r'(?m)^(?:(?:private|protected|noncomputable|unsafe|local)\s+)*'
    r'(?:import|export|theorem|lemma|def|abbrev|instance|example|axiom|namespace|section|end|open|variable|universe|'
    r'set_option|attribute|notation|infix|prefix|postfix|macro|syntax|inductive|structure)\b')


def strip_comments(text):
    """Lean nested block/line comments removed; string contents preserved."""
    out=[];i=0;depth=0;string=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i):depth+=1;i+=2
            elif text.startswith('-/',i):depth-=1;i+=2
            else:
                if text[i]=='\n':out.append('\n')
                i+=1
        elif string:
            out.append(text[i])
            if text[i]=='\\' and i+1<len(text):out.append(text[i+1]);i+=2;continue
            if text[i]=='"':string=False
            i+=1
        elif text.startswith('/-',i):out.append(' ');depth=1;i+=2
        elif text.startswith('--',i):
            end=text.find('\n',i);i=len(text) if end<0 else end
        else:
            if text[i]=='"':string=True
            out.append(text[i]);i+=1
    if depth:raise ValueError('Unclosed block comment')
    return '\n'.join(line.rstrip() for line in ''.join(out).splitlines()).strip()


def assignment(text):
    """Find declaration's outer proof assignment rather than a binder's default."""
    level=0;string=False;i=0
    while i<len(text)-1:
        ch=text[i]
        if string:
            if ch=='\\':i+=2;continue
            if ch=='"':string=False
        elif ch=='"':string=True
        elif ch in '([{':level+=1
        elif ch in ')]}':level-=1
        elif level==0 and text[i:i+2]==':=':return i
        i+=1
    raise ValueError('No outer proof assignment')


def extract(text,name):
    code=strip_comments(text)
    spans=list(COMMAND.finditer(code))
    chunks=[code[m.start():spans[i+1].start() if i+1<len(spans) else len(code)].strip()
        for i,m in enumerate(spans)]
    candidates=[]
    for i,chunk in enumerate(chunks):
        match=re.match(r'(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma)\s+([^\s(:{]+)',chunk)
        decl=match[1].removeprefix('_root_.') if match else ''
        if decl in [name,name+'_corrected']:
            candidates.append((i,decl))
    corrected=[x for x in candidates if x[1]==name+'_corrected']
    if len(corrected)==1:idx,target=corrected[0]
    elif len(candidates)==1:idx,target=candidates[0]
    else:raise ValueError('Cannot identify a unique corrected target')
    target_code=chunks[idx];split=assignment(target_code)
    body=target_code[split+2:].strip()
    if re.search(r'\b(?:sorry|admit|axiom)\b',body):raise ValueError('Target contains an admission')
    # Omit obsolete target declarations and all explicit refutation declarations.
    context=[];omitted=[]
    for chunk in chunks[:idx]:
        match=re.match(r'(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma|axiom)\s+([^\s(:{]+)',chunk)
        decl=match[1].removeprefix('_root_.') if match else ''
        if decl in [name,name+'_corrected'] or decl.startswith(name+'_'):
            omitted.append(decl);continue
        if re.search(r'\b(?:sorry|admit|axiom)\b',chunk):
            # A missing helper can hide essential reasoning. Exclude rather than
            # pass an admitted helper to the correspondence model.
            raise ValueError('Context contains an admitted declaration')
        context.append(chunk)
    if any(re.search(r'(?<![\w.])'+re.escape(n)+r'(?![\w.])',body) for n in omitted):
        raise ValueError('Target depends on omitted original/refutation')
    return {'formal_statement':target_code[:split].strip(),'formal_proof':body,
        'context':'\n\n'.join(context),'extracted_declaration':target}


def payload(row):
    for key in FIELDS:
        if not isinstance(row.get(key),str) or (key!='context' and not row[key].strip()):
            raise ValueError('Missing argument evidence: '+key)
    return {key:row[key] for key in FIELDS}


def swapped_negatives(rows,split):
    """Donor proofs remain within split; anchor statements and Lean code unchanged."""
    if len(rows)<2:raise ValueError('Need two distinct proof pairs per split')
    order=list(rows);random.Random(SEED).shuffle(order)
    for shift in range(1,len(order)):
        donors={r['id']:order[(i+shift)%len(order)] for i,r in enumerate(order)}
        if all(r['group']!=donors[r['id']]['group'] and r['informal_proof']!=donors[r['id']]['informal_proof'] for r in order):break
    else:raise ValueError('Cannot construct a proof derangement without identical proofs')
    result=[]
    for i,row in enumerate(rows):
        donor=donors[row['id']]
        negative=dict(row,id=row['id']+'-swapped',informal_proof=donor['informal_proof'],label=False,
            label_source='constructed_cross_problem_english_proof_swap',donor_group=donor['group'],
            label_assumption='Unrelated source proof does not implement the anchor argument; not human reviewed.')
        result.extend([dict(row,split=split),dict(negative,split=split)])
    return result


def paired_too_long(rows,lengths,budget):
    """Both variants retained or skipped; single unlabeled Herald items stand alone."""
    return {r['group'] for r,n in zip(rows,lengths) if n>budget and 'group' in r}


def prepare(destination):
    import pandas as pd
    destination.mkdir(parents=True,exist_ok=False)
    sources=json.loads((ROOT/'verified-data-manifest.json').read_text(encoding='utf-8'))['sources']
    source=next(s for s in sources if s['name']=='proofnet-verified')
    root=ROOT/source['local_directory']/'source'
    rows=read(root/'data/archive/proofnet-verified-4.28.jsonl')
    archive=root/'data/archive/proofnet-verified_gt-4.28.zip'
    positive=[];excluded=[]
    with zipfile.ZipFile(archive) as proofs:
        for row in rows:
            member=f'proofnet_verified_gt/proofnet-{row["index"]}.lean'
            text=proofs.read(member).decode('utf-8')
            try:
                formal=extract(text,row['name'])
                record=dict(formal,id=f'proofnet-{row["index"]}',group=f'proofnet-{row["index"]}',
                    informal_statement=row['informal_stmt'],informal_proof=row['informal_proof'],
                    name=row['name'],label=True,label_scope='argument_fidelity',
                    label_source='user_assumed_corrected_ProofNet_argument_correspondence',
                    label_assumption='Positive argument correspondence is assumed by user; not independently audited.',
                    source_revision=source['revision'],archive_member=member,
                    source_file_sha256=sha(text.encode()),lean_replay='not_run')
                payload(record)
                positive.append(record)
            except ValueError as exc:
                excluded.append({'id':row['index'],'reason':str(exc)})
    random.Random(SEED).shuffle(positive)
    n=max(2,len(positive)//5);validation=positive[:n];train=positive[n:]
    write(destination/'train.jsonl',swapped_negatives(train,'train'))
    write(destination/'validation.jsonl',swapped_negatives(validation,'validation'))
    write(destination/'positive-pairs.jsonl',positive)
    write(destination/'excluded.jsonl',excluded)
    herald=[]
    frame=pd.read_parquet(ROOT/'data/herald/data/train-00000-of-00001.parquet')
    for row in frame.to_dict('records'):
        code=strip_comments(row['formal_proof'])
        try:
            pos=assignment(code)
            record={'id':f'herald-{row["id"]}','name':row['name'],
                'informal_statement':row['informal_theorem'],'informal_proof':row['informal_proof'],
                'formal_statement':code[:pos].strip(),'formal_proof':code[pos+2:].strip(),
                'context':strip_comments(row['header']),'label_scope':'argument_fidelity',
                'label_source':None,'source_revision':'2d31b459df74d730bff85682de237d894b4eecfa'}
            payload(record);herald.append(record)
        except ValueError as exc:
            herald.append({'id':f'herald-{row["id"]}','name':row['name'],'extraction_error':str(exc)})
    write(destination/'herald.jsonl',herald)
    metadata(destination/'manifest.json',{'scope':'argument_fidelity','seed':SEED,
        'positive_label_policy':'User explicitly assumes corrected ProofNet proof-pair argument correspondence.',
        'negative_label_policy':'Constructed cross-problem English proof swaps; anchor statement pair unchanged.',
        'limitation':'Easy proof mismatches; does not measure subtle same-theorem alternate-argument discrimination.',
        'source_revision':source['revision'],'archive_sha256':sha(archive.read_bytes()),
        'positive_pairs':len(positive),'excluded':excluded,'train_pairs':2*len(train),
        'validation_pairs':2*len(validation),'split_policy':'Original problems split before negatives; donors within split',
        'herald_rows':len(herald),'lean_replay':'not_run','files':
            {p.name:sha(p.read_bytes()) for p in destination.glob('*.jsonl')}})
    print(json.dumps({'positive_pairs':len(positive),'excluded':len(excluded),
        'train':2*len(train),'validation':2*len(validation),'herald':len(herald)}),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    prepare(parser.parse_args().output)
