# First Herald informalization run

Authorized November 12: stop the 32B classifier training attempt; fine-tune
Qwen3-14B to informalize Lean proofs; have original untuned Qwen3-14B compare the
resulting English with the original English. Stage two is not fine-tuned here.

## Resources and preserved work

Stopped Python worker 34108 (32B gradient probe), verified its launcher exited,
and marked its job stopped_by_user. Pretrained predictions/metrics remain under
artifacts/source-balanced-20261112/qwen32. No completed training steps existed.
The 32B base stays available for inference. Disk inspection found 3.68 TB free;
all existing LoRA adapter files together occupy about 4.02 GB. No deletion needed.

## Data and training

Use original Herald proof pairs from the corrected data-v4 extraction. Inputs
contain only formal statement, formal proof body and context. English proof text
is the supervised completion; no binary labels, swaps, classifier predictions or
source English in the translator's input. The English theorem is available only
to the subsequent judge as context.

Group namespace families, duplicate normalized English proofs and duplicate
normalized formal signatures into connected components before splitting.
Assign components deterministically to 90/5/5 train/validation/test hash buckets.
Exclude exact ProofNet English-proof/signature overlaps to preserve ProofNet as
a future external candidate; this does not certify absence of conceptual overlap.
Select seeded subsets of 4,096 training, 64 validation and 64 test examples for
this first run. Full-corpus training is not claimed. Log unused eligible rows and
exclusions. Maximum 2,048 total training tokens and 1,024 target tokens; exclude
oversized examples rather than silently truncate them. This biases coverage
toward shorter proofs and must accompany results.

Fresh Qwen3-14B pinned base, BF16 entirely on the A6000, no quantization. New rank
16 LoRA, alpha 32, dropout .05, q/k/v/o projections, one epoch, learning rate 1e-4,
gradient accumulation 8. Supervise English completion tokens only. Check a
longest-example finite-gradient probe first. Log every training example and
refresh status/ETA every 8 examples. Keep one rolling checkpoint every 256
examples plus final adapter; do not merge or duplicate base weights.

## Automatic post-training stages

1. Compute validation English completion loss on the 64 validation pairs.
2. Generate English from each of the 64 held-out Lean inputs, using the trained
   adapter, greedy decoding and a 1,024-token output budget. Save all generations
   and explicit output-limit flags.
3. Disable the trained adapter, returning to the frozen original base, and judge
   original English versus generated English. The judge receives no Lean code.
   Use constrained YES/NO next-token comparison for argument correspondence;
   save the uncalibrated score and per-pair result.

These are model assessments of correspondence, not verified accuracy. Generated
English is a fallible intermediary: a mismatch can originate in the source pair
or translator. Keep that attribution unresolved without inspecting Lean. The
same-theorem proof-route objective remains; mere correctness/topic overlap does
not define a match. Human-readable English outputs also have independent value.

## Embedding question

English proof embeddings can supply an additional similarity baseline. Normalize
vectors and take their dot product (cosine similarity) to avoid vector norm
dominating the score. The result is not a calibrated faithfulness probability;
small changes in quantifiers, witnesses or inference may leave cosine similarity
high. A threshold requires separately labeled validation pairs. No embedding
model or embedding threshold is included in this initial run.

## Reproduction and status

Runner: scripts/informalization_pipeline.py (prepare, then run).
Exact split fingerprints: reports/informalization-14b-20261112/data-manifest.json.
Live status/logs/checkpoints: artifacts/informalization-14b-20261112/.
The output directory is protected against accidental rerunning/overwriting.
Inspect job.json for actual progress, not this planning document.

Launch verified at 16:22 Eastern: longest training example 1,992 tokens passed
the finite-gradient check in 4.08 seconds; 27 training examples completed, GPU
utilization 99%. Initial training estimate approximately 70 minutes, excluding
generation and judging. Selected groups, English proof texts and normalized
signatures are disjoint across all three splits. Syntax compilation passed.
