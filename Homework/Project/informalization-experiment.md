# Preferred next direction: informalize, then compare arguments

User direction recorded 2026-11-12 (America/New_York), from the laptop.
Planning/context update only: no training, downloads, or experiment-machine
inspection occurred. Resume local-model work on the larger experiment computer.

## Motivation and two training stages

The user now considers this the most promising direct route to semantic judging:
ask what a Lean argument actually establishes and how it establishes it, express
that in English, and compare it with the original English argument.

1. **Train Lean to English.** Given the actual Lean statement, proof body and
   required definitions/context, produce an English account of its assumptions,
   conclusion and essential reasoning. Existing English-to-Lean paired data may
   support reverse-direction supervision; usable proof-level coverage and fidelity
   must be audited rather than inferred from statement alignment.
2. **Train English-to-English argument comparison.** Compare the original English
   proof with the independently informalized Lean proof for semantic content and
   essential argument correspondence. Investigate collections containing multiple
   natural-language proofs of the same theorem, including genuinely different
   arguments and meaning-preserving presentations of the same argument.

The user's expectation that suitable training data exists is a research lead,
not a newly verified dataset finding. No new dataset search was performed here.

At inference: `Lean + context -> English account -> compare with source English`.
The informalizer must not see the source English being judged: copying or repairing
toward that text could hide the very mismatch the project seeks to detect.

## Target and limits

Retain the project's existing binary argument-fidelity target: YES requires
equivalent claims/assumptions and the same essential reasoning. Different valid
proofs of the same theorem are useful hard negatives, not automatic positives.
Paraphrases, routine elaborations and permissible reordering can be positives.
Resolve ambiguous granularity through the rubric; retain uncertain cases.

Answer both "what proposition does this Lean code prove?" and "what argument does
it use?" Statement-only informalization would not meet the primary objective.
English generated from checked Lean is not itself machine-verified. A translator
can omit assumptions, invent steps, or collapse distinct arguments into one story.
Assess translation fidelity separately from comparison accuracy, and retain source
links to declarations/steps where practical. Lean validity remains a separate gate.

## Resume on the experiment machine

- Inspect actual job state, logs, adapters and newer reports for the existing 14B
  argument experiment before starting anything. Laptop notes do not establish its
  current status. Preserve completed statement results and direct-judge artifacts
  as baselines; no running job was cancelled or changed by this discussion.
- Audit existing paired corpora for reversible proof-level supervision, licenses,
  provenance and label quality. Search for English proofs with same-theorem,
  different-argument pairs; theorem identity alone does not label argument identity.
- Split by theorem/source family before reversing pairs, paraphrasing, generating
  informalizations or constructing negatives. Keep evaluation families held out
  from both stages and check overlap across corpora.
- Prepare a small pilot with independently assessed Lean-to-English fidelity and
  English-to-English argument labels. Include paraphrases, different valid proofs
  of one theorem, changed assumptions, and translators that omit crucial steps.
- Compare an untuned pipeline, stage-one training, stage-two training, and the
  trained two-stage pipeline against the direct English/Lean judge on a common
  held-out set. Report per-stage errors and end-to-end mismatch metrics/coverage;
  generated text and model agreement are not ground truth.

Model/adapters, datasets, training objectives beyond these task definitions,
budgets and implementation details remain to be selected after that audit.

## Relationship to earlier plans and source discussion

This promotes the ordinary-English intermediary already contemplated in
[methodology.md](methodology.md) and the controlled/structured experiments into
the preferred next research direction, with explicit separate training stages.
[Verbose Lean](verbose-lean-experiment.md), ForTheL and direct judging remain
comparison options rather than prerequisites for this path.

Motivating article: [Xena, "…and the proof is checked in Lean", 2026-11-12](https://xenaproject.wordpress.com/2026/11/12/and-the-proof-is-checked-in-lean/).
Its final remark describes using AI to informalize Lean back into English when
the accompanying prose diverges from the formal proof. This motivates the design;
it does not establish the proposed pipeline's performance.
