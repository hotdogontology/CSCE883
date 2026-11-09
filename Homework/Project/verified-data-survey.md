# Verified correspondence data candidates

Checked 2026-11-06. Research findings, not an adopted benchmark. No new data
download, local replay, training, or ground-truth labels were produced here.

## Clarification after direct proof inspection (2026-11-09)

The statement "ProofNet-V does not give corresponding argument pairs" is too
broad. It does release English proofs with formal counterparts for the same
corrected problems; some inspected formal proofs visibly follow the English
method. What is not established by the published statement-level audit is a
dataset-wide guarantee or annotation of essential-argument preservation.

Inspected the pinned Lean 4.28 proof archive directly:

- Problem 11 (`Artin_exercise_11_4_1b`): English invokes Eisenstein at 3;
  corrected Lean proof explicitly constructs the Eisenstein conditions at 3
  and transfers irreducibility from integer to rational polynomials. Promising
  argument-aligned candidate; this is agent source inspection, not human review
  or local compilation.
- Problem 13 (`Artin_exercise_11_4_8`): English invokes Eisenstein at p;
  corrected Lean invokes `Polynomial.irreducible_of_eisenstein_criterion` and
  passes to Q. Another promising same-method candidate.
- Problem 1: English uses representations a^i b^j and commutation of powers;
  Lean uses two-variable subgroup closure induction. Whether this is accepted
  as the same essential argument depends on our intended granularity. Do not
  assign an automatic negative based solely on this presentation difference.

Some archive files contain an original admitted declaration, its refutation,
and a completed corrected theorem. A future extractor must isolate the corrected
target and dependencies; treating the entire file as the positive proof would
mix incompatible statements, commentary and `sorry` templates.

The proper next step is to inspect/align actual proof pairs, rather than dismiss
ProofNet-V as proof-level material or silently replace the requested target with
statement classification. No new argument-fidelity labels were established here.
The OpenReview paper/PDF access was blocked by browser verification; conclusions
above use the primary README/dataset card and downloaded archive, not an unseen paper.

Our target is preservation of the essential argument, including assumptions and
theorem meaning. Statement alignment and proof validity alone do not establish it.

| Source | Reviewed evidence | Fit and availability |
| --- | --- | --- |
| [ProofNet-Verified](https://huggingface.co/datasets/marcusm117/ProofNet-Verified) | 367 corrected examples; statement corrections assessed by human reviewers and an AI agent to consensus; formal proofs provided separately | Public, Apache-2.0. Strong auxiliary statement-alignment benchmark. Does not certify that each formal proof follows its English proof's argument. |
| [Pistis: Does the Proof Prove It That Way?](https://arxiv.org/abs/2608.15432) | Faithful formalization of Euclid; blinded human evaluation of 30 Book I propositions, 254 step-fidelity ratings across 127 completed assignments | Closest research match to our argument target. Ratings are graded, not our binary labels. Public download of individual annotations/artifacts was not located in this search. |
| [FaithSieve](https://arxiv.org/html/2608.26310#A5.SS2) | Appendix E.2: two human experts reviewed 135 local theorem/lemma statements against NL obligations and context; 115 faithful, 20 unfaithful | Potential chunk/statement-alignment evaluation. Individual audit-pair release not confirmed. Public ProofLoc benchmarks concern proof correctness/first errors, a different label. |
| [Human paper-to-Lean audit ledger](https://github.com/pengzhang91/generation-in-the-limit-lib/blob/main/GenLimitLean/AuditRecords/Human/README.md) | Explicit reviewer, scope and revision records; historical Level 3 includes proof correspondence | Source for small case studies, not a ready binary dataset. Historical proof-level scope now marked needs-review after changes; use audited historical revisions, never assume current code inherits the audit. |

## Practical recommendation

Inspect ProofNet-Verified first as an accessible statement-level auxiliary test,
while seeking Pistis's reviewed proof pairs for the primary task. Keep either
evaluation source reserved from adaptation/training. Check theorem/source-family
overlap against Herald/Mathlib; pretraining exposure is also possible.

ProofNet-Verified includes English statements/proofs, but its Hugging Face
`formal_proof` field is a placeholder pointing to an external archive, and
`formal_stmt` includes a `by sorry` template. Neither is a completed proof input.
The [repository](https://github.com/marcusm117/ProofNet-Verified) provides pinned
archives, including completed Lean 4.28 proofs; latest statement snapshots target
Lean 4.34. Match data, proof archive and environment before replay, and keep our
existing Lean 4.11 corpus environment intact. Inspect error-taxonomy annotations
and their original statement revision before interpreting them as negative pairs.

The [public FaithSieve materials](https://github.com/TropicalFatFish/anonymous-faithsieve)
list 350 Olympiad and 200 university problem/proof examples, with fields `id`,
`problem`, `steps`, `first_error_step`. They do not list Lean counterpart or
semantic-gate human-label fields. These downloadable correctness benchmarks must
not be relabeled as argument-correspondence data.

No source above is yet confirmed as a directly loadable, independently reviewed
binary benchmark for our full English/Lean argument-fidelity target. This is a
limitation of this search, not a claim that no such dataset exists. Pistis and
FaithSieve are also directly relevant related work for refining our novelty.
