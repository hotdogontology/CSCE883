# Related proof mining and random forest baseline

Status: 2026-11-10. Random forest implemented and run. The follow-on dependency
graph/mining pilot is now complete: all365 extracted targets compile under the
new isolated Lean4.28 environment; graph10343nodes/83785edges. See
`reports/relatedness-20261110/README.md` for related-swap surveys and limitations.
The design below records the starting proposal; route labels remain unverified.

## Mathlib graph proposal

Use a typed graph rather than a single subject tree. Nodes: ProofNet exercises,
Lean declarations, mathematical types/typeclasses, mathlib modules and subject
areas. Edges: statement mentions a concept, proof uses a declaration, declaration
belongs to a module, module imports another module. Keep statement dependencies
separate from proof-body dependencies. A statement can be close while its proof
route is different, which is precisely the desired difficult comparison.

Mathlib exposes an [import graph](https://leanprover-community.github.io/mathlib4_docs/mathlib.html).
Lean's [environment implementation](https://github.com/leanprover/lean4/blob/master/src/Lean/Environment.lean)
supports declaration provenance. Local Lean4.11 code confirms practical building
blocks: `importGraph/ImportGraph/RequiredModules.lean` uses `getModuleIdxFor?`
and module names; `Mathlib/Util/Export.lean` uses `getUsedConstants` on declaration
values. These are implementation leads, not a claim that a 4.28 extractor ran.

Many ProofNet inputs use `import Mathlib`, so direct imports do not identify a
subject. Extract elaborated theorem types and proof terms, resolve referenced
constants to modules, and expand local helper dependencies. Distinguish generic
infrastructure from mathematical dependencies. Proof terms may obscure the
human strategy and tactic names alone do not certify a route.

Original local mathlib is pinned for Lean4.11; ProofNet source is the 4.28 archive.
Follow-up installed an isolated matching4.28 toolchain/mathlib, so this version
obstacle is now resolved for the extracted targets;4.11 core remains separate.
Use the source's matching Lean/mathlib environment before authoritative graph
extraction. Text matching against 4.11 can only be a partial, version-mismatched
candidate index; unresolved names must remain explicitly unresolved.

Represent relatedness as several reported components:

- Subject/module proximity, including shared ancestors and graph distance.
- Overlap of statement types, typeclasses, constants and normalized structure.
- Overlap of proof mathematical dependencies, downweighting ubiquitous lemmas
  with training-corpus inverse-document-frequency weights.
- Evidence about route: induction variables, witnesses, intermediate claims,
  and ordered/subgoal structure. Treat lexical tactic proxies as weak evidence.

Start with ranked neighbors and component scores, not an asserted calibrated
probability or arbitrarily fixed weighted sum. Inspect candidate examples before
freezing weights. Favor same-domain/type/statement neighbors, then same-theorem
different-route examples where available. Dependency overlap is not itself proof
of faithfulness: different arguments share dependencies and equivalent arguments
can use different helper lemmas.

## Hard-negative protocol

Freeze exercise-family/shared-proof train, calibration and test partitions before
mining. Fit learned similarity models or IDF on training only; choose donors only
within a partition. Record graph/source versions and donor provenance. Balance
positive/negative field marginals where feasible; ensure swapped full prompts fit
the context limit. Never label a pair NO solely because its record ID differs.

Use difficulty tiers: unrelated problems; related-domain problems; near-identical
statements; identical theorem with substantively different arguments. The first
two still permit statement/coherence shortcuts and are not substitutes for the
last tier. Review hard candidates for actual mismatch; set aside uncertain cases.
Include positive paraphrases, expanded formal steps and equivalent presentations
so sensitivity to superficial changes is not rewarded. A swap must specify its
unit (proof body versus statement+proof bundle); swapping just the proof can
break English statement/proof coherence. Compare English-only and Lean-only
controls and reserve human-assessed same-theorem evaluation.

No new Qwen training or pseudo-label training was started.

## Completed random forest baseline

Run: `scripts/random_forest_argument.py`. Frozen overnight budget-data:
510 training rows, 118 validation rows, existing 16-case diagnostic. Input hashes
and full precision/recall/F1/AUROC are in `reports/random-forest-20261110/metrics.json`.

Features: train-only character TF-IDF 3–5 grams, at most 12,000 features, train-only
32-component truncated SVD, per-field projections, pairwise cosine similarities,
projection absolute differences/products, log field lengths. Both-language model
uses the two statements and two proof bodies; context is omitted. English control
uses only English statement/proof. Source theorem declaration names are normalized;
IDs, labels and route metadata are never feature inputs. No LLM or embeddings
from Qwen are used. All fitting is restricted to training rows.

Random forest: 400 trees, minimum leaf size 2, square-root feature subsampling,
balanced class weights, seed883, four CPU workers, fixed0.5 threshold. No validation
or diagnostic hyperparameter/threshold search. Script reruns fitting rather than
saving a classifier artifact. These fixed baseline choices are not tuned optima.

| Model | Swap validation accuracy (118) | Same-theorem diagnostic accuracy (16) |
| --- | ---: | ---: |
| English-only forest | 108/118 (91.53%) | 8/16 (50%) |
| Both-language forest | 105/118 (88.98%) | 9/16 (56.25%) |
| Untuned Qwen3-14B | 96/118 (81.36%) | 15/16 (93.75%) |
| LoRA Qwen3-14B | 118/118 (100%) | 8/16 (50%) |

Forest macro F1: English validation .9150, both-language validation .8896;
core .3333 and .4589. Forest core AUROC .5 and .578125, versus1.0 for both Qwen
models. Threshold accuracy alone hides the Qwen score separation discussed in
`RESULTS_2026-11-10.md`. The core has only four constructed theorem families;
these are descriptive results, not a robust model ranking or independent audit
of training labels. Follow-up forests have now scored the matched 44,537 Herald
pairs: English-only rejects 6 and both-language rejects 2. See
`reports/random-forest-herald-20261110/README.md`; no independent accuracy labels.
