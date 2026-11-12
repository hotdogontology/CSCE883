"""BF16 static CPU/GPU model parallel pilot: base, backward probe, LoRA, tuned.

Weights remain on their assigned device. Tensor copies preserve autograd;
no inference-only CPU-offload hooks, quantization, or disk weight swapping.
"""
import json
import time
import traceback
from pathlib import Path
import random
import hashlib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'artifacts/source-balanced-20261112/data'
OUT = ROOT / 'artifacts/source-balanced-20261112/qwen32'
PROMPT = ('Decide whether the English mathematics and Lean faithfully correspond. '
          'Preserve assumptions, domains, conclusions and essential inference steps. '
          'Equivalent presentations and routine formal elaboration are allowed. '
          'For a local step whose Lean body is a placeholder, assess its hypotheses and '
          'conclusion against the English inference, not whether the placeholder compiles. '
          'For a complete proof, also compare its essential argument. '
          'A true statement or a valid Lean proof alone does not establish correspondence. '
          'Answer only YES for faithful correspondence or NO for a semantic mismatch.')


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig, get_peft_model
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
    OUT.mkdir(parents=True, exist_ok=False)
    started = time.time()
    state = {'status': 'loading', 'precision': 'BF16 unquantized', 'seed': 883,
             'label_caution': 'Provisional mixed-scope pilot; not human-verified semantic benchmark',
             'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'prompt': PROMPT}
    save('job.json', state)
    try:
        torch.manual_seed(883); random.seed(883); torch.set_num_threads(8)
        manifest = json.loads((ROOT / 'qwen32-model-manifest.json').read_text())
        assert manifest['download_complete']
        path = ROOT / manifest['local_directory']
        tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
        rows = {s: [json.loads(x) for x in (DATA / (s + '.jsonl')).read_text(encoding='utf-8').splitlines()]
                for s in ('train', 'validation', 'test')}
        encoded = {}
        for split, records in rows.items():
            for r in records:
                ids = tokenizer.apply_chat_template([{'role': 'system', 'content': PROMPT},
                     {'role': 'user', 'content': json.dumps(r['input'], ensure_ascii=False)}],
                     tokenize=True, return_dict=False, add_generation_prompt=True, enable_thinking=False)
                assert isinstance(ids, list) and all(isinstance(i, int) for i in ids)
                assert len(ids) <= 4096, ('No silent truncation', r['id'], len(ids))
                encoded[r['id']] = ids
        state['max_tokens'] = max(map(len, encoded.values()))
        state['dataset_hashes'] = {s: hashlib.sha256((DATA / (s + '.jsonl')).read_bytes()).hexdigest() for s in rows}
        save('job.json', state)
        model = AutoModelForCausalLM.from_pretrained(path, local_files_only=True,
                   trust_remote_code=False, use_safetensors=True, dtype=torch.bfloat16,
                   device_map={'': 'cpu'}, attn_implementation='sdpa')
        assert not getattr(model, 'is_quantized', False)
        assert all(p.dtype == torch.bfloat16 for p in model.parameters())
        model.config.use_cache = False
        # Contiguous GPU prefix, CPU suffix. Output head on GPU for loss/logits.
        def size(module): return sum(p.numel() * p.element_size() for p in module.parameters())
        used = sum(size(m) for m in (model.model.embed_tokens, model.model.norm, model.lm_head))
        model.model.embed_tokens.to('cuda'); model.model.rotary_emb.to('cuda')
        model.model.norm.to('cuda'); model.lm_head.to('cuda')
        gpu_layers = 0
        for layer in model.model.layers:
            if used + size(layer) <= 35 * 2**30:
                used += size(layer); layer.to('cuda'); gpu_layers += 1
            else: break
        def move(value, device):
            if torch.is_tensor(value): return value.to(device)
            if isinstance(value, tuple): return tuple(move(v, device) for v in value)
            if isinstance(value, list): return [move(v, device) for v in value]
            if isinstance(value, dict): return {k: move(v, device) for k, v in value.items()}
            return value
        def placement_hook(module, args, kwargs):
            device = next(module.parameters()).device
            return move(args, device), move(kwargs, device)
        for module in [*model.model.layers, model.model.norm, model.lm_head]:
            module.register_forward_pre_hook(placement_hook, with_kwargs=True)
        state.update(status='base_evaluation', gpu_layers=gpu_layers, layers=len(model.model.layers),
                     base_revision=manifest['revision'])
        save('job.json', state)
        yes = tokenizer.encode('YES', add_special_tokens=False); no = tokenizer.encode('NO', add_special_tokens=False)
        assert len(yes) == len(no) == 1

        def evaluate(tag):
            model.eval(); results = {}
            for split in ('validation', 'test'):
                predictions = []
                for r in rows[split]:
                    x = torch.tensor([encoded[r['id']]], device='cuda')
                    with torch.inference_mode():
                        logits = model(input_ids=x, use_cache=False, logits_to_keep=1).logits[0, -1, [yes[0], no[0]]].float()
                    predictions.append({'id': r['id'], 'prediction': bool(logits[0] >= logits[1]),
                                        'yes_score_uncalibrated': float(logits.softmax(-1)[0])})
                    save(f'{tag}-{split}-predictions.json', predictions)
                groups = {}
                for source in ('all', 'proofnet', 'faithform'):
                    indices = [i for i, r in enumerate(rows[split]) if source == 'all' or r['source'] == source]
                    y = [not rows[split][i]['label'] for i in indices]
                    p = [not predictions[i]['prediction'] for i in indices]
                    pr, rc, f1, _ = precision_recall_fscore_support(y, p, average='binary', zero_division=0)
                    groups[source] = {'n': len(y), 'accuracy': accuracy_score(y, p),
                                      'mismatch_precision': pr, 'mismatch_recall': rc, 'mismatch_f1': f1,
                                      'confusion_matrix_match_then_mismatch': confusion_matrix(y, p, labels=[False, True]).tolist()}
                results[split] = groups
            save(tag + '-metrics.json', results)

        evaluate('pretrained')
        model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=.05,
                     target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'], task_type='CAUSAL_LM'))
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
        model.enable_input_require_grads()
        model.train()
        def loss_for(r):
            ids = encoded[r['id']]
            x = torch.tensor([ids], device='cuda')
            logits = model(input_ids=x, use_cache=False, logits_to_keep=1).logits[0, -1].float()
            return torch.nn.functional.cross_entropy(logits.unsqueeze(0),
                   torch.tensor([yes[0] if r['label'] else no[0]], device=logits.device))
        trainable = [p for p in model.parameters() if p.requires_grad]
        state['status'] = 'backward_probe'; save('job.json', state)
        probe = max(rows['train'], key=lambda r: len(encoded[r['id']]))
        loss = loss_for(probe); assert torch.isfinite(loss); loss.backward()
        gradients = [p.grad for p in trainable if p.grad is not None]
        assert len(gradients) == len(trainable) and all(torch.isfinite(g).all() for g in gradients)
        # Verify an optimizer step, then restore adapter tensors before real training.
        before = [p.detach().cpu().clone() for p in trainable]
        optimizer = torch.optim.AdamW(trainable, lr=1e-4)
        optimizer.step()
        assert all(torch.isfinite(p).all() for p in trainable)
        with torch.no_grad():
            for p, original in zip(trainable, before): p.copy_(original.to(p.device))
        del before, optimizer
        model.zero_grad(set_to_none=True)
        save('probe.json', {'status': 'passed', 'loss': float(loss.detach()),
                           'gradient_tensors': len(gradients), 'trainable_tensors': len(trainable),
                           'gpu_peak_gib': torch.cuda.max_memory_allocated()/2**30})
        del gradients, loss
        state['status'] = 'training'; save('job.json', state)
        torch.manual_seed(883)
        optimizer = torch.optim.AdamW(trainable, lr=1e-4)
        training = list(rows['train']); random.shuffle(training); history = []
        for i, r in enumerate(training):
            loss = loss_for(r); assert torch.isfinite(loss)
            (loss / 4).backward()
            if (i+1) % 4 == 0:
                torch.nn.utils.clip_grad_norm_(trainable, 1.0)
                optimizer.step(); optimizer.zero_grad(set_to_none=True)
            history.append({'id': r['id'], 'loss': float(loss.detach())})
            save('training.json', {'epochs': 1, 'learning_rate': 1e-4, 'rank': 16,
                                   'gradient_accumulation': 4, 'rows': history})
            print(f'Trained {i+1}/{len(training)}', flush=True)
        model.save_pretrained(OUT / 'adapter', safe_serialization=True)
        del optimizer
        evaluate('tuned')
        state.update(status='complete', seconds=time.time()-started,
                     gpu_peak_gib=torch.cuda.max_memory_allocated()/2**30)
        save('job.json', state)
    except Exception:
        state.update(status='failed', error=traceback.format_exc(), seconds=time.time()-started)
        save('job.json', state)
        raise


if __name__ == '__main__': main()
