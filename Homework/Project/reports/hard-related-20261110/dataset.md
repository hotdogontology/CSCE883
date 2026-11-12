# Related-proof dataset, 2026-11-10

The new data pairs English and Lean statements **and proof bodies**. Positive
argument correspondence is assumed from the corrected ProofNet source pairs,
as authorized by the user. Negatives replace the complete English statement and
proof with a different, related source. Their mismatch labels are synthetic
assumptions, not independently verified argument-fidelity annotations.

Swapping the complete English side keeps it internally coherent. The intended
semantic difference is between the English argument/claim and the supplied Lean
argument/claim. This can include different conclusions or assumptions; it does
not isolate subtle differences between two arguments for exactly the same theorem.
The original Lean side remains unchanged and was successfully replayed under
Lean 4.28. Successful compilation does not establish cross-language fidelity.

## Frozen construction

All 365 extracted source pairs were allocated by 335 precomputed exercise and
shared-English-proof families, using seed 884. There were 235 training families,
50 validation families and 50 test families, approximately 70/15/15. Allocation
occurred before context and similarity filtering. No family or shared English
proof crosses the new splits.

The relatedness score is the existing heuristic:

`0.45 English-statement cosine + 0.45 Lean-statement cosine + 0.10 mathlib proof-module cosine`.

The statement components use character TF-IDF; the module component uses the
resolved proof-dependency graph. Vocabulary and IDF are fitted on eligible
training sources only. The fixed threshold is **0.20**. It was fixed before
evaluating any models on the new split; it is not a calibrated semantic threshold.
Validation/test predictions did not determine it. Matching maximizes the number
of retained sources first and total similarity second, with donors confined to
their own split. Sources without a compatible threshold-qualified permutation
are omitted. Every retained English bundle and every retained Lean bundle appears
once in each class, so exact single-side input marginals are balanced.

| Split | Allocated source pairs | Eligible after dependency/context checks | Retained source pairs | Labeled examples | Mean relatedness |
| --- | ---: | ---: | ---: | ---: | ---: |
| Training | 258 | 224 | 183 | 366 (183 yes / 183 no) | 0.3432 |
| Validation | 57 | 48 | 30 | 60 (30 / 30) | 0.2870 |
| Test | 50 | 42 | 27 | 54 (27 / 27) | 0.2973 |

All 365 original Lean targets compile. Dependency expansion is incomplete for
proofnet-53, proofnet-239 and proofnet-328; those three are excluded here. Another
48 sources are excluded because their source or family exceeds the common
4096-token limit. Similarity matching omits a further 74. The final population
contains 240 original pairs and 480 labeled examples. Training-answer tokens
are included in the context check; no inputs are truncated.

## Files and checks

`artifacts/hard-related-20261110/data/{train,validation,test}.jsonl` are the primary
sets. Each row has `source_id`, `group`, `split`, label provenance and the five
model input fields. Negative rows also carry donor provenance and relatedness;
these metadata fields are excluded from model prompts by the existing payload
whitelist. `*-assignment.jsonl`, `split-allocation.jsonl`, `excluded.jsonl` and
the manifest record construction. Raw data remain ignored by Git.

The corresponding `*-proof-only-diagnostic.jsonl` files preserve the previous
proof-only swap transformation using exactly the same donors. They contain the
same 366/60/54 row counts. This is a secondary diagnostic, not additional
independent training data; do not concatenate it into the primary training set.

Seven checks passed with `python scripts/test_hard_related.py`, including
matching coverage/marginal preservation, split isolation, exact source-field
provenance, threshold compliance and detection of deliberately corrupted data.
The builder checks tokenizer lengths and writes hashes for every dataset file.
Rerunning `python scripts/prepare_hard_related.py` verifies the frozen artifacts
instead of replacing them.

## Interpretation

The new test is held out from this fresh adaptation run. This public source
corpus was already used and inspected in prior project experiments, so the test
is not a pristine external benchmark. Use a fresh original Qwen base for new
fine-tuning; the earlier adapter has seen a different allocation of these sources.
Compare new models on the identical frozen test. Comparing its accuracy directly
with the old random-swap score also changes the split and swap transformation.

Report accuracy, mismatch precision/recall/F1, confusion matrices and coverage
against the stated synthetic labels. Distinct source IDs do not prove semantic
inequivalence, and related topics do not guarantee subtle differences. Preserve
the separate same-theorem diagnostic to assess an additional kind of semantic
mismatch; do not use that diagnostic to choose this threshold or training data.
