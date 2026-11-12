# Search for argument-correspondence training data

Search date: 2026-11-11. This is a research note, not a training run or a change
to approved labels. The user requested alternatives to the synthetic 16-pair
diagnostic. Target: faithful English–Lean argument translation, including subtle
changes in steps, dependencies, assumptions and conclusions.

## Finding

## Follow-up: inspected paired releases and user-supplied blog

The IMO-Steps Hugging Face URL is indeed the public dataset. Its recursive file
listing contains Lean lemma/proof projects, README and an image, not the individual
o3-mini English outputs and correspondence annotations from its aggregate table.
The viewer's two rows are accidentally indexed lake-manifest files, not the
number of mathematical examples. A spot check of the GitHub mirror's 1959 P1
lemma and full-proof files finds Lean code without an English argument. This
does not rule out comments elsewhere, but no paired annotation release was found.

**FaithformBench companion releases do contain English–Lean pairs.** Inspected
Faithform-AF (viewer approximately 153k rows) and Faithform-LLMs (approximately
102k): step_content, dependencies_content, problem_id, node_id,
autoformalizer_model, autoformalizer_output, prover_output, proof_result,
is_perturbed and perturbation metadata. These counts include repeated source
steps across models/variants, not independent proofs. Formalizer output can
contain a Lean statement with sorry; prover output may prove that statement or
its negation. For example the LLM release preserves the false English arithmetic
claim 4*5=25 as Lean 4*5=25 and separately supplies a refutation. Thus Refuted
does not mean mistranslated, and is_perturbed is not a mismatch label. This is a
real candidate for step-level correspondence work after extraction and label
auditing, not an already human-labeled full-proof classifier corpus. Keep all
variants/models of one problem together in any train/test split.

User wants ProofFlow retained as interesting even without Lean correspondences.
Pistis paper added to references: it uses Claude-generated proofs of Euclid but
adds constrained decomposition/dependency tracking and human fidelity evaluation.

Read Robert Joseph George's original November 2026 blog,
[Getting the (In)formal Statement Right](https://www.robertj1.com/ai4science/getting-the-statement-right/).
Project applications (recommendations, not completed experiments):

- Source-step to Lean-declaration mappings, using blueprints and dependency
  graphs, could support our argument-level comparisons.
- Supply definitions, elaborated types and hypotheses to the judge; surface
  syntax can hide changed domains or implicit assumptions.
- Obtain realistic mismatch cases from public audits and versioned corrections,
  then independently verify source/code correspondence before labeling.
- Keep validity, semantic fidelity and readable argument structure distinct;
  back-translation alone is evidence, not a proof of fidelity.
- Inspect linked leanblueprint, literature-links and formal-companion tools
  for source-to-declaration linkage and review workflows. Links were identified;
  these tools were not installed or executed in this follow-up.

The blog's Yau example compares a paper's stronger growth condition with a
weaker Lean challenge; its abstract separating sequence establishes the
distinction between conditions, not a counterexample concerning actual
eigenfunctions. Treat as a candidate statement-level case, not already audited
argument-level gold. No datasets were relabeled or models trained.

## Initial search findings

No large, publicly downloadable, human-labeled full-proof match/mismatch corpus
was confirmed in this search. This is a search result, not proof none exists.
There are useful argument-level sources, actual human evaluation studies, and
larger constructed step-level tests. These must not be conflated with statement
equivalence datasets or compilation labels.

## Closest leads

### Pistis: closest human evaluation of argument fidelity

[Paper](https://arxiv.org/abs/2608.15432),
[PDF](https://arxiv.org/pdf/2608.15432).

Evaluates faithful formalization of Euclid's Elements, including dependency
tracking and blocking shortcuts. The human study reports 14 reviewers, 127
completed assignments, 254 step-fidelity ratings and 381 pairwise judgments.
These are not independent binary training pairs. No public release of the
individual reviewed pairs and annotations was located. Best author-data request
candidate: source English proofs, competing Lean formalizations, per-step
ratings, rubric, and environment. No request was sent.

### IMO-Steps: actual English–Lean mismatch analysis

[Official repository](https://github.com/roozbeh-mohit/IMO-Steps),
[dataset](https://huggingface.co/datasets/roozbeh-yz/IMO-Steps).

README reports 1,329 lemmas from 13 IMO problems and complete formal proofs for
20 problems. Its additional o3-mini analysis explicitly separates English
correctness, Lean correctness, and English–Lean matching; aggregate matching is
96.4%, with lower rates for three problems. This suggests naturally occurring
model mismatches rather than artificial swaps. However, the inspected recursive
repository tree did not expose individual generated pairs or correspondence
labels; llm_evaluation contains an extraction utility. Do not infer downloadable
labeled examples from the aggregate table, or interpret matching as correctness.
Potentially valuable author-data request, especially failed correspondence cases.

### ProofFlow: available proof-step and dependency supervision

[Repository](https://github.com/Huawei-AI4Math/ProofFlow),
[dataset](https://huggingface.co/datasets/rafaelcabral96/ProofFlowBench),
[paper](https://arxiv.org/abs/2510.15981).

Inspected actual data/benchmark_0409.json: 184 rows and 1,549 graph nodes.
Top-level fields: origin, id, nl_theorem, nl_proof, proof_graph. Nodes include
natural_language, statement and dependencies. This main file does not contain
completed Lean proofs or human match/mismatch labels. Generated result artifacts
exist separately; README describes ProofScore as AI-powered, not human gold.

Spot checks raise source-alignment concerns: naturalproofs_stein.json id 9 pairs
primitive-root existence with a counting argument assuming cyclicity; id 18 pairs
Mazur's torsion theorem with algebra concerning congruent numbers. These are
specific concerns requiring review, not a measured dataset-wide error rate.
Useful for graph/step supervision after auditing, not safe to import wholesale
as trusted positive English–Lean argument pairs. No untrusted pickle was loaded.

## Available constructed stress tests

- [FaithformBench](https://huggingface.co/datasets/ighina/FaithformBench): viewer
  reports about 27.9k rows of reasoning steps and perturbations. Related
  Faithform-AF and Faithform-LLMs releases contain formalizer results. Focus is
  preservation of valid/invalid steps, including silently repairing invalid
  English. Still constructed and step-level; prover outcomes do not themselves
  establish full argument correspondence. See [paper](https://arxiv.org/abs/2608.10916).
- [RobustPABench](https://huggingface.co/datasets/ucr-rai/RobustPABench) and
  [code](https://github.com/ucr-rai/robust-proof-autoformalization): local edits,
  deletions, and global paraphrases based on miniF2F and MATH500. Relevant subtle
  perturbations, but still synthetic. Inspected default subset shows formal_proof
  placeholders (sorry), not completed paired Lean proofs; other output artifacts
  would need a separate audit before training.

## Semantic labels that do not cover full proof arguments

- [MA-Align](https://huggingface.co/datasets/MathAtlas/MA-Align): 200 test items;
  informal/formal/label/type fields, aligned/misaligned statements and definitions.
- [ProofNetVerif](https://huggingface.co/datasets/PAug/ProofNetVerif): 3,752 labeled
  statement formalizations, distinct from our ProofNet-Verified data. Could help
  statement-semantic supervision; does not solve argument-route classification.
- [FaithAlign](https://arxiv.org/html/2610.18498): paper reports 460 items and
  4,982 phrase-level links, context and implicit-assumption annotation. No public
  individual release confirmed; targets statements/definitions, not whole routes.

## Recommended next decision

Prioritize obtaining Pistis and IMO-Steps individual human-reviewed outputs.
Audit ProofFlow as a source for step/dependency supervision rather than assigning
binary gold labels automatically. FaithformBench and RobustPABench can supply
larger controlled semantic stress tests, explicitly reported as constructed.
None of these findings authorizes treating compilation or an LLM judgment as
verified correspondence. Preserve a theorem/source-group-held-out evaluation;
avoid reusing benchmark test examples for both training and reported testing.

No training data, model weights, existing labels or experimental results were
changed during this search. No author outreach occurred.
