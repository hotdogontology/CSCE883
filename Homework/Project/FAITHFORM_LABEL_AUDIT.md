# Faithform label inspection

Inspected 2026-11-12. User corrected the intended 32B dataset from ProofFlow to
Faithform and requested inspection before choosing labels. No tuning or new
binary labeling performed.

## Evidence inspected

- First 100 test rows (offset0, default configuration) from each public release:
  [Faithform-AF](https://huggingface.co/datasets/ighina/Faithform-AF) and
  [Faithform-LLMs](https://huggingface.co/datasets/ighina/Faithform-LLMs).
  Raw API responses saved under ignored data/faithform-label-audit/.
- Upstream [outcome/metric implementation](https://github.com/Ighina/FaithformBench/blob/main/src/veriform/evaluation/uflb.py),
  [metric driver](https://github.com/Ighina/FaithformBench/blob/main/scripts/compute_uflb.py),
  [prover](https://github.com/Ighina/FaithformBench/blob/main/src/veriform/proving/deepseek_prover.py),
  and [perturbation judge](https://github.com/Ighina/FaithformBench/blob/main/src/veriform/perturbation/judge.py).

These are ordered samples, not random samples or dataset-wide estimates. No
released proof was replayed locally. Source code inspected at main on this date;
no assertion that current code exactly reproduces every historical artifact.

## What the fields mean

is_perturbed records intervention on English, not correspondence or independently
certified invalidity. proof_result describes a prover outcome for the generated
formal proposition: Proved, Refuted, Unknown, or formalization/type-check failure.
Upstream normalizes AF-Fail/AF_FAIL and TC-Fail/TC_FAIL; declarative cases are
excluded from its metrics. Unknown is not evidence of falsity or mismatch.

autoformalizer_output contains the proposed translation, often a theorem with
sorry, mixed with explanatory text. prover_output may prove the proposition OR
its negation. For correspondence extraction, retain the original proposed
formalization separately from the proof/refutation evidence. A refutation must
not silently become the claimed translation of the original English step.

No human binary argument-correspondence field was found in these schemas.
verification_note, inference_rule and dependency text are contextual metadata,
not certified English–Lean labels.

## Defensible interpretation

| English status (requires checking) | Formal result | Correspondence inference |
| --- | --- | --- |
| Valid source step | Refuted | Candidate mismatch: translation changed the claim/context |
| Invalid perturbed step | Proved | Candidate mismatch: repair, weakening, or added assumptions |
| Valid source step | Proved | Compatible with fidelity, but not a certified match |
| Invalid perturbed step | Refuted | Compatible with fidelity, but not a certified match |
| Any | Unknown / failed formalization | Unresolved; separate failure category |

Opposite truth status rules out faithful translation only when source validity,
context, and formal proof/refutation are trustworthy. Same truth status does not
establish equivalence or preserve argument structure. Upstream calls paired
original-Proved/perturbed-Refuted behavior 'faithfulness'; that is its operational
validity-preservation category, not a human gold proof-route label.

## Concrete inspected examples

1. Faithform-LLMs gsm8k-204, step_10, unperturbed/Refuted. English introduces
   an equation from the observation that five fries remain. Generated Lean states
   (1/3)*(x-30)-1=5 for arbitrary real x with no observation hypothesis. The
   missing assumption changes the claim: a useful candidate semantic negative.
2. gsm8k-201, step_3, perturbed/Proved. English claims that the number of distinct
   books is a product. Lean assumes exactly that equality and concludes it.
   This assumes the intended conclusion instead of establishing it. Candidate
   negative after checking the complete source context.
3. gsm8k-201, step_5, perturbed/Proved. English says each person reads at least
   one book after reading their own and each other's books. This appears still
   true under its stated premises. Thus the perturbation flag cannot be treated
   as proof that the English is false. This is a spot-check concern, not a final
   adjudication or a dataset-wide contamination estimate.

Counts in first100 rows per release:

| is_perturbed / proof_result | AF | LLMs |
| --- | ---: | ---: |
| True / Refuted | 45 | 41 |
| False / Proved | 29 | 49 |
| True / Proved | 21 | 9 |
| False / Refuted | 0 | 1 |
| False / TC-Fail | 2 | 0 |
| False / Unknown | 2 | 0 |
| True / Unknown | 1 | 0 |

## Recommended next use

Use validity reversals to mine real formalizer errors, then check source context
and the exact formal target before accepting negative labels. Positive labels
need an additional semantic check; do not infer YES from matching truth values.
Keep unresolved items unlabeled. Extract actual Lean code, not the formalizer's
reasoning/commentary, and keep proof_result, is_perturbed, model names and review
notes out of classifier inputs. Keep all steps, variants and model outputs of
one source problem in the same split. Frame this as local inference/step fidelity,
not already complete-proof route supervision. No new experiment was run.
