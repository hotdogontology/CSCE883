# Related proofs and translation intermediaries: 2026-11-10

**Completed:** all8stages finishedNovember10 at21:19 Eastern. Results were
reviewedNovember11 in `RESULTS_2026-11-11.md`. Launch notes below are historical;
the saved job state and completed stage reports are authoritative.

The user authorized this stage before leaving for the night. The connection
interruption happened before execution; work resumed after the connection test.
Earlier experiment outputs are preserved. This is a fresh experiment starting
from the original, unquantized BF16 Qwen3-14B, without second-pass self-training.

## Question and labels

Can a judge detect semantic differences between an English mathematical argument
and a Lean argument? Every primary comparison uses both sides. A proof of the
same theorem by a substantively different route can be a mismatch. Compiling
Lean and sharing a topic do not establish correspondence.

Corrected ProofNet source pairs remain positive under the user's explicit
assumption. The user now authorizes similar-proof swaps as synthetic negatives;
the older TODO requiring review before this training is superseded. Similarity
is a retrieval heuristic, not a semantic label certificate. Scores on these
labels measure the constructed task, with possible false negatives and imperfect
source positives, rather than independently verified real-world accuracy.

## Frozen data design

Create a new grouped 70/15/15 training/validation/test split with seed 884.
Group related exercises and identical English proofs before splitting; use
within-split donors only. Fit lexical vocabularies and module IDF on training
sources only. Use the existing relatedness formula:

`0.45 English statement cosine + 0.45 Lean statement cosine + 0.10 mathlib proof-module cosine`.

Require relatedness at least 0.20, fixed before looking at model outcomes or test
coverage. Keep matched donor permutations within the allowed graph; omit sources
that cannot participate rather than lowering the threshold using test results.
The primary negative swaps the whole English statement and proof together,
preserving each language's internal coherence. Save proof-only swaps separately
as a secondary diagnostic. Keep balanced labels and identical positive/negative
single-language marginals. Record exclusions and counts in the dataset manifest.
Require complete prompts and training answers to fit 4096 tokens; do not truncate
proofs. Use existing successful Lean4.28 replays as source validation.

The old 16-case same-theorem set remains a separate, previously inspected
diagnostic. It is never training data, threshold-selection data, or a new blind
test. The new test is held out from this adapter, but portions of the source
corpus appeared in earlier experiments; report that prior exposure explicitly.

## Direct and translation comparisons

1. Evaluate original Qwen3-14B on validation, test and the old diagnostic.
2. Train a fresh ordinary LoRA adapter on the new training set only, retaining
   the earlier one-epoch/rank16/learning-rate1e-4 recipe. Evaluate the same sets.
3. With original Qwen3-14B, translate English to Lean and compare to supplied Lean.
4. With original Qwen3-14B, translate Lean to English and compare to supplied English.
5. Independently translate each source to Verbose Lean, then compare the outputs.
6. Repeat with Natural Lean.

For generation, each branch sees only its own language's statement and proof
(plus existing formal context for the formal branch). It cannot see the other
proof or pair label. Use semantic argument comparison, not string equality.
Save source-isolated prompts, generated output, score margins, timing, truncation
and failure status. Report coverage separately; a translation failure is not a
semantic NO. Compiler validation is a separate outcome, and uncompiled text is
never described as verified dialect code. Use pinned source examples for dialect
syntax. Generation fine-tuning is conditional on finding suitable actual paired
training material; a small syntax-example repository is not automatically such
a dataset.

Use one GPU worker at a time with persistent logs, input fingerprints and a
resumable queue. Report accuracy, both classes' precision/recall/F1, confusion
matrices, ranking metrics where possible, and false acceptance of synthetic
mismatches. Preserve all raw outputs locally under ignored artifacts/.

## Larger model investigation

Inspect the implementation and requirements of JustVugg/colibri, including
Windows support, supported model architectures, offloading and precision.
Assess against the A6000 48GB GPU and 128GB system memory. Do not silently switch
to quantized weights or interfere with the scheduled 14B runs. Record whether
an unquantized larger model is actually supported before a large download.

## Live state

Data preparation and integrity checks are complete: 366 training rows (183 per
class), 60 validation rows (30 per class), and 54 test rows (27 per class).
After the initial family split, token/dependency/similarity filters retained 240
source pairs. Three sources compiled but had incomplete dependency expansion;
those were excluded. All admitted training prompts fit the 4096-token budget.

Each translation architecture receives the 54 new test pairs and the 16 old
diagnostic cases. A shared cache generates each unique source view only once.
The generation cap is min(1536, 4096 minus input tokens), requiring at least 256
output tokens; no source proof is truncated. Reaching the cap is an abstention.

GPU execution checks completed for both single-translation directions on four
old diagnostic cases. Both produced four judgments, but this is only an
execution check. The English-to-Lean outputs contain invalid Lean4 syntax and
omit an explicit ambient integer domain. Their textual argument judgments are
not proof of successful formal translation. Report ordinary textual judging
and compiler-qualified coverage separately. Compilation still does not certify
that a translation preserves its own source argument.

The background queue started at17:53 Eastern on2026-11-10 with untuned direct
evaluation. Live state is `artifacts/hard-related-20261110/job.json`; generated
small reports are in `reports/hard-related-20261110/`. Eight stages run serially:
untuned direct, fresh LoRA, tuned direct, four intermediary architectures, and a
separate compiler ledger. The aggregate report includes compiler-qualified
coverage for code-producing paths once the ledger exists. No second pass.
Use `scripts/run_hard_related_experiment.py --validate-only` for a read-only
queue check. Do not start another driver while the live process holds the GPU
lock. Completed stages are reused only when their provenance matches. Failed
training is not silently resumed from a partial adapter.

All four intermediary execution smoke checks completed on the GPU. Dataset
checks(7), runner checks(12), orchestration checks(6), existing extraction
checks(13), and compiler checks(6) passed. Natural Lean and Verbose Lean libraries
and upstream examples both built. The shorter workspace path resolved the
Verbose Windows path-length errors; two Verbose syntax probes also compiled.
The conservative generated-code screen can reject harmless admission keywords
inside string literals; these remain screening rejections, not compiler errors.
Source/planner research and dataset-search results
are in `reports/intermediary-sources-20261110/README.md`. No suitable paired
translation dataset was found, so no dialect-generation fine-tuning is claimed.
Colibri was inspected and its planner run; no larger checkpoint or Colibri
inference has run. A plan or script existing is not evidence of completion;
consult actual job status and completed result files.
