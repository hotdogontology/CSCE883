# Project continuity

## Research objective: governs every experiment

User clarification, 2026-11-10:

> Every test we do is meant to test whether we can identify semantic differences
> in natural language math proofs and corresponding Lean proofs. That is the
> entire question we are trying to work on.

The task is to judge whether a natural-language mathematical proof and its Lean
formalization are faithful translations. Compare their mathematical meaning:
assumptions, domains, quantifiers, conclusions, intermediate claims, witnesses,
dependencies, and essential steps of the argument. Allow routine formal
elaboration and equivalent presentations. Both proofs being valid, concerning
the same topic, or proving the same theorem does not establish correspondence.

Read `project-proposal-tbelcher.tex` when designing or revising experiments.
The proposal anchors the research question; subsequent user decisions govern
implementation choices and authorized dataset assumptions. Its motivating case
is accepting Lean code that passes verification but changes the English proof's
meaning or argument. Same-theorem examples test one important kind of semantic
difference; they do not replace testing changed assumptions or conclusions.

For every experiment, state what semantic correspondence or difference the pair
represents, how its label is justified (or assumed/unknown), and how the result
bears on the English–Lean task. Main model and baseline comparisons must address
paired English and Lean proof evidence. Single-language ablations are secondary
diagnostics; their scores are not semantic-correspondence performance. Do not
substitute English statement/proof coherence, lexical similarity, topic matching,
or compilation success for the research objective, or describe success on those
proxies as answering it. Obvious swaps can be coarse semantic-mismatch examples;
report their difficulty and limits rather than redefining the target around them.

Prioritize detecting unfaithful translations, including subtle changes that
preserve Lean validity. Report mismatch precision, recall, F1, confusion matrices
and concrete caught/missed semantic differences when justified labels exist.
Unlabeled acceptance rates and model agreement remain descriptive; they establish
neither semantic accuracy nor verified errors. Preserve earlier results with
their actual scope instead of retrospectively treating them as the target task.

## Working context

User clarification, 2026-11-12: the new pipeline is a checker. Stage one trains
Qwen to produce an English version of the supplied Lean proof, using existing
paired formalization corpora in reverse (Herald is a primary candidate). Stage
two compares that generated English with the original English proof. Stage one
does not require binary correspondence labels or train a formalizer. Do not turn
general data-quality caveats into a reason to dismiss reverse-direction training.
Readable informalization also has standalone value for human sanity checking of
Lean proofs. Translation fidelity is assessed separately from comparator quality.

When working in this project, read `SESSION_SUMMARY.md` and `TODO.md` first.
Use `methodology.md` as the current experimental plan and follow its linked
experiment documents for their scope. Check actual files before assuming a
planned component is implemented.

After meaningful work, update the summary's current state/session log and TODO
checkboxes. Keep recommendations, user decisions, completed work and measured
results distinct. Do not claim access to earlier sessions outside the available
history; preserve missing context as an explicit uncertainty.

Never display or commit `.env` credentials. Keep data downloads, environments,
model weights and build caches ignored; retain small source/provenance manifests
and curated annotations outside ignored download directories.
