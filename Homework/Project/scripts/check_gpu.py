"""Exercise CUDA inference, backward propagation, and a 4-bit linear layer."""
import importlib.metadata
import json
import platform

import torch

assert torch.cuda.is_available(), "CUDA is not available"
x = torch.randn(512, 512, device="cuda", dtype=torch.bfloat16, requires_grad=True)
loss = (x @ x.T).float().square().mean()
loss.backward()
torch.cuda.synchronize()
assert x.grad is not None and torch.isfinite(x.grad).all()

import bitsandbytes as bnb

linear = bnb.nn.Linear4bit(64, 32, bias=False, compute_dtype=torch.bfloat16,
                          quant_type="nf4").to("cuda")
batch = torch.randn(2, 64, device="cuda", dtype=torch.bfloat16, requires_grad=True)
linear(batch).float().square().mean().backward()
torch.cuda.synchronize()
assert batch.grad is not None and torch.isfinite(batch.grad).all()

from peft import LoraConfig, TaskType, get_peft_model
from transformers import Qwen3Config, Qwen3ForSequenceClassification

# Random tiny model: checks the training stack without downloading a checkpoint.
config = Qwen3Config(vocab_size=128, hidden_size=64, intermediate_size=128,
                     num_hidden_layers=2, num_attention_heads=4,
                     num_key_value_heads=2, head_dim=16,
                     max_position_embeddings=128, num_labels=2, pad_token_id=0)
model = get_peft_model(Qwen3ForSequenceClassification(config), LoraConfig(
    task_type=TaskType.SEQ_CLS, r=4, lora_alpha=8,
    target_modules=["q_proj", "v_proj"], modules_to_save=["score"])).to("cuda")
optimizer = torch.optim.AdamW(p for p in model.parameters() if p.requires_grad)
output = model(input_ids=torch.randint(1, 128, (2, 32), device="cuda"),
               labels=torch.tensor([0, 1], device="cuda"))
assert torch.isfinite(output.loss)
output.loss.backward()
assert any(p.grad is not None and torch.count_nonzero(p.grad).item() > 0
           for name, p in model.named_parameters() if "lora_B" in name)
optimizer.step()
torch.cuda.synchronize()

packages = ["torch", "transformers", "accelerate", "peft", "trl", "bitsandbytes",
            "datasets", "huggingface-hub", "scikit-learn", "jupyterlab"]
print(json.dumps({
    "python": platform.python_version(),
    "packages": {name: importlib.metadata.version(name) for name in packages},
    "cuda_runtime": torch.version.cuda,
    "gpu": torch.cuda.get_device_name(0),
    "vram_gib": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2),
    "compute_capability": torch.cuda.get_device_capability(0),
    "bf16_supported": torch.cuda.is_bf16_supported(),
    "bf16_forward_backward": "passed",
    "nf4_forward_backward": "passed",
    "tiny_random_qwen3_lora_classification_step": "passed",
}, indent=2))
