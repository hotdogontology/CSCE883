# Overnight run — 2026-11-09

User authorized continuing the next stage while away. The 14B download is
complete and hash-verified. The corrected run is active at
`artifacts/argument-14b/overnight-20261109/job.json`; aggregate reports are in
[reports/argument-14b-overnight/README.md](reports/argument-14b-overnight/README.md).
Read their timestamps for the current stage; this note records setup, not a
promise that queued stages finished.

## Corrections completed before restart

- Source-signature matching fixes all 99 known Herald type/proof-boundary errors
  and ProofNet-289. All 44,553 Herald signatures now agree with source templates.
- Genuine helpers 60/185/257 are retained; obsolete original declarations and
  refutations are omitted conservatively. Dependencies are checked in both
  context and target. Two unsafe/unclear ProofNet cases remain explicitly excluded.
- Exercise families and identical English proofs are union-grouped before
  splitting. The earlier train324/validation141 leakage is gone.
- Data-v4 has 365 assumed positive source pairs, producing 588 train / 142
  validation rows before token filtering. Historical v3 remains intact.
- Token-specific preparation regenerates swaps after filtering. Actual 4096-token
  data contain **510 training rows / 118 validation rows**, with balanced classes
  and equal English-proof marginals. No proof is truncated.
- Completed-stage reuse now checks input, prompt, model, adapter, token budget and
  implementation fingerprints; the run uses a fresh output directory and rejects
  duplicate GPU workers.

Data checks cover source signatures, admissions/references and split integrity;
full local Lean 4.28 corpus replay has not been performed. Corrected ProofNet
argument correspondence remains the user's explicit working assumption.

## Proof-route diagnostic added

Constructed four theorem families with two different valid proof routes each:
odd sums (induction/telescoping), consecutive-product evenness (induction/parity),
a real cubic root (explicit witness/intermediate value theorem), and power
divisibility (induction/geometric sum). Cross each English route with both Lean
routes: 16 pairs, eight YES/eight NO.

All eight source proofs and the exact normalized Lean model payloads compiled in
Lean 4.11. Axiom reports contain no `sorryAx`. Statements and context are literal
constants within each matrix; either side alone occurs with both labels.
The formal-proof-masked control is also frozen. These are **agent-constructed,
unreviewed diagnostic cases**, not a representative independent benchmark, and
are not used for training or prompt/threshold selection.

Source: `lean/ArgumentCore.lean`, `scripts/prepare_argument_core.py`.
Frozen inputs/provenance: `artifacts/argument-14b/core/`.
Masked regeneration: `scripts/prepare_argument_masked.py`.

## Precision, resource measurement and queued stages

Qwen3-14B runs entirely on GPU in BF16, without quantization. Ordinary LoRA:
rank 16, alpha 32, attention q/k/v/o modules, one epoch, seed 883. No second pass.

The 8192-token probe exceeded a 240-second resource limit while GPU memory was
observed near capacity; the installed Windows PyTorch lacks compiled FlashAttention.
The attempt was archived, not described as a successful run or mathematical failure.
The 4096-token probe passed on a 3946-token input, including backward/optimizer,
in **32.82 seconds**, peak allocated VRAM **39.11 GiB**. This common budget is
fixed for training and both model comparisons; long inputs become missing records.

Pipeline: CPU English-only control -> untuned proof-swap validation -> untuned
same-theorem core -> untuned masked core -> fresh-base LoRA -> tuned validation
and both core controls -> untuned Herald -> tuned Herald, all sequentially.

The swap task remains a coarse proof-consistency pilot with a known English-only
shortcut. Judge argument-route behavior using the separate same-theorem diagnostic,
with its small constructed-sample limitation. Herald has no independent labels:
report coverage/decisions/disagreements, not accuracy. Earlier 8B statement results
and self-training results remain unchanged in `artifacts/two-pass/`.

Twenty-four CPU regression/guard tests passed before launch. The core Lean build
and the real 14B memory probe are additional checks. The driver holds a temporary
Windows execution request and stops on a failed stage. Check local logs before
restarting; interrupted training recovery remains manual. No GitHub push is
assumed; the prior authentication/write-access issue remains unresolved.

The user requested Light/Medium thinking. No tool in this session can change the
active app/model effort setting; no unrelated global configuration was changed.
