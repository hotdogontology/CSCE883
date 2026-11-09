# References for future work

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
