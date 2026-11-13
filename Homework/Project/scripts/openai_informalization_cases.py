"""Pinned OpenAI subarguments through the existing trained informalizer and judge.

No direct baseline. Source selection is explicit, not a full Lean dependency closure.
All model inputs and outputs are retained; expected discrepancies are never inputs.
"""
import argparse
import json
import re
import time
import traceback
from pathlib import Path
from datetime import datetime, timezone
from informalization_pipeline import ROOT, MANIFEST, TRANSLATE, JUDGE, prefix, digest
from argument_data import strip_comments
from two_pass import metadata, read, write

DATA = ROOT / 'data/openai-correspondence-cases'
OUT = ROOT / 'artifacts/openai-informalization-20261113'
ADAPTER = ROOT / 'artifacts/informalization-14b-20261112/adapter'
REV = 'f9e8bc5b38b6e212696e8a30e3e91517af887bbd'
SOURCE = DATA / 'source' / ('NavierStokesAndEuler-' + REV)

def prepare():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ROOT / json.loads(MANIFEST.read_text())['local_directory'], local_files_only=True)
    inventory = []
    def block(file, name):
        path = SOURCE / 'NavierStokes' / file
        raw = path.read_text(encoding='utf-8')
        clean = strip_comments(raw)
        pattern = r'(?m)^(?:(?:noncomputable|private|protected)\s+)*(?:def|abbrev|theorem|lemma|structure|inductive)\s+(\S+)'
        hits = list(re.finditer(pattern, clean))
        matches = [(i,m) for i,m in enumerate(hits) if m.group(1) == name]
        if len(matches) != 1: raise ValueError((file,name,len(matches)))
        i,m = matches[0]
        end = hits[i+1].start() if i+1<len(hits) else len(clean)
        text = clean[m.start():end].strip()
        # Drop trailing namespace endings, not any theorem expression.
        text = re.split(r'\nend(?:\s|$)',text)[0].rstrip()
        inventory.append({'file':file,'declaration':name,'source_sha256':digest(raw), 'excerpt_sha256':digest(text)})
        return text
    def context(selections):
        return '\n\n'.join('Source module: NavierStokes.'+file.removesuffix('.lean').replace('/','.')+'\n'+block(file,name)
                           for file,names in selections for name in names)
    inv_target = block('SmoothFamilyTorusInverse.lean','norm_derivativeWord_inverse_le')
    inv_context = context([
        ('SmoothFamilyTorusInverse.lean',['Point','Source','slice','Periodic','coefficient','inverse','slice_smooth']),
        ('SmoothFourierData.lean',['partialX','xJet','swapFunction','coefficient_seminorm_bound']),
        ('TorusInverse.lean',['Plane','Frequency','Direction','vector','symbol','weight','coeffSeminorm','derivativeWord','inverse_derivativeWord_bound']),
        ('ParametricTorusInverse.lean',['mixedLossConstant'])])
    pressure_target = block('R3/PressureFlux.lean','exists_uniform_actual_pressure_flux_bound')
    pressure_context = context([
        ('R3/PressureFlux.lean',['canonicalCutoffFlux','actual_flux_integrable_and_le_canonicalNorm',
          'pressurePair_decomposition','norm_pressurePair_le_local_commutator','riesz_rTest_bound',
          'rTest_four_bound','localized_pair_bound','norm_cutoff_pressurePair_le_local_commutator',
          'cutoff_commutator_bound','cutoff_pressurePair_bound','canonicalCutoffFlux_bound',
          'exists_uniform_canonicalCutoffFlux_bound']),
        ('R3/RieszTestOperators.lean',['lpNorm_six_rieszTest_le','lpNorm_two_fderiv_rieszTest_le']),
        ('R3/PressureRecovery.lean',['Hypotheses'])])
    # Locate the exact source definitions, avoiding manual mathematical glosses.
    for name in ['cutoffL6','dissipationRoot','comparisonLpNorm']:
        candidates=[]
        for p in (SOURCE/'NavierStokes/R3').glob('*.lean'):
            if re.search(r'(?m)^(?:noncomputable )?(?:def|abbrev) '+name+r'\b',p.read_text(encoding='utf-8')):
                candidates.append(p)
        if len(candidates)!=1: raise ValueError((name,candidates))
        file=candidates[0].relative_to(SOURCE/'NavierStokes').as_posix()
        pressure_context += '\n\nSource module: '+file+'\n'+block(file,name)
    inv_english = r'''Fix the slow parameters. For the auxiliary-time operator N=v_t dot partial_y on the two-dimensional torus, the inverse estimate is
||N^{-1}F||_{C^m_y} <= C_m ||F||_{C^{m+4}_y}, for smooth zero-Haar-mean F and every integer m>=0.
The inverse is the Fourier series sum over nonzero k in Z^2 of Fhat(k)/(2*pi*i*v_t dot k) times exp(2*pi*i*k dot y).
The divisor bound (6.7) gives |v_t dot k|^{-1} <= C(1+|k|). Four more derivatives of F than the requested output leave a summable (1+|k|)^{-3} bound on the Fourier series in two dimensions. This proves the estimate. The zero Fourier coefficient is fixed to be zero.'''
    pressure_english = r'''We estimate the pressure flux in the comparison of two smooth solutions with common force and zero initial velocity, on a fixed interval [0,T]. Set w=v-u, pi=P-p, and g_ij=v_i*v_j-u_i*u_j=w_i*w_j+w_i*u_j+u_i*w_j. The L2 norm of w and the sum of the L1 norms of g_ij are uniformly bounded. The canonical pressure pi_* = sum_ij R_i R_j g_ij has the same pressure gradient as pi in the space-time interior; here R_i is the Riesz transform.
Choose 0<=phi<=1 smooth and compactly supported, equal to one on the unit ball. For R>=1, set phi_R(x)=phi(x/R), chi_R=phi_R^8, A_R=(integral chi_R |grad w|^2)^{1/2}, and B_R=||phi_R^4 w||_6. Sobolev and the product rule give B_R <= C(A_R+R^{-1}||w||_2).
Use Lp boundedness of Riesz transforms for 1<p<infinity. With [a,T]g=a(Tg)-T(ag),
phi_R^4 pi_* = sum_ij R_i R_j(phi_R^4 g_ij) + sum_ij [phi_R^4,R_i R_j]g_ij.
The first sum has L^{3/2} norm at most C_T(B_R+1), since ||phi_R^4 w_i w_j||_{3/2} <= B_R||w||_2 and ||phi_R^4 w_i u_j||_{3/2} <= ||w||_2||u||_6.
The nonlocal R_i R_j kernel is bounded by C|x-y|^{-3}; its identity term cancels in the commutator. The commutator kernel is bounded by K_R(z)=C|z|^{-3} min{|z|/R,1}. Radial integration gives ||K_R||_{4/3}^{4/3} <= C R^{-1}. Young's convolution inequality bounds the second sum in L^{4/3} by C_T R^{-3/4}. Pass from compact smooth cutoffs of g to g by L1 convergence, the uniform commutator bound, and convergence of Riesz transforms in H^{-s}.
The equality of pressure gradients tested against a(t)chi_R w gives integral pi w dot grad chi_R = integral pi_* w dot grad chi_R for almost every t. Since |grad chi_R| <= C R^{-1} phi_R^7, the two sums pair with C R^{-1} phi_R^3 |w|. Interpolation gives ||phi_R^3 w||_3 <= ||phi_R^2 w||_3 <= B_R^{1/2}||w||_2^{1/2} and ||phi_R^3 w||_4 <= B_R^{3/4}||w||_2^{1/4}. Consequently,
|integral pi w dot grad chi_R| <= C_T R^{-1}[(B_R+1) B_R^{1/2} + R^{-3/4} B_R^{3/4}].'''
    rows=[]
    for ident,target,ctx,english,pages in [('inverse-estimate',inv_target,inv_context,inv_english,[95,96]),
                                        ('pressure-flux',pressure_target,pressure_context,pressure_english,[121,122,123])]:
        # The selected declarations use an explicit := by delimiter.
        statement,proof=target.split(':= by',1)
        payload={'context':ctx,'formal_statement':statement.strip(),'formal_proof':'by'+proof}
        n=len(prefix(tok,TRANSLATE,payload))
        if n>28000: raise ValueError((ident,'too long',n))
        rows.append({'id':ident,**payload,'informal_statement':'Compare the supplied proof subarguments, allowing consistent changes of notation.',
                     'informal_proof':english,'english_pdf_pages':pages,'prompt_tokens':n})
    OUT.mkdir(parents=True,exist_ok=True)
    write(OUT/'cases.jsonl',rows)
    metadata(OUT/'preparation.json',{'revision':REV,'source_zip_sha256':digest((DATA/'source.zip').read_bytes()),
        'pdf_sha256':digest((DATA/'navier-stokes.pdf').read_bytes()),'declarations':inventory,
        'english_policy':'Manually normalized, scoped source subargument transcription; equations visually checked on PDF pages 95,96,122,123. Not the whole lemma.',
        'context_policy':'Explicit selected definitions and helper bodies, not complete transitive closure; no critique text or expected labels in model payloads.',
        'cases_sha256':digest((OUT/'cases.jsonl').read_bytes()),'tokens':{r['id']:r['prompt_tokens'] for r in rows}})
    print([(r['id'],r['prompt_tokens']) for r in rows],flush=True)

def run():
    import torch
    from argument_model import load
    if (OUT/'job.json').exists(): raise ValueError('Preserve existing run')
    start=time.monotonic()
    def status(stage,**kw):
        metadata(OUT/'job.json',{'status':stage,'updated_utc':datetime.now(timezone.utc).isoformat(),
                               'seconds':time.monotonic()-start,**kw})
        print(stage,kw,flush=True)
    try:
        status('loading')
        torch.set_num_threads(8)
        model,tok,base=load(MANIFEST,adapter=ADAPTER); model.eval()
        metadata(OUT/'run.json',{'base':base,'adapter_sha256':digest((ADAPTER/'adapter_model.safetensors').read_bytes()),
            'code_sha256':digest(Path(__file__).read_bytes()),'cases_sha256':digest((OUT/'cases.jsonl').read_bytes()),
            'translation_prompt':TRANSLATE,'judge_prompt':JUDGE,'max_new_tokens':2048,'max_input_tokens':28000,
            'decoding':'greedy, thinking disabled','precision':'BF16, no quantization',
            'notes':'Selected trained informalization adapter and existing YES/NO English judge; longer source context and 2048 output cap for external case study. No direct baseline.',
            'adapter_path':str(ADAPTER.relative_to(ROOT))})
        def generate(system,payload,cap):
            p=prefix(tok,system,payload)
            if len(p)>28000: raise ValueError('Context exceeds limit; no truncation')
            x=torch.tensor([p],device='cuda')
            with torch.inference_mode():
                y=model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,
                    max_new_tokens=cap,use_cache=True,pad_token_id=tok.eos_token_id)
            ids=y[0,len(p):].tolist()
            return {'text':tok.decode(ids,skip_special_tokens=True),'prompt_tokens':len(p),
                    'output_tokens':len(ids),'hit_limit':len(ids)>=cap}
        results=[]
        with (OUT/'results.jsonl').open('w',encoding='utf-8') as f:
            for r in read(OUT/'cases.jsonl'):
                status('informalizing',case=r['id'])
                translated=generate(TRANSLATE,{k:r[k] for k in ['context','formal_statement','formal_proof']},2048)
                metadata(OUT/(r['id']+'-translation.json'),translated)
                payload={'theorem':r['informal_statement'],'original_english_proof':r['informal_proof'],
                         'english_account_of_lean':translated['text']}
                status('judging',case=r['id'])
                with model.disable_adapter(),torch.inference_mode():
                    p=prefix(tok,JUDGE,payload)
                    if len(p)>8192: raise ValueError('Judge input exceeds existing 8192 limit')
                    x=torch.tensor([p],device='cuda')
                    yn=[tok.encode(s,add_special_tokens=False) for s in ['YES','NO']]
                    assert all(len(x)==1 for x in yn)
                    logits=model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False,logits_to_keep=1).logits[0,-1,[a[0] for a in yn]].float()
                    match=bool(logits[0]>=logits[1]); score=float(logits.softmax(-1)[0])
                    # Independent explanation request, not conditioned on label or critique.
                    explanation=generate(JUDGE+' Then explain the specific mathematical agreement or discrepancy. Cite the two accounts; state any uncertainty.',payload,1536)
                result={'id':r['id'],'translation':translated,'match':match,'yes_score_uncalibrated':score,
                        'judge_prompt_tokens':len(p),'judge_explanation':explanation}
                results.append(result); f.write(json.dumps(result,ensure_ascii=False)+'\n'); f.flush()
                status('case_complete',case=r['id'],match=match)
        status('complete',cases=len(results),peak_vram_gib=torch.cuda.max_memory_allocated()/2**30)
    except BaseException:
        status('failed',error=traceback.format_exc()); raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','run']);args=p.parse_args()
    prepare() if args.command=='prepare' else run()
