# Research and implementation audit — 2026-11-09

Audited the plans, actual data preparation, saved predictions and training code.
Independent reviews covered methodology, extraction/implementation and completed
results. New diagnostics below are CPU-only; no new large-model training ran.

**Disposition:** preserve the 8B results; keep the downloaded BF16 14B model;
hold the queued 14B experiment before its memory probe/training. Correct concrete
data defects and add a test that requires both proof arguments before presenting
any result as cross-language argument-correspondence performance.

## 1. The new proof-swap benchmark has a decisive English-only shortcut

The current negative keeps the statement pair and Lean code fixed but replaces
the English proof with a different problem's proof. It breaks the English
statement/proof relationship. A model can therefore classify it without reading
the formal proof, even though both proof bodies are present in its input.

Measured control on the prepared v3 data:

- TF-IDF cosine similarity between **English statement and English proof only**.
- Vocabulary and decision threshold fitted on training data only; threshold
  selected to maximize training accuracy.
- Training accuracy 89.27%; validation **132/144 = 91.67%**, macro F1 91.67%.
- This is a diagnostic on the full prepared set before model context filtering,
  not an independently reviewed semantic accuracy claim or a 14B model result.

This is stronger evidence than a generic warning about easy negatives. A high
14B score on this dataset would establish cross-problem proof consistency, not
that the model compared the English and Lean argument routes. Preserve the
cross-problem task as a pilot if useful; do not promote it to the core target.

Reproduction: `scripts/audit_argument_shortcuts.py`;
results: `reports/audit-20261109/english-only-shortcut.json`.

## 2. Proof extraction has concrete defects; fix before training

`scripts/argument_data.py` uses the first unbracketed `:=` as the proof boundary
(function `assignment`, line 42). That delimiter can occur in an unbracketed
`let`, `letI`, `haveI` or `let_fun` inside the theorem's type.

- **99/44,553 Herald declarations** are split incorrectly. For `herald-1087`,
  part of the theorem type is incorrectly assigned to the proof field.
- **ProofNet-289** in validation has the same defect: the purported statement
  stops at `let T_inf : Set (Set X)`, before its assigned set and actual claim.
- Three contexts retain references to removed genuine helper lemmas:
  `proofnet-60` (validation), `proofnet-185` and `proofnet-257` (training).
  The extractor deletes every theorem with the target-name prefix (lines
  79–86) and checks omitted dependencies only in the final body (88–89).
- Exact English proof text crosses the split between training `proofnet-324`
  and validation `proofnet-141`: parts a/b of Pugh exercise 3.63, covering the
  same integral-test argument. Splitting by individual problem ID misses this.

Required correction: use trustworthy supplied declaration signatures or Lean
syntax extraction rather than a generic assignment delimiter; retain actual
dependencies; validate context plus target in the pinned environment, including
transitive admissions/axioms. Group exercise families and exact shared proof
material before splitting and generating negatives. Preserve v3 as an auditable
failed preparation; regenerate into a fresh version rather than overwrite it.

Reproduction: `scripts/audit_argument_extraction.py`;
results: `reports/audit-20261109/extraction-integrity.json`.

## 3. The 8B numbers are correct, but source style confounds their interpretation

The old statement dataset mixes original audited statements with corrected
positive statements. Their contexts differ systematically. A one-feature rule
based on the presence of `noncomputable section`, without reading either
statement, performs as follows:

| Measure | Context-only diagnostic | First-pass Qwen |
| --- | ---: | ---: |
| Validation accuracy | 66.07% | 70.54% |
| Balanced accuracy | 69.79% | 61.87% |
| Macro F1 | 65.80% | 62.03% |

The feature was noticed during a post-hoc audit; only the rule's direction was
selected using training accuracy. Do not market it as a preregistered competing
model. It demonstrates an available shortcut, not proof that Qwen used it.

First-pass gains concentrate in corrected positives: original-row accuracy
changes from 45/71 to 42/71, while corrected-positive accuracy changes from
25/41 to 37/41. On 39 original-negative/corrected-positive problem pairs, each
of the three models classifies both members correctly on only 9 pairs.

Preserve all reported counts. Describe 70.54% as performance on this particular
constructed statement benchmark, with style confounds. Any future replication
should normalize semantically equivalent context styles, balance source/mutation
artifacts and include context-only controls. Do not overwrite the historical run.

One narrow documentation correction: old training `proofnet-35-corrected`
retained a completed proof in `formal_statement` because the stripping function
only removes `by sorry`. No held-out row contains that retained proof. The task
was statement correspondence, but not every training input was proof-free.

Reproduction: `scripts/audit_statement_controls.py`;
results: `reports/audit-20261109/statement-controls.json`.

## 4. Report ranking, operating points and sampling uncertainty separately

Previously reported accuracy, per-class precision/recall/F1 and confusion counts
recompute correctly. Saved YES scores also show:

| Measure | Untuned | First pass | Second pass |
| --- | ---: | ---: | ---: |
| AUROC | 0.6458 | 0.7215 | 0.6261 |
| Mismatch average precision | 0.5317 | 0.6032 | 0.4864 |

Thus first pass improves observed ranking, despite reduced mismatch recall at
the fixed YES/NO decision rule. Do not call it universally worse at mismatch
discrimination. Scores are uncalibrated. Select future thresholds using separate
calibration data or grouped training folds; do not tune on the 112 validation
rows and then call them an independent test.

Those 112 rows represent **71 source problems**, not 112 independent mathematical
cases. The +9/-5 correct-answer differences are single-seed exploratory results.
The specific second-pass recipe failed to improve first-pass validation; this
does not establish that self-training generally fails. It also changes domain,
label source, YES prevalence (~87.86%) and optimizer-update count (56 to 3371).

The new swap dataset similarly has 72 validation source problems, not 144
independent cases, and donor reuse couples different anchors. Filtering whole
anchor pairs preserves label balance but breaks the equal English-proof marginal
frequencies. At 8192 tokens, v3 retains 558 train / 138 validation rows; at 4096,
502 / 126; at 2048, 368 / 82. Marginal equality fails at all three budgets.
Reconstruct negatives after any filtering and recheck guarantees; do not assume
unfiltered derangement properties survive. No iid row-based significance claim.

Coverage evidence: `reports/audit-20261109/token-coverage.json`.

## 5. The core evaluation should require agreement of two valid routes

For each fixed theorem, obtain two substantively different correct arguments A/B,
with an English and a Lean version for each. Keep the statement pair and common
context identical in all four cells:

| | Lean argument A | Lean argument B |
| --- | --- | --- |
| English argument A | YES | NO |
| English argument B | NO | YES |

Both English proofs are valid proofs of the same theorem; both Lean proofs check.
Each individual proof occurs once per label. Either language alone, the statements
alone, and compilation alone cannot determine the label on a complete matrix.
This makes the model compare the relationship between proof routes.

Keep all four cells and all source variants in one theorem-family split. Reserve
a separate final suite before adapting prompts or representation architecture.
For uncertainty calculations, group by theorem. Include match/mismatch metrics,
AUROC/average precision, coverage and within-theorem pair discrimination. Report
performance on this designed suite as such, not universal mathematical ability.

The user's explicit assumption that corrected ProofNet pairs are positive
argument matches remains honored. These pairs can supply training positives;
their assumed status must stay recorded. New alternative-route material needs
its own transparent provenance. The distinction between routine elaboration and
an essential argument change still needs concrete examples; do not silently
change existing assumed labels or require the deferred 30-pair review to restart.

Minimum ablations: full evidence; English statement/proof only; formal proof
masked; statements only. The current cross-problem pilot can stay as an easy
control, but cannot substitute for this same-theorem evaluation.

## 6. Herald, external screening and future architecture have different roles

- **Herald:** unlabeled deployment/disagreement survey. Full-corpus predictions
  do not supply accuracy, calibration or independent validation. After extraction
  repairs, first inspect a bounded reproducible pilot before interpreting a
  larger sweep. No pseudo-label second pass in the new experiment.
- **IMO/OpenAI:** retain old outputs as exploratory input screening. Original
  questions versus solved assertions, aggregate versus individual theorem scope,
  flattened PDF notation and missing context prevent a defensible error-discovery
  claim. Align units before another accuracy test or public error claim.
- **Verbose Lean:** sensible future representation comparison. Translate both
  branches independently and verify each preserves its own source argument;
  two compiling outputs or matching outputs can still share a canonicalization
  error. Compare direct/original-plus-verbose/verbose-only on the same reserved
  same-theorem suite. Lean proof irrelevance and theorem equality do not certify
  proof-route fidelity. Compilation should guide a generator/ranker; it cannot
  teach a fixed-input binary classifier correspondence by itself. Establish
  judge quality before reward optimization or online RL.

## 7. Hardware and implementation status

The model choice and LoRA approach are reasonable for the authorized unquantized
fully GPU-resident run. Qwen3-14B downloaded successfully; all published LFS file
hash checks passed. Fixed the temporary manifest path left by the already-running
older downloader; the 14B model lives separately from the intact 8B model.
BF16/LoRA loading, suffix answer loss and gradient accumulation appear coherent;
the tiny-model masked-loss equality/backward check passed. Real 14B memory use
has not yet been measured. No 14B inference/training result exists at this audit.

The stage driver skips any completed marker without checking current provenance
(`scripts/run_argument_experiment.py`, line 70). Correct this or use a fresh run
directory for each dataset/configuration. Reuse must compare source/model/prompt/
adapter hashes and token budget. Record dependency versions for inference too.
Existing passing unit tests did not cover the concrete extraction counterexamples;
add those regressions and end-to-end data checks before restart.

## Prioritized next work

1. Correct extraction and family grouping; regenerate versioned inputs. Validate
   the affected examples, whole-context dependencies and full-corpus integrity.
2. Add the English-only/context-only controls to every relevant comparison.
   Build and freeze a compact same-theorem 2x2 argument test before more tuning.
3. Run the unquantized 14B memory probe and untuned/tuned comparison under the
   corrected protocol. Preserve the prior 8B statement scores separately.
4. Run Herald descriptively, then consider verbose Lean as a representation
   ablation. Defer generator/reward architecture complexity until the judge
   demonstrates the intended discrimination.

No weights, historical predictions or prior reported metrics were deleted or
rewritten. Current live status is `held_for_audit`; download is complete. This
audit does not revoke authorized training; it records the defects that need
correction before restarting it.
