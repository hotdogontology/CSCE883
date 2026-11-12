# Related-proof mining pilot

Completed 2026-11-10. This is a candidate-retrieval and frozen-model survey;
no new Qwen fine-tuning or self-training was performed.

## Extraction and graph

All **365 extracted ProofNet target proofs** successfully elaborated with their
retained helper context in isolated official Lean 4.28 and mathlib 4.28. The two
previously excluded source records 161/168 remain excluded. Original archived
files, some containing obsolete/admitted targets, were not replayed wholesale.
This establishes local elaboration, not fidelity to the English or a transitive
axiom-policy audit. Historical data/run manifests were preserved unchanged.

The resulting graph has **10,343 nodes and 83,785 typed edges**: source proofs,
resolved declarations, modules, subject directories; statement/proof uses,
declaration-to-module, direct module imports and subject-directory edges. It is
the ProofNet-reached slice, not all of mathlib. Local helpers are expanded until
imported constants; statement and proof dependencies remain distinct.

Pinned environment, input hashes, coverage and graph counts are in `summary.json`.
Raw graph and replay logs are ignored under `artifacts/relatedness-20261110/`.

## Candidate construction

Fit vocabularies/IDF on 255 eligible training positives only. Rank within the
existing splits using `0.45 English statement cosine + 0.45 formal statement cosine
+ 0.10 proof-module cosine`. This is a frozen heuristic, not a calibrated semantic
distance. No comparison yet establishes that graph features outperform lexical
retrieval alone. Subject directories are organizational hints, not a curated
mathematical taxonomy or proof-route labels.

Select one-to-one donor permutations, exclude same-family/shared-proof matches,
and reassign over 4096-token edges without truncation. Prepare three views per
source: original control, English-proof-only swap, English-statement+proof bundle
swap. Each source is used once as a donor; proof and English-bundle marginals
exactly match controls. No candidate has a binary label.

| Split | Sources | Total views | Old random mean score | Related mean score |
| --- | ---: | ---: | ---: | ---: |
| Training |255|765|.05054|.31114|
| Validation |59|177|.05628|.25678|

Five neighbors per source and selected donor metadata are saved. An example
retrieval links two primitive-root problems: Fermat primes versus negating a
primitive root for primes of form 4t+1. These share mathematical objects but ask
different questions. Most candidates still have different statements and do
not address the harder same-theorem route task.

See [candidate-review.md](candidate-review.md) for six examples selected across
the ranking without using model outputs. `tuned-accepted-candidates.json` lists
the 17 new candidate views accepted by tuned Qwen for follow-up, not verified errors.

## Frozen-model survey

Every column below has 59 examples. Entries are **YES/acceptance counts**, not
accuracy. Controls retain the user's assumed-positive ProofNet policy. The
original random swaps retain their earlier synthetic-negative policy; new swaps
remain unreviewed and could contain ambiguous or compatible arguments.

| Model | Original controls | Old random proof swaps | Related proof-only swaps | Related English bundles |
| --- | ---: | ---: | ---: | ---: |
| English-only forest |51|2|31|51|
| Both-language forest |50|4|39|48|
| Untuned Qwen3-14B |37|0|2|0|
| LoRA Qwen3-14B |59|0|9|8|

All 177 views were scored by each Qwen model, no skips. Original Qwen control
predictions reproduced exactly; original forest validation/core metrics also
reproduced. English-only forest bundle and control score multisets are identical,
as required by the English-bundle permutation. English-only coherence cannot
distinguish those two groups. Both-language lexical forest also accepts many
bundle swaps; Qwen responds differently from these lexical baselines.

This demonstrates a substantial reduction in the obvious lexical mismatch signal,
not a measured improvement in argument fidelity or a new ground-truth benchmark.
Qwen still rejects most related candidates. Preserve the independent 16-case
same-theorem diagnostic (untuned 15/16, tuned 8/16 at the fixed decision rule,
AUROC 1.0 for both) and do not fit thresholds using it.

## Verification and next step

Six targeted guard tests and 15 existing argument tests pass. Artifact validation
checks exact swap provenance, no binary labels, split isolation, balanced proof /
bundle marginals and all graph edge references. Full predictions are ignored;
small metrics and review indices are retained in reports.

An exact whitespace/name-normalized statement-signature audit found no duplicates
among 365 sources. This does not test alpha-equivalence, definitional equivalence
or logically equivalent formulations; no new same-theorem pairs were certified.

Next: assess candidate labels and source-positive route fidelity at a defined
granularity, expand independent same-theorem calibration/test families, and
compare lexical-only versus graph-assisted mining before additional fine-tuning.

The full matched-coverage [Herald forest comparison](../random-forest-herald-20261110/README.md)
is also complete; the forests accept nearly every pair. No Herald accuracy is known.
