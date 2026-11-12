# References for future work

## Lean-to-English informalization and semantic judging

Added at the user's request, 2026-11-12:

- [Xena: "…and the proof is checked in Lean" (2026-11-12)](https://xenaproject.wordpress.com/2026/11/12/and-the-proof-is-checked-in-lean/).
  Discusses checking statement correspondence, compilation, proof integrity and
  kernel soundness before interpreting a Lean verification claim. The final
  remark describes experts using AI to informalize Lean proofs into English
  when the accompanying prose diverges from the formal argument.

This motivated the user's preferred two-stage direction: train Lean-to-English
informalization, then English-to-English argument comparison. It is motivation,
not evidence that generated English inherits Lean verification or that this
pipeline has been validated. See
[informalization-experiment.md](informalization-experiment.md).

## Verbose Lean as an argument intermediary

Suggested by the user, 2026-11-09:

- [Patrick Massot: verbose-lean4](https://github.com/PatrickMassot/verbose-lean4)
  — natural-language tactics for teaching mathematics using Lean 4.
- [medovina: natural_lean](https://github.com/medovina/natural_lean)
  — controlled natural-language syntax for Lean.

Research idea: independently translate the English proof and the original Lean
proof into a shared verbose Lean representation, then compare their arguments.
Use actual compilation plus correspondence assessment to guide a future custom
architecture. See [verbose-lean-experiment.md](verbose-lean-experiment.md).

These are two candidate syntax/tooling projects, not assumed interchangeable
dialects or automatic translation services. Their repositories were inspected
on 2026-11-09; neither has been installed, version-pinned or tested locally.

Related project plans: [controlled-language-experiment.md](controlled-language-experiment.md),
[structured-proof-experiment.md](structured-proof-experiment.md),
[methodology.md](methodology.md).
