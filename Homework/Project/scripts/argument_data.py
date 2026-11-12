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


def assignment_candidates(text):
    """Lexically outer assignments; type-level lets require a trusted signature."""
    level=0;string=False;i=0;result=[]
    while i<len(text)-1:
        ch=text[i]
        if string:
            if ch=='\\':i+=2;continue
            if ch=='"':string=False
        elif ch=='"':string=True
        elif ch in '([{':level+=1
        elif ch in ')]}':level-=1
        elif level==0 and text[i:i+2]==':=':result.append(i)
        i+=1
    return result


def canonical_signature(text):
    text=strip_comments(text)
    declaration=re.search(r'(?m)^(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma|instance)\s+',text)
    if declaration:text=text[declaration.start():]
    text=re.sub(r'^(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma|instance)\s+[^\s(:{]+',
        'DECL',text)
    return re.sub(r'\s+','',text)


def trusted_signature(template):
    """Dataset templates carry the entire type, including unbracketed lets."""
    clean=strip_comments(template)
    trimmed=re.sub(r'\s*:=\s*(?:by\s+)?sorry\s*$', '',clean)
    if trimmed!=clean:return trimmed.strip()
    # Archived row 35 has a completed by-proof instead of a template. Its outer
    # by assignment is explicit; reject ambiguous other non-template formats.
    candidates=[p for p in assignment_candidates(clean) if re.match(r'\s*by\b',clean[p+2:])]
    if candidates:return clean[:candidates[0]].strip()
    raise ValueError('Trusted metadata has no proof template/by-proof boundary')


def assignment(text,expected_signature=None):
    candidates=assignment_candidates(text)
    if expected_signature is not None:
        expected=canonical_signature(expected_signature)
        matches=[p for p in candidates if canonical_signature(text[:p])==expected]
        if len(matches)!=1:raise ValueError('Source declaration does not uniquely match trusted signature')
        return matches[0]
    if candidates:return candidates[0]
    raise ValueError('No outer proof assignment')


def declaration_name(chunk):
    match=re.match(r'(?:(?:private|protected|noncomputable|unsafe|local)\s+)*'
        r'(?:theorem|lemma|axiom|def|abbrev|instance)\s+([^\s(:{]+)',chunk)
    return match[1].removeprefix('_root_.') if match else ''


def extract(text,name,expected_signature=None):
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
    target_code=chunks[idx];split=assignment(target_code,expected_signature)
    body=target_code[split+2:].strip()
    if re.search(r'\b(?:sorry|admit|axiom)\b',body):raise ValueError('Target contains an admission')
    # Omit obsolete target declarations and all explicit refutation declarations.
    context=[];omitted=[]
    for chunk in chunks[:idx]:
        decl=declaration_name(chunk)
        # Prefix alone does not denote a refutation: genuine helpers such as
        # *_mul_comm and *_center_eq must remain. Omit exact obsolete targets
        # regardless of declaration kind, and explicit refutation certificates.
        if decl in [name,name+'_corrected',name+'_neg',name+'_trivial']:
            omitted.append(decl);continue
        if re.search(r'\b(?:sorry|admit|axiom)\b',chunk):
            # A missing helper can hide essential reasoning. Exclude rather than
            # pass an admitted helper to the correspondence model.
            raise ValueError('Context contains an admitted declaration')
        context.append(chunk)
    retained='\n\n'.join(context)+'\n'+body
    if any(re.search(r'(?<!\w)'+re.escape(n)+r'(?!\w)',retained) for n in omitted):
        raise ValueError('Target/context depends on omitted original/refutation')
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


def family_groups(rows):
    """Union exercise parts and shared English proof texts before any split."""
    parent={r['id']:r['id'] for r in rows}
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):
        x,y=find(a),find(b)
        if x!=y:parent[max(x,y)]=min(x,y)
    families={};proofs={}
    for r in rows:
        key=re.sub(r'(?<=\d)_?[a-z]+$','',r['name'])
        proof=re.sub(r'\s+',' ',r['informal_proof']).strip()
        for index,value in [(families,key),(proofs,proof)]:
            if value in index:union(r['id'],index[value])
            else:index[value]=r['id']
    for r in rows:r['group']=find(r['id'])
    return rows


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
                formal=extract(text,row['name'],trusted_signature(row['formal_stmt']))
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
    family_groups(positive)
    groups=sorted({r['group'] for r in positive});random.Random(SEED).shuffle(groups)
    heldout=set(groups[:max(2,len(groups)//5)])
    validation=[r for r in positive if r['group'] in heldout]
    train=[r for r in positive if r['group'] not in heldout]
    write(destination/'train.jsonl',swapped_negatives(train,'train'))
    write(destination/'validation.jsonl',swapped_negatives(validation,'validation'))
    write(destination/'positive-pairs.jsonl',positive)
    write(destination/'excluded.jsonl',excluded)
    herald=[]
    frame=pd.read_parquet(ROOT/'data/herald/data/train-00000-of-00001.parquet')
    for row in frame.to_dict('records'):
        code=strip_comments(row['formal_proof'])
        try:
            pos=assignment(code,trusted_signature(row['formal_theorem']))
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
        'validation_pairs':2*len(validation),'split_policy':'Exercise families/shared English proofs grouped before split; donors within split',
        'herald_rows':len(herald),'lean_replay':'not_run','files':
            {p.name:sha(p.read_bytes()) for p in destination.glob('*.jsonl')}})
    train_proofs={re.sub(r'\s+',' ',r['informal_proof']).strip() for r in train}
    validation_proofs={re.sub(r'\s+',' ',r['informal_proof']).strip() for r in validation}
    overlap=train_proofs & validation_proofs
    extraction_errors=[r['id'] for r in herald if 'extraction_error' in r]
    mismatches=[]
    for raw,prepared in zip(frame.to_dict('records'),herald):
        if 'extraction_error' not in prepared and canonical_signature(prepared['formal_statement'])!=canonical_signature(trusted_signature(raw['formal_theorem'])):
            mismatches.append(prepared['id'])
    ready=not overlap and not extraction_errors and not mismatches
    metadata(destination/'integrity.json',{'ready_for_training':ready,
        'validation_kind':'trusted source-signature alignment, admission/dependency token checks and split-integrity checks; not Lean elaboration',
        'cross_split_duplicate_proofs':bool(overlap),'cross_split_family_overlap':bool({r['group'] for r in train}&{r['group'] for r in validation}),
        'herald_signature_mismatches':mismatches,'herald_extraction_errors':extraction_errors,
        'herald_all_99_known_boundary_errors_corrected':not mismatches and not extraction_errors,
        'positive_pairs':len(positive),'train_positive_pairs':len(train),'validation_positive_pairs':len(validation),
        'excluded_ProofNet':excluded,'local_Lean_4_28_replay':'not_run','lean_replay':'not_run',
        'source_revision':source['revision']})
    if not ready:raise ValueError('Prepared data integrity checks failed; inspect integrity.json')
    print(json.dumps({'positive_pairs':len(positive),'excluded':len(excluded),
        'train':2*len(train),'validation':2*len(validation),'herald':len(herald)}),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    prepare(parser.parse_args().output)
