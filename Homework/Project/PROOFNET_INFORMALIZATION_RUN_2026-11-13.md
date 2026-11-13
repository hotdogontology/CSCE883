# ProofNet informalization run

User requested a fresh two-stage run with ProofNet rather than Herald supervision.
Runner: `scripts/proofnet_informalization_pipeline.py`.
Output: `artifacts/informalization-proofnet-14b-20261113`.
Data manifest: `reports/informalization-proofnet-14b-20261113/data-manifest.json`.

## Training

Fresh base Qwen3-14B, not the Herald adapter. Use existing corrected ProofNet
pairs with Lean proof bodies, treating original argument correspondence as the
project's working assumption. Lean statement/proof/context is the input; original
English proof is the completion target. No swapped negatives train the translator.

Reuse the frozen related-proof 70/15/15 family allocation. Consider all original
allocated training pairs rather than restricting training to anchors that found
a related swap. Preserve the Herald run's total-token limit of 2,048 and target
limit of 1,024; exclude oversized examples, never truncate. This leaves **176
training and 36 validation pairs**. Assertions check disjoint family IDs and
normalized English/Lean proof texts across training, validation and evaluation.

Keep prior settings: BF16, rank-16 LoRA on q/k/v/o, alpha 32, dropout .05,
learning rate 1e-4, accumulation 8, one epoch. Original base English judge,
with adapter disabled during judging. The judge is not fine-tuned.

## Automatic evaluation sequence

1. Completion loss on the 36 validation pairs.
2. Informalize and judge the existing **54 related-swap test pairs** (27 assumed
   source matches, 27 constructed mismatches). Test labels do not enter model
   prompts. Record coverage, mismatch precision/recall/F1 and confusion matrix;
   output-limit hits are abstentions for classification metrics. Preserve the
   raw judge outputs even for those cases.
3. Repeat the two pinned OpenAI subarguments with the new adapter, in separate
   `artifacts/openai-proofnet-informalization-20261113` output. Same source
   selection and prompts as the Herald-adapter case study. Record explanations
   independently of the constrained YES/NO decision.

The standalone worker uses a hidden window and logs stdout/stderr in the training
output directory. `worker.pid`, `job.json`, and `training-loss.jsonl` allow progress
checks. After the training/evaluation job is complete, inspect the separate
external `job.json` to determine whether the entire sequence has finished.

## Interpretation

Training-set size differs substantially from Herald's 4,096 examples. This is
not a controlled equal-size comparison of data sources. The held-out ProofNet
test has been inspected in earlier experiments, and its correspondence labels
are assumed/synthetic. Comparing to the older untuned intermediary also requires
acknowledging prompt/protocol differences and generation coverage; no direct
classifier baseline is added. Original and newly generated artifacts remain
separate. Assess explanation quality as well as binary labels on OpenAI cases.
