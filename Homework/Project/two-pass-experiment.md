# First and second pass Qwen experiment

Monday review (2026-11-09): the full pipeline completed Saturday at 00:55 Eastern.
Second pass trained on 26,961 agreement-labeled Herald pairs for ~5.02 hours.
Validation accuracy: untuned 62.50%, first pass 70.54%, second pass 66.07%.
Second-pass confusion: TP 60, TN 14, FP 25, FN 13. Mismatch rejection is 14/39,
versus first-pass 13/39 and untuned 21/39. Both saved adapters were verified.
Herald teacher disagreements: 17,422; agreements: 27,077; missing: 54. After
contest exclusions, 26,962 agreements were eligible; one exceeded training length.
External cases: five scored, one too long; outcomes are unreviewed flags, not
verified errors. See `reports/two-pass/` for complete aggregate outputs.

Authorized 2026-11-06. This experiment supersedes the earlier decision to defer
task training. The original project target remains argument fidelity; this first
implemented experiment measures **statement fidelity**, which is the label scope
available in ProofNet-Verified. English proof text and Lean proof bodies are not
inputs. It cannot establish detection of changed proof arguments.

## Protocol

1. Use the pinned ProofNet-V original-statement audits for positive and negative
   examples, plus corrected statements as positives. Join by problem index and
   check names, exclude 10 ambiguous/incorrect-English problems, deduplicate
   whitespace-normalized statement pairs, reject conflicting duplicate labels.
   Do not train on the audit explanation or corrected counterpart as input.
2. Split by original problem, keeping original/corrected variants together,
   seed 883. Result: 448 training pairs (292 YES/156 NO), 112 validation pairs
   (73 YES/39 NO), 560 total. These are published labels, not newly audited labels.
3. Train first-pass Qwen from the pinned original Qwen3-8B with NF4 QLoRA:
   rank 16, alpha 32, dropout 0.05, q/k/v/o attention projections, BF16 compute,
   AdamW 1e-4, one epoch, batch 1 with accumulation 8, seed 883. Only YES/NO
   answer tokens and end-of-answer receive loss; prompt tokens are masked.
4. Evaluate original and first-pass Qwen on the same 112 validation pairs and
   all 44,553 Herald rows. Both use identical NF4/BF16, nonthinking prompt,
   and constrained YES/NO next-token scoring, batch 8. Scores are uncalibrated.
   Maximum input 2,048 tokens; record longer inputs/OOM as missing, never NO.
   No truncation. This is a fresh comparison, not the prior 30-pair argument run.
5. User explicitly selected **agreement-only** pseudo-labels. Exclude missing
   teacher predictions, disagreements and names/imports containing IMO,
   Olympiad, Archive or Putnam. Preserve exclusions separately. Agreement is
   not ground truth: both teachers share a backbone and can share errors.
6. Train second-pass Qwen from a fresh original checkpoint, not from first-pass
   adapter weights. Same one-epoch QLoRA settings, using eligible Herald agreement
   pseudo-labels. Record class balance and context-limit coverage.
7. Evaluate second-pass on the same frozen validation set, then screen a small
   source-pinned external pilot with original, first- and second-pass models.
   Do not train on or tune prompts using external outcomes. Retain untuned output
   as a control even though the user requested the two tuned models for this tier.

## Initial measured results

First-pass training completed: 448/448 pairs, 56 optimizer steps, 15,335,424
trainable parameters, 230.61 seconds, peak allocated VRAM 10.56 GiB.
One initial launch failed on a tokenizer return-type mismatch before training;
its output remains in `first-pass-statement/`. Corrected completed run is
`first-pass-statement-v2/`.

| Frozen validation result | Untuned | First pass |
| --- | ---: | ---: |
| Correct / 112 | 70 | 79 |
| Accuracy | 62.50% | 70.54% |
| Faithful pairs accepted / 73 | 49 | 66 |
| Mismatched pairs rejected / 39 | 21 | 13 |
| Mismatched pairs wrongly accepted / 39 | 18 | 26 |
| Balanced accuracy | 60.48% | 61.87% |

The first pass becomes more likely to say YES. Overall accuracy improves but
mismatch detection worsens, so it is not yet a dependable issue detector.
These small within-source validation results do not demonstrate argument fidelity
or broad generalization. A constant YES baseline scores 73/112 = 65.18%.

## External pilot and limitations

`external-two-pass-manifest.json` pins three Compfiles IMO statements (2022 P2,
2023 P1, 2024 P1) and three OpenAI formalization candidates from two manuscripts
(perfect-matching entropy/counting and bin packing). The pilot is unlabeled.
Published determine-all questions versus formal solution-set theorems have a
question/answer scope difference. OpenAI aggregate theorem versus individual
paper result, or theorem-strength/version differences, can also explain NO.
PDF extraction may flatten exponents/fractions; see each case's `unit_note`.
Context comes from compact comparator definitions, but theorem statements are
extracted from completed implementation sources, not sorry comparator bodies.
These candidates have not been locally compiled or independently semantically
reviewed. A model flag is a review lead, not a confirmed error in a release.

Contest-name/import exclusions are a conservative heuristic, not a complete
theorem-family overlap audit. Old IMO and Mathlib material may occur in Qwen's
pretraining. ProofNet and Herald share mathematical sources; second-pass
validation may have indirect overlap. Do not present it as a pristine independent
test. Broader family/semantic overlap review remains outstanding.

The second pass is **pseudo-label self-training / distillation**, not unsupervised
learning. It may amplify teacher mistakes, erase useful disagreement cases, or
collapse toward the majority class. Evaluate class-specific metrics against the
same untuned and first-pass controls; teacher agreement alone measures no gain
in correctness. No RL, GAN, or compilation reward is used here.

## Running and inspecting

Main scripts: `scripts/two_pass.py`, `scripts/run_two_pass.py`,
`scripts/prepare_external_two_pass.py`, `scripts/report_two_pass.py`.
Driver PID is recorded in ignored `artifacts/two-pass/job.pid`; it runs sequential
GPU stages in a hidden Windows process. It stops on stage failure. Inference
can resume matching inputs/settings; interrupted training needs explicit recovery
into a fresh output directory. Future training saves adapter/optimizer/RNG/progress
checkpoints every 512 examples at optimizer boundaries; recovery remains manual.
Do not launch another driver while one is active.

Inspect `artifacts/two-pass/job.json` for current stage, stage logs for progress,
and `artifacts/two-pass/report.json` for available results. Output tables are
`herald-comparison.csv` and `external-comparison.csv`. Training directories hold
adapters, per-example loss logs and settings/provenance. Bulk artifacts stay ignored.
No finished second-pass or external result is implied by this protocol document.
The Friday watcher exports local aggregate results in `reports/two-pass/`.
It was launched without publishing because native Git requires sign-in and the
connected app returned HTTP 403 on write. Consult `MONDAY_HANDOFF.md`; no successful
GitHub push is confirmed. Optional `--publish` mode is available after authentication.
