# Proposal review and suggested answers

Your existing prose is preserved in the TeX file; only citation commands and a reference list were added. These notes are suggestions for your own additions, not commitments made on your behalf.

## Requirements and current coverage

The course webpage could not be retrieved. The local `Project Instructions.docx` links to the same page and specifies a two-page proposal answering four questions:

1. **Problem and motivation:** Already covered. Clarify whether you want to judge theorem-statement equivalence, fidelity of proof arguments, or both. These require different labels. Two valid proofs of the same theorem can use different arguments.
2. **Data, with examples:** Name a specific corpus, show a pair, and explain how you obtain correspondence labels. Existing formal/informal pairs do not automatically supply trusted match/mismatch labels.
3. **ML method and use/modification of existing implementations:** Specify a first model, inputs, targets, and a feasible training procedure. Reinforcement learning remains optional; the kernel cannot directly provide the semantic-correspondence reward you need.
4. **Evaluation, qualitative and quantitative:** Specify a held-out test set, metrics, baselines, and expected figures or error examples.

## Suggested scope

Start with **theorem-statement correspondence in Lean**. Treat argument-level correspondence and transfer to Agda as extensions. This still addresses part of your motivation, but it will not establish that the English and formal proofs use the same argument. If proof fidelity is essential, restrict the project to short proofs and annotate their steps explicitly.

The claim that a formal proof establishes the intended theorem needs the same qualification: the kernel checks the formal statement under its assumptions and axioms. It does not establish that this is the theorem the English text intended.

## Suggested answer: data

Another candidate source is [1000+ theorems in Lean](https://leanprover-community.github.io/1000.html), a catalog of named theorems with formal statements and links to documentation and source. Use the theorem identities to locate corresponding English statements, then review their assumptions and scope before labeling pairs. The catalog includes the Pythagorean theorem and binomial theorem; it does not itself supply correspondence labels or aligned natural-language proof steps.

Use [Compfiles IMO problems](https://dwrensha.github.io/compfiles/imo.html) as a candidate source of problem statements and Lean formalizations. Inspect the linked files to confirm which entries include usable English statements and complete formal context. Use [Informath](https://github.com/GrammaticalFramework/informath) for controlled examples and paraphrases; its documentation includes corresponding English, Lean, and Agda statements. It currently emphasizes statements and definitions, so do not describe it as a ready-made corpus of aligned proof arguments.

A concrete example from the Informath README says that for odd integers a and c, ab + bc is even for every integer b; its Lean declaration expresses the oddness assumptions and the universally quantified conclusion. A proposed negative example could change the English conclusion from even to odd while keeping the formal declaration fixed. This would be your constructed example, not an existing mismatch label from the repository.

For each pair, retain the formal context, assumptions, source, and theorem identifier. Manually verify a manageable subset of positive pairs. Construct negative candidates by changing domains, quantifiers, hypotheses, or conclusions, and check that each edit actually changes meaning. Include close mismatches as well as unrelated pairings; unrelated negatives alone make the task artificially easy. Mark ambiguous examples separately instead of forcing a label.

Split by original theorem before making variants, so paraphrases and altered versions of one theorem stay in the same split. Where possible, also separate source files or mathematical topics to reduce leakage.

For an Agda extension, your [agda-categories-informalized dataset](https://huggingface.co/datasets/astral-expmath/agda-categories-informalized) currently displays approximately 4.54k rows, with source snippets, full source, informal statements, and a generating-model field. It is a useful candidate resource, but generated informalizations need manual validation before being treated as faithful labels. Records include definitions and field signatures as well as theorems; a row is not necessarily a natural-language proof paired with an Agda proof.

## Suggested answer: method

Frame the first experiment as supervised binary classification of an English statement and its formal counterpart. A possible starting point is a pretrained model that reads their concatenation and produces a match/mismatch score, using a classification head or parameter-efficient fine-tuning if available compute permits. Choose the exact checkpoint after checking access, memory, and support for code and mathematical notation; none is assumed here.

Compare against a simple text-feature classifier, such as TF-IDF plus logistic regression, and an unfine-tuned LLM judging the same pairs. Your contribution would be the correspondence task, reviewed labels, meaningful mismatch generation, and evaluation of what training improves. The model can judge a pair directly; generating a translation is not required, though a translate-then-compare method could be a separate baseline.

If retaining the reinforcement-learning idea, explain who or what supplies trustworthy correspondence rewards. A proof compiling is evidence of formal validity, not semantic fidelity. Begin with supervised labels to avoid making reward design an additional unsolved project.

## Suggested answer: evaluation

Evaluate on manually reviewed pairs held out by theorem. Report precision, recall, and F1 for detecting mismatches, plus a confusion matrix. Report false acceptance of mismatches separately because it directly undermines the proposed reviewer. Break results down by mismatch type, and distinguish constructed mismatches from any genuine errors you can collect.

If reporting probabilities as confidence, assess calibration using a reliability plot and Brier score; a raw output score is not automatically a calibrated probability. Use bootstrap confidence intervals at the original-theorem level if enough independent theorems are available. For a very small test set, state the uncertainty and avoid strong claims from small differences.

Expected outputs could include a baseline comparison table, confusion matrix, results by mismatch type, and a few annotated examples showing detected and missed semantic changes. For full proof correspondence, add a separate human annotation rubric covering assumptions, intermediate claims, and argument steps; statement labels alone cannot evaluate that goal.

## How the resource links fit

- [Formalizing Mathematics at Scale](https://arxiv.org/abs/2605.29955): Cited for LLM-assisted formalization. Describes AutoformBot and Atlas, with formalizations from 26 textbooks. It does not support the claim about OpenAI releasing hundreds of proofs.
- [Navier–Stokes lost in translation](https://arxiv.org/abs/2610.08144): Cited for the correspondence problem and the authors' reported mismatches. Attribute their findings to the paper rather than treating every conclusion as settled consensus.
- [AXLE](https://axle.axiommath.ai/) and [Aristotle](https://aristotle.harmonic.fun/): Related tools to discuss if you add a related-work comparison. They are not cited in the existing prose because it does not name or describe them. Verify their specific checking capabilities before claiming your proposed checker is distinct.
- [Informath](https://github.com/GrammaticalFramework/informath) and [Compfiles](https://dwrensha.github.io/compfiles/imo.html): Cited beside the availability of English/formal resources. They do not substantiate the separate claim that Lean is the most popular formalization language.
- [Agda dataset](https://huggingface.co/datasets/astral-expmath/agda-categories-informalized): Cite when you explicitly name this potential data source. It does not establish a comparison of total Lean and Agda data availability.
- Mathlib: Your resource file names it without a link. A formal library by itself should not be described as a reviewed English/Lean alignment dataset.

## Claims to check before submission

- Distinguish an **announced or claimed** Navier–Stokes result from an accepted solution to the Millennium Prize problem. The linked critique discusses an announced proof and challenges correspondence; it does not certify an accepted solution. The existing wording was left untouched.
- The IMO medal claim and the claim about OpenAI releasing hundreds of proofs need their own primary sources. The links currently supplied do not establish those claims.
- Kernel trust depends on the formal statement, its assumptions, admitted results, and axioms. A checked formal proof is not automatically evidence for an English statement whose translation is disputed.
- Typos remain untouched, including “Millenium,” “conejctur,” and “written the interactive theorem proving language.”
- The current body already occupies two pages. References and the missing answers will require space. The local instructions do not say whether references are excluded from the limit; keep this constraint in mind before adding material.
