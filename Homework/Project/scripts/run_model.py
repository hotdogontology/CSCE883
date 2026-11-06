"""Run the locally downloaded checkpoint; no network access or training required."""
import argparse
import json
from pathlib import Path
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--prompt", default="Reply with exactly the single word READY.")
parser.add_argument("--max-new-tokens", type=int, default=32)
args = parser.parse_args()
assert args.max_new_tokens > 0
manifest = json.loads((ROOT / "model-manifest.json").read_text(encoding="utf-8"))
assert manifest["download_complete"], "Run scripts/download_model.py first"
assert torch.cuda.is_available(), "A CUDA GPU is required for this configuration"
path = ROOT / manifest["local_directory"]
started = time.perf_counter()
tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
model = AutoModelForCausalLM.from_pretrained(
    path, local_files_only=True, trust_remote_code=False, use_safetensors=True,
    dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="sdpa")
model.eval()
load_seconds = time.perf_counter() - started
encoded = tokenizer.apply_chat_template(
    [{"role": "user", "content": args.prompt}], tokenize=True,
    add_generation_prompt=True, enable_thinking=False,
    return_dict=True, return_tensors="pt").to("cuda")
started = time.perf_counter()
with torch.inference_mode():
    generated = model.generate(**encoded, max_new_tokens=args.max_new_tokens,
                               do_sample=False, pad_token_id=tokenizer.eos_token_id)
torch.cuda.synchronize()
reply = tokenizer.decode(generated[0, encoded["input_ids"].shape[-1]:],
                         skip_special_tokens=True).strip()
assert reply, "Model produced no text"
report = {
    "repo_id": manifest["repo_id"], "revision": manifest["revision"],
    "gpu": torch.cuda.get_device_name(0), "dtype": str(model.dtype),
    "load_seconds": round(load_seconds, 2),
    "generation_seconds": round(time.perf_counter() - started, 2),
    "input_tokens": encoded["input_ids"].shape[-1],
    "output_tokens": generated.shape[-1] - encoded["input_ids"].shape[-1],
    "peak_allocated_vram_gib": round(torch.cuda.max_memory_allocated() / 2**30, 2),
    "reply": reply,
}
artifacts = ROOT / "artifacts"
artifacts.mkdir(exist_ok=True)
(artifacts / "last-model-run.json").write_text(json.dumps(report, indent=2) + "\n",
                                               encoding="utf-8")
print(json.dumps(report, indent=2), flush=True)
