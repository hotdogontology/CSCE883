# References for future work

## Argument fidelity and semantic review

Added at the user's request, 2026-11-11:

- Tadd Mao et al. (2026), [Does the Proof Prove It That Way? Faithful
  Formalization of Elements Proofs (Pistis)](https://arxiv.org/abs/2608.15432).
  Uses Euclid's English proofs and Claude-generated Lean, with structured
  decomposition, dependency constraints, gap detection and human fidelity
  evaluation. Relevant as a generation/evaluation method; not a confirmed
  downloadable gold binary-classification corpus.
- Robert Joseph George (November 2026), [Getting the (In)formal Statement
  Right](https://www.robertj1.com/ai4science/getting-the-statement-right/).
  Read the original article. Useful distinctions: checked proofs, faithful
  statements, faithful back-translations, and preservation of argument structure.
  Candidate project extensions: compare elaborated claims with definitions and
  hypotheses; map source steps to named Lean declarations; retain exact source
  revisions and review scope; investigate naturally occurring discrepancies as
  evaluation cases. Blog examples need independent artifact review before gold
  labels. Its statement checks alone do not establish proof-route fidelity.
- [ProofFlowBench](https://huggingface.co/datasets/rafaelcabral96/ProofFlowBench):
  retain as a source of proof decomposition/dependency graphs, even without
  ready English–Lean pair labels, as requested by the user.
- [Faithform-AF](https://huggingface.co/datasets/ighina/Faithform-AF) and
  [Faithform-LLMs](https://huggingface.co/datasets/ighina/Faithform-LLMs): public
  English reasoning steps, generated Lean formalizations and prover outputs.
  Separate translation fidelity from validity/refutation; see the dataset survey.

Detailed availability and schema notes:
[semantic data search](SEMANTIC_DATA_SEARCH_2026-11-11.md).

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
