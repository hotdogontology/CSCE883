# Proof-body correspondence experiment

Authorized 2026-11-09. Preserve the completed 8B statement-only experiment and its
metrics unchanged. The new task judges whether an English proof argument matches
the Lean proof body, including the statement and required context. **No second
pass or Herald pseudo-label training is included.**

## Model and precision

Selected Qwen/Qwen3-14B, pinned in `model-manifest-14b.json`, original safetensors
download about 27.52 GiB. Load the entire base model onto the RTX A6000 at BF16.
No 4-bit, 8-bit, NF4 or other quantization is used; adapters are ordinary LoRA.
BF16 is floating-point precision, not the integer/low-bit quantization previously
used for the 8B run. The loader asserts unquantized BF16 base weights.

14B is the largest practical standard dense Qwen3 option for a fully GPU-resident
unquantized comparison on this 48 GiB GPU: 32B BF16 weights alone exceed VRAM.
CPU offloading could allow larger models but is not part of this experiment.
Training memory feasibility is to be measured, not inferred from weight size.
Probe a forward/backward/optimizer step on the longest retained training input,
trying 8192, 4096, then 2048 tokens only if the larger budget OOMs. Freeze the
first successful budget for training and both model comparisons. Never fall
back to quantization automatically and never truncate a proof silently.

## Data and label assumptions

At the user's explicit direction, treat corrected ProofNet-V English/Lean proof
pairs as positive **argument** matches. This is a working dataset assumption,
not a newly established independent argument audit.

Extracted 361 candidate source pairs from the pinned Lean 4.28 archive. Six are
excluded because a unique target or safe dependency context could not be
isolated: indices 110, 161, 168, 254, 265, 367. Full reasons are recorded in the
ignored data manifest. Source inspection is not local Lean replay.

Remove all English comments/docstrings from formal code, including nested Lean
comments, and exclude obsolete admitted target declarations and refutations.
Select the corrected declaration (including `_root_.`-qualified targets), retain
context, split its statement from its actual proof body. Reject admitted target
bodies and contexts with admitted declarations. Never feed the placeholder
`formal_proof` dataset string or a `by sorry` template as a completed proof.

Payload fields are **informal_statement, informal_proof, formal_statement,
formal_proof, context**. Label/rationale/source fields are not model inputs.

Split original problems 80/20 with seed 883 before constructing negatives.
Both variants of a problem stay together, and negative donors stay within their
own split. Selected dataset: 578 training pairs (289 positive, 289 constructed
negative), 144 validation pairs (72 positive, 72 constructed negative), before
token-budget filtering. No proof body crosses the train/validation split by
negative construction. Broader semantic/theorem-family overlap still needs review.

Each negative keeps the anchor's English statement, Lean statement, Lean proof
and context identical, replacing only the English proof with a different source
problem's English proof. Donors form a derangement: every English proof appears
once in each class. Exact statement-only or single-proof-only inputs cannot
distinguish these complete balanced pairs. Filter pairs together if either
variant exceeds the context budget; record coverage and exclusions.

**Limitation:** these are constructed cross-problem negatives. They test whether
the model detects an unrelated argument; they do not establish discrimination
between subtle alternative arguments proving the same theorem. A later hard-
negative experiment is required for that claim. User-assumed positives and
constructed negatives are reported separately from human-audited labels.

## Execution

The sequential driver waits for the hash-verified download, probes BF16 training
memory, evaluates untuned 14B on validation, trains fresh original 14B with LoRA,
evaluates tuned 14B on the same validation, then runs **both** on all 44,553 Herald
proof pairs. No labels are assigned to Herald as ground truth and no further
training is triggered by those predictions.

LoRA: q/k/v/o projections, rank 16, alpha 32, dropout 0.05; seed 883; AdamW 1e-4;
one epoch; batch one, accumulation eight; gradient checkpointing. Train only
YES/NO answer and end-of-answer loss. Retain output logits only for answer
positions to reduce memory without dropping proof inputs. Save recovery
checkpoints every 128 examples and a final adapter; recovery is manual.

Inference: fixed nonthinking prompt, constrained next-token YES/NO comparison,
BF16 base, no quantization. Missing/extraction/length/OOM cases are missing
predictions, never NO. All proof inputs and prompts are reproducible from pinned
data hashes; scores are uncalibrated.

Report accuracy, both classes' precision/recall/F1, macro/weighted F1, balanced
accuracy and coverage on constructed validation. Report Herald decisions,
coverage and model disagreements, without accuracy claims. Do not compare the
new task's scores directly to 8B statement metrics as evidence of a model-size
effect: both task/input and model size changed.

## Files and status

Tracked source: `scripts/argument_data.py`, `scripts/argument_model.py`,
`scripts/run_argument_experiment.py`, `scripts/test_argument_experiment.py`,
`prompts/argument-v1.txt`, `model-manifest-14b.json`.

Local data: `artifacts/argument-14b/data-v3/` (v1/v2 preparation attempts are not
the active dataset). Local state: `artifacts/argument-14b/job.json`; PID in
`job.pid`; stage logs and checkpoints in that directory. Aggregate reports:
`reports/argument-14b/`. The driver holds a temporary Windows execution request
and stops on failure. It does not attempt GitHub pushes.

At setup time the download is still running; no 14B probe, training or accuracy
result is claimed. Fifteen existing/data guard tests passed. Consult live job
state and model manifest for later completion rather than assuming queued stages ran.
