# Qwen3-32B and ProofFlow comparison

Authorized 2026-11-11: download Qwen3-32B and compare pretrained and tuned
models using ProofFlow. Preserve the English–Lean argument-fidelity objective
and the user's unquantized preference.

## Current execution

- Download launched with scripts/download_model.py, PID 33988 at launch.
- Model: Qwen/Qwen3-32B, revision
  9216db5781bf21249d130ec9da846c4624c16137, 61.04 GiB selected files.
- Manifest: qwen32-model-manifest.json. Its download_complete flag becomes
  true only after all sizes and published LFS SHA-256 hashes pass verification.
- Logs: artifacts/qwen32-proofflow/download.stdout.log and download.stderr.log.
- Model weights remain under ignored data/models/Qwen3-32B.
- ProofFlow release audit: scripts/audit_proofflow_release.py downloads pinned
  JSON files only, checks Git blob hashes, and retains semantic labels as null.
  Pinned source: 97f1b7be82380733fb0380973c164e40645ae9da.

## New evidence

Release audit completed: all 737 JSON files downloaded and Git-blob hashes
verified (736 result artifacts plus main benchmark). Initial extractor recovered
366 full English–Lean pairs across 184 source groups. Upstream reports 31 passing
and 335 failing compilation; these are not local replays or fidelity labels.
The remaining 368 result files have a step-based schema (final_lean_code,
proof_steps, generated_steps) requiring a separate join to source English before
inclusion. Two full-proof-schema files did not supply both required pair fields.
Audit: reports/proofflow32/release-audit.json. Extracted pairs remain ignored at
data/proofflow/97f1b7be82380733fb0380973c164e40645ae9da/pairs-unlabeled.jsonl.

Beyond the 184-row English/graph benchmark, the upstream repository contains
736 JSON result artifacts. Inspected examples include original_theorem,
original_proof, and Lean_results.lean_code, with compilation results and attempt
histories. These supply paired materials, not verified argument labels. A failed
Lean compilation is not automatically an unfaithful mathematical translation;
a successful one is not automatically faithful.

## Pending methodological choice

An asynchronous question asks whether to train on existing labeled project data
and use ProofFlow as an external unlabeled test, or to build a ProofFlow training
set with explicitly provisional semantic labels. Await the user's answer before
dependent training. No labels have been manufactured from compilation flags.

If training on ProofFlow, group all attempts/model variants of a source problem
together, audit near-duplicates and source/proof alignment, split before training,
and record label evidence. Evaluate base and adapter on identical held-out pairs.
Accuracy/precision/recall/F1 require justified reference labels; otherwise report
prediction differences and acceptance rates without calling them accuracy.

## Runtime requirements

The existing argument_model.py forces the entire model onto GPU and cannot be
used unchanged for 32B. BF16 base weights exceed 48 GiB VRAM. Inference needs
explicit CPU/GPU placement and context memory headroom. Training needs its own
tested offload implementation; Accelerate inference dispatch is not evidence
that backward/optimizer steps are supported. A finite-loss forward/backward/
optimizer probe must pass before any full LoRA run. No quantization is authorized
by this request, and no 32B training or evaluation result exists yet.
