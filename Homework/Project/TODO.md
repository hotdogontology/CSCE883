# Project TODO

Last updated: 2026-11-12. Current plan: [methodology.md](methodology.md).
Current context and session log: [SESSION_SUMMARY.md](SESSION_SUMMARY.md).

**Governing objective (user reaffirmed 2026-11-10):** every test is intended to
evaluate detecting semantic differences between natural-language math proofs
and their corresponding Lean proofs. Follow `AGENTS.md` and the original proposal.
English-only coherence and other proxy results are secondary diagnostics, not
semantic-correspondence performance. Include assumptions, conclusions and argument
steps; do not narrow the research question to one proxy or only same-theorem routes.

**Latest results:** the related-proof and four-intermediary queue completed;
read `RESULTS_2026-11-11.md`. Training improved54-pair test42->53correct, but
old16-case argument diagnostic15->11. Generated-code validity remains a major
limitation; no complete code-intermediary pair passed all compilation checks.

**Earlier direction:** corrected overnight unquantized Qwen3-14B run completed;
read `RESULTS_2026-11-10.md`. Completed state is
`artifacts/argument-14b/overnight-20261109/job.json`. No second-pass self-training.
Preserve completed 8B statement-only results and the archived audit/v3 inputs.
For Monday, read `MONDAY_HANDOFF.md` and the newer generated aggregate snapshots
in `reports/two-pass/`; this static checklist may precede later job stages.

Unchecked tasks are outstanding, not evidence that work has begun. Human tasks
are judgment/coordination needs; agents should prepare concrete review material
and continue independent technical work rather than making the user do setup.

## HUMAN TODO

- [ ] Review an agent-prepared small pilot of side-by-side English/Lean pairs
  and provisional labels. Start with a few if useful; the suggested 30 is for
  rubric development, not the full evaluation set.
- [ ] Refine the argument-fidelity rubric: what routine elaboration, automation,
  reordering and proof compression count as the same essential argument?
- [ ] Review ambiguous or substantive labeling decisions and the sampled quality
  of weak training labels. Agree on a feasible, larger evaluation review budget.
- [ ] Identify subject areas the user or another qualified reviewer can assess;
  arrange independent second review of a subset if practical.
- [ ] Confirm course deliverables/deadline and prioritize optional experiments
  if available time cannot support all of them.
- [ ] For a large hosted AXLE job, obtain capacity guidance through its console
  or capacity form. No request to Axiom has been sent on the user's behalf.

Completed human actions:

- [x] Approved the required Windows C++ runtime installation.
- [x] Obtained an AXLE API key and saved it locally in ignored `.env`.

## AGENT TODO

### Next on experiment machine: informalization and English comparison

- [x] Record the user's two-stage direction and laptop-to-workstation handoff.
- [x] Read the workstation results and preserve completed 14B baselines; active32B pilot remains independent of this new plan.
- [ ] Audit existing paired proof data for Lean-to-English supervision and search
  for English alternative-proof datasets; distinguish theorem from argument labels.
- [ ] Prepare theorem-family splits and a small independently assessed pilot for
  both translator fidelity and English argument comparison.
- [ ] Select concrete models/objectives and train/evaluate both stages, including
  untuned and direct-judge baselines and end-to-end mismatch metrics.


### Source-balanced pilot, authorized 2026-11-12

- [x] Build32-row pilot balanced by source/class within each split, with explicit
  provisional Faithform semantic reviews and preserved ProofNet split lineage.
- [x] Strip label metadata/comments from inputs; check grouping, duplicates and balance.
- [x] Run source/length/single-language shortcut controls as secondary diagnostics.
- [x] Verify32B checkpoint completion and published hashes.
- [x] Implement and launch static CPU/GPU BF16 baseline/probe/LoRA comparison.
- [ ] Confirm backward/optimizer probe and complete baseline/tuned comparison;
  inspect artifacts/source-balanced-20261112/qwen32/job.json.
- [ ] Independently adjudicate pilot labels and expand Faithform problem/topic
  coverage before interpreting scores as general semantic-correspondence ability.

- [x] Inspect Faithform label semantics, upstream code and100 actual rows per
  paired release; save FAITHFORM_LABEL_AUDIT.md (2026-11-12).
- [ ] For the corrected32B Faithform experiment, establish semantic negative
  and positive label evidence; do not map validity flags directly to YES/NO.
  The earlier ProofFlow experiment target below was corrected by the user.

### Qwen32 / ProofFlow, authorized 2026-11-11

- [ ] Finish and hash-verify running Qwen3-32B download (qwen32-model-manifest.json).
- [x] Finish pinned ProofFlow JSON release audit; preserve null fidelity labels.
  Downloaded/hash-checked737 files; initial extractor recovered366 unlabeled pairs.
- [ ] Join step-based ProofFlow outputs to English sources; audit missing pairs.
- [ ] Resolve pending training-source/label-policy question; see QWEN32_PROOFFLOW.md.
- [ ] Verify BF16 offloaded inference and a separate LoRA backward/optimizer probe.
- [ ] Compare base/tuned 32B on identical ProofFlow pairs with appropriate metrics.

- [x] Add Pistis to references; inspect Faithform paired-output schemas and
  IMO-Steps HF files; read the user's semantic-fidelity blog and save ideas.
- [ ] Evaluate Faithform step-pair extraction and defensible correspondence
  labels; do not use perturbation flags or prover results as binary match labels.

- [x] Search for argument-level semantic-correspondence datasets beyond synthetic
  swaps; inspect public schemas and distinguish labels from validity proxies.
  See `SEMANTIC_DATA_SEARCH_2026-11-11.md`.
- [ ] Resolve availability of Pistis human-rated pairs and IMO-Steps individual
  English–Lean mismatch annotations; author outreach has not been authorized.
- [ ] If using ProofFlow, audit source alignment and obtain corresponding Lean
  artifacts before assigning any argument-correspondence training labels.

### Authorized overnight extension, 2026-11-10

- [x] Build and validate grouped train/validation/test pairs using a fixed
  relatedness threshold and explicitly synthetic negative labels.
- [x] Evaluate original 14B and train/evaluate a fresh BF16 LoRA on that dataset.
- [x] Run original 14B with English-to-Lean and Lean-to-English intermediaries.
- [x] Run independently generated Verbose Lean and Natural Lean intermediaries;
  preserve generation/compilation failures and coverage separately from labels.
- [x] Research actual dialect training data and Colibri larger-model feasibility.
- [x] Save the overnight queue, logs, provenance and report in
  `OVERNIGHT_2026-11-10.md` and `reports/hard-related-20261110/`.

Eight-stage background queue completed21:19 Eastern November10; independent
results review is in `RESULTS_2026-11-11.md`. Real GPU smoke checks passed for all four generation paths;
they do not establish translation validity. Natural Lean and Verbose Lean
environments both built, with actual syntax/compilation probes. No suitable curated paired
dialect training set found, so conditional generator fine-tuning is not run.
Colibri planner/source study completed; larger-model inference remains untested.

The new user authorization supersedes the older review-before-training task
below for these synthetic related swaps. It does not certify their labels.

- [x] Reread the original proposal and record the user's governing semantic
  correspondence objective in AGENTS, methodology and session context.
- [ ] Ground the next paired English–Lean evaluation in explicit semantic
  differences and justified/assumed labels; map every reported metric to that
  objective and prioritize false acceptance of unfaithful formalizations.
- [x] Run frozen-split random forest and English-only control against the same
  118 validation /16 diagnostic cases; save metrics and provenance.
- [x] Investigate mathlib relatedness and document graph features, version
  mismatch and hard-negative safeguards in `relatedness-and-baselines.md`.
- [x] Establish matching ProofNet Lean4.28/mathlib environment, extract typed
  statement/proof dependency graph, and prepare ranked related-proof candidates.
- [x] Install isolated official Lean4.28 and pinned mathlib4.28 compiled cache;
  first3 extracted-source replays compile. Full run tracked in
  `RELATEDNESS_RUN_2026-11-10.md` and relatedness artifact job state.
- [x] Replay all365 extracted targets successfully; build10343-node/83785-edge
  graph and survey frozen forests/Qwen on177 related validation views. Preserve
  unlabeled status, source-control reproduction and independent core holdout.
- [x] Complete matched-coverage full-Herald forest survey and disagreement report:
  44,537 unique IDs each, original baseline metrics reproduced, no accuracy labels.
- [ ] Compare graph-assisted versus lexical-only candidate mining and extend
  same-theorem route evaluation before interpreting relatedness as fidelity.
- [ ] Review subtle candidate mismatch labels before any further Qwen training;
  preserve separate calibration/test families and existing diagnostic holdout.

### Highest priority: audit corrections before restarting 14B

- [x] Audit methodology, actual inputs, extraction, metrics and saved results;
  reproduce English-only 91.67% shortcut and context-only 66.07% diagnostic.
- [x] Hold queued driver before training; finish/hash-verify 14B download and
  correct manifest path. No 14B probe or training has yet occurred.
- [x] Fix boundaries, preserve helpers, add signature/dependency regressions;
  data-v4 checks pass. Full local Lean4.28 corpus elaboration remains future work.
- [x] Group families/shared proofs before split; regenerate negatives after
  context filtering to preserve class balance and English-proof marginals.
- [x] Make stage reuse verify fingerprints and reject duplicate GPU jobs; use
  a fresh overnight output directory.
- [x] Freeze four locally compiled same-theorem two-route matrices (16 cases)
  and masked-formal control; label them agent-constructed diagnostics.
- [ ] Preserve old 8B scores with source-style and one-training-proof caveats;
  use calibration data for future thresholds and report AUROC/average precision.

### Active: BF16 14B argument correspondence

- [x] Complete corrected overnight training, untuned/tuned validation, compiled
  core and masked controls, and both44,553-rowHerald passes (finished07:01Eastern).
- [x] Review metrics and ranking: coarse validation81.36%->100%; core93.75%->50%
  atfixedrule, yetAUROC1.0forboth. Tunedmodeloveraccepts; preserve this distinction.
- [ ] Prepare a separate same-theorem calibration set and expanded reserved test;
  do not select thresholds on the existing16diagnostic cases.

- [x] Save user-suggested verbose-lean4 / natural_lean references and independent
  English/Lean-to-verbose-Lean architecture idea in `references.md` and
  `verbose-lean-experiment.md` as future work.
- [ ] After direct proof-body experiments, pilot independently compiled verbose
  Lean views and structured argument matching; evaluate combined compilation /
  correspondence ranking before generator reward optimization.

- [x] Start pinned original Qwen3-14B download; no quantization. Old 8B remains intact.
- [x] Extract corrected proof bodies; 361 candidates, six exclusions. Prepare
  balanced 578 train / 144 validation examples with within-split proof swaps.
- [x] Implement BF16 LoRA, real proof-body inference, paired length filtering,
  guard tests and sequential driver. Fifteen tests passed; download/probe pending.
- [x] Complete and hash-verify unquantized 14B download.
- [x] Pass real14B BF16 forward/backward/optimizer probe:4096-token budget,
  actual3946-token input,39.11GiB peak; archive over-budget8192 trial.
- [x] Compare untuned/tuned 14B on proof-body validation; report all class metrics
  with the positive-label assumption and synthetic-negative limitation.
- [x] Run both models on all Herald proof pairs and report disagreements/coverage.
- [ ] Develop same-theorem alternative-argument negatives in a separate experiment.

### Active: first/second pass experiment

- [x] Recheck ProofNet-V proof-pair availability: actual English/formal pairs
  exist and inspected Eisenstein examples follow the same method. Dataset-wide
  argument-fidelity annotation is not established by statement audit.
- [x] Extract a candidate ProofNet argument pilot; audit found fixes required,
  tracked above. Do not silently substitute statements for the argument target.

- [x] Compute class-specific precision/recall/F1, macro/weighted F1, balanced
  accuracy and coverage for all three models on frozen labeled validation.

- [x] Prepare original/corrected ProofNet-V statement pairs and grouped split.
- [x] Train first-pass QLoRA and compare on 112 held-out pairs: 62.50% untuned,
  70.54% first pass, but mismatch recall falls from 21/39 to 13/39.
- [x] Implement agreement-only labels, fresh-base second-pass training and
  source-pinned external screening; three guard tests passed.
- [x] Start sequential background driver; full Herald comparison is in progress.
- [x] Add periodic long-training checkpoints, safe aggregate-report exporter and
  publishing watcher; nine guard tests passed. See Monday handoff.
- [x] Commit project source/docs locally; verify no credentials, data or weights
  staged (45 files, 586,625 bytes). Push is blocked by GitHub write authentication.
- [ ] On Monday, authenticate native Git or enable connected-app repository write
  access, then push local commits and latest aggregate reports. Watcher is local-only.
- [x] Finish untuned/first-pass inference over all 44,553 Herald rows; report
  disagreement, class balance and missing/context-limit coverage.
- [x] Train second pass from original Qwen on eligible agreement pseudo-labels:
  26,961 examples, one epoch, ~5.02 hours; adapter saved.
- [x] Run all three models on frozen validation and external pilot. Validation:
  62.50% / 70.54% / 66.07%; external coverage 5/6, no external ground truth.
- [ ] Review external scope/version/PDF extraction problems and model flags
  before calling them errors; no independently confirmed issue exists yet.
- [ ] Audit representative Herald disagreements and pseudo-label correctness;
  both tuned models detect fewer held-out mismatches than untuned Qwen.
- [ ] Expand source-family overlap checks beyond contest-name/import heuristic.

### Next work: unlabeled exploration

- [x] Select Qwen3-8B as the first local model and start a revision-pinned download.
- [x] Complete/verify the download and run a local BF16 GPU inference smoke test.
  Published hashes passed; model replied `READY`; peak allocated VRAM 15.27 GiB.
- [x] Build a zero-shot binary-fidelity runner with reproducible prompts and
  source provenance. Its predictions are unvalidated, not ground-truth labels.
- [x] Run the 30-pair sample locally without editing review labels: 19 YES,
  11 NO, all 30 responses parseable; no correctness assessment performed.
- [ ] Explore corpus lengths/structure without requiring human annotation.
- [ ] Before any unsupervised adaptation, define the objective and reserve data
  families; no fine-tuning is started by the download task.

### Deferred: reviewed data pilot

- [x] Download ProofNet-V and FaithSieve pinned source snapshots, preserve labels,
  record checksums/schemas/counts and document usage in `dataset-guide.md`.
- [ ] Join archived ProofNet-V proof files to matching metadata; inspect taxonomy
  mappings and replay in an isolated compatible Lean environment before modeling.

- [x] Survey verified correspondence sources; see `verified-data-survey.md`.
- [ ] Inspect ProofNet-Verified archives/taxonomy with pinned revisions as a
  statement-level auxiliary benchmark; do not assume proof-argument labels.
- [ ] Locate released Pistis human ratings/proof pairs and FaithSieve's 135
  semantic-gate audit pairs; availability remains unconfirmed. No outreach sent.

- [ ] Prepare accessible review examples with English and Lean side by side,
  full relevant assumptions, provisional binary fidelity labels, source spans,
  and short explanations. Do not silently treat agent labels as human review.
- [ ] Select human-documented Mathlib examples and compare with the prepared
  Herald sample; record whether each English item describes a statement or proof.
- [ ] Create a trackable annotation schema and provenance/source manifest outside
  ignored download directories. Preserve uncertain/missing labels explicitly.
- [ ] Construct reviewed candidates for hard negatives and meaning-preserving
  positives, including changes to English that keep the Lean proof valid.
- [ ] Define and implement theorem-family grouping, deduplication and source
  overlap checks before generating variants or chunks; provisionally reserve
  external IMO problems/research families.

### Extraction and verification

- [ ] Build a local `.env` loader/AXLE client helper that never logs credentials;
  include low concurrency, bounded backoff, cache keys and source/environment pins.
- [ ] Investigate local Jixia/LeanDojo or Lean metaprogramming compatible with
  Lean 4.11. Compare against AXLE on a compatible synthetic or ported subset.
- [ ] Prototype chunk extraction on roughly 10 multi-step development proofs:
  source spans, context, local claims, witnesses, cases and dependencies.
- [ ] Implement a reusable verification policy beyond the smoke tests: target
  declarations, transitive axioms, admissions, pinned imports, timeouts, and
  separate environment-failure/invalid-proof outcomes.
- [ ] Check corpus replay coverage; document failures without treating all
  environment/version failures as mathematical invalidity.

### First model and baselines

- [ ] Assess Jev as an optional hosted typed-decision baseline and Clef-Flash
  as an open-weight candidate. Verify local custom-head training compatibility
  before changing the first-model recommendation. Neither has been tested here.
- [x] Select/pin the first checkpoint: Qwen3-8B. Download completion is tracked
  above and in `model-manifest.json`; Goedel remains an optional later comparison.
- [ ] Measure token lengths and real-checkpoint GPU memory/runtime; select input
  limits, batching, LoRA/QLoRA settings and treatment of long examples accordingly.
- [ ] Implement text-feature and unfine-tuned LLM baselines.
- [ ] Implement supervised LoRA training with one binary argument-fidelity head.
  Exclude uncertain/unassessable pairs from supervised labels; retain optional
  mismatch categories and verification status as independent metadata.
- [ ] Record seeds, exact checkpoint revisions, prompts, training settings and
  data manifests. Keep checkpoints and bulk results ignored.
- [ ] Evaluate false acceptance, mismatch precision/recall/F1, PR-AUC,
  calibration, abstention/coverage and theorem-clustered uncertainty.

### Separate experiments

- [ ] Compare whole-proof judging with chunk scores and with chunk alignment
  plus dependency/scope checks and global assessment.
- [ ] Pilot a restricted ForTheL fragment: pin grammar/tool version, establish
  vocabulary/foundation mappings, and test actual parser acceptance.
- [ ] Compare direct judging, ordinary-English normalization, controlled-language
  views, and original-plus-controlled inputs under comparable budgets.
- [ ] Curate and independently label frozen IMO and research-level test subsets;
  check overlap, source versions, available English arguments and build environments.
- [ ] Only after judge validation, evaluate compiler-only versus combined
  compiler/judge ranking of a fixed candidate set. Consider generator RL later.

### Project maintenance

- [ ] Review/commit newer project source/docs; two initial local commits exist,
  but no successful push has been confirmed. Keep credentials/bulk files ignored.
- [ ] Keep the summary, TODO and methodology synchronized as decisions change.

Completed agent work:

- [x] Clone repository and inspect the proposal and workstation.
- [x] Install Git, Python, GPU PyTorch/fine-tuning/evaluation tools, VS Code
  extensions and the Jupyter kernel.
- [x] Install/pin Lean 4.11 and Mathlib; pass local smoke proof and one Herald replay.
- [x] Pass CUDA BF16, NF4 and tiny random-model LoRA integration checks.
- [x] Download/pin/audit Herald; prepare 30 unlabeled review examples.
- [x] Document main methodology and controlled-language, structured-proof and
  external-test experiments.
- [x] Verify AXLE's three extraction tools anonymously and a request using the
  locally saved API key; identify missing hosted Lean 4.11 support.
- [x] Update/verify ignore rules and create persistent session summary/TODO docs.
