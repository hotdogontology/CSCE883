# Relatedness pilot, 2026-11-10

**Completed:** all365 extracted targets compile; graph10343nodes/83785edges;
765training views/177validation views mined. Frozen RF and both14B surveys
complete, all original controls reproduce. See
`reports/relatedness-20261110/README.md` and `summary.json` for measured results.
No new candidate labels or Qwen training. The separate full-Herald forest survey
also completed; see `reports/random-forest-herald-20261110/README.md`. Both forests
scored the same 44,537 IDs as Qwen and reproduced original frozen metrics.
English-only forest rejects 6; both-language forest rejects 2. No known accuracy.

User authorized continuing the mathlib-relatedness and baseline work while away
for about an hour. The current driver is `scripts/run_relatedness_pilot.py`;
live state is `artifacts/relatedness-20261110/job.json`. Do not start a duplicate.

## Implemented procedure

1. Installed workspace-local official Lean4.28 Windows release, verified SHA256
   `faa0a8213ec81035d1ff3745d6d28e55b9d80de63fb9cd33380cd51b23cfc1aa`.
   Cloned mathlib4 v4.28.0, commit
   `8f9d9cff6bd728b17a24e163c9402775d9e6a365`, fetched compiled cache.
   Original Lean4.11/core environment remains separate. Source checkout's current
   Lean4.34 environment is not the archived4.28 environment used here.
2. Replay 365 extracted ProofNet positives independently. Export resolved constants
   separately for statement and proof, expand local helper declarations, resolve
   imported declarations to modules. Logs, exact generated code, source hashes and
   per-proof status are retained. Successful compilation establishes elaboration,
   not correspondence to the English. Not a transitive axiom-policy audit.
3. Build a typed graph: proof→statement/proof dependencies→declaration module,
   module→direct imports and subject directory. This is the portion reached by
   ProofNet, not a complete graph of mathlib or a semantic ontology certification.
4. Restrict candidate sources to successful complete replays and existing train /
   validation membership. Fit statement character TF-IDF and proof-module IDF
   on eligible training positives only. Score pairs with the frozen heuristic
   `.45 English statement cosine + .45 formal statement cosine + .10 proof-module
   cosine`. Its scale is not a probability or validated semantic distance.
5. Save five ranked neighbors per source. Use maximum-weight donor permutations
   within each split, excluding same-family/shared-proof donors. Each English
   proof is used once, preserving exact marginals. Reject over4096-token edges
   and reassign; no proof truncation.
6. For each source, prepare its original pair, a related English-proof-only swap,
   and a related English-statement+proof bundle swap. The latter preserves
   English-side coherence. **No binary labels are assigned to either swap type.**
   Both remain cross-problem candidates, not same-theorem route ground truth.
7. Survey the existing fixed random forests and untuned/tuned14B on validation
   candidates. No fine-tuning, threshold fitting, or pseudo-label training. Verify
   original RF results and Qwen source-control predictions reproduce prior runs.
   Report acceptance counts, not candidate accuracy.

## Files

- Setup provenance: `data/lean428/setup.json` (ignored).
- Replay/export: `scripts/extract_proof_dependencies.py`,
  `lean/ProofDependencies.lean`.
- Mining: `scripts/mine_related_proofs.py`.
- Integrity guards: `scripts/test_relatedness.py`.
- Raw graph/candidates/replays/predictions: `artifacts/relatedness-20261110/`.
- Small final aggregate: `reports/relatedness-20261110/summary.json`.
- Original RF baseline: `reports/random-forest-20261110/`.

Large environments, cache, weights, raw graph and data remain gitignored. No
GitHub push or external message is part of this run. Final results must be read
from actual completed stages, not inferred from this procedure document.
