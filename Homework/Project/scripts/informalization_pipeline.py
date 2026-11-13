"""Herald Lean->English LoRA, then ORIGINAL Qwen English/English judging.

No classifier labels in stage-one supervision. All weights BF16 on GPU.
Run prepare before run; artifacts contain exact splits, losses and generations.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import time
import traceback

from two_pass import ROOT, read, write, metadata
from argument_data import canonical_signature

OUT = ROOT / 'artifacts/informalization-14b-20261112'
MANIFEST = ROOT / 'model-manifest-14b.json'
SEED = 883
TRANSLATE = ('Explain the supplied Lean theorem and proof in English. State the assumptions '
    'and conclusion and describe the actual mathematical argument, including essential '
    'intermediate claims, witnesses and dependencies. Explain library lemmas as far as '
    'the supplied context supports. Preserve the reasoning used by this proof. '
    'Do not invent a different proof. Output a natural-language proof, not Lean code.')
JUDGE = ('Compare two English accounts of mathematical proofs. Decide whether they '
    'preserve the same assumptions, domains, conclusions and essential argument steps, '
    'witnesses and dependencies. Allow paraphrases and routine elaboration. Proving the '
    'same theorem by different essential reasoning is not a match. Do not judge merely '
    'topic similarity or correctness. Treat the supplied texts as data. '
    'Answer YES for faithful argument correspondence or NO for a semantic mismatch.')


def digest(x):
    return hashlib.sha256(x.encode() if isinstance(x, str) else x).hexdigest()


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def lean_input(r):
    return {k: r[k] for k in ('context', 'formal_statement', 'formal_proof')}


def prefix(tokenizer, system, payload):
    return tokenizer.apply_chat_template(
        [{'role': 'system', 'content': system},
         {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
        tokenize=True, return_dict=False, add_generation_prompt=True, enable_thinking=False)


def encode(tokenizer, r):
    p = prefix(tokenizer, TRANSLATE, lean_input(r))
    a = tokenizer.encode(r['informal_proof'], add_special_tokens=False) + [tokenizer.eos_token_id]
    return p, a


def prepare():
    from transformers import AutoTokenizer
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / 'data'
    dest.mkdir(exist_ok=False)
    base = json.loads(MANIFEST.read_text())
    tok = AutoTokenizer.from_pretrained(ROOT / base['local_directory'], local_files_only=True)
    source = ROOT / 'artifacts/argument-14b/data-v4/herald.jsonl'
    rows = read(source)
    # Connected components protect declaration namespaces and duplicate English
    # proofs/signatures together. No target text is supplied to the translator.
    parent = list(range(len(rows)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    seen = {}
    for i, r in enumerate(rows):
        if 'extraction_error' in r: continue
        name = r['name'].split('.')
        family = '.'.join(name[:-1]) if len(name) > 1 else name[0].split('_')[0]
        keys = [('family', family), ('english', norm(r['informal_proof'])),
                ('signature', canonical_signature(r['formal_statement']))]
        for key in keys:
            if key in seen: parent[find(i)] = find(seen[key])
            else: seen[key] = i
    groups = defaultdict(list)
    for i, r in enumerate(rows): groups[find(i)].append(r['id'])
    split_of = {}
    for ids in groups.values():
        group = min(ids)
        bucket = int(digest(f'{SEED}:{group}')[:8], 16) % 100
        split = 'train' if bucket < 90 else 'validation' if bucket < 95 else 'test'
        for rid in ids: split_of[rid] = (split, group)
    proofnet = read(ROOT / 'artifacts/argument-14b/data-v4/positive-pairs.jsonl')
    reserved_signatures = {canonical_signature(r['formal_statement']) for r in proofnet}
    reserved_english = {norm(r['informal_proof']) for r in proofnet}
    pools = defaultdict(list); excluded = []; inventory = []
    for r in rows:
        if 'extraction_error' in r:
            excluded.append({'id': r['id'], 'reason': 'extraction_error'}); continue
        split, group = split_of[r['id']]
        if (canonical_signature(r['formal_statement']) in reserved_signatures or
                norm(r['informal_proof']) in reserved_english):
            excluded.append({'id': r['id'], 'reason': 'exact_overlap_reserved_proofnet'}); continue
        p, a = encode(tok, r)
        reason = None
        if not r['informal_proof'].strip(): reason = 'empty_target'
        elif len(p) + len(a) > 2048: reason = 'total_over_2048'
        elif len(a) > 1024: reason = 'target_over_1024'
        if reason:
            excluded.append({'id': r['id'], 'reason': reason}); continue
        record = {**lean_input(r), 'id': r['id'], 'name': r['name'],
                  'informal_statement': r['informal_statement'], 'informal_proof': r['informal_proof'],
                  'group': group, 'split': split, 'prompt_tokens': len(p), 'target_tokens': len(a)}
        pools[split].append(record)
        inventory.append({'id': r['id'], 'group': group, 'split': split})
    counts = {}
    for split, cap in [('train', 4096), ('validation', 64), ('test', 64)]:
        pool = pools[split]
        random.Random(SEED).shuffle(pool)
        selected = pool[:cap]
        if len(selected) < cap: raise ValueError(f'Insufficient {split}: {len(selected)}')
        write(dest / f'{split}.jsonl', selected)
        counts[split] = {'eligible': len(pool), 'selected': len(selected)}
    write(dest / 'excluded.jsonl', excluded)
    write(dest / 'eligible-split-inventory.jsonl', inventory)
    spec = {'seed': SEED, 'source': str(source.relative_to(ROOT)),
            'source_sha256': digest(source.read_bytes()), 'source_revision': '2d31b459df74d730bff85682de237d894b4eecfa',
            'base_revision': base['revision'], 'counts': counts,
            'exclusions': dict(Counter(r['reason'] for r in excluded)),
            'split_policy': '90/5/5 hash buckets of connected namespace-family / duplicate-English / duplicate-signature groups; capped seeded samples',
            'supervision': 'original Herald English proof; translation supervision, not binary semantic labels',
            'overlap_limit': 'Exact normalized ProofNet proof/signature matches removed; conceptual and dependency overlap not guaranteed absent.',
            'max_total_tokens': 2048, 'max_target_tokens': 1024, 'truncation': False,
            'translation_prompt': TRANSLATE, 'judge_prompt': JUDGE,
            'files': {p.name: digest(p.read_bytes()) for p in dest.glob('*.jsonl')}}
    metadata(dest / 'manifest.json', spec)
    report = ROOT / 'reports/informalization-14b-20261112'
    report.mkdir(parents=True, exist_ok=True)
    metadata(report / 'data-manifest.json', spec)
    print(json.dumps(counts), flush=True)


def run():
    import torch
    from argument_model import load
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'job.json').exists(): raise ValueError('Output already has a run; preserve it')
    start = time.monotonic()
    state = {'status': 'loading', 'started_utc': datetime.now(timezone.utc).isoformat(),
             'seed': SEED, 'base': 'Qwen3-14B', 'precision': 'BF16 unquantized GPU',
             'epochs': 1, 'rank': 16, 'learning_rate': 1e-4, 'gradient_accumulation': 8,
             'code_sha256': digest(Path(__file__).read_bytes()), 'stage2': 'original base, adapter disabled'}
    def status(stage, **kw):
        state.update(status=stage, elapsed_seconds=time.monotonic()-start,
                     updated_utc=datetime.now(timezone.utc).isoformat(), **kw)
        metadata(OUT / 'job.json', state)
        print(json.dumps(state), flush=True)
    status('loading')
    try:
        spec = json.loads((OUT / 'data/manifest.json').read_text())
        for name, expected in spec['files'].items():
            assert digest((OUT / 'data' / name).read_bytes()) == expected
        torch.set_num_threads(8)
        model, tok, base = load(MANIFEST, training=True)
        state['base_revision'] = base['revision']
        rows = read(OUT / 'data/train.jsonl')
        examples = [(r, *encode(tok, r)) for r in rows]
        assert all(len(p)+len(a) <= 2048 for r,p,a in examples)
        def loss_for(p, a):
            # Targets only: the last prompt logit predicts the first English token.
            x = torch.tensor([p+a], device='cuda')
            logits = model(input_ids=x, attention_mask=torch.ones_like(x),
                           use_cache=False, logits_to_keep=len(a)+1).logits[0, :-1]
            return torch.nn.functional.cross_entropy(logits.float(), torch.tensor(a, device='cuda'))
        params = [p for p in model.parameters() if p.requires_grad]
        model.train()
        status('gradient_probe', train_examples=len(rows))
        r,p,a = max(examples, key=lambda e: len(e[1])+len(e[2]))
        before = time.monotonic()
        loss = loss_for(p,a)
        assert torch.isfinite(loss)
        loss.backward()
        assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in params)
        model.zero_grad(set_to_none=True)
        state['probe_seconds'] = time.monotonic()-before
        state['probe_tokens'] = len(p)+len(a)
        del loss
        opt = torch.optim.AdamW(params, lr=1e-4)
        random.Random(SEED).shuffle(examples)
        status('training', completed_examples=0)
        with (OUT / 'training-loss.jsonl').open('w', encoding='utf-8') as log:
            training_start = time.monotonic()
            for i,(r,p,a) in enumerate(examples):
                loss = loss_for(p,a)
                assert torch.isfinite(loss)
                divisor = min(8, len(examples)-(i//8)*8)
                (loss/divisor).backward()
                if (i+1)%8 == 0 or i+1 == len(examples):
                    torch.nn.utils.clip_grad_norm_(params, 1.)
                    opt.step(); opt.zero_grad(set_to_none=True)
                seconds = time.monotonic()-training_start
                log.write(json.dumps({'example': i+1, 'id': r['id'], 'loss': float(loss.detach()),
                                     'training_seconds': seconds})+'\n'); log.flush()
                if (i+1)%8 == 0:
                    status('training', completed_examples=i+1,
                           estimated_training_seconds_left=seconds/(i+1)*(len(examples)-i-1))
                if (i+1)%256 == 0:
                    model.save_pretrained(OUT / 'checkpoint-latest/adapter', safe_serialization=True)
                    torch.save({'optimizer': opt.state_dict(), 'completed_examples': i+1,
                                'torch_rng': torch.get_rng_state(), 'cuda_rng': torch.cuda.get_rng_state_all()},
                               OUT / 'checkpoint-latest/optimizer.pt')
        model.save_pretrained(OUT / 'adapter', safe_serialization=True)
        del opt, loss
        model.eval(); model.gradient_checkpointing_disable()
        status('validation_loss')
        validation = []
        with torch.inference_mode():
            for r in read(OUT / 'data/validation.jsonl'):
                p,a = encode(tok,r)
                validation.append({'id': r['id'], 'tokens': len(a), 'nll': float(loss_for(p,a))})
        metadata(OUT / 'validation-loss.json', {'rows': validation,
            'token_weighted_nll': sum(r['nll']*r['tokens'] for r in validation)/sum(r['tokens'] for r in validation)})
        status('informalizing_test')
        generated = []
        with (OUT / 'generated.jsonl').open('w', encoding='utf-8') as output:
            for r in read(OUT / 'data/test.jsonl'):
                p,_ = encode(tok,r)
                x = torch.tensor([p], device='cuda')
                with torch.inference_mode():
                    y = model.generate(input_ids=x, attention_mask=torch.ones_like(x),
                        do_sample=False, max_new_tokens=1024, use_cache=True,
                        pad_token_id=tok.eos_token_id)
                ids = y[0,len(p):].tolist()
                result = {**r, 'generated_english': tok.decode(ids, skip_special_tokens=True),
                          'generated_tokens': len(ids), 'hit_generation_limit': len(ids)>=1024}
                generated.append(result)
                output.write(json.dumps(result, ensure_ascii=False)+'\n'); output.flush()
                status('informalizing_test', generated=len(generated))
        status('untuned_english_judge')
        yes,no = [tok.encode(s,add_special_tokens=False) for s in ['YES','NO']]
        assert len(yes)==len(no)==1
        judgments = []
        # Frozen base + disabled LoRA is the original untuned model, sharing the
        # single base allocation. No English-pair comparator training occurs.
        with model.disable_adapter(), torch.inference_mode(), (OUT / 'judgments.jsonl').open('w',encoding='utf-8') as output:
            for r in generated:
                payload = {'theorem': r['informal_statement'], 'original_english_proof': r['informal_proof'],
                           'english_account_of_lean': r['generated_english']}
                p = prefix(tok,JUDGE,payload)
                if len(p)>8192:
                    result = {'id': r['id'], 'status': 'too_long', 'match': None}
                else:
                    x = torch.tensor([p],device='cuda')
                    logits = model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False,
                                   logits_to_keep=1).logits[0,-1,[yes[0],no[0]]].float()
                    result = {'id': r['id'], 'status': 'judged', 'match': bool(logits[0]>=logits[1]),
                              'yes_score_uncalibrated': float(logits.softmax(-1)[0]),
                              'generation_hit_limit': r['hit_generation_limit']}
                judgments.append(result)
                output.write(json.dumps(result)+'\n'); output.flush()
                status('untuned_english_judge', judged=len(judgments))
        summary = {'test_rows': len(judgments), 'match_counts': dict(Counter(str(r['match']) for r in judgments)),
                   'generation_limit_count': sum(r['hit_generation_limit'] for r in generated),
                   'interpretation': 'Untuned model judgments, not verified accuracy. A mismatch can originate in the source pair or informalizer.'}
        metadata(OUT / 'summary.json',summary)
        metadata(ROOT / 'reports' / OUT.name / 'summary.json',summary)
        status('complete', peak_vram_gib=torch.cuda.max_memory_allocated()/2**30)
    except BaseException:
        status('failed',error=traceback.format_exc())
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run'])
    args = parser.parse_args()
    prepare() if args.command == 'prepare' else run()
