# Workstation setup verification

Verified on 2026-11-06, native Windows, NVIDIA RTX A6000 (47.99 GiB reported by
PyTorch), compute capability 8.6. Python 3.12.10; PyTorch 2.11.0+cu128 with CUDA
runtime 12.8. Exact Python dependencies are in `requirements-lock-windows.txt`.

Passed:

- Python dependency consistency (`pip check`).
- CUDA BF16 matrix computation and backward propagation with finite gradients.
- bitsandbytes NF4 linear layer forward/backward on CUDA.
- A tiny randomly initialized Qwen3 sequence classifier with PEFT LoRA:
  supervised loss, nonzero adapter gradients, and an optimizer step on CUDA.
  This is a software integration test, not model selection or a research result.
- Lean 4.11.0 / Lake, pinned Mathlib, and project `lake build`.
- The smoke theorem reports only `propext` as an axiom.
- Replaying Herald row 0 with its header and completed proof, under a fresh
  declaration name; printed axioms: `propext`, `Quot.sound`.
- Download and structural audit of all 44,553 Herald Proofs rows at the pinned
  dataset revision. Thirty unlabeled review pairs are in
  `data/herald/review-unlabeled.jsonl`.

Installed VS Code extensions: Lean 4, Python, Jupyter, and their dependencies.
Registered notebook kernel: `csce883-correspondence` (display name
`CSCE883 correspondence`). Microsoft Visual C++ x64 runtime installed for Torch.

The stack is native Windows; WSL2, vLLM, FlashAttention, and a standalone CUDA
Toolkit were not installed. Windows emitted optional Triton flop-counting and
distributed-output-redirection warnings during imports; the tested CUDA and
LoRA operations passed. Qwen3-8B was subsequently downloaded and tested as below;
no project fine-tuning has been performed.

## First pretrained model

Qwen/Qwen3-8B, revision `b968826d9c46dd6066d109eabc6255188de91218`, is
downloaded under ignored `data/models/Qwen3-8B/`. All selected file sizes and
published LFS SHA-256 hashes passed verification. The trackable
`model-manifest.json` records the source revision, files, sizes and hashes.

`scripts/run_model.py` loaded local safetensors on the A6000 in BF16 with remote
code disabled and produced `READY` for the readiness prompt. Measured load:
10.28 seconds; generation: 0.46 seconds for 2 tokens; peak allocated CUDA memory:
15.27 GiB. These are smoke-test measurements, not proof-task performance or
representative long-context throughput. The latest report is stored in ignored
`artifacts/last-model-run.json`.

No corpus-wide compilation, semantic-label validation, calibration experiment,
or model benchmark has been run. The replay does not establish absence of
circular dependencies on the imported original theorem. See `methodology.md`.
