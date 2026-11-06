# Experiment: local alignment plus global correspondence

Proposed 2026-11-06. This supplements whole-proof classification and the
controlled-language experiment. AXLE access was tested on a synthetic proof;
no project corpus was submitted and no chunk-level dataset has been created yet.

The user subsequently saved an API key in the project's ignored `.env`; a
synthetic `have2lemma` request using it succeeded with one extracted lemma and
no Lean/tool errors. The key was not displayed. There is not yet a persistent
SDK/environment-loader integration; credentials are loaded locally per request.

## Access verified on 2026-11-06

Anonymous HTTP calls succeeded for `have2lemma`, `extract_decls` and
`extract_proof_states` on a synthetic reflexivity proof in `lean-4.28.0`, with no
Lean/tool errors. `have2lemma` returned the intermediate lemma with its proof;
proof-state extraction returned the initial goal, context after `have`, and
`no goals` at completion. These are live smoke tests, not corpus-scale checks.

Working tool endpoint: `https://axle.axiommath.ai/api/v1/<tool>`.
Environment listing: `https://api.axle.axiommath.ai/v1/environments`.
The tool path `/v1/have2lemma` on the API subdomain returned 404; use the tested
tool endpoint rather than assuming the environment-list URL layout applies.

There is no connected AXLE MCP tool in this session, no installed AXLE Python
client, and no AXLE/AXIOM environment-variable name was found in the current
process. Direct HTTP access nevertheless works without an API key in these
tests. The configuration docs describe 10 concurrent anonymous requests; that
limit was not load-tested.

The service's advertised standard Lean environments currently range from
4.21.0 to 4.35.0; Lean 4.11.0 is absent. Therefore our existing Herald/Mathlib
snapshot cannot be assumed to run on this service unchanged. Preserve the pinned
local environment; evaluate version-compatible local extraction or an explicitly
ported, separately verified subset before processing the corpus remotely.

https://axle.axiommath.ai/v1/docs/setup/configuration/

## Available extraction tools

**Axiom's AXLE** has relevant documented primitives:

- `extract_decls`: separates declarations with dependency information;
  replaces the deprecated `extract_theorems` endpoint.
  https://api.axle.axiommath.ai/v1/docs/tools/extract_decls/
- `have2lemma`: promotes local `have` statements to standalone lemmas, retaining
  context. For extraction with proof bodies explicitly request
  `include_have_body=true`: the default substitutes `sorry`. Preserve original
  source positions, scope and declaration identity through any transformation.
  https://api.axle.axiommath.ai/v1/docs/tools/have2lemma/
- `extract_proof_states`: reports tactic goal states at line endings. It does not
  automatically supply a complete semantic argument graph or English alignment.
  https://api.axle.axiommath.ai/v1/docs/tools/extract_proof_states/

Record server version/environment and processed content. AXLE's default
`ignore_imports=true` can substitute the environment header; request original
imports and compatible dependencies for fidelity experiments. Keep full proof
elaboration enabled when extracting proof dependencies. Check warnings,
admissions and truncated outputs independently of generic success fields.
Compatibility with our Lean 4.11.0 corpus is not supplied by the currently
advertised standard environments.

**Local alternative:** Jixia extracts declaration ranges, elaboration/tactic
information, symbol reference graphs and line-start proof states. Its version
must match the Lean version being analyzed. LeanDojo also extracts tactic states
and premises. Assess a pinned compatible version rather than upgrading the
corpus environment merely to fit a tool.

https://github.com/frenzymath/jixia
https://leandojo.readthedocs.io/en/latest/

**Aristotle distinction:** its theorem-proving paper describes generating an
English proof, restructuring it into small lemmas, formalizing them, and proving
them. This is proposed decomposition/proof generation, not lossless extraction
of every lemma from an existing proof. Current public FAQ search results state
that Lean-only projects are presently unsupported; recheck product capabilities
before planning an integration. Do not equate a historical research pipeline
with an available extraction endpoint.

https://harmonic.fun/pdf/Aristotle_IMO_Level_Automated_Theorem_Proving.pdf
https://aristotle.harmonic.fun/docs/faq

## Representation

Build a hierarchical proof graph for each side independently:

- Nodes: assumptions, local definitions, witness choices, intermediate claims,
  cases/induction hypotheses, important deductions, and the final conclusion.
- Node context: bound variables, domains/types, active assumptions, definitions,
  source span and enclosing scopes.
- Edges: premise use and scope relationships; distinguish explicit source-level
  dependencies from elaborated dependencies and inferred English dependencies.

Group routine tactic sequences into meaningful mathematical steps. A named
`have` is a useful boundary, not a complete inventory of reasoning. Term proofs,
`calc`, cases, induction and automation may expose different boundaries. Retain
uncertainty where extraction cannot recover a meaningful human-level step.

For the English side, extract claims and dependencies without seeing the Lean
proof. A model-generated decomposition is a hypothesis requiring audits; it can
omit or invent a step. Optional ForTheL renders these nodes under a fixed
vocabulary and exposes assumptions and scope, with separate parsing checks.

## Matching and whole-proof decision

1. Retrieve candidate counterpart nodes using mathematical content and context.
2. Score each candidate pair with a shared model for claim correspondence and
   compatibility of assumptions/domains. A shared backbone can serve all pairs.
3. Align nodes with one-to-many and many-to-one matches, and allow unmatched
   nodes and abstention. One English sentence may compress many formal steps.
4. Check coverage of important claims, hypotheses, witnesses, branches and the
   final conclusion, then check consistency of mapped dependencies and scopes.
5. Combine local mismatch evidence, coverage, graph consistency and a whole-proof
   assessment. Lean verification remains an independent formal-validity gate.

Matching isolated claims is insufficient. For example, matching two existence
claims does not show that both proofs use the same witness throughout; a fact
available only inside one case cannot silently justify another case. Different
valid proofs can share a conclusion and several lemmas while following different
arguments. Do not demand identical tactic graphs: allow reviewed differences in
granularity and routine elaboration without erasing essential reasoning.

Do not average away one critical mismatch. Equally, do not multiply uncalibrated
step scores as though they were independent probabilities; this introduces
unjustified length effects. Treat pooling/aggregation as an evaluated design
choice, calibrated at the whole-theorem level, with explanations referencing
source spans rather than unsupported certainty.

## Pilot and comparisons

Begin with 10 short, multi-step proofs from the reviewed development pool.
Inspect their extracted chunks and annotate a small number of alignments. Keep
these development examples separate from the frozen external tests.

Compare (A) whole-proof judging, (B) local pair scores with simple pooling, and
(C) local alignment plus coverage/dependency/scope checks and a global judgment.
Cross these arms with controlled-language normalization on a manageable subset.
Match model and inference budgets where feasible and report extraction cost.

Train local scoring on reviewed local labels and carefully constructed
counterexamples. A whole-proof positive is not a label that every arbitrary
chunk pairing matches; a whole-proof negative does not make every chunk wrong.
Weak labels inherited from generated alignments must retain that provenance.

Measure node alignment precision/recall, important-claim coverage, scope/edge
consistency, mismatch localization, extraction success, latency and whole-proof
false acceptance/F1/calibration. Include alterations to one intermediate claim,
swapped witnesses, a missing branch, changed assumptions and faithful regrouping
of steps. Evaluate naturally occurring errors separately from constructed ones.

Split by original theorem family before extraction and mutation. Many chunks
from one theorem do not create independent test examples; bootstrap by theorem
or result family. Human review can focus on localized ambiguities and critical
steps, but decomposition does not automatically remove the labeling requirement.

## Connection to the commuting diagram

Use language on the horizontal axis and proof-to-argument-graph extraction on
the vertical axis. The resulting square asks whether graphs extracted from the
English and Lean correspond under a consistent node/edge alignment. Unlike a
proof-to-statement square, it retains evidence about the internal argument.
Approximate graph correspondence is an experimental criterion, not a proved
semantic preservation theorem.
