# Downloaded reference datasets

Downloaded 2026-11-06 using `scripts/download_verified_data.py`. Full source
snapshots and original labels are preserved in ignored `data/`; tracked
`verified-data-manifest.json` records immutable commits, file sizes, SHA256
checksums, JSONL schemas and counts. These are reference/evaluation candidates,
not an assigned training set. No local Lean replay has been performed.

## ProofNet-Verified

Base: `data/proofnet-verified/14879cb23e078d122adecd9578dd26a7304f753b/source/`

- `data/proofnet-verified-latest.jsonl`: 367 corrected examples, latest statements.
- `data/archive/proofnet-verified-4.28.jsonl`: matching archived statement snapshot.
- `data/archive/proofnet-verified_gt-4.28.zip`: 367 completed Lean proof files.
- `error_taxonomy/proofnet/results.jsonl` and `error_taxonomy/proofnet#/results.jsonl`:
  original-version statement audits, not argument-fidelity annotations.
- `README.md`, `LICENSE`, toolchain/build files: upstream provenance/environment.

Use archived pairs/proofs together when investigating the verified Lean 4.28
snapshot. Do not upgrade the existing Herald environment. JSONL `formal_proof`
is a placeholder; `formal_stmt` has a sorry template. Completed proofs must come
from the proof archive. Audited statement correspondence does not certify that
the formal proof follows the English argument. License: Apache-2.0 upstream.

## FaithSieve / ProofLoc

Base: `data/faithsieve/7df6da7fd7661d69fe875673f06770d260e4fd12/source/`

- `datasets/proofloc_olympiad/data/test.jsonl`: 350 examples; 145 correct, 205 with errors.
- `datasets/proofloc_university/data/test.jsonl`: 200 examples; 130 correct, 70 with errors.
- Each directory includes its upstream dataset card, manifest and formatting requirements.

Actual fields: `id`, `problem`, `steps`, `first_error_step`. A correct proof has
`first_error_step = "correct"`; otherwise this identifies the first erroneous
step. These files contain no Lean counterpart and no English/Lean match label.
The paper's separate 135-pair semantic-gate human audit is not in this snapshot.
No explicit LICENSE file appears in the repository snapshot; retain attribution
and establish dataset reuse terms before redistribution.

## How Qwen can become a binary classifier

An LLM can supply the language-understanding backbone of a binary classifier.
We do not need to train language understanding from scratch.

One proposed route is to present the English/Lean pair with a fixed instruction
and train Qwen to output `YES` or `NO`. During supervised training, the loss
penalizes the wrong target answer. LoRA freezes the pretrained base weights and
trains small adapter matrices inside the model. At inference, load the same
base model plus the saved adapter and judge unseen pairs. A second route replaces
the answer-generation output with a small binary classification head and trains
that head alongside LoRA. Both routes yield a binary classifier backed by an LLM.

The proposed first comparison is current zero-shot Qwen versus LoRA-tuned Qwen
with YES/NO targets. No task training is started or architecture change finalized
by downloading these datasets. We still need trustworthy labels for the intended
argument-fidelity task, including genuine mismatches. FaithSieve correctness
labels cannot stand in for match labels; ProofNet-V's statement labels support an
auxiliary task. Do not treat our previous predictions as independently verified
training answers. Reserve evaluation families and check overlap before training.

Reference: [Hugging Face PEFT LoRA guide](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora).
