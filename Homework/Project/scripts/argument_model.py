"""BF16, unquantized Qwen proof-argument judging and LoRA training."""
import argparse
from collections import Counter
import importlib.metadata
import json
from pathlib import Path
import random
import time

from argument_data import payload,paired_too_long
from two_pass import ROOT, read, write, metadata, sha

PROMPT=(ROOT/'prompts/argument-v1.txt').read_text(encoding='utf-8')
SEED=883


def messages(row):
    return [{'role':'system','content':PROMPT},
        {'role':'user','content':json.dumps(payload(row),ensure_ascii=False)}]


def tokens(tokenizer,row,training=False):
    prefix=tokenizer.apply_chat_template(messages(row),tokenize=True,return_dict=False,
        add_generation_prompt=True,enable_thinking=False)
    if not training:return prefix
    answer=tokenizer.encode('YES' if row['label'] else 'NO',add_special_tokens=False)+[tokenizer.eos_token_id]
    return prefix+answer,answer


def load(manifest,training=False,adapter=None):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    from peft import LoraConfig,get_peft_model,PeftModel
    torch.manual_seed(SEED)
    info=json.loads(manifest.read_text(encoding='utf-8'))
    if not info.get('download_complete'):raise ValueError('Checkpoint download not verified complete')
    location=ROOT/info['local_directory']
    tokenizer=AutoTokenizer.from_pretrained(location,local_files_only=True,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(location,local_files_only=True,trust_remote_code=False,
        use_safetensors=True,dtype=torch.bfloat16,device_map={'':0},attn_implementation='sdpa')
    if getattr(model,'is_quantized',False) or getattr(model,'is_loaded_in_4bit',False):
        raise ValueError('Quantization is prohibited for this experiment')
    if any(p.dtype!=torch.bfloat16 for p in model.parameters()):
        raise ValueError('Base model is not uniformly BF16')
    if training:
        model=get_peft_model(model,LoraConfig(r=16,lora_alpha=32,lora_dropout=.05,
            target_modules=['q_proj','k_proj','v_proj','o_proj'],task_type='CAUSAL_LM'))
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        model.enable_input_require_grads()
        model.config.use_cache=False
    elif adapter:model=PeftModel.from_pretrained(model,adapter,is_trainable=False)
    return model,tokenizer,info


def answer_loss(model,ids,answer):
    import torch
    x=torch.tensor([ids],device='cuda')
    # Retain logits only where the YES/NO answer and end token receive loss.
    # First retained logit is at the last prompt position, predicting answer[0].
    logits=model(input_ids=x,attention_mask=torch.ones_like(x),
        logits_to_keep=len(answer)+1).logits[0,:-1,:]
    return torch.nn.functional.cross_entropy(logits.float(),torch.tensor(answer,device='cuda'))


def train_or_probe(args):
    import torch
    started=time.perf_counter();args.output.mkdir(parents=True,exist_ok=False)
    state={'status':'loading','scope':'argument_fidelity','quantization':None,'base_dtype':'bfloat16',
        'input_sha256':sha(args.input.read_bytes()),'prompt_sha256':sha(PROMPT.encode()),
        'code_sha256':sha(Path(__file__).read_bytes()),'seed':SEED,'epochs':1,'learning_rate':1e-4,
        'max_tokens':args.max_tokens,'gradient_accumulation':8,'lora_rank':16,'lora_alpha':32,
        'lora_dropout':.05,'label_policy':'user-assumed original pairs; constructed proof-swap negatives',
        'packages':{k:importlib.metadata.version(k) for k in ['torch','transformers','peft']}}
    try:
        model,tokenizer,base=load(args.model_manifest,training=True)
        state['base_revision']=base['revision']
        examples=[];skipped=[]
        rows=read(args.input)
        encoded=[tokens(tokenizer,r,True) for r in rows]
        excluded_groups=paired_too_long(rows,[len(x[0]) for x in encoded],args.max_tokens)
        for row,(ids,answer) in zip(rows,encoded):
            if len(ids)>args.max_tokens or row.get('group') in excluded_groups:
                skipped.append({'id':row['id'],'tokens':len(ids),'label':row['label'],'reason':'pair_exceeds_context'})
            else:examples.append((row,ids,answer))
        if {r[0]['label'] for r in examples}!={True,False}:raise ValueError('Both classes must fit context')
        state.update(used=len(examples),skipped_too_long=len(skipped),
            used_labels=dict(Counter(str(x[0]['label']) for x in examples)),
            trainable_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad))
        write(args.output/'skipped.jsonl',skipped)
        write(args.output/'used.jsonl',[{'id':r['id'],'label':r['label'],'tokens':len(ids)} for r,ids,a in examples])
        opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=1e-4)
        model.train();opt.zero_grad(set_to_none=True)
        if args.command=='probe':
            row,ids,answer=max(examples,key=lambda x:len(x[1]))
            loss=answer_loss(model,ids,answer)
            if not torch.isfinite(loss):raise ValueError('Nonfinite probe loss')
            loss.backward();opt.step();opt.zero_grad(set_to_none=True)
            state.update(status='complete',probe_id=row['id'],probe_tokens=len(ids),loss=float(loss.detach()))
        else:
            state['status']='training';metadata(args.output/'training.json',state)
            random.Random(SEED).shuffle(examples)
            step=0
            with (args.output/'loss.jsonl').open('w',encoding='utf-8') as log:
                for i,(row,ids,answer) in enumerate(examples):
                    loss=answer_loss(model,ids,answer)
                    if not torch.isfinite(loss):raise ValueError('Nonfinite loss')
                    divisor=min(8,len(examples)-(i//8)*8)
                    (loss/divisor).backward()
                    if (i+1)%8==0 or i+1==len(examples):
                        torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.)
                        opt.step();opt.zero_grad(set_to_none=True);step+=1
                    record={'example':i+1,'optimizer_step':step,'loss':float(loss.detach()),
                        'seconds':round(time.perf_counter()-started,2)}
                    log.write(json.dumps(record)+'\n');log.flush()
                    if (i+1)%16==0:print(json.dumps(record),flush=True)
                    if (i+1)%128==0:
                        checkpoint=args.output/f'checkpoint-{i+1}'
                        model.save_pretrained(checkpoint/'adapter',safe_serialization=True)
                        torch.save({'optimizer':opt.state_dict(),'torch_rng':torch.get_rng_state(),
                            'cuda_rng':torch.cuda.get_rng_state_all()},checkpoint/'optimizer.pt')
                        metadata(checkpoint/'progress.json',record)
                model.save_pretrained(args.output/'adapter',safe_serialization=True)
            state.update(status='complete',optimizer_steps=step)
        state['peak_vram_gib']=torch.cuda.max_memory_allocated()/2**30
    except BaseException as exc:
        state.update(status='failed',error=repr(exc));raise
    finally:
        state['seconds']=time.perf_counter()-started
        metadata(args.output/('probe.json' if args.command=='probe' else 'training.json'),state)


def predict(args):
    import torch
    rows=read(args.input);args.output.mkdir(parents=True,exist_ok=True)
    model,tokenizer,base=load(args.model_manifest,adapter=args.adapter);model.eval()
    excluded_groups=set()
    if rows and all('label' in r and 'group' in r for r in rows):
        excluded_groups=paired_too_long(rows,[len(tokens(tokenizer,r)) for r in rows],args.max_tokens)
    spec={'input_sha256':sha(args.input.read_bytes()),'base_revision':base['revision'],
        'code_sha256':sha(Path(__file__).read_bytes()),
        'adapter_sha256':sha((args.adapter/'adapter_model.safetensors').read_bytes()) if args.adapter else None,
        'prompt_sha256':sha(PROMPT.encode()),'max_tokens':args.max_tokens,'quantization':None,
        'base_dtype':'bfloat16','scope':'argument_fidelity','inference':'constrained_YES_NO_next_token',
        'seed':SEED,'packages':{k:importlib.metadata.version(k) for k in ['torch','transformers','peft']}}
    run=args.output/'run.json';dest=args.output/'predictions.jsonl'
    if run.exists() and json.loads(run.read_text(encoding='utf-8'))['spec']!=spec:
        raise ValueError('Cannot resume changed inputs/settings')
    metadata(run,{'status':'running','spec':spec})
    done={r['id'] for r in read(dest)} if dest.exists() else set()
    yes,no=[tokenizer.encode(s,add_special_tokens=False) for s in ['YES','NO']]
    if len(yes)!=1 or len(no)!=1:raise ValueError('Expected single-token class names')
    started=time.perf_counter()
    with dest.open('a',encoding='utf-8') as output:
        for i,row in enumerate(rows):
            if row['id'] in done:continue
            result={'id':row['id'],'prediction':None,'scope':'argument_fidelity'}
            try:ids=tokens(tokenizer,row)
            except ValueError as exc:result.update(status='missing_evidence',error=str(exc))
            else:
                result['input_tokens']=len(ids)
                if len(ids)>args.max_tokens:result['status']='too_long'
                elif row.get('group') in excluded_groups:result['status']='paired_example_too_long'
                else:
                    x=torch.tensor([ids],device='cuda')
                    try:
                        with torch.inference_mode():
                            logits=model(input_ids=x,attention_mask=torch.ones_like(x),logits_to_keep=1).logits[0,-1,[yes[0],no[0]]].float()
                            score=logits.softmax(-1).cpu().tolist()
                        result.update(status='predicted',prediction=score[0]>=score[1],yes_score_uncalibrated=score[0],
                            yes_minus_no_logit=float((logits[0]-logits[1]).cpu()))
                    except torch.OutOfMemoryError:
                        result['status']='out_of_memory';torch.cuda.empty_cache()
            output.write(json.dumps(result)+'\n');output.flush()
            if (i+1)%50==0:print(json.dumps({'rows':i+1,'total':len(rows),'seconds':round(time.perf_counter()-started)}),flush=True)
    predictions=read(dest)
    state={'status':'complete','spec':spec,'rows':len(predictions),
        'status_counts':dict(Counter(r['status'] for r in predictions)),
        'prediction_counts':dict(Counter(str(r['prediction']) for r in predictions)),
        'seconds_this_process':time.perf_counter()-started,'accuracy':None,
        'peak_vram_gib':torch.cuda.max_memory_allocated()/2**30}
    if all('label' in r for r in rows):
        from classification_metrics import evaluate
        state['metrics']=evaluate(rows,predictions)
        state['accuracy']=state['metrics']['accuracy']
    metadata(run,state)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['probe','train','predict'])
    parser.add_argument('--model-manifest',type=Path,default=ROOT/'model-manifest-14b.json')
    parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--max-tokens',type=int,default=8192);parser.add_argument('--adapter',type=Path)
    args=parser.parse_args()
    if args.command=='predict':predict(args)
    else:train_or_probe(args)


if __name__=='__main__':main()
