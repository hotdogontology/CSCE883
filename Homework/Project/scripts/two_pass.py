"""Reproducible statement-fidelity LoRA/self-training experiment (not argument labels)."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import random
import re
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/models/Qwen3-8B'
PROMPT = (ROOT / 'prompts/statement-v1.txt').read_text(encoding='utf-8')
SEED = 883


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return [json.loads(l) for l in Path(path).read_text(encoding='utf-8').splitlines() if l.strip()]


def write(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')


def metadata(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def statement(text):
    # Only remove the final proof-template suffix, not arbitrary occurrences of :=.
    return re.sub(r'\s*:=\s*by\s+sorry\s*$', '', text).strip()


def messages(row):
    payload = {k: row[k] for k in ('informal_statement', 'formal_statement', 'context')}
    return [{'role': 'system', 'content': PROMPT},
            {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}]


def prepare(out):
    import pandas as pd
    manifest = json.loads((ROOT / 'verified-data-manifest.json').read_text(encoding='utf-8'))
    source = next(s for s in manifest['sources'] if s['name'] == 'proofnet-verified')
    p = ROOT / source['local_directory'] / 'source'
    original = {r['index']: r for r in read(p / 'data/proofnet/proofnet-4.28.jsonl')}
    corrected = {r['index']: r for r in read(p / 'data/archive/proofnet-verified-4.28.jsonl')}
    audits = read(p / 'error_taxonomy/proofnet/results.jsonl')
    rows, excluded, seen = [], [], {}
    for audit in audits:
        idx = int(audit['stem'].split('-')[-1])
        if audit['q1_informal_status'] != 'true_and_unambiguous':
            excluded.append({'group': idx, 'reason': audit['q1_informal_status']})
            continue
        if audit['q2_faithfulness'] not in ('faithful', 'stronger', 'weaker', 'incomparable'):
            raise ValueError('Unknown audit label')
        for variant, item, label in [('original', original[idx], audit['q2_faithfulness'] == 'faithful'),
                                     ('corrected', corrected[idx], True)]:
            assert item['name'] == original[idx]['name']
            row = {'id': f'proofnet-{idx}-{variant}', 'group': f'proofnet-{idx}',
                   'name': item['name'], 'informal_statement': item['informal_stmt'],
                   'formal_statement': statement(item['formal_stmt']),
                   'context': item['header'] + '\n' + item.get('helper', ''),
                   'label': label, 'label_scope': 'statement_fidelity',
                   'label_source': 'published_original_audit' if variant == 'original' else 'published_correction',
                   'source_revision': source['revision']}
            key = re.sub(r'\s+', '', row['informal_statement'] + row['formal_statement'])
            if key in seen:
                if seen[key]['label'] != label:
                    raise ValueError('Conflicting duplicate labels')
                continue
            seen[key] = row
            rows.append(row)
    groups = sorted({r['group'] for r in rows})
    random.Random(SEED).shuffle(groups)
    heldout = set(groups[:max(1, len(groups) // 5)])
    train = [r for r in rows if r['group'] not in heldout]
    valid = [r for r in rows if r['group'] in heldout]
    write(out / 'proofnet-train.jsonl', train)
    write(out / 'proofnet-validation.jsonl', valid)
    # Reserve contest/research-like rows from pseudo-training conservatively.
    frame = pd.read_parquet(ROOT / 'data/herald/data/train-00000-of-00001.parquet')
    herald = []
    for r in frame.to_dict('records'):
        herald.append({'id': f'herald-{r["id"]}', 'name': r['name'],
            'informal_statement': r['informal_theorem'], 'formal_statement': statement(r['formal_theorem']),
            'context': r['header'], 'label_scope': 'statement_fidelity',
            'source_revision': '2d31b459df74d730bff85682de237d894b4eecfa',
            'pseudo_train_eligible': not bool(re.search(r'imo|olympiad|archive|putnam',
                r['name'] + '\n' + r['header'], re.I))})
    write(out / 'herald.jsonl', herald)
    metadata(out / 'data.json', {'seed': SEED, 'scope': 'statement_fidelity',
        'proofnet_source': source['revision'], 'excluded': excluded,
        'split_unit': 'original_problem_all_variants', 'train_rows': len(train),
        'validation_rows': len(valid), 'train_labels': dict(Counter(str(r['label']) for r in train)),
        'validation_labels': dict(Counter(str(r['label']) for r in valid)), 'herald_rows': len(herald),
        'external_overlap_policy': 'contest-name/import exclusion; further source-family overlap audit required',
        'prompt_sha256': sha(PROMPT.encode()),
        'files': {f.name: sha(f.read_bytes()) for f in out.glob('*.jsonl')}})
    print((out / 'data.json').read_text(), flush=True)


def load(adapter=None, training=False):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
    torch.manual_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(BASE, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(BASE, local_files_only=True,
        dtype=torch.bfloat16, device_map={'': 0}, attn_implementation='sdpa',
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16))
    if training:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
            gradient_checkpointing_kwargs={'use_reentrant': False})
        model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
            target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'], task_type='CAUSAL_LM'))
        model.config.use_cache = False
    elif adapter:
        model = PeftModel.from_pretrained(model, adapter, is_trainable=False)
    return model, tokenizer


def encode(tokenizer, row, target=False):
    prefix = tokenizer.apply_chat_template(messages(row), tokenize=True,
        add_generation_prompt=True, enable_thinking=False, return_dict=False)
    if not target:
        return prefix
    answer = tokenizer.encode('YES' if row['label'] else 'NO', add_special_tokens=False)
    answer += [tokenizer.eos_token_id]
    return prefix + answer, [-100] * len(prefix) + answer


def train(args):
    import torch
    rows = read(args.input)
    if not rows or {r['label'] for r in rows} != {True, False}:
        raise ValueError('Training requires nonempty positive and negative sets')
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    meta = {'status': 'loading', 'input_sha256': sha(args.input.read_bytes()), 'input': str(args.input),
        'base': json.loads((ROOT / 'model-manifest.json').read_text(encoding='utf-8')),
        'prompt_sha256': sha(PROMPT.encode()), 'scope': 'statement_fidelity', 'seed': SEED,
        'epochs': args.epochs, 'learning_rate': 1e-4, 'gradient_accumulation': 8,
        'lora': {'rank': 16, 'alpha': 32, 'dropout': .05, 'modules': ['q_proj','k_proj','v_proj','o_proj']},
        'quantization': 'NF4_double_quant_BF16', 'max_tokens': args.max_tokens,
        'packages': {p: importlib.metadata.version(p) for p in ['torch','transformers','peft','bitsandbytes']}}
    metadata(out / 'training.json', meta)
    started = time.perf_counter()
    try:
        model, tokenizer = load(training=True)  # Always fresh original base, never pass-one weights.
        examples, skipped = [], []
        for row in rows:
            ids, labels = encode(tokenizer, row, True)
            if len(ids) > args.max_tokens:
                skipped.append(row['id'])
            else:
                examples.append((row['id'], ids, labels))
        if not examples:
            raise ValueError('No examples fit context budget')
        write(out / 'used-examples.jsonl', [{'id': x[0]} for x in examples])
        meta.update(status='training', used=len(examples), skipped_too_long=skipped,
            trainable_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad))
        metadata(out / 'training.json', meta)
        opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
        model.train()
        step = 0
        with (out / 'loss.jsonl').open('w', encoding='utf-8') as log:
            for epoch in range(args.epochs):
                random.Random(SEED + epoch).shuffle(examples)
                opt.zero_grad(set_to_none=True)
                for i, (_, ids, labels) in enumerate(examples):
                    x = torch.tensor([ids], device='cuda')
                    y = torch.tensor([labels], device='cuda')
                    group_start = (i // 8) * 8
                    divisor = min(8, len(examples) - group_start)
                    loss = model(input_ids=x, attention_mask=torch.ones_like(x), labels=y).loss
                    if not torch.isfinite(loss):
                        raise ValueError('Nonfinite training loss')
                    (loss / divisor).backward()
                    if (i + 1) % 8 == 0 or i + 1 == len(examples):
                        torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
                        opt.step()
                        opt.zero_grad(set_to_none=True)
                        step += 1
                    record = {'epoch': epoch + 1, 'example': i + 1, 'optimizer_step': step,
                              'loss': float(loss.detach()), 'seconds': round(time.perf_counter() - started, 2)}
                    log.write(json.dumps(record) + '\n')
                    log.flush()
                    if (i + 1) % 16 == 0:
                        print(json.dumps(record), flush=True)
                    if (i + 1) % 512 == 0:
                        checkpoint = out / f'checkpoint-{epoch+1}-{i+1}'
                        model.save_pretrained(checkpoint / 'adapter', safe_serialization=True)
                        torch.save({'optimizer': opt.state_dict(), 'torch_rng': torch.get_rng_state(),
                            'cuda_rng': torch.cuda.get_rng_state_all()}, checkpoint / 'optimizer.pt')
                        metadata(checkpoint / 'progress.json', dict(record,
                            input_sha256=meta['input_sha256'], prompt_sha256=meta['prompt_sha256'],
                            seed=SEED, note='Optimizer-boundary recovery checkpoint; not a finished model.'))
                        meta.update(last_checkpoint=str(checkpoint), progress=record)
                        metadata(out / 'training.json', meta)
                model.save_pretrained(out / f'epoch-{epoch+1}', safe_serialization=True)
            model.save_pretrained(out / 'adapter', safe_serialization=True)
        meta.update(status='complete', optimizer_steps=step,
            peak_vram_gib=torch.cuda.max_memory_allocated()/2**30)
    except BaseException as exc:
        meta.update(status='failed', error=repr(exc))
        raise
    finally:
        meta['seconds'] = time.perf_counter() - started
        metadata(out / 'training.json', meta)


def predict(args):
    import torch
    rows = read(args.input)
    if args.limit:
        rows = rows[:args.limit]
    args.output.mkdir(parents=True, exist_ok=True)
    dest = args.output / 'predictions.jsonl'
    old = read(dest) if dest.exists() else []
    done = {r['id'] for r in old}
    spec = {'input_sha256': sha(args.input.read_bytes()), 'adapter': str(args.adapter) if args.adapter else None,
            'adapter_sha256': sha((args.adapter/'adapter_model.safetensors').read_bytes()) if args.adapter else None,
            'prompt_sha256': sha(PROMPT.encode()), 'max_tokens': args.max_tokens, 'limit': args.limit,
            'base_revision': json.loads((ROOT/'model-manifest.json').read_text(encoding='utf-8'))['revision'],
            'inference': 'constrained_YES_NO_next_token_NF4_BF16', 'label_scope': 'statement_fidelity',
            'batch_size': args.batch_size}
    run = args.output / 'run.json'
    if run.exists() and json.loads(run.read_text(encoding='utf-8'))['spec'] != spec:
        raise ValueError('Cannot resume with changed inputs/model/prompt/settings')
    metadata(run, {'status': 'running', 'spec': spec})
    model, tokenizer = load(args.adapter)
    model.eval()
    tokenizer.padding_side = 'left'
    tokenizer.pad_token_id = tokenizer.eos_token_id
    yes, no = [tokenizer.encode(s, add_special_tokens=False) for s in ['YES','NO']]
    if len(yes)!=1 or len(no)!=1:
        raise ValueError('Constrained scoring requires single-token YES and NO')
    started = time.perf_counter()
    with dest.open('a', encoding='utf-8') as output:
        pending = [r for r in rows if r['id'] not in done]
        for start in range(0,len(pending),args.batch_size):
            batch = pending[start:start+args.batch_size]
            records, accepted = [], []
            for row in batch:
                ids = encode(tokenizer, row)
                record = {'id': row['id'], 'prediction': None, 'input_tokens': len(ids),
                'input_row_sha256': sha(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()),
                'label_scope': 'statement_fidelity', 'label_status': 'model_prediction'}
                records.append(record)
                if len(ids) > args.max_tokens:
                    record['status'] = 'too_long'
                else:
                    accepted.append((record,ids))
            if accepted:
                padded = tokenizer.pad({'input_ids':[x[1] for x in accepted]},return_tensors='pt').to('cuda')
                try:
                    with torch.inference_mode():
                        logits = model(**padded,logits_to_keep=1).logits[:,-1,[yes[0],no[0]]].float()
                        scores = logits.softmax(-1).cpu().tolist()
                    for (record,_),score in zip(accepted,scores):
                        record.update(prediction=score[0]>=score[1],status='predicted',
                            yes_score_uncalibrated=score[0])
                except torch.OutOfMemoryError:
                    for record,_ in accepted:
                        record['status'] = 'out_of_memory'
                    torch.cuda.empty_cache()
            for record in records:
                output.write(json.dumps(record)+'\n')
            output.flush()
            if start% (args.batch_size*10)==0:
                print(json.dumps({'rows':len(done)+start+len(batch),'total':len(rows),
                    'seconds':round(time.perf_counter()-started)}),flush=True)
    all_predictions = read(dest)
    valid = {r['id']:r['prediction'] for r in all_predictions if r['prediction'] is not None}
    labeled = [r for r in rows if 'label' in r and r['id'] in valid]
    confusion = Counter(('true_' if valid[r['id']]==r['label'] else 'false_')+
        ('positive' if valid[r['id']] else 'negative') for r in labeled)
    metadata(run, {'status':'complete','spec':spec,'rows':len(all_predictions),
        'status_counts':dict(Counter(r['status'] for r in all_predictions)),
        'predictions':dict(Counter(str(r['prediction']) for r in all_predictions)),
        'accuracy':sum(valid[r['id']]==r['label'] for r in labeled)/len(labeled) if labeled else None,
        'confusion':dict(confusion), 'labeled_coverage':len(labeled),
        'seconds_this_process':time.perf_counter()-started})


def consensus(args):
    rows = read(args.input)
    a = {r['id']:r for r in read(args.untuned)}
    b = {r['id']:r for r in read(args.first_pass)}
    kept, rejected = [], []
    counts = Counter()
    for row in rows:
        x, y = a.get(row['id'], {}).get('prediction'), b.get(row['id'], {}).get('prediction')
        if x is None or y is None:
            reason = 'missing_prediction'
        elif x != y:
            reason = 'disagreement'
        elif not row.get('pseudo_train_eligible',False):
            reason = 'reserved_contest_family'
        else:
            reason = 'agreement'
            kept.append(dict(row,label=x,label_source='two_model_agreement_pseudo_label',
                teacher_runs=[str(args.untuned),str(args.first_pass)]))
        counts[reason]+=1
        if reason!='agreement':
            rejected.append({'id':row['id'],'reason':reason,'untuned':x,'first_pass':y})
    args.output.mkdir(parents=True,exist_ok=False)
    write(args.output/'train.jsonl',kept)
    write(args.output/'excluded.jsonl',rejected)
    metadata(args.output/'summary.json',{'counts':dict(counts),'labels':dict(Counter(str(r['label']) for r in kept)),
        'trusted_ground_truth':False,'policy':'agreement_only_exclude_missing_and_contest_families',
        'teachers':{str(p):sha(p.read_bytes()) for p in [args.untuned,args.first_pass]},
        'warning':'Correlated teacher errors can agree. Agreement does not establish correctness.'})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    subs=parser.add_subparsers(dest='command',required=True)
    p=subs.add_parser('prepare');p.add_argument('--output',type=Path,required=True)
    for command in ['train','predict']:
        p=subs.add_parser(command);p.add_argument('--input',type=Path,required=True)
        p.add_argument('--output',type=Path,required=True);p.add_argument('--max-tokens',type=int,default=2048)
        if command=='train':p.add_argument('--epochs',type=int,default=1)
        else:
            p.add_argument('--adapter',type=Path);p.add_argument('--limit',type=int)
            p.add_argument('--batch-size',type=int,default=8)
    p=subs.add_parser('consensus');p.add_argument('--input',type=Path,required=True)
    p.add_argument('--untuned',type=Path,required=True);p.add_argument('--first-pass',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='prepare':
        args.output.mkdir(parents=True,exist_ok=False);prepare(args.output)
    else:globals()[args.command](args)


if __name__=='__main__':main()
